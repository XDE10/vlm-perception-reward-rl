"""Start Ray with the worker settings used in the formal Shuffle-R1 run."""
import ray
from shuffle_r1.main import main

ray.init(runtime_env={
    "env_vars": {"TOKENIZERS_PARALLELISM": "true", "NCCL_DEBUG": "WARN"},
    "worker_process_setup_hook": "configure_determinism.apply",
})
main()
