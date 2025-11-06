"""
Benchmark utility functions for GEO (adversarial SEO) methodology evaluation.

This module provides utilities to support various benchmark angles:
1. Changing product/retrieval item count
2. Changing order of products
3. Replicating papers on other datasets
4. Gauging efficacy of different LLMs
5. Ground truth availability effects
6. Anomaly type effects
7. Noise effects
8. Data cropping effects
9. Irrelevant feature effects
10. Performance accuracy + efficiency metrics
"""

import json
import random
import time
import psutil
import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Callable
from pathlib import Path
from dataclasses import dataclass
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class BenchmarkMetrics:
    """Container for benchmark performance metrics."""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    execution_time_ms: float
    memory_usage_mb: float
    gpu_memory_mb: Optional[float] = None
    token_count: Optional[int] = None


class UnifiedDataLoader:
    """
    Load and manipulate products from unified category-based structure.

    Supports filtering, sampling, and transformations for benchmark experiments.
    """

    def __init__(self, data_path: str = "data/products_master.json"):
        """
        Initialize the data loader.

        Args:
            data_path: Path to unified products JSON file
        """
        self.data_path = Path(data_path)
        self.data = self._load_data()
        self.products = self._extract_products()
        self.categories = self._extract_categories()

    def _load_data(self) -> Dict[str, Any]:
        """Load raw JSON data."""
        with open(self.data_path, "r") as f:
            return json.load(f)

    def _extract_products(self) -> List[Dict[str, Any]]:
        """Extract all products from categories into flat list."""
        products = []

        if "categories" in self.data:
            for category_name, category_data in self.data["categories"].items():
                for item in category_data.get("items", []):
                    if "category" not in item:
                        item["category"] = category_name
                    products.append(item)

        return products

    def _extract_categories(self) -> Dict[str, List[Dict[str, Any]]]:
        """Extract products grouped by category."""
        categories = defaultdict(list)

        for product in self.products:
            category = product.get("category", "Uncategorized")
            categories[category].append(product)

        return dict(categories)

    def get_all_products(self) -> List[Dict[str, Any]]:
        """Get all products."""
        return self.products.copy()

    def get_category_products(self, category: str) -> List[Dict[str, Any]]:
        """Get products from specific category."""
        return self.categories.get(category, []).copy()

    def get_categories(self) -> List[str]:
        """Get list of all categories."""
        return list(self.categories.keys())

    def sample_products(
        self,
        n: int,
        strategy: str = "random",
        category: Optional[str] = None,
        seed: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Sample n products using specified strategy.

        Args:
            n: Number of products to sample
            strategy: Sampling strategy ('random', 'stratified', 'top_rated', 'diverse')
            category: Specific category to sample from (None = all categories)
            seed: Random seed for reproducibility

        Returns:
            List of sampled products
        """
        if seed is not None:
            random.seed(seed)

        source_products = (
            self.get_category_products(category) if category
            else self.get_all_products()
        )

        if strategy == "random":
            return random.sample(source_products, min(n, len(source_products)))

        elif strategy == "stratified":
            # Sample proportionally from each category
            samples = []
            per_category = max(1, n // len(self.categories))

            for cat_products in self.categories.values():
                samples.extend(
                    random.sample(cat_products, min(per_category, len(cat_products)))
                )

            return samples[:n]

        elif strategy == "top_rated":
            # Sample highest rated products
            sorted_products = sorted(
                source_products,
                key=lambda p: p.get("rating", 0),
                reverse=True
            )
            return sorted_products[:n]

        elif strategy == "diverse":
            # Ensure at least one from each category
            samples = []
            for cat_products in self.categories.values():
                if cat_products and len(samples) < n:
                    samples.append(random.choice(cat_products))

            # Fill remaining with random
            if len(samples) < n:
                remaining = [p for p in source_products if p not in samples]
                samples.extend(
                    random.sample(remaining, min(n - len(samples), len(remaining)))
                )

            return samples[:n]

        else:
            raise ValueError(f"Unknown sampling strategy: {strategy}")


class ProductManipulator:
    """
    Manipulate product data for benchmark experiments.

    Supports ordering, cropping, noise injection, and feature manipulation.
    """

    @staticmethod
    def change_order(
        products: List[Dict[str, Any]],
        order_strategy: str = "random",
        seed: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Change order of products.

        Args:
            products: List of products
            order_strategy: Ordering strategy ('random', 'reverse', 'by_rating',
                          'by_price', 'by_category', 'alternating_category')
            seed: Random seed for reproducibility

        Returns:
            Reordered products
        """
        if seed is not None:
            random.seed(seed)

        products_copy = products.copy()

        if order_strategy == "random":
            random.shuffle(products_copy)

        elif order_strategy == "reverse":
            products_copy.reverse()

        elif order_strategy == "by_rating":
            products_copy.sort(key=lambda p: p.get("rating", 0), reverse=True)

        elif order_strategy == "by_price":
            products_copy.sort(key=lambda p: p.get("price", 0))

        elif order_strategy == "by_category":
            products_copy.sort(key=lambda p: p.get("category", ""))

        elif order_strategy == "alternating_category":
            # Group by category then alternate
            by_category = defaultdict(list)
            for p in products_copy:
                by_category[p.get("category", "Unknown")].append(p)

            result = []
            while any(by_category.values()):
                for category in sorted(by_category.keys()):
                    if by_category[category]:
                        result.append(by_category[category].pop(0))

            products_copy = result

        return products_copy

    @staticmethod
    def add_noise(
        products: List[Dict[str, Any]],
        noise_ratio: float = 0.1,
        noise_type: str = "description",
        seed: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Add noise to product data.

        Args:
            products: List of products
            noise_ratio: Ratio of products to add noise to (0.0-1.0)
            noise_type: Type of noise ('description', 'price', 'rating', 'all')
            seed: Random seed

        Returns:
            Products with noise added
        """
        if seed is not None:
            random.seed(seed)

        products_copy = [p.copy() for p in products]
        num_noisy = int(len(products_copy) * noise_ratio)
        noisy_indices = random.sample(range(len(products_copy)), num_noisy)

        noise_words = ["random", "irrelevant", "noise", "test", "placeholder"]

        for idx in noisy_indices:
            product = products_copy[idx]

            if noise_type in ("description", "all"):
                noise_text = " ".join(random.choices(noise_words, k=5))
                product["description"] = f"{product.get('description', '')} {noise_text}"

            if noise_type in ("price", "all"):
                product["price"] = product.get("price", 100) * random.uniform(0.5, 1.5)

            if noise_type in ("rating", "all"):
                product["rating"] = min(5.0, max(0.0,
                    product.get("rating", 4.0) + random.uniform(-1.0, 1.0)))

        return products_copy

    @staticmethod
    def crop_data(
        products: List[Dict[str, Any]],
        crop_strategy: str = "random",
        crop_ratio: float = 0.5,
        seed: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Crop product dataset.

        Args:
            products: List of products
            crop_strategy: Strategy ('random', 'top', 'bottom', 'category_balanced')
            crop_ratio: Ratio of products to keep (0.0-1.0)
            seed: Random seed

        Returns:
            Cropped products
        """
        if seed is not None:
            random.seed(seed)

        keep_count = int(len(products) * crop_ratio)

        if crop_strategy == "random":
            return random.sample(products, keep_count)

        elif crop_strategy == "top":
            return products[:keep_count]

        elif crop_strategy == "bottom":
            return products[-keep_count:]

        elif crop_strategy == "category_balanced":
            # Keep proportional number from each category
            by_category = defaultdict(list)
            for p in products:
                by_category[p.get("category", "Unknown")].append(p)

            result = []
            per_category = keep_count // len(by_category)

            for cat_products in by_category.values():
                result.extend(random.sample(
                    cat_products,
                    min(per_category, len(cat_products))
                ))

            return result[:keep_count]

        return products[:keep_count]

    @staticmethod
    def add_irrelevant_features(
        products: List[Dict[str, Any]],
        num_features: int = 5,
        seed: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Add irrelevant random features to products.

        Args:
            products: List of products
            num_features: Number of irrelevant features to add
            seed: Random seed

        Returns:
            Products with irrelevant features
        """
        if seed is not None:
            random.seed(seed)

        products_copy = [p.copy() for p in products]

        irrelevant_feature_names = [
            "random_score", "noise_metric", "irrelevant_value",
            "dummy_attribute", "placeholder_field", "test_property",
            "synthetic_measure", "arbitrary_rating", "meaningless_stat"
        ]

        for product in products_copy:
            for i in range(num_features):
                feature_name = random.choice(irrelevant_feature_names)
                product[f"{feature_name}_{i}"] = random.uniform(0, 100)

        return products_copy


class GroundTruthManager:
    """
    Manage ground truth rankings for benchmark evaluation.

    Supports different ground truth availability scenarios.
    """

    @staticmethod
    def create_ground_truth(
        products: List[Dict[str, Any]],
        ranking_criterion: str = "rating",
        seed: Optional[int] = None
    ) -> Dict[str, int]:
        """
        Create ground truth ranking.

        Args:
            products: List of products
            ranking_criterion: Criterion for ranking ('rating', 'price', 'random')
            seed: Random seed

        Returns:
            Dictionary mapping product ID to ground truth rank (1-indexed)
        """
        if seed is not None:
            random.seed(seed)

        if ranking_criterion == "rating":
            sorted_products = sorted(
                products,
                key=lambda p: p.get("rating", 0),
                reverse=True
            )
        elif ranking_criterion == "price":
            sorted_products = sorted(
                products,
                key=lambda p: p.get("price", 0)
            )
        elif ranking_criterion == "random":
            sorted_products = products.copy()
            random.shuffle(sorted_products)
        else:
            sorted_products = products

        return {p["id"]: rank + 1 for rank, p in enumerate(sorted_products)}

    @staticmethod
    def simulate_partial_ground_truth(
        ground_truth: Dict[str, int],
        availability_ratio: float = 0.5,
        seed: Optional[int] = None
    ) -> Dict[str, int]:
        """
        Simulate partial ground truth availability.

        Args:
            ground_truth: Complete ground truth
            availability_ratio: Ratio of ground truth available (0.0-1.0)
            seed: Random seed

        Returns:
            Partial ground truth dictionary
        """
        if seed is not None:
            random.seed(seed)

        all_ids = list(ground_truth.keys())
        keep_count = int(len(all_ids) * availability_ratio)
        kept_ids = random.sample(all_ids, keep_count)

        return {id_: rank for id_, rank in ground_truth.items() if id_ in kept_ids}


class PerformanceProfiler:
    """
    Profile performance metrics for benchmark experiments.

    Tracks execution time, memory usage, and resource efficiency.
    """

    def __init__(self):
        """Initialize the profiler."""
        self.start_time = None
        self.start_memory = None
        self.process = psutil.Process()

    def start(self):
        """Start profiling."""
        self.start_time = time.time()
        self.start_memory = self.process.memory_info().rss / 1024 / 1024  # MB

    def stop(self) -> Dict[str, float]:
        """
        Stop profiling and return metrics.

        Returns:
            Dictionary with performance metrics
        """
        if self.start_time is None:
            raise RuntimeError("Profiler not started")

        execution_time_ms = (time.time() - self.start_time) * 1000
        current_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        memory_delta = current_memory - self.start_memory

        return {
            "execution_time_ms": execution_time_ms,
            "memory_usage_mb": current_memory,
            "memory_delta_mb": memory_delta,
            "cpu_percent": self.process.cpu_percent()
        }


class AnomalyInjector:
    """
    Inject different types of anomalies into product data.

    Supports outliers, inconsistencies, and data quality issues.
    """

    @staticmethod
    def inject_anomalies(
        products: List[Dict[str, Any]],
        anomaly_type: str = "price_outlier",
        anomaly_ratio: float = 0.1,
        seed: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Inject anomalies into product data.

        Args:
            products: List of products
            anomaly_type: Type of anomaly ('price_outlier', 'rating_inconsistent',
                        'missing_description', 'duplicate_content')
            anomaly_ratio: Ratio of products with anomalies
            seed: Random seed

        Returns:
            Products with anomalies injected
        """
        if seed is not None:
            random.seed(seed)

        products_copy = [p.copy() for p in products]
        num_anomalies = int(len(products_copy) * anomaly_ratio)
        anomaly_indices = random.sample(range(len(products_copy)), num_anomalies)

        for idx in anomaly_indices:
            product = products_copy[idx]

            if anomaly_type == "price_outlier":
                # Make price 10x higher or lower
                multiplier = random.choice([0.1, 10.0])
                product["price"] = product.get("price", 100) * multiplier

            elif anomaly_type == "rating_inconsistent":
                # High rating but negative description
                product["rating"] = 5.0
                product["description"] = "Terrible product. Do not buy. " + product.get("description", "")

            elif anomaly_type == "missing_description":
                # Remove description
                product["description"] = ""

            elif anomaly_type == "duplicate_content":
                # Duplicate another product's content
                other_product = random.choice(products_copy)
                product["description"] = other_product.get("description", "")

        return products_copy


def create_benchmark_config(
    num_products: int = 10,
    order_strategy: str = "random",
    ground_truth_ratio: float = 1.0,
    noise_ratio: float = 0.0,
    crop_ratio: float = 1.0,
    anomaly_type: Optional[str] = None,
    anomaly_ratio: float = 0.0,
    add_irrelevant_features: bool = False,
    seed: Optional[int] = None
) -> Dict[str, Any]:
    """
    Create a benchmark configuration.

    This consolidates all benchmark angle settings into a single config.

    Args:
        num_products: Number of products to include
        order_strategy: Product ordering strategy
        ground_truth_ratio: Ratio of ground truth available
        noise_ratio: Ratio of products with noise
        crop_ratio: Ratio of dataset to keep
        anomaly_type: Type of anomaly to inject
        anomaly_ratio: Ratio of products with anomalies
        add_irrelevant_features: Whether to add irrelevant features
        seed: Random seed for reproducibility

    Returns:
        Benchmark configuration dictionary
    """
    return {
        "num_products": num_products,
        "order_strategy": order_strategy,
        "ground_truth_ratio": ground_truth_ratio,
        "noise_ratio": noise_ratio,
        "crop_ratio": crop_ratio,
        "anomaly_type": anomaly_type,
        "anomaly_ratio": anomaly_ratio,
        "add_irrelevant_features": add_irrelevant_features,
        "seed": seed
    }
