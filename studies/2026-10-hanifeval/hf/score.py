#!/usr/bin/env python3
"""Score model responses on HanIFEval with the bundled checker.

Usage:
    pip install absl-py immutabledict langdetect nltk
    python score.py --data data/hanifeval_v1.jsonl --responses responses.jsonl [--report per_item.json]

responses.jsonl: one {"key": int, "response": str} per line, one response per item.
Prints IFEval's four accuracies: prompt-level strict / loose (every instruction of an item followed)
and instruction-level strict / loose (each instruction counted separately). Items without a
response are reported as missing and are not counted as failures; score them or drop them
deliberately.
"""

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from checker.utils import InputExample, test_instruction_following_loose, test_instruction_following_strict  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=str(HERE / "data" / "hanifeval_v1.jsonl"))
    ap.add_argument("--responses", required=True)
    ap.add_argument("--report", default=None)
    args = ap.parse_args()
    items = {r["key"]: r for r in map(json.loads, Path(args.data).open(encoding="utf-8"))}
    resp = {r["key"]: r["response"] for r in map(json.loads, Path(args.responses).open(encoding="utf-8"))}
    rows, ps, pl, n_inst, is_, il = [], 0, 0, 0, 0, 0
    for k, it in sorted(items.items()):
        if k not in resp:
            continue
        inp = InputExample(key=k, instruction_id_list=it["instruction_id_list"], prompt=it["prompt"],
                           kwargs=it["kwargs"])
        s = test_instruction_following_strict(inp, resp[k])
        lo = test_instruction_following_loose(inp, resp[k])
        ps += s.follow_all_instructions
        pl += lo.follow_all_instructions
        n_inst += len(s.follow_instruction_list)
        is_ += sum(s.follow_instruction_list)
        il += sum(lo.follow_instruction_list)
        rows.append({"key": k, "strict": s.follow_all_instructions, "loose": lo.follow_all_instructions,
                     "strict_list": s.follow_instruction_list, "loose_list": lo.follow_instruction_list})
    n = len(rows)
    missing = len(items) - n
    print(f"scored {n} of {len(items)} items" + (f" ({missing} without a response)" if missing else ""))
    if n:
        print(f"prompt-level strict      {ps / n:.4f}  ({ps}/{n})")
        print(f"prompt-level loose       {pl / n:.4f}  ({pl}/{n})")
        print(f"instruction-level strict {is_ / n_inst:.4f}  ({is_}/{n_inst})")
        print(f"instruction-level loose  {il / n_inst:.4f}  ({il}/{n_inst})")
    if args.report:
        Path(args.report).write_text(json.dumps(rows, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
