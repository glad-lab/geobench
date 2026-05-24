#!/bin/bash
#SBATCH --job-name=llama-llm-rank-optimizer
#SBATCH --partition=gpu
#SBATCH --account=yzhao010_1245
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=150G
#SBATCH --time=36:00:00
#SBATCH --output=logs/llama-llm-rank-optimizer-%j.out
#SBATCH --error=logs/llama-llm-rank-optimizer-%j.err

module load conda
eval "$(conda shell.bash hook)"
conda activate /scratch1/nimase/geobench/env
export HF_HOME=/scratch1/nimase/hf_cache
cd /scratch1/nimase/geobench/geobench-stealth

export WANDB_AGENT_MAX_INITIAL_FAILURES=0
export WANDB_MODE=offline
python -m experiment.main_llm_rank_optimizer --model llama-3.1-8b --dataset llm_rank_optimizer_subsampled --mode suffix