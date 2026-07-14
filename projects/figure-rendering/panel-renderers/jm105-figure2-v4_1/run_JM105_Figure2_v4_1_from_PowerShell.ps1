$ErrorActionPreference = "Stop"

$PackageRoot = $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($PackageRoot)) {
    throw "PowerShell could not resolve the extracted package directory."
}

$RequiredLocalFiles = @(
    (Join-Path $PackageRoot "render_JM105_Figure2_v4_1_no_overlap.py"),
    (Join-Path $PackageRoot "run_JM105_Figure2_v4_1_on_euler.sh"),
    (Join-Path $PackageRoot "inputs\Panel2A_JM104_RLS_source_CLEAN_v3_1.tsv"),
    (Join-Path $PackageRoot "inputs\Figure_2A_Age_CR_candidate_map_LABEL_COLUMN_FINAL.plot_source.tsv"),
    (Join-Path $PackageRoot "inputs\Figure2E_existing.svg")
)

foreach ($RequiredLocalFile in $RequiredLocalFiles) {
    if (-not (Test-Path -LiteralPath $RequiredLocalFile -PathType Leaf)) {
        throw "Required package file is missing: $RequiredLocalFile"
    }
    if ((Get-Item -LiteralPath $RequiredLocalFile).Length -le 0) {
        throw "Required package file is empty: $RequiredLocalFile"
    }
}

$Euler = "jmccarthy@euler.ethz.ch"
$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$RemoteRoot = "/cluster/home/jmccarthy/JM105_Figure2_v4_1_no_overlap_${Stamp}"
$LocalRoot = Join-Path $env:USERPROFILE "Downloads\JM105_Figure2_v4_1_no_overlap_${Stamp}"

Write-Host "Creating the Euler run directory..." -ForegroundColor Cyan
ssh $Euler "mkdir -p '${RemoteRoot}/inputs'"
if ($LASTEXITCODE -ne 0) {
    throw "Could not create remote Euler directory: ${RemoteRoot}"
}

Write-Host "Uploading the complete Figure 2 v4.1 package..." -ForegroundColor Cyan
scp (Join-Path $PackageRoot "render_JM105_Figure2_v4_1_no_overlap.py") "${Euler}:${RemoteRoot}/"
if ($LASTEXITCODE -ne 0) { throw "Renderer upload failed." }
scp (Join-Path $PackageRoot "run_JM105_Figure2_v4_1_on_euler.sh") "${Euler}:${RemoteRoot}/"
if ($LASTEXITCODE -ne 0) { throw "Euler runner upload failed." }
scp (Join-Path $PackageRoot "inputs\Panel2A_JM104_RLS_source_CLEAN_v3_1.tsv") "${Euler}:${RemoteRoot}/inputs/"
if ($LASTEXITCODE -ne 0) { throw "Panel A source upload failed." }
scp (Join-Path $PackageRoot "inputs\Figure_2A_Age_CR_candidate_map_LABEL_COLUMN_FINAL.plot_source.tsv") "${Euler}:${RemoteRoot}/inputs/"
if ($LASTEXITCODE -ne 0) { throw "Strict source upload failed." }
scp (Join-Path $PackageRoot "inputs\Figure2E_existing.svg") "${Euler}:${RemoteRoot}/inputs/"
if ($LASTEXITCODE -ne 0) { throw "Panel E vector source upload failed." }

Write-Host "Rendering all six Figure 2 panels on Euler..." -ForegroundColor Cyan
ssh $Euler "chmod +x '${RemoteRoot}/run_JM105_Figure2_v4_1_on_euler.sh' && bash '${RemoteRoot}/run_JM105_Figure2_v4_1_on_euler.sh' '${RemoteRoot}/out'"
if ($LASTEXITCODE -ne 0) {
    throw "Figure 2 v4.1 Euler rendering failed. Remote run: ${RemoteRoot}"
}

if (Test-Path -LiteralPath $LocalRoot) {
    Remove-Item -LiteralPath $LocalRoot -Recurse -Force
}
New-Item -ItemType Directory -Path $LocalRoot -Force | Out-Null

Write-Host "Downloading the complete rendered output..." -ForegroundColor Cyan
scp -r "${Euler}:${RemoteRoot}/out/." "$LocalRoot\"
if ($LASTEXITCODE -ne 0) {
    throw "Figure 2 v4.1 output download failed. Remote output remains at: ${RemoteRoot}/out"
}

$Contact = Join-Path $LocalRoot "Figure_2_v4_1_full_composite.preview_white.png"
$Audit = Join-Path $LocalRoot "Figure_2_v4_1_hard_collision_audit.txt"

foreach ($RequiredOutput in @($Contact, $Audit)) {
    if (-not (Test-Path -LiteralPath $RequiredOutput -PathType Leaf)) {
        throw "Required output was not downloaded: $RequiredOutput"
    }
    if ((Get-Item -LiteralPath $RequiredOutput).Length -le 0) {
        throw "Downloaded output is empty: $RequiredOutput"
    }
}

foreach ($Panel in @("A", "B", "C", "D", "E", "F")) {
    $PanelDir = Join-Path $LocalRoot "panels\$Panel"
    if (-not (Test-Path -LiteralPath $PanelDir -PathType Container)) {
        throw "Panel directory is missing: $PanelDir"
    }
    foreach ($Pattern in @("*.transparent.svg", "*.transparent.pdf", "*.transparent.png", "*.preview_white.png")) {
        $Matches = @(Get-ChildItem -LiteralPath $PanelDir -File -Filter $Pattern)
        if ($Matches.Count -lt 1) {
            throw "Panel $Panel is missing required output: $Pattern"
        }
    }
}

$AuditText = Get-Content -LiteralPath $Audit -Raw
if ($AuditText -notmatch "RESULT: all six panels passed the hard pre-save collision gate") {
    throw "The downloaded collision audit did not report a complete pass."
}

Write-Host ""
Write-Host "FIGURE 2 V4.1 DOWNLOADED AND VERIFIED" -ForegroundColor Green
Write-Host "Remote output: ${RemoteRoot}/out"
Write-Host "Local output: $LocalRoot"
Write-Host "Contact sheet: $Contact"

Invoke-Item -LiteralPath $Contact
Invoke-Item -LiteralPath $LocalRoot
