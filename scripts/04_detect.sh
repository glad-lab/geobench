#!/usr/bin/env bash
# Step 4: detectability + relevance signals over the instances (inference only).
set -euo pipefail
cd "$(dirname "$0")/.."
# login-node safety: cap BLAS threads (RLIMIT_NPROC) and ignore ~/.local packages that shadow the env
export OPENBLAS_NUM_THREADS=${OPENBLAS_NUM_THREADS:-4} OMP_NUM_THREADS=${OMP_NUM_THREADS:-4} PYTHONNOUSERSITE=1
source .venv-geobench/bin/activate 2>/dev/null || { command -v conda >/dev/null && source "$(conda info --base)/etc/profile.d/conda.sh" && conda activate geobench; } || true
JUDGE=${JUDGE:-Qwen/Qwen2.5-7B-Instruct}      # must differ from the ranker under test
INST=(results/unified/instances/*.csv)

python -m geobench.detect judge  --instances "${INST[@]}" --judge "$JUDGE"
python -m geobench.detect judge-summary --judge "$JUDGE" --fpr 0.05
python -m geobench.detect drift  --instances "${INST[@]}" --embed BAAI/bge-large-en-v1.5
python -m geobench.detect rerank --instances "${INST[@]}" --reranker BAAI/bge-reranker-v2-m3
python -m geobench.stats --ranker bge-reranker-v2-m3      # NRG under a non-generative reranker
