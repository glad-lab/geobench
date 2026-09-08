#!/bin/bash
# Shared CARC settings for every submitter in scripts/slurm/.  Edit here only.
# Override any value on the command line, e.g.  ACCOUNT=yzhao010_1245 bash scripts/slurm/submit_eval.sh
export REPO=${REPO:-/scratch1/nimase/geobench/geobench-rev}         # clone of the `revision` branch
export ACCOUNT=${ACCOUNT:-xiangren_1715}
export PARTITION=${PARTITION:-nlp_hiprio}
export GPU_TYPE=${GPU_TYPE:-rtxa6000}                                  # --gres=gpu:${GPU_TYPE}:N
export CONDA_BIN=${CONDA_BIN:-/home1/nimase/.conda/envs/geobench/bin}  # env with requirements-geobench.txt
export CONDA_BIN_STEALTH=${CONDA_BIN_STEALTH:-/scratch1/nimase/geobench/env/bin}      # branches/Stealth-Rank, RAF, zero-shot env
export CONDA_BIN_STS=${CONDA_BIN_STS:-/scratch1/nimase/geobench/env-sts/bin}          # branches/STS env
export HF_HOME=${HF_HOME:-/scratch1/nimase/hf_cache}
# models--* dirs sit directly under hf_cache (not hf_cache/hub), so point the hub cache there too
export HF_HUB_CACHE=${HF_HUB_CACHE:-$HF_HOME}
export HF_HUB_OFFLINE=${HF_HUB_OFFLINE:-0}                          # set 1 to forbid downloads on compute nodes
export TIME=${TIME:-24:00:00}
export OPENBLAS_NUM_THREADS=4 OMP_NUM_THREADS=4 PYTHONNOUSERSITE=1   # also for the submitter itself

# Everything each job's shell needs; expanded INSIDE the heredoc at submit time.
common_env() {
cat <<EOT
export PATH=$1:\$PATH
export HF_HOME=$HF_HOME
export HF_HUB_CACHE=$HF_HUB_CACHE
export HF_HUB_OFFLINE=$HF_HUB_OFFLINE
export HF_TOKEN=${HF_TOKEN:-}
export OPENAI_API_KEY=${OPENAI_API_KEY:-}
export OPENAI_BASE_URL=${OPENAI_BASE_URL:-}
export WANDB_DISABLED=true
export TOKENIZERS_PARALLELISM=false
export OPENBLAS_NUM_THREADS=4
export OMP_NUM_THREADS=4
export PYTHONUNBUFFERED=1
export PYTHONNOUSERSITE=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
cd $REPO
mkdir -p logs results/unified
EOT
}
