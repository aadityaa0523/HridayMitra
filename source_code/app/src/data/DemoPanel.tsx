import {PlanMetadata} from '../doctor/SharedCare';
import {useState} from 'react';
import {useTranslation} from 'react-i18next';
import {LockKeyhole,Database,SkipForward} from 'lucide-react';
import type {DemoController} from './useDemo';
import {StatusOrb,type HealthStatus} from '../components';
import type {Checkin} from './model';
export function displayStatus(row?:Checkin):HealthStatus{
 if(!row)return 'unknown';
 if(row.result.light===2)return 'red';
 if(row.result.light===1)return 'amber';
 if(!row.result.data)return 'unknown';
 return row.result.learning?'learning':'green';
}
export function DemoPanel({demo}:{demo:DemoController}){
 const {t}=useTranslation(),[pin,setPin]=useState(''),[confirm,setConfirm]=useState(''),[consent,setConsent]=useState(false),[erase,setErase]=useState(false);
 const {state}=demo,current=state.checkins[state.cursor];
 async function submit(event:React.FormEvent){
  event.preventDefault();
  if(!demo.exists&&pin!==confirm)return;
  const value=pin;setPin('');setConfirm('');
  if(demo.exists)await demo.unlock(value);else await demo.create(value,consent);
 }
 const redIndex=state.checkins.findIndex((x,i)=>i>state.cursor&&x.result.light===2);
 return <section className="vault-panel" aria-labelledby="vault-title">
  <div className="vault-heading"><Database size={26}/><h2 id="vault-title">{t('vault.title')}</h2></div>
  <p>{t('vault.description')}</p>
  {!demo.unlocked?<form onSubmit={event=>void submit(event)}>
   <p>{demo.exists?t('vault.locked'):t('vault.first')}</p>
   <label>{t('vault.pin')}<input aria-label={t('vault.pin')} type="password" inputMode="numeric" autoComplete={demo.exists?'current-password':'new-password'} pattern="[0-9]{6,12}" minLength={6} maxLength={12} required value={pin} onChange={e=>setPin(e.target.value)}/></label>
   {!demo.exists&&<><label>{t('vault.confirm')}<input aria-label={t('vault.confirm')} type="password" inputMode="numeric" autoComplete="new-password" pattern="[0-9]{6,12}" minLength={6} maxLength={12} required value={confirm} onChange={e=>setConfirm(e.target.value)}/></label><label className="check-label"><input type="checkbox" checked={consent} onChange={e=>setConsent(e.target.checked)}/>{t('vault.consent')}</label></>}
   <button className="primary" disabled={demo.busy||(!demo.exists&&(!consent||pin!==confirm))} type="submit"><LockKeyhole size={22}/>{demo.busy?t('vault.busy'):t(demo.exists?'vault.unlock':'vault.create')}</button>
   <p className="vault-hint">{t('vault.noRecovery')}</p>
  </form>:<>
   <div className="vault-state"><span>{t('vault.unlocked')}</span><button className="secondary" onClick={demo.lock}>{t('vault.lock')}</button></div>
   {!state.patient?<button className="primary" disabled={demo.busy} onClick={()=>void demo.seed()}>{t('vault.load')}</button>:<>
    <h3>{state.patient?.name??t('vault.patient')}</h3><p>{t('vault.days',{count:state.checkins.length})}</p>
    <label>{t('vault.replayDate')}<select aria-label={t('vault.replayDate')} value={state.cursor} disabled={demo.busy} onChange={e=>void demo.move(Number(e.target.value))}>{state.checkins.map((r,i)=><option key={r.id} value={i}>{r.date}</option>)}</select></label>
    <div className="replay-actions"><button className="secondary" disabled={demo.busy||state.cursor===0} onClick={()=>void demo.move(state.cursor-1)}>{t('vault.previous')}</button><button className="secondary" disabled={demo.busy||state.cursor===state.checkins.length-1} onClick={()=>void demo.move(state.cursor+1)}><SkipForward size={20}/>{t('vault.next')}</button><button className="secondary" disabled={demo.busy||redIndex<0} onClick={()=>void demo.move(redIndex)}>{t('vault.nextRed')}</button></div>
    <p>{t('vault.score')}: {current?.result.S.toFixed(3)} · {t('vault.audit',{count:state.auditCount})}</p>
   </>}
   <label className="check-label"><input type="checkbox" checked={erase} onChange={e=>setErase(e.target.checked)}/>{t('vault.eraseConfirm')}</label>
   <button className="secondary" disabled={!erase||demo.busy} onClick={()=>void demo.erase().then(()=>setErase(false))}>{t('vault.erase')}</button>
  </>}
  {demo.failed&&<p role="alert">{t('vault.failed')}</p>}
  <p className="vault-hint">{t('vault.scope')}</p>
 </section>;
}
export function DemoSummary({demo}:{demo:DemoController}){
 const {t,i18n}=useTranslation(),row=demo.state.checkins[demo.state.cursor];
 if(!demo.unlocked||!row)return null;
 const n=(v:number)=>new Intl.NumberFormat(i18n.language,{maximumFractionDigits:1}).format(v);
 return <section className="demo-summary" aria-label={t('vault.summary')}>
  <span className="eyebrow">{t('vault.historical')}</span><h2>{demo.state.patient?.name??t('vault.patient')}</h2>
  <p>{row.date} · {row.deviceId?(row.source==='device'?'DEVICE · '+row.deviceId:'SIMULATOR · '+row.deviceId):t('vault.source')}</p>{row.deviceWhy&&<p>{row.deviceWhy}</p>}<StatusOrb status={displayStatus(row)}/>
  {!row.result.data&&<p>{t('vault.missing')}</p>}
  {row.result.guest&&<p>{t('vault.guest')}</p>}
  {row.result.plate&&<p>{t('vault.plate')}</p>}
  {row.result.learning&&<p>{t('status.learning')}</p>}
  {row.result.danger&&<p>{t('vault.oxygen')}</p>}
  <ul className="reason-list">{row.result.reasons.map(reason=><li key={reason.signal}>{t('reason.'+reason.signal)}{reason.level!==undefined&&reason.baseline!==undefined&&<span> · {n(reason.level)} / {n(reason.baseline)} {t('vault.normal')}</span>}</li>)}</ul>
  <dl className="reading-grid">{(['weight_kg','pulse_bpm','spo2','night_rr','activity_min'] as const).map(k=><div key={k}><dt>{t('reading.'+k)}</dt><dd>{row.result.gated[k]===null?'—':n(row.result.gated[k]!)} <small>{t('unit.'+k)}</small></dd></div>)}</dl>
  {row.result.light>0&&<div className="plan-missing">{demo.state.patient?.plan?<><strong>{t('familyMode.plan')}</strong><PlanMetadata plan={demo.state.patient.plan}/><ul className="reason-list">{demo.state.patient.plan[row.result.light===2?'red':'amber'].map(step=><li key={step}>{step}</li>)}</ul></>:<><strong>{t('vault.noPlan')}</strong><p>{t('vault.noTreatment')}</p></>}<a className="secondary" href="tel:108">{t('call108')}</a></div>}
  <p className="disclaimer">{t('disclaimer')}</p>
 </section>;
}


