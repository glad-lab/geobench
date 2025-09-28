import os
import re

def extract_pure_generated_prompt(main_log_file):
    """Extract ONLY the generated prompt text, excluding all training logs"""
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

# Test on several experiments
test_files = [
    ("results/json_split/coffee_machines/target_1/main.log", "Coffee Machines T1 (Success)"),
    ("results/json_split/books/target_1/main.log", "Books T1 (Rank 4)"),
    ("results/json_split/cameras/target_1/main.log", "Cameras T1 (Success)"),
    ("results/ragroll_split/smartphone/target_1/main.log", "Smartphone T1 (Success)"),
]

print("=== DEBUGGING: What are the actual generated prompts? ===")
for log_file, name in test_files:
    if os.path.exists(log_file):
        prompt = extract_pure_generated_prompt(log_file)
        print(f"\n{name}:")
        print(f"  Extracted prompt: '{prompt}'")
        print(f"  Length: {len(prompt.split()) if prompt else 0} words")
    else:
        print(f"\n{name}: FILE NOT FOUND")
