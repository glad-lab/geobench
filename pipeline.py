import json
import os
import argparse
import subprocess
import time
from datetime import timedelta

def get_elapsed_time(start_time):
    """Helper to format elapsed time string."""
    elapsed = time.time() - start_time
    return str(timedelta(seconds=int(elapsed)))

def prep_data(dataset_name):
    """Step 1: Split unified JSON into JSONL files."""
    print(f"\n[Step 1] Preparing Data for {dataset_name}...")
    
    base_folder = "data2"
    dataset_dir = os.path.join(base_folder, dataset_name)
    unified_file_path = os.path.join(dataset_dir, "unified_dataset.json")

    if not os.path.exists(unified_file_path):
        print(f"[Error] File not found: {unified_file_path}")
        return False

    print(f"Reading from: {unified_file_path}")
    
    try:
        with open(unified_file_path, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"[Error] Failed to parse JSON: {e}")
        return False

    print(f"Splitting data into {dataset_dir}...")

    count = 0
    for catalog, items in data.items():
        if not items:
            continue
            
        output_file = os.path.join(dataset_dir, f"{catalog}.jsonl")
        
        with open(output_file, 'w') as out_f:
            for item in items:
                new_item = {
                    "Name": item.get("name", ""),
                    "Natural": item.get("description", "")
                }
                out_f.write(json.dumps(new_item) + '\n')
        
        print(f"  -> Created {catalog}.jsonl ({len(items)} items)")
        count += 1

    print(f"Step 1 Complete. {count} catalog files created.")
    return True

def run_experiment(dataset_name, model_name):
    """Step 2: Run optimization loops."""
    print(f"\n[Step 2] Running Experiments for {dataset_name} using {model_name}...")
    
    base_folder = "data2"
    dataset_dir = os.path.join(base_folder, dataset_name)
    
    if not os.path.exists(dataset_dir):
        print(f"[Error] Directory not found: {dataset_dir}. Did Step 1 fail?")
        return False

    catalogs = []
    for filename in os.listdir(dataset_dir):
        if filename.endswith(".jsonl"):
            catalog_name = filename[:-6]
            with open(os.path.join(dataset_dir, filename), 'r') as f:
                item_count = sum(1 for line in f)
            catalogs.append((catalog_name, item_count))

    print(f"Found {len(catalogs)} catalogs. Starting optimization loop...")

    for catalog, num_items in catalogs:
        print(f"\n--- Catalog: {catalog} ({num_items} items) ---")
        
        for i in range(1, num_items + 1):
            idx = str(i)
            
            # --- RESUME LOGIC START ---
            # Construct the expected path for the result file
            # Pattern: result/raf/{model}/{dataset}/{catalog}/{idx}/autodan_results.csv
            expected_result_path = os.path.join(
                "result", "raf", model_name, dataset_name, catalog, idx, "autodan_results.csv"
            )

            if os.path.exists(expected_result_path):
                print(f"Skipping {catalog} target_idx {idx} - Found existing results at {expected_result_path}")
                continue
            # --- RESUME LOGIC END ---

            print(f"Running optimization for {catalog} target_idx {idx}...")

            cmd = [
                "python", "-m", "experiment.main",
                "--dataset", dataset_name,
                "--model", model_name,
                "--catalog", catalog,
                "--target_product_idx", idx,
                "--seed", "42",
                "--topk", "512",
                "--w_tar_1", "300",
                "--w_tar_2", "40",
                "--num_templates", "10",
                "--control_loss_method", "last_token_ll",
                "--single_template",
                "--n_steps", "300",
                "--random_order",
                "--use_entropy_adaptive_weighting",
                "--entropy_alpha", "3.0"
            ]

            try:
                subprocess.run(cmd, check=True)
            except subprocess.CalledProcessError as e:
                print(f"[Warning] Failed for {catalog} index {idx}. Error: {e}")
                continue

    print("Step 2 Complete.")
    return True

def evaluate(dataset_name, model_name):
    """Step 3: Run evaluation."""
    print(f"\n[Step 3] Evaluating Results...")

    base_folder = "data2"
    dataset_dir = os.path.join(base_folder, dataset_name)

    if not os.path.exists(dataset_dir):
        print(f"[Error] Directory not found: {dataset_dir}")
        return False

    catalogs = []
    for filename in os.listdir(dataset_dir):
        if filename.endswith(".jsonl"):
            catalog_name = filename[:-6]
            with open(os.path.join(dataset_dir, filename), 'r') as f:
                item_count = sum(1 for line in f)
            catalogs.append((catalog_name, item_count))

    print(f"Found {len(catalogs)} catalogs. Starting evaluation...")

    for catalog, num_items in catalogs:
        indices = [str(i) for i in range(1, num_items + 1)]
        
        print(f"Evaluating Catalog: {catalog}")

        cmd = [
            "python", "test_multiple_ranking.py",
            "--csv_file_template", f"result/raf/{{model}}/{dataset_name}/{{catalog}}/{{target_idx}}/autodan_results.csv",
            "--model", model_name,
            "--catalog", catalog,
            "--target_product_idx"
        ] + indices + [
            "--dataset", dataset_name,
            "--num_runs", "10",
            "--random_order"
        ]

        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"[Error] Evaluation failed for {catalog}: {e}")
            continue

    print("Step 3 Complete.")
    return True

def main():
    parser = argparse.ArgumentParser(description="Full Pipeline: Split Data -> Run Experiment -> Evaluate")
    parser.add_argument("--dataset_name", type=str, required=True, help="Name of the dataset folder inside data2")
    parser.add_argument("--model", type=str, default="llama-3.1-8b", help="Model name for experiment and evaluation")
    args = parser.parse_args()

    # Start Timer
    start_time = time.time()
    print(f"Pipeline started at {time.strftime('%X')}")

    # --- Step 1 ---
    if not prep_data(args.dataset_name):
        print("Pipeline aborted at Step 1.")
        return
    print(f"Time running: {get_elapsed_time(start_time)}")

    # --- Step 2 ---
    if not run_experiment(args.dataset_name, args.model):
        print("Pipeline aborted at Step 2.")
        return
    print(f"Time running: {get_elapsed_time(start_time)}")

    # --- Step 3 ---
    if not evaluate(args.dataset_name, args.model):
        print("Pipeline aborted at Step 3.")
        return
    
    # Final Time
    total_time = get_elapsed_time(start_time)
    print(f"\nAll steps completed successfully.")
    print(f"Total Runtime: {total_time}")

if __name__ == "__main__":
    main()
