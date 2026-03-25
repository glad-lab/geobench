#!/bin/bash
#SBATCH --job-name=llmrank-array
#SBATCH --partition=gpu
#SBATCH --account=YOUR_SLURM_ACCOUNT
#SBATCH --nodes=1
#SBATCH --gpus-per-node=a100:1
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

source /apps/conda/miniforge3/25.11.0-1/etc/profile.d/conda.sh
conda activate /path/to/scratch/geobench/env

export HF_HOME=/path/to/scratch/hf_cache
export OPENBLAS_NUM_THREADS=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export WANDB_DISABLED=true

cd /path/to/scratch/geobench/geobench-stealth
python -m experiment.run_no_wandb --model llama-3.1-8b --dataset llmrank_subsampled --mode suffix --catalog "${CATALOG}"