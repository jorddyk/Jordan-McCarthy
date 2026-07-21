#!/usr/bin/env bash
#SBATCH --job-name=JM105_aggregate
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem-per-cpu=8G
#SBATCH --time=08:00:00
#SBATCH --output=/cluster/scratch/jmccarthy/JM105_HGPS_Metazoan_Conservation/logs/distributed/aggregate_%j.out
#SBATCH --error=/cluster/scratch/jmccarthy/JM105_HGPS_Metazoan_Conservation/logs/distributed/aggregate_%j.err

set -euo pipefail
module load eth_proxy

PROJECT_ROOT="${PROJECT_ROOT:-/cluster/scratch/jmccarthy/JM105_HGPS_Metazoan_Conservation}"
CODE_DIR="$PROJECT_ROOT/code"
WORK_ROOT="$PROJECT_ROOT/work"
ENV_PREFIX="$PROJECT_ROOT/software/micromamba-root/envs/jm105-hgps-conservation"
export PATH="$ENV_PREFIX/bin:$PATH"

mkdir -p "$PROJECT_ROOT/logs/distributed"

"$ENV_PREFIX/bin/python" "$CODE_DIR/scripts/jm105_metazoan_distributed.py" \
    aggregate \
    --root "$WORK_ROOT"

echo "AGGREGATION_COMPLETE job=$SLURM_JOB_ID report=$WORK_ROOT/results/GATE_REPORT.md"
