[CmdletBinding()]
param(
    [string]$EulerUserHost = 'jmccarthy@euler.ethz.ch',
    [string]$RemoteRoot = '/cluster/scratch/jmccarthy/JM105_CELEGANS_WORM_ANALYSIS',
    [string]$LocalOutput = "$HOME\Downloads\JM105_CELEGANS_WORM_RESULTS"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path $LocalOutput | Out-Null

$RemoteResults = "$RemoteRoot/work/results"
$Files = @(
    'FINAL_REPORT.md',
    'FINAL_VERDICT.md',
    'sample_scores.tsv',
    'contrast_summary.tsv',
    'FIGURE_MANIFEST.tsv',
    'AGGREGATION_COMPLETE.json'
)
foreach ($File in $Files) {
    scp "${EulerUserHost}:${RemoteResults}/${File}" $LocalOutput
}
scp -r "${EulerUserHost}:${RemoteResults}/figures" $LocalOutput
Get-ChildItem -Recurse $LocalOutput
