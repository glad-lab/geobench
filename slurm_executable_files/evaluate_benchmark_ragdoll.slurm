#!/bin/bash
#SBATCH --job-name=eval-benchmark-ragdoll
#SBATCH --partition=cpu-preempt
#SBATCH --account=bfsl-delta-cpu
#SBATCH --nodes=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=20:00:00
#SBATCH --output=logs/eval-benchmark-ragdoll-%j.out
#SBATCH --error=logs/eval-benchmark-ragdoll-%j.err

source ~/miniconda3/bin/activate
conda activate controllable-seo
export HF_HOME=/work/hdd/beaa/onimase/hf_cache
cd /work/hdd/beaa/onimase/controllable-seo-project/geobench

python -m experiment.evaluate_benchmark_ragdoll