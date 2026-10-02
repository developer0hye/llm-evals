import json,asyncio,aiohttp,os,sys
SYS="""You translate IFEval instruction-following items from English into natural Korean for a Korean benchmark.
Input: one JSON object with "prompt", "instruction_id_list", "kwargs".
Rules:
- Translate "prompt" into fluent, natural Korean.
- Keep every verifiable constraint satisfiable in Korean. Any word or phrase that appears both in the prompt and in kwargs (keywords, forbidden_words, keyword, end_phrase, prompt_to_repeat, postscript_marker) must be translated identically in both places, so the checker and the prompt agree.
- Keep numbers, relations and markup instructions unchanged.
- If a constraint cannot work in Korean (letter case, English letter frequency), keep it in English and set "untranslatable": true.
Output only the JSON object with the same keys plus "untranslatable"."""
CFG={"gemini-3.1-pro(high)":("google/gemini-3.1-pro-preview",{"effort":"high"}),
     "gemini-3.8-flash(medium)":("google/gemini-3.8-flash",{"effort":"medium"}),
     "gemini-3.8-flash(off)":("google/gemini-3.8-flash",{"enabled":False})}
rows=json.load(open('probe5.json'))
async def one(s,name,mid,rs,r):
    kw=[{k:v for k,v in (d or {}).items() if v is not None} for d in r['kwargs']]
    item=json.dumps({"prompt":r['prompt'],"instruction_id_list":r['instruction_id_list'],"kwargs":kw},ensure_ascii=False)
    body={"model":mid,"messages":[{"role":"system","content":SYS},{"role":"user","content":item}],"temperature":0,"max_tokens":32000,"reasoning":rs,"usage":{"include":True}}
    async with s.post("https://openrouter.ai/api/v1/chat/completions",json=body,headers={"Authorization":"Bearer "+os.environ["OPENROUTER_API_KEY"]},timeout=aiohttp.ClientTimeout(total=900)) as resp:
        d=await resp.json()
    if 'error' in d: return name,r['key'],{'error':str(d['error'])[:150]}
    u=d['usage']; c=d['choices'][0]
    return name,r['key'],{"prompt_tokens":u['prompt_tokens'],"completion_tokens":u['completion_tokens'],"reasoning":(u.get('completion_tokens_details') or {}).get('reasoning_tokens'),"cost":u.get('cost'),"provider":d.get('provider'),"finish":c.get('finish_reason'),"out":c['message']['content']}
async def main():
    async with aiohttp.ClientSession() as s:
        res=await asyncio.gather(*(one(s,n,m,rs,r) for n,(m,rs) in CFG.items() for r in rows))
    json.dump(res,open('probe_out.json','w'),ensure_ascii=False,indent=1)
    for n in CFG:
        rr=[x for nn,k,x in res if nn==n]
        ok=[x for x in rr if 'error' not in x]
        print(n,'ok',len(ok),'/',len(rr),'| prompt tok',sum(x['prompt_tokens'] for x in ok),'completion',sum(x['completion_tokens'] for x in ok),'reasoning',sum(x['reasoning'] or 0 for x in ok),'cost $',round(sum(x['cost'] or 0 for x in ok),5),'| providers',{x['provider'] for x in ok},'| errors',[x.get('error') for x in rr if 'error' in x])
asyncio.run(main())
