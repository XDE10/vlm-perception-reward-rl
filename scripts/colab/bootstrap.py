"""VM bootstrap after the code is extracted: data pack, isolated venv, pinned model snapshot.

Called from ``colab/kernel_bootstrap.py`` inside the Colab kernel (standard library
only). Heavy work runs in subprocesses whose output goes to log files; a
heartbeat line is printed every 30 s. Writes ``state/bootstrap.json`` and prints
``BOOTSTRAP_OK`` / ``BOOTSTRAP_FAILED`` markers that the launcher looks for.

Also provides ``python -m scripts.colab.bootstrap vllm-env --root ...`` for the
optional vLLM probe venv.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

from scripts.colab.common import Heartbeat, join_parts, log, read_json, sha256_file, tail, write_json

UV_VERSION = "0.13.5"
PYTHON_VERSION = "3.12"
LOCKS = {"cu130": "requirements/locks/colab-gpu-cu130.txt", "cu129": "requirements/locks/colab-gpu-cu129.txt",
         "cu126": "requirements/locks/colab-gpu-cu126.txt"}
VLLM_LOCK = ("cu130", "requirements/locks/colab-gpu-vllm-cu130.txt")
TORCH_CHECK = r"""
import json, torch
ok = torch.cuda.is_available()
out = {"torch": torch.__version__, "cuda_runtime": torch.version.cuda, "cuda_available": ok}
if ok:
    x = torch.randn(512, 512, device="cuda", dtype=torch.bfloat16)
    y = (x @ x).float().sum().item()
    q = torch.randn(1, 4, 64, 32, device="cuda", dtype=torch.bfloat16)
    torch.nn.functional.scaled_dot_product_attention(q, q, q)
    torch.cuda.synchronize()
    out.update(device=torch.cuda.get_device_name(0), capability=list(torch.cuda.get_device_capability(0)),
               total_gb=torch.cuda.get_device_properties(0).total_memory / 1e9, matmul_finite=y == y)
print("TORCH_CHECK " + json.dumps(out))
"""


class StepError(RuntimeError):
    pass


def run_logged(cmd, log_path, label, cwd=None, env=None, timeout=None):
    log_path = Path(log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    started = time.time()
    with open(str(log_path), "ab") as handle:
        handle.write(("\n$ %s\n" % " ".join(str(c) for c in cmd)).encode())
        handle.flush()
        with Heartbeat(label, 30.0, lambda: tail(log_path, 1)[:160]):
            proc = subprocess.Popen([str(c) for c in cmd], cwd=None if cwd is None else str(cwd), env=env,
                                    stdout=handle, stderr=subprocess.STDOUT)
            try:
                rc = proc.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
                raise StepError("%s timed out after %ss; log tail:\n%s" % (label, timeout, tail(log_path, 30)))
    if rc != 0:
        raise StepError("%s failed (exit %s) after %.0fs; log tail:\n%s" % (label, rc, time.time() - started,
                                                                         tail(log_path, 40)))
    return time.time() - started


def gpu_info():
    if shutil.which("nvidia-smi") is None:
        return {"available": False}
    try:
        text = subprocess.run(["nvidia-smi"], capture_output=True, text=True, timeout=60).stdout
        query = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total,driver_version",
                                "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=60).stdout
    except Exception as exc:
        return {"available": False, "error": type(exc).__name__}
    match = re.search(r"CUDA Version:\s*(\d+)\.(\d+)", text)
    name, memory, driver = ([x.strip() for x in query.strip().splitlines()[0].split(",")] + ["", "", ""])[:3] if query.strip() else ("", "", "")
    return {"available": True, "name": name, "memory_mib": float(memory) if memory else None, "driver": driver,
            "driver_cuda": [int(match.group(1)), int(match.group(2))] if match else None, "nvidia_smi": text}


def backend_candidates(driver_cuda):
    """Highest compatible PyTorch CUDA build first; torch 2.13.0 exists for cu126/cu129/cu130 (not cu128)."""
    if not driver_cuda:
        return ["cu126"]
    major, minor = driver_cuda
    if major >= 13:
        return ["cu130", "cu129", "cu126"]
    if (major, minor) >= (12, 9):
        return ["cu129", "cu126"]
    return ["cu126", "cu129"]


def uv_cmd():
    probe = subprocess.run([sys.executable, "-m", "uv", "--version"], capture_output=True, text=True)
    if probe.returncode != 0 or UV_VERSION not in probe.stdout:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "uv==" + UV_VERSION], check=True)
    return [sys.executable, "-m", "uv"]


def create_env(root, repo, name, backend, lock_rel):
    env_dir = Path(root) / "env" / name
    python = env_dir / "bin" / "python"
    marker = env_dir / "p3_env.json"
    lock_sha = sha256_file(Path(repo) / lock_rel)
    if marker.is_file() and python.is_file():
        prior = read_json(marker)
        if prior.get("lock_sha256") == lock_sha and prior.get("torch_backend") == backend and prior.get("ok"):
            log("env %s already installed (%s), reusing" % (name, backend))
            return prior
    if env_dir.exists():
        shutil.rmtree(str(env_dir))
    uv = uv_cmd()
    logs = Path(root) / "state" / "logs"
    env = dict(os.environ, UV_CACHE_DIR=str(Path(root) / "uv-cache"), UV_HTTP_TIMEOUT="300")
    seconds = run_logged(uv + ["venv", str(env_dir), "--python", PYTHON_VERSION], logs / ("venv_%s.log" % name),
                         "creating venv " + name, env=env, timeout=1800)
    seconds += run_logged(uv + ["pip", "install", "--python", str(python), "--torch-backend", backend, "-r",
                                str(Path(repo) / lock_rel)], logs / ("install_%s.log" % name),
                          "installing %s (%s)" % (name, backend), env=env, timeout=3600)
    check = subprocess.run([str(python), "-c", TORCH_CHECK], capture_output=True, text=True, timeout=600)
    line = [x for x in check.stdout.splitlines() if x.startswith("TORCH_CHECK ")]
    result = json.loads(line[-1][len("TORCH_CHECK "):]) if line else {"error": check.stderr[-2000:]}
    freeze = subprocess.run(uv + ["pip", "freeze", "--python", str(python)], capture_output=True, text=True, env=env)
    (env_dir / "freeze.txt").write_text(freeze.stdout, encoding="utf-8")
    info = {"name": name, "python": str(python), "torch_backend": backend, "lock": lock_rel, "lock_sha256": lock_sha,
            "torch_check": result, "install_seconds": seconds, "ok": bool(result.get("cuda_available")),
            "freeze_sha256": sha256_file(env_dir / "freeze.txt")}
    write_json(marker, info)
    return info


def build_base_env(root, repo, gpu):
    attempts = []
    for backend in backend_candidates(gpu.get("driver_cuda")):
        try:
            info = create_env(root, repo, "base", backend, LOCKS[backend])
        except StepError as exc:
            attempts.append({"backend": backend, "error": str(exc)[-1500:]})
            log("backend %s failed to install: %s" % (backend, str(exc).splitlines()[0]))
            continue
        attempts.append({"backend": backend, "torch_check": info["torch_check"]})
        if info["ok"]:
            info["attempts"] = attempts
            return info
        log("backend %s installed but CUDA check failed: %s" % (backend, info["torch_check"]))
    raise StepError("no PyTorch CUDA backend worked: %s" % json.dumps(attempts)[:3000])


def experiment_model(repo):
    model = read_json(Path(repo) / "configs/experiments/rl_v3.json")["model"]
    return model["id"], model["revision"]


def fetch_model(root, repo, python):
    model_id, revision = experiment_model(repo)
    dest = Path(root) / "models" / ("%s@%s" % (model_id.split("/")[-1], revision[:12]))
    out = Path(root) / "state" / "model.json"
    if out.is_file():
        prior = read_json(out)
        if prior.get("revision") == revision and all((dest / f).is_file() for f in prior.get("files", {})):
            log("model snapshot already present, reusing")
            return prior
    env = dict(os.environ, HF_HOME=str(Path(root) / "hf_home"), PYTHONPATH=str(repo))
    run_logged([python, "-m", "scripts.colab.fetch_model", "--repo", model_id, "--revision", revision, "--dest", dest,
                "--out", out], Path(root) / "state" / "logs" / "model.log", "downloading %s@%s" % (model_id, revision[:8]),
               cwd=repo, env=env, timeout=5400)
    return read_json(out)


def main(root, request):
    root = Path(root)
    repo = root / "repo"
    state = root / "state"
    state.mkdir(parents=True, exist_ok=True)
    started = time.time()
    record = {"schema": "p3-bootstrap-v1", "run_id": request["run_id"], "code_sha256": request["code"]["sha256"],
              "pack_content_sha256": request["data_pack"]["content_sha256"], "dry_run": bool(request["options"].get("dry_run"))}
    try:
        from scripts.colab.pack_private_data import extract_pack, verify_tree

        inbox = root / "inbox"
        pack = join_parts(inbox, request["data_pack"]["parts"], inbox / request["data_pack"]["name"],
                          request["data_pack"]["sha256"])
        extract_pack(pack, repo)
        verification = verify_tree(repo)
        write_json(state / "pack_verification.json", verification)
        if not verification["ok"]:
            raise StepError("data pack verification failed: %s" % verification["problems"][:5])
        log("data pack verified: %d files, anchors %s" % (verification["files"], ",".join(verification["anchors"])))
        gpu = gpu_info()
        record["gpu"] = {k: v for k, v in gpu.items() if k != "nvidia_smi"}
        (state / "nvidia_smi.txt").write_text(gpu.get("nvidia_smi", "unavailable"), encoding="utf-8")
        if record["dry_run"]:
            record["envs"] = {"base": {"name": "base", "python": sys.executable, "torch_backend": "dry-run", "ok": True}}
            record["model"] = None
        else:
            if not gpu.get("available"):
                raise StepError("no NVIDIA GPU visible on this VM")
            log("GPU: %s, %s MiB, driver %s (CUDA %s)" % (gpu.get("name"), gpu.get("memory_mib"), gpu.get("driver"),
                                                        gpu.get("driver_cuda")))
            base = build_base_env(root, repo, gpu)
            record["envs"] = {"base": base}
            log("base env ready: torch %s, backend %s" % (base["torch_check"].get("torch"), base["torch_backend"]))
            record["model"] = fetch_model(root, repo, base["python"])
            log("model ready: %s (%d files)" % (record["model"]["local_dir"], len(record["model"]["files"])))
        record["seconds"] = time.time() - started
        record["ok"] = True
        write_json(state / "bootstrap.json", record)
        log("BOOTSTRAP_OK in %.0fs" % record["seconds"])
        return record
    except Exception as exc:  # report every failure through the marker protocol, never raise into the kernel
        record.update(ok=False, error="%s: %s" % (type(exc).__name__, str(exc)[-3000:]), seconds=time.time() - started)
        write_json(state / "bootstrap.json", record)
        log("BOOTSTRAP_FAILED %s" % record["error"].splitlines()[0][:300])
        sys.stdout.write(record["error"] + "\n")
        return record


def vllm_env(root):
    """Create the optional vLLM venv (cu130 only); write state/vllm_env.json; exit non-zero on failure."""
    root = Path(root)
    repo = root / "repo"
    base = read_json(root / "env" / "base" / "p3_env.json")
    backend, lock = VLLM_LOCK
    if base.get("torch_backend") != backend:
        result = {"ok": False, "skipped": True, "reason": "vLLM 0.32.0 wheels need CUDA 13; base backend is %s" % base.get("torch_backend")}
    else:
        try:
            result = create_env(root, repo, "vllm", backend, lock)
            check = subprocess.run([result["python"], "-c", "import vllm, json; print('VLLM ' + vllm.__version__)"],
                                   capture_output=True, text=True, timeout=900)
            result["vllm_import"] = check.stdout.strip()[-200:] or check.stderr[-1500:]
            result["ok"] = result["ok"] and check.returncode == 0
        except StepError as exc:
            result = {"ok": False, "error": str(exc)[-3000:]}
    write_json(root / "state" / "vllm_env.json", result)
    print(json.dumps({k: v for k, v in result.items() if k not in {"torch_check"}})[:2000])
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["vllm-env"])
    parser.add_argument("--root", required=True)
    args = parser.parse_args()
    sys.exit(vllm_env(args.root))
