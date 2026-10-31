# ggl — Agent Instructions

If this file still contains `TODO:` placeholders, tell the user to run `/init-project`; don't ask about them yourself.

## Project overview

TODO: 2-4 lines on what this project is, the data, and the main components.

TODO: run /init-project to fill in this file and rename "ggl" (the placeholder project name) to the real one.

## Never do

- **NEVER modify anything in the repo-root `data/` directory.** Don't create, edit, move, rename or delete files there,
  and don't run commands that write into it (including re-running download or preprocessing scripts) unless the user
  explicitly asks. This covers only the root-level `data/`, not paths like `src/**/data/` or `experiments/*/results/`.
  Exception: `cli/utils/download_dataset.sh` (and any future script that writes into `data/`) may run only when the
  user explicitly asks.
- Never commit `.env`.
- Don't delete `results/` or `done.done` files.
- Confirm before any real (non-dev, `--real`) run that logs to W&B.
- Add dependencies with `uv add`, not by hand-editing `pyproject.toml`. Commit `uv.lock`.
- Do NOT read files in `notes/discussions/` unless explicitly requested (private meeting notes). The rest of `notes/`
  is shared context and fine to read.

## Clarify before acting

Don't make silent assumptions. For any non-trivial task, restate the goal in one or two sentences, then ask about
what is ambiguous and would change what you build or run: outcome, scope (in/out), success criteria, constraints, and
which files, data or experiments are affected.

- Look things up first (repo, configs, scripts, docs); only ask what you couldn't determine.
- Ask in one batch of numbered questions that can be answered in a few words, with likely options and a recommended
  default where helpful. Keep following up until you could explain the task back with no guesses left; if a detail is
  unresolved, say so rather than filling it in. You may proceed on the clear parts meanwhile.
- Stop and ask before anything expensive, slow or hard to undo: large SLURM job arrays or GPU-heavy jobs, deleting or
  overwriting files, changing dependencies, touching shared config. The rules under "Never do" and "Cluster" (`--real`
  runs, `data/`, large arrays) still apply as written. Cheap dev runs (see the New-Experiment Checklist) don't need
  a question.
- Don't over-ask on trivial or fully specified tasks (a typo fix, an explicit command): just do them.
- If the user can't be reached (unattended or scheduled run), do only the safe, reversible part, list every
  assumption at the top of your final summary, and stop before the risky step.
- When finished, list any assumptions you did make so they can be corrected.

## Environment

- Runs on the Yale YCRC **Misha** SLURM cluster.
- Package manager: uv (NOT conda, NOT pip directly). Python version: see `pyproject.toml`.
- Virtual env: `.venv/` at the project root (managed by uv).
- Secrets and local settings live in `.env` (gitignored), loaded by `load_env_vars` in `cli/utils/utils.sh`.

## Cluster

- Before writing sbatch scripts, read `~/.claude/clusters/misha.md` if it exists; otherwise see the
  [YCRC docs](https://docs.ycrc.yale.edu/clusters/misha/).
- Don't run heavy compute on login nodes; use `sbatch` or the interactive launchers.
- Ask before submitting large job arrays.
- Store important outputs in project storage, not scratch (scratch purges old files).

## How to Run Things

Run all commands from the repo root.

```bash
./cli/utils/create_environment.sh                          # install uv (if needed) and create .venv
uv sync --extra dev                                        # install dependencies, including pytest and ruff
uv run python experiments/<experiment>/run.py              # run an experiment locally
sbatch --job-name=<name> cli/<experiment>/run.sh --real    # submit an experiment as a SLURM job
./cli/utils/start_interactive_cpu_session.sh               # interactive CPU node
./cli/utils/start_interactive_gpu_session.sh               # interactive GPU node
```

- `--real` in a `cli/<experiment>/*.sh` script turns on W&B (`online`); without it the run is a dev run (W&B
  `disabled`). The header of each script documents its flags.

### Lint and tests

```bash
uv run ruff check .                                        # lint
uv run ruff format .                                       # format (line length 120)
uv run pytest                                              # all tests
uv run pytest tests/<path>/test_<module>.py -k <name>      # one test file, tests matching a name
```

## Project Layout

- `src/ggl/` — reusable library code (currently `utils/path.py`, `utils/wandb.py`); `ggl` is the placeholder package name.
- `tests/` — pytest; mirrors `src/` (`src/ggl/utils/wandb.py` is tested in `tests/ggl/utils/test_wandb.py`).
- `experiments/` — date-prefixed folders (`YYYY-MM-DD_<short-name>/`); `experiments/README.md` indexes them.
- `cli/` — bash/sbatch scripts: `cli/<experiment>/` per experiment, `cli/utils/` (environment setup, dataset download,
  interactive-node launchers, shared `utils.sh` helpers such as `activate_uv_env`, `load_env_vars`, `log_info`,
  `get_done_file`), `cli/tests/`.
- `notebooks/` — exploratory notebooks.
- `data/` — datasets. Gitignored (only `.gitkeep` is tracked). Read-only; see "Never do".
- `docs/` — project guides for anyone working in the repo (currently `tuning.md`).
- `notes/` — working notes shared as context for Claude: `read/` paper summaries, `writeups/` project formulations and
  reports, `other/` anything else, `discussions/` private meeting notes (off limits, see "Never do").

## Conventions

- Experiments: one `experiments/YYYY-MM-DD_<short-name>/` folder per experiment, with a `README.md` (setup, results,
  observations) and a results notebook. `experiments/README.md` holds only brief descriptions.
- Don't rewrite old experiments; start a new folder. Bug fixes to old experiments are allowed (default; change if you
  prefer otherwise).
- Reusable code goes in `src/`; runnable scripts use argparse. TODO: add a `scripts/` dir if the project needs one.
- sbatch scripts for an experiment go in `cli/<experiment>/` and source `cli/utils/utils.sh`. SLURM logs go under
  `experiments/<experiment>/logs/` (`%x/%j/{out,err}.{out,err}`, or `%x/%A/...` for arrays), plus a `done.done` marker
  written via `get_done_file`.
- Python style: ruff, line length 120. Tracking: wandb (disable with `WANDB_MODE=disabled`).
- Before tuning hyperparameters or writing sweep/tuning scripts, read `docs/tuning.md`.

## New-Experiment Checklist

1. Create `experiments/YYYY-MM-DD_<short-name>/` with a `README.md` and a results notebook; copy the example
   experiment as a starting point. `run.py` is optional.
2. Mirror it in `cli/<experiment>/` with sbatch scripts that source `cli/utils/utils.sh`.
3. Add a brief entry to `experiments/README.md`.
4. Run it as a dev run first; use `--real` only after confirming with the user.

## Gotchas

TODO: project-specific data-integrity rules.
