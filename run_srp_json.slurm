#!/bin/bash
#SBATCH --job-name=srp-json
#SBATCH --partition=gpuA40x4
#SBATCH --account=beaa-delta-gpu
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=150G
#SBATCH --time=24:00:00
#SBATCH --output=logs/srp-json-%j.out
#SBATCH --error=logs/srp-json-%j.err

echo "=== SRP JSON Dataset Started at: $(date) ==="
echo "Job ID: $SLURM_JOB_ID"

source ~/miniconda3/bin/activate
conda activate controllable-seo
cd ~/controllable-seo-project/controllable-seo

mkdir -p logs results

MODEL="deepseek-7b"
DATASET="json"
MODE="suffix"

TARGET_INDICES=(1 5 8 10)
JSON_CATEGORIES=("coffee_machines" "books" "cameras")

echo "=== JSON: 3 categories × 4 targets = 12 experiments ==="

run_json_experiment() {
    local category=$1  
    local target_idx=$2
   
    echo "Running: Dataset=$DATASET, Category='$category', Target=$target_idx"
   
    RESULT_DIR="results/json_split/${category//[ ]/_}/target_${target_idx}"
    mkdir -p "$RESULT_DIR"
   
    MAIN_LOG="$RESULT_DIR/main.log"
    EVAL_LOG="$RESULT_DIR/eval.log"
    METRICS_FILE="$RESULT_DIR/metrics.txt"
   
    # Create optimized config
    OPT_CONFIG="configs/json_config.yaml"
    cp configs/suffix.yaml "$OPT_CONFIG"
   
    python << EOF
import yaml
with open('$OPT_CONFIG', 'r') as f:
    config = yaml.safe_load(f)

config['wandb']['project'] = 'controllable-seo-deepseek7b-json'

# Speed optimizations while maintaining quality
config['parameters']['num_iter']['value'] = 1000    
config['parameters']['test_iter']['value'] = 100      
config['parameters']['lr']['value'] = 0.05          
config['parameters']['batch_size']['value'] = 3      
config['parameters']['temperature']['value'] = 0.05  

# Update noise schedule for faster convergence
config['parameters']['iter_steps']['value'] = [0, 25, 100, 250, 750]
config['parameters']['noise_stds']['value'] = [0.05, 0.025, 0.01, 0.005, 0.001]

with open('$OPT_CONFIG', 'w') as f:
    yaml.dump(config, f)
EOF
   
    # Run main experiment
    python -m experiment.main \
        --dataset "$DATASET" \
        --catalog "$category" \
        --model "$MODEL" \
        --mode "$MODE" \
        > "$MAIN_LOG" 2>&1
   
    # Run evaluation
    python -m experiment.evaluate --job=rank_perplexity > "$EVAL_LOG" 2>&1
    python -m experiment.evaluate --job=bad_word >> "$EVAL_LOG" 2>&1
   
    # Extract metrics
    echo "Dataset: $DATASET" > "$METRICS_FILE"
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

for category in "${JSON_CATEGORIES[@]}"; do
    for target_idx in "${TARGET_INDICES[@]}"; do
        run_json_experiment "$category" "$target_idx"
        TOTAL_EXPERIMENTS=$((TOTAL_EXPERIMENTS + 1))
        echo "Completed $TOTAL_EXPERIMENTS of 12 JSON experiments"
        sleep 10
    done
done

# Aggregate JSON results
echo "=== Aggregating JSON Results ==="
python << 'EOF'
import pandas as pd
from pathlib import Path

results = []
for metrics_file in Path("results/json_split").rglob("metrics.txt"):
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
    df.to_csv("results/json_results.csv", index=False)
   
    # Summary stats
    if 'Final_Rank' in df.columns:
        df['Final_Rank'] = pd.to_numeric(df['Final_Rank'], errors='coerce')
        summary = df.groupby(['Category'])['Final_Rank'].agg(['mean', 'count']).round(2)
        print(f"Saved {len(results)} JSON results")
        print("\nJSON Rank Summary by Category:")
        print(summary)
   
    success_rate = (df['Success'] == 'TRUE').mean() if 'Success' in df.columns else 0
    print(f"\nJSON Success Rate (Rank=1): {success_rate:.2%}")
EOF

echo "=== JSON Dataset Completed at: $(date) ==="
echo "Total experiments: $TOTAL_EXPERIMENTS"
echo "Results: results/json_results.csv"
