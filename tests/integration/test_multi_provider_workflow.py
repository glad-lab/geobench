"""
Integration tests for multi-provider workflows.

Tests workflows across multiple LLM providers to validate
provider-agnostic implementation and cross-provider comparisons.
"""

import pytest
import os
from unittest.mock import Mock, patch

from src.llm import create_llm_client, LLMResponse
from src.experiments import (
    ExperimentRunner,
    ExperimentConfigBuilder,
    ExperimentType,
)
from src.evaluation import AttackEffectivenessEvaluator
from src.analysis import ComparativeAnalyzer
from src.attacks import AttackType


@pytest.mark.integration
class TestMultiProviderWorkflow:
    """Test workflows with multiple LLM providers."""

    @pytest.fixture
    def mock_providers(self):
        """Create mock clients for different providers."""
        providers = {}

        for provider_name in ["openai", "anthropic", "bedrock"]:
            mock_client = Mock()

            # Different response patterns per provider
            if provider_name == "openai":
                response_pattern = "OpenAI ranks: 1. A 2. B 3. C"
            elif provider_name == "anthropic":
                response_pattern = "Claude ranks: 1. C 2. A 3. B"
            else:  # bedrock
                response_pattern = "Bedrock ranks: 1. B 2. C 3. A"

            mock_response = Mock(spec=LLMResponse)
            mock_response.content = response_pattern
            mock_response.usage = {"total_tokens": 100 + len(provider_name)}
            mock_response.model = f"{provider_name}-model"

            mock_client.generate_text = Mock(return_value=mock_response)
            providers[provider_name] = mock_client

        return providers

    @pytest.mark.parametrize("provider", ["openai", "anthropic", "bedrock"])
    def test_provider_experiment(
        self, provider, mock_providers, setup_environment
    ):
        """Test experiment with specific provider."""
        mock_client = mock_providers[provider]

        config = (
            ExperimentConfigBuilder()
            .with_experiment_type(ExperimentType.BASELINE)
            .with_trials(5)
            .with_vector_store(setup_environment["vector_store"])
            .with_llm_client(mock_client)
            .build()
        )

        runner = ExperimentRunner()
        result = runner.run_experiment(config)

        # Validate
        assert result is not None
        assert len(result.trials) == 5

        # Verify provider was used
        assert mock_client.generate_text.called

    def test_cross_provider_comparison(
        self, mock_providers, setup_environment
    ):
        """Test comparison across all providers."""
        results_by_provider = {}

        for provider_name, mock_client in mock_providers.items():
            config = (
                ExperimentConfigBuilder()
                .with_experiment_type(ExperimentType.SINGLE_ATTACK)
                .with_trials(10)
                .with_vector_store(setup_environment["vector_store"])
                .with_llm_client(mock_client)
                .with_attack_types([AttackType.PROMPT_INJECTION])
                .build()
            )

            runner = ExperimentRunner()
            result = runner.run_experiment(config)
            results_by_provider[provider_name] = result

        # Verify all providers completed
        assert len(results_by_provider) == 3
        assert all(len(r.trials) == 10 for r in results_by_provider.values())

        # Compare providers
        all_data = []
        for provider_name, exp_result in results_by_provider.items():
            for trial in exp_result.trials:
                all_data.append({
                    "trial_id": trial.trial_id,
                    "metrics": trial.metrics,
                    "metadata": {
                        "provider": provider_name,
                        **getattr(trial, "metadata", {})
                    }
                })

        # Analyze
        analyzer = ComparativeAnalyzer()
        comparison = analyzer.compare_providers(all_data)

        assert comparison is not None
        assert hasattr(comparison, "metrics")

    def test_provider_specific_configurations(self, mock_providers, setup_environment):
        """Test provider-specific configuration handling."""
        configs = {
            "openai": {"temperature": 0.7, "max_tokens": 500},
            "anthropic": {"temperature": 1.0, "max_tokens": 1000},
            "bedrock": {"temperature": 0.5, "max_tokens": 750},
        }

        for provider_name, mock_client in mock_providers.items():
            config = (
                ExperimentConfigBuilder()
                .with_experiment_type(ExperimentType.BASELINE)
                .with_trials(3)
                .with_vector_store(setup_environment["vector_store"])
                .with_llm_client(mock_client)
                .build()
            )

            # Set provider-specific config
            config.llm_config = configs[provider_name]

            runner = ExperimentRunner()
            result = runner.run_experiment(config)

            assert result is not None

    def test_provider_failover(self, mock_providers, setup_environment):
        """Test graceful failover when provider fails."""
        # Make one provider fail
        failing_client = Mock()
        failing_client.generate_text = Mock(side_effect=Exception("Provider unavailable"))

        primary_config = (
            ExperimentConfigBuilder()
            .with_experiment_type(ExperimentType.BASELINE)
            .with_trials(3)
            .with_vector_store(setup_environment["vector_store"])
            .with_llm_client(failing_client)
            .build()
        )

        # Should raise exception
        runner = ExperimentRunner()
        with pytest.raises(Exception):
            runner.run_experiment(primary_config)

        # Failover to backup provider
        backup_client = mock_providers["openai"]
        backup_config = (
            ExperimentConfigBuilder()
            .with_experiment_type(ExperimentType.BASELINE)
            .with_trials(3)
            .with_vector_store(setup_environment["vector_store"])
            .with_llm_client(backup_client)
            .build()
        )

        result = runner.run_experiment(backup_config)
        assert result is not None

    def test_provider_response_consistency(self, mock_providers, setup_environment):
        """Test response format consistency across providers."""
        responses = {}

        for provider_name, mock_client in mock_providers.items():
            config = (
                ExperimentConfigBuilder()
                .with_experiment_type(ExperimentType.BASELINE)
                .with_trials(2)
                .with_vector_store(setup_environment["vector_store"])
                .with_llm_client(mock_client)
                .build()
            )

            runner = ExperimentRunner()
            result = runner.run_experiment(config)

            # Collect responses
            responses[provider_name] = result

        # Verify all have consistent structure
        for provider_name, result in responses.items():
            assert hasattr(result, "trials")
            assert hasattr(result, "experiment_type")
            assert len(result.trials) == 2

    @pytest.mark.skipif(
        not (os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")),
        reason="No real API keys available"
    )
    @pytest.mark.slow
    def test_real_provider_integration(self, setup_environment):
        """Test with real provider APIs if available."""
        # Detect available provider
        if os.getenv("ANTHROPIC_API_KEY"):
            provider = "anthropic"
            model = "claude-3-haiku-20240307"
        elif os.getenv("OPENAI_API_KEY"):
            provider = "openai"
            model = "gpt-3.5-turbo"
        else:
            pytest.skip("No API keys available")

        # Create real client
        client = create_llm_client(provider=provider, model=model)

        # Run small experiment
        config = (
            ExperimentConfigBuilder()
            .with_experiment_type(ExperimentType.BASELINE)
            .with_trials(2)
            .with_vector_store(setup_environment["vector_store"])
            .with_llm_client(client)
            .build()
        )

        runner = ExperimentRunner()
        result = runner.run_experiment(config)

        # Validate
        assert result is not None
        assert len(result.trials) == 2

    def test_provider_cost_tracking(self, mock_providers, setup_environment):
        """Test tracking costs across providers."""
        costs = {}

        # Different token costs per provider
        cost_per_1k_tokens = {
            "openai": 0.002,
            "anthropic": 0.001,
            "bedrock": 0.0015,
        }

        for provider_name, mock_client in mock_providers.items():
            config = (
                ExperimentConfigBuilder()
                .with_experiment_type(ExperimentType.BASELINE)
                .with_trials(5)
                .with_vector_store(setup_environment["vector_store"])
                .with_llm_client(mock_client)
                .build()
            )

            runner = ExperimentRunner()
            result = runner.run_experiment(config)

            # Calculate mock cost
            total_tokens = 0
            for trial in result.trials:
                # Mock response had ~100 tokens
                total_tokens += 100

            cost = (total_tokens / 1000) * cost_per_1k_tokens[provider_name]
            costs[provider_name] = cost

        # Verify costs tracked
        assert len(costs) == 3
        assert all(c > 0 for c in costs.values())

    def test_provider_performance_comparison(
        self, mock_providers, setup_environment, benchmark_timer
    ):
        """Test performance comparison across providers."""
        performance = {}

        for provider_name, mock_client in mock_providers.items():
            config = (
                ExperimentConfigBuilder()
                .with_experiment_type(ExperimentType.BASELINE)
                .with_trials(10)
                .with_vector_store(setup_environment["vector_store"])
                .with_llm_client(mock_client)
                .build()
            )

            with benchmark_timer() as timer:
                runner = ExperimentRunner()
                result = runner.run_experiment(config)

            performance[provider_name] = {
                "elapsed": timer.elapsed,
                "trials_per_second": 10 / timer.elapsed
            }

        # Verify all completed
        assert len(performance) == 3
        assert all(p["elapsed"] > 0 for p in performance.values())

    def test_provider_specific_error_handling(self, setup_environment):
        """Test provider-specific error handling."""
        # Simulate different provider errors
        error_scenarios = {
            "rate_limit": Exception("Rate limit exceeded"),
            "auth_error": Exception("Authentication failed"),
            "timeout": Exception("Request timeout"),
        }

        for error_type, error in error_scenarios.items():
            mock_client = Mock()
            mock_client.generate_text = Mock(side_effect=error)

            config = (
                ExperimentConfigBuilder()
                .with_experiment_type(ExperimentType.BASELINE)
                .with_trials(1)
                .with_vector_store(setup_environment["vector_store"])
                .with_llm_client(mock_client)
                .build()
            )

            runner = ExperimentRunner()

            # Should raise appropriate error
            with pytest.raises(Exception):
                runner.run_experiment(config)

    @pytest.fixture
    def setup_environment(
        self, qdrant_service, test_products, integration_test_collection
    ):
        """Setup test environment."""
        from src.vector_store import VectorStoreManager

        vector_store = VectorStoreManager(
            collection_name=integration_test_collection,
            embedding_provider="gemini",
            reset_collection=True,
            host=qdrant_service["host"],
            port=qdrant_service["port"],
        )

        # Add test data
        if "categories" in test_products:
            products = []
            for cat_data in list(test_products["categories"].values())[:2]:
                products.extend(cat_data["items"][:5])
        else:
            products = test_products[:10]

        vector_store.add_documents(products)

        yield {"vector_store": vector_store}

        try:
            vector_store.clear_collection()
        except Exception:
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
