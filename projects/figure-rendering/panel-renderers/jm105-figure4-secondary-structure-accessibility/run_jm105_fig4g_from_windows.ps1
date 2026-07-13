$ErrorActionPreference = "Stop"

<#
JM105 Figure 4G secondary-structure accessibility runner.

This runner uploads the stored Python scripts to Euler, installs the Python
ViennaRNA/RNAlib package into a local vendor_py directory if needed, computes
the locked-49 metric table, renders the final individual-dot + median/IQR panel,
retrieves the full out/ folder, and opens the white preview PNG.

No rendered figure binary is stored in GitHub. Outputs are created under
C:\Users\jmccarthy\Downloads\JM105_Figure4G_accessibility_<timestamp>\out.
#>

$EulerUser = "jmccarthy"
$EulerHost = "euler.ethz.ch"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$RunStem = "JM105_Figure4G_accessibility_$Timestamp"

$ScriptPath = $MyInvocation.MyCommand.Path
$RendererDir = Split-Path -Parent $ScriptPath
$LocalScriptDir = Join-Path $RendererDir "scripts"
$ComputePython = Join-Path $LocalScriptDir "compute_fig4g_rnalib_locked49_metrics.py"
$RenderPython = Join-Path $LocalScriptDir "rerender_fig4g_introns_median_order_label_fix.py"

if (-not (Test-Path -LiteralPath $ComputePython)) {
    throw "Missing compute script: $ComputePython"
}
if (-not (Test-Path -LiteralPath $RenderPython)) {
    throw "Missing render script: $RenderPython"
}

$LocalRunRoot = Join-Path $env:USERPROFILE "Downloads\$RunStem"
$LocalOutDir = Join-Path $LocalRunRoot "out"
$LocalGeneratedScriptDir = Join-Path $LocalRunRoot "scripts"
New-Item -ItemType Directory -Force -Path $LocalRunRoot, $LocalOutDir, $LocalGeneratedScriptDir | Out-Null

$RemoteRunDir = "/cluster/home/jmccarthy/$RunStem"
$BashPath = Join-Path $LocalGeneratedScriptDir "run_fig4g_on_euler.sh"

function Write-Utf8NoBom {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Text
    )
    $Encoding = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Path, $Text, $Encoding)
}

$BashCode = @'
#!/usr/bin/env bash
set -euo pipefail

RUN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$RUN_DIR"

mkdir -p out logs vendor_py

echo "JM105 Figure 4G accessibility runner"
echo "Run dir: $RUN_DIR"
echo "Started: $(date -Is)"
echo "Host: $(hostname)"

if [ -f /etc/profile.d/modules.sh ]; then
  source /etc/profile.d/modules.sh
fi

module purge >/dev/null 2>&1 || true
module load fast_python_workshop_cpu/2025.0.0 >/dev/null 2>&1 || true

if command -v venv_cpu_init >/dev/null 2>&1; then
  venv_cpu_init >/dev/null 2>&1 || true
fi

PYTHON_BIN="$(command -v python3 || true)"
if [ -z "$PYTHON_BIN" ]; then
  echo "No python3 found after fast_python_workshop_cpu module." | tee logs/NO_PYTHON.txt
  exit 10
fi

echo "Python: $PYTHON_BIN"
"$PYTHON_BIN" --version

"$PYTHON_BIN" - <<'PY' 2>&1 | tee logs/base_python_imports.log
import sys
print("python", sys.executable)
for mod in ["matplotlib", "pandas", "numpy", "scipy", "PIL"]:
    m = __import__(mod)
    print(mod, "OK", getattr(m, "__version__", ""))
PY

export PYTHONPATH="$RUN_DIR/vendor_py:${PYTHONPATH:-}"

if "$PYTHON_BIN" - <<'PY' >/dev/null 2>&1
import RNA
PY
then
  echo "RNA module already importable." | tee logs/RNA_module_status.txt
else
  echo "Installing ViennaRNA Python package into local vendor_py..." | tee logs/RNA_module_status.txt
  "$PYTHON_BIN" -m pip install --target "$RUN_DIR/vendor_py" --upgrade ViennaRNA 2>&1 | tee logs/pip_install_ViennaRNA.log
fi

"$PYTHON_BIN" - <<'PY' 2>&1 | tee logs/RNA_module_import_check.log
import RNA
print("RNA module OK")
print(getattr(RNA, "__file__", "unknown"))
print("RNA.fold test", RNA.fold("GCGCAAAAGCGC"))
PY

"$PYTHON_BIN" -m py_compile scripts/compute_fig4g_rnalib_locked49_metrics.py
"$PYTHON_BIN" scripts/compute_fig4g_rnalib_locked49_metrics.py 2>&1 | tee logs/compute.log

FIG4G_METRIC_TABLE="$RUN_DIR/out/derived_data/Figure4G_locked49_RNAlib_structure_metric_table.tsv" \
  "$PYTHON_BIN" -m py_compile scripts/rerender_fig4g_introns_median_order_label_fix.py

FIG4G_METRIC_TABLE="$RUN_DIR/out/derived_data/Figure4G_locked49_RNAlib_structure_metric_table.tsv" \
  "$PYTHON_BIN" scripts/rerender_fig4g_introns_median_order_label_fix.py 2>&1 | tee logs/render.log

echo "Finished: $(date -Is)"
'@

Write-Utf8NoBom -Path $BashPath -Text $BashCode

Write-Host "Local run root:"
Write-Host $LocalRunRoot
Write-Host "Remote run dir:"
Write-Host $RemoteRunDir

ssh "${EulerUser}@${EulerHost}" "mkdir -p '${RemoteRunDir}/scripts' '${RemoteRunDir}/out' '${RemoteRunDir}/logs' '${RemoteRunDir}/vendor_py'"
scp "$ComputePython" "${EulerUser}@${EulerHost}:${RemoteRunDir}/scripts/"
scp "$RenderPython" "${EulerUser}@${EulerHost}:${RemoteRunDir}/scripts/"
scp "$BashPath" "${EulerUser}@${EulerHost}:${RemoteRunDir}/scripts/"

ssh "${EulerUser}@${EulerHost}" "perl -pi -e 's/\r$//' '${RemoteRunDir}/scripts/compute_fig4g_rnalib_locked49_metrics.py' '${RemoteRunDir}/scripts/rerender_fig4g_introns_median_order_label_fix.py' '${RemoteRunDir}/scripts/run_fig4g_on_euler.sh' && chmod +x '${RemoteRunDir}/scripts/run_fig4g_on_euler.sh' && cd '${RemoteRunDir}' && bash scripts/run_fig4g_on_euler.sh"

scp -r "${EulerUser}@${EulerHost}:${RemoteRunDir}/out/." "$LocalOutDir\"
scp -r "${EulerUser}@${EulerHost}:${RemoteRunDir}/logs/." "$LocalOutDir\"

$WhitePreview = Join-Path $LocalOutDir "panels\Figure4G_introns_median_order_label_fix_white_preview.png"

if (Test-Path -LiteralPath $WhitePreview) {
    Start-Process $WhitePreview
} else {
    Start-Process $LocalOutDir
    throw "White preview was not retrieved. Check logs in $LocalOutDir"
}

Write-Host "DONE"
Write-Host "Output folder:"
Write-Host $LocalOutDir
Write-Host "White preview:"
Write-Host $WhitePreview
Write-Host "Main SVG:"
Write-Host (Join-Path $LocalOutDir "panels\Figure4G_introns_median_order_label_fix.svg")
Write-Host "Key audits/data:"
Write-Host (Join-Path $LocalOutDir "audits\Figure4G_group_count_audit.tsv")
Write-Host (Join-Path $LocalOutDir "audits\Figure4G_sequence_extraction_audit.tsv")
Write-Host (Join-Path $LocalOutDir "audits\Figure4G_structure_failures.tsv")
Write-Host (Join-Path $LocalOutDir "audits\Figure4G_order_label_fix_final_self_audit.tsv")
Write-Host (Join-Path $LocalOutDir "derived_data\Figure4G_locked49_RNAlib_structure_metric_table.tsv")
Write-Host (Join-Path $LocalOutDir "derived_data\Figure4G_order_label_fix_stats.tsv")
Write-Host (Join-Path $LocalOutDir "derived_data\Figure4G_introns_median_order_label_fix_summary.tsv")
