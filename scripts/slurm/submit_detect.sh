#!/bin/bash
# Detectability suite: LLM judge (Qwen2.5-14B, already cached, != the Llama ranker), relevance
# drift (bge-large), cross-encoder reranker (bge-reranker-v2-m3) + its stats.
source "$(dirname "$0")/_common.sh"
cd "$REPO" && mkdir -p logs
JUDGE=${JUDGE:-Qwen/Qwen2.5-14B-Instruct}
echo "Submitting detect (judge=${JUDGE}) ..."
sbatch <<SBEOF
#!/bin/bash
#SBATCH --job-name=geo_detect
#SBATCH --account=${ACCOUNT}
#SBATCH --partition=${PARTITION}
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --gres=gpu:${GPU_TYPE}:1
#SBATCH --time=${TIME}
#SBATCH --output=logs/detect_%j.out
#SBATCH --error=logs/detect_%j.err

export CUDA_VISIBLE_DEVICES=0
$(common_env "$CONDA_BIN")
INST=(results/unified/instances/*.csv)
python -m geobench.detect judge  --instances "\${INST[@]}" --judge ${JUDGE}
python -m geobench.detect judge-summary --judge ${JUDGE} --fpr 0.05
python -m geobench.detect drift  --instances "\${INST[@]}" --embed BAAI/bge-large-en-v1.5
python -m geobench.detect rerank --instances "\${INST[@]}" --reranker BAAI/bge-reranker-v2-m3
python -m geobench.stats --ranker bge-reranker-v2-m3
SBEOF
