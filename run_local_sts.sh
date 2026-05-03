#!/bin/bash
# Local runner for STS experiments + evaluations on a single GPU.
# Self-daemonizing: running `bash run_local_sts.sh` detaches via nohup automatically.
# Runs all rank_opt.py jobs sequentially, then runs the evaluation scripts.
# Skips already-finished rank_opt runs and already-evaluated datasets.

set -u

LOG_DIR="/media/volume/geo3/geobench_logs"
mkdir -p "$LOG_DIR"

# ---------------------------------------------------------------
# Self-daemonize: re-exec under nohup & disown the first time.
# Second run (with STS_RUNNER_DAEMONIZED=1) actually does the work.
# ---------------------------------------------------------------
if [ "${STS_RUNNER_DAEMONIZED:-0}" != "1" ]; then
    NOHUP_OUT="$LOG_DIR/nohup.out"
    echo "Launching run_local_sts.sh in the background via nohup..."
    echo "  stdout/stderr -> $NOHUP_OUT"
    echo "  main log      -> $LOG_DIR/run_local_sts.log"
    STS_RUNNER_DAEMONIZED=1 nohup bash "$0" "$@" >> "$NOHUP_OUT" 2>&1 &
    disown
    echo "PID=$!"
    echo "Tail progress with:  tail -f $LOG_DIR/run_local_sts.log"
    exit 0
fi

REPO_DIR="/home/exouser/geobench"
RESULTS_DIR="/media/volume/geo3/geobench_results"
HF_HOME_DIR="/media/volume/geo3/hf_cache"
CONDA_ENV="/media/volume/geo3/conda_envs/env-sts"
MAIN_LOG="$LOG_DIR/run_local_sts.log"
METRICS_DIR="$REPO_DIR/metric/benchmark"

mkdir -p "$RESULTS_DIR" "$METRICS_DIR"

source /home/exouser/miniconda3/etc/profile.d/conda.sh
conda activate "$CONDA_ENV"

export HF_HOME="$HF_HOME_DIR"
export TRANSFORMERS_OFFLINE=0
export OPENBLAS_NUM_THREADS=1
export WANDB_DISABLED=true
export TOKENIZERS_PARALLELISM=false
export CUDA_VISIBLE_DEVICES=0

cd "$REPO_DIR"

echo "============================================================" | tee -a "$MAIN_LOG"
echo "[$(date)] STS local run starting (daemonized pid=$$)"           | tee -a "$MAIN_LOG"
echo "Conda env: $CONDA_ENV"        | tee -a "$MAIN_LOG"
echo "HF cache:  $HF_HOME"          | tee -a "$MAIN_LOG"
echo "Results:   $RESULTS_DIR"      | tee -a "$MAIN_LOG"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader | tee -a "$MAIN_LOG"
echo "============================================================" | tee -a "$MAIN_LOG"

run_one () {
    local DATASET="$1"
    local CATALOG="$2"
    local PRODUCT_IDX="$3"
    local OUT="results/benchmark_results/sts/v1/llama-3.1-8b/$DATASET/$CATALOG/$PRODUCT_IDX"
    local TAG="$DATASET | $CATALOG | idx=$PRODUCT_IDX"

    # Skip if rank.csv shows the 500th iteration was logged (run completed).
    # rank_opt.py keeps state_dict.pth around forever, so presence of that file
    # is NOT a reliable "still running" signal -- check rank.csv tail instead.
    if [ -f "$OUT/rank.csv" ]; then
        local LAST_ITER
        LAST_ITER=$(tail -n 1 "$OUT/rank.csv" | cut -d, -f1)
        if [ "$LAST_ITER" = "500" ]; then
            echo "[$(date)] SKIP (done): $TAG" | tee -a "$MAIN_LOG"
            return 0
        fi
    fi

    echo "[$(date)] RUN  : $TAG" | tee -a "$MAIN_LOG"
    local PER_LOG="$LOG_DIR/run_${DATASET}_${CATALOG// /_}_${PRODUCT_IDX}.log"
    python rank_opt.py \
        --model llama-3.1-8b \
        --dataset "$DATASET" \
        --catalog "$CATALOG" \
        --target_product_idx "$PRODUCT_IDX" \
        --num_iter 500 \
        --test_iter 100 \
        --random_order \
        --save_state \
        --results_dir "$OUT" \
        > "$PER_LOG" 2>&1
    local RC=$?
    if [ $RC -ne 0 ]; then
        echo "[$(date)] FAIL ($RC): $TAG  (see $PER_LOG)" | tee -a "$MAIN_LOG"
    else
        echo "[$(date)] DONE : $TAG" | tee -a "$MAIN_LOG"
    fi
    return $RC
}

run_array () {
    local DATASET="$1"
    shift
    local CATALOGS=("$@")
    echo "" | tee -a "$MAIN_LOG"
    echo "### Dataset: $DATASET (${#CATALOGS[@]} catalogs)" | tee -a "$MAIN_LOG"
    for CATALOG in "${CATALOGS[@]}"; do
        local JSONL="benchmark_data/$DATASET/$CATALOG.jsonl"
        if [ ! -f "$JSONL" ]; then
            echo "[$(date)] MISS (no jsonl): $DATASET | $CATALOG" | tee -a "$MAIN_LOG"
            continue
        fi
        # Count actual products in this catalog instead of hardcoding.
        local N
        N=$(wc -l < "$JSONL")
        for PRODUCT_IDX in $(seq 1 "$N"); do
            run_one "$DATASET" "$CATALOG" "$PRODUCT_IDX" || true
        done
    done
}

# ---------- Experiment 1: cseo_subsampled (6 catalogs x 10 = 60) ----------
CSEO=("books" "debate" "news" "retail" "videogames" "web")
run_array "cseo_subsampled" "${CSEO[@]}"

# ---------- Experiment 2: llm_rank_subsampled (11 catalogs x 10 = 110) ----------
LLMRANK=("action" "adventure" "appliances" "automotive" "baby" "books" "cameras" "children's" "coffee_machines" "comedy" "computers")
run_array "llm_rank_subsampled" "${LLMRANK[@]}"

# ---------- Experiment 3: rewrite_to_rank_subsampled (20 catalogs x 10 = 200) ----------
REWRITE=("Apparel" "Automotive Lighting" "Automotive Parts" "Computer Accessories" "Education" "Fishing Gear" "Flooring" "Food" "Footwear" "Golf Clubs" "Handbags" "Health and Beauty" "Jewelry" "Lighting" "Lighting Fixtures" "Motorcycle Accessories" "Party Supplies" "Plumbing Fixtures" "Vitamins & Supplements" "Womens Clothing")
run_array "rewrite_to_rank_subsampled" "${REWRITE[@]}"

# ---------- Experiment 4: llm_rank_optimizer_subsampled (4 catalogs x 10 = 40) ----------
LLMOPT=("books" "cameras" "coffee_machines" "election_articles")
run_array "llm_rank_optimizer_subsampled" "${LLMOPT[@]}"

# ---------- Experiment 5: sts_subsampled (3 catalogs x 10 = 30) ----------
STSDATA=("books" "cameras" "coffee_machines")
run_array "sts_subsampled" "${STSDATA[@]}"

# ---------- Experiment 6: ragroll_subsampled (21 catalogs x 8 = 168) ----------
RAGROLL=("air compressor" "air purifier" "automatic garden watering system" "barbecue grill" "beard trimmer" "blender" "coffee maker" "computer monitor" "computer power supply" "cordless drill" "curling iron" "dishwasher" "electric sander" "electric toothbrush" "eyeshadow" "fascia gun" "hair dryer" "hair straightener" "hammock" "hedge trimmer" "laptop")
run_array "ragroll_subsampled" "${RAGROLL[@]}"

echo "" | tee -a "$MAIN_LOG"
echo "============================================================" | tee -a "$MAIN_LOG"
echo "[$(date)] All rank_opt runs complete. Starting evaluations." | tee -a "$MAIN_LOG"
echo "============================================================" | tee -a "$MAIN_LOG"

# ---------- Evaluations ----------
# Each entry: eval_script_module_name  dataset_name_used_for_csv
EVAL_SCRIPTS=(
    "evaluate_sts_cseo:cseo_subsampled"
    "evaluate_sts_llmrank:llm_rank_subsampled"
    "evaluate_sts_rewrite_to_rank:rewrite_to_rank_subsampled"
    "evaluate_sts_llm_rank_optimizer:llm_rank_optimizer_subsampled"
    "evaluate_sts_stsdata:sts_subsampled"
    "evaluate_sts_ragroll:ragroll_subsampled"
)

for PAIR in "${EVAL_SCRIPTS[@]}"; do
    EVAL="${PAIR%%:*}"
    DS="${PAIR##*:}"
    CSV="$METRICS_DIR/sts_${DS}_metrics.csv"

    # Skip if already evaluated: CSV has header + at least one data row.
    if [ -f "$CSV" ]; then
        LINES=$(wc -l < "$CSV" 2>/dev/null || echo 0)
        if [ "$LINES" -ge 2 ]; then
            echo "[$(date)] EVAL SKIP (exists, $LINES lines): $EVAL  [$CSV]" | tee -a "$MAIN_LOG"
            continue
        fi
    fi

    echo "[$(date)] EVAL: $EVAL" | tee -a "$MAIN_LOG"
    python -m "$EVAL" > "$LOG_DIR/eval_${EVAL}.log" 2>&1
    RC=$?
    if [ $RC -ne 0 ]; then
        echo "[$(date)] EVAL FAIL ($RC): $EVAL  (see $LOG_DIR/eval_${EVAL}.log)" | tee -a "$MAIN_LOG"
    else
        echo "[$(date)] EVAL DONE: $EVAL" | tee -a "$MAIN_LOG"
    fi
done

echo "[$(date)] ALL DONE" | tee -a "$MAIN_LOG"
