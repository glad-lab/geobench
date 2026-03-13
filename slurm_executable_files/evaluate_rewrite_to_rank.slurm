#!/bin/bash
#SBATCH --job-name=eval-rewrite
#SBATCH --partition=gpuA100x4
#SBATCH --account=bfsl-delta-gpu
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=20:00:00
#SBATCH --output=logs/eval-rewrite-%j.out
#SBATCH --error=logs/eval-rewrite-%j.err

module load miniforge3-python
eval "$(conda shell.bash hook)"
conda activate /work/hdd/bfsl/onimase/env
export HF_HOME=/work/hdd/bfsl/onimase/hf_cache
cd /work/hdd/bfsl/onimase/geobench-stealth

export WANDB_MODE=offline
python -m experiment.evaluate_rewrite_to_rank
