"""Create immutable app fixtures from the Python reference, never from the TS port."""
import sys,json,hashlib,datetime
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'engine'))
import alert_engine as A
cols=list(A.SIGNALS)+['breathless','orthopnea','night_situps']
def pack(pid,g):
    g=g.reset_index(drop=True)
    sc=A.scores(g)
    standard=A.lights(sc,7.0); sensitive=A.lights(sc,6.0)
    days=[]
    for i,row in g.iterrows():
        days.append(dict(date=(datetime.date(2026,1,1)+datetime.timedelta(days=i)).isoformat(),
            input={k:None if pd.isna(row[k]) else float(row[k]) for k in cols},
            expected=dict(light=int(standard[i]),sensitiveLight=int(sensitive[i]),S=float(sc[i]['S']),
                          guest=bool(sc[i]['guest']),learning=bool(sc[i]['learning']),data=bool(sc[i]['data']))))
    return dict(id=pid,days=days)
df=pd.read_csv(ROOT/'data/processed/daily_features.csv')
reference_patients=[pack(pid,df[df.patient_id==pid]) for pid in df.patient_id.unique()[:5]]
patients=[]
rng=np.random.default_rng(20261025)
for n in range(5):
    rows=[]
    for day in range(164):
        drift=max(0,1-abs(day-49)/9)+max(0,1-abs(day-109)/9)
        row=dict(weight_kg=60+n*4+rng.normal(0,.08)+1.8*drift,
          leg_z_ohm=500+n*10+rng.normal(0,1)-35*drift,
          trunk_z_ohm=30+rng.normal(0,.2)-4*drift,
          leg_ewi=0.69+n*0.005+rng.normal(0,.0007)+0.02*drift,
          pulse_bpm=70+n+rng.normal(0,.5)+12*drift,
          night_rr=16+rng.normal(0,.1)+3*drift,
          spo2=97+rng.normal(0,.1)-2*drift,
          activity_min=200+rng.normal(0,3)-80*drift,
          standup_s=3+rng.normal(0,.02)+.6*drift,
          breathless=int(drift>.55),orthopnea=int(drift>.75),night_situps=2 if drift>.6 else 0)
        if day in [18,19,72]: row={k:np.nan for k in row}
        if day==135: row['weight_kg']+=10
        if day==139: row['leg_z_ohm']*=1.6
        rows.append(row)
    patients.append(pack('DEMO%02d'%(n+1),pd.DataFrame(rows)))
base=dict(weight_kg=60,leg_z_ohm=500,trunk_z_ohm=30,leg_ewi=0.69,pulse_bpm=70,night_rr=16,spo2=97,activity_min=200,standup_s=3,breathless=0,orthopnea=0,night_situps=0)
cases=[]
for name in ['danger_recovery','guest_and_plate','missing_days','persistent_family','symptoms']:
    rows=[dict(base) for _ in range(55)]
    if name=='danger_recovery':
        rows[20]['spo2']=88
        rows[21]={k:np.nan for k in base}
    if name=='guest_and_plate':
        rows[20]['weight_kg']=70;rows[20]['spo2']=85
        rows[22]['leg_z_ohm']=800
    if name=='missing_days':
        for i in range(12,20): rows[i]={k:np.nan for k in base}
        rows[20]['weight_kg']=70
    if name=='persistent_family':
        for i in range(20,26): rows[i]['weight_kg']=62;rows[i]['leg_z_ohm']=470
    if name=='symptoms':
        for i in range(20,24): rows[i]['breathless']=1;rows[i]['orthopnea']=1;rows[i]['night_situps']=3
    cases.append(pack(name,pd.DataFrame(rows)))
out=dict(provenance=dict(reference='engine/alert_engine.py',referenceSha256=hashlib.sha256((ROOT/'engine/alert_engine.py').read_bytes()).hexdigest(),dataSha256=hashlib.sha256((ROOT/'data/processed/daily_features.csv').read_bytes()).hexdigest(),generator='app/tools/generate_vectors.py',note='Locally generated fixture; not the missing author-supplied fixture. Synthetic inputs only.',thresholds=[7.0,6.0],syntheticSeed=20261025,syntheticDescription='Five generated 164-day demonstration histories; original CSV histories retained separately as referencePatients'),patients=patients,cases=cases,referencePatients=reference_patients)
p=ROOT/'docs/app/engine_test_vectors.json';p.parent.mkdir(parents=True,exist_ok=True)
p.write_text(json.dumps(out,ensure_ascii=False,allow_nan=False,separators=(',',':')),encoding='utf8')
# Bundle only one synthetic history; expected outcomes are not used by the app.
seed=dict(id=patients[0]['id'],days=[dict(date=d['date'],input=d['input']) for d in patients[0]['days']])
p=ROOT/'app/src/data/demo.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(seed,separators=(',',':')),encoding='utf8')
print(f"Generated {sum(len(p['days']) for p in patients)} patient-days + {sum(len(p['days']) for p in cases)} edge-case days")

