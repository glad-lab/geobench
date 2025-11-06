"""
Integration tests for complete experiment workflow.

Tests the full experimental pipeline from data loading through
analysis, validating that all packages work together correctly.
"""

import pytest
import time
from pathlib import Path
from typing import Dict, Any

from src.vector_db import VectorDBPopulator, UnifiedDatasetLoader
from src.vector_store import VectorStoreManager
from src.llm import create_llm_client
from src.attacks import AttackFactory, AttackType
from src.ranking import create_ranker
from src.experiments import (
    ExperimentRunner,
    ExperimentConfigBuilder,
    ExperimentType,
    ExperimentFactory,
)
from src.evaluation import (
    AttackEffectivenessEvaluator,
    PaperComparisonEvaluator,
)
from src.analysis import (
    StatisticalAnalyzer,
    ComparativeAnalyzer,
    AnalysisEngine,
)


@pytest.mark.integration
class TestFullExperimentWorkflow:
    """Test complete experiment workflow from setup to analysis."""

    @pytest.fixture(scope="class")
    def setup_environment(self, qdrant_service, test_products, integration_test_collection):
        """
        Setup complete test environment with all components.

        Returns:
            dict: Configured components for testing
        """
        # 1. Setup vector database
        vector_store = VectorStoreManager(
            collection_name=integration_test_collection,
            embedding_provider="gemini",
            reset_collection=True,
            host=qdrant_service["host"],
            port=qdrant_service["port"],
        )

        # 2. Load and populate data
        if "categories" in test_products:
            # Unified format - sample from each category
            products = []
            for category_data in list(test_products["categories"].values())[:3]:
                products.extend(category_data["items"][:5])
        else:
            products = test_products[:15]

        vector_store.add_documents(products)

        # 3. Create LLM client (mock for integration tests)
        llm_client = None  # Will use mock in tests

        yield {
            "vector_store": vector_store,
            "llm_client": llm_client,
            "products": products,
            "collection_name": integration_test_collection,
        }

        # Cleanup
        try:
            vector_store.clear_collection()
        except Exception:
            pass

    def test_baseline_experiment(self, setup_environment, mock_llm_client):
        """Test baseline ranking without attacks."""
        # Create config
        config = (
            ExperimentConfigBuilder()
            .with_experiment_type(ExperimentType.BASELINE)
            .with_trials(5)
            .with_vector_store(setup_environment["vector_store"])
            .with_llm_client(mock_llm_client)
            .build()
        )

        # Run experiment
        runner = ExperimentRunner()
        result = runner.run_experiment(config)

        # Validate structure
        assert result is not None
        assert hasattr(result, "trials")
        assert len(result.trials) == 5
        assert hasattr(result, "experiment_type")
        assert result.experiment_type == ExperimentType.BASELINE

        # Validate trial structure
        for trial in result.trials:
            assert hasattr(trial, "trial_id")
            assert hasattr(trial, "metrics")
            assert "retrieval_count" in trial.metrics or "ranking_computed" in trial.metadata

    def test_single_attack_experiment(self, setup_environment, mock_llm_client):
        """Test single attack effectiveness."""
        # Create attacked document
        attack_factory = AttackFactory()
        attack_content = attack_factory.create_attack(
            AttackType.PROMPT_INJECTION,
            product_name="Test Product",
            approach="glass_box"
        )

        # Create config with attacks
        config = (
            ExperimentConfigBuilder()
            .with_experiment_type(ExperimentType.SINGLE_ATTACK)
            .with_trials(3)
            .with_vector_store(setup_environment["vector_store"])
            .with_llm_client(mock_llm_client)
            .with_attack_types([AttackType.PROMPT_INJECTION])
            .build()
        )

        # Run experiment
        runner = ExperimentRunner()
        result = runner.run_experiment(config)

        # Validate
        assert result is not None
        assert len(result.trials) == 3
        assert result.experiment_type == ExperimentType.SINGLE_ATTACK

        # Check that attack info is captured
        for trial in result.trials:
            assert "attack_info" in trial.metadata or hasattr(trial, "attack_info")

    def test_prisoners_dilemma_experiment(self, setup_environment, mock_llm_client):
        """Test prisoner's dilemma with multiple attackers."""
        config = (
            ExperimentConfigBuilder()
            .with_experiment_type(ExperimentType.PRISONERS_DILEMMA)
            .with_trials(3)
            .with_vector_store(setup_environment["vector_store"])
            .with_llm_client(mock_llm_client)
            .with_attack_types([AttackType.PROMPT_INJECTION])
            .with_num_attackers(3)
            .build()
        )

        # Run experiment
        runner = ExperimentRunner()
        result = runner.run_experiment(config)

        # Validate
        assert result is not None
        assert len(result.trials) == 3
        assert result.experiment_type == ExperimentType.PRISONERS_DILEMMA

    def test_positional_bias_experiment(self, setup_environment, mock_llm_client):
        """Test positional bias analysis."""
        config = (
            ExperimentConfigBuilder()
            .with_experiment_type(ExperimentType.POSITIONAL_BIAS)
            .with_trials(3)
            .with_vector_store(setup_environment["vector_store"])
            .with_llm_client(mock_llm_client)
            .with_attack_types([AttackType.PROMPT_INJECTION])
            .build()
        )

        # Run experiment
        runner = ExperimentRunner()
        result = runner.run_experiment(config)

        # Validate
        assert result is not None
        assert len(result.trials) >= 3

    def test_experiment_to_evaluation_pipeline(self, setup_environment, mock_llm_client):
        """Test pipeline from experiment to evaluation."""
        # Run experiment
        config = (
            ExperimentConfigBuilder()
            .with_experiment_type(ExperimentType.SINGLE_ATTACK)
            .with_trials(5)
            .with_vector_store(setup_environment["vector_store"])
            .with_llm_client(mock_llm_client)
            .with_attack_types([AttackType.PROMPT_INJECTION])
            .build()
        )

        runner = ExperimentRunner()
        exp_result = runner.run_experiment(config)

        # Convert to evaluation format
        eval_data = []
        for trial in exp_result.trials:
            eval_data.append({
                "trial_id": trial.trial_id,
                "metrics": trial.metrics,
                "metadata": trial.metadata,
            })

        # Evaluate
        evaluator = AttackEffectivenessEvaluator()
        eval_result = evaluator.evaluate(eval_data)

        # Validate evaluation
        assert eval_result is not None
        assert hasattr(eval_result, "metrics")
        assert len(eval_result.metrics) > 0

    def test_evaluation_to_analysis_pipeline(self, mock_experiment_results):
        """Test pipeline from evaluation to statistical analysis."""
        # Evaluate results
        evaluator = AttackEffectivenessEvaluator()
        eval_result = evaluator.evaluate(mock_experiment_results)

        # Analyze statistics
        analyzer = StatisticalAnalyzer(confidence_level=0.95)
        stat_result = analyzer.analyze(mock_experiment_results)

        # Validate
        assert stat_result is not None
        assert "mean" in stat_result.metrics
        assert "std" in stat_result.metrics
        assert "ci_lower" in stat_result.metrics
        assert "ci_upper" in stat_result.metrics

    @pytest.mark.slow
    def test_end_to_end_research_workflow(self, setup_environment, mock_llm_client):
        """
        Test complete research workflow.

        Simulates a full research study:
        1. Run multiple experiments
        2. Evaluate all results
        3. Perform statistical analysis
        4. Generate comparative insights
        """
        experiments_to_run = [
            (ExperimentType.BASELINE, {}),
            (ExperimentType.SINGLE_ATTACK, {"attack_types": [AttackType.PROMPT_INJECTION]}),
            (ExperimentType.SINGLE_ATTACK, {"attack_types": [AttackType.PERSUASION]}),
        ]

        all_results = []

        # 1. Run multiple experiments
        for exp_type, kwargs in experiments_to_run:
            config_builder = (
                ExperimentConfigBuilder()
                .with_experiment_type(exp_type)
                .with_trials(3)
                .with_vector_store(setup_environment["vector_store"])
                .with_llm_client(mock_llm_client)
            )

            for key, value in kwargs.items():
                if key == "attack_types":
                    config_builder = config_builder.with_attack_types(value)

            config = config_builder.build()

            runner = ExperimentRunner()
            result = runner.run_experiment(config)
            all_results.append(result)

        # 2. Convert to evaluation format
        eval_data = []
        for exp_result in all_results:
            for trial in exp_result.trials:
                eval_data.append({
                    "trial_id": trial.trial_id,
                    "metrics": trial.metrics,
                    "metadata": trial.metadata,
                    "experiment_type": exp_result.experiment_type.value,
                })

        # 3. Evaluate results
        evaluator = AttackEffectivenessEvaluator()
        eval_result = evaluator.evaluate(eval_data)

        # 4. Perform statistical analysis
        analysis_engine = AnalysisEngine()
        analysis_engine.add_analyzer(StatisticalAnalyzer())
        analysis_engine.add_analyzer(ComparativeAnalyzer())

        analysis_results = analysis_engine.run_analysis(eval_data)

        # 5. Validate complete workflow
        assert len(all_results) == 3
        assert eval_result is not None
        assert len(analysis_results) == 2
        assert all(hasattr(r, "metrics") for r in analysis_results)

    def test_multi_provider_workflow(self, setup_environment):
        """Test workflow with multiple LLM providers (mocked)."""
        providers = ["openai", "anthropic"]

        results_by_provider = {}

        for provider in providers:
            # Mock client for each provider
            from unittest.mock import Mock

            mock_client = Mock()
            mock_client.generate_text = Mock(
                return_value=Mock(
                    content=f"{provider} ranking: 1. A 2. B 3. C",
                    usage={"total_tokens": 100},
                    model=f"{provider}-model"
                )
            )

            # Run experiment
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
            results_by_provider[provider] = result

        # Compare providers
        assert len(results_by_provider) == 2
        assert all(len(r.trials) == 2 for r in results_by_provider.values())

    def test_experiment_factory_integration(self, setup_environment, mock_llm_client):
        """Test experiment creation via factory."""
        factory = ExperimentFactory()

        # Create different experiment types
        config = (
            ExperimentConfigBuilder()
            .with_experiment_type(ExperimentType.BASELINE)
            .with_trials(2)
            .with_vector_store(setup_environment["vector_store"])
            .with_llm_client(mock_llm_client)
            .build()
        )

        experiment = factory.create_experiment(config)

        # Run experiment
        result = experiment.run()

        assert result is not None
        assert len(result.trials) == 2

    def test_error_handling_in_workflow(self, setup_environment):
        """Test graceful error handling in workflow."""
        # Create config with invalid settings
        with pytest.raises((ValueError, TypeError)):
            config = (
                ExperimentConfigBuilder()
                .with_experiment_type(ExperimentType.BASELINE)
                .with_trials(-1)  # Invalid
                .build()
            )

    def test_performance_benchmarking(
        self, setup_environment, mock_llm_client, benchmark_timer
    ):
        """Test that experiments complete within reasonable time."""
        config = (
            ExperimentConfigBuilder()
            .with_experiment_type(ExperimentType.BASELINE)
            .with_trials(5)
            .with_vector_store(setup_environment["vector_store"])
            .with_llm_client(mock_llm_client)
            .build()
        )

        with benchmark_timer() as timer:
            runner = ExperimentRunner()
            result = runner.run_experiment(config)

        # Should complete reasonably fast with mock
        assert timer.elapsed < 10.0  # 10 seconds
        assert result is not None

    def test_data_persistence_across_experiments(self, setup_environment, mock_llm_client):
        """Test that experiments don't corrupt shared data."""
        # Run first experiment
        config1 = (
            ExperimentConfigBuilder()
            .with_experiment_type(ExperimentType.BASELINE)
            .with_trials(2)
            .with_vector_store(setup_environment["vector_store"])
            .with_llm_client(mock_llm_client)
            .build()
        )

        runner = ExperimentRunner()
        result1 = runner.run_experiment(config1)

        # Run second experiment
        config2 = (
            ExperimentConfigBuilder()
            .with_experiment_type(ExperimentType.SINGLE_ATTACK)
            .with_trials(2)
            .with_vector_store(setup_environment["vector_store"])
            .with_llm_client(mock_llm_client)
            .with_attack_types([AttackType.PROMPT_INJECTION])
            .build()
        )

        result2 = runner.run_experiment(config2)

        # Verify both completed successfully
        assert result1 is not None
        assert result2 is not None
        assert len(result1.trials) == 2
        assert len(result2.trials) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--tb=short"])
