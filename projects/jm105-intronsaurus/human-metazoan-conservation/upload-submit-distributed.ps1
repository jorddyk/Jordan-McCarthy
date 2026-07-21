$ErrorActionPreference = "Stop"

# Upload and submit the multi-node JM105 HGPS/metazoan workflow.
# Run this script from the extracted bundle directory in Windows PowerShell.

$Euler = "jmccarthy@euler.ethz.ch"
$RemoteRoot = "/cluster/scratch/jmccarthy/JM105_HGPS_Metazoan_Conservation"
$LocalRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

$RequiredFiles = @(
    "scripts/run_hgps_metazoan_conservation.py",
    "scripts/run_hgps_metazoan_conservation_manifest_hotfix.py",
    "scripts/jm105_metazoan_distributed.py",
    "slurm/00_prepare_reference.sbatch",
    "slurm/10_process_sample_array.sbatch",
    "slurm/20_aggregate.sbatch",
    "submit-distributed.sh",
    "watch-distributed.sh",
    "repair-failed-array.sh",
    "README.md"
)

foreach ($RelativePath in $RequiredFiles) {
    $FullPath = Join-Path $LocalRoot $RelativePath
    if (-not (Test-Path -LiteralPath $FullPath -PathType Leaf)) {
        throw "Required bundle file is missing: $FullPath"
    }
}

Write-Host "Creating remote code directories..." -ForegroundColor Cyan
ssh $Euler "mkdir -p '$RemoteRoot/code/scripts' '$RemoteRoot/code/slurm' '$RemoteRoot/logs/distributed' '$RemoteRoot/submission'"

Write-Host "Uploading complete distributed pipeline..." -ForegroundColor Cyan
scp (Join-Path $LocalRoot "scripts/run_hgps_metazoan_conservation.py") "$Euler`:$RemoteRoot/code/scripts/"
scp (Join-Path $LocalRoot "scripts/run_hgps_metazoan_conservation_manifest_hotfix.py") "$Euler`:$RemoteRoot/code/scripts/"
scp (Join-Path $LocalRoot "scripts/jm105_metazoan_distributed.py") "$Euler`:$RemoteRoot/code/scripts/"
scp (Join-Path $LocalRoot "slurm/00_prepare_reference.sbatch") "$Euler`:$RemoteRoot/code/slurm/"
scp (Join-Path $LocalRoot "slurm/10_process_sample_array.sbatch") "$Euler`:$RemoteRoot/code/slurm/"
scp (Join-Path $LocalRoot "slurm/20_aggregate.sbatch") "$Euler`:$RemoteRoot/code/slurm/"
scp (Join-Path $LocalRoot "submit-distributed.sh") "$Euler`:$RemoteRoot/code/"
scp (Join-Path $LocalRoot "watch-distributed.sh") "$Euler`:$RemoteRoot/code/"
scp (Join-Path $LocalRoot "repair-failed-array.sh") "$Euler`:$RemoteRoot/code/"
scp (Join-Path $LocalRoot "README.md") "$Euler`:$RemoteRoot/code/README_DISTRIBUTED.md"

Write-Host "Submitting dependency workflow and cancelling only superseded job 7869397 if still active..." -ForegroundColor Cyan
ssh $Euler "chmod 0755 '$RemoteRoot/code/submit-distributed.sh' '$RemoteRoot/code/watch-distributed.sh' '$RemoteRoot/code/repair-failed-array.sh' '$RemoteRoot/code/scripts/jm105_metazoan_distributed.py' '$RemoteRoot/code/scripts/run_hgps_metazoan_conservation_manifest_hotfix.py'; chmod 0755 '$RemoteRoot/code/slurm/'*.sbatch; OLD_JOB_ID=7869397 MAX_CONCURRENT_SAMPLES=6 bash '$RemoteRoot/code/submit-distributed.sh'"

Write-Host "Submission command completed." -ForegroundColor Green
