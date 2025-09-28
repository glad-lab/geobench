#!/usr/bin/env python3
"""
Fixed extraction script with proper case sensitivity and pattern matching
"""
import pandas as pd
import glob
import re
import os
from pathlib import Path
import numpy as np

def extract_rank_from_log(log_file):
    """Extract final rank from main experiment log - FIXED"""
    if not os.path.exists(log_file):
        return None
    
    try:
        with open(log_file, 'r') as f:
            content = f.read()
        
        # Look for multiple rank patterns (case insensitive)
        rank_patterns = [
            r'Rank=(\d+)',           # Original pattern
            r'rank=(\d+)',           # Lowercase
            r'Rank:\s*(\d+)',        # With colon
            r'Final\s*Rank:?\s*(\d+)', # Final rank
            r'ranking:?\s*(\d+)',    # ranking
            r'position:?\s*(\d+)'    # position
        ]
        
        all_ranks = []
        for pattern in rank_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            all_ranks.extend([int(m) for m in matches])
        
        if all_ranks:
            return all_ranks[-1]  # Return the last rank found
        
        # Alternative: look for any number after rank-related words
        lines = content.split('\n')
        for line in reversed(lines):
            line_lower = line.lower()
            if any(word in line_lower for word in ['rank', 'position', 'ranking']):
                numbers = re.findall(r'\d+', line)
                if numbers:
                    # Filter for reasonable rank values (1-10)
                    valid_ranks = [int(n) for n in numbers if 1 <= int(n) <= 10]
                    if valid_ranks:
                        return valid_ranks[0]
        
        return None
    except Exception as e:
        print(f"Error reading {log_file}: {e}")
        return None
def check_for_bad_words(main_log_file):
    """Fixed bad word checking that only analyzes generated prompts"""
    if not os.path.exists(main_log_file):
        return None
    
    with open(main_log_file, 'r') as f:
        content = f.read()
    
    # Find TARGET STR sections  
    if "TARGET STR:" not in content:
        return None
    
    target_sections = content.split("TARGET STR:")
    if len(target_sections) < 2:
        return None
    
    # Get only the generated prompt, not training logs
    generated_section = target_sections[-1]
    lines = generated_section.split('\n')
    prompt_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Stop at training/logging indicators
        if any(indicator in line for indicator in ['Training:', 'wandb:', 'Rank=', 'iter/s', '%|', 'Evaluation']):
            break
        prompt_lines.append(line)
    
    full_prompt = ' '.join(prompt_lines).strip()
    if not full_prompt:
        return 0.0
    
    # More specific bad words for SEO manipulation
    bad_words = ["prioritize", "priority", "recommend", "first", "top", "best", "leading", "featured"]
    
    prompt_lower = full_prompt.lower()
    words = prompt_lower.split()
    
    if len(words) == 0:
        return 0.0
    
    bad_word_count = 0
    for word in words:
        clean_word = re.sub(r'[^\w]', '', word.lower())
        if clean_word in bad_words:
            bad_word_count += 1
    
    return round(bad_word_count / len(words), 4)

def debug_single_experiment(exp_dir):
    """Debug a single experiment to understand the format"""
    main_log = os.path.join(exp_dir, "main.log")
    
    if not os.path.exists(main_log):
        return None
    
    print(f"\n=== DEBUGGING {exp_dir} ===")
    
    with open(main_log, 'r') as f:
        content = f.read()
    
    # Check what patterns exist
    print(f"File size: {len(content)} chars")
    
    # Look for target strings
    if "TARGET STR:" in content:
        print("✓ Found 'TARGET STR:'")
        target_sections = content.split("TARGET STR:")
        print(f"  Number of sections: {len(target_sections)}")
        if len(target_sections) > 1:
            sample = target_sections[-1][:200].strip()
            print(f"  Sample: {repr(sample[:100])}...")
    
    # Look for rank patterns
    rank_matches = re.findall(r'[Rr]ank[=:]\s*(\d+)', content)
    print(f"Rank matches: {rank_matches}")
    
    # Look for other potential rank indicators
    final_lines = content.split('\n')[-10:]
    print("Last 10 lines:")
    for i, line in enumerate(final_lines):
        print(f"  {i}: {line.strip()}")
    
    return {
        'has_target_str': "TARGET STR:" in content,
        'rank_matches': rank_matches,
        'file_size': len(content)
    }

def extract_all_results(results_base_dir="results"):
    """Extract results with improved pattern matching"""
    
    all_results = []
    
    # Debug a few experiments first
    print("=== DEBUGGING SAMPLE EXPERIMENTS ===")
    sample_dirs = [
        "results/json_split/coffee_machines/target_1",
        "results/json_split/cameras/target_8", 
        "results/json_split/cameras/target_10"
    ]
    
    for sample_dir in sample_dirs:
        if os.path.exists(sample_dir):
            debug_single_experiment(sample_dir)
    
    print("\n=== EXTRACTING ALL RESULTS ===")
    
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
            
            # Extract metrics with improved functions
            rank = extract_rank_from_log(main_log)
            bad_word_ratio = check_for_bad_words(main_log)
            
            # Determine success (rank 1 = success)
            success = rank == 1 if rank is not None else False
            
            result = {
                'Dataset': dataset_name,
                'Category': category,
                'Target_Index': target_idx,
                'Model': 'deepseek-7b',
                'Final_Rank': rank if rank is not None else "NOT_FOUND",
                'Bad_Word_Ratio': bad_word_ratio if bad_word_ratio is not None else "NOT_FOUND",
                'Success': success,
                'Experiment_Dir': exp_dir
            }
            
            all_results.append(result)
            print(f"  {category} target_{target_idx}: Rank={rank}, BadWord={bad_word_ratio}, Success={success}")
    
    return all_results

def main():
    print("=== FIXED StealthRank Results Extraction ===")
    print("Extracting results with improved pattern matching...\n")
    
    # Extract all results
    results = extract_all_results()
    
    if not results:
        print("No results found! Check your results directory structure.")
        return
    
    # Create DataFrame
    df = pd.DataFrame(results)
    
    # Save detailed results
    output_file = "fixed_deepseek_results.csv"
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
        
        # Bad word ratio stats
        print(f"  Bad Word Ratio by Category:")
        for category in sorted(dataset_df['Category'].unique()):
            cat_df = dataset_df[dataset_df['Category'] == category]
            ratios = [r for r in cat_df['Bad_Word_Ratio'] if isinstance(r, (int, float))]
            if ratios:
                avg_ratio = np.mean(ratios)
                print(f"    {category}: {avg_ratio:.4f}")
    
    # Check for patterns in the data
    print(f"\n=== DATA QUALITY CHECK ===")
    bad_word_ratios = [r for r in df['Bad_Word_Ratio'] if isinstance(r, (int, float))]
    unique_ratios = set(bad_word_ratios)
    print(f"Unique bad word ratios found: {len(unique_ratios)}")
    print(f"Values: {sorted(unique_ratios)}")
    
    missing_ranks = sum([1 for r in df['Final_Rank'] if r == "NOT_FOUND"])
    print(f"Missing ranks: {missing_ranks} out of {len(df)}")

if __name__ == "__main__":
    main()
