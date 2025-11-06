"""
Dataset loading with format detection and unified conversion.

Supports multiple dataset formats:
- Unified format: {"categories": {...}}
- Flat format: [...]
- Legacy formats
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from collections import defaultdict

from .sampling import SamplingStrategy

logger = logging.getLogger(__name__)


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
        self.format = self.detect_format(self.data)
        self.products = self._extract_products()
        self.categories = self._extract_categories()

        logger.info(
            f"Loaded {len(self.products)} products in {self.format} format "
            f"from {len(self.categories)} categories"
        )

    def _load_data(self) -> Dict[str, Any]:
        """Load raw JSON data."""
        try:
            with open(self.data_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Data file not found: {self.data_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {self.data_path}: {e}")

    def detect_format(self, data: Any) -> str:
        """
        Detect dataset format.

        Args:
            data: Loaded JSON data

        Returns:
            Format string: 'unified', 'flat', 'direct_categories', or 'unknown'
        """
        if isinstance(data, dict):
            if "categories" in data:
                return "unified"
            elif "products" in data:
                return "legacy_dict"
            # Check if this is a dict with category names as keys
            # Each category should have a list of items
            elif all(isinstance(v, list) for v in data.values() if v):
                return "direct_categories"
        elif isinstance(data, list):
            return "flat"

        return "unknown"

    def _extract_products(self) -> List[Dict[str, Any]]:
        """Extract all products from categories into flat list."""
        products = []

        if self.format == "unified":
            for category_name, category_data in self.data["categories"].items():
                for item in category_data.get("items", []):
                    if "category" not in item:
                        item["category"] = category_name
                    products.append(item)

        elif self.format == "direct_categories":
            # Categories are directly at top level, values are lists of products
            for category_name, items in self.data.items():
                for item in items:
                    if "category" not in item:
                        item["category"] = category_name
                    products.append(item)

        elif self.format == "flat":
            products = self.data

        elif self.format == "legacy_dict":
            products = self.data.get("products", [])

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

    def get_stats(self) -> Dict[str, Any]:
        """
        Get dataset statistics.

        Returns:
            Dictionary with dataset statistics
        """
        return {
            "total_products": len(self.products),
            "total_categories": len(self.categories),
            "format": self.format,
            "category_distribution": {
                cat: len(prods) for cat, prods in self.categories.items()
            },
            "avg_products_per_category": (
                len(self.products) / len(self.categories)
                if self.categories else 0
            ),
        }

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
            strategy: Sampling strategy ('random', 'stratified', 'weighted', 'diverse')
            category: Specific category to sample from (None = all categories)
            seed: Random seed for reproducibility

        Returns:
            List of sampled products
        """
        source_products = (
            self.get_category_products(category) if category
            else self.get_all_products()
        )

        if strategy == "random":
            return SamplingStrategy.random_sample(source_products, n, seed)

        elif strategy == "stratified":
            return SamplingStrategy.stratified_sample(
                source_products, n, "category", seed
            )

        elif strategy == "weighted":
            return SamplingStrategy.weighted_sample(
                source_products, n, "rating", seed
            )

        elif strategy == "diverse":
            return self._diverse_sample(source_products, n, seed)

        else:
            raise ValueError(f"Unknown sampling strategy: {strategy}")

    def _diverse_sample(
        self,
        products: List[Dict[str, Any]],
        n: int,
        seed: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Ensure at least one from each category, then fill randomly.

        Args:
            products: List of products
            n: Number to sample
            seed: Random seed

        Returns:
            Diverse sample of products
        """
        import random
        if seed is not None:
            random.seed(seed)

        samples = []
        for cat_products in self.categories.values():
            if cat_products and len(samples) < n:
                samples.append(random.choice(cat_products))

        # Fill remaining with random
        if len(samples) < n:
            remaining = [p for p in products if p not in samples]
            samples.extend(
                random.sample(remaining, min(n - len(samples), len(remaining)))
            )

        return samples[:n]
