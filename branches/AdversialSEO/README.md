# Adversarial SEO Research Framework

**Version**: 2.0.0
**Python**: 3.9+

A modular research framework for studying preference manipulation attacks on LLM-powered search engines and RAG systems.

---

## What It Does

This framework demonstrates how adversarial content can manipulate rankings in LLM-based search systems through controlled experiments. It provides tools for:

- Generating adversarial attacks (prompt injection, discreditation, persuasion)
- Testing attacks across multiple LLM providers (AWS Bedrock, OpenAI, Anthropic)
- Evaluating attack effectiveness with statistical analysis
- Visualizing results with publication-ready charts

**Ethical Use Only**: Designed for controlled research on local systems using fictional data. Never deploy against production services.

---

## Architecture

The framework consists of 12 modular packages:

```
src/
├── llm/              # Multi-provider LLM clients (OpenAI, Anthropic, Bedrock)
├── attacks/          # Attack generation (prompt injection, discreditation, persuasion)
├── ranking/          # LLM-based ranking algorithms
├── vector_db/        # Vector database management
├── experiments/      # Experiment orchestration
├── evaluation/       # Metrics and result evaluation
├── rag/             # RAG pipeline (retrieval + generation)
├── analysis/        # Statistical analysis
├── visualization/   # Chart generation
├── reporting/       # Report generation (Markdown, HTML)
├── utils/           # Data loading, sampling, validation
└── vector_store.py  # Unified vector store interface
```

**Tech Stack**:
- Python 3.9+ with LangChain
- Qdrant (vector database)
- Multi-provider LLMs (AWS Bedrock, OpenAI, Anthropic)
- Google Gemini or OpenAI for embeddings

---

## Getting Started

### Prerequisites

- Python 3.9+
- Docker (for Qdrant)
- API key for at least one: Anthropic Claude, OpenAI, or AWS Bedrock
- (Optional) Google Gemini API key for embeddings

### Quick Start

**1. Clone and setup:**
```bash
git clone https://github.com/your-org/adversarial-seo.git
cd adversarial-seo
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**2. Configure environment:**
```bash
cp .env.example .env
# Edit .env and add your API keys
```

**3. Start services:**
```bash
docker-compose up -d
```

**4. Populate database:**
```bash
python scripts/repopulate_db.py --reset --verify
```

**5. Run your first experiment:**
```bash
python run_experiment.py
```

---

## Basic Usage

```python
from experiments import ExperimentRunner, ExperimentConfig

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

## Examples

The `examples/` directory contains working code samples:

| Script | Purpose |
|--------|---------|
| `experiment_usage.py` | Core experiment patterns |
| `rag_example.py` | RAG pipeline usage |
| `experiments_evaluation_integration.py` | End-to-end workflow |
| `visualization_demo.py` | Chart generation |
| `reporting_package_example.py` | Report generation |

Run any example:
```bash
python examples/experiment_usage.py
```

---

## Configuration

### Environment Variables

```bash
# LLM Provider (choose one)
ANTHROPIC_API_KEY=sk-...
# OR
OPENAI_API_KEY=sk-...
# OR configure AWS CLI for Bedrock

# Embeddings (recommended: Google Gemini free tier)
GOOGLE_API_KEY=...

# Vector Store
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

### Getting API Keys

**Google Gemini** (embeddings, free tier):
- https://aistudio.google.com/app/apikey

**Anthropic Claude** (recommended):
- https://console.anthropic.com/

**OpenAI** (optional):
- https://platform.openai.com/api-keys

**AWS Bedrock**:
- Configure: `aws configure`
- Ensure IAM permissions for Bedrock

---

## Ethical Guidelines

This framework is for **controlled research only**:

- ✅ Use fictional products only (no real brands)
- ✅ Test on local/controlled systems
- ✅ No attacks on production services
- ✅ Sandboxed execution environment
- ❌ Never deploy against real systems

**Purpose**: Understand vulnerabilities to build better defenses
**Scope**: Academic research and controlled experiments

---
