#!/usr/bin/env bash
# Purpose: Slurm wrapper for the JM105 transformation-protocol RNA-seq expression workflow.
# Original source clue: recovered from uploaded folder `/mnt/data/JM105_Transformation_Protocol_Pipeline/JM105_transformation_expression.sbatch`.
# Expected inputs: exported PROJECT_ROOT and FASTQ_ROOT; optional HOUSEKEEPING_GENE, default TFC1.
# Expected outputs: delegates to JM105_run_transformation_expression.sh and writes pipeline outputs under transformation_protocol_analysis.
# Known assumptions: Euler/Slurm environment; the shell runner is executable in $PROJECT_ROOT/transformation_protocol_analysis/scripts/.
# Data status: real JM105 transformation-protocol workflow; no toy/simulated biological data.
#SBATCH --job-name=JM105_transform_expr
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=4G
#SBATCH --time=12:00:00
#SBATCH --output=JM105_transform_expr_%j.out
#SBATCH --error=JM105_transform_expr_%j.err

set -euo pipefail

: "${PROJECT_ROOT:?PROJECT_ROOT must be exported by the submission command}"
: "${FASTQ_ROOT:?FASTQ_ROOT must be exported by the submission command}"
HOUSEKEEPING_GENE="${HOUSEKEEPING_GENE:-TFC1}"

ANALYSIS_DIR="$PROJECT_ROOT/transformation_protocol_analysis"
SCRIPT="$ANALYSIS_DIR/scripts/JM105_run_transformation_expression.sh"

if [[ ! -x "$SCRIPT" ]]; then
    echo "ERROR: Runner not found or not executable: $SCRIPT" >&2
    exit 1
fi

cd "$ANALYSIS_DIR"
bash "$SCRIPT" "$PROJECT_ROOT" "$FASTQ_ROOT" "$HOUSEKEEPING_GENE"
