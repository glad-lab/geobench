"""
Product manipulation utilities for benchmark experiments.

Supports:
- Order manipulation (random, by rating, by category, alternating)
- Noise injection (description, price, rating)
- Data cropping (random, top, bottom, balanced)
- Irrelevant feature addition
- Anomaly injection (outliers, inconsistencies)
"""

import random
import logging
from typing import List, Dict, Any, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)


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

        else:
            raise ValueError(f"Unknown order strategy: {order_strategy}")

        logger.info(f"Reordered {len(products_copy)} products using '{order_strategy}' strategy")
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

        logger.info(
            f"Added {noise_type} noise to {num_noisy}/{len(products_copy)} products "
            f"(ratio={noise_ratio})"
        )
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
            result = random.sample(products, keep_count)

        elif crop_strategy == "top":
            result = products[:keep_count]

        elif crop_strategy == "bottom":
            result = products[-keep_count:]

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

            result = result[:keep_count]

        else:
            result = products[:keep_count]

        logger.info(
            f"Cropped dataset from {len(products)} to {len(result)} products "
            f"using '{crop_strategy}' strategy (ratio={crop_ratio})"
        )
        return result

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

        logger.info(f"Added {num_features} irrelevant features to {len(products_copy)} products")
        return products_copy

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

            else:
                raise ValueError(f"Unknown anomaly type: {anomaly_type}")

        logger.info(
            f"Injected {anomaly_type} anomalies to {num_anomalies}/{len(products_copy)} products "
            f"(ratio={anomaly_ratio})"
        )
        return products_copy
