#!/usr/bin/env bash
# Human purpose: Check the Euler status/logs for the Intronsaurus vNext3I Explore-tab restoration build.
# Original source clue: current JM105/Intronsaurus chat artifact `check_intronsaurus_explore_restored_DATA_fix_v3I_status.sh`.
# Expected inputs: `/cluster/scratch/jmccarthy/JM105_RNAseq/logs/intronsaurus_vnext3I_latest_jobid.txt` on Euler.
# Expected outputs: Slurm queue/accounting lines plus stdout/stderr tail for the build job.
# Known assumptions: run from an Euler login shell with Slurm available.
# Data status: administrative/status helper only; no biological data are generated or modified.

set -euo pipefail
PROJECT="/cluster/scratch/jmccarthy/JM105_RNAseq"
JOBID="$(tr -d '[:space:]' < "${PROJECT}/logs/intronsaurus_vnext3I_latest_jobid.txt")"
echo "JOBID=${JOBID}"
squeue -j "${JOBID}" || true
echo
sacct -X -j "${JOBID}" --format=JobID,JobName%34,State,ExitCode,Elapsed,MaxRSS,ReqMem,Start,End,NodeList%25 --parsable2 || true
echo
OUT="${PROJECT}/logs/Intronsaurus_vNext3I_${JOBID}.out"
ERR="${PROJECT}/logs/Intronsaurus_vNext3I_${JOBID}.err"
if [[ -f "${OUT}" ]]; then
  echo "=== STDOUT ==="
  tail -n 260 "${OUT}"
else
  echo "[stdout not created yet]"
fi
echo
if [[ -s "${ERR}" ]]; then
  echo "=== STDERR ==="
  tail -n 260 "${ERR}"
else
  echo "[stderr empty or not created yet]"
fi
