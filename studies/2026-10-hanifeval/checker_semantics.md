# Checker semantics (fixed before translation, 2026-10-01)

Every Korean item is translated to be scored by the checker in `checker/`. This
document says how each constraint is scored, and the translation guideline
follows from it.

`checker/` is the IFEval-Ko checker (`allganize/IFEval-Ko@54199e3`,
`ifeval_ko/`), which derives from Google's IFEval code (Apache-2.0). It is
vendored with five scoring changes, each marked `[hanifeval]` in the code
(a sixth, added 2026-10-03, makes two regex literals in `instructions_util.py`
raw strings; the regexes are identical, and re-scoring all 1,716 eval rows
changed 0 results):

1. `language:response_language`: `langdetect.DetectorFactory.seed = 0`, so the
   detection is deterministic.
2. `keywords:existence`: the keyword is escaped (`re.escape`) and matched as a
   substring, case-insensitively, so a keyword followed by a particle still
   counts.
3. `keywords:frequency`: the same escaped substring count.
4. `keywords:forbidden_words`: escaped substring, not `\b…\b`. With `\b`, a
   forbidden noun followed by a particle ("사과를") was not detected.
5. `length_constraints:nth_paragraph_first_word`: the paragraph must *start
   with* the word (prefix match), not have it as the whole first eojeol,
   because the first word usually carries a particle ("회사는").

## Per constraint

| instruction_id | How it is scored | What the translation must do |
|---|---|---|
| `length_constraints:number_words` | whitespace-separated tokens (eojeol), `<` or `>=` N | say "N단어(띄어쓰기 기준)"; never "자" or "글자" |
| `length_constraints:number_sentences` | IFEval-Ko rule-based splitter on `.`, `?`, `!` (with exceptions for English abbreviations and numbers) | say "N문장"; avoid example text with stray periods |
| `length_constraints:number_paragraphs` | paragraphs separated by the markdown divider `***` | keep `***` literally |
| `length_constraints:nth_paragraph_first_word` | paragraphs split on a blank line; count must match; the nth paragraph must start with `first_word` | the word in the prompt equals `first_word` exactly |
| `keywords:existence` | escaped substring, case-insensitive | every keyword appears in the prompt exactly as in kwargs |
| `keywords:frequency` | escaped substring count, `<` or `>=` N | the keyword appears in the prompt exactly as in kwargs; use a noun stem that survives particles |
| `keywords:forbidden_words` | escaped substring; any occurrence fails | every forbidden word is listed in the prompt exactly as in kwargs; prefer stems that do not hide inside unrelated words |
| `detectable_content:number_placeholders` | count of `[…]` | keep square brackets in examples |
| `detectable_content:postscript` | a line starting with `postscript_marker` (e.g. `P.S.`) | keep the marker literally |
| `detectable_format:number_bullet_lists` | lines starting with `* ` or `- ` | keep the markdown bullet example |
| `detectable_format:number_highlighted_sections` | count of `*text*` spans, `>=` N | keep `*…*` |
| `detectable_format:multiple_sections` | split on `section_spliter` + number | use `section_spliter` exactly as in kwargs (convention: "섹션", e.g. "섹션 1") |
| `detectable_format:title` | a `<<…>>` span | keep `<<…>>` |
| `detectable_format:json_format` | whole response parses as JSON (fences allowed) | keep "JSON" |
| `detectable_format:constrained_response` | response contains one of "제 답변은 예입니다." / "제 답변은 아니요입니다." / "제 답변은 아마도입니다." | list exactly these three strings |
| `combination:two_responses` | two different responses separated by `******` | keep `******` |
| `combination:repeat_prompt` | the response, lowercased and stripped, starts with `prompt_to_repeat` | `prompt_to_repeat` is a verbatim substring of the prompt, and the prompt says to repeat it first, with nothing before it |
| `startend:end_checker` | the stripped response ends with `end_phrase` | `end_phrase` appears verbatim in the prompt |
| `startend:quotation` | the whole response is wrapped in `"` | say "큰따옴표로 전체 응답을 감싸세요" |
| `punctuation:no_comma` | no ASCII `,` | say "쉼표(,)를 사용하지 마세요" |
| `language:response_language` | seeded langdetect equals `language` | keep the target language; these items are reported as a separate subset |

Relations: `less than N` means the count is `< N`. `at least N` means the
count is `>= N`.

## Excluded from translation

There are 112 items with `change_case:*` or `keywords:letter_frequency`
constraints. They test English letter case or Latin letter counts, which have
no Korean equivalent, and IFEval-Ko removed them too. Their keys are listed in
`excluded_keys.json`.
