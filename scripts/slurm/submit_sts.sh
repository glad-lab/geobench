#!/bin/bash
# STS (white-box) against a ranker: one array job per dataset, one task per
# catalog (the task loops over the catalog's <=10 targets; nlp_hiprio caps
# submitted jobs per user at ~500 and every array task counts).  MODEL keys: llama-3.1-8b mistral-7b vicuna-7b qwen2.5-7b qwen2.5-14b
# Dataset names are fixed by rank_opt.py: ragroll_subsampled sts_subsampled rewrite_to_rank_subsampled llm_rank_optimizer_subsampled cseo_subsampled
# (scripts/prepare_branch_data.py fills them with the manifest datasets, incl. all 50 Ragroll categories).
#   bash scripts/slurm/submit_sts.sh llama-3.1-8b                          # all datasets
#   bash scripts/slurm/submit_sts.sh llama-3.1-8b cseo_subsampled
source "$(dirname "$0")/_common.sh"
cd "$REPO" && mkdir -p logs
MODEL=${1:?usage: submit_sts.sh MODEL [dataset ...]}; shift
DATASETS=${@:-"ragroll_subsampled sts_subsampled rewrite_to_rank_subsampled llm_rank_optimizer_subsampled cseo_subsampled"}

# branches/STS/results is a dangling symlink to an old volume -> make it a real dir
if [[ -L branches/STS/results ]]; then rm -f branches/STS/results; fi
mkdir -p branches/STS/results

for ds in $DATASETS; do
  NCAT=$(ls branches/STS/benchmark_data/${ds}/*.jsonl 2>/dev/null | wc -l)
  [[ $NCAT -gt 0 ]] || { echo "no benchmark_data/${ds}; run scripts/10_branch_envs.sh"; continue; }
  echo "Submitting STS model=${MODEL} dataset=${ds} (${NCAT} catalogs, one task each) ..."
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
#SBATCH --time=${TIME}
#SBATCH --array=0-$((NCAT-1))
#SBATCH --output=logs/sts_${MODEL}_${ds}_%A_%a.out
#SBATCH --error=logs/sts_${MODEL}_${ds}_%A_%a.err

export CUDA_VISIBLE_DEVICES=0
$(common_env "$CONDA_BIN_STS")
cd branches/STS
mapfile -t CATALOGS < <(cd "benchmark_data/${ds}" && for f in *.jsonl; do echo "\${f%.jsonl}"; done | sort)   # names contain spaces
CATALOG=\${CATALOGS[\$SLURM_ARRAY_TASK_ID]}; [[ -n "\$CATALOG" ]] || { echo "no catalog for task \$SLURM_ARRAY_TASK_ID"; exit 1; }
NPROD=\$(wc -l < "benchmark_data/${ds}/\$CATALOG.jsonl")
for PRODUCT_IDX in \$(seq 1 \$NPROD); do
  OUT=results/benchmark_results/sts/v1/${MODEL}/${ds}/\$CATALOG/\$PRODUCT_IDX
  [[ -f \$OUT/sts.txt ]] && { echo "exists: \$OUT"; continue; }
  echo "=== \$CATALOG target \$PRODUCT_IDX / \$NPROD  \$(date)"
  python rank_opt.py --model ${MODEL} --dataset ${ds} --catalog "\$CATALOG" --target_product_idx \$PRODUCT_IDX \\
      --num_iter 500 --test_iter 100 --random_order --save_state --results_dir "\$OUT" || echo "FAILED target \$PRODUCT_IDX"
done
SBEOF
done
echo "When all arrays finish:  bash scripts/slurm/submit_collect_whitebox.sh ${MODEL}"
