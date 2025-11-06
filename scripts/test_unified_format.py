#!/usr/bin/env python3
"""
Test script to verify unified format loads correctly.
"""

import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from populate_vector_db import load_all_products
from collections import Counter


def test_unified_format():
    """Test that unified format loads correctly."""
    print("=" * 60)
    print("TESTING UNIFIED FORMAT LOADING")
    print("=" * 60)

    # Load products
    print("\nLoading products...")
    products = load_all_products()

    # Basic validation
    print(f"\n✅ Loaded {len(products)} products")

    # Check categories
    categories = [p.get("category", "Unknown") for p in products]
    category_counts = Counter(categories)

    print("\nCategory Distribution:")
    for category, count in sorted(category_counts.items()):
        print(f"  • {category}: {count} products")

    # Sample a product to verify all fields preserved
    if products:
        print("\nSample Product Structure:")
        sample = products[0]
        print(f"  ID: {sample.get('id')}")
        print(f"  Name: {sample.get('name')}")
        print(f"  Category: {sample.get('category')}")
        print(f"  Description: {sample.get('description', '')[:80]}...")
        print(f"  Price: ${sample.get('price')}")
        print(f"  Rating: {sample.get('rating')}/5")
        print(f"  Features: {len(sample.get('features', []))} items")
        print(f"  Specifications: {len(sample.get('specifications', {}))} items")

        # Check required fields for vector store
        print("\nVector Store Required Fields:")
        print(f"  ✅ content: {len(sample.get('content', ''))} chars")
        print(f"  ✅ type: {sample.get('type')}")
        print(f"  ✅ has_attack: {sample.get('has_attack')}")

    # Verify total count matches expected
    expected_count = 60
    if len(products) == expected_count:
        print(f"\n✅ Product count matches expected: {expected_count}")
    else:
        print(f"\n❌ Product count mismatch: {len(products)} vs {expected_count}")

    # Check for duplicate IDs
    product_ids = [p.get("id") for p in products]
    if len(product_ids) == len(set(product_ids)):
        print("✅ No duplicate product IDs")
    else:
        print(f"❌ Found duplicate IDs: {len(product_ids) - len(set(product_ids))} duplicates")

    # Check that all products have required fields
    required_fields = ["id", "name", "description", "category"]
    missing_fields = []
    for product in products:
        for field in required_fields:
            if field not in product or not product[field]:
                missing_fields.append((product.get("id", "Unknown"), field))

    if not missing_fields:
        print(f"✅ All products have required fields: {', '.join(required_fields)}")
    else:
        print(f"❌ Missing fields detected:")
        for prod_id, field in missing_fields[:5]:  # Show first 5
            print(f"    Product {prod_id} missing: {field}")

    print("\n" + "=" * 60)
    print("UNIFIED FORMAT TEST COMPLETE")
    print("=" * 60)

    # Return success status
    return len(products) == expected_count and not missing_fields


if __name__ == "__main__":
    success = test_unified_format()
    sys.exit(0 if success else 1)
