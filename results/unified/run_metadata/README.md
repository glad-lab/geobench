# GPT-4o-mini API revision run

Completed 2026-09-10 at 06:06:45 UTC (2026-09-09 at 23:06:45 America/Los_Angeles).

## Scope and outputs

- Generated all 10 CSEO rewriting strategies: 729 targets each, 7,290 new rows.
- Generated `zero_shot__att-gpt4omini`: 729 new rows.
- Evaluated all 15 instance variants: 10,672 rows in `../per_instance/gpt-4o-mini/`.
- Produced the four requested statistics CSVs in `../summary/`.
- TAP with DeepSeek and a Llama ranker was excluded as requested. No GPU or perplexity evaluation was run.

Requests used the BlockRun account API with the explicitly selected model `openai/gpt-4o-mini`. Responses reported `gpt-4o-mini-2024-07-18` 122,584 times and the accepted `openai/gpt-4o-mini` alias once. No model fallback or automatic routing was enabled.

Evaluation used K=10 seeded candidate orderings, median rank aggregation, and the shared clean-rank cache. API generation/evaluation ran at several worker counts, ending with 64 evaluation workers. Interruptions and connectivity failures were resumed from checkpoints. Successful API response counts include repeated work from interrupted, not-yet-saved evaluation targets.

## Validation and interpretation

`api_run_validation.json` records validation of all generated target sets, method variants, nonempty outputs, all 10,672 source descriptions, evaluation coverage, rank-list lengths and bounds, median aggregation, per-instance metrics, and statistics means. `sha256.json` records file hashes for instance CSVs, evaluation CSVs, their configuration sidecars, and summary CSVs.

Evaluation sidecars were marked complete after the full result validation; their original configuration fingerprints are unchanged.

Original output caps were preserved, including length-terminated responses: 7,160 of 122,585 successful responses ended at the cap. The original L+1 convention remains in place when the target is omitted or not parsed from the model's ranking. These cases are recorded rather than discarded or selectively regenerated. The validation report includes unchanged rewrite counts and target-absent ranking counts; the latter count reused before-rank lists once per evaluated variant.

The existing RAF variant covers 466 targets; other evaluated variants cover 729 each. Dataset-weighted overall statistics and pooled per-instance means are different aggregations. The validation report's `nrg_mean` values are pooled means; use the existing overall statistics CSV for the dataset-weighted comparison.

## Recorded usage and estimated cost

- Successful responses: 122,585
- Input tokens: 81,349,595
- Output tokens: 23,076,098
- Estimated token cost: USD 26.04809805 at USD 0.15/M input and USD 0.60/M output.

This is a local usage-based estimate, not reconciliation against the full account ledger. Unreceived timeout responses may not be represented. The preliminary four-call compatibility smoke test is separate. The account model catalog and sampled account charges were checked during the run and matched these token rates without an additional per-call fee on the sampled charges.

Credentials and raw runtime logs are not included. The reusable clean-rank cache remains locally available and is excluded from Git by the repository's existing ignore rule; before/after ranks are included in every committed evaluation row.
