#!/bin/bash
#SBATCH --job-name=llama-llmrank
#SBATCH --partition=gpuA100x4
#SBATCH --account=bfsl-delta-gpu
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=150G
#SBATCH --time=48:00:00
#SBATCH --output=logs/llama-llmrank-%j.out
#SBATCH --error=logs/llama-llmrank-%j.err

source ~/miniconda3/bin/activate
conda activate controllable-seo
export HF_HOME=/work/hdd/bfsl/onimase/hf_cache
cd /work/hdd/bfsl/onimase/geobench-stealth

export WANDB_AGENT_MAX_INITIAL_FAILURES=0
python -m experiment.main --model llama-3.1-8b --dataset llmrank_subsampled --mode suffix
