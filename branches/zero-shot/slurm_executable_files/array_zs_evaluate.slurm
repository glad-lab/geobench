#!/bin/bash
#SBATCH --job-name=zs-eval
#SBATCH --partition=gpu
#SBATCH --account=YOUR_SLURM_ACCOUNT
#SBATCH --nodes=1
#SBATCH --gpus-per-node=a100:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=20:00:00
#SBATCH --array=0-5%1
#SBATCH --output=logs/zs-eval-%A_%a.out
#SBATCH --error=logs/zs-eval-%A_%a.err

EVAL_SCRIPTS=(
    "experiment.evaluate_ragroll"
    "experiment.evaluate_json"
    "experiment.evaluate_cseo"
    "experiment.evaluate_llmrank"
    "experiment.evaluate_rewrite_to_rank"
    "experiment.evaluate_llm_rank_optimizer"
)

EVAL_SCRIPT=${EVAL_SCRIPTS[$SLURM_ARRAY_TASK_ID]}
echo "Running evaluation: ${EVAL_SCRIPT} (task ${SLURM_ARRAY_TASK_ID})"

source /apps/conda/miniforge3/25.11.0-1/etc/profile.d/conda.sh
conda activate /path/to/scratch/geobench/env

export HF_HOME=/path/to/scratch/hf_cache
export OPENBLAS_NUM_THREADS=1
export WANDB_DISABLED=true

cd /path/to/scratch/geobench/geobench-zero-shot
python -m ${EVAL_SCRIPT}
