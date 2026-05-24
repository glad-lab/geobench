"""
Extract a category from unified_data.json to a separate file.

Usage:
    python noquery/scripts/extract_category.py --category "Motorcycle Accessories"
    python noquery/scripts/extract_category.py --list
"""

import argparse
import json
from pathlib import Path


def read_json(path: str):
    """Read JSON file."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def list_categories(unified_data_path: str):
    """List all available categories."""
    obj = read_json(unified_data_path)
    if not isinstance(obj, dict):
        raise ValueError(f"Expected dict, got {type(obj).__name__}")
    categories = [k for k, v in obj.items() if isinstance(v, list)]
    return categories


def extract_category(unified_data_path: str, category: str, output_path: str, add_ids: bool = True):
    """Extract a category to a separate file."""
    obj = read_json(unified_data_path)

    if not isinstance(obj, dict):
        raise ValueError(f"Expected dict, got {type(obj).__name__}")

    if category not in obj:
        available = list(obj.keys())
        raise ValueError(
            f"Category '{category}' not found. Available: {', '.join(available[:10])}"
            f"{'...' if len(available) > 10 else ''}"
        )

    data = obj[category]

    if not isinstance(data, list):
        raise ValueError(f"Expected list for category, got {type(data).__name__}")

    # Add IDs if requested
    if add_ids:
        for i, item in enumerate(data):
            if isinstance(item, dict) and "id" not in item:
                item["id"] = i

    # Create output structure
    output_obj = {category: data}

    # Ensure output directory exists
    output_path_obj = Path(output_path)
    output_path_obj.parent.mkdir(parents=True, exist_ok=True)

    # Write to file
    output_path_obj.write_text(
        json.dumps(output_obj, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    return len(data)


def main():
    ap = argparse.ArgumentParser(description="Extract category from unified_data.json")
    ap.add_argument(
        "--unified_data",
        default="noquery/data/changed_json/unified_data.json",
        help="Path to unified_data.json"
    )
    ap.add_argument(
        "--category",
        help="Category name to extract"
    )
    ap.add_argument(
        "--output",
        help="Output file path (default: auto-generated in datasets folder)"
    )
    ap.add_argument(
        "--list",
        action="store_true",
        help="List all available categories"
    )
    ap.add_argument(
        "--no-ids",
        action="store_true",
        help="Don't add IDs to items"
    )
    args = ap.parse_args()

    if args.list:
        categories = list_categories(args.unified_data)
        print(f"\nFound {len(categories)} categories:")
        for i, cat in enumerate(categories, 1):
            print(f"  {i}. {cat}")
        return

    if not args.category:
        print("Error: --category is required (or use --list)")
        return 1

    # Generate output path if not provided
    if not args.output:
        cat_safe = args.category.lower().replace(" ", "_").replace("/", "_")
        args.output = f"noquery/data/datasets/{cat_safe}/{cat_safe}.json"

    # Extract category
    num_docs = extract_category(
        args.unified_data,
        args.category,
        args.output,
        add_ids=not args.no_ids
    )

    print(f"✓ Extracted {num_docs} documents from '{args.category}'")
    print(f"  Saved to: {args.output}")


if __name__ == "__main__":
    main()
