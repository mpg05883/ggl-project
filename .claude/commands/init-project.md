---
description: One-time setup after creating a repo from this template. Fills in AGENTS.md TODOs and renames "ggl".
---

Initialize this project from the template. Run once. Do not read anything in `notes/discussions/`. Do not commit.

"Machinery lines" in `AGENTS.md` are the two lines that point to this command: the sentence under the title that
starts "If this file still contains `TODO:` placeholders" and the `TODO: run /init-project ...` line in the
Project overview. They do not count as TODOs to fill in.

## Steps

1. Read `AGENTS.md` and `README.md` and list every remaining `TODO:` line, ignoring the machinery lines.

2. Ask the questions in four batches, not one per TODO. Use the AskUserQuestion tool if it is available; otherwise
   use plain numbered questions. Every question needs a "Skip / I don't know" option.
   - Batch 1: the project name (recommended default: the GitHub repo name, see step 5), a 2-4 line overview of what the project is, and the email for `#SBATCH --mail-user=`
     (skip it if the project is local only).
   - Batch 2: the data and the main components (which datasets; which models or modules).
   - Batch 3: compute and tracking.
     - Where does it run: a cluster (which one) or local only? If a cluster, which partition and account should the
       `cli/` scripts default to?
     - Where do results, checkpoints and large outputs go (a persistent path)?
     - Experiment tracker: keep Weights & Biases, use a different one (which), or none?
   - Batch 4: project-specific gotchas and data-integrity rules (the file already has generic leakage examples; show
     them as context), whether the project needs a `scripts/` directory, and whether to keep each *(default)* rule in
     "Never do" and "Conventions" as written (list them and let the user change any).

3. If an answer is skipped or "don't know", leave that TODO in place. Never invent answers or fill in
   plausible-sounding defaults.

4. Write the answers into `AGENTS.md` and `README.md`: replace the matching TODOs, and update the Project overview and
   layout to match (for example, add `scripts/` if wanted, and remove the `TODO: add a scripts/ dir` note either way
   once answered).
   - Overview: write the README's one-paragraph description from the Batch 1 and 2 answers (what the project studies,
     the data, the main components), keeping it consistent with the Project overview in `AGENTS.md`. If those answers
     were skipped, leave the README TODO in place.
   - Compute: if local only, delete the "Cluster rules" section from `AGENTS.md` and the `sbatch` and interactive-node
     lines from the README. If a cluster was named, update the partition, account and resource defaults in the headers
     of `cli/utils/start_interactive_*.sh` and `cli/<example>/run.sh`, and show those edits to the user.
   - Mail: set `#SBATCH --mail-user=` in every `cli/**/run.sh` to the email given.
   - Tracker: if not W&B, tell the user which files reference it (`src/ggl/utils/wandb.py`, its test, the `--real`
     handling in `cli/` scripts) and ask before changing any of them.
   - Remove the `(default)` marker from each rule the user confirmed, and delete any rule they declined.

5. Rename `ggl` to the project name:
   - Default package name: the GitHub repo's name, lowercased, with spaces replaced by underscores (repo `GIFT Eval`
     gives `gift_eval`). Get the repo name from `gh repo view --json name -q .name`, or failing that from the
     `origin` remote URL (`git remote get-url origin`, last path segment without `.git`). If neither works, derive it
     from the project name given in Batch 1 the same way.
   - Make sure the result is Python-safe: letters, digits and underscores only (replace any other character with an
     underscore), not starting with a digit, not a Python keyword. Confirm it with the user before renaming anything,
     offering the default as the recommended option.
   - Rename every whole-word `ggl`: `src/ggl/`, `tests/ggl/`, `cli/tests/ggl.sh` (use `git mv`), imports,
     `pyproject.toml` (project name and the hatch `packages` entry), `AGENTS.md` (title and layout), `README.md`,
     and the files under `experiments/`. Find them with `grep -rIlw ggl . --exclude-dir=.git --exclude-dir=.venv
     --exclude-dir=worktrees --exclude=uv.lock`. Don't hand-edit `uv.lock`.
   - Run `uv sync --extra dev`, `uv run ruff check .` and `uv run pytest`, and report the results. If anything
     fails, show the failure to the user before fixing it.

6. If `CLAUDE.md` exists and contains only `@AGENTS.md`, leave it alone.

7. Show the full `git diff` (and `git status` for new or renamed files).

8. Cleanup, in two parts:
   - Always: remove from `README.md` the `[!IMPORTANT]` callout under the title and the whole "Starting a New Project"
     section (through the line before the next `##` heading). Delete the example experiment folders
     (`experiments/2026-01-01_example/`, `cli/2026-01-01_example/`) only if the user asks.
   - Only if no non-machinery `TODO:` remains in `AGENTS.md`: delete `.claude/commands/init-project.md` (this file) and
     remove both machinery lines from `AGENTS.md`. If any TODOs remain, keep this file and both lines, and tell the
     user which TODOs are left, including any in `README.md` and `cli/` scripts.
