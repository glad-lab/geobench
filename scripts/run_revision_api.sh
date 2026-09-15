#!/usr/bin/env bash
# The three requested API-only steps, in dependency order. No TAP or GPU jobs.
# Usage: bash scripts/run_revision_api.sh [all|generate|evaluate|--dry-run]
set -euo pipefail
source "$(dirname "$0")/_api_local.sh"
stage=${1:-all}
case "$stage" in all|generate|evaluate|--dry-run) ;; *) echo "Unknown stage: $stage" >&2; exit 1 ;; esac
"$PYTHON_BIN" -c 'import pandas, numpy, scipy, openai; from geobench.api import api_identity; print(api_identity("gpt-4o-mini"))'
if [[ "$GEOBENCH_API_PROVIDER" == blockrun ]]; then
  "$PYTHON_BIN" -c 'import blockrun_llm'
fi
echo "Repository: $REPO; Python: $PYTHON_BIN; results: $GEOBENCH_RESULTS"
if [[ "$stage" == --dry-run ]]; then
  echo '1. python -m geobench.attacks.cseo_rewrite --rewriter gpt-4o-mini'
  echo '2. python -m geobench.attacks.zero_shot --attacker gpt-4o-mini --tag att-gpt4omini'
  echo '3. FOREGROUND=1 RANKERS=gpt-4o-mini bash scripts/slurm/submit_eval_api.sh'
  echo 'No API client initialized, no inference requests, no background jobs.'
  exit 0
fi
if [[ "$stage" == all || "$stage" == generate ]]; then
  "$PYTHON_BIN" -m geobench.attacks.cseo_rewrite --rewriter gpt-4o-mini
  "$PYTHON_BIN" -m geobench.attacks.zero_shot --attacker gpt-4o-mini --tag att-gpt4omini
fi
if [[ "$stage" == all || "$stage" == evaluate ]]; then
  GEOBENCH_API_WORKERS="${GEOBENCH_EVAL_WORKERS:-${GEOBENCH_API_WORKERS:-1}}" \
    FOREGROUND=1 RANKERS=gpt-4o-mini bash scripts/slurm/submit_eval_api.sh
fi
