#!/usr/bin/env python3
"""
Export product data to multiple formats.

Generates:
    - Individual product JSONs (data/products/*.json)
    - Category-grouped JSONs (data/categories/*.json)
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.data_export import export_data_formats


def main():
    """Export product data to all formats."""
    source_file = project_root / "data" / "products_master.json"
    output_dir = project_root / "data"

    print(f"Exporting data from: {source_file}")
    print(f"Output directory: {output_dir}")
    print()

    results = export_data_formats(
        source_file=str(source_file),
        output_dir=str(output_dir),
        formats=["all"]
    )

    print("\n✅ Export Summary:")
    print(f"   - Individual products: {results['products']} files")
    print(f"   - Category groups: {results['categories']} files")
    print(f"\nData exported to:")
    print(f"   - {output_dir / 'products'}/ (individual product JSONs)")
    print(f"   - {output_dir / 'categories'}/ (category-grouped JSONs)")


if __name__ == "__main__":
    main()
