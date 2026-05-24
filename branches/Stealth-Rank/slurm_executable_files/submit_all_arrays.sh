#!/bin/bash
# Submit all job arrays for running experiments
# SLURM automatically manages scheduling — runs as many in parallel
# as your account allows, queues the rest, and starts them as slots free up.

DIR="$(dirname "$0")"

echo "Submitting cseo array (6 catalogs)..."
sbatch "$DIR/array_cseo.slurm"

echo "Submitting llmrank array (9 catalogs)..."
sbatch "$DIR/array_llmrank.slurm"

echo "Submitting rewrite_to_rank array (20 catalogs)..."
sbatch "$DIR/array_rewrite_to_rank.slurm"

echo ""
echo "Total: 35 array tasks submitted across 3 array jobs."
echo "Monitor with: squeue -u \$USER"
