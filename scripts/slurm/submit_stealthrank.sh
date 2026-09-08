#!/bin/bash
# Re-optimise StealthRank (white-box) against a new ranker: one job per dataset.
# MODEL keys: llama-3.1-8b mistral-7b vicuna-7b deepseek-7b qwen2.5-7b
#   bash scripts/slurm/submit_stealthrank.sh mistral-7b
#   CONFIG=configs/suffix_llama-3.1-8b_cseo_uniform.yaml bash scripts/slurm/submit_stealthrank.sh llama-3.1-8b cseo_subsampled
source "$(dirname "$0")/_common.sh"
cd "$REPO" && mkdir -p logs
MODEL=${1:?usage: submit_stealthrank.sh MODEL [dataset ...]}; shift
DATASETS=${@:-"ragroll json rewrite_to_rank_subsampled llm_rank_optimizer_subsampled cseo_subsampled"}
CFG=${CONFIG:+--config $CONFIG}

for ds in $DATASETS; do
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
for f in benchmark_data/${ds}/*.jsonl data2/${ds}/*.jsonl; do
  [[ -f "\$f" ]] || continue
  CAT=\$(basename "\$f" .jsonl)
  python -m experiment.run_no_wandb --model ${MODEL} --dataset ${ds} --mode suffix --catalog "\$CAT" ${CFG}
done
cd "$REPO"
export PATH=$CONDA_BIN:\$PATH
python -m geobench.collect stealthrank --model ${MODEL} --out results/unified/instances/stealthrank__opt-${MODEL}.csv
SBEOF
done
