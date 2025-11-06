#!/usr/bin/env python3
"""
Data formatting utilities for visualizations.

Provides utilities for transforming, normalizing, and preparing data
for visualization components.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class DataFormatter:
    """
    Utilities for formatting and transforming visualization data.

    Provides methods for normalizing rates, aggregating results,
    and preparing data structures for different chart types.
    """

    @staticmethod
    def normalize_rates(rates: List[float], as_percentage: bool = True) -> List[float]:
        """
        Normalize success rates to [0, 1] or [0, 100] range.

        Handles rates that may be provided as decimals (0.5) or
        percentages (50) and normalizes them consistently.

        Args:
            rates: List of success rates
            as_percentage: If True, return as percentages (0-100)

        Returns:
            Normalized rates
        """
        normalized = []
        for rate in rates:
            # Convert to decimal if > 1
            if rate > 1:
                rate = min(rate / 100, 1.0)

            # Convert to percentage if requested
            if as_percentage:
                rate = rate * 100

            normalized.append(rate)

        return normalized

    @staticmethod
    def aggregate_by_category(
        results: List[Dict[str, Any]],
        category_key: str,
        value_key: str,
        aggregation: str = 'mean'
    ) -> Dict[str, float]:
        """
        Aggregate results by category.

        Args:
            results: List of result dictionaries
            category_key: Key to group by
            value_key: Key to aggregate
            aggregation: Aggregation method ('mean', 'sum', 'count')

        Returns:
            Dict mapping categories to aggregated values
        """
        df = pd.DataFrame(results)

        if category_key not in df.columns or value_key not in df.columns:
            logger.warning(f"Keys {category_key} or {value_key} not found in data")
            return {}

        if aggregation == 'mean':
            aggregated = df.groupby(category_key)[value_key].mean()
        elif aggregation == 'sum':
            aggregated = df.groupby(category_key)[value_key].sum()
        elif aggregation == 'count':
            aggregated = df.groupby(category_key)[value_key].count()
        else:
            logger.warning(f"Unknown aggregation method: {aggregation}")
            return {}

        return aggregated.to_dict()

    @staticmethod
    def extract_provider_metrics(
        results: List[Dict[str, Any]],
        metric: str = 'success_rate'
    ) -> Dict[str, float]:
        """
        Extract metrics grouped by provider.

        Args:
            results: List of cross-provider results
            metric: Metric to extract

        Returns:
            Dict mapping providers to metric values
        """
        provider_metrics = {}

        for result in results:
            provider = result.get('provider', 'unknown')
            value = result.get(metric, 0)

            if provider not in provider_metrics:
                provider_metrics[provider] = []

            provider_metrics[provider].append(value)

        # Compute means
        return {
            provider: np.mean(values)
            for provider, values in provider_metrics.items()
        }

    @staticmethod
    def prepare_heatmap_data(
        data: Dict[str, Dict[str, float]],
        row_order: Optional[List[str]] = None,
        col_order: Optional[List[str]] = None
    ) -> Tuple[np.ndarray, List[str], List[str]]:
        """
        Prepare data for heatmap visualization.

        Args:
            data: Nested dict {row: {col: value}}
            row_order: Optional ordering for rows
            col_order: Optional ordering for columns

        Returns:
            Tuple of (data_array, row_labels, col_labels)
        """
        df = pd.DataFrame(data).T

        if row_order:
            df = df.reindex(row_order, fill_value=0)

        if col_order:
            df = df.reindex(columns=col_order, fill_value=0)

        return df.values, list(df.index), list(df.columns)

    @staticmethod
    def compute_statistics(values: List[float]) -> Dict[str, float]:
        """
        Compute summary statistics for values.

        Args:
            values: List of numeric values

        Returns:
            Dict with mean, median, std, min, max
        """
        if not values:
            return {
                'mean': 0,
                'median': 0,
                'std': 0,
                'min': 0,
                'max': 0,
                'count': 0
            }

        return {
            'mean': np.mean(values),
            'median': np.median(values),
            'std': np.std(values),
            'min': np.min(values),
            'max': np.max(values),
            'count': len(values)
        }

    @staticmethod
    def prepare_time_series(
        results: List[Dict[str, Any]],
        time_key: str,
        value_key: str
    ) -> Tuple[List, List]:
        """
        Prepare time series data for plotting.

        Args:
            results: List of results with timestamps
            time_key: Key for time values
            value_key: Key for values to plot

        Returns:
            Tuple of (times, values) sorted by time
        """
        df = pd.DataFrame(results)

        if time_key not in df.columns or value_key not in df.columns:
            logger.warning(f"Keys {time_key} or {value_key} not found")
            return [], []

        df = df.sort_values(by=time_key)

        return list(df[time_key]), list(df[value_key])

    @staticmethod
    def format_percentage(value: float, decimals: int = 1) -> str:
        """
        Format value as percentage string.

        Args:
            value: Numeric value (0-1 or 0-100)
            decimals: Number of decimal places

        Returns:
            Formatted percentage string
        """
        if value > 1:
            value = value / 100

        return f"{value * 100:.{decimals}f}%"

    @staticmethod
    def create_comparison_matrix(
        baseline: Dict[str, float],
        experimental: Dict[str, float]
    ) -> pd.DataFrame:
        """
        Create comparison matrix for baseline vs experimental results.

        Args:
            baseline: Baseline metrics
            experimental: Experimental metrics

        Returns:
            DataFrame with comparison data
        """
        metrics = list(set(baseline.keys()) | set(experimental.keys()))

        data = {
            'Metric': metrics,
            'Baseline': [baseline.get(m, 0) for m in metrics],
            'Experimental': [experimental.get(m, 0) for m in metrics]
        }

        df = pd.DataFrame(data)
        df['Difference'] = df['Experimental'] - df['Baseline']
        df['Percent_Change'] = (df['Difference'] / df['Baseline'] * 100).fillna(0)

        return df

    @staticmethod
    def group_by_attack_type(
        results: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group results by attack type.

        Args:
            results: List of attack results

        Returns:
            Dict mapping attack types to result lists
        """
        grouped = {}

        for result in results:
            attack_type = result.get('attack_type', 'unknown')

            if attack_type not in grouped:
                grouped[attack_type] = []

            grouped[attack_type].append(result)

        return grouped

    @staticmethod
    def calculate_position_metrics(
        results: List[Dict[str, Any]]
    ) -> Dict[int, Dict[str, float]]:
        """
        Calculate metrics by position.

        Args:
            results: List of results with position information

        Returns:
            Dict mapping positions to metrics
        """
        position_data = {}

        for result in results:
            position = result.get('position', 0)

            if position not in position_data:
                position_data[position] = []

            # Extract success metric
            success = result.get('success', result.get('success_rate', 0))
            position_data[position].append(success)

        # Compute statistics for each position
        position_metrics = {}
        for position, values in position_data.items():
            position_metrics[position] = {
                'mean': np.mean(values),
                'std': np.std(values),
                'count': len(values)
            }

        return position_metrics
