#!/usr/bin/env python3
"""Recompute the translator-selection comparison (2026-10-01) from the files in this directory.

Inputs:
    sample.json      120 WMT24++ en-ko_KR segments (google/wmt24pp, 30 per domain, seed 0, bad sources removed)
    hyps.json        one translation per (model, segment), from translate.py
    mx_out.jsonl     MetricX-24 hybrid-large-v2p6 (bf16), reference-based
    mx_out_qe.jsonl  the same model in QE mode (no reference)

MetricX was run with google-research/metricx@fc4978e:
    python -m metricx24.predict --tokenizer google/mt5-large \
        --model_name_or_path google/metricx-24-hybrid-large-v2p6-bfloat16 \
        --max_input_length 1536 --batch_size 1 --input_file mx_in.jsonl --output_file mx_out.jsonl [--qe]
Scores: 0 = no error, 25 = worst. Pairwise: Wilcoxon signed-rank on the 120 paired segments,
Bonferroni over 6 pairs. CIs: 2,000 bootstrap resamples of segments (seed 0).
Requires sacrebleu and scipy.
"""

import collections
import itertools
import json
import random
from pathlib import Path

import sacrebleu
from scipy.stats import wilcoxon

HERE = Path(__file__).resolve().parent
MODELS = ["gemini-3.1-pro", "opus-5.5", "gpt-4o", "gemini-3.8-flash"]


def load_mx(name):
    d = collections.defaultdict(dict)
    for line in (HERE / name).open():
        r = json.loads(line)
        d[r["model"]][r["segment_id"]] = r["prediction"]
    return d


def main():
    sample = {r["segment_id"]: r for r in json.loads((HERE / "sample.json").read_text())}
    ids = sorted(sample)
    hyps = collections.defaultdict(dict)
    cost = collections.Counter()
    for h in json.loads((HERE / "hyps.json").read_text()):
        hyps[h["model"]][h["segment_id"]] = h["hyp"]
        cost[h["model"]] += h.get("cost") or 0
    rng = random.Random(0)
    print(f"n = {len(ids)} segments")
    print("chrF (corpus) and cost:")
    for m in MODELS:
        chrf = sacrebleu.corpus_chrf([hyps[m][i] for i in ids], [[sample[i]["target"] for i in ids]]).score
        print(f"  {m:17s} chrF {chrf:.1f}   ${cost[m]:.3f}")
    for label, f in (("MetricX-24 reference-based", "mx_out.jsonl"), ("MetricX-24 QE", "mx_out_qe.jsonl")):
        d = load_mx(f)
        print(label)
        for m in MODELS:
            xs = [d[m][i] for i in ids]
            bs = sorted(sum(rng.choice(xs) for _ in xs) / len(xs) for _ in range(2000))
            print(f"  {m:17s} {sum(xs) / len(xs):.2f} [{bs[50]:.2f}, {bs[1949]:.2f}]")
        for a, b in itertools.combinations(MODELS, 2):
            xa, xb = [d[a][i] for i in ids], [d[b][i] for i in ids]
            p = wilcoxon(xa, xb).pvalue
            print(f"    {a} vs {b}: {sum(xa) / len(xa) - sum(xb) / len(xb):+.2f}, p = {p:.4f}{' **' if p < 0.05 / 6 else ''}")


if __name__ == "__main__":
    main()
