#!/usr/bin/env bash
#SBATCH --job-name=JM105_ce_aggregate
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=8G
#SBATCH --time=12:00:00

set -euo pipefail
: "${WORM_ROOT:?WORM_ROOT is required}"
: "${CODE_ROOT:?CODE_ROOT is required}"
: "${ENV_PREFIX:?ENV_PREFIX is required}"
: "${MANIFEST:?MANIFEST is required}"

export PYTHONPATH="$CODE_ROOT/scripts${PYTHONPATH:+:$PYTHONPATH}"
"$ENV_PREFIX/bin/python" "$CODE_ROOT/scripts/aggregate_and_render.py" \
  --root "$WORM_ROOT" \
  --manifest "$MANIFEST"
