#!/bin/bash
# Submit all cseo per-catalog jobs
for f in $(dirname "$0")/cseo/run_llama_cseo_*.slurm; do
    echo "Submitting $f"
    sbatch "$f"
done
