#!/usr/bin/env bash
set -euo pipefail

RUN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$RUN_DIR"

mkdir -p out logs

echo "JM105 Figure 4B/C polished renderer"
echo "Run dir: $RUN_DIR"
echo "Started: $(date -Is)"
echo "Host: $(hostname)"

if type module >/dev/null 2>&1; then
  module purge || true
  module load fast_python_workshop_cpu/2025.0.0
else
  echo "ERROR: module command not available" >&2
  exit 20
fi

echo "Python after module load:"
which python || true
python --version || true

python - <<'PY'
import sys
import matplotlib
import PIL
print("Python:", sys.executable)
print("matplotlib:", matplotlib.__version__)
print("PIL import OK")
try:
    import scipy
    print("scipy:", scipy.__version__)
except Exception as exc:
    print("scipy unavailable; fallback stats path will be used if needed:", repr(exc))
PY

python -m py_compile render_jm105_fig4bc_polished.py
python render_jm105_fig4bc_polished.py 2>&1 | tee logs/render.log

echo "Finished: $(date -Is)"
