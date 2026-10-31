---
description: One-time setup after creating a repo from this template. Fills in AGENTS.md TODOs and renames "ggl".
---

Initialize this project from the template. Run once. Do not read anything in `notes/discussions/`. Do not commit.

"Machinery lines" in `AGENTS.md` are the two lines that point to this command: the sentence under the title that
starts "If this file still contains `TODO:` placeholders" and the `TODO: run /init-project ...` line in the
Project overview. They do not count as TODOs to fill in.

## Steps

1. Read `AGENTS.md` and list every remaining `TODO:` line, ignoring the machinery lines.

2. Ask the questions in three batches, not one per TODO. Use the AskUserQuestion tool if it is available; otherwise
   use plain numbered questions. Every question needs a "Skip / I don't know" option.
   - Batch 1: the project name, and a 2-4 line overview of what the project is.
   - Batch 2: the data and the main components (which datasets; which models or modules).
   - Batch 3: project-specific gotchas and data-integrity rules (the file already has generic leakage examples; show
     them as context), and whether the project needs a `scripts/` directory.

3. If an answer is skipped or "don't know", leave that TODO in place. Never invent answers or fill in
   plausible-sounding defaults.

4. Write the answers into `AGENTS.md`: replace the matching TODOs, and update the Project overview and Project Layout
   to match (for example, add `scripts/` to the layout if wanted, and remove the `TODO: add a scripts/ dir` note
   either way once answered).

5. Rename `ggl` to the project name:
   - Derive a Python-safe package name from the project name: lowercase, letters, digits and underscores only, not
     starting with a digit, not a Python keyword. Confirm it with the user before renaming anything.
   - Rename every whole-word `ggl`: `src/ggl/`, `tests/ggl/`, `cli/tests/ggl.sh` (use `git mv`), imports,
     `pyproject.toml` (project name and the hatch `packages` entry), `AGENTS.md` (title and layout), `README.md`,
     and the files under `experiments/`. Find them with `grep -rIlw ggl . --exclude-dir=.git --exclude-dir=.venv
     --exclude-dir=worktrees --exclude=uv.lock`. Don't hand-edit `uv.lock`.
   - Run `uv sync --extra dev`, `uv run ruff check .` and `uv run pytest`, and report the results. If anything
     fails, show the failure to the user before fixing it.

6. If `CLAUDE.md` exists and contains only `@AGENTS.md`, leave it alone.

7. Show the full `git diff` (and `git status` for new or renamed files).

8. Cleanup, only if no non-machinery `TODO:` remains in `AGENTS.md`: delete `.claude/commands/init-project.md` (this
   file), remove both machinery lines from `AGENTS.md`, and remove from `README.md` the `[!IMPORTANT]` callout under
   the title and the whole "Starting a New Project" section (through the line before the next `##` heading). If any
   TODOs remain, keep this file, both lines, and those README parts, and tell the user which TODOs are left. Also
   mention TODOs in `README.md` and `cli/` scripts, which this command does not handle.
