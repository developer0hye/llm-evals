"""KoBALT-700: Korean linguistic knowledge, 700 ten-option MCQ (snunlp/KoBALT-700@30c30a4).

Prompt: the official template, read verbatim at run time from the JSON block of
the dataset's own evaluation_protocol.md (so no hand-copy can drift).
Extraction: the LAST occurrence of the required closing sentence
"정답은 X입니다" (X in A-J, optional ** / [] around X). Nothing else counts:
no fallback to a letter elsewhere in the text (a lone letter in an explanation
is not an answer).
Known key defect: item 67c81c5d361c7932636b7c14 (Syntax/Scrambling) has options
B and E both "(5)", gold B; both B and E are accepted as correct.
"""

import json
import re
from pathlib import Path

from tasks.base import UNPARSED, Item, sha256_file

NAME = "kobalt"
FILES = {"kobalt.jsonl": "ecc68805e17d1c87b63cbb70ec3ba101eabcbd2c489e813ba229f272f20c092f",
         "kobalt_evaluation_protocol.md": "9f2a2b5cdc8758dc361d1ad376c829785bc4fe9cf7df4a415ba3e98e48cd0388"}
DUPLICATE_OPTION_ITEMS = {"67c81c5d361c7932636b7c14": {"B", "E"}}
_ANSWER_RE = re.compile(r"정답은\s*\**\s*\[?\s*([A-J])\s*\]?\s*\**\s*입니다")
_OPTION_RE = re.compile(r"(?m)^\s*([A-J])\s*[:.)]")


def official_messages(protocol_md: str) -> list[dict]:
    block = re.search(r"```json\s*(\{.*?\})\s*```", protocol_md, re.S).group(1)
    return json.loads(block)["messages"]


def load(data_dir: Path) -> list[Item]:
    for f, sha in FILES.items():
        assert sha256_file(data_dir / f) == sha, f"{f}: SHA-256 mismatch (re-run download_data.sh)"
    template = official_messages((data_dir / "kobalt_evaluation_protocol.md").read_text())
    assert [m["role"] for m in template] == ["system", "user"] and "<QUESTION>" in template[1]["content"]
    rows = json.loads((data_dir / "kobalt.jsonl").read_text())
    assert len(rows) == 700, len(rows)
    items = []
    for r in rows:
        assert sorted(set(_OPTION_RE.findall(r["Question"]))) == list("ABCDEFGHIJ"), r["ID"]
        messages = [dict(template[0]),
                    {"role": "user", "content": template[1]["content"].replace("<QUESTION>", r["Question"])}]
        gold = sorted(DUPLICATE_OPTION_ITEMS.get(r["ID"], {r["Answer"]}))
        items.append(Item(r["ID"], messages, gold, {"class": r["Class"], "subclass": r["Subclass"],
                                                    "level": r["Level"]}))
    return items


def parse(item: Item, response: str) -> str | None:
    hits = _ANSWER_RE.findall(response or "")
    return hits[-1] if hits else None


def score(item: Item, pred: str | None) -> dict:
    if pred is None:
        return {"outcome": UNPARSED}
    return {"outcome": "correct" if pred in item.gold else "wrong"}
