import json
import os

INPUT_DIR = "benchmark_data/llm_rank"
OUTPUT_DIR = "benchmark_data/llm_rank_subsampled"

os.makedirs(OUTPUT_DIR, exist_ok=True)

for filename in os.listdir(INPUT_DIR):
    if not filename.endswith('.jsonl'):
        continue
    
    input_path = os.path.join(INPUT_DIR, filename)
    output_path = os.path.join(OUTPUT_DIR, filename)
    
    products = []
    with open(input_path) as f:
        for line in f:
            products.append(json.loads(line))
    
    # Take first 8
    subsampled = products[:8]
    
    with open(output_path, 'w') as f:
        for product in subsampled:
            f.write(json.dumps(product) + '\n')
    
    print(f"{filename}: {len(products)} → 8")