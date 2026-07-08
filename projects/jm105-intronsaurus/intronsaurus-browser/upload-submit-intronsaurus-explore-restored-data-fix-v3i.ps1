$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

# Human purpose: Upload the Intronsaurus vNext3I code bundle to Euler and submit the restoration build job.
# Original source clue: current JM105/Intronsaurus chat artifact `upload_submit_intronsaurus_explore_restored_DATA_fix_v3I.ps1`.
# Expected inputs: downloaded `Intronsaurus_Explore_Restored_DATA_fix_vNext3I_code_bundle.zip` in `$HOME\Downloads`.
# Expected outputs: uploaded bundle under `/cluster/scratch/jmccarthy/JM105_RNAseq/scripts`, submitted Slurm job, latest-jobid file.
# Known assumptions: user can SSH/SCP to Euler as `jmccarthy`; bundle includes the v3I Python and required patch-chain sources.
# Data status: administrative upload/submit helper only; no biological data are generated or modified.

$RemoteLogin = "jmccarthy@eu-login-20.euler.ethz.ch"
$Project = "/cluster/scratch/jmccarthy/JM105_RNAseq"
$RemoteScripts = "$Project/scripts"
$LocalDownloads = "$HOME\Downloads"
$Bundle = Join-Path $LocalDownloads "Intronsaurus_Explore_Restored_DATA_fix_vNext3I_code_bundle.zip"

if (!(Test-Path -LiteralPath $Bundle)) {
    throw "Missing downloaded bundle: $Bundle"
}

Write-Host "Uploading Intronsaurus vNext3I bundle to Euler..."
scp $Bundle "${RemoteLogin}:${RemoteScripts}/Intronsaurus_Explore_Restored_DATA_fix_vNext3I_code_bundle.zip"

Write-Host "Unpacking and submitting on Euler..."
$RemoteCmd = @'
set -euo pipefail
PROJECT="/cluster/scratch/jmccarthy/JM105_RNAseq"
SCRIPTS="${PROJECT}/scripts"
mkdir -p "${SCRIPTS}" "${PROJECT}/logs"
cd "${SCRIPTS}"
unzip -o Intronsaurus_Explore_Restored_DATA_fix_vNext3I_code_bundle.zip >/dev/null
JOBID="$(sbatch --parsable "${SCRIPTS}/127_intronsaurus_explore_restored_DATA_fix_v3I.sbatch")"
echo "${JOBID}" > "${PROJECT}/logs/intronsaurus_vnext3I_latest_jobid.txt"
echo "INTRONSAURUS_VNEXT3I_JOB_ID=${JOBID}"
squeue -j "${JOBID}"
'@

ssh $RemoteLogin $RemoteCmd
