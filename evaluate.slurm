#!/bin/bash
#SBATCH --job-name=eval-benchmark-metrics
#SBATCH --partition=gpuA40x4
#SBATCH --account=bdns-delta-gpu
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=04:00:00
#SBATCH --output=logs/eval-benchmark-metrics-%j.out
#SBATCH --error=logs/eval-benchmark-metrics-%j.err

source ~/miniconda3/bin/activate
conda activate controllable-seo
export HF_HOME=/work/hdd/beaa/onimase/hf_cache
cd /work/hdd/beaa/onimase/controllable-seo-project/geobench

python -m experiment.evaluate_benchmark