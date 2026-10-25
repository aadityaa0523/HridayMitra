import type {TFunction} from 'i18next';
import type {Visit} from './model';
import {readingSummary,weeklySummary} from './model';
import type {FamilyData} from '../family/model';

export function referralLines(data:FamilyData,visit:Visit,t:TFunction){
 const p=data.patients.find(p=>p.id===visit.patientId)!;
 const summary=readingSummary(data.rows.filter(r=>r.patientId===p.id),visit.date),latest=summary.latest;
 const value=(x:number|null)=>x===null?t('asha.notRecorded'):String(x);
 return [t('asha.referral'),t('demo'),p.name+' | '+visit.date,(p.village||t('asha.noVillage'))+' | '+(p.house||t('asha.noHouse')),
  t('asha.referralReason')+': '+(visit.referralReason||t('asha.notRecorded')),
  t('asha.outcome')+': '+t('asha.outcomes.'+visit.outcome),
  t('asha.bp')+': '+value(visit.bpSys)+' / '+value(visit.bpDia)+' mmHg',t('reading.weight_kg')+': '+value(visit.weight)+' kg',
  t('asha.swelling')+': '+visit.edema+' / 3',t('asha.breathless')+': '+t(visit.breathlessRest?'elder.yes':'elder.no'),t('asha.pillows')+': '+t(visit.pillows?'elder.yes':'elder.no'),
  t('asha.medicinesSeen')+': '+(Object.keys(visit.medicinesSeen).length?'':t('familyMode.noMedicines')),...Object.entries(visit.medicinesSeen).map(([id,seen])=>(data.medicines.find(m=>m.id===id)?.name??id)+': '+t(seen?'elder.yes':'elder.no')),
  t('asha.thirtyDays'),t('asha.daysRecorded',{count:summary.days})+' | '+t('asha.redDays',{count:summary.reds})+' | '+t('asha.amberDays',{count:summary.amber}),
  ...Object.entries(summary.ranges).map(([k,range])=>t('reading.'+k)+': '+(range?range.min.toFixed(1)+' - '+range.max.toFixed(1):t('asha.notRecorded'))+' '+t('unit.'+k)),
  t('asha.lastReading')+': '+(latest?latest.date+' | '+t('status.'+(latest.result.light===2?'red':latest.result.light===1?'amber':latest.result.learning?'learning':'green')):t('asha.notRecorded')),
  ...(latest?.result.reasons.map(r=>t('reason.'+r.signal))??[]),t('asha.notes')+': '+(visit.notes||t('asha.notRecorded')),
  t('asha.seen')+' | '+t('asha.localStop'),t('asha.visitId')+': '+visit.id,t('asha.pdfImageNote'),t('disclaimer')+' '+t('call108')];
}
export function weeklyLines(data:FamilyData,visits:Visit[],date:string,village:string,t:TFunction){
 const s=weeklySummary(data,visits,date,village);
 return [t('asha.weekly'),t('demo'),s.start+' - '+s.end,t('asha.village')+': '+(village==='__unknown'?t('asha.noVillage'):village||t('asha.allVillages')),
  t('asha.visitCount')+': '+s.visits,t('asha.eldersVisited')+': '+s.eldersVisited,t('asha.redDayCount')+': '+s.reds,t('asha.redElderCount')+': '+s.redElders,t('asha.referrals')+': '+s.referrals,t('asha.calls108')+': '+s.called108,
  t('asha.countScope'),t('asha.deliveryHelp'),t('asha.pdfImageNote'),t('disclaimer')];
}
export function qrPayload(data:FamilyData,visit:Visit){
 const p=data.patients.find(p=>p.id===visit.patientId)!;
 return JSON.stringify({app:'Saathi',demo:true,visitId:visit.id,date:visit.date,patient:p.name,reason:visit.referralReason.slice(0,160),outcome:visit.outcome,bp:[visit.bpSys,visit.bpDia],weight:visit.weight,edema:visit.edema,breathlessRest:visit.breathlessRest,pillows:visit.pillows});
}
// Canvas uses the browser's shaping engine for Hindi; raster pages avoid missing conjuncts.
export async function createPDF(lines:string[]){
 await document.fonts.load('24px "Noto Sans"');await document.fonts.load('24px "Noto Sans Devanagari"');await document.fonts.ready;
 const {jsPDF}=await import('jspdf');const pdf=new jsPDF({unit:'mm',format:'a4',compress:true});
 const canvas=document.createElement('canvas');canvas.width=1240;canvas.height=1754;const ctx=canvas.getContext('2d')!;
 const font='"Noto Sans", "Noto Sans Devanagari", sans-serif';let y=0,page=0;
 function start(){ctx.fillStyle='#fff';ctx.fillRect(0,0,1240,1754);ctx.fillStyle='#0d6b6e';ctx.fillRect(0,0,1240,24);y=95;}
 function finish(){ctx.font='22px '+font;ctx.fillStyle='#4b6060';ctx.fillText('HridayMitra Saathi | '+(++page),80,1690);if(page>1)pdf.addPage();pdf.addImage(canvas.toDataURL('image/jpeg',.92),'JPEG',0,0,210,297);}
 start();
 for(let index=0;index<lines.length;index++){
  ctx.font=(index===0?'bold 38px ':'24px ')+font;
  const wrapped:string[]=[];let current='';
  for(const word of lines[index].replace(/[\r\n]+/g,' ').split(/\s+/)){
   if(ctx.measureText((current?current+' ':'')+word).width>1080&&current){wrapped.push(current);current='';}
   if(ctx.measureText(word).width>1080){for(const char of word){if(ctx.measureText(current+char).width>1080){wrapped.push(current);current='';}current+=char;}}
   else current+=(current?' ':'')+word;
  }
  if(current)wrapped.push(current);
  for(const text of wrapped){if(y>1600){finish();start();ctx.font='24px '+font;}ctx.fillStyle=index===0?'#0d6b6e':'#172b2c';ctx.fillText(text,80,y);y+=36;}
  y+=12;
 }
 finish();return pdf.output('blob');
}
export async function fileHash(blob:Blob){return [...new Uint8Array(await crypto.subtle.digest('SHA-256',await blob.arrayBuffer()))].map(n=>n.toString(16).padStart(2,'0')).join('');}
