# Purpose: retrieve and open the Intronsaurus vNext3AH-fix9 scientific-wording/dino archive from Euler.
# Original source clue: ChatGPT JM105/Intronsaurus conversation on 2026-06-26/2026-06-29; recovered bundle `Intronsaurus_Scientific_Wording_Dino_vNext3AH_fix9_code_bundle`, original filename `retrieve_scientific_wording_dino_v3AH_fix9.ps1`.
# Expected inputs: Euler archive `/cluster/scratch/jmccarthy/JM105_RNAseq/147_INTRONSAURUS_MRNA_LIKE_PREMRNA_MODEL_V3AH_FIX9/147_INTRONSAURUS_MRNA_LIKE_PREMRNA_MODEL_V3AH_FIX9.tar.gz`.
# Expected outputs: local HTML under `Y:\Jordan\JM101\Intronsaurus_Scientific_Wording_Dino_vNext3AH_fix9`.
# Known assumptions: runs on Windows PowerShell with `tar`, SSH/SCP, and mapped `Y:` drive available.
# Data status: retrieval helper only; no raw data committed and no fake biological data generated.
$ErrorActionPreference = "Stop"
$RemoteUser = "jmccarthy"
$RemoteHost = "euler.ethz.ch"
$RemoteDir = "/cluster/scratch/jmccarthy/JM105_RNAseq/147_INTRONSAURUS_MRNA_LIKE_PREMRNA_MODEL_V3AH_FIX9"
$LocalDir = "Y:\Jordan\JM101\Intronsaurus_Scientific_Wording_Dino_vNext3AH_fix9"
New-Item -ItemType Directory -Force -Path $LocalDir | Out-Null
scp "${RemoteUser}@${RemoteHost}:${RemoteDir}/147_INTRONSAURUS_MRNA_LIKE_PREMRNA_MODEL_V3AH_FIX9.tar.gz" "$LocalDir\"
scp "${RemoteUser}@${RemoteHost}:${RemoteDir}/qc/Intronsaurus_vNext3AH_fix9_validation_report.json" "$LocalDir\"
cd $LocalDir
tar -xzf "147_INTRONSAURUS_MRNA_LIKE_PREMRNA_MODEL_V3AH_FIX9.tar.gz"
$Html = Get-ChildItem -Path $LocalDir -Recurse -File | Where-Object { $_.Name -eq "Intronsaurus_Explore_Restored_vNext3AH_fix9.html" } | Select-Object -First 1
if (-not $Html) { throw "Could not find Intronsaurus_Explore_Restored_vNext3AH_fix9.html after extraction" }
Start-Process $Html.FullName
