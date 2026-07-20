#!/usr/bin/env bash
#SBATCH --job-name=JM105_Fig3_ADG_v22
#SBATCH --time=00:45:00
#SBATCH --cpus-per-task=2
#SBATCH --mem-per-cpu=4G
#SBATCH --output=JM105_Fig3_ADG_v22.%j.out
#SBATCH --error=JM105_Fig3_ADG_v22.%j.err

set -euo pipefail

BUNDLE_DIR="${SLURM_SUBMIT_DIR:?SLURM_SUBMIT_DIR is not set}"
cd "${BUNDLE_DIR}"

module load stack/2024-06
module load python/3.12.8

JM105_ROOT="/cluster/scratch/jmccarthy/JM105_RNAseq/162_FIG1EF_EXACT_RAW_FILES"
CANDIDATE_FILE="/cluster/scratch/jmccarthy/JM105_RNAseq/Figure2_stage1_audit_20260630_145204/Figure2_stage1B_STRICT_NUCLEAR_ORF_GATE/Figure_2_STRICT_candidate_gate_passed.tsv"
STATS_FILE="${JM105_ROOT}/JM105_replicate_stats_by_intron_condition.csv"
STAMP="$(date +%Y%m%d_%H%M%S)"
OUTPUT_DIR="/cluster/scratch/jmccarthy/JM105_RNAseq/Figure3_ADG_v22_${STAMP}"

for required in \
    render_figure3_ADG_v22.py \
    figure3_adg_v22_common.py \
    figure3_adg_v22_manifest.py \
    figure3_adg_v22_panel_a.py \
    figure3_adg_v22_panel_d.py \
    figure3_adg_v22_panel_g.py \
    Figure_3_render_all_v21.py \
    figure3_base_renderer.py \
    JM100.xlsx
do
    test -f "${BUNDLE_DIR}/${required}" || {
        echo "ERROR: missing ${BUNDLE_DIR}/${required}" >&2
        exit 20
    }
done

test -f "${CANDIDATE_FILE}"
test -f "${STATS_FILE}"

python "${BUNDLE_DIR}/render_figure3_ADG_v22.py" \
    --jm100-xlsx "${BUNDLE_DIR}/JM100.xlsx" \
    --jm105-root "${JM105_ROOT}" \
    --candidate-file "${CANDIDATE_FILE}" \
    --stats-file "${STATS_FILE}" \
    --output-dir "${OUTPUT_DIR}"

python - "${OUTPUT_DIR}" <<'VALIDATE_PY'
from pathlib import Path
import json
import sys

root = Path(sys.argv[1])
provenance = json.loads(
    (root / "Figure_3_ADG_provenance.json").read_text(encoding="utf-8")
)

for panel, stem in [
    ("A", "Figure_3A_lifespan"),
    ("D", "Figure_3D_candidate_responses"),
    ("G", "Figure_3G_host_abundance"),
]:
    for suffix in [
        "transparent.svg",
        "transparent.pdf",
        "transparent.png",
        "preview_white.png",
    ]:
        path = root / "panels" / panel / f"{stem}.{suffix}"
        if not path.is_file() or path.stat().st_size <= 0:
            raise SystemExit(f"ERROR: missing or empty output: {path}")

    if provenance["text_audits"][panel]["passed"] is not True:
        raise SystemExit(f"ERROR: text audit failed for Panel {panel}")

if provenance["panel_G_range_audit"]["points_clipped_in_v22"] != 0:
    raise SystemExit("ERROR: Panel G still clips points")

print("OUTPUT_VALIDATION=PASS")
VALIDATE_PY

echo "FIGURE3_ADG_V22_RENDER=PASS"
echo "OUTPUT_DIR=${OUTPUT_DIR}"
