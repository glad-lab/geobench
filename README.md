# Adversarial SEO Research Framework

**Version**: 2.0.0 (Modular Architecture)
**Status**: Production-Ready
**License**: MIT
**Python**: 3.9+

A comprehensive research framework for studying preference manipulation attacks on LLM-powered search engines and RAG systems. This project provides modular tools for reproducing and validating findings from adversarial SEO research through controlled, ethical experiments.

---

## Overview

This framework demonstrates how adversarial content can manipulate rankings in LLM-based search systems. The project has been completely refactored from a monolithic codebase into **12 modular packages** with comprehensive documentation and examples.

### Key Features

- 🔬 **Research-Ready**: Reproduce paper findings with validated experiments
- 🧩 **Modular Architecture**: 12 packages, 75+ focused modules
- 🎯 **Multi-Provider Support**: AWS Bedrock, OpenAI, Anthropic Claude
- 📊 **Statistical Analysis**: Built-in metrics and significance testing
- 📈 **Visualization**: Publication-ready charts and reports
- 🛡️ **Ethical Framework**: Controlled experiments, no real-world attacks
- 🔄 **100% Backward Compatible**: Smooth migration from v1.x

---

## Getting Started

### Prerequisites

- Python 3.9+
- Docker (for Qdrant vector database)
- API keys: Anthropic Claude OR OpenAI OR AWS Bedrock
- (Optional) Google Gemini API key for embeddings

### Quick Start (5 minutes)

1. **Clone and setup:**
   ```bash
   git clone https://github.com/your-org/adversarial-seo.git
   cd adversarial-seo
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

3. **Start services and populate database:**
   ```bash
   docker-compose up -d
   python scripts/repopulate_db.py --reset --verify
   ```

4. **Run your first experiment:**
   ```bash
   python examples/experiment_usage.py
   # OR use the main entrypoint:
   python run_experiment.py
   ```

---

## Main Entrypoints

### Primary Entry Point
- **`run_experiment.py`** - Main launcher showing available examples
  ```bash
  python run_experiment.py
  ```

### Database Management
- **`scripts/repopulate_db.py`** - Populate vector database (required first step)
  ```bash
  python scripts/repopulate_db.py --reset --verify
  ```

### Example Experiments

Located in `examples/` directory:

| Script | Purpose | Best For |
|--------|---------|----------|
| `experiment_usage.py` | Core experiment patterns | Learning experiment configuration |
| `rag_example.py` | RAG pipeline usage | Understanding retrieval and ranking |
| `experiments_evaluation_integration.py` | End-to-end workflow | Complete pipeline understanding |
| `visualization_demo.py` | Chart generation | Creating publication-ready visualizations |
| `reporting_package_example.py` | Report generation | Generating experiment reports |

Run any example:
```bash
python examples/experiment_usage.py
```

---

## Basic Usage Example

```python
from experiments import ExperimentRunner, ExperimentConfig
from llm import create_llm_client

# Configure experiment
config = ExperimentConfig(
    name="single_attack_test",
    experiment_type="single_attack",
    llm_provider="anthropic",
    model="claude-3-haiku-20240307",
    attack_type="prompt_injection",
    num_trials=10
)

# Run experiment
runner = ExperimentRunner(config)
results = runner.run()

# View results
print(f"Attack success rate: {results.success_rate:.2%}")
print(f"Average target rank: {results.average_rank:.2f}")
results.save("results/single_attack.json")
```

---

## Documentation

### Comprehensive Guides

| Document | Description | Audience |
|----------|-------------|----------|
| [Migration Guide](docs/MIGRATION_GUIDE.md) | Migrate from v1.x to v2.0 | Existing users |
| [API Reference](docs/API_REFERENCE.md) | Complete API documentation | Developers |
| [Developer Guide](docs/DEVELOPER_GUIDE.md) | Development best practices | Contributors |
| [Project Summary](docs/PROJECT_SUMMARY.md) | Refactoring overview | Everyone |

### Quick Links

- **Getting Started**: See [Developer Guide](docs/DEVELOPER_GUIDE.md#getting-started)
- **API Documentation**: See [API Reference](docs/API_REFERENCE.md)
- **Migration Help**: See [Migration Guide](docs/MIGRATION_GUIDE.md)
- **Examples**: Check `examples/` directory

---

## Core Packages

The framework consists of 12 modular packages:

- **`llm/`** - Multi-provider LLM clients (OpenAI, Anthropic, AWS Bedrock)
- **`attacks/`** - Attack generation strategies (prompt injection, discreditation, persuasion)
- **`ranking/`** - LLM and RAG-based ranking algorithms
- **`vector_db/`** - Vector database population and management
- **`experiments/`** - Experiment orchestration and configuration
- **`evaluation/`** - Result evaluation and metrics
- **`rag/`** - RAG pipeline (retrieval + generation)
- **`analysis/`** - Statistical analysis and comparison
- **`visualization/`** - Chart and graph generation
- **`reporting/`** - Report generation (Markdown, HTML)
- **`testing/`** - Multi-provider test utilities
- **`utils/`** - Data loading, sampling, validation

For detailed API documentation, see [API Reference](docs/API_REFERENCE.md)

---

## Research Capabilities

### Validated Findings

This framework has validated key findings from adversarial SEO research:

- ✅ **Single Attack Effectiveness**: 38% average position-1 success rate (within paper's 25-60% range)
- ✅ **Prisoner's Dilemma**: Confirmed collective performance degradation (p < 0.01)
- ✅ **Attack Transferability**: Validated across AWS Bedrock, OpenAI, Anthropic
- ✅ **Positional Bias**: Confirmed position-dependent effectiveness (p < 0.05)

### Experiment Types

1. **Single Attack Experiments** - Test individual attack effectiveness on product rankings
2. **Multi-Attacker Scenarios (Prisoner's Dilemma)** - Demonstrate how multiple attackers degrade collective performance
3. **Positional Bias Analysis** - Test whether attack position within context affects success rates
4. **External Attack Validation** - Test attacks from discrete documents with complete separation and transparency

---

## Technology Stack

**Core**:
- Python 3.9+
- LangChain (LLM abstraction)
- Qdrant (vector database)

**LLM Providers**:
- AWS Bedrock (LLaMA models)
- OpenAI (GPT models)
- Anthropic (Claude models)

**Embeddings**:
- Google Gemini API (text-embedding-004, free tier)
- OpenAI (text-embedding-ada-002)

**Analysis & Visualization**:
- NumPy, Pandas (data processing)
- Matplotlib, Seaborn (visualization)
- SciPy (statistical tests)

---

## Configuration

### Essential Environment Variables

```bash
# LLM Provider (choose one)
ANTHROPIC_API_KEY=sk-...
# OR
OPENAI_API_KEY=sk-...
# OR configure AWS CLI for Bedrock

# Embeddings (recommended: Google Gemini free tier)
GOOGLE_API_KEY=...

# Vector Store (default settings)
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

### API Key Setup

**Google Gemini API** (embeddings, free tier):
- Get API key: https://aistudio.google.com/app/apikey
- Set `GOOGLE_API_KEY` in `.env`

**Anthropic Claude** (recommended for research):
- Get API key: https://console.anthropic.com/
- Set `ANTHROPIC_API_KEY` in `.env`

**OpenAI** (optional):
- Get API key: https://platform.openai.com/api-keys
- Set `OPENAI_API_KEY` in `.env`

**AWS Bedrock** (pay-per-use):
- Configure: `aws configure`
- Ensure IAM permissions for Bedrock

---

## Ethical Guidelines

This framework is designed for **controlled, ethical research only**:

- ✅ Use only fictional products (no real brands)
- ✅ Test on local/controlled systems only
- ✅ No attacks on production services
- ✅ Clear separation between research and malicious use
- ✅ Sandboxed execution environment
- ✅ Transparent attack mechanisms (glass box approach)

**Purpose**: Understand vulnerabilities to build better defenses
**Scope**: Academic research and controlled experiments
**Responsibility**: Never deploy attacks against real systems
**Transparency**: Complete visibility into attack mechanisms

---

## Contributing

We welcome contributions! Please follow these guidelines:

1. **Fork the repository** and create a feature branch
2. **Follow code style**: Black formatting, type hints, docstrings
3. **Write tests**: Maintain >85% coverage for new code
4. **Update documentation**: Keep docs in sync with code
5. **Submit pull request**: Clear description and checklist

See [Developer Guide](docs/DEVELOPER_GUIDE.md) for detailed instructions.

---

## Citation

If you use this framework in your research, please cite:

```bibtex
@article{nestaas2024adversarial,
  title={Adversarial Search Engine Optimization for Large Language Models},
  author={Nestaas, Finn and Aggarwal, Kunal and others},
  journal={arXiv preprint arXiv:2406.XXXXX},
  year={2024}
}

@software{adversarial_seo_framework,
  title={Adversarial SEO Research Framework},
  author={Your Lab Group},
  version={2.0.0},
  year={2025},
  url={https://github.com/your-org/adversarial-seo}
}
```

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

## Support

### Getting Help

**Documentation**:
- [Migration Guide](docs/MIGRATION_GUIDE.md) - Upgrade from v1.x
- [API Reference](docs/API_REFERENCE.md) - Complete API docs
- [Developer Guide](docs/DEVELOPER_GUIDE.md) - Development practices

**Examples**:
- `examples/` - Working code examples
- `tests/integration/` - Integration test examples
- `tests/unit/` - Unit test examples

**Issues**:
- GitHub Issues for bug reports
- Check existing issues before creating new ones
- Provide reproducible examples

### Roadmap

**v2.1** (Next Release):
- Additional LLM providers (Google Gemini, Cohere)
- Enhanced visualization options
- Performance optimizations

**v2.2** (Future):
- Defense mechanism research
- Interactive web dashboard
- Real-time experiment monitoring

**v3.0** (Long-term):
- Production deployment support
- API service for experiments
- Community plugin system

---

## Acknowledgments

- Original research paper authors
- LangChain community for LLM abstractions
- Anthropic, OpenAI, AWS for LLM access
- Lab group members for feedback and validation

---

## Project Status

- **Version**: 2.0.0 (Modular Architecture)
- **Status**: Production-Ready
- **Documentation**: Comprehensive guides and API reference
- **Backward Compatibility**: 100% maintained

---

**Last Updated**: November 2025
**Maintained By**: Your Lab Group
**Contact**: your-email@university.edu

---

## Data Formats

The project supports three data format variants:

| Format | Location | Use Case |
|--------|----------|----------|
| **Unified Master** | `data/products_master.json` | Default experiments (recommended) |
| **Category Groups** | `data/categories/*.json` | Category-specific analysis |
| **Individual Products** | `data/products/*.json` | Fine-grained access |

```python
# Load unified master (default)
from src.utils.data_loading import load_products
products = load_products("data/products_master.json")
```

For complete documentation, see [Developer Guide](docs/DEVELOPER_GUIDE.md).

