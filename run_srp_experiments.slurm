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
MODELS=("deepseek-7b")
DATASETS=("json")

declare -A CATEGORIES
CATEGORIES[json]="coffee_machines books cameras"
CATEGORIES[ragroll]="coffee_maker laptop smartphone dishwasher"

TARGET_INDICES=(1 2 3 4 5 6 7 8 9 10)

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
        
        echo "  Processing: $category target_$target_idx"
        RESULT_DIR="results_new/full/${model}_${dataset}/${category}/target_${target_idx}"
        mkdir -p "$RESULT_DIR"
        
        # Update config for this specific target
        sed -i "s/values: \[.*\]  # \[1,2,3/values: [$target_idx]  # [1,2,3/" configs/suffix.yaml
        
        python -m experiment.main \
          --dataset "$dataset" \
          --catalog "$category" \
          --model "$model" \
          --mode "suffix" \
          > "$RESULT_DIR/main.log" 2>&1
        
        echo "  Completed: $category target_$target_idx at $(date)"
      done
    done
  done
done

echo "=== Complete: $(date) ==="