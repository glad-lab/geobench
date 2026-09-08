# GEO-Bench resubmission — to-do

Verdict: ARR May 2026, scores 2.5/2/2.5, meta-review "Resubmit next cycle." Every rebuttal promise is now required. Resubmit as a long paper.

## Security / repo hygiene (do first)

- [ ] Revoke the OpenAI key in `branches/cseo/config.json` (on `cseo`, `submission`, and the anonymous mirror); purge it and `noquery/src/config/__pycache__/*.pyc` from history (`git filter-repo`).
- [ ] Strip de-anonymizing paths from the release copy: `/scratch1/nimase/...`, `yzhao010_1245` in Slurm scripts, `wandb entity: nimase` in configs, the `STS/results` symlink to `/media/volume/geo2`.
- [ ] Delete tracked `.pyc` files, `.DS_Store`, and the unused `Manipulating-LLMs` and `AdversialSEO` folders from the release branch.
- [ ] Collapse to one branch: `geobench/{data,attacks/<method>,eval,scripts}` + `run_all.sh` + `make table4`.

## Code — recover what the paper used

- [ ] Get the TAP-for-GEO-Bench code into the repo (Llama-3.1-8B target, DeepSeek-R1-0528 attacker, unified-dataset loader, per-instance CSV output). `cse` is unmodified Pfrommer code; `git grep -i deepseek-r1` finds nothing on any branch.
- [ ] Get the C-SEO-for-GEO-Bench code in (GPT-4o-mini rewrites → Llama ranker → NRG/KVR/PPL-R). `cseo` only ranks via OpenAI citation order with a different Success@ definition.
- [ ] Check in RAF's Llama-3.1-8B results (`result/raf/` has deepseek/mistral/phi/qwen/vicuna only).
- [ ] Check in STS raw per-instance outputs (currently off-repo behind the symlink).

## Code — unify the protocol

- [ ] Freeze one instance manifest per dataset (every `(category, target_idx)`); all runners and evaluators read it. Ragroll today: StealthRank/Zero-Shot 50 cats, STS 21, RAF 53.
- [ ] Write one shared `eval.py`: same prompt builder, same product formatting (RAF uses `Name: Natural`, Zero-Shot description only), same parser, same r_after rule (e.g., median over K=10 random orderings). Today: StealthRank/STS = `min` over all iterations, Zero-Shot = mean of 10, RAF = 10 re-ranks.
- [ ] Switch every branch to `tokenizer.apply_chat_template`. `Stealth-Rank`, `zero-shot`, `RAF` wrap Llama-3.1 in the Llama-2 `[INST] <<SYS>>` format; only `STS/rank_opt.py` uses the Llama-3 template.
- [ ] Re-score all existing adversarial texts through the shared evaluator → corrected Table 4 with N per cell.
- [ ] Rerun STS on C-SEO `news` and `retail` (NRG 0.000, PPL-R 1.00±0.00 = no suffix appended; these rows feed the reported 0.18 / 2.82). Scan every method's C-SEO rows for the same signature.
- [ ] Make StealthRank's C-SEO config match the others or document why (`batch_size=2, ngram=2, target=20` vs `5/5/50`).

## Code — new experiments

- [ ] Multi-ranker panel: Llama-3.1-8B + Qwen2.5-7B/Qwen3-8B + Mistral-7B-v0.3 + one API model (GPT-4o-mini). Every method × every dataset. `MODEL_PATH_DICT` already covers mistral/vicuna/deepseek (StealthRank, zero-shot) and qwen/phi (RAF); STS is hard-coded to Llama and needs the flag.
- [ ] Cross-ranker transfer: optimize white-box attacks on the open ranker, score on the API ranker (reuse STS `--mode transfer` idea).
- [ ] Add one non-generative reranker (MonoT5 or `bge-reranker-v2-m3`) scored over existing adversarial texts.
- [ ] LLM-as-judge detector (non-ranker model, fixed prompt, yes/no + confidence) on adversarial + matched clean texts → AUROC / detection rate at fixed FPR.
- [ ] Relevance-drift signal: embedding cosine (BGE, already wired in `cseo/noquery/src/embeddings/provider.py`) or MonoT5 score, original vs. manipulated.
- [ ] Optional: small human annotation (2–3 annotators, ~100 items).
- [ ] Attacker-strength ablation: Zero-Shot/TAP with a small vs. large attacker; C-SEO rewrites with GPT-4o-mini vs. a small open model. One dataset is enough.
- [ ] Statistics script over per-instance rows: bootstrap 95% CIs on NRG/KVR/PPL-R; Wilcoxon signed-rank for the comparisons the text makes (TAP vs. best gradient, Authoritative vs. gradient on C-SEO Bench, black-box vs. white-box); report effect sizes.
- [ ] Compute-cost accounting per method (attacker calls, gradient steps, wall-clock per instance).

## Paper — results and tables

- [ ] Replace mean ± std with mean [95% CI]; drop std on 0/1 metrics.
- [ ] Split Table 4 into three threat-model blocks (white-box gradient / black-box adversarial / white-hat), each bolded separately; keep Figure 1 as the cross-paradigm view with threat models in the caption.
- [ ] Add the multi-ranker table and state whether the two headline claims survive across rankers.
- [ ] Add reranker, LLM-judge, relevance-drift, attacker-ablation, and compute columns/tables.
- [ ] Report N per (method, dataset) cell.

## Paper — text corrections

- [ ] Appendix A: "target is the first item" → every item is a target in turn.
- [ ] §3.1 / Appendix A: state that STSData (30) and LLM Rank Optimizer (40) are the complete source catalogs; justify or enlarge the RewriteToRank 200-item subsample (or show CI overlap vs. a larger sample for a cheap method).
- [ ] Fix rebuttal-vs-code mismatches: STS `batch_size=20` (not 200); StealthRank hyperparameters not uniform on C-SEO Bench.
- [ ] Rename "Stealth" → "Detectability"; state KVR/PPL-R are lower bounds bracketed by the semantic detector.

## Paper — new sections

- [ ] Reproducibility appendix: attacker models (Zero-Shot = ranker itself, `temp 0.7, top_p 0.9, ≤60 tok`; TAP = DeepSeek-R1-0528, 3 roots/b=3/w=5/d=5/m=2/δ=1), full W_bad (24 words + 55 phrases, matching rules), STS/RAF/StealthRank hyperparameters, PPL model (Vicuna-7B fp16), ranking protocol (K orderings, prompt, parser).
- [ ] Related Work: Parry et al. 2024 (query-agnostic positional injection) and follow-ups; neural-ranker attack line (PRADA, PAT/Order-Disorder, topic-oriented — verify venues); state what GEO-Bench does not cover (retrieval-stage attacks).
- [ ] Sharpen threat-model discussion in §3.2; add budget column to Table 2.
- [ ] Limitations/Ethics: update for multi-ranker, API use, detector scope, release plan.

## Order

1. Security + hygiene. 2. Recover code, manifest, shared evaluator, re-score. 3. Chat-template fix + STS reruns. 4. Multi-ranker/transfer runs. 5. Detectability + reranker scoring. 6. Stats + ablation. 7. Writing.

Compute: ~200 GPU-h (3× L40S) per ranker for gradient methods → budget ~600–800 GPU-h for three more open rankers; API-ranker transfer is inference-only.
