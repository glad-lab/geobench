"""
Utilities package for benchmark experiments.

This package provides modular utilities for:
- Dataset loading and format detection
- Product manipulation and transformation
- Sampling strategies (random, stratified, weighted)
- Data validation and integrity checks
"""

from .data_loader import UnifiedDataLoader
from .manipulator import ProductManipulator
from .sampling import SamplingStrategy
from .validation import DataValidator, ValidationResult

__all__ = [
    "UnifiedDataLoader",
    "ProductManipulator",
    "SamplingStrategy",
    "DataValidator",
    "ValidationResult",
]

__version__ = "1.0.0"
