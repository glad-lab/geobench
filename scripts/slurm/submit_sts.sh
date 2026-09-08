#!/bin/bash
# STS (white-box) against a ranker: one array job per dataset, one task per
# (catalog, target) pair.  MODEL keys: llama-3.1-8b mistral-7b vicuna-7b qwen2.5-7b
#   bash scripts/slurm/submit_sts.sh llama-3.1-8b cseo_subsampled       # e.g. rerun the failed news/retail rows
#   bash scripts/slurm/submit_sts.sh mistral-7b                         # all datasets
source "$(dirname "$0")/_common.sh"
cd "$REPO" && mkdir -p logs
MODEL=${1:?usage: submit_sts.sh MODEL [dataset ...]}; shift
DATASETS=${@:-"ragroll_subsampled sts_subsampled rewrite_to_rank_subsampled llm_rank_optimizer_subsampled cseo_subsampled"}

for ds in $DATASETS; do
  NCAT=$(ls branches/STS/benchmark_data/${ds}/*.jsonl 2>/dev/null | wc -l)
  [[ $NCAT -gt 0 ]] || { echo "no benchmark_data/${ds}; skipping"; continue; }
  NTASK=$((NCAT * 10))
  echo "Submitting STS model=${MODEL} dataset=${ds} (${NCAT} catalogs x 10 targets) ..."
  sbatch <<SBEOF
#!/bin/bash
#SBATCH --job-name=geo_sts_${MODEL}_${ds}
#SBATCH --account=${ACCOUNT}
#SBATCH --partition=${PARTITION}
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --gres=gpu:${GPU_TYPE}:1
#SBATCH --time=12:00:00
#SBATCH --array=1-${NTASK}%20
#SBATCH --output=logs/sts_${MODEL}_${ds}_%A_%a.out
#SBATCH --error=logs/sts_${MODEL}_${ds}_%A_%a.err

export CUDA_VISIBLE_DEVICES=0
$(common_env "$CONDA_BIN_STS")
cd branches/STS
mapfile -t CATALOGS < <(ls benchmark_data/${ds}/*.jsonl | xargs -n1 basename | sed 's/\\.jsonl\$//' | sort)
CATALOG_IDX=\$(( (SLURM_ARRAY_TASK_ID - 1) / 10 ))
PRODUCT_IDX=\$(( (SLURM_ARRAY_TASK_ID - 1) % 10 + 1 ))
CATALOG=\${CATALOGS[\$CATALOG_IDX]}
NPROD=\$(wc -l < "benchmark_data/${ds}/\$CATALOG.jsonl")
[[ \$PRODUCT_IDX -le \$NPROD ]] || { echo "catalog \$CATALOG has \$NPROD items; skip \$PRODUCT_IDX"; exit 0; }
python rank_opt.py --model ${MODEL} --dataset ${ds} --catalog "\$CATALOG" --target_product_idx \$PRODUCT_IDX \\
    --num_iter 500 --test_iter 100 --random_order --save_state \\
    --results_dir results/benchmark_results/sts/v1/${MODEL}/${ds}/\$CATALOG/\$PRODUCT_IDX
SBEOF
done
echo "After the arrays finish:  python -m geobench.collect sts --model ${MODEL} --out results/unified/instances/sts__opt-${MODEL}.csv"
