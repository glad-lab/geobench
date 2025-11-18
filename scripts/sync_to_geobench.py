#!/usr/bin/env python3
"""
Sync all data formats to geobench repository.

Copies all three data formats to the geobench Datasets/AdversarialSEO directory:
    - Unified master JSON
    - Category-grouped JSONs
    - Individual product JSONs
"""

import sys
import shutil
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def sync_to_geobench():
    """Sync all data formats to geobench repository."""
    # Source paths (adversarial-seo)
    source_base = project_root / "data"
    source_unified = source_base / "products_master.json"
    source_categories = source_base / "categories"
    source_products = source_base / "products"

    # Target paths (geobench)
    geobench_base = Path("/Users/freddy/Documents/FORTIS/geobench/Datasets/AdversarialSEO")
    target_unified = geobench_base / "adversarial-seo-unified.json"
    target_categories = geobench_base / "by-category"
    target_products = geobench_base / "by-product"

    print("🔄 Syncing data to geobench repository...")
    print()

    # Verify source files exist
    if not source_unified.exists():
        print(f"❌ Error: Source unified file not found: {source_unified}")
        return False

    if not source_categories.exists() or not list(source_categories.glob("*.json")):
        print(f"❌ Error: No category files found in: {source_categories}")
        print("   Run 'python scripts/export_data_formats.py' first")
        return False

    if not source_products.exists() or not list(source_products.glob("*.json")):
        print(f"❌ Error: No product files found in: {source_products}")
        print("   Run 'python scripts/export_data_formats.py' first")
        return False

    # Create geobench directory if it doesn't exist
    geobench_base.mkdir(parents=True, exist_ok=True)
    target_categories.mkdir(parents=True, exist_ok=True)
    target_products.mkdir(parents=True, exist_ok=True)

    # 1. Copy unified master JSON
    print(f"1. Copying unified master JSON...")
    print(f"   Source: {source_unified}")
    print(f"   Target: {target_unified}")
    shutil.copy2(source_unified, target_unified)
    print(f"   ✅ Copied")
    print()

    # 2. Copy category-grouped JSONs
    print(f"2. Copying category-grouped JSONs...")
    print(f"   Source: {source_categories}")
    print(f"   Target: {target_categories}")

    category_files = list(source_categories.glob("*.json"))
    for src_file in category_files:
        target_file = target_categories / src_file.name
        shutil.copy2(src_file, target_file)
        print(f"   ✅ {src_file.name}")

    print(f"   Total: {len(category_files)} category files")
    print()

    # 3. Copy individual product JSONs
    print(f"3. Copying individual product JSONs...")
    print(f"   Source: {source_products}")
    print(f"   Target: {target_products}")

    product_files = list(source_products.glob("*.json"))
    copied_count = 0

    for src_file in product_files:
        target_file = target_products / src_file.name
        shutil.copy2(src_file, target_file)
        copied_count += 1

        # Print progress every 10 files
        if copied_count % 10 == 0:
            print(f"   ... {copied_count} files copied")

    print(f"   ✅ Total: {copied_count} product files")
    print()

    # 4. Verify integrity
    print("4. Verifying data integrity...")
    integrity_ok = verify_data_integrity(target_unified, target_categories, target_products)

    if integrity_ok:
        print("   ✅ Data integrity verified")
    else:
        print("   ⚠️  Data integrity check found issues")

    print()
    print("=" * 60)
    print("✅ Sync complete!")
    print()
    print(f"Data synced to: {geobench_base}")
    print(f"   - Unified: adversarial-seo-unified.json")
    print(f"   - Categories: by-category/ ({len(category_files)} files)")
    print(f"   - Products: by-product/ ({copied_count} files)")
    print("=" * 60)

    return True


def verify_data_integrity(unified_file, categories_dir, products_dir):
    """
    Verify data integrity across all formats.

    Args:
        unified_file: Path to unified JSON
        categories_dir: Directory with category JSONs
        products_dir: Directory with product JSONs

    Returns:
        True if integrity check passes
    """
    try:
        # Load unified data
        with open(unified_file, 'r', encoding='utf-8') as f:
            unified_data = json.load(f)

        # Count products in unified format
        unified_products = 0
        if "categories" in unified_data:
            for category, category_info in unified_data["categories"].items():
                if isinstance(category_info, dict) and "items" in category_info:
                    unified_products += len(category_info["items"])
                else:
                    unified_products += len(category_info)
        else:
            for key, value in unified_data.items():
                if isinstance(value, list):
                    unified_products += len(value)

        # Count category files
        category_count = len(list(categories_dir.glob("*.json")))

        # Count product files
        product_count = len(list(products_dir.glob("*.json")))

        print(f"   Unified format: {unified_products} products")
        print(f"   Category files: {category_count} files")
        print(f"   Product files: {product_count} files")

        # Basic integrity check
        if product_count != unified_products:
            print(f"   ⚠️  Warning: Product count mismatch ({product_count} vs {unified_products})")
            return False

        return True

    except Exception as e:
        print(f"   ❌ Error during integrity check: {e}")
        return False


def main():
    """Main entry point."""
    success = sync_to_geobench()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
