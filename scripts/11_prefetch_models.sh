#!/usr/bin/env bash
# Download the (ungated) models the ablations need into HF_HOME, on a login node
# with network access.  Everything else is already cached.
set -euo pipefail
export PYTHONNOUSERSITE=1
source "$(conda info --base)/etc/profile.d/conda.sh" && conda activate geobench
: "${HF_HOME:=/scratch1/nimase/hf_cache}"; export HF_HOME HF_HUB_CACHE=$HF_HOME; unset HF_HUB_OFFLINE
for m in Qwen/Qwen2.5-1.5B-Instruct; do
  python -c "from huggingface_hub import snapshot_download; print(snapshot_download('$m'))"
done
