#!/usr/bin/env bash
# Step 5: regenerate tables, figure and the reproducibility appendix.
set -euo pipefail
cd "$(dirname "$0")/.."
source .venv-geobench/bin/activate 2>/dev/null || { command -v conda >/dev/null && source "$(conda info --base)/etc/profile.d/conda.sh" && conda activate geobench; } || true
RANKERS=${RANKERS:-"llama-3.1-8b qwen2.5-14b mistral-7b gpt-4o-mini"}
AVAIL=""
for r in $RANKERS; do [[ -f results/unified/summary/${r}_summary.csv ]] && AVAIL="$AVAIL $r"; done
python -m geobench.make_tables --rankers $AVAIL
mkdir -p results/unified/tables
python -m geobench.appendix > results/unified/tables/appendix_repro.tex
ls -1 results/unified/tables
