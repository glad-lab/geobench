"""
Configuration builders for complex experiment setups.

This module provides builder patterns and preset configurations for
constructing ExperimentConfig objects with validation and sensible defaults.

Design Patterns:
    - Builder Pattern: Fluent interface for configuration
    - Factory Method: Preset configuration creation
    - Validation: Configuration constraints enforcement

Example:
    >>> from experiments.configs import ExperimentConfigBuilder
    >>> from attacks import AttackType
    >>>
    >>> config = (ExperimentConfigBuilder()
    ...     .with_name("my_experiment")
    ...     .with_trials(100)
    ...     .with_attack_types([AttackType.PROMPT_INJECTION])
    ...     .with_model("openai", "gpt-4")
    ...     .build()
    ... )
"""

from typing import List, Optional, Any
import logging

from .base import ExperimentConfig, ExperimentType

try:
    from ..attacks import AttackType
except ImportError:
    AttackType = Any

logger = logging.getLogger(__name__)


class ExperimentConfigBuilder:
    """
    Builder pattern for constructing complex ExperimentConfig objects.

    Provides fluent interface for configuration construction with
    validation and sensible defaults. All methods return self for
    method chaining.

    Example:
        >>> config = (ExperimentConfigBuilder()
        ...     .with_experiment_type(ExperimentType.SINGLE_ATTACK)
        ...     .with_trials(100)
        ...     .with_products(5)
        ...     .with_attack_types([AttackType.PROMPT_INJECTION])
        ...     .with_query("best camera for photography")
        ...     .with_model("openai", "gpt-4")
        ...     .with_random_seed(42)
        ...     .build()
        ... )
    """

    def __init__(self):
        """Initialize builder with default values."""
        # Core experiment settings
        self._experiment_type = ExperimentType.SINGLE_ATTACK
        self._num_trials = 50
        self._num_products = 4
        self._query = "best camera for photography"

        # Attack configuration
        self._attack_types: List[Any] = []
        self._num_attackers = 0

        # Output configuration
        self._save_results = True
        self._output_dir = "data/results"

        # Reproducibility
        self._random_seed: Optional[int] = None

        # LLM configuration
        self._use_rag = True
        self._model: Optional[str] = None
        self._provider: Optional[str] = None

        # Performance tuning
        self._rate_limit_delay = 1.0
        self._batch_size = 10

    def with_experiment_type(self, exp_type: ExperimentType) -> 'ExperimentConfigBuilder':
        """
        Set experiment type.

        Args:
            exp_type: Type of experiment to run

        Returns:
            Self for method chaining
        """
        self._experiment_type = exp_type
        return self

    def with_trials(self, num_trials: int) -> 'ExperimentConfigBuilder':
        """
        Set number of trials to run.

        Args:
            num_trials: Number of trials (must be >= 1)

        Returns:
            Self for method chaining

        Raises:
            ValueError: If num_trials < 1
        """
        if num_trials < 1:
            raise ValueError(f"num_trials must be >= 1, got {num_trials}")
        self._num_trials = num_trials
        return self

    def with_products(self, num_products: int) -> 'ExperimentConfigBuilder':
        """
        Set number of products in catalog.

        Args:
            num_products: Number of products (must be >= 2)

        Returns:
            Self for method chaining

        Raises:
            ValueError: If num_products < 2
        """
        if num_products < 2:
            raise ValueError(f"num_products must be >= 2, got {num_products}")
        self._num_products = num_products
        return self

    def with_attack_types(self, attack_types: List[Any]) -> 'ExperimentConfigBuilder':
        """
        Set attack types to test.

        Args:
            attack_types: List of AttackType enum values

        Returns:
            Self for method chaining
        """
        self._attack_types = attack_types
        return self

    def with_num_attackers(self, num_attackers: int) -> 'ExperimentConfigBuilder':
        """
        Set number of attackers (for prisoner's dilemma).

        Args:
            num_attackers: Number of concurrent attackers (must be >= 0)

        Returns:
            Self for method chaining

        Raises:
            ValueError: If num_attackers < 0
        """
        if num_attackers < 0:
            raise ValueError(f"num_attackers must be >= 0, got {num_attackers}")
        self._num_attackers = num_attackers
        return self

    def with_query(self, query: str) -> 'ExperimentConfigBuilder':
        """
        Set search query.

        Args:
            query: Search query string

        Returns:
            Self for method chaining

        Raises:
            ValueError: If query is empty
        """
        if not query or not query.strip():
            raise ValueError("query cannot be empty")
        self._query = query.strip()
        return self

    def with_random_seed(self, seed: int) -> 'ExperimentConfigBuilder':
        """
        Set random seed for reproducibility.

        Args:
            seed: Random seed value

        Returns:
            Self for method chaining
        """
        self._random_seed = seed
        return self

    def with_model(self, provider: str, model: str) -> 'ExperimentConfigBuilder':
        """
        Set LLM provider and model.

        Args:
            provider: Provider name (openai, anthropic, bedrock)
            model: Model identifier

        Returns:
            Self for method chaining

        Example:
            >>> builder.with_model("openai", "gpt-4")
            >>> builder.with_model("anthropic", "claude-3-sonnet-20240229")
        """
        self._provider = provider
        self._model = model
        return self

    def with_rag(self, use_rag: bool) -> 'ExperimentConfigBuilder':
        """
        Enable or disable RAG-based ranking.

        Args:
            use_rag: Whether to use RAG

        Returns:
            Self for method chaining
        """
        self._use_rag = use_rag
        return self

    def with_output(
        self,
        save_results: bool,
        output_dir: Optional[str] = None
    ) -> 'ExperimentConfigBuilder':
        """
        Configure result output.

        Args:
            save_results: Whether to save results to disk
            output_dir: Directory for result files (if save_results=True)

        Returns:
            Self for method chaining
        """
        self._save_results = save_results
        if output_dir:
            self._output_dir = output_dir
        return self

    def with_rate_limit(self, delay: float) -> 'ExperimentConfigBuilder':
        """
        Set rate limiting delay between API calls.

        Args:
            delay: Delay in seconds (must be >= 0)

        Returns:
            Self for method chaining

        Raises:
            ValueError: If delay < 0
        """
        if delay < 0:
            raise ValueError(f"rate_limit_delay must be >= 0, got {delay}")
        self._rate_limit_delay = delay
        return self

    def with_batch_size(self, batch_size: int) -> 'ExperimentConfigBuilder':
        """
        Set batch size for trial processing.

        Args:
            batch_size: Number of trials per batch (must be >= 1)

        Returns:
            Self for method chaining

        Raises:
            ValueError: If batch_size < 1
        """
        if batch_size < 1:
            raise ValueError(f"batch_size must be >= 1, got {batch_size}")
        self._batch_size = batch_size
        return self

    def build(self) -> ExperimentConfig:
        """
        Build final ExperimentConfig object.

        Validates all configuration values before constructing the config.

        Returns:
            Validated ExperimentConfig instance

        Raises:
            ValueError: If configuration is invalid

        Example:
            >>> config = builder.build()
            >>> experiment = ExperimentFactory().create(config.experiment_type, config)
        """
        # Validate before building
        self._validate()

        config = ExperimentConfig(
            experiment_type=self._experiment_type,
            num_trials=self._num_trials,
            num_products=self._num_products,
            attack_types=self._attack_types,
            num_attackers=self._num_attackers,
            query=self._query,
            save_results=self._save_results,
            output_dir=self._output_dir,
            random_seed=self._random_seed,
            use_rag=self._use_rag,
            model=self._model,
            provider=self._provider,
            rate_limit_delay=self._rate_limit_delay,
            batch_size=self._batch_size,
        )

        logger.info(
            f"Built config: {config.experiment_type.value} "
            f"({config.num_trials} trials, {config.num_products} products)"
        )

        return config

    def _validate(self) -> None:
        """
        Validate configuration before building.

        Raises:
            ValueError: If configuration is invalid
        """
        # Validate num_trials
        if self._num_trials < 1:
            raise ValueError(f"num_trials must be >= 1, got {self._num_trials}")

        # Validate num_products
        if self._num_products < 2:
            raise ValueError(f"num_products must be >= 2, got {self._num_products}")

        # Validate num_attackers
        if self._num_attackers < 0:
            raise ValueError(f"num_attackers must be >= 0, got {self._num_attackers}")

        # Validate query
        if not self._query or not self._query.strip():
            raise ValueError("query cannot be empty")

        # Validate rate_limit_delay
        if self._rate_limit_delay < 0:
            raise ValueError(
                f"rate_limit_delay must be >= 0, got {self._rate_limit_delay}"
            )

        # Validate batch_size
        if self._batch_size < 1:
            raise ValueError(f"batch_size must be >= 1, got {self._batch_size}")

        # Experiment-specific validation
        if self._experiment_type == ExperimentType.PRISONERS_DILEMMA:
            if self._num_attackers == 0:
                logger.warning(
                    "Prisoner's dilemma experiment with num_attackers=0. "
                    "Consider setting num_attackers >= 2."
                )

        if self._experiment_type == ExperimentType.SINGLE_ATTACK:
            if not self._attack_types:
                logger.warning(
                    "Single attack experiment with no attack_types specified. "
                    "Will use default attack types."
                )


# Preset configurations for common experiment scenarios

PRESET_BASELINE = ExperimentConfig(
    experiment_type=ExperimentType.BASELINE,
    num_trials=50,
    num_products=4,
    attack_types=[],
    num_attackers=0,
    query="best camera for photography",
    save_results=True,
    output_dir="data/results",
    random_seed=42,
    use_rag=True,
    model=None,
    provider=None,
    rate_limit_delay=1.0,
    batch_size=10,
)

PRESET_SINGLE_ATTACK = ExperimentConfig(
    experiment_type=ExperimentType.SINGLE_ATTACK,
    num_trials=50,
    num_products=4,
    attack_types=[],  # Will be populated with all AttackType values
    num_attackers=0,
    query="best camera for photography",
    save_results=True,
    output_dir="data/results",
    random_seed=42,
    use_rag=True,
    model=None,
    provider=None,
    rate_limit_delay=1.0,
    batch_size=10,
)

PRESET_PRISONERS_DILEMMA = ExperimentConfig(
    experiment_type=ExperimentType.PRISONERS_DILEMMA,
    num_trials=50,
    num_products=4,
    attack_types=[],
    num_attackers=3,
    query="best camera for photography",
    save_results=True,
    output_dir="data/results",
    random_seed=42,
    use_rag=True,
    model=None,
    provider=None,
    rate_limit_delay=1.0,
    batch_size=10,
)

PRESET_POSITIONAL_BIAS = ExperimentConfig(
    experiment_type=ExperimentType.POSITIONAL_BIAS,
    num_trials=60,  # 20 per position
    num_products=4,
    attack_types=[],
    num_attackers=0,
    query="best camera for photography",
    save_results=True,
    output_dir="data/results",
    random_seed=42,
    use_rag=True,
    model=None,
    provider=None,
    rate_limit_delay=1.0,
    batch_size=10,
)

PRESET_QUICK_TEST = ExperimentConfig(
    experiment_type=ExperimentType.SINGLE_ATTACK,
    num_trials=5,  # Quick test
    num_products=3,
    attack_types=[],
    num_attackers=0,
    query="best laptop",
    save_results=False,
    output_dir="data/results",
    random_seed=42,
    use_rag=True,
    model=None,
    provider=None,
    rate_limit_delay=0.5,
    batch_size=5,
)


def create_preset_config(preset_name: str) -> Optional[ExperimentConfig]:
    """
    Create preset configuration by name.

    Args:
        preset_name: Name of preset (baseline, single_attack, prisoners_dilemma, etc.)

    Returns:
        ExperimentConfig if preset found, None otherwise

    Example:
        >>> config = create_preset_config("baseline")
        >>> experiment = ExperimentFactory().create(config.experiment_type, config)
    """
    presets = {
        "baseline": PRESET_BASELINE,
        "single_attack": PRESET_SINGLE_ATTACK,
        "prisoners_dilemma": PRESET_PRISONERS_DILEMMA,
        "positional_bias": PRESET_POSITIONAL_BIAS,
        "quick_test": PRESET_QUICK_TEST,
    }

    config = presets.get(preset_name.lower())
    if config:
        logger.info(f"Created preset config: {preset_name}")
    else:
        logger.warning(f"Unknown preset: {preset_name}")

    return config
