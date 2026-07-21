#!/usr/bin/env bash
# Purpose: Repair the 2026-07-20 distributed run after micromamba proc-lock failures.
# Inputs: completed outputs from array 7873466 and failed task IDs 1,5,33.
# Outputs: rerun array for only failed tasks, then a new dependent aggregate job.
# Assumptions: the existing jm105-hgps-conservation environment and 31 completed
# sample outputs are intact under the canonical Euler project root.
# Data status: real public RNA-seq; this script does not alter biological values.

set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/cluster/scratch/jmccarthy/JM105_HGPS_Metazoan_Conservation}"
CODE_DIR="$PROJECT_ROOT/code"
WORK_ROOT="$PROJECT_ROOT/work"
SUBMISSION_DIR="$PROJECT_ROOT/submission"
ENV_PREFIX="$PROJECT_ROOT/software/micromamba-root/envs/jm105-hgps-conservation"
FAILED_TASKS="${FAILED_TASKS:-1,5,33}"

export PATH="$ENV_PREFIX/bin:$PATH"

if [[ ! -x "$ENV_PREFIX/bin/python" ]]; then
    echo "ERROR: Environment Python not found at $ENV_PREFIX/bin/python" >&2
    exit 1
fi

for required in \
    "$CODE_DIR/scripts/jm105_metazoan_distributed.py" \
    "$CODE_DIR/slurm/10_process_sample_array.sbatch" \
    "$CODE_DIR/slurm/20_aggregate.sbatch" \
    "$WORK_ROOT/metadata/run_manifest.distributed.tsv"; do
    if [[ ! -f "$required" ]]; then
        echo "ERROR: Required file missing: $required" >&2
        exit 1
    fi
done

python3 -m py_compile \
    "$CODE_DIR/scripts/run_hgps_metazoan_conservation.py" \
    "$CODE_DIR/scripts/run_hgps_metazoan_conservation_manifest_hotfix.py" \
    "$CODE_DIR/scripts/jm105_metazoan_distributed.py"
bash -n "$CODE_DIR/slurm/10_process_sample_array.sbatch"
bash -n "$CODE_DIR/slurm/20_aggregate.sbatch"

COMPLETE_COUNT="$(
    find "$WORK_ROOT/status/sample_complete" \
        -maxdepth 1 -type f -name '*.json' 2>/dev/null | wc -l
)"
if [[ "$COMPLETE_COUNT" -ne 31 ]]; then
    echo "ERROR: Expected 31 completed samples before repair, found $COMPLETE_COUNT." >&2
    exit 1
fi

echo "Resubmitting only failed tasks: $FAILED_TASKS"
REPAIR_ARRAY_JOB="$(
    sbatch --parsable \
        --array="${FAILED_TASKS}%3" \
        "$CODE_DIR/slurm/10_process_sample_array.sbatch"
)"
REPAIR_ARRAY_JOB="${REPAIR_ARRAY_JOB%%;*}"

NEW_AGGREGATE_JOB="$(
    sbatch --parsable \
        --dependency="afterok:${REPAIR_ARRAY_JOB}" \
        "$CODE_DIR/slurm/20_aggregate.sbatch"
)"
NEW_AGGREGATE_JOB="${NEW_AGGREGATE_JOB%%;*}"

mkdir -p "$SUBMISSION_DIR"
STAMP="$(date +%Y%m%d_%H%M%S)"
STATE_FILE="$SUBMISSION_DIR/repair_${STAMP}.env"
cat > "$STATE_FILE" <<EOF
PROJECT_ROOT=$PROJECT_ROOT
MANIFEST=$WORK_ROOT/metadata/run_manifest.distributed.tsv
RUN_COUNT=34
HUMAN_REFERENCE_JOB=7873443
MOUSE_REFERENCE_JOB=7873444
SAMPLE_ARRAY_JOB=$REPAIR_ARRAY_JOB
AGGREGATE_JOB=$NEW_AGGREGATE_JOB
ORIGINAL_SAMPLE_ARRAY_JOB=7873466
FAILED_TASKS=$FAILED_TASKS
PRIMARY_METRIC=JM105_IR
PRIMARY_PSEUDOCOUNT=0
EOF
ln -sfn "$STATE_FILE" "$SUBMISSION_DIR/latest.env"

echo
echo "REPAIR_SUBMISSION_COMPLETE"
echo "Repair sample array: $REPAIR_ARRAY_JOB (tasks $FAILED_TASKS only)"
echo "New aggregate job : $NEW_AGGREGATE_JOB"
echo "State file        : $STATE_FILE"
echo
echo "Monitor with:"
echo "  bash $CODE_DIR/watch-distributed.sh"
