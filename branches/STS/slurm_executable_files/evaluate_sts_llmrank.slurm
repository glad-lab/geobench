#!/bin/bash
#SBATCH --job-name=eval-sts-llmrank
#SBATCH --partition=gpu
#SBATCH --account=yzhao010_1245
#SBATCH --gpus-per-node=a100:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=20:00:00
#SBATCH --output=logs/eval-sts-llmrank-%j.out
#SBATCH --error=logs/eval-sts-llmrank-%j.err

source /apps/conda/miniforge3/25.11.0-1/etc/profile.d/conda.sh
conda activate /scratch1/nimase/geobench/env-sts

export HF_HOME=/scratch1/nimase/hf_cache
export OPENBLAS_NUM_THREADS=1
export WANDB_DISABLED=true

cd /scratch1/nimase/geobench/geobench-sts
python evaluate_sts_llmrank.py