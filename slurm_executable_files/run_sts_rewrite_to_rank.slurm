#!/bin/bash
#SBATCH --job-name=sts-rewrite
#SBATCH --partition=gpuA100x4
#SBATCH --account=bfsl-delta-gpu
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=150G
#SBATCH --time=48:00:00
#SBATCH --output=logs/sts-rewrite-%j.out
#SBATCH --error=logs/sts-rewrite-%j.err
#SBATCH --array=1-1920

source ~/miniconda3/bin/activate
conda activate controllable-seo
export HF_HOME=/work/hdd/beaa/onimase/hf_cache
cd /work/hdd/beaa/onimase/controllable-seo-project/geobench

# Catalogs for rewrite_to_rank_subsampled (192 catalogs x 10 products = 1920 jobs)
CATALOGS=("accessories" "action_figures" "adhesives" "apparel" "appliance_parts" "art_prints" "arts_and_crafts" "artwork" "athletic_footwear" "automotive" "automotive_accessories" "automotive_batteries" "automotive_lighting" "automotive_parts" "automotive_performance_parts" "automotive_tires" "automotive_tools" "baby_clothing" "backpacks" "baking_supplies" "bathroom_fixtures" "bathroom_vanities" "batteries" "beauty_&_personal_care" "bedding" "beverages" "bicycles" "board_games" "books" "boots" "building_materials" "cameras" "camping_gear" "candy" "cell_phones" "christmas_decorations" "cleaning_supplies" "clothing" "coins" "collectibles" "computer_accessories" "computer_hardware" "computers" "cookbooks" "cookware" "cosmetics" "costumes" "dietary_supplements" "dolls" "dvds" "education" "educational_resources" "electrical_components" "electronics" "eyewear" "fabric" "fasteners" "fishing_gear" "fitness_equipment" "flooring" "flowers" "food" "food_&_beverage" "foot_care" "footwear" "fragrances" "furniture" "gaming_accessories" "gaming_consoles" "gardening_supplies" "generators" "gift_baskets" "gift_cards" "golf_clubs" "golf_equipment" "greeting_cards" "grocery" "gun_holsters" "hair_care" "halloween_costumes" "hand_tools" "handbags" "hardware" "hats" "headphones" "headsets" "health_&_beauty" "health_&_wellness" "health_and_beauty" "health_and_wellness" "health_supplements" "home_&_kitchen" "home_appliances" "home_audio" "home_decor" "home_furniture" "home_improvement" "home_security" "industrial_equipment" "industrial_supplies" "jewelry" "kitchen_appliances" "kitchen_storage" "kitchen_utensils" "knives" "laptops" "lawn_and_garden" "lawn_mower_parts" "lawn_mowers" "lighting" "lighting_fixtures" "lingerie" "liquor" "luggage" "major_appliances" "mattresses" "medical_equipment" "medical_supplies" "mens_clothing" "mens_shoes" "mobile_phones" "motorcycle_accessories" "movies" "music" "musical_instruments" "networking" "office_furniture" "office_supplies" "operating_systems" "optics" "outdoor_furniture" "outdoor_gear" "outerwear" "paint" "party_supplies" "patio_furniture" "perennials" "perfume" "pest_control" "pet_accessories" "pet_care" "pet_food" "pet_supplies" "phone_accessories" "phone_cases" "plants" "plumbing_fixtures" "plumbing_supplies" "plush_toys" "portable_speakers" "power_tools" "printer_supplies" "printers" "promotional_products" "running_shoes" "safety_equipment" "sandals" "shoes" "skincare" "snack_foods" "software" "sports_apparel" "sports_equipment" "sports_memorabilia" "storage_containers" "sunglasses" "supplements" "swimwear" "tablets" "tableware" "tactical_gear" "tea" "tires" "tool_storage" "toy_vehicles" "toys" "trading_cards" "tvs" "uncategorized" "vacuum_cleaners" "video_games" "vitamins_&_supplements" "watches" "water_heaters" "wheels" "window_treatments" "wine" "womens_boots" "womens_clothing" "womens_dresses" "womens_shoes" "workwear")

# Calculate catalog index and product index from array task ID
CATALOG_IDX=$(( (SLURM_ARRAY_TASK_ID - 1) / 10 ))
PRODUCT_IDX=$(( (SLURM_ARRAY_TASK_ID - 1) % 10 + 1 ))

CATALOG=${CATALOGS[$CATALOG_IDX]}

python rank_opt.py \
    --model llama-3.1-8b \
    --dataset rewrite_to_rank_subsampled \
    --catalog "$CATALOG" \
    --target_product_idx $PRODUCT_IDX \
    --num_iter 500 \
    --test_iter 100 \
    --random_order \
    --save_state \
    --results_dir results/benchmark_results/sts/v1/llama-3.1-8b/rewrite_to_rank_subsampled/$CATALOG/$PRODUCT_IDX
