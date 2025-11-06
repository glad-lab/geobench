"""
Unit tests for the ranking package.

Tests all ranking components including base classes, rankers, metrics,
and factory functionality.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from dataclasses import dataclass

from src.ranking import (
    BaseRanker,
    LLMRanker,
    RAGRanker,
    Product,
    RankingResult,
    RankingStrategy,
    RankingMetrics,
    RankerFactory,
    create_ranker,
    PositionalBiasAnalyzer,
    RankingValidationError,
    RankingExecutionError,
)


# Fixtures

@pytest.fixture
def sample_products():
    """Create sample products for testing."""
    return [
        Product(
            id="prod_001",
            name="Camera Pro X1",
            description="Professional camera with 45MP sensor and advanced features",
            category="Electronics"
        ),
        Product(
            id="prod_002",
            name="Camera Basic Z2",
            description="Entry-level camera for beginners",
            category="Electronics"
        ),
        Product(
            id="prod_003",
            name="Camera Advanced Y3",
            description="Advanced camera for enthusiasts with 4K video",
            category="Electronics"
        ),
    ]


@pytest.fixture
def mock_llm_client():
    """Create mock LLM client."""
    client = Mock()
    client.model = "test-model"

    # Mock response
    response = Mock()
    response.content = """1. prod_001
2. prod_002
3. prod_003"""
    response.model = "test-model"
    response.usage = {"total_tokens": 100}
    response.metadata = {"provider": "test"}

    client.generate_text.return_value = response

    return client


@pytest.fixture
def mock_embeddings():
    """Create mock embeddings model."""
    embeddings = Mock()

    # Mock methods
    embeddings.embed_query.return_value = [0.1, 0.2, 0.3]
    embeddings.embed_documents.return_value = [
        [0.15, 0.25, 0.35],
        [0.05, 0.15, 0.25],
        [0.2, 0.3, 0.4],
    ]

    return embeddings


# Test Product class

class TestProduct:
    """Tests for Product data class."""

    def test_create_valid_product(self):
        """Test creating valid Product."""
        product = Product(
            id="test_001",
            name="Test Product",
            description="Test description",
            category="Test"
        )

        assert product.id == "test_001"
        assert product.name == "Test Product"
        assert product.description == "Test description"
        assert product.category == "Test"

    def test_empty_id_fails(self):
        """Test that empty ID raises error."""
        with pytest.raises(ValueError, match="ID cannot be empty"):
            Product(
                id="",
                name="Test",
                description="Test description"
            )

    def test_empty_name_fails(self):
        """Test that empty name raises error."""
        with pytest.raises(ValueError, match="name cannot be empty"):
            Product(
                id="test_001",
                name="",
                description="Test description"
            )

    def test_empty_description_fails(self):
        """Test that empty description raises error."""
        with pytest.raises(ValueError, match="description cannot be empty"):
            Product(
                id="test_001",
                name="Test",
                description=""
            )


# Test RankingResult class

class TestRankingResult:
    """Tests for RankingResult data class."""

    def test_create_valid_result(self):
        """Test creating valid RankingResult."""
        result = RankingResult(
            query="test query",
            rankings=[("prod_001", 0.9), ("prod_002", 0.7)],
            strategy=RankingStrategy.LLM_DIRECT,
            ranking_time=1.5
        )

        assert result.query == "test query"
        assert len(result.rankings) == 2
        assert result.strategy == RankingStrategy.LLM_DIRECT
        assert result.ranking_time == 1.5

    def test_empty_query_fails(self):
        """Test that empty query raises error."""
        with pytest.raises(ValueError, match="Query cannot be empty"):
            RankingResult(
                query="",
                rankings=[("prod_001", 0.9)],
                strategy=RankingStrategy.LLM_DIRECT
            )

    def test_empty_rankings_fails(self):
        """Test that empty rankings raises error."""
        with pytest.raises(ValueError, match="Rankings list cannot be empty"):
            RankingResult(
                query="test",
                rankings=[],
                strategy=RankingStrategy.LLM_DIRECT
            )

    def test_invalid_score_fails(self):
        """Test that invalid scores raise error."""
        with pytest.raises(ValueError, match="Score must be between"):
            RankingResult(
                query="test",
                rankings=[("prod_001", 1.5)],
                strategy=RankingStrategy.LLM_DIRECT
            )

    def test_get_top_k(self):
        """Test getting top-k results."""
        result = RankingResult(
            query="test",
            rankings=[
                ("prod_001", 0.9),
                ("prod_002", 0.8),
                ("prod_003", 0.7)
            ],
            strategy=RankingStrategy.LLM_DIRECT
        )

        top_2 = result.get_top_k(2)
        assert len(top_2) == 2
        assert top_2[0][0] == "prod_001"
        assert top_2[1][0] == "prod_002"

    def test_get_product_rank(self):
        """Test getting product rank."""
        result = RankingResult(
            query="test",
            rankings=[
                ("prod_001", 0.9),
                ("prod_002", 0.8),
                ("prod_003", 0.7)
            ],
            strategy=RankingStrategy.LLM_DIRECT
        )

        assert result.get_product_rank("prod_002") == 2
        assert result.get_product_rank("prod_999") is None

    def test_get_product_score(self):
        """Test getting product score."""
        result = RankingResult(
            query="test",
            rankings=[
                ("prod_001", 0.9),
                ("prod_002", 0.8)
            ],
            strategy=RankingStrategy.LLM_DIRECT
        )

        assert result.get_product_score("prod_001") == 0.9
        assert result.get_product_score("prod_999") is None


# Test LLMRanker

class TestLLMRanker:
    """Tests for LLMRanker class."""

    def test_initialization(self, mock_llm_client):
        """Test LLM ranker initialization."""
        ranker = LLMRanker(mock_llm_client, temperature=0.0)

        assert ranker.llm_client == mock_llm_client
        assert ranker.temperature == 0.0

    def test_initialization_without_generate_text_fails(self):
        """Test that client without generate_text fails."""
        invalid_client = Mock(spec=[])

        with pytest.raises(ValueError, match="must have a generate_text"):
            LLMRanker(invalid_client)

    def test_rank_products_basic(self, mock_llm_client, sample_products):
        """Test basic product ranking."""
        ranker = LLMRanker(mock_llm_client, temperature=0.0)
        result = ranker.rank("best camera", sample_products)

        assert isinstance(result, RankingResult)
        assert result.query == "best camera"
        assert len(result.rankings) == 3
        assert result.strategy == RankingStrategy.LLM_DIRECT
        assert result.ranking_time > 0

    def test_rank_with_scores(self, mock_llm_client, sample_products):
        """Test ranking with relevance scores."""
        # Update mock to return scores
        response = Mock()
        response.content = """1. prod_001 (Score: 95)
2. prod_002 (Score: 80)
3. prod_003 (Score: 70)"""
        response.model = "test-model"
        response.usage = {}
        response.metadata = {}
        mock_llm_client.generate_text.return_value = response

        ranker = LLMRanker(mock_llm_client)
        result = ranker.rank("best camera", sample_products, return_scores=True)

        assert result.strategy == RankingStrategy.LLM_WITH_SCORES
        # Check scores are normalized
        assert 0.0 <= result.rankings[0][1] <= 1.0

    def test_rank_with_empty_query_fails(self, mock_llm_client, sample_products):
        """Test that empty query raises error."""
        ranker = LLMRanker(mock_llm_client)

        with pytest.raises(RankingValidationError, match="Query cannot be empty"):
            ranker.rank("", sample_products)

    def test_rank_with_empty_products_fails(self, mock_llm_client):
        """Test that empty products raises error."""
        ranker = LLMRanker(mock_llm_client)

        with pytest.raises(RankingValidationError, match="Products list cannot be empty"):
            ranker.rank("test query", [])

    def test_rank_handles_llm_failure(self, mock_llm_client, sample_products):
        """Test graceful handling of LLM failures."""
        # Make LLM fail
        mock_llm_client.generate_text.side_effect = Exception("LLM error")

        ranker = LLMRanker(mock_llm_client)
        result = ranker.rank("test query", sample_products)

        # Should return default rankings
        assert isinstance(result, RankingResult)
        assert "error" in result.metadata
        assert result.metadata.get("fallback") is True

    def test_parse_malformed_response(self, mock_llm_client, sample_products):
        """Test parsing malformed LLM responses."""
        # Return malformed response
        response = Mock()
        response.content = "Random text without product IDs"
        response.model = "test-model"
        response.usage = {}
        response.metadata = {}
        mock_llm_client.generate_text.return_value = response

        ranker = LLMRanker(mock_llm_client)
        result = ranker.rank("test query", sample_products)

        # Should still return valid result with all products
        assert len(result.rankings) == len(sample_products)


# Test RAGRanker

class TestRAGRanker:
    """Tests for RAGRanker class."""

    def test_initialization(self, mock_embeddings, mock_llm_client):
        """Test RAG ranker initialization."""
        ranker = RAGRanker(mock_embeddings, mock_llm_client, top_k=5)

        assert ranker.embeddings == mock_embeddings
        assert ranker.llm_client == mock_llm_client
        assert ranker.top_k == 5

    def test_initialization_without_embed_methods_fails(self, mock_llm_client):
        """Test that embeddings without required methods fails."""
        invalid_embeddings = Mock(spec=[])

        with pytest.raises(ValueError, match="must have embed_query"):
            RAGRanker(invalid_embeddings, mock_llm_client)

    def test_rank_with_retrieval(self, mock_embeddings, mock_llm_client, sample_products):
        """Test RAG ranking with retrieval step."""
        ranker = RAGRanker(mock_embeddings, mock_llm_client, top_k=2)
        result = ranker.rank("best camera", sample_products)

        assert isinstance(result, RankingResult)
        assert result.strategy == RankingStrategy.RAG
        assert result.metadata.get("retrieval_used") is True
        assert result.metadata.get("top_k") == 2

    def test_rank_without_retrieval(self, mock_embeddings, mock_llm_client, sample_products):
        """Test RAG ranking without retrieval."""
        ranker = RAGRanker(mock_embeddings, mock_llm_client, use_retrieval=False)
        result = ranker.rank("best camera", sample_products)

        assert result.strategy == RankingStrategy.RAG
        assert result.metadata.get("retrieval_used") is False

    def test_retrieval_with_few_products(self, mock_embeddings, mock_llm_client):
        """Test that retrieval is used even with few products."""
        products = [
            Product("prod_001", "Product 1", "Description 1"),
            Product("prod_002", "Product 2", "Description 2"),
        ]

        ranker = RAGRanker(mock_embeddings, mock_llm_client, top_k=10)
        result = ranker.rank("test", products)

        # Retrieval is still used (just returns fewer than top_k)
        assert result.metadata.get("retrieval_used") is True
        assert result.metadata.get("num_retrieved") == 2


# Test RankingMetrics

class TestRankingMetrics:
    """Tests for RankingMetrics class."""

    def test_precision_at_k(self):
        """Test Precision@K calculation."""
        predicted = ["a", "b", "c", "d"]
        relevant = {"b", "d"}

        p_at_2 = RankingMetrics.precision_at_k(predicted, relevant, k=2)
        assert p_at_2 == 0.5  # 1 relevant out of 2

        p_at_4 = RankingMetrics.precision_at_k(predicted, relevant, k=4)
        assert p_at_4 == 0.5  # 2 relevant out of 4

    def test_recall_at_k(self):
        """Test Recall@K calculation."""
        predicted = ["a", "b", "c"]
        relevant = {"b", "c", "d"}

        r_at_2 = RankingMetrics.recall_at_k(predicted, relevant, k=2)
        assert abs(r_at_2 - 0.333) < 0.01  # 1 out of 3 relevant items

        r_at_3 = RankingMetrics.recall_at_k(predicted, relevant, k=3)
        assert abs(r_at_3 - 0.666) < 0.01  # 2 out of 3 relevant items

    def test_mean_reciprocal_rank(self):
        """Test MRR calculation."""
        rankings = [
            ["a", "b", "c"],
            ["x", "y", "z"]
        ]
        relevant_items = ["b", "x"]

        mrr = RankingMetrics.mean_reciprocal_rank(rankings, relevant_items)
        assert mrr == 0.75  # (1/2 + 1/1) / 2 = 1.5 / 2 = 0.75

    def test_ndcg_perfect_ranking(self):
        """Test NDCG with perfect ranking."""
        predicted = ["a", "b", "c", "d"]
        ideal = ["a", "b", "c", "d"]

        ndcg = RankingMetrics.ndcg(predicted, ideal, k=4)
        assert ndcg == 1.0

    def test_ndcg_worst_ranking(self):
        """Test NDCG with reversed ranking."""
        predicted = ["d", "c", "b", "a"]
        ideal = ["a", "b", "c", "d"]

        ndcg = RankingMetrics.ndcg(predicted, ideal, k=4)
        # NDCG still considers position - reversed is ~0.75, not close to 0
        assert 0.5 < ndcg < 1.0  # Worse than perfect but not terrible

    def test_average_precision(self):
        """Test Average Precision calculation."""
        predicted = ["a", "b", "c", "d"]
        relevant = {"b", "d"}

        ap = RankingMetrics.average_precision(predicted, relevant)
        # AP = (1/2 + 2/4) / 2 = 0.5
        assert abs(ap - 0.5) < 0.01

    def test_evaluate_ranking(self):
        """Test comprehensive ranking evaluation."""
        predicted = ["a", "b", "c", "d"]
        ideal = ["b", "a", "c", "d"]
        relevant = {"a", "b"}

        metrics = RankingMetrics.evaluate_ranking(
            predicted, ideal, relevant, k_values=[1, 3]
        )

        assert "ndcg@1" in metrics
        assert "ndcg@3" in metrics
        assert "precision@1" in metrics
        assert "recall@1" in metrics
        assert "average_precision" in metrics


# Test RankerFactory

class TestRankerFactory:
    """Tests for RankerFactory class."""

    def test_create_llm_ranker(self, mock_llm_client):
        """Test creating LLM ranker via factory."""
        factory = RankerFactory(llm_client=mock_llm_client)
        ranker = factory.create_ranker("llm")

        assert isinstance(ranker, LLMRanker)

    def test_create_rag_ranker(self, mock_embeddings, mock_llm_client):
        """Test creating RAG ranker via factory."""
        factory = RankerFactory(
            llm_client=mock_llm_client,
            embeddings=mock_embeddings
        )
        ranker = factory.create_ranker("rag", top_k=5)

        assert isinstance(ranker, RAGRanker)
        assert ranker.top_k == 5

    def test_create_unknown_type_fails(self, mock_llm_client):
        """Test that unknown type raises error."""
        factory = RankerFactory(llm_client=mock_llm_client)

        with pytest.raises(ValueError, match="Unknown ranker type"):
            factory.create_ranker("unknown")

    def test_create_without_llm_fails(self):
        """Test that creating without LLM client fails."""
        factory = RankerFactory()

        with pytest.raises(ValueError, match="llm_client is required"):
            factory.create_ranker("llm")


# Test PositionalBiasAnalyzer

class TestPositionalBiasAnalyzer:
    """Tests for PositionalBiasAnalyzer."""

    def test_initialization(self, mock_llm_client):
        """Test analyzer initialization."""
        ranker = LLMRanker(mock_llm_client)
        analyzer = PositionalBiasAnalyzer(ranker)

        assert analyzer.ranker == ranker

    def test_position_effect(self, mock_llm_client, sample_products):
        """Test testing position effects."""
        ranker = LLMRanker(mock_llm_client)
        analyzer = PositionalBiasAnalyzer(ranker)

        results = analyzer.test_position_effect(
            "best camera",
            sample_products,
            "ATTACK TEXT",
            positions=["start", "end"]
        )

        assert "start" in results
        assert "end" in results
        assert isinstance(results["start"], RankingResult)

    def test_inject_at_start(self, sample_products):
        """Test injecting attack at start."""
        ranker = Mock(spec=BaseRanker)
        analyzer = PositionalBiasAnalyzer(ranker)

        modified = analyzer._inject_at_position(
            sample_products,
            "ATTACK",
            "start"
        )

        assert modified[0].description.startswith("ATTACK")

    def test_inject_at_end(self, sample_products):
        """Test injecting attack at end."""
        ranker = Mock(spec=BaseRanker)
        analyzer = PositionalBiasAnalyzer(ranker)

        modified = analyzer._inject_at_position(
            sample_products,
            "ATTACK",
            "end"
        )

        assert modified[0].description.endswith("ATTACK")

    def test_invalid_position_fails(self, sample_products):
        """Test that invalid position raises error."""
        ranker = Mock(spec=BaseRanker)
        analyzer = PositionalBiasAnalyzer(ranker)

        with pytest.raises(ValueError, match="Invalid position"):
            analyzer._inject_at_position(
                sample_products,
                "ATTACK",
                "invalid"
            )


# Test module-level convenience functions

class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""

    def test_create_ranker(self, mock_llm_client):
        """Test create_ranker convenience function."""
        ranker = create_ranker("llm", llm_client=mock_llm_client)

        assert isinstance(ranker, LLMRanker)

    def test_create_ranker_with_params(self, mock_llm_client):
        """Test create_ranker with parameters."""
        ranker = create_ranker(
            "llm",
            llm_client=mock_llm_client,
            temperature=0.5
        )

        assert ranker.temperature == 0.5


# Test backward compatibility

class TestBackwardCompatibility:
    """Tests for backward compatibility features."""

    def test_ranking_system_alias(self):
        """Test RankingSystem alias."""
        from src.ranking import RankingSystem, BaseRanker

        assert RankingSystem is BaseRanker

    def test_simple_rag_alias(self):
        """Test SimpleRAG alias."""
        from src.ranking import SimpleRAG, RAGRanker

        assert SimpleRAG is RAGRanker


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
