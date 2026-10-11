#!/bin/bash
# Whole revision pipeline in dependency order (each stage waits for the previous
# via --dependency where the stage is a single job; array/loop stages are
# chained by re-running this script after they finish).  Read before running.
#   bash scripts/slurm/submit_all.sh stage1   # attacks (Zero-Shot, C-SEO, TAP) on Llama
#   bash scripts/slurm/submit_all.sh stage2   # evaluate on llama/qwen/mistral + detect   (after stage1)
#   bash scripts/slurm/submit_all.sh stage3   # white-box re-optimisation vs mistral-7b + qwen2.5-14b (~200 GPU-h each)
#   bash scripts/slurm/submit_all.sh stage4   # evaluate the __opt-* instances (white-box + transfer)  (after stage3)
source "$(dirname "$0")/_common.sh"
cd "$REPO"
case "${1:-}" in
  stage1) bash scripts/01_collect_existing.sh; bash scripts/slurm/submit_attacks.sh ablation ;;
  stage2) bash scripts/slurm/submit_eval.sh; bash scripts/slurm/submit_detect.sh
          echo "run on login node:  RANKERS=gpt-4o-mini bash scripts/slurm/submit_eval_api.sh" ;;
  stage3) for m in mistral-7b qwen2.5-14b; do
            bash scripts/slurm/submit_stealthrank.sh $m; bash scripts/slurm/submit_raf.sh $m; bash scripts/slurm/submit_sts.sh $m
          done ;;
  stage4) RANKERS="mistral-7b qwen2.5-14b" bash scripts/slurm/submit_eval.sh
          echo "then:  RANKERS=gpt-4o-mini bash scripts/slurm/submit_eval_api.sh   (transfer)" ;;
  *) echo "usage: $0 stage1|stage2|stage3|stage4"; exit 1 ;;
esac
