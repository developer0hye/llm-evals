"""Offline tests for every extractor and scorer. Synthetic responses only, no dataset text,
no network. Negative cases encode past failures: a letter picked out of prose
("C2", "option (D)"), a half-written answer, a paraphrased label."""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(HERE), str(HERE.parents[1])]

from common.stats import mcnemar_exact, wilson  # noqa: E402
from tasks import klue_ner, kobalt, kosimpleqa, lbox_casename  # noqa: E402
from tasks.base import Item  # noqa: E402


def mcq(gold=("C",)):
    return Item("x", [], list(gold))


# --- KoBALT -------------------------------------------------------------
def test_kobalt_official_sentence():
    assert kobalt.parse(mcq(), "풀이...\n\n정답은 C입니다.") == "C"
    assert kobalt.parse(mcq(), "정답은 **H**입니다.") == "H"
    assert kobalt.parse(mcq(), "정답은 [J]입니다") == "J"


def test_kobalt_last_statement_wins():
    assert kobalt.parse(mcq(), "처음엔 정답은 A입니다라고 생각했지만 다시 보면\n정답은 D입니다.") == "D"


def test_kobalt_no_fallback_to_prose_letters():
    for r in ["C2 채널과 관련된 C가 맞아 보입니다.", "보기 (D)는 틀렸고 B도 아닙니다.", "답: C", "정답은 K입니다."]:
        assert kobalt.parse(mcq(), r) is None, r


def test_kobalt_duplicate_option_item_accepts_both():
    it = Item("67c81c5d361c7932636b7c14", [], ["B", "E"])
    assert kobalt.score(it, "E")["outcome"] == "correct"
    assert kobalt.score(it, "A")["outcome"] == "wrong"
    assert kobalt.score(it, None)["outcome"] == "no_answer_unparsed"


def test_kobalt_official_prompt_is_read_from_protocol():
    md = (HERE / "data" / "kobalt_evaluation_protocol.md").read_text()
    msgs = kobalt.official_messages(md)
    assert msgs[0]["role"] == "system" and "<QUESTION>" in msgs[1]["content"]
    assert "정답은 [정답 보기]입니다." in msgs[1]["content"]


# --- KoSimpleQA ---------------------------------------------------------
def test_kosimpleqa_judge_parse_is_strict():
    assert kosimpleqa.parse_judge("A") == "correct"
    assert kosimpleqa.parse_judge(" B\n") == "incorrect"
    assert kosimpleqa.parse_judge("\"C\"") == "not_attempted"
    # simple-evals would default these to NOT_ATTEMPTED; here they are judge errors
    for r in ["", "The answer is A", "A or B", "CORRECT"]:
        assert kosimpleqa.parse_judge(r) is None, r


def test_kosimpleqa_metrics_keep_no_response_out_of_incorrect():
    m = kosimpleqa.metrics(["correct", "correct", "incorrect", "not_attempted", "no_answer_truncated"])
    assert (m["CO"], m["IN"], m["NA"], m["NR"]) == (0.4, 0.2, 0.2, 0.2)
    assert abs(m["CGA"] - 2 / 3) < 1e-9
    assert abs(m["F"] - 2 * 0.4 * (2 / 3) / (0.4 + 2 / 3)) < 1e-9


def test_kosimpleqa_grader_template_has_slots():
    it = Item("1", [{"role": "user", "content": "한반도에서 가장 높은 산은?"}], "백두산")
    msg = kosimpleqa.judge_messages(it, "백두산입니다.")[0]["content"]
    assert "한반도에서 가장 높은 산은?" in msg and "백두산입니다." in msg and "{target}" not in msg


# --- KLUE-NER -----------------------------------------------------------
def ner(sentence, gold):
    return Item("s", [], [list(g) for g in gold], {"sentence": sentence})


def test_ner_parses_offsets_and_types():
    it = ner("김철수는 서울에서 3시에 왔다.", [(0, 3, "PS"), (5, 7, "LC"), (10, 12, "TI")])
    r = "추론...\n결과: ⟦김철수|PS⟧는 ⟦서울|LC⟧에서 ⟦3시|TI⟧에 왔다."
    pred = klue_ner.parse(it, r)
    assert pred == [(0, 3, "PS"), (5, 7, "LC"), (10, 12, "TI")]
    assert klue_ner.score(it, pred) == {"outcome": "parsed", "tp": 3, "fp": 0, "fn": 0, "pred_spans": pred}


def test_ner_rejects_altered_sentence():
    it = ner("김철수는 서울에서 왔다.", [(0, 3, "PS")])
    assert klue_ner.parse(it, "결과: ⟦김철수|PS⟧는 서울에서 왔습니다.") is None  # text changed
    assert klue_ner.parse(it, "⟦김철수|PS⟧는 서울에서 왔다.") is None          # no 결과: line
    assert klue_ner.parse(it, "결과: ⟦김철수|XX⟧는 서울에서 왔다.") is None     # unknown type left markers


def test_ner_lenient_only_forgives_trailing_punctuation():
    it = ner("10년,20년이 흘러도 남을 것", [(0, 3, "DT"), (4, 7, "DT")])
    r = "결과: ⟦10년|DT⟧,⟦20년|DT⟧이 흘러도 남을 것."
    assert klue_ner.parse(it, r) is None                       # strict: the added "." is a change
    assert klue_ner.parse(it, r, lenient=True) == [(0, 3, "DT"), (4, 7, "DT")]
    assert klue_ner.parse(it, "결과: ⟦10년|DT⟧, ⟦20년|DT⟧이 흘러도 남을 것", lenient=True) is None  # inner edit


def test_ner_boundary_and_type_errors_count():
    it = ner("서울시청에 갔다.", [(0, 4, "OG")])
    pred = klue_ner.parse(it, "결과: ⟦서울|LC⟧시청에 갔다.")
    assert klue_ner.score(it, pred)[("tp")] == 0
    s = klue_ner.score(it, pred)
    assert (s["fp"], s["fn"]) == (1, 1)


def test_ner_no_entities_is_valid_and_angle_brackets_are_plain_text():
    it = ner("영화 <레이>는 좋았다.", [])
    assert klue_ner.parse(it, "결과: 영화 <레이>는 좋았다.") == []
    assert klue_ner.score(it, None) == {"outcome": "no_answer_unparsed", "tp": 0, "fp": 0, "fn": 0}


def test_ner_colon_inside_entity():
    it = ner("10:30에 만나자", [(0, 5, "TI")])
    assert klue_ner.parse(it, "결과: ⟦10:30|TI⟧에 만나자") == [(0, 5, "TI")]


# --- LBox casename ------------------------------------------------------
def lbox(gold):
    return Item("1", [], gold, {"labels": ["건물인도", "건물명도(인도)", "손해배상", "손해배상(기)", "사기"]})


def test_lbox_exact_label_only():
    it = lbox("건물명도(인도)")
    assert lbox_casename.parse(it, "판단...\n사건명: 건물명도(인도)") == "건물명도(인도)"
    assert lbox_casename.parse(it, "**사건명: \"손해배상(기)\"**") == "손해배상(기)"
    assert lbox_casename.parse(it, "사건명: 건물 명도") is None       # paraphrase
    assert lbox_casename.parse(it, "사건명: 사기죄") is None          # not in the list
    assert lbox_casename.parse(it, "정답은 사기입니다") is None        # no 사건명: line


def test_lbox_overlapping_labels_are_distinct():
    it = lbox("건물명도(인도)")
    assert lbox_casename.score(it, "건물인도")["outcome"] == "wrong"


def test_lbox_leak_key():
    assert lbox_casename.leak_key("도로교통법위반(음주운전)") == "도로교통법"
    assert lbox_casename.leak_key("공무집행방해, 상해") == "공무집행방해"


# --- stats --------------------------------------------------------------
def test_stats():
    assert mcnemar_exact(0, 0) == 1.0
    assert abs(mcnemar_exact(0, 13) - 0.000244140625) < 1e-12
    lo, hi = wilson(36, 39)
    assert abs(lo - 0.797) < 1e-3 and abs(hi - 0.973) < 1e-3
