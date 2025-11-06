#!/bin/bash
# Migration script for AdversarialSEO dataset to geobench
# Usage: ./migrate_to_geobench.sh /path/to/geobench

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if geobench path provided
if [ -z "$1" ]; then
    echo -e "${YELLOW}Usage: $0 /path/to/geobench${NC}"
    echo ""
    echo "Example: $0 ~/Documents/FORTIS/geobench"
    exit 1
fi

GEOBENCH_PATH="$1"
DATASET_DIR="$GEOBENCH_PATH/Datasets/AdversarialSEO"

# Verify geobench directory exists
if [ ! -d "$GEOBENCH_PATH" ]; then
    echo -e "${YELLOW}Error: Geobench directory not found: $GEOBENCH_PATH${NC}"
    exit 1
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}AdversarialSEO Dataset Migration${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "Source: $(pwd)"
echo -e "Target: $DATASET_DIR"
echo ""

# Create directory structure
echo -e "${GREEN}Creating directory structure...${NC}"
mkdir -p "$DATASET_DIR"/{data,utils,tools,docs}

# Copy core dataset files
echo -e "${GREEN}Copying core dataset files...${NC}"
cp data/products_master.json "$DATASET_DIR/data/"
cp data/noise_documents.json "$DATASET_DIR/data/"
echo -e "  ✓ products_master.json (60 products, 7 categories)"
echo -e "  ✓ noise_documents.json (20 noise documents)"

# Copy utilities
echo -e "${GREEN}Copying benchmark utilities...${NC}"
cp src/benchmark_utils.py "$DATASET_DIR/utils/"
echo -e "  ✓ benchmark_utils.py"

# Copy tools
echo -e "${GREEN}Copying migration and validation tools...${NC}"
cp scripts/migrate_to_unified_format.py "$DATASET_DIR/tools/"
cp scripts/test_unified_format.py "$DATASET_DIR/tools/"
echo -e "  ✓ migrate_to_unified_format.py"
echo -e "  ✓ test_unified_format.py"

# Copy documentation
echo -e "${GREEN}Copying documentation...${NC}"
cp MIGRATION_SUMMARY.md "$DATASET_DIR/docs/"
cp GEOBENCH_MIGRATION_GUIDE.md "$DATASET_DIR/docs/"
echo -e "  ✓ MIGRATION_SUMMARY.md"
echo -e "  ✓ GEOBENCH_MIGRATION_GUIDE.md"

# Create dataset_info.json
echo -e "${GREEN}Creating dataset_info.json...${NC}"
cat > "$DATASET_DIR/dataset_info.json" << 'EOF'
{
  "name": "AdversarialSEO",
  "version": "1.0.0",
  "description": "Adversarial SEO dataset with unified category-based structure for GEO methodology benchmarking",
  "format_version": "unified_v1",
  "total_products": 60,
  "total_categories": 7,
  "category_distribution": {
    "Books & Media": 10,
    "Computing Hardware": 15,
    "Home Furniture": 10,
    "Kitchen Appliances": 10,
    "Cameras": 8,
    "Lenses": 4,
    "Accessories": 3
  },
  "benchmark_angles": [
    "product_count_variation",
    "product_ordering",
    "ground_truth_availability",
    "anomaly_injection",
    "noise_effects",
    "data_cropping",
    "irrelevant_features",
    "performance_metrics",
    "multi_dataset_replication",
    "llm_efficacy_comparison"
  ],
  "source": "Fictional products created for adversarial SEO research",
  "paper": "Nestaas et al., 2024 - Adversarial Search Engine Optimization for Large Language Models",
  "license": "Research Use Only",
  "created_by": "FORTIS Lab",
  "created_date": "2025-10-29",
  "files": {
    "products": "data/products_master.json",
    "noise": "data/noise_documents.json",
    "utilities": "utils/benchmark_utils.py",
    "migration_tool": "tools/migrate_to_unified_format.py",
    "validation_tool": "tools/test_unified_format.py"
  }
}
EOF
echo -e "  ✓ dataset_info.json"

# Create README.md
echo -e "${GREEN}Creating README.md...${NC}"
cat > "$DATASET_DIR/README.md" << 'EOF'
# AdversarialSEO Dataset

Unified category-based dataset for adversarial SEO research and GEO methodology benchmarking.

## Overview

- **Products**: 60 fictional products across 7 categories
- **Format**: Unified hierarchical category-based structure
- **Noise Documents**: 20 supporting documents for realistic context
- **Benchmark Support**: 10 benchmark angles for comprehensive evaluation

## Structure

```
AdversarialSEO/
├── data/
│   ├── products_master.json       # 60 products, 7 categories
│   └── noise_documents.json       # 20 noise documents
├── utils/
│   └── benchmark_utils.py         # Benchmark utilities
├── tools/
│   ├── migrate_to_unified_format.py
│   └── test_unified_format.py
├── docs/
│   ├── MIGRATION_SUMMARY.md
│   └── GEOBENCH_MIGRATION_GUIDE.md
├── dataset_info.json
└── README.md (this file)
```

## Quick Start

```python
import sys
sys.path.append("Datasets/AdversarialSEO/utils")
from benchmark_utils import UnifiedDataLoader

# Load dataset
loader = UnifiedDataLoader("Datasets/AdversarialSEO/data/products_master.json")

# Get all products
products = loader.get_all_products()
print(f"Loaded {len(products)} products")

# Sample by category
cameras = loader.get_category_products("Cameras")
print(f"Found {len(cameras)} cameras")

# Sample for experiments
sample = loader.sample_products(10, strategy="stratified", seed=42)
```

## Categories

- **Books & Media**: 10 products
- **Computing Hardware**: 15 products
- **Home Furniture**: 10 products
- **Kitchen Appliances**: 10 products
- **Cameras**: 8 products
- **Lenses**: 4 products
- **Accessories**: 3 products

## Benchmark Angles Supported

1. Product count variation (2-60 products)
2. Product ordering (random, by rating, alternating categories, etc.)
3. Ground truth availability (full, partial, none)
4. Anomaly injection (price outliers, rating inconsistencies, etc.)
5. Noise effects (description, price, rating noise)
6. Data cropping (random, stratified, balanced)
7. Irrelevant feature injection
8. Performance metrics (execution time, memory usage)
9. Multi-dataset replication
10. LLM efficacy comparison

## Verification

```bash
# Test dataset loading
cd Datasets/AdversarialSEO
python3 tools/test_unified_format.py
```

Expected output:
```
✅ Loaded 60 products
✅ Product count matches expected: 60
✅ No duplicate product IDs
✅ All products have required fields
```

## Citation

If you use this dataset in your research, please cite:

```bibtex
@misc{adversarialseo2024,
  title={AdversarialSEO Dataset for GEO Methodology Benchmarking},
  author={FORTIS Lab},
  year={2024},
  note={Unified category-based structure for adversarial SEO research}
}
```

## Original Research

Based on the paper:
> Nestaas et al., 2024. "Adversarial Search Engine Optimization for Large Language Models"

## License

Research Use Only

## Documentation

See `docs/` directory for:
- Migration history and verification results
- Complete migration guide
- Benchmark angle documentation
- Usage examples
EOF
echo -e "  ✓ README.md"

# Verification
echo ""
echo -e "${GREEN}Running verification tests...${NC}"
cd "$DATASET_DIR"
python3 tools/test_unified_format.py

# Summary
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Migration Complete!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${GREEN}✅ Dataset migrated successfully${NC}"
echo ""
echo -e "Location: $DATASET_DIR"
echo ""
echo -e "Files migrated:"
echo -e "  • products_master.json (60 products, 7 categories)"
echo -e "  • noise_documents.json (20 documents)"
echo -e "  • benchmark_utils.py (comprehensive utilities)"
echo -e "  • Migration and validation tools"
echo -e "  • Complete documentation"
echo ""
echo -e "Next steps:"
echo -e "  1. Update geobench dataset registry (if applicable)"
echo -e "  2. Test dataset loading in geobench framework"
echo -e "  3. Run benchmark experiments"
echo ""
