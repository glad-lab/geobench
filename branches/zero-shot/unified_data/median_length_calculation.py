import json
import statistics

def calculate_median_description_length(filepath):
    with open(filepath) as f:
        data = json.load(f)
    
    # Extract all description lengths
    lengths = []
    for category, items in data.items():
        for item in items:
            lengths.append(len(item['description']))
    
    median = statistics.median(lengths)
    return median, lengths

# Calculate for both files
files = [
    'unified_dataset_ragroll.json',
    'unified_dataset_json.json'
]

for filepath in files:
    median, lengths = calculate_median_description_length(filepath)
    print(f"\n{filepath}:")
    print(f"  Median description length: {median}")
    print(f"  Min length: {min(lengths)}")
    print(f"  Max length: {max(lengths)}")
    print(f"  Total items: {len(lengths)}")