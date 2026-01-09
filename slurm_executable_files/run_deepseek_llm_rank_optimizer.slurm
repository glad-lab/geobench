#!/bin/bash
#SBATCH --job-name=deepseek-llm-rank-optimizer
#SBATCH --partition=gpuA100x4
#SBATCH --account=bfsl-delta-gpu
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=150G
#SBATCH --time=36:00:00
#SBATCH --output=logs/deepseek-llm-rank-optimizer-%j.out
#SBATCH --error=logs/deepseek-llm-rank-optimizer-%j.err

source ~/miniconda3/bin/activate
conda activate controllable-seo
export HF_HOME=/work/hdd/beaa/onimase/hf_cache
cd /work/hdd/beaa/onimase/controllable-seo-project/geobench

export WANDB_AGENT_MAX_INITIAL_FAILURES=0
python -m experiment.main_llm_rank_optimizer --model deepseek-7b --dataset llm_rank_optimizer_subsampled --mode suffix