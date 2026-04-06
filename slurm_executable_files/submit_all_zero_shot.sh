#!/bin/bash
# Submit all zero-shot baseline experiments

DIR="$(dirname "$0")"

echo "Submitting zero-shot ragroll (50 catalogs)..."
sbatch "$DIR/array_zs_ragroll.slurm"

echo "Submitting zero-shot json/STSData (3 catalogs)..."
sbatch "$DIR/array_zs_json.slurm"

echo "Submitting zero-shot cseo (6 catalogs)..."
sbatch "$DIR/array_zs_cseo.slurm"

echo "Submitting zero-shot llmrank (11 catalogs)..."
sbatch "$DIR/array_zs_llmrank.slurm"

echo "Submitting zero-shot rewrite_to_rank (20 catalogs)..."
sbatch "$DIR/array_zs_rewrite_to_rank.slurm"

echo "Submitting zero-shot llm_rank_optimizer (4 catalogs)..."
sbatch "$DIR/array_zs_llm_rank_optimizer.slurm"

echo ""
echo "Total: 94 array tasks across 6 array jobs."
echo "Monitor with: squeue -u \$USER"
