# C-SEO Bench

A comprehensive benchmark system for evaluating Citation-based Search Engine Optimization (C-SEO) methods.

## 🎯 Project Overview

C-SEO Bench is a research framework designed to evaluate and compare different methods for improving document visibility in citation-based search systems. The project includes two main implementations:

1. **NoQuery System** - An improved implementation that uses semantic similarity without predefined queries
2. **Legacy System** - Original implementation with query-based evaluation

## 📁 Project Structure

```
c-seo-bench/
├── noquery/                           # Main NoQuery System (Recommended)
│   ├── README.md                     # Complete NoQuery documentation
│   ├── requirements.txt              # Python dependencies
│   ├── run_category.py              # Main orchestration script
│   │
│   ├── scripts/                     # Executable Scripts
│   │   ├── README.md               # Scripts documentation
│   │   ├── 1_extract_category.py   # Extract category from data
│   │   ├── 2_gen_need_improve.py   # Sample documents
│   │   ├── 3_build_cohorts.py      # Build semantic cohorts
│   │   ├── 4_improve_texts.py      # Apply C-SEO methods
│   │   ├── 5_run_benchmark.py      # Run benchmarks
│   │   ├── 6_eval_wilcoxon.py      # Statistical evaluation
│   │   └── util_*.py               # Utility scripts
│   │
│   ├── src/                         # Core Source Code
│   │   ├── llms/                   # LLM interfaces (OpenAI, Anthropic)
│   │   ├── methods/                # C-SEO method implementations
│   │   ├── embeddings/             # Embedding providers
│   │   ├── config/                 # Configuration management
│   │   └── utils/                  # Utility functions
│   │
│   └── data/                        # Data Directory
│       ├── changed_json/           # Source data files (not in repo)
│       │   ├── books.json         # Download from HuggingFace
│       │   ├── retail.json        # Download from HuggingFace
│       │   └── ...                # Other categories
│       └── datasets/               # Generated datasets
│           └── apparel/           # Sample data (included)
│
├── experiments/                     # Experiment Results (Generated)
│   ├── results/                    # Completed experiments
│   │   └── {domain}/{method}/{model}/
│   └── running/                    # In-progress experiments
│
├── README.md                        # This file - Main documentation
├── config.example.json             # Configuration template
├── pyproject.toml                  # Python project metadata
└── .gitignore                      # Git ignore rules

Note: legacy/ folder (original implementation) is not included in this repository.
```

### Key Components Explained

**NoQuery System**: The main implementation using semantic similarity-based evaluation
- **scripts/**: Numbered scripts for the complete workflow (1-6) plus utilities
- **src/**: Reusable Python modules for LLMs, methods, and embeddings
- **data/**: Data storage (source files not included, see [Data Files](#-data-files))

**Configuration Files**:
- `config.example.json`: Template for API keys (copy to `config.json`)
- `.gitignore`: Ensures sensitive files are not committed

**Documentation**:
- `README.md`: Main project documentation (this file)
- `noquery/README.md`: Detailed NoQuery system guide
- `noquery/scripts/README.md`: Scripts reference and usage guide

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key (for GPT models)
- Anthropic API key (for Claude models, optional)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/c-seo-bench.git
cd c-seo-bench
```

2. Install dependencies:
```bash
pip install -r noquery/requirements.txt
```

3. Configure API keys:
```bash
# Copy the example config file
cp config.example.json config.json

# Edit config.json and add your API keys
# IMPORTANT: Never commit config.json to version control!
```

### Basic Usage

#### Quick Start with Sample Data

The fastest way to get started is using the included sample data:

```bash
cd noquery
python run_category.py "Apparel" --samples 10 --method Authoritative
```

This will:
- Use the included Apparel sample dataset
- Sample 10 documents for improvement
- Build semantic cohorts automatically
- Apply the Authoritative C-SEO method
- Submit batch processing to OpenAI

#### Complete Workflow (Step-by-Step)

After obtaining data files (see [Data Files](#-data-files) section), run the complete workflow:

**Step 1: Extract Category**
```bash
cd noquery
python scripts/1_extract_category.py --category "Books"
# Output: data/datasets/books/books.json
```

**Step 2: Sample Documents**
```bash
python scripts/2_gen_need_improve.py \
    --changed_json data/datasets/books/books.json \
    --out_json data/datasets/books/need_improve.json \
    --num 30
# Output: data/datasets/books/need_improve.json (30 sampled documents)
```

**Step 3: Build Semantic Cohorts**
```bash
python scripts/3_build_cohorts.py \
    --changed_json data/datasets/books/books.json \
    --need_improve_json data/datasets/books/need_improve.json \
    --out_dir data/datasets/books
# Output: cohorts.json, boosted.json
```

**Step 4: Apply C-SEO Method**
```bash
python scripts/4_improve_texts.py \
    --changed_json data/datasets/books/books.json \
    --need_improve_json data/datasets/books/need_improve.json \
    --out_json data/datasets/books/improved_Authoritative.json \
    --method Authoritative \
    --llm_name gpt-4o-2024-11-20
# Submits to OpenAI Batch API, waits for completion
```

**Step 5: Run Benchmark**
```bash
# Baseline
python scripts/5_run_benchmark.py \
    --domain books \
    --changed_json data/datasets/books/books.json \
    --cohorts data/datasets/books/cohorts.json \
    --boosted data/datasets/books/boosted.json \
    --method baseline \
    --llm_name gpt-4o-2024-11-20

# Improved method
python scripts/5_run_benchmark.py \
    --domain books \
    --changed_json data/datasets/books/books.json \
    --cohorts data/datasets/books/cohorts.json \
    --boosted data/datasets/books/boosted.json \
    --improved_json data/datasets/books/improved_Authoritative.json \
    --method Authoritative \
    --llm_name gpt-4o-2024-11-20
```

**Step 6: Evaluate Results**
```bash
python scripts/6_eval_wilcoxon.py \
    --domain books \
    --method Authoritative \
    --llm_name gpt-4o-2024-11-20
# Output: Statistical significance (p-value, Delta Rank)
```

#### Automated Workflow (Recommended)

Use the orchestration script to run steps 1-4 automatically:
```bash
cd noquery
python run_category.py "Books" --samples 30 --method Authoritative

# Then manually run steps 5-6 for benchmarking and evaluation
```

## 📊 Available C-SEO Methods

The system implements several C-SEO optimization methods:

- **Authoritative** - Citation boosting with authoritative framing
- **Statistics** - Content improvement with statistical claims
- **Controversial** - Engagement through controversial statements
- **Instructional** - Step-by-step guides and tutorials
- **Original** - Baseline (no optimization)

## 📚 Documentation

- [NoQuery System Documentation](noquery/README.md) - Detailed guide for the main system
- [GitHub Upload Guide](GITHUB_UPLOAD_GUIDE.md) - Instructions for uploading to GitHub
- [Scripts Documentation](noquery/scripts/README.md) - Reference for all scripts

## 🔧 Configuration

The `config.json` file (created from `config.example.json`) should contain:

```json
{
  "openai_api_key": "sk-proj-...",
  "anthropic_api_key": "sk-ant-...",
  "model": "gpt-4o-mini",
  "temperature": 0.7,
  "max_tokens": 2000,
  "batch_size": 100
}
```

**⚠️ Security Note:** Never commit `config.json` to version control. It's already in `.gitignore`.

## 📦 Data Files

Due to file size constraints (64MB+), large data files are **not included** in this repository.

### Required Data Files

The benchmark requires the following data files in `noquery/data/changed_json/`:

| File | Category | Size | Items | Description |
|------|----------|------|-------|-------------|
| `books.json` | Books | ~2.8 MB | 2,245 | Book descriptions |
| `retail.json` | Retail | ~16 MB | 5,000 | Product descriptions |
| `videogames.json` | Video Games | ~7.5 MB | 4,360 | Game descriptions |
| `web.json` | Web Content | ~18 MB | 1,500 | Web articles |
| `news.json` | News | ~11 MB | 2,375 | News articles |
| `debate.json` | Debates | ~9.7 MB | 880 | Debate topics |
| `unified_data_merged.json` | All Categories | ~64 MB | 16,360 | Combined dataset |

### How to Obtain Data Files

#### Option 1: Download from HuggingFace (Recommended)
The original C-SEO Bench dataset is available on HuggingFace:
```bash
# Download from HuggingFace
# Visit: https://huggingface.co/datasets/parameterlab/c-seo-bench

# Or use the datasets library
pip install datasets
python -c "from datasets import load_dataset; dataset = load_dataset('parameterlab/c-seo-bench')"
```

After downloading, you may need to reformat the data to match the NoQuery structure (see below).

#### Option 2: Use Sample Data (For Testing)
Small sample datasets are included in `noquery/data/datasets/` for testing purposes:
```bash
# Sample data is already included in the repository
ls noquery/data/datasets/apparel/
# Contains: apparel.json (small sample for quick testing)
```

#### Option 3: Create Your Own Dataset
You can create custom datasets following this JSON format:
```json
{
  "category_name": [
    {
      "name": "Item Name",
      "description": "Detailed description of the item..."
    },
    {
      "name": "Another Item",
      "description": "Another description..."
    }
  ]
}
```

### Data Format

The NoQuery system expects JSON files with this structure:
```json
{
  "books": [
    {
      "name": "Book Title",
      "description": "Book description without 'Description:' prefix"
    }
  ]
}
```

**Important Notes**:
- Each file should contain one top-level category key
- `name` field: Document/product name
- `description` field: Full text description (no prefix)
- Files should be UTF-8 encoded
- Unicode characters should be standard (use `util_clean_unicode.py` if needed)

### Converting from Original Dataset

If you download the original C-SEO Bench data, you may need to:

1. **Extract names from descriptions**:
```bash
python noquery/scripts/util_extract_names.py \
    original_file.json \
    --category-keys books
```

2. **Remove description prefixes**:
```bash
python noquery/scripts/util_remove_description_prefix.py \
    file.json \
    --category-keys books
```

3. **Merge multiple files**:
```bash
python noquery/scripts/util_merge_json_files.py \
    books.json retail.json videogames.json \
    -o unified_data_merged.json
```

### Quick Start Without Full Data

You can start experimenting immediately with the included sample data:
```bash
# Use the Apparel sample (already included)
cd noquery
python run_category.py "Apparel" --samples 10 --method Authoritative
```

This will work with the small sample dataset included in the repository.

## 🧪 Experiments

Results from experiments are stored in the `experiments/` directory:

```
experiments/
├── results/          # Completed experiment results
│   └── [category]/
│       └── [method]/
│           └── [model]/
└── running/          # In-progress experiments
```

## 🛠️ Utility Scripts

The `noquery/scripts/` directory includes several utility scripts:

- `util_fetch_batch_results.py` - Retrieve OpenAI batch processing results
- `util_clean_unicode.py` - Clean Unicode characters from JSON files
- `util_extract_names.py` - Extract names from descriptions
- `util_merge_json_files.py` - Merge multiple JSON files
- `util_run_pipeline.py` - Run complete processing pipeline

## 📈 Evaluation

The system uses the Wilcoxon signed-rank test to evaluate the effectiveness of C-SEO methods by comparing:

- **Baseline**: Original document rankings
- **Treatment**: Rankings after applying C-SEO methods

Results include:
- Statistical significance (p-value)
- Effect size (Delta Rank)
- Win/Loss/Tie breakdown

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

[Add your license information here]

## 📧 Contact

[Add your contact information here]

## 🙏 Acknowledgments

- Based on the C-SEO Bench paper [add citation]
- OpenAI for GPT models
- Anthropic for Claude models

## 📝 Citation

If you use this code in your research, please cite:

```bibtex
[Add your BibTeX citation here]
```

## 🆘 Troubleshooting

### Common Issues

#### Issue 1: ModuleNotFoundError
```
ModuleNotFoundError: No module named 'noquery'
```

**Solutions**:
```bash
# Solution 1: Install in development mode
pip install -e .

# Solution 2: Install from requirements
pip install -r noquery/requirements.txt

# Solution 3: Add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"  # Linux/Mac
set PYTHONPATH=%PYTHONPATH%;%CD%  # Windows
```

#### Issue 2: API Key Error
```
openai.AuthenticationError: Error code: 401
```

**Solutions**:
1. Check if API key is complete (starts with `sk-proj-` or `sk-`)
2. Verify key is set in `config.json` or environment variable
3. Ensure key has sufficient credits
4. Check API key hasn't expired

#### Issue 3: Data Files Not Found
```
FileNotFoundError: [Errno 2] No such file or directory: 'noquery/data/changed_json/books.json'
```

**Solutions**:
1. Download files from HuggingFace: https://huggingface.co/datasets/parameterlab/c-seo-bench
2. Use sample data: `python run_category.py "Apparel" --samples 10`
3. Check file paths are correct
4. See [Data Files](#-data-files) section above

#### Issue 4: Batch Processing Timeout
```
Batch processing taking too long or hanging
```

**Solutions**:
```bash
# Increase timeout
python scripts/4_improve_texts.py ... --max_wait_seconds 7200

# Check batch status manually
python scripts/util_fetch_batch_results.py --batch_id batch_xxx ...
```

#### Issue 5: Unicode Characters Warning
```
VS Code: "This document contains ambiguous Unicode characters"
```

**Solution**:
```bash
python noquery/scripts/util_clean_unicode.py \
    noquery/data/changed_json/*.json --clean
```

#### Issue 6: Import Errors in Methods
```
ModuleNotFoundError: No module named 'llms'
```

**Solutions**:
- All imports in `noquery/src/` should use absolute imports: `from noquery.src.llms import ...`
- Ensure you're running scripts from the project root or `noquery/` directory
- Check `sys.path` includes the project root

### FAQ

**Q: How long does batch processing take?**
A: Typically 10-30 minutes for 30 documents, depending on OpenAI API load and model used.

**Q: Can I use Claude/Anthropic models?**
A: Yes, set `ANTHROPIC_API_KEY` and use `--llm_name claude-3-5-sonnet-20241022`

**Q: How much does it cost to run?**
A: For 30 documents with GPT-4o-mini: ~$1-2 for improvements + ~$5-10 for benchmarking

**Q: Can I run this without API keys for testing?**
A: No, the system requires OpenAI API for embeddings and LLM calls. Use the free tier with `gpt-4o-mini` for cost-effective testing.

**Q: Where are experiment results saved?**
A: Results are in `experiments/results/{domain}/{method}/{llm_name}/AdoptionMode.{mode}/`

## ⚠️ Known Issues

- Large JSON files (>50MB) require Git LFS or external storage
- Batch operations may take 10 minutes to 2 hours depending on API load
- Unicode characters in downloaded data may need cleaning with `util_clean_unicode.py`
- Windows users: Use Git Bash or WSL for best compatibility with shell commands

## 🔄 Version History

- **v1.0.0** - Initial release with NoQuery system
  - Semantic similarity-based evaluation
  - No predefined queries required
  - Complete English documentation
  - Sample data included

## 📚 Additional Resources

- **Original Paper**: [C-SEO Bench Paper](https://arxiv.org/abs/2506.11097)
- **HuggingFace Dataset**: https://huggingface.co/datasets/parameterlab/c-seo-bench
- **Detailed Documentation**: [noquery/README.md](noquery/README.md)
- **Scripts Reference**: [noquery/scripts/README.md](noquery/scripts/README.md)
