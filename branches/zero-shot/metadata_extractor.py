import json
import os
from pathlib import Path

def analyze_dataset(base_path):
    """Analyze a dataset directory and extract statistics."""
    stats = {
        'total_items': 0,
        'num_categories': 0,
        'items_per_category': {},
        'domain': 'Products'
    }
    
    # Get all .jsonl files
    jsonl_files = list(Path(base_path).glob('*.jsonl'))
    stats['num_categories'] = len(jsonl_files)
    
    for file in jsonl_files:
        category = file.stem  # filename without extension
        item_count = 0
        
        with open(file, 'r') as f:
            for line in f:
                if line.strip():
                    item_count += 1
        
        stats['items_per_category'][category] = item_count
        stats['total_items'] += item_count
    
    # Calculate average
    if stats['num_categories'] > 0:
        stats['avg_items_per_category'] = round(stats['total_items'] / stats['num_categories'], 2)
    else:
        stats['avg_items_per_category'] = 0
    
    return stats

# Analyze both datasets
ragroll_stats = analyze_dataset('/work/hdd/bfsl/onimase/geobench-stealth/data2/ragroll')
stsdata_stats = analyze_dataset('/work/hdd/bfsl/onimase/geobench-stealth/data2/json')

# Print results
print("=" * 60)
print("RAGROLL DATASET")
print("=" * 60)
print(f"Total Items: {ragroll_stats['total_items']}")
print(f"Number of Categories: {ragroll_stats['num_categories']}")
print(f"Avg Items per Category: {ragroll_stats['avg_items_per_category']}")
print(f"Domain/Field: {ragroll_stats['domain']}")
print(f"\nCategories: {', '.join(sorted(ragroll_stats['items_per_category'].keys()))}")

print("\n" + "=" * 60)
print("STSDATA DATASET")
print("=" * 60)
print(f"Total Items: {stsdata_stats['total_items']}")
print(f"Number of Categories: {stsdata_stats['num_categories']}")
print(f"Avg Items per Category: {stsdata_stats['avg_items_per_category']}")
print(f"Domain/Field: {stsdata_stats['domain']}")
print(f"\nCategories: {', '.join(sorted(stsdata_stats['items_per_category'].keys()))}")

# Print detailed breakdown
print("\n" + "=" * 60)
print("DETAILED BREAKDOWN")
print("=" * 60)
print("\nRagroll - Items per category:")
for cat, count in sorted(ragroll_stats['items_per_category'].items()):
    print(f"  {cat}: {count}")

print("\nSTSData - Items per category:")
for cat, count in sorted(stsdata_stats['items_per_category'].items()):
    print(f"  {cat}: {count}")