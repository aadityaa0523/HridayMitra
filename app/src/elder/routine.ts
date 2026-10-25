import {Vault} from '../data/vault';
export type Dose={id:string;patientId:string;date:string;medicineId:'practice-tablet';state:'pending'|'taken'|'missed';takenAt?:string;source?:'tap'|'voice';dueAt:number|null;snoozes:number};
export type Answers={id:string;patientId:string;date:string;breathless:0|1;orthopnea:0|1;at:string;source:'tap'|'voice'};
export type CareContact={id:string;patientId:string;role:'family1'|'family2'|'asha';name:string;phone:string};
export type Routine={dose:Dose|null;answers:Answers|null;contacts:CareContact[];pendingHelp:boolean};
export const noRoutine=():Routine=>({dose:null,answers:null,contacts:[],pendingHelp:false});
export function doseId(patientId:string,date:string){return 'practice-dose:'+patientId+':'+date;}
export function nextDose(current:Dose|null,patientId:string,date:string,action:'take'|'snooze'|'remind'|'expire',now:number,source:'tap'|'voice'='tap'):Dose{
 const d=current?{...current}:{id:doseId(patientId,date),patientId,date,medicineId:'practice-tablet' as const,state:'pending' as const,dueAt:null,snoozes:0};
 if(d.patientId!==patientId||d.date!==date)throw new Error('Wrong dose');
 if(d.state==='taken')return d;
 if(action==='take')return {...d,state:'taken',takenAt:new Date(now).toISOString(),source,dueAt:null};
 if(action==='snooze'){if(d.snoozes>=3)throw new Error('Snooze limit');return {...d,snoozes:d.snoozes+1,dueAt:now+600000};}
 if(action==='remind')return {...d,dueAt:now};
 if(d.dueAt!==null&&now>=d.dueAt&&d.snoozes>=3)return {...d,state:'missed',dueAt:null};
 return d;
}
export async function loadRoutine(v:Vault,patientId:string,date:string):Promise<Routine>{
 const doses=await v.all<Dose>('doses'),settings=await v.all<Answers>('settings'),contacts=await v.all<CareContact>('contacts'),outbox=await v.all<{id:string;patientId:string;date:string;status:string;type?:string}>('outbox');
 return {dose:doses.find(x=>x.id===doseId(patientId,date))??null,answers:settings.find(x=>x.id==='answers:'+patientId+':'+date)??null,contacts:contacts.filter(x=>x.patientId===patientId),pendingHelp:outbox.some(x=>x.patientId===patientId&&x.date===date&&x.status==='pending'&&x.type==='missed-practice-dose')};
}
export async function actDose(v:Vault,patientId:string,date:string,action:'take'|'snooze'|'remind'|'expire',source:'tap'|'voice'='tap',now=Date.now()){
 const current=(await v.all<Dose>('doses')).find(x=>x.id===doseId(patientId,date))??null;
 const next=nextDose(current,patientId,date,action,now,source);
 if(JSON.stringify(next)===JSON.stringify(current))return;
 const entries:{kind:'doses'|'outbox';id:string;value:unknown}[]=[{kind:'doses',id:next.id,value:next}];
 if(next.state==='missed')entries.push({kind:'outbox',id:'missed:'+next.id,value:{id:'missed:'+next.id,patientId,date,status:'pending',type:'missed-practice-dose',at:new Date(now).toISOString(),delivery:'not-sent'}});
 await v.write(entries,'practice-dose-'+action,{patientId,date,source});
}
export async function saveAnswers(v:Vault,patientId:string,date:string,breathless:0|1,orthopnea:0|1,source:'tap'|'voice'){
 if(![0,1].includes(breathless)||![0,1].includes(orthopnea))throw new Error('Invalid answer');
 const id='answers:'+patientId+':'+date;
 await v.write([{kind:'settings',id,value:{id,patientId,date,breathless,orthopnea,source,at:new Date().toISOString()}}],'practice-answers',{patientId,date,source});
}
export async function saveContact(v:Vault,patientId:string,role:CareContact['role'],name:string,phone:string){
 if(!['family1','family2','asha'].includes(role)||!name.trim()||!/^\+?[0-9]{7,15}$/.test(phone))throw new Error('Invalid contact');
 const id='contact:'+patientId+':'+role;
 await v.write([{kind:'contacts',id,value:{id,patientId,role,name:name.trim().slice(0,80),phone}}],'contact-updated',{patientId,role});
}

