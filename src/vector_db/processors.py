"""
Data processors for vector database population.

This module provides abstract and concrete data processor implementations
for transforming, batching, and enriching data before insertion into
the vector database.

Classes:
    DataProcessor: Abstract base class for all data processors
    BatchProcessor: Processes data in batches for efficiency
    EmbeddingProcessor: Generates embeddings for documents
    MetadataProcessor: Enriches documents with metadata
    ContentProcessor: Normalizes and validates content fields

Example:
    >>> from vector_db import BatchProcessor, EmbeddingProcessor
    >>> batch_proc = BatchProcessor(batch_size=100)
    >>> embed_proc = EmbeddingProcessor(embedding_provider, text_field="description")
    >>>
    >>> for batch in batch_proc.process(documents):
    ...     enriched = embed_proc.process(batch)
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Iterator, Optional
import logging

from .exceptions import ProcessingError

logger = logging.getLogger(__name__)


class DataProcessor(ABC):
    """Abstract base class for data processors.

    All data processors must implement the process() method to transform
    data in a consistent way.
    """

    @abstractmethod
    def process(self, data: List[Dict[str, Any]]) -> Any:
        """Process data.

        Args:
            data: Input data to process

        Returns:
            Processed data (type depends on processor implementation)

        Raises:
            ProcessingError: If processing fails
        """
        pass


class BatchProcessor(DataProcessor):
    """Processes data in batches for memory efficiency and performance.

    This processor yields data in fixed-size batches, which is useful for:
    - Memory-efficient processing of large datasets
    - Batch API calls to embedding providers
    - Parallel processing across multiple batches

    Example:
        >>> processor = BatchProcessor(batch_size=100)
        >>> for batch in processor.process(documents):
        ...     # Process each batch
        ...     print(f"Processing {len(batch)} documents")
    """

    def __init__(self, batch_size: int = 100):
        """Initialize batch processor.

        Args:
            batch_size: Number of items per batch

        Raises:
            ValueError: If batch_size is not positive
        """
        if batch_size <= 0:
            raise ValueError(f"Batch size must be positive, got {batch_size}")

        self.batch_size = batch_size
        logger.debug(f"Initialized BatchProcessor with batch_size={batch_size}")

    def process(self, data: List[Dict[str, Any]]) -> Iterator[List[Dict[str, Any]]]:
        """Yield data in batches.

        Args:
            data: Full dataset to batch

        Yields:
            Batches of data (each batch has at most batch_size items)

        Raises:
            ProcessingError: If batching fails
        """
        try:
            total_items = len(data)
            num_batches = (total_items + self.batch_size - 1) // self.batch_size

            logger.info(f"Processing {total_items} items in {num_batches} batches of {self.batch_size}")

            for i in range(0, total_items, self.batch_size):
                batch = data[i:i + self.batch_size]
                batch_num = i // self.batch_size + 1

                logger.debug(f"Yielding batch {batch_num}/{num_batches} ({len(batch)} items)")
                yield batch

        except Exception as e:
            raise ProcessingError(
                "Failed to batch data",
                details={"batch_size": self.batch_size, "total_items": len(data)},
                original_error=e
            )


class EmbeddingProcessor(DataProcessor):
    """Generates embeddings for documents using an embedding provider.

    This processor adds embedding vectors to documents by:
    1. Extracting text from specified field
    2. Generating embeddings via provider
    3. Adding 'embedding' field to each document

    Example:
        >>> from langchain_community.embeddings import OpenAIEmbeddings
        >>> embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        >>> processor = EmbeddingProcessor(embeddings, text_field="description")
        >>> enriched_docs = processor.process(documents)
    """

    def __init__(
        self,
        embedding_provider: Any,
        text_field: str = "content",
        embedding_field: str = "embedding"
    ):
        """Initialize embedding processor.

        Args:
            embedding_provider: Embedding provider with embed_documents method
            text_field: Field to extract text from for embedding
            embedding_field: Field name to store embedding vectors
        """
        self.embedding_provider = embedding_provider
        self.text_field = text_field
        self.embedding_field = embedding_field

        logger.debug(
            f"Initialized EmbeddingProcessor with text_field='{text_field}', "
            f"embedding_field='{embedding_field}'"
        )

    def process(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add embedding vectors to documents.

        Args:
            data: Documents to embed

        Returns:
            Documents with embedding field added

        Raises:
            ProcessingError: If embedding generation fails
        """
        try:
            if not data:
                logger.warning("No data to process for embeddings")
                return data

            # Extract text for embedding
            texts = []
            for doc in data:
                text = doc.get(self.text_field, "")
                if not text:
                    logger.warning(f"Document {doc.get('id', 'unknown')} has no {self.text_field} field")
                    text = doc.get("description", doc.get("name", ""))
                texts.append(text)

            logger.info(f"Generating embeddings for {len(texts)} documents")

            # Generate embeddings
            embeddings = self.embedding_provider.embed_documents(texts)

            # Add embeddings to documents
            for doc, embedding in zip(data, embeddings):
                doc[self.embedding_field] = embedding

            logger.info(f"Successfully added embeddings to {len(data)} documents")
            return data

        except Exception as e:
            raise ProcessingError(
                "Failed to generate embeddings",
                details={
                    "text_field": self.text_field,
                    "document_count": len(data),
                    "provider": str(type(self.embedding_provider).__name__)
                },
                original_error=e
            )


class MetadataProcessor(DataProcessor):
    """Enriches documents with metadata fields.

    This processor extracts and structures metadata from documents,
    ensuring consistent metadata format across all documents.

    Example:
        >>> processor = MetadataProcessor(["id", "name", "category", "type"])
        >>> enriched_docs = processor.process(documents)
    """

    def __init__(self, metadata_fields: List[str]):
        """Initialize metadata processor.

        Args:
            metadata_fields: List of fields to include in metadata
        """
        self.metadata_fields = metadata_fields
        logger.debug(f"Initialized MetadataProcessor with fields: {metadata_fields}")

    def process(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract and structure metadata.

        Args:
            data: Documents to process

        Returns:
            Documents with structured metadata

        Raises:
            ProcessingError: If metadata processing fails
        """
        try:
            for doc in data:
                # Create metadata dict if it doesn't exist
                if "metadata" not in doc:
                    doc["metadata"] = {}

                # Extract specified fields into metadata
                for field in self.metadata_fields:
                    if field in doc and field != "metadata":
                        doc["metadata"][field] = doc[field]

            logger.info(f"Processed metadata for {len(data)} documents")
            return data

        except Exception as e:
            raise ProcessingError(
                "Failed to process metadata",
                details={"metadata_fields": self.metadata_fields},
                original_error=e
            )


class ContentProcessor(DataProcessor):
    """Normalizes and validates content fields.

    This processor ensures all documents have required content fields
    and normalizes them to a consistent format.

    Example:
        >>> processor = ContentProcessor(
        ...     content_field="content",
        ...     fallback_fields=["description", "name"]
        ... )
        >>> normalized_docs = processor.process(documents)
    """

    def __init__(
        self,
        content_field: str = "content",
        fallback_fields: Optional[List[str]] = None,
        min_length: int = 0
    ):
        """Initialize content processor.

        Args:
            content_field: Primary content field name
            fallback_fields: Fields to use if content_field is missing
            min_length: Minimum content length (0 = no minimum)
        """
        self.content_field = content_field
        self.fallback_fields = fallback_fields or ["description", "name"]
        self.min_length = min_length

        logger.debug(
            f"Initialized ContentProcessor with content_field='{content_field}', "
            f"fallback_fields={fallback_fields}, min_length={min_length}"
        )

    def process(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normalize and validate content fields.

        Args:
            data: Documents to process

        Returns:
            Documents with normalized content

        Raises:
            ProcessingError: If content processing fails
        """
        try:
            processed_count = 0
            fallback_count = 0
            warning_count = 0

            for doc in data:
                # Check if content field exists
                if self.content_field not in doc or not doc[self.content_field]:
                    # Try fallback fields
                    content = None
                    for fallback_field in self.fallback_fields:
                        if fallback_field in doc and doc[fallback_field]:
                            content = doc[fallback_field]
                            fallback_count += 1
                            break

                    if content:
                        doc[self.content_field] = content
                    else:
                        logger.warning(
                            f"Document {doc.get('id', 'unknown')} has no content in "
                            f"{self.content_field} or fallback fields {self.fallback_fields}"
                        )
                        doc[self.content_field] = ""
                        warning_count += 1

                # Validate minimum length
                content = doc[self.content_field]
                if isinstance(content, str) and len(content) < self.min_length:
                    logger.warning(
                        f"Document {doc.get('id', 'unknown')} content length "
                        f"({len(content)}) is below minimum ({self.min_length})"
                    )
                    warning_count += 1

                processed_count += 1

            logger.info(
                f"Processed content for {processed_count} documents "
                f"(fallbacks: {fallback_count}, warnings: {warning_count})"
            )
            return data

        except Exception as e:
            raise ProcessingError(
                "Failed to process content",
                details={
                    "content_field": self.content_field,
                    "fallback_fields": self.fallback_fields
                },
                original_error=e
            )
