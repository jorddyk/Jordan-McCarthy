#!/usr/bin/env bash
# Purpose: Inspect the latest or specified JM105 HGPS/metazoan conservation Slurm job.
# Usage: bash check-hgps-metazoan-conservation-status.sh [JOBID]
# Data status: administrative helper only; reads Slurm accounting and text logs.

set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/cluster/scratch/jmccarthy/JM105_HGPS_Metazoan_Conservation}"
LOG_DIR="$PROJECT_ROOT/logs"
JOB_ID="${1:-}"

if [[ -z "$JOB_ID" ]]; then
    if [[ ! -s "$LOG_DIR/latest_jobid.txt" ]]; then
        echo "ERROR: No JOBID supplied and $LOG_DIR/latest_jobid.txt is missing or empty." >&2
        exit 1
    fi
    JOB_ID="$(tr -d '[:space:]' < "$LOG_DIR/latest_jobid.txt")"
fi

if [[ ! "$JOB_ID" =~ ^[0-9]+$ ]]; then
    echo "ERROR: Invalid Slurm JOBID: $JOB_ID" >&2
    exit 1
fi

OUT="$LOG_DIR/JM105_HGPS_CR_${JOB_ID}.out"
ERR="$LOG_DIR/JM105_HGPS_CR_${JOB_ID}.err"

echo "=== SLURM ACCOUNTING ==="
sacct -j "$JOB_ID" --format=JobID,JobName%24,State,ExitCode,Elapsed,MaxRSS,AllocCPUS,Reason -X

echo
echo "=== STDOUT: $OUT ==="
if [[ -f "$OUT" ]]; then
    tail -n 120 "$OUT"
else
    echo "NO DATA: stdout log does not exist yet."
fi

echo
echo "=== STDERR: $ERR ==="
if [[ -f "$ERR" ]]; then
    tail -n 120 "$ERR"
else
    echo "NO DATA: stderr log does not exist yet."
fi
