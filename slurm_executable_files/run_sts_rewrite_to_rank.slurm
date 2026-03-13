#!/bin/bash
#SBATCH --job-name=sts-rewrite
#SBATCH --partition=gpuA100x4
#SBATCH --account=bfsl-delta-gpu
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=150G
#SBATCH --time=48:00:00
#SBATCH --output=logs/sts-rewrite-%j.out
#SBATCH --error=logs/sts-rewrite-%j.err
#SBATCH --array=1-200

module load miniforge3-python
eval "$(conda shell.bash hook)"
conda activate /work/hdd/bfsl/onimase/env-sts
export HF_HOME=/work/hdd/bfsl/onimase/hf_cache
cd /work/hdd/bfsl/onimase/geobench-sts

# Catalogs for rewrite_to_rank_subsampled (20 catalogs x 10 products = 200 jobs)
CATALOGS=("Apparel" "Automotive Lighting" "Automotive Parts" "Computer Accessories" "Education" "Fishing Gear" "Flooring" "Food" "Footwear" "Golf Clubs" "Handbags" "Health and Beauty" "Jewelry" "Lighting" "Lighting Fixtures" "Motorcycle Accessories" "Party Supplies" "Plumbing Fixtures" "Vitamins & Supplements" "Womens Clothing")

# Calculate catalog index and product index from array task ID
CATALOG_IDX=$(( (SLURM_ARRAY_TASK_ID - 1) / 10 ))
PRODUCT_IDX=$(( (SLURM_ARRAY_TASK_ID - 1) % 10 + 1 ))

CATALOG=${CATALOGS[$CATALOG_IDX]}

export WANDB_MODE=offline
python rank_opt.py \
    --model llama-3.1-8b \
    --dataset rewrite_to_rank_subsampled \
    --catalog "$CATALOG" \
    --target_product_idx $PRODUCT_IDX \
    --num_iter 500 \
    --test_iter 100 \
    --random_order \
    --save_state \
    --results_dir "results/benchmark_results/sts/v1/llama-3.1-8b/rewrite_to_rank_subsampled/$CATALOG/$PRODUCT_IDX"
