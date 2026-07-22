#!/usr/bin/env bash
set -euo pipefail

WORM_ROOT="${WORM_ROOT:-/cluster/scratch/jmccarthy/JM105_CELEGANS_WORM_ANALYSIS}"
CODE_ROOT="${CODE_ROOT:-$WORM_ROOT/code/JM105_CELEGANS_WORM_ANALYSIS}"
ENV_PREFIX="${ENV_PREFIX:-/cluster/scratch/jmccarthy/JM105_HGPS_Metazoan_Conservation/software/micromamba-root/envs/jm105-hgps-conservation}"
LOG_DIR="$WORM_ROOT/logs"

if ! env | grep -qiE '^(http|https)_proxy='; then
  echo "ERROR: no HTTP/HTTPS proxy is exported. Run 'module load eth_proxy' in the Euler login shell before submission." >&2
  exit 9
fi

mkdir -p "$LOG_DIR" "$WORM_ROOT/work"

for tool in python STAR samtools prefetch fasterq-dump; do
  if [[ ! -x "$ENV_PREFIX/bin/$tool" ]]; then
    echo "ERROR: missing executable $ENV_PREFIX/bin/$tool" >&2
    exit 10
  fi
done

for package in numpy pandas scipy pysam matplotlib; do
  if ! "$ENV_PREFIX/bin/python" -c "import $package" >/dev/null 2>&1; then
    echo "ERROR: Python package '$package' is missing from $ENV_PREFIX" >&2
    exit 11
  fi
done

if [[ ! -f "$CODE_ROOT/slurm/00_driver.sbatch" ]]; then
  echo "ERROR: code bundle was not unpacked at $CODE_ROOT" >&2
  exit 12
fi

DRIVER_JOB=$(sbatch --parsable \
  --export=ALL,WORM_ROOT="$WORM_ROOT",CODE_ROOT="$CODE_ROOT",ENV_PREFIX="$ENV_PREFIX" \
  --output="$LOG_DIR/driver_%j.out" \
  --error="$LOG_DIR/driver_%j.err" \
  "$CODE_ROOT/slurm/00_driver.sbatch")

printf 'DRIVER_JOB=%s\n' "$DRIVER_JOB"
printf 'WORM_ROOT=%s\n' "$WORM_ROOT"
printf 'CODE_ROOT=%s\n' "$CODE_ROOT"
printf 'WATCH_COMMAND=bash %s/watch_pipeline.sh %s\n' "$CODE_ROOT" "$DRIVER_JOB"
