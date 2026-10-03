#!/usr/bin/env python3
"""Assemble v1.1 evaluation logs from v1 runs plus re-generated responses for the items v1.1 edited.

Usage:
    python3 build_v11_eval.py --models deepseek-v4.1-flash gpt-6-luna glm-5.3-flash solar-pro4 solar-mini4

For each model, writes eval/v1.1/<model>.jsonl with one row per v1.1 item:
  - items whose prompt or kwargs changed in v1.1: the row from eval/v1.1_regen/ (a new model call);
  - every other item: the v1 row from eval/main/, whose response is re-scored with the current checker.
    The item text is identical (asserted by item hash), so the old response is a valid answer to it.
Each row records `response_source` ("v1" or "v1.1") so the provenance of every score is visible.
"""

import argparse
import json
from pathlib import Path

from run_eval import RELEASES, item_sha, score

HERE = Path(__file__).resolve().parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", required=True)
    args = ap.parse_args()
    v1 = {r["key"]: r for r in map(json.loads, RELEASES["1"].open())}
    v11 = {r["key"]: r for r in map(json.loads, RELEASES["1.1"].open())}
    changed = {k for k in v11 if item_sha(v11[k]) != item_sha(v1[k])}
    out = HERE / "eval" / "v1.1"
    out.mkdir(parents=True, exist_ok=True)
    for m in args.models:
        old = {r["key"]: r for r in map(json.loads, (HERE / "eval" / "main" / f"{m}.jsonl").open()) if not r["error"]}
        new = {r["key"]: r for r in map(json.loads, (HERE / "eval" / "v1.1_regen" / f"{m}.jsonl").open())
               if not r["error"]}
        missing = sorted(changed - set(new))
        assert not missing, f"{m}: no v1.1 response for {missing}"
        rows = []
        for k in sorted(v11):
            if k in changed:
                r = dict(new[k], response_source="v1.1")
            else:
                r = dict(old[k])
                assert r["item_sha256"] == item_sha(v11[k])
                r.update(score(v11[k], r["response"]), subset=v11[k]["subset"], response_source="v1")
            assert r["item_sha256"] == item_sha(v11[k])
            rows.append(r)
        (out / f"{m}.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
        print(f"{m}: {len(rows)} rows ({len(changed)} from v1.1 calls, {len(rows) - len(changed)} re-scored v1 rows)")


if __name__ == "__main__":
    main()
