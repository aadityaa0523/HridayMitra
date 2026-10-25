import {Vault,type Collection} from '../data/vault';
import type {Patient,Checkin,CarePlan} from '../data/model';
import {dayNumber,evaluateDaily} from '../engine/daily';
import type {FamilyData,ScheduledDose,Pending} from '../family/model';
import type {Visit} from '../asha/model';

export type PlanVersion={id:string;kind:'doctor-plan';patientId:string;date:string;at:string;doctorName:string;plan:CarePlan;previousPlan?:CarePlan|null};
export type SensitivityVersion={id:string;kind:'doctor-sensitivity';patientId:string;date:string;at:string;doctorName:string;value:'standard'|'high';previous:'standard'|'high';threshold:7|6};
export const labUnits={Na:['mmol/L'],K:['mmol/L'],Creatinine:['mg/dL','µmol/L'],eGFR:['mL/min/1.73m²'],NTproBNP:['pg/mL','ng/L'],Hb:['g/dL','g/L']} as const;
export type LabTest=keyof typeof labUnits;
export type Lab={id:string;patientId:string;date:string;at:string;test:LabTest;value:number;unit:string;doctorName:string};
export type ConsultNote={id:string;patientId:string;date:string;at:string;text:string;doctorName:string};
export type AuditRecord={id:string;at:string;actor:string;action:string;details?:{patientId?:string;date?:string;checkinId?:string;response?:1|2|3;visitId?:string}};
export type DoctorData={plans:PlanVersion[];sensitivities:SensitivityVersion[];labs:Lab[];notes:ConsultNote[];audit:AuditRecord[]};
export const emptyDoctor=():DoctorData=>({plans:[],sensitivities:[],labs:[],notes:[],audit:[]});
export async function loadDoctor(v:Vault):Promise<DoctorData>{
 const [settings,labs,notes,audit]=await Promise.all([v.all<PlanVersion|SensitivityVersion>('settings'),v.all<Lab>('labs'),v.all<ConsultNote>('notes'),v.all<AuditRecord>('audit')]);
 return {plans:settings.filter((s):s is PlanVersion=>s.kind==='doctor-plan'),sensitivities:settings.filter((s):s is SensitivityVersion=>s.kind==='doctor-sensitivity'),labs,notes,audit};
}
export function asOfPatient(p:Patient,data:DoctorData,date:string):Patient{
 const plans=data.plans.filter(x=>x.patientId===p.id),versions=plans.filter(x=>x.date<=date).sort((a,b)=>b.date.localeCompare(a.date)||b.at.localeCompare(a.at));
 const sensitivities=data.sensitivities.filter(x=>x.patientId===p.id),s=sensitivities.filter(x=>x.date<=date).sort((a,b)=>b.date.localeCompare(a.date)||b.at.localeCompare(a.at))[0];
 return {...p,plan:versions[0]?.plan??(plans.length&&p.plan?.source==='clinician'?[...plans].sort((a,b)=>a.at.localeCompare(b.at))[0].previousPlan??null:p.plan),sensitivity:s?.value??(sensitivities.length?'standard':p.sensitivity??'standard')};
}
export const thresholdFor=(p:Patient)=>p.sensitivity==='high'?6:7;
function author(name:string){if(!name.trim()||name.length>80)throw new Error('Doctor name required');return name.trim();}
async function patient(v:Vault,id:string){const p=(await v.all<Patient>('patients')).find(p=>p.id===id);if(!p)throw new Error('Unknown patient');return p;}
function dateBefore(date:string,cutoff:string){if(dayNumber(date)>dayNumber(cutoff))throw new Error('Future entry');}
export async function savePlan(v:Vault,patientId:string,date:string,doctorName:string,input:{amber:string;red:string;dryWeightKg:number|null;fluidLimitL:number|null;saltAdvice:string;followUp:string}){
 const p=await patient(v,patientId),name=author(doctorName);dayNumber(date);
 if(!input.amber.trim()||!input.red.trim()||input.amber.length>2000||input.red.length>2000||input.saltAdvice.length>800||input.dryWeightKg!==null&&(!Number.isFinite(input.dryWeightKg)||input.dryWeightKg<10||input.dryWeightKg>300)||input.fluidLimitL!==null&&(!Number.isFinite(input.fluidLimitL)||input.fluidLimitL<=0||input.fluidLimitL>20))throw new Error('Invalid plan');
 if(input.followUp&&dayNumber(input.followUp)<dayNumber(date))throw new Error('Follow-up before plan');
 const id=crypto.randomUUID(),at=new Date().toISOString(),lines=(s:string)=>[...new Set(s.split('\n').map(x=>x.trim()).filter(Boolean))];
 const plan:CarePlan={source:'clinician',amber:lines(input.amber),red:lines(input.red),dryWeightKg:input.dryWeightKg,fluidLimitL:input.fluidLimitL,saltAdvice:input.saltAdvice.trim(),followUp:input.followUp||undefined,doctorName:name,at,effectiveDate:date,versionId:id};
 const version:PlanVersion={id,kind:'doctor-plan',patientId,date,at,doctorName:name,plan,previousPlan:p.plan};
 await v.write([{kind:'patients',id:p.id,value:{...p,plan}},{kind:'settings',id,value:version},{kind:'outbox',id:'plan:'+id,value:{id:'plan:'+id,patientId,date,type:'doctor-plan',versionId:id,status:'pending',delivery:'not-sent'}}],'doctor-plan-saved',{patientId,date,versionId:id},false,name);
}
export async function setSensitivity(v:Vault,patientId:string,date:string,doctorName:string,value:'standard'|'high'){
 const p=await patient(v,patientId),name=author(doctorName);dayNumber(date);if(!['standard','high'].includes(value))throw new Error('Invalid sensitivity');
 const current=asOfPatient(p,await loadDoctor(v),date);if((current.sensitivity??'standard')===value)return;
 const id=crypto.randomUUID(),version:SensitivityVersion={id,kind:'doctor-sensitivity',patientId,date,at:new Date().toISOString(),doctorName:name,value,previous:current.sensitivity??'standard',threshold:value==='high'?6:7};
 await v.write([{kind:'patients',id:p.id,value:{...p,sensitivity:value}},{kind:'settings',id,value:version},{kind:'outbox',id:'sensitivity:'+id,value:{id:'sensitivity:'+id,patientId,date,type:'sensitivity-update',threshold:version.threshold,status:'pending',delivery:'not-sent'}}],'doctor-sensitivity-changed',{patientId,date,from:version.previous,to:value,threshold:version.threshold},false,name);
}
export function sensitivityPreview(rows:Checkin[],date:string,threshold:number){
 return evaluateDaily(rows.filter(r=>r.date<=date).map(r=>({patientId:r.patientId,eventId:r.id,date:r.date,input:r.raw,source:'manual' as const})),threshold).at(-1)?.result;
}
export async function saveLab(v:Vault,patientId:string,cutoff:string,doctorName:string,input:{id:string;date:string;test:LabTest;value:number;unit:string}){
 await patient(v,patientId);const name=author(doctorName);dateBefore(input.date,cutoff);
 if(!input.id||input.id.length>100||!(input.test in labUnits)||!(labUnits[input.test] as readonly string[]).includes(input.unit)||!Number.isFinite(input.value)||input.value<0||input.value>1e9)throw new Error('Invalid lab');
 const existing=(await v.all<Lab>('labs')).find(x=>x.id===input.id);if(existing){if(existing.patientId!==patientId)throw new Error('Wrong patient');return;}
 const value:Lab={...input,patientId,doctorName:name,at:new Date().toISOString()};await v.write([{kind:'labs',id:value.id,value}],'doctor-lab-added',{patientId,date:input.date,test:input.test},true,name);
}
export async function saveNote(v:Vault,patientId:string,cutoff:string,doctorName:string,input:{id:string;date:string;text:string}){
 await patient(v,patientId);const name=author(doctorName);dateBefore(input.date,cutoff);if(!input.id||input.id.length>100||!input.text.trim()||input.text.length>4000)throw new Error('Invalid note');
 const existing=(await v.all<ConsultNote>('notes')).find(x=>x.id===input.id);if(existing){if(existing.patientId!==patientId)throw new Error('Wrong patient');return;}
 const value:ConsultNote={...input,text:input.text.trim(),patientId,doctorName:name,at:new Date().toISOString()};await v.write([{kind:'notes',id:value.id,value}],'doctor-note-added',{patientId,date:input.date},true,name);
}
export async function assignPHC(v:Vault,patientId:string,date:string,doctorName:string,phcName:string,phone:string){
 const p=await patient(v,patientId),name=author(doctorName);dayNumber(date);if(phcName.length>100||phone&&!/^\+?[0-9]{7,15}$/.test(phone))throw new Error('Invalid PHC');
 await v.write([{kind:'patients',id:p.id,value:{...p,phcName:phcName.trim(),phcPhone:phone||undefined}}],'doctor-phc-assigned',{patientId,date,phcName:phcName.trim()},false,name);
}
export type TimelineItem={id:string;date:string;at?:string;kind:'checkin'|'alert'|'response'|'visit'|'dose'|'lab'|'note'|'plan'|'sensitivity'|'delivery';actor?:string;medicineName?:string;row?:Checkin;visit?:Visit;dose?:ScheduledDose;lab?:Lab;note?:ConsultNote;plan?:PlanVersion;sensitivity?:SensitivityVersion;pending?:Pending;response?:number};
export function timeline(data:FamilyData,doctor:DoctorData,visits:Visit[],patientId:string,date:string):TimelineItem[]{
 const items:TimelineItem[]=[],rows=data.rows.filter(r=>r.patientId===patientId&&r.date<=date);
 for(const row of rows){items.push({id:'checkin:'+row.id,date:row.date,kind:'checkin',row});if(row.result.data&&row.result.light>0)items.push({id:'alert:'+row.id,date:row.date,kind:'alert',row});}
 for(const v of visits.filter(v=>v.patientId===patientId&&v.date<=date))items.push({id:'visit:'+v.id,date:v.date,at:v.at,kind:'visit',actor:'ASHA demo',visit:v});
 for(const d of data.doses.filter(d=>d.patientId===patientId&&d.date<=date&&d.state!=='pending'))items.push({id:d.id,date:d.date,at:d.takenAt,kind:'dose',actor:d.source,medicineName:data.medicines.find(m=>m.id===d.medicineId)?.name,dose:d});
 for(const lab of doctor.labs.filter(l=>l.patientId===patientId&&l.date<=date))items.push({id:lab.id,date:lab.date,at:lab.at,kind:'lab',actor:lab.doctorName,lab});
 for(const note of doctor.notes.filter(l=>l.patientId===patientId&&l.date<=date))items.push({id:note.id,date:note.date,at:note.at,kind:'note',actor:note.doctorName,note});
 for(const plan of doctor.plans.filter(l=>l.patientId===patientId&&l.date<=date))items.push({id:plan.id,date:plan.date,at:plan.at,kind:'plan',actor:plan.doctorName,plan});
 for(const sensitivity of doctor.sensitivities.filter(l=>l.patientId===patientId&&l.date<=date))items.push({id:sensitivity.id,date:sensitivity.date,at:sensitivity.at,kind:'sensitivity',actor:sensitivity.doctorName,sensitivity});
 for(const a of doctor.audit.filter(a=>a.action==='family-alert-response'&&a.details?.patientId===patientId)){const r=rows.find(r=>r.id===a.details?.checkinId);if(r)items.push({id:a.id,date:r.date,at:a.at,kind:'response',actor:a.actor,response:a.details?.response});}
 for(const pending of data.pending.filter(x=>x.patientId===patientId&&x.date<=date))items.push({id:pending.id,date:pending.date,kind:'delivery',pending});
 return items.sort((a,b)=>b.date.localeCompare(a.date)||(b.at??'').localeCompare(a.at??'')||a.id.localeCompare(b.id));
}
