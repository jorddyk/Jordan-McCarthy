#!/usr/bin/env bash

WORM_ROOT="${WORM_ROOT:-/cluster/scratch/jmccarthy/JM105_CELEGANS_WORM_ANALYSIS}"
DRIVER_JOB="${1:-}"
LEDGER="$WORM_ROOT/job_ledger.env"

while true; do
  clear 2>/dev/null || true
  printf 'JM105 C. elegans public RNA-seq analysis\n'
  printf 'Updated: %s\n\n' "$(date)"

  if [[ -f "$LEDGER" ]]; then
    # shellcheck disable=SC1090
    source "$LEDGER"
    printf 'Driver:    %s\n' "${DRIVER_JOB:-NA}"
    printf 'Reference: %s\n' "${REFERENCE_JOB:-NA}"
    printf 'Samples:   %s\n' "${SAMPLE_JOB:-NA}"
    printf 'Aggregate: %s\n' "${AGGREGATE_JOB:-NA}"
    printf 'Tasks:     %s\n\n' "${N_TASKS:-NA}"
    JOBS="${DRIVER_JOB:-},${REFERENCE_JOB:-},${SAMPLE_JOB:-},${AGGREGATE_JOB:-}"
  else
    printf 'Driver: %s\n' "${DRIVER_JOB:-not supplied}"
    printf 'Waiting for driver to create %s\n\n' "$LEDGER"
    JOBS="$DRIVER_JOB"
  fi

  printf '=== ACTIVE JOBS ===\n'
  if [[ -n "${JOBS//,/}" ]]; then
    squeue -j "$JOBS" -o '%.20i %.10P %.18j %.9u %.2t %.10M %.6D %R' 2>/dev/null || true
  fi

  printf '\n=== MANIFEST GATE ===\n'
  if [[ -f "$WORM_ROOT/work/metadata/MANIFEST_GATE.md" ]]; then
    sed -n '1,80p' "$WORM_ROOT/work/metadata/MANIFEST_GATE.md"
  else
    printf 'PENDING\n'
  fi

  COMPLETE=$(find "$WORM_ROOT/work/complete_markers" -maxdepth 1 -name '*.complete.json' 2>/dev/null | wc -l | tr -d ' ')
  EXPECTED="NA"
  if [[ -f "$LEDGER" ]]; then EXPECTED="${N_TASKS:-NA}"; fi
  printf '\n=== SAMPLE OUTPUTS: %s/%s COMPLETE ===\n' "$COMPLETE" "$EXPECTED"

  printf '\n=== AGGREGATE STATUS ===\n'
  if [[ -f "$WORM_ROOT/work/results/AGGREGATION_COMPLETE.json" ]]; then
    printf 'COMPLETED\n'
  elif [[ -f "$LEDGER" ]]; then
    printf 'PENDING OR RUNNING\n'
  else
    printf 'WAITING FOR DRIVER\n'
  fi

  if [[ -f "$WORM_ROOT/work/results/FINAL_REPORT.md" ]]; then
    printf '\n=== FINAL REPORT ===\n'
    sed -n '1,120p' "$WORM_ROOT/work/results/FINAL_REPORT.md"
  fi

  printf '\nRefreshing in 10 seconds. Ctrl+C stops only this watcher.\n'
  sleep 10
done
