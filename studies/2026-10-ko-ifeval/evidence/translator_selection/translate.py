import json,asyncio,aiohttp,os,random,collections,sys
S=sys.argv[1]
rows=[json.loads(l) for l in open(f'{S}/kgen/wmt_enko.jsonl')]
ok=[r for r in rows if not r.get('is_bad_source') and r.get('domain')!='canary']
rng=random.Random(0); sample=[]
for d in ('literary','news','social','speech'):
    sample+=rng.sample([r for r in ok if r['domain']==d],30)
json.dump(sample,open('sample.json','w'),ensure_ascii=False)
INSTR="Translate the following English text into Korean. Preserve meaning, tone and formatting. Output only the Korean translation, nothing else.\n\n"
CFG={"opus-5.5":("anthropic/claude-opus-5.5",{"effort":"medium"}),
     "gemini-3.1-pro":("google/gemini-3.1-pro-preview",{"effort":"high"}),
     "gemini-3.8-flash":("google/gemini-3.8-flash",{"effort":"medium"}),
     "gpt-4o":("openai/gpt-4o-2024-08-06",None)}
async def one(s,sem,name,mid,rs,r):
    body={"model":mid,"messages":[{"role":"user","content":INSTR+r['source']}],"temperature":0,"max_tokens":16000,"usage":{"include":True}}
    if rs: body["reasoning"]=rs
    async with sem:
        for a in range(5):
            try:
                async with s.post("https://openrouter.ai/api/v1/chat/completions",json=body,headers={"Authorization":"Bearer "+os.environ["OPENROUTER_API_KEY"]},timeout=aiohttp.ClientTimeout(total=900)) as resp:
                    d=await resp.json()
                if 'error' in d: raise RuntimeError(str(d['error'])[:200])
                c=d['choices'][0]; txt=(c['message'].get('content') or '').strip()
                if not txt: raise RuntimeError('empty')
                return {"model":name,"segment_id":r['segment_id'],"domain":r['domain'],"hyp":txt,"finish":c.get('finish_reason'),"provider":d.get('provider'),"cost":d['usage'].get('cost'),"out_tokens":d['usage'].get('completion_tokens')}
            except Exception as e:
                err=str(e); await asyncio.sleep(5*(a+1))
        return {"model":name,"segment_id":r['segment_id'],"error":err}
async def main():
    sem=asyncio.Semaphore(16)
    async with aiohttp.ClientSession() as s:
        res=await asyncio.gather(*(one(s,sem,n,m,rs,r) for n,(m,rs) in CFG.items() for r in sample))
    json.dump(res,open('hyps.json','w'),ensure_ascii=False,indent=1)
    for n in CFG:
        rr=[x for x in res if x['model']==n]; okk=[x for x in rr if 'error' not in x]
        print(n,'ok',len(okk),'/',len(rr),'cost $',round(sum(x['cost'] or 0 for x in okk),3),'providers',collections.Counter(x['provider'] for x in okk),'finish',collections.Counter(x['finish'] for x in okk))
asyncio.run(main())
