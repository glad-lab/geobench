#!/bin/bash
# Test script for SRP experimental suite
# This runs a minimal test to verify everything works before the full suite

echo "=== SRP Experiment Test Started at: $(date) ==="

# Setup environment
source ~/miniconda3/bin/activate
conda activate controllable-seo
cd ~/controllable-seo-project/controllable-seo

# Create test directories
mkdir -p test_results logs

echo "=== Environment Check ==="
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
python -c "import transformers; print(f'Transformers version: {transformers.__version__}')"
python -c "import wandb; print(f'Wandb logged in: {wandb.api.api_key is not None}')"

echo "=== Testing Available Data ==="
echo "Available datasets:"
ls data2/

echo "Available ragroll categories:"
ls data2/ragroll/ | head -10

echo "Available json categories:"
ls data2/json/ 2>/dev/null || echo "No json directory found"

echo "=== Testing Single Experiment ==="
# Test parameters
TEST_DATASET="ragroll"
TEST_CATEGORY="coffee maker"
TEST_TARGET="8"
TEST_MODEL="deepseek-7b"

echo "Testing: Dataset=$TEST_DATASET, Category='$TEST_CATEGORY', Target=$TEST_TARGET"

# Create test result directory
TEST_DIR="test_results/single_test"
mkdir -p "$TEST_DIR"

MAIN_LOG="$TEST_DIR/main.log"
EVAL_LOG="$TEST_DIR/eval.log"
METRICS_FILE="$TEST_DIR/metrics.txt"

echo "=== Running Main Experiment (Test) ==="
timeout 300 python -m experiment.main \
    --dataset "$TEST_DATASET" \
    --catalog "$TEST_CATEGORY" \
    --model "$TEST_MODEL" \
    --mode suffix \
    > "$MAIN_LOG" 2>&1

MAIN_EXIT_CODE=$?
echo "Main experiment exit code: $MAIN_EXIT_CODE"

if [ $MAIN_EXIT_CODE -eq 0 ]; then
    echo "✓ Main experiment completed successfully"
elif [ $MAIN_EXIT_CODE -eq 124 ]; then
    echo "⚠ Main experiment timed out (5 minutes) - this is expected for testing"
else
    echo "✗ Main experiment failed"
fi

echo "=== Checking Main Log Content ==="
if [ -f "$MAIN_LOG" ]; then
    echo "Main log file size: $(wc -l < "$MAIN_LOG") lines"
    echo "Last 10 lines of main log:"
    tail -10 "$MAIN_LOG"
    
    # Check for key indicators
    if grep -q "wandb" "$MAIN_LOG"; then
        echo "✓ Wandb integration detected"
    fi
    
    if grep -q "Training:" "$MAIN_LOG"; then
        echo "✓ Training progress detected"
    fi
    
    if grep -q "Rank=" "$MAIN_LOG"; then
        echo "✓ Rank output detected"
        grep "Rank=" "$MAIN_LOG" | tail -3
    fi
else
    echo "✗ Main log file not created"
fi

echo "=== Testing Evaluation Scripts ==="
# Test evaluation commands (with timeout)
echo "Testing rank/perplexity evaluation..."
timeout 60 python -m experiment.evaluate --job=rank_perplexity > "$EVAL_LOG" 2>&1
EVAL_EXIT_CODE=$?

echo "Evaluation exit code: $EVAL_EXIT_CODE"

if [ -f "$EVAL_LOG" ]; then
    echo "Eval log file size: $(wc -l < "$EVAL_LOG") lines"
    echo "Eval log content preview:"
    head -5 "$EVAL_LOG"
    tail -5 "$EVAL_LOG"
else
    echo "No evaluation log created"
fi
