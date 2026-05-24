"""
DEPRECATED: This module is deprecated. Use src.vector_db package instead.

This file provides backward compatibility for code using the old populate_vector_db module.
All new code should use the modular vector_db package with its Builder pattern API.

Old usage:
    from src.populate_vector_db import populate_database, load_all_products
    products = load_all_products()
    populate_database()

New usage:
    from src.vector_db import VectorDBPopulator, UnifiedDatasetLoader
    from src.vector_store import VectorStoreManager

    vector_store = VectorStoreManager(collection_name="adversarial_seo")
    populator = (VectorDBPopulator(vector_store)
        .add_loader(UnifiedDatasetLoader("data/products_master.json"))
        .add_loader(AttackDocumentLoader())
        .populate(reset=True))

Migration Guide:
    See docs/REFACTORING_GUIDE.md for complete migration instructions.
"""

import warnings
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


def _show_deprecation_warning(old_function: str, new_api: str):
    """Show deprecation warning with migration guidance."""
    warnings.warn(
        f"{old_function} is deprecated and will be removed in version 3.0.0. "
        f"Use {new_api} instead. See docs/REFACTORING_GUIDE.md for migration guidance.",
        DeprecationWarning,
        stacklevel=3
    )


def load_all_products() -> List[Dict[str, Any]]:
    """Load all products from the master products file (DEPRECATED).

    Deprecated:
        Use UnifiedDatasetLoader instead:
        >>> from vector_db import UnifiedDatasetLoader
        >>> loader = UnifiedDatasetLoader("data/products_master.json")
        >>> products = loader.load()

    Returns:
        List of product dictionaries
    """
    _show_deprecation_warning(
        "load_all_products()",
        "UnifiedDatasetLoader('data/products_master.json').load()"
    )

    from vector_db import UnifiedDatasetLoader

    loader = UnifiedDatasetLoader("data/products_master.json")
    return loader.load()


def load_noise_documents() -> List[Dict[str, Any]]:
    """Load noise documents from the data directory (DEPRECATED).

    Deprecated:
        Use NoiseDocumentLoader instead:
        >>> from vector_db import NoiseDocumentLoader
        >>> loader = NoiseDocumentLoader("data/noise_documents.json")
        >>> noise_docs = loader.load()

    Returns:
        List of noise document dictionaries
    """
    _show_deprecation_warning(
        "load_noise_documents()",
        "NoiseDocumentLoader('data/noise_documents.json').load()"
    )

    from vector_db import NoiseDocumentLoader

    loader = NoiseDocumentLoader("data/noise_documents.json")
    return loader.load()


def create_attack_documents() -> List[Dict[str, Any]]:
    """Create attack documents following the paper's Appendix B.2 (DEPRECATED).

    Deprecated:
        Use AttackDocumentLoader instead:
        >>> from vector_db import AttackDocumentLoader
        >>> loader = AttackDocumentLoader()
        >>> attack_docs = loader.load()

    Returns:
        List of attack document dictionaries
    """
    _show_deprecation_warning(
        "create_attack_documents()",
        "AttackDocumentLoader().load()"
    )

    from vector_db import AttackDocumentLoader

    loader = AttackDocumentLoader()
    return loader.load()


def populate_database(
    collection_name: str = "adversarial_seo_products",
    embedding_provider: str = "gemini",
    reset_collection: bool = True,
    verify_attacks: bool = False
) -> bool:
    """Populate the vector database with products and attack documents (DEPRECATED).

    Deprecated:
        Use VectorDBPopulator instead:
        >>> from vector_db import VectorDBPopulator, UnifiedDatasetLoader, AttackDocumentLoader
        >>> from vector_store import VectorStoreManager
        >>>
        >>> vector_store = VectorStoreManager(
        ...     collection_name=collection_name,
        ...     embedding_provider=embedding_provider,
        ...     reset_collection=reset_collection
        ... )
        >>> populator = (VectorDBPopulator(vector_store)
        ...     .add_loader(UnifiedDatasetLoader("data/products_master.json"))
        ...     .add_loader(AttackDocumentLoader())
        ...     .populate(reset=reset_collection))

    Args:
        collection_name: Name of the Qdrant collection
        embedding_provider: Embedding provider (gemini or openai)
        reset_collection: Whether to reset the collection
        verify_attacks: Whether to verify attack documents are searchable

    Returns:
        True if successful, False otherwise
    """
    _show_deprecation_warning(
        "populate_database()",
        "VectorDBPopulator(vector_store).add_loader(...).populate()"
    )

    try:
        from vector_db import (
            VectorDBPopulator,
            UnifiedDatasetLoader,
            AttackDocumentLoader,
            AttackPatternValidator
        )
        from vector_store import VectorStoreManager

        # Create vector store
        vector_store = VectorStoreManager(
            collection_name=collection_name,
            embedding_provider=embedding_provider,
            reset_collection=reset_collection
        )

        # Build populator
        populator = (VectorDBPopulator(vector_store)
            .add_loader(UnifiedDatasetLoader("data/products_master.json"))
            .add_loader(AttackDocumentLoader()))

        # Add attack validator if verification requested
        if verify_attacks:
            populator.add_validator(AttackPatternValidator())

        # Execute population
        result = populator.populate(reset=reset_collection)

        return result.success

    except Exception as e:
        logger.error(f"Error populating database: {e}")
        return False


# Expose deprecated functions for backward compatibility
__all__ = [
    'load_all_products',
    'load_noise_documents',
    'create_attack_documents',
    'populate_database',
]

if __name__ == "__main__":
    warnings.warn(
        "Running populate_vector_db.py directly is deprecated. "
        "Use 'python -m src.vector_db.cli populate' instead.",
        DeprecationWarning,
        stacklevel=2
    )

    print("=" * 80)
    print("DEPRECATION WARNING")
    print("=" * 80)
    print("This script is deprecated. Please use the new CLI:")
    print()
    print("  python -m src.vector_db.cli populate")
    print()
    print("Or for more options:")
    print("  python -m src.vector_db.cli populate --help")
    print("=" * 80)

    # Run populate with default settings for backward compatibility
    success = populate_database()

    if success:
        print("✅ Vector database populated successfully!")
        print("🎉 Database is ready for RAG experiments!")
    else:
        print("❌ Failed to populate vector database")
        import sys
        sys.exit(1)
