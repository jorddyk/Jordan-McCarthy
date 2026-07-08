#!/bin/bash
# Purpose: check Euler output files and validation flags for Intronsaurus vNext3AH-fix9 scientific-wording/dino build.
# Original source clue: ChatGPT JM105/Intronsaurus conversation on 2026-06-26/2026-06-29; recovered bundle `Intronsaurus_Scientific_Wording_Dino_vNext3AH_fix9_code_bundle`, original filename `check_scientific_wording_dino_v3AH_fix9_status.sh`.
# Expected inputs: Euler folder `/cluster/scratch/jmccarthy/JM105_RNAseq/147_INTRONSAURUS_MRNA_LIKE_PREMRNA_MODEL_V3AH_FIX9` with HTML, tarball, and validation JSON.
# Expected outputs: terminal status report with file presence and validation key/value flags.
# Known assumptions: runs on ETH Euler with Python 3 available.
# Data status: checker only; no raw data committed and no fake biological data generated.
set -euo pipefail
ROOT=/cluster/scratch/jmccarthy/JM105_RNAseq/147_INTRONSAURUS_MRNA_LIKE_PREMRNA_MODEL_V3AH_FIX9
REPORT=$ROOT/qc/Intronsaurus_vNext3AH_fix9_validation_report.json
HTML=$ROOT/interactive/Intronsaurus_Explore_Restored_vNext3AH_fix9.html
TAR=$ROOT/147_INTRONSAURUS_MRNA_LIKE_PREMRNA_MODEL_V3AH_FIX9.tar.gz
echo "=== OUTPUT CHECK ==="
ls -lh "$HTML" "$TAR" 2>/dev/null || true
echo
echo "=== VALIDATION REPORT ==="
if [[ -f "$REPORT" ]]; then
  python3 -c "import json; r=json.load(open('$REPORT')); [print(f'{k}={v}') for k,v in r.items()]"
else
  echo REPORT_MISSING=$REPORT
fi
