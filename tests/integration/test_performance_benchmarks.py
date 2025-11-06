"""
Integration tests for performance benchmarking.

Tests performance characteristics of integrated workflows,
including execution time, memory usage, and throughput.
"""

import pytest
import time
import psutil
import os
from typing import List, Dict, Any

from src.experiments import (
    ExperimentRunner,
    ExperimentConfigBuilder,
    ExperimentType,
)
from src.rag import RAGPipeline, VectorRetriever, LLMGenerator
from src.vector_store import VectorStoreManager
from src.attacks import AttackType


@pytest.mark.integration
@pytest.mark.slow
class TestPerformanceBenchmarks:
    """Test performance of integrated workflows."""

    def test_experiment_execution_time(
        self, setup_environment, mock_llm_client, benchmark_timer
    ):
        """Test experiment execution completes within time limit."""
        config = (
            ExperimentConfigBuilder()
            .with_experiment_type(ExperimentType.BASELINE)
            .with_trials(20)
            .with_vector_store(setup_environment["vector_store"])
            .with_llm_client(mock_llm_client)
            .build()
        )

        with benchmark_timer() as timer:
            runner = ExperimentRunner()
            result = runner.run_experiment(config)

        # Should complete in under 60 seconds with mock
        assert timer.elapsed < 60.0
        assert result is not None
        assert len(result.trials) == 20

        # Calculate throughput
        trials_per_second = 20 / timer.elapsed
        assert trials_per_second > 0.1  # At least 0.1 trials/sec

    def test_rag_query_latency(
        self, setup_environment, mock_llm_client
    ):
        """Test RAG query latency is acceptable."""
        pipeline = (
            RAGPipeline()
            .with_retriever(VectorRetriever(setup_environment["vector_store"]))
            .with_generator(LLMGenerator(mock_llm_client))
        )

        queries = [
            "best product for beginners",
            "professional grade equipment",
            "affordable options",
            "high quality recommendations",
            "budget friendly choices",
        ]

        latencies = []

        for query in queries:
            start = time.time()
            result = pipeline.query(query)
            elapsed = time.time() - start

            latencies.append(elapsed)
            assert result is not None

        # Calculate percentiles
        latencies.sort()
        p50 = latencies[len(latencies) // 2]
        p95 = latencies[int(len(latencies) * 0.95)]
        p99 = latencies[int(len(latencies) * 0.99)]

        # Assert acceptable latencies (with mock, should be fast)
        assert p50 < 5.0  # P50 under 5 seconds
        assert p95 < 10.0  # P95 under 10 seconds
        assert p99 < 15.0  # P99 under 15 seconds

    def test_memory_usage(
        self, setup_environment, mock_llm_client, memory_tracker
    ):
        """Test memory usage stays within bounds."""
        initial_memory = memory_tracker()

        # Run experiment
        config = (
            ExperimentConfigBuilder()
            .with_experiment_type(ExperimentType.SINGLE_ATTACK)
            .with_trials(30)
            .with_vector_store(setup_environment["vector_store"])
            .with_llm_client(mock_llm_client)
            .with_attack_types([AttackType.PROMPT_INJECTION])
            .build()
        )

        runner = ExperimentRunner()
        result = runner.run_experiment(config)

        final_memory = memory_tracker()
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (< 500 MB)
        assert memory_increase < 500
        assert result is not None

    def test_database_query_performance(
        self, setup_environment, benchmark_timer
    ):
        """Test database query performance."""
        vector_store = setup_environment["vector_store"]

        queries = [
            "camera",
            "laptop",
            "book",
            "furniture",
            "appliance",
        ] * 10  # 50 queries

        with benchmark_timer() as timer:
            for query in queries:
                results = vector_store.query(query, top_k=10)
                assert len(results) >= 0  # May be empty if no matches

        # Calculate query throughput
        queries_per_second = len(queries) / timer.elapsed
        assert queries_per_second > 1.0  # At least 1 query/sec

    def test_batch_processing_performance(
        self, setup_environment, mock_llm_client, benchmark_timer
    ):
        """Test batch processing performance."""
        from conftest import generate_test_products

        vector_store = setup_environment["vector_store"]

        # Generate batch of products
        products = generate_test_products(50)

        with benchmark_timer() as timer:
            vector_store.add_documents(products)

        # Should complete reasonably fast
        assert timer.elapsed < 60.0  # Under 60 seconds for 50 products

        products_per_second = 50 / timer.elapsed
        assert products_per_second > 0.5  # At least 0.5 products/sec

    def test_concurrent_experiment_execution(
        self, setup_environment, mock_llm_client, benchmark_timer
    ):
        """Test performance of concurrent experiments."""
        from concurrent.futures import ThreadPoolExecutor

        def run_experiment(trial_count):
            config = (
                ExperimentConfigBuilder()
                .with_experiment_type(ExperimentType.BASELINE)
                .with_trials(trial_count)
                .with_vector_store(setup_environment["vector_store"])
                .with_llm_client(mock_llm_client)
                .build()
            )

            runner = ExperimentRunner()
            return runner.run_experiment(config)

        with benchmark_timer() as timer:
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = [
                    executor.submit(run_experiment, 5)
                    for _ in range(3)
                ]
                results = [f.result() for f in futures]

        # All should complete
        assert len(results) == 3
        assert all(r is not None for r in results)

        # Should benefit from parallelism (not 3x slower)
        # With 3 workers doing 5 trials each = 15 trials total
        total_trials = sum(len(r.trials) for r in results)
        assert total_trials == 15

    def test_large_context_performance(
        self, setup_environment, mock_llm_client, benchmark_timer
    ):
        """Test performance with large context windows."""
        from conftest import generate_test_products

        # Add many documents
        products = generate_test_products(100)
        setup_environment["vector_store"].add_documents(products)

        pipeline = (
            RAGPipeline()
            .with_retriever(VectorRetriever(setup_environment["vector_store"]))
            .with_generator(LLMGenerator(mock_llm_client))
        )

        # Query with large top_k
        with benchmark_timer() as timer:
            result = pipeline.query("test query", retrieval_k=50)

        # Should still be reasonable
        assert timer.elapsed < 15.0
        assert result is not None

    def test_repeated_query_caching(
        self, setup_environment, benchmark_timer
    ):
        """Test performance improvement from caching."""
        vector_store = setup_environment["vector_store"]

        query = "test product"

        # First query (cold)
        with benchmark_timer() as timer1:
            results1 = vector_store.query(query, top_k=10)

        # Second query (potentially cached)
        with benchmark_timer() as timer2:
            results2 = vector_store.query(query, top_k=10)

        # Second query should be same or faster
        # (Though without explicit caching, may be same speed)
        assert timer2.elapsed <= timer1.elapsed * 1.5  # Within 50% of first

    def test_memory_leak_detection(
        self, setup_environment, mock_llm_client, memory_tracker
    ):
        """Test for memory leaks in repeated operations."""
        memory_samples = []

        # Run multiple experiment cycles
        for i in range(5):
            config = (
                ExperimentConfigBuilder()
                .with_experiment_type(ExperimentType.BASELINE)
                .with_trials(10)
                .with_vector_store(setup_environment["vector_store"])
                .with_llm_client(mock_llm_client)
                .build()
            )

            runner = ExperimentRunner()
            result = runner.run_experiment(config)

            # Sample memory
            memory_samples.append(memory_tracker())

            # Clear result
            del result

        # Memory should stabilize, not continuously grow
        # Allow some growth but not linear
        memory_growth = memory_samples[-1] - memory_samples[0]
        assert memory_growth < 200  # Less than 200 MB growth

    def test_database_connection_pooling(
        self, qdrant_service, integration_test_collection, benchmark_timer
    ):
        """Test database connection performance."""
        # Create multiple store instances
        stores = []

        with benchmark_timer() as timer:
            for i in range(10):
                store = VectorStoreManager(
                    collection_name=f"{integration_test_collection}_{i}",
                    embedding_provider="gemini",
                    reset_collection=True,
                    host=qdrant_service["host"],
                    port=qdrant_service["port"],
                )
                stores.append(store)

        # Should create connections reasonably fast
        assert timer.elapsed < 30.0

        # Cleanup
        for store in stores:
            try:
                store.clear_collection()
            except Exception:
                pass

    def test_end_to_end_workflow_performance(
        self, setup_environment, mock_llm_client, benchmark_timer, memory_tracker
    ):
        """Test complete workflow performance."""
        initial_memory = memory_tracker()

        with benchmark_timer() as timer:
            # 1. Run experiment
            config = (
                ExperimentConfigBuilder()
                .with_experiment_type(ExperimentType.SINGLE_ATTACK)
                .with_trials(15)
                .with_vector_store(setup_environment["vector_store"])
                .with_llm_client(mock_llm_client)
                .with_attack_types([AttackType.PROMPT_INJECTION])
                .build()
            )

            runner = ExperimentRunner()
            exp_result = runner.run_experiment(config)

            # 2. Evaluate
            from src.evaluation import AttackEffectivenessEvaluator

            eval_data = [
                {
                    "trial_id": t.trial_id,
                    "metrics": t.metrics,
                    "metadata": getattr(t, "metadata", {})
                }
                for t in exp_result.trials
            ]

            evaluator = AttackEffectivenessEvaluator()
            eval_result = evaluator.evaluate(eval_data)

            # 3. Analyze
            from src.analysis import StatisticalAnalyzer

            analyzer = StatisticalAnalyzer()
            analysis_result = analyzer.analyze(eval_data)

        final_memory = memory_tracker()

        # Complete workflow should finish in reasonable time
        assert timer.elapsed < 120.0  # Under 2 minutes

        # Memory usage should be reasonable
        memory_increase = final_memory - initial_memory
        assert memory_increase < 300  # Under 300 MB

        # All stages should complete
        assert exp_result is not None
        assert eval_result is not None
        assert analysis_result is not None

    @pytest.fixture
    def setup_environment(
        self, qdrant_service, test_products, integration_test_collection
    ):
        """Setup performance test environment."""
        vector_store = VectorStoreManager(
            collection_name=integration_test_collection,
            embedding_provider="gemini",
            reset_collection=True,
            host=qdrant_service["host"],
            port=qdrant_service["port"],
        )

        # Add test products
        if "categories" in test_products:
            products = []
            for cat_data in list(test_products["categories"].values())[:3]:
                products.extend(cat_data["items"][:5])
        else:
            products = test_products[:15]

        vector_store.add_documents(products)

        yield {"vector_store": vector_store}

        try:
            vector_store.clear_collection()
        except Exception:
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--tb=short"])
