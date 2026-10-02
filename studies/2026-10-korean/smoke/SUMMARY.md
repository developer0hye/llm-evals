# Summary of `smoke/`

Recomputed by `analyze.py` from the logged rows. Rows with an API/judge error are excluded (they are retried, never scored).

## gpt-6-luna-flex

`openai/gpt-6-luna` pinned to `openai/flex`, reasoning on, max_tokens 16000, subset `golden`, judge `openai/gpt-6-luna` @ `openai/flex`

| task | n | outcomes | metric | providers | mean out tok | $/item (model + judge) | projected main-set $ |
|---|---|---|---|---|---|---|---|
| kobalt | 10 | correct 10 | **accuracy 1.000** | {'OpenAI': 10} | 1261 | $0.00034 | $0.23 |
| kosimpleqa | 10 | correct 9, incorrect 1 | **F 0.900** (CO 0.900; NA 0.000; IN 0.100; NR 0.000; CGA 0.900) | {'OpenAI': 10} | 377 | $0.00019 | $0.17 |
| klue_ner | 10 | parsed 9, no_answer_unparsed 1 | **micro_f1 0.867** (precision 0.897; recall 0.839; parse_rate 0.900; lenient_micro_f1 0.903; lenient_parse_rate 1.000; micro_f1_wikitree 0.880; micro_f1_nsmc 0.800) | {'OpenAI': 10} | 301 | $0.00010 | $0.10 |
| lbox_casename | 10 | correct 8, wrong 2 | **accuracy 0.800** (accuracy_leak=True 0.800; accuracy_leak=False 0.800) | {'OpenAI': 10} | 348 | $0.00022 | $0.22 |

