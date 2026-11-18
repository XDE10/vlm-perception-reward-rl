#!/usr/bin/env bash
set -euo pipefail
cd /content/shuffle-r1-formal
root=$PWD
mkdir -p evidence
read -r deadline stop_step resume_step < run-target.txt
# A replacement runtime follows the same one-step limit.
stop_step=1
[[ "$deadline" =~ ^[0-9]+$ && "$stop_step" =~ ^[1-9][0-9]*$ && "$resume_step" =~ ^[0-9]+$ ]]
checkpoint_root="$root/checkpoints/qwen25vl3b_b512_seed1"
warm_resume=${P3_FORMAL_WARM_RESUME:-0}
export RCLONE_CONFIG=/content/.p3-overnight-rclone.conf
export RCLONE_TPSLIMIT=2 RCLONE_CHECKERS=2 RCLONE_TRANSFERS=2 RCLONE_DRIVE_STOP_ON_UPLOAD_LIMIT=true
drive=mydrive:ColabProjects/vlm-perception-reward-rl/shuffle-r1-overnight-20261116
export PYTHONUNBUFFERED=1 PYTHONHASHSEED=0
export FLASH_ATTENTION_DETERMINISTIC=1 CUBLAS_WORKSPACE_CONFIG=:4096:8
export VLLM_USE_V1=1 VLLM_ENABLE_V1_MULTIPROCESSING=0 VLLM_ATTENTION_BACKEND=FLASH_ATTN
export VLLM_USE_FLASHINFER_SAMPLER=0 RAY_DEDUP_LOGS=0
export NCCL_SOCKET_IFNAME=lo NCCL_IB_DISABLE=1 NCCL_P2P_DISABLE=1 TORCH_NCCL_AVOID_RECORD_STREAMS=1
export HF_HOME="$root/hf"
export COLAB_PROBE_SOURCE="$root/source"
export PYTHONPATH="$root:$root/source${PYTHONPATH:+:$PYTHONPATH}"

finish() {
    rc=$?
    printf '%s\n' "$rc" > "$root/evidence/remote-exit-code.txt"
    [ -z "${monitor:-}" ] || kill "$monitor" 2>/dev/null || true
    [ -z "${publisher:-}" ] || kill "$publisher" 2>/dev/null || true
    for phase in qwen25vl3b_b512_seed1; do
        for step in "$stop_step"; do
            manifest="$root/checkpoints/$phase/global_step_$step/manifest.json"
            [ ! -f "$manifest" ] || cp "$manifest" "$root/evidence/${phase}-step${step}-manifest.json" || true
        done
    done
    if (( rc != 0 )) && [[ -d /tmp/ray/session_latest/logs ]]; then
        {
            for log in /tmp/ray/session_latest/logs/worker-*.err /tmp/ray/session_latest/logs/raylet.err; do
                [[ -f "$log" ]] || continue
                printf '\n%s\n' "${log##*/}"
                tail -n 60 "$log"
            done
        } > "$root/evidence/ray-errors.log"
    fi
    tar -C "$root" -czf "$root/evidence.tgz" evidence || true
    if [[ -z "${model_fetch:-}" ]]; then :; else kill "$model_fetch" 2>/dev/null || true; fi
}
trap finish EXIT

echo 'FORMAL_STAGE=GPU_AND_DISK_CHECK'
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader | tee evidence/gpu.txt
if ! grep -q 'RTX PRO 6000.*Blackwell' evidence/gpu.txt; then exit 12; fi
avail_kb=$(df -Pk . | awk 'NR==2 {print $4}')
free -h | tee evidence/ram.txt
df -h . | tee evidence/disk.txt
# One complete checkpoint and the environment need space.
if (( warm_resume == 0 && avail_kb < 140 * 1024 * 1024 )); then echo 'Insufficient local space for the checkpoint and environment'; exit 13; fi
(
    while true; do
        printf 'FORMAL_RESOURCE '
        nvidia-smi --query-gpu=timestamp,memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits
        awk '/MemAvailable:/ {printf "FORMAL_HOST_RAM available_kib=%s\n",$2}' /proc/meminfo
        sleep 30
    done
) &
monitor=$!

if (( warm_resume == 0 )); then
sha256sum -c SHA256SUMS
git clone -q --branch g4-logical-batch-prep-20261115 source.bundle source
[[ "$(git -C source rev-parse HEAD)" == '1a7fb4b67e02a6b41cde437d7edc074ddd5a22e6' ]]
git -C source diff --exit-code
cp data/split_manifest.json evidence/input-manifest.json
cp probe.yaml evidence/probe.yaml
cp model-identity.json evidence/model-identity.json

echo 'FORMAL_STAGE=GPU_ENVIRONMENT_AND_MODEL_PREPARATION'
if ! command -v uv >/dev/null; then python3 -m pip -q install uv; fi
if python3 -c 'import huggingface_hub' 2>/dev/null; then
    python3 -u model_cache.py > evidence/model-fetch.txt 2>&1 &
    model_fetch=$!
fi
uv venv --python 3.12 env
uv pip install --python env/bin/python --torch-backend cu128 \
    'vllm==0.9.2' 'transformers==4.52.4' 'datasets==3.6.0' 'ray[default]==2.48.0' \
    'torchdata==0.11.0' 'tensordict==0.8.3' 'mathruler==0.1.0' 'codetiming==1.4.0' \
    'omegaconf==2.3.0' 'numpy==2.2.6' pandas 'pylatexenc==2.10' 'tensorboard==2.19.0' accelerate qwen-vl-utils
wheel='flash_attn-2.8.3+cu12torch2.7cxx11abiTRUE-cp312-cp312-linux_x86_64.whl'
curl -fLsS --retry 3 --connect-timeout 15 -o "$wheel" "https://github.com/Dao-AILab/flash-attention/releases/download/v2.8.3/${wheel}"
printf '%s  %s\n' 'cafd4f708725e1be95495a86cbf418cfada08e707c8a797def61488a2a3c4f72' "$wheel" | sha256sum -c
uv pip install --python env/bin/python --no-deps "./$wheel"
uv pip install --python env/bin/python --target nccl --no-deps 'nvidia-nccl-cu12==2.27.3'
export LD_PRELOAD="$root/nccl/nvidia/nccl/lib/libnccl.so.2"
uv pip check --python env/bin/python
uv pip freeze --python env/bin/python > evidence/packages.txt
if [[ -n "${model_fetch:-}" ]] && wait "$model_fetch"; then
    model_fetch=
else
    env/bin/python -u model_cache.py | tee -a evidence/model-fetch.txt
    model_fetch=
fi
export HF_HUB_OFFLINE=1

echo 'FORMAL_STAGE=FROZEN_TRAIN_DATA'
if ! command -v rclone >/dev/null; then
    apt-get update -qq && apt-get install -y -qq rclone
fi
rclone copyto "$drive/inputs/train.parquet" data/train.parquet --drive-chunk-size 64M --stats 30s --stats-one-line
else
    echo 'FORMAL_STAGE=REUSING_GPU_ENVIRONMENT'
    [[ "$(git -C source rev-parse HEAD)" == '1a7fb4b67e02a6b41cde437d7edc074ddd5a22e6' ]]
    git -C source diff --exit-code
    test -x env/bin/python
    export LD_PRELOAD="$root/nccl/nvidia/nccl/lib/libnccl.so.2"
    export HF_HUB_OFFLINE=1
fi

echo 'FORMAL_STAGE=CUDA_KERNEL_AND_DATA_PREFLIGHT' 
env/bin/python -u - <<'PY'
import torch, vllm, transformers
from flash_attn import flash_attn_func
from transformers.models.qwen2_5_vl.modeling_qwen2_5_vl import Qwen2_5_VLFlashAttention2
from shuffle_r1.main import load_config
from shuffle_r1.checkpoint import verify_split_manifest
from transformers import AutoTokenizer, AutoProcessor
assert torch.cuda.is_available() and torch.cuda.device_count() == 1
assert torch.cuda.get_device_capability() == (12, 0)
print('GPU_VERSIONS', torch.__version__, torch.version.cuda, vllm.__version__, transformers.__version__, torch.cuda.nccl.version(), flush=True)
a=torch.ones(1, 16, 2, 32, device='cuda', dtype=torch.bfloat16)
assert flash_attn_func(a,a,a).isfinite().all().item()
cfg=load_config(['config=/content/shuffle-r1-formal/probe.yaml'])
verify_split_manifest(cfg)
path=cfg.worker.actor.model.model_path
assert AutoTokenizer.from_pretrained(path, local_files_only=True, use_fast=True).is_fast
assert AutoProcessor.from_pretrained(path, local_files_only=True, use_fast=True).image_processor is not None
print('FORMAL_OFFLINE_MODEL_AND_TOKENIZER_OK', path, flush=True)
PY
cd "$root/source"
resume_path=
if (( resume_step > 0 )); then
    local_resume="$checkpoint_root/global_step_$resume_step"
    if (( warm_resume == 1 )) && [[ -n "${P3_WARM_MANIFEST_SHA:-}" ]] &&
       printf '%s  %s\n' "$P3_WARM_MANIFEST_SHA" "$local_resume/manifest.json" | sha256sum -c -; then
        resume_path=$local_resume
    else
        resume_path="$root/resume/global_step_$resume_step"
        mkdir -p "$resume_path"
        rclone copy "$drive/formal-checkpoints/global_step_$resume_step" "$resume_path" --exclude /PERSISTED.json --transfers 3 --stats 30s --stats-one-line
    fi
    if (( resume_step >= stop_step )); then
        rclone copyto "$drive/formal-checkpoints/global_step_$resume_step/PERSISTED.json" "$root/evidence/persistent-checkpoint.json"
        echo 'FORMAL_STOP_AFTER_FIRST_PERSISTED_CHECKPOINT'
        exit 0
    fi
fi

run_training() {
    local step_target=$1
    local start_checkpoint=$2
    local -a timeout_args=()
    if (( deadline > 0 )); then
        local seconds=$(( deadline - $(date +%s) - 2700 ))
        if (( seconds < 60 )); then
            echo 'Training window exhausted before the checkpoint transfer reserve'
            return 31
        fi
        timeout_args=(timeout --signal=TERM --kill-after=20s "${seconds}s")
    fi
    local -a resume_args=()
    if [[ -n "$start_checkpoint" ]]; then
        resume_args+=("trainer.load_checkpoint_path=$start_checkpoint")
    fi
    "${timeout_args[@]}" "$root/env/bin/python" -u "$root/run_main.py" \
        "config=$root/probe.yaml" "trainer.stop_after_step=$step_target" "${resume_args[@]}" \
        2>&1 | tee -a "$root/evidence/continuous.log"
    return "${PIPESTATUS[0]}"
}

mkdir -p "$checkpoint_root"
if (( resume_step == 0 )); then
    echo 'FORMAL_STAGE=FIRST_STEP_CHECKPOINT_READBACK'
    run_training 1 ""
    resume_path="$checkpoint_root/global_step_1"
    test -f "$resume_path/manifest.json"
    grep -F 'Training paused after verified checkpoint at logical step 1' "$root/evidence/continuous.log"
    cp "$resume_path/manifest.json" "$root/evidence/first-step-verified-manifest.json"
    bash "$root/persist_checkpoint.sh" "$checkpoint_root" "$drive" "$root/evidence"
    echo 'FORMAL_FIRST_STEP_CHECKPOINT_VERIFIED_AND_PERSISTED'
    if (( stop_step == 1 )); then
        exit 0
    fi
    "$root/env/bin/ray" stop --force || true
    resume_step=1
fi

echo "FORMAL_STAGE=TRAINING stop_after_step=$stop_step resume_step=$resume_step"
(
    while true; do
        sleep 20
        bash "$root/persist_checkpoint.sh" "$checkpoint_root" "$drive" "$root/evidence" || true
    done
) &
publisher=$!
set +e
run_training "$stop_step" "$resume_path"
train_rc=$?
set -e
printf '%s\n' "$train_rc" > "$root/evidence/training-exit-code.txt"
kill "$publisher" 2>/dev/null || true
publisher=
bash "$root/persist_checkpoint.sh" "$checkpoint_root" "$drive" "$root/evidence"
exit "$train_rc"
