#!/bin/bash
# Stage 3 = all three white-box attacks re-optimised against MODEL under the unified prompt.
#   bash scripts/slurm/submit_stage3.sh llama-3.1-8b
source "$(dirname "$0")/_common.sh"
MODEL=${1:?usage: submit_stage3.sh MODEL}
for env in "$CONDA_BIN_STEALTH" "$CONDA_BIN_STS"; do
  "$env/python" -c "import torch, transformers" 2>/dev/null || { echo "env $env not usable; run: bash scripts/10_branch_envs.sh"; exit 1; }
done
[[ -d "$REPO/branches/RAF/data2/u_ragroll" ]] || { echo "branch data missing; run: python scripts/prepare_branch_data.py"; exit 1; }
bash scripts/slurm/submit_stealthrank.sh "$MODEL"
bash scripts/slurm/submit_raf.sh "$MODEL"
bash scripts/slurm/submit_sts.sh "$MODEL"
squeue -u "$USER" -o "%.10i %.32j %.8T %.10M %.4D %R" | head -20
