#!/bin/bash
#SBATCH --job-name=eval-ragroll
#SBATCH --partition=gpu
#SBATCH --account=YOUR_SLURM_ACCOUNT
#SBATCH --gpus-per-node=a100:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=20:00:00
#SBATCH --output=logs/eval-ragroll-%j.out
#SBATCH --error=logs/eval-ragroll-%j.err

source /apps/conda/miniforge3/25.11.0-1/etc/profile.d/conda.sh
conda activate /path/to/scratch/geobench/env

export HF_HOME=/path/to/scratch/hf_cache
export OPENBLAS_NUM_THREADS=1
export WANDB_DISABLED=true

cd /path/to/scratch/geobench/geobench-stealth
python -m experiment.evaluate_ragroll