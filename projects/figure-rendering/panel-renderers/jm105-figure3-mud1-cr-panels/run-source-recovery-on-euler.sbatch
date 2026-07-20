#!/usr/bin/env bash
#SBATCH --job-name=JM105_Fig3_recover
#SBATCH --time=00:20:00
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=4G
#SBATCH --output=JM105_Fig3_recover.%j.out
#SBATCH --error=JM105_Fig3_recover.%j.err

set -euo pipefail

BUNDLE_DIR="${SLURM_SUBMIT_DIR:?SLURM_SUBMIT_DIR is not set}"
cd "${BUNDLE_DIR}"

RECOVERY_SCRIPT="${BUNDLE_DIR}/recover-figure3-v21-and-provenance.sh"
[[ -f "${RECOVERY_SCRIPT}" ]] || {
    echo "ERROR: recovery script not found: ${RECOVERY_SCRIPT}" >&2
    exit 20
}

bash "${RECOVERY_SCRIPT}"
