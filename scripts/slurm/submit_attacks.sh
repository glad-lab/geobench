#!/bin/bash
# Inference-only attack families with the unified runners: Zero-Shot (ranker as
# attacker), C-SEO rewrites (gpt-4o-mini), TAP (DeepSeek-R1 attacker, Llama ranker).
# One 1-GPU job each so they run in parallel.  Needs OPENAI_API_KEY exported
# (and OPENAI_BASE_URL=https://api.deepseek.com + a DeepSeek key for TAP).
#   bash scripts/slurm/submit_attacks.sh            # paper setting
#   bash scripts/slurm/submit_attacks.sh ablation   # + attacker/rewriter-strength ablation
source "$(dirname "$0")/_common.sh"
cd "$REPO" && mkdir -p logs

declare -A JOBS
JOBS[zs_llama]="python -m geobench.attacks.zero_shot --attacker meta-llama/Meta-Llama-3.1-8B-Instruct"
JOBS[cseo_gpt4omini]="python -m geobench.attacks.cseo_rewrite --rewriter gpt-4o-mini"
JOBS[tap_llama]="python -m geobench.attacks.tap --ranker llama-3.1-8b --attacker api:deepseek-reasoner --tag llama-3.1-8b"
if [[ "${1:-}" == "ablation" ]]; then
  JOBS[zs_gpt4omini]="python -m geobench.attacks.zero_shot --attacker gpt-4o-mini --tag att-gpt4omini"
  JOBS[zs_qwen1p5b]="python -m geobench.attacks.zero_shot --attacker Qwen/Qwen2.5-1.5B-Instruct --tag att-qwen1.5b"
  JOBS[cseo_qwen7b]="python -m geobench.attacks.cseo_rewrite --rewriter Qwen/Qwen2.5-7B-Instruct --tag rw-qwen7b --methods authoritative content_improvement llm_guidance"
  JOBS[tap_att_llama]="python -m geobench.attacks.tap --ranker llama-3.1-8b --attacker meta-llama/Meta-Llama-3.1-8B-Instruct --tag att-llama8b --datasets cseo stsdata"
fi

for name in "${!JOBS[@]}"; do
  echo "Submitting attack job ${name} ..."
  sbatch <<SBEOF
#!/bin/bash
#SBATCH --job-name=geo_${name}
#SBATCH --account=${ACCOUNT}
#SBATCH --partition=${PARTITION}
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --gres=gpu:${GPU_TYPE}:1
#SBATCH --time=${TIME}
#SBATCH --output=logs/${name}_%j.out
#SBATCH --error=logs/${name}_%j.err

export CUDA_VISIBLE_DEVICES=0
$(common_env "$CONDA_BIN")
${JOBS[$name]}
SBEOF
done
echo "Submitted ${#JOBS[@]} attack jobs."
