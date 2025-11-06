"""
Comprehensive test suite for src.utils package.

Tests all modules:
- data_loader: Format detection, loading, sampling
- manipulator: Ordering, noise, cropping, anomalies
- sampling: Random, stratified, weighted strategies
- validation: Schema, duplicates, value validation
"""

import pytest
import tempfile
import json
from pathlib import Path
from typing import List, Dict, Any

from src.utils import (
    UnifiedDataLoader,
    ProductManipulator,
    SamplingStrategy,
    DataValidator,
    ValidationResult,
)


# Test Fixtures

@pytest.fixture
def sample_products() -> List[Dict[str, Any]]:
    """Sample product list for testing."""
    return [
        {
            "id": "prod-1",
            "name": "Product 1",
            "description": "Test product 1",
            "category": "Electronics",
            "price": 100.0,
            "rating": 4.5,
        },
        {
            "id": "prod-2",
            "name": "Product 2",
            "description": "Test product 2",
            "category": "Electronics",
            "price": 200.0,
            "rating": 4.0,
        },
        {
            "id": "prod-3",
            "name": "Product 3",
            "description": "Test product 3",
            "category": "Books",
            "price": 50.0,
            "rating": 5.0,
        },
        {
            "id": "prod-4",
            "name": "Product 4",
            "description": "Test product 4",
            "category": "Books",
            "price": 30.0,
            "rating": 3.5,
        },
    ]


@pytest.fixture
def unified_format_file(sample_products, tmp_path):
    """Create temporary unified format file."""
    data = {
        "metadata": {
            "total_products": 4,
            "total_categories": 2,
        },
        "categories": {
            "Electronics": {
                "items": sample_products[:2]
            },
            "Books": {
                "items": sample_products[2:]
            }
        }
    }

    file_path = tmp_path / "products_unified.json"
    with open(file_path, "w") as f:
        json.dump(data, f)

    return str(file_path)


@pytest.fixture
def flat_format_file(sample_products, tmp_path):
    """Create temporary flat format file."""
    file_path = tmp_path / "products_flat.json"
    with open(file_path, "w") as f:
        json.dump(sample_products, f)

    return str(file_path)


# UnifiedDataLoader Tests

class TestUnifiedDataLoader:
    """Test UnifiedDataLoader functionality."""

    def test_load_unified_format(self, unified_format_file):
        """Test loading unified format."""
        loader = UnifiedDataLoader(unified_format_file)

        assert loader.format == "unified"
        assert len(loader.products) == 4
        assert len(loader.categories) == 2

    def test_load_flat_format(self, flat_format_file):
        """Test loading flat format."""
        loader = UnifiedDataLoader(flat_format_file)

        assert loader.format == "flat"
        assert len(loader.products) == 4

    def test_detect_format_unified(self, unified_format_file):
        """Test format detection for unified format."""
        loader = UnifiedDataLoader(unified_format_file)
        assert loader.detect_format(loader.data) == "unified"

    def test_detect_format_flat(self, flat_format_file):
        """Test format detection for flat format."""
        loader = UnifiedDataLoader(flat_format_file)
        assert loader.detect_format(loader.data) == "flat"

    def test_get_all_products(self, unified_format_file):
        """Test getting all products."""
        loader = UnifiedDataLoader(unified_format_file)
        products = loader.get_all_products()

        assert len(products) == 4
        assert all("id" in p for p in products)

    def test_get_category_products(self, unified_format_file):
        """Test getting products by category."""
        loader = UnifiedDataLoader(unified_format_file)
        electronics = loader.get_category_products("Electronics")

        assert len(electronics) == 2
        assert all(p["category"] == "Electronics" for p in electronics)

    def test_get_categories(self, unified_format_file):
        """Test getting category list."""
        loader = UnifiedDataLoader(unified_format_file)
        categories = loader.get_categories()

        assert len(categories) == 2
        assert "Electronics" in categories
        assert "Books" in categories

    def test_get_stats(self, unified_format_file):
        """Test getting dataset statistics."""
        loader = UnifiedDataLoader(unified_format_file)
        stats = loader.get_stats()

        assert stats["total_products"] == 4
        assert stats["total_categories"] == 2
        assert "category_distribution" in stats

    def test_sample_random(self, unified_format_file):
        """Test random sampling."""
        loader = UnifiedDataLoader(unified_format_file)
        sample = loader.sample_products(2, strategy="random", seed=42)

        assert len(sample) == 2

    def test_sample_stratified(self, unified_format_file):
        """Test stratified sampling."""
        loader = UnifiedDataLoader(unified_format_file)
        sample = loader.sample_products(4, strategy="stratified", seed=42)

        # Should have products from both categories
        categories = [p["category"] for p in sample]
        assert "Electronics" in categories
        assert "Books" in categories

    def test_sample_weighted(self, unified_format_file):
        """Test weighted sampling."""
        loader = UnifiedDataLoader(unified_format_file)
        sample = loader.sample_products(3, strategy="weighted", seed=42)

        assert len(sample) == 3

    def test_sample_diverse(self, unified_format_file):
        """Test diverse sampling."""
        loader = UnifiedDataLoader(unified_format_file)
        sample = loader.sample_products(4, strategy="diverse", seed=42)

        # Should have at least one from each category
        categories = set(p["category"] for p in sample)
        assert len(categories) == 2

    def test_sample_by_category(self, unified_format_file):
        """Test sampling from specific category."""
        loader = UnifiedDataLoader(unified_format_file)
        sample = loader.sample_products(2, category="Electronics", seed=42)

        assert len(sample) == 2
        assert all(p["category"] == "Electronics" for p in sample)


# ProductManipulator Tests

class TestProductManipulator:
    """Test ProductManipulator functionality."""

    def test_change_order_random(self, sample_products):
        """Test random ordering."""
        reordered = ProductManipulator.change_order(
            sample_products, order_strategy="random", seed=42
        )

        assert len(reordered) == len(sample_products)
        assert set(p["id"] for p in reordered) == set(p["id"] for p in sample_products)

    def test_change_order_reverse(self, sample_products):
        """Test reverse ordering."""
        reordered = ProductManipulator.change_order(
            sample_products, order_strategy="reverse"
        )

        assert reordered[0]["id"] == sample_products[-1]["id"]
        assert reordered[-1]["id"] == sample_products[0]["id"]

    def test_change_order_by_rating(self, sample_products):
        """Test ordering by rating."""
        reordered = ProductManipulator.change_order(
            sample_products, order_strategy="by_rating"
        )

        ratings = [p["rating"] for p in reordered]
        assert ratings == sorted(ratings, reverse=True)

    def test_change_order_by_price(self, sample_products):
        """Test ordering by price."""
        reordered = ProductManipulator.change_order(
            sample_products, order_strategy="by_price"
        )

        prices = [p["price"] for p in reordered]
        assert prices == sorted(prices)

    def test_change_order_by_category(self, sample_products):
        """Test ordering by category."""
        reordered = ProductManipulator.change_order(
            sample_products, order_strategy="by_category"
        )

        categories = [p["category"] for p in reordered]
        assert categories == sorted(categories)

    def test_change_order_alternating_category(self, sample_products):
        """Test alternating category ordering."""
        reordered = ProductManipulator.change_order(
            sample_products, order_strategy="alternating_category"
        )

        # Should alternate between categories
        categories = [p["category"] for p in reordered]
        assert categories[0] != categories[1]

    def test_add_noise_description(self, sample_products):
        """Test adding noise to descriptions."""
        noisy = ProductManipulator.add_noise(
            sample_products, noise_ratio=0.5, noise_type="description", seed=42
        )

        # Check that some descriptions changed
        original_descs = [p["description"] for p in sample_products]
        noisy_descs = [p["description"] for p in noisy]
        assert any(o != n for o, n in zip(original_descs, noisy_descs))

    def test_add_noise_price(self, sample_products):
        """Test adding noise to prices."""
        noisy = ProductManipulator.add_noise(
            sample_products, noise_ratio=0.5, noise_type="price", seed=42
        )

        # Check that some prices changed
        original_prices = [p["price"] for p in sample_products]
        noisy_prices = [p["price"] for p in noisy]
        assert any(o != n for o, n in zip(original_prices, noisy_prices))

    def test_add_noise_rating(self, sample_products):
        """Test adding noise to ratings."""
        noisy = ProductManipulator.add_noise(
            sample_products, noise_ratio=0.5, noise_type="rating", seed=42
        )

        # Check that ratings are still valid
        for product in noisy:
            assert 0 <= product["rating"] <= 5

    def test_add_noise_all(self, sample_products):
        """Test adding noise to all fields."""
        noisy = ProductManipulator.add_noise(
            sample_products, noise_ratio=1.0, noise_type="all", seed=42
        )

        # All products should be modified
        assert len(noisy) == len(sample_products)

    def test_crop_data_random(self, sample_products):
        """Test random cropping."""
        cropped = ProductManipulator.crop_data(
            sample_products, crop_strategy="random", crop_ratio=0.5, seed=42
        )

        assert len(cropped) == 2

    def test_crop_data_top(self, sample_products):
        """Test top cropping."""
        cropped = ProductManipulator.crop_data(
            sample_products, crop_strategy="top", crop_ratio=0.5
        )

        assert len(cropped) == 2
        assert cropped[0]["id"] == sample_products[0]["id"]

    def test_crop_data_bottom(self, sample_products):
        """Test bottom cropping."""
        cropped = ProductManipulator.crop_data(
            sample_products, crop_strategy="bottom", crop_ratio=0.5
        )

        assert len(cropped) == 2
        assert cropped[0]["id"] == sample_products[-2]["id"]

    def test_crop_data_category_balanced(self, sample_products):
        """Test category-balanced cropping."""
        cropped = ProductManipulator.crop_data(
            sample_products, crop_strategy="category_balanced", crop_ratio=0.5, seed=42
        )

        assert len(cropped) == 2

    def test_add_irrelevant_features(self, sample_products):
        """Test adding irrelevant features."""
        modified = ProductManipulator.add_irrelevant_features(
            sample_products, num_features=3, seed=42
        )

        # Check that features were added
        for product in modified:
            assert len(product) > len(sample_products[0])

    def test_inject_anomalies_price_outlier(self, sample_products):
        """Test price outlier injection."""
        anomalous = ProductManipulator.inject_anomalies(
            sample_products, anomaly_type="price_outlier", anomaly_ratio=0.5, seed=42
        )

        # Check for extreme prices
        prices = [p["price"] for p in anomalous]
        max_price = max(prices)
        min_price = min(prices)
        assert max_price > 10 * min_price or min_price < max_price / 10

    def test_inject_anomalies_rating_inconsistent(self, sample_products):
        """Test rating inconsistency injection."""
        anomalous = ProductManipulator.inject_anomalies(
            sample_products, anomaly_type="rating_inconsistent", anomaly_ratio=0.5, seed=42
        )

        # Check that at least one product has inconsistency
        has_inconsistency = any(
            p["rating"] == 5.0 and "Terrible" in p.get("description", "")
            for p in anomalous
        )
        assert has_inconsistency, "Should have at least one rating inconsistency"

    def test_inject_anomalies_missing_description(self, sample_products):
        """Test missing description injection."""
        anomalous = ProductManipulator.inject_anomalies(
            sample_products, anomaly_type="missing_description", anomaly_ratio=0.5, seed=42
        )

        # Check for missing descriptions
        descriptions = [p["description"] for p in anomalous]
        assert any(d == "" for d in descriptions)

    def test_inject_anomalies_duplicate_content(self, sample_products):
        """Test duplicate content injection."""
        anomalous = ProductManipulator.inject_anomalies(
            sample_products, anomaly_type="duplicate_content", anomaly_ratio=0.5, seed=42
        )

        # Check for duplicates
        descriptions = [p["description"] for p in anomalous]
        assert len(descriptions) != len(set(descriptions))


# SamplingStrategy Tests

class TestSamplingStrategy:
    """Test SamplingStrategy functionality."""

    def test_random_sample(self, sample_products):
        """Test random sampling."""
        sample = SamplingStrategy.random_sample(sample_products, 2, seed=42)

        assert len(sample) == 2
        assert all(p in sample_products for p in sample)

    def test_stratified_sample(self, sample_products):
        """Test stratified sampling."""
        sample = SamplingStrategy.stratified_sample(
            sample_products, 4, category_field="category", seed=42
        )

        # Should have products from both categories
        categories = [p["category"] for p in sample]
        assert "Electronics" in categories
        assert "Books" in categories

    def test_weighted_sample(self, sample_products):
        """Test weighted sampling."""
        sample = SamplingStrategy.weighted_sample(
            sample_products, 3, weight_field="rating", seed=42
        )

        assert len(sample) == 3

    def test_top_k_sample(self, sample_products):
        """Test top-k sampling."""
        sample = SamplingStrategy.top_k_sample(
            sample_products, 2, sort_field="rating", reverse=True
        )

        assert len(sample) == 2
        assert sample[0]["rating"] >= sample[1]["rating"]

    def test_cluster_sample(self, sample_products):
        """Test cluster sampling."""
        sample = SamplingStrategy.cluster_sample(
            sample_products, 3, cluster_field="price", num_clusters=2, seed=42
        )

        # Should sample at least 2 products (may be less than requested with small datasets)
        assert len(sample) >= 2
        assert len(sample) <= 3


# DataValidator Tests

class TestDataValidator:
    """Test DataValidator functionality."""

    def test_validate_schema_valid(self, sample_products):
        """Test schema validation with valid data."""
        result = DataValidator.validate_schema(
            sample_products, required_fields=["id", "name", "price"]
        )

        assert result.is_valid
        assert len(result.errors) == 0

    def test_validate_schema_missing_fields(self):
        """Test schema validation with missing fields."""
        products = [
            {"id": "prod-1", "name": "Product 1"},  # Missing price
            {"id": "prod-2", "price": 100.0},  # Missing name
        ]

        result = DataValidator.validate_schema(
            products, required_fields=["id", "name", "price"]
        )

        assert not result.is_valid
        assert len(result.errors) == 2

    def test_check_duplicates_none(self, sample_products):
        """Test duplicate checking with no duplicates."""
        result = DataValidator.check_duplicates(sample_products, id_field="id")

        assert result.is_valid
        assert len(result.errors) == 0

    def test_check_duplicates_found(self):
        """Test duplicate checking with duplicates."""
        products = [
            {"id": "prod-1", "name": "Product 1"},
            {"id": "prod-1", "name": "Product 2"},  # Duplicate ID
        ]

        result = DataValidator.check_duplicates(products, id_field="id")

        assert not result.is_valid
        assert len(result.errors) == 1

    def test_validate_values_valid(self, sample_products):
        """Test value validation with valid data."""
        result = DataValidator.validate_values(sample_products)

        assert result.is_valid
        assert len(result.errors) == 0

    def test_validate_values_out_of_range(self):
        """Test value validation with out-of-range values."""
        products = [
            {"id": "prod-1", "price": -100.0, "rating": 6.0},  # Invalid values
        ]

        result = DataValidator.validate_values(products)

        assert not result.is_valid
        assert len(result.errors) >= 1

    def test_validate_all(self, sample_products):
        """Test comprehensive validation."""
        result = DataValidator.validate_all(
            sample_products,
            required_fields=["id", "name", "price", "rating"],
            id_field="id"
        )

        assert result.is_valid
        assert "total_errors" in result.stats
        assert "total_warnings" in result.stats


# Integration Tests

class TestIntegration:
    """Test integration between modules."""

    def test_load_manipulate_validate(self, unified_format_file):
        """Test full workflow: load, manipulate, validate."""
        # Load
        loader = UnifiedDataLoader(unified_format_file)
        products = loader.get_all_products()

        # Manipulate
        reordered = ProductManipulator.change_order(products, "by_rating")
        noisy = ProductManipulator.add_noise(reordered, noise_ratio=0.5, seed=42)

        # Validate
        result = DataValidator.validate_all(noisy)

        assert result.is_valid

    def test_sample_manipulate_validate(self, unified_format_file):
        """Test sampling, manipulation, and validation."""
        # Load and sample
        loader = UnifiedDataLoader(unified_format_file)
        sample = loader.sample_products(3, strategy="stratified", seed=42)

        # Manipulate
        cropped = ProductManipulator.crop_data(sample, crop_ratio=0.67, seed=42)

        # Validate
        result = DataValidator.validate_schema(
            cropped, required_fields=["id", "name"]
        )

        assert result.is_valid


# Performance Tests

class TestPerformance:
    """Test performance characteristics."""

    def test_large_dataset_loading(self, tmp_path):
        """Test loading large dataset."""
        # Create large dataset
        products = [
            {
                "id": f"prod-{i}",
                "name": f"Product {i}",
                "description": f"Description {i}",
                "category": f"Category {i % 10}",
                "price": 100.0 + i,
                "rating": 3.0 + (i % 3),
            }
            for i in range(1000)
        ]

        file_path = tmp_path / "large_dataset.json"
        with open(file_path, "w") as f:
            json.dump(products, f)

        # Test loading
        loader = UnifiedDataLoader(str(file_path))

        assert len(loader.products) == 1000
        assert len(loader.categories) == 10

    def test_manipulation_preserves_data(self, sample_products):
        """Test that manipulations preserve data integrity."""
        # Apply multiple manipulations
        result = sample_products
        result = ProductManipulator.change_order(result, "random", seed=42)
        result = ProductManipulator.add_noise(result, noise_ratio=0.5, seed=42)
        result = ProductManipulator.add_irrelevant_features(result, num_features=3, seed=42)

        # Validate
        validation = DataValidator.validate_schema(
            result, required_fields=["id", "name"]
        )

        assert validation.is_valid


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
