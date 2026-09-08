#!/bin/bash
# API rankers (gpt-4o-mini, gpt-4o, claude-haiku) need no GPU: run on a login
# node inside tmux/nohup.  export OPENAI_API_KEY / ANTHROPIC_API_KEY first.
#   RANKERS="gpt-4o-mini" bash scripts/slurm/submit_eval_api.sh
source "$(dirname "$0")/_common.sh"
cd "$REPO" && mkdir -p logs
export PATH=$CONDA_BIN:$PATH
RANKERS=${RANKERS:-"gpt-4o-mini"}
for ranker in $RANKERS; do
  nohup bash -c "python -m geobench.evaluate --ranker ${ranker} --K ${K:-10} --no-ppl \
        --instances results/unified/instances/*.csv && python -m geobench.stats --ranker ${ranker}" \
        > logs/eval_${ranker}_$(date +%s).out 2>&1 &
  echo "Started ${ranker} in background (pid $!)"
done
