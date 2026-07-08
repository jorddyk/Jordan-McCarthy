$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

# Human purpose: Retrieve and open the completed Intronsaurus vNext3I archive from Euler.
# Original source clue: current JM105/Intronsaurus chat artifact `retrieve_intronsaurus_explore_restored_DATA_fix_v3I.ps1`.
# Expected inputs: completed archive/checksum on Euler from the v3I build job.
# Expected outputs: extracted HTML under `Y:\Jordan\JM101\Intronsaurus_Explore_Restored_vNext3I` and opened in the default browser.
# Known assumptions: user can SCP from Euler as `jmccarthy`; Windows has `tar` available.
# Data status: retrieval helper only; no biological data are generated or modified.

$RemoteLogin = "jmccarthy@eu-login-20.euler.ethz.ch"
$RemoteArchive = "/cluster/scratch/jmccarthy/JM105_RNAseq/Intronsaurus_Explore_Restored_vNext3I.tar.gz"
$RemoteChecksum = "/cluster/scratch/jmccarthy/JM105_RNAseq/Intronsaurus_Explore_Restored_vNext3I.tar.gz.sha256"
$Dest = "Y:\Jordan\JM101\Intronsaurus_Explore_Restored_vNext3I"

New-Item -ItemType Directory -Force -Path $Dest | Out-Null

Write-Host "Retrieving Intronsaurus vNext3I archive..."
scp "${RemoteLogin}:${RemoteArchive}" "$Dest\"
scp "${RemoteLogin}:${RemoteChecksum}" "$Dest\"

Write-Host "Extracting..."
tar -xzf "$Dest\Intronsaurus_Explore_Restored_vNext3I.tar.gz" -C $Dest

$Html = "$Dest\106_INTRONSAURUS_EXPLORE_RESTORED_V3I\interactive\Intronsaurus_Explore_Restored_vNext3I.html"
if (!(Test-Path -LiteralPath $Html)) {
    throw "Expected HTML not found after extraction: $Html"
}

Write-Host "Opening:"
Write-Host $Html
Start-Process $Html
