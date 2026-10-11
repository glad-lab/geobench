#!/usr/bin/env bash
# Step 2: (re)generate the inference-only attack families with the unified
# runners.  These are the cheap ones; gradient attacks stay in their branches
# (see scripts/slurm/*).  Usage: bash scripts/02_generate_attacks.sh [ablation]
set -euo pipefail
cd "$(dirname "$0")/.."
# login-node safety: cap BLAS threads (RLIMIT_NPROC) and ignore ~/.local packages that shadow the env
export OPENBLAS_NUM_THREADS=${OPENBLAS_NUM_THREADS:-4} OMP_NUM_THREADS=${OMP_NUM_THREADS:-4} PYTHONNOUSERSITE=1
source .venv-geobench/bin/activate 2>/dev/null || { command -v conda >/dev/null && source "$(conda info --base)/etc/profile.d/conda.sh" && conda activate geobench; } || true
export TOKENIZERS_PARALLELISM=false

# --- Zero-Shot, attacker = target ranker (paper setting) ---------------------
python -m geobench.attacks.zero_shot --attacker meta-llama/Meta-Llama-3.1-8B-Instruct

# --- C-SEO white-hat rewrites, GPT-4o-mini rewriter (paper setting) ----------
python -m geobench.attacks.cseo_rewrite --rewriter gpt-4o-mini

# --- TAP, DeepSeek-R1 attacker (paper setting; needs DeepSeek/OpenAI-compatible key)
#     OPENAI_BASE_URL=https://api.deepseek.com OPENAI_API_KEY=...
python -m geobench.attacks.tap --ranker llama-3.1-8b --attacker api:deepseek-reasoner --tag llama-3.1-8b

if [[ "${1:-}" == "ablation" ]]; then
  # --- Attacker-strength ablation (reviewer wK3H W2) --------------------------
  python -m geobench.attacks.zero_shot   --attacker gpt-4o-mini                 --tag att-gpt4omini
  python -m geobench.attacks.zero_shot   --attacker Qwen/Qwen2.5-1.5B-Instruct   --tag att-qwen1.5b
  python -m geobench.attacks.cseo_rewrite --rewriter Qwen/Qwen2.5-7B-Instruct    --tag rw-qwen7b \
         --methods authoritative content_improvement llm_guidance
  python -m geobench.attacks.tap --ranker llama-3.1-8b --attacker meta-llama/Meta-Llama-3.1-8B-Instruct --tag att-llama8b --datasets cseo stsdata
fi
