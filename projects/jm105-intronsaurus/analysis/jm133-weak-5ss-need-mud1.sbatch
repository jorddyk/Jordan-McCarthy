#!/bin/bash
# JM-133 — Do weak 5′ splice sites need Mud1?
#
# Human purpose:
#   Run the JM133 5′SS:U1 strength vs Mud1-dependence analysis on Euler.
#
# Original source clue / conversation context:
#   Canonicalized from the JM105 RNA-seq ChatGPT project after Jordan requested
#   experiment JM-133 and submitted a job named JM133_5SS_Mud1.
#
# Expected inputs:
#   /cluster/scratch/jmccarthy/JM105_RNAseq containing the total/rRNA-depleted
#   intron retention tables and intron feature/5′SS tables.
#
# Expected outputs:
#   /cluster/scratch/jmccarthy/JM105_RNAseq/outputs/jm133-weak-5ss-need-mud1/
#
# Known assumptions:
#   The Python environment contains pandas, numpy, scipy, matplotlib, and ideally
#   statsmodels and ViennaRNA. If ViennaRNA is absent, the Python script records
#   a fallback U1 base-pair score in the output statistics.
#
# Data status:
#   Uses real total/rRNA-depleted RNA-seq tables only. Does not generate fake data.

#SBATCH --job-name=JM133_5SS_Mud1
#SBATCH --partition=normal.4h
#SBATCH --time=04:00:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --output=/cluster/scratch/jmccarthy/JM105_RNAseq/logs/JM133_5SS_Mud1_%j.out
#SBATCH --error=/cluster/scratch/jmccarthy/JM105_RNAseq/logs/JM133_5SS_Mud1_%j.err

set -euo pipefail

PROJECT_ROOT="/cluster/scratch/jmccarthy/JM105_RNAseq"
PYTHON="${PROJECT_ROOT}/.venv_jm105_module_python/bin/python"
SCRIPT="${PROJECT_ROOT}/scripts/jm133-weak-5ss-need-mud1.py"
OUT="${PROJECT_ROOT}/outputs/jm133-weak-5ss-need-mud1"

cd "${PROJECT_ROOT}"
mkdir -p logs outputs scripts

if [[ ! -x "${PYTHON}" ]]; then
  echo "Expected Python environment not executable: ${PYTHON}" >&2
  exit 2
fi

if [[ ! -f "${SCRIPT}" ]]; then
  echo "Expected analysis script not found on Euler: ${SCRIPT}" >&2
  echo "Copy projects/jm105-intronsaurus/analysis/jm133-weak-5ss-need-mud1.py to ${SCRIPT} before submitting." >&2
  exit 3
fi

"${PYTHON}" "${SCRIPT}" --project "${PROJECT_ROOT}" --out "${OUT}"
