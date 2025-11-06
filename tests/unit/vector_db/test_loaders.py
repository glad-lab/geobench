"""
Unit tests for vector_db.loaders module.

Tests all data loader implementations including:
- UnifiedDatasetLoader
- ProductCatalogLoader
- NoiseDocumentLoader
- AttackDocumentLoader
- LoaderFactory
"""

import pytest
import json
import tempfile
from pathlib import Path
from typing import List, Dict, Any

from src.vector_db.loaders import (
    DataLoader,
    UnifiedDatasetLoader,
    ProductCatalogLoader,
    NoiseDocumentLoader,
    AttackDocumentLoader,
    LoaderFactory
)
from src.vector_db.exceptions import DataLoadError, DataSourceError


class TestUnifiedDatasetLoader:
    """Test UnifiedDatasetLoader class."""

    def test_load_unified_format(self, tmp_path):
        """Test loading unified category-based format."""
        # Create test dataset
        data = {
            "metadata": {
                "total_products": 2,
                "total_categories": 1,
                "format_version": "unified_v1"
            },
            "categories": {
                "Electronics": {
                    "items": [
                        {
                            "id": "prod-1",
                            "name": "Product 1",
                            "description": "Test product 1"
                        },
                        {
                            "id": "prod-2",
                            "name": "Product 2",
                            "description": "Test product 2",
                            "category": "Custom"  # Should be overridden
                        }
                    ]
                }
            }
        }

        # Write to file
        dataset_path = tmp_path / "products.json"
        with open(dataset_path, 'w') as f:
            json.dump(data, f)

        # Load data
        loader = UnifiedDatasetLoader(str(dataset_path))
        products = loader.load()

        # Verify
        assert len(products) == 2
        assert products[0]["id"] == "prod-1"
        assert products[0]["category"] == "Electronics"
        assert products[0]["content"] == "Test product 1"
        assert products[0]["type"] == "product"
        assert products[0]["has_attack"] is False

        assert products[1]["category"] == "Custom"  # Preserved existing category

    def test_load_legacy_format(self, tmp_path):
        """Test loading legacy products array format."""
        data = {
            "products": [
                {"id": "p1", "name": "Product 1", "description": "Desc 1"},
                {"id": "p2", "name": "Product 2", "description": "Desc 2"}
            ]
        }

        dataset_path = tmp_path / "products.json"
        with open(dataset_path, 'w') as f:
            json.dump(data, f)

        loader = UnifiedDatasetLoader(str(dataset_path))
        products = loader.load()

        assert len(products) == 2
        assert products[0]["content"] == "Desc 1"
        assert products[0]["type"] == "product"

    def test_load_simple_array_format(self, tmp_path):
        """Test loading simple array format."""
        data = [
            {"id": "p1", "name": "Product 1", "description": "Desc 1"},
            {"id": "p2", "name": "Product 2", "description": "Desc 2"}
        ]

        dataset_path = tmp_path / "products.json"
        with open(dataset_path, 'w') as f:
            json.dump(data, f)

        loader = UnifiedDatasetLoader(str(dataset_path))
        products = loader.load()

        assert len(products) == 2
        assert products[0]["content"] == "Desc 1"

    def test_validate_source_missing_file(self):
        """Test validation fails for missing file."""
        loader = UnifiedDatasetLoader("nonexistent.json")

        with pytest.raises(DataSourceError) as exc_info:
            loader.validate_source()

        assert "not found" in str(exc_info.value).lower()

    def test_validate_source_invalid_json(self, tmp_path):
        """Test validation fails for invalid JSON."""
        dataset_path = tmp_path / "invalid.json"
        with open(dataset_path, 'w') as f:
            f.write("{invalid json")

        loader = UnifiedDatasetLoader(str(dataset_path))

        with pytest.raises(DataSourceError) as exc_info:
            loader.validate_source()

        assert "invalid json" in str(exc_info.value).lower()

    def test_load_unknown_format(self, tmp_path):
        """Test error handling for unknown format."""
        data = {"unknown_key": "value"}

        dataset_path = tmp_path / "products.json"
        with open(dataset_path, 'w') as f:
            json.dump(data, f)

        loader = UnifiedDatasetLoader(str(dataset_path))

        with pytest.raises(DataLoadError) as exc_info:
            loader.load()

        assert "unknown" in str(exc_info.value).lower()


class TestProductCatalogLoader:
    """Test ProductCatalogLoader class."""

    def test_load_product_catalog(self, tmp_path):
        """Test loading product catalog."""
        data = [
            {"id": "p1", "name": "Product 1", "description": "Desc 1"},
            {"id": "p2", "name": "Product 2", "description": "Desc 2", "content": "Custom content"}
        ]

        catalog_path = tmp_path / "catalog.json"
        with open(catalog_path, 'w') as f:
            json.dump(data, f)

        loader = ProductCatalogLoader(str(catalog_path))
        products = loader.load()

        assert len(products) == 2
        assert products[0]["content"] == "Desc 1"
        assert products[1]["content"] == "Custom content"  # Preserved
        assert products[0]["type"] == "product"
        assert products[0]["has_attack"] is False

    def test_validate_source_not_array(self, tmp_path):
        """Test validation fails for non-array format."""
        data = {"products": []}  # Object, not array

        catalog_path = tmp_path / "catalog.json"
        with open(catalog_path, 'w') as f:
            json.dump(data, f)

        loader = ProductCatalogLoader(str(catalog_path))

        with pytest.raises(DataSourceError) as exc_info:
            loader.validate_source()

        assert "array" in str(exc_info.value).lower()


class TestNoiseDocumentLoader:
    """Test NoiseDocumentLoader class."""

    def test_load_noise_documents(self, tmp_path):
        """Test loading noise documents."""
        data = {
            "noise_documents": [
                {
                    "id": "noise-1",
                    "content": "Noise content 1",
                    "category": "Random",
                    "relevance": 0.5
                },
                {
                    "id": "noise-2",
                    "content": "Noise content 2",
                    "category": "Unrelated"
                }
            ]
        }

        noise_path = tmp_path / "noise.json"
        with open(noise_path, 'w') as f:
            json.dump(data, f)

        loader = NoiseDocumentLoader(str(noise_path))
        docs = loader.load()

        assert len(docs) == 2
        assert docs[0]["id"] == "noise-1"
        assert docs[0]["type"] == "noise"
        assert docs[0]["has_attack"] is False
        assert docs[0]["relevance"] == 0.5
        assert docs[1]["relevance"] == 0.0  # Default value

    def test_load_simple_array_format(self, tmp_path):
        """Test loading simple array format for noise docs."""
        data = [
            {"id": "n1", "content": "Noise 1", "category": "Cat1"},
            {"id": "n2", "content": "Noise 2", "category": "Cat2"}
        ]

        noise_path = tmp_path / "noise.json"
        with open(noise_path, 'w') as f:
            json.dump(data, f)

        loader = NoiseDocumentLoader(str(noise_path))
        docs = loader.load()

        assert len(docs) == 2
        assert docs[0]["type"] == "noise"


class TestAttackDocumentLoader:
    """Test AttackDocumentLoader class."""

    def test_load_attack_documents(self):
        """Test loading attack documents."""
        loader = AttackDocumentLoader()
        docs = loader.load()

        # Should have exactly 3 attack documents from the paper
        assert len(docs) == 3

        # Verify attack types
        attack_types = [doc["_attack_type"] for doc in docs]
        assert "prompt_injection" in attack_types
        assert "discreditation" in attack_types
        assert "persuasion" in attack_types

        # Verify all have required fields
        for doc in docs:
            assert "id" in doc
            assert "name" in doc
            assert "description" in doc
            assert "content" in doc
            assert doc["content"] == doc["description"]
            assert doc["type"] == "product"
            assert doc["has_attack"] is False  # Set to False for embedding

        # Verify attack patterns in descriptions
        descriptions = [doc["description"] for doc in docs]

        # Check for attack patterns
        assert any("[system]" in desc for desc in descriptions)
        assert any("WARNING:" in desc for desc in descriptions)
        assert any("blind puppies" in desc for desc in descriptions)

    def test_validate_source_always_valid(self):
        """Test validation always succeeds for hardcoded documents."""
        loader = AttackDocumentLoader()
        assert loader.validate_source() is True

    def test_attack_document_structure(self):
        """Test attack documents have complete structure."""
        loader = AttackDocumentLoader()
        docs = loader.load()

        for doc in docs:
            # Verify complete product structure
            assert "brand" in doc
            assert "category" in doc
            assert "price" in doc
            assert "rating" in doc
            assert "features" in doc
            assert "specifications" in doc
            assert isinstance(doc["features"], list)
            assert isinstance(doc["specifications"], dict)


class TestLoaderFactory:
    """Test LoaderFactory class."""

    def test_create_unified_loader(self, tmp_path):
        """Test creating unified dataset loader."""
        dataset_path = tmp_path / "products.json"
        with open(dataset_path, 'w') as f:
            json.dump([], f)

        loader = LoaderFactory.create("unified", file_path=str(dataset_path))

        assert isinstance(loader, UnifiedDatasetLoader)
        assert loader.file_path == dataset_path

    def test_create_catalog_loader(self, tmp_path):
        """Test creating catalog loader."""
        catalog_path = tmp_path / "catalog.json"
        with open(catalog_path, 'w') as f:
            json.dump([], f)

        loader = LoaderFactory.create("catalog", file_path=str(catalog_path))

        assert isinstance(loader, ProductCatalogLoader)

    def test_create_noise_loader(self, tmp_path):
        """Test creating noise loader."""
        noise_path = tmp_path / "noise.json"
        with open(noise_path, 'w') as f:
            json.dump([], f)

        loader = LoaderFactory.create("noise", file_path=str(noise_path))

        assert isinstance(loader, NoiseDocumentLoader)

    def test_create_attack_loader(self):
        """Test creating attack loader."""
        loader = LoaderFactory.create("attack")

        assert isinstance(loader, AttackDocumentLoader)

    def test_create_unknown_type(self):
        """Test error handling for unknown loader type."""
        with pytest.raises(ValueError) as exc_info:
            LoaderFactory.create("unknown")

        assert "unknown" in str(exc_info.value).lower()
        assert "unified" in str(exc_info.value)  # Should list valid types
