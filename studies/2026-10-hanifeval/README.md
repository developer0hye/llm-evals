# HanIFEval: a checker-consistent Korean translation of IFEval (v1.1, 2026-10)

**Naming.** HanIFEval was called "Ko-IFEval v1" until 2026-10-03. The name was
changed because four Hugging Face datasets already use Ko-IFEval-style names:
`allganize/IFEval-Ko`, `thunder-research-group/SNU_Ko-IFEval`,
`davidkim205/ko-ifeval` and `global-llm-2024/ko_ifeval`. HanIFEval is not
derived from any of them. It is translated from `google/IFEval`, and
IFEval-Ko was used only as the audited comparison.

**Status (2026-10-03): v1.1 is the current release** (`release/hanifeval_v1.1.jsonl`,
Hugging Face `developer0hye/HanIFEval`). It was made after two external
reviews of v1:
- 16 items were edited;
- the checker was fixed (sentence splitter, undetectable language);
- three fields were added (`answer_language`, `adaptation`, `edits`).

v1 (`release/hanifeval_v1.jsonl`) is unchanged and kept. NOTES §10 has
every finding, ruling and re-score.

**No native-speaker review was done, and none is planned.** The items are
validated by code (prompt↔kwargs checks, satisfiability, 37 checker tests)
and by models (Gemini translated, Claude reviewers), not by humans.

## Results on v1.1: 5 models × 429 items (2026-10-03)

v1.1 results are assembled by `build_v11_eval.py` and written to
`eval/v1.1/`:
- the 16 edited items were re-generated (`eval/v1.1_regen/`);
- the other 413 items reuse the v1 responses, re-scored with the v1.1
  checker.

```bash
python3 analyze_eval.py eval/v1.1 --release 1.1 --models deepseek-v4.1-flash gpt-6-luna glm-5.3-flash solar-pro4
python3 analyze_eval.py eval/v1.1 --release 1.1 --models deepseek-v4.1-flash gpt-6-luna glm-5.3-flash solar-pro4 solar-mini4 --focus solar-mini4
```

| Model | prompt strict [95% CI] | quality-controlled (n=421) | prompt loose | inst strict | inst loose |
|---|---|---|---|---|---|
| DeepSeek V4.1 Flash | **97.2** [95.2, 98.4] | 98.1 | 97.7 | 97.9 | 98.4 |
| GLM 5.3 Flash | 95.3 [92.9, 97.0] | 96.2 | 97.2 | 96.8 | 98.1 |
| GPT-6 Luna | 93.2 [90.5, 95.3] | 94.1 | 94.2 | 95.1 | 95.7 |
| Solar Pro 4 | 93.0 [90.2, 95.1] | 94.1 | 95.3 | 95.1 | 96.8 |
| Solar Mini 4 | 92.5 [89.7, 94.7] | 93.3 | 95.6 | 94.6 | 96.8 |

"Quality-controlled" is the same metric over the 421 items without
`known_issues`.

**Paired tests (McNemar exact, prompt-level strict).**
- **First four models, Bonferroni over their 6 pairs:**
  - DeepSeek > GPT-6 Luna (22 vs 5 discordant, p = 0.0015);
  - DeepSeek > Solar Pro 4 (22 vs 4, p = 0.0005);
  - the other four pairs are not significant.
- **Solar Mini 4, added after the main run, tested in its own family of 4
  pairs:**
  - DeepSeek > Mini 4 (26 vs 6, p = 0.0005);
  - Mini 4 vs Luna, GLM and Pro 4: not significant (p ≥ 0.096).
  - Mini 4 scores 83.3% on the 30 `response_language` items. Its five
    failures there were checked by hand: two are refusals or answers in
    the wrong language, three break other instructions. None is a
    language-detection error.

**v1 → v1.1.** Scores moved by at most 0.3 points: Luna 93.5 → 93.2, Solar
Pro 4 93.2 → 93.0, the others unchanged. Both changed rows fail an
instruction the edit did not touch, so they are re-generation variance.
The ranking and the significant pairs are unchanged.

The v1 analysis follows (4 models, `eval/main/`). Its numbers are
unchanged, and re-scoring with the v1.1 checker changes 0 rows.

## Results on v1: 4 models × 429 items (2026-10-02)

Prompt-level strict is the share of items in which every instruction is
followed; n = 429 per model. All rows are in `eval/main/`, and the numbers
are recomputed by

```bash
python3 analyze_eval.py eval/main --models deepseek-v4.1-flash gpt-6-luna glm-5.3-flash solar-pro4 --md eval/main/SUMMARY.md
```

| Model | prompt strict [95% CI] | prompt loose | inst strict | inst loose | cost |
|---|---|---|---|---|---|
| DeepSeek V4.1 Flash | **97.2** [95.2, 98.4] | 97.7 | 97.9 | 98.4 | $0.731 |
| GLM 5.3 Flash | 95.3 [92.9, 97.0] | 97.2 | 96.8 | 98.1 | $0.899 |
| GPT-6 Luna | 93.5 [90.7, 95.4] | 94.4 | 95.3 | 95.9 | $0.159 |
| Solar Pro 4 | 93.2 [90.5, 95.3] | 95.6 | 95.3 | 97.0 | $0.466 |

Settings are the same as `studies/2026-10-korean`: pinned providers
(StreamLake, OpenAI, Z.AI, Upstage), reasoning on at the provider default,
temperature 0, `max_tokens` 64000, one sample. 1,716/1,716 rows were scored,
with 0 errors and 0 truncations.

1. **DeepSeek V4.1 Flash is ahead of GPT-6 Luna and Solar Pro 4.** McNemar
   exact on prompt-level strict, Bonferroni over 6 pairs (α = 0.0083):
   - vs GPT-6 Luna: 21 vs 5 discordant items, p = 0.0025;
   - vs Solar Pro 4: 21 vs 4, p = 0.0009.

   DeepSeek vs GLM (p = 0.13) and the three pairs among GLM, Luna and
   Solar (p ≥ 0.16) are not significant.
2. **The benchmark is near ceiling for these models.** 366/429 items are
   passed by all four, so 63 items carry every difference.
   - The 4 items no model passes are the 3 tagged
     `source_unsatisfiable_strict` and 2859. 2859 is an XML
     sentence-count trap inherited from the English item.
   - Removing the 5 known-issue items moves each model by ≤ 0.7 points
     and changes no ordering.
3. **Each model has one distinct weak instruction type** (instruction-level
   strict):
   - Solar Pro 4 `number_words` 72.1%: all 12 failures fall short of an
     eojeol minimum, at 43–97% of the target;
   - GPT-6 Luna `number_paragraphs` 63.6%: it ignores the `***` divider
     the prompt names;
   - GLM 5.3 Flash `forbidden_words` 84.4%: it restates the forbidden
     word while saying it avoided it.
4. **The ranking differs from Korean knowledge tasks.** GPT-6 Luna was in
   the top tier on KoBALT and LBox (`studies/2026-10-korean`) but ties for
   last here.

**No item defect surfaced in the model outputs.** Every
`forbidden_words` and `repeat_prompt` failure, and every GPT-6 Luna
paragraph failure, was checked against the response. All are model
failures under the checker; none is a substring-collision false fail
(NOTES §8). Total cost was $2.409, pilot included.

HanIFEval v1 is a Korean translation of `google/IFEval@966cd89`. It differs
from a plain translation in one respect: every item is translated *together
with* the arguments of the rule-based checker that scores it. The Korean
prompt and the checker kwargs therefore say the same thing, which is the
property that existing translations break.

Hugging Face: [`developer0hye/HanIFEval`](https://huggingface.co/datasets/developer0hye/HanIFEval).

The research log, with every decision, number and dead end, is
[`NOTES.md`](NOTES.md). This README summarises it.

## Why another Korean IFEval

We audited `allganize/IFEval-Ko@54199e3` (342 items; NOTES §1). In 27/342
items (7.9%), the Korean prompt and the checker disagree. Examples:
- "more than 2 times" was translated as "2번 이상" while the checker counts
  ≥ 3;
- forbidden words were present in kwargs but never stated in the prompt;
- repeat instructions lost their "nothing before the repetition" clause.

The defects come from the procedure (prompt translated alone, kwargs
patched separately), not from translation quality. On 120 WMT24++ en→ko
segments, MetricX-24 does not separate GPT-4o from Gemini 3.1 Pro, Gemini
3.8 Flash or Claude Opus 5.5 (NOTES §2).

## Construction

| Step | What | Result |
|---|---|---|
| Scope | IFEval minus 112 items with `change_case:*` / `keywords:letter_frequency` (no Korean equivalent) | 429 items, 21 instruction types, 633 instructions |
| Checker | IFEval-Ko checker with 5 marked fixes: seeded langdetect, escaped substring match for keywords and forbidden words, prefix match for a paragraph's first word | [`checker_semantics.md`](checker_semantics.md) |
| Guideline | System prompt fixed before translation: joint prompt+kwargs translation, numbers/relations from kwargs through a fixed table ("N 이상" / "N 미만"), word counts as "N단어(띄어쓰기 기준)" | [`translation_guideline.md`](translation_guideline.md) v1.1 |
| Translator | `google/gemini-3.1-pro-preview`, pinned to Vertex flex, reasoning high, temperature 0 | 429/429 ok, $3.689 |
| Pilot | 28 items covering all types + the 7 known IFEval-Ko defects | all 7 fixed; guideline v1.0 → v1.1 |
| Validator | deterministic prompt↔kwargs checks ([`validate.py`](validate.py)) | 9/429 flagged, 0 translation defects (19/429 with the post-hoc `repeat_conflict` check; 12/429 on the release, all adjudicated) |
| Semantic review | 8 Claude Opus 5.5 reviewers (a different model family from the translator), all 429 items | 70 findings on 60 items; 15 break scoring |
| Corpus screen | every Korean keyword / forbidden string against KLUE-NER dev eojeol ([`lexical_collisions.py`](lexical_collisions.py)) | used to adjudicate collisions |
| Adjudication | 17 logged edits on 17 items ([`postedit.py`](postedit.py)) | [`release/provenance.json`](release/provenance.json) |
| Satisfiability | reviewer-written honest answers, scored by the checker on the released items | strict 426/429, loose 429/429 |

Total OpenRouter cost of the study, including the audit and the translator
comparison: $10.34 (NOTES, cost ledger). The Claude reviews ran in a Claude
Code session and are not in that figure.

The 3 strict failures (374, 3369, 3371) cannot be passed in English either:
the text the answer must repeat already contains a forbidden word or the
capped keyword. They are tagged `source_unsatisfiable_strict`.

## Using it

Use `release/hanifeval_v1.1.jsonl`. The Hugging Face card
(`hf/README.md`) documents its fields:
- `key`, `prompt`, `instruction_id_list`, `kwargs`;
- `subset`;
- `answer_language`;
- `adaptation`;
- `edits`;
- `known_issues`.

Score responses (one `{"key": int, "response": str}` per line) with the
standalone scorer, which is also shipped on Hugging Face. It counts a
missing response as a failure:

```bash
pip install -r ../../requirements.txt
python3 hf/score.py --data release/hanifeval_v1.1.jsonl --responses <responses.jsonl> --report <out.json>
python -m pytest tests -q                      # 37 checker regression tests
```

## Caveats a reader should weigh

- **Word counts are eojeol.** `number_words` counts whitespace tokens,
  as the prompts say. The Korean *prompts* have 0.717 eojeol per English
  word (11,373 vs 15,855). The burden this places on *answers* was not
  measured. (v1 extrapolated the prompt ratio to "about 1.4× the content";
  external review F10 correctly called that unsupported, and the claim was
  withdrawn in v1.1.) N is kept as in the source. This affects 41 items
  (43 instructions).
- **Loose scoring hides repeat conflicts.** The loose variants include one
  that drops the first line of the answer, which is where the repeated
  prompt sits. Report strict scores alongside loose ones.
- **Substring matching on Korean.** Keywords and forbidden words are
  matched as substrings. The edits fix the cases where common unrelated
  words collide, or where a dictionary-form string made a constraint
  near-vacuous. Two kinds of finding are accepted and documented rather
  than edited:
  - scope shifts from a synonym choice;
  - spacing variants (유리공장 / 유리 공장).

  Two items have no safe rendering and are tagged:
  - 2028, 'yes'/'no' → '예'/'아니요': `lexical_collision`;
  - 1580, 'ride' → '타다', where inflected forms escape:
    `lexical_inflection_weak`.
- **Stems.**
  - 1733's kwarg is the stem '대답했'. Since v1.1 its prompt says that
    inflected forms count.
  - 3369 counts '옳' while its prompt names '옳다'. It is tagged
    `source_unsatisfiable_strict` and left as is.
- **No human validation.** The naturalness and faithfulness of the Korean
  are judged only by models. Agreement between prompts and checker
  arguments, and satisfiability, are checked by code and do not depend on
  this.
- **Same model family as some evaluated models.** The translator is Gemini
  and the reviewers are Claude. Neither was evaluated here, but a study
  that evaluates Gemini or Claude models on this set should state this.
- **Not identical to English IFEval item by item.** In 1627 and 3718, the
  English repeat contains a comma under `no_comma`, so the English items
  are unsatisfiable. Our guideline had added a second comma ("쉼표(,)") in
  Korean, and removing it made the Korean items satisfiable. In 127, 337
  and 2785, the Korean prompt states the kwargs number where the English
  wording disagrees with it.

## Files

| Path | Content |
|---|---|
| `release/hanifeval_v1.1.jsonl` | the dataset, current version |
| `release/hanifeval_v1.jsonl` | v1, unchanged |
| `release/provenance.json` | source and translator pins, every edit of both versions with its reason, file hashes |
| `NOTES.md` | full research log (§0–§10) |
| `tests/test_checker.py` | checker regression tests |
| `hf/` | Hugging Face card, `score.py`, `build.sh` |
| `build_v11_eval.py`, `eval/v1.1/`, `eval/v1.1_regen/` | v1.1 evaluation |
| `translation_guideline.md`, `checker_semantics.md` | the fixed procedure |
| `translate.py`, `validate.py`, `satisfy.py`, `review_input.py`, `lexical_collisions.py`, `postedit.py`, `human_review_sample.py` | the pipeline, in order |
| `work/translations.jsonl` | raw translator output with per-row usage, cost, provider and guideline hash |
| `work/review/` | reviewer inputs, findings and honest answers |
| `work/pilot_*`, `work/v11_check.jsonl` | pilot evidence |
| `evidence/ifeval_ko_audit/` | the IFEval-Ko audit |
| `evidence/translator_selection/` | WMT24++ MetricX / chrF comparison |
| `checker/` | vendored checker (Apache-2.0, changes marked `[hanifeval]`) |

## License

The release is a derivative of `google/IFEval` (Apache-2.0) and is
distributed under Apache-2.0. The checker derives from Google Research's
IFEval code via IFEval-Ko (Apache-2.0). See `../../NOTICE`.
