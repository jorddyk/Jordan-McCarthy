#!/usr/bin/env bash
#SBATCH --job-name=JM105_sample
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=6G
#SBATCH --time=24:00:00
#SBATCH --tmp=250G
#SBATCH --output=/cluster/scratch/jmccarthy/JM105_HGPS_Metazoan_Conservation/logs/distributed/sample_%A_%a.out
#SBATCH --error=/cluster/scratch/jmccarthy/JM105_HGPS_Metazoan_Conservation/logs/distributed/sample_%A_%a.err

set -euo pipefail
module load eth_proxy

PROJECT_ROOT="${PROJECT_ROOT:-/cluster/scratch/jmccarthy/JM105_HGPS_Metazoan_Conservation}"
CODE_DIR="$PROJECT_ROOT/code"
WORK_ROOT="$PROJECT_ROOT/work"
ENV_PREFIX="$PROJECT_ROOT/software/micromamba-root/envs/jm105-hgps-conservation"
export PATH="$ENV_PREFIX/bin:$PATH"

mkdir -p "$PROJECT_ROOT/logs/distributed"
TASK_TMP="${TMPDIR:-/tmp}/JM105_HGPS_${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}"
mkdir -p "$TASK_TMP"

"$ENV_PREFIX/bin/python" "$CODE_DIR/scripts/jm105_metazoan_distributed.py" \
    process-sample \
    --root "$WORK_ROOT" \
    --task-index "$SLURM_ARRAY_TASK_ID" \
    --threads "$SLURM_CPUS_PER_TASK" \
    --tmpdir "$TASK_TMP"

echo "SAMPLE_COMPLETE array=$SLURM_ARRAY_JOB_ID task=$SLURM_ARRAY_TASK_ID job=$SLURM_JOB_ID"
