#!/usr/bin/env python3
"""
Demonstration of unified data structure and benchmark utilities.

This script shows how to use the new category-based structure and
benchmark utilities for GEO methodology evaluation.
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from benchmark_utils import (
    UnifiedDataLoader,
    ProductManipulator,
    GroundTruthManager,
    PerformanceProfiler,
    AnomalyInjector,
    create_benchmark_config
)


def demo_unified_loader():
    """Demonstrate unified data loading capabilities."""
    print("\n" + "=" * 70)
    print("DEMO 1: Unified Data Loader")
    print("=" * 70)

    loader = UnifiedDataLoader("data/products_master.json")

    print(f"\nTotal products: {len(loader.get_all_products())}")
    print(f"Total categories: {len(loader.get_categories())}")
    print(f"\nCategories: {', '.join(loader.get_categories())}")

    # Sample products using different strategies
    print("\n--- Sampling Strategies ---")

    random_sample = loader.sample_products(5, strategy="random", seed=42)
    print(f"Random sample: {len(random_sample)} products")

    stratified_sample = loader.sample_products(10, strategy="stratified", seed=42)
    print(f"Stratified sample: {len(stratified_sample)} products")

    top_rated = loader.sample_products(5, strategy="top_rated")
    print(f"Top rated sample: {len(top_rated)} products")
    for p in top_rated:
        print(f"  • {p['name']} (Rating: {p['rating']})")

    # Sample from specific category
    camera_products = loader.get_category_products("Cameras")
    print(f"\nCameras category: {len(camera_products)} products")


def demo_product_manipulation():
    """Demonstrate product manipulation for benchmarks."""
    print("\n" + "=" * 70)
    print("DEMO 2: Product Manipulation")
    print("=" * 70)

    loader = UnifiedDataLoader("data/products_master.json")
    products = loader.sample_products(10, strategy="random", seed=42)

    print(f"\nOriginal order (first 3):")
    for i, p in enumerate(products[:3]):
        print(f"  {i+1}. {p['name']} (Category: {p['category']})")

    # Change ordering
    print("\n--- Reordering Strategies ---")

    by_rating = ProductManipulator.change_order(
        products, order_strategy="by_rating"
    )
    print(f"\nBy rating (first 3):")
    for i, p in enumerate(by_rating[:3]):
        print(f"  {i+1}. {p['name']} (Rating: {p['rating']})")

    alternating = ProductManipulator.change_order(
        products, order_strategy="alternating_category", seed=42
    )
    print(f"\nAlternating category (first 5):")
    for i, p in enumerate(alternating[:5]):
        print(f"  {i+1}. {p['name']} (Category: {p['category']})")

    # Add noise
    print("\n--- Adding Noise ---")
    noisy = ProductManipulator.add_noise(
        products, noise_ratio=0.3, noise_type="description", seed=42
    )
    print(f"Added noise to {int(len(products) * 0.3)} products")

    # Crop data
    print("\n--- Data Cropping ---")
    cropped = ProductManipulator.crop_data(
        products, crop_strategy="random", crop_ratio=0.5, seed=42
    )
    print(f"Cropped dataset: {len(cropped)} products (50% of {len(products)})")


def demo_ground_truth():
    """Demonstrate ground truth management."""
    print("\n" + "=" * 70)
    print("DEMO 3: Ground Truth Management")
    print("=" * 70)

    loader = UnifiedDataLoader("data/products_master.json")
    products = loader.sample_products(8, strategy="random", seed=42)

    # Create ground truth
    ground_truth = GroundTruthManager.create_ground_truth(
        products, ranking_criterion="rating", seed=42
    )

    print("\nGround Truth Rankings (by rating):")
    sorted_gt = sorted(ground_truth.items(), key=lambda x: x[1])
    for prod_id, rank in sorted_gt[:5]:
        product = next(p for p in products if p['id'] == prod_id)
        print(f"  Rank {rank}: {product['name']} (Rating: {product['rating']})")

    # Simulate partial ground truth
    print("\n--- Partial Ground Truth (50% available) ---")
    partial_gt = GroundTruthManager.simulate_partial_ground_truth(
        ground_truth, availability_ratio=0.5, seed=42
    )
    print(f"Complete ground truth: {len(ground_truth)} products")
    print(f"Partial ground truth: {len(partial_gt)} products")


def demo_performance_profiling():
    """Demonstrate performance profiling."""
    print("\n" + "=" * 70)
    print("DEMO 4: Performance Profiling")
    print("=" * 70)

    profiler = PerformanceProfiler()

    print("\nProfiling a sample operation...")
    profiler.start()

    # Simulate some work
    loader = UnifiedDataLoader("data/products_master.json")
    products = loader.get_all_products()

    for _ in range(1000):
        ProductManipulator.change_order(products, order_strategy="random")

    metrics = profiler.stop()

    print(f"\nPerformance Metrics:")
    print(f"  Execution time: {metrics['execution_time_ms']:.2f} ms")
    print(f"  Memory usage: {metrics['memory_usage_mb']:.2f} MB")
    print(f"  Memory delta: {metrics['memory_delta_mb']:.2f} MB")
    print(f"  CPU usage: {metrics['cpu_percent']:.1f}%")


def demo_anomaly_injection():
    """Demonstrate anomaly injection."""
    print("\n" + "=" * 70)
    print("DEMO 5: Anomaly Injection")
    print("=" * 70)

    loader = UnifiedDataLoader("data/products_master.json")
    products = loader.sample_products(10, strategy="random", seed=42)

    print(f"\nOriginal products (first 3):")
    for p in products[:3]:
        print(f"  • {p['name']} - ${p['price']:.2f}")

    # Inject price outliers
    print("\n--- Price Outlier Injection (30% of products) ---")
    with_outliers = AnomalyInjector.inject_anomalies(
        products, anomaly_type="price_outlier", anomaly_ratio=0.3, seed=42
    )

    print(f"\nProducts with anomalies (showing first 5):")
    for p in with_outliers[:5]:
        print(f"  • {p['name']} - ${p['price']:.2f}")


def demo_benchmark_config():
    """Demonstrate benchmark configuration."""
    print("\n" + "=" * 70)
    print("DEMO 6: Benchmark Configuration")
    print("=" * 70)

    # Create different benchmark scenarios
    scenarios = [
        ("Baseline", create_benchmark_config(
            num_products=10,
            seed=42
        )),
        ("With Noise", create_benchmark_config(
            num_products=10,
            noise_ratio=0.2,
            seed=42
        )),
        ("Partial Ground Truth", create_benchmark_config(
            num_products=10,
            ground_truth_ratio=0.5,
            seed=42
        )),
        ("With Anomalies", create_benchmark_config(
            num_products=10,
            anomaly_type="price_outlier",
            anomaly_ratio=0.2,
            seed=42
        )),
        ("Complex Scenario", create_benchmark_config(
            num_products=20,
            order_strategy="alternating_category",
            ground_truth_ratio=0.7,
            noise_ratio=0.1,
            anomaly_type="rating_inconsistent",
            anomaly_ratio=0.1,
            add_irrelevant_features=True,
            seed=42
        ))
    ]

    for name, config in scenarios:
        print(f"\n--- {name} Scenario ---")
        print(f"  Products: {config['num_products']}")
        print(f"  Order strategy: {config['order_strategy']}")
        print(f"  Ground truth ratio: {config['ground_truth_ratio']}")
        print(f"  Noise ratio: {config['noise_ratio']}")
        if config['anomaly_type']:
            print(f"  Anomaly type: {config['anomaly_type']} ({config['anomaly_ratio']})")
        print(f"  Irrelevant features: {config['add_irrelevant_features']}")


def main():
    """Run all demonstrations."""
    print("\n" + "=" * 70)
    print("UNIFIED DATA STRUCTURE & BENCHMARK UTILITIES DEMONSTRATION")
    print("=" * 70)

    try:
        demo_unified_loader()
        demo_product_manipulation()
        demo_ground_truth()
        demo_performance_profiling()
        demo_anomaly_injection()
        demo_benchmark_config()

        print("\n" + "=" * 70)
        print("DEMONSTRATION COMPLETE")
        print("=" * 70)
        print("\nAll benchmark utilities are working correctly!")
        print("You can now use these tools for comprehensive GEO methodology evaluation.")

    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
