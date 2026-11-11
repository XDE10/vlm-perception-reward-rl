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


def train_cmd(ctx, arm, smoke, out_dir, runtime=None, resume=None, python=None, experiment=None):
    cmd = [python or ctx.python, "-m", "scripts.training.train_rl", "--arm", arm, "--seed", "1", "--smoke", smoke,
           "--output-dir", out_dir]
    if experiment:
        cmd += ["--experiment", experiment]
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
    # without the HF measurement there is nothing to decide: report "skipped (smoke_full_hf)", not a second failure
    steps.append(step("decide_runtime", [py, "-m", "scripts.colab.decide_runtime", "--out-dir", out], 600,
                      depends_on=["smoke_full_hf"], description="freeze runtime decisions from the measurements"))
    return steps


FROZEN_RUNTIME = "configs/experiments/runtime_frozen_20261109.json"
IS_CHECK_SMOKE = "max_steps=3"


def v0_steps(ctx):
    """S3 (docs/plan/S3设计_20261109.md section 7): evaluation inputs, train-only decisions, V0 diagnosis, IS check."""
    py, out, model = ctx.python, ctx.out, ctx.model_dir
    public = ctx.root / "public"
    common = [
        step("env_report", [py, "-m", "scripts.colab.env_report", "--root", ctx.root, "--out", out / "env.json"], 900,
             description="software, GPU and environment lock report"),
        step("verify_pack", [py, "-m", "scripts.colab.verify_pack", "--repo", ctx.repo, "--out",
                             out / "pack_verification.json"], 900, description="private data matches its anchors"),
    ]
    decide = [py, "-m", "scripts.colab.decide_s3", "--out-dir", out]
    if ctx.dry_run:
        return common + [
            step("pytest", [py, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests/test_eval_stats.py",
                            "--junitxml=%s" % (out / "pytest.xml")], 1800, env={"CUDA_VISIBLE_DEVICES": ""},
                 description="dry run: one fast test module"),
            step("decide_s3", decide + ["--allow-missing"], 600, description="dry run: decisions from what exists"),
        ]
    steps = common + [
        step("pytest", [py, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--junitxml=%s" % (out / "pytest.xml")], 3600,
             env={"CUDA_VISIBLE_DEVICES": "", "P3_QWEN_PROCESSOR_DIR": model, "HF_HUB_OFFLINE": "1"},
             description="full CPU test suite on the VM (GPU hidden)"),
        step("public_sources", [py, "-m", "scripts.colab.public_sources", "--dest", public, "--out",
                                out / "public_sources.json"], 1800,
             description="pinned Geometry3K wrapper parquets, checked against migration_manifest.json"),
        step("eval_sets", [py, "-m", "scripts.colab.eval_inputs", "eval-sets", "--sources", public, "--out",
                           out / "eval_sets_check.json"], 1800, depends_on=["public_sources"],
             description="evaluation-set rules reproduce reports/eval_sets_20261109/eval_sets.json (no model)"),
        step("cfgeo_build", [py, "-m", "scripts.colab.eval_inputs", "cfgeo", "--sources", public, "--out",
                             out / "cfgeo_build.json"], 1800, depends_on=["public_sources"],
             description="every CF-Geo image rebuilds from its patches to the recorded pixels (no model)"),
        step("prompt_select", [py, "-m", "scripts.colab.prompt_select", "--model-path", model, "--out",
                               out / "prompt_select"], 7200,
             description="P0 vs P1, warm-up and length measurements on 64 approved train problems"),
        step("v0_val82", [py, "-m", "scripts.colab.v0_diagnosis", "--model-path", model, "--out", out / "v0_val82"], 5400,
             description="V0 greedy on the 82 validation problems (with image, without, answer-only): measurement only"),
        step("harness_check", [py, "-m", "scripts.colab.harness_check", "--model-path", model, "--sources", public,
                               "--out", out / "harness_check"], 5400, depends_on=["cfgeo_build"],
             description="the S5 evaluation path on train-only inputs, all five conditions and the statistics"),
    ]
    if ctx.options.get("vllm_probe", True):
        steps += [
            step("vllm_env", [ctx.kernel_python, "-m", "scripts.colab.bootstrap", "vllm-env", "--root", ctx.root], 5400,
                 required=False, description="vLLM venv (CUDA 13 only) for the importance-sampling check"),
            step("is_check", train_cmd(ctx, "rl_v5", IS_CHECK_SMOKE, out / "is_check", runtime=ctx.repo / FROZEN_RUNTIME,
                                       python=ctx.vllm_python), 7200, required=False, depends_on=["vllm_env"],
                 description="3 GRPO steps with vLLM and the frozen runtime: importance-sampling weights (D41)"),
        ]
    steps.append(step("decide_s3", decide, 600, depends_on=["prompt_select"],
                      description="apply the pre-registered S3 decision rules (s3_decisions.json)"))
    return steps


def drive_check_steps(ctx):
    """Cheap CPU-VM check of the optional Drive setup; no data, no GPU environment, no model."""
    return [
        step("env_report", [ctx.python, "-m", "scripts.colab.env_report", "--root", ctx.root, "--out", ctx.out / "env.json"],
             900, required=False, description="VM software, RAM and disk"),
        drive_probe_step(ctx, required=True),
    ]


S4_REGISTRY = "configs/experiments/s4_runs_20261110.json"
PILOT_ARMS = ["rl_ans", "rl_v4", "rl_v5_placebo", "rl_blind"]  # registry pilot.arm_runs, in that order


def drive_flags(ctx):
    flags = []
    for flag, key in [("--drive-remote", "drive_remote"), ("--drive-dir", "drive_dir"), ("--drive-mount", "drive_mount")]:
        if ctx.options.get(key):
            flags += [flag, ctx.options[key]]
    return flags


def s4_common(ctx):
    py, out = ctx.python, ctx.out
    return [
        step("env_report", [py, "-m", "scripts.colab.env_report", "--root", ctx.root, "--out", out / "env.json"], 900,
             description="software, GPU and environment lock report"),
        step("verify_pack", [py, "-m", "scripts.colab.verify_pack", "--repo", ctx.repo, "--out",
                             out / "pack_verification.json"], 900, description="private data matches its anchors"),
    ]


def register_check_step(ctx):
    return step("register_check", [ctx.python, "-m", "scripts.training.register_runs", "--check"], 900,
                description="registered runs equal the configs; data on this VM equals the registered SHA256 and rows")


def vllm_env_step(ctx):
    return step("vllm_env", [ctx.kernel_python, "-m", "scripts.colab.bootstrap", "vllm-env", "--root", ctx.root], 5400,
                description="vLLM venv (CUDA 13): the frozen runtime generates with vLLM")


def pilot_steps(ctx):
    """S4 pilot (docs/plan/S4预注册_20261110.md section 11): train-only, smoke-marked, gates G1-G6."""
    py, out, model = ctx.python, ctx.out, ctx.model_dir
    decide = [py, "-m", "scripts.colab.decide_pilot", "--out-dir", out, "--repo", ctx.repo, "--job", ctx.run_id]
    if ctx.dry_run:  # the test world's synthetic data cannot match the registered SHA256: no register_check here
        return s4_common(ctx) + [
            step("pytest", [py, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests/test_eval_stats.py",
                            "--junitxml=%s" % (out / "pytest.xml")], 1800, env={"CUDA_VISIBLE_DEVICES": ""},
                 description="dry run: one fast test module"),
            step("decide_pilot", decide + ["--python", py, "--allow-missing"], 900,
                 description="dry run: gates from what exists, nothing written to Drive"),
        ]
    supervise = [py, "-m", "scripts.colab.s4_supervise"]
    common = ["--repo", ctx.repo, "--job", ctx.run_id, "--python", ctx.vllm_python, "--model-path", model] + drive_flags(ctx)
    steps = s4_common(ctx) + [
        step("pytest", [py, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--junitxml=%s" % (out / "pytest.xml")], 3600,
             env={"CUDA_VISIBLE_DEVICES": "", "P3_QWEN_PROCESSOR_DIR": model, "HF_HUB_OFFLINE": "1"},
             description="full CPU test suite on the VM (GPU hidden)"),
        register_check_step(ctx),
        drive_probe_step(ctx, required=True),
        vllm_env_step(ctx),
        step("pilot_v5", supervise + ["pilot-run", "--kind", "learning_run", "--name", "pilot_v5", "--out",
                                      out / "pilot_v5", "--drive"] + common, 3 * 3600,
             depends_on=["vllm_env", "drive_probe"],
             description="rl_v5 seed 1, formal shape, 40 steps, checkpoints every 20 steps copied to Drive (G1-G6)"),
        step("pilot_resume", supervise + ["pilot-resume", "--name", "pilot_resume", "--out", out / "pilot_resume"]
             + common, 2 * 3600, depends_on=["vllm_env", "drive_probe"],
             description="small shape: stop after checkpoint-1, restore it from Drive, resume to step 2 (G5)"),
    ]
    for index, arm in enumerate(PILOT_ARMS):
        name = "pilot_" + arm
        steps.append(step(name, supervise + ["pilot-run", "--kind", "arm_runs", "--index", str(index), "--name", name,
                                             "--out", out / name] + common, 3600, depends_on=["vllm_env"],
                          description="%s seed 1, formal shape, 3 steps (G1-G3, G6)" % arm))
    steps += [
        step("pilot_v5_retry", supervise + ["pilot-run", "--kind", "learning_retry", "--name", "pilot_v5_retry", "--out",
                                            out / "pilot_v5_retry", "--only-if-g4-failed", out / "pilot_v5"] + common,
             4 * 3600, depends_on=["vllm_env", "pilot_v5"],
             description="only if G4 failed and the other gates passed: rl_v5, 76 steps"),
        # no depends_on: the gates are decided (and PILOT_LATEST.json written) whatever the pilot runs did
        step("decide_pilot", decide + ["--python", ctx.vllm_python] + drive_flags(ctx), 1800,
             description="gates G1-G6; pilot_gates.json and PILOT_LATEST.json on Drive"),
    ]
    return steps


def train_steps(ctx):
    """S4 formal runs (docs/plan/S4预注册_20261110.md sections 8-12): as many as fit in this VM's remaining time."""
    py, out = ctx.python, ctx.out
    opts = ctx.options
    cmd = [py, "-m", "scripts.colab.train_s4", "--repo", ctx.repo, "--root", ctx.root, "--out", out, "--job", ctx.run_id,
           "--session", opts.get("session") or ""] + drive_flags(ctx)
    for flag, key in [("--max-hours", "max_hours"), ("--vm-hours", "vm_hours"), ("--cu-balance", "cu_balance"),
                      ("--cu-rate", "cu_rate"), ("--cu-measured-epoch", "cu_measured_epoch")]:
        if opts.get(key) is not None:
            cmd += [flag, str(opts[key])]
    if ctx.dry_run:
        return s4_common(ctx) + [
            step("train_runs", cmd + ["--python", py, "--dry-run"], 1800,
                 description="dry run: read the Drive state and print the plan; nothing is written or trained"),
        ]
    cmd += ["--python", ctx.vllm_python, "--model-path", ctx.model_dir]
    return s4_common(ctx) + [
        register_check_step(ctx),
        drive_probe_step(ctx, required=True),
        vllm_env_step(ctx),
        step("train_runs", cmd, 84600, depends_on=["vllm_env", "drive_probe", "register_check"],
             description="registered runs in order: claim, restore from Drive, train, verify on Drive"),
    ]


TASKS = {"preflight": preflight_steps, "drive-check": drive_check_steps, "v0": v0_steps, "pilot": pilot_steps,
         "train": train_steps}


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


__all__ = ["ARMS", "Context", "PILOT_ARMS", "S4_REGISTRY", "TASKS", "prepare", "steps_for"]
