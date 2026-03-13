#!/bin/bash
#SBATCH --job-name=eval-sts-cseo
#SBATCH --partition=gpuA100x4
#SBATCH --account=bfsl-delta-gpu
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=20:00:00
#SBATCH --output=logs/eval-sts-cseo-%j.out
#SBATCH --error=logs/eval-sts-cseo-%j.err

source ~/miniconda3/bin/activate
conda activate controllable-seo
export HF_HOME=/work/hdd/bfsl/onimase/hf_cache
cd /work/hdd/bfsl/onimase/geobench-sts

python evaluate_sts_cseo.py
