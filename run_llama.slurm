#!/bin/bash
#SBATCH --job-name=llama-ragroll
#SBATCH --partition=gpuA40x4
#SBATCH --account=bdns-delta-gpu
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=150G
#SBATCH --time=48:00:00
#SBATCH --output=logs/llama-%j.out
#SBATCH --error=logs/llama-%j.err

source ~/miniconda3/bin/activate
conda activate controllable-seo
export HF_HOME=/work/hdd/beaa/onimase/hf_cache
cd /work/hdd/beaa/onimase/controllable-seo-project/geobench

python -m experiment.main --model llama-3.1-8b --dataset ragroll --mode suffix