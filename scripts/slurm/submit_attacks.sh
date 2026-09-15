#!/bin/bash
# Inference-only attack families with the unified runners: Zero-Shot (ranker as
# attacker), C-SEO rewrites (gpt-4o-mini), TAP (DeepSeek-R1 attacker, Llama ranker).
# One 1-GPU job each so they run in parallel.  Needs OPENAI_API_KEY exported
# (and OPENAI_BASE_URL=https://api.deepseek.com + a DeepSeek key for TAP).
#   bash scripts/slurm/submit_attacks.sh            # TAP with open attackers (llama-8b self, qwen2.5-14b); never while a TAP job is queued
#   bash scripts/slurm/submit_attacks.sh ablation   # + attacker/rewriter-strength ablation (open models)
#   bash scripts/slurm/submit_attacks.sh api        # GPT-4o-mini jobs (need OPENAI_API_KEY; already done by Zhe)
#   bash scripts/slurm/submit_attacks.sh zeroshot   # regenerate paper-setting Zero-Shot
source "$(dirname "$0")/_common.sh"
cd "$REPO" && mkdir -p logs

declare -A JOBS GPUS
# Open-weight TAP: attacker = the ranker itself (1 GPU) and a stronger open attacker
# (Qwen2.5-14B, 2 GPUs).  DeepSeek-R1-0528 is no longer served, so the paper's
# TAP attacker is replaced by these two; the C-SEO GPT-4o-mini rewrites and the
# GPT-4o-mini zero-shot attacker were produced off-cluster (results/unified/instances/).
if [[ -z "${1:-}" || "${1:-}" == "tap" ]]; then     # ONLY with no argument (or "tap"): never alongside ablation/api/zeroshot,
  JOBS[tap_att_llama8b]="python -m geobench.attacks.tap --ranker llama-3.1-8b --attacker meta-llama/Meta-Llama-3.1-8B-Instruct --tag att-llama8b"
  JOBS[tap_att_qwen14b]="python -m geobench.attacks.tap --ranker llama-3.1-8b --attacker Qwen/Qwen2.5-14B-Instruct --tag att-qwen14b"; GPUS[tap_att_qwen14b]=2
fi                                                    # two TAP jobs on one checkpoint file would corrupt it
if [[ "${1:-}" == "zeroshot" ]]; then
  JOBS[zs_llama]="python -m geobench.attacks.zero_shot --attacker meta-llama/Meta-Llama-3.1-8B-Instruct"   # already run once (9/7)
fi
if [[ "${1:-}" == "api" ]]; then           # needs OPENAI_API_KEY; Zhe already ran these
  JOBS[cseo_gpt4omini]="python -m geobench.attacks.cseo_rewrite --rewriter gpt-4o-mini"
  JOBS[zs_gpt4omini]="python -m geobench.attacks.zero_shot --attacker gpt-4o-mini --tag att-gpt4omini"
fi
if [[ "${1:-}" == "ablation" ]]; then
  JOBS[zs_qwen1p5b]="python -m geobench.attacks.zero_shot --attacker Qwen/Qwen2.5-1.5B-Instruct --tag att-qwen1.5b"
  JOBS[zs_qwen14b]="python -m geobench.attacks.zero_shot --attacker Qwen/Qwen2.5-14B-Instruct --tag att-qwen14b"
  JOBS[cseo_qwen14b]="python -m geobench.attacks.cseo_rewrite --rewriter Qwen/Qwen2.5-14B-Instruct --tag rw-qwen14b --methods authoritative content_improvement llm_guidance"
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
#SBATCH --gres=gpu:${GPU_TYPE}:${GPUS[$name]:-1}
#SBATCH --time=${TIME}
#SBATCH --output=logs/${name}_%j.out
#SBATCH --error=logs/${name}_%j.err

$(common_env "$CONDA_BIN")
${JOBS[$name]}
SBEOF
done
echo "Submitted ${#JOBS[@]} attack jobs."
