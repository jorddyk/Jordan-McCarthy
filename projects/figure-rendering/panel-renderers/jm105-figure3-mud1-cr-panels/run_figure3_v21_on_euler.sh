#!/usr/bin/env bash
# Legacy code backfill: Euler runner for JM105 Figure 3 Mud1/caloric-restriction panel renderer.
# Human purpose: copy the recovered v21 renderer into a timestamped Euler run directory, precheck real JM105 inputs, and submit the Slurm job.
# Original source clue/conversation context: recovered from ChatGPT JM105 Figure 3 rendering session; final successful Euler run was /cluster/scratch/jmccarthy/JM105_RNAseq/Figure3_render_v21_20260702_161316.
# Expected inputs: local renderer files in this directory, JM105 Figure 2 candidate TSV, and JM105 replicate stats CSV on /cluster/scratch.
# Expected outputs: Figure3_render_v21_* directory containing transparent SVG/PDF/PNG, white previews, audits, and provenance JSON.
# Known assumptions: EULER module stack/2024-06 and python/3.12.8 are available; no raw sequencing data are copied or committed.
# Data status: real JM105 RNA-seq summary inputs; no mockup or simulated biological data.
set -euo pipefail

ROOT="/cluster/scratch/jmccarthy/JM105_RNAseq"
SELF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STAMP="$(date +%Y%m%d_%H%M%S)"
RUN_DIR="${ROOT}/Figure3_render_v21_${STAMP}"
SCRIPT="${RUN_DIR}/Figure_3_render_all_v21.py"
BASEMOD="${RUN_DIR}/figure3_base_renderer.py"
CANDIDATE_FILE="${ROOT}/Figure2_stage1_audit_20260630_145204/Figure2_stage1B_STRICT_NUCLEAR_ORF_GATE/Figure_2_STRICT_candidate_gate_passed.tsv"
STATS_FILE="${ROOT}/101_INTRONSAURUS_LEAKAGE_FIRST_EXPRESSION_FIXED/tables/JM105_replicate_stats_by_intron_condition.csv"

mkdir -p "${RUN_DIR}"
cp "${SELF_DIR}/Figure_3_render_all_v21.py" "${SCRIPT}"
cp "${SELF_DIR}/figure3_base_renderer.py" "${BASEMOD}"

set +u
module load stack/2024-06 python/3.12.8
set -u

if command -v python >/dev/null 2>&1; then
    PYBIN="$(command -v python)"
elif command -v python3 >/dev/null 2>&1; then
    PYBIN="$(command -v python3)"
else
    echo "ERROR: python not found after module load" >&2
    exit 1
fi

"${PYBIN}" -m py_compile "${SCRIPT}" "${BASEMOD}"

"${PYBIN}" - <<PY
import pandas as pd
c = pd.read_csv("${CANDIDATE_FILE}", sep='\t')
s = pd.read_csv("${STATS_FILE}")
print('PRECHECK candidate rows:', len(c))
print('PRECHECK stats rows:', len(s))
print('PRECHECK metrics:', sorted(s['metric'].astype(str).unique()))
need = {'IR','host_cpm'}
missing = sorted(need - set(s['metric'].astype(str)))
if missing:
    raise SystemExit('ERROR: missing metrics ' + ','.join(missing))
overlap = s['intron_id'].astype(str).isin(set(c['intron_id'].astype(str))).sum()
print('PRECHECK overlap rows:', overlap)
if overlap == 0:
    raise SystemExit('ERROR: zero candidate/source overlap')
PY

cat > "${RUN_DIR}/Figure_3_render_v21.slurm" <<EOF
#!/usr/bin/env bash
#SBATCH --job-name=Fig3_v21
#SBATCH --output=${RUN_DIR}/Figure_3_render_v21.%j.out
#SBATCH --error=${RUN_DIR}/Figure_3_render_v21.%j.err
#SBATCH --time=00:45:00
#SBATCH --mem-per-cpu=8G
#SBATCH --cpus-per-task=1

set -euo pipefail
set +u
module load stack/2024-06 python/3.12.8
set -u
if command -v python >/dev/null 2>&1; then
    PYBIN="\$(command -v python)"
else
    PYBIN="\$(command -v python3)"
fi
"\${PYBIN}" "${SCRIPT}" \
    --jm105-root "${ROOT}" \
    --output-dir "${RUN_DIR}" \
    --candidate-file "${CANDIDATE_FILE}" \
    --stats-file "${STATS_FILE}"
EOF

JOBID="$(sbatch "${RUN_DIR}/Figure_3_render_v21.slurm" | awk '{print $4}')"
echo "RUN_DIR=${RUN_DIR}"
echo "JOBID=${JOBID}"
