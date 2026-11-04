#!/bin/bash
#
# Summarize why the tasks of a SLURM job (array) failed.
#
# A task counts as failed if it has an error file but no done file:
#   ./experiments/<experiment>/logs/<job_name>/<job_id>/err/<task>.err
#   ./experiments/<experiment>/logs/<job_name>/<job_id>/done/<task>.done
#
# For each failed task the failure reason is parsed from its error file and
# all reasons are written to:
#   ./experiments/<experiment>/logs/<job_name>/<job_id>/error_dump.csv
# with columns: array_task_id,message
#
# Usage:
#   cli/utils/create_error_dump.sh --experiment <name> --job_id <id>
#
# Example:
#   cli/utils/create_error_dump.sh \
#       --experiment 2026-11-02_reproduce_shen_et_al --job_id 31827680

usage() {
    echo "Usage: $0 --experiment <experiment_name> --job_id <job_id>" >&2
}

experiment=""
job_id=""
while (( $# > 0 )); do
    case "$1" in
        --experiment|--job_id)
            if [[ $# -lt 2 || -z "$2" || "$2" == --* ]]; then
                echo "Missing value for $1" >&2
                usage
                exit 1
            fi
            case "$1" in
                --experiment) experiment="$2" ;;
                --job_id) job_id="$2" ;;
            esac
            shift 2
            ;;
        *)
            echo "Unknown argument: $1" >&2
            usage
            exit 1
            ;;
    esac
done

if [[ -z "$experiment" || -z "$job_id" ]]; then
    usage
    exit 1
fi

# Unmatched globs expand to nothing.
shopt -s nullglob

# Run from the repo root so relative paths work from anywhere.
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${script_dir}/../.." || exit 1

logs_dir="./experiments/${experiment}/logs"
if [[ ! -d "$logs_dir" ]]; then
    echo "No logs directory found at ${logs_dir}" >&2
    exit 1
fi

# Logs live in <logs_dir>/<job_name>/<job_id>.
job_dirs=("${logs_dir}"/*/"${job_id}")
if (( ${#job_dirs[@]} == 0 )); then
    echo "No directory for job ${job_id} found under ${logs_dir}/*/" >&2
    exit 1
elif (( ${#job_dirs[@]} > 1 )); then
    echo "Job ${job_id} matches more than one directory:" >&2
    printf '  %s\n' "${job_dirs[@]}" >&2
    exit 1
fi
job_dir="${job_dirs[0]}"

err_files=("${job_dir}"/err/*.err)
if (( ${#err_files[@]} == 0 )); then
    echo "No .err files found under ${job_dir}/err" >&2
    exit 1
fi

done_files=("${job_dir}"/done/*.done)
output_file="${job_dir}/error_dump.csv"

# Print the reason a task failed, parsed from its error file ($1).
#  1. Last Python exception line (the last line after a Traceback block
#     that is not indented).
#  2. A SLURM kill message (time limit, out of memory, cancellation).
#  3. The last non-empty line of the file.
get_failure_reason() {
    local err_file="$1"
    local reason

    reason=$(awk '
        /^Traceback/ { in_tb = 1; next }
        in_tb && /^[^ \t]/ && !/^Traceback/ { last = $0; in_tb = 0 }
        END { if (last != "") print last }
    ' "$err_file")

    if [[ -z "$reason" ]]; then
        reason=$(grep -iE \
            "DUE TO TIME LIMIT|oom[-_ ]kill|out of memory|CANCELLED" \
            "$err_file" | tail -n 1)
    fi

    if [[ -z "$reason" ]]; then
        reason=$(grep -v '^[[:space:]]*$' "$err_file" | tail -n 1)
    fi

    echo "${reason:-No error message found}"
}

# Quote a string as a CSV field: collapse whitespace, truncate, double quotes.
csv_quote() {
    local text
    text=$(printf '%s' "$1" | tr '\n\t\r' '   ' | tr -s ' ' | cut -c1-500)
    text=${text//\"/\"\"}
    printf '"%s"' "$text"
}

echo "array_task_id,message" > "$output_file"

# Sort numerically so tasks are processed in array order.
mapfile -t sorted_err_files < <(printf '%s\n' "${err_files[@]}" | sort -V)

failed_task_ids=()
for err_file in "${sorted_err_files[@]}"; do
    task_id=$(basename "$err_file" .err)

    # A done file means the task finished successfully.
    [[ -e "${job_dir}/done/${task_id}.done" ]] && continue

    failed_task_ids+=("$task_id")
    reason=$(get_failure_reason "$err_file")
    printf '%s,%s\n' "$task_id" "$(csv_quote "$reason")" >> "$output_file"
done

num_failed=${#failed_task_ids[@]}

printf '%*s\n' 80 '' | tr ' ' '-'
echo "Job ${job_id} (${job_dir})"
echo "Found ${#err_files[@]} .err files and ${#done_files[@]} .done files"
echo "${num_failed} task(s) have an error file but no done file"

if (( num_failed > 0 )); then
    echo ""
    echo "Failed task IDs: --array=$(IFS=,; echo "${failed_task_ids[*]}")"
    echo "Error summary written to ${output_file}"
else
    rm -f "$output_file"
    echo "No failures found"
fi
