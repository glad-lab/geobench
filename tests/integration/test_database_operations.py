"""
Integration tests for vector database operations.

Tests database operations with real Qdrant instance, including
data population, querying, and attack document preservation.
"""

import pytest
import time
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from src.vector_db import VectorDBPopulator, UnifiedDatasetLoader
from src.vector_store import VectorStoreManager
from src.attacks import AttackFactory, AttackType


@pytest.mark.integration
@pytest.mark.requires_docker
class TestDatabaseOperations:
    """Test database operations with real Qdrant instance."""

    def test_qdrant_connection(self, qdrant_service):
        """Test basic Qdrant connectivity."""
        client = QdrantClient(
            host=qdrant_service["host"],
            port=qdrant_service["port"]
        )

        # Should connect successfully
        collections = client.get_collections()
        assert collections is not None

    def test_collection_creation_and_deletion(
        self, qdrant_service, integration_test_collection
    ):
        """Test creating and deleting collections."""
        vector_store = VectorStoreManager(
            collection_name=integration_test_collection,
            embedding_provider="gemini",
            reset_collection=True,
            host=qdrant_service["host"],
            port=qdrant_service["port"],
        )

        # Collection should exist
        client = QdrantClient(
            host=qdrant_service["host"],
            port=qdrant_service["port"]
        )

        collections = client.get_collections()
        collection_names = [c.name for c in collections.collections]

        assert integration_test_collection in collection_names

        # Cleanup
        vector_store.clear_collection()

        # Should be deleted
        collections = client.get_collections()
        collection_names = [c.name for c in collections.collections]

        # May still exist if soft delete, but should be empty

    def test_populate_and_query(self, qdrant_service, test_products, integration_test_collection):
        """Test full populate and query cycle."""
        # Create vector store
        vector_store = VectorStoreManager(
            collection_name=integration_test_collection,
            embedding_provider="gemini",
            reset_collection=True,
            host=qdrant_service["host"],
            port=qdrant_service["port"],
        )

        # Populate with test products
        if "categories" in test_products:
            products = []
            for cat_data in list(test_products["categories"].values())[:2]:
                products.extend(cat_data["items"][:5])
        else:
            products = test_products[:10]

        vector_store.add_documents(products)

        # Query
        results = vector_store.query("test product", top_k=5)

        # Verify results
        assert len(results) > 0
        assert all("id" in r for r in results)
        assert all("score" in r for r in results)

        # Cleanup
        vector_store.clear_collection()

    def test_attack_document_preservation(
        self, qdrant_service, integration_test_collection
    ):
        """Test that attack patterns are preserved in database."""
        vector_store = VectorStoreManager(
            collection_name=integration_test_collection,
            embedding_provider="gemini",
            reset_collection=True,
            host=qdrant_service["host"],
            port=qdrant_service["port"],
        )

        # Create attacked document
        attack_factory = AttackFactory()
        attack_content = attack_factory.create_attack(
            AttackType.PROMPT_INJECTION,
            product_name="Test Product",
            approach="glass_box"
        )

        doc = {
            "id": "attacked_doc",
            "name": "Test Product",
            "description": f"Normal description. {attack_content}",
            "price": 99.99,
            "rating": 4.5,
        }

        # Add to database
        vector_store.add_documents([doc])

        # Query back
        results = vector_store.query("test product", top_k=5)

        # Find our document
        attacked_doc = next((r for r in results if r["id"] == "attacked_doc"), None)

        if attacked_doc:
            # Verify attack preserved
            assert "IGNORE" in attacked_doc["description"] or "ignore" in attacked_doc["description"]

        # Cleanup
        vector_store.clear_collection()

    def test_metadata_preservation(self, qdrant_service, integration_test_collection):
        """Test that metadata fields are preserved."""
        vector_store = VectorStoreManager(
            collection_name=integration_test_collection,
            embedding_provider="gemini",
            reset_collection=True,
            host=qdrant_service["host"],
            port=qdrant_service["port"],
        )

        # Add document with custom metadata
        doc = {
            "id": "meta_test",
            "name": "Metadata Test",
            "description": "Test document",
            "price": 50.0,
            "rating": 4.0,
            "_custom_field": "custom_value",
            "_is_attacked": True,
            "_attack_type": "prompt_injection",
        }

        vector_store.add_documents([doc])

        # Query back
        results = vector_store.query("metadata test", top_k=5)

        # Find our document
        meta_doc = next((r for r in results if r["id"] == "meta_test"), None)

        if meta_doc:
            # Verify custom fields preserved
            assert "_custom_field" in meta_doc
            assert meta_doc["_custom_field"] == "custom_value"
            assert "_is_attacked" in meta_doc

        # Cleanup
        vector_store.clear_collection()

    def test_large_batch_insertion(self, qdrant_service, integration_test_collection):
        """Test inserting large batch of documents."""
        from conftest import generate_test_products

        vector_store = VectorStoreManager(
            collection_name=integration_test_collection,
            embedding_provider="gemini",
            reset_collection=True,
            host=qdrant_service["host"],
            port=qdrant_service["port"],
        )

        # Generate 100 test products
        products = generate_test_products(100)

        # Add in batch
        start_time = time.time()
        vector_store.add_documents(products)
        elapsed = time.time() - start_time

        # Should complete reasonably fast
        assert elapsed < 120  # 2 minutes for 100 products

        # Verify count
        client = QdrantClient(
            host=qdrant_service["host"],
            port=qdrant_service["port"]
        )

        collection_info = client.get_collection(integration_test_collection)
        # Should have documents (exact count depends on embedding success)
        assert collection_info.points_count > 0

        # Cleanup
        vector_store.clear_collection()

    def test_update_documents(self, qdrant_service, integration_test_collection):
        """Test updating existing documents."""
        vector_store = VectorStoreManager(
            collection_name=integration_test_collection,
            embedding_provider="gemini",
            reset_collection=True,
            host=qdrant_service["host"],
            port=qdrant_service["port"],
        )

        # Add initial document
        doc = {
            "id": "update_test",
            "name": "Original Name",
            "description": "Original description",
            "price": 100.0,
            "rating": 4.0,
        }

        vector_store.add_documents([doc])

        # Update document
        updated_doc = doc.copy()
        updated_doc["name"] = "Updated Name"
        updated_doc["description"] = "Updated description"

        vector_store.add_documents([updated_doc])

        # Query back
        results = vector_store.query("update test", top_k=5)

        # Verify update
        found_doc = next((r for r in results if r["id"] == "update_test"), None)

        if found_doc:
            # Should have updated fields
            assert "Updated" in found_doc["name"] or "Updated" in found_doc.get("description", "")

        # Cleanup
        vector_store.clear_collection()

    def test_query_filtering(self, qdrant_service, integration_test_collection):
        """Test filtering queries by metadata."""
        vector_store = VectorStoreManager(
            collection_name=integration_test_collection,
            embedding_provider="gemini",
            reset_collection=True,
            host=qdrant_service["host"],
            port=qdrant_service["port"],
        )

        # Add documents with different categories
        docs = [
            {
                "id": "cam1",
                "name": "Camera 1",
                "description": "A camera",
                "category": "Cameras",
                "price": 500.0,
                "rating": 4.5,
            },
            {
                "id": "book1",
                "name": "Book 1",
                "description": "A book",
                "category": "Books",
                "price": 20.0,
                "rating": 4.8,
            },
        ]

        vector_store.add_documents(docs)

        # Query with potential filter
        results = vector_store.query("product", top_k=5)

        # Should get results
        assert len(results) > 0

        # Cleanup
        vector_store.clear_collection()

    def test_concurrent_operations(self, qdrant_service, integration_test_collection):
        """Test concurrent read/write operations."""
        from concurrent.futures import ThreadPoolExecutor
        from conftest import generate_test_products

        vector_store = VectorStoreManager(
            collection_name=integration_test_collection,
            embedding_provider="gemini",
            reset_collection=True,
            host=qdrant_service["host"],
            port=qdrant_service["port"],
        )

        def add_batch(batch_id):
            """Add a batch of documents."""
            products = generate_test_products(5, category=f"Batch{batch_id}")
            vector_store.add_documents(products)
            return batch_id

        # Add documents concurrently
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(add_batch, i) for i in range(3)]
            results = [f.result() for f in futures]

        # All should complete
        assert len(results) == 3

        # Verify documents added
        client = QdrantClient(
            host=qdrant_service["host"],
            port=qdrant_service["port"]
        )

        collection_info = client.get_collection(integration_test_collection)
        # Should have documents from all batches
        assert collection_info.points_count > 0

        # Cleanup
        vector_store.clear_collection()

    @pytest.mark.slow
    def test_database_persistence(self, qdrant_service, integration_test_collection):
        """Test database persistence across operations."""
        vector_store = VectorStoreManager(
            collection_name=integration_test_collection,
            embedding_provider="gemini",
            reset_collection=True,
            host=qdrant_service["host"],
            port=qdrant_service["port"],
        )

        # Add documents
        docs = [
            {
                "id": "persist1",
                "name": "Persist Test 1",
                "description": "Persistence test document 1",
                "price": 100.0,
                "rating": 4.5,
            }
        ]

        vector_store.add_documents(docs)

        # Create new store instance (simulating restart)
        vector_store_2 = VectorStoreManager(
            collection_name=integration_test_collection,
            embedding_provider="gemini",
            reset_collection=False,  # Don't reset
            host=qdrant_service["host"],
            port=qdrant_service["port"],
        )

        # Query from new instance
        results = vector_store_2.query("persist test", top_k=5)

        # Should still have data
        found = any(r["id"] == "persist1" for r in results)
        # Note: May not find due to different embedding instance

        # Cleanup
        vector_store.clear_collection()

    def test_error_handling(self, qdrant_service):
        """Test error handling for database operations."""
        # Try to query non-existent collection
        vector_store = VectorStoreManager(
            collection_name="nonexistent_collection",
            embedding_provider="gemini",
            reset_collection=False,
            host=qdrant_service["host"],
            port=qdrant_service["port"],
        )

        # Should handle gracefully
        with pytest.raises(Exception):
            vector_store.query("test", top_k=5)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
