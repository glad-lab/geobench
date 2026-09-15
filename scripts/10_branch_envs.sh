#!/usr/bin/env bash
# Build the two branch environments the white-box attacks run in.  Run once on a
# login node (tmux recommended; ~10-20 min of pip).  Paths match _common.sh defaults.
set -euo pipefail
export PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=4
source "$(conda info --base)/etc/profile.d/conda.sh"
cd "$(dirname "$0")/.."
ENV_SR=${CONDA_BIN_STEALTH:-/scratch1/nimase/geobench/env/bin}; ENV_SR=${ENV_SR%/bin}
ENV_STS=${CONDA_BIN_STS:-/scratch1/nimase/geobench/env-sts/bin}; ENV_STS=${ENV_STS%/bin}

echo "== Stealth-Rank / RAF / zero-shot env -> $ENV_SR"
[[ -x $ENV_SR/bin/python ]] || conda create -y -p "$ENV_SR" python=3.11
"$ENV_SR/bin/python" -m pip install -U pip
"$ENV_SR/bin/python" -m pip install -r branches/Stealth-Rank/requirements.txt
"$ENV_SR/bin/python" -m pip install -r branches/RAF/requirements.txt
"$ENV_SR/bin/python" -c "import torch, transformers, wandb, yaml; print('stealth env ok: torch', torch.__version__, 'transformers', transformers.__version__)"

echo "== STS env -> $ENV_STS"
[[ -x $ENV_STS/bin/python ]] || conda create -y -p "$ENV_STS" python=3.11
"$ENV_STS/bin/python" -m pip install -U pip
"$ENV_STS/bin/python" -m pip install -r branches/STS/requirements.txt
"$ENV_STS/bin/python" -c "import torch, transformers; print('sts env ok: torch', torch.__version__, 'transformers', transformers.__version__)"

echo "== branch data (manifest datasets in branch layout)"
python scripts/prepare_branch_data.py
