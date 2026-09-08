#!/usr/bin/env bash
# Step 3: score every instances CSV against one ranker with the unified
# protocol.  Usage: bash scripts/03_evaluate.sh <ranker-key> [K]
#   ranker keys: see geobench/config.py RANKERS (llama-3.1-8b qwen2.5-7b mistral-7b gpt-4o-mini ...)
# PPL-R is ranker-independent, so it is computed once (with the first ranker)
# and skipped for the others via --no-ppl.
set -euo pipefail
cd "$(dirname "$0")/.."
# login-node safety: cap BLAS threads (RLIMIT_NPROC) and ignore ~/.local packages that shadow the env
export OPENBLAS_NUM_THREADS=${OPENBLAS_NUM_THREADS:-4} OMP_NUM_THREADS=${OMP_NUM_THREADS:-4} PYTHONNOUSERSITE=1
source .venv-geobench/bin/activate 2>/dev/null || { command -v conda >/dev/null && source "$(conda info --base)/etc/profile.d/conda.sh" && conda activate geobench; } || true
RANKER=${1:-llama-3.1-8b}
K=${2:-10}
PPLFLAG=""
[[ "$RANKER" != "llama-3.1-8b" ]] && PPLFLAG="--no-ppl"

python -m geobench.evaluate --ranker "$RANKER" --K "$K" $PPLFLAG \
       --instances results/unified/instances/*.csv
python -m geobench.stats --ranker "$RANKER"
