#!/bin/bash
#SBATCH --job-name=eval-llm-rank-optimizer
#SBATCH --partition=gpuA100x4
#SBATCH --account=bfsl-delta-gpu
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=20:00:00
#SBATCH --output=logs/eval-llm-rank-optimizer-%j.out
#SBATCH --error=logs/eval-llm-rank-optimizer-%j.err

module load miniforge3-python
eval "$(conda shell.bash hook)"
conda activate /work/hdd/bfsl/onimase/env
export HF_HOME=/work/hdd/bfsl/onimase/hf_cache
cd /work/hdd/bfsl/onimase/geobench-stealth

python -m experiment.evaluate_llm_rank_optimizer
