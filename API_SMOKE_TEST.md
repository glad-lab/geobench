# BlockRun API-key smoke test

Date: 2026-09-09. Scope: GPT-4o-mini for the first three revision tasks.

**Result: PASS for the sampled requests.** This does not establish full-dataset success, sustained throughput or total cost.

- Provider mode: `blockrun-openai`
- Base URL: `https://api.blockrun.ai/v1`
- Requested model: `openai/gpt-4o-mini`
- Reported model on all four successful responses: `gpt-4o-mini-2024-07-18`
- Authentication: user-supplied account key, entered through hidden stdin and held in process memory. The key is not included in this file, experiment data, or code.

| Test | HTTP | Prompt tokens | Output tokens | Seconds | Validation |
| --- | ---: | ---: | ---: | ---: | --- |
| cseo_fluency | 200 | 234 | 55 | 3.59 | Nonempty postprocessed rewrite |
| zero_shot | 200 | 151 | 23 | 0.88 | 23-token suffix, below requested 50-token limit |
| rank_clean | 200 | 681 | 64 | 1.23 | All 10 candidate names parsed |
| rank_manipulated | 200 | 704 | 64 | 1.18 | All 10 candidate names parsed |

Successful inference usage: 1770 input + 206 output = 1976 tokens. Billing amounts were not returned in the inspected response fields; no invoice total is claimed.

The sample used one target from `stsdata/books`, the repository fluency/zero-shot prompts and generation parameters, and the unified ranking prompt. Each ranking used one ordering for connectivity validation; this was not the full K=10 protocol. No output was added to `results/unified/`.

Before locating the account endpoint, six requests to the wallet gateway at `https://blockrun.ai/api/v1` returned HTTP 402 Payment Required and produced no model responses. A diagnostic HTTP response hook caused these to be wrapped as connection errors and retried; the hook was corrected for the successful test. These six unsuccessful requests are separate from the four successful inference requests above.

For later use, configure the nonsecret settings `GEOBENCH_API_PROVIDER=blockrun-openai` and `OPENAI_BASE_URL=https://api.blockrun.ai/v1`, and provide the account key locally via `OPENAI_API_KEY`. Do not use this account key as `BLOCKRUN_WALLET_KEY`. No key has been persisted by this test.

No DeepSeek, Llama, full batch, or long-running concurrency test was run.
