#!/bin/bash
# Re-optimise StealthRank (white-box) against a ranker under the patched
# (Llama-3 / ChatML) prompt.  One ARRAY job per dataset, one task per catalog
# (8-10 targets, a few GPU-hours), so nothing hits the wall-clock limit.
# MODEL keys: llama-3.1-8b mistral-7b vicuna-7b deepseek-7b qwen2.5-7b qwen2.5-14b
# Dataset dirs (branch convention): ragroll json rewrite_to_rank_subsampled llm_rank_optimizer_subsampled cseo_subsampled
#   bash scripts/slurm/submit_stealthrank.sh llama-3.1-8b                    # all five datasets
#   bash scripts/slurm/submit_stealthrank.sh llama-3.1-8b json cseo_subsampled
# Requires: bash scripts/10_branch_envs.sh (env + branch data) once.
# Outputs go to a NEW result root (…/suffix/v2_unified): the submission-era
# results under …/suffix/v1 are neither reused nor overwritten (run_no_wandb
# skips a target whose result file already exists).  Collect afterwards with
# scripts/slurm/submit_collect_whitebox.sh MODEL.
source "$(dirname "$0")/_common.sh"
cd "$REPO" && mkdir -p logs
MODEL=${1:?usage: submit_stealthrank.sh MODEL [dataset ...]}; shift
DATASETS=${@:-"ragroll json rewrite_to_rank_subsampled llm_rank_optimizer_subsampled cseo_subsampled"}
RESULT_DIR="results_new/benchmark_results/suffix/v2_unified"

for ds in $DATASETS; do
  ddir=branches/Stealth-Rank/benchmark_data/$ds; [[ -d $ddir ]] || ddir=branches/Stealth-Rank/data2/$ds
  [[ -d $ddir ]] || { echo "no data dir for $ds (run scripts/10_branch_envs.sh)"; continue; }
  NCAT=$(ls "$ddir"/*.jsonl | wc -l)
  echo "Submitting StealthRank model=${MODEL} dataset=${ds} (${NCAT} catalogs, one task each) ..."
  sbatch <<SBEOF
#!/bin/bash
#SBATCH --job-name=geo_sr_${MODEL}_${ds}
#SBATCH --account=${ACCOUNT}
#SBATCH --partition=${PARTITION}
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --gres=gpu:${GPU_TYPE}:1
#SBATCH --time=24:00:00
#SBATCH --array=0-$((NCAT-1))%25
#SBATCH --output=logs/sr_${MODEL}_${ds}_%A_%a.out
#SBATCH --error=logs/sr_${MODEL}_${ds}_%A_%a.err

export CUDA_VISIBLE_DEVICES=0
$(common_env "$CONDA_BIN_STEALTH")
cd branches/Stealth-Rank
mapfile -t CATALOGS < <(ls ${ddir#branches/Stealth-Rank/}/*.jsonl | xargs -n1 basename | sed 's/\\.jsonl\$//' | sort)
CAT=\${CATALOGS[\$SLURM_ARRAY_TASK_ID]}
# pick the config run_no_wandb would pick, but redirect result_dir to the v2 root
label=${ds%_subsampled}
for cand in configs/suffix_${MODEL}_\${label}.yaml configs/suffix_llama-3.1-8b_\${label}.yaml configs/suffix.yaml; do
  [[ -f \$cand ]] && { SRC=\$cand; break; }
done
CFG=configs/_v2_${MODEL}_${ds}.yaml
[[ -f \$CFG ]] || sed -e 's#^\(\s*value:\s*\)"results_new/[^"]*"#\1"${RESULT_DIR}"#' "\$SRC" > "\$CFG"
grep -q "${RESULT_DIR}" "\$CFG" || { echo "result_dir substitution failed in \$SRC"; exit 1; }
echo "catalog='\$CAT'  config: \$SRC -> \$CFG"
python -m experiment.run_no_wandb --model ${MODEL} --dataset ${ds} --mode suffix --catalog "\$CAT" --config "\$CFG"
SBEOF
done
echo "When all arrays finish:  bash scripts/slurm/submit_collect_whitebox.sh ${MODEL}"
