import fixture from '../data/demo.json';
import {evaluate,type Inputs} from '../engine';
import {LineDecoder} from './protocol';
import type {Link} from './transport';
export type Scenario='stable'|'worsening'|'recovery';
export function simulator(wireId:string,scenario:()=>Scenario,onLine:(line:string)=>void):Link{
 const inputs=fixture.days.map(d=>d.input as Inputs),results=evaluate(inputs);let closed=false;
 const index=()=>scenario()==='stable'?30:scenario()==='worsening'?results.findIndex(r=>r.light===2):results.findIndex((r,i)=>i>results.findIndex(r=>r.light===2)&&r.light===0);
 const emit=(i:number)=>{const r=results[i],d=fixture.days[i],line=JSON.stringify({t:'checkin',id:wireId,date:d.date,event_id:'fixture:'+i,...d.input,light:r.light,S:r.S,learning:r.learning,guest:r.guest,plate:r.plate,why:r.reasons.map(x=>x.signal+' z='+x.z.toFixed(2)).join('; ')})+'\n',bytes=new TextEncoder().encode(line),decoder=new LineDecoder();for(let n=0;n<bytes.length;n+=180)for(const l of decoder.push(bytes.slice(n,n+180)))if(!closed)onLine(l);};
 return {kind:'simulator',send:async(text,isHistory)=>{if(closed)throw Error('Disconnected');if(isHistory){const {since}=JSON.parse(text);for(let i=0;i<=index();i++)if(fixture.days[i].date>=since)emit(i);}else if(text==='checkin')emit(index());else if(text==='selftest')onLine(JSON.stringify({t:'selftest',battery_mv:3950,signal:18,problems:'SIMULATED telemetry, not physical hardware'}));else throw Error('Unsupported simulator command');},close:async()=>{closed=true;}};
}
