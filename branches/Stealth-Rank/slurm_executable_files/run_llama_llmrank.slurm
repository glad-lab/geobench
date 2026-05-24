#!/bin/bash
#SBATCH --job-name=llama-llmrank
#SBATCH --partition=gpu
#SBATCH --account=YOUR_SLURM_ACCOUNT
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=150G
#SBATCH --time=48:00:00
#SBATCH --output=logs/llama-llmrank-%j.out
#SBATCH --error=logs/llama-llmrank-%j.err

module load conda
eval "$(conda shell.bash hook)"
conda activate /path/to/scratch/geobench/env
export HF_HOME=/path/to/scratch/hf_cache
cd /path/to/scratch/geobench/geobench-stealth

export WANDB_AGENT_MAX_INITIAL_FAILURES=0
export WANDB_MODE=offline
python -m experiment.main --model llama-3.1-8b --dataset llmrank_subsampled --mode suffix
