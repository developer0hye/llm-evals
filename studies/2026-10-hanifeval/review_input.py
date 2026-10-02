#!/usr/bin/env python3
"""Build reviewer input (English source + Korean translation) from a translations log, in shards.

Usage:
    python3 review_input.py --translations work/translations.jsonl --shards 8 --out-prefix work/review/input

Writes <out-prefix>_<i>.jsonl, one line per item: key, instruction_id_list, english {prompt, kwargs},
korean {prompt, kwargs}. Items are sorted by key and dealt round-robin, so shards mix instruction types.
"""

import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--translations", required=True)
    ap.add_argument("--shards", type=int, default=1)
    ap.add_argument("--out-prefix", required=True)
    args = ap.parse_args()
    src = {r["key"]: r for r in map(json.loads, (HERE / "data" / "ifeval_input_data.jsonl").open())}
    newest = {}
    for r in map(json.loads, Path(args.translations).open()):
        if not r["error"]:
            newest[r["key"]] = r["output"]
    rows = [{"key": k, "instruction_id_list": src[k]["instruction_id_list"],
             "english": {"prompt": src[k]["prompt"], "kwargs": src[k]["kwargs"]},
             "korean": {"prompt": o["prompt"], "kwargs": o["kwargs"]}} for k, o in sorted(newest.items())]
    Path(args.out_prefix).parent.mkdir(parents=True, exist_ok=True)
    for i in range(args.shards):
        part = rows[i::args.shards]
        with open(f"{args.out_prefix}_{i}.jsonl", "w") as f:
            for r in part:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"{args.out_prefix}_{i}.jsonl: {len(part)} items")


if __name__ == "__main__":
    main()
