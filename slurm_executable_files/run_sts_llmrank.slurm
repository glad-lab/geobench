#!/bin/bash
#SBATCH --job-name=sts-llmrank
#SBATCH --partition=gpu
#SBATCH --account=yzhao010_1245
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=150G
#SBATCH --time=48:00:00
#SBATCH --output=logs/sts-llmrank-%j.out
#SBATCH --error=logs/sts-llmrank-%j.err
#SBATCH --array=1-110

source /apps/conda/miniforge3/25.11.0-1/etc/profile.d/conda.sh
conda activate /scratch1/nimase/geobench/env-sts

export HF_HOME=/scratch1/nimase/hf_cache
export OPENBLAS_NUM_THREADS=1
export WANDB_DISABLED=true

cd /scratch1/nimase/geobench/geobench-sts

CATALOGS=("action" "adventure" "appliances" "automotive" "baby" "books" "cameras" "children's" "coffee_machines" "comedy" "computers")
CATALOG_IDX=$(( (SLURM_ARRAY_TASK_ID - 1) / 10 ))
PRODUCT_IDX=$(( (SLURM_ARRAY_TASK_ID - 1) % 10 + 1 ))
CATALOG=${CATALOGS[$CATALOG_IDX]}

python rank_opt.py \
    --model llama-3.1-8b \
    --dataset llm_rank_subsampled \
    --catalog "$CATALOG" \
    --target_product_idx $PRODUCT_IDX \
    --num_iter 500 \
    --test_iter 100 \
    --random_order \
    --save_state \
    --results_dir results/benchmark_results/sts/v1/llama-3.1-8b/llm_rank_subsampled/$CATALOG/$PRODUCT_IDX