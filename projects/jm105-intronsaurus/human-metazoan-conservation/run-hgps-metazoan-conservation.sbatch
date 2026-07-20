#!/usr/bin/env bash
# Purpose: One-job Euler launcher for the JM105 HGPS + metazoan CR conservation analysis.
# Expected inputs: public GEO/SRA access; code bundle uploaded by the companion PowerShell helper.
# Expected outputs: panel-ready metadata, QC, PEI, per-intron contrast tables, and GATE_REPORT.md.
# Known assumptions: Euler Slurm, outbound HTTPS, x86_64 Linux, and at least 1.5 TB scratch quota.
# Data status: public real RNA-seq only; no simulated biological data.
#
# Figure 2 scope fence: this job does not touch JM105 Figure 2 data.
# Tight bounding-box export is not used because this analysis-only job renders no figures.
#SBATCH --job-name=JM105_HGPS_CR
#SBATCH --cpus-per-task=24
#SBATCH --mem-per-cpu=7G
#SBATCH --time=120:00:00
#SBATCH --output=/cluster/scratch/jmccarthy/JM105_HGPS_Metazoan_Conservation/logs/JM105_HGPS_CR_%j.out
#SBATCH --error=/cluster/scratch/jmccarthy/JM105_HGPS_Metazoan_Conservation/logs/JM105_HGPS_CR_%j.err

set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/cluster/scratch/jmccarthy/JM105_HGPS_Metazoan_Conservation}"
CODE_DIR="$PROJECT_ROOT/code"
WORK_ROOT="$PROJECT_ROOT/work"
LOG_DIR="$PROJECT_ROOT/logs"
ENV_ROOT="$PROJECT_ROOT/software"
MAMBA_ROOT_PREFIX="$ENV_ROOT/micromamba-root"
MICROMAMBA="$ENV_ROOT/bin/micromamba"
MICROMAMBA_VERSION="2.6.2-1"
MICROMAMBA_URL="https://github.com/mamba-org/micromamba-releases/releases/download/${MICROMAMBA_VERSION}/micromamba-linux-64"
ENV_NAME="jm105-hgps-conservation"

mkdir -p "$CODE_DIR" "$WORK_ROOT" "$LOG_DIR" "$ENV_ROOT/bin" "$MAMBA_ROOT_PREFIX"

install_micromamba() {
    local tmp_dir
    local tmp_binary
    local attempt
    local byte_count

    echo "Installing pinned micromamba ${MICROMAMBA_VERSION} under $ENV_ROOT"
    tmp_dir="$(mktemp -d)"
    tmp_binary="$tmp_dir/micromamba"

    for attempt in 1 2 3 4 5 6; do
        echo "Micromamba download attempt ${attempt}/6"
        rm -f "$tmp_binary"
        if curl \
            --fail \
            --location \
            --connect-timeout 30 \
            --max-time 900 \
            --output "$tmp_binary" \
            "$MICROMAMBA_URL"; then
            byte_count="$(stat -c '%s' "$tmp_binary")"
            if [[ "$byte_count" -ge 1000000 ]]; then
                chmod 0755 "$tmp_binary"
                if "$tmp_binary" --version; then
                    install -m 0755 "$tmp_binary" "$MICROMAMBA"
                    "$MICROMAMBA" --version
                    rm -rf "$tmp_dir"
                    return 0
                fi
            fi
        fi
        echo "Micromamba attempt ${attempt} failed or produced an invalid binary." >&2
        sleep $((attempt * 10))
    done

    rm -rf "$tmp_dir"
    echo "ERROR: Could not install a valid micromamba binary after 6 attempts." >&2
    return 1
}

if [[ ! -x "$MICROMAMBA" ]] || ! "$MICROMAMBA" --version >/dev/null 2>&1; then
    rm -f "$MICROMAMBA"
    install_micromamba
fi

export MAMBA_ROOT_PREFIX
if ! "$MICROMAMBA" env list | awk '{print $1}' | grep -qx "$ENV_NAME"; then
    "$MICROMAMBA" create -y -n "$ENV_NAME" \
        -c conda-forge -c bioconda \
        python=3.11 \
        star=2.7.11b \
        samtools=1.21 \
        sra-tools=3.2.1 \
        pandas=2.2 \
        numpy=2.1 \
        scipy=1.15 \
        pysam=0.23 \
        pyarrow=19 \
        tabulate=0.9
fi

echo "Starting full public-data analysis"
"$MICROMAMBA" run -n "$ENV_NAME" \
    python "$CODE_DIR/scripts/run_hgps_metazoan_conservation.py" \
    --root "$WORK_ROOT" \
    --threads "${SLURM_CPUS_PER_TASK:-24}"

echo "Finished: $WORK_ROOT/results/GATE_REPORT.md"
