"""KoSimpleQA: Korea-specific short-form factuality (naver-ai/KoSimpleQA@1bdbb61,
updated_kosimpleqa_with_trans.json, the 938-item set that matches arXiv:2510.18368 v2).

The model gets the Korean question alone. An LLM judge grades each answer with
the SimpleQA grader prompt (vendored from openai/simple-evals, MIT) as
CORRECT / INCORRECT / NOT_ATTEMPTED. Metrics as defined in the paper, section 3.3:
CO, NA, IN, CGA = CO / (CO + IN), F = harmonic mean of CO and CGA.

Deviations, both disclosed in the study README:
- The paper's Appendix E counter-examples for NOT_ATTEMPTED are not applied (the
  paper's text is not licensed for copying), so vague answers and false refusals
  may be graded NOT_ATTEMPTED more often than in the paper.
- simple-evals maps an unparseable judge reply to NOT_ATTEMPTED. Here it is a
  judge error: logged and retried, never counted as the model declining.
"""

import json
import re
from pathlib import Path

from tasks.base import Item, sha256_file
from third_party.simple_evals_grader import GRADER_TEMPLATE

NAME = "kosimpleqa"
FILES = {"kosimpleqa.json": "4d6d41c70dcffc32a794c454fb832eb0088ea63bc3c99c1009f04fbd49ab68a8"}
GRADES = {"A": "correct", "B": "incorrect", "C": "not_attempted"}


def load(data_dir: Path) -> list[Item]:
    for f, sha in FILES.items():
        assert sha256_file(data_dir / f) == sha, f"{f}: SHA-256 mismatch (re-run download_data.sh)"
    rows = json.loads((data_dir / "kosimpleqa.json").read_text())
    assert len(rows) == 938, len(rows)
    assert len({r["id"] for r in rows}) == 938
    return [Item(str(r["id"]), [{"role": "user", "content": r["content"]}], r["answer"],
                 {"category": r["category"], "answer_type": r["answer_type"]}) for r in rows]


def parse(item: Item, response: str) -> str | None:
    # The whole answer goes to the judge; an empty answer cannot be graded.
    text = (response or "").strip()
    return text or None


def judge_messages(item: Item, pred: str) -> list[dict]:
    return [{"role": "user", "content": GRADER_TEMPLATE.format(
        question=item.messages[0]["content"], target=item.gold, predicted_answer=pred)}]


def parse_judge(text: str) -> str | None:
    """The grader is told to return only A, B or C. Anything else is a judge error."""
    m = re.fullmatch(r"\W*([ABC])\W*", (text or "").strip())
    return GRADES[m.group(1)] if m else None


def score(item: Item, pred: str | None) -> dict:
    # Final grades come from the judge stage in run.py; this only marks what the judge must see.
    return {"outcome": "needs_judge" if pred else "no_answer_unparsed"}


def metrics(outcomes: list[str]) -> dict:
    """Paper metrics over all items, plus NR for rows with no gradable answer.

    NR (no response): truncated at max_tokens or empty. The paper has no such
    class. NR rows get no credit in CO and F, but are neither INCORRECT (they are
    not a wrong claim, so they must not inflate the hallucination rate) nor
    NOT_ATTEMPTED (they are not an explicit refusal). CGA excludes them.
    """
    n = len(outcomes)
    co = sum(o == "correct" for o in outcomes) / n
    na = sum(o == "not_attempted" for o in outcomes) / n
    inc = sum(o == "incorrect" for o in outcomes) / n
    nr = sum(o in ("no_answer_truncated", "no_answer_unparsed") for o in outcomes) / n
    cga = co / (co + inc) if co + inc else 0.0
    f = 2 * co * cga / (co + cga) if co + cga else 0.0
    return {"n": n, "CO": co, "NA": na, "IN": inc, "NR": nr, "CGA": cga, "F": f}
