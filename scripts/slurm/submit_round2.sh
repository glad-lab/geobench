#!/bin/bash
# Round-2 submission (everything still needed for the resubmission draft, one call):
#   1. evaluate the 11 GPT-4o-mini-generated instance sets on llama / qwen2.5-14b / mistral
#   2. detectability (judge / drift / reranker) over all instance sets
#   3. TAP with open attackers (llama-8b self-attack, qwen2.5-14b)
#   4. StealthRank re-optimised under the unified prompt on the two small datasets
#      (STSData = "json", C-SEO) -> the "true white-box" sanity row; submitted only
#      if the Stealth-Rank branch env imports cleanly.
#   bash scripts/slurm/submit_round2.sh
source "$(dirname "$0")/_common.sh"
cd "$REPO" && mkdir -p logs

echo "== 1/4 evaluation on open rankers";  bash scripts/slurm/submit_eval.sh
echo "== 2/4 detectability";               bash scripts/slurm/submit_detect.sh
echo "== 3/4 TAP (open attackers)";        bash scripts/slurm/submit_attacks.sh

echo "== 4/4 StealthRank mini re-optimisation (STSData + C-SEO, llama-3.1-8b)"
if "$CONDA_BIN_STEALTH/python" -c "import torch, transformers, wandb, yaml" 2>/dev/null; then
  bash scripts/slurm/submit_stealthrank.sh llama-3.1-8b json cseo_subsampled
else
  echo "   SKIPPED: $CONDA_BIN_STEALTH is missing torch/transformers/wandb/yaml."
  echo "   To enable: conda create -y -p ${CONDA_BIN_STEALTH%/bin} python=3.11 && ${CONDA_BIN_STEALTH}/pip install -r branches/Stealth-Rank/requirements.txt"
fi
echo; squeue -u "$USER" -o "%.10i %.28j %.8T %.10M %.6D %R"
