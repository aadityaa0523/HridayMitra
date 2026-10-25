import {evaluate,type Inputs,type Result} from '../engine';
import demo from './demo.json';
import {Vault} from './vault';
export type CarePlan={source:'demo'|'clinician'|'transcribed';amber:string[];red:string[];dryWeightKg?:number|null;fluidLimitL?:number|null;saltAdvice?:string;followUp?:string;doctorName?:string;at?:string;effectiveDate?:string;versionId?:string};
export type Patient={id:string;name:string;synthetic:true;fixtureId:string;timeZone:'Asia/Kolkata';plan:CarePlan|null;phone?:string;village?:string;house?:string;phcPhone?:string;phcName?:string;sensitivity?:'standard'|'high'};
export type Checkin={id:string;patientId:string;date:string;source:'simulator'|'device';raw:Inputs;result:Result;deviceWhy?:string;deviceId?:string;extras?:{walk6_steps?:number;ref_ratio?:number}};
export type Cursor={id:'demo-cursor';patientId:string;index:number};
export type Snapshot={patient:Patient|null;patients:Patient[];checkins:Checkin[];cursor:number;auditCount:number};
export const blankSnapshot=():Snapshot=>({patient:null,patients:[],checkins:[],cursor:0,auditCount:0});
export async function snapshot(vault:Vault):Promise<Snapshot>{
 const patients=await vault.all<Patient>('patients'),checkins=await vault.all<Checkin>('checkins'),settings=await vault.all<Cursor>('settings'),audit=await vault.all('audit');
 const selected=settings.find(x=>x.id==='selected-patient' as string);
 const patient=patients.find(p=>p.id===selected?.patientId)??patients[0]??null,rows=checkins.filter(x=>x.patientId===patient?.id).sort((a,b)=>a.date.localeCompare(b.date));
 const saved=settings.find(x=>x.id==='demo-cursor'&&x.patientId===patient?.id);
 return {patient,patients,checkins:rows,cursor:Math.max(0,Math.min(rows.length-1,saved?.index??0)),auditCount:audit.length};
}
export async function seedDemo(vault:Vault){
 if((await vault.all<Patient>('patients')).length) return;
 const patient:Patient={id:'synthetic-patient-1',name:'Demo elder 01',synthetic:true,fixtureId:demo.id,timeZone:'Asia/Kolkata',plan:null};
 const inputs=demo.days.map(d=>d.input as Inputs),results=evaluate(inputs);
 const checkins:Checkin[]=demo.days.map((d,i)=>({id:'demo-day-'+d.date,patientId:patient.id,date:d.date,source:'simulator',raw:inputs[i],result:results[i]}));
 await vault.write([{kind:'patients',id:patient.id,value:patient},...checkins.map(row=>({kind:'checkins' as const,id:row.id,value:row})),{kind:'settings',id:'demo-cursor',value:{id:'demo-cursor',patientId:patient.id,index:Math.min(30,checkins.length-1)}}],'seed-demo',{fixtureId:demo.id,days:checkins.length},true);
}
export async function moveCursor(vault:Vault,state:Snapshot,index:number){
 if(!state.patient||!Number.isInteger(index)||index<0||index>=state.checkins.length)throw new Error('Invalid replay position');
 await vault.write([{kind:'settings',id:'demo-cursor',value:{id:'demo-cursor',patientId:state.patient.id,index}}],'replay-day',{patientId:state.patient.id,date:state.checkins[index].date});
}


export async function selectPatient(vault:Vault,id:string){
 if(!(await vault.all<Patient>('patients')).some(p=>p.id===id))throw new Error('Unknown patient');
 const cursor=(await vault.all<Cursor>('settings')).find(x=>x.id==='demo-cursor');
 await vault.write([{kind:'settings',id:'demo-cursor',value:{id:'demo-cursor',patientId:id,index:cursor?.index??0}},{kind:'settings',id:'selected-patient',value:{id:'selected-patient',patientId:id}}],'select-patient',{id});
}
export async function addDemoPatient(vault:Vault){
 const all=await vault.all<Patient>('patients');if(all.length>=4)throw new Error('Household limit');
 const number=all.length+1,id='synthetic-patient-'+number;
 const patient:Patient={id,name:'Demo elder 0'+number,synthetic:true,fixtureId:demo.id,timeZone:'Asia/Kolkata',plan:null};
 const inputs=demo.days.map(d=>d.input as Inputs),results=evaluate(inputs);
 await vault.write([{kind:'patients',id,value:patient},...demo.days.map((d,i)=>({kind:'checkins' as const,id:id+':'+d.date,value:{id:id+':'+d.date,patientId:id,date:d.date,source:'simulator',raw:inputs[i],result:results[i]}}))],'add-demo-elder',{id,sharedFixture:demo.id},true);
}
