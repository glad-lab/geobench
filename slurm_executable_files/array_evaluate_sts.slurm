#!/bin/bash
#SBATCH --job-name=eval-sts-array
#SBATCH --partition=gpuA100x4
#SBATCH --account=bfsl-delta-gpu
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=20:00:00
#SBATCH --array=0-3
#SBATCH --output=logs/eval-sts-%A_%a.out
#SBATCH --error=logs/eval-sts-%A_%a.err

# 4 evaluation scripts for all datasets
EVAL_SCRIPTS=(
    "evaluate_sts_cseo"
    "evaluate_sts_llmrank"
    "evaluate_sts_rewrite_to_rank"
    "evaluate_sts_llm_rank_optimizer"
)

EVAL_SCRIPT=${EVAL_SCRIPTS[$SLURM_ARRAY_TASK_ID]}
echo "Running evaluation: ${EVAL_SCRIPT} (task ${SLURM_ARRAY_TASK_ID})"

module load miniforge3-python
eval "$(conda shell.bash hook)"
conda activate /work/hdd/bfsl/onimase/env-sts
export HF_HOME=/work/hdd/bfsl/onimase/hf_cache
cd /work/hdd/bfsl/onimase/geobench-sts

python -m ${EVAL_SCRIPT}
