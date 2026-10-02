# llm-evals

LLM evaluations, accumulated one study at a time. Each study under `studies/`
is self-contained (data download, prompts, scorers, runner, analysis, results)
and shares `common/`: model and provider pins, the OpenRouter client, and paired
statistics.

## Studies

| Study | What it measures | Status |
|---|---|---|
| [`studies/2026-10-korean`](studies/2026-10-korean/README.md) | Korean ability of 6 budget-tier models: linguistic knowledge (KoBALT), Korea-specific factuality (KoSimpleQA), NER (KLUE-NER), long-document classification (LBox casename) | KoBALT, KLUE-NER, LBox done for 4 models; Gemma 4 31B/26B dropped (not runnable normally via OpenRouter); KoSimpleQA in TODO |
| [`studies/2026-10-hanifeval`](studies/2026-10-hanifeval/README.md) | HanIFEval v1 (formerly Ko-IFEval v1): Korean IFEval translated jointly with its checker kwargs (Gemini 3.1 Pro), audited against IFEval-Ko, reviewed by 8 Claude reviewers, 17 logged edits | Release v1 (429 items; satisfiability strict 426/429). 4 models evaluated: DeepSeek V4.1 Flash 97.2% prompt-level strict, GLM 5.3 Flash 95.3, GPT-6 Luna 93.5, Solar Pro 4 93.2; model-validated, no human review |

## Layout

| Path | Contents |
|---|---|
| `common/models.py` | models under test, pinned providers, prices; the smoke-test model |
| `common/openrouter.py` | one chat call; retries infrastructure failures, never truncations |
| `common/stats.py` | exact McNemar, Wilson interval |
| `studies/<date>-<topic>/` | one study: `download_data.sh`, `tasks/`, `run.py`, `analyze.py`, `tests/`, results |
| `CLAUDE.md` | rules every study follows (scoring, infrastructure failures, data licences) |

## OpenRouter provider limits (observed)

Model/provider pins that could not take concurrent requests. A 429 row is an
infrastructure failure: it is retried and never scored. The caps below are in
`common/models.py` (`MODEL_CONCURRENCY_CAP`). Add a row whenever a new limit is
seen.

| Model | Pinned provider | Observed | Date | Setting now |
|---|---|---|---|---|
| `google/gemma-4-31b-it` | Crusoe (bf16) | HTTP 429 "temporarily rate-limited upstream": 17 of 150 pilot rows at 8 in flight after 6 retries; 100 of 836 main-run rows (12%) at 4 in flight after 8 retries (≥30 s backoff); about 736 items in 6.5 h | 2026-09-29/30 | **dropped from the Korean study**; Crusoe was the only bf16 provider up |
| `google/gemma-4-26b-a4b-it` | CoreWeave (bf16) | HTTP 429, same message: 13 of 48 pilot rows at 8 in flight; 2 of 3 rows at 2 in flight after 8 retries; 4 of 4 short probe calls sent together | 2026-09-29 | **pin moved to NextBit (bf16)**, which served 4 of 4 concurrent probes, as did Parasail and Cloudflare |

The other pins in `common/models.py` (DeepSeek V4.1 Flash on StreamLake,
GPT-6 Luna on OpenAI, GLM 5.3 Flash on Z.AI, Solar Pro 4 on Upstage) left no
429 row in the 2026-09-29 pilots at 8 in flight. The harness retries 429s
before logging, so a row appears only when every retry failed.

## Setup

```bash
uv venv .venv && uv pip install --python .venv/bin/python -r requirements.txt
cp .env.example .env    # add OPENROUTER_API_KEY
set -a; source .env; set +a
```

Then follow the study's README.

## License

Apache-2.0 for this project's code, logs and write-ups ([LICENSE](LICENSE)).
Third-party code and dataset licences: [NOTICE](NOTICE). Evaluation data is
fetched at run time and not redistributed.

## Repository history

The git history was squashed into a single commit on 2026-10-02, when the
repository was made public. Harness revisions that the study write-ups
mention from before that date are described in the text rather than linked.
