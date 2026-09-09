#!/usr/bin/env bash
# Sourced only by API launchers; GPU/CARC defaults remain in slurm/_common.sh.
export REPO="${REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
[[ -f "$REPO/geobench/config.py" ]] || { echo "Invalid geobench REPO: $REPO" >&2; exit 1; }
if [[ -z "${PYTHON_BIN:-}" ]]; then
  if [[ -n "${CONDA_BIN:-}" ]]; then
    PYTHON_BIN="$CONDA_BIN/python"
  elif [[ -x "$REPO/.venv-geobench/bin/python" ]]; then
    PYTHON_BIN="$REPO/.venv-geobench/bin/python"
  elif [[ -x /opt/anaconda3/bin/python ]]; then
    PYTHON_BIN=/opt/anaconda3/bin/python
  else
    PYTHON_BIN=$(command -v python3)
  fi
fi
[[ -x "$PYTHON_BIN" ]] || { echo "Invalid PYTHON_BIN: $PYTHON_BIN" >&2; exit 1; }
export PYTHON_BIN
export GEOBENCH_API_PROVIDER="${GEOBENCH_API_PROVIDER:-blockrun}"
export GEOBENCH_RESULTS="${GEOBENCH_RESULTS:-$REPO/results/unified}"
export OPENBLAS_NUM_THREADS="${OPENBLAS_NUM_THREADS:-4}" OMP_NUM_THREADS="${OMP_NUM_THREADS:-4}"
export PYTHONUNBUFFERED=1 PYTHONNOUSERSITE=1
cd "$REPO"
