#!/bin/bash
#SBATCH --job-name=eval-sts-cseo
#SBATCH --partition=gpu
#SBATCH --account=YOUR_SLURM_ACCOUNT
#SBATCH --gpus-per-node=a100:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=20:00:00
#SBATCH --output=logs/eval-sts-cseo-%j.out
#SBATCH --error=logs/eval-sts-cseo-%j.err

source /apps/conda/miniforge3/25.11.0-1/etc/profile.d/conda.sh
conda activate /path/to/scratch/geobench/env-sts

export HF_HOME=/path/to/scratch/hf_cache
export OPENBLAS_NUM_THREADS=1
export WANDB_DISABLED=true

cd /path/to/scratch/geobench/geobench-sts
python evaluate_sts_cseo.py