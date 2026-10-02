#!/usr/bin/env python3
"""Recompute every number for the Korean study from the logged rows.

Usage:
    python3 analyze.py smoke                 # golden-sample smoke rows
    python3 analyze.py results --md results/summary.md

Per model and task: outcome counts, the task metric, parse rate, token use,
cost per item (model + judge) and the cost projected to the main item set.
Task metrics:
    kobalt, lbox_casename  accuracy = correct / all items (non-answers count as not correct)
    kosimpleqa             CO / NA / IN / NR / CGA / F (see tasks/kosimpleqa.py)
    klue_ner               entity-level micro-F1 over all items (unparsed = all gold missed)
Pairwise McNemar tests (Bonferroni over model pairs) are printed for kobalt,
lbox_casename and kosimpleqa (correct vs not) when two or more models share items.
klue_ner: 95% bootstrap CI of micro-F1 and a paired bootstrap test of each
F1 difference, resampling sentences (10,000 resamples, seed 0). Added after
the main run, not pre-registered.
Rows with an `error` are excluded: they are infrastructure failures, retried by run.py.
--models restricts the report to models whose runs are complete.
"""

import random

import argparse
import itertools
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parents[1])]
from common.stats import mcnemar_exact, wilson  # noqa: E402
from tasks import klue_ner, kosimpleqa  # noqa: E402

MAIN_N = {"kobalt": 700, "kosimpleqa": 938, "klue_ner": 1000, "lbox_casename": 1000}  # subsets.json "main"
TASKS = list(MAIN_N)


def rows_of(path: Path) -> list[dict]:
    return [r for r in map(json.loads, path.open(encoding="utf-8")) if not r["error"]] if path.exists() else []


def task_metric(task, rows):
    oc = Counter(r["outcome"] for r in rows)
    n = len(rows)
    if task in ("kobalt", "lbox_casename"):
        k = oc["correct"]
        lo, hi = wilson(k, n)
        out = {"accuracy": k / n, "wilson95": [lo, hi]}
        if task == "lbox_casename":
            for leak in (True, False):
                sub = [r for r in rows if r["label_leak"] == leak]
                if sub:
                    out[f"accuracy_leak={leak}"] = sum(r["outcome"] == "correct" for r in sub) / len(sub)
        return out
    if task == "kosimpleqa":
        return kosimpleqa.metrics([r["outcome"] for r in rows])
    out = f1_of(rows)
    out["parse_rate"] = sum(r["outcome"] == "parsed" for r in rows) / n
    # Pre-registered sensitivity check: re-parse the logged replies with lenient=True.
    items = {i.id: i for i in NER_ITEMS()}
    lenient = []
    for r in rows:
        if r["outcome"] == "no_answer_unparsed":
            pred = klue_ner.parse(items[r["item"]], r["response"], lenient=True)
            lenient.append(klue_ner.score(items[r["item"]], pred))
        else:
            lenient.append(r)
    out["lenient_micro_f1"] = f1_of(lenient)["micro_f1"]
    out["lenient_parse_rate"] = sum(r["outcome"] == "parsed" for r in lenient) / n
    for src in ("wikitree", "nsmc"):
        sub = [r for r in rows if r["source"] == src]
        if sub:
            out[f"micro_f1_{src}"] = f1_of(sub)["micro_f1"]
    return out


def f1_of(rows):
    tp, fp, fn = (sum(r[k] for r in rows) for k in ("tp", "fp", "fn"))
    p = tp / (tp + fp) if tp + fp else 0.0
    rc = tp / (tp + fn) if tp + fn else 0.0
    return {"micro_f1": 2 * p * rc / (p + rc) if p + rc else 0.0, "precision": p, "recall": rc,
            "tp": tp, "fp": fp, "fn": fn}


_NER = []


def NER_ITEMS():
    if not _NER:
        _NER.extend(klue_ner.load(HERE / "data"))
    return _NER


def _f1(tp, fp, fn):
    return 2 * tp / (2 * tp + fp + fn) if tp else 0.0


def ner_bootstrap(by_model: dict, n_boot: int = 10000, seed: int = 0):
    """Per-model 95% CI of micro-F1 and paired two-sided p for each pair, resampling sentences."""
    models = sorted(by_model)
    items = sorted(set.intersection(*(set(v) for v in by_model.values())))
    arr = {m: [by_model[m][i] for i in items] for m in models}
    rng = random.Random(seed)
    samples = {m: [] for m in models}
    for _ in range(n_boot):
        idx = [rng.randrange(len(items)) for _ in items]
        for m in models:
            tp = fp = fn = 0
            for k in idx:
                a, b, c = arr[m][k]
                tp += a; fp += b; fn += c
            samples[m].append(_f1(tp, fp, fn))
    ci = {m: (sorted(v)[int(0.025 * n_boot)], sorted(v)[int(0.975 * n_boot) - 1]) for m, v in samples.items()}
    tests = {}
    for a, b in itertools.combinations(models, 2):
        d = [x - y for x, y in zip(samples[a], samples[b])]
        point = _f1(*map(sum, zip(*arr[a]))) - _f1(*map(sum, zip(*arr[b])))
        p = min(1.0, 2 * min(sum(x <= 0 for x in d), sum(x >= 0 for x in d)) / n_boot)
        tests[(a, b)] = (point, p)
    return len(items), ci, tests


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    ap.add_argument("--md", default=None)
    ap.add_argument("--models", nargs="*", default=None, help="only these model directories")
    args = ap.parse_args()
    root = HERE / args.run_dir
    models = sorted(p.name for p in root.iterdir() if p.is_dir() and (not args.models or p.name in args.models))
    lines = [f"# Summary of `{args.run_dir}/`", "",
             "Recomputed by `analyze.py` from the logged rows. Rows with an API/judge error are excluded "
             "(they are retried, never scored).", ""]
    correct, ner, ner_lenient = {}, {}, {}
    for m in models:
        cfg = json.loads((root / m / "run_config.json").read_text())
        lines += [f"## {m}", "", f"`{cfg['model_id']}` pinned to `{cfg['provider']}`, reasoning "
                  f"{'on' if cfg['reasoning'] else 'off'}, max_tokens {cfg['max_tokens']}, subset "
                  f"`{cfg['subset']}`" + (f", judge `{cfg['judge'][0]}` @ `{cfg['judge'][1]}`" if cfg["judge"] else ""), "",
                  "| task | n | outcomes | metric | providers | mean out tok | $/item (model + judge) | projected main-set $ |",
                  "|---|---|---|---|---|---|---|---|"]
        for t in TASKS:
            rows = rows_of(root / m / f"{t}.jsonl")
            errors = sum(1 for l in (root / m / f"{t}.jsonl").open() if json.loads(l)["error"]) \
                if (root / m / f"{t}.jsonl").exists() else 0
            if not rows:
                continue
            met = task_metric(t, rows)
            main_k = {"kobalt": "accuracy", "lbox_casename": "accuracy", "kosimpleqa": "F", "klue_ner": "micro_f1"}[t]
            cost = sum((r.get("cost") or 0) + ((r.get("judge") or {}).get("cost") or 0) for r in rows) / len(rows)
            tok = sum(r.get("completion_tokens") or 0 for r in rows) / len(rows)
            provs = dict(Counter(r.get("provider") for r in rows))
            oc = ", ".join(f"{k} {v}" for k, v in Counter(r["outcome"] for r in rows).most_common())
            extra = "; ".join(f"{k} {v:.3f}" for k, v in met.items() if isinstance(v, float) and k != main_k)
            lines.append(f"| {t} | {len(rows)}" + (f" (+{errors} errored)" if errors else "") +
                         f" | {oc} | **{main_k} {met[main_k]:.3f}**" + (f" ({extra})" if extra else "") +
                         f" | {provs} | {tok:.0f} | ${cost:.5f} | ${cost * MAIN_N[t]:.2f} |")
            if t != "klue_ner":
                correct.setdefault(t, {})[m] = {r["item"]: r["outcome"] == "correct" for r in rows}
            else:
                ner.setdefault(m, {r["item"]: (r["tp"], r["fp"], r["fn"]) for r in rows})
                items = {i.id: i for i in NER_ITEMS()}
                len_rows = {}
                for r in rows:
                    if r["outcome"] == "no_answer_unparsed":
                        sc = klue_ner.score(items[r["item"]], klue_ner.parse(items[r["item"]], r["response"], lenient=True))
                    else:
                        sc = r
                    len_rows[r["item"]] = (sc["tp"], sc["fp"], sc["fn"])
                ner_lenient[m] = len_rows
        lines.append("")
    pairs = list(itertools.combinations(models, 2))
    if pairs:
        alpha = 0.05 / len(pairs)
        lines += [f"## Pairwise McNemar (Bonferroni alpha = {alpha:.4f} over {len(pairs)} pairs per task)", ""]
        for t, by in correct.items():
            for a, b in pairs:
                if a in by and b in by:
                    ks = sorted(set(by[a]) & set(by[b]))
                    bb = sum(by[a][k] and not by[b][k] for k in ks)
                    cc = sum(by[b][k] and not by[a][k] for k in ks)
                    p = mcnemar_exact(bb, cc)
                    lines.append(f"- {t}: {a} vs {b}: n={len(ks)} b={bb} c={cc} p={'<0.0001' if p < 1e-4 else f'{p:.4f}'}{' **' if p < alpha else ''}")
        lines.append("")
    if len(ner) >= 2:
        n, ci, tests = ner_bootstrap(ner)
        alpha = 0.05 / len(tests)
        lines += [f"## klue_ner: bootstrap over {n} shared sentences (10,000 resamples; Bonferroni alpha = "
                  f"{alpha:.4f}; added after the main run, not pre-registered)", ""]
        lines += [f"- {m}: micro-F1 95% CI [{lo:.3f}, {hi:.3f}]" for m, (lo, hi) in ci.items()]
        lines += [f"- {a} vs {b}: dF1 {d:+.3f}, p={'<0.0001' if p == 0 else f'{p:.4f}'}{' **' if p < alpha else ''}"
                  for (a, b), (d, p) in tests.items()]
        _, ci, tests = ner_bootstrap(ner_lenient)
        lines += ["", "Sensitivity, lenient parse (trailing punctuation/whitespace forgiven):", ""]
        lines += [f"- {m}: micro-F1 95% CI [{lo:.3f}, {hi:.3f}]" for m, (lo, hi) in ci.items()]
        lines += [f"- {a} vs {b}: dF1 {d:+.3f}, p={'<0.0001' if p == 0 else f'{p:.4f}'}{' **' if p < alpha else ''}"
                  for (a, b), (d, p) in tests.items()]
        lines.append("")
    text = "\n".join(lines)
    print(text)
    if args.md:
        (HERE / args.md).write_text(text + "\n")


if __name__ == "__main__":
    main()
