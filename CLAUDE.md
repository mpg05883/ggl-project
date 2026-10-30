# GGL Project — Claude Instructions

## Environment

- Yale YCRC **Misha** SLURM cluster (Wu Tsai Institute): <https://docs.ycrc.yale.edu/clusters/misha/>
- Package manager: uv (NOT conda, NOT pip directly)
- Python: managed by uv, pinned in pyproject.toml (>=3.11,<3.14)
- Virtual env: `.venv/` at project root (managed by uv)

## Cluster Info

- **Access:** SSH or Open OnDemand; accounts requested at research.computing.yale.edu
- **Partitions:**

  | Partition | Max walltime | Notes |
  | ----------- | -------------- | ------- |
  | `day` (default) | 24h | CPU batch jobs |
  | `devel` | 6h | interactive CPU work (10 CPUs, 70G per user) |
  | `week` | 7 days | long CPU jobs |
  | `gpu` | 48h | H100, H200, A100, A40, L40S; 4 GPUs/node |
  | `gpu_devel` | 6h | GPU debugging (1 A40; 4 CPUs, 32G per user) |
  | `bigmem` | 24h | ~2TB RAM nodes |

- **Default resources (if unspecified):** `--time=01:00:00 --nodes=1 --ntasks=1 --cpus-per-task=1 --mem-per-cpu=5120`
- **Limits:** 4 simultaneous interactive instances; 200 job submissions per hour
- **Storage (`/gpfs/radev`):** home 125GiB/user; project 1TiB/group (expandable to 4TiB); scratch 10TiB/group, files older than 60 days are purged, so keep important data/results in project

## How to Run Things

Run all commands from the repo root.

```bash
./cli/utils/create_environment.sh                                # install uv (if needed) and create .venv
uv sync                                                          # install dependencies
uv run python experiments/<experiment>/run.py                    # run locally
uv run pytest                                                    # run tests
./cli/utils/download_sp500-pit.sh                                # download SP500-PIT data into data/
sbatch experiments/01_baselines/cli/run_baseline.sh              # submit baseline array job
sbatch experiments/01_baselines/cli/evaluate.sh                  # submit evaluation array job
```

Array jobs set `SLURM_ARRAY_TASK_ID` env var; experiments can read it via `os.environ.get("SLURM_ARRAY_TASK_ID")`.

## Project Layout

# TODO: Update for generic project template

- `src/chronosense/` — shared library code for this project (`common.py`, `data.py`, `features.py`, `path.py`)
- `src/allegro/` — leftover template code (`example.py`, `tracking.py`)
- `experiments/` — numbered experiment folders (00_xxx/, 01_xxx/, ...), each with its scripts (e.g. `run.py`), `README.md`, and gitignored `results/`, `logs/`, `figures/`; an experiment may have its own `cli/` with sbatch/bash scripts
- `cli/` — repo-level bash scripts: `cli/utils/` (environment setup, data downloads, shared `utils.sh` helpers such as `activate_uv_env`, `log_info`, `get_done_file`) and `cli/00_example/`
- `data/` — datasets, e.g. `sp500-pit/` (gitignored)
- `tests/` — pytest tests; `tests/chronosense/` mirrors `src/chronosense/` (e.g. `src/chronosense/data/preprocess.py` is tested in `tests/chronosense/data/test_preprocess.py`)

## Conventions

- Experiments: numbered folders in `experiments/` (00_xxx/, 01_xxx/, ...) each with a `run.py`. Create new folders, don't edit old ones.
- Each experiment folder should have a `README.md` with detailed setup, results, and observations. The top-level `experiments/README.md` should only contain brief descriptions of each experiment.
- Reusable code goes in `src/chronosense/` with argparse for flexibility
- Bash/sbatch scripts for an experiment go in `experiments/<experiment>/cli/` and source the `utils.sh` helpers; job logs go under `experiments/<experiment>/logs/` (`job_name=<name>/job_id=<id>[/array_task_id=<n>]/done.done` via `get_done_file`)
- Python style: ruff, line length 120
- Tracking: wandb (disable with `WANDB_MODE=disabled`)
- Do NOT read files in `notes/discussions/` (meeting notes) unless explicitly requested by the user
