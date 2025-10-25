#!/bin/bash
#SBATCH --job-name=deepseek-json
#SBATCH --partition=gpuA40x4
#SBATCH --account=beaa-delta-gpu
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=150G
#SBATCH --time=48:00:00
#SBATCH --output=logs/deepseek-%j.out
#SBATCH --error=logs/deepseek-%j.err

source ~/miniconda3/bin/activate
conda activate controllable-seo
export HF_HOME=/work/hdd/beaa/onimase/hf_cache
cd /work/hdd/beaa/onimase/controllable-seo-project/geobench

python -m experiment.main --model deepseek-7b --dataset json --mode suffix