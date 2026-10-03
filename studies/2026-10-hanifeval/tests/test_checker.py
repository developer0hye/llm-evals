"""Regression tests for the HanIFEval checker (checker/).

Each test pins one scoring behaviour: a fix made in v1.1, a boundary (N-1 / N / N+1), or a policy that
is kept on purpose (substring matching, >= for sections and highlights, contains-one for constrained
responses). Several cases come from the two external reviews of 2026-10-03 (NOTES.md section 10).

    cd studies/2026-10-hanifeval && python -m pytest tests -q
"""

import sys
import unicodedata
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
from checker import instructions_util as U  # noqa: E402
from checker import utils as CU  # noqa: E402
from checker.utils import InputExample  # noqa: E402


def follows(iid, kwargs, response, prompt="p"):
    inp = InputExample(key=0, instruction_id_list=[iid], prompt=prompt, kwargs=[kwargs])
    return CU.test_instruction_following_strict(inp, response).follow_all_instructions


# --- sentence splitting (v1.1 fix; review F02, F12) ---------------------------------------------

@pytest.mark.parametrize("text,n", [
    ("사랑의 비율은 따지지 마. 선율이 창문을 두드린다. 오늘 밤도 춤을 춰.", 3),   # imperative "마." is not a list marker
    ("별빛 아래로 가. 선율이 창문을 두드린다. 오늘 밤도 춤을 춰.", 3),             # imperative "가."
    ("1. 첫날 이동하세요.\n2. 점심을 먹으세요.\n3. 야경을 보세요.\n4. 섬으로 가세요.\n5. 공항으로 가세요.", 5),
    ("가. 첫째 항목입니다.\n나. 둘째 항목입니다.", 2),                             # line-start Korean markers
    ("1) 첫째입니다.\n2) 둘째입니다.", 2),
    ("가격은 3.5달러입니다. 할인은 없습니다.", 2),                                # decimals
])
def test_count_sentences(text, n):
    assert U.count_sentences(text) == n


def test_xml_closing_tags_count_as_a_sentence_known_artifact():
    # Kept as is; item 2859 carries known_issues "source_checker_artifact".
    xml = "<요약>\n  <문장>첫째 문장이다.</문장>\n  <문장>둘째 문장이다.</문장>\n  <문장>셋째 문장이다.</문장>\n</요약>"
    assert U.count_sentences(xml) == 4


# --- language (v1.1 fix; review F13) ------------------------------------------------------------

def test_undetectable_text_fails_language_check():
    assert not follows("language:response_language", {"language": "hi"}, "12345")


def test_hindi_passes_language_check():
    assert follows("language:response_language", {"language": "hi"},
                   "जलवायु परिवर्तन हमारे समय की सबसे बड़ी चुनौती है और हमें मिलकर काम करना होगा।")


# --- keywords: escaped substring, case-insensitive, NFC ----------------------------------------

def test_keyword_followed_by_particle_counts():
    assert follows("keywords:existence", {"keywords": ["평화"]}, "모두가 평화를 원한다.")


def test_forbidden_word_is_a_substring_rule():
    # Policy: substring. '청사진' contains '사진'; item 1342 states this in its prompt from v1.1.
    assert not follows("keywords:frequency", {"keyword": "사진", "frequency": 1, "relation": "less than"},
                       "사업의 청사진을 먼저 그리세요.")


def test_nfd_response_and_kwargs_are_normalised():
    nfd = unicodedata.normalize("NFD", "평화를 원한다")
    assert follows("keywords:existence", {"keywords": [unicodedata.normalize("NFD", "평화")]}, nfd)
    assert follows("keywords:existence", {"keywords": ["평화"]}, nfd)


@pytest.mark.parametrize("count,relation,ok", [(1, "at least", False), (2, "at least", True), (3, "at least", True),
                                              (1, "less than", True), (2, "less than", False)])
def test_keyword_frequency_boundaries(count, relation, ok):
    text = " ".join(["그는 대답했습니다."] * count)
    assert follows("keywords:frequency", {"keyword": "대답했", "frequency": 2, "relation": relation}, text) == ok


# --- counts: N-1 / N / N+1 ----------------------------------------------------------------------

@pytest.mark.parametrize("n,ok", [(3, False), (4, True), (5, True)])
def test_sections_are_scored_at_least(n, ok):
    text = "\n".join(f"섹션 {i}\n내용 {i}" for i in range(1, n + 1))
    assert follows("detectable_format:multiple_sections", {"section_spliter": "섹션", "num_sections": 4}, text) == ok


@pytest.mark.parametrize("n,ok", [(1, False), (2, True), (3, True)])
def test_highlights_are_scored_at_least(n, ok):
    text = " ".join(f"*강조 {i}*" for i in range(n))
    assert follows("detectable_format:number_highlighted_sections", {"num_highlights": 2}, text) == ok


@pytest.mark.parametrize("n,ok", [(2, False), (3, True), (4, False)])
def test_bullets_are_scored_exactly(n, ok):
    text = "\n".join(f"* 항목 {i}" for i in range(n))
    assert follows("detectable_format:number_bullet_lists", {"num_bullets": 3}, text) == ok


@pytest.mark.parametrize("n,ok", [(2, False), (3, True), (4, False)])
def test_paragraphs_are_scored_exactly(n, ok):
    text = "\n***\n".join(f"문단 {i}입니다." for i in range(n))
    assert follows("length_constraints:number_paragraphs", {"num_paragraphs": 3}, text) == ok


@pytest.mark.parametrize("words,relation,ok", [(29, "less than", True), (30, "less than", False),
                                               (29, "at least", False), (30, "at least", True), (31, "at least", True)])
def test_word_count_boundaries(words, relation, ok):
    assert follows("length_constraints:number_words", {"num_words": 30, "relation": relation},
                   " ".join(["단어"] * words)) == ok


# --- policies kept on purpose -------------------------------------------------------------------

def test_constrained_response_is_contains_one_as_in_google_ifeval():
    assert follows("detectable_format:constrained_response", {}, "제 답변은 예입니다. 제 답변은 아니요입니다.")


def test_first_word_is_a_prefix_match():
    text = "기업은 오늘도 분주합니다.\n\n둘째 문단입니다."
    assert follows("length_constraints:nth_paragraph_first_word",
                   {"num_paragraphs": 2, "nth_paragraph": 1, "first_word": "기업"}, text)


# --- release-level: the reviewers' honest answers pass everything except the tagged items --------

def test_release_satisfiability_matches_known_issues():
    import json
    rel = HERE / "release" / "hanifeval_v1.1.jsonl"
    resp_path = HERE / "work" / "review" / "responses_final_v1.1.jsonl"
    if not rel.exists() or not resp_path.exists():
        pytest.skip("release v1.1 not built")
    items = {r["key"]: r for r in map(json.loads, rel.open())}
    resp = {r["key"]: r["response"] for r in map(json.loads, resp_path.open())}
    failing = set()
    for k, it in items.items():
        inp = InputExample(key=k, instruction_id_list=it["instruction_id_list"], prompt=it["prompt"], kwargs=it["kwargs"])
        if not CU.test_instruction_following_strict(inp, resp[k]).follow_all_instructions:
            failing.add(k)
    assert failing == {k for k, it in items.items() if "source_unsatisfiable_strict" in it["known_issues"]}
