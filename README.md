# ggl

> [!IMPORTANT]
> **Just created a repo from this template? Run `/init-project` first.**
> Open Claude Code in the repo root and run `/init-project` before doing anything else below. It fills in
> `AGENTS.md` and this README, renames the placeholder `ggl` to your project name, and checks that the environment,
> linter and tests work.

TODO: one-paragraph description of the project (what it studies, the data, the main components).

TODO: where this project runs (cluster name, or local only). Package management is done with
[uv](https://docs.astral.sh/uv/).

## Starting a New Project

*Template-only section. Delete it once the project is initialized.*

1. Click **"Use this template"** on GitHub to create your repo, then clone it:

   ```bash
   git clone git@github.com:<your-username>/<your-project>.git
   cd <your-project>
   ```

2. **Run `/init-project` in Claude Code.** This is the first step. It asks about your project (name, data, where it
   runs, tracker, gotchas), fills in the `TODO:` items in `AGENTS.md` and this README, sets `#SBATCH --mail-user=`,
   renames `ggl` everywhere (package, imports, `pyproject.toml`, scripts), then runs `uv sync --extra dev`, `ruff`
   and `pytest`.
3. Continue with [Setup](#setup).

Without Claude Code, find every place to rename by hand with:

```bash
grep -rIlw ggl . --exclude-dir=.git --exclude-dir=.venv --exclude-dir=worktrees --exclude=uv.lock
```

You will also need to fill in the `TODO:` items in `AGENTS.md` and this README, and set `#SBATCH --mail-user=` in the
`cli/` scripts.

## Setup

Assumes `/init-project` has been run. Run all commands from the repo root.

```bash
./cli/utils/create_environment.sh   # install uv (if needed) and create .venv
uv sync --extra dev                 # install dependencies, including pytest and ruff
```

Create a `.env` file in the repo root for secrets and local settings (e.g. your W&B API key). It is gitignored and
loaded by `load_env_vars` in `cli/utils/utils.sh`.

## Usage

```bash
# Run an experiment locally (uv run handles the venv)
uv run python experiments/<experiment>/run.py

# SLURM only (skip if the project runs locally): submit as a job (dev run: tracking disabled)
sbatch --job-name=<name> cli/<experiment>/run.sh
# Real run: tracking online
sbatch --job-name=<name> cli/<experiment>/run.sh --real

# Interactive nodes (SLURM only)
./cli/utils/start_interactive_cpu_session.sh
./cli/utils/start_interactive_gpu_session.sh

# Lint, format, test
uv run ruff check .
uv run ruff format .
uv run pytest
```

Don't run heavy compute on login nodes. Always do a dev run before `--real`. The `data/` directory is gitignored and
read-only; `cli/utils/download_dataset.sh` populates it.

## Project Structure

```text
src/ggl/           # Reusable library code
tests/             # pytest; mirrors src/
experiments/       # One date-prefixed folder per experiment, plus an index README
cli/               # bash/sbatch scripts: per experiment, plus utils/ (setup, data download, interactive nodes)
notebooks/         # Exploratory notebooks
data/              # Datasets (gitignored, read-only)
docs/              # Project guides (e.g. tuning.md)
notes/             # Working notes: read/ paper summaries, writeups/ reports, other/, discussions/ (private)
```

## Experiments

Each experiment lives in `experiments/YYYY-MM-DD_<short-name>/` with a `README.md` (setup, results, observations), a
results notebook, and optionally a `run.py`. Its sbatch scripts go in `cli/<experiment>/`. Start a new folder for each
new experiment rather than rewriting old ones, and add a brief entry to `experiments/README.md`.

Copy [`experiments/2026-01-01_example/`](experiments/2026-01-01_example) and
[`cli/2026-01-01_example/`](cli/2026-01-01_example) as a starting point. They are examples only: delete them (and
their entries in `experiments/README.md`) once you have your own experiments.

## Experiment Tracking

Runs are tracked with Weights & Biases by default. `--real` turns it on (`online`); otherwise it is `disabled`. To
disable it manually:

```bash
export WANDB_MODE=disabled
```

TODO: if this project uses a different tracker, or none, update this section.

For hyperparameter tuning, see [`docs/tuning.md`](docs/tuning.md).

## For AI Agents

Project instructions for Claude Code live in [`AGENTS.md`](AGENTS.md) (imported by `CLAUDE.md`).
