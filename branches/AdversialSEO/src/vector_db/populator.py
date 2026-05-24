"""
Vector database populator with Builder pattern.

This module provides the main VectorDBPopulator class that orchestrates
the complete population pipeline using a fluent Builder pattern.

Classes:
    PopulationEvent: Event emitted during population (Observer pattern)
    PopulationResult: Result of population operation
    VectorDBPopulator: Main populator class with Builder pattern

Example:
    >>> from vector_db import VectorDBPopulator, UnifiedDatasetLoader
    >>> from vector_store import VectorStoreManager
    >>>
    >>> vector_store = VectorStoreManager()
    >>> populator = (VectorDBPopulator(vector_store)
    ...     .add_loader(UnifiedDatasetLoader("data/products_master.json"))
    ...     .add_processor(BatchProcessor(batch_size=100))
    ...     .add_validator(AttackPatternValidator())
    ...     .with_progress_tracking(lambda e: print(f"{e.stage}: {e.progress}%"))
    ...     .populate(reset=True))
"""

from typing import List, Optional, Callable, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
import time
import logging

from .loaders import DataLoader
from .processors import DataProcessor
from .validators import DataValidator, ValidationResult
from .exceptions import PopulationError

logger = logging.getLogger(__name__)


@dataclass
class PopulationEvent:
    """Event emitted during population (Observer pattern).

    Attributes:
        stage: Current stage of population
        progress: Progress percentage (0-100)
        message: Human-readable message
        timestamp: Event timestamp
        details: Additional event details
    """
    stage: str
    progress: float
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    details: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        """Format event as string."""
        return (
            f"[{self.timestamp.strftime('%H:%M:%S')}] "
            f"{self.stage} ({self.progress:.1f}%): {self.message}"
        )


@dataclass
class PopulationResult:
    """Result of population operation.

    Attributes:
        success: Whether population succeeded
        documents_processed: Number of documents processed
        documents_stored: Number of documents stored in vector DB
        errors: List of error messages
        warnings: List of warning messages
        duration: Population duration in seconds
        metadata: Additional result metadata
        validation_results: Results from all validators
    """
    success: bool
    documents_processed: int
    documents_stored: int
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    duration: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    validation_results: List[ValidationResult] = field(default_factory=list)

    def __str__(self) -> str:
        """Format result as string."""
        status = "SUCCESS" if self.success else "FAILURE"
        parts = [
            f"Population {status}",
            f"Processed: {self.documents_processed} documents",
            f"Stored: {self.documents_stored} documents",
            f"Duration: {self.duration:.2f}s"
        ]

        if self.errors:
            parts.append(f"Errors: {len(self.errors)}")
            parts.extend(f"  - {error}" for error in self.errors[:3])
            if len(self.errors) > 3:
                parts.append(f"  ... and {len(self.errors) - 3} more errors")

        if self.warnings:
            parts.append(f"Warnings: {len(self.warnings)}")

        if self.metadata:
            parts.append("Metadata:")
            for key, value in self.metadata.items():
                parts.append(f"  {key}: {value}")

        return "\n".join(parts)


class VectorDBPopulator:
    """Manages vector database population using Builder pattern.

    This class orchestrates the complete population pipeline:
    1. Load data from all loaders
    2. Process data through all processors
    3. Validate data with all validators
    4. Store data in vector database

    The Builder pattern allows flexible configuration through method chaining.

    Example:
        >>> populator = (VectorDBPopulator(vector_store)
        ...     .add_loader(UnifiedDatasetLoader("data/products_master.json"))
        ...     .add_loader(AttackDocumentLoader())
        ...     .add_processor(BatchProcessor(batch_size=100))
        ...     .add_validator(SchemaValidator(required_fields=["id", "content"]))
        ...     .add_validator(AttackPatternValidator())
        ...     .with_progress_tracking(on_progress)
        ...     .populate(reset=True))
    """

    def __init__(self, vector_store: Any):
        """Initialize populator.

        Args:
            vector_store: VectorStore instance to populate
        """
        self.vector_store = vector_store
        self.loaders: List[DataLoader] = []
        self.processors: List[DataProcessor] = []
        self.validators: List[DataValidator] = []
        self.progress_callback: Optional[Callable[[PopulationEvent], None]] = None

        logger.debug(f"Initialized VectorDBPopulator with vector_store={type(vector_store).__name__}")

    def add_loader(self, loader: DataLoader) -> 'VectorDBPopulator':
        """Add data loader (Builder pattern).

        Args:
            loader: DataLoader instance

        Returns:
            Self for method chaining

        Example:
            >>> populator.add_loader(UnifiedDatasetLoader("data/products.json"))
        """
        self.loaders.append(loader)
        logger.debug(f"Added loader: {type(loader).__name__}")
        return self

    def add_processor(self, processor: DataProcessor) -> 'VectorDBPopulator':
        """Add data processor (Builder pattern).

        Args:
            processor: DataProcessor instance

        Returns:
            Self for method chaining

        Example:
            >>> populator.add_processor(BatchProcessor(batch_size=100))
        """
        self.processors.append(processor)
        logger.debug(f"Added processor: {type(processor).__name__}")
        return self

    def add_validator(self, validator: DataValidator) -> 'VectorDBPopulator':
        """Add data validator (Builder pattern).

        Args:
            validator: DataValidator instance

        Returns:
            Self for method chaining

        Example:
            >>> populator.add_validator(AttackPatternValidator())
        """
        self.validators.append(validator)
        logger.debug(f"Added validator: {type(validator).__name__}")
        return self

    def with_progress_tracking(
        self,
        callback: Callable[[PopulationEvent], None]
    ) -> 'VectorDBPopulator':
        """Enable progress tracking (Observer pattern).

        Args:
            callback: Function called with PopulationEvent on progress updates

        Returns:
            Self for method chaining

        Example:
            >>> def on_progress(event: PopulationEvent):
            ...     print(f"{event.stage}: {event.progress}% - {event.message}")
            >>> populator.with_progress_tracking(on_progress)
        """
        self.progress_callback = callback
        logger.debug("Enabled progress tracking")
        return self

    def populate(
        self,
        reset: bool = False,
        batch_size: int = 100,
        skip_validation: bool = False
    ) -> PopulationResult:
        """Execute population pipeline.

        Pipeline stages:
        1. Load data from all loaders
        2. Process data through all processors
        3. Validate data with all validators (unless skipped)
        4. Store data in vector database

        Args:
            reset: If True, clear collection before populating
            batch_size: Batch size for database insertion
            skip_validation: If True, skip validation stage

        Returns:
            PopulationResult with statistics and errors

        Raises:
            PopulationError: If population fails
        """
        start_time = time.time()
        errors = []
        warnings = []
        validation_results = []

        try:
            logger.info("=" * 80)
            logger.info("Starting vector database population")
            logger.info("=" * 80)

            # Validate configuration
            if not self.loaders:
                raise PopulationError(
                    "No loaders configured",
                    details={"loaders": 0, "processors": len(self.processors), "validators": len(self.validators)}
                )

            # Stage 1: Load data
            self._emit_event("Loading", 0, "Loading data from all sources")

            all_data = []
            for i, loader in enumerate(self.loaders):
                loader_name = type(loader).__name__
                logger.info(f"Loading data from {loader_name} ({i + 1}/{len(self.loaders)})")

                try:
                    data = loader.load()
                    all_data.extend(data)
                    logger.info(f"Loaded {len(data)} documents from {loader_name}")
                except Exception as e:
                    error_msg = f"Loader {loader_name} failed: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)

            if not all_data:
                raise PopulationError(
                    "No data loaded from any loader",
                    details={"loaders": len(self.loaders), "documents": 0}
                )

            progress = 25
            self._emit_event(
                "Loading",
                progress,
                f"Loaded {len(all_data)} documents from {len(self.loaders)} loaders"
            )

            # Stage 2: Process data
            self._emit_event("Processing", progress, "Processing data through pipeline")

            processed_data = all_data
            for i, processor in enumerate(self.processors):
                processor_name = type(processor).__name__
                logger.info(f"Processing data with {processor_name} ({i + 1}/{len(self.processors)})")

                try:
                    # Handle both regular processors and batch processors
                    result = processor.process(processed_data)

                    # If processor returns an iterator (BatchProcessor), collect all batches
                    if hasattr(result, '__iter__') and not isinstance(result, (list, dict, str)):
                        batches = list(result)
                        # Flatten batches back into single list
                        processed_data = []
                        for batch in batches:
                            if isinstance(batch, list):
                                processed_data.extend(batch)
                            else:
                                processed_data.append(batch)
                    else:
                        processed_data = result

                    logger.info(f"Processed {len(processed_data)} documents with {processor_name}")

                except Exception as e:
                    error_msg = f"Processor {processor_name} failed: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)

            progress = 50
            self._emit_event(
                "Processing",
                progress,
                f"Processed {len(processed_data)} documents through {len(self.processors)} processors"
            )

            # Stage 3: Validate data
            if not skip_validation and self.validators:
                self._emit_event("Validating", progress, "Validating data quality")

                for i, validator in enumerate(self.validators):
                    validator_name = type(validator).__name__
                    logger.info(f"Validating data with {validator_name} ({i + 1}/{len(self.validators)})")

                    try:
                        result = validator.validate(processed_data)
                        validation_results.append(result)

                        if not result.is_valid:
                            errors.extend(result.errors)
                            logger.error(
                                f"{validator_name} validation failed with {len(result.errors)} errors"
                            )
                        else:
                            logger.info(f"{validator_name} validation passed")

                        warnings.extend(result.warnings)

                    except Exception as e:
                        error_msg = f"Validator {validator_name} failed: {str(e)}"
                        logger.error(error_msg)
                        errors.append(error_msg)

                progress = 75
                self._emit_event(
                    "Validating",
                    progress,
                    f"Validation complete: {len(self.validators)} validators run"
                )
            else:
                logger.info("Skipping validation stage")
                progress = 75

            # Stage 4: Store data
            self._emit_event("Storing", progress, "Storing documents in vector database")

            if reset:
                logger.info("Resetting vector store collection")
                try:
                    # Use the vector store's reset method if available
                    if hasattr(self.vector_store, 'clear_collection'):
                        self.vector_store.clear_collection()
                    elif hasattr(self.vector_store, 'reset_collection'):
                        self.vector_store.reset_collection()
                    else:
                        logger.warning("Vector store does not support collection reset")
                except Exception as e:
                    error_msg = f"Failed to reset collection: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)

            # Store documents
            logger.info(f"Storing {len(processed_data)} documents in vector database")

            try:
                success = self.vector_store.add_documents(processed_data, batch_size=batch_size)

                if success:
                    stored_count = len(processed_data)
                    logger.info(f"Successfully stored {stored_count} documents")
                else:
                    stored_count = 0
                    error_msg = "Vector store add_documents returned False"
                    logger.error(error_msg)
                    errors.append(error_msg)

            except Exception as e:
                stored_count = 0
                error_msg = f"Failed to store documents: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)

            progress = 100
            self._emit_event(
                "Storing",
                progress,
                f"Stored {stored_count} documents in vector database"
            )

            # Calculate final statistics
            duration = time.time() - start_time
            success = len(errors) == 0 and stored_count > 0

            result = PopulationResult(
                success=success,
                documents_processed=len(processed_data),
                documents_stored=stored_count,
                errors=errors,
                warnings=warnings,
                duration=duration,
                metadata={
                    "loaders": len(self.loaders),
                    "processors": len(self.processors),
                    "validators": len(self.validators),
                    "reset": reset,
                    "batch_size": batch_size,
                    "skip_validation": skip_validation
                },
                validation_results=validation_results
            )

            logger.info("=" * 80)
            if success:
                logger.info("Population completed successfully")
            else:
                logger.error("Population completed with errors")
            logger.info(f"Duration: {duration:.2f}s")
            logger.info(f"Documents processed: {len(processed_data)}")
            logger.info(f"Documents stored: {stored_count}")
            logger.info(f"Errors: {len(errors)}")
            logger.info(f"Warnings: {len(warnings)}")
            logger.info("=" * 80)

            return result

        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Population failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            errors.append(error_msg)

            return PopulationResult(
                success=False,
                documents_processed=0,
                documents_stored=0,
                errors=errors,
                warnings=warnings,
                duration=duration,
                metadata={
                    "loaders": len(self.loaders),
                    "processors": len(self.processors),
                    "validators": len(self.validators)
                }
            )

    def _emit_event(
        self,
        stage: str,
        progress: float,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Emit progress event (Observer pattern).

        Args:
            stage: Current stage name
            progress: Progress percentage (0-100)
            message: Human-readable message
            details: Additional event details
        """
        if self.progress_callback:
            event = PopulationEvent(
                stage=stage,
                progress=progress,
                message=message,
                details=details or {}
            )

            try:
                self.progress_callback(event)
            except Exception as e:
                logger.warning(f"Progress callback failed: {e}")
