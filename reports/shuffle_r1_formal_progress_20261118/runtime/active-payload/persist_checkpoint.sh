#!/usr/bin/env bash
set -euo pipefail
checkpoint_root=$1
drive=$2
evidence=$3
while [[ -f "$(dirname "$evidence")/storage-switch.pause" ]]; do
    echo 'FORMAL_STORAGE_SWITCH_PAUSED_PUBLICATION'
    sleep 5
done

# A fourth argument identifies the periodic publisher. The final call omits it
# so the latest completed step is published at the runtime boundary.
if (( $# > 3 )); then
    set -- "$1" "$2" "$3" 1
fi

latest=$(find "$checkpoint_root" -mindepth 2 -maxdepth 2 -path "$checkpoint_root/global_step_*/manifest.json" -printf '%h\n' 2>/dev/null | awk -F / '$NF ~ /^global_step_[1-9][0-9]*$/' | sort -V | tail -n 1)
[[ -n "$latest" ]] || exit 3
step=${latest##*_}
interval=${4:-1}
(( step % interval == 0 || step % 25 == 0 )) || exit 0
stage="$checkpoint_root/.drive-upload-$step"
dest="$drive/formal-checkpoints/global_step_$step"
exec 8>"$checkpoint_root/.drive-upload.lock"
flock 8

if [[ -f "$evidence/persistent-checkpoint.json" ]] &&
   grep -Fq "\"step\":$step," "$evidence/persistent-checkpoint.json"; then
    exit 0
fi

trap 'rm -rf -- "$stage"' EXIT
rm -rf -- "$stage"
python3 "$(dirname "$evidence")/formal_validation.py" "$evidence" "$drive" "$P3_FORMAL_RESUME_STEP" "$latest"
cp -al -- "$latest" "$stage"
echo "FORMAL_STAGE=PERSISTING_CHECKPOINT step=$step"
rclone copy "$stage" "$dest" --drive-chunk-size 64M --transfers 3 --stats 30s --stats-one-line
rclone check "$stage" "$dest" --one-way --checkers 8
cp "$stage/manifest.json" "$evidence/persisted-checkpoint-manifest.json"
validation_helper="$(dirname "$evidence")/formal_validation.py"
if [[ -f "$validation_helper" ]] && (( step > 8 )); then
    retention=rolling
    if (( step % 25 == 0 )); then retention=archive; fi
    printf '{"step":%d,"remote":"%s","verified":true,"retention":"%s"}\n' "$step" "$dest" "$retention" > "$evidence/persistence.tmp"
else
    printf '{"step":%d,"remote":"%s","verified":true}\n' "$step" "$dest" > "$evidence/persistence.tmp"
fi
rclone copyto "$evidence/persistence.tmp" "$dest/PERSISTED.json"
mv "$evidence/persistence.tmp" "$evidence/persistent-checkpoint.json"
echo "FORMAL_CHECKPOINT_PERSISTED step=$step"
if [[ -f "$validation_helper" && -f "$(dirname "$evidence")/enable-rolling-retention" ]]; then
    python3 "$validation_helper" retire "$drive" "$stage" ||
        printf 'FORMAL_CHECKPOINT_RETENTION_DEFERRED step=%d\n' "$step"
fi
