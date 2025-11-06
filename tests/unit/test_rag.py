"""Comprehensive unit tests for RAG package."""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from rag import (
    BaseRAG,
    RAGConfig,
    RAGResult,
    VectorRetriever,
    HybridRetriever,
    LLMGenerator,
    RAGPipeline,
    ConsoleObserver,
    StructuredLogger,
    MetricsCollector,
)


class TestRAGConfig:
    """Test RAGConfig dataclass."""

    def test_default_config(self):
        """Test default configuration values."""
        config = RAGConfig()
        assert config.retrieval_top_k == 10
        assert config.rerank_top_k == 5
        assert config.generation_temperature == 0.0
        assert config.max_tokens == 500
        assert config.system_prompt is None
        assert config.metadata == {}

    def test_custom_config(self):
        """Test custom configuration values."""
        config = RAGConfig(
            retrieval_top_k=20,
            rerank_top_k=10,
            generation_temperature=0.7,
            max_tokens=1000,
            system_prompt="Custom prompt",
            metadata={"test": "value"},
        )
        assert config.retrieval_top_k == 20
        assert config.rerank_top_k == 10
        assert config.generation_temperature == 0.7
        assert config.max_tokens == 1000
        assert config.system_prompt == "Custom prompt"
        assert config.metadata == {"test": "value"}

    def test_config_validation(self):
        """Test configuration validation."""
        with pytest.raises(ValueError, match="retrieval_top_k must be >= 1"):
            RAGConfig(retrieval_top_k=0)

        with pytest.raises(ValueError, match="rerank_top_k must be >= 1"):
            RAGConfig(rerank_top_k=0)

        with pytest.raises(ValueError, match="rerank_top_k cannot exceed retrieval_top_k"):
            RAGConfig(retrieval_top_k=5, rerank_top_k=10)

        with pytest.raises(ValueError, match="generation_temperature must be between"):
            RAGConfig(generation_temperature=2.5)

        with pytest.raises(ValueError, match="max_tokens must be >= 1"):
            RAGConfig(max_tokens=0)


class TestRAGResult:
    """Test RAGResult dataclass."""

    def test_rag_result_creation(self):
        """Test creating RAGResult."""
        retrieved_docs = [{"id": "doc1", "content": "test"}]
        result = RAGResult(
            query="test query",
            retrieved_docs=retrieved_docs,
            generated_response="test response",
        )

        assert result.query == "test query"
        assert len(result.retrieved_docs) == 1
        assert result.generated_response == "test response"
        assert result.reranked_docs is None

    def test_final_docs_property(self):
        """Test final_docs property."""
        retrieved = [{"id": "doc1"}]
        reranked = [{"id": "doc2"}]

        # Without reranking
        result1 = RAGResult(query="test", retrieved_docs=retrieved)
        assert result1.final_docs == retrieved

        # With reranking
        result2 = RAGResult(query="test", retrieved_docs=retrieved, reranked_docs=reranked)
        assert result2.final_docs == reranked

    def test_num_properties(self):
        """Test num_retrieved and num_final properties."""
        retrieved = [{"id": f"doc{i}"} for i in range(10)]
        reranked = [{"id": f"doc{i}"} for i in range(5)]

        result = RAGResult(query="test", retrieved_docs=retrieved, reranked_docs=reranked)

        assert result.num_retrieved == 10
        assert result.num_final == 5


class TestVectorRetriever:
    """Test VectorRetriever."""

    def test_vector_retriever_basic(self):
        """Test basic vector retrieval."""
        mock_vector_store = Mock()
        mock_vector_store.search.return_value = [
            ("doc1", 0.95, {"name": "Product 1", "content": "test content"}),
            ("doc2", 0.85, {"name": "Product 2", "content": "test content 2"}),
        ]

        retriever = VectorRetriever(mock_vector_store)
        docs = retriever.retrieve("test query", top_k=2)

        assert len(docs) == 2
        assert docs[0]["id"] == "doc1"
        assert docs[0]["retrieval_score"] == 0.95
        assert docs[1]["id"] == "doc2"
        assert docs[1]["retrieval_score"] == 0.85

        mock_vector_store.search.assert_called_once_with("test query", limit=2)

    def test_vector_retriever_empty_results(self):
        """Test vector retriever with empty results."""
        mock_vector_store = Mock()
        mock_vector_store.search.return_value = []

        retriever = VectorRetriever(mock_vector_store)
        docs = retriever.retrieve("test query", top_k=10)

        assert len(docs) == 0


class TestHybridRetriever:
    """Test HybridRetriever."""

    def test_hybrid_retriever_basic(self):
        """Test basic hybrid retrieval with reranking."""
        # Mock vector store
        mock_vector_store = Mock()
        mock_vector_store.search.return_value = [
            ("doc1", 0.95, {"name": "Product 1", "content": "test 1"}),
            ("doc2", 0.85, {"name": "Product 2", "content": "test 2"}),
        ]

        # Mock reranker
        mock_reranker = Mock()
        mock_ranking_result = Mock()
        mock_ranking_result.rankings = [("doc2", 0.9), ("doc1", 0.7)]
        mock_reranker.rank.return_value = mock_ranking_result

        retriever = HybridRetriever(
            vector_store=mock_vector_store,
            reranker=mock_reranker,
            retrieval_k=20,
            rerank_k=5,
        )

        docs = retriever.retrieve("test query")

        # Should retrieve then rerank
        mock_vector_store.search.assert_called_once()
        mock_reranker.rank.assert_called_once()

        # Results should be in reranked order
        assert len(docs) == 2
        assert docs[0]["id"] == "doc2"
        assert docs[0]["rerank_score"] == 0.9


class TestLLMGenerator:
    """Test LLMGenerator."""

    def test_llm_generator_with_generate_text(self):
        """Test generator with new generate_text interface."""
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "Generated response"
        mock_llm.generate_text.return_value = mock_response

        generator = LLMGenerator(mock_llm)
        documents = [
            {"name": "Product 1", "description": "Test product", "price": 99.99}
        ]

        response = generator.generate("test query", documents)

        assert response == "Generated response"
        mock_llm.generate_text.assert_called_once()

    def test_llm_generator_with_generate_fallback(self):
        """Test generator with old generate interface."""
        mock_llm = Mock(spec=['generate'])  # Only has generate, not generate_text

        mock_response = Mock()
        mock_response.content = "Generated response"
        mock_llm.generate.return_value = mock_response

        generator = LLMGenerator(mock_llm)
        documents = [{"name": "Product 1", "description": "Test product"}]

        response = generator.generate("test query", documents)

        assert response == "Generated response"
        mock_llm.generate.assert_called_once()

    def test_llm_generator_document_formatting(self):
        """Test document formatting in generator."""
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "Generated response"
        mock_llm.generate_text.return_value = mock_response

        generator = LLMGenerator(mock_llm)
        documents = [
            {
                "name": "Product 1",
                "description": "Test product",
                "price": 99.99,
                "rating": 4.5,
                "category": "Electronics",
                "retrieval_score": 0.95,
            }
        ]

        response = generator.generate("test query", documents)

        # Check that generate_text was called with formatted documents
        call_args = mock_llm.generate_text.call_args
        prompt = call_args[1]["prompt"] if "prompt" in call_args[1] else call_args[0][0]

        assert "Product 1" in prompt
        assert "Test product" in prompt
        assert "99.99" in prompt
        assert "4.5" in prompt
        assert "Electronics" in prompt
        assert "0.95" in prompt  # retrieval score


class TestRAGPipeline:
    """Test RAGPipeline."""

    def test_pipeline_builder_pattern(self):
        """Test Builder pattern for pipeline configuration."""
        mock_retriever = Mock()
        mock_generator = Mock()
        mock_observer = Mock()

        pipeline = (
            RAGPipeline()
            .with_retriever(mock_retriever)
            .with_generator(mock_generator)
            .with_observability(mock_observer)
        )

        assert pipeline.retriever == mock_retriever
        assert pipeline.generator == mock_generator
        assert mock_observer in pipeline.observability_hooks

    def test_pipeline_missing_retriever(self):
        """Test error when retriever not configured."""
        pipeline = RAGPipeline()

        with pytest.raises(ValueError, match="No retriever configured"):
            pipeline.retrieve("test query")

    def test_pipeline_missing_generator(self):
        """Test error when generator not configured."""
        pipeline = RAGPipeline()

        with pytest.raises(ValueError, match="No generator configured"):
            pipeline.generate("test query", [])

    def test_pipeline_full_query(self):
        """Test full pipeline query execution."""
        # Mock retriever
        mock_retriever = Mock()
        mock_retriever.retrieve.return_value = [
            {"id": "doc1", "content": "test content"}
        ]

        # Mock generator
        mock_generator = Mock()
        mock_generator.generate.return_value = "Generated response"

        # Mock observer
        mock_observer = Mock()

        # Build pipeline
        pipeline = (
            RAGPipeline()
            .with_retriever(mock_retriever)
            .with_generator(mock_generator)
            .with_observability(mock_observer)
        )

        # Execute query
        result = pipeline.query("test query")

        # Verify result
        assert result.query == "test query"
        assert len(result.retrieved_docs) == 1
        assert result.generated_response == "Generated response"
        assert result.total_time > 0

        # Verify components were called
        mock_retriever.retrieve.assert_called_once()
        mock_generator.generate.assert_called_once()

        # Verify observer was notified
        assert mock_observer.on_stage.call_count >= 3  # start, retrieval, generation, complete


class TestObservability:
    """Test observability hooks."""

    def test_console_observer(self, capsys):
        """Test ConsoleObserver output."""
        observer = ConsoleObserver(verbose=True)
        observer.on_stage("retrieval", {"query": "test", "num_retrieved": 5})

        captured = capsys.readouterr()
        assert "[RETRIEVAL]" in captured.out
        assert "query:" in captured.out
        assert "num_retrieved:" in captured.out

    def test_structured_logger(self, tmp_path):
        """Test StructuredLogger."""
        log_file = tmp_path / "test.log"
        logger = StructuredLogger(str(log_file))

        logger.on_stage("retrieval", {"query": "test", "num_docs": 5})

        # Verify log file exists and contains data
        assert log_file.exists()
        content = log_file.read_text()
        assert "retrieval" in content
        assert "test" in content

    def test_metrics_collector(self):
        """Test MetricsCollector."""
        collector = MetricsCollector()

        # Simulate pipeline stages
        collector.on_stage("retrieval", {"duration": 0.5, "num_retrieved": 10})
        collector.on_stage("generation", {"duration": 1.0})
        collector.on_stage("complete", {})

        summary = collector.get_summary()

        assert summary["total_queries"] == 1
        assert summary["avg_retrieval_time"] == 0.5
        assert summary["avg_generation_time"] == 1.0
        assert summary["avg_documents_retrieved"] == 10

        # Test reset
        collector.reset()
        assert collector.metrics["total_queries"] == 0


class TestIntegration:
    """Integration tests for complete RAG pipeline."""

    def test_end_to_end_pipeline(self):
        """Test complete end-to-end pipeline execution."""
        # Mock vector store
        mock_vector_store = Mock()
        mock_vector_store.search.return_value = [
            ("doc1", 0.95, {"name": "Product 1", "content": "High quality camera"}),
            ("doc2", 0.85, {"name": "Product 2", "content": "Budget camera"}),
        ]

        # Mock LLM client
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "I recommend Product 1 for its high quality."
        mock_llm.generate_text.return_value = mock_response

        # Build pipeline
        retriever = VectorRetriever(mock_vector_store)
        generator = LLMGenerator(mock_llm)
        metrics = MetricsCollector()

        pipeline = (
            RAGPipeline()
            .with_retriever(retriever)
            .with_generator(generator)
            .with_observability(metrics)
        )

        # Execute query
        result = pipeline.query("best camera for photography")

        # Verify results
        assert result.query == "best camera for photography"
        assert result.num_retrieved == 2
        assert "Product 1" in result.generated_response
        assert result.total_time > 0

        # Verify metrics
        summary = metrics.get_summary()
        assert summary["total_queries"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
