import {emptyInput,evaluate,type Inputs,type Result} from './index';
export type Reading={patientId:string;eventId:string;date:string;input:Inputs;source:'manual'|'asha'|'device';deviceResult?:Result};
export function dayNumber(date:string):number{
 if(!/^\d{4}-\d{2}-\d{2}$/.test(date))throw new Error('Invalid date');
 const time=Date.parse(date+'T00:00:00Z');
 if(!Number.isFinite(time)||new Date(time).toISOString().slice(0,10)!==date)throw new Error('Invalid date');
 return time/86400000;
}
export function dailyHistory(readings:Reading[]):{date:string;input:Inputs;record?:Reading}[]{
 if(!readings.length)return [];
 if(new Set(readings.map(x=>x.patientId)).size!==1)throw new Error('Mixed patients');
 const days=new Map<string,Reading>(),events=new Map<string,string>();
 for(const record of readings){
  dayNumber(record.date);
  if(events.has(record.eventId)){
   if(events.get(record.eventId)!==JSON.stringify(record))throw new Error('Conflicting event');
   continue;
  }
  events.set(record.eventId,JSON.stringify(record));
  if(days.has(record.date))throw new Error('Explicit same-day correction required');
  days.set(record.date,record);
 }
 const sorted=[...days.keys()].sort(),start=dayNumber(sorted[0]),end=dayNumber(sorted.at(-1)!);
 if(end-start>3660)throw new Error('History too long');
 return Array.from({length:end-start+1},(_,i)=>{
  const date=new Date((start+i)*86400000).toISOString().slice(0,10),record=days.get(date);
  return {date,input:record?.input??emptyInput(),record};
 });
}
export function evaluateDaily(readings:Reading[],threshold=7){
 const rows=dailyHistory(readings),results=evaluate(rows.map(x=>x.input),threshold);
 return rows.map((row,i)=>{
  if(row.record?.source==='device'&&!row.record.deviceResult)throw new Error('Device result required');
  return {...row,result:row.record?.source==='device'?row.record.deviceResult!:results[i]};
 });
}

