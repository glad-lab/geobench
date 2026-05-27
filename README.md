# GEO-Bench

A unified benchmark that aggregates and evaluates published methods for
**ranking manipulation and generative engine optimization (GEO)** against
LLM-powered search, recommendation, and RAG systems.

This `submission` branch consolidates nine reference implementations
(previously maintained on per-method Git branches) and a shared set of
datasets so that every method can be re-run and compared on the same inputs.

## Repository Layout

```
.
├── Datasets/      # Source, unified, and subsampled datasets shared across methods
└── branches/      # One subfolder per method (the per-paper implementations)
```

### `branches/` — methods included

| Folder              | Method / Paper                                                                                     |
| ------------------- | -------------------------------------------------------------------------------------------------- |
| `AdversialSEO/`     | Adversarial SEO research framework — prompt-injection, discreditation, persuasion attacks on RAG.  |
| `cse/`              | *Ranking Manipulation for Conversational Search Engines* (Pfrommer et al., EMNLP 2024) + RAGDOLL.  |
| `cseo/`             | **C-SEO Bench** — Citation-based SEO benchmark (NoQuery and legacy systems).                       |
| `geo/`              | GEO dataset slice used by the unified evaluator.                                                   |
| `Manipulating-LLMs/`| Local reproduction of GEO / StealthRank using GCG (Greedy Coordinate Gradient).                    |
| `RAF/`              | *Are LLMs Reliable Rankers? Rank Manipulation via Two-Stage Token Optimization* (Xing et al. 2025).|
| `Stealth-Rank/`     | `controllable-seo` — StealthRank rank/perplexity optimization with W&B sweeps.                     |
| `STS/`              | *Manipulating LLMs to Increase Product Visibility* — Strategic Text Sequences (arXiv:2404.07981).  |
| `zero-shot/`        | Zero-shot ranker evaluation pipeline (controllable-seo variant).                                   |

Each method directory keeps its original `README.md`, requirements, and run
scripts; consult them for method-specific setup, hyperparameters, and
reproduction commands.

### `Datasets/` — shared data

| Folder                        | Contents                                                                |
| ----------------------------- | ----------------------------------------------------------------------- |
| `Datasets_subsampled_all/`    | Unified subsampled benchmark (≤20 categories × ≤10 items per algorithm).|
| `AdversarialSEO/`             | Unified AdversarialSEO corpus and per-category splits.                  |
| `GEO/`                        | GEO train / val / test splits and unified JSON.                         |
| `RewriteToRank/`              | Full Rewrite-to-Rank train/test data.                                   |
| `RewriteToRank_Subsampled/`   | Per-category JSONL subsamples used for the benchmark.                   |
| `StealthRank/`                | StealthRank JSON catalogs (incl. `ragroll` variant).                    |
| `Verifiability/`              | Verifiability judgements and human annotations.                         |
| `Zero-Shot Rankers/`          | Unified dataset for zero-shot ranker evaluation.                        |
| `cseo_subsampled/`            | C-SEO subsamples (books, debate, news, retail, videogames, web).        |
| `llm-rank-optimizer/`         | Source + extended data for the LLM rank optimizer method.               |
| `llmrank_subsampled/`         | Per-category LLMRank subsamples.                                        |
| `ragdoll_subsampled/`         | Per-product RAGDOLL subsamples used for cross-method comparison.        |

The subsampling rule for `Datasets_subsampled_all/` is documented in
`Datasets/Datasets_subsampled_all/README.md`: at most 20 categories per
algorithm and at most 10 items per category, so results are directly
comparable across methods.

## Getting Started

Pick the method you want to run and follow its own README:

```bash
cd branches/<method>           # e.g. branches/RAF
pip install -r requirements.txt
# then run the method's entry point (see that folder's README)
```

Datasets the methods consume live under `../../Datasets/` relative to each
method folder; most methods expect either the unified JSON or a category
JSONL from `Datasets_subsampled_all/`.

## Branch Layout

- `submission` — *this branch*, the consolidated drop with all methods and datasets in one tree.
- `main` — landing branch.
- One branch per method (`AdversialSEO`, `Manipulating-LLMs`, `RAF`, `STS`,
  `Stealth-Rank`, `cse`, `cseo`, `geo`, `zero-shot`) preserves the
  upstream development history before consolidation.

## License & Attribution

Each method retains the license and attribution of its original repository
(see the `LICENSE` / `README.md` inside each `branches/<method>/` folder).
Please cite the original papers when using a specific method.
