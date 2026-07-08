#!/usr/bin/env bash
# Human purpose:
#   Run the canonical JM105 Figure 4 Panel E external-context layout-fix renderer on Euler.
#
# Original source clue / conversation context:
#   Recovered from the 2026-07-06 Figure 4 V17D/V17E2 repair workflow, where Panel E
#   needed a targeted geometry fix after label collisions in the V17D full composite.
#
# Expected inputs:
#   - Repository file: projects/figure-rendering/panel-renderers/render-figure4-panel-e-external-context.py
#   - Previous render directory with derived_data/Figure4E_source_values.tsv
#
# Expected outputs:
#   - SVG/PDF/transparent PNG/white-preview PNG for clean Panel E
#   - audit/ and derived_data/ TSVs under the output directory
#   - a tar.gz archive of the output directory
#
# Known assumptions:
#   - This is a layout repair only and does not recompute biological source values.
#   - Uses real V17D derived values when Figure4E_source_values.tsv is present.
#   - Does not use a tight crop option. SVG text remains editable.
#
# Data status:
#   Real derived JM105 / published-starvation comparison values from V17D. No fake data.

ROOT="/cluster/scratch/jmccarthy/JM105_RNAseq"
PREV="/cluster/scratch/jmccarthy/JM105_RNAseq/Figure4_RENDER_V17D_PPTSAFE_EXPORT_20260706_155050"
STAMP="$(date +%Y%m%d_%H%M%S)"
OUTDIR="${ROOT}/Figure4_PANEL_E_EXTERNAL_CONTEXT_${STAMP}"
ARCHIVE="${OUTDIR}.tar.gz"

SCRIPT_PATH="${ROOT}/repo/Jordan-McCarthy/projects/figure-rendering/panel-renderers/render-figure4-panel-e-external-context.py"

PYTHON_BIN="$(command -v python3)"
PYTHON_RECORD="${ROOT}/Figure2_stage1_audit_20260630_145204/PYTHON_WITH_NUMPY_PANDAS.txt"
if [ -f "$PYTHON_RECORD" ]; then
  PYTHON_BIN="$(cat "$PYTHON_RECORD")"
fi

mkdir -p "$OUTDIR"

if [ ! -f "$SCRIPT_PATH" ]; then
  echo "ERROR: renderer script missing: $SCRIPT_PATH"
  echo "Clone or update jorddyk/Jordan-McCarthy under ${ROOT}/repo/Jordan-McCarthy, or edit SCRIPT_PATH."
else
  echo "ROOT=$ROOT"
  echo "PREV=$PREV"
  echo "OUTDIR=$OUTDIR"
  echo "PYTHON_BIN=$PYTHON_BIN"
  echo "SCRIPT_PATH=$SCRIPT_PATH"

  "$PYTHON_BIN" "$SCRIPT_PATH" \
    --root "$ROOT" \
    --previous-render "$PREV" \
    --outdir "$OUTDIR" \
    --stem "Figure4_panel_E_external_context" \
    | tee "$OUTDIR/run_stdout.txt"

  echo
  echo "=== VERIFY OUTPUTS ==="
  ls -lh "$OUTDIR/panels/Figure4_panel_E_external_context.svg"
  ls -lh "$OUTDIR/panels/Figure4_panel_E_external_context.pdf"
  ls -lh "$OUTDIR/panels/Figure4_panel_E_external_context.transparent.png"
  ls -lh "$OUTDIR/panels/Figure4_panel_E_external_context.preview_white.png"
  ls -lh "$OUTDIR/audit/00_PANEL_E_LAYOUT_FIX_AUDIT.tsv"
  ls -lh "$OUTDIR/audit/09_TRANSPARENCY_AUDIT.tsv"
  ls -lh "$OUTDIR/derived_data/Figure4E_locked_values.tsv"

  echo
  echo "=== PACKAGE ==="
  rm -f "$ARCHIVE"
  tar -czf "$ARCHIVE" -C "$ROOT" "$(basename "$OUTDIR")"

  echo
  echo "=== ARCHIVE CHECK ==="
  ls -lh "$ARCHIVE"

  echo
  echo "READY_TO_RETRIEVE_FIGURE4_PANEL_E_EXTERNAL_CONTEXT"
  echo "OUTDIR=$OUTDIR"
  echo "ARCHIVE=$ARCHIVE"
fi
