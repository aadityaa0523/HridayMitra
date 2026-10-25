import {Vault,type Collection} from '../data/vault';
import type {Patient,Checkin} from '../data/model';
import {dayShift,windowRows,applicable,type FamilyData,type FamilyAlert} from '../family/model';

export type Visit={id:string;patientId:string;date:string;at:string;bpSys:number|null;bpDia:number|null;weight:number|null;edema:0|1|2|3;breathlessRest:boolean;pillows:boolean;medicinesSeen:Record<string,boolean>;photo?:string;notes:string;outcome:'fine'|'advised'|'referred'|'called108';referralReason:string;checkinId?:string};
export type VisitInput=Omit<Visit,'at'|'checkinId'>;
export type DraftFields={sys:string;dia:string;weight:string;edema:string;breath:string;pillows:string;seen:Record<string,boolean>;notes:string;outcome:string;reason:string;photo?:string};
export type VisitDraft={id:string;kind:'visit-draft';patientId:string;date:string;visitId:string;fields:DraftFields;cleared?:boolean};
export type ReviewedExample={id:string;kind:'edema-example';grade:0|1|2|3;photo:string;reviewedBy:string;source:string;at:string;removed?:boolean};
export type AshaData={visits:Visit[];drafts:VisitDraft[];examples:ReviewedExample[]};
export const emptyAsha=():AshaData=>({visits:[],drafts:[],examples:[]});
export async function loadAsha(v:Vault):Promise<AshaData>{const settings=await v.all<VisitDraft|ReviewedExample>('settings');return {visits:await v.all<Visit>('visits'),drafts:settings.filter((s):s is VisitDraft=>s.kind==='visit-draft'&&!s.cleared),examples:settings.filter((s):s is ReviewedExample=>s.kind==='edema-example'&&!s.removed)};}
export async function saveDraft(v:Vault,patientId:string,date:string,visitId:string,fields:DraftFields){
 if(!(await v.all<Patient>('patients')).some(p=>p.id===patientId)||!/^\d{4}-\d{2}-\d{2}$/.test(date)||!visitId||visitId.length>100||fields.notes.length>3000||fields.reason.length>600||Object.values(fields).some(x=>typeof x==='string'&&x.length>800000)||fields.photo&&(!/^data:image\/(jpeg|png|webp);base64,/.test(fields.photo)||fields.photo.length>800000))throw new Error('Invalid draft');
 const id='visit-draft:'+patientId+':'+date;await v.write([{kind:'settings',id,value:{id,kind:'visit-draft',patientId,date,visitId,fields}}],'asha-draft-saved',{patientId,date});
}
export async function saveExample(v:Vault,grade:0|1|2|3,photo:string,reviewedBy:string,source:string){
 if(![0,1,2,3].includes(grade)||!reviewedBy.trim()||reviewedBy.length>80||!source.trim()||source.length>300||!/^data:image\/(jpeg|png|webp);base64,/.test(photo)||photo.length>800000)throw new Error('Invalid example');
 const id='edema-example:'+grade;await v.write([{kind:'settings',id,value:{id,kind:'edema-example',grade,photo,reviewedBy:reviewedBy.trim(),source:source.trim(),at:new Date().toISOString()}}],'edema-example-reviewed',{grade,source,reviewedBy},false,reviewedBy.trim());
}
export async function removeExample(v:Vault,grade:0|1|2|3,reviewedBy:string){
 if(![0,1,2,3].includes(grade)||!reviewedBy.trim()||reviewedBy.length>80)throw new Error('Invalid review');const id='edema-example:'+grade;
 await v.write([{kind:'settings',id,value:{id,kind:'edema-example',removed:true}}],'edema-example-removed',{grade},false,reviewedBy.trim());
}
export function latestRow(rows:Checkin[],id:string,date:string){return rows.filter(r=>r.patientId===id&&r.date<=date&&r.result.data&&!r.result.guest).sort((a,b)=>b.date.localeCompare(a.date))[0];}
export function daysBetween(a:string,b:string){return Math.round((Date.parse(b+'T12:00:00Z')-Date.parse(a+'T12:00:00Z'))/86400000);}
export function todayList(data:FamilyData,visits:Visit[],date:string,village=''){
 return data.patients.filter(p=>!village||(p.village??'')===(village==='__unknown'?'':village)).map(p=>{
  const row=latestRow(data.rows,p.id,date),gap=row?daysBetween(row.date,date):null;
  const visit=visits.filter(v=>v.patientId===p.id&&v.date<=date).sort((a,b)=>b.date.localeCompare(a.date)||b.at.localeCompare(a.at))[0];
  const priority=row?.result.light===2?0:row?.result.light===1?1:gap===null||gap>1?2:3;
  return {patient:p,row,gap,visit,priority};
 }).sort((a,b)=>a.priority-b.priority||a.patient.name.localeCompare(b.patient.name));
}
export function weeklySummary(data:FamilyData,visits:Visit[],date:string,village=''){
 const ids=new Set(data.patients.filter(p=>!village||(p.village??'')===(village==='__unknown'?'':village)).map(p=>p.id));
 const start=dayShift(date,-6),week=visits.filter(v=>ids.has(v.patientId)&&v.date>=start&&v.date<=date);
 const reds=data.rows.filter(r=>ids.has(r.patientId)&&r.date>=start&&r.date<=date&&r.result.data&&!r.result.guest&&r.result.light===2);
 return {start,end:date,visits:week.length,eldersVisited:new Set(week.map(v=>v.patientId)).size,reds:reds.length,redElders:new Set(reds.map(r=>r.patientId)).size,referrals:week.filter(v=>v.outcome==='referred').length,called108:week.filter(v=>v.outcome==='called108').length};
}
export function readingSummary(rows:Checkin[],date:string){
 const past=windowRows(rows,date,30).filter(r=>r.result.data&&!r.result.guest);
 return {days:past.length,reds:past.filter(r=>r.result.light===2).length,amber:past.filter(r=>r.result.light===1).length,latest:past.at(-1),ranges:Object.fromEntries((['weight_kg','pulse_bpm','spo2','night_rr','leg_z_ohm'] as const).map(k=>{const values=past.map(r=>r.result.gated[k]).filter((x):x is number=>x!==null);return [k,values.length?{min:Math.min(...values),max:Math.max(...values)}:null];}))};
}
export async function saveLocation(v:Vault,patientId:string,village:string,house:string,phcPhone:string){
 const p=(await v.all<Patient>('patients')).find(x=>x.id===patientId);
 if(!p||village.length>100||house.length>100||(phcPhone&&!/^\+?[0-9]{7,15}$/.test(phcPhone)))throw new Error('Invalid location');
 await v.write([{kind:'patients',id:p.id,value:{...p,village:village.trim(),house:house.trim(),phcPhone:phcPhone||undefined}}],'asha-location',{patientId});
}
export async function saveVisit(v:Vault,input:VisitInput){
 if(!input.id||input.id.length>100||!/^\d{4}-\d{2}-\d{2}$/.test(input.date)||new Date(input.date+'T12:00:00Z').toISOString().slice(0,10)!==input.date)throw new Error('Invalid visit');
 const p=(await v.all<Patient>('patients')).find(x=>x.id===input.patientId);if(!p)throw new Error('Unknown patient');
 const prior=(await v.all<Visit>('visits')).find(x=>x.id===input.id);if(prior){if(prior.patientId!==input.patientId)throw new Error('Wrong patient');return;}
 const numeric=(x:number|null,min:number,max:number)=>x===null||Number.isFinite(x)&&x>=min&&x<=max;
 if(!numeric(input.bpSys,50,300)||!numeric(input.bpDia,30,200)||(input.bpSys===null)!==(input.bpDia===null)||(input.bpSys!==null&&input.bpDia!==null&&input.bpSys<=input.bpDia)||!numeric(input.weight,10,300)||![0,1,2,3].includes(input.edema)||typeof input.breathlessRest!=='boolean'||typeof input.pillows!=='boolean'||!['fine','advised','referred','called108'].includes(input.outcome)||input.notes.length>3000||input.referralReason.length>600||(input.outcome==='referred'&&!input.referralReason.trim()))throw new Error('Invalid observations');
 if(input.photo&&(!/^data:image\/(jpeg|png|webp);base64,/.test(input.photo)||input.photo.length>800000))throw new Error('Invalid photo');
 const medicines=(await v.all<{id:string;patientId:string;startDate:string;endDate?:string}>('medicines')).filter(m=>m.patientId===p.id&&applicable(m as Parameters<typeof applicable>[0],input.date));
 if(Object.keys(input.medicinesSeen).length!==medicines.length||medicines.some(m=>typeof input.medicinesSeen[m.id]!=='boolean')||Object.keys(input.medicinesSeen).some(id=>!medicines.some(m=>m.id===id)))throw new Error('Check each medicine');
 const row=latestRow(await v.all<Checkin>('checkins'),p.id,input.date),at=new Date().toISOString();
 const value:Visit={...input,at,notes:input.notes.trim(),referralReason:input.referralReason.trim(),checkinId:row?.id};
 const draftId='visit-draft:'+p.id+':'+input.date;
 const entries:{kind:Collection;id:string;value:unknown}[]=[{kind:'visits',id:value.id,value},{kind:'settings',id:draftId,value:{id:draftId,kind:'visit-draft',cleared:true}}];
 if(row&&row.result.light>0){
  const id='alert:'+row.id,old=(await v.all<FamilyAlert>('alerts')).find(a=>a.id===id);
  entries.push({kind:'alerts',id,value:{...old,id,patientId:p.id,checkinId:row.id,date:row.date,light:row.result.light,checked:old?.checked??[],seenByAsha:{visitId:value.id,at,date:input.date},escalation:'stopped-local'}});
  const pending='asha-seen:'+row.id;entries.push({kind:'outbox',id:pending,value:{id:pending,patientId:p.id,date:input.date,type:'asha-seen',status:'pending',delivery:'not-sent',visitId:value.id,instruction:'stop-escalation'}});
 }
 await v.write(entries,'asha-visit-saved',{patientId:p.id,visitId:value.id,outcome:value.outcome});
}
export async function recordExport(v:Vault,patientId:string,date:string,type:'referral'|'weekly',sha256:string,channel:'pdf'|'qr'|'sms'='pdf'){
 if(!(await v.all<Patient>('patients')).some(p=>p.id===patientId))throw new Error('Unknown patient');
 if(!/^[a-f0-9]{64}$/.test(sha256))throw new Error('Invalid report hash');
 const id=crypto.randomUUID();await v.write([{kind:'reports',id,value:{id,patientId,date,type,sha256,createdAt:new Date().toISOString(),source:'synthetic-demo',storage:'metadata-only',channel}}],'asha-report-generated',{patientId,date,type,sha256,channel});
}
