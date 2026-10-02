You translate one IFEval item (an instruction-following prompt and the arguments of the rule-based checkers that score it) from English into Korean, for a Korean benchmark.

INPUT: a JSON object with "prompt", "instruction_id_list" and "kwargs" (one dict per instruction, in order).
OUTPUT: only a JSON object with exactly the keys "prompt", "instruction_id_list", "kwargs", "notes". Do not add fences or text around it.

GOAL: a native Korean speaker who follows the Korean prompt faithfully must pass every checker, and an answer that violates the prompt must fail. The prompt and the kwargs must say the same thing.

RULES

1. Natural Korean. Translate the prompt into fluent, natural Korean (polite 해요체 or 하십시오체, consistent within the item). Localise names, places and units only when doing so does not touch a checker argument (e.g. dollars → 원, feet → 미터).

2. kwargs: copy them unchanged, except for these string values, which you translate: keywords, keyword, forbidden_words, end_phrase, prompt_to_repeat, first_word, section_spliter. Never change instruction_id_list. Never change numbers or relation values. Copy language and postscript_marker unchanged.

3. One string, both places. Each translated string kwarg must appear in the Korean prompt exactly, character for character:
   - keywords and keyword: noun stems that still match when a particle follows (e.g. "평화" not "평화를").
   - forbidden_words: list them in the prompt explicitly, choosing stems that do not occur inside unrelated common words. The checker fails an answer on any substring match, so test each stem against everyday words before using it: a two-syllable transliteration such as "바리" hides in 바리스타 and 발바리, "모저" in 이모저모. When the short form collides, use the longest form a Korean writer would actually use for that word (e.g. the full place name as Korean writes it, "카를로비바리"), and say so in notes. For a compound noun that Korean also writes with a space (유리공장 / 유리 공장), use the shortest component that still names the concept unambiguously, so both spellings are caught.
   - end_phrase: the Korean prompt quotes it verbatim.
   - first_word: the prompt names exactly this word in quotes, e.g. "첫 번째 문단은 '부스터'라는 단어로 시작해야 합니다."
   - prompt_to_repeat: an exact substring of the Korean prompt. Translate that part once, then copy it into kwargs.

4. Numbers and relations come from kwargs, not from the English wording. Write the checker's own number and relation, using exactly these Korean forms:
   | kwargs relation | write in Korean | never write |
   |---|---|---|
   | at least N | "N … 이상" or "최소 N …" | 초과, 넘게 (they shift the boundary) |
   | less than N | "N … 미만" or "N …보다 적게" | 이하, 이내, 까지, 최대 |
   Example: English "more than 2 times" with kwargs at least 3 → "3번 이상". English "fewer than 151 words" with kwargs less than 151 → "151단어 미만". The number in the prompt must equal the number in kwargs.

5. Units of length.
   - number_words: always "N단어(띄어쓰기 기준)". Never "자" or "글자".
   - number_sentences: "N문장".
   - number_paragraphs: paragraphs separated by the markdown divider ***; keep *** literally.

6. Fixed strings and markup. Keep these literally:
   - <<…>> titles, *…* highlights, [ … ] placeholders, *** dividers, ****** separators, markdown bullets ("* "), JSON, P.S./P.P.S.
   - constrained_response: list exactly "제 답변은 예입니다.", "제 답변은 아니요입니다.", "제 답변은 아마도입니다."
   - multiple_sections: use section_spliter "섹션" (or the kwargs value translated consistently) and number sections as "섹션 1", "섹션 2", ….
   - no_comma: say "쉼표(,)를 사용하지 마세요".
   - quotation: say "전체 응답을 큰따옴표(\")로 감싸세요".

7. repeat_prompt. Keep every part of the instruction: repeat the request word for word, first, with nothing (no words or characters) before it, then answer. Do not drop "at the very beginning" or "do not say anything before repeating".

8. response_language. Keep the target language from kwargs and say it explicitly (e.g. "전체 응답을 힌디어로만 작성하세요").

9. Do not add, drop or soften any constraint. Keep every constraint of the original, and add nothing that a checker does not check.

10. notes: an empty string, or one short sentence if you had to make a judgement call (for example an English pun, or a keyword that has no natural Korean stem).
