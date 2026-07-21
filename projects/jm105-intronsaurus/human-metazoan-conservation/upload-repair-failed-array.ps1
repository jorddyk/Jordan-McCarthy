$ErrorActionPreference = "Stop"

# Purpose: upload the concurrency-lock fix and rerun only failed array tasks 1,5,33.
# Inputs: the existing 31 completed sample outputs from array 7873466.
# Outputs: a repair array plus a new dependency-controlled aggregate job.
# Data status: administrative helper only; raw sequencing data remain on Euler.

$Euler = "jmccarthy@euler.ethz.ch"
$RemoteRoot = "/cluster/scratch/jmccarthy/JM105_HGPS_Metazoan_Conservation"
$LocalRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

$RequiredFiles = @(
    "slurm/10_process_sample_array.sbatch",
    "slurm/20_aggregate.sbatch",
    "repair-failed-array.sh",
    "watch-distributed.sh"
)

foreach ($RelativePath in $RequiredFiles) {
    $FullPath = Join-Path $LocalRoot $RelativePath
    if (-not (Test-Path -LiteralPath $FullPath -PathType Leaf)) {
        throw "Required repair file is missing: $FullPath"
    }
}

Write-Host "Uploading the lock-free array and aggregate launchers..." -ForegroundColor Cyan
ssh $Euler "mkdir -p '$RemoteRoot/code/slurm' '$RemoteRoot/code' '$RemoteRoot/logs/distributed' '$RemoteRoot/submission'"
scp (Join-Path $LocalRoot "slurm/10_process_sample_array.sbatch") "$Euler`:$RemoteRoot/code/slurm/"
scp (Join-Path $LocalRoot "slurm/20_aggregate.sbatch") "$Euler`:$RemoteRoot/code/slurm/"
scp (Join-Path $LocalRoot "repair-failed-array.sh") "$Euler`:$RemoteRoot/code/"
scp (Join-Path $LocalRoot "watch-distributed.sh") "$Euler`:$RemoteRoot/code/"

Write-Host "Submitting only tasks 1, 5 and 33, then a new aggregate job..." -ForegroundColor Cyan
ssh $Euler "chmod 0755 '$RemoteRoot/code/repair-failed-array.sh' '$RemoteRoot/code/watch-distributed.sh' '$RemoteRoot/code/slurm/10_process_sample_array.sbatch' '$RemoteRoot/code/slurm/20_aggregate.sbatch'; FAILED_TASKS=1,5,33 bash '$RemoteRoot/code/repair-failed-array.sh'"

Write-Host "Repair submission completed." -ForegroundColor Green
Write-Host "Monitor on Euler with:" -ForegroundColor Green
Write-Host "bash $RemoteRoot/code/watch-distributed.sh"
