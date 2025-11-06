"""
Backward compatibility layer for legacy ranking imports.

DEPRECATED: This module is maintained for backward compatibility only.
New code should import from the 'ranking' package instead:

    from ranking import (
        create_ranker,
        LLMRanker,
        RAGRanker,
        Product,
        RankingResult,
        RankingMetrics,
    )

The modular ranking package provides better organization, error handling,
and follows SOLID principles with comprehensive testing.
"""

import warnings
from typing import List, Dict, Optional, Tuple, Any

# Issue deprecation warning
warnings.warn(
    "Importing from ranking is deprecated and will be removed in a future version. "
    "Use 'from ranking import ...' (package) instead. "
    "See docs/ for migration guide.",
    DeprecationWarning,
    stacklevel=2
)

# Import all public APIs from the new package
from .ranking import (
    # Core classes
    BaseRanker,
    Product,
    RankingResult,
    RankingStrategy,
    RankingError,
    RankingValidationError,
    RankingExecutionError,
    # Rankers
    LLMRanker,
    RAGRanker,
    # Metrics
    RankingMetrics,
    # Factory
    RankerFactory,
    create_ranker,
    # Utilities
    PositionalBiasAnalyzer,
    # Backward compatibility aliases
    RankingSystem,
    SimpleRAG,
)

__all__ = [
    # Core classes
    "BaseRanker",
    "Product",
    "RankingResult",
    "RankingStrategy",
    "RankingError",
    "RankingValidationError",
    "RankingExecutionError",
    # Rankers
    "LLMRanker",
    "RAGRanker",
    # Metrics
    "RankingMetrics",
    # Factory
    "RankerFactory",
    "create_ranker",
    # Utilities
    "PositionalBiasAnalyzer",
    # Backward compatibility aliases
    "RankingSystem",
    "SimpleRAG",
]
