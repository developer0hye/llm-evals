# Agent instructions

This repo accumulates LLM evaluations, one self-contained study per folder under
`studies/`, sharing `common/` (model pins, OpenRouter client, statistics). It is
read by practitioners in AI evaluation and is meant to be citable. Write for
that reader.

## Studies are frozen once reported

- Each study README pins the commit of the harness that produced its numbers.
  Changing `common/` must not silently change a reported study; if it would,
  re-run the study or leave its README pointing at the old commit.
- New work goes in a new dated study folder (`studies/YYYY-MM-topic/`), not
  into a reported one.

## Numbers are claims, and claims get verified

- Every figure in a README must be recomputable from committed rows (the
  study's `analyze.py`). Recompute before publishing; never copy from a draft.
- State the denominator of every rate and the n of every test.
- When a methodological choice could change a conclusion (how truncations,
  refusals, parse failures or judge errors are counted; which subset), report
  the sensitivity check next to the headline.
- Smoke runs on golden samples check the pipeline. Their scores are not
  results and are never quoted as model performance.

## Scoring rules carried over from earlier work

- A non-answer is not a wrong answer: truncated (hit max_tokens) and unparsed
  (finished, no explicitly stated answer) are separate outcomes, and a
  truncated reply is never parsed.
- Extract only an explicitly stated answer. Never fall back to "a letter/label
  appearing somewhere in the text" (such a fallback misreads option lists,
  articles and stray capitals as answers).
- Infrastructure failures (HTTP 429/5xx, timeouts, empty content with finish
  "stop", judge errors) are retried, never counted as model outcomes. Record
  them and what they would have looked like if left unfixed.
- Pin one provider per model with fallbacks off; record the serving provider
  per row.
- Every extractor/scorer has offline tests with synthetic responses.

## Data and third-party code

- Evaluation data is fetched at pinned revisions and SHA-256-checked by the
  study's `download_data.sh`; it is never committed. List each dataset's
  licence in NOTICE.
- Vendoring code or prompts is a redistribution decision: check the upstream
  licence first, keep its licence file, pin the commit. Paper text on arXiv's
  default licence is not copyable.
- Research: analyse primary sources (paper, repo, dataset card), not summaries.

## Write in the field's vocabulary

Name things exactly: model IDs, provider pins, commits, file paths, flags,
ISO dates. No marketing adjectives, no hedging filler. Claims carry a number,
a test, or a file reference.
