#!/usr/bin/env bash
#SBATCH --job-name=Intronsaurus_v3I
#SBATCH --output=/cluster/scratch/jmccarthy/JM105_RNAseq/logs/Intronsaurus_vNext3I_%j.out
#SBATCH --error=/cluster/scratch/jmccarthy/JM105_RNAseq/logs/Intronsaurus_vNext3I_%j.err
#SBATCH --time=04:00:00
#SBATCH --cpus-per-task=2
#SBATCH --mem-per-cpu=8G

# Human purpose: Build Intronsaurus vNext3I on Euler, restoring the original Explore-tab total/rRNA-depleted graphs while adding poly-A views.
# Original source clue: current JM105/Intronsaurus chat artifact `127_intronsaurus_explore_restored_DATA_fix_v3I.sbatch`.
# Expected inputs: v3I Python builder plus prior Intronsaurus patch-chain Python files under `${PROJECT}/scripts`, JM105 primary53 table, Barral Lab logo.
# Expected outputs: `${PROJECT}/106_INTRONSAURUS_EXPLORE_RESTORED_V3I/interactive/Intronsaurus_Explore_Restored_vNext3I.html` and archive/checksum.
# Known assumptions: project Python exists at `${PROJECT}/.venv_jm105_module_python/bin/python`; prior patch-chain scripts are already uploaded.
# Data status: uses real JM105/JM101-derived tables already present on Euler; does not generate fake biological data.

set -euo pipefail

PROJECT="/cluster/scratch/jmccarthy/JM105_RNAseq"
PYTHON="${PROJECT}/.venv_jm105_module_python/bin/python"
SCRIPT="${PROJECT}/scripts/127_intronsaurus_explore_restored_DATA_fix_v3I.py"
PREV3F_SCRIPT="${PROJECT}/scripts/124_intronsaurus_stories_polya_mud1_hover_v3F.py"
PREV3E_SCRIPT="${PROJECT}/scripts/123_intronsaurus_elegant_ui_v3E.py"
PREV3D_SCRIPT="${PROJECT}/scripts/122_intronsaurus_leakage_first_expression_v3D.py"
PREV3C_SCRIPT="${PROJECT}/scripts/121_intronsaurus_dynamic_burden_v3C.py"
PREV3B_SCRIPT="${PROJECT}/scripts/120_intronsaurus_reader_first_rna_fate_v3B.py"
PREV2_SCRIPT="${PROJECT}/scripts/118_intronsaurus_rna_fate_human_ui_v2.py"
PREVIOUS_SCRIPT="${PROJECT}/scripts/117_intronsaurus_aging_rna_fate_atlas.py"
BASE_SCRIPT="${PROJECT}/scripts/109_JM105_intronsaurus_major_upgrade_UI_POLISH2.py"
PRIMARY="${PROJECT}/06_intron_counts/combined/JM105_primary53_intron_EI_IE_EE_counts_LONG.csv"
LOGO="${PROJECT}/scripts/BarralLab_real_logo.png"
OUTDIR="${PROJECT}/106_INTRONSAURUS_EXPLORE_RESTORED_V3I"

mkdir -p "${PROJECT}/logs"

echo "============================================================"
echo "Intronsaurus vNext3I — restore Explore introns DATA access"
echo "============================================================"
echo "DATE=$(date '+%Y-%m-%d %H:%M:%S')"
echo "HOST=$(hostname)"
echo "PYTHON=${PYTHON}"
echo "SCRIPT=${SCRIPT}"
echo "OUTDIR=${OUTDIR}"
echo

"${PYTHON}" -m py_compile "${SCRIPT}"
echo "PYTHON_COMPILE=PASS"

"${PYTHON}" "${SCRIPT}" \
  --project "${PROJECT}" \
  --primary "${PRIMARY}" \
  --outdir "${OUTDIR}" \
  --prev3f-script "${PREV3F_SCRIPT}" \
  --prev3e-script "${PREV3E_SCRIPT}" \
  --prev3d-script "${PREV3D_SCRIPT}" \
  --prev3c-script "${PREV3C_SCRIPT}" \
  --prev3b-script "${PREV3B_SCRIPT}" \
  --prev2-script "${PREV2_SCRIPT}" \
  --previous-script "${PREVIOUS_SCRIPT}" \
  --base-script "${BASE_SCRIPT}" \
  --logo "${LOGO}"
