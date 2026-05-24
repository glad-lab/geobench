#!/bin/bash
#SBATCH --job-name=eval-llm-rank-optimizer
#SBATCH --partition=gpu
#SBATCH --account=YOUR_SLURM_ACCOUNT
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=20:00:00
#SBATCH --output=logs/eval-llm-rank-optimizer-%j.out
#SBATCH --error=logs/eval-llm-rank-optimizer-%j.err

module load conda
eval "$(conda shell.bash hook)"
conda activate /path/to/scratch/geobench/env
export HF_HOME=/path/to/scratch/hf_cache
cd /path/to/scratch/geobench/geobench-stealth

export WANDB_MODE=offline
python -m experiment.evaluate_llm_rank_optimizer
