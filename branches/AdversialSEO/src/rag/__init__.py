"""RAG (Retrieval-Augmented Generation) package with glass-box transparency.

This package provides a transparent RAG system for adversarial SEO research,
with complete visibility into retrieval, reranking, and generation stages.

Example:
    >>> from src.rag import RAGPipeline, VectorRetriever, LLMGenerator
    >>> from src.llm import create_llm_client
    >>> from src.vector_store import VectorStoreManager
    >>>
    >>> llm = create_llm_client(provider="openai")
    >>> vector_store = VectorStoreManager()
    >>>
    >>> pipeline = (RAGPipeline()
    ...     .with_retriever(VectorRetriever(vector_store))
    ...     .with_generator(LLMGenerator(llm))
    ...     .with_observability(ConsoleObserver()))
    >>>
    >>> result = pipeline.query("What camera should I buy?")
"""

from .base import BaseRAG, RAGConfig, RAGResult
from .retriever import BaseRetriever, VectorRetriever, HybridRetriever
from .generator import BaseGenerator, LLMGenerator
from .pipeline import RAGPipeline
from .observability import ObservabilityHook, ConsoleObserver, StructuredLogger, MetricsCollector

__all__ = [
    'BaseRAG',
    'RAGConfig',
    'RAGResult',
    'BaseRetriever',
    'VectorRetriever',
    'HybridRetriever',
    'BaseGenerator',
    'LLMGenerator',
    'RAGPipeline',
    'ObservabilityHook',
    'ConsoleObserver',
    'StructuredLogger',
    'MetricsCollector',
]

__version__ = '1.0.0'
