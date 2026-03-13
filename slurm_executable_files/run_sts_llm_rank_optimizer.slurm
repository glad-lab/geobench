#!/bin/bash
#SBATCH --job-name=sts-llm-rank-opt
#SBATCH --partition=gpuA100x4
#SBATCH --account=bfsl-delta-gpu
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=150G
#SBATCH --time=48:00:00
#SBATCH --output=logs/sts-llm-rank-opt-%j.out
#SBATCH --error=logs/sts-llm-rank-opt-%j.err
#SBATCH --array=1-40

source ~/miniconda3/bin/activate
conda activate controllable-seo
export HF_HOME=/work/hdd/bfsl/onimase/hf_cache
cd /work/hdd/bfsl/onimase/geobench-sts

# Catalogs for llm_rank_optimizer_subsampled (4 catalogs x 10 products = 40 jobs)
CATALOGS=("books" "cameras" "coffee_machines" "election_articles")

# Calculate catalog index and product index from array task ID
CATALOG_IDX=$(( (SLURM_ARRAY_TASK_ID - 1) / 10 ))
PRODUCT_IDX=$(( (SLURM_ARRAY_TASK_ID - 1) % 10 + 1 ))

CATALOG=${CATALOGS[$CATALOG_IDX]}

python rank_opt.py \
    --model llama-3.1-8b \
    --dataset llm_rank_optimizer_subsampled \
    --catalog "$CATALOG" \
    --target_product_idx $PRODUCT_IDX \
    --num_iter 500 \
    --test_iter 100 \
    --random_order \
    --save_state \
    --results_dir results/benchmark_results/sts/v1/llama-3.1-8b/llm_rank_optimizer_subsampled/$CATALOG/$PRODUCT_IDX
