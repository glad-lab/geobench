#!/bin/bash
#SBATCH --job-name=mistral-llm-rank
#SBATCH --partition=gpuA100x4
#SBATCH --account=bfsl-delta-gpu
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=150G
#SBATCH --time=48:00:00
#SBATCH --output=logs/mistral-llm-rank-%j.out
#SBATCH --error=logs/mistral-llm-rank-%j.err

source ~/miniconda3/bin/activate
conda activate controllable-seo
export HF_HOME=/work/hdd/beaa/onimase/hf_cache
cd /work/hdd/beaa/onimase/controllable-seo-project/geobench

export WANDB_AGENT_MAX_INITIAL_FAILURES=0
python -m experiment.main --model mistral-7b --dataset llm_rank --mode suffix