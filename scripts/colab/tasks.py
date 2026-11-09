"""Task definitions: which steps a Colab job runs (standard library only).

A step is a dict: ``name``, ``cmd`` (argv), ``timeout`` (s), ``required``
(counts toward the overall verdict), ``depends_on`` (skipped unless those
passed), ``env`` and ``description``. Commands run from the extracted repo with
the base venv's interpreter unless stated otherwise.
"""
from pathlib import Path

from scripts.colab.common import write_json

ARMS = ["rl_ans", "rl_v4", "rl_v5", "rl_v5_placebo", "rl_blind"]
SMALL_SMOKE = "max_steps=1,num_generations=2,prompts_per_step=2,per_device_train_batch_size=2,max_completion_length=256,save_steps=1"
RESUME_SMOKE = "max_steps=2,num_generations=2,prompts_per_step=2,per_device_train_batch_size=2,max_completion_length=128,save_steps=1"
FULL_SMOKE = "max_steps=3"


class Context(object):
    def __init__(self, root, request, bootstrap, kernel_python):
        self.root = Path(root)
        self.repo = self.root / "repo"
        self.request = request
        self.options = request.get("options", {})
        self.run_id = request["run_id"]
        self.out = self.root / "out" / self.run_id
        self.bootstrap = bootstrap
        base = (bootstrap.get("envs") or {}).get("base") or {}
        self.python = base.get("python") or kernel_python  # tasks without a GPU env run on the kernel's python
        self.kernel_python = kernel_python
        self.dry_run = bool(self.options.get("dry_run"))
        model = bootstrap.get("model") or {}
        self.model_dir = model.get("local_dir")
        self.vllm_python = str(self.root / "env" / "vllm" / "bin" / "python")


def drive_probe_step(ctx, required):
    """Write/read/verify/delete probe files on the user's Drive through rclone (stdlib only, kernel python)."""
    cmd = [ctx.kernel_python, "-m", "scripts.colab.drive", "probe", "--out", ctx.out / "drive_probe.json",
           "--run-id", ctx.run_id, "--scratch", ctx.out / ".drive_scratch"]
    for flag, key in [("--remote", "drive_remote"), ("--dir", "drive_dir"), ("--mount", "drive_mount")]:
        if ctx.options.get(key):
            cmd += [flag, ctx.options[key]]
    if required:
        cmd.append("--require")
    return step("drive_probe", cmd, 3600, required=required,
                description="Google Drive via rclone: write, read back, hash check, delete (optional unless drive-check)")


def step(name, cmd, timeout=3600, required=True, depends_on=(), env=None, description=""):
    return {"name": name, "cmd": [str(c) for c in cmd], "timeout": timeout, "required": required,
            "depends_on": list(depends_on), "env": dict(env or {}), "description": description}


def train_cmd(ctx, arm, smoke, out_dir, runtime=None, resume=None, python=None):
    cmd = [python or ctx.python, "-m", "scripts.training.train_rl", "--arm", arm, "--seed", "1", "--smoke", smoke,
           "--output-dir", out_dir]
    if ctx.model_dir:
        cmd += ["--model-path", ctx.model_dir]
    if runtime:
        cmd += ["--runtime", runtime]
    if resume:
        cmd += ["--resume", resume]
    return cmd


def preflight_steps(ctx):
    py, out = ctx.python, ctx.out
    common = [
        step("env_report", [py, "-m", "scripts.colab.env_report", "--root", ctx.root, "--out", out / "env.json"], 900,
             description="software, GPU and environment lock report"),
        step("verify_pack", [py, "-m", "scripts.colab.verify_pack", "--repo", ctx.repo, "--out",
                             out / "pack_verification.json"], 900, description="private data matches its anchors"),
        drive_probe_step(ctx, required=False),
    ]
    if ctx.dry_run:
        return common + [
            step("pytest", [py, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests/test_claims.py",
                            "--junitxml=%s" % (out / "pytest.xml")], 1800, env={"CUDA_VISIBLE_DEVICES": ""},
                 description="dry run: one fast test module"),
            step("calibration", [py, "-m", "scripts.data.calibrate_perception_v5", "--output", out / "calibration"], 1800,
                 description="v5 oracle calibration on certified facts"),
            step("decide_runtime", [py, "-m", "scripts.colab.decide_runtime", "--out-dir", out], 600,
                 description="freeze runtime decisions"),
        ]
    model = ctx.model_dir
    steps = common + [
        step("pytest", [py, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--junitxml=%s" % (out / "pytest.xml")], 3600,
             env={"CUDA_VISIBLE_DEVICES": "", "P3_QWEN_PROCESSOR_DIR": model, "HF_HUB_OFFLINE": "1"},
             description="full CPU test suite on the VM (GPU hidden)"),
        step("calibration", [py, "-m", "scripts.data.calibrate_perception_v5", "--output", out / "calibration"], 3600,
             description="v5 oracle calibration on all certified facts"),
        step("gpu_probe", [py, "-m", "scripts.colab.gpu_probe", "--model-path", model, "--out", out / "gpu_probe.json"],
             3600, description="real-model LoRA scope, prompt lengths, peak memory, generation throughput, ViT cache"),
        step("v0_probe", [py, "-m", "scripts.colab.v0_probe", "--model-path", model, "--out", out / "v0_probe", "--n", "16"],
             3600, required=False, description="V0 greedy protocol-v3 probe on 16 validation problems (with/without image)"),
    ]
    for arm in ARMS:
        steps.append(step("smoke_" + arm, train_cmd(ctx, arm, SMALL_SMOKE, out / "smoke" / arm), 3600,
                          description="1 GRPO step at a small shape for arm " + arm))
    steps += [
        step("smoke_full_hf", train_cmd(ctx, "rl_v5", FULL_SMOKE, out / "smoke_full_hf", runtime=out / "runtime_hf.json"),
             7200, description="3 GRPO steps at the registered shape (8 prompts x 8 generations), HF generation"),
        step("resume_a", train_cmd(ctx, "rl_v5", RESUME_SMOKE, out / "resume"), 3600,
             description="2 steps with a checkpoint every step"),
        step("resume_b", train_cmd(ctx, "rl_v5", RESUME_SMOKE, out / "resume", resume=out / "resume" / "checkpoint-1"),
             3600, depends_on=["resume_a"], description="resume from checkpoint-1 to step 2 with identity check"),
    ]
    if ctx.options.get("vllm_probe", True):
        steps += [
            step("vllm_env", [ctx.kernel_python, "-m", "scripts.colab.bootstrap", "vllm-env", "--root", ctx.root], 5400,
                 required=False, description="optional vLLM venv (CUDA 13 only)"),
            step("smoke_full_vllm", train_cmd(ctx, "rl_v5", FULL_SMOKE, out / "smoke_full_vllm",
                                              runtime=out / "runtime_vllm.json", python=ctx.vllm_python), 7200,
                 required=False, depends_on=["vllm_env"], description="same 3 steps with vLLM colocate generation"),
        ]
    steps.append(step("decide_runtime", [py, "-m", "scripts.colab.decide_runtime", "--out-dir", out], 600,
                      description="freeze runtime decisions from the measurements"))
    return steps


def drive_check_steps(ctx):
    """Cheap CPU-VM check of the optional Drive setup; no data, no GPU environment, no model."""
    return [
        step("env_report", [ctx.python, "-m", "scripts.colab.env_report", "--root", ctx.root, "--out", ctx.out / "env.json"],
             900, required=False, description="VM software, RAM and disk"),
        drive_probe_step(ctx, required=True),
    ]


TASKS = {"preflight": preflight_steps, "drive-check": drive_check_steps}


def steps_for(ctx):
    task = ctx.request["task"]
    if task not in TASKS:
        raise ValueError("task %r is not available in this version; known: %s" % (task, sorted(TASKS)))
    return TASKS[task](ctx)


def prepare(ctx):
    """Write per-run inputs that steps read (runtime files for the backend smokes)."""
    ctx.out.mkdir(parents=True, exist_ok=True)
    write_json(ctx.out / "runtime_hf.json", {"generation_backend": "hf", "source": "preflight smoke (hf)"})
    write_json(ctx.out / "runtime_vllm.json", {"generation_backend": "vllm", "vllm_gpu_memory_utilization": 0.3,
                                                "vllm_max_model_length": 4096, "source": "preflight smoke (vllm)"})
    write_json(ctx.out / "request.json", ctx.request)
    write_json(ctx.out / "bootstrap.json", ctx.bootstrap)


__all__ = ["ARMS", "Context", "TASKS", "prepare", "steps_for"]
