#!/usr/bin/env bash
# Project 3 Colab launcher (WSL2 / Linux / macOS). Usage:
#   bash colab/launch.sh check                     # verify local prerequisites, data, Colab auth, git push access
#   bash colab/launch.sh preflight [options]       # run the GPU preflight on a fresh Colab VM
#   bash colab/launch.sh collect <run_id>          # reattach after a disconnect: wait, fetch, stop VM, push
#   bash colab/launch.sh push <run_id>             # (re)push fetched results to the results/<run_id> branch
#   bash colab/launch.sh stop <run_id>             # release the VM of a run
#   bash colab/launch.sh list                      # local runs and their last known state
# Options: --gpu A100|H100|G4|L4  --keep (do not stop the VM)  --no-vllm  --allow-dirty  --dry-run
# Settings (environment or .colab_local.env): P3_DATA_ROOT, P3_GPU, COLAB_GLOBAL_FLAGS, P3_POLL_SECONDS.
# See colab/README.md.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
if [[ -f "$ROOT/.colab_local.env" ]]; then
  # shellcheck disable=SC1091
  source "$ROOT/.colab_local.env"
fi
COLAB_BIN="${P3_COLAB_BIN:-colab}"
read -r -a COLAB_FLAGS <<< "${COLAB_GLOBAL_FLAGS:-}"
REMOTE="/content/p3"
CACHE="$ROOT/.colab_cache"
RUNS="$ROOT/.colab_runs"
POLL="${P3_POLL_SECONDS:-120}"
PY="${P3_PYTHON:-python3}"
DATA_ROOT="${P3_DATA_ROOT:-$ROOT/data}"
GPU="${P3_GPU:-A100}"
RUN_LOG=/dev/null
SESSION=""
RUN_ID=""
RUN_DIR=""
JOB_STARTED=0
RESULTS_FETCHED=0
SESSION_STOPPED=0
KEEP=0

log() { printf '[launch %s] %s\n' "$(date +%H:%M:%S)" "$*" | tee -a "$RUN_LOG" >&2; }
die() { log "ERROR: $*"; exit 1; }
colab_() { "$COLAB_BIN" ${COLAB_FLAGS[@]+"${COLAB_FLAGS[@]}"} "$@"; }
need() { command -v "$1" >/dev/null 2>&1 || die "missing command '$1' (see colab/README.md)"; }

retry() {
  local tries=$1 i
  shift
  for ((i = 1; i <= tries; i++)); do
    if "$@"; then return 0; fi
    log "attempt $i/$tries failed: $*"
    sleep $((i * 15))
  done
  return 1
}

repo_web_url() {
  local url
  url="$(git remote get-url origin 2>/dev/null || true)"
  url="${url%.git}"
  url="$(printf '%s' "$url" | sed -E 's#^git@github.com:#https://github.com/#; s#^ssh://git@github.com/#https://github.com/#')"
  printf '%s' "$url"
}

check_python() {
  "$PY" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)' || die "$PY must be Python >= 3.8"
}

stop_session() {
  if [[ -n "$SESSION" && "$SESSION_STOPPED" != 1 ]]; then
    log "releasing VM $SESSION"
    colab_ stop -s "$SESSION" </dev/null >/dev/null 2>&1 || log "colab stop failed; check 'colab sessions' and stop it manually"
    SESSION_STOPPED=1
    printf 'stopped\n' > "$RUN_DIR/state" 2>/dev/null || true
  fi
}

on_exit() {
  local rc=$?
  if [[ -n "$SESSION" && "$SESSION_STOPPED" != 1 && "$KEEP" != 1 ]]; then
    if [[ "$JOB_STARTED" == 1 && "$RESULTS_FETCHED" != 1 ]]; then
      log "the job keeps running on the VM; reattach with: bash colab/launch.sh collect $RUN_ID"
      log "to release the VM instead: bash colab/launch.sh stop $RUN_ID"
    else
      stop_session
    fi
  fi
  exit "$rc"
}

remote_status_line() {
  local target="$RUN_DIR/remote_status.json"
  if colab_ download -s "$SESSION" "$REMOTE/out/$RUN_ID/status.json" "$target" </dev/null >/dev/null 2>&1; then
    "$PY" -m scripts.colab.local_tools status-line "$target"
    return 0
  fi
  return 1
}

poll_until_done() {
  local fails=0 state
  while true; do
    if line="$(remote_status_line)"; then
      fails=0
      log "remote: $line"
      state="$("$PY" -m scripts.colab.local_tools field "$RUN_DIR/remote_status.json" state)"
      [[ "$state" == "done" ]] && return 0
    else
      fails=$((fails + 1))
      log "could not read remote status ($fails/15)"
      if ((fails >= 15)); then return 1; fi
    fi
    sleep "$POLL"
  done
}

wait_bootstrap() {
  local fails=0 target="$RUN_DIR/bootstrap.json"
  while true; do
    if colab_ download -s "$SESSION" "$REMOTE/state/bootstrap.json" "$target" </dev/null >/dev/null 2>&1 &&
      [[ "$("$PY" -m scripts.colab.local_tools field "$target" run_id)" == "$RUN_ID" ]]; then
      [[ "$("$PY" -m scripts.colab.local_tools field "$target" ok)" == "True" ]] && return 0
      log "bootstrap failed: $("$PY" -m scripts.colab.local_tools field "$target" error | head -c 600)"
      return 1
    fi
    fails=$((fails + 1))
    if ((fails >= 40)); then return 1; fi
    log "waiting for bootstrap to finish on the VM ($fails)"
    sleep "$POLL"
  done
}

fetch_results() {
  log "fetching results"
  retry 5 colab_ download -s "$SESSION" "$REMOTE/out/$RUN_ID.done.json" "$RUN_DIR/done.json" </dev/null >/dev/null ||
    die "could not download done.json"
  mkdir -p "$RUN_DIR/parts"
  local part
  for part in $("$PY" -m scripts.colab.local_tools parts "$RUN_DIR/done.json"); do
    retry 5 colab_ download -s "$SESSION" "$REMOTE/out/$part" "$RUN_DIR/parts/$part" </dev/null >/dev/null ||
      die "could not download $part"
  done
  "$PY" -m scripts.colab.local_tools join "$RUN_DIR/done.json" "$RUN_DIR/parts" "$RUN_DIR/results.tar.gz" >/dev/null
  rm -rf "$RUN_DIR/results"
  "$PY" -m scripts.colab.local_tools extract "$RUN_DIR/results.tar.gz" "$RUN_DIR/results"
  colab_ download -s "$SESSION" "$REMOTE/out/$RUN_ID/status.json" "$RUN_DIR/results/$RUN_ID/status.json" \
    </dev/null >/dev/null 2>&1 || true
  rm -rf "$RUN_DIR/parts"
  RESULTS_FETCHED=1
  printf 'fetched\n' > "$RUN_DIR/state"
  log "results in $RUN_DIR/results/$RUN_ID (overall: $("$PY" -m scripts.colab.local_tools field "$RUN_DIR/done.json" overall))"
}

push_results() {
  local run_id=$1 run_dir="$RUNS/$1"
  local src="$run_dir/results/$run_id"
  [[ -d "$src" ]] || die "no fetched results for $run_id in $run_dir"
  local commit day task branch wt dest overall
  commit="$(cat "$run_dir/commit")"
  day="$(printf '%s' "$run_id" | sed -E 's/^.*-([0-9]{8})T[0-9]{6}Z-.*$/\1/')"
  task="$(cat "$run_dir/task")"
  overall="$("$PY" -m scripts.colab.local_tools field "$run_dir/done.json" overall)"
  branch="results/$run_id"
  wt="$CACHE/worktree-$run_id"
  git worktree remove --force "$wt" >/dev/null 2>&1 || true
  git worktree add -q -B "$branch" "$wt" "$commit"
  dest="$wt/reports/colab_runs_${day}/$run_id"
  mkdir -p "$dest/_local"
  cp -R "$src/." "$dest/"
  for f in launch.log bootstrap.log job.log usage_before.txt usage_after.txt local.json dirty.diff colab_version.txt; do
    [[ -f "$run_dir/$f" ]] && cp "$run_dir/$f" "$dest/_local/"
  done
  local large
  large="$(find "$dest" -type f -size +25M -print)"
  if [[ -n "$large" ]]; then
    printf '%s\n' "$large" | sed "s#^$dest/##" > "$dest/SKIPPED_LARGE_FILES.txt"
    printf '%s\n' "$large" | while IFS= read -r f; do rm -f "$f"; done
    log "files over 25 MB were kept locally only (listed in SKIPPED_LARGE_FILES.txt)"
  fi
  local who=()
  if [[ -z "$(git config user.email || true)" ]]; then
    who=(-c user.name="p3-colab-launcher" -c user.email="p3-colab-launcher@users.noreply.github.com")
  fi
  # -f: the repository ignores *.log globally, but run logs are evidence and must travel with the results
  git -C "$wt" add -f "reports/colab_runs_${day}/$run_id"
  git -C "$wt" ${who[@]+"${who[@]}"} commit -q -m "results($task): $run_id overall=$overall"
  if git -C "$wt" push -q -u origin "$branch"; then
    printf 'pushed\n' > "$run_dir/state"
    log "pushed results: $(repo_web_url)/tree/$branch"
  else
    log "git push failed. Results are safe in $src. Fix git credentials, then: bash colab/launch.sh push $run_id"
    git worktree remove --force "$wt" >/dev/null 2>&1 || true
    return 1
  fi
  git worktree remove --force "$wt" >/dev/null 2>&1 || true
}

print_summary() {
  local md="$RUN_DIR/results/$RUN_ID/summary.md"
  if [[ -f "$md" ]]; then
    printf '\n'
    sed -n '1,30p' "$md"
    printf '\n(full summary: %s)\n' "$md"
  fi
}

cmd_check() {
  local ok=1
  need git
  need tar
  need "$PY"
  check_python
  if command -v "$COLAB_BIN" >/dev/null 2>&1; then
    log "colab CLI: $(colab_ version 2>/dev/null | tail -n 1)"
    if colab_ sessions </dev/null >/dev/null 2>&1; then log "colab auth: OK"; else log "colab auth: FAILED (run 'colab sessions' to see why)"; ok=0; fi
    colab_ usage </dev/null 2>/dev/null | tail -n 5 || true
  else
    log "colab CLI not found on PATH"
    ok=0
  fi
  log "data root: $DATA_ROOT"
  mkdir -p "$CACHE"
  "$PY" -m scripts.colab.pack_private_data --data-root "$DATA_ROOT" --check-only > "$CACHE/check.json" 2>&1 || true
  log "data check: $(head -c 600 "$CACHE/check.json")"
  grep -q '"ok": true' "$CACHE/check.json" || ok=0
  if git push --dry-run -q origin "HEAD:refs/heads/results/_push_check" >/dev/null 2>&1; then
    log "git push access: OK"
  else
    log "git push access: FAILED (configure credentials, e.g. 'gh auth login' or a credential helper)"
    ok=0
  fi
  if [[ "$ok" == 1 ]]; then log "all checks passed"; else die "some checks failed (see above)"; fi
}

cmd_run() {
  local task=$1 vllm=1 dirty_ok=0 dry=0
  shift
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --gpu) GPU="$2"; shift 2 ;;
      --keep) KEEP=1; shift ;;
      --no-vllm) vllm=0; shift ;;
      --allow-dirty) dirty_ok=1; shift ;;
      --dry-run) dry=1; shift ;;
      *) die "unknown option $1" ;;
    esac
  done
  need git
  need tar
  need "$PY"
  need "$COLAB_BIN"
  check_python
  mkdir -p "$CACHE" "$RUNS"
  RUN_ID="${task}-$(date -u +%Y%m%dT%H%M%SZ)-$(od -An -N2 -tx1 /dev/urandom | tr -d ' \n')"
  RUN_DIR="$RUNS/$RUN_ID"
  mkdir -p "$RUN_DIR"
  RUN_LOG="$RUN_DIR/launch.log"
  SESSION="p3-${task}-$(date -u +%m%d%H%M)-${RUN_ID##*-}"
  printf '%s\n' "$SESSION" > "$RUN_DIR/session"
  printf '%s\n' "$task" > "$RUN_DIR/task"
  printf 'preparing\n' > "$RUN_DIR/state"
  local commit dirty=0 code
  commit="$(git rev-parse HEAD)"
  printf '%s\n' "$commit" > "$RUN_DIR/commit"
  local watched=(src scripts configs colab tests tools requirements)
  if ! git diff --quiet --ignore-cr-at-eol HEAD -- "${watched[@]}" || [[ -n "$(git ls-files --others --exclude-standard -- "${watched[@]}")" ]]; then
    dirty=1
    if [[ "$dirty_ok" != 1 ]]; then
      git status --short -- "${watched[@]}" | head -n 20 >&2
      RUN_LOG=/dev/null
      rm -rf "$RUN_DIR"
      SESSION=""
      die "uncommitted changes in code directories; commit them, or rerun with --allow-dirty (recorded in the results)"
    fi
    git diff HEAD -- "${watched[@]}" > "$RUN_DIR/dirty.diff" || true
    log "running with uncommitted changes (diff saved to the results)"
  fi
  log "run $RUN_ID (task $task, commit ${commit:0:12}, GPU $GPU)"
  if [[ "$dirty" == 1 ]]; then
    code="$CACHE/code_${commit:0:12}_dirty.tar.gz"
    git ls-files -co --exclude-standard -z | tar --null -czf "$code" -T -
  else
    code="$CACHE/code_${commit:0:12}.tar.gz"
    [[ -f "$code" ]] || git archive --format=tar.gz -o "$code" HEAD
  fi
  log "building private data pack from $DATA_ROOT"
  "$PY" -m scripts.colab.pack_private_data --data-root "$DATA_ROOT" --out "$CACHE" > "$RUN_DIR/pack.json" ||
    die "data pack failed: $(tail -c 800 "$RUN_DIR/pack.json")"
  log "data pack: $(head -c 300 "$RUN_DIR/pack.json")"
  local colab_version options local_json
  colab_version="$(colab_ version 2>/dev/null | tail -n 1 || true)"
  printf '%s\n' "$colab_version" > "$RUN_DIR/colab_version.txt"
  options="$("$PY" -c 'import json,sys; print(json.dumps({"vllm_probe": sys.argv[1] == "1", "dry_run": sys.argv[2] == "1", "gpu_requested": sys.argv[3]}))' "$vllm" "$dry" "$GPU")"
  local_json="$("$PY" -c 'import json,platform,sys; print(json.dumps({"colab_version": sys.argv[1], "data_root": sys.argv[2], "host": platform.platform(), "python": platform.python_version()}))' "$colab_version" "$DATA_ROOT")"
  printf '%s\n' "$local_json" > "$RUN_DIR/local.json"
  "$PY" -m scripts.colab.local_tools make-request --task "$task" --run-id "$RUN_ID" --code "$code" --commit "$commit" \
    --dirty "$dirty" --pack-json "$RUN_DIR/pack.json" --staging "$RUN_DIR/upload" --uploads "$RUN_DIR/uploads.tsv" \
    --options "$options" --local "$local_json" >/dev/null
  colab_ usage </dev/null > "$RUN_DIR/usage_before.txt" 2>&1 || true

  trap on_exit EXIT
  trap 'log "interrupted"; exit 130' INT TERM
  log "allocating Colab VM $SESSION ($GPU)"
  retry 3 colab_ new -s "$SESSION" --gpu "$GPU" </dev/null >> "$RUN_LOG" 2>&1 ||
    die "could not allocate a $GPU VM (quota or availability). Try later or with --gpu H100."
  printf 'allocated\n' > "$RUN_DIR/state"
  printf 'import os\nos.makedirs(os.path.join(os.environ.get("P3_REMOTE_ROOT", "/content/p3"), "inbox"), exist_ok=True)\nprint("[p3] inbox ready")\n' |
    colab_ exec -s "$SESSION" --timeout 600 >> "$RUN_LOG" 2>&1 || die "could not prepare the VM"
  local n=0 total local_path remote_name
  total="$(wc -l < "$RUN_DIR/uploads.tsv" | tr -d ' ')"
  while IFS=$'\t' read -r local_path remote_name; do
    n=$((n + 1))
    log "upload $n/$total $remote_name"
    retry 3 colab_ upload -s "$SESSION" "$local_path" "$REMOTE/inbox/$remote_name" </dev/null >/dev/null ||
      die "upload of $remote_name failed"
  done < "$RUN_DIR/uploads.tsv"
  rm -rf "$RUN_DIR/upload"

  log "bootstrap on the VM (environment install and model download; ~10-20 min)"
  colab_ exec -s "$SESSION" -f colab/kernel_bootstrap.py --timeout 14400 </dev/null 2>&1 | tee "$RUN_DIR/bootstrap.log" || true
  if ! grep -q "BOOTSTRAP_OK" "$RUN_DIR/bootstrap.log"; then
    if grep -q "BOOTSTRAP_FAILED" "$RUN_DIR/bootstrap.log" || ! wait_bootstrap; then
      die "bootstrap failed on the VM (see $RUN_DIR/bootstrap.log)"
    fi
  fi
  JOB_STARTED=1
  printf 'running\n' > "$RUN_DIR/state"
  log "job running on the VM; progress lines follow (Ctrl-C detaches, the job keeps running)"
  colab_ exec -s "$SESSION" -f colab/kernel_job.py --timeout 86400 </dev/null 2>&1 | tee "$RUN_DIR/job.log" || true
  if ! grep -q "JOB_DONE" "$RUN_DIR/job.log"; then
    log "lost the live connection; polling the VM every ${POLL}s"
    poll_until_done || die "the VM stopped answering; reattach later with: bash colab/launch.sh collect $RUN_ID"
  fi
  fetch_results
  if [[ "$KEEP" != 1 ]]; then stop_session; else log "--keep: VM $SESSION left running (stop it with: bash colab/launch.sh stop $RUN_ID)"; fi
  colab_ usage </dev/null > "$RUN_DIR/usage_after.txt" 2>&1 || true
  push_results "$RUN_ID" || true
  print_summary
  [[ "$("$PY" -m scripts.colab.local_tools field "$RUN_DIR/done.json" overall)" == "passed" ]] || exit 3
}

load_run() {
  RUN_ID="${1:?run id required (see: bash colab/launch.sh list)}"
  RUN_DIR="$RUNS/$RUN_ID"
  [[ -d "$RUN_DIR" ]] || die "unknown run $RUN_ID"
  RUN_LOG="$RUN_DIR/launch.log"
  SESSION="$(cat "$RUN_DIR/session")"
}

cmd_collect() {
  load_run "$1"
  need "$COLAB_BIN"
  JOB_STARTED=1
  trap on_exit EXIT
  log "reattaching to $SESSION"
  poll_until_done || die "the VM does not answer; it may have been reclaimed (check 'colab sessions')"
  fetch_results
  stop_session
  colab_ usage </dev/null > "$RUN_DIR/usage_after.txt" 2>&1 || true
  push_results "$RUN_ID" || true
  print_summary
}

cmd_list() {
  local d
  for d in "$RUNS"/*/; do
    [[ -d "$d" ]] || continue
    printf '%-48s %s\n' "$(basename "$d")" "$(cat "$d/state" 2>/dev/null || printf '?')"
  done
}

main() {
  local command="${1:-}"
  [[ -n "$command" ]] || { sed -n '2,12p' "$0"; exit 2; }
  shift
  case "$command" in
    check) cmd_check ;;
    preflight) cmd_run preflight "$@" ;;
    collect) cmd_collect "$@" ;;
    push) need git; check_python; load_run "$1"; push_results "$RUN_ID" ;;
    stop) load_run "$1"; need "$COLAB_BIN"; stop_session ;;
    list) cmd_list ;;
    *) sed -n '2,12p' "$0"; exit 2 ;;
  esac
}

main "$@"
