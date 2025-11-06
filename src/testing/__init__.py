"""
Testing framework for adversarial SEO experiments.

This package provides multi-provider testing infrastructure for validating
adversarial attacks across different LLM providers and models.
"""

from .base import TestConfig, BaseTestSuite
from .provider_tests import MultiProviderTestSuite, ProviderTestResult
from .scenarios import TestScenario, ScenarioBuilder
from .reporters import TestReporter, TestReport

__all__ = [
    "TestConfig",
    "BaseTestSuite",
    "MultiProviderTestSuite",
    "ProviderTestResult",
    "TestScenario",
    "ScenarioBuilder",
    "TestReporter",
    "TestReport",
]

__version__ = "1.0.0"
