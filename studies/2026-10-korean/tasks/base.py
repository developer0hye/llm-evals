"""Shared item type and outcome vocabulary for the four task modules.

Every task module exposes:
    NAME, load(data_dir) -> list[Item], parse(item, response) -> pred | None,
    score(item, pred) -> dict with at least {"outcome": ...}.
KoSimpleQA additionally exposes judge_messages() and parse_judge().

Outcomes are never inferred from infrastructure: API/transport failures are
errors (retried), not outcomes. A response cut at max_tokens is
"no_answer_truncated" and is never parsed, even if an answer can be pulled from
the half-written text. A finished response with no explicitly stated answer is
"no_answer_unparsed".
"""

import hashlib
import json
from dataclasses import dataclass, field

TRUNCATED = "no_answer_truncated"
UNPARSED = "no_answer_unparsed"


@dataclass
class Item:
    id: str
    messages: list[dict]
    gold: object
    meta: dict = field(default_factory=dict)

    @property
    def prompt_sha256(self) -> str:
        return hashlib.sha256(json.dumps(self.messages, ensure_ascii=False).encode()).hexdigest()

    @property
    def gold_sha256(self) -> str:
        return hashlib.sha256(json.dumps(self.gold, ensure_ascii=False, sort_keys=True,
                                         default=list).encode()).hexdigest()


def sha256_file(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()
