import {Vault} from '../data/vault';
import type {Patient,Checkin} from '../data/model';
import {dayNumber} from '../engine/daily';
import type {Packet,Status} from './protocol';
export type DeviceKind='ble'|'serial'|'simulator';
export type Binding={id:string;kind:'device-binding';patientId:string;wireId:string;mode:DeviceKind};
export type DeviceEvent={id:string;kind:'device-event';patientId:string;mode:DeviceKind;at:string;status:Status};
export type DeviceData={bindings:Binding[];events:DeviceEvent[]};
export const emptyDevices=():DeviceData=>({bindings:[],events:[]});
export async function loadDevices(v:Vault):Promise<DeviceData>{const all=await v.all<Binding|DeviceEvent>('settings');return {bindings:all.filter((x):x is Binding=>x.kind==='device-binding'),events:all.filter((x):x is DeviceEvent=>x.kind==='device-event')};}
export async function createLinked(v:Vault,wireId:string,mode:DeviceKind){
 if(!/^[\w.-]{1,64}$/.test(wireId)||!['ble','serial','simulator'].includes(mode))throw Error('Invalid binding');
 const patients=await v.all<Patient>('patients');if(patients.length>=4)throw Error('Four elder limit');
 const id='linked-'+crypto.randomUUID(),binding:Binding={id:'device-binding:'+id,kind:'device-binding',patientId:id,wireId,mode},p:Patient={id,name:'Linked demo elder '+(patients.length+1),synthetic:true,fixtureId:'linked:'+mode,timeZone:'Asia/Kolkata',plan:null};
 await v.write([{kind:'patients',id,value:p},{kind:'settings',id:binding.id,value:binding},{kind:'settings',id:'selected-patient',value:{id:'selected-patient',patientId:id}},{kind:'settings',id:'demo-cursor',value:{id:'demo-cursor',patientId:id,index:0}}],'device-demo-created',{patientId:id,wireId,mode},false);
}
export async function ingest(v:Vault,patientId:string,mode:DeviceKind,packets:Packet[],legacyDate:string){
 if(!packets.length||packets.length>200)throw Error('Invalid batch');const binding=(await loadDevices(v)).bindings.find(b=>b.patientId===patientId);if(!binding||binding.mode!==mode)throw Error('Wrong binding');
 if(packets.length>1&&packets.some(p=>!p.date))throw Error('Import undated legacy records individually');
 const all=await v.all<Checkin>('checkins'),rows=all.filter(r=>r.patientId===patientId),entries:{kind:'checkins'|'settings';id:string;value:unknown}[]=[],next=[...rows];
 for(const packet of packets){if(packet.id!==binding.wireId)throw Error('Device patient mismatch');const date=packet.date??legacyDate;dayNumber(date);const id=patientId+':'+(packet.event_id??(packet.id+':'+date));
  const value:Checkin={id,patientId,date,source:mode==='simulator'?'simulator':'device',raw:packet.raw,result:packet.result,deviceWhy:packet.why,deviceId:packet.id,...(packet.extras?{extras:packet.extras}:{})};
  const existing=next.find(r=>r.date===date||r.id===id);if(existing){if(JSON.stringify(existing)!==JSON.stringify(value))throw Error('Conflicting event or same-day record');continue;}next.push(value);entries.push({kind:'checkins',id,value});
 }
 if(!entries.length)return;next.sort((a,b)=>a.date.localeCompare(b.date));entries.push({kind:'settings',id:'demo-cursor',value:{id:'demo-cursor',patientId,index:next.length-1}});await v.write(entries,'device-checkins-imported',{patientId,mode,count:entries.length-1});
}
export async function saveStatus(v:Vault,patientId:string,mode:DeviceKind,status:Status){
 const binding=(await loadDevices(v)).bindings.find(b=>b.patientId===patientId&&b.mode===mode);if(!binding)throw Error('Wrong binding');
 const id='device-event:'+crypto.randomUUID(),event:DeviceEvent={id,kind:'device-event',patientId,mode,at:new Date().toISOString(),status};await v.write([{kind:'settings',id,value:event}],'device-health-received',{patientId,mode});
}
