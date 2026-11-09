---
inclusion: always
---

# Colab runs in this repository: the user's environment

- The repository lives in WSL2 Ubuntu at `/home/xde10/projects/vlm-perception-reward-rl`
  (from Windows: `\\wsl.localhost\Ubuntu\home\xde10\projects\vlm-perception-reward-rl`). `data/` is inside it,
  and the Colab CLI runs in the same WSL2 environment.
- The user's shell there is zsh. Commands for the user to paste must be zsh-safe: no trailing `# comments`
  (zsh passes them to the command as arguments), quote patterns such as `'refs/heads/results/*'`, and run the
  launcher as `bash colab/launch.sh ...`. Commands for `colab console` run in bash on the VM.
- Two ways to run a task (see `colab/README.md`):
  - `bash colab/launch.sh <task>`: a fresh VM; the launcher downloads the results and pushes `results/<run_id>`.
  - `bash colab/launch.sh <task> --session p3`: a VM the user prepared in `colab console` (section 8:
    Drive mounted with rclone at `/content/mydrive`, GitHub PAT in `/content/gh_credentials`). The VM pushes
    `results/<run_id>` itself; the launcher adds its own logs under `_local/`, and does not release that VM.
- Read results yourself; do not ask the user to paste logs or summaries:
  `git fetch origin 'refs/heads/results/*:refs/remotes/origin/results/*'`, then look under
  `reports/colab_runs_<YYYYMMDD>/<run_id>/` (`summary.md`, `summary.json`, `status.json`, `logs/`, `_local/`;
  `RUN_STOPPED_EARLY.txt` when a run died before its job started).
- Never read, print, copy or log the VM credentials (`/content/gh_credentials`, `~/.config/rclone/rclone.conf`).
