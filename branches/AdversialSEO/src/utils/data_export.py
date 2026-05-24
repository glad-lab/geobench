"""
Data export utilities for generating multiple format variants.

This module supports exporting the unified product catalog into
different formats:
    - Individual product JSONs (one file per product)
    - Category-grouped JSONs (one file per category)
    - Unified master JSON (single file with all data)
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import re

logger = logging.getLogger(__name__)


class DataExporter:
    """
    Export product data in multiple formats.

    Supports three export formats:
        1. Individual products: One JSON file per product
        2. Category groups: One JSON file per category
        3. Unified master: Single JSON with all data (already exists)

    Example:
        >>> exporter = DataExporter("data/products_master.json")
        >>> exporter.export_all("data")
    """

    def __init__(self, source_file: str):
        """
        Initialize exporter with source data file.

        Args:
            source_file: Path to unified products JSON file
        """
        self.source_file = Path(source_file)
        self.data = self._load_source_data()

    def _load_source_data(self) -> Dict[str, Any]:
        """Load and validate source data."""
        if not self.source_file.exists():
            raise FileNotFoundError(f"Source file not found: {self.source_file}")

        with open(self.source_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Validate data structure
        if not isinstance(data, dict):
            raise ValueError("Source data must be a dictionary")

        if "categories" not in data and not any(isinstance(v, list) for v in data.values()):
            raise ValueError("Invalid data structure: no categories or product lists found")

        return data

    def export_individual_products(self, output_dir: str) -> int:
        """
        Export each product to an individual JSON file.

        Creates one JSON file per product with naming pattern:
            {category}_{product_name_slug}.json

        Args:
            output_dir: Directory to write product JSONs

        Returns:
            Number of products exported

        Example:
            >>> exporter.export_individual_products("data/products")
            60  # Returns count of exported products
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        count = 0

        # Handle both unified and legacy formats
        categories_data = self._get_categories_data()

        for category, products in categories_data.items():
            for product in products:
                # Generate filename from category and product name
                filename = self._generate_product_filename(category, product.get("name", "unknown"))
                filepath = output_path / filename

                # Write individual product JSON
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(product, f, indent=2, ensure_ascii=False)

                count += 1
                logger.debug(f"Exported product: {filepath}")

        logger.info(f"Exported {count} individual product files to {output_path}")
        return count

    def export_category_groups(self, output_dir: str) -> int:
        """
        Export products grouped by category to separate files.

        Creates one JSON file per category with naming pattern:
            {category_slug}.json

        Args:
            output_dir: Directory to write category JSONs

        Returns:
            Number of categories exported

        Example:
            >>> exporter.export_category_groups("data/categories")
            7  # Returns count of categories
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        count = 0

        # Handle both unified and legacy formats
        categories_data = self._get_categories_data()

        for category, products in categories_data.items():
            # Generate filename from category name
            filename = self._slugify(category) + ".json"
            filepath = output_path / filename

            # Write category JSON
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(products, f, indent=2, ensure_ascii=False)

            count += 1
            logger.info(f"Exported category: {filepath} ({len(products)} products)")

        logger.info(f"Exported {count} category files to {output_path}")
        return count

    def export_all(self, base_output_dir: str) -> Dict[str, int]:
        """
        Export to all three formats.

        Creates directory structure:
            base_output_dir/
                products/       (individual product JSONs)
                categories/     (category-grouped JSONs)

        Args:
            base_output_dir: Base directory for all exports

        Returns:
            Dictionary with export counts for each format

        Example:
            >>> exporter.export_all("data")
            {'products': 60, 'categories': 7}
        """
        base_path = Path(base_output_dir)
        base_path.mkdir(parents=True, exist_ok=True)

        # Export individual products
        products_count = self.export_individual_products(str(base_path / "products"))

        # Export category groups
        categories_count = self.export_category_groups(str(base_path / "categories"))

        results = {
            "products": products_count,
            "categories": categories_count
        }

        logger.info(f"Export complete: {results}")
        return results

    def _get_categories_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract categories data from source file.

        Handles both unified format (with metadata and categories)
        and legacy format (direct category dictionary).

        Returns:
            Dictionary mapping category names to product lists
        """
        data = self.data

        # Check for unified format
        if "categories" in data:
            categories_data = {}
            for category, category_info in data["categories"].items():
                if isinstance(category_info, dict) and "items" in category_info:
                    categories_data[category] = category_info["items"]
                else:
                    # Legacy format within categories
                    categories_data[category] = category_info
            return categories_data

        # Legacy format: direct category dictionary
        return {k: v for k, v in data.items() if isinstance(v, list)}

    def _generate_product_filename(self, category: str, product_name: str) -> str:
        """
        Generate filename for individual product.

        Args:
            category: Product category
            product_name: Product name

        Returns:
            Filename in format: {category}_{product_name}.json

        Example:
            >>> exporter._generate_product_filename("Cameras", "PhotoMaster Z1 Camera")
            'camera_photomaster_z1_camera.json'
        """
        category_slug = self._slugify(category)
        product_slug = self._slugify(product_name)

        # Limit length to avoid filesystem issues
        max_length = 200
        if len(product_slug) > max_length:
            product_slug = product_slug[:max_length]

        return f"{category_slug}_{product_slug}.json"

    def _slugify(self, text: str) -> str:
        """
        Convert text to filesystem-safe slug.

        Args:
            text: Input text

        Returns:
            Slugified text (lowercase, alphanumeric with hyphens)

        Example:
            >>> exporter._slugify("Books & Media")
            'books-media'
        """
        # Convert to lowercase
        text = text.lower()

        # Replace spaces and special chars with hyphens
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[\s_]+', '-', text)

        # Remove leading/trailing hyphens
        text = text.strip('-')

        return text


def export_data_formats(
    source_file: str,
    output_dir: str,
    formats: Optional[List[str]] = None
) -> Dict[str, int]:
    """
    Convenience function to export data in specified formats.

    Args:
        source_file: Path to source JSON file
        output_dir: Base output directory
        formats: List of formats to export (default: all)
                 Options: 'products', 'categories', 'all'

    Returns:
        Dictionary with export counts

    Example:
        >>> export_data_formats(
        ...     "data/products_master.json",
        ...     "data",
        ...     formats=["products", "categories"]
        ... )
        {'products': 60, 'categories': 7}
    """
    if formats is None:
        formats = ["all"]

    exporter = DataExporter(source_file)
    results = {}

    if "all" in formats:
        return exporter.export_all(output_dir)

    if "products" in formats:
        results["products"] = exporter.export_individual_products(
            str(Path(output_dir) / "products")
        )

    if "categories" in formats:
        results["categories"] = exporter.export_category_groups(
            str(Path(output_dir) / "categories")
        )

    return results
