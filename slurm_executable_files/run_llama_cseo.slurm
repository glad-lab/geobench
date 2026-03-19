#!/bin/bash
#SBATCH --job-name=llama-cseo
#SBATCH --partition=gpu
#SBATCH --account=yzhao010_1245
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=150G
#SBATCH --time=48:00:00
#SBATCH --output=logs/llama-cseo-%j.out
#SBATCH --error=logs/llama-cseo-%j.err

module load conda
eval "$(conda shell.bash hook)"
conda activate /scratch1/nimase/geobench/env
export HF_HOME=/scratch1/nimase/hf_cache
cd /scratch1/nimase/geobench/geobench-stealth

export WANDB_AGENT_MAX_INITIAL_FAILURES=0
export WANDB_MODE=offline
python -m experiment.main --model llama-3.1-8b --dataset cseo_subsampled --mode suffix
