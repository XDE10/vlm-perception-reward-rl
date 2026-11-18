"""Run the project entry with the same Ray worker settings as the recovery probe."""
import ray
from shuffle_r1.main import main

ray.init(runtime_env={
    "env_vars": {"TOKENIZERS_PARALLELISM": "true", "NCCL_DEBUG": "WARN"},
    "worker_process_setup_hook": "configure_determinism.apply",
})
main()
