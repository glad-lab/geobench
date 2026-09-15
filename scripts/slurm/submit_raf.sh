#!/bin/bash
# RAF (white-box) against a ranker: one ARRAY job per dataset, one task per
# catalog, hyper-parameters exactly as branches/RAF/pipeline.py.
# MODEL keys: see branches/RAF/experiment/main.py MODEL_PATH_DICT (llama-3.1-8b mistral-7b vicuna-7b deepseek-7b qwen-4b qwen2.5-7b qwen2.5-14b phi-2.7b)
# Datasets (unified copies written by scripts/prepare_branch_data.py): u_ragroll u_stsdata u_llmrankoptim u_rewrite_to_rank u_cseo
#   bash scripts/slurm/submit_raf.sh llama-3.1-8b
#   bash scripts/slurm/submit_raf.sh llama-3.1-8b u_stsdata u_cseo
source "$(dirname "$0")/_common.sh"
cd "$REPO" && mkdir -p logs
MODEL=${1:?usage: submit_raf.sh MODEL [dataset ...]}; shift
DATASETS=${@:-"u_ragroll u_stsdata u_llmrankoptim u_rewrite_to_rank u_cseo"}

for ds in $DATASETS; do
  ddir=branches/RAF/data2/$ds
  [[ -d $ddir ]] || { echo "no $ddir (run scripts/10_branch_envs.sh)"; continue; }
  NCAT=$(ls "$ddir"/*.jsonl | wc -l)
  echo "Submitting RAF model=${MODEL} dataset=${ds} (${NCAT} catalogs, one task each) ..."
  sbatch <<SBEOF
#!/bin/bash
#SBATCH --job-name=geo_raf_${MODEL}_${ds}
#SBATCH --account=${ACCOUNT}
#SBATCH --partition=${PARTITION}
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --gres=gpu:${GPU_TYPE}:1
#SBATCH --time=24:00:00
#SBATCH --array=0-$((NCAT-1))%25
#SBATCH --output=logs/raf_${MODEL}_${ds}_%A_%a.out
#SBATCH --error=logs/raf_${MODEL}_${ds}_%A_%a.err

export CUDA_VISIBLE_DEVICES=0
$(common_env "$CONDA_BIN_STEALTH")
cd branches/RAF
mapfile -t CATALOGS < <(ls data2/${ds}/*.jsonl | xargs -n1 basename | sed 's/\\.jsonl\$//' | sort)
CAT=\${CATALOGS[\$SLURM_ARRAY_TASK_ID]}
N=\$(wc -l < "data2/${ds}/\$CAT.jsonl")
echo "catalog='\$CAT' targets=\$N"
for idx in \$(seq 1 \$N); do
  out="result/raf/${MODEL}/${ds}/\$CAT/\$idx/autodan_results.csv"
  [[ -f "\$out" ]] && { echo "skip \$idx (exists)"; continue; }
  python -m experiment.main --dataset ${ds} --model ${MODEL} --catalog "\$CAT" --target_product_idx \$idx \\
      --seed 42 --topk 512 --w_tar_1 300 --w_tar_2 40 --num_templates 10 --control_loss_method last_token_ll \\
      --single_template --n_steps 300 --random_order --use_entropy_adaptive_weighting --entropy_alpha 3.0 \\
      || echo "WARNING: target \$idx failed"
done
SBEOF
done
echo "When all arrays finish:  bash scripts/slurm/submit_collect_whitebox.sh ${MODEL}"
