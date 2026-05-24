"""Base abstractions for evaluation system."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime


@dataclass
class EvaluationResult:
    """Result of an evaluation operation.

    Attributes:
        evaluator_name: Name of evaluator that produced this result
        metrics: Dictionary of metric name to value
        passed: Whether evaluation passed threshold criteria
        errors: List of error messages
        warnings: List of warning messages
        metadata: Additional metadata
        timestamp: When evaluation was performed
    """
    evaluator_name: str
    metrics: Dict[str, float]
    passed: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def add_error(self, error: str) -> None:
        """Add error message and mark as failed.

        Args:
            error: Error message to add
        """
        self.errors.append(error)
        self.passed = False

    def add_warning(self, warning: str) -> None:
        """Add warning message.

        Args:
            warning: Warning message to add
        """
        self.warnings.append(warning)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary.

        Returns:
            Dictionary representation of result
        """
        return {
            "evaluator_name": self.evaluator_name,
            "metrics": self.metrics,
            "passed": self.passed,
            "errors": self.errors,
            "warnings": self.warnings,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
        }


class BaseEvaluator(ABC):
    """Abstract base class for evaluators.

    All evaluators should extend this class and implement the evaluate method.
    Provides common functionality for creating results and handling errors.
    """

    def __init__(self, name: str):
        """Initialize evaluator.

        Args:
            name: Name of this evaluator
        """
        self.name = name

    @abstractmethod
    def evaluate(self, data: List[Dict[str, Any]]) -> EvaluationResult:
        """Evaluate data and return results.

        Args:
            data: List of experiment results to evaluate

        Returns:
            EvaluationResult with metrics and status

        Raises:
            ValueError: If data is invalid or missing required fields
        """
        pass

    def _create_result(
        self,
        metrics: Dict[str, float],
        metadata: Optional[Dict[str, Any]] = None
    ) -> EvaluationResult:
        """Helper to create EvaluationResult.

        Args:
            metrics: Dictionary of metric name to value
            metadata: Optional metadata to include

        Returns:
            EvaluationResult instance
        """
        return EvaluationResult(
            evaluator_name=self.name,
            metrics=metrics,
            metadata=metadata or {}
        )

    def _validate_data(
        self,
        data: List[Dict[str, Any]],
        required_fields: Optional[List[str]] = None
    ) -> None:
        """Validate input data.

        Args:
            data: Data to validate
            required_fields: Fields that must be present in each data item

        Raises:
            ValueError: If validation fails
        """
        if not data:
            raise ValueError("Data cannot be empty")

        if required_fields:
            for i, item in enumerate(data):
                missing = [f for f in required_fields if f not in item]
                if missing:
                    raise ValueError(
                        f"Item {i} missing required fields: {missing}"
                    )
