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

Document each dataset and model you use in `docs/` (e.g. `docs/datasets.md`, `docs/models.md`): source, version or
checkpoint, how `data/` is populated, and for datasets the exact splits (sizes, how they were made, seeds) and any
preprocessing. Claude Code reads these when scaffolding experiments, so keep them current.

## Project Structure

```text
src/ggl/           # Reusable library code
tests/             # pytest; mirrors src/
experiments/       # One date-prefixed folder per experiment, plus an index README
cli/               # bash/sbatch scripts: per experiment, plus utils/ (setup, data download, interactive nodes)
notebooks/         # Exploratory notebooks
data/              # Datasets (gitignored, read-only)
docs/              # Project guides: datasets (splits, preprocessing), models, hyperparameter_tuning.md
notes/             # Working notes: ideas/ experiment proposals, read/ paper summaries, writeups/ reports, other/, discussions/ (private)
```

## Experiments

Each experiment lives in `experiments/YYYY-MM-DD_<short-name>/` with a `README.md` (setup, results, observations), a
results notebook, and optionally a `run.py`. Its sbatch scripts go in `cli/<experiment>/`. Start a new folder for each
new experiment rather than rewriting old ones, and add a brief entry to `experiments/README.md`.

Copy [`experiments/2026-01-01_example/`](experiments/2026-01-01_example) and
[`cli/2026-01-01_example/`](cli/2026-01-01_example) as a starting point. They are examples only: delete them (and
their entries in `experiments/README.md`) once you have your own experiments.

## Git Workflow

Branches are named `<type>/<short-description>`: lowercase, hyphen-separated, 2-4 words. Don't put dates or run IDs in
branch names; those belong in commit messages, tags, or your experiment tracker. In multi-person repos, prefix your name
(`mike/exp/lora-rank-sweep`); skip the prefix for solo projects.

| Type | Use for |
|------|---------|
| `exp` | Experiments: new runs, sweeps, ablations, hypothesis tests |
| `feat` | New functionality in the codebase |
| `fix` | Bug fixes |
| `refactor` | Restructuring with no behavior change |
| `docs` | README, `AGENTS.md`, and other documentation |
| `chore` | Dependency bumps, config, tooling |

Examples: `exp/lora-rank-sweep`, `feat/lr-warmup-scheduler`, `fix/dataloader-seed`, `chore/bump-torch`.

Keep `main` always runnable: no half-finished experiment code on `main`. The agent-facing version of these rules is in
[`AGENTS.md`](AGENTS.md).

### Experiment branches

`exp/` branches are distinct because they live longer, diverge further from `main`, and are often exploratory, so they
have their own lifecycle. Name them after the question or variable being tested, not the outcome: `exp/lora-rank-sweep`,
not `exp/best-lora-config`. (The experiment *folder*, `experiments/YYYY-MM-DD_<short-name>/`, still carries a date; the
branch name does not.)

1. **Create** the branch from `main`:

   ```bash
   git switch main && git switch -c exp/lora-rank-sweep
   ```

2. **Run** the experiment on the branch: scaffold the folder, iterate, do dev runs, then real runs.
3. **Conclude** in one of two ways:
   - **Keep the useful code.** Merge it into `main`. If the changes need cleanup first, move them onto a `feat/` or
     `refactor/` branch and merge that instead, so `main` only gets finished code.
   - **Archive.** Tag the final commit and delete the branch:

     ```bash
     git tag archive/exp/lora-rank-sweep
     git branch -D exp/lora-rank-sweep
     git push origin archive/exp/lora-rank-sweep   # if you use a remote
     ```

Results and configs for an experiment should be reproducible from the tagged (or merged) commit, so commit the configs
and seeds, and note the commit hash wherever you record the results.

## Example Workflow with Claude Code

A typical loop from idea to results. Conventions (naming, layout, tracking) are in [`AGENTS.md`](AGENTS.md), which
Claude Code reads automatically.

1. **Draft the idea.** Ask Claude Code to write a short proposal in `notes/writeups/<short-name>.md`:

   > Draft an experiment idea for <topic> in `notes/writeups/`. Check `docs/datasets.md` and `docs/models.md` for the
   > available data, splits, and models. Include the hypothesis, variables, baselines, metrics, and what result would
   > change our plans.

   Read and edit it before moving on. This is the cheapest place to catch a bad design.

2. **Scaffold the experiment.** Once you're happy with the idea:

   > Create `experiments/YYYY-MM-DD_<short-name>/` from the idea in `notes/writeups/<short-name>.md`, following the
   > example experiment. Add `run.py` and the matching sbatch script at `cli/YYYY-MM-DD_<short-name>/run.sh`, and add
   > an entry to `experiments/README.md`.

3. **Dev run.** Smoke-test locally or on an interactive node with tracking disabled, then submit a dev job:

   ```bash
   uv run python experiments/YYYY-MM-DD_<short-name>/run.py
   sbatch --job-name=<name> cli/YYYY-MM-DD_<short-name>/run.sh
   ```

   Fix problems here, before spending compute on a real run.

4. **Real run.** Once the dev run is clean:

   ```bash
   sbatch --job-name=<name> cli/YYYY-MM-DD_<short-name>/run.sh --real
   ```

5. **View results.** After the run finishes:

   > Create a results notebook in `experiments/YYYY-MM-DD_<short-name>/` that loads the outputs of this run and plots
   > <metrics>. Then fill in the Results and Observations sections of the experiment's `README.md`.

## Experiment Tracking

Runs are tracked with Weights & Biases by default. `--real` turns it on (`online`); otherwise it is `disabled`. To
disable it manually:

```bash
export WANDB_MODE=disabled
```

TODO: if this project uses a different tracker, or none, update this section.

For hyperparameter tuning, see [`docs/hyperparameter_tuning.md`](docs/hyperparameter_tuning.md).

## For AI Agents

Project instructions for Claude Code live in [`AGENTS.md`](AGENTS.md) (imported by `CLAUDE.md`).
