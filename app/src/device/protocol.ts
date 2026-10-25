import {emptyInput,signalNames,type Inputs,type Result} from '../engine';
import {dayNumber} from '../engine/daily';
export const UUID={service:'6e8a0001-4b5a-4c3e-9a51-6d697472a001',reports:'6e8a0001-4b5a-4c3e-9a51-6d697472a002',history:'6e8a0001-4b5a-4c3e-9a51-6d697472a003',commands:'6e8a0001-4b5a-4c3e-9a51-6d697472a004',status:'6e8a0001-4b5a-4c3e-9a51-6d697472a005'};
export type Extras={walk6_steps?:number;ref_ratio?:number};
export type Packet={t:'checkin';id:string;date?:string;event_id?:string;raw:Inputs;result:Result;why:string;extras?:Extras};
export type Status={t:'selftest'|'status';battery_mv:number|null;signal:number|null;problems:string;light?:number;learning?:boolean};
export type Message=Packet|Status|{t:'ack';command:string;ok:boolean}|{t:'info';text:string};
const flag=(x:unknown)=>{if(x!==0&&x!==1&&typeof x!=='boolean')throw Error('Invalid flag');return Boolean(x);};
const text=(x:unknown,max:number)=>{if(typeof x!=='string'||x.length>max)throw Error('Invalid text');return x;};
export function parseLine(line:string):Message{
 if(new TextEncoder().encode(line).length>8192)throw Error('Oversized line');
 // Only repair bare firmware nan tokens in value position, never within strings.
 const normalized=line.replace(/"(?:\\.|[^"\\])*"|:\s*-?nan(?=\s*[,}])/g,x=>x.startsWith('"')?x:':null');
 const o=JSON.parse(normalized);if(!o||typeof o!=='object'||Array.isArray(o))throw Error('Invalid packet');
 if(o.t==='checkin'){
  const id=text(o.id,64);if(!/^[\w.-]{1,64}$/.test(id))throw Error('Invalid device patient ID');
  if(o.date!==undefined)dayNumber(o.date);if(o.event_id!==undefined)text(o.event_id,100);
  const raw=emptyInput();for(const k of Object.keys(raw) as (keyof Inputs)[]){const v=o[k]??null;if(v!==null&&(typeof v!=='number'||!Number.isFinite(v)||v<0||v>1e7))throw Error('Invalid measurement');if(v!==null&&['breathless','orthopnea'].includes(k)&&v!==0&&v!==1)throw Error('Invalid symptom');if(v===0&&['weight_kg','leg_z_ohm','trunk_z_ohm','leg_ewi','standup_s'].includes(k))throw Error('Invalid zero');raw[k]=v;}
  if(![0,1,2].includes(o.light)||typeof o.S!=='number'||!Number.isFinite(o.S)||o.S<0||o.S>100)throw Error('Invalid result');
  const guest=flag(o.guest),learning=flag(o.learning),plate=o.plate===undefined?false:flag(o.plate),gated={...raw};
  if(guest)for(const k of ['weight_kg','leg_z_ohm','trunk_z_ohm','leg_ewi','pulse_bpm','spo2','standup_s'] as const)gated[k]=null;
  if(plate){gated.leg_z_ohm=null;gated.trunk_z_ohm=null;gated.leg_ewi=null;}
  const extras:Extras={};for(const [k,max] of [['walk6_steps',5000],['ref_ratio',100]] as const){const v=o[k];if(v===undefined||v===null)continue;if(typeof v!=='number'||!Number.isFinite(v)||v<0||v>max)throw Error('Invalid device field');extras[k]=v;}
  return {t:'checkin',id,...(o.date?{date:o.date}:{}),...(o.event_id?{event_id:o.event_id}:{}),...(Object.keys(extras).length?{extras}:{}),raw,why:text(o.why??'',500),result:{light:o.light,S:o.S,guest,learning,plate,gated,data:signalNames.some(k=>gated[k]!==null)||gated.breathless!==null||gated.orthopnea!==null,danger:!guest&&raw.spo2!==null&&raw.spo2<90,reasons:[],families:{},threshold:7,engineVersion:'device-reported-unverified'}};
 }
 if(o.t==='selftest'||o.t==='status'||(o.battery_mv!==undefined&&o.t===undefined)){
  const number=(v:unknown,min:number,max:number)=>{if(v===null||v===undefined||v===-1)return null;if(typeof v!=='number'||!Number.isInteger(v)||v<min||v>max)throw Error('Invalid telemetry');return v;};
  return {t:o.t==='selftest'?'selftest':'status',battery_mv:number(o.battery_mv,0,6000),signal:number(o.signal,0,99),problems:text(o.problems??o.selftest??'',500),...(o.light!==undefined?{light:number(o.light,0,2)!}:{}),...(o.learning!==undefined?{learning:flag(o.learning)}:{})};
 }
 if(o.t==='ack')return {t:'ack',command:text(o.command,40),ok:flag(o.ok)};
 if(['ready','ok','sms','reply','error'].includes(o.t))return {t:'info',text:JSON.stringify(o).slice(0,500)};
 throw Error('Unknown message');
}
export class LineDecoder{
 private decoder=new TextDecoder('utf-8',{fatal:true});private buffer='';
 push(bytes:Uint8Array):string[]{
  try{this.buffer+=this.decoder.decode(bytes,{stream:true});const lines=this.buffer.split('\n');this.buffer=lines.pop()!;if(this.buffer.length>8192||lines.some(l=>new TextEncoder().encode(l).length>8192))throw Error('Oversized stream');return lines.map(l=>l.trim()).filter(Boolean);}catch(e){this.buffer='';this.decoder=new TextDecoder('utf-8',{fatal:true});throw e;}
 }
}
export function command(value:'checkin'|'selftest'|{since:string}){if(typeof value==='string')return value;if(dayNumber(value.since)<0)throw Error('Invalid history date');return JSON.stringify(value);}

