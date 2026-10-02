#!/usr/bin/env python3
"""Satisfiability check: score hand-written compliant Korean answers with the checker.

Usage:
    python3 satisfy.py --translations work/pilot_translations.jsonl --responses work/pilot_responses.jsonl

--responses rows: {"key": int, "response": str} -- an answer written to follow the Korean prompt
faithfully (by a reviewer, not by a model under test). If such an answer fails the checker,
the item (or the checker) is broken, whatever a reading of the prompt suggested.
Prints per-item strict and loose results and the failing instruction ids.
"""

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from checker.utils import InputExample, test_instruction_following_loose, test_instruction_following_strict  # noqa: E402


def newest(path):
    """Items by key, from a translate.py log (newest ok row wins) or a release file (one item per row)."""
    out = {}
    for r in map(json.loads, Path(path).open()):
        if "prompt" in r:
            out[r["key"]] = r
        elif not r["error"]:
            out[r["key"]] = r["output"]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--translations", required=True)
    ap.add_argument("--responses", required=True)
    ap.add_argument("--report", default=None)
    args = ap.parse_args()
    items = newest(args.translations)
    rows, n_strict, n_loose = [], 0, 0
    for r in map(json.loads, Path(args.responses).open()):
        o = items[r["key"]]
        inp = InputExample(key=r["key"], instruction_id_list=o["instruction_id_list"], prompt=o["prompt"],
                           kwargs=[{k: v for k, v in d.items()} for d in o["kwargs"]])
        s = test_instruction_following_strict(inp, r["response"])
        lo = test_instruction_following_loose(inp, r["response"])
        failed = [i for i, ok in zip(o["instruction_id_list"], s.follow_instruction_list) if not ok]
        n_strict += s.follow_all_instructions
        n_loose += lo.follow_all_instructions
        rows.append({"key": r["key"], "strict": s.follow_all_instructions, "loose": lo.follow_all_instructions,
                     "failed_strict": failed})
        print(f"  {r['key']}: strict {'PASS' if s.follow_all_instructions else 'FAIL ' + str(failed)}"
              f" | loose {'PASS' if lo.follow_all_instructions else 'FAIL'}")
    print(f"strict {n_strict}/{len(rows)}, loose {n_loose}/{len(rows)}")
    if args.report:
        Path(args.report).write_text(json.dumps(rows, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
