#!/usr/bin/env python3
"""Corpus check of Korean keyword / forbidden-word strings: where else does each string occur?

The checker matches keywords and forbidden words as case-insensitive substrings (checker_semantics.md).
A short or inflected Korean string can therefore occur inside unrelated words (false fail for a
forbidden word, free credit for a keyword). Reviewers catch some of these by reading; this script
lists, for every Korean string kwarg, the corpus eojeol that contain it, so all items get the same check.

Usage:
    python3 lexical_collisions.py --translations work/translations.jsonl \
        --klue-ner ../2026-10-korean/data/klue-ner-v1.1_dev.tsv --out work/lexical_collisions.json

Corpus: KLUE-NER v1.1 dev sentences (news and web text; 5,000 sentences), entity markup stripped.
Output per (key, kwarg, string): occurrences per 10k eojeol, the share of hits where the string is
not at the start of the eojeol (embedded, e.g. 다가오는 for 가오), and the most frequent containing
eojeol, for manual adjudication. The score is a screening signal, not a verdict.
"""

import argparse
import json
import re
from collections import Counter
from pathlib import Path

KEYS = ("keywords", "keyword", "forbidden_words")


def load_klue(path):
    for line in Path(path).open(encoding="utf-8"):
        if line.startswith("## klue-ner"):
            text = line.split("\t", 1)[1]
            yield re.sub(r"<([^:<>]+):[A-Z]{2}>", r"\1", text).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--translations", required=True)
    ap.add_argument("--klue-ner", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--top", type=int, default=8)
    args = ap.parse_args()
    eojeol = Counter(w for s in load_klue(args.klue_ner) for w in s.split())
    total = sum(eojeol.values())
    items = {}
    for r in map(json.loads, Path(args.translations).open()):
        if not r["error"]:
            items[r["key"]] = r["output"]
    rows = []
    for key, o in sorted(items.items()):
        for iid, kw in zip(o["instruction_id_list"], o["kwargs"]):
            for k in KEYS:
                vals = (kw or {}).get(k)
                if not vals:
                    continue
                for s in vals if isinstance(vals, list) else [vals]:
                    if not re.search(r"[가-힣]", s):
                        continue
                    sl = s.lower()
                    hits = Counter({w: c for w, c in eojeol.items() if sl in w.lower()})
                    n = sum(hits.values())
                    embedded = sum(c for w, c in hits.items() if not w.lower().startswith(sl))
                    rows.append({"key": key, "instruction_id": iid, "kwarg": k, "string": s,
                                 "per_10k": round(n / total * 1e4, 2), "hits": n,
                                 "embedded_share": round(embedded / n, 3) if n else None,
                                 "top": hits.most_common(args.top)})
    Path(args.out).write_text(json.dumps({"corpus": "KLUE-NER v1.1 dev", "eojeol": total, "rows": rows},
                                         ensure_ascii=False, indent=1))
    print(f"corpus eojeol {total}; {len(rows)} Korean string kwargs checked")
    for r in sorted(rows, key=lambda r: -r["per_10k"])[:40]:
        print(f"  {r['key']:5d} {r['kwarg']:15s} {r['string']:12s} {r['per_10k']:7.2f}/10k "
              f"emb {r['embedded_share']}  {[w for w, _ in r['top'][:5]]}")


if __name__ == "__main__":
    main()
