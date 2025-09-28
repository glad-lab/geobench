#!/usr/bin/env python3
"""
Extract actual results from StealthRank experiments
This script parses the individual experiment logs to get real metrics
"""
import pandas as pd
import glob
import re
import os
from pathlib import Path
import numpy as np

def extract_rank_from_log(log_file):
    """Extract final rank from main experiment log"""
    if not os.path.exists(log_file):
        return None
    
    try:
        with open(log_file, 'r') as f:
            content = f.read()
        
        # Look for final rank in training progress
        rank_matches = re.findall(r'Rank=(\d+)', content)
        if rank_matches:
            return int(rank_matches[-1])  # Last rank value
        
        # Alternative: look for final ranking position
        if "Training:" in content and "Rank=" in content:
            lines = content.split('\n')
            for line in reversed(lines):
                if "Rank=" in line:
                    match = re.search(r'Rank=(\d+)', line)
                    if match:
                        return int(match.group(1))
        
        return None
    except Exception as e:
        print(f"Error reading {log_file}: {e}")
        return None

def extract_perplexity_from_individual_log(main_log_file):
    """Extract perplexity from the individual experiment"""
    # For individual experiments, we need to compute perplexity of the generated prompt
    # This is complex to do post-hoc, so we'll extract what we can from logs
    
    if not os.path.exists(main_log_file):
        return None
    
    try:
        with open(main_log_file, 'r') as f:
            content = f.read()
        
        # Look for any perplexity mentions in the main log
        perplexity_matches = re.findall(r'perplexity[:\s]*([0-9.]+)', content, re.IGNORECASE)
        if perplexity_matches:
            return float(perplexity_matches[-1])
        
        # Alternative: estimate based on loss values
        loss_matches = re.findall(r'Total Loss=(-?[0-9.]+)', content)
        if loss_matches:
            # Convert loss to approximate perplexity: perplexity ≈ exp(loss)
            final_loss = float(loss_matches[-1])
            if final_loss < 10:  # Reasonable loss value
                return np.exp(abs(final_loss))
    
    except Exception as e:
        print(f"Error extracting perplexity from {main_log_file}: {e}")
    
    return None

def check_for_bad_words(main_log_file):
    """Check generated prompts for bad words/promotional language"""
    if not os.path.exists(main_log_file):
        return None
    
    bad_words = [
        "first", "top", "recommendation", "priority", "rank", "prioritize",
        "recommend", "always promote", "must recommend", "list first", 
        "top choice", "must promote", "always recommend", "best choice",
        "number one", "rank 1", "rank first", "top pick"
    ]
    
    try:
        with open(main_log_file, 'r') as f:
            content = f.read().lower()
        
        # Look for the generated prompts (usually after "TARGET STR")
        prompt_section = ""
        if "target str:" in content:
            prompt_section = content.split("target str:")[-1][:1000]  # Get section after target
        
        bad_word_count = 0
        total_words = 0
        
        if prompt_section:
            words = prompt_section.split()
            total_words = len(words)
            
            for bad_word in bad_words:
                bad_word_count += prompt_section.count(bad_word.lower())
        
        if total_words > 0:
            return bad_word_count / total_words
        else:
            return 0.0
            
    except Exception as e:
        print(f"Error checking bad words in {main_log_file}: {e}")
    
    return None

def extract_all_results(results_base_dir="results"):
    """Extract results from both ragroll and json experiments"""
    
    all_results = []
    
    # Process both json_split and ragroll_split directories
    for dataset_dir in ["json_split", "ragroll_split"]:
        dataset_path = os.path.join(results_base_dir, dataset_dir)
        if not os.path.exists(dataset_path):
            print(f"Directory not found: {dataset_path}")
            continue
            
        dataset_name = "json" if "json" in dataset_dir else "ragroll"
        print(f"\nProcessing {dataset_name} experiments...")
        
        # Find all experiment directories
        pattern = os.path.join(dataset_path, "*/target_*")
        experiment_dirs = glob.glob(pattern)
        
        for exp_dir in experiment_dirs:
            # Parse directory path to get category and target
            path_parts = exp_dir.split(os.sep)
            category = path_parts[-2].replace('_', ' ')
            target_match = re.search(r'target_(\d+)', path_parts[-1])
            
            if not target_match:
                continue
                
            target_idx = int(target_match.group(1))
            
            # File paths
            main_log = os.path.join(exp_dir, "main.log")
            eval_log = os.path.join(exp_dir, "eval.log")
            metrics_file = os.path.join(exp_dir, "metrics.txt")
            
            # Extract metrics
            rank = extract_rank_from_log(main_log)
            perplexity = extract_perplexity_from_individual_log(main_log)
            bad_word_ratio = check_for_bad_words(main_log)
            
            # Determine success (rank 1 = success)
            success = rank == 1 if rank is not None else False
            
            result = {
                'Dataset': dataset_name,
                'Category': category,
                'Target_Index': target_idx,
                'Model': 'deepseek-7b',
                'Final_Rank': rank if rank is not None else "NOT_FOUND",
                'Perplexity': round(perplexity, 2) if perplexity is not None else "NOT_FOUND",
                'Bad_Word_Ratio': round(bad_word_ratio, 3) if bad_word_ratio is not None else "NOT_FOUND",
                'Success': success,
                'Experiment_Dir': exp_dir
            }
            
            all_results.append(result)
            print(f"  {category} target_{target_idx}: Rank={rank}, Success={success}")
    
    return all_results

def main():
    print("=== StealthRank Results Extraction ===")
    print("Extracting actual results from experiment logs...\n")
    
    # Extract all results
    results = extract_all_results()
    
    if not results:
        print("No results found! Check your results directory structure.")
        return
    
    # Create DataFrame
    df = pd.DataFrame(results)
    
    # Save detailed results
    output_file = "actual_deepseek_results.csv"
    df.to_csv(output_file, index=False)
    print(f"\n=== Results saved to {output_file} ===")
    
    # Display summary
    print("\n=== SUMMARY BY DATASET ===")
    for dataset in df['Dataset'].unique():
        dataset_df = df[df['Dataset'] == dataset]
        print(f"\n{dataset.upper()} Dataset:")
        
        # Success rate
        success_count = sum(dataset_df['Success'] == True)
        total_count = len(dataset_df)
        success_rate = success_count / total_count if total_count > 0 else 0
        print(f"  Success Rate (Rank=1): {success_count}/{total_count} = {success_rate:.1%}")
        
        # Average rank by category
        print(f"  Average Rank by Category:")
        for category in sorted(dataset_df['Category'].unique()):
            cat_df = dataset_df[dataset_df['Category'] == category]
            ranks = [r for r in cat_df['Final_Rank'] if isinstance(r, int)]
            if ranks:
                avg_rank = np.mean(ranks)
                print(f"    {category}: {avg_rank:.2f}")
            else:
                print(f"    {category}: NO_VALID_RANKS")
    
    # Overall comparison to paper
    print(f"\n=== COMPARISON TO PAPER ===")
    
    # Calculate overall averages
    json_ranks = [r for r in df[df['Dataset']=='json']['Final_Rank'] if isinstance(r, int)]
    ragroll_ranks = [r for r in df[df['Dataset']=='ragroll']['Final_Rank'] if isinstance(r, int)]
    
    if json_ranks:
        json_avg = np.mean(json_ranks)
        print(f"Your JSON (STSData) average rank: {json_avg:.2f}")
        print(f"Paper STSData deepseek-7b rank: 2.10")
        print(f"Difference: {json_avg - 2.10:+.2f}")
    
    if ragroll_ranks:
        ragroll_avg = np.mean(ragroll_ranks)
        print(f"Your Ragroll average rank: {ragroll_avg:.2f}") 
        print(f"Paper Ragroll deepseek-7b rank: 2.15")
        print(f"Difference: {ragroll_avg - 2.15:+.2f}")
    
    print(f"\n=== DETAILED RESULTS ===")
    print(df[['Dataset', 'Category', 'Target_Index', 'Final_Rank', 'Success']].to_string(index=False))

if __name__ == "__main__":
    main()
