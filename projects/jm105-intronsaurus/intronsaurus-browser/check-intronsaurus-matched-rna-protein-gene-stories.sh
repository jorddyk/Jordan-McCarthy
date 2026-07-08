#!/usr/bin/env bash
# Purpose: Safe Euler status checker for the Intronsaurus vNext3Y matched RNA/protein Gene Stories Slurm job.
# Original source clue: ChatGPT JM105/Intronsaurus conversation on 2026-06-23; recovered bundle `Intronsaurus_MatchedRNAProteinGeneStories_vNext3Y_code_bundle`, original filename `check_intronsaurus_matched_rna_protein_gene_stories_v3Y_status.sh`.
# Expected inputs: Latest-job-id file and Slurm stdout/stderr logs under `/cluster/scratch/jmccarthy/JM105_RNAseq/logs`.
# Expected outputs: Human-readable squeue/sacct status and tail of stdout/stderr with validation markers.
# Known assumptions: Uses timeout around Slurm commands so Euler DB hiccups do not freeze the terminal.
# Data status: Administrative helper only; no fake biological data.
set +e
PROJECT="/cluster/scratch/jmccarthy/JM105_RNAseq"
JOBFILE="${PROJECT}/logs/intronsaurus_vnext3Y_latest_jobid.txt"
if [ -f "$JOBFILE" ]; then
  JOBID="$(cat "$JOBFILE" | tr -d '[:space:]')"
else
  JOBID=""
fi
if [ -z "$JOBID" ]; then
  echo "No latest v3Y job id file found: $JOBFILE"
  echo "Recent v3Y logs:"
  ls -lh "${PROJECT}/logs"/*vNext3Y* 2>/dev/null | tail -n 20
  exit 0
fi

echo "JOBID=$JOBID"
echo

echo "=== squeue, max 8 seconds ==="
timeout 8s squeue -j "$JOBID" || echo "[squeue timed out or unavailable; continuing]"
echo

echo "=== sacct, max 12 seconds ==="
timeout 12s sacct -X -j "$JOBID" --format=JobID,JobName%34,State,ExitCode,Elapsed,MaxRSS,ReqMem,Start,End,NodeList%25 --parsable2 || echo "[sacct timed out or unavailable; continuing]"

OUT="${PROJECT}/logs/Intronsaurus_vNext3Y_${JOBID}.out"
ERR="${PROJECT}/logs/Intronsaurus_vNext3Y_${JOBID}.err"

echo
echo "=== stdout ==="
if [ -f "$OUT" ]; then tail -n 280 "$OUT"; else echo "[stdout not created yet] $OUT"; fi

echo
echo "=== stderr ==="
if [ -s "$ERR" ]; then tail -n 280 "$ERR"; else echo "[stderr empty or not created yet] $ERR"; fi
