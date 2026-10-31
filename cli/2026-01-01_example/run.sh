#!/bin/bash
# Fit a one-layer linear network to a dummy dataset with 
# ./experiments/2026-01-01_example/run.py.
#
# Create a single SLURM job. Results and checkpoints are saved under
# ./experiments/<experiment>/results/. Submit the job from the repo's root.
#
# How to run:
#   sbatch --job-name=linear-regression-example cli/2026-01-01_example/run.sh --real
#
# Flags:
#   --real - enable W&B tracking (W&B mode "online") instead of a development
#           run (W&B mode "disabled")

#SBATCH --job-name=linear-regression-example
#SBATCH --partition=day
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=00:10:00
#SBATCH --output=./experiments/2026-01-01_example/logs/%x/%j/out.out
#SBATCH --error=./experiments/2026-01-01_example/logs/%x/%j/err.err
#SBATCH --mail-user=  # TODO: set your email
#SBATCH --mail-type=BEGIN,END,FAIL

experiment="2026-01-01_example"
mkdir -p ./experiments/${experiment}/logs ./experiments/${experiment}/results
set -e

source ./cli/utils/utils.sh
log_slurm_info
activate_uv_env
load_env_vars

# Initialize W&B arguments
wandb_mode="disabled"
real=false

# Initialize training arguments
seed=42

# Update variables based on command line flags
for arg in "$@"; do
    case "$arg" in
    --real) real=true ;;
    *)
        echo "Unknown argument: $arg (expected --real)" >&2
        exit 1
        ;;
    esac
done

# Update W&B arguments based on --real flag
if [[ "$real" == "true" ]]; then
    wandb_mode="online"
fi

run_python_script() {
    uv run python ./experiments/2026-01-01_example/run.py \
        --experiment "$experiment" \
        --seed "$seed" \
        --wandb-mode "$wandb_mode"
}

if run_python_script; then
    log_info "Successfully ran run.py"
    log_error "No errors"
    echo "[$(get_timestamp)] Done" >"$(get_done_file "$experiment")"
    exit 0
else
    log_error "Job failed for $(log_slurm_info)!"
    exit 1
fi
