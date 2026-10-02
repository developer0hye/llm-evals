#!/usr/bin/env python3
"""Summarise run_eval.py logs: IFEval's four accuracies, per-type accuracy, paired tests, cost.

Usage:
    python3 analyze_eval.py eval/main --models deepseek-v4.1-flash gpt-6-luna glm-5.3-flash solar-pro4 \
        --md eval/main/SUMMARY.md

Metrics (as in IFEval): prompt-level strict / loose (all instructions of an item followed) and
instruction-level strict / loose (each instruction counted separately). Denominators are the scored
items (rows without `error`); rows with an error are listed, never counted as failures.
Intervals: Wilson 95% for prompt-level rates. Pairwise: McNemar exact test on prompt-level strict,
over items scored for both models, Bonferroni over all model pairs.
Sensitivity: (a) without the items tagged in the release `known_issues` field, (b) without truncated
rows, (c) core subset only (no response_language items).
"""

import argparse
import itertools
import json
import math
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"),) * 2
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def mcnemar_exact(b, c):
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    p = 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, p)


def load(dir_, model):
    rows = [json.loads(l) for l in (dir_ / f"{model}.jsonl").open()]
    newest = {}
    for r in rows:
        newest[r["key"]] = r
    return newest


def metrics(rows):
    n = len(rows)
    ps = sum(r["strict"] for r in rows)
    pl = sum(r["loose"] for r in rows)
    ins = sum(len(r["strict_list"]) for r in rows)
    isx = sum(sum(r["strict_list"]) for r in rows)
    ilx = sum(sum(r["loose_list"]) for r in rows)
    return {"n": n, "prompt_strict": ps, "prompt_loose": pl, "inst_n": ins, "inst_strict": isx, "inst_loose": ilx}


def pct(k, n):
    return f"{100 * k / n:.1f}" if n else "–"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--models", nargs="+", required=True)
    ap.add_argument("--md", default=None)
    args = ap.parse_args()
    d = HERE / args.dir
    release = {r["key"]: r for r in map(json.loads, (HERE / "release" / "ko_ifeval_v1.jsonl").open())}
    known = {k for k, r in release.items() if r["known_issues"]}
    data = {m: load(d, m) for m in args.models}
    out = []
    w = out.append

    w("## Overall (prompt- and instruction-level accuracy, %)\n")
    w("| Model | scored / errors | prompt strict [95% CI] | prompt loose | inst strict | inst loose | truncated | cost $ | mean reasoning tok | mean visible tok |")
    w("|---|---|---|---|---|---|---|---|---|---|")
    scored = {}
    for m, rows in data.items():
        ok = [r for r in rows.values() if not r["error"]]
        err = [r for r in rows.values() if r["error"]]
        scored[m] = {r["key"]: r for r in ok}
        x = metrics(ok)
        lo, hi = wilson(x["prompt_strict"], x["n"])
        trunc = sum(r["truncated"] for r in ok)
        cost = sum(r.get("cost") or 0 for r in ok)
        rt = sum((r.get("reasoning_tokens") or 0) for r in ok) / max(1, len(ok))
        vt = sum((r.get("completion_tokens") or 0) - (r.get("reasoning_tokens") or 0) for r in ok) / max(1, len(ok))
        w(f"| {m} | {x['n']} / {len(err)} | {pct(x['prompt_strict'], x['n'])} [{100 * lo:.1f}, {100 * hi:.1f}] "
          f"| {pct(x['prompt_loose'], x['n'])} | {pct(x['inst_strict'], x['inst_n'])} | {pct(x['inst_loose'], x['inst_n'])} "
          f"| {trunc} | {cost:.3f} | {rt:.0f} | {vt:.0f} |")
    w("")
    w("Denominators: prompt-level = scored items; instruction-level = instructions in scored items.\n")

    w("## Sensitivity (prompt-level strict, %)\n")
    w(f"| Model | all | without {len(known)} known-issue items | without truncated | core subset | response_language subset |")
    w("|---|---|---|---|---|---|")
    for m in args.models:
        ok = list(scored[m].values())
        def r_(f):
            s = [r for r in ok if f(r)]
            return f"{pct(sum(r['strict'] for r in s), len(s))} (n={len(s)})"
        w(f"| {m} | {r_(lambda r: True)} | {r_(lambda r: r['key'] not in known)} | {r_(lambda r: not r['truncated'])} "
          f"| {r_(lambda r: r['subset'] == 'core')} | {r_(lambda r: r['subset'] == 'response_language')} |")
    w("")

    pairs = list(itertools.combinations(args.models, 2))
    if pairs:
        alpha = 0.05 / len(pairs)
        w(f"## Paired comparison (prompt-level strict, McNemar exact, Bonferroni α = {alpha:.4f} over {len(pairs)} pairs)\n")
        w("| A | B | n (both scored) | A only | B only | p | significant |")
        w("|---|---|---|---|---|---|---|")
        for a, b in pairs:
            common = sorted(set(scored[a]) & set(scored[b]))
            ao = sum(scored[a][k]["strict"] and not scored[b][k]["strict"] for k in common)
            bo = sum(scored[b][k]["strict"] and not scored[a][k]["strict"] for k in common)
            p = mcnemar_exact(ao, bo)
            w(f"| {a} | {b} | {len(common)} | {ao} | {bo} | {p:.4g} | {'yes' if p < alpha else 'no'} |")
        w("")

    w("## Instruction-level strict accuracy by instruction type (%)\n")
    types = sorted({i for m in args.models for r in scored[m].values() for i in r["instruction_id_list"]})
    w("| Instruction | n | " + " | ".join(args.models) + " |")
    w("|---|---|" + "---|" * len(args.models))
    for t in types:
        cells, n = [], None
        for m in args.models:
            hits = [ok for r in scored[m].values() for i, ok in zip(r["instruction_id_list"], r["strict_list"]) if i == t]
            n = len(hits)
            cells.append(pct(sum(hits), len(hits)))
        w(f"| `{t}` | {n} | " + " | ".join(cells) + " |")
    w("")

    errs = {m: [(r["key"], r["error"][:80]) for r in data[m].values() if r["error"]] for m in args.models}
    if any(errs.values()):
        w("## Errored rows (not scored)\n")
        for m, e in errs.items():
            for k, msg in e:
                w(f"- {m} {k}: {msg}")
        w("")
    providers = {m: sorted({r.get("provider") for r in scored[m].values()}) for m in args.models}
    w("Providers serving scored rows: " + "; ".join(f"{m}: {', '.join(map(str, p))}" for m, p in providers.items()))
    text = "\n".join(out)
    print(text)
    if args.md:
        (HERE / args.md).write_text(text + "\n")


if __name__ == "__main__":
    main()
