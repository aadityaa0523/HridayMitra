import {useTranslation} from 'react-i18next';
import type {TFunction} from 'i18next';
import type {CarePlan} from '../data/model';
import type {DemoController} from '../data/useDemo';
export function planText(plan:CarePlan|null|undefined,light:number,t:TFunction){
 if(!plan)return '';
 return [...(light===2?plan.red:light===1?plan.amber:[]),plan.dryWeightKg!=null?t('doctor.dryWeight')+': '+plan.dryWeightKg+' kg':'',plan.fluidLimitL!=null?t('doctor.fluidLimit')+': '+plan.fluidLimitL+' L':'',plan.saltAdvice??'',plan.followUp?t('doctor.followUp')+': '+plan.followUp:''].filter(Boolean).join('. ');
}
export function PlanMetadata({plan}:{plan:CarePlan}){
 const {t}=useTranslation();
 return <div className="plan-metadata"><p>{plan.source==='clinician'?t('doctor.enteredBy',{name:plan.doctorName??''}):t('familyMode.recordedPlan')}</p>{plan.effectiveDate&&<p>{t('doctor.effectiveDate')}: {plan.effectiveDate}</p>}<dl className="reading-grid">{plan.dryWeightKg!=null&&<div><dt>{t('doctor.dryWeight')}</dt><dd>{plan.dryWeightKg} kg</dd></div>}{plan.fluidLimitL!=null&&<div><dt>{t('doctor.fluidLimit')}</dt><dd>{plan.fluidLimitL} L</dd></div>}</dl>{plan.saltAdvice&&<p>{t('doctor.salt')}: {plan.saltAdvice}</p>}{plan.followUp&&<p>{t('doctor.followUp')}: {plan.followUp}</p>}</div>;
}
export function SharedPlan({demo}:{demo:DemoController}){const {t}=useTranslation(),plan=demo.state.patient?.plan;if(!plan)return null;return <section className="family-card"><h2>{t('familyMode.plan')}</h2><PlanMetadata plan={plan}/><h3>{t('familyMode.amberPlan')}</h3><ul className="reason-list">{plan.amber.map(s=><li key={s}>{s}</li>)}</ul><h3>{t('familyMode.redPlan')}</h3><ul className="reason-list">{plan.red.map(s=><li key={s}>{s}</li>)}</ul></section>;}
export function SharedNotes({demo}:{demo:DemoController}){
 const {t}=useTranslation(),date=demo.state.checkins[demo.state.cursor]?.date,notes=demo.doctor.notes.filter(n=>n.patientId===demo.state.patient?.id&&n.date<=date).sort((a,b)=>b.date.localeCompare(a.date)||b.at.localeCompare(a.at));
 if(!notes.length)return null;
 return <section className="family-card"><h2>{t('doctor.sharedNotes')}</h2>{notes.map(n=><article className="consult-note" key={n.id}><strong>{n.date} · {n.doctorName}</strong><p>{n.text}</p></article>)}</section>;
}
