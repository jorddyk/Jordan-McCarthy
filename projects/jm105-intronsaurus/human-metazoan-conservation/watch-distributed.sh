#!/usr/bin/env bash
set -uo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/cluster/scratch/jmccarthy/JM105_HGPS_Metazoan_Conservation}"
STATE_FILE="$PROJECT_ROOT/submission/latest.env"
WORK_ROOT="$PROJECT_ROOT/work"

if [[ ! -f "$STATE_FILE" ]]; then
    echo "Submission record not found: $STATE_FILE" >&2
    exit 1
fi
# shellcheck disable=SC1090
source "$STATE_FILE"

ALL_IDS="${HUMAN_REFERENCE_JOB},${MOUSE_REFERENCE_JOB},${SAMPLE_ARRAY_JOB},${AGGREGATE_JOB}"
while true; do
    clear
    echo "JM105 HGPS/metazoan distributed analysis"
    echo "Updated: $(date)"
    echo
    echo "Human reference: $HUMAN_REFERENCE_JOB"
    echo "Mouse reference: $MOUSE_REFERENCE_JOB"
    echo "Sample array:    $SAMPLE_ARRAY_JOB"
    echo "Aggregate:       $AGGREGATE_JOB"
    echo
    echo "=== ACTIVE JOBS ==="
    squeue -j "$ALL_IDS" 2>/dev/null || true
    echo
    COMPLETE_COUNT="$(find "$WORK_ROOT/status/sample_complete" -maxdepth 1 -name '*.json' -type f 2>/dev/null | wc -l)"
    echo "=== SAMPLE OUTPUTS: ${COMPLETE_COUNT}/${RUN_COUNT} COMPLETE ==="
    echo
    AGG_STATE="$(sacct -j "$AGGREGATE_JOB" -X -n -P --format=State 2>/dev/null | awk -F'|' 'NF && $1 != "" {print $1; exit}')"
    [[ -n "$AGG_STATE" ]] || AGG_STATE="PENDING/UNKNOWN"
    echo "=== AGGREGATE STATUS: $AGG_STATE ==="

    if [[ "$AGG_STATE" == COMPLETED* ]]; then
        echo
        echo "=== FINAL GATE REPORT ==="
        cat "$WORK_ROOT/results/GATE_REPORT.md" 2>/dev/null || true
        break
    fi
    case "$AGG_STATE" in
        FAILED*|CANCELLED*|TIMEOUT*|OUT_OF_MEMORY*|NODE_FAIL*|PREEMPTED*)
            echo
            echo "Aggregate terminated: $AGG_STATE"
            tail -n 100 "$PROJECT_ROOT/logs/distributed/aggregate_${AGGREGATE_JOB}.err" 2>/dev/null || true
            break
            ;;
    esac

    echo
    echo "Refreshing in 5 seconds. Ctrl+C stops only this watcher."
    sleep 5
done
