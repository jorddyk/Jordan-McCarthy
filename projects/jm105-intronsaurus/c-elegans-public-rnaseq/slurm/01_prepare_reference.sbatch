#!/usr/bin/env bash
#SBATCH --job-name=JM105_ce_ref
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=4G
#SBATCH --time=12:00:00

set -euo pipefail

# Euler compute nodes inherit ETH proxy variables from the submitting shell.
export NO_PROXY=localhost,127.0.0.1,.ethz.ch
export no_proxy="$NO_PROXY"
: "${WORM_ROOT:?WORM_ROOT is required}"
: "${CODE_ROOT:?CODE_ROOT is required}"
: "${ENV_PREFIX:?ENV_PREFIX is required}"

export PYTHONPATH="$CODE_ROOT/scripts${PYTHONPATH:+:$PYTHONPATH}"
"$ENV_PREFIX/bin/python" "$CODE_ROOT/scripts/prepare_reference.py" \
  --root "$WORM_ROOT" \
  --star "$ENV_PREFIX/bin/STAR" \
  --threads "${SLURM_CPUS_PER_TASK:-8}"
