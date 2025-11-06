"""
Sampling strategies for dataset experiments.

Supports:
- Random sampling
- Stratified sampling (by category)
- Weighted sampling (by rating or other field)
"""

import random
import logging
from typing import List, Dict, Any, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)


class SamplingStrategy:
    """Base class for sampling strategies."""

    @staticmethod
    def random_sample(
        products: List[Dict[str, Any]],
        n: int,
        seed: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Random sampling.

        Args:
            products: List of products
            n: Number to sample
            seed: Random seed

        Returns:
            Randomly sampled products
        """
        if seed is not None:
            random.seed(seed)

        sample_size = min(n, len(products))
        result = random.sample(products, sample_size)

        logger.debug(f"Random sampled {sample_size} products")
        return result

    @staticmethod
    def stratified_sample(
        products: List[Dict[str, Any]],
        n: int,
        category_field: str = "category",
        seed: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Stratified sampling by category.

        Ensures proportional representation from each category.

        Args:
            products: List of products
            n: Number to sample
            category_field: Field to stratify by
            seed: Random seed

        Returns:
            Stratified sample of products
        """
        if seed is not None:
            random.seed(seed)

        # Group by category
        by_category = defaultdict(list)
        for product in products:
            category = product.get(category_field, "Unknown")
            by_category[category].append(product)

        # Calculate per-category sample size
        num_categories = len(by_category)
        per_category = max(1, n // num_categories)

        # Sample from each category
        samples = []
        for category, cat_products in by_category.items():
            sample_size = min(per_category, len(cat_products))
            samples.extend(random.sample(cat_products, sample_size))

        # Trim to exact size
        result = samples[:n]

        logger.debug(
            f"Stratified sampled {len(result)} products from {num_categories} categories "
            f"(~{per_category} per category)"
        )
        return result

    @staticmethod
    def weighted_sample(
        products: List[Dict[str, Any]],
        n: int,
        weight_field: str = "rating",
        seed: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Weighted sampling based on field value.

        Higher values have higher probability of being selected.

        Args:
            products: List of products
            n: Number to sample
            weight_field: Field to use as weight
            seed: Random seed

        Returns:
            Weighted sample of products
        """
        if seed is not None:
            random.seed(seed)

        # Extract weights
        weights = [product.get(weight_field, 0) for product in products]

        # Ensure positive weights
        min_weight = min(weights)
        if min_weight < 0:
            weights = [w - min_weight + 1 for w in weights]

        # Handle all-zero weights
        if sum(weights) == 0:
            weights = [1] * len(weights)

        # Sample with replacement using weights
        sample_size = min(n, len(products))
        result = random.choices(products, weights=weights, k=sample_size)

        logger.debug(
            f"Weighted sampled {sample_size} products by '{weight_field}' "
            f"(weight range: {min(weights):.2f}-{max(weights):.2f})"
        )
        return result

    @staticmethod
    def top_k_sample(
        products: List[Dict[str, Any]],
        n: int,
        sort_field: str = "rating",
        reverse: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Sample top-k products by specified field.

        Args:
            products: List of products
            n: Number to sample
            sort_field: Field to sort by
            reverse: Sort descending if True, ascending if False

        Returns:
            Top-k products
        """
        sorted_products = sorted(
            products,
            key=lambda p: p.get(sort_field, 0),
            reverse=reverse
        )

        result = sorted_products[:n]

        logger.debug(
            f"Top-{n} sampled products by '{sort_field}' "
            f"({'descending' if reverse else 'ascending'})"
        )
        return result

    @staticmethod
    def cluster_sample(
        products: List[Dict[str, Any]],
        n: int,
        cluster_field: str = "price",
        num_clusters: int = 3,
        seed: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Sample from value clusters.

        Divides products into clusters based on field value, then samples
        proportionally from each cluster.

        Args:
            products: List of products
            n: Number to sample
            cluster_field: Field to cluster by
            num_clusters: Number of clusters to create
            seed: Random seed

        Returns:
            Cluster-sampled products
        """
        if seed is not None:
            random.seed(seed)

        # Sort by cluster field
        sorted_products = sorted(
            products,
            key=lambda p: p.get(cluster_field, 0)
        )

        # Divide into clusters
        cluster_size = len(sorted_products) // num_clusters
        clusters = [
            sorted_products[i:i + cluster_size]
            for i in range(0, len(sorted_products), cluster_size)
        ]

        # Sample from each cluster
        per_cluster = max(1, n // num_clusters)
        samples = []

        for cluster in clusters:
            if cluster:
                sample_size = min(per_cluster, len(cluster))
                samples.extend(random.sample(cluster, sample_size))

        result = samples[:n]

        logger.debug(
            f"Cluster sampled {len(result)} products from {num_clusters} clusters "
            f"by '{cluster_field}'"
        )
        return result
