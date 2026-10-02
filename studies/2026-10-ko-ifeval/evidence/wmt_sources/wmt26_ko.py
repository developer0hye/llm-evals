import json,collections,statistics,itertools,math,numpy as np,scipy.stats,functools
data=json.load(open('wmt26_ann.json'))
print(list(data.keys()))
key=[k for k in data if 'kor' in k]
print('korean keys',key)
data={k:data[k] for k in key}
for langs,dl in data.items():
    new=collections.defaultdict(list)
    for line in dl:
        if line["annotation"]=="__RESET__": new[line["user_id"]]=[]
        elif "item_id" not in line["item"][0]: pass
        elif line["item"][0]["item_id"].startswith("attention_check_"): pass
        elif "_#_tutorial_#_" in line["item"][0]["item_id"]: pass
        else: new[line["user_id"]].append(line)
    data[langs]=[l for u in new.values() for l in u]
def filt(langs,dl):
    byu=collections.defaultdict(list)
    for l in dl: byu[l["user_id"]].append(l)
    ms=collections.defaultdict(list)
    for l in dl:
        for ia,it in zip(l["annotation"],l["item"]):
            for m,a in ia.items(): ms[m].append(a["score"])
    mu={(a,b):statistics.mean(x)-statistics.mean(y) for a,x in ms.items() for b,y in ms.items() if a!=b and len(x)>10 and len(y)>10}
    var={(a,b):statistics.variance(x)+statistics.variance(y) for a,x in ms.items() for b,y in ms.items() if a!=b and len(x)>10 and len(y)>10}
    ban=set()
    for u,du in byu.items():
        if len(du)<3: continue
        p=[]
        for l in du:
            for ia,it in zip(l["annotation"],l["item"]):
                for (m1,a1),(m2,a2) in itertools.combinations(ia.items(),2):
                    if (m1,m2) not in var: continue
                    p.append(2**(-((a1["score"]-a2["score"]-mu[(m1,m2)])**2/(2*var[(m1,m2)]+1e-6))))
        if p and statistics.mean(p)<0.75: ban.add(u)
    print(langs,'users',len(byu),'banned',len(ban))
    return [l for l in dl if l["user_id"] not in ban]
data={k:filt(k,v) for k,v in data.items()}
def sig(a,b,n=1000):
    pairs=[(x,y) for x,y in zip(a,b) if not(math.isnan(x) or math.isnan(y))]
    d=np.array([x-y for x,y in pairs])
    va=np.array([x for x in a if not math.isnan(x)]); vb=np.array([x for x in b if not math.isnan(x)])
    if len(d)>=2 and np.any(d>0):
        try:
            r=scipy.stats.bootstrap((d,),np.mean,vectorized=True,n_resamples=n,confidence_level=0.95,alternative="greater",random_state=0)
            if r.confidence_interval.low>0: return True
        except ValueError: pass
    if len(va)>=2 and len(vb)>=2:
        try:
            r=scipy.stats.bootstrap((va,vb),lambda x,y,axis=-1:np.mean(x,axis=axis)-np.mean(y,axis=axis),vectorized=True,n_resamples=n,confidence_level=0.95,alternative="greater",random_state=0)
            if r.confidence_interval.low>0: return True
        except ValueError: pass
    return False
for langs,dl in data.items():
    dmi=collections.defaultdict(lambda:collections.defaultdict(list)); items=set(); users=set()
    for l in dl:
        users.add(l["user_id"])
        for ia,it in zip(l["annotation"],l["item"]):
            items.add(it["item_id"])
            for m,a in ia.items(): dmi[m][it["item_id"]].append(a["score"])
    items=sorted(items)
    avg={m:[statistics.mean(dmi[m][i]) if i in dmi[m] else float('nan') for i in items] for m in dmi}
    flat=sorted(avg.items(),key=lambda x:-np.nanmean(x[1]))
    print(langs,'items',len(items),'annotators',len(users),'lines',len(dl))
    N=len(flat)
    for i,(m,s) in enumerate(flat):
        top=i
        for top in range(i,-1,-1):
            if top-1>=0 and sig(tuple(flat[top-1][1]),tuple(s)): break
        bot=i
        for bot in range(i,N-1):
            if sig(tuple(s),tuple(flat[bot+1][1])): break
        v=[x for x in s if not math.isnan(x)]
        ci=scipy.stats.t.interval(0.95,len(v)-1,loc=np.mean(v),scale=scipy.stats.sem(v))
        print(f"{top+1:>2}-{bot+1:<2} {m:35s} {np.mean(v):6.1f}  [{ci[0]:.1f},{ci[1]:.1f}] n={len(v)}")

print('--- paired on shared items')
A=dict(flat)
for a,b in [('Gemini 3.1 Pro','GPT 5.5'),('Gemini 3.1 Pro','DeepSeek V4 Pro'),('GPT 5.5','DeepSeek V4 Pro'),('Gemini 3.1 Pro','Qwen 3.6 - 27b'),('Gemini 3.1 Pro','Mistral Medium 3.5')]:
    p=[(x,y) for x,y in zip(A[a],A[b]) if not(math.isnan(x) or math.isnan(y))]
    d=[x-y for x,y in p]
    w=scipy.stats.wilcoxon(d).pvalue if any(d) else 1
    print(a,'vs',b,'n',len(p),'meanA',round(np.mean([x for x,_ in p]),1),'meanB',round(np.mean([y for _,y in p]),1),'wilcoxon p',round(w,4))
