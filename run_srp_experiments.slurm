#!/bin/bash
#SBATCH --job-name=srp-exp
#SBATCH --partition=gpuA40x4
#SBATCH --account=beaa-delta-gpu
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=150G
#SBATCH --time=24:00:00
#SBATCH --output=logs/srp-%j.out
#SBATCH --error=logs/srp-%j.err

# ===== CONFIGURATION =====
MODELS=("deepseek-7b" "mistral-7b")
DATASETS=("json" "ragroll")

declare -A CATEGORIES
CATEGORIES[json]="coffee_machines books cameras"
CATEGORIES[ragroll]="coffee_maker laptop smartphone dishwasher"

TARGET_INDICES=(1 5 8 10)

# ===== SETUP =====
echo "=== Experiments Started: $(date) ==="
echo "Models: ${MODELS[@]}"
echo "Datasets: ${DATASETS[@]}"

source ~/miniconda3/bin/activate
conda activate controllable-seo
export HF_HOME=/work/hdd/beaa/onimase/hf_cache
cd /work/hdd/beaa/onimase/controllable-seo-project/geobench

mkdir -p logs results_new/full

# ===== RUN EXPERIMENTS =====
for model in "${MODELS[@]}"; do
  for dataset in "${DATASETS[@]}"; do
    echo "=== Running $model on $dataset ==="
    
    for category in ${CATEGORIES[$dataset]}; do
      for target_idx in "${TARGET_INDICES[@]}"; do
        
        RESULT_DIR="results_new/full/${model}_${dataset}/${category}/target_${target_idx}"
        mkdir -p "$RESULT_DIR"
        
        python -m experiment.main \
          --dataset "$dataset" \
          --catalog "$category" \
          --model "$model" \
          --mode "suffix" \
          > "$RESULT_DIR/main.log" 2>&1
        
        python -m experiment.evaluate --job=rank_perplexity > "$RESULT_DIR/eval.log" 2>&1
        python -m experiment.evaluate --job=bad_word >> "$RESULT_DIR/eval.log" 2>&1
        
      done
    done
  done
done

echo "=== Complete: $(date) ==="