/** Frozen v3 (v2 + leg spectroscopy index, T 7.0), CUSUM off. Reference: engine/alert_engine.py. */
export const ENGINE_VERSION='python-v3';
export const signals={
 weight_kg:['fluid',1,.30,false,1],leg_z_ohm:['fluid',-1,.010,true,1],
 trunk_z_ohm:['fluid',-1,3,false,.5],leg_ewi:['fluid',1,.003,true,1],pulse_bpm:['heart_lungs',1,2,false,1],
 night_rr:['heart_lungs',1,.7,false,1],spo2:['heart_lungs',-1,.7,false,.5],
 activity_min:['daily_life',-1,.08,true,1],standup_s:['daily_life',1,.04,true,1]
} as const;
export type Signal=keyof typeof signals;
export type Inputs=Record<Signal|'breathless'|'orthopnea'|'night_situps',number|null>;
export const signalNames=Object.keys(signals) as Signal[];
export const emptyInput=():Inputs=>Object.fromEntries([...signalNames,'breathless','orthopnea','night_situps'].map(s=>[s,null])) as Inputs;
export type Reason={signal:string;z:number;level?:number;baseline?:number};
export type Result={light:0|1|2;S:number;guest:boolean;learning:boolean;data:boolean;danger:boolean;plate:boolean;reasons:Reason[];gated:Inputs;families:Record<string,number>;threshold:number;engineVersion:string};
const median=(v:number[])=>{const a=[...v].sort((x,y)=>x-y);return a.length%2?a[a.length>>1]:(a[a.length/2-1]+a[a.length/2])/2;};
const numbers=(v:(number|null)[])=>v.filter((x):x is number=>x!==null);
const sum=(v:number[])=>v.reduce((a,b)=>a+b,0);
export function evaluate(history:Inputs[],threshold=7):Result[]{
 if(![7,6].includes(threshold))throw new Error('Unsupported threshold');
 for(const d of history)for(const k of Object.keys(emptyInput()) as (keyof Inputs)[]){
  const x=d[k];if(x!==null&&(typeof x!=='number'||!Number.isFinite(x)))throw new Error('Invalid reading');
  if(x!==null&&((k==='breathless'||k==='orthopnea')?![0,1].includes(x):x<0||(['weight_kg','leg_z_ohm','trunk_z_ohm','leg_ewi','standup_s'].includes(k)&&x===0)))throw new Error('Invalid reading');
 }
 const gated=history.map(d=>({...d})),guest=history.map(()=>false),plate=history.map(()=>false);
 // Use the last seven calendar rows, not the last seven non-null readings.
 gated.forEach((d,t)=>{
  const prev=numbers(gated.slice(Math.max(0,t-7),t).map(x=>x.weight_kg));
  if(d.weight_kg!==null&&prev.length>=3&&Math.abs(d.weight_kg-median(prev))>2.5){
   guest[t]=true;for(const k of ['weight_kg','leg_z_ohm','trunk_z_ohm','leg_ewi','pulse_bpm','spo2','standup_s'] as Signal[])d[k]=null;
  }
 });
 gated.forEach((d,t)=>{
  const prev=numbers(gated.slice(Math.max(0,t-7),t).map(x=>x.leg_z_ohm));
  if(d.leg_z_ohm!==null&&prev.length>=3&&Math.abs(d.leg_z_ohm/median(prev)-1)>.25){plate[t]=true;d.leg_z_ohm=null;d.trunk_z_ohm=null;d.leg_ewi=null;}
 });
 let red=false,last:0|1|2=0;const high:boolean[]=[],famHigh:boolean[]=[];
 return gated.map((d,t)=>{
  const z:Record<string,number>={},info:Record<string,{level:number;baseline:number}>={};
  for(const k of signalNames){
   const base=numbers(gated.slice(Math.max(0,t-35),Math.max(0,t-6)).map(x=>x[k]));
   const level=numbers(gated.slice(Math.max(0,t-2),t+1).map(x=>x[k]));
   if(base.length<6||!level.length)continue;
   const [,direction,floor,relative,weight]=signals[k],med=median(base);
   const spread=Math.max(1.4826*median(base.map(x=>Math.abs(x-med))),floor*(relative?Math.abs(med):1));
   const mean=sum(level)/level.length;
   z[k]=Math.min(5,Math.max(0,(mean-med)/spread*direction))*weight;
   info[k]={level:mean,baseline:med};
  }
  const learning=!signalNames.some(k=>k in z),window=gated.slice(Math.max(0,t-2),t+1);
  z.symptoms=1.2*Math.max(0,sum(window.map(x=>(x.breathless??0)+(x.orthopnea??0)))-1);
  const sit=numbers(window.map(x=>x.night_situps));if(sit.length)z.night_situps=Math.max(0,sum(sit)-1);
  const families:Record<string,number>={};
  for(const family of ['fluid','heart_lungs','daily_life']){
   const values=Object.entries(z).filter(([k])=>(k in signals?signals[k as Signal][0]:'daily_life')===family).map(([,v])=>v).sort((a,b)=>b-a);
   families[family]=(values[0]??0)+.5*(values[1]??0);
  }
  const S=sum(Object.values(families)),maxFam=Math.max(...Object.values(families)),nFam=Object.values(families).filter(x=>x>=1.5).length;
  const data=signalNames.some(k=>d[k]!==null)||d.breathless!==null||d.orthopnea!==null;
  const danger=!guest[t]&&history[t].spo2!==null&&history[t].spo2!<90;
  high.push(S>=threshold);famHigh.push(maxFam>=threshold);
  if(data){
   if(danger)red=true;else if(red)red=S>=.4*threshold;
   else red=(high.slice(-3).filter(Boolean).length>=2&&nFam>=2)||(famHigh.length>=3&&famHigh.slice(-3).every(Boolean));
   last=red?2:S>=.6*threshold?1:0;
  }
  const reasons=Object.entries(z).sort((a,b)=>b[1]-a[1]).slice(0,3).filter(([,v])=>v>=1).map(([signal,value])=>({signal,z:value,...info[signal]}));
  return {light:last,S,guest:guest[t],plate:plate[t],learning,data,danger,reasons,gated:{...d},families,threshold,engineVersion:ENGINE_VERSION};
 });
}

