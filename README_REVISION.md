# GEO-Bench — revision branch (`revision`)

This branch adds a **single evaluation protocol** on top of the per-method
implementations in `branches/`, plus the new experiments the ARR May 2026
reviews require.  Everything new lives in `geobench/`, `scripts/`, `manifests/`
and `results/unified/`; the method branches are only patched (chat template,
extra rankers, pad token) — see `scripts/patch_branches.py`.

```
geobench/
  config.py          datasets, ranker panel, K, W_bad lexicon (24 words / 54 phrases), method groups
  data.py            dataset loading + instance manifests (python -m geobench.data)
  prompts.py         ONE ranking prompt, chat-template rendering, deterministic rank parser
  rankers.py         HF / OpenAI / Anthropic rankers; K seeded random orderings; greedy decoding
  metrics.py         NRG, Success@a, Promote@a, KVR, PPL-R (Appendix C, implemented once)
  collect.py         adapters: raw StealthRank / Zero-Shot / STS / RAF outputs -> unified instances CSV
  evaluate.py        re-rank every instance (clean + manipulated), same K orderings -> per-instance CSV
  detect.py          LLM-judge detectability (AUROC), relevance drift, cross-encoder reranker ranking
  stats.py           bootstrap 95% CIs, paired Wilcoxon (+Holm), rank-biserial effect sizes, group tests
  make_tables.py     Table 4 blocks by threat model, cross-ranker table, Figure 1 with CIs
  appendix.py        reproducibility appendix generated from code/config
  scan_failed_runs.py coverage per (method, dataset) + degenerate-run signatures
  attacks/           unified-schema runners: zero_shot.py, cseo_rewrite.py, tap.py
scripts/             00_setup .. 05_tables, slurm/ templates, patch_branches.py
tests/               offline tests (python -m pytest -q tests)
```

## Unified schema

Every attack ends as a row in `results/unified/instances/<method>.csv`:

| column | meaning |
|---|---|
| `method` | `sts`, `raf`, `stealthrank`, `zero_shot`, `tap`, `authoritative`, … , `clean` |
| `dataset`, `category`, `target_idx` | instance id; `target_idx` is 1-based, matches `manifests/<dataset>.csv` |
| `orig_text` | description shown to the ranker before manipulation |
| `adv_text` | description shown after manipulation (suffix appended, or full rewrite) |
| `adv_suffix` | the appended text (empty for rewrites) |
| `select_rule` | `best` / `last` / `single` — how the final text was chosen from an optimizer trace |

`evaluate.py` never reads method-specific files.  It ranks the clean list and
the manipulated list with the **same K seeded orderings**, aggregates (median),
and writes `results/unified/per_instance/<ranker>/<method>.csv` with
`r_before, r_after, ranks_before, ranks_after, nrg, success@0.1, promote@0.1,
kvr, kvr_hits, kvr_orig, ppl_orig, ppl_adv, ppl_r`.

## Commands

```bash
# 0. environment (once).  Needs HF_TOKEN for Llama/Gemma, OPENAI_API_KEY for gpt-4o-mini.
bash scripts/00_setup.sh            # or: make setup
python -m pytest -q tests           # offline sanity tests

# 0b. apply the branch patches (idempotent; --check to preview)
python scripts/patch_branches.py

# 1. Collect what is already in the repo -> unified instances + coverage/failure report
make collect                        # CPU, seconds

# 2. Regenerate the inference-only attack families with the unified runners
#    (Zero-Shot with the ranker as attacker; C-SEO rewrites with GPT-4o-mini; TAP with DeepSeek-R1)
make attacks                        # 1 GPU + API keys
make ablation                       # attacker/rewriter-strength ablation (wK3H W2)

# 3. Evaluate every instances CSV with one ranker (unified protocol, K=10)
make evaluate RANKER=llama-3.1-8b   # -> per_instance/llama-3.1-8b/*.csv + summary/llama-3.1-8b_*.csv
make evaluate RANKER=qwen2.5-7b
make evaluate RANKER=mistral-7b
make evaluate RANKER=gpt-4o-mini    # API; transfer setting for the white-box attacks
#   cluster:  bash scripts/slurm/submit_eval.sh   (see "Running on USC CARC")

# 4. Detectability + relevance signals (LLM judge != ranker; bge embeddings; bge cross-encoder reranker)
make detect                         # -> detect/judge/summary_*.csv, detect/drift/*.csv, per_instance/bge-reranker-v2-m3/

# 5. Tables / figure / appendix
make tables RANKERS="llama-3.1-8b qwen2.5-7b mistral-7b gpt-4o-mini"
#   -> results/unified/tables/table_main_<ranker>.tex, table_rankers.tex, ranker_order_spearman.csv,
#      fig_tradeoff_<ranker>.pdf, appendix_repro.tex
```

### Running on USC CARC

All submitters live in `scripts/slurm/` and follow the heredoc-`sbatch` pattern
(account `xiangren_1715`, partition `nlp_hiprio`, `--gres=gpu:rtxa6000:N`,
conda env on `PATH`).  Every setting is a variable in `scripts/slurm/_common.sh`
and can be overridden inline (`ACCOUNT=yzhao010_1245 PARTITION=gpu GPU_TYPE=a100 bash …`).

```bash
# once, on a login node
cd /scratch1/nimase/geobench && git clone -b revision <repo-url> geobench-rev && cd geobench-rev
export HF_HOME=/scratch1/nimase/hf_cache HF_TOKEN=... OPENAI_API_KEY=...
bash scripts/00_setup.sh                       # conda env "geobench" + manifests + tests

bash scripts/slurm/submit_all.sh stage1        # collect existing outputs; attacks (Zero-Shot, C-SEO, TAP) + ablation, 1 GPU each
bash scripts/slurm/submit_all.sh stage2        # evaluate on llama / qwen2.5 / mistral (1 GPU each) + detect
RANKERS=gpt-4o-mini bash scripts/slurm/submit_eval_api.sh      # API ranker, login node (transfer setting)
bash scripts/slurm/submit_all.sh stage3        # white-box re-optimisation vs mistral-7b + qwen2.5-7b  (~200 GPU-h each)
bash scripts/slurm/submit_all.sh stage4        # evaluate the *__opt-<model>.csv instances (white-box + transfer)
bash scripts/05_tables.sh                      # CPU: tables / figure / appendix

# individual submitters
bash scripts/slurm/submit_attacks.sh [ablation]
RANKERS="llama-3.1-8b" K=10 bash scripts/slurm/submit_eval.sh
bash scripts/slurm/submit_detect.sh
bash scripts/slurm/submit_stealthrank.sh mistral-7b [datasets…]      # env: CONDA_BIN_STEALTH
bash scripts/slurm/submit_raf.sh llama-3.1-8b [datasets…]            # env: CONDA_BIN_STEALTH
bash scripts/slurm/submit_sts.sh llama-3.1-8b cseo_subsampled        # env: CONDA_BIN_STS; array, one task per (catalog, target)
```

The white-box attacks run inside their branch folders with the branch envs
(`CONDA_BIN_STEALTH`, `CONDA_BIN_STS` in `_common.sh`; defaults are the
`/scratch1/nimase/geobench/env*` envs from the submission runs) and end by
collecting into `results/unified/instances/<method>__opt-<MODEL>.csv`.
Evaluate those with `RANKERS=<MODEL>` (white-box) and `gpt-4o-mini` (transfer).
Budget: ~200 GPU-h per additional open ranker for the three gradient attacks.

### What the coverage report will show first

`make collect` prints, per (method, dataset), how many of the manifest's
instances have a raw output and how many are degenerate (`adv_text ==
orig_text`).  Expected on the current tree: STS C-SEO `news`/`retail` flagged
(no `sts.txt`), RAF Llama missing entirely, TAP and C-SEO absent until the
runners in `geobench/attacks/` are run or the original code is added.

## Secrets / anonymity (do before any release)

* `branches/cseo/config.json` contained a live OpenAI key.  It is now
  git-ignored and removed from the index on this branch, **but it is still in
  history on `cseo` and `submission` (and on the 4open.science mirror)**:
  revoke the key, then purge with
  `git filter-repo --invert-paths --path branches/cseo/config.json --path branches/cseo/noquery/src/config/__pycache__`
  and force-push every branch.
* Slurm/W&B identifiers (`/scratch1/<user>`, account ids, `entity: nimase`)
  live only in `branches/*/slurm_executable_files` and `branches/Stealth-Rank/configs`;
  `scripts/slurm/_env.sh` is the single place the new pipeline reads them from.
