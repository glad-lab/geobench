#!/bin/bash
#SBATCH --job-name=llmrank-array
#SBATCH --partition=gpuA100x4
#SBATCH --account=bfsl-delta-gpu
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=150G
#SBATCH --time=48:00:00
#SBATCH --array=0-8
#SBATCH --output=logs/llmrank-%A_%a.out
#SBATCH --error=logs/llmrank-%A_%a.err

# 9 catalogs (remaining + appliances rerun)
CATALOGS=(
    "appliances"
    "automotive"
    "baby"
    "books"
    "cameras"
    "children's"
    "coffee_machines"
    "comedy"
    "computers"
)

CATALOG=${CATALOGS[$SLURM_ARRAY_TASK_ID]}
echo "Running catalog: ${CATALOG} (task ${SLURM_ARRAY_TASK_ID})"

module load miniforge3-python
eval "$(conda shell.bash hook)"
conda activate /work/hdd/bfsl/onimase/env
export HF_HOME=/work/hdd/bfsl/onimase/hf_cache
cd /work/hdd/bfsl/onimase/geobench-stealth

export WANDB_AGENT_MAX_INITIAL_FAILURES=0
export WANDB_MODE=offline
python -m experiment.main --model llama-3.1-8b --dataset llmrank_subsampled --mode suffix --catalog "${CATALOG}"
