#!/bin/bash
#SBATCH --job-name=eval-array
#SBATCH --partition=gpuA100x4
#SBATCH --account=bfsl-delta-gpu
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=20:00:00
#SBATCH --array=0-3
#SBATCH --output=logs/eval-%A_%a.out
#SBATCH --error=logs/eval-%A_%a.err

# 4 evaluation scripts: all datasets
EVAL_SCRIPTS=(
    "experiment.evaluate_cseo"
    "experiment.evaluate_llmrank"
    "experiment.evaluate_rewrite_to_rank"
    "experiment.evaluate_llm_rank_optimizer"
)

EVAL_SCRIPT=${EVAL_SCRIPTS[$SLURM_ARRAY_TASK_ID]}
echo "Running evaluation: ${EVAL_SCRIPT} (task ${SLURM_ARRAY_TASK_ID})"

source ~/miniconda3/bin/activate
conda activate controllable-seo
export HF_HOME=/work/hdd/bfsl/onimase/hf_cache
cd /work/hdd/bfsl/onimase/geobench-stealth

python -m ${EVAL_SCRIPT}
