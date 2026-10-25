import {SharedNotes,PlanMetadata} from '../doctor/SharedCare';
import {useEffect,useState} from 'react';
import {useTranslation} from 'react-i18next';
import {ArrowLeft,Users,Pill,Plus,Phone,Check,CalendarDays} from 'lucide-react';
import type {DemoController} from '../data/useDemo';
import type {Checkin} from '../data/model';
import {displayStatus,DemoSummary} from '../data/DemoPanel';
import {adherence,dosesFor,refillDays,streak,windowRows,dayShift,type Medicine} from './model';
import type {Signal} from '../engine';

const signals:Signal[]=['weight_kg','leg_z_ohm','pulse_bpm','spo2','night_rr'];
export async function photoData(file:File){
 if(!['image/jpeg','image/png','image/webp'].includes(file.type)||file.size>5*1024*1024)throw new Error('Unsupported photo');
 const bitmap=await createImageBitmap(file);try{const canvas=document.createElement('canvas'),scale=Math.min(1,640/Math.max(bitmap.width,bitmap.height));canvas.width=Math.round(bitmap.width*scale);canvas.height=Math.round(bitmap.height*scale);canvas.getContext('2d')!.drawImage(bitmap,0,0,canvas.width,canvas.height);return canvas.toDataURL('image/jpeg',.8);}finally{bitmap.close();}
}
export function FamilyExperience({demo,openSettings}:{demo:DemoController;openSettings:()=>void}){
 const {t,i18n}=useTranslation(),[view,setView]=useState<'elders'|'detail'|'medicines'|'alert'>('elders'),[days,setDays]=useState(7),[alertId,setAlertId]=useState(''),[checked,setChecked]=useState<string[]>([]),[clock,setClock]=useState('11:05'),[notice,setNotice]=useState('');
 const {state,family}=demo,p=state.patient,row=state.checkins[state.cursor],date=row?.date;
 const alertRow=state.checkins.find(x=>x.id===alertId),saved=family.alerts.find(a=>a.checkinId===alertId);
 useEffect(()=>{setView('elders');setAlertId('');setNotice('');},[demo.unlocked]);
 useEffect(()=>{const steps=p?.plan?.[alertRow?.result.light===2?'red':'amber']??[];setChecked((saved?.checked??[]).filter(step=>steps.includes(step)));},[alertId,saved,p?.plan]);
 if(!demo.unlocked||!p||!row)return <section className="family-card"><Users size={44}/><h2>{t('familyMode.locked')}</h2><p>{t('elder.unlock')}</p><button className="primary" onClick={openSettings}>{t('vault.open')}</button></section>;
 const current=adherence(family,p.id,date),rows=windowRows(state.checkins,date,days),alerts=windowRows(state.checkins,date,30).filter(r=>r.result.light>0&&r.result.data).reverse();
 function openAlert(r:Checkin){setAlertId(r.id);setView('alert');}
 const n=(value:number)=>new Intl.NumberFormat(i18n.language,{maximumFractionDigits:1}).format(value);
 return <div className="family-mode">
  <div className="family-toolbar"><span className="eyebrow">{t('vault.historical')} · {date}</span>{view!=='elders'&&<button className="secondary" onClick={()=>setView('elders')}><ArrowLeft size={20}/>{t('familyMode.elders')}</button>}</div>
  {demo.failed&&<p role="alert" className="pending-notice">{t('vault.failed')}</p>}{notice&&<p role="status" className="success-note">{notice}</p>}
  {family.pending.filter(x=>x.date===date&&['missed-checkin','missed-dose'].includes(x.type)).map(x=><p className="pending-notice" role="status" key={x.id}>{state.patients.find(elder=>elder.id===x.patientId)?.name}: {t('familyMode.notice.'+x.type)} · {t('familyMode.notSent')}</p>)}
  {view==='elders'?<>
   <div className="section-heading"><h2>{t('familyMode.elders')}</h2><span>{state.patients.length} / 4</span></div>
   <div className="elder-list">{state.patients.map(elder=>{
    const r=family.rows.find(x=>x.patientId===elder.id&&x.date===date),med=adherence(family,elder.id,date),response=family.alerts.find(a=>a.checkinId===r?.id);
    return <button className="family-card elder-tile" key={elder.id} disabled={demo.busy} onClick={async()=>{if(elder.id===p.id||await demo.select(elder.id))setView('detail');}}><span className={'status-chip '+displayStatus(r)}>{t('status.'+displayStatus(r))}</span><h3>{elder.name}</h3><p>{t('familyMode.lastCheckin')}: {r?.result.data?r.date:t('familyMode.none')}</p><p><Pill size={20}/> {med.total?t('familyMode.dosesTaken',{taken:med.taken,total:med.total}):t('familyMode.noMedicines')}</p>{r&&r.result.light>0&&r.result.data&&<strong className="alert-badge">{t('familyMode.alertBadge')} · {response?.response?t('familyMode.response'+response.response):t('familyMode.noResponse')}</strong>}</button>;
   })}</div>
   <button className="secondary" disabled={demo.busy||state.patients.length>=4} onClick={()=>void demo.addElder()}><Plus size={22}/>{t('familyMode.addDemo')}</button><p className="capability-note">{t('familyMode.sharedFixture')}</p>
  </>:view==='detail'?<>
   <div className="section-heading"><h2>{p.name}</h2><button className="secondary" onClick={()=>setView('medicines')}><Pill size={20}/>{t('familyMode.manager')}</button></div>
   <div className="family-stats"><div><CalendarDays/><strong>{streak(state.checkins,date)}</strong><span>{t('familyMode.streak')}</span></div><div><Pill/><strong>{current.taken} / {current.total}</strong><span>{t('familyMode.takenOnDate')}</span></div><div><Users/><strong>{family.pending.filter(x=>x.patientId===p.id&&x.date===date).length}</strong><span>{t('familyMode.pending')}</span></div></div>
   {row.result.light>0&&row.result.data&&<button className="primary" onClick={()=>openAlert(row)}>{t('familyMode.viewAlert')}</button>}
   <DemoSummary demo={demo}/>
   <section className="family-card"><div className="section-heading"><h2>{t('familyMode.trends')}</h2><div className="period-buttons">{[7,30].map(d=><button key={d} aria-pressed={days===d} onClick={()=>setDays(d)}>{t('familyMode.days',{count:d})}</button>)}</div></div><p>{t('familyMode.trendsScope')}</p><div className="trend-grid">{signals.map(k=><Trend key={k} signal={k} rows={rows} date={date} days={days}/>)}</div></section>
   <section className="family-card"><h2>{t('familyMode.adherence')}</h2><p>{t('familyMode.calendarKey')}</p><div className="adherence-grid">{Array.from({length:30},(_,i)=>dayShift(date,i-29)).map(d=>{const a=adherence(family,p.id,d);return <div key={d} className={a.total&&a.taken===a.total?'complete':a.missed?'missed':''} title={d}><time dateTime={d}>{Number(d.slice(-2))}</time><span>{a.total?a.taken+'/'+a.total:'—'}</span></div>;})}</div></section>
   <section className="family-card"><h2>{t('familyMode.alertHistory')}</h2>{alerts.length?<div className="alert-list">{alerts.map(r=><button className="secondary" key={r.id} onClick={()=>openAlert(r)}><span className={'status-chip '+displayStatus(r)}>{t('status.'+displayStatus(r))}</span>{r.date}<span>{family.alerts.find(a=>a.checkinId===r.id)?.response?t('familyMode.recorded'):t('familyMode.noResponse')}</span></button>)}</div>:<p>{t('familyMode.noAlerts')}</p>}</section>
   <section className="family-card"><h2>{t('familyMode.reminders')}</h2><p>{t('familyMode.clockHelp')}</p><label>{t('familyMode.demoTime')}<input type="time" value={clock} onChange={e=>setClock(e.target.value)} required/></label><button className="secondary" disabled={demo.busy||!clock} onClick={async()=>{if(await demo.reminders(clock))setNotice(t('familyMode.remindersChecked'));}}>{t('familyMode.runReminders')}</button><p>{t('elder.foreground')}</p>{family.pending.filter(x=>x.patientId===p.id&&x.date===date).map(x=><p key={x.id} className="pending-notice">{t('familyMode.notice.'+x.type,{defaultValue:t('familyMode.pending')})} · {t('familyMode.notSent')}</p>)}</section>
   <SharedNotes demo={demo}/><CareDetails demo={demo}/><section className="family-card"><h2>{t('familyMode.nearby')}</h2><p>{t('familyMode.nearbyMissing')}</p><a className="secondary" href="tel:108">{t('call108')}</a><p>{t('familyMode.reportsLater')}</p></section>
  </>:view==='medicines'?<MedicineManager demo={demo}/>:alertRow?<section className={'family-card alert-panel '+displayStatus(alertRow)}>
   <span className={'status-chip '+displayStatus(alertRow)}>{t('status.'+displayStatus(alertRow))}</span><h2>{t('familyMode.alertTitle')}</h2><p>{p.name} · {alertRow.date}</p>
   <p>{alertRow.deviceWhy}</p><ul className="reason-list">{alertRow.result.reasons.map(r=><li key={r.signal}>{t('reason.'+r.signal)}</li>)}</ul><h3>{t('familyMode.why')}</h3><p>{t('familyMode.whyText')}</p>
   <h3>{t('familyMode.plan')}</h3>{p.plan?<><PlanMetadata plan={p.plan}/>{p.plan[alertRow.result.light===2?'red':'amber'].map(step=><label className="check-label" key={step}><input type="checkbox" checked={checked.includes(step)} onChange={e=>setChecked(e.target.checked?[...checked,step]:checked.filter(s=>s!==step))}/>{step}</label>)}</>:<p className="pending-notice">{t('vault.noPlan')} {t('vault.noTreatment')}</p>}
   <div className="response-actions">{([1,2,3] as const).map(digit=><button className={digit===2?'primary':'secondary'} aria-pressed={saved?.response===digit} disabled={demo.busy} key={digit} onClick={async()=>{if(await demo.respond(alertRow.id,digit,checked))setNotice(t('familyMode.responseSaved'));}}>{t('familyMode.response'+digit)} ({digit})</button>)}</div>
   {saved?.response&&<p role="status">{t('familyMode.recorded')}: {t('familyMode.response'+saved.response)} · {t('familyMode.notSent')}</p>}
   <p>{t('familyMode.responseScope')}</p>{saved?.seenByAsha&&<p className="success-note">{t('asha.seen')} · {saved.seenByAsha.date} · {t('asha.localStop')}</p>}{p.phone?<a className="secondary" href={'tel:'+p.phone}><Phone/>{t('familyMode.callElder')}</a>:<p>{t('familyMode.noElderPhone')}</p>}<a className="secondary" href="tel:108">{t('call108')}</a><p className="disclaimer">{t('disclaimer')}</p>
  </section>:null}
 </div>;
}
function Trend({signal,rows,date,days}:{signal:Signal;rows:Checkin[];date:string;days:number}){
 const {t}=useTranslation(),values=rows.map(r=>r.result.gated[signal]).filter((v):v is number=>v!==null),lo=Math.min(...values),hi=Math.max(...values),span=Math.max(hi-lo,1),start=dayShift(date,1-days);
 const points=rows.map(r=>({date:r.date,v:r.result.gated[signal]}));
 const x=(d:string)=>20+(Date.parse(d)-Date.parse(start))/86400000/(days-1)*260,y=(v:number)=>92-(v-lo)/span*64;
 return <article className="trend-card"><h3>{t('reading.'+signal)} <small>{t('unit.'+signal)}</small></h3>{values.length?<><svg viewBox="0 0 300 128" role="img" aria-label={t('familyMode.chartLabel',{name:t('reading.'+signal),min:lo.toFixed(1),max:hi.toFixed(1)})}>
  <path d="M20 20V96H280" stroke="#9aada4" fill="none"/>{points.map((point,i)=>{if(point.v===null)return null;const prev=points[i-1];return <g key={point.date}>{prev?.v!==null&&prev&&dayShift(prev.date,1)===point.date&&<line x1={x(prev.date)} y1={y(prev.v)} x2={x(point.date)} y2={y(point.v)} stroke="#0d6b6e" strokeWidth="2"/>}<circle cx={x(point.date)} cy={y(point.v)} r="3" fill="#0d6b6e"><title>{point.date+': '+point.v}</title></circle></g>;})}<text x="20" y="119">{start.slice(5)}</text><text x="240" y="119">{date.slice(5)}</text>
  </svg><p>{lo.toFixed(1)} – {hi.toFixed(1)} {t('unit.'+signal)}</p><details><summary>{t('familyMode.showReadings')}</summary><table><caption>{t('reading.'+signal)}</caption><thead><tr><th>{t('familyMode.date')}</th><th>{t('familyMode.value')}</th></tr></thead><tbody>{points.map(pt=><tr key={pt.date}><th>{pt.date}</th><td>{pt.v===null?'—':pt.v.toFixed(1)}</td></tr>)}</tbody></table></details></>:<p>{t('familyMode.noReadings')}</p>}</article>;
}
function MedicineManager({demo}:{demo:DemoController}){
 const {t}=useTranslation(),[adding,setAdding]=useState(false),[name,setName]=useState(''),[strength,setStrength]=useState(''),[times,setTimes]=useState('08:00'),[units,setUnits]=useState('1'),[stock,setStock]=useState('0'),[food,setFood]=useState<Medicine['food']>('after'),[photo,setPhoto]=useState<string>(),[prescription,setPrescription]=useState<string>(),[confirmed,setConfirmed]=useState(false),[busy,setBusy]=useState(false),[message,setMessage]=useState('');
 const p=demo.state.patient!,date=demo.state.checkins[demo.state.cursor].date,medicines=demo.family.medicines.filter(m=>m.patientId===p.id);
 async function upload(file:File|undefined,kind:'photo'|'prescription'){if(!file)return;setBusy(true);try{const data=await photoData(file);if(kind==='photo')setPhoto(data);else setPrescription(data);}catch{setMessage(t('familyMode.photoFailed'));}finally{setBusy(false);}}
 return <section className="family-card"><div className="section-heading"><h2>{t('familyMode.manager')}</h2><button className="secondary" onClick={()=>setAdding(!adding)}><Plus size={20}/>{t(adding?'close':'familyMode.addMedicine')}</button></div><p>{t('familyMode.medicineScope')}</p>{message&&<p role="status">{message}</p>}
  {adding&&<form className="medicine-form" onSubmit={async e=>{e.preventDefault();if(!confirmed)return;if(await demo.saveMedicine({name,strength,times:times.split(',').map(x=>x.trim()),units:Number(units),stock:Number(stock),food,photo,prescription})){setAdding(false);setName('');setStrength('');setPhoto(undefined);setPrescription(undefined);setConfirmed(false);setMessage(t('familyMode.medicineSaved'));}else setMessage(t('familyMode.invalidMedicine'));}}>
   <label>{t('familyMode.medicineName')}<input value={name} maxLength={80} required onChange={e=>setName(e.target.value)}/></label><label>{t('familyMode.strength')}<input value={strength} maxLength={80} required onChange={e=>setStrength(e.target.value)}/></label>
   <label>{t('familyMode.times')}<input value={times} required placeholder="08:00, 20:00" onChange={e=>setTimes(e.target.value)}/></label><label>{t('familyMode.food')}<select value={food} onChange={e=>setFood(e.target.value as Medicine['food'])}>{(['before','after','any'] as const).map(v=><option key={v} value={v}>{t('familyMode.food_'+v)}</option>)}</select></label>
   <label>{t('familyMode.units')}<input type="number" min="0.25" max="10" step="0.25" value={units} required onChange={e=>setUnits(e.target.value)}/></label><label>{t('familyMode.stock')}<input type="number" min="0" max="10000" step="0.25" value={stock} required onChange={e=>setStock(e.target.value)}/></label>
   <label>{t('familyMode.tabletPhoto')}<input type="file" accept="image/jpeg,image/png,image/webp" onChange={e=>void upload(e.target.files?.[0],'photo')}/></label>{photo&&<img className="tablet-photo" src={photo} alt={t('familyMode.tabletPhoto')}/>}
   <label>{t('familyMode.prescriptionPhoto')}<input type="file" accept="image/jpeg,image/png,image/webp" onChange={e=>void upload(e.target.files?.[0],'prescription')}/></label><p>{t('familyMode.photoPrivacy')}</p>
   <label className="check-label"><input type="checkbox" checked={confirmed} onChange={e=>setConfirmed(e.target.checked)} required/>{t('familyMode.prescriptionConfirm')}</label><button className="primary" disabled={demo.busy||busy||!confirmed}>{t('familyMode.saveMedicine')}</button>
  </form>}
  {!medicines.length&&<p>{t('familyMode.noMedicines')}</p>}{medicines.map(m=><MedicineCard key={m.id} medicine={m} demo={demo}/>)}
  <p>{t('familyMode.scheduleScope',{date})}</p><p>{t('familyMode.reviseSchedule')}</p><p>{t('elder.foreground')}</p>
 </section>;
}
function MedicineCard({medicine:m,demo}:{medicine:Medicine;demo:DemoController}){
 const {t}=useTranslation(),[amount,setAmount]=useState('30');
 return <article className="medicine-record">{m.photo&&<img className="tablet-photo" src={m.photo} alt={m.name}/>}<h3>{m.name} · {m.strength}</h3><p>{m.times.join(', ')} · {t('familyMode.food_'+m.food)} · {m.units} {t('familyMode.unitsShort')}</p><p>{t('familyMode.stock')}: {m.stock} · {t('familyMode.refillDays',{count:refillDays(m)})}</p>{m.prescription&&<details><summary>{t('familyMode.prescriptionPhoto')}</summary><img className="prescription-photo" src={m.prescription} alt={t('familyMode.prescriptionPhoto')}/></details>}
  {m.active?<><label>{t('familyMode.addStock')}<input aria-label={t('familyMode.addStock')+' '+m.name} type="number" min="0.25" max="10000" step="0.25" value={amount} onChange={e=>setAmount(e.target.value)}/></label><div className="response-actions"><button className="secondary" disabled={demo.busy||!Number.isFinite(Number(amount))||Number(amount)<=0} onClick={()=>void demo.medicineChange(m.id,'refill',Number(amount))}>{t('familyMode.refill')}</button><button className="secondary" disabled={demo.busy} onClick={()=>void demo.medicineChange(m.id,'archive')}>{t('familyMode.archive')}</button></div></>:<p>{t('familyMode.archived')}</p>}
 </article>;
}

function CareDetails({demo}:{demo:DemoController}){
 const {t}=useTranslation(),p=demo.state.patient!,[phone,setPhone]=useState(p.phone??''),[amber,setAmber]=useState(p.plan?.amber.join('\n')??''),[red,setRed]=useState(p.plan?.red.join('\n')??''),[confirm,setConfirm]=useState(false),[saved,setSaved]=useState(false);
 useEffect(()=>{setPhone(p.phone??'');setAmber(p.plan?.amber.join('\n')??'');setRed(p.plan?.red.join('\n')??'');setConfirm(false);setSaved(false);},[p.id]);
 return <section className="family-card"><h2>{t('familyMode.careDetails')}</h2><p>{t(demo.doctor.plans.some(x=>x.patientId===p.id)?'doctor.familyPlanHelp':'familyMode.transcriptionHelp')}</p><form onSubmit={async e=>{e.preventDefault();if(await demo.careDetails(phone,amber,red))setSaved(true);}}><label>{t('familyMode.elderPhone')}<input type="tel" pattern={'\\+?[0-9]{7,15}'} value={phone} onChange={e=>setPhone(e.target.value)}/></label><label>{t('familyMode.amberPlan')}<textarea aria-label={t('familyMode.amberPlan')} readOnly={demo.doctor.plans.some(x=>x.patientId===p.id)} maxLength={2000} value={amber} onChange={e=>setAmber(e.target.value)}/></label><label>{t('familyMode.redPlan')}<textarea aria-label={t('familyMode.redPlan')} readOnly={demo.doctor.plans.some(x=>x.patientId===p.id)} maxLength={2000} value={red} onChange={e=>setRed(e.target.value)}/></label><label className="check-label"><input type="checkbox" checked={confirm} onChange={e=>setConfirm(e.target.checked)}/>{t('familyMode.planConfirm')}</label><button className="secondary" disabled={!confirm||demo.busy}>{t('familyMode.saveCare')}</button></form>{saved&&<p role="status">{t('familyMode.careSaved')}</p>}</section>;
}

