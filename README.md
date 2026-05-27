# GEO-Bench

A unified benchmark that aggregates and re-evaluates published methods for
**ranking manipulation and generative engine optimization (GEO)** against
LLM-powered search, recommendation, and RAG systems.

Each method comes from a different paper or framework and was originally
released with its own datasets and code. GEO-Bench collects them, subsamples
their data onto a common scale, and keeps every implementation runnable so
the methods can be compared on the same inputs.

## Repository Layout

This repository is organized across branches:

- **`main`** (this branch) — the shared `Datasets/` tree: source, unified, and
  subsampled data used by every method.
- **`submission`** — the consolidated drop: `Datasets/` plus a `branches/`
  folder with all nine method implementations in one tree. Start here to run
  or compare methods.
- **One branch per method** — preserves each implementation's upstream
  development history (see table below).

```
main
└── Datasets/        # source, unified, and subsampled datasets shared across methods
```

## Datasets

| Folder                       | Contents                                                                  |
| ---------------------------- | ------------------------------------------------------------------------- |
| `Datasets_subsampled_all/`   | Unified subsampled benchmark (≤20 categories × ≤10 items per algorithm).  |
| `AdversarialSEO/`            | Unified AdversarialSEO corpus and per-category splits.                    |
| `GEO/`                       | GEO train / val / test splits and unified JSON.                           |
| `RewriteToRank/`             | Full Rewrite-to-Rank train/test data.                                     |
| `RewriteToRank_Subsampled/`  | Per-category JSONL subsamples used for the benchmark.                     |
| `StealthRank/`               | StealthRank JSON catalogs (incl. `ragroll` variant).                      |
| `Verifiability/`             | Verifiability judgements and human annotations.                           |
| `Zero-Shot Rankers/`         | Unified dataset for zero-shot ranker evaluation.                          |
| `cseo_subsampled/`           | C-SEO subsamples (books, debate, news, retail, videogames, web).          |
| `llm-rank-optimizer/`        | Source + extended data for the LLM rank optimizer method.                 |
| `llmrank_subsampled/`        | Per-category LLMRank subsamples.                                          |
| `ragdoll_subsampled/`        | Per-product RAGDOLL subsamples used for cross-method comparison.          |

**Subsampling rule** (`Datasets/Datasets_subsampled_all/README.md`): at most
20 categories per algorithm and at most 10 items per category, so results are
directly comparable across methods.

## Methods

Each method lives on its own branch (and is also collected under
`branches/<method>/` on the `submission` branch).

| Branch               | Method / Paper                                                                                       |
| -------------------- | ---------------------------------------------------------------------------------------------------- |
| `AdversialSEO`       | Adversarial SEO research framework — prompt-injection, discreditation, and persuasion attacks on RAG. |
| `cse`                | *Ranking Manipulation for Conversational Search Engines* (Pfrommer et al., EMNLP 2024) + RAGDOLL.    |
| `cseo`               | **C-SEO Bench** — citation-based SEO benchmark (NoQuery and legacy systems).                         |
| `geo`                | GEO dataset slice used by the unified evaluator.                                                     |
| `Manipulating-LLMs`  | Local reproduction of GEO / StealthRank using GCG (Greedy Coordinate Gradient).                      |
| `RAF`                | *Are LLMs Reliable Rankers? Rank Manipulation via Two-Stage Token Optimization* (Xing et al. 2025).  |
| `Stealth-Rank`       | `controllable-seo` — StealthRank rank/perplexity optimization with W&B sweeps.                       |
| `STS`                | *Manipulating LLMs to Increase Product Visibility* — Strategic Text Sequences (arXiv:2404.07981).    |
| `zero-shot`          | Zero-shot ranker evaluation pipeline (controllable-seo variant).                                     |

Each method keeps its original `README.md`, requirements, and run scripts;
consult those for method-specific setup, hyperparameters, and reproduction
commands.

## Getting Started

To run or compare methods, check out the `submission` branch, then pick a
method:

```bash
git checkout submission
cd branches/<method>           # e.g. branches/RAF
pip install -r requirements.txt
# then run the method's entry point (see that folder's README)
```

Methods read their data from the shared `Datasets/` tree; most expect either a
unified JSON or a category JSONL from `Datasets_subsampled_all/`.

## License & Attribution

Each method retains the license and attribution of its original repository
(see the `LICENSE` / `README.md` inside each method). Please cite the original
papers when using a specific method.
