#!/bin/bash
#SBATCH --job-name=eval-rewrite
#SBATCH --partition=gpu
#SBATCH --account=yzhao010_1245
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=20:00:00
#SBATCH --output=logs/eval-rewrite-%j.out
#SBATCH --error=logs/eval-rewrite-%j.err

module load conda
eval "$(conda shell.bash hook)"
conda activate /scratch1/nimase/geobench/env
export HF_HOME=/scratch1/nimase/hf_cache
cd /scratch1/nimase/geobench/geobench-stealth

export WANDB_MODE=offline
python -m experiment.evaluate_rewrite_to_rank
