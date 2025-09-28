#!/bin/bash
#SBATCH --job-name=controllable-seo
#SBATCH --partition=gpuA40x4
#SBATCH --account=beaa-delta-gpu
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=100G
#SBATCH --time=06:00:00
#SBATCH --output=logs/controllable-seo-%j.out
#SBATCH --error=logs/controllable-seo-%j.err

echo "Job started at: $(date)"
#!/bin/bash
#SBATCH --job-name=controllable-seo
#SBATCH --partition=gpuA40x4
#SBATCH --account=beaa-delta-gpu
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=100G
#SBATCH --time=06:00:00
#SBATCH --output=logs/controllable-seo-%j.out
#SBATCH --error=logs/controllable-seo-%j.err

echo "Job started at: $(date)"
echo "Job ID: $SLURM_JOB_ID"

source ~/miniconda3/bin/activate
conda activate controllable-seo
cd ~/controllable-seo-project/controllable-seo

mkdir -p logs

echo "=== GPU Verification ==="
nvidia-smi
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"

echo "=== Running Setup Test ==="
python test_setup.py

echo "=== Starting Main Experiment ==="
# FIXED: Pass the correct arguments to match your config
python -m experiment.main --dataset ragroll --catalog "coffee maker" --model deepseek-7b --mode suffix

echo "=== Running Evaluations ==="
python -m experiment.evaluate --job=rank_perplexity
python -m experiment.evaluate --job=bad_word
python ablation_bad_word.py

echo "Job completed at: $(date)"
