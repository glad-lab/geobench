# API revision preparation

Scope: C-SEO (all 10 strategies), GPT-4o-mini zero-shot with tag
`att-gpt4omini`, and GPT-4o-mini evaluation/statistics. TAP is excluded.
Base: `revision` at `6c819b1524afda6b0c2bbed098d92b68bef67277`.

**Status: implementation and offline validation complete. Real authentication,
payment, model availability, throughput and cost still need a small live test.**
No paid inference was performed and existing experiment results were not edited.

## Implemented

- Local launchers discover the checkout and use the project's Python environment.
  No CARC paths, GPU or Slurm are required for these three steps.
- Shared BlockRun adapter for both generation and ranking, mapping
  `gpt-4o-mini` to `openai/gpt-4o-mini`. Wallet SDK and bearer-compatible
  endpoint modes are explicit. No automatic routing or alternate-model fallback
  is enabled. Unexpected models, empty/filtered/truncated responses are rejected.
- Transient API failures retry with backoff. Authentication, payment and spending
  guardrail failures stop immediately instead of repeating requests.
- The full experiment label survives generation, evaluation, resume, statistics,
  table labels and plots. The base method remains available for threat-model
  grouping. Legacy filename-only tags (including RAF optimization tags) are
  normalized on read. Duplicate identities are rejected instead of pooled.
- Both generation runners save each completed target via atomic CSV replacement.
  Adjacent `.run.json` files bind outputs to parameters, prompts, source data and
  implementation. Repeating an unchanged command resumes; a completed run does
  not instantiate an API client. Changed configurations require a new tag or
  output directory. Concurrent writers are rejected by file locks.
- Evaluation output and clean-rank caches are also saved atomically. Evaluation
  resume binds the input, protocol, source catalogs and provider. Clean-cache
  identity includes protocol, provider, source texts and seed. Incomplete new
  generation CSVs are blocked before evaluation.

Checkpoints prevent redoing successfully saved work. A process killed after an
API response but before saving can still repeat that in-flight request on resume;
this is not an exactly-once billing guarantee. API calls remain sequential and
K=10 is unchanged. Truncated output stops the run; if token limits must change,
use a new experiment tag/output directory rather than mixing configurations.

## Local environment and entry points

The project environment is `.venv-geobench`, using Python 3.13.5. It inherits
existing Anaconda packages through `--system-site-packages`; the BlockRun SDK
itself is installed locally from the published **1.4.5** wheel. This avoids the
previous editable SDK checkout, whose import stalled while reading its code.
Shared environment packages were not changed. `requirements-api.txt` describes
an API-only install on a fresh machine, without torch or GPU dependencies.

```bash
# No paid requests:
bash scripts/run_revision_api.sh --dry-run
DRY_RUN=1 bash scripts/slurm/submit_eval_api.sh

# After configuring credentials locally and checking the intended budget:
bash scripts/run_revision_api.sh all
# Separate stages:
bash scripts/run_revision_api.sh generate
bash scripts/run_revision_api.sh evaluate
```

Environment settings:

| Variable | Meaning |
| --- | --- |
| `GEOBENCH_API_PROVIDER=blockrun` | Wallet SDK; default in launchers |
| `BLOCKRUN_WALLET_KEY` | Optional locally exported wallet key; SDK may use its existing wallet file |
| `GEOBENCH_API_PROVIDER=blockrun-openai` | Bearer-compatible BlockRun endpoint/proxy |
| `OPENAI_BASE_URL`, `OPENAI_API_KEY` | URL and bearer key for that endpoint; never put a wallet key here |
| `GEOBENCH_API_PROVIDER=openai` | Direct OpenAI-compatible client; Python entry-point default |
| `PYTHON_BIN` | Override the Python executable |
| `GEOBENCH_RESULTS` | Override output/cache root; use a separate directory for smoke tests |
| `FOREGROUND=1` | Run the evaluation launcher synchronously; the all-stage launcher sets this |

Keep `*.run.json` metadata with CSVs when committing or moving results. Do not
commit credentials, the virtual environment, or lock files. Existing evaluation
outputs without metadata are not silently adopted; select a new results root.

## Validation

**24 tests passed** using the project environment, including:

- The original 9 offline tests.
- Interruption after two successful generations, resume of only the missing
  target, no repeated client initialization after completion, and rejection of
  changed generation settings.
- All 10 rewrite strategies with checkpoint/repeat behavior.
- Original and tagged zero-shot evaluated and summarized separately, shared
  clean-rank caching, no calls on a repeated evaluation, and rejection of a
  changed evaluation seed.
- BlockRun and bearer-client mapping, retry/error handling, and invalid responses.
- The installed real BlockRun SDK against `httpx.MockTransport`, with a public
  unfunded test key and no real wallet or network. This verifies the request path,
  model name, response schema and adapter compatibility, not live payment.
- Local launcher dry-run from outside the checkout, and failure on bad paths.

Both launchers passed dry-run checks and shell syntax checks. The installed SDK
emits upstream Pydantic deprecation warnings; they did not fail validation.

## Workload and remaining research caveats

The checked-in manifests exactly match source data: ragroll 399, stsdata 30,
rewrite_to_rank 200, llm_rank_optimizer 40, cseo 60: **729 targets**.
Generation requires **7,290 + 729 = 8,019 calls**, before retries.

Existing instance CSVs contain clean 729, stealthrank 729, zero_shot 729 and
RAF optimized on Vicuna 466 rows. Adding the 11 generated files gives 10,672
rows across 15 files. With K=10 and an empty clean cache, evaluating all of these
requires approximately **114,010 ranking calls** (7,290 shared clean calls plus
106,720 per-row calls), or **122,029 total calls** including generation, before
retries. This is a request count, not a dollar estimate; ranking prompts contain
whole candidate lists. More files at launch increase the workload.

Existing RAF coverage is incomplete and STS instances are absent. These are
pre-existing limitations outside the requested scope. The C-SEO source still
marks the Authoritative prompt for upstream provenance verification; this
implementation does not change its wording or resolve that scientific question.

Before production: configure the credential type and endpoint, establish a run
budget, then test a few actual requests in a separate output/cache directory.
No live credentials, balances, authentication or inference were tested here.
