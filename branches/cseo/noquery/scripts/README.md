# C-SEO Benchmark Scripts Documentation

This directory contains all scripts for the C-SEO Benchmark system. Scripts are renamed according to execution order for better understanding of the evaluation workflow.

## 📋 Core Workflow Scripts (in execution order)

### 1️⃣ `1_extract_category.py` - Extract Category Data
**Function**: Extract all documents of a specified category from unified_data.json

**Usage Examples**:
```bash
# List all available categories
python noquery/scripts/1_extract_category.py --list

# Extract a specific category
python noquery/scripts/1_extract_category.py --category "Apparel"
```

**Output**: `noquery/data/datasets/{category}/{category}.json`

---

### 2️⃣ `2_gen_need_improve.py` - Sample Documents for Improvement
**Function**: Randomly sample a specified number of documents from category data for subsequent improvement

**Usage Examples**:
```bash
# Sample fixed number
python noquery/scripts/2_gen_need_improve.py \
    --changed_json noquery/data/datasets/apparel/apparel.json \
    --out_json noquery/data/datasets/apparel/need_improve.json \
    --strategy random \
    --num 30 \
    --seed 42

# Sample by ratio
python noquery/scripts/2_gen_need_improve.py \
    --changed_json noquery/data/datasets/apparel/apparel.json \
    --out_json noquery/data/datasets/apparel/need_improve.json \
    --strategy random \
    --ratio 0.7 \
    --seed 42
```

**Output**: `noquery/data/datasets/{category}/need_improve.json`

---

### 3️⃣ `3_build_cohorts.py` - Build Semantic Similarity Cohorts
**Function**: Use embedding models to compute semantic similarity between documents and build document cohorts

**Usage Examples**:
```bash
# Use OpenAI embeddings
python noquery/scripts/3_build_cohorts.py \
    --changed_json noquery/data/datasets/apparel/apparel.json \
    --need_improve_json noquery/data/datasets/apparel/need_improve.json \
    --backend openai \
    --model_name text-embedding-3-large \
    --out_dir noquery/data/datasets/apparel \
    --cohort_size 8 \
    --cohorts_per_doc 2

# Use local embedding models
python noquery/scripts/3_build_cohorts.py \
    --changed_json noquery/data/datasets/apparel/apparel.json \
    --need_improve_json noquery/data/datasets/apparel/need_improve.json \
    --backend local \
    --model_name bge-large-en-v1.5 \
    --device cpu \
    --out_dir noquery/data/datasets/apparel
```

**Outputs**:
- `noquery/data/datasets/{category}/cohorts.json`
- `noquery/data/datasets/{category}/boosted.json`

---

### 4️⃣ `4_improve_texts.py` - Apply Improvement Methods
**Function**: Improve document descriptions using specified C-SEO methods (e.g., Authoritative, Statistics) and submit to OpenAI Batch API

**Usage Example**:
```bash
python noquery/scripts/4_improve_texts.py \
    --changed_json noquery/data/datasets/apparel/apparel.json \
    --need_improve_json noquery/data/datasets/apparel/need_improve.json \
    --out_json noquery/data/datasets/apparel/improved_Authoritative.json \
    --method Authoritative \
    --llm_name gpt-4o-2024-11-20 \
    --config config.json \
    --max_wait_seconds 3600 \
    --poll_interval 30
```

**Available Methods**:
- `Authoritative` - Add authoritative citations
- `Statistics` - Add statistical data
- `Citations` - Add citation sources
- `Fluency` - Improve fluency
- `ContentImprovement` - Overall content improvement
- `LLMstxt` - Generate LLM-friendly format
- And more...

**Output**: `noquery/data/datasets/{category}/improved_{method}.json`

---

### 5️⃣ `5_run_benchmark.py` - Run Benchmark Evaluation
**Function**: Run benchmark tests to evaluate document ranking performance in language engines

**Usage Examples**:
```bash
# Run baseline test (original text)
python noquery/scripts/5_run_benchmark.py \
    --domain apparel \
    --changed_json noquery/data/datasets/apparel/apparel.json \
    --cohorts noquery/data/datasets/apparel/cohorts.json \
    --boosted noquery/data/datasets/apparel/boosted.json \
    --method baseline \
    --llm_name gpt-4o-2024-11-20

# Run improved method test
python noquery/scripts/5_run_benchmark.py \
    --domain apparel \
    --changed_json noquery/data/datasets/apparel/apparel.json \
    --cohorts noquery/data/datasets/apparel/cohorts.json \
    --boosted noquery/data/datasets/apparel/boosted.json \
    --improved_json noquery/data/datasets/apparel/improved_Authoritative.json \
    --method Authoritative \
    --llm_name gpt-4o-2024-11-20
```

**Output**: `experiments/results/{domain}/{method}/{llm_name}/AdoptionMode.{mode}/responses.parquet`

---

### 6️⃣ `6_eval_wilcoxon.py` - Statistical Evaluation
**Function**: Use Wilcoxon signed-rank test to compare effectiveness of baseline and improved methods

**Usage Example**:
```bash
python noquery/scripts/6_eval_wilcoxon.py \
    --domain apparel \
    --method Authoritative \
    --llm_name gpt-4o-2024-11-20
```

**Output Example**:
```json
{
    "statistic": 441.0,
    "pvalue": 2.82e-06,
    "Delta Rank": (0.7, 1.12),
    "count": 60
}
```

**Result Interpretation**:
- `pvalue < 0.05`: Improvement is statistically significant
- `Delta Rank > 0`: Average ranking improvement
- `count`: Number of comparison samples

---

## 🔧 Utility Scripts

### `util_fetch_batch_results.py` - Manually Fetch Batch Results
**Function**: Manually fetch results after batch processing is complete (`4_improve_texts.py` already includes automatic waiting)

**Usage Example**:
```bash
python noquery/scripts/util_fetch_batch_results.py \
    --batch_id batch_xxx \
    --changed_json noquery/data/datasets/apparel/apparel.json \
    --need_improve_json noquery/data/datasets/apparel/need_improve.json \
    --out_json noquery/data/datasets/apparel/improved_Authoritative.json \
    --method Authoritative \
    --llm_name gpt-4o-2024-11-20 \
    --config config.json
```

---

### `util_run_pipeline.py` - Legacy Pipeline Script
**Function**: Complete workflow script from earlier version (may be deprecated)

⚠️ Recommended to use `run_category.py` in the root directory instead

---

### `util_clean_unicode.py` - Clean Unicode Characters
**Function**: Detect and clean ambiguous Unicode characters from JSON files

---

### `util_extract_names.py` - Extract Names from Descriptions
**Function**: Extract name fields from description content in JSON files

---

### `util_remove_description_prefix.py` - Remove Description Prefix
**Function**: Remove "Description:\n" prefix from description fields

---

### `util_merge_json_files.py` - Merge JSON Files
**Function**: Merge multiple JSON files into a single unified file

---

### `util_run_category_benchmark.bat` - Windows Batch File
**Function**: Windows batch script shortcut

---

## 🚀 Complete Workflow Examples

### Method 1: Using Automation Script (Recommended)

```bash
# One command to run steps 1-4
python noquery/run_category.py "Apparel" --samples 30 --method Authoritative

# After batch processing completes, run benchmark tests
python noquery/scripts/5_run_benchmark.py --domain apparel ... --method baseline
python noquery/scripts/5_run_benchmark.py --domain apparel ... --method Authoritative

# Evaluate results
python noquery/scripts/6_eval_wilcoxon.py --domain apparel --method Authoritative --llm_name gpt-4o-2024-11-20
```

### Method 2: Manual Step-by-Step Execution

```bash
# Step 1: Extract category
python noquery/scripts/1_extract_category.py --category "Apparel"

# Step 2: Sample documents
python noquery/scripts/2_gen_need_improve.py \
    --changed_json noquery/data/datasets/apparel/apparel.json \
    --out_json noquery/data/datasets/apparel/need_improve.json \
    --num 30

# Step 3: Build cohorts
python noquery/scripts/3_build_cohorts.py \
    --changed_json noquery/data/datasets/apparel/apparel.json \
    --need_improve_json noquery/data/datasets/apparel/need_improve.json \
    --out_dir noquery/data/datasets/apparel

# Step 4: Improve texts
python noquery/scripts/4_improve_texts.py \
    --changed_json noquery/data/datasets/apparel/apparel.json \
    --need_improve_json noquery/data/datasets/apparel/need_improve.json \
    --out_json noquery/data/datasets/apparel/improved_Authoritative.json \
    --method Authoritative

# Step 5a: Baseline benchmark
python noquery/scripts/5_run_benchmark.py \
    --domain apparel \
    --method baseline \
    ...

# Step 5b: Method benchmark
python noquery/scripts/5_run_benchmark.py \
    --domain apparel \
    --method Authoritative \
    ...

# Step 6: Evaluation
python noquery/scripts/6_eval_wilcoxon.py \
    --domain apparel \
    --method Authoritative
```

---

## 📁 Directory Structure

```
noquery/
├── scripts/                              # This directory
│   ├── 1_extract_category.py            # Step 1: Extract category
│   ├── 2_gen_need_improve.py            # Step 2: Sample documents
│   ├── 3_build_cohorts.py               # Step 3: Build cohorts
│   ├── 4_improve_texts.py               # Step 4: Improve texts
│   ├── 5_run_benchmark.py               # Step 5: Benchmark test
│   ├── 6_eval_wilcoxon.py               # Step 6: Statistical evaluation
│   ├── util_fetch_batch_results.py      # Utility: Fetch batch results
│   ├── util_clean_unicode.py            # Utility: Clean Unicode
│   ├── util_extract_names.py            # Utility: Extract names
│   ├── util_remove_description_prefix.py # Utility: Remove prefix
│   ├── util_merge_json_files.py         # Utility: Merge files
│   ├── util_run_pipeline.py             # Utility: Legacy pipeline
│   └── README.md                         # This file
├── run_category.py                       # Automation script (steps 1-4)
└── data/
    └── datasets/
        └── {category}/
            ├── {category}.json           # Step 1 output
            ├── need_improve.json         # Step 2 output
            ├── cohorts.json              # Step 3 output
            ├── boosted.json              # Step 3 output
            └── improved_{method}.json    # Step 4 output
```

---

## ⚙️ Configuration File

Create `config.json` in the project root directory:

```json
{
    "OPENAI_API_KEY": "sk-your-key-here",
    "ANTHROPIC_API_KEY": ""
}
```

---

## 📝 Important Notes

1. **API Keys**: Ensure you have configured a complete OpenAI API key in `config.json`
2. **Batch Processing Wait**: After submitting batch in step 4, need to wait (typically 10 minutes - 2 hours)
3. **Disk Space**: Ensure sufficient disk space to store results
4. **Python Environment**: Use conda environment `cseo1` or other properly configured environment

---

## 🆘 Troubleshooting

### Issue: ModuleNotFoundError
**Solution**: Check if all dependency packages are properly installed
```bash
pip install -r requirements.txt
```

### Issue: API Key Error
**Solution**: Check if the API key in `config.json` is complete and valid

### Issue: Batch Processing Timeout
**Solution**: Use `util_fetch_batch_results.py` to manually fetch results

---

**Last Updated**: 2025-11-17
