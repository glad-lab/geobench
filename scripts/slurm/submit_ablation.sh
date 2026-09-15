#!/bin/bash
# Attacker / rewriter-strength ablation with open models (reviewer wK3H W2).
# Needs Qwen2.5-1.5B cached: bash scripts/11_prefetch_models.sh (login node, once).
source "$(dirname "$0")/_common.sh"
bash scripts/slurm/submit_attacks.sh ablation
