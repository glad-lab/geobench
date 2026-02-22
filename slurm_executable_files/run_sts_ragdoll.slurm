#!/bin/bash
#SBATCH --job-name=sts-ragdoll
#SBATCH --partition=gpuA100x4
#SBATCH --account=bfsl-delta-gpu
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=150G
#SBATCH --time=48:00:00
#SBATCH --output=logs/sts-ragdoll-%j.out
#SBATCH --error=logs/sts-ragdoll-%j.err
#SBATCH --array=1-500

source ~/miniconda3/bin/activate
conda activate controllable-seo
export HF_HOME=/work/hdd/beaa/onimase/hf_cache
cd /work/hdd/beaa/onimase/controllable-seo-project/geobench

# Catalogs for ragdoll_subsampled (50 catalogs x 10 products = 500 jobs)
CATALOGS=("air_compressor" "air_purifier" "automatic_garden_watering_system" "barbecue_grill" "beard_trimmer" "blender" "coffee_maker" "computer_monitor" "computer_power_supply" "cordless_drill" "curling_iron" "dishwasher" "electric_sander" "electric_toothbrush" "eyeshadow" "fascia_gun" "hair_dryer" "hair_straightener" "hammock" "hedge_trimmer" "laptop" "laser_measure" "lawn_mower" "leaf_blower" "lipstick" "microwave_oven" "network_attached_storage" "noise-canceling_headphone" "paint_sprayer" "pool_cleaner" "portable_air_conditioner" "portable_speaker" "pressure_washer" "robot_vacuum" "screw_driver" "shampoo" "skin_cleansing_brush" "sleeping_bag" "slow_cooker" "smartphone" "solid_state_drive" "space_heater" "string_trimmer" "tablet" "tent" "tool_chest" "washing_machine" "wet-dry_vacuum" "wifi_router" "wood_router")

# Calculate catalog index and product index from array task ID
CATALOG_IDX=$(( (SLURM_ARRAY_TASK_ID - 1) / 10 ))
PRODUCT_IDX=$(( (SLURM_ARRAY_TASK_ID - 1) % 10 + 1 ))

CATALOG=${CATALOGS[$CATALOG_IDX]}

python rank_opt.py \
    --model llama-3.1-8b \
    --dataset ragdoll_subsampled \
    --catalog "$CATALOG" \
    --target_product_idx $PRODUCT_IDX \
    --num_iter 500 \
    --test_iter 100 \
    --random_order \
    --save_state \
    --results_dir results/benchmark_results/sts/v1/llama-3.1-8b/ragdoll_subsampled/$CATALOG/$PRODUCT_IDX
