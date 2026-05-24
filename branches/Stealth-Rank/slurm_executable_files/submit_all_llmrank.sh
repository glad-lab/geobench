#!/bin/bash
# Submit all llmrank per-catalog jobs
for f in $(dirname "$0")/llmrank/run_llama_llmrank_*.slurm; do
    echo "Submitting $f"
    sbatch "$f"
done
