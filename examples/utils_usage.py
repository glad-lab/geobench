"""
Example usage of src.utils package.

Demonstrates:
- Loading datasets in various formats
- Sampling strategies
- Product manipulation
- Data validation
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils import (
    UnifiedDataLoader,
    ProductManipulator,
    SamplingStrategy,
    DataValidator,
)


def example_1_loading_data():
    """Example 1: Load and explore dataset."""
    print("=" * 60)
    print("Example 1: Loading and Exploring Data")
    print("=" * 60)

    # Load unified format (use absolute path or check current working directory)
    data_path = Path(__file__).parent.parent / "data" / "products_master.json"
    loader = UnifiedDataLoader(str(data_path))

    # Get statistics
    stats = loader.get_stats()
    print(f"\nDataset Statistics:")
    print(f"  Total Products: {stats['total_products']}")
    print(f"  Total Categories: {stats['total_categories']}")
    print(f"  Format: {stats['format']}")
    print(f"\nCategory Distribution:")
    for category, count in stats['category_distribution'].items():
        print(f"  {category}: {count} products")

    # Get products from specific category
    electronics = loader.get_category_products("Computing Hardware")
    print(f"\nComputing Hardware Products: {len(electronics)}")
    for product in electronics[:3]:
        price = product.get('price', 'N/A')
        print(f"  - {product['name']} (${price})")


def example_2_sampling_strategies():
    """Example 2: Different sampling strategies."""
    print("\n" + "=" * 60)
    print("Example 2: Sampling Strategies")
    print("=" * 60)

    data_path = Path(__file__).parent.parent / "data" / "products_master.json"
    loader = UnifiedDataLoader(str(data_path))

    # Random sampling
    random_sample = loader.sample_products(5, strategy="random", seed=42)
    print(f"\nRandom Sample ({len(random_sample)} products):")
    for p in random_sample:
        print(f"  - {p['name']} ({p['category']})")

    # Stratified sampling
    stratified_sample = loader.sample_products(10, strategy="stratified", seed=42)
    print(f"\nStratified Sample ({len(stratified_sample)} products):")
    categories = {}
    for p in stratified_sample:
        cat = p['category']
        categories[cat] = categories.get(cat, 0) + 1
    for cat, count in categories.items():
        print(f"  {cat}: {count} products")

    # Weighted sampling (by rating)
    weighted_sample = loader.sample_products(5, strategy="weighted", seed=42)
    print(f"\nWeighted Sample by Rating ({len(weighted_sample)} products):")
    for p in weighted_sample:
        print(f"  - {p['name']} (rating: {p['rating']})")

    # Diverse sampling
    diverse_sample = loader.sample_products(7, strategy="diverse", seed=42)
    print(f"\nDiverse Sample ({len(diverse_sample)} products):")
    categories = set(p['category'] for p in diverse_sample)
    print(f"  Unique categories: {len(categories)}")


def example_3_product_manipulation():
    """Example 3: Product manipulation."""
    print("\n" + "=" * 60)
    print("Example 3: Product Manipulation")
    print("=" * 60)

    data_path = Path(__file__).parent.parent / "data" / "products_master.json"
    loader = UnifiedDataLoader(str(data_path))
    products = loader.sample_products(10, strategy="random", seed=42)

    # Change order
    print("\nOriginal order:")
    for i, p in enumerate(products[:3]):
        print(f"  {i+1}. {p['name']} (${p['price']}, rating: {p['rating']})")

    by_rating = ProductManipulator.change_order(products, "by_rating")
    print("\nOrdered by rating:")
    for i, p in enumerate(by_rating[:3]):
        print(f"  {i+1}. {p['name']} (${p['price']}, rating: {p['rating']})")

    by_price = ProductManipulator.change_order(products, "by_price")
    print("\nOrdered by price:")
    for i, p in enumerate(by_price[:3]):
        print(f"  {i+1}. {p['name']} (${p['price']}, rating: {p['rating']})")

    # Add noise
    noisy = ProductManipulator.add_noise(
        products, noise_ratio=0.3, noise_type="price", seed=42
    )
    print("\nAfter adding price noise (30% of products):")
    for i, (orig, noise) in enumerate(zip(products[:3], noisy[:3])):
        print(f"  {orig['name']}: ${orig['price']:.2f} → ${noise['price']:.2f}")

    # Crop data
    cropped = ProductManipulator.crop_data(
        products, crop_strategy="random", crop_ratio=0.5, seed=42
    )
    print(f"\nCropped dataset: {len(products)} → {len(cropped)} products")

    # Add irrelevant features
    with_features = ProductManipulator.add_irrelevant_features(
        products[:2], num_features=3, seed=42
    )
    print(f"\nOriginal fields: {len(products[0])} → With irrelevant features: {len(with_features[0])}")


def example_4_anomaly_injection():
    """Example 4: Anomaly injection."""
    print("\n" + "=" * 60)
    print("Example 4: Anomaly Injection")
    print("=" * 60)

    data_path = Path(__file__).parent.parent / "data" / "products_master.json"
    loader = UnifiedDataLoader(str(data_path))
    products = loader.sample_products(5, strategy="random", seed=42)

    # Price outliers
    with_outliers = ProductManipulator.inject_anomalies(
        products, anomaly_type="price_outlier", anomaly_ratio=0.4, seed=42
    )
    print("\nPrice Outlier Injection (40% of products):")
    for orig, anom in zip(products, with_outliers):
        if orig['price'] != anom['price']:
            print(f"  {anom['name']}: ${orig['price']:.2f} → ${anom['price']:.2f}")

    # Rating inconsistencies
    with_inconsistent = ProductManipulator.inject_anomalies(
        products, anomaly_type="rating_inconsistent", anomaly_ratio=0.4, seed=42
    )
    print("\nRating Inconsistency Injection:")
    for anom in with_inconsistent:
        if anom['rating'] == 5.0 and "Terrible" in anom['description']:
            print(f"  {anom['name']}: rating={anom['rating']}, but description mentions issues")


def example_5_validation():
    """Example 5: Data validation."""
    print("\n" + "=" * 60)
    print("Example 5: Data Validation")
    print("=" * 60)

    data_path = Path(__file__).parent.parent / "data" / "products_master.json"
    loader = UnifiedDataLoader(str(data_path))
    products = loader.sample_products(10, strategy="random", seed=42)

    # Schema validation
    print("\nSchema Validation:")
    schema_result = DataValidator.validate_schema(
        products, required_fields=["id", "name", "price", "rating"]
    )
    print(f"  Valid: {schema_result.is_valid}")
    print(f"  Errors: {len(schema_result.errors)}")
    print(f"  Warnings: {len(schema_result.warnings)}")

    # Duplicate checking
    print("\nDuplicate Checking:")
    duplicate_result = DataValidator.check_duplicates(products, id_field="id")
    print(f"  Valid: {duplicate_result.is_valid}")
    print(f"  Unique IDs: {duplicate_result.stats['unique_ids']}")
    print(f"  Duplicate IDs: {duplicate_result.stats['duplicate_ids']}")

    # Value validation
    print("\nValue Validation:")
    value_result = DataValidator.validate_values(products)
    print(f"  Valid: {value_result.is_valid}")
    print(f"  Value Errors: {len(value_result.errors)}")

    # Full validation
    print("\nFull Validation:")
    full_result = DataValidator.validate_all(products)
    print(f"  Valid: {full_result.is_valid}")
    print(f"  Total Errors: {full_result.stats['total_errors']}")
    print(f"  Total Warnings: {full_result.stats['total_warnings']}")


def example_6_integrated_workflow():
    """Example 6: Integrated workflow."""
    print("\n" + "=" * 60)
    print("Example 6: Integrated Workflow")
    print("=" * 60)

    # Load data
    data_path = Path(__file__).parent.parent / "data" / "products_master.json"
    loader = UnifiedDataLoader(str(data_path))
    print(f"\n1. Loaded {loader.get_stats()['total_products']} products")

    # Sample products
    products = loader.sample_products(15, strategy="stratified", seed=42)
    print(f"2. Sampled {len(products)} products using stratified strategy")

    # Validate original data
    validation = DataValidator.validate_all(products)
    print(f"3. Validated data: {validation.is_valid} (0 errors)")

    # Apply manipulations
    products = ProductManipulator.change_order(products, "by_rating")
    print(f"4. Reordered products by rating")

    products = ProductManipulator.add_noise(
        products, noise_ratio=0.2, noise_type="description", seed=42
    )
    print(f"5. Added description noise to 20% of products")

    products = ProductManipulator.crop_data(
        products, crop_strategy="top", crop_ratio=0.67
    )
    print(f"6. Cropped to {len(products)} products (top 67%)")

    # Validate manipulated data
    validation = DataValidator.validate_all(products)
    print(f"7. Validated manipulated data: {validation.is_valid}")

    # Display sample results
    print(f"\n8. Final sample (top 3):")
    for i, p in enumerate(products[:3]):
        print(f"   {i+1}. {p['name']} - ${p['price']:.2f} (rating: {p['rating']})")


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("UTILS PACKAGE USAGE EXAMPLES")
    print("=" * 60)

    try:
        example_1_loading_data()
        example_2_sampling_strategies()
        example_3_product_manipulation()
        example_4_anomaly_injection()
        example_5_validation()
        example_6_integrated_workflow()

        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60 + "\n")

    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
