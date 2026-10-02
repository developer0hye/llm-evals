#!/usr/bin/env python3
"""Draw the 40-item native-speaker review sample (NOTES.md section 4, step 7) and write a review sheet.

Usage:
    python3 human_review_sample.py      # writes work/human_review_40.md

Uniform random sample of the released items, random.Random(20261001), drawn once. The sheet shows the
English source, the Korean item and its kwargs, with three questions per item. Fill in the answers;
until then no human validation is claimed.
"""

import json
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
N, SEED = 40, 20261001


def main():
    src = {r["key"]: r for r in map(json.loads, (HERE / "data" / "ifeval_input_data.jsonl").open())}
    items = [json.loads(l) for l in (HERE / "release" / "ko_ifeval_v1.jsonl").open()]
    sample = sorted(random.Random(SEED).sample([r["key"] for r in items], N))
    by_key = {r["key"]: r for r in items}
    out = ["# Ko-IFEval v1: native-speaker review sheet (40 items)", "",
           f"Sample: `random.Random({SEED}).sample(keys, {N})` over the 429 released keys.", "",
           "For each item, answer:",
           "1. Natural: is the Korean prompt natural Korean? (yes / awkward / no)",
           "2. Faithful: does it ask for the same thing as the English, constraint by constraint? (yes / no + what differs)",
           "3. Scorable: would an answer that follows the Korean prompt pass the kwargs as written? (yes / no + why)", ""]
    for k in sample:
        r = by_key[k]
        out += [f"## {k}", "", f"**instructions:** `{', '.join(r['instruction_id_list'])}`", "",
                "**English**", "", "```", src[k]["prompt"], "```", "",
                "**Korean**", "", "```", r["prompt"], "```", "",
                f"**kwargs:** `{json.dumps(r['kwargs'], ensure_ascii=False)}`", "",
                "- Natural: ", "- Faithful: ", "- Scorable: ", ""]
    (HERE / "work" / "human_review_40.md").write_text("\n".join(out))
    print("sample:", sample)


if __name__ == "__main__":
    main()
