"""KLUE-NER v1.1 dev (KLUE-benchmark/KLUE@3efd987): Korean NER, 6 types, character-level BIO.

The test split's labels are not released (the evaluation server is gone), so the
dev split is the evaluation set: 5,000 sentences, 14,257 entities (KLUE paper
Table 9). Gold spans are read from the per-character BIO rows, not from the
"##" header line (whose inline <text:TAG> form is ambiguous: 18 dev sentences
contain literal '<' or '>', one even contains "<일:;LC>").

Output format asked of the model: the sentence copied exactly, each entity
wrapped as ⟦text|TYPE⟧, on a final line starting "결과:". The three delimiter
characters ⟦ ⟧ | do not occur anywhere in the dev text, so parsing is
unambiguous. A reply counts only if removing the markers reproduces the input
sentence exactly (outer whitespace aside); otherwise it is no_answer_unparsed.
Scoring: entity-level exact (start, end, type) match -> TP/FP/FN per sentence,
aggregated to micro-F1 in analyze.py. An unparsed reply scores TP 0, FP 0,
FN = all gold entities.

Sensitivity check (pre-registered 2026-09-29, before any pilot or main score):
`parse(..., lenient=True)` also accepts a copy that differs from the sentence
only in trailing punctuation or whitespace (" .!?…~。"), e.g. an added final
period. Offsets are unaffected because only the end of the string may differ.
The strict rule stays primary; analyze.py reports both.
"""

import re
from pathlib import Path

from tasks.base import UNPARSED, Item, sha256_file

NAME = "klue_ner"
FILES = {"klue-ner-v1.1_dev.tsv": "0f4d5e818f7b82d299c3a87856fc40a706f5943207580ddb252397e387050a54"}
TYPES = ["PS", "LC", "OG", "DT", "TI", "QT"]
_SPAN_RE = re.compile(r"⟦([^⟦⟧|]+)\|(PS|LC|OG|DT|TI|QT)⟧")
_RESULT_RE = re.compile(r"^[\s*#>`]*결과\s*[:：]\s?(.*)$")
_TRAIL = " .!?…~。"

PROMPT = """다음 한국어 문장에서 개체명을 찾아 표시하세요.

개체명 유형 (6종):
- PS: 인명 (사람 이름, 별명)
- LC: 지명 (국가, 도시, 지역, 장소, 건물 등)
- OG: 기관명 (회사, 정부 기관, 단체, 팀 등)
- DT: 날짜 (연, 월, 일, 요일, 기간 등 날짜 표현)
- TI: 시간 (시, 분, 초, 시간대 등 시간 표현)
- QT: 수량 (숫자가 포함된 수량, 나이, 금액, 비율, 순서 등)

규칙:
- 문장을 한 글자도 바꾸지 말고 그대로 옮겨 적되, 각 개체명을 ⟦개체명|유형⟧ 형태로 감싸세요.
- 조사는 개체명에 포함하지 마세요. 예: "서울에서" → "⟦서울|LC⟧에서"
- 개체명이 없으면 문장을 그대로 적으세요.
- 마지막 줄은 반드시 "결과: "로 시작하고, 그 뒤에 표시된 문장 전체를 한 줄로 적으세요.

예시
문장: 김철수는 2023년 3월 삼성전자에 입사해 서울 본사에서 3년간 일했다.
결과: ⟦김철수|PS⟧는 ⟦2023년 3월|DT⟧ ⟦삼성전자|OG⟧에 입사해 ⟦서울|LC⟧ 본사에서 ⟦3년간|DT⟧ 일했다.

문장: {sentence}"""


def read_dev(path: Path) -> list[tuple[str, str, list[tuple[int, int, str]]]]:
    """-> [(id, sentence, [(start, end_exclusive, type), ...])] from the per-character BIO rows."""
    out = []
    for block in path.read_text(encoding="utf-8").strip().split("\n\n"):
        lines = block.split("\n")
        sid = next((l[3:].split("\t")[0] for l in lines if l.startswith("## klue-ner")), None)
        rows = [l for l in lines if not l.startswith("##")]
        if sid is None or not rows:
            continue  # the file's format-description header block
        chars, tags = [], []
        for row in rows:
            ch, _, tag = row.partition("\t")
            chars.append(ch if ch else " ")
            tags.append(tag)
        spans, start, typ = [], None, None
        for i, tag in enumerate(tags + ["O"]):
            if start is not None and not (tag.startswith("I-") and tag[2:] == typ):
                spans.append((start, i, typ))
                start = None
            if tag.startswith("B-"):
                start, typ = i, tag[2:]
        out.append((sid, "".join(chars), spans))
    return out


def load(data_dir: Path) -> list[Item]:
    for f, sha in FILES.items():
        assert sha256_file(data_dir / f) == sha, f"{f}: SHA-256 mismatch (re-run download_data.sh)"
    rows = read_dev(data_dir / "klue-ner-v1.1_dev.tsv")
    assert len(rows) == 5000, len(rows)
    assert sum(len(s) for _, _, s in rows) == 14257
    for _, sent, _ in rows:
        assert not any(c in sent for c in "⟦⟧|")
    return [Item(sid, [{"role": "user", "content": PROMPT.format(sentence=sent)}],
                 [list(s) for s in spans],
                 {"sentence": sent, "source": sid.rsplit("-", 1)[-1]}) for sid, sent, spans in rows]


def parse(item: Item, response: str, lenient: bool = False) -> list[tuple[int, int, str]] | None:
    sentence = item.meta["sentence"]
    lines = [m.group(1) for m in map(_RESULT_RE.match, (response or "").splitlines()) if m]
    if not lines:
        return None
    marked = lines[-1].strip()
    spans, plain, pos = [], [], 0
    for m in _SPAN_RE.finditer(marked):
        plain.append(marked[pos:m.start()])
        start = sum(map(len, plain))
        plain.append(m.group(1))
        spans.append((start, start + len(m.group(1)), m.group(2)))
        pos = m.end()
    plain.append(marked[pos:])
    plain = "".join(plain)
    if any(c in plain for c in "⟦⟧"):
        return None
    if plain != sentence.strip():
        if not (lenient and plain.rstrip(_TRAIL) == sentence.strip().rstrip(_TRAIL)):
            return None
        if any(e > len(sentence.strip().rstrip(_TRAIL)) for _, e, _ in spans):
            return None  # an entity over the altered tail cannot be placed
    lead = len(sentence) - len(sentence.lstrip())
    return [(s + lead, e + lead, t) for s, e, t in spans]


def score(item: Item, pred: list | None) -> dict:
    gold = {tuple(s) for s in item.gold}
    if pred is None:
        return {"outcome": UNPARSED, "tp": 0, "fp": 0, "fn": len(gold)}
    pred = set(pred)
    return {"outcome": "parsed", "tp": len(gold & pred), "fp": len(pred - gold), "fn": len(gold - pred),
            "pred_spans": sorted(pred)}
