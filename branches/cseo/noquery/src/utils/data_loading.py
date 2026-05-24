"""
Data loading utilities for the noquery project.

This module provides unified functions for loading and normalizing JSON data
from various formats used in the changed_json and need_improve files.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union

logger = logging.getLogger(__name__)


def read_json(path: str) -> Any:
    """
    Read and parse a JSON file.

    Args:
        path: Path to the JSON file

    Returns:
        Parsed JSON object (dict, list, etc.)

    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"JSON file not found: {path}")

    return json.loads(file_path.read_text(encoding="utf-8"))


def load_changed_json(
    changed_json_path: str,
    return_as_dict: bool = False
) -> Union[List[Tuple[str, str]], Dict[str, str]]:
    """
    Load and normalize changed_json format.

    Supports multiple formats:
    - Top-level array: [{"id": 1, "description": "..."}, ...]
    - Single key object: {"books": [{"id": 1, "description": "..."}, ...]}
    - Auto-detects single array field in dict

    Args:
        changed_json_path: Path to the changed_json file
        return_as_dict: If True, return {doc_id: description}.
                       If False, return [(doc_id, description), ...]

    Returns:
        Either list of (doc_id, description) tuples or dict mapping doc_id to description

    Raises:
        ValueError: If the JSON structure is not supported
        FileNotFoundError: If the file doesn't exist
    """
    obj = read_json(changed_json_path)

    # Normalize to list
    if isinstance(obj, list):
        data = obj
    elif isinstance(obj, dict):
        # Find all keys with list values
        arr_keys = [k for k, v in obj.items() if isinstance(v, list)]
        if len(arr_keys) == 1:
            data = obj[arr_keys[0]]
        elif "books" in obj and isinstance(obj["books"], list):
            # Legacy fallback
            data = obj["books"]
        else:
            raise ValueError(
                f"Unsupported changed_json structure: expected a list or a single array field. "
                f"Found keys: {list(obj.keys())}"
            )
    else:
        raise ValueError(
            f"Unsupported changed_json structure: expected list or dict, got {type(obj).__name__}"
        )

    # Extract records
    records = []
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            continue

        # Get description field
        desc = item.get("description")
        if not isinstance(desc, str):
            continue

        # Get or generate ID
        did = item.get("id", i)
        try:
            # Try to convert to int first, then to string for consistency
            did_int = int(did)
            did_str = str(did_int)
        except (ValueError, TypeError):
            # If ID is not numeric, use index
            did_str = str(i)

        records.append((did_str, desc))

    if return_as_dict:
        return dict(records)
    return records


def load_need_improve(need_improve_path: str) -> List[str]:
    """
    Load document IDs from need_improve.json.

    Supports multiple formats:
    - {"doc_ids": [1, 2, 3]}
    - [1, 2, 3]

    Args:
        need_improve_path: Path to the need_improve.json file

    Returns:
        List of document IDs (as strings)

    Raises:
        ValueError: If the JSON structure is not supported
        FileNotFoundError: If the file doesn't exist
    """
    obj = read_json(need_improve_path)

    if isinstance(obj, dict) and "doc_ids" in obj:
        doc_ids = obj["doc_ids"]
    elif isinstance(obj, list):
        doc_ids = obj
    else:
        raise ValueError(
            f"Unsupported need_improve format: expected dict with 'doc_ids' key or list, "
            f"got {type(obj).__name__}"
        )

    # Convert all IDs to strings for consistency
    return [str(x) for x in doc_ids]


def load_changed_json_with_ids(
    changed_json_path: str
) -> List[Tuple[int, str]]:
    """
    Load changed_json and return records with integer IDs.

    This is a specialized version used by gen_need_improve.py that preserves
    integer IDs for sampling purposes.

    Args:
        changed_json_path: Path to the changed_json file

    Returns:
        List of (doc_id_int, description) tuples

    Raises:
        ValueError: If the JSON structure is not supported
    """
    obj = read_json(changed_json_path)

    if isinstance(obj, list):
        data = obj
    elif isinstance(obj, dict):
        arr_keys = [k for k, v in obj.items() if isinstance(v, list)]
        if len(arr_keys) == 1:
            data = obj[arr_keys[0]]
        elif "books" in obj and isinstance(obj["books"], list):
            data = obj["books"]
        else:
            raise ValueError(
                "Unsupported changed_json structure: expected a list or a single array field."
            )
    else:
        raise ValueError("Unsupported changed_json structure: expected list or dict.")

    out: List[Tuple[int, str]] = []
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            continue
        desc = item.get("description")
        if not isinstance(desc, str):
            continue
        did = item.get("id", i)
        try:
            did_int = int(did)
        except (ValueError, TypeError):
            # If ID is not numeric, use index
            did_int = i
        out.append((did_int, desc))

    return out


def list_categories(unified_data_path: str) -> List[str]:
    """
    List all available categories in unified_data.json.

    Args:
        unified_data_path: Path to the unified_data.json file

    Returns:
        List of category names

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file structure is invalid
    """
    obj = read_json(unified_data_path)

    if not isinstance(obj, dict):
        raise ValueError(
            f"Invalid unified_data format: expected dict at top level, got {type(obj).__name__}"
        )

    categories = [k for k, v in obj.items() if isinstance(v, list)]

    if not categories:
        raise ValueError("No valid categories found in unified_data.json")

    logger.info(f"Found {len(categories)} categories: {', '.join(categories[:5])}{'...' if len(categories) > 5 else ''}")
    return categories


def extract_category(
    unified_data_path: str,
    category: str,
    output_path: str,
    add_ids: bool = True
) -> int:
    """
    Extract a specific category from unified_data.json and save to a separate file.

    Args:
        unified_data_path: Path to the unified_data.json file
        category: Category name to extract
        output_path: Path to save the extracted category data
        add_ids: If True, add sequential IDs to items that don't have them

    Returns:
        Number of documents extracted

    Raises:
        FileNotFoundError: If the unified_data file doesn't exist
        ValueError: If the category doesn't exist or is invalid
    """
    obj = read_json(unified_data_path)

    if not isinstance(obj, dict):
        raise ValueError(
            f"Invalid unified_data format: expected dict at top level, got {type(obj).__name__}"
        )

    if category not in obj:
        available = list(obj.keys())
        raise ValueError(
            f"Category '{category}' not found. Available categories: {', '.join(available[:10])}"
            f"{'...' if len(available) > 10 else ''}"
        )

    data = obj[category]

    if not isinstance(data, list):
        raise ValueError(
            f"Invalid data for category '{category}': expected list, got {type(data).__name__}"
        )

    # Add IDs if requested
    if add_ids:
        for i, item in enumerate(data):
            if isinstance(item, dict) and "id" not in item:
                item["id"] = i

    # Create output structure
    output_obj = {category: data}

    # Ensure output directory exists
    output_path_obj = Path(output_path)
    output_path_obj.parent.mkdir(parents=True, exist_ok=True)

    # Write to file
    output_path_obj.write_text(
        json.dumps(output_obj, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    logger.info(f"Extracted {len(data)} documents from category '{category}' to {output_path}")
    return len(data)
