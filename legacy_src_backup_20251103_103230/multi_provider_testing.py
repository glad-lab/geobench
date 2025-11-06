#!/usr/bin/env python3
"""
Multi-provider testing framework for cross-provider validation.
Tests attack effectiveness across OpenAI, Anthropic, and AWS Bedrock LLM providers.

This module provides comprehensive testing of adversarial attacks across multiple
LLM providers to validate attack transferability and provider-specific vulnerabilities.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum
import asyncio
import time
import random
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse

try:
    from .llm_client import (
        LLMClient,
        OpenAIClient,
        AnthropicClient,
        BedrockClient,
        LLMResponse,
    )
    from .attacks import AttackGenerator, AttackType, Attack
    from .ranking import LLMRanker, RankingResult
    from .vector_store import VectorStoreManager
    from .evaluation import EvaluationMetrics
    from .experiments import ExperimentConfig, ExperimentType
except ImportError:
    from llm_client import (
        LLMClient,
        OpenAIClient,
        AnthropicClient,
        BedrockClient,
        LLMResponse,
    )
    from attacks import AttackGenerator, AttackType, Attack
    from ranking import LLMRanker, RankingResult
    from vector_store import VectorStoreManager
    from evaluation import EvaluationMetrics
    from experiments import ExperimentConfig, ExperimentType

logger = logging.getLogger(__name__)


class ProviderType(Enum):
    """Supported LLM providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    BEDROCK = "bedrock"


@dataclass
class ProviderConfig:
    """Configuration for a specific LLM provider."""

    provider: ProviderType
    model: str
    api_key: Optional[str] = None
    region: Optional[str] = None
    max_tokens: int = 1000
    temperature: float = 0.1
    timeout: int = 30
    rate_limit_delay: float = 1.0

    # Provider-specific settings
    additional_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CrossProviderResult:
    """Results from cross-provider testing."""

    provider: ProviderType
    model: str
    attack_type: AttackType
    attack_successful: bool
    ranking_position: int
    confidence_score: float
    response_time: float
    tokens_used: int

    # Attack details
    attack_content: str
    target_product: str
    baseline_position: int
    position_change: int

    # Error handling
    error_occurred: bool = False
    error_message: str = ""

    # Metadata
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    experiment_id: str = ""


@dataclass
class ProviderComparisonReport:
    """Comprehensive comparison report across providers."""

    # Overall statistics
    total_experiments: int
    successful_experiments: int
    overall_success_rate: float

    # Provider-specific results
    provider_results: Dict[str, Dict[str, Any]]

    # Attack transferability analysis
    transferability_matrix: Dict[str, Dict[str, float]]
    universal_attacks: List[str]
    provider_specific_vulnerabilities: Dict[str, List[str]]

    # Performance metrics
    response_time_comparison: Dict[str, float]
    cost_analysis: Dict[str, float]
    reliability_scores: Dict[str, float]

    # Statistical analysis
    statistical_significance: Dict[str, float]
    effect_sizes: Dict[str, float]
    confidence_intervals: Dict[str, Tuple[float, float]]

    # Metadata
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    experiment_duration: float = 0.0


class MultiProviderTester:
    """
    Multi-provider testing framework for adversarial SEO attacks.
    Tests attack effectiveness across multiple LLM providers with comprehensive analysis.
    """

    def __init__(
        self,
        output_dir: str = "data/results/multi_provider",
        vector_store_host: str = "localhost",
        vector_store_port: int = 6333,
        collection_name: str = "adversarial_seo_products",
        max_workers: int = 3,
        enable_parallel: bool = True,
    ):
        """
        Initialize multi-provider testing framework.

        Args:
            output_dir: Directory for saving results
            vector_store_host: Qdrant vector store host
            vector_store_port: Qdrant vector store port
            collection_name: Vector collection name
            max_workers: Maximum concurrent workers
            enable_parallel: Enable parallel testing across providers
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.vector_store_host = vector_store_host
        self.vector_store_port = vector_store_port
        self.collection_name = collection_name
        self.max_workers = max_workers
        self.enable_parallel = enable_parallel

        # Initialize components
        self.attack_generator = AttackGenerator()
        self.vector_manager = VectorStoreManager(
            host=vector_store_host,
            port=vector_store_port,
            collection_name=collection_name
        )
        self.metrics = EvaluationMetrics()

        # Provider configurations
        self.provider_configs: Dict[ProviderType, ProviderConfig] = {}
        self.provider_clients: Dict[ProviderType, LLMClient] = {}

        # Results storage
        self.cross_provider_results: List[CrossProviderResult] = []

        logger.info(f"Multi-provider tester initialized")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info(f"Parallel testing: {self.enable_parallel}")

    def configure_provider(
        self,
        provider: ProviderType,
        model: str,
        api_key: Optional[str] = None,
        region: Optional[str] = None,
        **kwargs,
    ):
        """Configure a specific LLM provider."""
        config = ProviderConfig(
            provider=provider, model=model, api_key=api_key, region=region, **kwargs
        )

        self.provider_configs[provider] = config

        # Initialize client
        try:
            if provider == ProviderType.OPENAI:
                client = OpenAIClient(
                    api_key=api_key or os.getenv("OPENAI_API_KEY"),
                    model=model,
                    max_tokens=config.max_tokens,
                    temperature=config.temperature,
                )
            elif provider == ProviderType.ANTHROPIC:
                client = AnthropicClient(
                    api_key=api_key or os.getenv("ANTHROPIC_API_KEY"),
                    model=model,
                    max_tokens=config.max_tokens,
                    temperature=config.temperature,
                )
            elif provider == ProviderType.BEDROCK:
                client = BedrockClient(
                    region=region or os.getenv("AWS_REGION", "us-east-1"),
                    model=model,
                    max_tokens=config.max_tokens,
                    temperature=config.temperature,
                )
            else:
                raise ValueError(f"Unsupported provider: {provider}")

            self.provider_clients[provider] = client
            logger.info(f"Configured {provider.value} with model {model}")

        except Exception as e:
            logger.error(f"Failed to configure {provider.value}: {e}")
            raise

    def auto_configure_providers(self):
        """Auto-configure providers based on available environment variables."""
        # OpenAI configuration
        if os.getenv("OPENAI_API_KEY"):
            try:
                self.configure_provider(
                    ProviderType.OPENAI,
                    model="gpt-3.5-turbo",
                    api_key=os.getenv("OPENAI_API_KEY"),
                )
            except Exception as e:
                logger.warning(f"Failed to auto-configure OpenAI: {e}")

        # Anthropic configuration
        if os.getenv("ANTHROPIC_API_KEY"):
            try:
                self.configure_provider(
                    ProviderType.ANTHROPIC,
                    model="claude-3-5-haiku-20241022",  # Use the correct model ID
                    api_key=os.getenv("ANTHROPIC_API_KEY"),
                )
            except Exception as e:
                logger.warning(f"Failed to auto-configure Anthropic: {e}")

        # AWS Bedrock configuration
        try:
            # Check if AWS credentials are available
            import boto3

            session = boto3.Session()
            credentials = session.get_credentials()

            if credentials:
                # Try LLaMA 3 70B first (available in us-east-1)
                try:
                    self.configure_provider(
                        ProviderType.BEDROCK,
                        model="meta.llama3-70b-instruct-v1:0",  # LLaMA 3 70B in us-east-1
                        region=os.getenv("AWS_REGION", "us-east-1"),
                    )
                except Exception:
                    # Fallback to LLaMA 3 8B if 70B not accessible
                    logger.info("LLaMA 3 70B not accessible, trying 8B model")
                    self.configure_provider(
                        ProviderType.BEDROCK,
                        model="meta.llama3-8b-instruct-v1:0",  # LLaMA 3 8B fallback
                        region=os.getenv("AWS_REGION", "us-east-1"),
                    )
        except Exception as e:
            logger.warning(f"Failed to auto-configure Bedrock: {e}")

        logger.info(f"Auto-configured {len(self.provider_clients)} provider clients")

    def test_provider_connectivity(self) -> Dict[ProviderType, bool]:
        """Test connectivity to all configured providers."""
        connectivity_results = {}

        for provider, client in self.provider_clients.items():
            try:
                # Simple test query
                test_prompt = "Hello, this is a connectivity test. Please respond with 'Connected'."
                response = client.generate_text(test_prompt)

                if response and response.content:
                    connectivity_results[provider] = True
                    logger.info(f"✅ {provider.value} connectivity test passed")
                else:
                    connectivity_results[provider] = False
                    logger.warning(
                        f"❌ {provider.value} connectivity test failed - empty response"
                    )

            except Exception as e:
                connectivity_results[provider] = False
                logger.error(f"❌ {provider.value} connectivity test failed: {e}")

        return connectivity_results

    def run_cross_provider_experiment(
        self,
        query: str,
        attack_types: List[AttackType],
        target_products: List[str],
        num_trials: int = 10,
    ) -> List[CrossProviderResult]:
        """Run cross-provider attack experiment."""
        logger.info(
            f"Running cross-provider experiment with {len(self.provider_clients)} providers"
        )

        experiment_results = []
        experiment_id = f"cross_provider_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Generate baseline rankings for each provider
        baseline_rankings = self._get_baseline_rankings(query)

        # Test each combination of provider, attack type, and target product
        test_combinations = []
        for provider in self.provider_clients.keys():
            for attack_type in attack_types:
                for target_product in target_products:
                    for trial in range(num_trials):
                        test_combinations.append(
                            (provider, attack_type, target_product, trial)
                        )

        logger.info(f"Testing {len(test_combinations)} combinations")

        if self.enable_parallel and len(test_combinations) > 1:
            experiment_results = self._run_parallel_tests(
                test_combinations, query, baseline_rankings, experiment_id
            )
        else:
            experiment_results = self._run_sequential_tests(
                test_combinations, query, baseline_rankings, experiment_id
            )

        self.cross_provider_results.extend(experiment_results)

        # Save results
        self._save_experiment_results(experiment_results, experiment_id)

        return experiment_results

    def _run_parallel_tests(
        self,
        test_combinations: List[Tuple],
        query: str,
        baseline_rankings: Dict,
        experiment_id: str,
    ) -> List[CrossProviderResult]:
        """Run tests in parallel using ThreadPoolExecutor."""
        results = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all test jobs
            future_to_test = {
                executor.submit(
                    self._execute_single_test,
                    provider,
                    attack_type,
                    target_product,
                    trial,
                    query,
                    baseline_rankings,
                    experiment_id,
                ): (provider, attack_type, target_product, trial)
                for provider, attack_type, target_product, trial in test_combinations
            }

            # Collect results as they complete
            for future in as_completed(future_to_test):
                provider, attack_type, target_product, trial = future_to_test[future]
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                        logger.debug(
                            f"Completed test: {provider.value} {attack_type.value} {target_product}"
                        )
                except Exception as e:
                    logger.error(
                        f"Test failed: {provider.value} {attack_type.value} {target_product} - {e}"
                    )

        return results

    def _run_sequential_tests(
        self,
        test_combinations: List[Tuple],
        query: str,
        baseline_rankings: Dict,
        experiment_id: str,
    ) -> List[CrossProviderResult]:
        """Run tests sequentially."""
        results = []

        for provider, attack_type, target_product, trial in test_combinations:
            try:
                result = self._execute_single_test(
                    provider,
                    attack_type,
                    target_product,
                    trial,
                    query,
                    baseline_rankings,
                    experiment_id,
                )
                if result:
                    results.append(result)
                    logger.debug(
                        f"Completed test: {provider.value} {attack_type.value} {target_product}"
                    )

                # Rate limiting
                config = self.provider_configs.get(provider)
                if config:
                    time.sleep(config.rate_limit_delay)

            except Exception as e:
                logger.error(
                    f"Test failed: {provider.value} {attack_type.value} {target_product} - {e}"
                )

        return results

    def _execute_single_test(
        self,
        provider: ProviderType,
        attack_type: AttackType,
        target_product: str,
        trial: int,
        query: str,
        baseline_rankings: Dict,
        experiment_id: str,
    ) -> Optional[CrossProviderResult]:
        """Execute a single attack test."""
        try:
            start_time = time.time()

            # Get client and config
            client = self.provider_clients[provider]
            config = self.provider_configs[provider]

            # Generate attack
            attack = self.attack_generator.generate_attack(attack_type, target_product)

            # Create ranker for this provider
            ranker = LLMRanker(client)

            # Get baseline position
            baseline_position = baseline_rankings.get(provider, {}).get(
                target_product, 999
            )

            # Execute attack
            ranking_result = ranker.rank_products_with_attack(query, attack)

            # Calculate results
            attack_successful = False
            ranking_position = 999
            position_change = 0

            if ranking_result and ranking_result.rankings:
                # Find target product position
                for i, product in enumerate(ranking_result.rankings):
                    if target_product in product or product in target_product:
                        ranking_position = i + 1
                        break

                position_change = baseline_position - ranking_position
                attack_successful = position_change > 0

            response_time = time.time() - start_time

            # Create result
            result = CrossProviderResult(
                provider=provider,
                model=config.model,
                attack_type=attack_type,
                attack_successful=attack_successful,
                ranking_position=ranking_position,
                confidence_score=ranking_result.confidence if ranking_result else 0.0,
                response_time=response_time,
                tokens_used=ranking_result.tokens_used if ranking_result else 0,
                attack_content=attack.content,
                target_product=target_product,
                baseline_position=baseline_position,
                position_change=position_change,
                experiment_id=experiment_id,
            )

            return result

        except Exception as e:
            logger.error(f"Single test execution failed: {e}")
            return CrossProviderResult(
                provider=provider,
                model=config.model if config else "unknown",
                attack_type=attack_type,
                attack_successful=False,
                ranking_position=999,
                confidence_score=0.0,
                response_time=0.0,
                tokens_used=0,
                attack_content="",
                target_product=target_product,
                baseline_position=999,
                position_change=0,
                error_occurred=True,
                error_message=str(e),
                experiment_id=experiment_id,
            )

    def _get_baseline_rankings(self, query: str) -> Dict[ProviderType, Dict[str, int]]:
        """Get baseline rankings for all providers."""
        baseline_rankings = {}

        for provider, client in self.provider_clients.items():
            try:
                ranker = LLMRanker(client)
                result = ranker.rank_products(query)

                if result and result.rankings:
                    provider_rankings = {}
                    for i, product in enumerate(result.rankings):
                        provider_rankings[product] = i + 1
                    baseline_rankings[provider] = provider_rankings
                else:
                    baseline_rankings[provider] = {}

            except Exception as e:
                logger.error(
                    f"Failed to get baseline rankings for {provider.value}: {e}"
                )
                baseline_rankings[provider] = {}

        return baseline_rankings

    def analyze_cross_provider_results(self) -> ProviderComparisonReport:
        """Analyze cross-provider results and generate comprehensive report."""
        if not self.cross_provider_results:
            logger.warning("No cross-provider results to analyze")
            return ProviderComparisonReport(
                total_experiments=0,
                successful_experiments=0,
                overall_success_rate=0.0,
                provider_results={},
                transferability_matrix={},
                universal_attacks=[],
                provider_specific_vulnerabilities={},
                response_time_comparison={},
                cost_analysis={},
                reliability_scores={},
                statistical_significance={},
                effect_sizes={},
                confidence_intervals={},
            )

        logger.info(
            f"Analyzing {len(self.cross_provider_results)} cross-provider results"
        )

        # Group results by provider
        provider_results = {}
        for provider in ProviderType:
            provider_data = [
                r for r in self.cross_provider_results if r.provider == provider
            ]
            if provider_data:
                provider_results[provider.value] = self._analyze_provider_results(
                    provider_data
                )

        # Calculate transferability matrix
        transferability_matrix = self._calculate_transferability_matrix()

        # Identify universal attacks and provider-specific vulnerabilities
        universal_attacks = self._identify_universal_attacks()
        provider_vulnerabilities = self._identify_provider_vulnerabilities()

        # Performance analysis
        response_times = self._analyze_response_times()
        cost_analysis = self._estimate_costs()
        reliability_scores = self._calculate_reliability_scores()

        # Statistical analysis
        statistical_tests = self._perform_statistical_tests()

        # Create comprehensive report
        report = ProviderComparisonReport(
            total_experiments=len(self.cross_provider_results),
            successful_experiments=sum(
                1 for r in self.cross_provider_results if r.attack_successful
            ),
            overall_success_rate=sum(
                1 for r in self.cross_provider_results if r.attack_successful
            )
            / len(self.cross_provider_results),
            provider_results=provider_results,
            transferability_matrix=transferability_matrix,
            universal_attacks=universal_attacks,
            provider_specific_vulnerabilities=provider_vulnerabilities,
            response_time_comparison=response_times,
            cost_analysis=cost_analysis,
            reliability_scores=reliability_scores,
            statistical_significance=statistical_tests.get("p_values", {}),
            effect_sizes=statistical_tests.get("effect_sizes", {}),
            confidence_intervals=statistical_tests.get("confidence_intervals", {}),
        )

        # Save report
        self._save_comparison_report(report)

        return report

    def _analyze_provider_results(
        self, results: List[CrossProviderResult]
    ) -> Dict[str, Any]:
        """Analyze results for a specific provider."""
        if not results:
            return {}

        total = len(results)
        successful = sum(1 for r in results if r.attack_successful)

        # Group by attack type
        attack_type_results = {}
        for attack_type in AttackType:
            type_results = [r for r in results if r.attack_type == attack_type]
            if type_results:
                type_successful = sum(1 for r in type_results if r.attack_successful)
                attack_type_results[attack_type.value] = {
                    "total": len(type_results),
                    "successful": type_successful,
                    "success_rate": type_successful / len(type_results),
                    "avg_position_change": np.mean(
                        [r.position_change for r in type_results]
                    ),
                    "avg_response_time": np.mean(
                        [r.response_time for r in type_results]
                    ),
                }

        return {
            "total_experiments": total,
            "successful_attacks": successful,
            "success_rate": successful / total,
            "avg_response_time": np.mean([r.response_time for r in results]),
            "avg_position_change": np.mean([r.position_change for r in results]),
            "error_rate": sum(1 for r in results if r.error_occurred) / total,
            "attack_type_breakdown": attack_type_results,
        }

    def _calculate_transferability_matrix(self) -> Dict[str, Dict[str, float]]:
        """Calculate attack transferability matrix across providers."""
        matrix = {}

        for attack_type in AttackType:
            attack_results = [
                r for r in self.cross_provider_results if r.attack_type == attack_type
            ]
            if not attack_results:
                continue

            type_matrix = {}
            for provider in ProviderType:
                provider_results = [r for r in attack_results if r.provider == provider]
                if provider_results:
                    success_rate = sum(
                        1 for r in provider_results if r.attack_successful
                    ) / len(provider_results)
                    type_matrix[provider.value] = success_rate

            matrix[attack_type.value] = type_matrix

        return matrix

    def _identify_universal_attacks(self) -> List[str]:
        """Identify attacks that work across all providers."""
        universal_attacks = []

        # Group by attack content
        attack_groups = {}
        for result in self.cross_provider_results:
            content = result.attack_content
            if content not in attack_groups:
                attack_groups[content] = []
            attack_groups[content].append(result)

        # Find attacks successful across multiple providers
        for attack_content, results in attack_groups.items():
            providers_tested = set(r.provider for r in results)
            successful_providers = set(
                r.provider for r in results if r.attack_successful
            )

            # Consider universal if successful on >70% of tested providers
            if len(successful_providers) / len(providers_tested) > 0.7:
                universal_attacks.append(attack_content)

        return universal_attacks

    def _identify_provider_vulnerabilities(self) -> Dict[str, List[str]]:
        """Identify provider-specific vulnerabilities."""
        vulnerabilities = {}

        for provider in ProviderType:
            provider_results = [
                r for r in self.cross_provider_results if r.provider == provider
            ]
            if not provider_results:
                continue

            # Find attacks that work particularly well on this provider
            provider_specific = []

            for attack_type in AttackType:
                type_results = [
                    r for r in provider_results if r.attack_type == attack_type
                ]
                if type_results:
                    success_rate = sum(
                        1 for r in type_results if r.attack_successful
                    ) / len(type_results)

                    # Compare with overall success rate for this attack type
                    all_type_results = [
                        r
                        for r in self.cross_provider_results
                        if r.attack_type == attack_type
                    ]
                    overall_success_rate = sum(
                        1 for r in all_type_results if r.attack_successful
                    ) / len(all_type_results)

                    # If significantly higher than average, consider it a vulnerability
                    if success_rate > overall_success_rate * 1.5:
                        provider_specific.append(attack_type.value)

            vulnerabilities[provider.value] = provider_specific

        return vulnerabilities

    def _analyze_response_times(self) -> Dict[str, float]:
        """Analyze response times across providers."""
        response_times = {}

        for provider in ProviderType:
            provider_results = [
                r for r in self.cross_provider_results if r.provider == provider
            ]
            if provider_results:
                avg_time = np.mean([r.response_time for r in provider_results])
                response_times[provider.value] = avg_time

        return response_times

    def _estimate_costs(self) -> Dict[str, float]:
        """Estimate costs across providers based on token usage."""
        # Simplified cost estimation (would need actual pricing)
        cost_per_1k_tokens = {
            ProviderType.OPENAI: 0.002,  # GPT-3.5-turbo
            ProviderType.ANTHROPIC: 0.001,  # Claude-3-Haiku
            ProviderType.BEDROCK: 0.0015,  # LLaMA
        }

        costs = {}
        for provider in ProviderType:
            provider_results = [
                r for r in self.cross_provider_results if r.provider == provider
            ]
            if provider_results:
                total_tokens = sum(r.tokens_used for r in provider_results)
                estimated_cost = (total_tokens / 1000) * cost_per_1k_tokens.get(
                    provider, 0.001
                )
                costs[provider.value] = estimated_cost

        return costs

    def _calculate_reliability_scores(self) -> Dict[str, float]:
        """Calculate reliability scores based on error rates and consistency."""
        reliability_scores = {}

        for provider in ProviderType:
            provider_results = [
                r for r in self.cross_provider_results if r.provider == provider
            ]
            if provider_results:
                error_rate = sum(1 for r in provider_results if r.error_occurred) / len(
                    provider_results
                )
                reliability_score = 1.0 - error_rate
                reliability_scores[provider.value] = reliability_score

        return reliability_scores

    def _perform_statistical_tests(self) -> Dict[str, Dict[str, Any]]:
        """Perform statistical tests across providers."""
        # This would implement chi-square tests, ANOVA, etc.
        # Placeholder implementation
        return {"p_values": {}, "effect_sizes": {}, "confidence_intervals": {}}

    def _save_experiment_results(
        self, results: List[CrossProviderResult], experiment_id: str
    ):
        """Save experiment results to file."""
        results_data = [asdict(r) for r in results]

        output_file = self.output_dir / f"{experiment_id}_results.json"
        with open(output_file, "w") as f:
            json.dump(results_data, f, indent=2, default=str)

        logger.info(f"Saved {len(results)} results to {output_file}")

    def _save_comparison_report(self, report: ProviderComparisonReport):
        """Save comparison report to file."""
        report_data = asdict(report)

        output_file = self.output_dir / "cross_provider_comparison_report.json"
        with open(output_file, "w") as f:
            json.dump(report_data, f, indent=2, default=str)

        logger.info(f"Saved comparison report to {output_file}")

        # Also create human-readable summary
        self._create_readable_summary(report)

    def _create_readable_summary(self, report: ProviderComparisonReport):
        """Create human-readable summary of results."""
        # Build provider performance section
        provider_sections = []
        for provider, data in report.provider_results.items():
            section = f"### {provider.title()}\n"
            section += f"- Success Rate: {data['success_rate']:.2%}\n"
            section += f"- Average Response Time: {data['avg_response_time']:.2f}s\n"
            section += f"- Error Rate: {data['error_rate']:.2%}\n"
            provider_sections.append(section)
        provider_performance = "\n".join(provider_sections)

        # Build transferability section
        transferability_sections = []
        for attack_type, provider_data in report.transferability_matrix.items():
            section = f"### {attack_type.title()}\n"
            for provider, success_rate in provider_data.items():
                section += f"- {provider}: {success_rate:.2%}\n"
            transferability_sections.append(section)
        transferability_content = "\n".join(transferability_sections)

        # Build universal attacks section
        universal_attacks = "\n".join(
            [f"- {attack}" for attack in report.universal_attacks[:5]]
        )

        # Build vulnerabilities section
        vulnerability_sections = []
        for (
            provider,
            vulnerabilities,
        ) in report.provider_specific_vulnerabilities.items():
            section = f"### {provider.title()}\n"
            for vuln in vulnerabilities:
                section += f"- {vuln}\n"
            vulnerability_sections.append(section)
        vulnerabilities_content = "\n".join(vulnerability_sections)

        summary_text = f"""# Multi-Provider Testing Report

        ## Overview

        - **Total Experiments**: {report.total_experiments}
        - **Successful Attacks**: {report.successful_experiments}
        - **Overall Success Rate**: {report.overall_success_rate:.2%}

        ## Provider Performance

        {provider_performance}

        ## Attack Transferability

        {transferability_content}

        ## Universal Attacks

        {universal_attacks}

        ## Provider-Specific Vulnerabilities

        {vulnerabilities_content}

        ---

        Generated on: {report.timestamp}
        Experiment Duration: {report.experiment_duration:.2f} seconds
        """

        with open(self.output_dir / "MULTI_PROVIDER_SUMMARY.md", "w") as f:
            f.write(summary_text)


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(
        description="Multi-provider adversarial SEO testing"
    )
    parser.add_argument(
        "--output-dir",
        default="data/results/multi_provider",
        help="Output directory for results",
    )
    parser.add_argument(
        "--query", default="best photography camera", help="Search query for testing"
    )
    parser.add_argument(
        "--num-trials", type=int, default=5, help="Number of trials per combination"
    )
    parser.add_argument(
        "--parallel", action="store_true", help="Enable parallel testing"
    )
    parser.add_argument(
        "--max-workers", type=int, default=3, help="Maximum parallel workers"
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Initialize tester
    tester = MultiProviderTester(
        output_dir=args.output_dir,
        max_workers=args.max_workers,
        enable_parallel=args.parallel,
    )

    # Auto-configure providers
    tester.auto_configure_providers()

    if not tester.provider_clients:
        print("❌ No providers configured. Please set up API keys.")
        return

    # Test connectivity
    connectivity = tester.test_provider_connectivity()
    available_providers = [p for p, connected in connectivity.items() if connected]

    if not available_providers:
        print("❌ No providers available. Check your API keys and network connection.")
        return

    print(
        f"✅ {len(available_providers)} providers available: {[p.value for p in available_providers]}"
    )

    # Run experiments
    attack_types = [
        AttackType.PROMPT_INJECTION,
        AttackType.DISCREDITATION,
        AttackType.PERSUASION,
    ]
    target_products = ["Canon EOS R6", "Sony A7 IV", "Nikon Z6 II"]

    start_time = time.time()

    results = tester.run_cross_provider_experiment(
        query=args.query,
        attack_types=attack_types,
        target_products=target_products,
        num_trials=args.num_trials,
    )

    experiment_duration = time.time() - start_time

    # Analyze results
    report = tester.analyze_cross_provider_results()
    report.experiment_duration = experiment_duration

    # Print summary
    print(f"\n✅ Multi-provider testing complete!")
    print(f"📁 Results saved to: {args.output_dir}")
    print(f"🧪 Total experiments: {len(results)}")
    print(f"⚡ Success rate: {report.overall_success_rate:.2%}")
    print(f"⏱️  Duration: {experiment_duration:.1f} seconds")


if __name__ == "__main__":
    main()
