#!/bin/bash
#SBATCH --job-name=llmrank-array
#SBATCH --partition=gpu
#SBATCH --account=yzhao010_1245
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

module load conda
eval "$(conda shell.bash hook)"
conda activate /scratch1/nimase/geobench/env
export HF_HOME=/scratch1/nimase/hf_cache
cd /scratch1/nimase/geobench/geobench-stealth

export WANDB_AGENT_MAX_INITIAL_FAILURES=0
export WANDB_DISABLED=true
python -m experiment.main --model llama-3.1-8b --dataset llmrank_subsampled --mode suffix --catalog "${CATALOG}"