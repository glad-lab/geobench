"""Base classes and abstractions for RAG system components."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class RAGConfig:
    """Configuration for RAG pipeline.

    Attributes:
        retrieval_top_k: Number of documents to retrieve
        rerank_top_k: Number of documents after reranking
        generation_temperature: LLM temperature
        max_tokens: Maximum generation tokens
        system_prompt: System prompt for generation
        metadata: Additional configuration
    """

    retrieval_top_k: int = 10
    rerank_top_k: int = 5
    generation_temperature: float = 0.0
    max_tokens: int = 500
    system_prompt: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.retrieval_top_k < 1:
            raise ValueError("retrieval_top_k must be >= 1")
        if self.rerank_top_k < 1:
            raise ValueError("rerank_top_k must be >= 1")
        if self.rerank_top_k > self.retrieval_top_k:
            raise ValueError("rerank_top_k cannot exceed retrieval_top_k")
        if not 0.0 <= self.generation_temperature <= 2.0:
            raise ValueError("generation_temperature must be between 0.0 and 2.0")
        if self.max_tokens < 1:
            raise ValueError("max_tokens must be >= 1")


@dataclass
class RAGResult:
    """Result of RAG pipeline execution.

    Attributes:
        query: Original query
        retrieved_docs: Documents from retrieval stage
        reranked_docs: Documents after reranking (if applicable)
        generated_response: LLM-generated response
        retrieval_time: Time for retrieval (seconds)
        generation_time: Time for generation (seconds)
        total_time: Total pipeline time (seconds)
        metadata: Additional result metadata
        observability_log: Log of pipeline stages (if observability enabled)
    """

    query: str
    retrieved_docs: List[Dict[str, Any]]
    reranked_docs: Optional[List[Dict[str, Any]]] = None
    generated_response: str = ""
    retrieval_time: float = 0.0
    generation_time: float = 0.0
    total_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    observability_log: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def final_docs(self) -> List[Dict[str, Any]]:
        """Get final documents used for generation."""
        return self.reranked_docs if self.reranked_docs else self.retrieved_docs

    @property
    def num_retrieved(self) -> int:
        """Get number of documents retrieved."""
        return len(self.retrieved_docs)

    @property
    def num_final(self) -> int:
        """Get number of final documents used for generation."""
        return len(self.final_docs)

    def __str__(self) -> str:
        """Format result for display."""
        return (
            f"RAGResult(query='{self.query[:50]}...', "
            f"retrieved={self.num_retrieved}, "
            f"final={self.num_final}, "
            f"time={self.total_time:.2f}s)"
        )


class BaseRAG(ABC):
    """Abstract base class for RAG systems.

    Defines the interface for retrieval-augmented generation systems.
    """

    @abstractmethod
    def retrieve(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Retrieve relevant documents.

        Args:
            query: Search query
            top_k: Number of documents to retrieve

        Returns:
            List of retrieved documents with scores
        """
        pass

    @abstractmethod
    def generate(self, query: str, documents: List[Dict[str, Any]]) -> str:
        """Generate response from documents.

        Args:
            query: Original query
            documents: Retrieved documents

        Returns:
            Generated response text
        """
        pass

    def query(self, query: str) -> RAGResult:
        """Execute full RAG pipeline (Template Method pattern).

        Args:
            query: User query

        Returns:
            RAGResult with full pipeline output
        """
        import time

        start_time = time.time()

        # Retrieve
        retrieval_start = time.time()
        docs = self.retrieve(query)
        retrieval_time = time.time() - retrieval_start

        # Generate
        generation_start = time.time()
        response = self.generate(query, docs)
        generation_time = time.time() - generation_start

        total_time = time.time() - start_time

        return RAGResult(
            query=query,
            retrieved_docs=docs,
            generated_response=response,
            retrieval_time=retrieval_time,
            generation_time=generation_time,
            total_time=total_time,
        )
