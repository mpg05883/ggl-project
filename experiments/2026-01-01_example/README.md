# Example

End-to-end sanity check of the project setup: fit a one-layer linear network to a dummy dataset, save the results, and optionally track the run with W&B.

## Setup

- Data: 256 samples with `x ~ U(-1, 1)` and `y = 3.0 * x + 0.5 + N(0, 0.1)` (`--true-weight`, `--true-bias`,
  `--num-samples`).
- Model: `LinearRegressor`, a single `nn.Linear(1, 1)` layer trained with MSE loss and SGD (`--lr 0.1`).
- Training: 50 epochs, batch size 32, CPU, seed 42 (`--epochs`, `--batch-size`, `--seed`). `deterministic=True`, so
  a given seed reproduces the run.
- W&B: `--wandb-mode` is `disabled` by default. When it is on, the run logs the results and uploads the final checkpoint as
  a `model` artifact (saved through a temporary directory).

## Run

```bash
# Python script
uv run python experiments/2026-01-01_example/run.py --experiment 2026-01-01_example --seed 0

# SLURM job
sbatch --job-name=example cli/2026-01-01_example/run.sh --real
```

Pass `--experiment 2026-01-01_example` when running `run.py` directly. Its default is still `2026-01-01_example`, which
would write the results to a different folder. `run.sh` passes it for you. `--real` turns on W&B (`online`).

## Outputs

| File | Description |
| ---- | ----------- |
| `results/losses.csv` | Mean training loss at the end of each epoch |
| `results/results.json` | Learned and true weight and bias, final loss, and all arguments |
| `results/checkpoints/model.ckpt` | Final Lightning checkpoint |
| `figures/losses.png` | Loss curve, saved by `results.ipynb` |

## Results

Analysis in `view_results.ipynb` (loss curve and a one-row table of the parameters).

| learned weight | true weight | learned bias | true bias | final loss |
| -------------- | ------------ | ----------- | --------- | ---------- |
| 2.9924 | 3.0 | 0.5006 | 0.5 | 0.00915 |

## Observations

- The loss falls from 2.06 after epoch 1 to 0.57 after epoch 2 and to 0.0092 after epoch 50, and the learned parameters are
  within 0.01 of the true ones.
- The final loss is near the noise floor: the noise variance is 0.1^2 = 0.01.
