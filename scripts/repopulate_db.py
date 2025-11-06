#!/usr/bin/env python3
"""
Vector Database Repopulation Script

This script clears the existing Qdrant collection and repopulates it with
the unified product dataset using OpenAI embeddings. It ensures that all
adversarial attack documents remain searchable and properly indexed.

Usage:
    python scripts/repopulate_db.py [OPTIONS]

Options:
    --reset              Clear and recreate the collection
    --collection NAME    Specify collection name (default: adversarial_seo)
    --provider PROVIDER  Embedding provider: openai or gemini (default: openai)
    --model MODEL        Embedding model (default: text-embedding-3-small)
    --batch-size SIZE    Batch size for embedding generation (default: 100)
    --verify             Verify attack documents are searchable after population
    --dry-run            Show what would be done without making changes

Examples:
    # Full repopulation with verification
    python scripts/repopulate_db.py --reset --verify

    # Use Gemini embeddings instead
    python scripts/repopulate_db.py --reset --provider gemini --model text-embedding-004

    # Dry run to check what would happen
    python scripts/repopulate_db.py --reset --dry-run
"""

import sys
import os
import argparse
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import time

# Add parent directory and src to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from vector_store import VectorStoreManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def load_unified_dataset(filepath: str) -> List[Dict[str, Any]]:
    """
    Load the unified category-based product dataset.

    Args:
        filepath: Path to the products_master.json file

    Returns:
        List of product dictionaries

    Raises:
        FileNotFoundError: If the dataset file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    logger.info(f"Loading unified dataset from: {filepath}")

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Dataset not found: {filepath}")

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Convert category-based structure to flat list
    products = []
    for category_name, category_items in data.items():
        if isinstance(category_items, list):
            # Handle flat array format (legacy)
            for item in category_items:
                item['category'] = category_name
                products.append(item)
        else:
            # Handle nested object format (newer format may have this)
            for item in category_items:
                item['category'] = category_name
                products.append(item)

    logger.info(f"Loaded {len(products)} products from {len(data)} categories")

    # Count attack documents
    attack_count = sum(
        1 for p in products
        if any(pattern in p.get('description', '').lower()
               for pattern in ['[system]', 'warning:', 'blind puppies',
                               'wildlife conservation', 'nsfw', 'toxic'])
    )
    logger.info(f"Found {attack_count} products with attack patterns")

    return products


def verify_attack_documents(
    vector_store: VectorStoreManager,
    expected_attack_count: int = 3
) -> bool:
    """
    Verify that attack documents are properly indexed and searchable.

    Args:
        vector_store: Vector store instance
        expected_attack_count: Expected number of attack documents

    Returns:
        True if verification passes, False otherwise
    """
    logger.info("Verifying attack documents are searchable...")

    # Test queries for different attack types
    test_queries = [
        ("system prompt injection", "[system]"),
        ("camera safety warnings", "WARNING:"),
        ("wildlife conservation cameras", "blind puppies"),
    ]

    found_attacks = set()

    for query, pattern in test_queries:
        logger.info(f"Testing query: '{query}' (looking for pattern: '{pattern}')")

        results = vector_store.search(query, limit=10)

        for doc_id, score, metadata in results:
            description = metadata.get('description', '')
            if pattern.lower() in description.lower():
                found_attacks.add(metadata.get('name'))
                logger.info(f"  ✓ Found attack document: {metadata.get('name')[:50]}... (score: {score:.3f})")

    logger.info(f"Found {len(found_attacks)} unique attack documents via search")

    if len(found_attacks) >= expected_attack_count:
        logger.info("✓ Attack document verification PASSED")
        return True
    else:
        logger.warning(
            f"✗ Attack document verification FAILED: "
            f"Expected at least {expected_attack_count}, found {len(found_attacks)}"
        )
        return False


def repopulate_database(
    collection_name: str = "adversarial_seo",
    embedding_provider: str = "openai",
    embedding_model: str = "text-embedding-3-small",
    reset: bool = False,
    batch_size: int = 100,
    verify: bool = False,
    dry_run: bool = False
) -> bool:
    """
    Repopulate the vector database with the unified dataset.

    Args:
        collection_name: Qdrant collection name
        embedding_provider: Embedding provider (openai or gemini)
        embedding_model: Embedding model name
        reset: Whether to reset the collection before populating
        batch_size: Batch size for embedding generation
        verify: Whether to verify attack documents after population
        dry_run: If True, show what would be done without making changes

    Returns:
        True if successful, False otherwise
    """
    try:
        # Load dataset
        data_dir = Path(__file__).parent.parent / "data"
        dataset_path = data_dir / "products_master.json"

        products = load_unified_dataset(str(dataset_path))

        if dry_run:
            logger.info("=" * 80)
            logger.info("DRY RUN MODE - No changes will be made")
            logger.info("=" * 80)
            logger.info(f"Would populate collection: {collection_name}")
            logger.info(f"Embedding provider: {embedding_provider}")
            logger.info(f"Embedding model: {embedding_model}")
            logger.info(f"Total products: {len(products)}")
            logger.info(f"Batch size: {batch_size}")
            logger.info(f"Reset collection: {reset}")
            logger.info(f"Verify after population: {verify}")
            return True

        # Initialize vector store
        logger.info("Initializing vector store...")
        vector_store = VectorStoreManager(
            collection_name=collection_name,
            embedding_provider=embedding_provider,
            embedding_model=embedding_model,
            reset_collection=reset
        )

        # Get initial stats
        if not reset:
            initial_stats = vector_store.get_collection_stats()
            logger.info(
                f"Collection '{collection_name}' has "
                f"{initial_stats.get('points_count', 0)} existing documents"
            )

        # Prepare documents for insertion
        logger.info(f"Preparing {len(products)} documents for insertion...")

        documents = []
        for product in products:
            # Create document with required fields
            doc = {
                "id": product.get("id", product.get("name", "")).replace(" ", "_"),
                "content": product.get("description", ""),
                "name": product.get("name", ""),
                "category": product.get("category", "Unknown"),
                "type": "product",
            }

            # Add all other product metadata
            for key, value in product.items():
                if key not in ["id", "description"]:
                    doc[key] = value

            documents.append(doc)

        # Add documents in batches with progress tracking
        logger.info(f"Adding {len(documents)} documents to vector store...")
        start_time = time.time()

        success = vector_store.add_documents(documents, batch_size=batch_size)

        elapsed_time = time.time() - start_time

        if success:
            logger.info(f"✓ Successfully added all documents in {elapsed_time:.2f}s")

            # Get final stats
            final_stats = vector_store.get_collection_stats()
            logger.info(
                f"Collection now contains {final_stats.get('points_count', 0)} documents"
            )

            # Verify attack documents if requested
            if verify:
                verification_passed = verify_attack_documents(vector_store)
                if not verification_passed:
                    logger.warning("Attack document verification failed!")
                    return False

            return True
        else:
            logger.error("✗ Failed to add documents to vector store")
            return False

    except Exception as e:
        logger.error(f"Error during database repopulation: {e}", exc_info=True)
        return False


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Repopulate Qdrant vector database with unified product dataset",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        "--reset",
        action="store_true",
        help="Clear and recreate the collection before populating"
    )

    parser.add_argument(
        "--collection",
        type=str,
        default="adversarial_seo",
        help="Collection name (default: adversarial_seo)"
    )

    parser.add_argument(
        "--provider",
        type=str,
        choices=["openai", "gemini"],
        default="openai",
        help="Embedding provider (default: openai)"
    )

    parser.add_argument(
        "--model",
        type=str,
        default="text-embedding-3-small",
        help="Embedding model (default: text-embedding-3-small)"
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Batch size for embedding generation (default: 100)"
    )

    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify attack documents are searchable after population"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )

    args = parser.parse_args()

    # Display configuration
    logger.info("=" * 80)
    logger.info("Vector Database Repopulation Script")
    logger.info("=" * 80)

    # Run repopulation
    success = repopulate_database(
        collection_name=args.collection,
        embedding_provider=args.provider,
        embedding_model=args.model,
        reset=args.reset,
        batch_size=args.batch_size,
        verify=args.verify,
        dry_run=args.dry_run
    )

    if success:
        logger.info("=" * 80)
        logger.info("✓ Database repopulation completed successfully")
        logger.info("=" * 80)
        sys.exit(0)
    else:
        logger.error("=" * 80)
        logger.error("✗ Database repopulation failed")
        logger.error("=" * 80)
        sys.exit(1)


if __name__ == "__main__":
    main()
