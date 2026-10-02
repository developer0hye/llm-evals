# Summary of `results/`

Recomputed by `analyze.py` from the logged rows. Rows with an API/judge error are excluded (they are retried, never scored).

## deepseek-v4.1-flash

`deepseek/deepseek-v4.1-flash` pinned to `streamlake/fp8`, reasoning on, max_tokens 64000, subset `main`

| task | n | outcomes | metric | providers | mean out tok | $/item (model + judge) | projected main-set $ |
|---|---|---|---|---|---|---|---|
| kobalt | 700 | correct 572, wrong 121, no_answer_truncated 4, no_answer_unparsed 3 | **accuracy 0.817** | {'StreamLake': 700} | 9308 | $0.00621 | $4.35 |
| klue_ner | 1000 | parsed 979, no_answer_unparsed 21 | **micro_f1 0.786** (precision 0.773; recall 0.800; parse_rate 0.979; lenient_micro_f1 0.787; lenient_parse_rate 0.984; micro_f1_wikitree 0.753; micro_f1_nsmc 0.870) | {'StreamLake': 1000} | 3005 | $0.00200 | $2.00 |
| lbox_casename | 1000 | correct 846, wrong 153, no_answer_unparsed 1 | **accuracy 0.846** (accuracy_leak=True 0.936; accuracy_leak=False 0.811) | {'StreamLake': 1000} | 1507 | $0.00115 | $1.15 |

## glm-5.3-flash

`z-ai/glm-5.3-flash` pinned to `z-ai/fp8`, reasoning on, max_tokens 64000, subset `main`

| task | n | outcomes | metric | providers | mean out tok | $/item (model + judge) | projected main-set $ |
|---|---|---|---|---|---|---|---|
| kobalt | 700 | correct 497, wrong 112, no_answer_truncated 91 | **accuracy 0.710** | {'Z.AI': 700} | 19368 | $0.00975 | $6.82 |
| klue_ner | 1000 | parsed 978, no_answer_unparsed 21, no_answer_truncated 1 | **micro_f1 0.764** (precision 0.766; recall 0.762; parse_rate 0.978; lenient_micro_f1 0.764; lenient_parse_rate 0.978; micro_f1_wikitree 0.732; micro_f1_nsmc 0.844) | {'Z.AI': 1000} | 2012 | $0.00103 | $1.03 |
| lbox_casename | 1000 | correct 807, wrong 171, no_answer_truncated 13, no_answer_unparsed 9 | **accuracy 0.807** (accuracy_leak=True 0.943; accuracy_leak=False 0.753) | {'Z.AI': 1000} | 2621 | $0.00146 | $1.46 |

## gpt-6-luna

`openai/gpt-6-luna` pinned to `openai`, reasoning on, max_tokens 64000, subset `main`

| task | n | outcomes | metric | providers | mean out tok | $/item (model + judge) | projected main-set $ |
|---|---|---|---|---|---|---|---|
| kobalt | 700 | correct 577, wrong 123 | **accuracy 0.824** | {'OpenAI': 700} | 1121 | $0.00060 | $0.42 |
| klue_ner | 1000 | parsed 921, no_answer_unparsed 79 | **micro_f1 0.748** (precision 0.757; recall 0.739; parse_rate 0.921; lenient_micro_f1 0.768; lenient_parse_rate 0.994; micro_f1_wikitree 0.733; micro_f1_nsmc 0.789) | {'OpenAI': 1000} | 198 | $0.00014 | $0.14 |
| lbox_casename | 1000 | correct 845, wrong 155 | **accuracy 0.845** (accuracy_leak=True 0.940; accuracy_leak=False 0.808) | {'OpenAI': 1000} | 109 | $0.00028 | $0.28 |

## solar-pro4

`upstage/solar-pro4` pinned to `upstage`, reasoning on, max_tokens 64000, subset `main`

| task | n | outcomes | metric | providers | mean out tok | $/item (model + judge) | projected main-set $ |
|---|---|---|---|---|---|---|---|
| kobalt | 700 | correct 509, wrong 190, no_answer_unparsed 1 | **accuracy 0.727** | {'Upstage': 700} | 5892 | $0.00214 | $1.50 |
| klue_ner | 1000 | parsed 970, no_answer_unparsed 30 | **micro_f1 0.764** (precision 0.767; recall 0.761; parse_rate 0.970; lenient_micro_f1 0.764; lenient_parse_rate 0.970; micro_f1_wikitree 0.730; micro_f1_nsmc 0.848) | {'Upstage': 1000} | 3336 | $0.00123 | $1.23 |
| lbox_casename | 1000 | correct 814, wrong 184, no_answer_unparsed 2 | **accuracy 0.814** (accuracy_leak=True 0.933; accuracy_leak=False 0.767) | {'Upstage': 1000} | 873 | $0.00041 | $0.41 |

## Pairwise McNemar (Bonferroni alpha = 0.0083 over 6 pairs per task)

- kobalt: deepseek-v4.1-flash vs glm-5.3-flash: n=700 b=108 c=33 p=<0.0001 **
- kobalt: deepseek-v4.1-flash vs gpt-6-luna: n=700 b=40 c=45 p=0.6646
- kobalt: deepseek-v4.1-flash vs solar-pro4: n=700 b=100 c=37 p=<0.0001 **
- kobalt: glm-5.3-flash vs gpt-6-luna: n=700 b=38 c=118 p=<0.0001 **
- kobalt: glm-5.3-flash vs solar-pro4: n=700 b=67 c=79 p=0.3627
- kobalt: gpt-6-luna vs solar-pro4: n=700 b=96 c=28 p=<0.0001 **
- lbox_casename: deepseek-v4.1-flash vs glm-5.3-flash: n=1000 b=66 c=27 p=<0.0001 **
- lbox_casename: deepseek-v4.1-flash vs gpt-6-luna: n=1000 b=34 c=33 p=1.0000
- lbox_casename: deepseek-v4.1-flash vs solar-pro4: n=1000 b=50 c=18 p=0.0001 **
- lbox_casename: glm-5.3-flash vs gpt-6-luna: n=1000 b=29 c=67 p=0.0001 **
- lbox_casename: glm-5.3-flash vs solar-pro4: n=1000 b=42 c=49 p=0.5296
- lbox_casename: gpt-6-luna vs solar-pro4: n=1000 b=62 c=31 p=0.0017 **

## klue_ner: bootstrap over 1000 shared sentences (10,000 resamples; Bonferroni alpha = 0.0083; added after the main run, not pre-registered)

- deepseek-v4.1-flash: micro-F1 95% CI [0.768, 0.804]
- glm-5.3-flash: micro-F1 95% CI [0.745, 0.783]
- gpt-6-luna: micro-F1 95% CI [0.729, 0.766]
- solar-pro4: micro-F1 95% CI [0.744, 0.782]
- deepseek-v4.1-flash vs glm-5.3-flash: dF1 +0.022, p=0.0014 **
- deepseek-v4.1-flash vs gpt-6-luna: dF1 +0.038, p=<0.0001 **
- deepseek-v4.1-flash vs solar-pro4: dF1 +0.022, p=0.0042 **
- glm-5.3-flash vs gpt-6-luna: dF1 +0.016, p=0.0354
- glm-5.3-flash vs solar-pro4: dF1 +0.000, p=0.9710
- gpt-6-luna vs solar-pro4: dF1 -0.016, p=0.0396

Sensitivity, lenient parse (trailing punctuation/whitespace forgiven):

- deepseek-v4.1-flash: micro-F1 95% CI [0.769, 0.805]
- glm-5.3-flash: micro-F1 95% CI [0.745, 0.783]
- gpt-6-luna: micro-F1 95% CI [0.750, 0.786]
- solar-pro4: micro-F1 95% CI [0.744, 0.782]
- deepseek-v4.1-flash vs glm-5.3-flash: dF1 +0.023, p=0.0008 **
- deepseek-v4.1-flash vs gpt-6-luna: dF1 +0.018, p=0.0072 **
- deepseek-v4.1-flash vs solar-pro4: dF1 +0.023, p=0.0022 **
- glm-5.3-flash vs gpt-6-luna: dF1 -0.005, p=0.5000
- glm-5.3-flash vs solar-pro4: dF1 +0.000, p=0.9710
- gpt-6-luna vs solar-pro4: dF1 +0.005, p=0.4922

