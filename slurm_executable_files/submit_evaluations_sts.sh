#!/bin/bash
# Submit STS evaluation array (5 datasets evaluated in parallel)
# Run this AFTER all experiment runs have completed.

DIR="$(dirname "$0")"

echo "Submitting STS evaluation array (5 datasets: cseo, llmrank, rewrite_to_rank, ragdoll, llm_rank_optimizer)..."
sbatch "$DIR/array_evaluate_sts.slurm"

echo "Monitor with: squeue -u \$USER"
