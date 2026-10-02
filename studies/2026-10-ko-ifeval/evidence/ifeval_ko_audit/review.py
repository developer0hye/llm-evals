import json,asyncio,aiohttp,os,sys,re
import numpy as np, pandas as pd
S=sys.argv[1]
ko=pd.read_parquet(f'{S}/ifevalko.parquet'); en={json.loads(l)['key']:json.loads(l) for l in open(f'{S}/xl/ifeval.jsonl')}
def clean(kw): return {k:(v.tolist() if isinstance(v,np.ndarray) else (int(v) if isinstance(v,float) and v==int(v) else v)) for k,v in (kw or {}).items() if v is not None and not (isinstance(v,float) and np.isnan(v))}
SYS="""You audit a Korean translation of an IFEval item (instruction-following benchmark scored by rule-based checkers).
You get the English original (prompt + checker kwargs) and the Korean version (prompt + checker kwargs). The Korean checkers work like this:
- keywords:existence / keywords:frequency: case-insensitive regex search of the kwargs string in the response (substring, particles allowed).
- keywords:forbidden_words: regex \\b{word}\\b, so a forbidden Korean word followed by a particle is NOT caught.
- length_constraints:number_words: counts whitespace-separated tokens (Korean eojeol).
- relation "less than N" means count < N; "at least N" means count >= N.
- startend:end_checker / combination:repeat_prompt / detectable_content:postscript compare strings exactly.
Find problems that make the Korean item NOT equivalent to the original or NOT fairly checkable:
 dropped_constraint (a constraint in the original prompt is missing from the Korean prompt),
 changed_constraint (number, boundary such as more-than vs at-least, scope or wording changed so a faithful answer could fail or a wrong answer could pass),
 kwarg_mismatch (Korean prompt and Korean kwargs disagree),
 unsatisfiable (cannot be satisfied by any Korean answer that follows the Korean prompt),
 meaning_change (task content changed), mistranslation (wrong/awkward Korean that misleads), other.
Ignore harmless stylistic differences and unit localisation (feet->meters, $->원) unless it breaks a checker.
Return ONLY JSON: {"issues":[{"type":...,"severity":"breaks_scoring"|"minor","detail":"<=40 words"}]} ; empty list if none."""
async def one(s,sem,r):
    e=en[r['key']]
    item={"instruction_id_list":e['instruction_id_list'],
          "english":{"prompt":e['prompt'],"kwargs":[{k:v for k,v in d.items() if v is not None} for d in e['kwargs']]},
          "korean":{"prompt":r['prompt'],"kwargs":[clean(d) for d in r['kwargs']]}}
    body={"model":"google/gemini-3.1-pro-preview","messages":[{"role":"system","content":SYS},{"role":"user","content":json.dumps(item,ensure_ascii=False)}],
          "temperature":0,"max_tokens":16000,"reasoning":{"effort":"medium"},"usage":{"include":True},"response_format":{"type":"json_object"}}
    async with sem:
        for attempt in range(5):
            try:
                async with s.post("https://openrouter.ai/api/v1/chat/completions",json=body,headers={"Authorization":"Bearer "+os.environ["OPENROUTER_API_KEY"]},timeout=aiohttp.ClientTimeout(total=900)) as resp:
                    d=await resp.json()
                if 'error' in d: raise RuntimeError(str(d['error'])[:200])
                txt=d['choices'][0]['message']['content']; m=re.search(r'\{.*\}',txt,re.S)
                return {"key":int(r['key']),"issues":json.loads(m.group(0))['issues'],"cost":d['usage'].get('cost'),"provider":d.get('provider')}
            except Exception as ex:
                err=str(ex); await asyncio.sleep(5*(attempt+1))
        return {"key":int(r['key']),"error":err}
async def main():
    sem=asyncio.Semaphore(12)
    async with aiohttp.ClientSession() as s:
        res=await asyncio.gather(*(one(s,sem,r) for _,r in ko.iterrows()))
    json.dump(res,open('review.json','w'),ensure_ascii=False,indent=1)
    ok=[x for x in res if 'error' not in x]
    print('reviewed',len(ok),'errors',len(res)-len(ok),'cost $',round(sum(x['cost'] or 0 for x in ok),3))
asyncio.run(main())
