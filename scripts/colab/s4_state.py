"""Google Drive state of the S4 runs (standard library only; docs/plan/S4预注册_20261110.md sections 8-12).

Everything lives under <remote><base dir>/s4/<experiment>/ (registry ``checkpoints`` section, D58):

    PILOT_LATEST.json                       the most recent pilot result, passed or not (scripts/colab/decide_pilot.py)
    code_baseline/<job>.json                source_sha256 and package versions of the first formal run (one file per
                                            job; the earliest one is the baseline, pre-registration section 9)
    pilot/<job run id>/RESULT.json          that pilot's result (the same document as PILOT_LATEST.json)
    pilot/<job run id>/<pilot run>/...      pilot runs (same layout as a run directory)
    <arm>/seed<k>/checkpoint-<step>/        trainer files and a rollouts.jsonl snapshot; DRIVE_VERIFIED.json is
                                            written last, after `rclone check` passed
    <arm>/seed<k>/final/ + run files        the step-228 adapter, run_identity.json, train_summary.json,
                                            log_history.json, trainable_parameters.json, rollouts.jsonl
    <arm>/seed<k>/STARTED.json              written when a job starts the run for the first time
    <arm>/seed<k>/COMPLETED.json            written last, after the final files were verified
    <arm>/seed<k>/failures/<job>-<n>.json   computation failures; the second one also writes FAILED.json
    <arm>/seed<k>/claims/<job>.json         which job is running the run: one file per job, so two VMs never write
                                            the same name (Drive allows two files with one name)

Every marker carries the run's ``key`` (its registered config_sha256 and, for formal runs, the content hash of the
frozen runtime); markers with another key are ignored, never resumed and never deleted. Only the runner writes
there, and the only deletions are older checkpoint directories of the run being written whose marker has this key
(``RunDrive.retain``; permanent, because Drive's trash still counts against the quota), and the job's own claim file.
"""
import hashlib
import json
import os
import re
import shutil
import time
from pathlib import Path, PurePosixPath

from scripts.colab import drive
from scripts.colab.common import log

CLAIM_TTL_SECONDS = 3600  # a claim without a heartbeat for this long belongs to a dead job
HEARTBEAT_SECONDS = 300
CLAIM_SETTLE_SECONDS = 10.0  # between writing a claim and reading every claim back
VERIFIED = "DRIVE_VERIFIED.json"
COMPLETED = "COMPLETED.json"
FAILED = "FAILED.json"
STARTED = "STARTED.json"
ROLLOUTS = "rollouts.jsonl"
RESTORED_NOTE = "restored_from_drive.json"  # not named checkpoint-*: HF Trainer globs that prefix
RUN_FILES = ("run_identity.json", "train_summary.json", "log_history.json", "trainable_parameters.json")
CHECKPOINT = re.compile(r"^checkpoint-(\d+)$")


def utc(epoch=None):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() if epoch is None else epoch))


def percentile(values, q):
    """Nearest-rank percentile (the k-th smallest value, k = ceil(q * n)), as in S3 design section 6."""
    values = sorted(values)
    if not values:
        return None
    rank = max(1, -(-int(round(q * 1000)) * len(values) // 1000))
    return values[min(rank, len(values)) - 1]


def sha256_file(path):
    digest = hashlib.sha256()
    with open(str(path), "rb") as handle:
        for block in iter(lambda: handle.read(1 << 22), b""):
            digest.update(block)
    return digest.hexdigest()


def file_table(directory, skip=()):
    """{relative posix path: {"bytes", "sha256"}} of every file under ``directory``."""
    directory = Path(directory)
    table = {}
    for path in sorted(directory.rglob("*")):
        rel = path.relative_to(directory).as_posix()
        if path.is_file() and rel not in skip:
            table[rel] = {"bytes": path.stat().st_size, "sha256": sha256_file(path)}
    return table


def experiment_base(registry, experiment_name):
    """'s4/<experiment>' from the registry's drive_dir template 's4/{experiment}/{arm}/seed{seed}'."""
    template = registry["checkpoints"]["drive_dir"]
    return str(PurePosixPath(template.format(experiment=experiment_name, arm="_", seed=0)).parent.parent)


def run_rel(registry, experiment_name, arm, seed):
    return drive.check_rel(registry["checkpoints"]["drive_dir"].format(experiment=experiment_name, arm=arm,
                                                                       seed=int(seed)))


def complete_lines(source, target):
    """Copy ``source`` up to its last newline (a growing JSONL file may end in half a record); return the line count."""
    data = Path(source).read_bytes() if Path(source).is_file() else b""
    end = data.rfind(b"\n") + 1
    Path(target).write_bytes(data[:end])
    return data[:end].count(b"\n")


def link_tree(source, target):
    """Hard-link (or copy) every file of ``source`` into ``target``: an upload staging copy that costs no space.
    Safe because HF Trainer never rewrites a checkpoint directory after it saved it."""
    source, target = Path(source), Path(target)
    for path in sorted(source.rglob("*")):
        if not path.is_file():
            continue
        out = target / path.relative_to(source)
        out.parent.mkdir(parents=True, exist_ok=True)
        try:
            os.link(str(path), str(out))
        except OSError:
            shutil.copy2(str(path), str(out))


def rollouts_before(snapshot, target, step):
    """Keep the records of steps 1..step (rl_rewards logs them with global_step 0..step-1); return (kept, dropped)."""
    kept = dropped = 0
    with open(str(snapshot), "r", encoding="utf-8") as source, open(str(target), "w", encoding="utf-8") as out:
        for line in source:
            if not line.strip():
                continue
            record = json.loads(line)
            if record.get("global_step") is not None and int(record["global_step"]) < int(step):
                out.write(line if line.endswith("\n") else line + "\n")
                kept += 1
            else:
                dropped += 1
    return kept, dropped


class Store(object):
    """Drive operations relative to <remote><base dir>; ``info`` comes from ``drive.detect`` (called once)."""

    def __init__(self, info, scratch):
        self.info = info
        self.scratch = Path(scratch)
        self.scratch.mkdir(parents=True, exist_ok=True)

    @classmethod
    def open(cls, scratch, remote=None, base_dir=None, mount=None):
        """(Store or None, detect info)."""
        info = drive.detect(remote, base_dir, mount)
        return (cls(info, scratch) if info["usable"] else None), info

    def put_json(self, rel, value):
        return drive.put_text(self.info, rel, json.dumps(value, indent=2, ensure_ascii=False) + "\n", self.scratch)

    def get_json(self, rel):
        """(value, "ok") / (None, "missing") / (None, "error: ...") / (None, "invalid json")."""
        text, status = drive.get_text(self.info, rel)
        if text is None:
            return None, status
        try:
            return json.loads(text), "ok"
        except ValueError:
            return None, "invalid json"

    def tree(self, rel, depth=3):
        return drive.list_tree(self.info, rel, max_depth=depth)

    def delete(self, rel):
        return drive.delete_file(self.info, rel)

    def purge(self, rel):
        return drive.purge(self.info, rel)

    def copy_verify(self, src, rel):
        return drive.copy_verify(self.info, src, rel)

    def fetch_verify(self, rel, dest):
        return drive.fetch_verify(self.info, rel, dest)

    def about(self):
        return drive.about(self.info)


def _brief(result):
    return {k: result.get(k) for k in ("ok", "target", "source", "files", "bytes", "copy_seconds", "check_seconds",
                                       "copy_rc", "check_rc", "reason") if k in result}


# ---- one run's directory -----------------------------------------------------------------------------------------

class RunDrive(object):
    """Checkpoint uploads, final upload, restore and retention for one run directory on Drive.

    ``key``: dict identifying the run's configuration (set later with ``set_key`` when only the training process
    knows it, as for unregistered pilot runs). ``guard``: optional callable checked before every upload; False
    means another job holds the run now, and nothing is written (the caller stops the training)."""

    def __init__(self, store, rel, key, job_id, run_name, keep=1, guard=None):
        self.store, self.rel, self.key = store, drive.check_rel(rel), dict(key) if key else None
        self.job_id, self.run_name, self.keep = job_id, run_name, int(keep)
        self.guard = guard
        self.lost_claim = False
        self.ours = set()  # checkpoint steps this object uploaded or restored: they may be retained or purged

    def set_key(self, key):
        if self.key is None:
            self.key = dict(key)
        return self.key == dict(key)

    def _staging(self, label):
        path = self.store.scratch / ("%s-%s-%d" % (self.run_name.replace("/", "_"), label, os.getpid()))
        shutil.rmtree(str(path), ignore_errors=True)
        path.mkdir(parents=True)
        return path

    def _guarded(self):
        if self.guard is not None and not self.guard():
            self.lost_claim = True
            return False
        return True

    def upload_checkpoint(self, checkpoint_dir, step, rollouts=None):
        """Copy checkpoint-<step> plus a rollouts snapshot, verify, then write the marker; keep the newest."""
        started = time.time()
        step = int(step)
        record = {"step": step, "ok": False, "started_utc": utc()}
        if self.key is None:
            record["reason"] = "the run's key is unknown; nothing was written"
            return record
        if not self._guarded():
            record["reason"] = "another job holds this run now; nothing was written"
            return record
        staging = self._staging("ckpt%d" % step)
        try:
            link_tree(checkpoint_dir, staging)
            files = file_table(staging)
            snapshot = None
            if rollouts is not None and Path(rollouts).is_file():
                lines = complete_lines(rollouts, staging / ROLLOUTS)
                snapshot = {"lines": lines, "bytes": (staging / ROLLOUTS).stat().st_size,
                            "sha256": sha256_file(staging / ROLLOUTS)}
            target = "%s/checkpoint-%d" % (self.rel, step)
            self.ours.add(step)
            copied = self.store.copy_verify(staging, target)
            record.update(copy=_brief(copied), bytes=copied.get("bytes"), files=copied.get("files"))
            if not copied.get("ok"):
                record["reason"] = copied.get("reason")
                return record
            marker = {"schema": "p3-drive-verified-v1", "run": self.run_name, "key": self.key, "step": step,
                      "job": self.job_id, "files": files, "rollouts": snapshot, "verified_utc": utc(),
                      "copy_seconds": copied.get("copy_seconds"), "check_seconds": copied.get("check_seconds")}
            written = self.store.put_json(target + "/" + VERIFIED, marker)
            if not written.get("ok"):
                record["reason"] = "marker not written: %s" % written.get("reason")
                return record
            record.update(ok=True, marker=VERIFIED, retained=self.retain(step))
            return record
        except Exception as exc:  # a Drive problem never stops the training (D31); it is reported
            record["reason"] = "%s: %s" % (type(exc).__name__, str(exc)[:300])
            return record
        finally:
            shutil.rmtree(str(staging), ignore_errors=True)
            record["seconds"] = round(time.time() - started, 1)

    def checkpoints(self):
        """{step: has marker} of the checkpoint directories on Drive, or None when the listing failed."""
        entries = self.store.tree(self.rel, depth=2)
        if entries is None:
            return None
        found = {}
        for entry in entries:
            parts = entry["Path"].split("/")
            match = CHECKPOINT.match(parts[0])
            if not match:
                continue
            step = int(match.group(1))
            found.setdefault(step, False)
            if len(parts) == 2 and parts[1] == VERIFIED:
                found[step] = True
        return found

    def _marker(self, step):
        marker, status = self.store.get_json("%s/checkpoint-%d/%s" % (self.rel, step, VERIFIED))
        if marker is None:
            return None, status
        if marker.get("key") != self.key or marker.get("step") != step:
            return None, "belongs to another configuration"
        return marker, "ok"

    def retain(self, newest):
        """Purge checkpoint directories older than ``newest``, keeping the newest ``keep`` verified ones. A directory
        is purged only if it is attributable to this run: written or restored by this object, or carrying a marker
        with this key. Anything else (another configuration, a dead job's partial upload) is left alone."""
        found = self.checkpoints()
        if found is None:
            return {"ok": False, "reason": "could not list the run directory"}
        verified = sorted(step for step, ok in found.items() if ok and step <= newest)
        keep = set(verified[-self.keep:]) | {newest}
        purged, failed, foreign = [], [], []
        for step in sorted(found):
            if step >= newest or step in keep:
                continue
            ours = step in self.ours or (found[step] and self._marker(step)[0] is not None)
            if not ours:
                foreign.append(step)
                continue
            result = self.store.purge("%s/checkpoint-%d" % (self.rel, step))
            (purged if result["ok"] else failed).append(step)
        return {"ok": not failed, "purged": purged, "failed": failed, "kept": sorted(keep), "left_alone": foreign}

    def latest_verified(self):
        """(step, marker) of the newest checkpoint whose marker has this key, or (None, reason)."""
        if self.key is None:
            return None, "the run's key is unknown"
        found = self.checkpoints()
        if found is None:
            return None, "could not list %s" % self.rel
        for step in sorted((s for s, ok in found.items() if ok), reverse=True):
            marker, status = self._marker(step)
            if marker is None:
                log("checkpoint-%d of %s ignored (%s)" % (step, self.run_name, status))
                continue
            return step, marker
        return None, "no verified checkpoint"

    def restore(self, step, marker, out_dir):
        """Download checkpoint-<step> into ``out_dir`` (must be empty or absent), check every file against the
        marker, and rebuild rollouts.jsonl from the snapshot without the steps after the checkpoint."""
        out_dir = Path(out_dir)
        step = int(step)
        record = {"step": step, "ok": False, "started_utc": utc()}
        started = time.time()
        if out_dir.exists() and any(out_dir.iterdir()):
            record["reason"] = "%s is not empty" % out_dir
            return record
        download = out_dir.parent / (".restore-%s-%d" % (out_dir.name, step))
        shutil.rmtree(str(download), ignore_errors=True)
        try:
            fetched = self.store.fetch_verify("%s/checkpoint-%d" % (self.rel, step), download)
            record["fetch"] = _brief(fetched)
            if not fetched.get("ok"):
                record["reason"] = fetched.get("reason")
                return record
            got = file_table(download, skip={VERIFIED, ROLLOUTS})
            expected = marker.get("files") or {}
            if got != expected:
                missing = sorted(set(expected) - set(got))
                changed = sorted(k for k in got if expected.get(k) != got[k])
                record["reason"] = "downloaded files differ from the marker (missing %s, changed or extra %s)" % (
                    missing[:5], changed[:5])
                return record
            kept = dropped = 0
            snapshot = download / ROLLOUTS
            if snapshot.is_file() and (marker.get("rollouts") or {}).get("sha256") not in (None, sha256_file(snapshot)):
                record["reason"] = "the rollouts snapshot differs from the marker"
                return record
            out_dir.mkdir(parents=True, exist_ok=True)
            checkpoint = out_dir / ("checkpoint-%d" % step)
            checkpoint.mkdir()
            for rel in got:
                target = checkpoint / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                os.replace(str(download / rel), str(target))
            if snapshot.is_file():
                kept, dropped = rollouts_before(snapshot, out_dir / ROLLOUTS, step)
            self.ours.add(step)
            note = {"run": self.run_name, "step": step, "marker": marker, "restored_utc": utc(), "job": self.job_id,
                    "rollouts_kept": kept, "rollouts_dropped_after_checkpoint": dropped}
            (out_dir / RESTORED_NOTE).write_text(json.dumps(note, indent=2), encoding="utf-8")
            record.update(ok=True, path=str(checkpoint), files=len(got), rollouts_kept=kept,
                          rollouts_dropped_after_checkpoint=dropped)
            return record
        except Exception as exc:
            record["reason"] = "%s: %s" % (type(exc).__name__, str(exc)[:300])
            return record
        finally:
            shutil.rmtree(str(download), ignore_errors=True)
            record["seconds"] = round(time.time() - started, 1)

    def upload_final(self, out_dir, global_step):
        """Copy final/ and the run files, verify, then write COMPLETED.json (the run's last Drive write)."""
        out_dir = Path(out_dir)
        record = {"ok": False, "started_utc": utc()}
        started = time.time()
        if not (out_dir / "final").is_dir():
            record["reason"] = "no final/ directory"
            return record
        if self.key is None:
            record["reason"] = "the run's key is unknown; nothing was written"
            return record
        if not self._guarded():
            record["reason"] = "another job holds this run now; nothing was written"
            return record
        staging = self._staging("final")
        try:
            link_tree(out_dir / "final", staging / "final")
            for name in RUN_FILES:
                if (out_dir / name).is_file():
                    shutil.copy2(str(out_dir / name), str(staging / name))
            lines = complete_lines(out_dir / ROLLOUTS, staging / ROLLOUTS)
            files = file_table(staging)
            copied = self.store.copy_verify(staging, self.rel)
            record.update(copy=_brief(copied), files=len(files), bytes=copied.get("bytes"))
            if not copied.get("ok"):
                record["reason"] = copied.get("reason")
                return record
            marker = {"schema": "p3-run-completed-v1", "run": self.run_name, "key": self.key,
                      "global_step": int(global_step), "job": self.job_id, "files": files, "rollouts_lines": lines,
                      "completed_utc": utc()}
            written = self.store.put_json(self.rel + "/" + COMPLETED, marker)
            record.update(ok=bool(written.get("ok")), marker=COMPLETED if written.get("ok") else None)
            if not written.get("ok"):
                record["reason"] = "COMPLETED.json not written: %s" % written.get("reason")
            return record
        except Exception as exc:
            record["reason"] = "%s: %s" % (type(exc).__name__, str(exc)[:300])
            return record
        finally:
            shutil.rmtree(str(staging), ignore_errors=True)
            record["seconds"] = round(time.time() - started, 1)


# ---- run status, claims, failures --------------------------------------------------------------------------------

def run_status(store, rel, key):
    """What Drive says about one run: completed / failed / foreign / started / new / unknown, plus claims, failures
    and verified checkpoints. ``foreign``: a final marker with another key (left alone, reported)."""
    entries = store.tree(rel, depth=2)
    if entries is None:
        return {"state": "unknown", "reason": "could not list %s" % rel, "claims": [], "failures": [],
                "checkpoints": []}
    names = {e["Path"] for e in entries}
    status = {"state": "new", "claims": [],
              "failures": sorted(n for n in names if n.startswith("failures/") and n.endswith(".json")),
              "checkpoints": sorted(int(CHECKPOINT.match(n.split("/")[0]).group(1)) for n in names
                                    if n.endswith("/" + VERIFIED) and CHECKPOINT.match(n.split("/")[0]))}
    for name in sorted(n for n in names if n.startswith("claims/") and n.endswith(".json")):
        claim, why = store.get_json(rel + "/" + name)
        if claim is not None:
            status["claims"].append(claim)
        else:
            log("claim %s/%s unreadable (%s)" % (rel, name, why))
    for marker_name, state in ((COMPLETED, "completed"), (FAILED, "failed")):
        if marker_name in names:
            marker, why = store.get_json(rel + "/" + marker_name)
            if marker is None or marker.get("key") != key:
                return dict(status, state="foreign", reason="%s is unreadable or has another key (%s)"
                            % (marker_name, why))
            return dict(status, state=state, marker=marker)
    if status["checkpoints"] or status["failures"] or STARTED in names:
        status["state"] = "started"  # "already started" runs are resumed even after the cutoff (section 10)
    return status


def live_claims(claims, now, session, own_job, ttl=CLAIM_TTL_SECONDS):
    """Claims that may still belong to a running job. A claim made from this job's session name is dead unless it is
    this job's own: a Colab session runs one kernel job at a time, and this job is the one running now."""
    live = []
    for claim in claims:
        if claim.get("job") == own_job:
            live.append(claim)
            continue
        if session and claim.get("session") == session:
            continue
        if now - float(claim.get("heartbeat_epoch") or 0) < ttl:
            live.append(claim)
    return live


def winner(claims):
    return min(claims, key=lambda c: (float(c.get("claimed_epoch") or 0), str(c.get("job")))) if claims else None


class Claim(object):
    """This job's claim on one run: write, confirm (the earliest live claim wins), heartbeat, release."""

    def __init__(self, store, rel, job_id, session, task="train", settle=None, ttl=None):
        self.store, self.rel, self.job_id, self.session, self.task = store, rel, job_id, session, task
        self.settle = CLAIM_SETTLE_SECONDS if settle is None else settle
        self.ttl = CLAIM_TTL_SECONDS if ttl is None else ttl
        self.claimed_epoch = None
        self.name = "%s/claims/%s.json" % (rel, job_id)

    def _doc(self):
        now = time.time()
        return {"schema": "p3-s4-claim-v1", "job": self.job_id, "session": self.session, "task": self.task,
                "claimed_epoch": self.claimed_epoch, "claimed_utc": utc(self.claimed_epoch),
                "heartbeat_epoch": now, "heartbeat_utc": utc(now)}

    def acquire(self):
        """(True, None) when this job may run it; (False, reason) otherwise (our claim is then withdrawn)."""
        self.claimed_epoch = time.time()
        written = self.store.put_json(self.name, self._doc())
        if not written.get("ok"):
            return False, "could not write the claim: %s" % written.get("reason")
        time.sleep(self.settle)
        held, reason = self.holds()
        if not held:
            self.release()
        return held, reason

    def holds(self):
        entries = self.store.tree(self.rel + "/claims", depth=1)
        if entries is None:
            return False, "could not list the claims"
        claims = []
        for entry in entries:
            if entry.get("IsDir") or not entry["Path"].endswith(".json"):
                continue
            claim, _ = self.store.get_json("%s/claims/%s" % (self.rel, entry["Path"]))
            if claim is not None:
                claims.append(claim)
        first = winner(live_claims(claims, time.time(), self.session, self.job_id, self.ttl))
        if first is None or first.get("job") != self.job_id:
            return False, "run held by job %s (session %s, last heartbeat %s)" % (
                (first or {}).get("job"), (first or {}).get("session"), (first or {}).get("heartbeat_utc"))
        return True, None

    def heartbeat(self):
        return self.store.put_json(self.name, self._doc())

    def release(self):
        return self.store.delete(self.name)


def record_failure(store, rel, job_id, attempt, record):
    return store.put_json("%s/failures/%s-%d.json" % (rel, job_id, int(attempt)), record)


__all__ = ["CLAIM_TTL_SECONDS", "COMPLETED", "Claim", "FAILED", "HEARTBEAT_SECONDS", "RESTORED_NOTE", "ROLLOUTS",
           "RunDrive", "STARTED", "Store", "VERIFIED", "complete_lines", "experiment_base", "file_table", "live_claims",
           "percentile", "record_failure", "rollouts_before", "run_rel", "run_status", "utc", "winner"]
