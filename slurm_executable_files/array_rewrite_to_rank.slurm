#!/bin/bash
#SBATCH --job-name=rtr-array
#SBATCH --partition=gpu
#SBATCH --account=yzhao010_1245
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=150G
#SBATCH --time=48:00:00
#SBATCH --array=0-19
#SBATCH --output=logs/rtr-%A_%a.out
#SBATCH --error=logs/rtr-%A_%a.err

CATALOGS=(
    "Apparel"
    "Automotive Lighting"
    "Automotive Parts"
    "Computer Accessories"
    "Education"
    "Fishing Gear"
    "Flooring"
    "Food"
    "Footwear"
    "Golf Clubs"
    "Handbags"
    "Health and Beauty"
    "Jewelry"
    "Lighting"
    "Lighting Fixtures"
    "Motorcycle Accessories"
    "Party Supplies"
    "Plumbing Fixtures"
    "Vitamins & Supplements"
    "Womens Clothing"
)

CATALOG=${CATALOGS[$SLURM_ARRAY_TASK_ID]}
echo "Running catalog: ${CATALOG} (task ${SLURM_ARRAY_TASK_ID})"

source /apps/conda/miniforge3/25.11.0-1/etc/profile.d/conda.sh
conda activate /scratch1/nimase/geobench/env

echo "Python path: $(which python)"
echo "Conda env: $CONDA_PREFIX"

export HF_HOME=/scratch1/nimase/hf_cache
export OPENBLAS_NUM_THREADS=1
export WANDB_DISABLED=true

cd /scratch1/nimase/geobench/geobench-stealth
python -m experiment.run_no_wandb --model llama-3.1-8b --dataset rewrite_to_rank_subsampled --mode suffix --catalog "${CATALOG}"