#!/bin/bash
# Purpose: Slurm wrapper for the Intronsaurus vNext3Y matched RNA/protein Gene Stories build.
# Original source clue: ChatGPT JM105/Intronsaurus conversation on 2026-06-23; recovered bundle `Intronsaurus_MatchedRNAProteinGeneStories_vNext3Y_code_bundle`, original filename `141_intronsaurus_matched_rna_protein_gene_stories_v3Y.sbatch`.
# Expected inputs: Python builder under `$PROJECT/code/intronsaurus_vnext3Y_single_entry_gene_stories/`, precise v3M archive, and Sun MOESM3 workbook on Euler.
# Expected outputs: Slurm logs plus `121_INTRONSAURUS_GENE_STORIES_SINGLE_ENTRY_V3Y` output folder and archive.
# Known assumptions: Runs on ETH Euler with `/cluster/scratch/jmccarthy/JM105_RNAseq` as project root.
# Data status: Workflow wrapper only; invokes real-data build and does not generate fake biological data.
#SBATCH --job-name=RNAProtV3Y
#SBATCH --output=/cluster/scratch/jmccarthy/JM105_RNAseq/logs/Intronsaurus_vNext3Y_%j.out
#SBATCH --error=/cluster/scratch/jmccarthy/JM105_RNAseq/logs/Intronsaurus_vNext3Y_%j.err
#SBATCH --time=00:30:00
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=12000M

set -euo pipefail

PROJECT="/cluster/scratch/jmccarthy/JM105_RNAseq"
RUN_NAME="121_INTRONSAURUS_GENE_STORIES_SINGLE_ENTRY_V3Y"
SCRIPT="${PROJECT}/code/intronsaurus_vnext3Y_single_entry_gene_stories/141_intronsaurus_matched_rna_protein_gene_stories_v3Y.py"
SOURCE_ARCHIVE="${PROJECT}/input/intronsaurus_vnext3Y_single_entry_gene_stories/110_INTRONSAURUS_GENE_STORIES_PRECISE_INTERPRETER_V3M.tar.gz"
SUN_XLSX="${PROJECT}/input/intronsaurus_vnext3Y_single_entry_gene_stories/11357_2021_412_MOESM3_ESM.xlsx"

mkdir -p "${PROJECT}/logs"

echo "START: $(date)"
echo "HOST: $(hostname)"
echo "PROJECT=${PROJECT}"
echo "RUN_NAME=${RUN_NAME}"
echo "SCRIPT=${SCRIPT}"
echo "SOURCE_ARCHIVE=${SOURCE_ARCHIVE}"
echo "SUN_XLSX=${SUN_XLSX}"

PROJECT="${PROJECT}" RUN_NAME="${RUN_NAME}" SOURCE_ARCHIVE="${SOURCE_ARCHIVE}" SUN_XLSX="${SUN_XLSX}" python3 "${SCRIPT}"

echo "END: $(date)"
echo "INTRONSAURUS_MATCHED_RNA_PROTEIN_GENE_STORIES_VNEXT3Y_SBATCH_DONE"
