#!/bin/bash
#
# Shared utility functions for bash scripts.

# Return the current timestamp (Eastern Time) formatted as:
# "month day year, hour:minute:second AM/PM".
get_timestamp() {
    TZ="America/New_York" date +"%b %d, %Y %I:%M:%S%p"
}

# Print timestamped info messages to stdout.
log_info() {
    timestamp=$(get_timestamp)
    echo "[${timestamp}] $*"
}

# Print timestamped error messages to stderr.
log_error() {
    timestamp=$(get_timestamp)
    echo "[${timestamp}] $*" >&2
}

# Activate the project's uv virtual environment.
activate_uv_env() {
    local script_dir
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

    local venv_dir="${script_dir}/../../.venv"
    local venv_activate="${venv_dir}/bin/activate"
    [[ -f "$venv_activate" ]] || venv_activate="${venv_dir}/Scripts/activate"

    if [[ ! -f "$venv_activate" ]]; then
        log_error "uv venv not found in ${venv_dir}. Run 'uv sync' first."
        return 1
    fi

    source "$venv_activate"  
}

# Load the CUDA module. Does nothing when running locally on Windows (Git
# Bash/MSYS/Cygwin), where there is no module system.
load_cuda() {
    case "${OSTYPE:-}" in
    msys* | cygwin* | win32*) return 0 ;;
    esac

    module load CUDA/12.8.0
    export CUDA_HOME="${CUDA_HOME:-$EBROOTCUDA}"
}

# Export WANDB_* variables from the repo .env. Variables already set in the
# environment are left unchanged.
load_wandb() {
    local script_dir
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local env_file="${script_dir}/../../.env"

    if [[ ! -f "$env_file" ]]; then
        log_error ".env not found at ${env_file}."
        return 1
    fi

    local line key value
    while IFS= read -r line || [[ -n "$line" ]]; do
        line="${line%$'\r'}"
        line="${line#"${line%%[![:space:]]*}"}"
        [[ -z "$line" || "$line" == \#* ]] && continue

        if [[ "$line" == export[[:space:]]* ]]; then
            line="${line#export}"
            line="${line#"${line%%[![:space:]]*}"}"
        fi

        [[ "$line" == WANDB_*=* ]] || continue

        key="${line%%=*}"
        key="${key%"${key##*[![:space:]]}"}"
        value="${line#*=}"
        value="${value#"${value%%[![:space:]]*}"}"
        value="${value%"${value##*[![:space:]]}"}"

        if [[ ${#value} -ge 2 && ( "$value" == \"*\" || "$value" == \'*\' ) ]]; then
            value="${value:1:${#value}-2}"
        fi

        if [[ -z "${!key+x}" ]]; then
            export "${key}=${value}"
        fi
    done < "$env_file"
}

# Export all variables from the repo .env. Variables already set in the
# environment are left unchanged.
load_dotenv() {
    local script_dir
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local env_file="${script_dir}/../../.env"

    if [[ ! -f "$env_file" ]]; then
        log_error ".env not found at ${env_file}."
        return 1
    fi

    local line key value
    while IFS= read -r line || [[ -n "$line" ]]; do
        line="${line%$'\r'}"
        line="${line#"${line%%[![:space:]]*}"}"
        [[ -z "$line" || "$line" == \#* ]] && continue

        if [[ "$line" == export[[:space:]]* ]]; then
            line="${line#export}"
            line="${line#"${line%%[![:space:]]*}"}"
        fi

        [[ "$line" == *=* ]] || continue

        key="${line%%=*}"
        key="${key%"${key##*[![:space:]]}"}"
        [[ "$key" =~ ^[a-zA-Z_][a-zA-Z0-9_]*$ ]] || continue
        value="${line#*=}"
        value="${value#"${value%%[![:space:]]*}"}"
        value="${value%"${value##*[![:space:]]}"}"

        if [[ ${#value} -ge 2 && ( "$value" == \"*\" || "$value" == \'*\' ) ]]; then
            value="${value:1:${#value}-2}"
        fi

        if [[ -z "${!key+x}" ]]; then
            export "${key}=${value}"
        fi
    done < "$env_file"
}

# Load all environment variables
load_env_vars() {
    load_cuda
    load_dotenv
}

# Return the path to a "done" file to mark completion of a SLURM job and 
# ensure that the file and its directory exist.
#
# Arguments:
# - $1: Experiment name. The done path is created under
#   ./experiments/<experiment>
#
# The directory path is formatted as follows:
# - If the job is part of a SLURM array, the directory path is:
#     ./experiments/<experiment>/logs/<SLURM_JOB_NAME>/<SLURM_ARRAY_JOB_ID>/done
#
# - Otherwise, the directory path is:
#     ./experiments/<experiment>/logs/<SLURM_JOB_NAME>/<SLURM_JOB_ID>
#
# Where:
# - `SLURM_JOB_NAME`: The name of the SLURM job. Same value as %x.
# - `SLURM_ARRAY_JOB_ID`: The array's master job ID. Same value as %A.
#   On Slurm 24 this differs from SLURM_JOB_ID, which is the task's own job ID.
# - `SLURM_JOB_ID`: The job ID. Used for the directory only when the job is not 
#   an array.
# - `SLURM_ARRAY_TASK_ID`: The index of the array task, if applicable. Same value
#   as %a.
#
# Example output for a job in an array:
#   ./experiments/2026-09-30_sp500-pit_daily_baselines/logs/sp500-pit_daily_baselines/123456/done
#
# Example output for a non-array job:
#   ./experiments/2026-09-30_sp500-pit_daily_baselines/logs/sp500-pit_daily_baselines/123456
#
# The file name is formatted as follows:
# - If the job is part of a SLURM array, the file name is:
#   <SLURM_ARRAY_TASK_ID>.done
#
# - Otherwise, the file name is:
#   done.done
#
# Example output for a job in an array:
#   ./experiments/2026-09-30_sp500-pit_daily_baselines/logs/sp500-pit_daily_baselines/123456/done/0.done
#
# Example output for a non-array job:
#   ./experiments/2026-09-30_sp500-pit_daily_baselines/logs/sp500-pit_daily_baselines/123456/done.done
get_done_file() {
    local experiment="$1"
    local job_id="${SLURM_JOB_ID}"
    local done_file="done.done"
    local is_array=0

    # Array stdout/stderr use %A (SLURM_ARRAY_JOB_ID), not the per-task SLURM_JOB_ID.
    if [[ -n "${SLURM_ARRAY_JOB_ID:-}" ]]; then
        is_array=1
        job_id="${SLURM_ARRAY_JOB_ID}"
        done_file="${SLURM_ARRAY_TASK_ID}.done"
    fi

    local done_dir="./experiments/${experiment}/logs/${SLURM_JOB_NAME}/${job_id}"
    if [[ "$is_array" -eq 1 ]]; then
        done_dir="${done_dir}/done"
    fi

    mkdir -p "$done_dir"

    local done_path="${done_dir}/${done_file}"
    touch "$done_path"
    echo "$done_path"
}

# Log a formatted string containing information about the SLURM job like:
# - `SLURM_JOB_NAME`: The name of the SLURM job, or "N/A" if not set.
# - `SLURM_JOB_ID`: The unique SLURM job ID, or "N/A" if not set.
# - `SLURM_ARRAY_TASK_ID`: The specific task index within the array job, or 
#   "N/A" if not set.
#
# If the job is part of an array, the logged string includes the array task ID.
# Otherwise, it only logs the job name and job ID.
# 
# Example output for a job in an array:
#   "Job Name: foo, Job ID: 123456, Array Task ID: 0"
#
# Example output for a non-array job:
#   "Job Name: foo, Job ID: 123456"
log_slurm_info() {
    local job_name="Job Name: ${SLURM_JOB_NAME:-N/A}"
    local job_id="Job ID: ${SLURM_JOB_ID:-N/A}"
    local array_task_id="Array Task ID: ${SLURM_ARRAY_TASK_ID:-N/A}"

    if [ -n "${SLURM_ARRAY_JOB_ID:-}" ]; then
        echo "${job_name}, ${job_id}, ${array_task_id}"
    else
        echo "${job_name}, ${job_id}"
    fi
}