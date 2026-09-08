#!/usr/bin/env bash
# Step 1: pull the final adversarial texts out of the raw outputs that are
# already in the repo (StealthRank, Zero-Shot, RAF, STS) into the unified schema,
# then report coverage and degenerate runs.  CPU only, seconds.
set -euo pipefail
cd "$(dirname "$0")/.."
source .venv-geobench/bin/activate 2>/dev/null || { command -v conda >/dev/null && source "$(conda info --base)/etc/profile.d/conda.sh" && conda activate geobench; } || true

python -m geobench.data

# StealthRank + Zero-Shot raw outputs live under branches/*/results_new/...; the
# StealthRank dir for STSData is called "json".
python -m geobench.collect stealthrank --datasets ragroll stsdata rewrite_to_rank llm_rank_optimizer cseo
python -m geobench.collect zero_shot   --datasets ragroll stsdata rewrite_to_rank llm_rank_optimizer cseo

# RAF: only non-Llama models are checked in.  Point --root/--model at the Llama
# results once they are added (see coauthor request), e.g.
#   python -m geobench.collect raf --model llama-3.1-8b --root branches/RAF/result/raf
python -m geobench.collect raf --model llama-3.1-8b --datasets ragroll stsdata llm_rank_optimizer || true

# STS: raw results are behind the branches/STS/results symlink -> put them at
# branches/STS/results/benchmark_results/sts/v1/llama-3.1-8b/<dsdir>/<cat>/<idx>/{rank.csv,sts.txt}
python -m geobench.collect sts --datasets ragroll stsdata rewrite_to_rank llm_rank_optimizer cseo || true

# Clean baseline (adv_text == orig_text): measures ranking noise.
python -m geobench.collect clean

python -m geobench.scan_failed_runs results/unified/instances/*.csv --out results/unified/coverage_report.csv
