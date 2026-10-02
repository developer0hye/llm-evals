## Overall (prompt- and instruction-level accuracy, %)

| Model | scored / errors | prompt strict [95% CI] | prompt loose | inst strict | inst loose | truncated | cost $ | mean reasoning tok | mean visible tok |
|---|---|---|---|---|---|---|---|---|---|
| deepseek-v4.1-flash | 28 / 0 | 96.4 [82.3, 99.4] | 100.0 | 97.8 | 100.0 | 0 | 0.054 | 2804 | 571 |
| gpt-6-luna | 28 / 0 | 96.4 [82.3, 99.4] | 96.4 | 97.8 | 97.8 | 0 | 0.009 | 295 | 355 |
| glm-5.3-flash | 28 / 0 | 96.4 [82.3, 99.4] | 96.4 | 97.8 | 97.8 | 0 | 0.069 | 3827 | 1081 |
| solar-pro4 | 28 / 0 | 92.9 [77.4, 98.0] | 92.9 | 95.6 | 95.6 | 0 | 0.022 | 1912 | 275 |

Denominators: prompt-level = scored items; instruction-level = instructions in scored items.

## Sensitivity (prompt-level strict, %)

| Model | all | without 5 known-issue items | without truncated | core subset | response_language subset |
|---|---|---|---|---|---|
| deepseek-v4.1-flash | 96.4 (n=28) | 96.4 (n=28) | 96.4 (n=28) | 96.3 (n=27) | 100.0 (n=1) |
| gpt-6-luna | 96.4 (n=28) | 96.4 (n=28) | 96.4 (n=28) | 96.3 (n=27) | 100.0 (n=1) |
| glm-5.3-flash | 96.4 (n=28) | 96.4 (n=28) | 96.4 (n=28) | 96.3 (n=27) | 100.0 (n=1) |
| solar-pro4 | 92.9 (n=28) | 92.9 (n=28) | 92.9 (n=28) | 92.6 (n=27) | 100.0 (n=1) |

## Paired comparison (prompt-level strict, McNemar exact, Bonferroni α = 0.0083 over 6 pairs)

| A | B | n (both scored) | A only | B only | p | significant |
|---|---|---|---|---|---|---|
| deepseek-v4.1-flash | gpt-6-luna | 28 | 1 | 1 | 1 | no |
| deepseek-v4.1-flash | glm-5.3-flash | 28 | 1 | 1 | 1 | no |
| deepseek-v4.1-flash | solar-pro4 | 28 | 2 | 1 | 1 | no |
| gpt-6-luna | glm-5.3-flash | 28 | 1 | 1 | 1 | no |
| gpt-6-luna | solar-pro4 | 28 | 1 | 0 | 1 | no |
| glm-5.3-flash | solar-pro4 | 28 | 1 | 0 | 1 | no |

## Instruction-level strict accuracy by instruction type (%)

| Instruction | n | deepseek-v4.1-flash | gpt-6-luna | glm-5.3-flash | solar-pro4 |
|---|---|---|---|---|---|
| `combination:repeat_prompt` | 3 | 100.0 | 100.0 | 100.0 | 100.0 |
| `combination:two_responses` | 2 | 100.0 | 100.0 | 100.0 | 100.0 |
| `detectable_content:number_placeholders` | 2 | 100.0 | 100.0 | 100.0 | 100.0 |
| `detectable_content:postscript` | 2 | 100.0 | 100.0 | 100.0 | 100.0 |
| `detectable_format:constrained_response` | 1 | 100.0 | 100.0 | 100.0 | 100.0 |
| `detectable_format:json_format` | 1 | 100.0 | 100.0 | 100.0 | 100.0 |
| `detectable_format:multiple_sections` | 1 | 100.0 | 100.0 | 100.0 | 100.0 |
| `detectable_format:number_bullet_lists` | 1 | 100.0 | 100.0 | 100.0 | 100.0 |
| `detectable_format:number_highlighted_sections` | 4 | 100.0 | 100.0 | 75.0 | 75.0 |
| `detectable_format:title` | 3 | 100.0 | 100.0 | 100.0 | 100.0 |
| `keywords:existence` | 2 | 100.0 | 100.0 | 100.0 | 100.0 |
| `keywords:forbidden_words` | 2 | 100.0 | 100.0 | 100.0 | 100.0 |
| `keywords:frequency` | 7 | 100.0 | 100.0 | 100.0 | 100.0 |
| `language:response_language` | 1 | 100.0 | 100.0 | 100.0 | 100.0 |
| `length_constraints:nth_paragraph_first_word` | 2 | 100.0 | 100.0 | 100.0 | 100.0 |
| `length_constraints:number_paragraphs` | 1 | 0.0 | 100.0 | 100.0 | 100.0 |
| `length_constraints:number_sentences` | 1 | 100.0 | 100.0 | 100.0 | 100.0 |
| `length_constraints:number_words` | 2 | 100.0 | 50.0 | 100.0 | 50.0 |
| `punctuation:no_comma` | 1 | 100.0 | 100.0 | 100.0 | 100.0 |
| `startend:end_checker` | 3 | 100.0 | 100.0 | 100.0 | 100.0 |
| `startend:quotation` | 3 | 100.0 | 100.0 | 100.0 | 100.0 |

Providers serving scored rows: deepseek-v4.1-flash: StreamLake; gpt-6-luna: OpenAI; glm-5.3-flash: Z.AI; solar-pro4: Upstage
