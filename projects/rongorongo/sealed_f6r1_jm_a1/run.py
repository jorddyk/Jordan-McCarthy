from __future__ import annotations

import csv, hashlib, io, json, os, re, urllib.request, xml.etree.ElementTree as ET
from pathlib import Path
from collections import Counter

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score

RUN_ID='F6R1-JM-A1'
SEED=20260716
N_PERM=20000
N_BOOT=10000
TARGETS={'6':'006','10':'010','61':'061','62':'062','63':'063','999':'999'}
MODEL_SPECS={
 'MATCH':{'cat':['host_freq_bin','meaning_class','position_quartile'],'num':['host_len','position_frac','segment_length']},
 'GEOMETRY':{'cat':['primary_hundreds','primary_decade','host_hundreds_signature','host_decades_signature'],'num':['host_len']},
 'SCRIBE':{'cat':['tablet','face'],'num':[]},
 'GRAMMAR':{'cat':['prev_host','next_host','position_quartile'],'num':['at_start','at_end','position_frac','segment_length']},
 'MEANING':{'cat':['meaning_class','prev_class','next_class'],'num':[]},
 'SOUND':{'cat':['host'],'num':[]},
 'COMBINED':{'cat':['host_freq_bin','primary_hundreds','primary_decade','host_hundreds_signature','host_decades_signature','tablet','face','prev_host','next_host','position_quartile','meaning_class','prev_class','next_class','host'],'num':['host_len','position_frac','segment_length','at_start','at_end']},
}
TRAIN_URLS=['https://raw.githubusercontent.com/jgregoriods/rongopy/master/horley_parallels.csv','https://raw.githubusercontent.com/jgregoriods/rongopy/main/horley_parallels.csv']
MAP_URL='https://raw.githubusercontent.com/sperkswerks-ai/hackingrongo/main/data/catalog/horley_encoding.json'
HIDDEN_URLS=['https://kohaumotu.org/Rongorongo/xml/F.xml','http://kohaumotu.org/Rongorongo/xml/F.xml']
ROOT=Path(os.environ.get('RR_OUT','sealed_output'))
PRED=ROOT/'predictions'; TRUTH=ROOT/'truth'; RESULTS=ROOT/'results'
for d in (PRED,TRUTH,RESULTS): d.mkdir(parents=True,exist_ok=True)

def sha_bytes(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def sha_file(p:Path)->str:return sha_bytes(p.read_bytes())
def fetch_first(urls:list[str])->tuple[bytes,str]:
    err=[]
    for u in urls:
        try:
            req=urllib.request.Request(u,headers={'User-Agent':'RongorongoBlindTest/1.0'})
            with urllib.request.urlopen(req,timeout=45) as r:b=r.read()
            if len(b)>20:return b,u
        except Exception as e:err.append(f'{u}: {type(e).__name__}')
    raise RuntimeError('all sources failed: '+'; '.join(err))
def code_key(part:str)->str|None:
    m=re.search(r'\d{1,3}',str(part));return str(int(m.group(0))) if m else None
def expand_unit(raw:str,hmap:dict[str,str])->list[str]:
    out=[]
    for part in re.split(r'[.:]',str(raw)):
        k=code_key(part);out.extend(['?'] if k is None else str(hmap.get(k,k)).split())
    return out
def side_label(exp:list[str],target:str)->str:
    ti=[i for i,x in enumerate(exp) if x==target];hi=[i for i,x in enumerate(exp) if x not in TARGETS and x!='?']
    if not hi:return 'standalone'
    if len(ti)>=2 and min(ti)<min(hi) and max(ti)>max(hi):return 'bilateral'
    if max(ti)<min(hi):return 'left'
    if min(ti)>max(hi):return 'right'
    return 'internal'
def num(x:str|None)->int:
    m=re.search(r'\d+',str(x)) if x is not None else None;return int(m.group(0)) if m else -1
def broad_class(primary:str|None)->str:
    n=num(primary)
    if 200<=n<400:return 'anthropomorphic'
    if 400<=n<500 or 600<=n<700:return 'avian'
    if 700<=n<800:return 'animal_aquatic'
    if 500<=n<600:return 'object_composite'
    if n>=0:return 'geometric_object'
    return 'unresolved'
def tablet_from_line(line:str)->str:return str(line).split('/')[0][0] if line else '?'
def face_from_line(line:str)->str:
    s=str(line).split('/')[0];return s[1] if len(s)>1 and s[1].isalpha() else '?'
def units_from_training(csv_bytes:bytes)->list[dict]:
    rows=[]
    for r in csv.DictReader(io.StringIO(csv_bytes.decode('utf-8'))):
        seq=r['Sequence'].split('#',1)[0].strip();units=seq.split('-') if seq else []
        rows.append({'passage_id':int(r['ID']),'line':r['Line'],'tablet':tablet_from_line(r['Line']),'face':face_from_line(r['Line']),'units':units})
    return rows
def units_from_xml(xml_bytes:bytes)->list[dict]:
    root=ET.fromstring(xml_bytes);tablet=root.find('tablet') if root.tag!='tablet' else root
    if tablet is None:raise ValueError('no tablet element')
    tid=(tablet.findtext('tablet-code') or 'F').strip();rows=[];pid=100000
    for side in tablet.findall('side'):
        sc=(side.findtext('side-code') or '?').strip()
        for line in side.findall('line'):
            lc=(line.findtext('line-code') or '?').strip();units=[];current=''
            for g in line.findall('glyph'):
                c=(g.findtext('code/ceipp') or '').strip()
                if not c:continue
                c='?' if c=='_' else c;current+=c;link=(g.findtext('link') or '').strip()
                if link in ('.',':'):current+=link
                else:units.append(current.rstrip('.:'));current=''
            if current:units.append(current.rstrip('.:'))
            if units:pid+=1;rows.append({'passage_id':pid,'line':f'{tid}{sc}{lc}','tablet':tid,'face':sc,'units':units})
    return rows
def derive(rows:list[dict],hmap:dict[str,str])->pd.DataFrame:
    rec=[]
    for row in rows:
        units=row['units'];n=len(units);exps=[expand_unit(u,hmap) for u in units];hosts=[tuple(x for x in e if x not in TARGETS and x!='?') for e in exps]
        for i,(raw,exp,host) in enumerate(zip(units,exps,hosts)):
            tset=sorted(set(x for x in exp if x in TARGETS),key=lambda x:int(x));uncertain=('?' in raw or '_' in raw or '(' in raw);eligible=(not uncertain and len(host)>0 and len(tset)<=1);target=tset[0] if len(tset)==1 else None;side='bare' if target is None else side_label(exp,target);primary=host[0] if host else None;ph=hosts[i-1] if i else tuple();nh=hosts[i+1] if i+1<n else tuple()
            rec.append({'passage_id':row['passage_id'],'line':row['line'],'tablet':row['tablet'],'face':row['face'],'token_index':i,'segment_length':n,'position_frac':(i+.5)/max(n,1),'position_quartile':str(min(3,int(4*i/max(n,1)))),'at_start':int(i==0),'at_end':int(i==n-1),'raw_unit':raw,'expansion':' '.join(exp),'host':'+'.join(host) if host else 'NONE','host_len':len(host),'primary_host':num(primary),'meaning_class':broad_class(primary),'prev_host':'+'.join(ph) if ph else 'BOUNDARY','next_host':'+'.join(nh) if nh else 'BOUNDARY','prev_class':broad_class(ph[0] if ph else None),'next_class':broad_class(nh[0] if nh else None),'uncertain':uncertain,'mixed_target':len(tset)>1,'eligible':eligible,'presence':int(target is not None),'target':TARGETS.get(target,'bare'),'side':side,'joint':'bare' if target is None else f'{TARGETS[target]}_{side}'})
    return pd.DataFrame(rec)
def add_train_frequency(train:pd.DataFrame,test:pd.DataFrame)->tuple[pd.DataFrame,pd.DataFrame]:
    counts=train.groupby('host').size()
    def add(d):
        d=d.copy();d['host_frequency']=d.host.map(counts).fillna(0).astype(int);d['host_freq_bin']=np.select([d.host_frequency.eq(0),d.host_frequency.eq(1),d.host_frequency.eq(2),d.host_frequency.between(3,5),d.host_frequency.between(6,10)],['0','1','2','3-5','6-10'],default='11+');d['primary_hundreds']=(d.primary_host//100).astype(str);d['primary_decade']=((d.primary_host%100)//10).astype(str)
        def sig(h,div):return 'NONE' if h=='NONE' else '+'.join(str(num(z)//div) for z in str(h).split('+'))
        d['host_hundreds_signature']=d.host.map(lambda h:sig(h,100));d['host_decades_signature']=d.host.map(lambda h:sig(h,10));return d
    return add(train),add(test)
def pipe(spec):
    ts=[]
    if spec['cat']:ts.append(('cat',Pipeline([('imp',SimpleImputer(strategy='most_frequent')),('oh',OneHotEncoder(handle_unknown='ignore'))]),spec['cat']))
    if spec['num']:ts.append(('num',Pipeline([('imp',SimpleImputer(strategy='median')),('sc',StandardScaler(with_mean=False))]),spec['num']))
    return Pipeline([('pre',ColumnTransformer(ts,remainder='drop')),('clf',SGDClassifier(loss='log_loss',alpha=.001,max_iter=1500,tol=1e-4,random_state=SEED))])
def prior(y:list[str],labels:list[str],n:int)->np.ndarray:
    c=Counter(y);den=len(y)+len(labels);p=np.array([(c[l]+1)/den for l in labels],float);return np.tile(p,(n,1))
def aligned(model,X,labels):
    p=model.predict_proba(X);out=np.full((len(X),len(labels)),1e-15)
    for j,c in enumerate(model.named_steps['clf'].classes_):out[:,labels.index(str(c))]=p[:,j]
    out/=out.sum(1,keepdims=True);return out
def fit_predict(train,test,ycol,labels):
    tr,te=add_train_frequency(train,test);y=tr[ycol].astype(str).tolist();out={'FREQ':prior(y,labels,len(te))}
    for name,spec in MODEL_SPECS.items():m=pipe(spec);m.fit(tr,y);out[name]=aligned(m,te,labels)
    return out,te
def loss_rows(y,labels,p):
    ix=np.array([labels.index(str(v)) for v in y]);return -np.log(np.clip(p[np.arange(len(ix)),ix],1e-15,1))
def metric(y,labels,p):
    ix=np.array([labels.index(str(v)) for v in y]);pred=np.argmax(p,1);oh=np.zeros_like(p);oh[np.arange(len(ix)),ix]=1
    return {'n':len(ix),'log_loss':float(loss_rows(y,labels,p).mean()),'brier':float(np.mean(np.sum((p-oh)**2,1))),'accuracy':float(accuracy_score(ix,pred)),'balanced_accuracy':float(balanced_accuracy_score(ix,pred)),'macro_f1':float(f1_score(ix,pred,average='macro',zero_division=0))}
def paired_test(df,y,labels,probs,base='MATCH'):
    rng=np.random.default_rng(SEED+31);groups=df.line.to_numpy();ug=np.unique(groups);out={};bl=loss_rows(y,labels,probs[base])
    for name,p in probs.items():
        ml=loss_rows(y,labels,p);g=np.array([(bl[groups==u].mean()-ml[groups==u].mean()) for u in ug]);obs=float(g.mean());signs=rng.choice([-1.,1.],size=(N_PERM,len(g)));null=(signs*g).mean(1);pv=float((1+(null>=obs).sum())/(N_PERM+1));bi=rng.integers(0,len(g),size=(N_BOOT,len(g)));boot=g[bi].mean(1);out[name]={'gain_vs_'+base+'_nats':obs,'signflip_p':pv,'ci95':[float(np.quantile(boot,.025)),float(np.quantile(boot,.975))]}
    return out
def shuffle_test(df,y,labels,probs):
    rng=np.random.default_rng(SEED+99);y=np.asarray([str(v) for v in y]);yi=np.array([labels.index(v) for v in y],dtype=np.int16);n=len(yi);rows=np.arange(n)[None,:];keys=df[['face','host_freq_bin','host_len']].astype(str);strata=[s.index.to_numpy() for _,s in keys.groupby(list(keys.columns),sort=False)];obs={m:float(loss_rows(y,labels,p).mean()) for m,p in probs.items()};count={m:0 for m in probs};acc={m:0. for m in probs};block=250
    for st in range(0,N_PERM,block):
        b=min(block,N_PERM-st);yp=np.tile(yi,(b,1))
        for ix in strata:
            if len(ix)>1:yp[:,ix]=yi[ix][np.argsort(rng.random((b,len(ix))),1)]
        for m,p in probs.items():ll=-np.log(np.clip(p[rows,yp],1e-15,1)).mean(1);count[m]+=int((ll<=obs[m]+1e-15).sum());acc[m]+=float(np.mean(np.argmax(p,1)[None,:]==yp,1).sum())
    return {m:{'shuffle_p':float((count[m]+1)/(N_PERM+1)),'shuffle_mean_accuracy':acc[m]/N_PERM} for m in probs}
def write_prob_columns(base,prefix,labels,probs):
    for name,p in probs.items():base[f'{prefix}_{name}_prediction']=[labels[i] for i in np.argmax(p,1)];base[f'{prefix}_{name}_confidence']=p.max(1);base[f'{prefix}_{name}_probabilities']=[json.dumps(dict(zip(labels,map(float,r))),sort_keys=True) for r in p]
def main():
    train_b,train_url=fetch_first(TRAIN_URLS);map_b,map_url=fetch_first([MAP_URL]);xml_b,hidden_url=fetch_first(HIDDEN_URLS);hmap=json.loads(map_b.decode('utf-8'));hmap={k:v for k,v in hmap.items() if not k.startswith('_')};training=derive(units_from_training(train_b),hmap);hidden_all=derive(units_from_xml(xml_b),hmap);tr=training[training.eligible].copy().reset_index(drop=True);hid=hidden_all[hidden_all.eligible].copy().reset_index(drop=True)
    tasks={'presence':(tr,hid,'presence',['0','1']),'target':(tr[tr.presence==1].copy(),hid,'target',['006','010','061','062','063','999']),'side':(tr[tr.presence==1].copy(),hid,'side',['left','right','internal','bilateral']),'joint':(tr,hid,'joint',sorted(tr.joint.astype(str).unique()))};pred=hid[['passage_id','line','face','token_index','host','host_len','meaning_class','prev_host','next_host']].copy();task_probs={};task_test={}
    for task,(td,hd,ycol,labels) in tasks.items():probs,hd2=fit_predict(td,hd,ycol,labels);task_probs[task]=(labels,probs);task_test[task]=hd2;write_prob_columns(pred,task,labels,probs)
    pred_path=PRED/'predictions.csv';pred.to_csv(pred_path,index=False);truth_cols=['passage_id','line','face','token_index','raw_unit','expansion','host','eligible','presence','target','side','joint','uncertain','mixed_target'];truth_path=TRUTH/'truth.csv';hidden_all[truth_cols].to_csv(truth_path,index=False);masked_path=PRED/'masked_features.csv';hid.drop(columns=['raw_unit','expansion','presence','target','side','joint','uncertain','mixed_target','eligible'],errors='ignore').to_csv(masked_path,index=False);truth_sha=sha_file(truth_path);pred_sha=sha_file(pred_path)
    manifest={'run_id':RUN_ID,'git_commit':os.environ.get('GITHUB_SHA',''),'script_sha256':sha_file(Path(__file__)),'sources':{'training_url':train_url,'training_sha256':sha_bytes(train_b),'map_url':map_url,'map_sha256':sha_bytes(map_b),'hidden_url':hidden_url,'hidden_source_sha256':sha_bytes(xml_b)},'sealed_truth_sha256':truth_sha,'prediction_sha256':pred_sha,'masked_features_sha256':sha_file(masked_path),'training_counts':{'all_units':len(training),'eligible':len(tr),'positive':int(tr.presence.sum())},'hidden_candidate_count':len(hid),'targets':list(TARGETS.values()),'models':MODEL_SPECS,'seed':SEED,'permutations':N_PERM,'bootstrap':N_BOOT};(PRED/'manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True));(TRUTH/'manifest.json').write_text(json.dumps({'run_id':RUN_ID,'truth_sha256':truth_sha,'source_sha256':sha_bytes(xml_b),'prediction_sha256':pred_sha},indent=2,sort_keys=True));(TRUTH/'F.xml').write_bytes(xml_b)
    score={'run_id':RUN_ID,'prediction_sha256':pred_sha,'truth_sha256':truth_sha,'tasks':{},'coverage':{'candidates':len(hid),'positives':int(hid.presence.sum()),'target_counts':hid.loc[hid.presence==1,'target'].value_counts().to_dict(),'side_counts':hid.loc[hid.presence==1,'side'].value_counts().to_dict()}}
    for task,(td,hd,ycol,labels) in tasks.items():
        evaldf=hid if task in ('presence','joint') else hid[hid.presence==1].copy().reset_index(drop=True);labels0,probs0=task_probs[task];mask=hid.presence.to_numpy()==1;probs={m:p if task in ('presence','joint') else p[mask] for m,p in probs0.items()};y=evaldf[ycol].astype(str).to_numpy()
        if len(y)==0:score['tasks'][task]={'underpowered':True};continue
        edf=task_test[task] if task in ('presence','joint') else task_test[task].loc[mask].reset_index(drop=True);score['tasks'][task]={'metrics':{m:metric(y,labels0,p) for m,p in probs.items()},'paired_vs_MATCH':paired_test(edf,y,labels0,probs,'MATCH'),'paired_vs_FREQ':paired_test(edf,y,labels0,probs,'FREQ'),'shuffled':shuffle_test(edf,y,labels0,probs)}
    p_match=task_probs['presence'][1]['MATCH'][:,1];wr={}
    for face,g in hid.assign(match_p=p_match).groupby('face'):wr[str(face)]={'n':len(g),'observed_positive_rate':float(g.presence.mean()),'MATCH_expected_rate':float(g.match_p.mean()),'residual':float(g.presence.mean()-g.match_p.mean())}
    score['witness_residuals']=wr;(RESULTS/'score_summary.json').write_text(json.dumps(score,indent=2,sort_keys=True));print(json.dumps({'status':'ok','run_id':RUN_ID,'prediction_sha256':pred_sha,'sealed_truth_sha256':truth_sha,'candidates':len(hid)},sort_keys=True))
if __name__=='__main__':main()
