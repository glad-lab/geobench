#!/usr/bin/env python3
"""
Complete extraction script with perplexity, multi-model support, and fixed pattern matching
"""
import pandas as pd
import glob
import re
import os
from pathlib import Path
import numpy as np

def extract_model_from_log(log_file):
    """Extract model name from experiment log"""
    if not os.path.exists(log_file):
        return "unknown"
    
    try:
        with open(log_file, 'r') as f:
            content = f.read()
        
        # Look for model specifications in wandb config or command line
        model_patterns = [
            r'model:\s*([^\s\n]+)',
            r'--model\s+([^\s\n]+)',
            r'MODEL["\']?\s*[:=]\s*["\']?([^"\'\s\n]+)',
            r'deepseek[^"\']*7b[^"\']*',
            r'llama[^"\']*3\.1[^"\']*8b[^"\']*',
            r'mistral[^"\']*7b[^"\']*',
            r'vicuna[^"\']*7b[^"\']*'
        ]
        
        for pattern in model_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                model_name = matches[0].lower()
                # Normalize model names
                if 'deepseek' in model_name:
                    return 'deepseek-7b'
                elif 'llama' in model_name and '3.1' in model_name:
                    return 'llama-3.1-8b'
                elif 'mistral' in model_name:
                    return 'mistral-7b'
                elif 'vicuna' in model_name:
                    return 'vicuna-7b'
                else:
                    return model_name
        
        # Default fallback
        return 'deepseek-7b'
        
    except Exception as e:
        print(f"Error extracting model from {log_file}: {e}")
        return 'unknown'

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

def extract_perplexity_from_individual_log(main_log_file):
    """Extract perplexity from the individual experiment"""
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

def extract_pure_generated_prompt(main_log_file):
    """Extract ONLY the generated prompt text, excluding all training logs"""
    if not os.path.exists(main_log_file):
        return None
    
    with open(main_log_file, 'r') as f:
        content = f.read()
    
    # Find TARGET STR sections (case insensitive)
    if "TARGET STR:" not in content:
        return None
    
    target_sections = content.split("TARGET STR:")
    if len(target_sections) < 2:
        return None
    
    # Get the actual generated text (after TARGET STR:)
    generated_section = target_sections[-1]  # Last occurrence
    
    # Split into lines and extract only the prompt content
    lines = generated_section.split('\n')
    prompt_lines = []
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
            
        # STOP at any training/logging indicators
        stop_indicators = [
            'Training:', 'wandb:', 'INFO:', 'DEBUG:', 'ERROR:', 'WARNING:',
            'Epoch', 'Step', 'Iteration', 'Loss=', 'Rank=',
            'iter/s', '%|', 'Evaluation completed',
            '===', 'Local result saved'
        ]
        
        if any(indicator in line for indicator in stop_indicators):
            break
            
        # Keep lines that look like actual prompt content
        prompt_lines.append(line)
    
    # Join the prompt lines
    full_prompt = ' '.join(prompt_lines).strip()
    
    # Additional cleaning - remove any stray training artifacts
    full_prompt = re.sub(r'[|\[\]]+', '', full_prompt)  # Remove |, [, ]
    full_prompt = re.sub(r'\d+%', '', full_prompt)      # Remove percentages
    full_prompt = re.sub(r'\d+/\d+', '', full_prompt)   # Remove fraction patterns
    full_prompt = re.sub(r'\s+', ' ', full_prompt)      # Normalize whitespace
    
    return full_prompt.strip()

def check_for_bad_words(main_log_file):
    """Check generated prompts for bad words/promotional language - FIXED"""
    prompt = extract_pure_generated_prompt(main_log_file)
    if not prompt:
        return None
    
    # More specific bad words that indicate SEO manipulation
    bad_words = [
        "prioritize", "priority", "recommend", "first", "top", "best", 
        "leading", "featured", "popular", "choice", "ultimate", "premier"
    ]
    
    prompt_lower = prompt.lower()
    words = prompt_lower.split()
    
    if len(words) == 0:
        return 0.0
    
    bad_word_count = 0
    for word in words:
        # Clean word of punctuation
        clean_word = re.sub(r'[^\w]', '', word.lower())
        if clean_word in bad_words:
            bad_word_count += 1
    
    return round(bad_word_count / len(words), 4)

def extract_all_results(results_base_dir="results"):
    """Extract results with multi-model support and all metrics"""
    
    all_results = []
    
    print("=== EXTRACTING ALL RESULTS ===")
    
    # Define all experiment directories to process
    experiment_configs = [
        # DeepSeek experiments
        {"dir": "json_split", "dataset": "json", "model": "deepseek-7b"},
        {"dir": "ragroll_split", "dataset": "ragroll", "model": "deepseek-7b"},
        # Mistral experiments  
        {"dir": "mistral_json_split", "dataset": "json", "model": "mistral-7b"},
        {"dir": "mistral_ragroll_split", "dataset": "ragroll", "model": "mistral-7b"},
    ]
    
    for config in experiment_configs:
        dataset_dir = config["dir"]
        dataset_name = config["dataset"] 
        expected_model = config["model"]
        
        dataset_path = os.path.join(results_base_dir, dataset_dir)
        if not os.path.exists(dataset_path):
            print(f"Directory not found: {dataset_path}")
            continue
            
        print(f"\nProcessing {expected_model} {dataset_name} experiments...")
        
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
            
            # Extract all metrics
            # Use expected model from directory structure as fallback
            model = extract_model_from_log(main_log)
            if model == "unknown" or model == "deepseek-7b":
                model = expected_model  # Use the expected model based on directory
            
            rank = extract_rank_from_log(main_log)
            perplexity = extract_perplexity_from_individual_log(main_log)
            bad_word_ratio = check_for_bad_words(main_log)
            
            # Determine success (rank 1 = success)
            success = rank == 1 if rank is not None else False
            
            result = {
                'Dataset': dataset_name,
                'Category': category,
                'Target_Index': target_idx,
                'Model': model,
                'Final_Rank': rank if rank is not None else "NOT_FOUND",
                'Perplexity': round(perplexity, 2) if perplexity is not None else "NOT_FOUND",
                'Bad_Word_Ratio': bad_word_ratio if bad_word_ratio is not None else "NOT_FOUND",
                'Success': success,
                'Experiment_Dir': exp_dir
            }
            
            all_results.append(result)
            print(f"  {category} target_{target_idx}: Model={model}, Rank={rank}, Success={success}")
    
    return all_results

def main():
    print("=== Complete StealthRank Results Extraction ===")
    print("Extracting results with multi-model support...\n")
    
    # Extract all results
    results = extract_all_results()
    
    if not results:
        print("No results found! Check your results directory structure.")
        return
    
    # Create DataFrame
    df = pd.DataFrame(results)
    
    # Save detailed results
    output_file = "complete_multi_model_results.csv"
    df.to_csv(output_file, index=False)
    print(f"\n=== Results saved to {output_file} ===")
    
    # Display summary by model and dataset
    print("\n=== SUMMARY BY MODEL AND DATASET ===")
    for model in sorted(df['Model'].unique()):
        model_df = df[df['Model'] == model]
        print(f"\n{model.upper()} Model:")
        
        for dataset in sorted(model_df['Dataset'].unique()):
            dataset_df = model_df[model_df['Dataset'] == dataset]
            
            # Success rate
            success_count = sum(dataset_df['Success'] == True)
            total_count = len(dataset_df)
            success_rate = success_count / total_count if total_count > 0 else 0
            
            # Average rank
            ranks = [r for r in dataset_df['Final_Rank'] if isinstance(r, int)]
            avg_rank = np.mean(ranks) if ranks else "N/A"
            
            print(f"  {dataset.upper()} Dataset: {success_count}/{total_count} = {success_rate:.1%}, Avg Rank: {avg_rank:.2f}")
    
    # Model vs Model Comparison
    print(f"\n=== MODEL COMPARISON ===")
    comparison_data = []
    
    for model in sorted(df['Model'].unique()):
        model_df = df[df['Model'] == model]
        
        for dataset in ['json', 'ragroll']:
            dataset_df = model_df[model_df['Dataset'] == dataset]
            
            if not dataset_df.empty:
                ranks = [r for r in dataset_df['Final_Rank'] if isinstance(r, int)]
                success_count = sum(dataset_df['Success'] == True)
                total_count = len(dataset_df)
                
                comparison_data.append({
                    'Model': model,
                    'Dataset': dataset,
                    'Avg_Rank': np.mean(ranks) if ranks else None,
                    'Success_Rate': success_count / total_count if total_count > 0 else 0,
                    'Total_Experiments': total_count
                })
    
    comp_df = pd.DataFrame(comparison_data)
    if not comp_df.empty:
        print("\nDetailed Comparison:")
        print(comp_df.to_string(index=False))
        
        # Best performing model per dataset
        print(f"\n=== BEST PERFORMING MODELS ===")
        for dataset in ['json', 'ragroll']:
            dataset_comp = comp_df[comp_df['Dataset'] == dataset]
            if not dataset_comp.empty:
                best_rank = dataset_comp.loc[dataset_comp['Avg_Rank'].idxmin()]
                best_success = dataset_comp.loc[dataset_comp['Success_Rate'].idxmax()]
                
                print(f"{dataset.upper()} Dataset:")
                print(f"  Best Average Rank: {best_rank['Model']} ({best_rank['Avg_Rank']:.2f})")
                print(f"  Best Success Rate: {best_success['Model']} ({best_success['Success_Rate']:.1%})")
    
    # Paper comparison (DeepSeek-7B)
    print(f"\n=== COMPARISON TO PAPER (DeepSeek-7B) ===")
    deepseek_df = df[df['Model'] == 'deepseek-7b']
    
    if not deepseek_df.empty:
        json_ranks = [r for r in deepseek_df[deepseek_df['Dataset']=='json']['Final_Rank'] if isinstance(r, int)]
        ragroll_ranks = [r for r in deepseek_df[deepseek_df['Dataset']=='ragroll']['Final_Rank'] if isinstance(r, int)]
        
        if json_ranks:
            json_avg = np.mean(json_ranks)
            print(f"Your JSON average rank: {json_avg:.2f} vs Paper: 2.10 (Difference: {json_avg - 2.10:+.2f})")
        
        if ragroll_ranks:
            ragroll_avg = np.mean(ragroll_ranks)
            print(f"Your Ragroll average rank: {ragroll_avg:.2f} vs Paper: 2.15 (Difference: {ragroll_avg - 2.15:+.2f})")
    
    # Mistral vs DeepSeek Direct Comparison
    mistral_df = df[df['Model'] == 'mistral-7b']
    if not mistral_df.empty and not deepseek_df.empty:
        print(f"\n=== MISTRAL vs DEEPSEEK COMPARISON ===")
        
        for dataset in ['json', 'ragroll']:
            deepseek_data = deepseek_df[deepseek_df['Dataset'] == dataset]
            mistral_data = mistral_df[mistral_df['Dataset'] == dataset]
            
            if not deepseek_data.empty and not mistral_data.empty:
                ds_ranks = [r for r in deepseek_data['Final_Rank'] if isinstance(r, int)]
                ms_ranks = [r for r in mistral_data['Final_Rank'] if isinstance(r, int)]
                
                ds_success = sum(deepseek_data['Success'] == True) / len(deepseek_data)
                ms_success = sum(mistral_data['Success'] == True) / len(mistral_data)
                
                if ds_ranks and ms_ranks:
                    ds_avg = np.mean(ds_ranks)
                    ms_avg = np.mean(ms_ranks)
                    
                    print(f"{dataset.upper()} Dataset:")
                    print(f"  DeepSeek: Avg Rank {ds_avg:.2f}, Success Rate {ds_success:.1%}")
                    print(f"  Mistral:  Avg Rank {ms_avg:.2f}, Success Rate {ms_success:.1%}")
                    print(f"  Winner: {'Mistral' if ms_avg < ds_avg else 'DeepSeek' if ds_avg < ms_avg else 'Tie'} (rank), {'Mistral' if ms_success > ds_success else 'DeepSeek' if ds_success > ms_success else 'Tie'} (success)")
 
if __name__ == "__main__":
    main()
