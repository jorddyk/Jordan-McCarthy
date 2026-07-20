#!/usr/bin/env bash
#SBATCH --job-name=jm105_ce_step01
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=4G
#SBATCH --time=02:00:00
#SBATCH --output=jm105_ce_step01_%j.out
#SBATCH --error=jm105_ce_step01_%j.err

set -euo pipefail

# Step 1 is metadata-only. It downloads no FASTQ, BAM, or biological count data.
# It is intentionally submitted through Slurm so the workflow is reproducible
# and does not depend on a long interactive Euler login session.

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
CANDIDATE_TABLE="${SCRIPT_DIR}/candidate_datasets.tsv"
AUDIT_SCRIPT="${SCRIPT_DIR}/step01_audit_public_datasets.py"

: "${JM105_CELEGANS_ROOT:?JM105_CELEGANS_ROOT must point to the Euler result root.}"

if [[ ! -f "${CANDIDATE_TABLE}" ]]; then
    echo "ERROR: candidate dataset table not found: ${CANDIDATE_TABLE}" >&2
    exit 10
fi
if [[ ! -f "${AUDIT_SCRIPT}" ]]; then
    echo "ERROR: metadata audit script not found: ${AUDIT_SCRIPT}" >&2
    exit 11
fi
if ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: python3 is not available on PATH." >&2
    exit 12
fi
if ! command -v sha256sum >/dev/null 2>&1; then
    echo "ERROR: sha256sum is not available on PATH." >&2
    exit 13
fi

RUN_TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
JOB_TOKEN="${SLURM_JOB_ID:-manual}"
RUN_DIR="${JM105_CELEGANS_ROOT}/step01_metadata_audit_${RUN_TIMESTAMP}_${JOB_TOKEN}"
OUTPUT_DIR="${RUN_DIR}/outputs"
LOG_DIR="${RUN_DIR}/logs"
PROVENANCE_DIR="${RUN_DIR}/provenance"

mkdir -p "${OUTPUT_DIR}" "${LOG_DIR}" "${PROVENANCE_DIR}"

cp -- "${CANDIDATE_TABLE}" "${PROVENANCE_DIR}/candidate_datasets.tsv"
cp -- "${AUDIT_SCRIPT}" "${PROVENANCE_DIR}/step01_audit_public_datasets.py"
cp -- "${BASH_SOURCE[0]}" "${PROVENANCE_DIR}/run_step01_metadata_audit.sbatch"

{
    echo -e "key\tvalue"
    echo -e "run_timestamp_utc\t${RUN_TIMESTAMP}"
    echo -e "slurm_job_id\t${SLURM_JOB_ID:-NA}"
    echo -e "slurm_job_name\t${SLURM_JOB_NAME:-NA}"
    echo -e "hostname\t$(hostname -f 2>/dev/null || hostname)"
    echo -e "working_directory\t$(pwd)"
    echo -e "script_directory\t${SCRIPT_DIR}"
    echo -e "results_root\t${JM105_CELEGANS_ROOT}"
    echo -e "python3\t$(command -v python3)"
    echo -e "python_version\t$(python3 --version 2>&1)"
    echo -e "ncbi_email_supplied\t$([[ -n "${NCBI_EMAIL:-}" ]] && echo yes || echo no)"
    echo -e "ncbi_api_key_supplied\t$([[ -n "${NCBI_API_KEY:-}" ]] && echo yes || echo no)"
} > "${PROVENANCE_DIR}/software_and_run_manifest.tsv"

python3 "${AUDIT_SCRIPT}" \
    --datasets "${CANDIDATE_TABLE}" \
    --output-dir "${OUTPUT_DIR}" \
    --email "${NCBI_EMAIL:-}" \
    --api-key "${NCBI_API_KEY:-}" \
    --timeout 90 \
    --retries 5 \
    > "${LOG_DIR}/step01_python.stdout.log" \
    2> "${LOG_DIR}/step01_python.stderr.log"

find "${RUN_DIR}" -type f ! -name 'SHA256SUMS_ALL.txt' -print0 \
    | sort -z \
    | xargs -0 sha256sum \
    > "${PROVENANCE_DIR}/SHA256SUMS_ALL.txt"

printf 'SUCCESS\n' > "${RUN_DIR}/STEP01_COMPLETE.txt"

LATEST_LINK="${JM105_CELEGANS_ROOT}/step01_latest"
TEMP_LINK="${JM105_CELEGANS_ROOT}/.step01_latest_${JOB_TOKEN}"
ln -sfn "${RUN_DIR}" "${TEMP_LINK}"
mv -Tf "${TEMP_LINK}" "${LATEST_LINK}"

cat <<EOF
JM105 C. elegans Step 1 metadata audit complete.
Run directory: ${RUN_DIR}
Latest symlink: ${LATEST_LINK}
Dataset summary: ${OUTPUT_DIR}/dataset_summary.tsv
Contrast capability: ${OUTPUT_DIR}/contrast_capability.tsv
Audit report: ${OUTPUT_DIR}/AUDIT_REPORT.md
EOF
