#!/bin/bash
#SBATCH --job-name=eval-sts-llmrankopt
#SBATCH --partition=gpuA100x4
#SBATCH --account=bfsl-delta-gpu
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=20:00:00
#SBATCH --output=logs/eval-sts-llmrankopt-%j.out
#SBATCH --error=logs/eval-sts-llmrankopt-%j.err

module load miniforge3-python
eval "$(conda shell.bash hook)"
conda activate /work/hdd/bfsl/onimase/env-sts
export HF_HOME=/work/hdd/bfsl/onimase/hf_cache
cd /work/hdd/bfsl/onimase/geobench-sts

export WANDB_MODE=offline
python evaluate_sts_llm_rank_optimizer.py
