#!/usr/bin/env python3
"""
Migrate products_master.json from flat array format to unified category-based structure.

This script transforms:
  {"products": [...]}  →  {"categories": {"Category1": {"items": [...]}, ...}}

All product fields are preserved. The transformation is reversible.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict
import argparse


def load_current_format(file_path: Path) -> List[Dict[str, Any]]:
    """
    Load products from current format (flat array).

    Supports multiple formats:
    - {"products": [...]}
    - [...]

    Returns:
        List of product dictionaries
    """
    with open(file_path, "r") as f:
        data = json.load(f)

    if isinstance(data, dict) and "products" in data:
        products = data["products"]
    elif isinstance(data, list):
        products = data
    else:
        raise ValueError(f"Unknown format in {file_path}")

    return products


def group_by_category(products: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Group products by their category field.

    Args:
        products: List of product dictionaries

    Returns:
        Dictionary mapping category name to list of products
    """
    categories = defaultdict(list)

    for product in products:
        category = product.get("category", "Uncategorized")
        categories[category].append(product)

    return dict(categories)


def create_unified_structure(
    products: List[Dict[str, Any]],
    include_metadata: bool = True
) -> Dict[str, Any]:
    """
    Create unified category-based structure.

    Args:
        products: List of product dictionaries
        include_metadata: Whether to include metadata section

    Returns:
        Unified structure with categories and metadata
    """
    grouped = group_by_category(products)

    unified = {}

    if include_metadata:
        unified["metadata"] = {
            "total_products": len(products),
            "total_categories": len(grouped),
            "format_version": "unified_v1",
            "category_distribution": {
                cat: len(items) for cat, items in grouped.items()
            }
        }

    unified["categories"] = {}
    for category_name, items in sorted(grouped.items()):
        unified["categories"][category_name] = {
            "items": items
        }

    return unified


def validate_transformation(
    original: List[Dict[str, Any]],
    unified: Dict[str, Any]
) -> tuple[bool, List[str]]:
    """
    Validate that transformation preserves all data.

    Args:
        original: Original product list
        unified: Unified structure

    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []

    # Extract all products from unified structure
    reconstructed = []
    for category_name, category_data in unified.get("categories", {}).items():
        for item in category_data.get("items", []):
            reconstructed.append(item)

    # Check product count
    if len(original) != len(reconstructed):
        issues.append(
            f"Product count mismatch: {len(original)} original vs {len(reconstructed)} unified"
        )

    # Check that all product IDs are preserved
    original_ids = {p["id"] for p in original}
    unified_ids = {p["id"] for p in reconstructed}

    if original_ids != unified_ids:
        missing = original_ids - unified_ids
        extra = unified_ids - original_ids
        if missing:
            issues.append(f"Missing product IDs: {missing}")
        if extra:
            issues.append(f"Extra product IDs: {extra}")

    # Check that all fields are preserved for each product
    original_by_id = {p["id"]: p for p in original}
    unified_by_id = {p["id"]: p for p in reconstructed}

    for prod_id in original_ids:
        orig = original_by_id[prod_id]
        unified_prod = unified_by_id.get(prod_id)

        if not unified_prod:
            issues.append(f"Product {prod_id} missing in unified format")
            continue

        # Check all fields
        orig_keys = set(orig.keys())
        unified_keys = set(unified_prod.keys())

        if orig_keys != unified_keys:
            missing_keys = orig_keys - unified_keys
            extra_keys = unified_keys - orig_keys
            if missing_keys:
                issues.append(f"Product {prod_id} missing fields: {missing_keys}")
            if extra_keys:
                issues.append(f"Product {prod_id} has extra fields: {extra_keys}")

        # Check field values match
        for key in orig_keys & unified_keys:
            if orig[key] != unified_prod[key]:
                issues.append(
                    f"Product {prod_id} field '{key}' mismatch: "
                    f"'{orig[key]}' vs '{unified_prod[key]}'"
                )

    is_valid = len(issues) == 0
    return is_valid, issues


def print_summary(unified: Dict[str, Any]):
    """Print summary of unified structure."""
    metadata = unified.get("metadata", {})

    print("\n" + "=" * 60)
    print("UNIFIED STRUCTURE SUMMARY")
    print("=" * 60)
    print(f"Total Products: {metadata.get('total_products', 'Unknown')}")
    print(f"Total Categories: {metadata.get('total_categories', 'Unknown')}")
    print(f"Format Version: {metadata.get('format_version', 'Unknown')}")
    print("\nCategory Distribution:")

    for category, count in metadata.get("category_distribution", {}).items():
        print(f"  • {category}: {count} products")

    print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Migrate products_master.json to unified category-based format"
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/products_master.json"),
        help="Input file path (default: data/products_master.json)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/products_master_unified.json"),
        help="Output file path (default: data/products_master_unified.json)"
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate transformation, don't write output"
    )
    parser.add_argument(
        "--no-metadata",
        action="store_true",
        help="Exclude metadata section from output"
    )

    args = parser.parse_args()

    # Load current format
    print(f"Loading products from {args.input}...")
    try:
        products = load_current_format(args.input)
        print(f"✅ Loaded {len(products)} products")
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        sys.exit(1)

    # Create unified structure
    print("\nTransforming to unified category-based structure...")
    unified = create_unified_structure(
        products,
        include_metadata=not args.no_metadata
    )
    print("✅ Transformation complete")

    # Validate
    print("\nValidating transformation...")
    is_valid, issues = validate_transformation(products, unified)

    if is_valid:
        print("✅ Validation passed - all data preserved")
    else:
        print(f"❌ Validation failed with {len(issues)} issues:")
        for issue in issues:
            print(f"  • {issue}")
        if not args.validate_only:
            print("\n⚠️  Output will NOT be written due to validation errors")
            sys.exit(1)

    # Print summary
    print_summary(unified)

    # Write output
    if not args.validate_only:
        print(f"Writing unified structure to {args.output}...")
        with open(args.output, "w") as f:
            json.dump(unified, f, indent=2, ensure_ascii=False)
        print(f"✅ Output written to {args.output}")

        print("\n" + "=" * 60)
        print("MIGRATION COMPLETE")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Review the output file")
        print("2. Backup original: cp data/products_master.json data/products_master.json.backup")
        print("3. Replace original: mv data/products_master_unified.json data/products_master.json")
        print("4. Update populate_vector_db.py to support new format")
        print("=" * 60)
    else:
        print("\n✅ Validation-only mode - no output written")


if __name__ == "__main__":
    main()
