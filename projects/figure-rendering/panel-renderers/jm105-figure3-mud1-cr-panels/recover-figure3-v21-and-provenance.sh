#!/usr/bin/env bash
set -euo pipefail

ROOT="/cluster/scratch/jmccarthy/JM105_RNAseq"
HISTORICAL_V21="${ROOT}/Figure3_render_v21_20260702_161316"
STAMP="$(date +%Y%m%d_%H%M%S)"
OUT="${ROOT}/Figure3_source_recovery_${STAMP}"
mkdir -p "${OUT}/source" "${OUT}/legacy_run" "${OUT}/audits"

find_exact() {
    local name="$1"
    local candidate
    candidate="$(find "${HISTORICAL_V21}" "${ROOT}" /cluster/home/jmccarthy -type f -name "${name}" 2>/dev/null | head -n 1 || true)"
    [[ -n "${candidate}" ]] || { echo "ERROR: could not locate ${name}" >&2; exit 10; }
    printf '%s\n' "${candidate}"
}

V21_SCRIPT="$(find_exact Figure_3_render_all_v21.py)"
V21_BASE="$(find_exact figure3_base_renderer.py)"
cp "${V21_SCRIPT}" "${OUT}/source/Figure_3_render_all_v21.py"
cp "${V21_BASE}" "${OUT}/source/figure3_base_renderer.py"

SUCCESS_SUMMARY="$(find "${ROOT}" -type f -name Figure_3_RUN_SUMMARY.txt -printf '%T@ %p\n' 2>/dev/null | sort -nr | awk '{print $2}' | while read -r summary; do
    if grep -q '^ALL_PANELS_RENDERED=True$' "${summary}" && grep -q '^TEXT_OVERLAPS_TOTAL=0$' "${summary}" && grep -q '^TEXT_CLIPPED_TOTAL=0$' "${summary}" && grep -q '^ASPECT_RATIO_PASS=True$' "${summary}"; then
        printf '%s\n' "${summary}"
        break
    fi
done)"
[[ -n "${SUCCESS_SUMMARY}" ]] || { echo "ERROR: no successful v21 output directory found" >&2; exit 11; }
SUCCESS_DIR="$(dirname "${SUCCESS_SUMMARY}")"

for pattern in 'Figure_3_RUN_SUMMARY.txt' 'Figure_3_INPUT_MANIFEST.tsv' 'Figure_3_PANEL_CONTRACTS.tsv' 'Figure_3_PROVENANCE.json' 'Figure_3_DATA_INTEGRITY_AUDIT.tsv' 'Figure_3_ASPECT_RATIO_VERIFICATION.tsv' 'Figure_3_output_file_manifest.tsv' 'Figure_3*_plot_source.tsv' 'Figure_3*_statistics_audit.tsv' 'Figure_3*_layout_decisions.tsv'; do
    find "${SUCCESS_DIR}" -maxdepth 1 -type f -name "${pattern}" -exec cp {} "${OUT}/legacy_run/" \;
done

CANDIDATE_FILE="${ROOT}/Figure2_stage1_audit_20260630_145204/Figure2_stage1B_STRICT_NUCLEAR_ORF_GATE/Figure_2_STRICT_candidate_gate_passed.tsv"
STATS_FILE="${ROOT}/162_FIG1EF_EXACT_RAW_FILES/JM105_replicate_stats_by_intron_condition.csv"
COUNTS_FILE="${ROOT}/162_FIG1EF_EXACT_RAW_FILES/JM105_primary53_intron_EI_IE_EE_counts_LONG.csv"
SAMPLE_AUDIT="${ROOT}/162_FIG1EF_EXACT_RAW_FILES/JM105_rebuilt_annotation_sample_audit_FIXED.tsv"
for source in "${CANDIDATE_FILE}" "${STATS_FILE}" "${COUNTS_FILE}" "${SAMPLE_AUDIT}"; do
    [[ -f "${source}" ]] || { echo "ERROR: required provenance source missing: ${source}" >&2; exit 12; }
done

module load stack/2024-06 python/3.12.8
python - "${OUT}" "${CANDIDATE_FILE}" "${STATS_FILE}" "${COUNTS_FILE}" "${SAMPLE_AUDIT}" <<'PY'
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path
import pandas as pd

out = Path(sys.argv[1])
records = []
for path in [Path(value) for value in sys.argv[2:]]:
    sep = "\t" if path.suffix.lower() == ".tsv" else ","
    frame = pd.read_csv(path, sep=sep, low_memory=False)
    record = {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "rows": int(len(frame)), "columns": list(map(str, frame.columns))}
    for name in ["sample_id", "sample", "replicate", "age", "glucose", "condition", "genotype", "strain", "nmd", "nmd_state", "capture", "rna_source", "intron_id", "gene_id"]:
        if name in frame.columns:
            record[f"unique_{name}"] = frame[name].dropna().astype(str).unique().tolist()[:200]
    records.append(record)
(out / "audits" / "raw_source_schema_and_hashes.json").write_text(json.dumps(records, indent=2), encoding="utf-8")
PY

{
    printf 'role\tsource_path\tsha256\n'
    printf 'v21_orchestrator\t%s\t%s\n' "${V21_SCRIPT}" "$(sha256sum "${V21_SCRIPT}" | awk '{print $1}')"
    printf 'v21_base\t%s\t%s\n' "${V21_BASE}" "$(sha256sum "${V21_BASE}" | awk '{print $1}')"
    printf 'successful_v21_output\t%s\tNA\n' "${SUCCESS_DIR}"
    printf 'candidate_table\t%s\t%s\n' "${CANDIDATE_FILE}" "$(sha256sum "${CANDIDATE_FILE}" | awk '{print $1}')"
    printf 'condition_stats\t%s\t%s\n' "${STATS_FILE}" "$(sha256sum "${STATS_FILE}" | awk '{print $1}')"
    printf 'raw_ei_ie_ee_counts\t%s\t%s\n' "${COUNTS_FILE}" "$(sha256sum "${COUNTS_FILE}" | awk '{print $1}')"
    printf 'sample_audit\t%s\t%s\n' "${SAMPLE_AUDIT}" "$(sha256sum "${SAMPLE_AUDIT}" | awk '{print $1}')"
} > "${OUT}/RECOVERY_MANIFEST.tsv"

python -m py_compile "${OUT}/source/Figure_3_render_all_v21.py" "${OUT}/source/figure3_base_renderer.py"
tar -C "$(dirname "${OUT}")" -czf "${OUT}.tar.gz" "$(basename "${OUT}")"
echo "FIGURE3_SOURCE_RECOVERY=PASS"
echo "RECOVERY_DIR=${OUT}"
echo "RECOVERY_ARCHIVE=${OUT}.tar.gz"
