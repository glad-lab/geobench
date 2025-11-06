"""
Base classes for testing framework.

Provides abstract interfaces and configuration for test suites.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum


class ProviderType(Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    BEDROCK = "bedrock"


@dataclass
class TestConfig:
    """Configuration for multi-provider tests."""

    # Provider configuration
    providers: List[str] = field(default_factory=lambda: ["openai", "anthropic", "bedrock"])
    models: Dict[str, str] = field(default_factory=dict)

    # Attack configuration
    attack_types: List[str] = field(default_factory=list)
    target_products: List[str] = field(default_factory=list)

    # Test parameters
    num_trials: int = 10
    enable_parallel: bool = True
    max_workers: int = 3

    # Rate limiting
    rate_limit_delay: float = 1.0
    timeout: int = 30

    # Output configuration
    output_dir: str = "data/results/testing"
    save_results: bool = True

    # Vector store configuration
    vector_store_host: str = "localhost"
    vector_store_port: int = 6333
    collection_name: str = "adversarial_seo_products"

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "providers": self.providers,
            "models": self.models,
            "attack_types": self.attack_types,
            "target_products": self.target_products,
            "num_trials": self.num_trials,
            "enable_parallel": self.enable_parallel,
            "max_workers": self.max_workers,
            "rate_limit_delay": self.rate_limit_delay,
            "timeout": self.timeout,
            "output_dir": self.output_dir,
            "save_results": self.save_results,
            "vector_store_host": self.vector_store_host,
            "vector_store_port": self.vector_store_port,
            "collection_name": self.collection_name,
        }

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "TestConfig":
        """Create configuration from dictionary."""
        return cls(**config_dict)


class BaseTestSuite(ABC):
    """Abstract base class for test suites."""

    def __init__(self, config: TestConfig):
        """
        Initialize test suite.

        Args:
            config: Test configuration
        """
        self.config = config
        self.results: List[Any] = []
        self._is_setup = False

    @abstractmethod
    def setup(self) -> None:
        """
        Setup test environment.

        This method should initialize all required resources like clients,
        vector stores, and configuration.
        """
        pass

    @abstractmethod
    def run_tests(self) -> Dict[str, Any]:
        """
        Run test suite.

        Returns:
            Dictionary containing test results and metrics
        """
        pass

    @abstractmethod
    def teardown(self) -> None:
        """
        Cleanup test environment.

        This method should release all resources and save results.
        """
        pass

    def execute(self) -> Dict[str, Any]:
        """
        Execute complete test suite lifecycle.

        Returns:
            Dictionary containing test results
        """
        try:
            self.setup()
            results = self.run_tests()
            return results
        finally:
            self.teardown()

    def validate_config(self) -> bool:
        """
        Validate test configuration.

        Returns:
            True if configuration is valid
        """
        if not self.config.providers:
            raise ValueError("At least one provider must be specified")

        if not self.config.attack_types:
            raise ValueError("At least one attack type must be specified")

        if self.config.num_trials < 1:
            raise ValueError("Number of trials must be at least 1")

        if self.config.max_workers < 1:
            raise ValueError("Max workers must be at least 1")

        return True


class TestResult:
    """Base class for test results."""

    def __init__(
        self,
        test_name: str,
        success: bool,
        duration: float,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize test result.

        Args:
            test_name: Name of the test
            success: Whether test succeeded
            duration: Test execution time in seconds
            error_message: Error message if test failed
            metadata: Additional test metadata
        """
        self.test_name = test_name
        self.success = success
        self.duration = duration
        self.error_message = error_message
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "test_name": self.test_name,
            "success": self.success,
            "duration": self.duration,
            "error_message": self.error_message,
            "metadata": self.metadata,
        }
