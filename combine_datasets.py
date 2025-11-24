import json
import os
from pathlib import Path

datasets = ['json', 'ragroll']
unified = {}

for dataset in datasets:
    data_path = Path(f'data2/{dataset}')
    for jsonl_file in data_path.glob('*.jsonl'):
        category = jsonl_file.stem
        items = []
        
        with open(jsonl_file) as f:
            for line in f:
                item = json.loads(line)
                items.append({
                    "name": item["Name"],
                    "description": item["Natural"]
                })
        
        unified[category] = items

# Save combined file
with open('unified_dataset.json', 'w') as f:
    json.dump(unified, f, indent=2)

print(f"Created unified_dataset.json with {len(unified)} categories")