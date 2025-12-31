import json
import os

os.makedirs('benchmark_data/llm_rank', exist_ok=True)

with open('benchmark_data/raw_files/llm_rank_unified_games.json') as f:
    data = json.load(f)

for category, items in data.items():
    jsonl_data = []
    for item in items:
        jsonl_data.append({
            "Name": item['name'],
            "Natural": item['description']
        })
    
    # Sanitize category name - replace / with _
    category_name = category.lower().replace(' ', '_').replace('/', '_')
    with open(f'benchmark_data/llm_rank/{category_name}.jsonl', 'w') as f:
        for entry in jsonl_data:
            f.write(json.dumps(entry) + '\n')
    
    print(f"Created {category_name}.jsonl with {len(jsonl_data)} items")