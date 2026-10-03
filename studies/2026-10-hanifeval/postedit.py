#!/usr/bin/env python3
"""Apply the logged manual edits to the Gemini translations and write the release files.

Usage:
    python3 postedit.py                     # writes release/hanifeval_v1.jsonl, release/provenance.json,
                                            # and work/review/responses_final.jsonl

Every edit is a literal entry in EDITS below: which item, which string is replaced in the prompt
(and in prompt_to_repeat, which must stay a substring of the prompt), which kwargs change, why, and
which finding triggered it. Each `old` string must be present, so a stale table fails loudly.
Items not listed are released exactly as Gemini 3.1 Pro produced them (guideline v1.1).

The same string edits are applied to the reviewers' satisfiability answers (RESPONSE_EDITS), so the
satisfiability check can be re-run on the released items; those edits are logged too.
"""

import copy
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
COMMA = "쉼표(,)"

# finding: R = semantic review (work/review/review_*.jsonl), V = validator repeat_conflict,
#          C = corpus screen (work/lexical_collisions.json)
EDITS = [
    *[{"key": k, "id": f"E{i + 1:02d}", "finding": "R+V",
       "prompt": [(COMMA, "쉼표")], "repeat": [(COMMA, "쉼표")], "kwargs": {},
       "reason": "Guideline rule 6 wording '쉼표(,)' put an ASCII comma inside prompt_to_repeat, so the "
                 "required verbatim repeat always fails punctuation:no_comma (strict). '(,)' removed from "
                 "prompt and prompt_to_repeat."}
      for i, k in enumerate([1546, 1627, 2063, 2337, 2713, 2739, 3633, 3718])],
    {"key": 1691, "id": "E09", "finding": "R+C",
     "prompt": [("모저크리스탈", "모저"), ("카를로비바리", "바리")], "repeat": [],
     "kwargs": {1: {"forbidden_words": ["모저", "유리공장", "프라프치체", "카를로비", "바리"]}},
     "reason": "Guideline v1.1 over-corrected: '모저크리스탈' lets bare '모저' pass. Reverted to the v1.0 "
               "pilot rendering (Gemini output, work/pilot_translations.jsonl). Corpus screen: '모저' "
               "0.00/10k, '바리' 0.31/10k eojeol, so the collision v1.1 guarded against is rare."},
    {"key": 2471, "id": "E10", "finding": "R+C",
     "prompt": [("'미친'", "'광기'")], "repeat": [],
     "kwargs": {0: {"forbidden_words": ["슬픈", "광기", "스트레스"]}},
     "reason": "'미친' (crazy) is a substring of '영향을 미친다', routine in the requested academic paper, "
               "so faithful answers fail. Replaced by another negative example word, '광기' (madness; "
               "0.00/10k). The English lists the words as examples ('such as')."},
    {"key": 2549, "id": "E11", "finding": "R+C",
     "prompt": [("'가오'", "'gao'")], "repeat": [],
     "kwargs": {1: {"keywords": ["gao", "하트"]}},
     "reason": "Keyword '가오' is satisfied by '다가오는' (0.46/10k), giving free credit. The source "
               "keyword 'gao' is a nonce token; kept in Latin script, as in the English item."},
    {"key": 3369, "id": "E12", "finding": "R",
     "prompt": [], "repeat": [],
     "kwargs": {1: {"keyword": "옳"}},
     "reason": "Keyword '옳다' (dictionary form) misses 옳은/옳습니다, so the '< 2' cap was near-vacuous. "
               "Stem '옳' (0.15/10k) counts all forms. Consequence: the required repeat now contains it "
               "twice (옳은, 옳다), so the item is unsatisfiable under strict scoring, exactly like the "
               "English source ('right' twice in the repeat). Tagged source_unsatisfiable_strict."},
    {"key": 1733, "id": "E13", "finding": "R",
     "prompt": [], "repeat": [],
     "kwargs": {0: {"keyword": "대답했"}},
     "reason": "Keyword '대답했다' fails a fairy tale written in -습니다 style ('대답했습니다'). Stem "
               "'대답했' covers both and is a substring of the prompt's '대답했다'."},
    {"key": 2515, "id": "E14", "finding": "R",
     "prompt": [("1개의 구역을", "최소 1개의 구역을")], "repeat": [], "kwargs": {},
     "reason": "Source 'at least one'; kwargs num_highlights >= 1. '1개의' read as exactly one."},
    {"key": 3629, "id": "E15", "finding": "R",
     "prompt": [("핵심 부분 1개를", "핵심 부분을 1개 이상")], "repeat": [], "kwargs": {},
     "reason": "Source 'some key parts'; kwargs >= 1. '1개를' read as exactly one."},
    {"key": 3549, "id": "E16", "finding": "R",
     "prompt": [("정확히 두 번", "두 번 이상")], "repeat": [], "kwargs": {},
     "reason": "Translator added 'exactly'; source 'twice', kwargs num_highlights >= 2."},
    {"key": 3624, "id": "E17", "finding": "R",
     "prompt": [('(예: "\n\n")', '(예: "\\n\\n")')], "repeat": [], "kwargs": {},
     "reason": "The source's literal '\\n\\n' example became two real newlines (an empty quote). "
               "Restored the literal. Not scored."},
]

# Known issues kept in the release (not edited). Codes are defined in NOTES.md section 7.
KNOWN = {
    374: ["source_unsatisfiable_strict"], 3371: ["source_unsatisfiable_strict"],
    3369: ["source_unsatisfiable_strict"],
    2028: ["lexical_collision"],
    1580: ["lexical_inflection_weak"],
}

# ---- v1.1 (2026-10-03), after two external reviews (NOTES.md section 10) -------------------------
# Applied on top of the v1 items above. v1 stays byte-identical in release/hanifeval_v1.jsonl.
GE = "Checker scores this count as >= N (as in Google's IFEval); the prompt said N."
EDITS_V11 = [
    *[{"key": k, "id": f"V11-{i + 1:02d}", "finding": "review-1, review-2",
       "prompt": [(old, new)], "kwargs": {}, "reason": GE + " Now states 'N개 이상'."}
      for i, (k, old, new) in enumerate([
          (357, "응답은 3개의 섹션으로", "응답은 3개 이상의 섹션으로"),
          (1127, "4개의 섹션으로 구성되어야", "4개 이상의 섹션으로 구성되어야"),
          (1131, "이력서를 4개의 섹션으로", "이력서를 4개 이상의 섹션으로"),
          (1548, "문서는 4개의 섹션으로", "문서는 4개 이상의 섹션으로"),
          (1730, "응답은 5개의 섹션으로", "응답은 5개 이상의 섹션으로"),
          (2023, "시는 4개의 섹션으로", "시는 4개 이상의 섹션으로"),
          (2889, "라는 두 개의 섹션을 포함하세요", "를 포함해 섹션을 두 개 이상 작성하세요"),
          (2925, "농담을 3개의 섹션으로", "농담을 3개 이상의 섹션으로"),
          (3324, "각 버전은 7개의 섹션으로", "각 버전은 7개 이상의 섹션으로"),
          (340, "섹션을 1개 포함해 주세요", "섹션을 1개 이상 포함해 주세요"),
      ])],
    {"key": 1342, "id": "V11-11", "finding": "review-2 F01; corpus screen (사진 10.86/10k)",
     "prompt": [('"사진"이라는 단어는 언급하지 마세요.',
                 '"사진"이라는 단어는 언급하지 마세요("청사진"처럼 "사진"이 들어간 다른 단어도 쓰지 마세요).')],
     "kwargs": {},
     "reason": "keywords:frequency < 1 on '사진' is a substring rule, so '청사진' (a common business word) fails. "
               "The prompt now states the rule the checker applies, as item 3114 does ('글자')."},
    {"key": 1466, "id": "V11-12", "finding": "review-1, review-2 F11",
     "prompt": [("'테일러', '스위프트', '투게더'라는 단어는",
                 "'테일러', '스위프트', '투게더'라는 단어(영문 'Taylor', 'Swift', 'Together' 포함)는")],
     "kwargs": {1: {"forbidden_words": ["테일러", "스위프트", "투게더", "Taylor", "Swift", "Together"]}},
     "reason": "The prompt keeps the English song title, so the Latin forms escaped the Hangul-only forbidden list; "
               "the English item forbids them. Latin forms added to prompt and kwargs (matching is case-insensitive)."},
    {"key": 1733, "id": "V11-13", "finding": "review-1, review-2 F04",
     "prompt": [("'대답했다'라는 단어가 최소 2번 이상 포함되어야 합니다.",
                 "'대답했다'라는 표현이 최소 2번 이상 포함되어야 합니다('대답했습니다'처럼 어미가 바뀐 형태도 셉니다).")],
     "kwargs": {},
     "reason": "Since v1 (E13) the checker counts the stem '대답했'; the prompt now says that inflected forms count."},
    {"key": 3311, "id": "V11-14", "finding": "review-2 F05 (inherited from google/IFEval)",
     "prompt": [], "kwargs": {2: {"keywords": ["지표", "목표", "관리"]}},
     "reason": "The prompt requires three keywords; the source kwargs check two ('objective' missing). "
               "v1.1 fixes inherited prompt/kwargs mismatches on scored instructions."},
    {"key": 30, "id": "V11-15", "finding": "review-2 F15",
     "prompt": [("소문자로 답변해 주세요. ", "")], "kwargs": {},
     "reason": "'Answer in lower case' has no meaning for Hangul and is not scored (the change_case checker is not "
               "in this item). Removed; adaptation = task."},
    {"key": 2807, "id": "V11-16", "finding": "review-2 F15",
     "prompt": [(" 오직 소문자만 사용하세요.", "")], "kwargs": {},
     "reason": "Same as V11-15."},
]
KNOWN_V11 = {**KNOWN,
             2859: ["source_checker_artifact"],     # XML closing tags count as a sentence (review-2 F03)
             3305: ["source_contradiction"],        # Hindi-only answer must start with a Korean repeat (F07)
             2078: ["source_contradiction"]}       # exactly 1 bullet vs "a few bullet points"
# adaptation: how far an item departs from a word-for-word rendering of the English task.
#   task    = the constraint itself was changed (2716 'the' -> '회사', 2207 'have' -> '영향', 30/2807 removed)
#   lexical = a keyword/forbidden string's scope differs from the English word (synonym choice, stem, syllable)
ADAPTATION = {**{k: "task" for k in (2716, 2207, 30, 2807)},
              **{k: "lexical" for k in (127, 301, 1242, 1342, 1476, 1580, 1629, 1733, 1936, 2028, 2041, 2395,
                                         2471, 2577, 2997, 3081, 3114, 3345, 3369, 3386)}}
ANSWER_LANGUAGE = {1137: ["fr"], 1675: ["de"], 2534: ["de", "ko"]}   # items without a language checker
RESPONSE_EDITS_V11 = []   # filled below if a reviewer answer needs to follow a v1.1 edit

RESPONSE_EDITS = [
    *[{"key": k, "old": COMMA, "new": "쉼표", "reason": f"follow {e}"}
      for e, k in zip([f"E{i + 1:02d}" for i in range(8)], [1546, 1627, 2063, 2337, 2713, 2739, 3633, 3718])],
    {"key": 2549, "old": "가오", "new": "gao", "reason": "follow E11"},
]


def main():
    src = {r["key"]: r for r in map(json.loads, (HERE / "data" / "ifeval_input_data.jsonl").open())}
    rows = {}
    for r in map(json.loads, (HERE / "work" / "translations.jsonl").open()):
        if not r["error"]:
            rows[r["key"]] = r
    items = {k: json.loads(json.dumps(r["output"])) for k, r in rows.items()}
    for e in EDITS:
        o = items[e["key"]]
        for old, new in e["prompt"]:
            assert o["prompt"].count(old) == 1, (e["id"], old)
            o["prompt"] = o["prompt"].replace(old, new)
        for old, new in e["repeat"]:
            kw = next(kw for kw in o["kwargs"] if kw and kw.get("prompt_to_repeat"))
            assert old in kw["prompt_to_repeat"], (e["id"], old)
            kw["prompt_to_repeat"] = kw["prompt_to_repeat"].replace(old, new)
        for idx, upd in e["kwargs"].items():
            o["kwargs"][idx].update(upd)
    out_dir = HERE / "release"
    out_dir.mkdir(exist_ok=True)
    edited = {e["key"] for e in EDITS}
    with (out_dir / "hanifeval_v1.jsonl").open("w", encoding="utf-8") as f:
        for k in sorted(items):
            o = items[k]
            subset = "response_language" if "language:response_language" in o["instruction_id_list"] else "core"
            f.write(json.dumps({"key": k, "prompt": o["prompt"], "instruction_id_list": o["instruction_id_list"],
                                "kwargs": o["kwargs"], "subset": subset, "edited": k in edited,
                                "known_issues": KNOWN.get(k, [])}, ensure_ascii=False) + "\n")
    resp = {}
    for p in sorted((HERE / "work" / "review").glob("responses_[0-9].jsonl")):  # reviewer shards only
        if p.name == "responses_final.jsonl":
            continue
        for r in map(json.loads, p.open()):
            resp[r["key"]] = r["response"]
    for e in RESPONSE_EDITS:
        assert e["old"] in resp[e["key"]], e
        resp[e["key"]] = resp[e["key"]].replace(e["old"], e["new"])
    with (HERE / "work" / "review" / "responses_final.jsonl").open("w", encoding="utf-8") as f:
        for k in sorted(resp):
            f.write(json.dumps({"key": k, "response": resp[k]}, ensure_ascii=False) + "\n")
    # v1.1
    items11 = copy.deepcopy(items)
    for e in EDITS_V11:
        o = items11[e["key"]]
        for old, new in e["prompt"]:
            assert o["prompt"].count(old) == 1, (e["id"], old)
            o["prompt"] = o["prompt"].replace(old, new)
        for idx, upd in e["kwargs"].items():
            o["kwargs"][idx].update(upd)
    ids11 = {}
    for e in EDITS + EDITS_V11:
        ids11.setdefault(e["key"], []).append(e["id"])
    with (out_dir / "hanifeval_v1.1.jsonl").open("w", encoding="utf-8") as f:
        for k in sorted(items11):
            o = items11[k]
            lang = [kw["language"] for kw in o["kwargs"] if kw and kw.get("language")]
            f.write(json.dumps({"key": k, "prompt": o["prompt"], "instruction_id_list": o["instruction_id_list"],
                                "kwargs": o["kwargs"],
                                "subset": "response_language" if lang else "core",
                                "answer_language": lang or ANSWER_LANGUAGE.get(k, ["ko"]),
                                "adaptation": ADAPTATION.get(k, "none"),
                                "edits": ids11.get(k, []),
                                "known_issues": KNOWN_V11.get(k, [])}, ensure_ascii=False) + "\n")
    resp11 = dict(resp)
    for e in RESPONSE_EDITS_V11:
        assert e["old"] in resp11[e["key"]], e
        resp11[e["key"]] = resp11[e["key"]].replace(e["old"], e["new"])
    with (HERE / "work" / "review" / "responses_final_v1.1.jsonl").open("w", encoding="utf-8") as f:
        for k in sorted(resp11):
            f.write(json.dumps({"key": k, "response": resp11[k]}, ensure_ascii=False) + "\n")
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    meta = {k: rows[k] for k in sorted(rows)}
    prov = {
        "source": {"dataset": "google/IFEval", "revision": "966cd89545d6b6acfd7638bc708b98261ca58e84",
                   "items_total": len(src), "items_excluded": len(src) - len(items), "items_released": len(items)},
        "translator": {"model": rows[min(rows)]["model"], "provider_pin": rows[min(rows)]["provider_pin"],
                       "reasoning": rows[min(rows)]["reasoning"], "temperature": rows[min(rows)]["temperature"],
                       "guideline_sha256": sorted({r["guideline_sha256"] for r in meta.values()}),
                       "cost_usd": round(sum(r["cost"] or 0 for r in meta.values()), 4)},
        "checker": "checker/ (allganize/IFEval-Ko@54199e3 with [hanifeval] changes; v1.1 changes listed under v1.1)",
        "edits": [{k: v for k, v in e.items()} | {"prompt": [list(p) for p in e["prompt"]],
                                                   "repeat": [list(p) for p in e["repeat"]]} for e in EDITS],
        "response_edits": RESPONSE_EDITS,
        "known_issues": {str(k): v for k, v in KNOWN.items()},
        "v1.1": {"date": "2026-10-03",
                 "edits": [{k: v for k, v in e.items()} | {"prompt": [list(p) for p in e["prompt"]]}
                           for e in EDITS_V11],
                 "response_edits": RESPONSE_EDITS_V11,
                 "known_issues": {str(k): v for k, v in KNOWN_V11.items()},
                 "adaptation": {str(k): v for k, v in sorted(ADAPTATION.items())},
                 "answer_language_overrides": {str(k): v for k, v in ANSWER_LANGUAGE.items()},
                 "checker_changes": ["sentence splitter: list markers only at line start (review-2 F02, F12)",
                                     "response_language: undetectable text fails (review-2 F13)",
                                     "kwargs strings NFC-normalised (review-1)"]},
        "files": {"release/hanifeval_v1.jsonl": sha(out_dir / "hanifeval_v1.jsonl"),
                  "release/hanifeval_v1.1.jsonl": sha(out_dir / "hanifeval_v1.1.jsonl"),
                  "work/translations.jsonl": sha(HERE / "work" / "translations.jsonl"),
                  "translation_guideline.md": sha(HERE / "translation_guideline.md")},
    }
    (out_dir / "provenance.json").write_text(json.dumps(prov, ensure_ascii=False, indent=1))
    print(f"v1: {len(items)} items, {len(edited)} edited ({len(EDITS)} edits), {len(RESPONSE_EDITS)} response edits")
    print(f"v1.1: +{len(EDITS_V11)} edits on {len({e['key'] for e in EDITS_V11})} items, "
          f"{len(RESPONSE_EDITS_V11)} response edits, {sum(1 for v in KNOWN_V11.values() if v)} items with known_issues")


if __name__ == "__main__":
    main()
