import json
import os
from statistics import median

ROOT = "benchmark_data/ragdoll"
CATEGORY_LIST = "benchmark_data/list_8_products/ragdoll_at_least_8.txt"

with open(CATEGORY_LIST) as f:
    categories = [line.split('\t')[0] for line in f]

results = []
for category in categories:
    jsonl_path = f"{ROOT}/{category}.jsonl"
    if not os.path.exists(jsonl_path):
        continue
    
    lengths = []
    with open(jsonl_path) as f:
        for line in f:
            if line.strip():
                item = json.loads(line)
                lengths.append(len(item['Natural']))
    
    med_len = median(lengths)
    max_len = max(lengths)
    results.append((category, med_len, max_len, len(lengths)))

results.sort(key=lambda x: x[1])

print(f"{'Category':<35} {'Med Len':>8} {'Max Len':>8} {'Count':>6}")
print("-" * 65)
for cat, med, max_l, count in results[:15]:
    print(f"{cat:<35} {med:>8.1f} {max_l:>8} {count:>6}")