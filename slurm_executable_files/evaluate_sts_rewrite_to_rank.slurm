#!/bin/bash
#SBATCH --job-name=eval-sts-rewrite
#SBATCH --partition=gpu
#SBATCH --account=yzhao010_1245
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=20:00:00
#SBATCH --output=logs/eval-sts-rewrite-%j.out
#SBATCH --error=logs/eval-sts-rewrite-%j.err

module load conda
eval "$(conda shell.bash hook)"
conda activate /scratch1/nimase/geobench/env-sts-sts
export HF_HOME=/scratch1/nimase/hf_cache
cd /work/hdd/bfsl/onimase/geobench-sts

export WANDB_MODE=offline
python evaluate_sts_rewrite_to_rank.py
