#!/bin/bash
#SBATCH --job-name=zs-rtr
#SBATCH --partition=gpu
#SBATCH --account=yzhao010_1245
#SBATCH --nodes=1
#SBATCH --gpus-per-node=a100:1
#SBATCH --cpus-per-task=16
#SBATCH --mem=150G
#SBATCH --time=24:00:00
#SBATCH --array=0-19
#SBATCH --output=logs/zs-rtr-%A_%a.out
#SBATCH --error=logs/zs-rtr-%A_%a.err

CATALOGS=(
    "Apparel" "Automotive Lighting" "Automotive Parts" "Computer Accessories"
    "Education" "Fishing Gear" "Flooring" "Food" "Footwear" "Golf Clubs"
    "Handbags" "Health and Beauty" "Jewelry" "Lighting" "Lighting Fixtures"
    "Motorcycle Accessories" "Party Supplies" "Plumbing Fixtures"
    "Vitamins & Supplements" "Womens Clothing"
)

CATALOG=${CATALOGS[$SLURM_ARRAY_TASK_ID]}
echo "Running catalog: ${CATALOG} (task ${SLURM_ARRAY_TASK_ID})"

source /apps/conda/miniforge3/25.11.0-1/etc/profile.d/conda.sh
conda activate /scratch1/nimase/geobench/env

export HF_HOME=/scratch1/nimase/hf_cache
export OPENBLAS_NUM_THREADS=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export WANDB_DISABLED=true

cd /scratch1/nimase/geobench/geobench-zero-shot
python -m experiment.zero_shot_baseline --model llama-3.1-8b --dataset rewrite_to_rank_subsampled --catalog "${CATALOG}"
