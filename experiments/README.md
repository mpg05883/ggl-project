# Experiments

Each date-prefixed folder is a self-contained experiment with its own `README.md`, results notebook, and results.

| Date | Name | Status | Description |
|------|------|--------|-------------|
| 2026-01-01 | `2026-01-01_example` | Template | End-to-end sanity check of the project setup |

## Convention
- Create a new `YYYY-MM-DD_<short-name>/` folder for each experiment — don't rewrite old ones.
- Each folder contains: `README.md` (setup, results, observations), a results notebook, `results/`, `logs/`, and optionally `run.py`.
- Mirror it in `cli/<experiment>/` with sbatch scripts.
- This README should only contain brief descriptions of each experiment. Detailed setup, results, and observations belong in each experiment's own `README.md`.
