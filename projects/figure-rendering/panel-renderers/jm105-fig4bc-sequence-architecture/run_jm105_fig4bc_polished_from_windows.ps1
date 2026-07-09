$ErrorActionPreference = "Stop"

# JM105 Figure 4B/C polished renderer Windows orchestrator.
# Run this from a local clone of jorddyk/Jordan-McCarthy.
# It uploads the sibling Python renderer and Euler bash runner, executes on Euler,
# retrieves out/ and logs/, and opens the white-preview contact sheet.

$RunStamp = Get-Date -Format "yyyyMMdd_HHmmss"
$EulerUser = "jmccarthy"
$EulerHost = "euler.ethz.ch"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonPath = Join-Path $ScriptDir "render_jm105_fig4bc_polished.py"
$BashPath = Join-Path $ScriptDir "run_jm105_fig4bc_polished_euler.sh"

if (-not (Test-Path -LiteralPath $PythonPath)) {
    throw "Missing sibling Python renderer: $PythonPath"
}
if (-not (Test-Path -LiteralPath $BashPath)) {
    throw "Missing sibling Euler bash runner: $BashPath"
}

$LocalRunRoot = Join-Path $env:USERPROFILE "Downloads\JM105_Fig4BC_polished_$RunStamp"
$LocalOutDir = Join-Path $LocalRunRoot "out"
$RemoteRunDir = "/cluster/home/jmccarthy/JM105_Fig4BC_polished_$RunStamp"

New-Item -ItemType Directory -Force -Path $LocalRunRoot, $LocalOutDir | Out-Null

Write-Host "Local run root:"
Write-Host $LocalRunRoot
Write-Host "Remote run dir:"
Write-Host $RemoteRunDir

ssh "${EulerUser}@${EulerHost}" "mkdir -p '${RemoteRunDir}' '${RemoteRunDir}/out' '${RemoteRunDir}/logs'"
scp "$PythonPath" "${EulerUser}@${EulerHost}:${RemoteRunDir}/render_jm105_fig4bc_polished.py"
scp "$BashPath" "${EulerUser}@${EulerHost}:${RemoteRunDir}/run_jm105_fig4bc_polished_euler.sh"

ssh "${EulerUser}@${EulerHost}" "perl -pi -e 's/\r$//' '${RemoteRunDir}/render_jm105_fig4bc_polished.py' '${RemoteRunDir}/run_jm105_fig4bc_polished_euler.sh' && chmod +x '${RemoteRunDir}/run_jm105_fig4bc_polished_euler.sh' && cd '${RemoteRunDir}' && bash run_jm105_fig4bc_polished_euler.sh"

scp -r "${EulerUser}@${EulerHost}:${RemoteRunDir}/out/." "$LocalOutDir\"
scp -r "${EulerUser}@${EulerHost}:${RemoteRunDir}/logs/." "$LocalOutDir\"

$ContactSheet = Join-Path $LocalOutDir "panels\Figure4BC_polished_contact_sheet_white_preview.png"
$PanelBPreview = Join-Path $LocalOutDir "panels\Figure4_panel_B_polished_white_preview.png"
$PanelCPreview = Join-Path $LocalOutDir "panels\Figure4_panel_C_polished_white_preview.png"
$RenderLog = Join-Path $LocalOutDir "render.log"

if (Test-Path -LiteralPath $ContactSheet) {
    Start-Process $ContactSheet
} elseif (Test-Path -LiteralPath $PanelBPreview) {
    Start-Process $PanelBPreview
} elseif (Test-Path -LiteralPath $PanelCPreview) {
    Start-Process $PanelCPreview
} else {
    Start-Process $LocalOutDir
    throw "No preview PNG was retrieved. Check output folder and render log: $RenderLog"
}

Write-Host "DONE"
Write-Host "Output folder:"
Write-Host $LocalOutDir
Write-Host "Open contact sheet:"
Write-Host $ContactSheet
Write-Host "Key audits:"
Write-Host (Join-Path $LocalOutDir "audits\Figure4BC_collision_audit.tsv")
Write-Host (Join-Path $LocalOutDir "audits\Figure4BC_final_self_audit.tsv")
Write-Host (Join-Path $LocalOutDir "audits\Figure4B_stats_audit.tsv")
Write-Host (Join-Path $LocalOutDir "audits\Figure4C_stats_audit.tsv")
