"""RAG pipeline orchestration with Builder pattern."""

from typing import List, Dict, Any, Optional
import time
from .base import BaseRAG, RAGConfig, RAGResult
from .retriever import BaseRetriever
from .generator import BaseGenerator
from .observability import ObservabilityHook


class RAGPipeline(BaseRAG):
    """RAG pipeline with configurable stages and observability.

    Uses Builder pattern for flexible configuration:

    Example:
        >>> pipeline = (RAGPipeline()
        ...     .with_retriever(VectorRetriever(vector_store))
        ...     .with_generator(LLMGenerator(llm))
        ...     .with_observability(ConsoleObserver()))
        >>>
        >>> result = pipeline.query("What's the best camera?")
    """

    def __init__(self, config: Optional[RAGConfig] = None):
        """Initialize pipeline.

        Args:
            config: RAG configuration (uses defaults if not provided)
        """
        self.config = config or RAGConfig()
        self.retriever: Optional[BaseRetriever] = None
        self.generator: Optional[BaseGenerator] = None
        self.observability_hooks: List[ObservabilityHook] = []

    def with_retriever(self, retriever: BaseRetriever) -> "RAGPipeline":
        """Set retriever (Builder pattern).

        Args:
            retriever: Retriever instance

        Returns:
            Self for method chaining
        """
        self.retriever = retriever
        return self

    def with_generator(self, generator: BaseGenerator) -> "RAGPipeline":
        """Set generator (Builder pattern).

        Args:
            generator: Generator instance

        Returns:
            Self for method chaining
        """
        self.generator = generator
        return self

    def with_observability(self, hook: ObservabilityHook) -> "RAGPipeline":
        """Add observability hook (Observer pattern).

        Args:
            hook: Observability hook to add

        Returns:
            Self for method chaining
        """
        self.observability_hooks.append(hook)
        return self

    def with_config(self, config: RAGConfig) -> "RAGPipeline":
        """Set configuration (Builder pattern).

        Args:
            config: RAG configuration

        Returns:
            Self for method chaining
        """
        self.config = config
        return self

    def retrieve(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """Retrieve documents (implements BaseRAG).

        Args:
            query: Search query
            top_k: Override config's retrieval_top_k

        Returns:
            Retrieved documents

        Raises:
            ValueError: If no retriever configured
        """
        if not self.retriever:
            raise ValueError("No retriever configured. Use with_retriever()")

        k = top_k if top_k is not None else self.config.retrieval_top_k
        docs = self.retriever.retrieve(query, top_k=k)

        # Notify observers
        self._notify_stage(
            "retrieval", {"query": query, "top_k": k, "num_retrieved": len(docs)}
        )

        return docs

    def generate(self, query: str, documents: List[Dict[str, Any]]) -> str:
        """Generate response (implements BaseRAG).

        Args:
            query: User query
            documents: Retrieved documents

        Returns:
            Generated response

        Raises:
            ValueError: If no generator configured
        """
        if not self.generator:
            raise ValueError("No generator configured. Use with_generator()")

        response = self.generator.generate(query, documents)

        # Notify observers
        self._notify_stage(
            "generation",
            {"query": query, "num_docs": len(documents), "response_length": len(response)},
        )

        return response

    def query(self, query: str) -> RAGResult:
        """Execute full RAG pipeline with observability.

        Args:
            query: User query

        Returns:
            RAGResult with complete pipeline output
        """
        start_time = time.time()
        observability_log = []

        # Notify start
        self._notify_stage("start", {"query": query})

        # Retrieval stage
        retrieval_start = time.time()
        docs = self.retrieve(query)
        retrieval_time = time.time() - retrieval_start

        observability_log.append(
            {"stage": "retrieval", "duration": retrieval_time, "num_docs": len(docs)}
        )

        # Generation stage
        generation_start = time.time()
        response = self.generate(query, docs)
        generation_time = time.time() - generation_start

        observability_log.append(
            {
                "stage": "generation",
                "duration": generation_time,
                "response_length": len(response),
            }
        )

        total_time = time.time() - start_time

        result = RAGResult(
            query=query,
            retrieved_docs=docs,
            generated_response=response,
            retrieval_time=retrieval_time,
            generation_time=generation_time,
            total_time=total_time,
            observability_log=observability_log,
        )

        # Notify observers of final result
        self._notify_stage("complete", {"result": result})

        return result

    def _notify_stage(self, stage: str, data: Dict[str, Any]) -> None:
        """Notify all observability hooks of pipeline stage.

        Args:
            stage: Stage name
            data: Stage data
        """
        for hook in self.observability_hooks:
            try:
                hook.on_stage(stage, data)
            except Exception as e:
                # Don't let observer errors break pipeline
                import logging

                logging.warning(f"Observer error in stage {stage}: {e}")
