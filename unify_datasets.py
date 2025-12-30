import json
import os
from pathlib import Path

datasets = ['json', 'ragroll']

for dataset in datasets:
    unified = {}
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
    
    # Save separate file for each dataset
    output_file = f'unified_dataset_{dataset}.json'
    with open(output_file, 'w') as f:
        json.dump(unified, f, indent=2)
    
    print(f"Created {output_file} with {len(unified)} categories")
