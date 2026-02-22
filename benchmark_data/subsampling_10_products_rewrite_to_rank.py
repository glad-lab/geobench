import json
import os

INPUT_DIR = "benchmark_data/rewrite_to_rank"
OUTPUT_DIR = "benchmark_data/rewrite_to_rank_subsampled"
LIST_FILE = "benchmark_data/list_8_products/rewrite_to_rank_at_least_8.txt"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Read categories with at least 10 products
categories_with_10_plus = set()
with open(LIST_FILE) as f:
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) == 2:
            category, count = parts[0], int(parts[1])
            if count >= 10:
                categories_with_10_plus.add(category)

print(f"Found {len(categories_with_10_plus)} categories with at least 10 products")

count = 0
for filename in sorted(os.listdir(INPUT_DIR)):
    if not filename.endswith('.jsonl'):
        continue

    category = filename.replace('.jsonl', '')
    if category not in categories_with_10_plus:
        continue

    input_path = os.path.join(INPUT_DIR, filename)
    output_path = os.path.join(OUTPUT_DIR, filename)

    products = []
    with open(input_path) as f:
        for line in f:
            products.append(json.loads(line))

    # Take first 10
    subsampled = products[:10]

    with open(output_path, 'w') as f:
        for product in subsampled:
            f.write(json.dumps(product) + '\n')

    count += 1
    print(f"{filename}: {len(products)} → 10")

print(f"\nTotal: {count} categories subsampled to 10 products each")
