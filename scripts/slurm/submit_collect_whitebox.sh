#!/bin/bash
# After the white-box re-optimisation arrays finish: collect the new outputs into
# unified instance files (CPU, seconds) and report coverage.
#   bash scripts/slurm/submit_collect_whitebox.sh llama-3.1-8b
source "$(dirname "$0")/_common.sh"
cd "$REPO"
export PATH=$CONDA_BIN:$PATH
MODEL=${1:?usage: submit_collect_whitebox.sh MODEL}
DS="ragroll stsdata rewrite_to_rank llm_rank_optimizer cseo"

python -m geobench.collect stealthrank --model "$MODEL" --datasets $DS \
    --root branches/Stealth-Rank/results_new/benchmark_results/suffix/v2_unified \
    --out results/unified/instances/stealthrank__opt-${MODEL}.csv || true
python -m geobench.collect raf --model "$MODEL" --datasets $DS \
    --dsdir ragroll=u_ragroll stsdata=u_stsdata llm_rank_optimizer=u_llmrankoptim rewrite_to_rank=u_rewrite_to_rank cseo=u_cseo \
    --out results/unified/instances/raf__opt-${MODEL}.csv || true
python -m geobench.collect sts --model "$MODEL" --datasets $DS \
    --root branches/STS/results/benchmark_results/sts/v1 \
    --out results/unified/instances/sts__opt-${MODEL}.csv || true
python -m geobench.scan_failed_runs results/unified/instances/*__opt-${MODEL}.csv
echo "Next:  RANKERS=\"${MODEL}\" bash scripts/slurm/submit_eval.sh   (white-box)   then   RANKERS=\"llama-3.1-8b qwen2.5-14b mistral-7b\" ...  (transfer)"
