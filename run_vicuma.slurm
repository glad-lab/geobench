#!/bin/bash
#SBATCH --job-name=vicuna-json
#SBATCH --partition=gpuA40x4
#SBATCH --account=beaa-delta-gpu
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=150G
#SBATCH --time=40:00:00
#SBATCH --output=logs/vicuna-%j.out
#SBATCH --error=logs/vicuna-%j.err

MODELS=("vicuna-7b")
DATASETS=("json")
declare -A CATEGORIES
CATEGORIES[json]="coffee_machines books cameras"
TARGET_INDICES=(1 2 3 4 5 6 7 8 9 10)

source ~/miniconda3/bin/activate
conda activate controllable-seo
export HF_HOME=/work/hdd/beaa/onimase/hf_cache
cd /work/hdd/beaa/onimase/controllable-seo-project/geobench

mkdir -p logs results_new/full

for model in "${MODELS[@]}"; do
  for dataset in "${DATASETS[@]}"; do
    for category in ${CATEGORIES[$dataset]}; do
      for target_idx in "${TARGET_INDICES[@]}"; do
        echo "$(date): $model $category target_$target_idx"
        RESULT_DIR="results_new/full/${model}_${dataset}/${category}/target_${target_idx}"
        mkdir -p "$RESULT_DIR"
        
        sed -i '/target_product_idx:/!b;n;s/values: \[.*\]/values: ['"$target_idx"']/' configs/suffix_${model}.yaml
        
        python -m experiment.main \
          --dataset "$dataset" \
          --catalog "$category" \
          --model "$model" \
          --mode "suffix" \
          > "$RESULT_DIR/main.log" 2>&1
      done
    done
  done
done