#!/bin/bash
# Submit all rewrite_to_rank per-catalog jobs
for f in $(dirname "$0")/rewrite_to_rank/run_llama_rtr_*.slurm; do
    echo "Submitting $f"
    sbatch "$f"
done
