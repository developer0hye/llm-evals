"""LBox Open casename_classification test (lbox/lbox_open@10429ac): read the facts of a
Korean court judgment, pick the case name (사건명) from 100 classes.

1,000 items, exactly 10 per class. The label list is derived from the file and
shown to the model in full. A reply counts only if its final "사건명:" line is
exactly one of the 100 labels (outer quotes, brackets and ** stripped);
anything else, including a close paraphrase, is no_answer_unparsed.
Per-item `label_leak` flags items whose case name, reduced by a heuristic
(first offence of a compound label, "위반" and parentheticals removed), appears
verbatim in the facts (~27% of test); report accuracy split by it. Some labels
overlap structurally (e.g. 건물명도(인도) vs 건물인도, 손해배상 vs 손해배상(기)),
so 100% is not reachable.
"""

import json
import re
from collections import Counter
from pathlib import Path

from tasks.base import UNPARSED, Item, sha256_file

NAME = "lbox_casename"
FILES = {"lbox_casename_test.jsonl": "e4095da9314786bd7ca782f02e729b8ad2129f809643794d594f07079fcd8d25"}
_ANSWER_RE = re.compile(r"^[\s*#>`]*사건명\s*[:：]\s*(.+?)\s*$")

PROMPT = """다음은 한국 법원 판결문의 사실관계입니다. 이 사건의 사건명을 아래 목록에서 정확히 하나 고르세요.

[사건명 목록]
{labels}

[사실관계]
{facts}

목록에 있는 사건명을 글자 그대로 사용하세요. 답변의 마지막 줄은 반드시 "사건명: [목록의 사건명]" 형식이어야 합니다."""


def leak_key(label: str) -> str:
    first = label.split(",")[0]
    return re.sub(r"\(.*?\)", "", first).replace("위반", "").strip()


def load(data_dir: Path) -> list[Item]:
    for f, sha in FILES.items():
        assert sha256_file(data_dir / f) == sha, f"{f}: SHA-256 mismatch (re-run download_data.sh)"
    rows = [json.loads(l) for l in (data_dir / "lbox_casename_test.jsonl").open(encoding="utf-8")]
    counts = Counter(r["casename"] for r in rows)
    assert len(rows) == 1000 and len(counts) == 100 and set(counts.values()) == {10}, (len(rows), len(counts))
    labels = sorted(counts)
    label_block = "\n".join(f"- {l}" for l in labels)
    items = []
    for r in rows:
        key = leak_key(r["casename"])
        items.append(Item(str(r["id"]),
                          [{"role": "user", "content": PROMPT.format(labels=label_block, facts=r["facts"])}],
                          r["casename"],
                          {"casetype": r["casetype"], "labels": labels,
                           "label_leak": bool(key) and key in r["facts"]}))
    return items


def parse(item: Item, response: str) -> str | None:
    lines = [m.group(1) for m in map(_ANSWER_RE.match, (response or "").splitlines()) if m]
    if not lines:
        return None
    ans = lines[-1].strip().strip("*").strip().strip("\"'“”‘’[]「」").strip()
    return ans if ans in item.meta["labels"] else None


def score(item: Item, pred: str | None) -> dict:
    if pred is None:
        return {"outcome": UNPARSED}
    return {"outcome": "correct" if pred == item.gold else "wrong"}
