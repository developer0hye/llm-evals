#!/usr/bin/env python3
"""Deterministic checks that a Korean IFEval item's prompt agrees with its checker kwargs.

Usage:
    python3 validate.py --ifeval-ko evidence/ifeval_ko_audit/ifeval_ko_54199e3.parquet   # audit IFEval-Ko
    python3 validate.py --translations work/translations.jsonl                            # validate ours
    python3 validate.py --translations release/hanifeval_v1.jsonl                         # validate the release

Each item is compared with its English source (google/IFEval, matched by key).
Checks, each reported per item:
  ids_changed        instruction_id_list differs from the source
  kwargs_changed     a non-string kwarg (number, relation, language, marker) differs from the source
  string_not_in_prompt  a translated string kwarg (keywords, keyword, forbidden_words, end_phrase,
                     first_word, prompt_to_repeat, section_spliter) is not a verbatim substring of the prompt
  latin_kwarg        a translated string kwarg is still in Latin script (allowed: json, P.S.-style markers)
  number_missing     a numeric kwarg value does not appear in the prompt (digits or a Korean numeral word)
  boundary_wording   the Korean qualifier next to the number disagrees with the checker relation
                     (less than N written as 이하/이내/까지/최대; at least N written as N-1 초과/넘게, or as N-1 이상)
  char_unit_for_words  number_words constraint phrased with 자/글자
  repeat_wording     repeat_prompt item lacks an instruction that nothing may precede the repetition
  constrained_options  constrained_response item lacks one of the three fixed Korean options
  ge_wording         a count the checker scores as >= N (sections, highlights, placeholders) is stated
                     without 이상/최소 in the prompt (added in v1.1, after external review)
  keyword_not_in_kwargs  a quoted word in the sentence that asks for keywords is missing from the kwargs
                     (added in v1.1; the case was 3311, inherited from google/IFEval)
  repeat_conflict    the text the answer must repeat violates another constraint of the same item
                     (an ASCII comma under no_comma, or a forbidden word); unsatisfiable under strict scoring
Writes a JSON report (--report) and prints counts.
"""

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
STRING_KEYS = ("keywords", "keyword", "forbidden_words", "end_phrase", "first_word", "prompt_to_repeat", "section_spliter")
NUM_KEYS = ("num_words", "num_sentences", "num_paragraphs", "num_highlights", "num_bullets",
            "num_placeholders", "num_sections", "frequency", "nth_paragraph")
KO_NUM = {1: "한|하나|첫", 2: "두|둘", 3: "세|셋", 4: "네|넷", 5: "다섯", 6: "여섯", 7: "일곱", 8: "여덟", 9: "아홉", 10: "열"}
OPTIONS = ("제 답변은 예입니다.", "제 답변은 아니요입니다.", "제 답변은 아마도입니다.")
UNIT = r"(?:개의?|회|번|단어|문장|단락|문단|줄|섹션|항목)?"
QUAL = r"(이상|이하|미만|초과|넘게|넘는|넘지|보다\s*적게|보다\s*많이|이내|까지|최대|최소)"


def clean(kw):
    out = {}
    for k, v in (kw or {}).items():
        if v is None or (isinstance(v, float) and v != v):
            continue
        if hasattr(v, "tolist"):
            v = v.tolist()
        if isinstance(v, float) and v == int(v):
            v = int(v)
        out[k] = v
    return out


def check_item(src, prompt, ids, kwargs):
    issues = []
    if list(ids) != src["instruction_id_list"]:
        issues.append(("ids_changed", ""))
    for iid, kw, skw in zip(src["instruction_id_list"], kwargs, src["kwargs"]):
        kw, skw = clean(kw), {k: v for k, v in skw.items() if v is not None}
        for k, v in skw.items():
            if k in STRING_KEYS:
                continue
            if kw.get(k) != v:
                issues.append(("kwargs_changed", f"{iid}.{k}: {v!r} -> {kw.get(k)!r}"))
        for k in STRING_KEYS:
            vals = kw.get(k)
            if vals is None:
                continue
            for s in (vals if isinstance(vals, list) else [vals]):
                if k == "prompt_to_repeat":
                    if s.strip() not in prompt:
                        issues.append(("string_not_in_prompt", f"{iid}.{k}"))
                elif s not in prompt:
                    issues.append(("string_not_in_prompt", f"{iid}.{k}={s!r}"))
                if k != "prompt_to_repeat" and not re.search(r"[가-힣]", s) and s.lower() not in ("json",):
                    issues.append(("latin_kwarg", f"{iid}.{k}={s!r}"))
        rel = kw.get("relation")
        for k in NUM_KEYS:
            if k not in kw:
                continue
            n = int(kw[k])
            if not re.search(rf"(?<!\d){n}(?!\d)", prompt) and not (n in KO_NUM and re.search(KO_NUM[n], prompt)):
                issues.append(("number_missing", f"{iid}.{k}={n}"))
            if rel:
                for m in re.finditer(rf"(\d+)\s*{UNIT}\s*(?:을|를|이|가)?\s*{QUAL}", prompt):
                    pn, q = int(m.group(1)), re.sub(r"\s", "", m.group(2))
                    if pn not in (n, n - 1):
                        continue
                    if rel == "less than" and q in ("이하", "이내", "까지", "최대") and pn == n:
                        issues.append(("boundary_wording", f"{iid}: checker < {n}, prompt '{m.group(0)}'"))
                    if rel == "at least" and ((pn == n - 1 and q in ("이상", "최소")) or (pn == n and q in ("초과", "넘게", "넘는", "보다많이"))):
                        issues.append(("boundary_wording", f"{iid}: checker >= {n}, prompt '{m.group(0)}'"))
        if iid == "length_constraints:number_words" and re.search(r"\d+\s*(?:자|글자)(?![가-힣])", prompt):
            issues.append(("char_unit_for_words", iid))
        src_says_nothing_before = bool(re.search(r"(?i)(not|n't|nothing|before)[^.\n]{0,60}(say|output|write)|very beginning|before you say", src["prompt"]))
        if iid == "combination:repeat_prompt" and src_says_nothing_before and not re.search(
                r"(아무|어떤|어떠한|다른)[^.\n]{0,25}(말|단어|문자|글자)[^.\n]{0,30}(앞에|전에|전까지)"
                r"|(앞에|전에|전까지|전에는)[^.\n]{0,40}(아무|어떤|어떠한|다른)[^.\n]{0,20}(말|단어|문자|글자)"
                r"|맨\s*앞|가장\s*먼저|맨\s*처음|처음에", prompt):
            issues.append(("repeat_wording", iid))
        if iid == "detectable_format:constrained_response" and not all(o in prompt for o in OPTIONS):
            issues.append(("constrained_options", iid))
    GE_KEYS = {"detectable_format:multiple_sections": "num_sections",
               "detectable_format:number_highlighted_sections": "num_highlights",
               "detectable_content:number_placeholders": "num_placeholders"}
    for iid, kw in zip(ids, kwargs):
        kw = clean(kw)
        if iid in GE_KEYS and GE_KEYS[iid] in kw:
            n = int(kw[GE_KEYS[iid]])
            stated = re.search(rf"(?<!\d){n}(?!\d)|({KO_NUM.get(n, 'X')})\s*(개|번|군데|곳|가지)", prompt)
            if stated and not re.search(r"이상|최소|적어도", prompt):
                issues.append(("ge_wording", f"{iid}: checker >= {n}, prompt states the count without 이상/최소"))
        if iid == "keywords:existence":
            want = {w for k2 in kwargs for w in (clean(k2).get("keywords") or [])}
            want |= {clean(k2)["keyword"] for k2 in kwargs if clean(k2).get("keyword")}
            want |= {w for k2 in kwargs for w in (clean(k2).get("forbidden_words") or [])}
            for sent in re.split(r"(?<=[.?!])\s+", prompt):
                if "키워드" in sent or "단어" in sent:
                    quoted = re.findall(r"['\"‘“]([^'\"’”]{1,15})['\"’”]", sent)
                    if want & set(quoted):
                        for q in quoted:
                            if q not in want and re.search(r"[가-힣A-Za-z]", q):
                                issues.append(("keyword_not_in_kwargs", f"{q!r} requested, kwargs {sorted(want)}"))
    rep = next((clean(kw).get("prompt_to_repeat") for kw in kwargs if clean(kw).get("prompt_to_repeat")), None)
    if rep:
        for iid, kw in zip(ids, kwargs):
            kw = clean(kw)
            if iid == "punctuation:no_comma" and "," in rep:
                issues.append(("repeat_conflict", "comma in prompt_to_repeat under no_comma"))
            for w in kw.get("forbidden_words") or []:
                if w.lower() in rep.lower():
                    issues.append(("repeat_conflict", f"forbidden {w!r} in prompt_to_repeat"))
    return issues


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--ifeval-ko")
    g.add_argument("--translations")
    ap.add_argument("--report", default=None)
    args = ap.parse_args()
    src = {r["key"]: r for r in map(json.loads, (HERE / "data" / "ifeval_input_data.jsonl").open())}
    items = []
    if args.ifeval_ko:
        import pandas as pd
        for _, r in pd.read_parquet(args.ifeval_ko).iterrows():
            items.append((int(r["key"]), r["prompt"], list(r["instruction_id_list"]), list(r["kwargs"])))
    else:
        newest = {}
        for r in map(json.loads, Path(args.translations).open()):
            if "prompt" in r:                      # release file: one item per row
                newest[r["key"]] = r
            elif not r["error"]:                   # translate.py log: newest ok row wins
                newest[r["key"]] = r["output"]
        for k, o in newest.items():
            items.append((k, o["prompt"], o["instruction_id_list"], o["kwargs"]))
    report, counts, flagged = {}, Counter(), 0
    for key, prompt, ids, kwargs in sorted(items):
        iss = check_item(src[key], prompt, ids, kwargs)
        if iss:
            flagged += 1
            report[key] = iss
            for t, _ in iss:
                counts[t] += 1
    print(f"items {len(items)}, flagged {flagged} ({flagged / len(items):.1%})")
    by_items = defaultdict(set)
    for k, iss in report.items():
        for t, _ in iss:
            by_items[t].add(k)
    for t, c in counts.most_common():
        print(f"  {t:22s} {c:4d} issues in {len(by_items[t]):3d} items")
    if args.report:
        Path(args.report).write_text(json.dumps({"items": len(items), "flagged": flagged,
                                                 "counts": counts, "report": report}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
