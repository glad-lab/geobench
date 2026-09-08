#!/usr/bin/env bash
# One-time environment setup for the unified pipeline (run from repo root).
# On CARC this creates the conda env that scripts/slurm/_common.sh expects
# (/home1/<user>/.conda/envs/geobench); elsewhere it falls back to a venv.
set -euo pipefail
cd "$(dirname "$0")/.."
# login-node safety: cap BLAS threads (RLIMIT_NPROC) and ignore ~/.local packages that shadow the env
export OPENBLAS_NUM_THREADS=${OPENBLAS_NUM_THREADS:-4} OMP_NUM_THREADS=${OMP_NUM_THREADS:-4} PYTHONNOUSERSITE=1

if command -v conda >/dev/null 2>&1; then
  source "$(conda info --base)/etc/profile.d/conda.sh"
  conda env list | grep -q "^geobench " || conda create -y -n geobench python=3.11
  conda activate geobench
else
  python -m venv .venv-geobench 2>/dev/null || true
  source .venv-geobench/bin/activate
fi
pip install -U pip
pip install -r requirements-geobench.txt

: "${HF_HOME:=$HOME/.cache/huggingface}"
echo "HF_HOME=$HF_HOME  (export HF_TOKEN for gated models: Llama-3.1, Gemma)"
echo "export OPENAI_API_KEY for gpt-4o-mini; for the DeepSeek attacker also OPENAI_BASE_URL=https://api.deepseek.com"

python -m geobench.data            # write manifests/<dataset>.csv
python -m pytest -q tests || true
