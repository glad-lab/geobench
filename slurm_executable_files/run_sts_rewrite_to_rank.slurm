#!/bin/bash
#SBATCH --job-name=sts-rewrite
#SBATCH --partition=gpu
#SBATCH --account=yzhao010_1245
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=150G
#SBATCH --time=48:00:00
#SBATCH --output=logs/sts-rewrite-%j.out
#SBATCH --error=logs/sts-rewrite-%j.err
#SBATCH --array=1-200

source /apps/conda/miniforge3/25.11.0-1/etc/profile.d/conda.sh
conda activate /scratch1/nimase/geobench/env-sts

export HF_HOME=/scratch1/nimase/hf_cache
export OPENBLAS_NUM_THREADS=1
export WANDB_DISABLED=true

cd /scratch1/nimase/geobench/geobench-sts

CATALOGS=("Apparel" "Automotive Lighting" "Automotive Parts" "Computer Accessories" "Education" "Fishing Gear" "Flooring" "Food" "Footwear" "Golf Clubs" "Handbags" "Health and Beauty" "Jewelry" "Lighting" "Lighting Fixtures" "Motorcycle Accessories" "Party Supplies" "Plumbing Fixtures" "Vitamins & Supplements" "Womens Clothing")
CATALOG_IDX=$(( (SLURM_ARRAY_TASK_ID - 1) / 10 ))
PRODUCT_IDX=$(( (SLURM_ARRAY_TASK_ID - 1) % 10 + 1 ))
CATALOG=${CATALOGS[$CATALOG_IDX]}

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