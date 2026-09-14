#!/bin/bash
# Re-optimise StealthRank (white-box) against a ranker, under the patched
# (Llama-3 / ChatML) prompt: one job per dataset.
# MODEL keys: llama-3.1-8b mistral-7b vicuna-7b deepseek-7b qwen2.5-7b qwen2.5-14b
# Dataset dir names (branch convention): ragroll json rewrite_to_rank_subsampled llm_rank_optimizer_subsampled cseo_subsampled
#   bash scripts/slurm/submit_stealthrank.sh llama-3.1-8b json cseo_subsampled
#   bash scripts/slurm/submit_stealthrank.sh mistral-7b                       # all five datasets
# Outputs go to a NEW result root (…/suffix/v2_unified) so the submission-era
# llama results under …/suffix/v1 are neither reused nor overwritten
# (run_no_wandb skips a target whose result file already exists).
source "$(dirname "$0")/_common.sh"
cd "$REPO" && mkdir -p logs
MODEL=${1:?usage: submit_stealthrank.sh MODEL [dataset ...]}; shift
DATASETS=${@:-"ragroll json rewrite_to_rank_subsampled llm_rank_optimizer_subsampled cseo_subsampled"}
RESULT_DIR="results_new/benchmark_results/suffix/v2_unified"

# branch dataset dir -> geobench dataset key (for collect)
declare -A DSKEY=([ragroll]=ragroll [json]=stsdata [rewrite_to_rank_subsampled]=rewrite_to_rank
                  [llm_rank_optimizer_subsampled]=llm_rank_optimizer [cseo_subsampled]=cseo)

for ds in $DATASETS; do
  key=${DSKEY[$ds]:?unknown dataset dir $ds}
  echo "Submitting StealthRank model=${MODEL} dataset=${ds} ..."
  sbatch <<SBEOF
#!/bin/bash
#SBATCH --job-name=geo_sr_${MODEL}_${ds}
#SBATCH --account=${ACCOUNT}
#SBATCH --partition=${PARTITION}
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=120G
#SBATCH --gres=gpu:${GPU_TYPE}:1
#SBATCH --time=48:00:00
#SBATCH --output=logs/sr_${MODEL}_${ds}_%j.out
#SBATCH --error=logs/sr_${MODEL}_${ds}_%j.err

export CUDA_VISIBLE_DEVICES=0
$(common_env "$CONDA_BIN_STEALTH")
cd branches/Stealth-Rank
# pick the config run_no_wandb would pick, but redirect result_dir to the v2 root
label=${ds%_subsampled}
for cand in configs/suffix_${MODEL}_\${label}.yaml configs/suffix_llama-3.1-8b_\${label}.yaml configs/suffix.yaml; do
  [[ -f \$cand ]] && { SRC=\$cand; break; }
done
CFG=configs/_v2_${MODEL}_${ds}.yaml
sed -e 's#^\(\s*value:\s*\)"results_new/[^"]*"#\1"${RESULT_DIR}"#' "\$SRC" > "\$CFG"
grep -q "${RESULT_DIR}" "\$CFG" || { echo "result_dir substitution failed in \$SRC"; exit 1; }
echo "config: \$SRC -> \$CFG"
for f in benchmark_data/${ds}/*.jsonl data2/${ds}/*.jsonl; do
  [[ -f "\$f" ]] || continue
  CAT=\$(basename "\$f" .jsonl)
  python -m experiment.run_no_wandb --model ${MODEL} --dataset ${ds} --mode suffix --catalog "\$CAT" --config "\$CFG"
done
cd "$REPO"
export PATH=$CONDA_BIN:\$PATH
python -m geobench.collect stealthrank --model ${MODEL} --datasets ${key} \\
    --root branches/Stealth-Rank/${RESULT_DIR} \\
    --out results/unified/instances/stealthrank__opt-${MODEL}-unified-${key}.csv
SBEOF
done
echo "When done, evaluate the new files:  RANKERS=${MODEL} bash scripts/slurm/submit_eval.sh"
