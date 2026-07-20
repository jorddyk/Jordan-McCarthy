# Purpose: Upload and submit the JM105 HGPS + metazoan CR conservation bundle to Euler.
# Expected input: this script remains beside scripts/, config/, README.md and the .sbatch file.
# Expected output: uploaded code under Euler scratch and a submitted Slurm job.
# Known assumptions: Windows OpenSSH ssh/scp; user jmccarthy; Euler hostname euler.ethz.ch.
# Data status: administrative helper only; raw RNA-seq remains on Euler and is never uploaded to GitHub.

$ErrorActionPreference = "Stop"

$Remote = "jmccarthy@euler.ethz.ch"
$Project = "/cluster/scratch/jmccarthy/JM105_HGPS_Metazoan_Conservation"
$BundleDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RemoteCode = "$Project/code"
$RemoteLogs = "$Project/logs"

$Required = @(
    (Join-Path $BundleDir "README.md"),
    (Join-Path $BundleDir "run-hgps-metazoan-conservation.sbatch"),
    (Join-Path $BundleDir "scripts\run_hgps_metazoan_conservation.py"),
    (Join-Path $BundleDir "scripts\run_hgps_metazoan_conservation_manifest_hotfix.py"),
    (Join-Path $BundleDir "config\datasets.tsv")
)

foreach ($File in $Required) {
    if (!(Test-Path $File)) {
        throw "Missing required bundle file: $File"
    }
}

ssh $Remote "mkdir -p '$RemoteCode/scripts' '$RemoteCode/config' '$RemoteLogs'"

scp (Join-Path $BundleDir "README.md") "${Remote}:${RemoteCode}/README.md"
scp (Join-Path $BundleDir "run-hgps-metazoan-conservation.sbatch") "${Remote}:${RemoteCode}/run-hgps-metazoan-conservation.sbatch"
scp (Join-Path $BundleDir "scripts\run_hgps_metazoan_conservation.py") "${Remote}:${RemoteCode}/scripts/run_hgps_metazoan_conservation.py"
scp (Join-Path $BundleDir "scripts\run_hgps_metazoan_conservation_manifest_hotfix.py") "${Remote}:${RemoteCode}/scripts/run_hgps_metazoan_conservation_manifest_hotfix.py"
scp (Join-Path $BundleDir "config\datasets.tsv") "${Remote}:${RemoteCode}/config/datasets.tsv"

$SubmitLines = @(& ssh $Remote "sbatch '$RemoteCode/run-hgps-metazoan-conservation.sbatch'" 2>&1)
$SubmitExitCode = $LASTEXITCODE
$SubmitText = ($SubmitLines | Out-String).Trim()
Write-Host $SubmitText

if ($SubmitExitCode -ne 0) {
    throw "Euler sbatch failed with exit code $SubmitExitCode`n$SubmitText"
}

$SubmitMatch = [regex]::Match($SubmitText, "Submitted batch job\s+(\d+)")
if (-not $SubmitMatch.Success) {
    throw "Euler returned success but no Slurm job ID could be parsed:`n$SubmitText"
}

$JobID = $SubmitMatch.Groups[1].Value
ssh $Remote "printf '%s' '$JobID' > '$RemoteLogs/latest_jobid.txt'"
Write-Host "Submitted JOBID=$JobID"
Write-Host "Euler report will be: $Project/work/results/GATE_REPORT.md"
Write-Host "Check status with: ssh $Remote `"squeue -j $JobID; tail -n 80 '$RemoteLogs/JM105_HGPS_CR_${JobID}.out'`""
