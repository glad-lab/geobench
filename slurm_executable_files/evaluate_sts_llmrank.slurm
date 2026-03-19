#!/bin/bash
#SBATCH --job-name=eval-sts-llmrank
#SBATCH --partition=gpu
#SBATCH --account=YOUR_SLURM_ACCOUNT
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=20:00:00
#SBATCH --output=logs/eval-sts-llmrank-%j.out
#SBATCH --error=logs/eval-sts-llmrank-%j.err

module load conda
eval "$(conda shell.bash hook)"
conda activate /path/to/scratch/geobench/env-sts-sts
export HF_HOME=/path/to/scratch/hf_cache
cd /path/to/work/geobench-sts

export WANDB_MODE=offline
python evaluate_sts_llmrank.py
