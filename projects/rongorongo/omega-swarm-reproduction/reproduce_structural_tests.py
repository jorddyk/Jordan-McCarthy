#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, importlib.util, json, random, re
from collections import Counter, defaultdict
from math import comb
from pathlib import Path
import numpy as np


ALLOWED=set("ABCDEGHNPQRS")


def load_encoding(path):
    spec=importlib.util.spec_from_file_location("enc",path)
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod.horley_encoding


def clean(x):
    for s in "bcdeghijkostxy!*?()": x=x.replace(s,"")
    out=[]
    for z in x.replace("."," ").split():
        if ":" in z:
            j=z.index(":"); z=z[j+1:]+" "+z[:j]
        out.append(z)
    x=" ".join(i.lstrip("0") for i in " ".join(out).split()).lower()
    return x if x!="0" else ""


def normalize(seq,enc):
    out=[]
    for glyph in seq.split("#")[0].replace("-"," ").split():
        for g in clean(glyph).split():
            mapped=enc.get(g,enc.get(re.sub("[a-z]","",g),g))
            out.extend(u for u in mapped.split() if u and u!="?")
    return out


def max_support(seqs,n=5):
    c=Counter()
    for s in seqs: c.update(set(tuple(s[i:i+n]) for i in range(len(s)-n+1)))
    return max(c.values(),default=0)


def adj(pos): return sum(b==a+1 for a,b in zip(pos,pos[1:]))


def exact_p(n,k,obs):
    fav=0
    for runs in range(1,k+1):
        a=k-runs
        if a<=obs and runs<=n-k+1:
            fav+=comb(k-1,runs-1)*comb(n-k+1,runs)
    return fav/comb(n,k)


def base(part):
    m=re.match(r"0*(\d+)",part)
    return str(int(m.group(1))) if m else None


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--dir",default=".")
    ap.add_argument("--terminal-reps",type=int,default=100000)
    ap.add_argument("--ba6-reps",type=int,default=50000)
    ap.add_argument("--orientation-reps",type=int,default=20000)
    a=ap.parse_args(); root=Path(a.dir); enc=load_encoding(root/"horley_encoding.py")


    records=[]; whole=0
    with open(root/"horley_parallels.csv",encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            arts={re.match(r"([A-Za-z])",p.strip()).group(1).upper() for p in row["Line"].split("/") if re.match(r"([A-Za-z])",p.strip())}
            if not arts or any(x not in ALLOWED for x in arts): continue
            seq=row["Sequence"].split("\t",1)[0].strip(); toks=[x for x in seq.split("-") if x]
            if len(toks)<2: continue
            records.append((int(row["ID"]),row["Line"],normalize(seq,enc))); whole+=len(toks)
    seqs=[r[2] for r in records]
    assert (len(records),whole,sum(map(len,seqs)))==(141,1021,1598)


    core=("2a","2a","8","8","4"); loc=[]
    for rid,line,s in records:
        for i in range(len(s)-4):
            if tuple(s[i:i+5])==core: loc.append((rid,line,i+1))
    observed=max_support(seqs); rng=np.random.default_rng(987654321); dist=Counter()
    for _ in range(a.terminal_reps):
        shuffled=[]
        for s in seqs:
            q=list(s); rng.shuffle(q); shuffled.append(q)
        dist[max_support(shuffled)]+=1
    terminal_p=(sum(v for k,v in dist.items() if k>=observed)+1)/(a.terminal_reps+1)


    passages=json.loads((root/"frozen_passages.json").read_text())
    tests=[]
    for row in passages:
        t=row["strict_tokens"]
        for token,k in Counter(t).items():
            if k<2: continue
            pos=[i for i,x in enumerate(t) if x==token]
            tests.append((row["passage_id"],row["source_line"],token,len(t),k,adj(pos),exact_p(len(t),k,adj(pos))))
    tests.sort(key=lambda x:x[-1]); obs=tests[0][-1]; rng2=random.Random(32711); extreme=0
    for _ in range(a.ba6_reps):
        minp=1.0
        for row in passages:
            t=list(row["strict_tokens"]); rng2.shuffle(t)
            for token,k in Counter(t).items():
                if k<2: continue
                pos=[i for i,x in enumerate(t) if x==token]
                minp=min(minp,exact_p(len(t),k,adj(pos)))
        extreme+=minp<=obs
    ba6_p=(extreme+1)/(a.ba6_reps+1)


    compounds=[]
    for row in passages:
        for token in row["strict_tokens"]:
            if ":" in token or token.count(".")!=1: continue
            x,y=map(base,token.split("."))
            if x and y and x!=y: compounds.append((x,y))
    pairs=defaultdict(list); lr=defaultdict(lambda:[0,0])
    for x,y in compounds:
        pairs[tuple(sorted((x,y),key=int))].append((x,y)); lr[x][0]+=1; lr[y][1]+=1
    mirrors=sum(len(set(v))==2 for v in pairs.values())


    rng3=random.Random(0x7031); fair=[]
    for _ in range(a.orientation_reps):
        fair.append(sum(len({rng3.random()<0.5 for _ in occ})==2 for occ in pairs.values()))
    fair_p=(sum(v<=mirrors for v in fair)+1)/(len(fair)+1)


    def propensity(x,y,alpha=.5):
        lx,rx=lr[x]; ly,ry=lr[y]
        px=(lx+alpha)/(lx+rx+2*alpha); py=(ly+alpha)/(ly+ry+2*alpha)
        w1,w2=px*(1-py),py*(1-px)
        return .5 if w1+w2==0 else w1/(w1+w2)
    rng4=random.Random(0x7032); prop=[]
    for _ in range(a.orientation_reps):
        prop.append(sum(len({rng4.random()<propensity(x,y) for _ in occ})==2 for (x,y),occ in pairs.items()))
    prop_p=(sum(v<=mirrors for v in prop)+1)/(len(prop)+1)


    print(json.dumps({
      "corpus":{"passages":len(records),"whole_tokens":whole,"components":sum(map(len,seqs))},
      "terminal":{"core":core,"locations":loc,"max_support":observed,"null":dict(dist),"p":terminal_p},
      "ba6":{"best":tests[0],"eligible_tests":len(tests),"extreme":extreme,"p":ba6_p},
      "orientation":{"occurrences":len(compounds),"pairs":len(pairs),"mirrors":mirrors,"fair_mean":sum(fair)/len(fair),"fair_p":fair_p,"propensity_mean":sum(prop)/len(prop),"propensity_p":prop_p,"side_counts":dict(lr)}
    },indent=2))


if __name__=="__main__": main()


