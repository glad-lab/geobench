# C-SEO Benchmark - NoQuery Complete Guide

> **NoQuery Version of C-SEO Benchmark System** - Citation optimization evaluation framework based on semantic similarity

This document consolidates all usage instructions, providing complete project introduction, quick start guide, and detailed documentation.

---

## 📚 Table of Contents

- [Project Overview](#project-overview)
- [Quick Start](#quick-start)
- [Core Concepts](#core-concepts)
- [Complete Workflow](#complete-workflow)
- [Script Details](#script-details)
- [Configuration Guide](#configuration-guide)
- [Available C-SEO Methods](#available-c-seo-methods)
- [Usage Examples](#usage-examples)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)
- [Project Improvements](#project-improvements)
- [FAQ](#faq)

---

## Project Overview

### What is C-SEO Benchmark?

C-SEO (Citation-based Search Engine Optimization) Benchmark is a benchmarking system for evaluating content optimization methods' performance in generative search engines. The NoQuery version builds document cohorts through **semantic similarity**, without requiring predefined queries, making it more flexible and universal.

### Key Features

- ✅ **No Queries Needed**: Automatically build evaluation scenarios based on semantic similarity
- ✅ **2202 Categories**: Covers a wide range of products and topics
- ✅ **Multiple Optimization Methods**: 10+ C-SEO optimization strategies
- ✅ **Automated Workflow**: One-click to run the complete evaluation pipeline
- ✅ **Statistical Evaluation**: Wilcoxon test ensures result significance
- ✅ **Secure Configuration**: No hardcoded keys, supports multiple configuration methods

### Differences from Legacy Version

| Aspect | Legacy | NoQuery |
|--------|---------|---------|
| Data Format | Query-document pairs | Description text only |
| Evaluation Method | Query-based retrieval | Semantic cohort-based |
| Document Selection | Random per query | Embedding-based sampling |
| Flexibility | Requires predefined queries | Auto-build scenarios |

---

## Quick Start

### 1. Environment Setup

#### Install Dependencies

```bash
# Method 1: Use pip (recommended for development)
pip install -e .

# Method 2: Install with optional dependencies
pip install -e ".[dev,dotenv]"

# Method 3: Install required dependencies only
pip install -r noquery/requirements.txt
```

#### Configure API Keys

**Method A: Environment Variables (Recommended)**
```bash
# Linux/Mac
export OPENAI_API_KEY="sk-your-key-here"

# Windows PowerShell
$env:OPENAI_API_KEY="sk-your-key-here"

# Windows CMD
set OPENAI_API_KEY=sk-your-key-here
```

**Method B: config.json**
```bash
# 1. Copy template
cp config.json.example config.json

# 2. Edit config.json
{
    "OPENAI_API_KEY": "sk-your-actual-key-here",
    "ANTHROPIC_API_KEY": ""
}
```

**Method C: .env File**
```bash
# 1. Copy template
cp noquery/.env.example noquery/.env

# 2. Edit .env file
OPENAI_API_KEY=sk-your-key-here
```

### 2. Run Complete Workflow

```bash
# Run steps 1-4: extract, sample, build cohorts, and improve
python noquery/run_category.py "Apparel" --samples 30 --method Authoritative

# Run steps 5-6: benchmark and evaluation
python noquery/scripts/5_run_benchmark.py --domain apparel --method baseline ...
python noquery/scripts/5_run_benchmark.py --domain apparel --method Authoritative ...
python noquery/scripts/6_eval_wilcoxon.py --domain apparel --method Authoritative
```

---

## Core Concepts

### 1. Semantic Cohorts
- **Definition**: Groups of semantically similar documents
- **Purpose**: Create evaluation contexts without predefined queries
- **Method**: Use embedding models to compute document similarity

### 2. Document Roles
- **Boosted Documents**: Documents to be optimized (30-100 per category)
- **Cohort Members**: Similar documents forming the evaluation context (7-8 per cohort)
- **Baseline**: Original document descriptions
- **Treatment**: Improved document descriptions after C-SEO methods

### 3. Evaluation Metrics
- **Ranking**: Document position in cohort (1-8)
- **Delta Rank**: Change in ranking after optimization
- **P-value**: Statistical significance (Wilcoxon test)
- **Win/Loss/Tie**: Distribution of ranking changes

---

## Complete Workflow

### Step-by-Step Process

```
1. Extract Category      →  2. Sample Documents  →  3. Build Cohorts
        ↓                           ↓                      ↓
  category.json          need_improve.json      cohorts.json + boosted.json
        ↓                                               ↓
4. Improve Texts         →  5. Run Benchmark    →  6. Statistical Evaluation
        ↓                           ↓                      ↓
  improved_{method}.json    results/*.parquet      Wilcoxon test results
```

### Execution Methods

**Method 1: Automated (Recommended)**
```bash
python noquery/run_category.py "Category" --samples 30 --method Authoritative
```

**Method 2: Manual Step-by-Step**
```bash
python noquery/scripts/1_extract_category.py --category "Category"
python noquery/scripts/2_gen_need_improve.py ...
python noquery/scripts/3_build_cohorts.py ...
python noquery/scripts/4_improve_texts.py ...
python noquery/scripts/5_run_benchmark.py ...
python noquery/scripts/6_eval_wilcoxon.py ...
```

---

## Script Details

### Core Scripts (Execution Order)

1. **`1_extract_category.py`** - Extract category data from unified_data.json
2. **`2_gen_need_improve.py`** - Sample documents for improvement
3. **`3_build_cohorts.py`** - Build semantic similarity cohorts
4. **`4_improve_texts.py`** - Apply C-SEO improvement methods
5. **`5_run_benchmark.py`** - Run benchmark evaluation
6. **`6_eval_wilcoxon.py`** - Statistical significance testing

### Utility Scripts

- **`util_fetch_batch_results.py`** - Manually fetch OpenAI batch results
- **`util_clean_unicode.py`** - Clean Unicode characters from JSON files
- **`util_extract_names.py`** - Extract name fields from descriptions
- **`util_remove_description_prefix.py`** - Remove "Description:\n" prefix
- **`util_merge_json_files.py`** - Merge multiple JSON files

For detailed documentation, see [scripts/README.md](scripts/README.md)

---

## Configuration Guide

### API Configuration Priority

1. **Environment Variables** (Highest priority)
   - `OPENAI_API_KEY`
   - `ANTHROPIC_API_KEY`

2. **.env File** (Medium priority)
   - Located in `noquery/.env`
   - Auto-loaded if `python-dotenv` is installed

3. **config.json** (Lowest priority)
   - Located in project root
   - Legacy configuration method

### Configuration File Format

```json
{
    "OPENAI_API_KEY": "sk-proj-...",
    "ANTHROPIC_API_KEY": "sk-ant-...",
    "embedding_model": "text-embedding-3-large",
    "temperature": 0.7,
    "max_tokens": 2000
}
```

---

## Available C-SEO Methods

### Citation-Based Methods
- **`Authoritative`** - Add authoritative citations and references
- **`Statistics`** - Incorporate statistical data and metrics
- **`Citations`** - Add explicit citation sources
- **`Sourcing`** - Include source attribution

### Content Enhancement Methods
- **`ContentImprovement`** - Overall content quality improvement
- **`Fluency`** - Improve text fluency and readability
- **`Unique`** - Emphasize unique features
- **`Technical`** - Add technical details

### Engagement Methods
- **`Controversial`** - Create controversial statements
- **`Counterintuitive`** - Present counterintuitive perspectives
- **`Emotional`** - Add emotional appeals

### Format Methods
- **`LLMstxt`** - Generate LLM-friendly structured format
- **`Instructional`** - Create step-by-step instructions

---

## Usage Examples

### Example 1: Evaluate Authoritative Method on Books Category

```bash
# Step 1-4: Prepare data and improve texts
python noquery/run_category.py "Books" --samples 30 --method Authoritative

# Step 5: Run benchmarks
python noquery/scripts/5_run_benchmark.py \
    --domain books \
    --changed_json noquery/data/datasets/books/books.json \
    --cohorts noquery/data/datasets/books/cohorts.json \
    --boosted noquery/data/datasets/books/boosted.json \
    --method baseline \
    --llm_name gpt-4o-2024-11-20

python noquery/scripts/5_run_benchmark.py \
    --domain books \
    --changed_json noquery/data/datasets/books/books.json \
    --cohorts noquery/data/datasets/books/cohorts.json \
    --boosted noquery/data/datasets/books/boosted.json \
    --improved_json noquery/data/datasets/books/improved_Authoritative.json \
    --method Authoritative \
    --llm_name gpt-4o-2024-11-20

# Step 6: Evaluate
python noquery/scripts/6_eval_wilcoxon.py \
    --domain books \
    --method Authoritative \
    --llm_name gpt-4o-2024-11-20
```

### Example 2: Compare Multiple Methods

```bash
# Run for multiple methods
for method in Authoritative Statistics Citations; do
    python noquery/run_category.py "Retail" --samples 30 --method $method
    python noquery/scripts/5_run_benchmark.py --domain retail --method $method ...
    python noquery/scripts/6_eval_wilcoxon.py --domain retail --method $method ...
done
```

### Example 3: Use Local Embeddings

```bash
python noquery/scripts/3_build_cohorts.py \
    --changed_json noquery/data/datasets/books/books.json \
    --need_improve_json noquery/data/datasets/books/need_improve.json \
    --backend local \
    --model_name bge-large-en-v1.5 \
    --device cuda \
    --out_dir noquery/data/datasets/books
```

---

## Troubleshooting

### Common Issues

#### Issue 1: ModuleNotFoundError
**Symptoms**: `ModuleNotFoundError: No module named 'noquery'`

**Solutions**:
```bash
# Solution 1: Install in development mode
pip install -e .

# Solution 2: Add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Solution 3: Install from requirements
pip install -r noquery/requirements.txt
```

#### Issue 2: API Key Error
**Symptoms**: `openai.AuthenticationError: Error code: 401`

**Solutions**:
1. Check if API key is complete (starts with `sk-proj-` or `sk-`)
2. Verify key is correctly set in environment or config file
3. Check key has sufficient credits

#### Issue 3: Batch Processing Timeout
**Symptoms**: Batch takes too long or hangs

**Solutions**:
```bash
# Check batch status
python noquery/scripts/util_fetch_batch_results.py --batch_id batch_xxx ...

# Increase timeout
python noquery/scripts/4_improve_texts.py ... --max_wait_seconds 7200
```

#### Issue 4: Unicode Characters Warning
**Symptoms**: VS Code shows "ambiguous Unicode characters" warning

**Solution**:
```bash
python noquery/scripts/util_clean_unicode.py \
    noquery/data/changed_json/*.json --clean
```

---

## Best Practices

### 1. Sampling Strategy
- **Small categories** (<100 docs): Sample 30-50 documents
- **Medium categories** (100-500 docs): Sample 50-100 documents
- **Large categories** (>500 docs): Sample 100-200 documents

### 2. Cohort Configuration
- **Cohort size**: 7-8 documents per cohort
- **Cohorts per document**: 2-3 cohorts per boosted document
- **Embedding model**: Use `text-embedding-3-large` for best quality

### 3. Batch Processing
- Submit batches during off-peak hours
- Monitor batch status every 30-60 seconds
- Set appropriate timeout (1-2 hours for 30 documents)

### 4. Result Interpretation
- **P-value < 0.05**: Statistically significant improvement
- **Delta Rank > 0.5**: Meaningful ranking improvement
- **Win rate > 60%**: Strong method effectiveness

---

## Project Improvements

### NoQuery vs Legacy

1. **No Query Dependency**: Builds evaluation scenarios automatically
2. **Semantic Cohorts**: More natural document grouping
3. **Flexible Sampling**: Embedding-based document selection
4. **Better Scalability**: Works with any category without manual query creation

### Recent Enhancements

- ✅ Unicode character cleaning utilities
- ✅ Automated batch result fetching
- ✅ Improved error handling and logging
- ✅ Configuration flexibility (env vars, .env, config.json)
- ✅ Comprehensive documentation

---

## FAQ

### Q1: How long does batch processing take?
**A**: Typically 10 minutes to 2 hours, depending on:
- Number of documents (30 docs ≈ 10-30 minutes)
- OpenAI API load
- Model used (GPT-4 is slower than GPT-3.5)

### Q2: Can I use Claude/Anthropic models?
**A**: Yes, set `ANTHROPIC_API_KEY` and use:
```bash
python noquery/scripts/4_improve_texts.py ... --llm_name claude-3-5-sonnet-20241022
```

### Q3: How to handle large categories?
**A**: Use sampling:
```bash
python noquery/scripts/2_gen_need_improve.py ... --ratio 0.1  # Sample 10%
```

### Q4: Where can I get the data files?
**A**: Large data files are not included in the repository due to size constraints. Options:
1. **HuggingFace**: Download from [parameterlab/c-seo-bench](https://huggingface.co/datasets/parameterlab/c-seo-bench)
2. **Sample Data**: Use included `noquery/data/datasets/apparel/` for testing
3. **Custom Data**: Create your own following the JSON format

See the [main README](../README.md#-data-files) for detailed instructions on obtaining and formatting data files.

### Q5: Where are results stored?
**A**: Results are in:
- **Data**: `noquery/data/datasets/{category}/`
- **Benchmarks**: `experiments/results/{domain}/{method}/{llm}/`

### Q6: How to add custom C-SEO methods?
**A**:
1. Create method class in `noquery/src/methods/`
2. Inherit from `GEOMethod` base class
3. Implement `improve()` method
4. Register in method factory

---

## Directory Structure

```
noquery/
├── README.md                   # This file
├── requirements.txt            # Python dependencies
├── run_category.py            # Main automation script
├── scripts/                   # All scripts
│   ├── 1_extract_category.py
│   ├── 2_gen_need_improve.py
│   ├── 3_build_cohorts.py
│   ├── 4_improve_texts.py
│   ├── 5_run_benchmark.py
│   ├── 6_eval_wilcoxon.py
│   ├── util_*.py             # Utility scripts
│   └── README.md
├── src/                       # Source code
│   ├── llms/                 # LLM interfaces
│   ├── methods/              # C-SEO methods
│   ├── embeddings/           # Embedding providers
│   ├── config/               # Configuration
│   └── utils/                # Utilities
├── data/                      # Data directory
│   ├── datasets/             # Category datasets
│   └── changed_json/         # Source data
└── docs/                      # Documentation
    ├── INDEX.md
    └── archived/             # Archived docs
```

---

## Additional Resources

- **Scripts Reference**: [scripts/README.md](scripts/README.md)
- **Documentation Index**: [docs/INDEX.md](docs/INDEX.md)
- **GitHub Upload Guide**: [../GITHUB_UPLOAD_GUIDE.md](../GITHUB_UPLOAD_GUIDE.md)

---

**Last Updated**: 2025-11-17
