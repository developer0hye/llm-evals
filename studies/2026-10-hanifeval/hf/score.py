#!/usr/bin/env python3
"""Score model responses on HanIFEval with the bundled checker.

Usage:
    pip install absl-py immutabledict langdetect nltk
    python score.py --responses responses.jsonl [--data data/hanifeval_v1.1.jsonl] [--report per_item.json]

responses.jsonl: one {"key": int, "response": str} per line, one response per item.
Prints IFEval's four accuracies: prompt-level strict / loose (every instruction of an item followed)
and instruction-level strict / loose (each instruction counted separately). An item without a
response counts as a failure (all its instructions fail); --skip-missing drops it from the
denominator instead. The denominator is always printed.
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
    ap.add_argument("--data", default=str(HERE / "data" / "hanifeval_v1.1.jsonl"))
    ap.add_argument("--responses", required=True)
    ap.add_argument("--report", default=None)
    ap.add_argument("--skip-missing", action="store_true",
                    help="leave items without a response out of the denominator (default: count them as failures)")
    args = ap.parse_args()
    items = {r["key"]: r for r in map(json.loads, Path(args.data).open(encoding="utf-8"))}
    resp = {r["key"]: r["response"] for r in map(json.loads, Path(args.responses).open(encoding="utf-8"))}
    unknown = sorted(set(resp) - set(items))
    if unknown:
        sys.exit(f"responses for keys not in the data: {unknown[:10]}")
    given = set(resp)
    rows, ps, pl, n_inst, is_, il = [], 0, 0, 0, 0, 0
    for k, it in sorted(items.items()):
        if k not in resp:
            if args.skip_missing:
                continue
            # No response: every instruction fails. (An empty string would pass e.g. no_comma.)
            fail = [False] * len(it["instruction_id_list"])
            n_inst += len(fail)
            rows.append({"key": k, "missing": True, "strict": False, "loose": False,
                         "strict_list": fail, "loose_list": fail})
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
    missing = sum(1 for k in items if k not in given)
    print(f"items {len(items)}; responses given {len(items) - missing}; "
          + (f"{missing} missing, {'excluded' if args.skip_missing else 'counted as failures'}; " if missing else "")
          + f"denominator {n}")
    if n:
        print(f"prompt-level strict      {ps / n:.4f}  ({ps}/{n})")
        print(f"prompt-level loose       {pl / n:.4f}  ({pl}/{n})")
        print(f"instruction-level strict {is_ / n_inst:.4f}  ({is_}/{n_inst})")
        print(f"instruction-level loose  {il / n_inst:.4f}  ({il}/{n_inst})")
    if args.report:
        Path(args.report).write_text(json.dumps(rows, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
