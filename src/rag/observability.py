"""Transparency and logging for RAG pipeline."""

from abc import ABC, abstractmethod
from typing import Dict, Any
import json
from datetime import datetime


class ObservabilityHook(ABC):
    """Abstract base for observability hooks (Observer pattern)."""

    @abstractmethod
    def on_stage(self, stage: str, data: Dict[str, Any]) -> None:
        """Called when a pipeline stage completes.

        Args:
            stage: Stage name (e.g., 'retrieval', 'generation')
            data: Stage-specific data
        """
        pass


class ConsoleObserver(ObservabilityHook):
    """Prints pipeline stages to console.

    Example:
        >>> observer = ConsoleObserver()
        >>> pipeline.with_observability(observer)
    """

    def __init__(self, verbose: bool = True):
        """Initialize observer.

        Args:
            verbose: If True, print detailed information
        """
        self.verbose = verbose

    def on_stage(self, stage: str, data: Dict[str, Any]) -> None:
        """Print stage information.

        Args:
            stage: Stage name
            data: Stage data
        """
        print(f"\n[{stage.upper()}]")

        for key, value in data.items():
            if key == "result":
                # Don't print full result object
                print(f"  {key}: RAGResult object")
            elif key == "query" and len(str(value)) > 100:
                # Truncate long queries
                print(f"  {key}: {str(value)[:100]}...")
            elif self.verbose or key in ("num_retrieved", "num_docs", "duration"):
                # Always print key metrics
                print(f"  {key}: {value}")


class StructuredLogger(ObservabilityHook):
    """Logs pipeline stages as structured JSON.

    Example:
        >>> logger = StructuredLogger("rag_pipeline.log")
        >>> pipeline.with_observability(logger)
    """

    def __init__(self, log_file: str):
        """Initialize logger.

        Args:
            log_file: Path to log file
        """
        self.log_file = log_file

    def on_stage(self, stage: str, data: Dict[str, Any]) -> None:
        """Log stage as JSON.

        Args:
            stage: Stage name
            data: Stage data
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "stage": stage,
            "data": self._serialize(data),
        }

        with open(self.log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

    def _serialize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize data to JSON-compatible format.

        Args:
            data: Data dictionary

        Returns:
            JSON-compatible dictionary
        """
        serialized = {}

        for key, value in data.items():
            if hasattr(value, "__dict__"):
                # Convert objects to string representation
                serialized[key] = str(value)
            elif isinstance(value, (list, dict, str, int, float, bool, type(None))):
                # JSON-compatible types
                serialized[key] = value
            else:
                # Convert to string for other types
                serialized[key] = str(value)

        return serialized


class MetricsCollector(ObservabilityHook):
    """Collects metrics from RAG pipeline execution.

    Example:
        >>> metrics = MetricsCollector()
        >>> pipeline.with_observability(metrics)
        >>> result = pipeline.query("test")
        >>> print(metrics.get_summary())
    """

    def __init__(self):
        """Initialize metrics collector."""
        self.metrics = {
            "total_queries": 0,
            "total_retrieval_time": 0.0,
            "total_generation_time": 0.0,
            "total_documents_retrieved": 0,
            "stages": [],
        }

    def on_stage(self, stage: str, data: Dict[str, Any]) -> None:
        """Collect metrics from pipeline stage.

        Args:
            stage: Stage name
            data: Stage data
        """
        self.metrics["stages"].append({"stage": stage, "data": data})

        if stage == "retrieval":
            self.metrics["total_retrieval_time"] += data.get("duration", 0.0)
            self.metrics["total_documents_retrieved"] += data.get("num_retrieved", 0)

        elif stage == "generation":
            self.metrics["total_generation_time"] += data.get("duration", 0.0)

        elif stage == "complete":
            self.metrics["total_queries"] += 1

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of collected metrics.

        Returns:
            Dictionary with aggregated metrics
        """
        if self.metrics["total_queries"] == 0:
            return self.metrics

        return {
            "total_queries": self.metrics["total_queries"],
            "avg_retrieval_time": (
                self.metrics["total_retrieval_time"] / self.metrics["total_queries"]
            ),
            "avg_generation_time": (
                self.metrics["total_generation_time"] / self.metrics["total_queries"]
            ),
            "avg_documents_retrieved": (
                self.metrics["total_documents_retrieved"] / self.metrics["total_queries"]
            ),
        }

    def reset(self) -> None:
        """Reset all collected metrics."""
        self.metrics = {
            "total_queries": 0,
            "total_retrieval_time": 0.0,
            "total_generation_time": 0.0,
            "total_documents_retrieved": 0,
            "stages": [],
        }
