#!/bin/bash
#SBATCH --job-name=eval-sts-array
#SBATCH --partition=gpu
#SBATCH --account=yzhao010_1245
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=20:00:00
#SBATCH --array=0-3
#SBATCH --output=logs/eval-sts-%A_%a.out
#SBATCH --error=logs/eval-sts-%A_%a.err

EVAL_SCRIPTS=(
    "evaluate_sts_cseo"
    "evaluate_sts_llmrank"
    "evaluate_sts_rewrite_to_rank"
    "evaluate_sts_llm_rank_optimizer"
)

EVAL_SCRIPT=${EVAL_SCRIPTS[$SLURM_ARRAY_TASK_ID]}
echo "Running evaluation: ${EVAL_SCRIPT} (task ${SLURM_ARRAY_TASK_ID})"

source /apps/conda/miniforge3/25.11.0-1/etc/profile.d/conda.sh
conda activate /scratch1/nimase/geobench/env-sts

export HF_HOME=/scratch1/nimase/hf_cache
export OPENBLAS_NUM_THREADS=1
export WANDB_DISABLED=true

cd /scratch1/nimase/geobench/geobench-sts
python -m ${EVAL_SCRIPT}