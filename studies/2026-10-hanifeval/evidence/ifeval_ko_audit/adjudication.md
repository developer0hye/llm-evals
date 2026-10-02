# IFEval-Ko audit: adjudicated findings (2026-10-01)

Dataset audited: `allganize/IFEval-Ko@54199e3`. It has 342 items, all matched
by `key` to `google/IFEval@966cd89`.

Each item was flagged by either or both of two methods:
- the deterministic validator (`../../validate.py`, report in
  `validator_report.json`);
- an LLM comparison of each English item with its Korean version
  (`review.py`, `google/gemini-3.1-pro-preview`, reasoning medium,
  `review.json`; it flagged 94 items, 48 as `breaks_scoring`; cost $2.128).

Every finding below was then checked by hand against the English source, the
Korean prompt, the Korean kwargs and the checker code. The LLM's verdicts were
not taken as final.

"Faithful answer fails" means that an answer which follows the Korean prompt
exactly is scored as not following it.

## A. A faithful answer fails, and the failure is likely: 12 items

| Key | Defect | Found by |
|---|---|---|
| 1203, 2142, 3345 | `keywords:frequency` keyword left in English ("peace", "predatory", "robber") while the prompt asks for the Korean word (평화, 포식자, 강도) | validator + LLM |
| 127, 1643, 3109 | "more than N" (checker `at least N+1`) translated as "N 이상" (≥ N) | validator + LLM |
| 3538 | "600+ word" translated as "600자 이상" (characters); the checker counts eojeol | validator + LLM |
| 1561 | repeat instruction reversed: "먼저 위의 요청을 반복한 후, 아무 말도 하지 않거나 요청에 진짜로 응답하지 마세요" | validator + LLM |
| 1627, 2063, 3505 | repeat instruction loses "say nothing before repeating" / "at the very beginning", while the checker requires the response to start with the request | validator + LLM |
| 227 | constrained-response options written as "내 대답은 예입니다." etc.; the checker looks for "제 답변은 예입니다." | validator only (LLM review: no issue) |

## B. A faithful answer fails only at the exact boundary: 15 items

"less than N" (checker `< N`) was translated as "N 이하" or "N 이내" (≤ N),
so an answer of exactly N fails. Keys: 164, 286, 340, 1092, 1268, 1381, 1879,
2243, 2266, 2674, 2780, 3041, 3415, 3691, 3739.

**Total where a faithful answer can fail: 27 of 342 items (7.9%).**

## C. Checked constraints the prompt does not state

- **1691:** the five forbidden words (moser, glassworks, pravcice, karlovy,
  vary) are in kwargs only, in English. The model is never told and passes
  unless it happens to use them.
- **2395:** the forbidden word "json" is not in the prompt.
- **1348, 1658:** keywords stayed in English ("brilliant", "le", "hou";
  "python", "java"). The checker is case-insensitive, so this is minor.

## D. Misleading wording (a likely failure, not a certain one)

- **3351, 3549:** the explanation of the `*italic*` format became an
  instruction to write a literal phrase ("*이탤릭 텍스트*로 시작하고 끝내주세요",
  "*이것은 강조된 구문*을 두 번 강조하세요").
- **2969:** the instruction to wrap the title in `<<>>` was dropped. The
  example still shows `<<>>`.

## E. Checker problems (not translation)

- **`keywords:forbidden_words`** uses `\bword\b`. A Korean noun followed by a
  particle ("사과를") is not detected, so all 28 forbidden-word prompts let
  violations pass.
- **`language:response_language`** uses unseeded langdetect, and returns
  "pass" when detection fails. Of these 25 items, 24 require a non-Korean
  answer.

## F. Inherited from English IFEval

- **3305:** the prompt asks the model to repeat the request verbatim and also
  to answer only in Hindi.
- **337:** the prompt says "at least 400 words" but the checker uses 336.
- **2355, 2359, 3563:** the English source also lacks the "nothing before
  repeating" sentence.

## Validator and LLM-review errors

- **LLM false positives:**
  - 1446: the checker tests `endswith`, so the full phrase passes.
  - 2164 and 3754: the Korean wording is stricter than the checker but
    never fails a faithful answer.
  - 3629: the checker is ≥ 1 highlight, so "some" passes.
- **LLM false negative:** 227.
- **Validator false positives, removed by refining the rule:** repeat-wording
  on 1480, 1518, 2071, 2482, 2713 and 3369; their Korean prompts contain the
  instruction in a phrasing the first regex missed.
- **Validator `latin_kwarg` flags that are intended:** 2534 (German "schlau"
  in a translate-to-German task), 2577 ("BC"), 2997 ("para").
- **Validator `number_missing` flags:** these are mostly IFEval's own
  encoding, e.g. "20 to 25 sentences" with checker `< 26`. They are not
  translation errors.
