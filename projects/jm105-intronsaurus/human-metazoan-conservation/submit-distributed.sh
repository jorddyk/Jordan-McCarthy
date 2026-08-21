#!/usr/bin/env bash
# Complete Euler submission orchestrator for the distributed JM105 HGPS/metazoan workflow.
# It cancels only the superseded monolithic job ID supplied through OLD_JOB_ID,
# verifies the existing environment, freezes the 34-run manifest, and submits:
#   2 reference jobs in parallel -> 34-task array (max 6 concurrent) -> aggregate.

set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/cluster/scratch/jmccarthy/JM105_HGPS_Metazoan_Conservation}"
CODE_DIR="$PROJECT_ROOT/code"
WORK_ROOT="$PROJECT_ROOT/work"
LOG_DIR="$PROJECT_ROOT/logs/distributed"
MICROMAMBA="$PROJECT_ROOT/software/bin/micromamba"
ENV_NAME="jm105-hgps-conservation"
ENV_PREFIX="$PROJECT_ROOT/software/micromamba-root/envs/$ENV_NAME"
OLD_JOB_ID="${OLD_JOB_ID:-7869397}"
MAX_CONCURRENT_SAMPLES="${MAX_CONCURRENT_SAMPLES:-6}"
export MAMBA_ROOT_PREFIX="$PROJECT_ROOT/software/micromamba-root"
export PATH="$ENV_PREFIX/bin:$PATH"

mkdir -p "$LOG_DIR" "$WORK_ROOT/metadata" "$PROJECT_ROOT/submission"

if [[ ! -x "$MICROMAMBA" ]]; then
    echo "ERROR: Existing micromamba was not found at $MICROMAMBA." >&2
    echo "Run the original environment bootstrap once before this distributed submission." >&2
    exit 1
fi
if [[ ! -x "$ENV_PREFIX/bin/python" ]]; then
    echo "ERROR: Environment Python is absent at $ENV_PREFIX/bin/python." >&2
    exit 1
fi

python3 -m py_compile \
    "$CODE_DIR/scripts/run_hgps_metazoan_conservation.py" \
    "$CODE_DIR/scripts/run_hgps_metazoan_conservation_manifest_hotfix.py" \
    "$CODE_DIR/scripts/jm105_metazoan_distributed.py"

bash -n "$CODE_DIR/slurm/00_prepare_reference.sbatch"
bash -n "$CODE_DIR/slurm/10_process_sample_array.sbatch"
bash -n "$CODE_DIR/slurm/20_aggregate.sbatch"

module load eth_proxy
"$ENV_PREFIX/bin/python" "$CODE_DIR/scripts/jm105_metazoan_distributed.py" \
    audit \
    --root "$WORK_ROOT"

MANIFEST="$WORK_ROOT/metadata/run_manifest.distributed.tsv"
RUN_COUNT="$(awk 'NR > 1 {count += 1} END {print count + 0}' "$MANIFEST")"
if [[ "$RUN_COUNT" -ne 34 ]]; then
    echo "ERROR: Expected 34 manifest rows, observed $RUN_COUNT in $MANIFEST" >&2
    exit 1
fi

# Cancel the superseded monolithic job only after all new code, environment and
# manifest checks have passed. Wait for Slurm to release its allocation before
# submitting replacement jobs that may reuse the same reference directories.
if squeue -h -j "$OLD_JOB_ID" 2>/dev/null | grep -q .; then
    echo "Cancelling superseded monolithic job $OLD_JOB_ID"
    scancel "$OLD_JOB_ID"
    for _ in $(seq 1 60); do
        if ! squeue -h -j "$OLD_JOB_ID" 2>/dev/null | grep -q .; then
            break
        fi
        sleep 2
    done
    if squeue -h -j "$OLD_JOB_ID" 2>/dev/null | grep -q .; then
        echo "ERROR: Job $OLD_JOB_ID is still active after cancellation wait." >&2
        exit 1
    fi
else
    echo "Superseded job $OLD_JOB_ID is not active; nothing to cancel."
fi

HUMAN_JOB="$(sbatch --parsable "$CODE_DIR/slurm/00_prepare_reference.sbatch" human)"
MOUSE_JOB="$(sbatch --parsable "$CODE_DIR/slurm/00_prepare_reference.sbatch" mouse)"
HUMAN_JOB="${HUMAN_JOB%%;*}"
MOUSE_JOB="${MOUSE_JOB%%;*}"
REFERENCE_DEPENDENCY="afterok:${HUMAN_JOB}:${MOUSE_JOB}"
ARRAY_JOB="$(
    sbatch --parsable \
        --dependency="$REFERENCE_DEPENDENCY" \
        --array="1-${RUN_COUNT}%${MAX_CONCURRENT_SAMPLES}" \
        "$CODE_DIR/slurm/10_process_sample_array.sbatch"
)"
ARRAY_JOB="${ARRAY_JOB%%;*}"
AGGREGATE_JOB="$(
    sbatch --parsable \
        --dependency="afterok:${ARRAY_JOB}" \
        "$CODE_DIR/slurm/20_aggregate.sbatch"
)"
AGGREGATE_JOB="${AGGREGATE_JOB%%;*}"

STAMP="$(date +%Y%m%d_%H%M%S)"
SUBMISSION_FILE="$PROJECT_ROOT/submission/distributed_${STAMP}.env"
cat > "$SUBMISSION_FILE" <<EOF
PROJECT_ROOT=$PROJECT_ROOT
MANIFEST=$MANIFEST
RUN_COUNT=$RUN_COUNT
HUMAN_REFERENCE_JOB=$HUMAN_JOB
MOUSE_REFERENCE_JOB=$MOUSE_JOB
SAMPLE_ARRAY_JOB=$ARRAY_JOB
AGGREGATE_JOB=$AGGREGATE_JOB
MAX_CONCURRENT_SAMPLES=$MAX_CONCURRENT_SAMPLES
PRIMARY_METRIC=JM105_IR
PRIMARY_PSEUDOCOUNT=0
EOF
ln -sfn "$SUBMISSION_FILE" "$PROJECT_ROOT/submission/latest.env"

cat <<EOF
DISTRIBUTED_SUBMISSION_COMPLETE
Human reference job : $HUMAN_JOB
Mouse reference job : $MOUSE_JOB
Sample array job    : $ARRAY_JOB (1-$RUN_COUNT, at most $MAX_CONCURRENT_SAMPLES concurrent)
Aggregate job       : $AGGREGATE_JOB
Submission record   : $SUBMISSION_FILE

Monitor all stages:
  squeue -j ${HUMAN_JOB},${MOUSE_JOB},${ARRAY_JOB},${AGGREGATE_JOB}

Detailed accounting:
  sacct -j ${HUMAN_JOB},${MOUSE_JOB},${ARRAY_JOB},${AGGREGATE_JOB} --format=JobID,JobName%22,State,ExitCode,Elapsed,MaxRSS,AllocCPUS

Final report after aggregate completes:
  cat $WORK_ROOT/results/GATE_REPORT.md
EOF
