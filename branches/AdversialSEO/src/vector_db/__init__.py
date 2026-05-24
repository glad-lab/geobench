"""
Vector database package for adversarial SEO research.

This package provides a modular, well-tested system for populating and managing
vector databases with product catalogs and adversarial attack documents.

Architecture:
    - Loaders: Load data from various sources (unified dataset, legacy formats, noise docs)
    - Processors: Transform and enrich data (batching, embedding, metadata)
    - Validators: Validate data quality (schema, attack patterns, integrity)
    - Populator: Orchestrate the complete population pipeline (Builder pattern)
    - CLI: Command-line interface for database operations

Example - Basic Usage:
    >>> from vector_db import VectorDBPopulator, UnifiedDatasetLoader
    >>> from vector_store import VectorStoreManager
    >>>
    >>> vector_store = VectorStoreManager()
    >>> populator = (VectorDBPopulator(vector_store)
    ...     .add_loader(UnifiedDatasetLoader("data/products_master.json"))
    ...     .populate(reset=True))

Example - Advanced Usage:
    >>> from vector_db import (
    ...     VectorDBPopulator,
    ...     UnifiedDatasetLoader,
    ...     AttackDocumentLoader,
    ...     BatchProcessor,
    ...     ContentProcessor,
    ...     SchemaValidator,
    ...     AttackPatternValidator
    ... )
    >>>
    >>> def on_progress(event):
    ...     print(f"{event.stage}: {event.progress}% - {event.message}")
    >>>
    >>> populator = (VectorDBPopulator(vector_store)
    ...     .add_loader(UnifiedDatasetLoader("data/products_master.json"))
    ...     .add_loader(AttackDocumentLoader())
    ...     .add_processor(BatchProcessor(batch_size=100))
    ...     .add_processor(ContentProcessor(content_field="content"))
    ...     .add_validator(SchemaValidator(required_fields=["id", "content"]))
    ...     .add_validator(AttackPatternValidator())
    ...     .with_progress_tracking(on_progress)
    ...     .populate(reset=True))

Example - CLI Usage:
    # Basic population
    python -m src.vector_db.cli populate

    # Full reset with verification
    python -m src.vector_db.cli populate --reset --verify

    # Custom configuration
    python -m src.vector_db.cli populate --batch-size 50 --provider gemini
"""

# Core classes
from .populator import (
    VectorDBPopulator,
    PopulationEvent,
    PopulationResult
)

# Loaders
from .loaders import (
    DataLoader,
    UnifiedDatasetLoader,
    ProductCatalogLoader,
    NoiseDocumentLoader,
    AttackDocumentLoader,
    LoaderFactory
)

# Processors
from .processors import (
    DataProcessor,
    BatchProcessor,
    EmbeddingProcessor,
    MetadataProcessor,
    ContentProcessor
)

# Validators
from .validators import (
    ValidationResult,
    DataValidator,
    SchemaValidator,
    AttackPatternValidator,
    IntegrityValidator,
    ContentValidator
)

# Exceptions
from .exceptions import (
    VectorDBError,
    DataLoadError,
    DataSourceError,
    ProcessingError,
    ValidationError,
    PopulationError,
    EmbeddingError
)

__all__ = [
    # Core classes
    'VectorDBPopulator',
    'PopulationEvent',
    'PopulationResult',

    # Loaders
    'DataLoader',
    'UnifiedDatasetLoader',
    'ProductCatalogLoader',
    'NoiseDocumentLoader',
    'AttackDocumentLoader',
    'LoaderFactory',

    # Processors
    'DataProcessor',
    'BatchProcessor',
    'EmbeddingProcessor',
    'MetadataProcessor',
    'ContentProcessor',

    # Validators
    'ValidationResult',
    'DataValidator',
    'SchemaValidator',
    'AttackPatternValidator',
    'IntegrityValidator',
    'ContentValidator',

    # Exceptions
    'VectorDBError',
    'DataLoadError',
    'DataSourceError',
    'ProcessingError',
    'ValidationError',
    'PopulationError',
    'EmbeddingError',
]

__version__ = '2.0.0'
