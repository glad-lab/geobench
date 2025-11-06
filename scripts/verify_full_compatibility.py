#!/usr/bin/env python3
"""
Comprehensive verification that all code works with unified data structure.

Tests:
1. Data loading (populate_vector_db.py)
2. Benchmark utilities (benchmark_utils.py)
3. Attack generation (attacks.py)
4. Product structure compatibility
5. Prepare for geobench migration
"""

import sys
import os
import json

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from populate_vector_db import load_all_products, load_noise_documents, create_attack_documents
from benchmark_utils import UnifiedDataLoader, ProductManipulator
from attacks import AttackGenerator, AttackType
from ranking import Product


def test_data_loading():
    """Test that populate_vector_db loads unified format correctly."""
    print("\n" + "=" * 70)
    print("TEST 1: Data Loading (populate_vector_db.py)")
    print("=" * 70)

    products = load_all_products()

    assert len(products) == 60, f"Expected 60 products, got {len(products)}"
    print(f"✅ Loaded {len(products)} products")

    # Check all products have required fields
    required_fields = ["id", "name", "description", "category", "content", "type", "has_attack"]
    for product in products:
        for field in required_fields:
            assert field in product, f"Product {product.get('id')} missing field: {field}"

    print(f"✅ All products have required fields: {', '.join(required_fields)}")

    # Check category distribution
    from collections import Counter
    categories = Counter(p["category"] for p in products)
    expected_distribution = {
        "Books & Media": 10,
        "Computing Hardware": 15,
        "Home Furniture": 10,
        "Kitchen Appliances": 10,
        "Cameras": 8,
        "Lenses": 4,
        "Accessories": 3
    }

    for category, count in expected_distribution.items():
        assert categories[category] == count, f"Category {category}: expected {count}, got {categories[category]}"

    print(f"✅ Category distribution correct:")
    for cat, count in sorted(categories.items()):
        print(f"    {cat}: {count}")

    return True


def test_benchmark_utilities():
    """Test that benchmark_utils works with unified structure."""
    print("\n" + "=" * 70)
    print("TEST 2: Benchmark Utilities (benchmark_utils.py)")
    print("=" * 70)

    loader = UnifiedDataLoader("data/products_master.json")

    # Test basic loading
    all_products = loader.get_all_products()
    assert len(all_products) == 60, f"Expected 60 products, got {len(all_products)}"
    print(f"✅ UnifiedDataLoader loaded {len(all_products)} products")

    # Test category access
    categories = loader.get_categories()
    assert len(categories) == 7, f"Expected 7 categories, got {len(categories)}"
    print(f"✅ Found {len(categories)} categories")

    # Test sampling
    sample = loader.sample_products(10, strategy="random", seed=42)
    assert len(sample) == 10, f"Expected 10 products, got {len(sample)}"
    print(f"✅ Sampling works (10 random products)")

    # Test product manipulation
    reordered = ProductManipulator.change_order(sample, order_strategy="by_rating")
    assert len(reordered) == len(sample), "Reordering lost products"
    print(f"✅ Product reordering works")

    noisy = ProductManipulator.add_noise(sample, noise_ratio=0.2, seed=42)
    assert len(noisy) == len(sample), "Noise injection lost products"
    print(f"✅ Noise injection works")

    return True


def test_attack_generation():
    """Test that attacks work with unified structure products."""
    print("\n" + "=" * 70)
    print("TEST 3: Attack Generation (attacks.py)")
    print("=" * 70)

    loader = UnifiedDataLoader("data/products_master.json")
    products = loader.sample_products(5, strategy="random", seed=42)

    generator = AttackGenerator(enable_noise=True, seed=42)

    # Test each attack type
    target = products[0]
    competitors = [p["name"] for p in products[1:]]

    for attack_type in AttackType:
        attack = generator.generate_attack(
            attack_type=attack_type,
            target_product=target["name"],
            competitors=competitors if attack_type == AttackType.DISCREDITATION else None
        )
        assert attack.content, f"Attack {attack_type.value} generated empty content"
        assert attack.target_product == target["name"], "Attack target mismatch"
        print(f"✅ {attack_type.value} attack generated successfully")

    # Test attack injection into content
    original_desc = target["description"]
    attack = generator.generate_attack(
        attack_type=AttackType.PERSUASION,
        target_product=target["name"]
    )

    injected = generator.inject_into_content(original_desc, attack, position="end")
    assert len(injected) > len(original_desc), "Attack not injected"
    assert attack.content in injected, "Attack content not found in injected text"
    print(f"✅ Attack injection into description works")

    return True


def test_product_dataclass_compatibility():
    """Test that products can be converted to Product dataclass."""
    print("\n" + "=" * 70)
    print("TEST 4: Product Dataclass Compatibility")
    print("=" * 70)

    loader = UnifiedDataLoader("data/products_master.json")
    products_dict = loader.sample_products(5, strategy="random", seed=42)

    # Convert to Product dataclass (used in experiments.py and ranking.py)
    products_obj = []
    for p in products_dict:
        product = Product(
            id=p["id"],
            name=p["name"],
            description=p["description"],
            category=p.get("category"),
            metadata={
                "price": p.get("price"),
                "rating": p.get("rating"),
                "brand": p.get("brand")
            }
        )
        products_obj.append(product)

    assert len(products_obj) == 5, "Conversion to Product dataclass failed"
    print(f"✅ Converted {len(products_obj)} products to Product dataclass")

    # Verify all fields accessible
    for product in products_obj:
        assert product.id, "Product ID missing"
        assert product.name, "Product name missing"
        assert product.description, "Product description missing"
        assert product.category, "Product category missing"
        assert product.metadata, "Product metadata missing"

    print(f"✅ All Product dataclass fields accessible")

    return True


def test_attack_documents():
    """Test that hardcoded attack documents work."""
    print("\n" + "=" * 70)
    print("TEST 5: Hardcoded Attack Documents")
    print("=" * 70)

    attack_docs = create_attack_documents()

    assert len(attack_docs) == 3, f"Expected 3 attack documents, got {len(attack_docs)}"
    print(f"✅ Created {len(attack_docs)} attack documents")

    attack_types = {
        "prompt_injection": False,
        "discreditation": False,
        "persuasion": False
    }

    for doc in attack_docs:
        attack_type = doc.get("_attack_type")
        assert attack_type in attack_types, f"Unknown attack type: {attack_type}"
        attack_types[attack_type] = True

        # Verify attack is in description
        assert doc.get("description"), "Attack document missing description"
        assert doc.get("content"), "Attack document missing content"
        assert doc.get("content") == doc.get("description"), "Content != description"

        print(f"✅ {attack_type}: {doc['name']}")

    assert all(attack_types.values()), "Not all attack types present"

    return True


def prepare_geobench_migration():
    """Prepare unified structure for geobench migration."""
    print("\n" + "=" * 70)
    print("GEOBENCH MIGRATION PREPARATION")
    print("=" * 70)

    # Load current unified structure
    with open("data/products_master.json", "r") as f:
        unified = json.load(f)

    # Verify structure for geobench
    assert "metadata" in unified, "Missing metadata section"
    assert "categories" in unified, "Missing categories section"

    metadata = unified["metadata"]
    assert metadata["format_version"] == "unified_v1", "Wrong format version"
    assert metadata["total_products"] == 60, "Wrong product count"
    assert metadata["total_categories"] == 7, "Wrong category count"

    print(f"✅ Unified structure ready for geobench migration")
    print(f"\nCurrent location: data/products_master.json")
    print(f"Target location: geobench/Datasets/AdversarialSEO/")
    print(f"\nStructure details:")
    print(f"  Format version: {metadata['format_version']}")
    print(f"  Total products: {metadata['total_products']}")
    print(f"  Total categories: {metadata['total_categories']}")
    print(f"\nCategory distribution:")
    for cat, count in sorted(metadata["category_distribution"].items()):
        print(f"    {cat}: {count} products")

    # Show what needs to be migrated
    print(f"\n📦 Files to migrate to geobench:")
    print(f"  1. data/products_master.json (unified structure)")
    print(f"  2. data/noise_documents.json (20 noise docs)")
    print(f"  3. src/benchmark_utils.py (benchmark utilities)")
    print(f"  4. scripts/migrate_to_unified_format.py (migration tool)")

    return True


def main():
    """Run all verification tests."""
    print("\n" + "=" * 70)
    print("COMPREHENSIVE COMPATIBILITY VERIFICATION")
    print("=" * 70)
    print("\nVerifying that all code works with unified data structure...")

    tests = [
        ("Data Loading", test_data_loading),
        ("Benchmark Utilities", test_benchmark_utilities),
        ("Attack Generation", test_attack_generation),
        ("Product Dataclass Compatibility", test_product_dataclass_compatibility),
        ("Hardcoded Attack Documents", test_attack_documents),
        ("Geobench Migration Prep", prepare_geobench_migration)
    ]

    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success, None))
        except Exception as e:
            results.append((name, False, str(e)))
            print(f"\n❌ {name} FAILED: {e}")
            import traceback
            traceback.print_exc()

    # Summary
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, success, _ in results if success)
    total = len(results)

    for name, success, error in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {name}")
        if error:
            print(f"         Error: {error}")

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("\n✅ Unified data structure is fully compatible")
        print("✅ All code works correctly")
        print("✅ Ready for geobench migration")
        print("\nNext steps:")
        print("  1. Review unified structure: data/products_master.json")
        print("  2. Migrate to geobench/Datasets/AdversarialSEO/")
        print("  3. Run /sc:cleanup to remove old code")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        print("\nPlease review errors above before proceeding.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
