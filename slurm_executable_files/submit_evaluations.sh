#!/bin/bash
# Submit evaluation array (5 datasets evaluated in parallel)
# Run this AFTER all experiment runs have completed.

DIR="$(dirname "$0")"

echo "Submitting evaluation array (4 datasets: cseo, llmrank, rewrite_to_rank, llm_rank_optimizer)..."
sbatch "$DIR/array_evaluate.slurm"

echo "Monitor with: squeue -u \$USER"
