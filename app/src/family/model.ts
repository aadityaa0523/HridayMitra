import {Vault,type Collection} from '../data/vault';
import type {Checkin,Patient} from '../data/model';
export type Medicine={id:string;patientId:string;name:string;strength:string;times:string[];food:'before'|'after'|'any';units:number;stock:number;photo?:string;prescription?:string;active:boolean;startDate:string;endDate?:string};
export type ScheduledDose={id:string;kind:'scheduled';patientId:string;medicineId:string;date:string;time:string;state:'pending'|'taken'|'missed';snoozes:number;dueAt:number|null;takenAt?:string;source?:'tap'|'voice';units:number};
export type FamilyAlert={id:string;patientId:string;checkinId:string;date:string;light:1|2;response?:1|2|3;respondedAt?:string;checked:string[];seenByAsha?:{visitId:string;at:string;date:string};escalation?:'stopped-local'};
export type Pending={id:string;patientId:string;date:string;type:string;status:'pending';delivery:'not-sent';digit?:number};
export type FamilyData={patients:Patient[];rows:Checkin[];medicines:Medicine[];doses:ScheduledDose[];alerts:FamilyAlert[];pending:Pending[]};
export const emptyFamily=():FamilyData=>({patients:[],rows:[],medicines:[],doses:[],alerts:[],pending:[]});
export async function loadFamily(v:Vault):Promise<FamilyData>{
 const [patients,rows,medicines,doses,alerts,pending]=await Promise.all([v.all<Patient>('patients'),v.all<Checkin>('checkins'),v.all<Medicine>('medicines'),v.all<ScheduledDose>('doses'),v.all<FamilyAlert>('alerts'),v.all<Pending>('outbox')]);
 return {patients,rows,medicines,doses:doses.filter(d=>d.kind==='scheduled'),alerts,pending};
}
export const dayShift=(date:string,n:number)=>new Date(Date.parse(date+'T12:00:00Z')+n*86400000).toISOString().slice(0,10);
export function windowRows(rows:Checkin[],date:string,days:number){return rows.filter(r=>r.date<=date&&r.date>=dayShift(date,1-days)).sort((a,b)=>a.date.localeCompare(b.date));}
export function streak(rows:Checkin[],date:string){const days=new Set(rows.filter(r=>r.result.data&&!r.result.guest).map(r=>r.date));let n=0;while(days.has(dayShift(date,-n)))n++;return n;}
export function applicable(m:Medicine,date:string){return m.startDate<=date&&(!m.endDate||date<m.endDate);}
export function scheduled(m:Medicine,date:string):ScheduledDose[]{return applicable(m,date)?m.times.map(time=>({id:'dose:'+m.id+':'+date+':'+time,kind:'scheduled',patientId:m.patientId,medicineId:m.id,date,time,state:'pending',snoozes:0,dueAt:null,units:m.units})):[];}
export function dosesFor(data:FamilyData,patientId:string,date:string){
 const generated=data.medicines.filter(m=>m.patientId===patientId).flatMap(m=>scheduled(m,date).map(d=>data.doses.find(x=>x.id===d.id)??d));
 return [...generated,...data.doses.filter(d=>d.patientId===patientId&&d.date===date&&d.state==='taken'&&!generated.some(x=>x.id===d.id))].sort((a,b)=>a.time.localeCompare(b.time));
}
export function adherence(data:FamilyData,patientId:string,date:string){const doses=dosesFor(data,patientId,date);return {total:doses.length,taken:doses.filter(d=>d.state==='taken').length,missed:doses.filter(d=>d.state==='missed').length};}
export function refillDays(m:Medicine){return Math.floor(m.stock/(m.units*m.times.length));}
async function patient(v:Vault,id:string){if(!(await v.all<Patient>('patients')).some(p=>p.id===id))throw new Error('Unknown patient');}
export async function saveMedicine(v:Vault,patientId:string,date:string,input:Omit<Medicine,'id'|'patientId'|'active'|'startDate'>){
 await patient(v,patientId);
 if(!input.name.trim()||input.name.length>80||!input.strength.trim()||input.strength.length>80||!input.times.length||input.times.length>6||new Set(input.times).size!==input.times.length||input.times.some(t=>!/^([01]\d|2[0-3]):[0-5]\d$/.test(t))||!['before','after','any'].includes(input.food)||!Number.isFinite(input.units)||input.units<=0||input.units>10||!Number.isFinite(input.stock)||input.stock<0||input.stock>10000)throw new Error('Invalid medicine');
 for(const image of [input.photo,input.prescription])if(image&&(!/^data:image\/(jpeg|png|webp);base64,/.test(image)||image.length>800000))throw new Error('Invalid photo');
 const id=crypto.randomUUID(),value:Medicine={...input,name:input.name.trim(),strength:input.strength.trim(),times:[...input.times].sort(),id,patientId,active:true,startDate:date};
 await v.write([{kind:'medicines',id,value}],'medicine-added',{patientId,id});
}
export async function changeMedicine(v:Vault,patientId:string,id:string,action:'archive'|'refill',date:string,amount=0){
 const m=(await v.all<Medicine>('medicines')).find(x=>x.id===id&&x.patientId===patientId);if(!m)throw new Error('Unknown medicine');
 if(action==='refill'&&(!Number.isFinite(amount)||amount<=0||m.stock+amount>10000))throw new Error('Invalid stock');
 const value=action==='archive'?{...m,active:false,endDate:date}:{...m,stock:m.stock+amount};
 await v.write([{kind:'medicines',id,value}],'medicine-'+action,{patientId,id,amount});
}
export async function scheduledAction(v:Vault,patientId:string,date:string,id:string,action:'take'|'snooze'|'remind',source:'tap'|'voice'='tap',now=Date.now()){
 const data=await loadFamily(v),d=dosesFor(data,patientId,date).find(x=>x.id===id),m=data.medicines.find(x=>x.id===d?.medicineId&&x.patientId===patientId);
 if(!d||!m)throw new Error('Unknown dose');if(d.state==='taken')return;
 let next={...d};const entries:{kind:Collection;id:string;value:unknown}[]=[];
 if(action==='take'){if(m.stock<d.units)throw new Error('Stock needs reconciliation');next={...d,state:'taken',dueAt:null,takenAt:new Date(now).toISOString(),source};entries.push({kind:'medicines',id:m.id,value:{...m,stock:Math.max(0,m.stock-d.units)}});}
 else if(action==='snooze'){if(d.snoozes>=3)throw new Error('Snooze limit');next={...d,snoozes:d.snoozes+1,dueAt:now+600000};}
 else next={...d,dueAt:now};
 entries.push({kind:'doses',id:next.id,value:next});await v.write(entries,'scheduled-dose-'+action,{patientId,id,source});
}
export async function respondAlert(v:Vault,patientId:string,checkinId:string,response:1|2|3,checked:string[]=[]){
 if(![1,2,3].includes(response))throw new Error('Invalid response');
 const row=(await v.all<Checkin>('checkins')).find(r=>r.id===checkinId&&r.patientId===patientId);if(!row||!row.result.data||row.result.light===0)throw new Error('No actionable alert');
 const id='alert:'+row.id,old=(await v.all<FamilyAlert>('alerts')).find(a=>a.id===id);
 if(old?.response===response&&JSON.stringify(old.checked)===JSON.stringify(checked))return;
 const p=(await v.all<Patient>('patients')).find(x=>x.id===patientId),steps=p?.plan?.[row.result.light===2?'red':'amber']??[];
 if(checked.some(s=>!steps.includes(s)))throw new Error('Invalid checklist');
 const value:FamilyAlert={...old,id,patientId,checkinId,date:row.date,light:row.result.light as 1|2,response,respondedAt:new Date().toISOString(),checked};
 const pendingId='response:'+id;
 await v.write([{kind:'alerts',id,value},{kind:'outbox',id:pendingId,value:{id:pendingId,patientId,date:row.date,type:'alert-response',status:'pending',delivery:'not-sent',digit:response}}],'family-alert-response',{patientId,checkinId,response});
}
export async function checkReminders(v:Vault,patientId:string,date:string,time:string,now=Date.now()){
 if(!/^([01]\d|2[0-3]):[0-5]\d$/.test(time))throw new Error('Invalid time');await patient(v,patientId);
 const data=await loadFamily(v),entries:{kind:Collection;id:string;value:unknown}[]=[];
 function queue(id:string,type:string){if(!data.pending.some(x=>x.id===id))entries.push({kind:'outbox',id,value:{id,patientId,date,type,status:'pending',delivery:'not-sent'}});}
 if(time>='11:00'&&!data.rows.some(r=>r.patientId===patientId&&r.date===date&&r.result.data&&!r.result.guest))queue('checkin-missed:'+patientId+':'+date,'missed-checkin');
 for(const d of dosesFor(data,patientId,date)){
  if(d.state!=='pending')continue;
  if(d.dueAt!==null&&d.snoozes>=3&&d.dueAt<=now){entries.push({kind:'doses',id:d.id,value:{...d,state:'missed',dueAt:null}});queue('missed:'+d.id,'missed-dose');}
  else if(d.dueAt===null&&d.time<=time)entries.push({kind:'doses',id:d.id,value:{...d,dueAt:now}});
 }
 if(entries.length)await v.write(entries,'foreground-reminders',{patientId,date,time});
}

export async function saveCareDetails(v:Vault,patientId:string,phone:string,amber:string,red:string){
 const p=(await v.all<Patient>('patients')).find(x=>x.id===patientId);if(!p||phone&&!/^\+?[0-9]{7,15}$/.test(phone)||amber.length>2000||red.length>2000)throw new Error('Invalid care details');
 const list=(text:string)=>[...new Set(text.split('\n').map(x=>x.trim()).filter(Boolean))];
 await v.write([{kind:'patients',id:p.id,value:{...p,phone:phone||undefined,plan:p.plan?.source==='clinician'?p.plan:amber.trim()||red.trim()?{source:'transcribed',amber:list(amber),red:list(red)}:null}}],'care-details-transcribed',{patientId,requiresReview:true});
}
