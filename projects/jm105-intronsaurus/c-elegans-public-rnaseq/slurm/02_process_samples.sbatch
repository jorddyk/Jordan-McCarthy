#!/usr/bin/env bash
#SBATCH --job-name=JM105_ce_sample
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=6G
#SBATCH --time=24:00:00

set -euo pipefail

# Euler compute nodes inherit ETH proxy variables from the submitting shell.
export NO_PROXY=localhost,127.0.0.1,.ethz.ch
export no_proxy="$NO_PROXY"
: "${WORM_ROOT:?WORM_ROOT is required}"
: "${CODE_ROOT:?CODE_ROOT is required}"
: "${ENV_PREFIX:?ENV_PREFIX is required}"
: "${MANIFEST:?MANIFEST is required}"
: "${SLURM_ARRAY_TASK_ID:?SLURM_ARRAY_TASK_ID is required}"

export PYTHONPATH="$CODE_ROOT/scripts${PYTHONPATH:+:$PYTHONPATH}"
TMP_BASE="${TMPDIR:-/scratch/tmp.${SLURM_JOB_ID}.${USER}}"
TMP_ROOT="$TMP_BASE/JM105_CELEGANS_${SLURM_ARRAY_JOB_ID:-$SLURM_JOB_ID}_${SLURM_ARRAY_TASK_ID}"
mkdir -p "$TMP_ROOT"

cleanup() {
  rm -rf "$TMP_ROOT"
}
trap cleanup EXIT

"$ENV_PREFIX/bin/python" "$CODE_ROOT/scripts/process_sample.py" \
  --root "$WORM_ROOT" \
  --manifest "$MANIFEST" \
  --array-index "$SLURM_ARRAY_TASK_ID" \
  --env-prefix "$ENV_PREFIX" \
  --threads "${SLURM_CPUS_PER_TASK:-8}" \
  --tmp-root "$TMP_ROOT"
