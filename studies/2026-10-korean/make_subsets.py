#!/usr/bin/env python3
"""Define the fixed item subsets every run draws from; writes subsets.json (ids only).

golden  10 per task (seed 0). Smoke runs: check the pipeline end to end.
        Scores are not results.
pilot   50 per task (seed 1), disjoint from golden. Per-model pilot: measures
        output tokens, truncation and parse rates to fix the budget before
        the main run. Scores are not results.
main    the reported evaluation set (seed 2 where sampled), fixed before any
        main-run score was seen (2026-09-29):
          kobalt 700 (all), kosimpleqa 938 (all), lbox_casename 1,000 (all),
          klue_ner 1,000 of the 5,000 dev sentences: 500 wikitree + 500 nsmc.

Golden, per task, 10 items:
- kobalt: 2 per linguistic domain, including 67c81c5d... (the duplicate-option item)
- kosimpleqa: 1 per topic category (10 categories)
- klue_ner: 5 wikitree + 5 nsmc, including one sentence with a literal '<' or '>'
- lbox_casename: 5 criminal + 5 civil, at least 3 with and 3 without label leak
"""

import json
import random
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parents[1])]
from tasks import klue_ner, kobalt, kosimpleqa, lbox_casename  # noqa: E402


def strata(items, key, per, rng, force=()):
    groups = defaultdict(list)
    for it in items:
        groups[key(it)].append(it)
    chosen = [it for it in items if it.id in force]
    for g in sorted(groups):
        pool = [it for it in groups[g] if it not in chosen]
        need = per - sum(key(c) == g for c in chosen)
        chosen += rng.sample(pool, max(0, need))
    return [it.id for it in chosen]


def main():
    rng = random.Random(0)
    d = HERE / "data"
    kb = kobalt.load(d)
    ks = kosimpleqa.load(d)
    kn = klue_ner.load(d)
    lb = lbox_casename.load(d)
    angle = next(i.id for i in kn if i.meta["source"] == "wikitree" and ("<" in i.meta["sentence"] or ">" in i.meta["sentence"]))
    golden = {
        "kobalt": strata(kb, lambda i: i.meta["class"], 2, rng, force={"67c81c5d361c7932636b7c14"}),
        "kosimpleqa": strata(ks, lambda i: i.meta["category"], 1, rng),
        "klue_ner": strata(kn, lambda i: i.meta["source"], 5, rng, force={angle}),
    }
    # LBox: 5 per casetype, 3 leak + 2 no-leak for criminal, 2 leak + 3 no-leak for civil.
    pick = []
    for ct, leak, n in [("criminal", True, 3), ("criminal", False, 2), ("civil", True, 2), ("civil", False, 3)]:
        pick += rng.sample([i.id for i in lb if i.meta["casetype"] == ct and i.meta["label_leak"] == leak], n)
    golden["lbox_casename"] = pick
    assert all(len(v) == 10 for v in golden.values()), {k: len(v) for k, v in golden.items()}

    rng = random.Random(1)
    used = {t: set(v) for t, v in golden.items()}
    free = lambda items, t: [i for i in items if i.id not in used[t]]  # noqa: E731
    pilot = {
        "kobalt": strata(free(kb, "kobalt"), lambda i: i.meta["class"], 10, rng),
        "kosimpleqa": strata(free(ks, "kosimpleqa"), lambda i: i.meta["category"], 5, rng),
        "klue_ner": strata(free(kn, "klue_ner"), lambda i: i.meta["source"], 25, rng),
        "lbox_casename": [i.id for i in rng.sample(free(lb, "lbox_casename"), 50)],
    }
    assert all(len(v) == 50 for v in pilot.values()), {k: len(v) for k, v in pilot.items()}

    rng = random.Random(2)
    main_set = {
        "kobalt": [i.id for i in kb],
        "kosimpleqa": [i.id for i in ks],
        "klue_ner": strata(kn, lambda i: i.meta["source"], 500, rng),
        "lbox_casename": [i.id for i in lb],
    }
    subsets = {"golden": golden, "pilot": pilot, "main": main_set}
    (HERE / "subsets.json").write_text(json.dumps(subsets, indent=1) + "\n")
    print({s: {k: len(v) for k, v in d.items()} for s, d in subsets.items()})


if __name__ == "__main__":
    main()
