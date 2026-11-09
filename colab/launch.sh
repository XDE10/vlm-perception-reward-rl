#!/usr/bin/env bash
# Project 3 Colab launcher (WSL2 / Linux / macOS; run it with bash, also from zsh). Usage:
#   bash colab/launch.sh check                 verify local prerequisites, data, Colab auth, git push access
#   bash colab/launch.sh preflight [options]   run the GPU preflight (fresh VM, or --session NAME)
#   bash colab/launch.sh drive-check [options] cheap test of the optional Google Drive (rclone) setup
#   bash colab/launch.sh collect RUN_ID        reattach after a disconnect: wait, fetch, push (from GitHub if the VM is gone)
#   bash colab/launch.sh push RUN_ID           (re)push a run to its results/RUN_ID branch
#   bash colab/launch.sh stop RUN_ID           release the VM of a run
#   bash colab/launch.sh list                  local runs and their last known state
# Options: --gpu A100|H100|G4|L4   --session NAME (use a VM you prepared, see colab/README.md section 8)
#   --keep (do not release a VM this run created)   --release (also release a --session VM at the end)
#   --no-vm-push   --no-vllm   --allow-dirty   --dry-run
# Settings (environment or .colab_local.env): P3_DATA_ROOT, P3_GPU, COLAB_GLOBAL_FLAGS, P3_POLL_SECONDS,
#   P3_PART_MB, P3_UPLOAD_TRIES, P3_UPLOAD_BACKOFF, P3_UPLOAD_TIMEOUT, P3_RETRY_SLEEP, P3_CODE_SOURCE (auto|upload),
#   P3_VM_GH_CREDENTIALS (credential file on the VM, default /content/gh_credentials),
#   Drive: P3_DRIVE_MOUNT_CMD, P3_DRIVE_SETUP_FILE, P3_DRIVE_REMOTE, P3_DRIVE_DIR, P3_DRIVE_MOUNT.
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
PART_MB="${P3_PART_MB:-2}"
UPLOAD_TRIES="${P3_UPLOAD_TRIES:-6}"
UPLOAD_BACKOFF="${P3_UPLOAD_BACKOFF:-10}"
UPLOAD_TIMEOUT="${P3_UPLOAD_TIMEOUT:-600}"
RETRY_SLEEP="${P3_RETRY_SLEEP:-15}"
RUN_LOG=/dev/null
SESSION=""
RUN_ID=""
RUN_DIR=""
JOB_STARTED=0
RESULTS_FETCHED=0
SESSION_STOPPED=0
SESSION_HANDLED=0
PUSH_ON_FAILURE=0
KEEP=0
ATTACHED=0
RELEASE=0

log() { printf '[launch %s] %s\n' "$(date +%H:%M:%S)" "$*" | tee -a "$RUN_LOG" >&2; }
die() { log "ERROR: $*"; exit 1; }
need() { command -v "$1" >/dev/null 2>&1 || die "missing command '$1' (see colab/README.md)"; }
usage() { awk 'NR > 1 && /^#/ { sub(/^# ?/, ""); print; next } NR > 1 { exit }' "$0"; }
run_day() { printf '%s' "$1" | sed -E 's/^.*-([0-9]{8})T[0-9]{6}Z-.*$/\1/'; }

git_quiet() {
  # git calls that touch the network: never prompt for credentials, never hang longer than 5 minutes
  local limit=()
  command -v timeout >/dev/null 2>&1 && limit=(timeout 300)
  GIT_TERMINAL_PROMPT=0 GIT_SSH_COMMAND="${GIT_SSH_COMMAND:-ssh -o BatchMode=yes}" \
    ${limit[@]+"${limit[@]}"} git "$@" </dev/null
}
remote_branch_exists() { git_quiet ls-remote --exit-code -q origin "refs/heads/$1" >/dev/null 2>&1; }

# The Colab CLI sends uploads/downloads with no client timeout and does not enforce `exec --timeout` after the
# deadline, so every call gets a wall-clock limit from coreutils `timeout` when it is available (--foreground keeps
# Ctrl-C working). colab_t SECONDS args... ; colab_ args... uses 30 minutes.
TIMEOUT_CMD=()
if command -v timeout >/dev/null 2>&1 && timeout --foreground 5 true >/dev/null 2>&1; then
  TIMEOUT_CMD=(timeout --foreground)
fi
colab_t() {
  local seconds=$1
  shift
  if [[ ${#TIMEOUT_CMD[@]} -gt 0 ]]; then
    "${TIMEOUT_CMD[@]}" "$seconds" "$COLAB_BIN" ${COLAB_FLAGS[@]+"${COLAB_FLAGS[@]}"} "$@"
  else
    "$COLAB_BIN" ${COLAB_FLAGS[@]+"${COLAB_FLAGS[@]}"} "$@"
  fi
}
colab_() { colab_t 1800 "$@"; }

retry() {
  local tries=$1 i
  shift
  for ((i = 1; i <= tries; i++)); do
    if "$@"; then return 0; fi
    log "attempt $i/$tries failed: $*"
    ((i < tries)) && sleep $((i * RETRY_SLEEP))
  done
  return 1
}

repo_web_url() {
  local url
  url="$(git remote get-url origin 2>/dev/null || true)"
  url="${url%.git}"
  # drop any user:token@ part so credentials embedded in the remote URL are never printed or logged
  url="$(printf '%s' "$url" | sed -E 's#^git@github.com:#https://github.com/#; s#^ssh://git@github.com/#https://github.com/#;
    s#^(https?://)[^/@]+@#\1#')"
  printf '%s' "$url"
}

check_python() {
  "$PY" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)' || die "$PY must be Python >= 3.8"
}

stop_session() {
  if [[ -n "$SESSION" && "$SESSION_STOPPED" != 1 ]]; then
    log "releasing VM $SESSION"
    colab_t 300 stop -s "$SESSION" </dev/null >/dev/null 2>&1 || log "colab stop failed; check 'colab sessions' and stop it manually"
    SESSION_STOPPED=1
    SESSION_HANDLED=1
    printf 'stopped\n' > "$RUN_DIR/state" 2>/dev/null || true
  fi
}

# a VM this run created is released at the end (unless --keep); a VM you prepared (--session) only with --release
should_release() { [[ "$KEEP" != 1 && ( "$ATTACHED" != 1 || "$RELEASE" == 1 ) ]]; }

release_or_remind() {
  if should_release; then
    stop_session
  elif [[ "$ATTACHED" == 1 ]]; then
    log "your session $SESSION stays up and keeps using compute units; when you are done: colab stop -s $SESSION"
  else
    log "--keep: VM $SESSION left running (release it with: bash colab/launch.sh stop $RUN_ID)"
  fi
  SESSION_HANDLED=1
}

on_exit() {
  local rc=$?
  trap - EXIT
  # remember how far the run got before releasing the VM overwrites the state
  if [[ -n "$RUN_DIR" && -f "$RUN_DIR/state" ]]; then cp "$RUN_DIR/state" "$RUN_DIR/exit_state" 2>/dev/null || true; fi
  if [[ -n "$SESSION" && "$SESSION_HANDLED" != 1 ]]; then
    if [[ "$JOB_STARTED" == 1 && "$RESULTS_FETCHED" != 1 ]]; then
      log "the job keeps running on the VM; reattach with: bash colab/launch.sh collect $RUN_ID"
      [[ "$ATTACHED" == 1 ]] || log "to release the VM instead: bash colab/launch.sh stop $RUN_ID"
    else
      release_or_remind
    fi
  fi
  if [[ "$rc" != 0 && "$JOB_STARTED" != 1 && "$PUSH_ON_FAILURE" == 1 ]]; then
    # the run died before the job started (VM allocation, upload, bootstrap): publish the logs so they can be read
    # on GitHub instead of being copied out of the terminal (D39)
    printf '%s\n' "$rc" > "$RUN_DIR/exit_code"
    log "the run stopped before the job started; publishing its logs to results/$RUN_ID"
    ( push_results "$RUN_ID" ) || log "could not publish the logs; they are in $RUN_DIR"
  fi
  exit "$rc"
}

# --- uploads: small parts, captured CLI errors, backoff, then a remote SHA256 check of every part --------------
upload_part() {
  local local_path=$1 name=$2 attempt start rc last out="$RUN_DIR/upload_attempt.out"
  for ((attempt = 1; attempt <= UPLOAD_TRIES; attempt++)); do
    start=$(date +%s)
    rc=0
    colab_t "$UPLOAD_TIMEOUT" upload -s "$SESSION" "$local_path" "$REMOTE/inbox/$name" </dev/null > "$out" 2>&1 || rc=$?
    { printf '\n[%s] upload %s attempt %d (exit %s, %ss)\n' "$(date +%H:%M:%S)" "$name" "$attempt" "$rc" \
        "$(($(date +%s) - start))"; cat "$out"; } >> "$RUN_DIR/upload.log"
    if [[ "$rc" == 0 ]]; then
      printf '%s\t%s\n' "$name" "$(($(date +%s) - start))" >> "$RUN_DIR/upload_times.tsv"
      return 0
    fi
    if [[ "$rc" == 124 && ${#TIMEOUT_CMD[@]} -gt 0 ]]; then
      last="no answer within the ${UPLOAD_TIMEOUT}s limit, call ended (P3_UPLOAD_TIMEOUT)"
    else
      last="$(tail -n 2 "$out" | tr '\n' ' ' | "$PY" -m scripts.colab.local_tools redact-stdin | cut -c1-300)"
    fi
    log "upload of $name failed (attempt $attempt/$UPLOAD_TRIES after $(($(date +%s) - start))s): $last"
    ((attempt < UPLOAD_TRIES)) && sleep $((attempt < 4 ? attempt * UPLOAD_BACKOFF : 6 * UPLOAD_BACKOFF))
  done
  return 1
}

upload_list() {
  local tsv=$1 label=$2 n=0 total local_path name bytes started
  total="$(grep -c . "$tsv" || true)"
  [[ "$total" -gt 0 ]] || return 0
  started=$(date +%s)
  bytes=0
  while IFS=$'\t' read -r local_path name; do
    [[ -n "$name" ]] || continue
    n=$((n + 1))
    bytes=$((bytes + $(wc -c < "$local_path")))
    log "upload $label $n/$total $name ($(($(wc -c < "$local_path") / 1024)) KiB)"
    upload_part "$local_path" "$name" || die "upload of $name failed $UPLOAD_TRIES times (CLI output in $RUN_DIR/upload.log)"
  done < "$tsv"
  local seconds=$(($(date +%s) - started))
  log "uploaded $label: $((bytes / 1024)) KiB in ${seconds}s (~$((bytes / 1024 / (seconds > 0 ? seconds : 1))) KiB/s)"
}

inbox_listing() {
  # a failed listing must not look like "every part is missing" (that would re-upload everything)
  local i
  for ((i = 1; i <= 3; i++)); do
    colab_t 1200 exec -s "$SESSION" -f "$RUN_DIR/kernel/kernel_inbox.py" --timeout 900 </dev/null > "$RUN_DIR/inbox.log" 2>&1 || true
    grep -q '^\[p3\] INBOX ' "$RUN_DIR/inbox.log" && return 0
    log "could not list the uploaded files on the VM (attempt $i/3): $(tail -n 2 "$RUN_DIR/inbox.log" | tr '\n' ' ' |
      "$PY" -m scripts.colab.local_tools redact-stdin | cut -c1-200)"
    sleep $((i * 10))
  done
  return 1
}

verify_inbox() {
  local tsv=$1 round stale
  for round in 0 1 2 3; do
    inbox_listing || die "could not list the uploaded files on the VM (see $RUN_DIR/inbox.log)"
    stale="$("$PY" -m scripts.colab.local_tools inbox-diff "$tsv" "$RUN_DIR/inbox.log")"
    if [[ -z "$stale" ]]; then
      log "all uploaded parts verified on the VM (size and SHA256)"
      return 0
    fi
    ((round < 3)) || break
    log "re-uploading $(printf '%s\n' "$stale" | grep -c .) part(s) that are missing or damaged on the VM (repair round $((round + 1))/3)"
    printf '%s\n' "$stale" > "$RUN_DIR/stale.tsv"
    upload_list "$RUN_DIR/stale.tsv" "repair"
  done
  die "uploaded parts still differ on the VM after 3 repair rounds (see $RUN_DIR/upload.log)"
}

remote_status_line() {
  local target="$RUN_DIR/remote_status.json"
  if colab_t 600 download -s "$SESSION" "$REMOTE/out/$RUN_ID/status.json" "$target" </dev/null >/dev/null 2>&1; then
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
    if colab_t 600 download -s "$SESSION" "$REMOTE/state/bootstrap.json" "$target" </dev/null >/dev/null 2>&1 &&
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

run_bootstrap() {
  # each attempt gets its own log so a marker from an earlier attempt never decides a later one
  local attempt_log=$1
  : > "$attempt_log"
  colab_t 15000 exec -s "$SESSION" -f "$RUN_DIR/kernel/kernel_bootstrap.py" --timeout 14400 </dev/null 2>&1 |
    tee "$attempt_log" || true
  cat "$attempt_log" >> "$RUN_DIR/bootstrap.log"
}

download_file() {
  local remote_path=$1 local_path=$2
  printf '\n[%s] download %s\n' "$(date +%H:%M:%S)" "$remote_path" >> "$RUN_DIR/download.log"
  colab_t "$UPLOAD_TIMEOUT" download -s "$SESSION" "$remote_path" "$local_path" </dev/null >> "$RUN_DIR/download.log" 2>&1
}

mirror_branch_results() {
  # local copy of a run that is already on GitHub (pushed by the VM): no download through the Colab proxy
  local branch="results/$RUN_ID" tmp
  git_quiet fetch -q origin "+refs/heads/$branch:refs/remotes/origin/$branch" >/dev/null 2>&1 || return 1
  tmp="$RUN_DIR/results.mirror"
  rm -rf "$tmp"
  mkdir -p "$tmp"
  git archive "refs/remotes/origin/$branch" "reports/colab_runs_$(run_day "$RUN_ID")/$RUN_ID" | tar -x -C "$tmp" ||
    return 1
  [[ -d "$tmp/reports/colab_runs_$(run_day "$RUN_ID")/$RUN_ID" ]] || return 1
  rm -rf "$RUN_DIR/results"
  mkdir -p "$RUN_DIR/results"
  mv "$tmp/reports/colab_runs_$(run_day "$RUN_ID")/$RUN_ID" "$RUN_DIR/results/$RUN_ID"
  rm -rf "$tmp"
}

finish_from_github() {
  # the VM does not answer (reclaimed, or this machine lost the connection); a VM-side push may have published the run
  remote_branch_exists "results/$RUN_ID" || return 1
  log "the VM is not reachable, but results/$RUN_ID is on GitHub; using that copy"
  mirror_branch_results || return 1
  RESULTS_FETCHED=1
  printf 'fetched\n' > "$RUN_DIR/state"
  log "results in $RUN_DIR/results/$RUN_ID (overall: $(run_overall))"
}

run_overall() {
  local value=""
  [[ -f "$RUN_DIR/done.json" ]] && value="$(done_field overall 2>/dev/null || true)"
  [[ -z "$value" && -f "$RUN_DIR/results/$RUN_ID/summary.json" ]] &&
    value="$("$PY" -m scripts.colab.local_tools field "$RUN_DIR/results/$RUN_ID/summary.json" overall 2>/dev/null || true)"
  printf '%s' "${value:-unknown}"
}

fetch_results() {
  log "fetching results"
  if ! retry 5 download_file "$REMOTE/out/$RUN_ID.done.json" "$RUN_DIR/done.json"; then
    finish_from_github && return 0
    die "could not download done.json (CLI output in $RUN_DIR/download.log)"
  fi
  local from_branch=0
  if [[ "$(done_field github.ok)" == "True" ]]; then
    log "the VM pushed the results itself: $(repo_web_url)/tree/results/$RUN_ID"
    if mirror_branch_results; then
      from_branch=1
    else
      log "could not read that branch from here; downloading the results from the VM instead"
    fi
  elif [[ "$(done_field github.attempted)" == "True" ]]; then
    log "WARNING: the VM could not push the results ($(done_field github.reason | head -c 300)); pushing them from here"
  fi
  if [[ "$from_branch" != 1 ]]; then
    mkdir -p "$RUN_DIR/parts"
    local part
    for part in $("$PY" -m scripts.colab.local_tools parts "$RUN_DIR/done.json"); do
      retry 5 download_file "$REMOTE/out/$part" "$RUN_DIR/parts/$part" ||
        die "could not download $part (CLI output in $RUN_DIR/download.log)"
    done
    "$PY" -m scripts.colab.local_tools join "$RUN_DIR/done.json" "$RUN_DIR/parts" "$RUN_DIR/results.tar.gz" >/dev/null
    rm -rf "$RUN_DIR/results"
    "$PY" -m scripts.colab.local_tools extract "$RUN_DIR/results.tar.gz" "$RUN_DIR/results"
    rm -rf "$RUN_DIR/parts"
  fi
  colab_t 600 download -s "$SESSION" "$REMOTE/out/$RUN_ID/status.json" "$RUN_DIR/results/$RUN_ID/status.json" \
    </dev/null >/dev/null 2>&1 || true
  RESULTS_FETCHED=1
  printf 'fetched\n' > "$RUN_DIR/state"
  log "results in $RUN_DIR/results/$RUN_ID (overall: $(run_overall))"
  if [[ "$(done_field drive.attempted)" == "True" ]]; then
    if [[ "$(done_field drive.ok)" == "True" ]]; then
      log "Drive copy verified: $(done_field drive.target)"
    else
      log "WARNING: Drive copy failed: $(done_field drive.reason | head -c 300) (the results branch is unaffected)"
    fi
  elif [[ -n "$(done_field drive.mode)" && "$(done_field drive.mode)" != "none" ]]; then
    log "Drive copy skipped: $(done_field drive.reason | head -c 200)"
  fi
}

done_field() { "$PY" -m scripts.colab.local_tools field "$RUN_DIR/done.json" "$1"; }

push_results() {
  # Three cases, all on results/RUN_ID: (1) the branch is already on GitHub (the VM pushed it): add this machine's
  # logs as _local/ on top; (2) results were fetched: push results plus _local/; (3) the run stopped before the
  # job started: push _local/ and RUN_STOPPED_EARLY.txt so the failure can be read on GitHub.
  local run_id=$1 run_dir="$RUNS/$1"
  local src="$run_dir/results/$run_id"
  local commit day task branch wt dest overall mode
  commit="$(cat "$run_dir/commit")"
  day="$(run_day "$run_id")"
  task="$(cat "$run_dir/task")"
  overall="unknown"
  if [[ -f "$run_dir/done.json" ]]; then
    overall="$("$PY" -m scripts.colab.local_tools field "$run_dir/done.json" overall 2>/dev/null || printf 'unknown')"
  fi
  branch="results/$run_id"
  wt="$CACHE/worktree-$run_id"
  git worktree remove --force "$wt" >/dev/null 2>&1 || true
  if remote_branch_exists "$branch" && git_quiet fetch -q origin "+refs/heads/$branch:refs/remotes/origin/$branch"; then
    mode=append
    git worktree add -q -B "$branch" "$wt" "refs/remotes/origin/$branch"
  elif [[ -d "$src" ]]; then
    mode=full
    git worktree add -q -B "$branch" "$wt" "$commit"
  else
    mode=early
    git worktree add -q -B "$branch" "$wt" "$commit"
  fi
  dest="$wt/reports/colab_runs_${day}/$run_id"
  mkdir -p "$dest/_local"
  [[ "$mode" == full ]] && cp -R "$src/." "$dest/"
  if [[ "$mode" == early ]]; then
    {
      printf 'Run %s stopped before its job started.\n' "$run_id"
      printf 'stage reached: %s; exit code: %s\n' \
        "$(cat "$run_dir/exit_state" 2>/dev/null || cat "$run_dir/state" 2>/dev/null || printf '?')" \
        "$(cat "$run_dir/exit_code" 2>/dev/null || printf '?')"
      printf 'last errors from _local/launch.log:\n'
      grep 'ERROR' "$run_dir/launch.log" 2>/dev/null | tail -n 5 || true
    } > "$dest/RUN_STOPPED_EARLY.txt"
  fi
  # drive_mount.log stays local: the user's Drive tooling may print credentials
  for f in launch.log bootstrap.log job.log upload.log upload_times.tsv inbox.log download.log usage_before.txt \
    usage_after.txt local.json dirty.diff colab_version.txt done.json bootstrap.json pack.json; do
    [[ -f "$run_dir/$f" ]] && cp "$run_dir/$f" "$dest/_local/"
  done
  # CLI error messages contain request URLs with the runtime proxy token: never publish them unredacted
  local redacted
  redacted="$("$PY" -m scripts.colab.local_tools redact "$dest" --report "$dest/_local/REDACTIONS.txt")"
  [[ "$redacted" == 0 ]] || log "redacted $redacted credential-like string(s) before publishing (see _local/REDACTIONS.txt)"
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
  local message="results($task): $run_id overall=$overall"
  [[ "$mode" == append ]] && message="results($task): $run_id launcher logs (_local/)"
  [[ "$mode" == early ]] && message="results($task): $run_id stopped before the job (logs only)"
  # -f: the repository ignores *.log globally, but run logs are evidence and must travel with the results
  git -C "$wt" add -f "reports/colab_runs_${day}/$run_id"
  if git -C "$wt" diff --cached --quiet; then
    log "results/$run_id on GitHub is already up to date"
    git worktree remove --force "$wt" >/dev/null 2>&1 || true
    printf 'pushed\n' > "$run_dir/state"
    return 0
  fi
  git -C "$wt" ${who[@]+"${who[@]}"} commit -q --no-verify -m "$message"
  if GIT_TERMINAL_PROMPT=0 git -C "$wt" push -q -u origin "$branch" </dev/null; then
    if [[ "$mode" == early ]]; then printf 'failed (logs on GitHub)\n' > "$run_dir/state"; else printf 'pushed\n' > "$run_dir/state"; fi
    log "pushed $([[ "$mode" == append ]] && printf 'launcher logs ' || true)to $(repo_web_url)/tree/$branch"
  else
    log "git push failed. Everything is in $run_dir. Fix git credentials, then: bash colab/launch.sh push $run_id"
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
    log "colab CLI: $(colab_t 120 version 2>/dev/null | tail -n 1)"
    if colab_t 300 sessions </dev/null >/dev/null 2>&1; then log "colab auth: OK"; else log "colab auth: FAILED (run 'colab sessions' to see why)"; ok=0; fi
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
  if commit_is_published "$(git rev-parse HEAD)"; then
    log "code source: the VM will download commit $(git rev-parse --short=12 HEAD) from GitHub (no code upload)"
  else
    log "code source: HEAD is not on origin yet, so the code archive will be uploaded (push to avoid that)"
  fi
  if [[ -n "${P3_DRIVE_MOUNT_CMD:-}${P3_DRIVE_SETUP_FILE:-}" ]]; then
    log "Google Drive (optional): a Drive hook is configured; test it with: bash colab/launch.sh drive-check"
  else
    log "Google Drive (optional): no Drive hook configured; results still go to the results/<run_id> branch"
  fi
  if [[ "$ok" == 1 ]]; then log "all checks passed"; else die "some checks failed (see above)"; fi
}

commit_is_published() {
  # never prompt for credentials here: a failed fetch just means "upload the code instead"
  local limit=()
  command -v timeout >/dev/null 2>&1 && limit=(timeout 120)
  GIT_TERMINAL_PROMPT=0 GIT_SSH_COMMAND="${GIT_SSH_COMMAND:-ssh -o BatchMode=yes}" \
    ${limit[@]+"${limit[@]}"} git fetch -q origin </dev/null >/dev/null 2>&1 || return 1
  [[ -n "$(git branch -r --contains "$1" 2>/dev/null)" ]]
}

drive_hooks() {
  # optional: let the user's own tooling mount Drive / configure rclone on the fresh VM. Output stays local
  # (drive_mount.log is never pushed) and the command text is not logged, since either may carry credentials.
  local task=$1 failed=0
  if [[ -n "${P3_DRIVE_MOUNT_CMD:-}" ]]; then
    log "running the Drive hook P3_DRIVE_MOUNT_CMD on this machine (output: $RUN_DIR/drive_mount.log, kept local)"
    P3_SESSION="$SESSION" bash -c "${P3_DRIVE_MOUNT_CMD//\{session\}/$SESSION}" </dev/null >> "$RUN_DIR/drive_mount.log" 2>&1 ||
      failed=1
  fi
  if [[ -n "${P3_DRIVE_SETUP_FILE:-}" ]]; then
    if [[ ! -f "$P3_DRIVE_SETUP_FILE" ]]; then
      log "P3_DRIVE_SETUP_FILE does not exist: $P3_DRIVE_SETUP_FILE"
      failed=1
    else
      log "running P3_DRIVE_SETUP_FILE on the VM (output: $RUN_DIR/drive_mount.log, kept local)"
      colab_t 1200 exec -s "$SESSION" -f "$P3_DRIVE_SETUP_FILE" --timeout 900 </dev/null >> "$RUN_DIR/drive_mount.log" 2>&1 ||
        failed=1
    fi
  fi
  if [[ "$failed" == 1 ]]; then
    [[ "$task" == "drive-check" ]] && die "the Drive hook failed (see $RUN_DIR/drive_mount.log)"
    log "WARNING: the Drive hook failed; continuing without Drive (see $RUN_DIR/drive_mount.log)"
  fi
}

cmd_run() {
  local task=$1 vllm=1 dirty_ok=0 dry=0 needs_data=1 env_mode=gpu drive_persist=results vm_push=auto attach=""
  shift
  if [[ "$task" == "drive-check" ]]; then
    needs_data=0
    env_mode=none
    drive_persist=none
    GPU="${P3_DRIVE_CHECK_GPU:-}"
  fi
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --gpu) GPU="${2:?--gpu needs a value}"; shift 2 ;;
      --session) attach="${2:?--session needs the name of a session you created with colab new}"; shift 2 ;;
      --keep) KEEP=1; shift ;;
      --release) RELEASE=1; shift ;;
      --no-vm-push) vm_push=off; shift ;;
      --no-vllm) vllm=0; shift ;;
      --allow-dirty) dirty_ok=1; shift ;;
      --dry-run) dry=1; shift ;;
      *) die "unknown option '$1' (in zsh, do not put a # comment after the command)" ;;
    esac
  done
  if [[ -n "$attach" ]]; then
    [[ "$attach" =~ ^[A-Za-z0-9._-]+$ ]] || die "session names contain only letters, digits, '.', '_' and '-'"
    ATTACHED=1
  fi
  need git
  need tar
  need "$PY"
  need "$COLAB_BIN"
  check_python
  mkdir -p "$CACHE" "$RUNS"
  RUN_ID="${task}-$(date -u +%Y%m%dT%H%M%SZ)-$(od -An -N2 -tx1 /dev/urandom | tr -d ' \n')"
  RUN_DIR="$RUNS/$RUN_ID"
  mkdir -p "$RUN_DIR/kernel"
  RUN_LOG="$RUN_DIR/launch.log"
  # snapshot the kernel-side scripts: later git checkouts must not change what this run executes
  cp colab/kernel_bootstrap.py colab/kernel_job.py colab/kernel_inbox.py "$RUN_DIR/kernel/"
  if [[ "$ATTACHED" == 1 ]]; then
    SESSION="$attach"
    printf 'yes\n' > "$RUN_DIR/attached"
  else
    SESSION="p3-${task}-$(date -u +%m%d%H%M)-${RUN_ID##*-}"
  fi
  printf '%s\n' "$SESSION" > "$RUN_DIR/session"
  printf '%s\n' "$task" > "$RUN_DIR/task"
  printf 'preparing\n' > "$RUN_DIR/state"
  local commit dirty=0 code code_mode=upload tarball=""
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
  if [[ "$ATTACHED" == 1 ]]; then
    log "run $RUN_ID (task $task, commit ${commit:0:12}) on your session $SESSION (its hardware decides the GPU)"
  else
    log "run $RUN_ID (task $task, commit ${commit:0:12}, GPU ${GPU:-none (CPU VM)})"
  fi
  if [[ "$dirty" == 1 ]]; then
    code="$CACHE/code_${commit:0:12}_dirty.tar.gz"
    git ls-files -co --exclude-standard -z | tar --null -czf "$code" -T -
  else
    code="$CACHE/code_${commit:0:12}.tar.gz"
    [[ -f "$code" ]] || git archive --format=tar.gz -o "$code" HEAD
    if [[ "${P3_CODE_SOURCE:-auto}" != "upload" ]]; then
      local web
      web="$(repo_web_url)"
      if [[ -n "${P3_CODE_TARBALL_URL:-}" ]]; then
        tarball="${P3_CODE_TARBALL_URL//\{commit\}/$commit}"
      elif [[ "$web" =~ ^https://github\.com/([^/]+)/([^/]+)$ ]]; then
        tarball="https://codeload.github.com/${BASH_REMATCH[1]}/${BASH_REMATCH[2]}/tar.gz/$commit"
      fi
      if [[ -n "$tarball" ]] && commit_is_published "$commit"; then
        code_mode=github
        git ls-tree -r -z "$commit" > "$RUN_DIR/tree.bin"
      fi
    fi
  fi
  if [[ "$code_mode" == github ]]; then
    log "code: the VM downloads commit ${commit:0:12} from GitHub and verifies every file against its git blob SHA-1"
  else
    log "code: uploading the archive (commit not on the remote, uncommitted changes, or P3_CODE_SOURCE=upload)"
  fi
  local pack_json=""
  if [[ "$needs_data" == 1 ]]; then
    log "building private data pack from $DATA_ROOT"
    "$PY" -m scripts.colab.pack_private_data --data-root "$DATA_ROOT" --out "$CACHE" > "$RUN_DIR/pack.json" ||
      die "data pack failed: $(tail -c 800 "$RUN_DIR/pack.json")"
    log "data pack: $(head -c 300 "$RUN_DIR/pack.json")"
    pack_json="$RUN_DIR/pack.json"
  fi
  local colab_version options local_json
  colab_version="$(colab_ version 2>/dev/null | tail -n 1 || true)"
  printf '%s\n' "$colab_version" > "$RUN_DIR/colab_version.txt"
  options="$("$PY" -c 'import json,sys; a=sys.argv; print(json.dumps({"vllm_probe": a[1] == "1", "dry_run": a[2] == "1", "gpu_requested": a[3], "env": a[4], "drive_persist": a[5], "drive_remote": a[6], "drive_dir": a[7], "drive_mount": a[8]}))' \
    "$vllm" "$dry" "${GPU:-none}" "$env_mode" "$drive_persist" "${P3_DRIVE_REMOTE:-mydrive:}" \
    "${P3_DRIVE_DIR:-ColabProjects/vlm-perception-reward-rl}" "${P3_DRIVE_MOUNT:-/content/mydrive}")"
  local_json="$("$PY" -c 'import json,platform,sys; print(json.dumps({"colab_version": sys.argv[1], "data_root": sys.argv[2], "host": platform.platform(), "python": platform.python_version()}))' "$colab_version" "$DATA_ROOT")"
  printf '%s\n' "$local_json" > "$RUN_DIR/local.json"
  # VM-side push (D37): only the target and the path of a credential file the user put on the VM travel in the
  # request; the VM pushes only if that file exists there, otherwise this machine pushes as before.
  local push_url="" github_json="{}" web_url
  web_url="$(repo_web_url)"
  if [[ "$vm_push" != off ]]; then
    if [[ -n "${P3_VM_PUSH_URL:-}" ]]; then
      push_url="$P3_VM_PUSH_URL"
    elif [[ "$web_url" =~ ^https://github\.com/[^/]+/[^/]+$ ]]; then
      push_url="$web_url.git"
    fi
  fi
  if [[ -n "$push_url" ]]; then
    github_json="$("$PY" -c 'import json,sys; a=sys.argv; print(json.dumps({"mode": "auto", "url": a[1], "branch": a[2], "base_commit": a[3], "day": a[4], "credentials": a[5], "task": a[6], "max_file_mb": 25}))' \
      "$push_url" "results/$RUN_ID" "$commit" "$(run_day "$RUN_ID")" "${P3_VM_GH_CREDENTIALS:-/content/gh_credentials}" "$task")"
  fi
  "$PY" -m scripts.colab.local_tools make-request --task "$task" --run-id "$RUN_ID" --code "$code" --commit "$commit" \
    --dirty "$dirty" --pack-json "$pack_json" --staging "$RUN_DIR/upload" --uploads "$RUN_DIR/uploads.tsv" \
    --code-uploads "$RUN_DIR/code_uploads.tsv" --code-mode "$code_mode" --tarball-url "$tarball" \
    --tree-file "$RUN_DIR/tree.bin" --part-mb "$PART_MB" --options "$options" --local "$local_json" \
    --github "$github_json" >/dev/null
  colab_ usage </dev/null > "$RUN_DIR/usage_before.txt" 2>&1 || true

  trap on_exit EXIT
  trap 'log "interrupted"; exit 130' INT TERM
  PUSH_ON_FAILURE=1
  if [[ "$ATTACHED" == 1 ]]; then
    log "using your session $SESSION; it is not released at the end unless you pass --release"
    inbox_listing || die "could not run code on session $SESSION (does it exist? check with: colab sessions)"
  else
    log "allocating Colab VM $SESSION (${GPU:-CPU})"
    local gpu_args=()
    [[ -n "$GPU" ]] && gpu_args=(--gpu "$GPU")
    retry 3 colab_ new -s "$SESSION" ${gpu_args[@]+"${gpu_args[@]}"} </dev/null >> "$RUN_LOG" 2>&1 ||
      die "could not allocate a ${GPU:-CPU} VM (quota or availability). Try later or with --gpu H100."
    inbox_listing || die "could not run code on the new VM (see $RUN_DIR/inbox.log)"
  fi
  printf 'allocated\n' > "$RUN_DIR/state"
  if [[ "$ATTACHED" == 1 ]]; then
    [[ -z "${P3_DRIVE_MOUNT_CMD:-}${P3_DRIVE_SETUP_FILE:-}" ]] ||
      log "Drive hooks skipped: you prepared session $SESSION yourself"
  else
    drive_hooks "$task"
  fi
  # a session you reuse may already hold identical parts (same SHA256): send only what is missing or different
  "$PY" -m scripts.colab.local_tools inbox-diff "$RUN_DIR/uploads.tsv" "$RUN_DIR/inbox.log" > "$RUN_DIR/uploads_todo.tsv"
  local reused
  reused=$(( $(grep -c . "$RUN_DIR/uploads.tsv" || true) - $(grep -c . "$RUN_DIR/uploads_todo.tsv" || true) ))
  ((reused == 0)) || log "$reused part(s) are already on the VM with the right SHA256; not sending them again"
  upload_list "$RUN_DIR/uploads_todo.tsv" "inputs"
  verify_inbox "$RUN_DIR/uploads.tsv"

  if [[ "$env_mode" == none ]]; then
    log "bootstrap on the VM (code only; this task needs no GPU environment)"
  else
    log "bootstrap on the VM (code, environment install and model download; ~10-20 min)"
  fi
  : > "$RUN_DIR/bootstrap.log"
  local attempt_log="$RUN_DIR/bootstrap_1.log"
  run_bootstrap "$attempt_log"
  if grep -q "CODE_DOWNLOAD_FAILED" "$attempt_log"; then
    log "the VM could not fetch or verify the code from GitHub; uploading the code archive instead"
    upload_list "$RUN_DIR/code_uploads.tsv" "code"
    verify_inbox "$RUN_DIR/code_uploads.tsv"
    attempt_log="$RUN_DIR/bootstrap_2.log"
    run_bootstrap "$attempt_log"
  fi
  if ! grep -q "BOOTSTRAP_OK" "$attempt_log"; then
    if grep -q -E "BOOTSTRAP_FAILED|CODE_DOWNLOAD_FAILED" "$attempt_log" || ! wait_bootstrap; then
      die "bootstrap failed on the VM (see $RUN_DIR/bootstrap.log)"
    fi
  fi
  rm -rf "$RUN_DIR/upload"
  JOB_STARTED=1
  printf 'running\n' > "$RUN_DIR/state"
  log "job running on the VM; progress lines follow (Ctrl-C detaches, the job keeps running)"
  colab_t 87000 exec -s "$SESSION" -f "$RUN_DIR/kernel/kernel_job.py" --timeout 86400 </dev/null 2>&1 | tee "$RUN_DIR/job.log" || true
  wait_and_fetch "the VM stopped answering; reattach later with: bash colab/launch.sh collect $RUN_ID"
  release_or_remind
  colab_ usage </dev/null > "$RUN_DIR/usage_after.txt" 2>&1 || true
  push_results "$RUN_ID" || true
  print_summary
  [[ "$(run_overall)" == "passed" ]] || exit 3
}

wait_and_fetch() {
  local message=$1
  if ! grep -q "JOB_DONE" "$RUN_DIR/job.log" 2>/dev/null; then
    log "no live connection to the job; polling the VM every ${POLL}s"
    if ! poll_until_done; then
      finish_from_github || die "$message"
      return 0
    fi
  fi
  fetch_results
}

load_run() {
  RUN_ID="${1:?run id required (see: bash colab/launch.sh list)}"
  RUN_DIR="$RUNS/$RUN_ID"
  [[ -d "$RUN_DIR" ]] || die "unknown run $RUN_ID"
  RUN_LOG="$RUN_DIR/launch.log"
  SESSION="$(cat "$RUN_DIR/session")"
  [[ -f "$RUN_DIR/attached" ]] && ATTACHED=1
  return 0
}

cmd_collect() {
  load_run "$1"
  shift
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --release) RELEASE=1; shift ;;
      --keep) KEEP=1; shift ;;
      *) die "unknown option '$1'" ;;
    esac
  done
  need "$COLAB_BIN"
  JOB_STARTED=1
  trap on_exit EXIT
  log "reattaching to $SESSION"
  wait_and_fetch_collect
  release_or_remind
  colab_ usage </dev/null > "$RUN_DIR/usage_after.txt" 2>&1 || true
  push_results "$RUN_ID" || true
  print_summary
}

wait_and_fetch_collect() {
  # collect never relies on the live output: poll, and use GitHub if the VM is gone
  if ! poll_until_done; then
    finish_from_github || die "the VM does not answer and results/$RUN_ID is not on GitHub; it may have been reclaimed"
    return 0
  fi
  fetch_results
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
  [[ -n "$command" ]] || { usage; exit 2; }
  shift
  case "$command" in
    check) cmd_check ;;
    preflight) cmd_run preflight "$@" ;;
    drive-check) cmd_run drive-check "$@" ;;
    collect) cmd_collect "$@" ;;
    push) need git; check_python; load_run "${1:-}"; push_results "$RUN_ID" ;;
    stop) load_run "${1:-}"; need "$COLAB_BIN"; stop_session ;;
    list) cmd_list ;;
    *) usage; exit 2 ;;
  esac
}

main "$@"
