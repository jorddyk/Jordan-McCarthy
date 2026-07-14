#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT_DIR="${1:-${SCRIPT_DIR}/out}"

if ! command -v module >/dev/null 2>&1; then
    source /etc/profile >/dev/null 2>&1 || true
fi

module load fast_python_workshop_cpu/2025.0.0
if command -v venv_cpu_init >/dev/null 2>&1; then
    venv_cpu_init >/dev/null 2>&1
fi

export MPLBACKEND=Agg
export PYTHONUNBUFFERED=1

RENDERER="${SCRIPT_DIR}/render_JM105_Figure2_v4_1_no_overlap.py"
PANEL_A="${SCRIPT_DIR}/inputs/Panel2A_JM104_RLS_source_CLEAN_v3_1.tsv"
STRICT="${SCRIPT_DIR}/inputs/Figure_2A_Age_CR_candidate_map_LABEL_COLUMN_FINAL.plot_source.tsv"
PANEL_E_SVG="${SCRIPT_DIR}/inputs/Figure2E_existing.svg"

for required in "${RENDERER}" "${PANEL_A}" "${STRICT}" "${PANEL_E_SVG}"; do
    if [[ ! -s "${required}" ]]; then
        echo "MISSING OR EMPTY: ${required}" >&2
        exit 20
    fi
done

python3 -m py_compile "${RENDERER}"
rm -rf "${OUT_DIR}"
mkdir -p "${OUT_DIR}"

python3 "${RENDERER}" \
    --panel-a-tsv "${PANEL_A}" \
    --strict-table "${STRICT}" \
    --panel-e-svg-source "${PANEL_E_SVG}" \
    --out "${OUT_DIR}" \
    2>&1 | tee "${OUT_DIR}/render.log"

CONTACT="${OUT_DIR}/Figure_2_v4_1_full_composite.preview_white.png"
AUDIT="${OUT_DIR}/Figure_2_v4_1_hard_collision_audit.txt"

if [[ ! -s "${CONTACT}" ]]; then
    echo "CONTACT SHEET MISSING: ${CONTACT}" >&2
    exit 30
fi
if [[ ! -s "${AUDIT}" ]]; then
    echo "AUDIT MISSING: ${AUDIT}" >&2
    exit 31
fi

for panel in A B C D E F; do
    panel_dir="${OUT_DIR}/panels/${panel}"
    for suffix in transparent.svg transparent.pdf transparent.png preview_white.png; do
        count="$(find "${panel_dir}" -maxdepth 1 -type f -name "*.${suffix}" | wc -l)"
        if [[ "${count}" -lt 1 ]]; then
            echo "PANEL ${panel} MISSING ${suffix}" >&2
            exit 40
        fi
    done
done

echo "FIGURE2_V4_1_EULER_RENDER_COMPLETE"
echo "OUT=${OUT_DIR}"
echo "CONTACT=${CONTACT}"
cat "${AUDIT}"
