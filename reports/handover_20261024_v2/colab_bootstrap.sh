#!/usr/bin/env bash
# Prepare only. Never downloads a model or launches training. Colab: 未验证.
set -euo pipefail
if [[ "$(uname -s)" != Linux ]]; then echo 'Linux/Colab only' >&2; exit 1; fi
python -c 'import sys; assert sys.version_info[:2] == (3,12), "Use Python 3.12 runtime; do not silently change pins"'
if [[ ! -d /content/drive/MyDrive ]]; then
  python - <<'PY'
from google.colab import drive
try:
    drive.mount('/content/drive')
except Exception as exc:
    raise SystemExit("Mount Drive in a notebook Python cell first: from google.colab import drive; drive.mount('/content/drive'). " + str(exc))
PY
fi
: "${PROJECT3_DRIVE_ROOT:?Set PROJECT3_DRIVE_ROOT to the complete migrated project on Drive}"
PROJECT3_SESSION_ROOT="${PROJECT3_SESSION_ROOT:-/content/project3}"
mkdir -p "$PROJECT3_SESSION_ROOT"
# Copy a complete package, preserving relative image/data paths and old manifests.
rsync -a --exclude '.venv*' --exclude 'blind' --exclude 'key' "$PROJECT3_DRIVE_ROOT/" "$PROJECT3_SESSION_ROOT/"
cd "$PROJECT3_SESSION_ROOT"
OUT=reports/handover_20261024_v2/colab_environment
mkdir -p "$OUT"
python -m venv /content/project3-env
PY=/content/project3-env/bin/python
"$PY" -m pip install -r reports/handover_20261024_v2/requirements-colab-cu126.txt --extra-index-url https://download.pytorch.org/whl/cu126 2>&1 | tee "$OUT/install.log"
"$PY" -m pip check | tee "$OUT/pip_check.log"
"$PY" -m pip freeze > "$OUT/pip_freeze.txt"
"$PY" -m torch.utils.collect_env > "$OUT/collect_env.txt"
nvidia-smi > "$OUT/nvidia-smi.txt"
"$PY" - <<'PY' | tee "$OUT/cuda_capability.json"
import json, torch
assert torch.cuda.is_available(), 'CUDA unavailable; do not start training'
assert torch.cuda.is_bf16_supported(), 'BF16 unavailable'
p=torch.cuda.get_device_properties(0)
print(json.dumps({'device':p.name,'total_memory_bytes':p.total_memory,'torch':torch.__version__,'cuda':torch.version.cuda}))
PY
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
"$PY" tools/verify_migration.py | tee "$OUT/verify_migration.log"
"$PY" -m pytest tests/test_approved_training_inputs.py tests/test_training_entries_cpu.py tests/test_perception_v4.py tests/test_geometry_model_serialization.py -q | tee "$OUT/readme_tests.log"
echo 'Environment prepared only. Model weights and GPU acceptance remain 未验证.'
