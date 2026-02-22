#!/bin/bash
#SBATCH --job-name=eval-llmrank
#SBATCH --partition=gpuA100x4
#SBATCH --account=bfsl-delta-gpu
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=20:00:00
#SBATCH --output=logs/eval-llmrank-%j.out
#SBATCH --error=logs/eval-llmrank-%j.err

source ~/miniconda3/bin/activate
conda activate controllable-seo
export HF_HOME=/work/hdd/beaa/onimase/hf_cache
cd /work/hdd/beaa/onimase/controllable-seo-project/geobench

python -m experiment.evaluate_llmrank
