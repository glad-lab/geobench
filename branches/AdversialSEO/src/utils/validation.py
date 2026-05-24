"""
Data validation utilities for benchmark experiments.

Supports:
- Schema validation (required fields)
- Duplicate detection
- Value validation (ranges, types)
- Data quality checks
"""

import logging
from typing import List, Dict, Any, Set
from dataclasses import dataclass, field
from collections import Counter

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of dataset validation."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    stats: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        """String representation of validation result."""
        status = "VALID" if self.is_valid else "INVALID"
        lines = [f"Validation: {status}"]

        if self.errors:
            lines.append(f"\nErrors ({len(self.errors)}):")
            for error in self.errors[:10]:  # Show first 10
                lines.append(f"  - {error}")
            if len(self.errors) > 10:
                lines.append(f"  ... and {len(self.errors) - 10} more")

        if self.warnings:
            lines.append(f"\nWarnings ({len(self.warnings)}):")
            for warning in self.warnings[:10]:  # Show first 10
                lines.append(f"  - {warning}")
            if len(self.warnings) > 10:
                lines.append(f"  ... and {len(self.warnings) - 10} more")

        if self.stats:
            lines.append(f"\nStats:")
            for key, value in self.stats.items():
                lines.append(f"  {key}: {value}")

        return "\n".join(lines)


class DataValidator:
    """Validate dataset integrity."""

    @staticmethod
    def validate_schema(
        products: List[Dict[str, Any]],
        required_fields: List[str]
    ) -> ValidationResult:
        """
        Validate dataset schema.

        Args:
            products: List of products
            required_fields: List of required field names

        Returns:
            ValidationResult with errors and warnings
        """
        errors = []
        warnings = []

        for i, product in enumerate(products):
            for field in required_fields:
                if field not in product:
                    errors.append(f"Product {i} (id={product.get('id', 'unknown')}) missing field: {field}")

            # Check for empty values in required fields
            for field in required_fields:
                if field in product and not product[field]:
                    warnings.append(f"Product {i} has empty {field}")

        stats = {
            "num_products": len(products),
            "required_fields": required_fields,
            "missing_field_count": len(errors),
        }

        logger.info(f"Schema validation: {len(errors)} errors, {len(warnings)} warnings")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            stats=stats
        )

    @staticmethod
    def check_duplicates(
        products: List[Dict[str, Any]],
        id_field: str = "id"
    ) -> ValidationResult:
        """
        Check for duplicate IDs.

        Args:
            products: List of products
            id_field: Field to check for duplicates

        Returns:
            ValidationResult with duplicate information
        """
        errors = []
        warnings = []

        # Count IDs
        id_counts = Counter([p.get(id_field) for p in products])

        # Find duplicates
        duplicates = {id_: count for id_, count in id_counts.items() if count > 1}

        if duplicates:
            for id_, count in duplicates.items():
                errors.append(f"Duplicate {id_field}='{id_}' appears {count} times")

        # Check for missing IDs
        missing_ids = [
            i for i, p in enumerate(products)
            if id_field not in p or not p.get(id_field)
        ]

        if missing_ids:
            warnings.append(f"{len(missing_ids)} products missing {id_field}")

        stats = {
            "num_products": len(products),
            "unique_ids": len(id_counts),
            "duplicate_ids": len(duplicates),
            "missing_ids": len(missing_ids),
        }

        logger.info(
            f"Duplicate check: {len(duplicates)} duplicates, "
            f"{len(missing_ids)} missing IDs"
        )

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            stats=stats
        )

    @staticmethod
    def validate_values(
        products: List[Dict[str, Any]],
        field_constraints: Dict[str, Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        Validate field values (ranges, types).

        Args:
            products: List of products
            field_constraints: Optional constraints dict like:
                {
                    "price": {"min": 0, "max": 10000, "type": float},
                    "rating": {"min": 0, "max": 5, "type": float},
                }

        Returns:
            ValidationResult with value errors
        """
        errors = []
        warnings = []

        # Default constraints
        if field_constraints is None:
            field_constraints = {
                "price": {"min": 0, "max": 100000, "type": (int, float)},
                "rating": {"min": 0, "max": 5, "type": (int, float)},
            }

        for i, product in enumerate(products):
            product_id = product.get("id", f"index_{i}")

            for field, constraints in field_constraints.items():
                if field not in product:
                    continue

                value = product[field]

                # Type check
                if "type" in constraints:
                    expected_type = constraints["type"]
                    if not isinstance(value, expected_type):
                        errors.append(
                            f"Product {product_id}: {field}={value} has wrong type "
                            f"(expected {expected_type})"
                        )

                # Range check
                if "min" in constraints and value < constraints["min"]:
                    errors.append(
                        f"Product {product_id}: {field}={value} below min "
                        f"({constraints['min']})"
                    )

                if "max" in constraints and value > constraints["max"]:
                    errors.append(
                        f"Product {product_id}: {field}={value} above max "
                        f"({constraints['max']})"
                    )

        stats = {
            "num_products": len(products),
            "fields_checked": list(field_constraints.keys()),
            "value_errors": len(errors),
        }

        logger.info(f"Value validation: {len(errors)} errors")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            stats=stats
        )

    @staticmethod
    def validate_all(
        products: List[Dict[str, Any]],
        required_fields: List[str] = None,
        id_field: str = "id",
        field_constraints: Dict[str, Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        Run all validations.

        Args:
            products: List of products
            required_fields: Required fields to check
            id_field: ID field for duplicate checking
            field_constraints: Value constraints

        Returns:
            Combined ValidationResult
        """
        if required_fields is None:
            required_fields = ["id", "name", "description", "price", "rating"]

        # Run all validations
        schema_result = DataValidator.validate_schema(products, required_fields)
        duplicate_result = DataValidator.check_duplicates(products, id_field)
        value_result = DataValidator.validate_values(products, field_constraints)

        # Combine results
        all_errors = schema_result.errors + duplicate_result.errors + value_result.errors
        all_warnings = schema_result.warnings + duplicate_result.warnings + value_result.warnings

        combined_stats = {
            "num_products": len(products),
            "total_errors": len(all_errors),
            "total_warnings": len(all_warnings),
            "schema_errors": len(schema_result.errors),
            "duplicate_errors": len(duplicate_result.errors),
            "value_errors": len(value_result.errors),
        }

        logger.info(
            f"Full validation: {len(all_errors)} errors, {len(all_warnings)} warnings"
        )

        return ValidationResult(
            is_valid=len(all_errors) == 0,
            errors=all_errors,
            warnings=all_warnings,
            stats=combined_stats
        )
