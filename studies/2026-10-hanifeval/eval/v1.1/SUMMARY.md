## Overall (prompt- and instruction-level accuracy, %)

| Model | scored / errors | prompt strict [95% CI] | prompt loose | inst strict | inst loose | truncated | cost $ | mean reasoning tok | mean visible tok |
|---|---|---|---|---|---|---|---|---|---|
| deepseek-v4.1-flash | 429 / 0 | 97.2 [95.2, 98.4] | 97.7 | 97.9 | 98.4 | 0 | 0.730 | 2416 | 575 |
| gpt-6-luna | 429 / 0 | 93.2 [90.5, 95.3] | 94.2 | 95.1 | 95.7 | 0 | 0.159 | 301 | 426 |
| glm-5.3-flash | 429 / 0 | 95.3 [92.9, 97.0] | 97.2 | 96.8 | 98.1 | 0 | 0.910 | 3201 | 1008 |
| solar-pro4 | 429 / 0 | 93.0 [90.2, 95.1] | 95.3 | 95.1 | 96.8 | 0 | 0.465 | 2651 | 337 |

Denominators: prompt-level = scored items; instruction-level = instructions in scored items.

## Sensitivity (prompt-level strict, %)

| Model | all | without 8 known-issue items | without truncated | core subset | response_language subset |
|---|---|---|---|---|---|
| deepseek-v4.1-flash | 97.2 (n=429) | 98.1 (n=421) | 97.2 (n=429) | 97.0 (n=399) | 100.0 (n=30) |
| gpt-6-luna | 93.2 (n=429) | 94.1 (n=421) | 93.2 (n=429) | 93.2 (n=399) | 93.3 (n=30) |
| glm-5.3-flash | 95.3 (n=429) | 96.2 (n=421) | 95.3 (n=429) | 95.0 (n=399) | 100.0 (n=30) |
| solar-pro4 | 93.0 (n=429) | 94.1 (n=421) | 93.0 (n=429) | 92.7 (n=399) | 96.7 (n=30) |

## Paired comparison (prompt-level strict, McNemar exact, Bonferroni α = 0.0083 over 6 pairs)

| A | B | n (both scored) | A only | B only | p | significant |
|---|---|---|---|---|---|---|
| deepseek-v4.1-flash | gpt-6-luna | 429 | 22 | 5 | 0.001514 | yes |
| deepseek-v4.1-flash | glm-5.3-flash | 429 | 15 | 7 | 0.1338 | no |
| deepseek-v4.1-flash | solar-pro4 | 429 | 22 | 4 | 0.0005335 | yes |
| gpt-6-luna | glm-5.3-flash | 429 | 15 | 24 | 0.1996 | no |
| gpt-6-luna | solar-pro4 | 429 | 24 | 23 | 1 | no |
| glm-5.3-flash | solar-pro4 | 429 | 22 | 12 | 0.1214 | no |

## Instruction-level strict accuracy by instruction type (%)

| Instruction | n | deepseek-v4.1-flash | gpt-6-luna | glm-5.3-flash | solar-pro4 |
|---|---|---|---|---|---|
| `combination:repeat_prompt` | 40 | 90.0 | 95.0 | 97.5 | 82.5 |
| `combination:two_responses` | 23 | 100.0 | 91.3 | 100.0 | 100.0 |
| `detectable_content:number_placeholders` | 24 | 100.0 | 100.0 | 100.0 | 100.0 |
| `detectable_content:postscript` | 22 | 100.0 | 100.0 | 100.0 | 100.0 |
| `detectable_format:constrained_response` | 10 | 100.0 | 100.0 | 100.0 | 100.0 |
| `detectable_format:json_format` | 17 | 100.0 | 100.0 | 100.0 | 100.0 |
| `detectable_format:multiple_sections` | 13 | 100.0 | 100.0 | 100.0 | 100.0 |
| `detectable_format:number_bullet_lists` | 26 | 100.0 | 96.2 | 92.3 | 92.3 |
| `detectable_format:number_highlighted_sections` | 45 | 95.6 | 95.6 | 97.8 | 100.0 |
| `detectable_format:title` | 33 | 100.0 | 100.0 | 100.0 | 100.0 |
| `keywords:existence` | 34 | 100.0 | 100.0 | 100.0 | 100.0 |
| `keywords:forbidden_words` | 45 | 97.8 | 97.8 | 84.4 | 91.1 |
| `keywords:frequency` | 35 | 97.1 | 91.4 | 97.1 | 97.1 |
| `language:response_language` | 30 | 100.0 | 100.0 | 100.0 | 100.0 |
| `length_constraints:nth_paragraph_first_word` | 11 | 100.0 | 100.0 | 90.9 | 100.0 |
| `length_constraints:number_paragraphs` | 22 | 100.0 | 59.1 | 95.5 | 100.0 |
| `length_constraints:number_sentences` | 41 | 97.6 | 92.7 | 92.7 | 97.6 |
| `length_constraints:number_words` | 43 | 93.0 | 86.0 | 95.3 | 69.8 |
| `punctuation:no_comma` | 58 | 98.3 | 96.6 | 100.0 | 96.6 |
| `startend:end_checker` | 25 | 100.0 | 100.0 | 100.0 | 96.0 |
| `startend:quotation` | 36 | 100.0 | 100.0 | 97.2 | 100.0 |

Providers serving scored rows: deepseek-v4.1-flash: StreamLake; gpt-6-luna: OpenAI; glm-5.3-flash: Z.AI; solar-pro4: Upstage
