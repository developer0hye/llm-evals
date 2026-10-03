# Korean ability of budget-tier LLMs (2026-10)

**Status (2026-10-03): KoBALT, KLUE-NER and LBox main runs are complete for 5
models:**
- DeepSeek V4.1 Flash, GPT-6 Luna, GLM 5.3 Flash and Solar Pro 4, run on
  2026-09-29/30;
- Solar Mini 4, added on 2026-10-03 (see
  [Added model: Solar Mini 4](#added-model-solar-mini-4-2026-10-03)).
**Gemma 4 31B and Gemma 4 26B were dropped.** Neither could be evaluated
normally through OpenRouter under this protocol (see
[Not evaluated](#not-evaluated-gemma-4-31b-and-gemma-4-26b)). KoSimpleQA has
not been run (see [TODO](#todo)).

## Results: 4 models × 3 tasks (main run, 2026-09-29/30)

Setup: reasoning on (OpenRouter medium effort), `max_tokens = 64000`,
temperature 0, one sample per item, each model on its pinned provider. Rows
are in `results/<model>/`, and every number below is recomputed by

```bash
python3 analyze.py results --models deepseek-v4.1-flash gpt-6-luna glm-5.3-flash solar-pro4 --md results/SUMMARY.md
```

The run left 0 errored rows, and every row was served by the pinned provider
(StreamLake, OpenAI, Z.AI, Upstage). Tests are within a task, Bonferroni over
the 6 model pairs (α = 0.0083). Rows came from two revisions of the
harness with identical scoring code; the later one only adds the in-process
credit guard (`--min-credit`).

### Key findings

1. **KoBALT and LBox split the four models into the same two tiers.**
   DeepSeek V4.1 Flash and GPT-6 Luna score above GLM 5.3 Flash and Solar Pro 4
   on both tasks: all 8 cross-tier tests are significant (p ≤ 0.0017), and
   none of the 4 within-tier tests is (p ≥ 0.36).
2. **GLM's low KoBALT score comes from non-termination, not wrong answers.**
   91 of 700 replies (13%) were still reasoning at 64k tokens. On the 609
   items it answered, GLM is 81.6% correct, level with the top tier (82.4–82.5%).
   Its truncations cluster in phonetics/phonology (19 of 62) and morphology
   (12 of 42).
3. **On LBox, the gap is only where the label does not leak.** When the case
   name appears in the facts (282 items), all four models score 93–94%. When
   it does not (718 items), they score 75–81%, and that is where the tiers
   separate.
4. **On KLUE-NER, DeepSeek leads and the other three are close.** DeepSeek's
   micro-F1 is above each of the others:
   - strict rule: by 2.2–3.8 points (p ≤ 0.0042);
   - lenient rule: by 1.8–2.3 points (p ≤ 0.0072).

   GPT-6 Luna's lower strict score is largely formatting. In 73 of its 79
   unparsed replies, the copy differed from the sentence only in trailing
   punctuation, mostly an added final period. Under the lenient rule, GPT-6
   Luna is not separable from GLM or Solar.
5. **Cost differs about elevenfold for the same three tasks.** All three
   tasks cost $0.83 on GPT-6 Luna, $3.15 on Solar, $7.49 on DeepSeek and $9.32
   on GLM. The gap follows output tokens: mean KoBALT output was 1,121 tokens
   for GPT-6 Luna against 19,368 for GLM.

### KoBALT (700 ten-option MCQ)

Accuracy = correct / 700. Truncated and unparsed replies count as not correct.

| Model | Accuracy [95% CI] | Of answered | Truncated | Unparsed | Cost |
|---|---|---|---|---|---|
| GPT-6 Luna | **0.824** [0.794, 0.851] | 0.824 | 0 | 0 | $0.42 |
| DeepSeek V4.1 Flash | **0.817** [0.787, 0.844] | 0.825 | 4 | 3 | $4.35 |
| Solar Pro 4 | 0.727 [0.693, 0.759] | 0.728 | 0 | 1 | $1.50 |
| GLM 5.3 Flash | 0.710 [0.675, 0.742] | 0.816 | **91** | 0 | $6.82 |

McNemar, where b is the number of items only the first model got right and c
the number only the second got right:

| Pair | b / c | p |
|---|---|---|
| DeepSeek vs GPT-6 Luna | 40 / 45 | 0.66 |
| DeepSeek vs GLM | 108 / 33 | **<0.0001** |
| DeepSeek vs Solar | 100 / 37 | **<0.0001** |
| GPT-6 Luna vs GLM | 118 / 38 | **<0.0001** |
| GPT-6 Luna vs Solar | 96 / 28 | **<0.0001** |
| GLM vs Solar | 67 / 79 | 0.36 |

By domain (accuracy; truncations in brackets). Phonology (n=62) and
morphology (n=42) are small: a 95% interval there is roughly ±11–14 points,
so read those two columns as indicative.

| Model | Syntax (300) | Semantics (215) | Pragmatics (81) | Phon. (62) | Morph. (42) |
|---|---|---|---|---|---|
| GPT-6 Luna | 0.867 | 0.777 | 0.716 | 0.871 | 0.905 |
| DeepSeek V4.1 Flash | 0.867 [2] | 0.767 [1] | 0.778 | 0.806 [1] | 0.810 |
| Solar Pro 4 | 0.777 | 0.744 | 0.605 | 0.645 | 0.643 |
| GLM 5.3 Flash | 0.783 [31] | 0.716 [17] | 0.741 [12] | 0.484 [19] | 0.429 [12] |

For scale, the best model in the KoBALT paper (Claude 3.7 Sonnet, early 2025,
`max_new_tokens` 2048, no reasoning mode) scored 0.61. The protocols differ, so
this is not a like-for-like comparison.

### LBox Open casename (1,000 items, 100 classes)

| Model | Accuracy [95% CI] | Label in facts (282) | Label not in facts (718) | Truncated / unparsed | Cost |
|---|---|---|---|---|---|
| DeepSeek V4.1 Flash | **0.846** [0.822, 0.867] | 0.936 | 0.811 | 0 / 1 | $1.15 |
| GPT-6 Luna | **0.845** [0.821, 0.866] | 0.940 | 0.808 | 0 / 0 | $0.28 |
| Solar Pro 4 | 0.814 [0.789, 0.837] | 0.933 | 0.767 | 0 / 2 | $0.41 |
| GLM 5.3 Flash | 0.807 [0.781, 0.830] | 0.943 | 0.753 | 13 / 9 | $1.46 |

| Pair | b / c | p |
|---|---|---|
| DeepSeek vs GPT-6 Luna | 34 / 33 | 1.00 |
| DeepSeek vs GLM | 66 / 27 | **0.0001** |
| DeepSeek vs Solar | 50 / 18 | **0.0001** |
| GPT-6 Luna vs GLM | 67 / 29 | **0.0001** |
| GPT-6 Luna vs Solar | 62 / 31 | **0.0017** |
| GLM vs Solar | 42 / 49 | 0.53 |

### KLUE-NER (1,000 dev sentences, entity-level micro-F1)

The strict rule is primary: a reply that alters the sentence scores zero
entities. The lenient rule forgives only trailing punctuation or whitespace.
Both were pre-registered. The 95% CIs and the paired tests are a sentence-level
bootstrap (10,000 resamples), which was added after the main run and was not
pre-registered.

| Model | F1 strict [95% CI] | Parse rate | F1 lenient | News (500) / reviews (500), strict | Cost |
|---|---|---|---|---|---|
| DeepSeek V4.1 Flash | **0.786** [0.768, 0.804] | 0.979 | **0.787** | 0.753 / 0.870 | $2.00 |
| GLM 5.3 Flash | 0.764 [0.745, 0.783] | 0.978 | 0.764 | 0.732 / 0.844 | $1.03 |
| Solar Pro 4 | 0.764 [0.744, 0.782] | 0.970 | 0.764 | 0.730 / 0.848 | $1.23 |
| GPT-6 Luna | 0.748 [0.729, 0.766] | 0.921 | 0.768 | 0.733 / 0.789 | $0.14 |

| Pair | ΔF1, p (strict) | ΔF1, p (lenient) |
|---|---|---|
| DeepSeek vs GLM | +0.022, **0.0014** | +0.023, **0.0008** |
| DeepSeek vs GPT-6 Luna | +0.038, **<0.0001** | +0.018, **0.0072** |
| DeepSeek vs Solar | +0.022, **0.0042** | +0.023, **0.0022** |
| GLM vs GPT-6 Luna | +0.016, 0.035 | −0.005, 0.50 |
| GLM vs Solar | +0.000, 0.97 | +0.000, 0.97 |
| GPT-6 Luna vs Solar | −0.016, 0.040 | +0.005, 0.49 |

All four models score lower on news than on movie reviews. In the 1,000
evaluated sentences, news sentences average 70.8 characters and 4.08 gold
entities, against 40.8 characters and 1.68 entities for reviews. That
difference in length and entity density is not tested as a cause here.

### Caveats that bound these results

- **One configuration per model.** Each model runs on one pinned provider at
  medium reasoning effort with one sample per item. Repeat runs were not made,
  so run-to-run variance is not measured.
- **Contamination is not controlled.** All three sets were public with their
  answers before these models were released: KLUE in 2021, LBox in 2022,
  KoBALT in 2025-05.
- **KLUE-NER is scored on dev**, because the test labels are withheld. Every
  dev sentence contains at least one entity, so false positives on entity-free
  text are not measured.
- **LBox labels overlap structurally**, e.g. 건물명도(인도) vs 건물인도, so 100% is
  not reachable. Its facts are public court precedents.


## Added model: Solar Mini 4 (2026-10-03)

`upstage/solar-mini4` (released on OpenRouter 2026-09-23), pinned to
Upstage. It was run with the same settings as the four models above:
- reasoning on, `max_tokens` 64000, temperature 0;
- the same item sets.

**Statistics.** It was added after the main run, so it is tested in its
own family: the 4 pairs that include it, Bonferroni α = 0.0125
(`analyze.py --focus solar-mini4`). The 6-pair family of the original
four models is unchanged. Rows are in `results/solar-mini4/`; the summary
is in `results/SUMMARY_solar-mini4.md`.

| Task | Solar Mini 4 | Solar Pro 4 | vs each of the other four models |
|---|---|---|---|
| KoBALT accuracy (n=700) | **0.591** | 0.727 | lower than all four, p < 0.0001 |
| KLUE-NER micro-F1 (n=1000) | **0.651** [0.626, 0.676] | 0.764 | lower than all four, p < 0.0001 (paired bootstrap) |
| LBox casename accuracy (n=1000) | **0.770** | 0.814 | lower than all four, p ≤ 0.0025 |

**Solar Mini 4 is the weakest of the five models on all three tasks**,
significantly so in every pairwise test. The gap to Solar Pro 4 is
13.6 points on KoBALT (34 vs 129 discordant items), 0.113 F1 on NER and
4.4 points on LBox (33 vs 77).

**Run record.**
- **Rows.** 2,700/2,700 rows scored, 0 errored, every row served by
  Upstage. Cost $3.32: KoBALT $1.61, NER $0.95, LBox $0.76.
- **Pilot.** The pilot (50 items per task, `pilot/solar-mini4/`) had 0
  errors and 0 truncations.
- **Low NER parse rate.** In the pilot, all 8 of 50 NER replies that
  failed to parse were copy errors by the model, not parser misses:
  - dropped words ("선고");
  - duplicated words ("연내 연내", "6시2분분");
  - a changed particle ("두개는" → "두개은");
  - a dropped closing parenthesis.

  01689's ᄏ (U+110F) is in the source sentence itself, so it is not a
  normalisation artefact. The main run's parse rate is 84.1%: 159
  unparsed, the lowest of the five models.
- **Truncations.** KoBALT 2, LBox 1. LBox 1896 shows a degenerate loop in
  the visible content:
  - the reasoning reached the correct label '근저당권말소' in 930 tokens;
  - the content then repeated "사건명: 근저당권설정등기? No." 1,892 times
    until it hit 64,000 tokens.

  Per protocol it is scored `no_answer_truncated`.
- **Throughput.** KoBALT took 9,162 s for its 700 items, about 4.6 items
  per minute (mean 11.4k output tokens per item). The run was
  first started as one process doing the tasks in order. It was stopped
  after 117 KoBALT rows (killed by exact PID) and restarted as one process
  per task. The resume kept the 117 logged rows; no row was lost or run
  twice. At 24–32 requests in flight, 0 rows ended in an error. Retries
  are not logged, so whether any 429s were retried is unknown.


Four tasks, each measuring a different Korean ability. They are reported
separately, never pooled.

| Task | Ability | Eval set | Scoring | Judge |
|---|---|---|---|---|
| **KoBALT** ([arXiv:2505.16125](https://arxiv.org/abs/2505.16125)) | Korean linguistic knowledge: syntax 300, semantics 215, pragmatics 81, phonetics/phonology 62, morphology 42 | all 700, 10-option MCQ | accuracy over all items | no |
| **KoSimpleQA** ([arXiv:2510.18368](https://arxiv.org/abs/2510.18368)) | Korea-specific factual knowledge and whether the model declines rather than invents | all 938, short answer | CO / NA / IN / NR / CGA / F | yes |
| **KLUE-NER** ([arXiv:2105.09680](https://arxiv.org/abs/2105.09680)) | extracting 6 entity types from Korean news and movie-review text | 1,000 of the 5,000 dev sentences (500 news + 500 reviews; test labels withheld) | entity-level exact (start, end, type) micro-F1 | no |
| **LBox Open casename** ([arXiv:2206.05224](https://arxiv.org/abs/2206.05224)) | reading a court judgment's facts (mean 773 chars) and classifying the case name | test, 1,000 items, 100 classes × 10 | accuracy; split by label leak | no |

Models: the six in [`common/models.py`](../../common/models.py), each pinned to one
OpenRouter provider (fallbacks off): DeepSeek V4.1 Flash (StreamLake fp8),
GPT-6 Luna (OpenAI), GLM 5.3 Flash (Z.AI fp8), Solar Pro 4 (Upstage),
Gemma 4 26B A4B (NextBit bf16), Gemma 4 31B (Crusoe bf16). Gemma 4 26B was
first pinned to CoreWeave bf16, which rate-limited nearly every call (see the
limits table in the root README), so it moved to NextBit before any main run;
the partial CoreWeave pilot is kept in `pilot_coreweave_gemma26b/`. A one-call probe on
2026-09-29 confirmed that each pin is served by the named provider, returns
reasoning tokens and reports `usage.cost`.

Protocol for all tasks: temperature 0, `reasoning: {enabled: true}`
(OpenRouter medium effort), `max_tokens = 64000`, one sample per item.
Per-call timeout is 3,600 s (64k tokens at GLM/Solar's ~40 tokens/s needs about
1,600 s). Gemma 4 26B and 31B run at most 2 requests in flight, because both
pinned providers returned upstream rate limits (HTTP 429) at 8.

**Why 64k, not 16k (decided 2026-09-29, before any main-run score).** A first
pilot at 16k (`pilot_16k/`, kept as design data) truncated on KoBALT for most
reasoning models. All truncated replies spent the whole budget on reasoning
with empty content. Counts are of 50 items, errored rows excluded:

| Model | Truncated at 16k |
|---|---|
| Gemma 4 26B | 32/35 |
| GLM 5.3 Flash | 21/50 |
| DeepSeek V4.1 Flash | 15/50 |
| Solar Pro 4 | 9/50 |
| Gemma 4 31B | 2/41 |
| GPT-6 Luna | 0/50 |

Five of DeepSeek's truncated items were re-run at 64k (`pilot_16k_diag_64k/`).
All five finished on their own, in 2,649, 6,565, 11,380, 17,393 and 28,422
tokens, and 4 of the 5 were correct. The same item at temperature 0 can
therefore run past 16k on one call and finish in 2.6k on the next. At 16k, a
KoBALT score would largely measure which models happened to finish in time.

## Scoring rules, per task

Common to all four: a reply cut at `max_tokens` is `no_answer_truncated` and is
never parsed; a finished reply without an explicitly stated answer is
`no_answer_unparsed`; API/transport failures and judge failures are retried and
never scored. Every rule below is covered by `tests/test_scoring.py` (17 tests,
synthetic responses, no network).

- **KoBALT.** Prompt is the official template, read at run time from the
  dataset's `evaluation_protocol.md`. The answer is the last "정답은 X입니다"
  (X in A–J); no fallback to letters elsewhere in the text. Key defect: item
  `67c81c5d361c7932636b7c14` has options B and E both "(5)" (gold B); both are
  accepted. Deviation from the paper: `max_tokens` 16000 instead of 2048.
- **KoSimpleQA.** The model gets the question alone. The grader prompt is
  SimpleQA's, vendored from `openai/simple-evals@652c89d` (MIT). Two deviations
  from the paper:
  - The paper's Appendix E counter-examples, which move vague answers and false
    refusals from NOT_ATTEMPTED to INCORRECT, are **not applied**: the paper is
    on arXiv's non-exclusive licence, so its prompt text is not copied. Expect
    NA higher and IN lower than the paper's grader would give.
  - simple-evals maps an unparseable grader reply to NOT_ATTEMPTED; here it is
    a judge error (retried), so judge failures never look like the model
    declining.

  NR counts truncated or empty replies: no credit, but not counted as INCORRECT
  (that would inflate the hallucination rate).
- **KLUE-NER.** Gold spans come from the per-character BIO rows (5,000
  sentences, 14,257 entities, matching KLUE Table 9). The model copies the
  sentence and wraps entities as `⟦text|TYPE⟧` on a final `결과:` line; the three
  delimiter characters never occur in the dev text (the KLUE `<text:TAG>` form
  would be ambiguous: 18 dev sentences contain `<` or `>`). A reply counts only
  if removing the markers reproduces the sentence exactly; otherwise it is
  unparsed and all its gold entities count as missed. The prompt is written for
  this study (not taken from another harness).
- **LBox casename.** All 100 labels (derived from the file) are listed in the
  prompt; the final `사건명:` line must be exactly one of them. `label_leak`
  marks items whose case name (heuristic: first offence, `위반` and
  parentheticals removed) appears verbatim in the facts: 282 of 1,000.

## Caveats known before any run

- **Contamination.** KoBALT (2025-05), KLUE (2021) and LBox (2022; public
  precedents) are public with answers. KoSimpleQA answers are public too, and
  it covers facts up to 2023-12-31.
- **KLUE-NER** is scored on dev, not test. All 5,000 dev sentences contain at
  least one entity, so false positives on entity-free text are not measured.
- **LBox** has structurally overlapping labels (`건물명도(인도)` vs `건물인도`,
  `손해배상` vs `손해배상(기)`, compound labels), so 100% is not reachable.
- **KoSimpleQA** scores depend on the judge (see below).

## Pre-registered before any pilot or main-run score (2026-09-29)

- **Item sets** (`subsets.json`, from `make_subsets.py`):
  - `golden`: 10 per task, for smoke runs.
  - `pilot`: 50 per task, disjoint from golden, for measuring each model's
    token use and parse rates.
  - `main`: the reported set. KoBALT 700, KoSimpleQA 938, LBox 1,000, and
    KLUE-NER 1,000 dev sentences (500 wikitree + 500 nsmc, seed 2).
  - Pilot and golden scores are never reported as results.
- **KLUE-NER:** the strict exact-copy rule is primary. As a sensitivity check,
  `analyze.py` re-parses every unparsed reply with `lenient=True`, which
  forgives differences only in trailing punctuation or whitespace, and reports
  both. It also reports micro-F1 separately for news and reviews.
- **LBox:** accuracy is reported overall and split by `label_leak`.
- **Order of work:** KoBALT, KLUE-NER and LBox (no judge) run first.
  KoSimpleQA waits until the judge is chosen.

## Golden samples and smoke run

The golden subset holds 10 item ids per task, stratified:
- KoBALT: 2 per domain, including the duplicate-option item.
- KoSimpleQA: 1 per topic.
- KLUE-NER: 5 news + 5 reviews, including a sentence with a literal `<`.
- LBox: 5 criminal + 5 civil, mixing leak and no-leak items.

Smoke run, 2026-09-29: `gpt-6-luna-flex` (`openai/gpt-6-luna` on OpenAI's flex
tier, the cheapest pin that probed cleanly), also used as the KoSimpleQA judge.
Rows in [`smoke/`](smoke/), summary in [`smoke/SUMMARY.md`](smoke/SUMMARY.md); produced by an earlier revision of the harness (see the root README, Repository history).

| Task | n | Outcomes | Pipeline observations |
|---|---|---|---|
| KoBALT | 10 | 10 correct | every reply ended with "정답은 X입니다"; the duplicate-option item parsed (B) |
| KoSimpleQA | 10 | 9 correct, 1 incorrect | 10 judge calls, all returned a bare letter |
| KLUE-NER | 10 | 9 parsed, 1 unparsed | the unparsed reply added a trailing "." to the sentence, so the exact-copy rule rejected it (working as specified) |
| LBox | 10 | 8 correct, 2 wrong | both errors are label-set issues: one compound label with an omitted part, one 매매대금 → 약정금 |

- 0 API errors, 0 judge errors, 0 truncations. Resuming skipped all 40 logged
  rows, a changed judge was refused by the settings guard, and `--subset all`
  without `--confirm-full` was refused.
- **Judge leniency seen in the smoke run.** Item 435 (gold 크래프톤) was graded
  CORRECT for "펍지 주식회사", a subsidiary. Before a full run, fix the judge
  model and measure its agreement on a hand-checked sample (see next steps).
- **Smoke cost:** $0.0083 for 40 items plus 10 judge calls ($0.0074 model, $0.0009 judge). Projected
  main-set cost for this model: KoBALT $0.23, KoSimpleQA $0.17, KLUE-NER $0.10 (1,000 sentences), LBox
  $0.22 (`analyze.py`, from $/item × set size).
- **Other models will cost more.** gpt-6-luna-flex is the cheapest pin and the
  tersest reasoner (mean 301–1,261 output tokens per item here). The earlier
  estimate for the six models, about $25 with a cheap judge and $60 with
  GPT-4o, still stands until each model's own pilot measures its token use.

## Reproducing

```bash
./download_data.sh                        # pinned revisions, SHA-256 checked
../../.venv/bin/python -m pytest -q tests # offline scorer tests
set -a; source ../../.env; set +a
../../.venv/bin/python run.py --models gpt-6-luna-flex --judge gpt-6-luna-flex --out smoke
../../.venv/bin/python analyze.py smoke --md smoke/SUMMARY.md
```

The main run requires `--subset main --confirm-full`; the per-model pilot is
`--subset pilot`.

## 64k pilot and the main-run plan (2026-09-30)

Pilot at the final settings, rows in `pilot/`: 50 items per task and model.
GLM and Gemma 4 31B were stopped after 44 and 29 KoBALT items, and Gemma 4
26B after 6. KoBALT truncations at 64k:

| Model | Truncated at 64k |
|---|---|
| Gemma 4 26B | 4/6 |
| GLM 5.3 Flash | 12/44 |
| DeepSeek V4.1 Flash | 2/50 |
| Gemma 4 31B | 1/29 |
| Solar Pro 4 | 0/50 |
| GPT-6 Luna | 0/50 |

The remaining truncations do not look like a cap problem. The logged
reasoning tails show endless re-checking ("let me re-check …", "Hmm, hmm …
let me reconsider") or a finished decision repeated in the reasoning
("정답은 H입니다. I'll output." over and over). They count as
`no_answer_truncated`, as specified.

Projected main-run cost from the pilot's $/item (the 16k pilot's rate where
the 64k pilot has no rows for KLUE-NER/LBox, which barely truncated):

| Model | KoBALT | KLUE-NER | LBox | Sum |
|---|---|---|---|---|
| DeepSeek V4.1 Flash | $5.97 | $2.27 | $1.15 | $9.39 |
| GLM 5.3 Flash | $9.81 | $1.46 | $0.54 | $11.81 |
| Gemma 4 26B | $10.27 (n=6) | ? | ? | ≥$10.27 |
| Solar Pro 4 | $2.00 | $1.39 | $0.51 | $3.90 |
| Gemma 4 31B | $2.07 | $0.49 | $0.51 | $3.07 |
| GPT-6 Luna | $0.47 | $0.17 | $0.26 | $0.89 |

The total, at least $39.34, is about equal to the $40.32 then reported as remaining. That figure was the API key's own limit (`/api/v1/key` `limit_remaining`), not the account balance; the account balance (`/api/v1/credits`) is shared with other keys and projects and was not checked at the time. The credit guard has used the smaller of the two since 2026-10-01.
The main run therefore goes in this order:
1. The five other models, all three tasks (about $29).
2. Gemma 4 26B: KLUE-NER and LBox pilot first. Its KoBALT main run (at least
   $10, and at the observed ~25 min per truncated call, days of wall-clock)
   waits for a budget decision.

`run.py --min-credit 2` stops new calls if spendable credit (the smaller of the account balance and the key's limit) falls
below $2. An external watcher was tried first and could not see the run
processes from a background shell, so the check moved into `run.py`.

## Not evaluated: Gemma 4 31B and Gemma 4 26B

Decided 2026-09-30. Both models fail under this protocol (one pinned bf16
provider, reasoning on, `max_tokens` 64k), for different reasons. Their
partial rows are design data only: `excluded/gemma-4-31b-incomplete/` and
`pilot*/gemma-4-26b/`.

- **Gemma 4 31B: infrastructure.**
  - Crusoe was the only bf16 provider that was up on 2026-09-29 (Novita bf16
    was down).
  - Crusoe rate-limits upstream. At 4 requests in flight, 100 of 836 LBox
    calls (12%) still ended in HTTP 429 after 8 retries, and the run finished
    736 items in about 6.5 hours.
  - At that rate, KLUE-NER and KoBALT would take well over a day, and every
    429 row needs another pass.
  - The model itself did not fail: 613 of the 736 finished LBox items were
    correct (0.833), and on KoBALT 1 of 29 pilot items truncated at 64k.
    These partial numbers are not results.
- **Gemma 4 26B: the model does not terminate.**
  - With reasoning on, it repeats the same check until the cap, e.g. "Wait,
    I'll check if '도쿄전력' is '도쿄전력' or '도쿄 전력'".
  - This happened on two providers: CoreWeave (16k pilot, KoBALT 32/35
    truncated) and NextBit (64k pilot, KoBALT 4/6, KLUE-NER 23/50).
  - LBox was mostly fine (3/50 truncated, 44/50 correct).
  - A main run would mostly measure non-termination, at a projected $21 for
    the three tasks.

Not tried, and each would change the comparison:
- 31B on an fp8 provider (Parasail, DeepInfra), which gives a different
  quantization from the other pins.
- 26B with reasoning off, which is a different condition from the other
  models.
- Self-hosting either model (e.g. vLLM), which is a different serving stack.

## TODO

1. **KoSimpleQA: judge not chosen.** The paper used GPT-4o ($2.50/$10). Any
   cheaper judge must first be checked against GPT-4o or hand grades on about
   100 items, with the agreement reported. The smoke run already showed one
   lenient grade (펍지 주식회사 accepted for 크래프톤). The judge must not be a
   model under test grading itself.
2. **Optional:** IFEval-Ko (342 items, rule-based, no judge) would cover
   Korean generation and instruction following, which none of the current
   tasks measures.
3. **Optional:** a replacement for the dropped Gemma models, run under the
   same protocol, if one is wanted.
