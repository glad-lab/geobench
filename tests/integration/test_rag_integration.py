"""Integration tests for RAG package with real components."""

import pytest
import os
from pathlib import Path


@pytest.mark.integration
class TestRAGIntegration:
    """Integration tests requiring real services."""

    @pytest.fixture
    def vector_store(self):
        """Create test vector store."""
        from src.vector_store import VectorStoreManager

        # Use test collection
        store = VectorStoreManager(
            collection_name="test_rag_integration",
            embedding_provider="gemini",
            reset_collection=True,
        )

        # Add test documents
        test_docs = [
            {
                "id": "cam1",
                "name": "Camera Pro X1",
                "description": "Professional DSLR camera with 45MP sensor",
                "price": 1299.99,
                "rating": 4.8,
                "category": "Cameras",
            },
            {
                "id": "cam2",
                "name": "Budget Cam Y1",
                "description": "Affordable point-and-shoot camera for beginners",
                "price": 199.99,
                "rating": 4.2,
                "category": "Cameras",
            },
            {
                "id": "cam3",
                "name": "Mirrorless Z1",
                "description": "Compact mirrorless camera with 4K video",
                "price": 899.99,
                "rating": 4.6,
                "category": "Cameras",
            },
        ]

        store.add_documents(test_docs)

        yield store

        # Cleanup
        store.clear_collection()

    @pytest.fixture
    def llm_client(self):
        """Create test LLM client."""
        from src.llm import create_llm_client

        # Skip if no API key
        if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("No LLM API key available")

        provider = "anthropic" if os.getenv("ANTHROPIC_API_KEY") else "openai"
        model = (
            "claude-3-haiku-20240307"
            if provider == "anthropic"
            else "gpt-3.5-turbo"
        )

        return create_llm_client(provider=provider, model=model)

    def test_vector_retriever_integration(self, vector_store):
        """Test VectorRetriever with real vector store."""
        from src.rag import VectorRetriever

        retriever = VectorRetriever(vector_store)
        docs = retriever.retrieve("professional camera", top_k=3)

        assert len(docs) > 0
        assert all("id" in doc for doc in docs)
        assert all("retrieval_score" in doc for doc in docs)

        # First result should be most relevant
        assert docs[0]["retrieval_score"] > 0.5

    def test_llm_generator_integration(self, llm_client):
        """Test LLMGenerator with real LLM."""
        from src.rag import LLMGenerator

        generator = LLMGenerator(llm_client)
        documents = [
            {
                "name": "Camera Pro X1",
                "description": "Professional camera",
                "price": 1299.99,
                "rating": 4.8,
            }
        ]

        response = generator.generate("best camera", documents)

        assert isinstance(response, str)
        assert len(response) > 0

    @pytest.mark.slow
    def test_full_pipeline_integration(self, vector_store, llm_client):
        """Test complete RAG pipeline with real components."""
        from src.rag import RAGPipeline, VectorRetriever, LLMGenerator, ConsoleObserver

        pipeline = (
            RAGPipeline()
            .with_retriever(VectorRetriever(vector_store))
            .with_generator(LLMGenerator(llm_client))
            .with_observability(ConsoleObserver(verbose=False))
        )

        result = pipeline.query("professional camera for photography")

        # Verify result structure
        assert result.query == "professional camera for photography"
        assert result.num_retrieved > 0
        assert len(result.generated_response) > 0
        assert result.total_time > 0
        assert result.retrieval_time > 0
        assert result.generation_time > 0

        # Verify observability log
        assert len(result.observability_log) >= 2  # retrieval + generation

    def test_hybrid_retriever_integration(self, vector_store, llm_client):
        """Test HybridRetriever with real components."""
        from src.rag import HybridRetriever
        from src.ranking import create_ranker

        # Create reranker
        reranker = create_ranker("llm", llm_client=llm_client)

        retriever = HybridRetriever(
            vector_store=vector_store,
            reranker=reranker,
            retrieval_k=3,
            rerank_k=2,
        )

        docs = retriever.retrieve("budget camera", top_k=2)

        # Should retrieve and rerank
        assert len(docs) <= 2
        assert all("rerank_score" in doc for doc in docs)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
