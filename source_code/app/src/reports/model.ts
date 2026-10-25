import type {Patient,Checkin} from '../data/model';
import {dayShift,dosesFor,type FamilyData,type FamilyAlert} from '../family/model';
import type {AshaData} from '../asha/model';
import type {DoctorData} from '../doctor/model';
import {signals,type Signal} from '../engine';
import {dayNumber} from '../engine/daily';
import type {DeviceEvent} from '../device/model';

export const reportTypes=['daily','weekly','monthly','opd','alert','medication','labs','referral','device'] as const;
export type ReportType=typeof reportTypes[number];
export const titles:Record<ReportType,[string,string]>={daily:['Daily card','दैनिक कार्ड'],weekly:['Weekly summary','साप्ताहिक सारांश'],monthly:['Monthly clinical report','मासिक चिकित्सकीय रिपोर्ट'],opd:['OPD visit summary','ओपीडी सारांश'],alert:['Alert episode report','चेतावनी प्रकरण'],medication:['Medication adherence','दवा पालन'],labs:['Lab history','जाँच इतिहास'],referral:['ASHA referral slip','आशा रेफरल पर्ची'],device:['Device health','उपकरण की स्थिति']};
export const measures=[['weight_kg','Body weight','kg'],['leg_z_ohm','Leg impedance','Ohm'],['trunk_z_ohm','Chest impedance','Ohm'],['leg_ewi','Leg extracellular-water index','ratio'],['pulse_bpm','Heart rate','/min'],['spo2','SpO2','%'],['night_rr','Night respiratory rate','/min']] as const;
export const hindiMeasures={weight_kg:'वज़न',leg_z_ohm:'पैर का प्रतिबाधा',trunk_z_ohm:'छाती का प्रतिबाधा',leg_ewi:'पैर का पानी सूचकांक',pulse_bpm:'नाड़ी',spo2:'ऑक्सीजन संतृप्ति',night_rr:'रात की श्वसन दर'};
export type Chart={label:string;points:{date:string;value:number|null}[];band:[number,number]|null};
export type Report={version:1;id:string;type:ReportType;language:'en'|'hi';patientId:string;patientName:string;date:string;start:string;generatedAt:string;author:string;sections:{title:string;lines:string[]}[];charts:Chart[];synthetic:true};
const med=(a:number[])=>{const s=[...a].sort((a,b)=>a-b),n=s.length;return n%2?s[n>>1]:(s[n/2-1]+s[n/2])/2;};
export function personalBand(rows:Checkin[],date:string,key:Signal):[number,number]|null{
 const n=dayNumber(date),base=rows.filter(r=>{const d=n-dayNumber(r.date);return d>=7&&d<=35;}).map(r=>r.result.gated[key]).filter((x):x is number=>x!==null);
 if(base.length<6)return null;const m=med(base),s=signals[key],spread=Math.max(1.4826*med(base.map(x=>Math.abs(x-m))),s[2]*(s[3]?Math.abs(m):1));return [m-spread,m+spread];
}
export function buildReport(f:FamilyData,a:AshaData,d:DoctorData,p:Patient,date:string,type:ReportType,language:'en'|'hi',author:string,deviceEvents:DeviceEvent[]=[]):Report{
 dayNumber(date);if(!author.trim()||author.length>80)throw new Error('Generating name required');
 const tr=(en:string,hi:string)=>language==='hi'?hi:en,none=tr('Not recorded','दर्ज नहीं'),days=type==='daily'?1:type==='weekly'?7:30,start=dayShift(date,1-days);
 const all=f.rows.filter(r=>r.patientId===p.id&&r.date<=date).sort((a,b)=>a.date.localeCompare(b.date)),rows=all.filter(r=>r.date>=start),latest=all.at(-1),visits=a.visits.filter(v=>v.patientId===p.id&&v.date>=start&&v.date<=date),labs=d.labs.filter(l=>l.patientId===p.id&&l.date<=date).sort((a,b)=>a.date.localeCompare(b.date));
 const alerts:FamilyAlert[]=rows.filter(r=>r.result.data&&!r.result.guest&&r.result.light>0).map(r=>{const saved=f.alerts.find(x=>x.patientId===p.id&&x.checkinId===r.id),seen=saved?.seenByAsha&&saved.seenByAsha.date<=date?saved.seenByAsha:undefined;return {...saved,id:'alert:'+r.id,patientId:p.id,checkinId:r.id,date:r.date,light:r.result.light as 1|2,checked:saved?.checked??[],seenByAsha:seen,escalation:seen?saved?.escalation:undefined};}),doses=Array.from({length:days},(_,i)=>dosesFor(f,p.id,dayShift(start,i))).flat(),taken=doses.filter(x=>x.state==='taken').length;
 const sections:Report['sections']=[],add=(title:string,lines:string[])=>sections.push({title,lines:lines.length?lines:[none]});
 const light=(r:Checkin)=>r.result.guest?'Excluded: guest':!r.result.data?'No data':r.result.learning?'Learning':['Green','Amber','Red'][r.result.light];
 const alertLines=alerts.map(x=>`${x.date} | ${x.light===2?'Red':'Amber'} | response ${x.response??none} ${x.respondedAt??''} | ASHA ${x.seenByAsha?.date??none} | ${x.escalation??'No delivery confirmed'}`);
 const medicineLines=f.medicines.filter(m=>m.patientId===p.id&&m.startDate<=date&&(!m.endDate||m.endDate>start)).map(m=>`${m.name} ${m.strength} | ${m.times.join(', ')} | ${m.units} units/dose`);
 const labLines=labs.map(l=>`${l.date} | ${l.test}: ${l.value} ${l.unit} | ${l.doctorName}`);
 const visitLines=visits.map(v=>`${v.date} | BP ${v.bpSys??none}/${v.bpDia??none} mmHg | weight ${v.weight??none} kg | edema ${v.edema}/3 | ${v.outcome} | ${v.notes||none}`);
 if(['daily','weekly','monthly','opd'].includes(type)){
  add(tr('Monitoring status','निगरानी स्थिति'),[`${latest?.date??none} | ${latest?light(latest):none}`,`Reasons: ${latest?.deviceWhy||latest?.result.reasons.map(x=>x.signal+' (z '+x.z.toFixed(2)+')').join(', ')||none}`,`Check-ins: ${new Set(rows.map(r=>r.date)).size}/${days}`,...(type==='weekly'?[`Light strip: ${Array.from({length:days},(_,i)=>{const dt=dayShift(start,i),r=rows.find(r=>r.date===dt);return dt.slice(5)+' '+(r?light(r):'No data');}).join(' | ')}`]:[])]);
  add(tr('Medicines / adherence','दवाएँ / पालन'),[...medicineLines,`Taken ${taken}/${doses.length} (${doses.length?Math.round(taken/doses.length*100)+'%':'N/A'}); pending ${doses.filter(x=>x.state==='pending').length}; recorded missed ${doses.filter(x=>x.state==='missed').length}`]);
 }
 if(type==='daily')add(tr('Clinical values / English','माप / English'),measures.map(([k,label,unit])=>{const band=personalBand(all,date,k),value=latest?.date===date?latest.result.gated[k]:null;return `${language==='hi'?hindiMeasures[k]+' | ':''}${label}: ${value===null?none:Number(value.toFixed(2))} ${unit} | personal band ${band?band.map(x=>x.toFixed(2)).join(' - '):none}`;}));
 if(['weekly','monthly','opd'].includes(type))add(tr(type==='opd'?'Recent alerts (latest three)':'Alerts and responses',type==='opd'?'हाल की तीन चेतावनियाँ':'चेतावनी और जवाब'),type==='opd'?alertLines.slice(-3):alertLines);
 if(['monthly','opd','referral'].includes(type)){add(tr('ASHA findings','आशा निष्कर्ष'),visitLines);add(tr('Labs','जाँच'),labLines);}
 if(type==='opd')add(tr('Symptoms / latest check-in','लक्षण / अंतिम जाँच'),[`Breathlessness ${latest?.result.gated.breathless??none}; extra pillows ${latest?.result.gated.orthopnea??none}; night sit-ups ${latest?.result.gated.night_situps??none}`,`Latest ASHA: ${a.visits.filter(v=>v.patientId===p.id&&v.date<=date).sort((a,b)=>a.date.localeCompare(b.date)).at(-1)?.notes||none}`]);
 if(type==='alert'){
  const episode=alerts.at(-1),trigger=all.find(r=>r.id===episode?.checkinId);
  add(tr('Latest alert episode','अंतिम चेतावनी प्रकरण'),episode?[`Trigger ${episode.date} | ${trigger?light(trigger):none}`,`Reasons: ${trigger?.deviceWhy||trigger?.result.reasons.map(x=>x.signal+' z='+x.z.toFixed(2)).join(', ')||none}`,`Family response: ${episode.response??none} | ${episode.respondedAt??none}`,`Checks: ${episode.checked.join(', ')||none}`,`ASHA: ${episode.seenByAsha?.date??none}`,`Outcome: ${episode.escalation??'No clinical outcome recorded'}`]:[]);
  add(tr('Escalation timeline','सूचना का क्रम'),episode?f.pending.filter(x=>x.patientId===p.id&&x.date>=episode.date&&x.date<=date).map(x=>`${x.date} | ${x.type} | ${x.status} | ${x.delivery}`):[]);
 }
 if(type==='medication'){
  add(tr('Medicines','दवाएँ'),medicineLines);
  add(tr('Dose heat map: T taken, M missed, P pending, - unscheduled','दवा तालिका: T ली, M छूटी, P लंबित, - समय नहीं'),f.medicines.filter(m=>m.patientId===p.id&&m.startDate<=date).map(m=>m.name+' | '+Array.from({length:days},(_,i)=>{const ds=doses.filter(x=>x.medicineId===m.id&&x.date===dayShift(start,i));return ds.length?ds.map(x=>x.state==='taken'?'T':x.state==='missed'?'M':'P').join(''):'-';}).join(' ')));
  add(tr('Recorded missed doses','दर्ज छूटी खुराक'),doses.filter(x=>x.state==='missed').map(x=>`${x.date} ${x.time} | ${f.medicines.find(m=>m.id===x.medicineId)?.name??x.medicineId}`));
 }
 if(type==='labs')add(tr('Lab history - units kept as reported','जाँच इतिहास - मूल इकाइयाँ'),labLines);
 if(type==='referral'){const v=visits.at(-1);add(tr('Referral reason and contact','रेफरल कारण और संपर्क'),[`Reason: ${v?.referralReason||none}`,`Outcome: ${v?.outcome??none}`,`${p.village||none} | ${p.house||none}`,`Family: ${p.phone||none} | PHC: ${p.phcName||none} ${p.phcPhone||none}`,`30-day check-ins ${rows.length}; amber ${rows.filter(r=>r.result.data&&r.result.light===1).length}; red ${rows.filter(r=>r.result.data&&r.result.light===2).length}`]);}
 if(type==='device'){
  const events=deviceEvents.filter(e=>e.patientId===p.id).sort((a,b)=>a.at.localeCompare(b.at));
  if(events.length)add(tr('Received device health - receipt times independent of replay date','उपकरण स्थिति - प्राप्ति समय जाँच की तारीख से अलग'),[...events.map(e=>`${e.at} | ${e.mode} | battery ${e.status.battery_mv??'unknown'} mV | signal ${e.status.signal===99?'unknown':e.status.signal??'unknown'} | ${e.status.problems||'No problems reported by device'}`),'Connection at report generation: not verified','Service actions: not recorded','Amulet reaches app through check-in device; no separate pairing.']);
  else add(tr('Device telemetry unavailable','उपकरण के आँकड़े उपलब्ध नहीं'),['Check-in attachment: not connected','Amulet: not connected','Self-test history: not recorded','Battery: unknown','Signal: unknown','Service actions: not recorded','No hardware telemetry has been saved.']);
 }
 const charts:Chart[]=[];
 if(['monthly','opd','weekly','referral'].includes(type))for(const [k,label,unit] of measures.filter(x=>type!=='weekly'||x[0]==='weight_kg'))charts.push({label:(language==='hi'?hindiMeasures[k]+' | ':'')+label+' ('+unit+')',points:Array.from({length:days},(_,i)=>{const dt=dayShift(start,i);return {date:dt,value:rows.find(r=>r.date===dt)?.result.gated[k]??null};}),band:personalBand(all,date,k)});
 if(type==='labs')for(const test of [...new Set(labs.map(l=>l.test+'|'+l.unit))]){const [key,unit]=test.split('|');charts.push({label:key+' ('+unit+')',points:labs.filter(l=>l.test===key&&l.unit===unit).map(l=>({date:l.date,value:l.value})),band:null});}
 return {version:1,id:crypto.randomUUID(),type,language,patientId:p.id,patientName:p.name,date,start:type==='labs'&&labs[0]?labs[0].date:start,generatedAt:new Date().toISOString(),author:author.trim(),sections,charts,synthetic:true};
}
export function fhirBundle(rows:Checkin[],p:Patient,start:string,end:string){
 dayNumber(start);dayNumber(end);if(start>end)throw new Error('Invalid range');
 const map=[['weight_kg','29463-7','Body weight','kg'],['pulse_bpm','8867-4','Heart rate','/min'],['spo2','59408-5','Oxygen saturation by pulse oximetry','%'],['night_rr','9279-1','Respiratory rate','/min'],['leg_z_ohm',null,'Leg bioimpedance at 5 kHz','Ohm'],['trunk_z_ohm',null,'Trunk bioimpedance at 5 kHz','Ohm']] as const;
 return {resourceType:'Bundle',type:'collection',entry:[{resource:{resourceType:'Patient',id:p.id,name:[{text:p.name}],meta:{tag:[{system:'https://hridaymitra.example/demo',code:'synthetic'}]}}},...rows.filter(r=>r.patientId===p.id&&r.date>=start&&r.date<=end&&!r.result.guest).flatMap(r=>map.flatMap(([k,code,text,unit])=>{const value=r.result.gated[k];return value===null?[]:[{resource:{resourceType:'Observation',status:'final',category:[{coding:[{system:'http://terminology.hl7.org/CodeSystem/observation-category',code:code?'vital-signs':'exam'}]}],code:{...(code?{coding:[{system:'http://loinc.org',code,display:text}]}:{}),text},subject:{reference:'Patient/'+p.id},effectiveDateTime:r.date,valueQuantity:{value:Math.round(value*100)/100,unit,system:'http://unitsofmeasure.org',code:unit},note:[{text:r.source==='device'?'Synthetic device demo record; not a verified clinical measurement.':'Synthetic simulator reading; not a clinical measurement.'}]}}];}))]};
}



