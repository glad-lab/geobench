"""
Factory pattern for experiment creation.

This module provides a centralized factory for creating experiment instances
based on configuration, following the Factory pattern for extensibility.

Design Patterns:
    - Factory Pattern: Centralized object creation
    - Registry Pattern: Pluggable experiment types
    - Open/Closed Principle: Extend without modification

Example:
    >>> from experiments.factory import ExperimentFactory
    >>> from experiments.base import ExperimentConfig, ExperimentType
    >>>
    >>> config = ExperimentConfig(
    ...     experiment_type=ExperimentType.SINGLE_ATTACK,
    ...     num_trials=50
    ... )
    >>> factory = ExperimentFactory()
    >>> experiment = factory.create(config.experiment_type, config)
    >>> result = experiment.run()
"""

from typing import Dict, Type, Optional
import logging

from .base import BaseExperiment, ExperimentConfig, ExperimentType
from .commands import (
    BaselineExperiment,
    SingleAttackExperiment,
    PrisonersDilemmaExperiment,
    ExternalAttackExperiment,
    PositionalBiasExperiment,
)

logger = logging.getLogger(__name__)


class ExperimentFactory:
    """
    Factory for creating experiment instances (Factory pattern).

    This factory centralizes experiment instantiation logic and provides
    extensibility for new experiment types through registration.

    The factory maintains a registry mapping ExperimentType to concrete
    experiment classes, allowing new types to be added without modifying
    the factory code (Open/Closed Principle).

    Attributes:
        _registry: Mapping of ExperimentType to experiment class

    Example:
        >>> factory = ExperimentFactory()
        >>>
        >>> # Create experiment from config
        >>> config = ExperimentConfig(experiment_type=ExperimentType.BASELINE)
        >>> experiment = factory.create(config.experiment_type, config)
        >>>
        >>> # Register custom experiment type
        >>> class MyExperiment(BaseExperiment):
        ...     def setup(self): pass
        ...     def execute(self): return []
        ...     def analyze(self, results): return {}
        >>>
        >>> factory.register(ExperimentType.BASELINE, MyExperiment)
    """

    # Class-level registry (shared across all instances)
    _registry: Dict[ExperimentType, Type[BaseExperiment]] = {
        ExperimentType.BASELINE: BaselineExperiment,
        ExperimentType.SINGLE_ATTACK: SingleAttackExperiment,
        ExperimentType.PRISONERS_DILEMMA: PrisonersDilemmaExperiment,
        ExperimentType.EXTERNAL_ATTACK: ExternalAttackExperiment,
        ExperimentType.POSITIONAL_BIAS: PositionalBiasExperiment,
    }

    def create(
        self,
        experiment_type: ExperimentType,
        config: ExperimentConfig,
        **kwargs
    ) -> BaseExperiment:
        """
        Create experiment instance based on type and configuration.

        This is the main factory method that instantiates the appropriate
        experiment class based on the experiment type.

        Args:
            experiment_type: Type of experiment to create
            config: Experiment configuration object
            **kwargs: Additional arguments passed to experiment constructor

        Returns:
            Configured experiment instance ready to run

        Raises:
            ValueError: If experiment type not registered
            TypeError: If experiment class doesn't extend BaseExperiment

        Example:
            >>> config = ExperimentConfig(
            ...     experiment_type=ExperimentType.SINGLE_ATTACK,
            ...     num_trials=50
            ... )
            >>> experiment = factory.create(
            ...     config.experiment_type,
            ...     config,
            ...     custom_param="value"
            ... )
        """
        # Validate experiment type is registered
        if experiment_type not in self._registry:
            available = ", ".join(t.value for t in self._registry.keys())
            raise ValueError(
                f"Unknown experiment type: {experiment_type.value}. "
                f"Available types: {available}"
            )

        # Get experiment class
        experiment_class = self._registry[experiment_type]

        # Validate it's a BaseExperiment subclass
        if not issubclass(experiment_class, BaseExperiment):
            raise TypeError(
                f"Experiment class {experiment_class.__name__} must extend BaseExperiment"
            )

        # Instantiate and return
        logger.info(
            f"Creating experiment: {experiment_type.value} "
            f"({experiment_class.__name__})"
        )

        try:
            experiment = experiment_class(config, **kwargs)
            logger.debug(f"Created {experiment_class.__name__} with config: {config}")
            return experiment

        except Exception as e:
            logger.error(
                f"Failed to create experiment {experiment_type.value}: {e}",
                exc_info=True
            )
            raise ValueError(
                f"Failed to create experiment {experiment_type.value}: {e}"
            ) from e

    @classmethod
    def register(
        cls,
        experiment_type: ExperimentType,
        experiment_class: Type[BaseExperiment]
    ) -> None:
        """
        Register new experiment type (Open/Closed principle).

        This allows extending the factory with new experiment types without
        modifying the factory code itself.

        Args:
            experiment_type: ExperimentType enum value
            experiment_class: Class implementing BaseExperiment

        Raises:
            TypeError: If experiment_class doesn't extend BaseExperiment
            ValueError: If experiment_type is None

        Example:
            >>> class CustomExperiment(BaseExperiment):
            ...     def setup(self): pass
            ...     def execute(self): return []
            ...     def analyze(self, results): return {}
            >>>
            >>> ExperimentFactory.register(
            ...     ExperimentType.BASELINE,
            ...     CustomExperiment
            ... )
        """
        if experiment_type is None:
            raise ValueError("experiment_type cannot be None")

        if not issubclass(experiment_class, BaseExperiment):
            raise TypeError(
                f"Experiment class {experiment_class.__name__} must extend BaseExperiment"
            )

        logger.info(
            f"Registering experiment type {experiment_type.value} -> "
            f"{experiment_class.__name__}"
        )

        cls._registry[experiment_type] = experiment_class

    @classmethod
    def unregister(cls, experiment_type: ExperimentType) -> None:
        """
        Remove experiment type from registry.

        Args:
            experiment_type: Type to remove

        Example:
            >>> ExperimentFactory.unregister(ExperimentType.BASELINE)
        """
        if experiment_type in cls._registry:
            experiment_class = cls._registry[experiment_type]
            logger.info(
                f"Unregistering {experiment_type.value} "
                f"({experiment_class.__name__})"
            )
            del cls._registry[experiment_type]
        else:
            logger.warning(
                f"Cannot unregister {experiment_type.value}: not in registry"
            )

    @classmethod
    def get_registered_types(cls) -> Dict[ExperimentType, Type[BaseExperiment]]:
        """
        Get all registered experiment types.

        Returns:
            Dictionary mapping ExperimentType to experiment class

        Example:
            >>> types = ExperimentFactory.get_registered_types()
            >>> for exp_type, exp_class in types.items():
            ...     print(f"{exp_type.value}: {exp_class.__name__}")
        """
        return dict(cls._registry)

    @classmethod
    def is_registered(cls, experiment_type: ExperimentType) -> bool:
        """
        Check if experiment type is registered.

        Args:
            experiment_type: Type to check

        Returns:
            True if registered, False otherwise

        Example:
            >>> if ExperimentFactory.is_registered(ExperimentType.BASELINE):
            ...     print("Baseline experiment available")
        """
        return experiment_type in cls._registry

    def create_from_name(
        self,
        experiment_name: str,
        config: ExperimentConfig,
        **kwargs
    ) -> Optional[BaseExperiment]:
        """
        Create experiment from string name.

        Convenience method for creating experiments from string identifiers.

        Args:
            experiment_name: Name matching ExperimentType.value
            config: Experiment configuration
            **kwargs: Additional constructor arguments

        Returns:
            Experiment instance if found, None otherwise

        Example:
            >>> experiment = factory.create_from_name(
            ...     "single_attack",
            ...     config
            ... )
        """
        # Find matching ExperimentType
        for exp_type in ExperimentType:
            if exp_type.value == experiment_name:
                return self.create(exp_type, config, **kwargs)

        logger.warning(f"No experiment type found for name: {experiment_name}")
        return None

    def create_all(
        self,
        config: ExperimentConfig,
        **kwargs
    ) -> Dict[ExperimentType, BaseExperiment]:
        """
        Create all registered experiment types with same config.

        Useful for running comprehensive test suites.

        Args:
            config: Base configuration (experiment_type will be overridden)
            **kwargs: Additional constructor arguments

        Returns:
            Dictionary mapping ExperimentType to experiment instance

        Example:
            >>> experiments = factory.create_all(base_config)
            >>> for exp_type, experiment in experiments.items():
            ...     result = experiment.run()
        """
        experiments = {}

        for exp_type in self._registry.keys():
            try:
                # Create modified config with correct experiment_type
                exp_config = ExperimentConfig(
                    experiment_type=exp_type,
                    num_trials=config.num_trials,
                    num_products=config.num_products,
                    attack_types=config.attack_types,
                    num_attackers=config.num_attackers,
                    query=config.query,
                    save_results=config.save_results,
                    output_dir=config.output_dir,
                    random_seed=config.random_seed,
                    use_rag=config.use_rag,
                    model=config.model,
                    provider=config.provider,
                    rate_limit_delay=config.rate_limit_delay,
                    batch_size=config.batch_size,
                )

                experiment = self.create(exp_type, exp_config, **kwargs)
                experiments[exp_type] = experiment

            except Exception as e:
                logger.error(f"Failed to create {exp_type.value}: {e}")
                continue

        logger.info(f"Created {len(experiments)}/{len(self._registry)} experiments")
        return experiments
