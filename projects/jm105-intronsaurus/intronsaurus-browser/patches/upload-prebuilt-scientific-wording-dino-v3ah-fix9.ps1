# Purpose: upload prebuilt Intronsaurus vNext3AH-fix9 archive to Euler and unpack it for inspection.
# Original source clue: ChatGPT JM105/Intronsaurus conversation on 2026-06-26/2026-06-29; recovered bundle `Intronsaurus_Scientific_Wording_Dino_vNext3AH_fix9_code_bundle`, original filename `upload_prebuilt_scientific_wording_dino_v3AH_fix9.ps1`.
# Expected inputs: `147_INTRONSAURUS_MRNA_LIKE_PREMRNA_MODEL_V3AH_FIX9.tar.gz` and the matching status checker in the same extracted bundle.
# Expected outputs: unpacked Euler folder `/cluster/scratch/jmccarthy/JM105_RNAseq/147_INTRONSAURUS_MRNA_LIKE_PREMRNA_MODEL_V3AH_FIX9`.
# Known assumptions: runs from Windows PowerShell with SSH/SCP access to `euler.ethz.ch` as `jmccarthy`.
# Data status: deployment helper only; no raw data committed and no fake biological data generated.
$ErrorActionPreference = "Stop"
$RemoteUser = "jmccarthy"
$RemoteHost = "euler.ethz.ch"
$RemoteOut = "/cluster/scratch/jmccarthy/JM105_RNAseq/147_INTRONSAURUS_MRNA_LIKE_PREMRNA_MODEL_V3AH_FIX9"
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$Prebuilt = Get-ChildItem -Path $Here -Recurse -File | Where-Object { $_.Name -eq "147_INTRONSAURUS_MRNA_LIKE_PREMRNA_MODEL_V3AH_FIX9.tar.gz" } | Select-Object -First 1
$Check = Get-ChildItem -Path $Here -Recurse -File | Where-Object { $_.Name -eq "check_scientific_wording_dino_v3AH_fix9_status.sh" } | Select-Object -First 1
if (-not $Prebuilt) { throw "Missing prebuilt output tarball" }
if (-not $Check) { throw "Missing check script" }
ssh "$RemoteUser@$RemoteHost" "rm -rf $RemoteOut && mkdir -p $RemoteOut /cluster/scratch/jmccarthy/JM105_RNAseq/code/intronsaurus_vnext3AH_fix9_scientific_wording_dino"
scp $Prebuilt.FullName "$RemoteUser@$RemoteHost`:$RemoteOut/"
scp $Check.FullName "$RemoteUser@$RemoteHost`:/cluster/scratch/jmccarthy/JM105_RNAseq/code/intronsaurus_vnext3AH_fix9_scientific_wording_dino/"
ssh "$RemoteUser@$RemoteHost" "cd $RemoteOut && tar -xzf 147_INTRONSAURUS_MRNA_LIKE_PREMRNA_MODEL_V3AH_FIX9.tar.gz --strip-components=1 && ls -lh interactive/Intronsaurus_Explore_Restored_vNext3AH_fix9.html qc/Intronsaurus_vNext3AH_fix9_validation_report.json"
