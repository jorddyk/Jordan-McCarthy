#!/usr/bin/env bash
#SBATCH --job-name=JM105_ce_driver
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=4G
#SBATCH --time=04:00:00

set -euo pipefail

: "${WORM_ROOT:?WORM_ROOT is required}"
: "${CODE_ROOT:?CODE_ROOT is required}"
: "${ENV_PREFIX:?ENV_PREFIX is required}"

PYTHON="$ENV_PREFIX/bin/python"
MANIFEST_DIR="$WORM_ROOT/work/metadata"
MANIFEST="$MANIFEST_DIR/run_manifest.tsv"
LOG_DIR="$WORM_ROOT/logs"
LEDGER="$WORM_ROOT/job_ledger.env"

mkdir -p "$MANIFEST_DIR" "$LOG_DIR" "$WORM_ROOT/work/results"

for required in \
  "$PYTHON" \
  "$CODE_ROOT/config/datasets.tsv" \
  "$CODE_ROOT/scripts/build_manifest.py" \
  "$CODE_ROOT/slurm/01_prepare_reference.sbatch" \
  "$CODE_ROOT/slurm/02_process_samples.sbatch" \
  "$CODE_ROOT/slurm/03_aggregate.sbatch"
do
  if [[ ! -e "$required" ]]; then
    echo "ERROR: missing required path: $required" >&2
    exit 20
  fi
done

export PYTHONPATH="$CODE_ROOT/scripts${PYTHONPATH:+:$PYTHONPATH}"

"$PYTHON" "$CODE_ROOT/scripts/build_manifest.py" \
  --datasets "$CODE_ROOT/config/datasets.tsv" \
  --output-dir "$MANIFEST_DIR"

if [[ ! -s "$MANIFEST" ]]; then
  echo "ERROR: manifest was not created: $MANIFEST" >&2
  exit 21
fi

N_TASKS=$(( $(wc -l < "$MANIFEST") - 1 ))
if [[ "$N_TASKS" -lt 1 ]]; then
  echo "ERROR: manifest contains no data rows." >&2
  exit 22
fi

REFERENCE_JOB=$(sbatch --parsable \
  --export=ALL,WORM_ROOT="$WORM_ROOT",CODE_ROOT="$CODE_ROOT",ENV_PREFIX="$ENV_PREFIX" \
  --output="$LOG_DIR/reference_%j.out" \
  --error="$LOG_DIR/reference_%j.err" \
  "$CODE_ROOT/slurm/01_prepare_reference.sbatch")

SAMPLE_JOB=$(sbatch --parsable \
  --dependency="afterok:$REFERENCE_JOB" \
  --array="1-${N_TASKS}%4" \
  --export=ALL,WORM_ROOT="$WORM_ROOT",CODE_ROOT="$CODE_ROOT",ENV_PREFIX="$ENV_PREFIX",MANIFEST="$MANIFEST" \
  --output="$LOG_DIR/sample_%A_%a.out" \
  --error="$LOG_DIR/sample_%A_%a.err" \
  "$CODE_ROOT/slurm/02_process_samples.sbatch")

AGGREGATE_JOB=$(sbatch --parsable \
  --dependency="afterok:$SAMPLE_JOB" \
  --export=ALL,WORM_ROOT="$WORM_ROOT",CODE_ROOT="$CODE_ROOT",ENV_PREFIX="$ENV_PREFIX",MANIFEST="$MANIFEST" \
  --output="$LOG_DIR/aggregate_%j.out" \
  --error="$LOG_DIR/aggregate_%j.err" \
  "$CODE_ROOT/slurm/03_aggregate.sbatch")

cat > "$LEDGER" <<LEDGER
PIPELINE_VERSION=2026-07-22.3
DRIVER_JOB=${SLURM_JOB_ID:-NA}
REFERENCE_JOB=$REFERENCE_JOB
SAMPLE_JOB=$SAMPLE_JOB
AGGREGATE_JOB=$AGGREGATE_JOB
N_TASKS=$N_TASKS
WORM_ROOT=$WORM_ROOT
CODE_ROOT=$CODE_ROOT
MANIFEST=$MANIFEST
LEDGER

cat <<REPORT
JM105 C. elegans pipeline submitted.
Driver:    ${SLURM_JOB_ID:-NA}
Reference: $REFERENCE_JOB
Samples:   $SAMPLE_JOB (1-$N_TASKS, max 4 concurrent)
Aggregate: $AGGREGATE_JOB
Ledger:    $LEDGER
REPORT
