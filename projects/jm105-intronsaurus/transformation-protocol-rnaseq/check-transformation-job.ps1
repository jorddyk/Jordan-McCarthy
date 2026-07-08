<#
Purpose: Check Slurm/job status and recent logs for the JM105 transformation-protocol RNA-seq workflow.
Original source clue: recovered from uploaded folder `/mnt/data/JM105_Transformation_Protocol_Pipeline/03_JM105_Check_Job.ps1`.
Expected inputs: Euler username, optional Euler host, remote project root.
Expected outputs: terminal status from squeue plus recent stdout/stderr/log tails.
Known assumptions: Windows PowerShell with ssh available; remote analysis directory is $RemoteProjectRoot/transformation_protocol_analysis.
Data status: administrative helper; no biological data generated or modified.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$EulerUser,

    [string]$EulerHost = "euler.ethz.ch",

    [Parameter(Mandatory = $true)]
    [string]$RemoteProjectRoot
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$RemoteTarget = "$EulerUser@$EulerHost"
$RemoteAnalysisDir = "$RemoteProjectRoot/transformation_protocol_analysis"

Write-Host "Current Slurm jobs:"
ssh $RemoteTarget "squeue -u '$EulerUser'"

Write-Host ""
Write-Host "Most recent Slurm stdout/stderr files:"
ssh $RemoteTarget "cd '$RemoteAnalysisDir' && ls -lt JM105_transform_expr_*.out JM105_transform_expr_*.err 2>/dev/null | head -10"

Write-Host ""
Write-Host "Tail of the newest analysis log, when available:"
$TailCommand = @'
latest=$(ls -1t '__REMOTE_ANALYSIS_DIR__'/logs/JM105_transformation_expression_*.log 2>/dev/null | head -1)
if [ -n "$latest" ]; then
    echo "$latest"
    tail -40 "$latest"
else
    echo 'No analysis log exists yet.'
fi
'@
$TailCommand = $TailCommand.Replace("__REMOTE_ANALYSIS_DIR__", $RemoteAnalysisDir)
ssh $RemoteTarget $TailCommand
