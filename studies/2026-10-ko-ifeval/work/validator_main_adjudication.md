# Validator adjudication, main run (guideline v1.1, 429 items)

`validate.py --translations work/translations.jsonl` flagged 9/429 items (2.1%).
All 9 were checked by hand against the English source. None is a translation defect.

| Key | Flag | Ruling |
|---|---|---|
| 143 | number_missing num_paragraphs=2 | Inherited: the English prompt also never states "2"; two parts follow from the single `***` divider. |
| 1137 | latin_kwarg 'nourriture' | Correct: the answer is in French, so the forbidden word stays French. |
| 1675 | latin_kwarg 'heute' | Correct: German forbidden word in a German answer. |
| 2534 | latin_kwarg 'schlau' | Correct: same. |
| 1348 | latin_kwarg 'Brilliant', 'Le', 'Hou' | Accepted: the person's name is kept in Latin script; the translator's note says Korean syllables (르, 후) would collide with ordinary words. |
| 1658 | latin_kwarg 'Python', 'Java' | Correct: Korean writes these names in Latin script. |
| 3324 | latin_kwarg section_spliter 'Day' | Accepted: "Day 1", "Day 2" is the usual Korean itinerary format; prompt and kwargs agree. |
| 1379 | number_missing frequency=2 | Validator false positive: relation `less than 2` is phrased "단 한 번만" (as in English "only once"). |
| 2616 | boundary_wording '1개 이상' | Validator false positive: "1개 이상" belongs to num_highlights=1, not to frequency=2, which reads "2번 이상". |
