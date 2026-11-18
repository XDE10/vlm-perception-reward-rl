"""Publish and read back the fixed dev metrics before checkpoint commitment."""

import json
import math
from pathlib import Path
import re
import subprocess
import sys
from tempfile import TemporaryDirectory


FREQUENCY = 25
METRICS = {"reward_score", "accuracy_reward", "format_reward", "overall_reward"}


def read_metrics(text, step):
    ansi = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
    sections = {}
    current = None
    in_validation = False
    for line in ansi.sub("", text).splitlines():
        match = re.search(r"\(Runner pid=\d+\) (.*)$", line)
        if not match:
            continue
        line = match[1]
        header = re.fullmatch(r"Step (\d+)", line)
        if header:
            current = int(header[1])
            in_validation = False
        elif line == "val:":
            sections[current] = {}
            in_validation = True
        elif in_validation and line.startswith("  "):
            name, separator, value = line.strip().partition(":")
            if separator and name in METRICS:
                sections[current][name] = float(value)
        else:
            in_validation = False
    return sections.get(step, {})


def validate_record(record, step, identity):
    metrics = record.get("metrics", {})
    if (record.get("step") != step or record.get("identity") != identity
            or set(metrics) != METRICS
            or not all(type(value) in (int, float) and math.isfinite(value)
                       for value in metrics.values())):
        raise RuntimeError(f"Missing or invalid fixed-dev metrics at step {step}")


def result_path(drive, step):
    return f"{drive}/formal-validation/global_step_{step}.json"


def publish(log, evidence, drive, since, checkpoint, read_drive):
    manifest = json.loads((checkpoint / "manifest.json").read_text())
    through = manifest["global_step"]
    identity = manifest["identity"]
    for step in range((since // FREQUENCY + 1) * FREQUENCY, through + 1, FREQUENCY):
        path = evidence / f"validation-step-{step}.json"
        remote = result_path(drive, step)
        if path.exists():
            validate_record(json.loads(path.read_bytes()), step, identity)
            continue
        record = {"step": step, "identity": identity,
                  "metrics": read_metrics(log.read_text(errors="replace"), step)}
        validate_record(record, step, identity)
        payload = (json.dumps(record, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
        temporary = path.with_suffix(".tmp")
        temporary.write_bytes(payload)
        subprocess.run(["rclone", "copyto", str(temporary), remote], check=True, timeout=120)
        if read_drive(remote) != payload:
            raise RuntimeError(f"Drive readback differs for fixed-dev results at step {step}")
        temporary.replace(path)
        print(f"FORMAL_VALIDATION_PERSISTED step={step}", flush=True)


def archive_validation_model(drive, remote, manifest, rclone):
    step = manifest["global_step"]
    model_files = {
        name: record
        for name, record in manifest["files"].items()
        if name == "actor/model_world_size_1_rank_0.pt"
        or re.fullmatch(r"actor/huggingface/[A-Za-z0-9_.-]+", name)
    }
    required = {
        "actor/model_world_size_1_rank_0.pt", "actor/huggingface/config.json",
        "actor/huggingface/tokenizer.json", "actor/huggingface/preprocessor_config.json",
    }
    if not required.issubset(model_files):
        raise RuntimeError(f"Missing weights or processor files for milestone {step}")
    validation = rclone("cat", result_path(drive, step))
    validate_record(json.loads(validation), step, manifest["identity"])
    archive = f"{drive}/formal-model-archives/global_step_{step}"
    metadata = {
        "global_step": step,
        "identity": manifest["identity"],
        "files": model_files,
        "weight_format": "FSDP world size 1",
        "validation_file": "validation.json",
    }
    record = (json.dumps(metadata, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()
    with TemporaryDirectory(prefix="formal-model-archive-") as folder:
        folder = Path(folder)
        files = folder / "files.txt"
        files.write_text("".join(f"{name}\n" for name in sorted(model_files)))
        rclone("copy", remote, archive, "--files-from-raw", str(files), timeout=600)
        rclone("check", remote, archive, "--files-from-raw", str(files), "--one-way", timeout=300)
        for name, data in (("validation.json", validation), ("ARCHIVED.json", record)):
            path = folder / name
            path.write_bytes(data)
            rclone("copyto", str(path), f"{archive}/{name}")
            if rclone("cat", f"{archive}/{name}") != data:
                raise RuntimeError(f"Readback differs for {name} at milestone {step}")
    expected = {name: item["bytes"] for name, item in model_files.items()}
    expected.update({"validation.json": len(validation), "ARCHIVED.json": len(record)})
    saved = json.loads(rclone("lsjson", "--recursive", "--files-only", archive))
    if len(saved) != len(expected) or {item["Path"]: item["Size"] for item in saved} != expected:
        raise RuntimeError(f"Archive files differ from manifest at milestone {step}")
    print(f"FORMAL_MILESTONE_ARCHIVED step={step}", flush=True)


def retire_checkpoints(drive, checkpoint):
    """Keep two resumable checkpoints and archive older milestones after readback."""
    root = f"{drive}/formal-checkpoints"
    local = json.loads((checkpoint / "manifest.json").read_text())
    newest = local["global_step"]

    def rclone(*args, timeout=45):
        return subprocess.check_output(
            ["rclone", *args, "--retries", "1"], timeout=timeout,
        )

    def read_marker(step):
        remote = f"{root}/global_step_{step}"
        data = rclone("cat", f"{remote}/PERSISTED.json")
        marker = json.loads(data)
        if (marker.get("step") != step or marker.get("verified") is not True
                or marker.get("remote") != remote):
            raise RuntimeError(f"Invalid Drive checkpoint marker at step {step}")
        return remote, data, marker

    def verify(step):
        remote, marker_bytes, _ = read_marker(step)
        manifest_bytes = rclone("cat", f"{remote}/manifest.json")
        manifest = json.loads(manifest_bytes)
        if (manifest["identity"] != local["identity"] or manifest["global_step"] != step
                or manifest["optimizer_steps"] != 4 * step or manifest["scheduler_steps"] != step
                or (step == newest and manifest != local)):
            raise RuntimeError(f"Unexpected checkpoint identity or state at step {step}")
        expected = {name: record["bytes"] for name, record in manifest["files"].items()}
        expected.update({"manifest.json": len(manifest_bytes), "PERSISTED.json": len(marker_bytes)})
        files = json.loads(rclone("lsjson", "--recursive", "--files-only", remote))
        if len(files) != len(expected) or {item["Path"]: item["Size"] for item in files} != expected:
            raise RuntimeError(f"Checkpoint files differ from manifest at step {step}")

    listing = rclone("lsf", "--dirs-only", root).decode()
    steps = sorted({int(n) for n in re.findall(r"^global_step_([1-9]\d*)/$", listing, re.M)}, reverse=True)
    if len(steps) < 3 or steps[0] != newest:
        return
    candidates = [step for step in steps[2:] if step > 8]
    if not candidates:
        return
    verify(newest)
    verify(steps[1])
    for step in candidates:
        try:
            remote, _, marker = read_marker(step)
        except subprocess.CalledProcessError:
            continue
        milestone = step % FREQUENCY == 0
        retention = "archive" if milestone else "rolling"
        if marker.get("retention") != retention:
            continue
        manifest = json.loads(rclone("cat", f"{remote}/manifest.json"))
        if manifest["identity"] != local["identity"] or manifest["global_step"] != step:
            raise RuntimeError(f"Unexpected older checkpoint identity at step {step}")
        if milestone:
            archive_validation_model(drive, remote, manifest, rclone)
        rclone("purge", remote, "--drive-use-trash=false")
        print(f"FORMAL_CHECKPOINT_RETIRED step={step}", flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "retire":
        retire_checkpoints(sys.argv[2], Path(sys.argv[3]))
    else:
        evidence, drive, since, checkpoint = sys.argv[1:]
        evidence = Path(evidence)
        publish(
            evidence / "continuous.log", evidence, drive, int(since), Path(checkpoint),
            lambda remote: subprocess.check_output(["rclone", "cat", remote], timeout=45),
        )
