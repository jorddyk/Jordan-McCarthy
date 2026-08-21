[CmdletBinding()]
param(
    [string]$EulerUserHost = 'jmccarthy@euler.ethz.ch',
    [string]$RemoteRoot = '/cluster/scratch/jmccarthy/JM105_CELEGANS_WORM_ANALYSIS',
    [string]$EnvironmentPrefix = '/cluster/scratch/jmccarthy/JM105_HGPS_Metazoan_Conservation/software/micromamba-root/envs/jm105-hgps-conservation'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

foreach ($Command in @('ssh', 'scp')) {
    if (-not (Get-Command $Command -ErrorAction SilentlyContinue)) {
        throw "$Command was not found. Enable the Windows OpenSSH Client."
    }
}

$SourceRoot = $PSScriptRoot
$RemoteCodeParent = "$RemoteRoot/code"
$RemoteCodeRoot = "$RemoteCodeParent/JM105_CELEGANS_WORM_ANALYSIS"
$TemporaryZip = Join-Path ([System.IO.Path]::GetTempPath()) (
    'JM105_CELEGANS_WORM_ANALYSIS_' + [guid]::NewGuid().ToString('N') + '.zip'
)
$RemoteZip = "$RemoteCodeParent/JM105_CELEGANS_WORM_ANALYSIS_upload.zip"

try {
    Write-Host '1) Creating a temporary source archive.' -ForegroundColor Cyan
    Compress-Archive -Path (Join-Path $SourceRoot '*') -DestinationPath $TemporaryZip -Force

    Write-Host '2) Preparing the remote code directory.' -ForegroundColor Cyan
    & ssh $EulerUserHost "mkdir -p '$RemoteCodeParent'"
    if ($LASTEXITCODE -ne 0) {
        throw 'Could not create the remote code directory.'
    }

    Write-Host '3) Uploading the complete canonical source.' -ForegroundColor Cyan
    & scp $TemporaryZip "${EulerUserHost}:${RemoteZip}"
    if ($LASTEXITCODE -ne 0) {
        throw 'The source upload failed.'
    }

    Write-Host '4) Unpacking, loading eth_proxy and submitting.' -ForegroundColor Cyan

    $InnerCommand = @(
        "rm -rf '$RemoteCodeRoot'",
        "mkdir -p '$RemoteCodeRoot'",
        "unzip -q -o '$RemoteZip' -d '$RemoteCodeRoot'",
        "rm -f '$RemoteZip'",
        "chmod +x '$RemoteCodeRoot/submit_pipeline.sh' '$RemoteCodeRoot/watch_pipeline.sh' '$RemoteCodeRoot'/slurm/*.sbatch",
        "module load eth_proxy",
        "WORM_ROOT='$RemoteRoot' CODE_ROOT='$RemoteCodeRoot' ENV_PREFIX='$EnvironmentPrefix' bash '$RemoteCodeRoot/submit_pipeline.sh'"
    ) -join ' && '

    $RemoteCommand = "/bin/bash -lc `"$InnerCommand`""
    $SubmissionOutput = & ssh $EulerUserHost $RemoteCommand
    $RemoteExitCode = $LASTEXITCODE
    $SubmissionOutput | ForEach-Object { Write-Host $_ }

    if ($RemoteExitCode -ne 0) {
        throw 'Euler submission failed. Read the output immediately above.'
    }

    $DriverJob = $null
    foreach ($Line in $SubmissionOutput) {
        if ($Line -match '^DRIVER_JOB=(\d+)$') {
            $DriverJob = $Matches[1]
            break
        }
    }

    if (-not $DriverJob) {
        throw 'Submission returned no parseable driver job ID.'
    }

    $Record = [ordered]@{
        submitted_at_local = (Get-Date).ToString('o')
        euler = $EulerUserHost
        driver_job = $DriverJob
        remote_root = $RemoteRoot
        code_root = $RemoteCodeRoot
        environment_prefix = $EnvironmentPrefix
    }

    $RecordPath = Join-Path (Get-Location) "worm_pipeline_submission_${DriverJob}.json"
    $Record | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $RecordPath -Encoding utf8

    Write-Host "`nSubmitted driver job: $DriverJob" -ForegroundColor Green
    Write-Host "Submission record: $RecordPath"
    Write-Host "`nLive tracker command after logging into Euler:"
    Write-Host "bash '$RemoteCodeRoot/watch_pipeline.sh' '$DriverJob'"
}
finally {
    Remove-Item -LiteralPath $TemporaryZip -Force -ErrorAction SilentlyContinue
}
