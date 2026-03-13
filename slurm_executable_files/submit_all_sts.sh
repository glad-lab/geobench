#!/bin/bash
# Submit all STS experiment array jobs
# SLURM automatically manages scheduling — runs as many in parallel
# as your account allows, queues the rest, and starts them as slots free up.

DIR="$(dirname "$0")"

echo "Submitting cseo array (6 catalogs x 10 products = 60 jobs)..."
sbatch "$DIR/run_sts_cseo.slurm"

echo "Submitting llmrank array (11 catalogs x 10 products = 110 jobs)..."
sbatch "$DIR/run_sts_llmrank.slurm"

echo "Submitting rewrite_to_rank array (20 catalogs x 10 products = 200 jobs)..."
sbatch "$DIR/run_sts_rewrite_to_rank.slurm"

echo "Submitting llm_rank_optimizer array (4 catalogs x 10 products = 40 jobs)..."
sbatch "$DIR/run_sts_llm_rank_optimizer.slurm"

echo ""
echo "Total: 410 array tasks submitted across 4 array jobs."
echo "Monitor with: squeue -u \$USER"
