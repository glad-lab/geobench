#!/bin/bash
# RAF (white-box) against a new ranker: one job per dataset.
# MODEL keys: see branches/RAF/experiment/main.py MODEL_PATH_DICT (llama-3.1-8b mistral-7b vicuna-7b deepseek-7b qwen-4b qwen2.5-7b phi-2.7b)
#   bash scripts/slurm/submit_raf.sh llama-3.1-8b
source "$(dirname "$0")/_common.sh"
cd "$REPO" && mkdir -p logs
MODEL=${1:?usage: submit_raf.sh MODEL [dataset ...]}; shift
DATASETS=${@:-"ragroll stsdata llmrankoptim rewrite_to_rank cseo"}

for ds in $DATASETS; do
  echo "Submitting RAF model=${MODEL} dataset=${ds} ..."
  sbatch <<SBEOF
#!/bin/bash
#SBATCH --job-name=geo_raf_${MODEL}_${ds}
#SBATCH --account=${ACCOUNT}
#SBATCH --partition=${PARTITION}
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=120G
#SBATCH --gres=gpu:${GPU_TYPE}:1
#SBATCH --time=48:00:00
#SBATCH --output=logs/raf_${MODEL}_${ds}_%j.out
#SBATCH --error=logs/raf_${MODEL}_${ds}_%j.err

export CUDA_VISIBLE_DEVICES=0
$(common_env "$CONDA_BIN_STEALTH")
cd branches/RAF
python pipeline.py --dataset_name ${ds} --model ${MODEL}
cd "$REPO"
export PATH=$CONDA_BIN:\$PATH
python -m geobench.collect raf --model ${MODEL} --out results/unified/instances/raf__opt-${MODEL}.csv
SBEOF
done
