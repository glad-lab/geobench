#!/bin/bash
# Unified evaluation of every results/unified/instances/*.csv against each
# open-weight ranker (one 1-GPU job per ranker), K=10 orderings, then stats.
# PPL-R (Vicuna-7B) is computed only in the llama-3.1-8b job — it is ranker-independent.
#   bash scripts/slurm/submit_eval.sh                       # llama qwen2.5-14b mistral
#   RANKERS="llama-3.1-8b" bash scripts/slurm/submit_eval.sh
#   K=10 bash scripts/slurm/submit_eval.sh
source "$(dirname "$0")/_common.sh"
cd "$REPO" && mkdir -p logs
RANKERS=${RANKERS:-"llama-3.1-8b qwen2.5-14b mistral-7b"}
K=${K:-10}

for ranker in $RANKERS; do
  PPL="--no-ppl"; [[ "$ranker" == "llama-3.1-8b" ]] && PPL=""
  tag=${ranker//./p}
  echo "Submitting eval ranker=${ranker} K=${K} ..."
  sbatch <<SBEOF
#!/bin/bash
#SBATCH --job-name=geo_eval_${tag}
#SBATCH --account=${ACCOUNT}
#SBATCH --partition=${PARTITION}
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --gres=gpu:${GPU_TYPE}:1
#SBATCH --time=${TIME}
#SBATCH --output=logs/eval_${tag}_%j.out
#SBATCH --error=logs/eval_${tag}_%j.err

export CUDA_VISIBLE_DEVICES=0
$(common_env "$CONDA_BIN")
python -m geobench.evaluate --ranker ${ranker} --K ${K} ${PPL} --batch-size 10 \\
    --instances results/unified/instances/*.csv
python -m geobench.stats --ranker ${ranker}
SBEOF
done
echo "Submitted eval jobs for: ${RANKERS}"
