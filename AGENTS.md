# ggl — Agent Instructions

If this file still contains `TODO:` placeholders, tell the user to run `/init-project`; don't ask about them yourself.

## Project overview

TODO: 2-4 lines on what this project is, the data, and the main components.

TODO: run /init-project to fill in this file and rename "ggl" (the placeholder project name) to the real one.

Commands, setup and directory structure are in `README.md`. This file holds the rules and context that aren't obvious
from the code.

## Never do

Rules marked *(default)* are template defaults that `/init-project` confirms; the others are always on.

- Never commit `.env`.
- Don't delete `results/` or `done.done` files.
- Add dependencies with `uv add`, not by hand-editing `pyproject.toml`. Commit `uv.lock`.
- *(default)* **NEVER modify anything in the repo-root `data/` directory.** Don't create, edit, move, rename or delete
  files there, and don't run commands that write into it (including re-running download or preprocessing scripts)
  unless the user explicitly asks. This covers only the root-level `data/`, not paths like `src/**/data/` or
  `experiments/*/results/`. Exception: `cli/utils/download_dataset.sh` (and any future script that writes into `data/`)
  may run only when the user explicitly asks.
- *(default)* Confirm before any real (non-dev, `--real`) run that logs to the experiment tracker.
- *(default)* Do NOT read files in `notes/discussions/` unless explicitly requested (private meeting notes). The rest
  of `notes/` is shared context and fine to read.

## Clarify before acting

Don't make silent assumptions. For any non-trivial task, restate the goal in one or two sentences, then ask about what
is ambiguous and would change what you build or run: outcome, scope, success criteria, constraints, and which files,
data or experiments are affected.

- Look things up first (repo, configs, scripts, docs); only ask what you couldn't determine.
- Ask in one batch of numbered questions that can be answered in a few words, with likely options and a recommended
  default. If a detail is unresolved, say so rather than filling it in. You may proceed on the clear parts meanwhile.
- Ask only when a wrong guess would cost more than a dev run. Don't over-ask on trivial or fully specified tasks (a
  typo fix, an explicit command): just do them.
- Stop and ask before anything expensive, slow or hard to undo: large job arrays or GPU-heavy jobs, deleting or
  overwriting files, changing dependencies, touching shared config. Cheap dev runs don't need a question.
- If the user can't be reached (unattended or scheduled run), do only the safe, reversible part, list every
  assumption at the top of your final summary, and stop before the risky step.
- When finished, list any assumptions you did make so they can be corrected.

## Environment

- Package manager: uv (NOT conda, NOT pip directly). Python version: see `pyproject.toml`. Virtual env: `.venv/` at
  the project root.
- Secrets and local settings live in `.env` (gitignored), loaded by `load_env_vars` in `cli/utils/utils.sh`.
- `.claude/settings.json` runs `ruff format` automatically after every edit, so don't run it again by hand.
- Compute: TODO: where this project runs (cluster name, or "local only"). For cluster-specific notes, read
  `~/.claude/clusters/<cluster>.md` if it exists. Partition, account and resource defaults are set in the header of
  each `cli/` script (the interactive launchers also read `PARTITION` and `ACCOUNT` env vars).
- Outputs: TODO: where results, checkpoints and large outputs are stored (use persistent storage, not purgeable
  scratch space, for anything you need to keep).

## Cluster rules

Skip this section if the project is local only.

- Don't run heavy compute on login nodes; use `sbatch` or the interactive launchers in `cli/utils/`.
- Ask before submitting large job arrays.
- Cluster-specific setup (SLURM conventions, storage paths, module/env quirks) lives in `docs/clusters/<name>.md`.
  Before submitting or configuring any job, read the file for the cluster you're on (e.g. `docs/clusters/misha.md`).

## Conventions

- Experiments: one `experiments/YYYY-MM-DD_<short-name>/` folder per experiment, with a `README.md` (setup, results,
  observations) and a results notebook. `experiments/README.md` holds only brief descriptions.
- Experiment ideas are drafted in `notes/ideas/<short-name>.md` (hypothesis, variables, baselines, metrics, what result
  would change our plans) and reviewed by the user before any code is scaffolded.
- Don't rewrite old experiments; start a new folder. Bug fixes to old experiments are allowed *(default)*.
- Reusable code goes in `src/ggl/`; runnable scripts use argparse. TODO: add a `scripts/` dir if the project needs one.
- sbatch scripts for an experiment go in `cli/<experiment>/` and source `cli/utils/utils.sh`. Logs go under
  `experiments/<experiment>/logs/`, plus a `done.done` marker written via `get_done_file`.
- Tests mirror `src/` (`src/ggl/utils/wandb.py` is tested in `tests/ggl/utils/test_wandb.py`).
- Python style: ruff, line length 120.
- Experiment tracking defaults to Weights & Biases (`--real` turns it on, otherwise it is `disabled`). TODO: if this
  project uses a different tracker, or none, say so here and update `src/ggl/utils/wandb.py` and the `cli/` scripts.
- Before tuning hyperparameters or writing sweep/tuning scripts, read `docs/tuning.md`.
- Before designing an experiment or writing data-loading, preprocessing or model code, read `docs/datasets.md` (sources,
  splits, preprocessing) and `docs/models.md` (checkpoints, configs). Take splits from there; never re-derive or guess
  them. If a doc is missing, a stub, or doesn't cover what you need, ask the user rather than filling it in.
- Keep those docs current: when you change a split, preprocessing step or model, update the doc in the same change. They
  should describe what the code does (e.g. name the function that builds each split and its seed), not replace it.

## New-Experiment Checklist

1. Read `docs/datasets.md` and `docs/models.md`; ground the idea in `notes/ideas/<short-name>.md` in what exists there.
2. Create `experiments/YYYY-MM-DD_<short-name>/` with a `README.md` and a results notebook; copy the example
   experiment as a starting point. `run.py` is optional.
3. Mirror it in `cli/<experiment>/` with sbatch scripts that source `cli/utils/utils.sh`.
4. Add a brief entry to `experiments/README.md`.
5. Run it as a dev run first; use `--real` only after confirming with the user.

## Gotchas

TODO: project-specific data-integrity rules. Examples to adapt or delete:

- Never tune hyperparameters or choose checkpoints on the test split.
- Fit preprocessing (scalers, tokenizers, normalization statistics) on training data only.
- Split by the right unit (subject, series, document), not by row, to avoid leakage across splits.
- Fix random seeds and record them in each experiment's README.
