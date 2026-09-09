#!/usr/bin/env bash
# API evaluation, locally or on a login node. No Slurm or GPU is used.
# DRY_RUN=1 prints commands without loading credentials or starting jobs.
# FOREGROUND=1 runs synchronously and propagates evaluation/statistics failures.
set -euo pipefail
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
source "$SCRIPT_DIR/../_api_local.sh"
shopt -s nullglob
instances=("$GEOBENCH_RESULTS"/instances/*.csv)
(( ${#instances[@]} )) || { echo "No instance CSVs under $GEOBENCH_RESULTS/instances" >&2; exit 1; }
read -r -a rankers <<< "${RANKERS:-gpt-4o-mini}"
for ranker in "${rankers[@]}"; do
  case "$ranker" in
    gpt-4o-mini|gpt-4o|claude-haiku) ;;
    *) echo "Not a configured API ranker: $ranker" >&2; exit 1 ;;
  esac
  "$PYTHON_BIN" -m geobench.evaluate --ranker "$ranker" --K "${K:-10}" --no-ppl \
    --instances "${instances[@]}" --preflight
done
for ranker in "${rankers[@]}"; do
  command_args=("$PYTHON_BIN" -m geobench.evaluate --ranker "$ranker" --K "${K:-10}" --no-ppl --instances "${instances[@]}")
  if [[ "${DRY_RUN:-0}" == 1 ]]; then
    printf '%q ' "${command_args[@]}"; printf '\n'
    printf '%q ' "$PYTHON_BIN" -m geobench.stats --ranker "$ranker"; printf '\n'
  elif [[ "${FOREGROUND:-0}" == 1 ]]; then
    "${command_args[@]}"
    "$PYTHON_BIN" -m geobench.stats --ranker "$ranker"
  else
    mkdir -p logs
    logfile="logs/eval_${ranker}_$(date +%s)_$$.out"
    FOREGROUND=1 RANKERS="$ranker" nohup bash "$SCRIPT_DIR/submit_eval_api.sh" >"$logfile" 2>&1 &
    echo "Started $ranker (pid $!); log: $REPO/$logfile"
  fi
done
