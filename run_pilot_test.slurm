#!/bin/bash
#SBATCH --job-name=srp-pilot
#SBATCH --partition=gpuA40x4-interactive
#SBATCH --account=beaa-delta-gpu
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=80G
#SBATCH --time=01:00:00
#SBATCH --output=logs/pilot-%j.out
#SBATCH --error=logs/pilot-%j.err

echo "=== PILOT TEST at $(date) ==="

source ~/miniconda3/bin/activate
conda activate controllable-seo
export HF_HOME=/work/hdd/beaa/onimase/hf_cache
cd /work/hdd/beaa/onimase/controllable-seo-project/geobench

mkdir -p logs results_new/pilot

MODELS=("deepseek-7b" "mistral-7b" "llama-3.1-8b" "vicuna-7b")

for model in "${MODELS[@]}"; do
    echo "=== Testing $model at $(date) ==="
    
    python -m experiment.main \
        --config configs/pilot.yaml \
        --dataset "json" \
        --catalog "coffee_machines" \
        --model "$model" \
        --mode "suffix" \
        --num_iter 20 \
        > results_new/pilot/${model}.log 2>&1
    
    if grep -q "model.*loaded\|Model loaded" results_new/pilot/${model}.log; then
        echo "✓ $model loaded successfully"
    else
        echo "✗ $model failed - check results_new/pilot/${model}.log"
        tail -20 results_new/pilot/${model}.log
    fi
done

echo "=== ALL PILOTS COMPLETE at $(date) ==="