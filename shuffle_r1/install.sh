#!/usr/bin/env bash
set -euo pipefail

root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
env_dir=${1:?Usage: bash shuffle_r1/install.sh /path/to/venv}
uv venv --python 3.12 "$env_dir"
py="$env_dir/bin/python"
uv pip install --python "$py" --torch-backend cu128 -r "$root/requirements.txt"

wheel='flash_attn-2.8.3+cu12torch2.7cxx11abiTRUE-cp312-cp312-linux_x86_64.whl'
tmp=$(mktemp -d --tmpdir="$env_dir")
trap 'rm -f -- "$tmp/$wheel"; rmdir -- "$tmp"' EXIT
curl -fLsS --retry 3 -o "$tmp/$wheel" "https://github.com/Dao-AILab/flash-attention/releases/download/v2.8.3/$wheel"
printf '%s  %s\n' 'cafd4f708725e1be95495a86cbf418cfada08e707c8a797def61488a2a3c4f72' "$tmp/$wheel" | sha256sum -c -
uv pip install --python "$py" --no-deps "$tmp/$wheel"
uv pip install --python "$py" --target "$env_dir/nccl" --no-deps 'nvidia-nccl-cu12==2.27.3'
uv pip check --python "$py"
