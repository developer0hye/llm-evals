# HanIFEval v1: native-speaker review sheet (40 items)

Sample: `random.Random(20261001).sample(keys, 40)` over the 429 released keys.

For each item, answer:
1. Natural: is the Korean prompt natural Korean? (yes / awkward / no)
2. Faithful: does it ask for the same thing as the English, constraint by constraint? (yes / no + what differs)
3. Scorable: would an answer that follows the Korean prompt pass the kwargs as written? (yes / no + why)

## 168

**instructions:** `detectable_format:number_highlighted_sections`

**English**

```
Write a funny and sarcastic template for rating the quality of a marriage between two people who are both moms. This is for the couple themselves. Please highlight at least 3 sections with markdown,  i.e *highlighted section*.
```

**Korean**

```
두 명의 엄마로 이루어진 부부의 결혼 생활을 평가하는 재미있고 비꼬는 듯한 템플릿을 작성해 주세요. 이 템플릿은 부부 당사자들이 직접 사용할 용도입니다. 마크다운을 사용하여 최소 3개의 섹션을 강조 표시해 주세요(예: *강조된 섹션*).
```

**kwargs:** `[{"num_highlights": 3}]`

- Natural: 
- Faithful: 
- Scorable: 

## 240

**instructions:** `language:response_language`

**English**

```
What is a lattice? Rewrite the answer to be understandable to a young audience and make sure it's entirely in Russian, no other language is allowed.
```

**Korean**

```
격자란 무엇인가요? 어린 독자들이 이해할 수 있도록 답변을 재작성해 주시고, 전체 응답은 반드시 러시아어로만 작성하세요. 다른 언어는 허용되지 않습니다.
```

**kwargs:** `[{"language": "ru"}]`

- Natural: 
- Faithful: 
- Scorable: 

## 1000

**instructions:** `punctuation:no_comma, detectable_format:number_highlighted_sections, length_constraints:number_words`

**English**

```
Write a 300+ word summary of the wikipedia page "https://en.wikipedia.org/wiki/Raymond_III,_Count_of_Tripoli". Do not use any commas and highlight at least 3 sections that has titles in markdown format, for example *highlighted section part 1*, *highlighted section part 2*, *highlighted section part 3*.
```

**Korean**

```
위키백과 페이지 "https://en.wikipedia.org/wiki/Raymond_III,_Count_of_Tripoli"의 요약을 300단어(띄어쓰기 기준) 이상으로 작성하세요. 쉼표(,)를 사용하지 마세요. 그리고 마크다운 형식으로 제목이 있는 섹션을 3개 이상 강조 표시하세요. 예를 들어 *강조 표시된 섹션 파트 1*, *강조 표시된 섹션 파트 2*, *강조 표시된 섹션 파트 3*처럼 작성하면 됩니다.
```

**kwargs:** `[{}, {"num_highlights": 3}, {"relation": "at least", "num_words": 300}]`

- Natural: 
- Faithful: 
- Scorable: 

## 1203

**instructions:** `keywords:frequency, keywords:frequency`

**English**

```
What happened when the Tang dynasty of China was in power? Make sure to use the word war at least 8 times, and the word peace at least 10 times.
```

**Korean**

```
중국의 당나라가 집권했을 때 어떤 일들이 있었나요? '전쟁'이라는 단어를 8번 이상, '평화'라는 단어를 10번 이상 반드시 포함해서 작성하세요.
```

**kwargs:** `[{"relation": "at least", "keyword": "전쟁", "frequency": 8}, {"relation": "at least", "keyword": "평화", "frequency": 10}]`

- Natural: 
- Faithful: 
- Scorable: 

## 1237

**instructions:** `detectable_format:number_highlighted_sections, keywords:existence`

**English**

```
Write a funny post for teenagers about a restaurant called "Buena Onda" which serves Argentinian food. Highlight at least three sections of your response in markdown such as *highlighted section*. Mention "Argentinian" in the post.
```

**Korean**

```
아르헨티나 음식을 제공하는 '부에나 온다(Buena Onda)'라는 식당에 대해 10대들을 위한 재미있는 게시물을 작성해 주세요. 응답에서 *강조된 부분*과 같이 마크다운을 사용하여 3개 이상의 부분을 강조 표시하세요. 게시물에 '아르헨티나'를 언급하세요.
```

**kwargs:** `[{"num_highlights": 3}, {"keywords": ["아르헨티나"]}]`

- Natural: 
- Faithful: 
- Scorable: 

## 1262

**instructions:** `detectable_format:title, length_constraints:number_sentences`

**English**

```
Can you elaborate on the following text: "Increased axle weight increased the damage to the road"? Your response must contain a title wrapped in double angular brackets, i.e. <<title>>. Use less than 5 sentences.
```

**Korean**

```
다음 텍스트에 대해 자세히 설명해 주시겠어요? "축하중이 증가하면 도로의 손상도 증가합니다." 응답에는 이중 꺾쇠괄호로 감싼 제목이 포함되어야 합니다(예: <<제목>>). 5문장 미만으로 작성하세요.
```

**kwargs:** `[{}, {"relation": "less than", "num_sentences": 5}]`

- Natural: 
- Faithful: 
- Scorable: 

## 1393

**instructions:** `keywords:frequency`

**English**

```
List the pros and cons of using two different names for the same thing. Make sure the word synonyms appears at least 3 time.
```

**Korean**

```
같은 대상을 두 가지 다른 이름으로 부르는 것의 장단점을 나열해 주세요. '동의어'라는 단어가 3번 이상 포함되도록 작성하세요.
```

**kwargs:** `[{"relation": "at least", "keyword": "동의어", "frequency": 3}]`

- Natural: 
- Faithful: 
- Scorable: 

## 1418

**instructions:** `punctuation:no_comma, length_constraints:number_sentences, length_constraints:number_sentences`

**English**

```
Write a 30-line poem with short sentences without any comma. Each line should contain exactly one sentence. Make sure that you put the right punctuation at the end of each line. Your entire response should contain the poem only.
```

**Korean**

```
짧은 문장들로 이루어진 30줄짜리 시를 작성하되, 쉼표(,)를 사용하지 마세요. 각 줄에는 정확히 한 문장만 포함되어야 하며, 전체 문장 수는 30문장 이상, 31문장 미만이어야 합니다. 각 줄의 끝에는 알맞은 문장 부호를 넣으세요. 전체 응답에는 시만 포함되어야 합니다.
```

**kwargs:** `[{}, {"relation": "less than", "num_sentences": 31}, {"relation": "at least", "num_sentences": 30}]`

- Natural: 
- Faithful: 
- Scorable: 

## 1466

**instructions:** `startend:quotation, keywords:forbidden_words`

**English**

```
Write a song that critiques the song "We Are Never Ever Getting Back Together" by Taylor Swift. Wrap your entire response with double quotation marks. Do not mention the word Taylor, Swift, or Together.
```

**Korean**

```
테일러 스위프트의 노래 'We Are Never Ever Getting Back Together'를 비판하는 노래를 작성하세요. 전체 응답을 큰따옴표(")로 감싸세요. '테일러', '스위프트', '투게더'라는 단어는 언급하지 마세요.
```

**kwargs:** `[{}, {"forbidden_words": ["테일러", "스위프트", "투게더"]}]`

- Natural: 
- Faithful: 
- Scorable: 

## 1508

**instructions:** `keywords:existence, punctuation:no_comma`

**English**

```
Write a haiku about a lion that includes the keywords "forests" and "riddle". Refrain from using commas in your haiku.
```

**Korean**

```
사자에 대한 하이쿠를 작성하세요. 키워드 '숲'과 '수수께끼'를 포함해야 합니다. 하이쿠에 쉼표(,)를 사용하지 마세요.
```

**kwargs:** `[{"keywords": ["숲", "수수께끼"]}, {}]`

- Natural: 
- Faithful: 
- Scorable: 

## 1546

**instructions:** `combination:repeat_prompt, punctuation:no_comma`

**English**

```
In this task, repeat the exact request below first, then give your response. Do not say any word before repeating the exact request.

Write an acoustic song about the Korean peninsula without using any commas.
```

**Korean**

```
이 작업에서는 먼저 아래의 요청을 정확히 반복한 다음, 답변을 제공하세요. 정확한 요청을 반복하기 전에 어떤 단어도 말하지 마세요.

한반도에 대한 어쿠스틱 노래를 작성하세요. 쉼표를 사용하지 마세요.
```

**kwargs:** `[{"prompt_to_repeat": "한반도에 대한 어쿠스틱 노래를 작성하세요. 쉼표를 사용하지 마세요."}, {}]`

- Natural: 
- Faithful: 
- Scorable: 

## 1619

**instructions:** `detectable_content:postscript, detectable_content:number_placeholders`

**English**

```
Write a rap about a new smartphone. At the end of your response add a postscript starting with P.P.S The response must contain at least 6 placeholders represented by square brackets.
```

**Korean**

```
새로운 스마트폰에 대한 랩을 작성해 주세요. 응답의 마지막에는 P.P.S로 시작하는 추신을 추가하세요. 응답에는 대괄호([ ])로 표시된 자리 표시자가 6개 이상 포함되어야 합니다.
```

**kwargs:** `[{"postscript_marker": "P.P.S"}, {"num_placeholders": 6}]`

- Natural: 
- Faithful: 
- Scorable: 

## 1629

**instructions:** `keywords:forbidden_words`

**English**

```
Make the sentence “The bus arrived at the station” sound more interesting. Avoid using the word “station”.
```

**Korean**

```
“버스가 정류장에 도착했다”라는 문장을 더 흥미롭게 만들어 보세요. 단, “정류장”이라는 단어는 피하세요.
```

**kwargs:** `[{"forbidden_words": ["정류장"]}]`

- Natural: 
- Faithful: 
- Scorable: 

## 1658

**instructions:** `startend:quotation, keywords:existence`

**English**

```
Create a resume for a 20-year-old college student with no work experience. Include the keywords "Python" and "Java" and wrap the response with double quotation marks.
```

**Korean**

```
직장 경력이 없는 20세 대학생의 이력서를 작성해 주세요. 'Python'과 'Java'라는 키워드를 포함하고, 전체 응답을 큰따옴표(")로 감싸세요.
```

**kwargs:** `[{}, {"keywords": ["Python", "Java"]}]`

- Natural: 
- Faithful: 
- Scorable: 

## 1686

**instructions:** `combination:repeat_prompt`

**English**

```
For the following request, please repeat the request itself exactly as it is, then give your reply. Do not change the request whatsoever, and do not say anything before repeating the request.

Hello. I need to give a lecture to my students about the movie La La Land. Please help me write a lecture outline that is engaging and informative.
```

**Korean**

```
다음 요청에 대해, 요청 자체를 있는 그대로 정확히 반복한 다음 답변을 제공해 주세요. 요청을 조금도 변경하지 말고, 요청을 반복하기 전에 아무 말도 하지 마세요.

안녕하세요. 학생들에게 영화 라라랜드에 대한 강의를 해야 합니다. 흥미롭고 유익한 강의 개요를 작성하도록 도와주세요.
```

**kwargs:** `[{"prompt_to_repeat": "안녕하세요. 학생들에게 영화 라라랜드에 대한 강의를 해야 합니다. 흥미롭고 유익한 강의 개요를 작성하도록 도와주세요."}]`

- Natural: 
- Faithful: 
- Scorable: 

## 1739

**instructions:** `punctuation:no_comma, language:response_language`

**English**

```
Rewrite the following sentence in only Vietnamese, no other language is allowed, and refrain from using commas: "We may be able to improve our model for the next year. We will be able to compare our data with the data from the previous year, and see how our model performed. We can also compare our model against a model that was trained on the previous year's data and see how our model performs." No other language except Vietnamese is allowed to be used in your response.
```

**Korean**

```
다음 문장을 베트남어로만 다시 작성하세요. 다른 언어는 허용되지 않으며, 쉼표(,)를 사용하지 마세요: "우리는 내년에 모델을 개선할 수 있을지도 모릅니다. 우리의 데이터를 작년 데이터와 비교하여 모델이 어떻게 수행되었는지 확인할 수 있을 것입니다. 또한 작년 데이터로 훈련된 모델과 우리 모델을 비교하여 우리 모델의 성능을 확인할 수도 있습니다." 응답에는 베트남어 외에 다른 언어를 사용할 수 없습니다.
```

**kwargs:** `[{}, {"language": "vi"}]`

- Natural: 
- Faithful: 
- Scorable: 

## 1928

**instructions:** `detectable_format:title, punctuation:no_comma, keywords:frequency`

**English**

```
Elaborate on the following sentence into a formal story: "My dog is brown, and my cat is black." Your answer must contain a title, wrapped in double angular brackets, i.e. <<title>>, and should not contain any commas. In your response, the word flesh should appear less than 3 times.
```

**Korean**

```
다음 문장을 격식 있는 이야기로 자세히 써주세요: "내 개는 갈색이고 내 고양이는 검은색이다." 답변에는 이중 꺾쇠괄호로 감싼 제목(예: <<제목>>)이 포함되어야 하며, 쉼표(,)를 사용하지 마세요. 응답에서 '살점'이라는 단어는 3번 미만으로 나타나야 합니다.
```

**kwargs:** `[{}, {}, {"relation": "less than", "keyword": "살점", "frequency": 3}]`

- Natural: 
- Faithful: 
- Scorable: 

## 1943

**instructions:** `length_constraints:number_paragraphs, startend:end_checker`

**English**

```
My brother is trying to install a new toilet in his bathroom. Could you give me details of how-to? You don't need to show all details -- just the first 5 steps for now. Separated them with "***", such as:
Step 1: ......
***
Step 2: ......
***
...

End your whole response with the phrase "Let me know how it works. I can give you next steps when you finish all steps above."
```

**Korean**

```
제 동생이 화장실에 새 변기를 설치하려고 합니다. 설치 방법에 대한 자세한 내용을 알려주시겠어요? 모든 세부 사항을 다 보여줄 필요는 없고, 일단 처음 5단계만 알려주세요. 각 단계는 "***"로 구분해 주세요. 예시는 다음과 같습니다:
1단계: ......
***
2단계: ......
***
...

전체 응답은 "어떻게 진행되었는지 알려주세요. 위의 모든 단계를 마치면 다음 단계를 알려드릴 수 있습니다."라는 문구로 끝내주세요.
```

**kwargs:** `[{"num_paragraphs": 5}, {"end_phrase": "어떻게 진행되었는지 알려주세요. 위의 모든 단계를 마치면 다음 단계를 알려드릴 수 있습니다."}]`

- Natural: 
- Faithful: 
- Scorable: 

## 2041

**instructions:** `length_constraints:number_sentences, keywords:forbidden_words`

**English**

```
Write a very long email to my "friend" Jake, asking how is everything going. Say that I am rich now, without saying I am rich. Your entire response should contain at least 40 sentences, and not contain the word "rich" and "money".
```

**Korean**

```
내 '친구' 제이크에게 요즘 어떻게 지내는지 안부를 묻는 아주 긴 이메일을 작성하세요. 내가 이제 부유해졌다는 사실을 알리되, '부유'라는 단어는 직접 쓰지 마세요. 전체 응답은 40문장 이상이어야 하며, '부유'와 '금전'이라는 단어를 포함해서는 안 됩니다.
```

**kwargs:** `[{"relation": "at least", "num_sentences": 40}, {"forbidden_words": ["부유", "금전"]}]`

- Natural: 
- Faithful: 
- Scorable: 

## 2139

**instructions:** `length_constraints:number_sentences, keywords:existence`

**English**

```
Compose a song with at least three sentences that can be sung by a professional singer in the style of a 1930s jazz standard. Include the keywords "rate" and "rte".
```

**Korean**

```
1930년대 재즈 스탠더드 스타일로 전문 가수가 부를 수 있는 노래를 3문장 이상으로 작곡하세요. 키워드 '비율'과 '알티이'를 포함하세요.
```

**kwargs:** `[{"relation": "at least", "num_sentences": 3}, {"keywords": ["비율", "알티이"]}]`

- Natural: 
- Faithful: 
- Scorable: 

## 2225

**instructions:** `language:response_language`

**English**

```
what is the difference between a levee and an embankment? Please respond to me only in Korean.
```

**Korean**

```
제방과 둑의 차이점은 무엇인가요? 오직 한국어로만 대답해 주세요.
```

**kwargs:** `[{"language": "ko"}]`

- Natural: 
- Faithful: 
- Scorable: 

## 2246

**instructions:** `length_constraints:number_words, keywords:frequency, detectable_content:number_placeholders`

**English**

```
I want to travel to the Subic Bay Freeport Zone, which subdistrict should I stay in? Give me an angry recommendation. Answer with at least 400 words. In your response, the word climatic should appear at least 2 times. The response must contain at least 3 placeholders represented by square brackets, such as [address].
```

**Korean**

```
수빅만 경제자유구역(Subic Bay Freeport Zone)으로 여행을 가고 싶은데, 어느 구역에 머무는 것이 좋을까요? 화난 어조로 추천해 주세요. 답변은 최소 400단어(띄어쓰기 기준) 이상으로 작성하세요. 답변에 '기후'라는 단어가 최소 2번 이상 포함되어야 합니다. 답변에는 [주소]와 같이 대괄호로 표시된 자리 표시자(placeholder)가 최소 3개 이상 포함되어야 합니다.
```

**kwargs:** `[{"relation": "at least", "num_words": 400}, {"relation": "at least", "keyword": "기후", "frequency": 2}, {"num_placeholders": 3}]`

- Natural: 
- Faithful: 
- Scorable: 

## 2439

**instructions:** `punctuation:no_comma, length_constraints:nth_paragraph_first_word, detectable_content:number_placeholders`

**English**

```
Rewrite the following sentence to exactly 3 paragraphs, separated by two new lines and without using any commas: "Offences are not the only things that are grasped by the police.". Paragraph 1 must start with word punched. The response must contain at least 2 placeholders represented by square brackets, such as [address].
```

**Korean**

```
다음 문장을 정확히 3개의 문단으로 다시 작성하되, 각 문단은 두 번의 줄바꿈으로 구분하고 쉼표(,)를 사용하지 마세요: "범죄만이 경찰이 파악하는 유일한 것은 아닙니다." 첫 번째 문단은 '펀치'라는 단어로 시작해야 합니다. 응답에는 [주소]와 같이 대괄호로 표시된 자리 표시자가 2개 이상 포함되어야 합니다.
```

**kwargs:** `[{}, {"first_word": "펀치", "num_paragraphs": 3, "nth_paragraph": 1}, {"num_placeholders": 2}]`

- Natural: 
- Faithful: 
- Scorable: 

## 2677

**instructions:** `startend:end_checker`

**English**

```
Write a limerick about a guy named Dave that is funny to moms. The limerick should end with the phrase "Yes Mom, I am Dave." Do not say anything after the limerick.
```

**Korean**

```
엄마들이 재미있어할 만한, 데이브라는 남자에 대한 리머릭(5행시)을 작성해 주세요. 이 리머릭은 "네 엄마, 제가 데이브예요."라는 문구로 끝나야 합니다. 리머릭 이후에는 아무 말도 하지 마세요.
```

**kwargs:** `[{"end_phrase": "네 엄마, 제가 데이브예요."}]`

- Natural: 
- Faithful: 
- Scorable: 

## 2752

**instructions:** `detectable_format:number_highlighted_sections`

**English**

```
The opposite of youth is not age, but ...? Highlight at least 2 sections in your answer with markdown, i.e. *highlighted section*.
```

**Korean**

```
젊음의 반대는 나이가 아니라 ...? 답변에서 마크다운을 사용하여 최소 2개의 부분을 강조 표시하세요(예: *강조된 부분*).
```

**kwargs:** `[{"num_highlights": 2}]`

- Natural: 
- Faithful: 
- Scorable: 

## 2811

**instructions:** `keywords:forbidden_words`

**English**

```
Can you write a rap that doesn't include the keywords "Yo", "check", and "peace"?
```

**Korean**

```
키워드 '요우', '체크', '평화'를 포함하지 않는 랩을 작성해 주실 수 있나요?
```

**kwargs:** `[{"forbidden_words": ["요우", "평화", "체크"]}]`

- Natural: 
- Faithful: 
- Scorable: 

## 2859

**instructions:** `length_constraints:number_sentences`

**English**

```
Kindly summarize the text below in XML format. Make sure the summary contains less than 4 sentences.

Quantum entanglement is the phenomenon that occurs when a group of particles are generated, interact, or share spatial proximity in such a way that the quantum state of each particle of the group cannot be described independently of the state of the others, including when the particles are separated by a large distance. The topic of quantum entanglement is at the heart of the disparity between classical and quantum physics: entanglement is a primary feature of quantum mechanics not present in classical mechanics.

Measurements of physical properties such as position, momentum, spin, and polarization performed on entangled particles can, in some cases, be found to be perfectly correlated. For example, if a pair of entangled particles is generated such that their total spin is known to be zero, and one particle is found to have clockwise spin on a first axis, then the spin of the other particle, measured on the same axis, is found to be anticlockwise. However, this behavior gives rise to seemingly paradoxical effects: any measurement of a particle's properties results in an apparent and irreversible wave function collapse of that particle and changes the original quantum state. With entangled particles, such measurements affect the entangled system as a whole.

Such phenomena were the subject of a 1935 paper by Albert Einstein, Boris Podolsky, and Nathan Rosen, and several papers by Erwin Schrödinger shortly thereafter, describing what came to be known as the EPR paradox. Einstein and others considered such behavior impossible, as it violated the local realism view of causality (Einstein referring to it as "spooky action at a distance") and argued that the accepted formulation of quantum mechanics must therefore be incomplete.


```

**Korean**

```
아래 텍스트를 XML 형식으로 요약해 주세요. 요약은 4문장 미만이어야 합니다.

양자 얽힘은 입자 그룹이 생성되거나, 상호 작용하거나, 공간적 근접성을 공유할 때, 입자들이 먼 거리로 떨어져 있는 경우를 포함하여 그룹 내 각 입자의 양자 상태를 다른 입자의 상태와 독립적으로 설명할 수 없는 방식으로 발생하는 현상입니다. 양자 얽힘이라는 주제는 고전 물리학과 양자 물리학 간의 차이의 핵심입니다. 얽힘은 고전 역학에는 없는 양자 역학의 주요 특징입니다.

얽힌 입자에 대해 수행된 위치, 운동량, 스핀, 편광과 같은 물리적 특성의 측정값은 경우에 따라 완벽하게 상관관계가 있는 것으로 나타날 수 있습니다. 예를 들어, 총 스핀이 0으로 알려진 얽힌 입자 쌍이 생성되고 한 입자가 첫 번째 축에서 시계 방향 스핀을 갖는 것으로 밝혀지면, 동일한 축에서 측정된 다른 입자의 스핀은 반시계 방향인 것으로 나타납니다. 그러나 이러한 동작은 역설적으로 보이는 효과를 낳습니다. 입자의 특성을 측정하면 해당 입자의 명백하고 되돌릴 수 없는 파동 함수 붕괴가 발생하고 원래의 양자 상태가 변경됩니다. 얽힌 입자의 경우 이러한 측정은 얽힌 시스템 전체에 영향을 미칩니다.

이러한 현상은 알베르트 아인슈타인, 보리스 포돌스키, 네이선 로젠의 1935년 논문과 그 직후 에르빈 슈뢰딩거의 여러 논문의 주제였으며, EPR 역설로 알려지게 된 것을 설명했습니다. 아인슈타인과 다른 사람들은 이러한 동작이 인과관계에 대한 국소적 실재론의 관점을 위반하기 때문에 불가능하다고 여겼으며(아인슈타인은 이를 "원거리에서의 유령 같은 행동"이라고 불렀습니다), 따라서 인정받는 양자 역학의 공식화가 불완전함에 틀림없다고 주장했습니다.


```

**kwargs:** `[{"relation": "less than", "num_sentences": 4}]`

- Natural: 
- Faithful: 
- Scorable: 

## 2929

**instructions:** `detectable_content:postscript`

**English**

```
Write a text ad for an adult website that is not pornographic, and at the end of your response, add a postscript starting with P.S.
```

**Korean**

```
음란물이 아닌 성인용 웹사이트를 위한 텍스트 광고를 작성해 주세요. 그리고 응답의 마지막에는 P.S.로 시작하는 추신을 추가하세요.
```

**kwargs:** `[{"postscript_marker": "P.S."}]`

- Natural: 
- Faithful: 
- Scorable: 

## 3084

**instructions:** `punctuation:no_comma, startend:end_checker`

**English**

```
Write a weird and short haiku about the state of Gujarat in India. Don't use any commas in your entire response. End your response with the EXACT phrase of "in India."
```

**Korean**

```
인도의 구자라트주에 대한 기묘하고 짧은 하이쿠를 작성하세요. 전체 응답에 쉼표(,)를 사용하지 마세요. 응답은 정확히 "인도에서."라는 문구로 끝나야 합니다.
```

**kwargs:** `[{}, {"end_phrase": "인도에서."}]`

- Natural: 
- Faithful: 
- Scorable: 

## 3280

**instructions:** `detectable_content:number_placeholders`

**English**

```
What's the difference between the Apple and Albania? Answer in email format. Your response must contain at least six placeholders which should be represented by square brackets like [name].
```

**Korean**

```
애플과 알바니아의 차이점은 무엇인가요? 이메일 형식으로 작성해 주세요. 응답에는 [이름]과 같이 대괄호로 표시된 자리 표시자가 최소 6개 이상 포함되어야 합니다.
```

**kwargs:** `[{"num_placeholders": 6}]`

- Natural: 
- Faithful: 
- Scorable: 

## 3386

**instructions:** `keywords:forbidden_words, keywords:existence`

**English**

```
Jennifer goes to the store to buy milk. She has 10 dollars in her pocket and milk costs 3 dollars per gallon. How many gallons of milk can she buy? Explain your thinking. Avoid the keywords: 'divide', 'answer'. Include the keyword 'remainder'.
```

**Korean**

```
제니퍼는 우유를 사러 가게에 갑니다. 그녀는 주머니에 10달러를 가지고 있고, 우유는 1갤런에 3달러입니다. 그녀는 우유를 몇 갤런 살 수 있을까요? 생각한 과정을 설명하세요. '나눗셈', '정답'이라는 키워드는 사용하지 마세요. '나머지'라는 키워드는 포함하세요.
```

**kwargs:** `[{"forbidden_words": ["나눗셈", "정답"]}, {"keywords": ["나머지"]}]`

- Natural: 
- Faithful: 
- Scorable: 

## 3453

**instructions:** `detectable_format:number_highlighted_sections`

**English**

```
Summarize the history of Japan. Italicize at least 5 keywords in your response. To indicate a italic word, wrap it with asterisk, like *italic*
```

**Korean**

```
일본의 역사를 요약해 주세요. 응답에서 최소 5개의 키워드를 기울임꼴로 표시하세요. 기울임꼴 단어를 나타내려면 *기울임꼴*처럼 별표로 감싸세요.
```

**kwargs:** `[{"num_highlights": 5}]`

- Natural: 
- Faithful: 
- Scorable: 

## 3536

**instructions:** `startend:quotation`

**English**

```
Write a song about innovation with a positive tone that is appealing to teenagers. Put your entire response in double quotation marks.
```

**Korean**

```
10대들의 마음을 사로잡을 수 있는 긍정적인 분위기의 혁신에 관한 노래를 만들어 주세요. 전체 응답을 큰따옴표(")로 감싸세요.
```

**kwargs:** `[{}]`

- Natural: 
- Faithful: 
- Scorable: 

## 3563

**instructions:** `combination:repeat_prompt`

**English**

```
What is the name of the actor who played Gandalf in Lord of the Rings?
First repeat the question above without change of words, then give your answer.
```

**Korean**

```
반지의 제왕에서 간달프 역을 맡은 배우의 이름은 무엇인가요?
먼저 위의 질문을 단어 하나 바꾸지 말고 그대로 반복한 다음, 답변을 제시하세요.
```

**kwargs:** `[{"prompt_to_repeat": "반지의 제왕에서 간달프 역을 맡은 배우의 이름은 무엇인가요?"}]`

- Natural: 
- Faithful: 
- Scorable: 

## 3565

**instructions:** `keywords:forbidden_words, length_constraints:number_paragraphs`

**English**

```
What does the word "jock" mean to you? Please generate an answer with two parts. The two parts should be separated by 3 asterisks '***'. Also, reply without mentioning the word "jock" throughout.
```

**Korean**

```
당신에게 "운동광"이라는 단어는 어떤 의미인가요? 두 문단으로 구성된 답변을 작성해 주세요. 두 문단은 3개의 별표 '***'로 구분되어야 합니다. 또한, 답변 전체에서 "운동광"이라는 단어를 언급하지 마세요.
```

**kwargs:** `[{"forbidden_words": ["운동광"]}, {"num_paragraphs": 2}]`

- Natural: 
- Faithful: 
- Scorable: 

## 3690

**instructions:** `detectable_format:title`

**English**

```
Critique the following ad copy for a new dating app, and make sure to include a title wrapped in double angular brackets, i.e. <<title>>: "Meet your new match! Cohen is a free app that matches you with others based on your interests and location. With Cohen, you can find love, friendship, or just someone to swing with. Download Cohen today and start meeting new people!"
```

**Korean**

```
새로운 데이팅 앱을 위한 다음 광고 문구를 비평해 주세요. 단, 이중 꺾쇠괄호로 감싼 제목(예: <<제목>>)을 반드시 포함해야 합니다.

"새로운 인연을 만나보세요! 코헨(Cohen)은 관심사와 위치를 기반으로 다른 사람들과 매칭해 주는 무료 앱입니다. 코헨과 함께라면 사랑, 우정, 혹은 가볍게 어울릴 사람을 찾을 수 있습니다. 오늘 코헨을 다운로드하고 새로운 사람들을 만나보세요!"
```

**kwargs:** `[{}]`

- Natural: 
- Faithful: 
- Scorable: 

## 3718

**instructions:** `detectable_format:title, combination:repeat_prompt, punctuation:no_comma`

**English**

```
Create a resume for a military officer who served in Iraq and was later hired by a private military contractor. Make sure to include a title that is wrapped in double angular brackets, i.e. <<resume of xyz>>. Refrain from using any commas in your response.

Before you respond with any word, first repeat the exact, entire request above, word for word without change.
```

**Korean**

```
이라크에서 복무한 후 민간 군사 기업에 고용된 장교의 이력서를 작성하세요. 이중 꺾쇠괄호로 감싼 제목(예: <<xyz의 이력서>>)을 반드시 포함하세요. 응답에 쉼표를 사용하지 마세요.

어떤 단어로든 응답을 시작하기 전에, 먼저 위의 요청 전체를 토씨 하나 바꾸지 말고 정확히 그대로 반복하세요.
```

**kwargs:** `[{}, {"prompt_to_repeat": "이라크에서 복무한 후 민간 군사 기업에 고용된 장교의 이력서를 작성하세요. 이중 꺾쇠괄호로 감싼 제목(예: <<xyz의 이력서>>)을 반드시 포함하세요. 응답에 쉼표를 사용하지 마세요."}, {}]`

- Natural: 
- Faithful: 
- Scorable: 

## 3719

**instructions:** `detectable_format:title`

**English**

```
Write a song about choking on a piece of chicken in the Potomac River. Put the title in double angular brackets, i.e. <<title of my song>>.
```

**Korean**

```
포토맥 강에서 닭고기를 먹다 목에 걸린 것에 대한 노래를 써주세요. 제목은 이중 꺾쇠괄호로 감싸주세요(예: <<내 노래 제목>>).
```

**kwargs:** `[{}]`

- Natural: 
- Faithful: 
- Scorable: 

## 3743

**instructions:** `detectable_content:number_placeholders`

**English**

```
I need a joke involving Zoe and bubbles that contains at least 3 placeholders represented by square brackets such as [date].
```

**Korean**

```
조이와 비눗방울이 등장하는 농담을 하나 해주세요. 단, [날짜]와 같이 대괄호로 표시된 자리 표시자가 3개 이상 포함되어야 합니다.
```

**kwargs:** `[{"num_placeholders": 3}]`

- Natural: 
- Faithful: 
- Scorable: 

## 3750

**instructions:** `detectable_format:constrained_response`

**English**

```
Is the moon landing a propaganda made up by the government? Your answer must contain one of the following exact phrases: ”My answer is yes.", "My answer is no.", "My answer is maybe."
```

**Korean**

```
달 착륙은 정부가 꾸며낸 선전인가요? 답변에는 다음 중 하나의 문구가 정확히 포함되어야 합니다: "제 답변은 예입니다.", "제 답변은 아니요입니다.", "제 답변은 아마도입니다."
```

**kwargs:** `[{}]`

- Natural: 
- Faithful: 
- Scorable: 
