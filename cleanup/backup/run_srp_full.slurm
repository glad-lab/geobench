#!/bin/bash
#SBATCH --job-name=srp-full
#SBATCH --partition=gpuA40x4
#SBATCH --account=beaa-delta-gpu
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=150G
#SBATCH --time=12:00:00
#SBATCH --output=logs/srp-full-%j.out
#SBATCH --error=logs/srp-full-%j.err

echo "=== Optimized SRP Full Suite Started at: $(date) ==="
echo "Job ID: $SLURM_JOB_ID"

source ~/miniconda3/bin/activate
conda activate controllable-seo
cd ~/controllable-seo-project/controllable-seo

mkdir -p logs results

MODEL="deepseek-7b"
DATASETS=("ragroll" "json")
MODE="suffix"

# OPTIMIZED: Fewer targets, strategic selection
TARGET_INDICES=(1 5 8 10)  # Reduced from 10 targets to 4

# Key categories only
RAGROLL_CATEGORIES=("coffee maker" "laptop" "smartphone" "dishwasher")
JSON_CATEGORIES=("coffee_machines" "books" "cameras")

echo "=== Optimized Scope: Ragroll(4×4) + JSON(3×4) = 28 experiments ==="

run_optimized_experiment() {
    local dataset=$1
    local category=$2  
    local target_idx=$3
    
    echo "Running: Dataset=$dataset, Category='$category', Target=$target_idx"
    
    RESULT_DIR="results/optimized/${dataset}/${category//[ ]/_}/target_${target_idx}"
    mkdir -p "$RESULT_DIR"
    
    MAIN_LOG="$RESULT_DIR/main.log"
    EVAL_LOG="$RESULT_DIR/eval.log"
    METRICS_FILE="$RESULT_DIR/metrics.txt"
    
    # SPEED OPTIMIZATION: Create optimized config
    OPT_CONFIG="configs/optimized_suffix.yaml"
    cp configs/suffix.yaml "$OPT_CONFIG"
    
    python << EOF
import yaml
with open('$OPT_CONFIG', 'r') as f:
    config = yaml.safe_load(f)

# Speed optimizations while maintaining quality
config['parameters']['num_iter']['value'] = 1000     # Reduce from 2000
config['parameters']['test_iter']['value'] = 100     # Keep same  
config['parameters']['lr']['value'] = 0.05           # Increase from 0.03
config['parameters']['batch_size']['value'] = 3      # Reduce from 5
config['parameters']['temperature']['value'] = 0.05  # Reduce for faster convergence

# Update noise schedule for faster convergence
config['parameters']['iter_steps']['value'] = [0, 25, 100, 250, 750]
config['parameters']['noise_stds']['value'] = [0.05, 0.025, 0.01, 0.005, 0.001]

with open('$OPT_CONFIG', 'w') as f:
    yaml.dump(config, f)
EOF
    
    # Run main experiment
    python -m experiment.main \
        --dataset "$dataset" \
        --catalog "$category" \
        --model "$MODEL" \
        --mode "$MODE" \
        > "$MAIN_LOG" 2>&1
    
    # Quick evaluation
    python -m experiment.evaluate --job=rank_perplexity > "$EVAL_LOG" 2>&1
    python -m experiment.evaluate --job=bad_word >> "$EVAL_LOG" 2>&1
    
    # Extract metrics
    echo "Dataset: $dataset" > "$METRICS_FILE"
    echo "Category: $category" >> "$METRICS_FILE"
    echo "Target_Index: $target_idx" >> "$METRICS_FILE"
    echo "Model: $MODEL" >> "$METRICS_FILE"
    echo "Timestamp: $(date)" >> "$METRICS_FILE"
    
    # Extract rank
    if grep -q "Rank=" "$MAIN_LOG"; then
        FINAL_RANK=$(grep "Rank=" "$MAIN_LOG" | tail -1 | sed 's/.*Rank=\([0-9]*\).*/\1/')
        echo "Final_Rank: $FINAL_RANK" >> "$METRICS_FILE"
    else
        echo "Final_Rank: NOT_FOUND" >> "$METRICS_FILE"
    fi
    
    # Extract perplexity
    if [ -f "$EVAL_LOG" ] && grep -q -i "perplexity" "$EVAL_LOG"; then
        PERPLEXITY=$(grep -i "perplexity" "$EVAL_LOG" | head -1)
        echo "Perplexity: $PERPLEXITY" >> "$METRICS_FILE"
    else
        echo "Perplexity: NOT_FOUND" >> "$METRICS_FILE"
    fi
    
    # Extract bad word ratio  
    if [ -f "$EVAL_LOG" ] && grep -q -i "bad.*word\|ratio" "$EVAL_LOG"; then
        BAD_WORD_RATIO=$(grep -i "bad.*word\|ratio" "$EVAL_LOG" | head -1)
        echo "Bad_Word_Ratio: $BAD_WORD_RATIO" >> "$METRICS_FILE"
    else
        echo "Bad_Word_Ratio: NOT_FOUND" >> "$METRICS_FILE"
    fi
    
    # Success indicator
    if [[ "$FINAL_RANK" == "1" ]]; then
        echo "Success: TRUE" >> "$METRICS_FILE"
    else
        echo "Success: FALSE" >> "$METRICS_FILE"
    fi
    
    # Clean up
    rm -f "$OPT_CONFIG"
}

# Main execution loop
TOTAL_EXPERIMENTS=0

for dataset in "${DATASETS[@]}"; do
    if [[ "$dataset" == "ragroll" ]]; then
        CATEGORIES=("${RAGROLL_CATEGORIES[@]}")
    elif [[ "$dataset" == "json" ]]; then
        CATEGORIES=("${JSON_CATEGORIES[@]}")
    else
        continue
    fi
    
    for category in "${CATEGORIES[@]}"; do
        for target_idx in "${TARGET_INDICES[@]}"; do
            run_optimized_experiment "$dataset" "$category" "$target_idx"
            TOTAL_EXPERIMENTS=$((TOTAL_EXPERIMENTS + 1))
            echo "Completed $TOTAL_EXPERIMENTS experiments"
            sleep 10
        done
    done
done

# Aggregate results
echo "=== Aggregating Results ==="
python << 'EOF'
import pandas as pd
from pathlib import Path

results = []
for metrics_file in Path("results/optimized").rglob("metrics.txt"):
    data = {}
    with open(metrics_file, 'r') as f:
        for line in f:
            if ':' in line and not line.startswith('==='):
                key, value = line.split(':', 1)
                data[key.strip()] = value.strip()
    if data:
        results.append(data)

if results:
    df = pd.DataFrame(results)
    df.to_csv("results/optimized_results.csv", index=False)
    
    # Summary stats
    if 'Final_Rank' in df.columns:
        df['Final_Rank'] = pd.to_numeric(df['Final_Rank'], errors='coerce')
        summary = df.groupby(['Dataset', 'Category'])['Final_Rank'].agg(['mean', 'count']).round(2)
        print(f"Saved {len(results)} results")
        print("\nRank Summary by Category:")
        print(summary)
    
    success_rate = (df['Success'] == 'TRUE').mean() if 'Success' in df.columns else 0
    print(f"\nOverall Success Rate (Rank=1): {success_rate:.2%}")
EOF

echo "=== Optimized Suite Completed at: $(date) ==="
echo "Total experiments: $TOTAL_EXPERIMENTS"
echo "Results: results/optimized_results.csv"
