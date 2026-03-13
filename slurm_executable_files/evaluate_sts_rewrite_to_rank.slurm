#!/bin/bash
#SBATCH --job-name=eval-sts-rewrite
#SBATCH --partition=gpuA100x4
#SBATCH --account=bfsl-delta-gpu
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=20:00:00
#SBATCH --output=logs/eval-sts-rewrite-%j.out
#SBATCH --error=logs/eval-sts-rewrite-%j.err

module load miniforge3-python
eval "$(conda shell.bash hook)"
conda activate /path/to/work/env-sts
export HF_HOME=/path/to/work/hf_cache
cd /path/to/work/geobench-sts

export WANDB_MODE=offline
python evaluate_sts_rewrite_to_rank.py
