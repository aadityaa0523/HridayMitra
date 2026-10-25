import {speechSupported} from '../i18n/languages';
import {stopSpeech,isSpeaking} from '../voice/speech';
import {planText} from '../doctor/SharedCare';
import {dosesFor} from '../family/model';
import {useEffect,useRef,useState} from 'react';
import * as Dialog from '@radix-ui/react-dialog';
import {useTranslation} from 'react-i18next';
import {Mic,Volume2,Phone,Pill,Check} from 'lucide-react';
import type {DemoController} from '../data/useDemo';
import {matchIntent,type Intent} from '../voice/intents';
import {OfflineVoice,hasPack,installPack,deletePacks} from '../voice/offline';

export type ElderScreen='medicine'|'questions'|'voice'|'sos'|'family'|'alarm'|null;
type Props={enabled?:boolean;demo:DemoController;screen:ElderScreen;setScreen:(screen:ElderScreen)=>void;speak:(text:string)=>void};
export function ElderExperience({enabled=true,demo,screen,setScreen,speak}:Props){
 const {t,i18n}=useTranslation();
 const [selectedDose,setSelectedDose]=useState<string|null>(null);
 const [question,setQuestion]=useState(0),[first,setFirst]=useState<0|1|null>(null),[confirmDose,setConfirmDose]=useState(false);
 const [count,setCount]=useState<number|null>(null),[helpReady,setHelpReady]=useState(false);
 const [feedback,setFeedback]=useState(''),[transcript,setTranscript]=useState(''),[listening,setListening]=useState(false),[voiceBusy,setVoiceBusy]=useState(false),[pack,setPack]=useState(false);
 const voice=useRef(new OfflineVoice()).current,hold=useRef<ReturnType<typeof setTimeout>|null>(null),timer=useRef<ReturnType<typeof setTimeout>|null>(null);
 const listenGeneration=useRef(0);
 const finalAt=useRef({text:'',at:0}),online=useRef<{stop:()=>void}|null>(null);
 const context=useRef({screen,question,first,confirmDose,demo});context.current={screen,question,first,confirmDose,demo};
 const scheduledDoses=demo.state.patient&&demo.state.checkins[demo.state.cursor]?dosesFor(demo.family,demo.state.patient.id,demo.state.checkins[demo.state.cursor].date):[];
 const target=scheduledDoses.find(d=>d.id===selectedDose)??(scheduledDoses.length===1?scheduledDoses[0]:null);
 const active=enabled&&demo.unlocked&&!!demo.state.patient,date=demo.state.checkins[demo.state.cursor]?.date;
 const stop=()=>{listenGeneration.current++;voice.stop();online.current?.stop();online.current=null;setListening(false);setVoiceBusy(false);if(timer.current)clearTimeout(timer.current);};
 function say(key:string){const text=t(key);setFeedback(text);speak(text);navigator.vibrate?.(60);}
 const cancelHold=()=>{if(hold.current)clearTimeout(hold.current);hold.current=null;};
 useEffect(()=>{void hasPack(i18n.language).then(setPack).catch(()=>setPack(false));stop();return()=>{voice.stop();online.current?.stop();cancelHold();if(timer.current)clearTimeout(timer.current);};},[i18n.language]);
 useEffect(()=>{if(screen==='voice')void hasPack(i18n.language).then(setPack).catch(()=>setPack(false));},[screen,i18n.language]);
 useEffect(()=>{if(screen==='questions'&&question===0)speak(t('elder.q1'));return()=>stopSpeech();},[screen]);
 useEffect(()=>{if(!screen){stop();setCount(null);setHelpReady(false);setConfirmDose(false);setFeedback('');setTranscript('');}},[screen]);
 useEffect(()=>{setQuestion(0);setFirst(null);setSelectedDose(null);setConfirmDose(false);if(!active){stop();if(screen==='medicine'||screen==='questions'||screen==='alarm')setScreen(null);}},[active,date]);
 useEffect(()=>{const hide=()=>{stop();cancelHold();setCount(null);setHelpReady(false);};window.addEventListener('pagehide',hide);return()=>window.removeEventListener('pagehide',hide);},[]);
 useEffect(()=>{
  if(count===null||count===0)return;
  const id=setTimeout(()=>setCount(n=>n===null?null:n-1),1000);return()=>clearTimeout(id);
 },[count]);
 useEffect(()=>{if(count===0){setHelpReady(true);setCount(null);say('elder.helpReady');}},[count]);
 useEffect(()=>{
  if(!active)return;
  const check=()=>{
   if(document.visibilityState!=='visible')return;
   const due=scheduledDoses.find(d=>d.state==='pending'&&d.dueAt!==null&&d.dueAt<=Date.now());
   if(due){if(due.snoozes>=3){if(!demo.busy)void demo.reminders('00:00');}else if(screen!=='alarm'){setSelectedDose(due.id);setScreen('alarm');say('familyMode.scheduledReminder');}return;}
   if(scheduledDoses.length)return;
   const dose=demo.routine.dose;
   if(dose?.state==='pending'&&dose.dueAt!==null&&Date.now()>=dose.dueAt){
    if(dose.snoozes>=3){if(!demo.busy)void demo.dose('expire');}
    else if(screen!=='alarm'){setScreen('alarm');say('elder.reminder');}
   }
  };
  const id=setInterval(check,1000);return()=>clearInterval(id);
 },[active,demo.routine.dose,demo.family.doses,demo.family.medicines,demo.busy,screen]);
 useEffect(()=>{
  if(screen!=='alarm')return;
  const id=setInterval(()=>{if(document.visibilityState==='visible')say('elder.reminder');},30000);
  return()=>clearInterval(id);
 },[screen,i18n.language]);
 function startSOS(){cancelHold();setScreen('sos');setHelpReady(false);setCount(5);say('elder.countdown');}
 async function take(source:'tap'|'voice'){
  if(!active){say('elder.unlock');return;}
  if(scheduledDoses.length&&!target){say('elder.selectDose');return;}
  if(await (target?demo.scheduledDose(target.id,'take',source):demo.dose('take',source))){setConfirmDose(false);say(target?'familyMode.doseTaken':'elder.taken');if(screen==='alarm')setScreen('medicine');}
 }
 async function answer(value:0|1,source:'tap'|'voice'){
  const c=context.current;
  if(c.screen!=='questions'||!c.demo.unlocked)return;
  if(c.question===0){setFirst(value);setQuestion(1);speak(t('elder.q2'));}
  else if(c.first!==null&&await c.demo.answers(c.first,value,source)){setQuestion(2);say('elder.saved');}
 }
 function execute(intent:Intent|null){
  const c=context.current;
  if(!intent){say('elder.unknown');return;}
  if(intent==='cancel'){setCount(null);setHelpReady(false);setConfirmDose(false);setScreen(null);stopSpeech();return;}
  if(intent==='sos'){startSOS();return;}
  if(intent==='go_home'){setScreen(null);return;}
  if(intent==='medicine_next'){setScreen('medicine');say(scheduledDoses.length?'familyMode.chooseDose':'elder.practice');return;}
  if(intent==='medicine_taken'){
   if(!active){say('elder.unlock');return;}
   if(c.screen!=='medicine'&&c.screen!=='alarm'){setScreen('medicine');say('elder.selectDose');return;}
   if((target??demo.routine.dose)?.state==='taken'){say(target?'familyMode.doseTaken':'elder.taken');return;}
   if(scheduledDoses.length&&!target){say('familyMode.chooseDose');return;}
   setConfirmDose(true);say(target?'familyMode.confirmDose':'elder.confirmTaken');return;
  }
  if(intent==='answer_yes'||intent==='answer_no'){
   if(c.confirmDose){if(intent==='answer_yes')void take('voice');else setConfirmDose(false);return;}
   if(c.screen==='questions'){void answer(intent==='answer_yes'?1:0,'voice');return;}
   say('elder.noQuestion');return;
  }
  if(intent==='start_checkin'){setQuestion(0);setFirst(null);setScreen('questions');speak(t('elder.q1'));return;}
  if(intent==='call_family'||intent==='call_asha'){setScreen('family');say('elder.chooseContact');return;}
  if(intent==='water_left'){const limit=demo.state.patient?.plan?.fluidLimitL;if(limit!=null){const text=t('doctor.fluidLimit')+': '+limit+' L. '+t('doctor.noIntakeLog');setFeedback(text);speak(text);}else say('elder.noWater');return;}
  if(intent==='repeat'){speak(feedback||t('elder.voiceHelp'));return;}
  if(intent==='read_screen'&&screen){speak(document.querySelector('.elder-dialog')?.textContent||t('elder.voiceHelp'));return;}
  if(intent==='status_today'||intent==='read_screen'){
   const row=demo.state.checkins[demo.state.cursor];
   const status=row?(row.result.light===2?'red':row.result.light===1?'amber':row.result.learning?'learning':'green'):'unknown';
   speak(screen==='questions'?t(question===0?'elder.q1':'elder.q2'):active?t('vault.historical')+'. '+t('status.'+status)+'. '+(row?.deviceWhy||row?.result.reasons.map(r=>t('reason.'+r.signal)).join('. ')||'')+'. '+planText(demo.state.patient?.plan,row?.result.light??0,t)+'. '+t('disclaimer'):t('elder.unlock'));
  }
 }
 const executeRef=useRef(execute);executeRef.current=execute;
 function onText(text:string,final:boolean){
  setTranscript(text);
  if(!final||!text.trim())return;
  if(finalAt.current.text===text&&Date.now()-finalAt.current.at<2000)return;
  finalAt.current={text,at:Date.now()};
  const intent=matchIntent(text,i18n.language);
  if(isSpeaking()&&intent!=='cancel')return;
  executeRef.current(intent);
 }
 async function listen(){
  if(listening){stop();return;}
  stopSpeech();setVoiceBusy(true);setFeedback('');const generation=++listenGeneration.current;
  try{const started=await voice.start(i18n.language,onText);if(started&&generation===listenGeneration.current){setListening(true);timer.current=setTimeout(stop,60000);}}
  catch{if(generation===listenGeneration.current)say('elder.voiceFailed');}finally{if(generation===listenGeneration.current)setVoiceBusy(false);}
 }
 function listenOnline(){
  type Recognition={lang:string;continuous:boolean;interimResults:boolean;onresult:((e:{results:{isFinal:boolean;[key:number]:{transcript:string}}[];resultIndex:number})=>void)|null;onerror:(()=>void)|null;onend:(()=>void)|null;start:()=>void;stop:()=>void};
  const api=window as unknown as {SpeechRecognition?:new()=>Recognition;webkitSpeechRecognition?:new()=>Recognition};
  const Constructor=api.SpeechRecognition??api.webkitSpeechRecognition;
  if(!navigator.onLine||!Constructor){say('elder.voiceFailed');return;}
  stop();stopSpeech();
  const recognition=new Constructor();recognition.lang=i18n.language==='hi'?'hi-IN':'en-IN';recognition.continuous=true;recognition.interimResults=true;
  recognition.onresult=e=>{const row=e.results[e.resultIndex];onText(row[0].transcript,row.isFinal);};
  recognition.onerror=()=>{stop();say('elder.voiceFailed');};recognition.onend=()=>setListening(false);
  online.current=recognition;try{recognition.start();setListening(true);timer.current=setTimeout(stop,60000);}catch{stop();say('elder.voiceFailed');}
 }
 const title=screen==='medicine'?t('medicines'):screen==='questions'?t('elder.questions'):screen==='sos'?t('helpTitle'):screen==='family'?t('family'):screen==='alarm'?t(scheduledDoses.length?'familyMode.alarmTitle':'elder.reminder'):t('voice.title');
 return <Dialog.Root open={screen!==null} onOpenChange={open=>{if(!open)setScreen(null);}}><Dialog.Portal><Dialog.Overlay className="dialog-overlay"/><Dialog.Content className={'dialog-content elder-dialog '+(screen==='alarm'?'alarm-screen':'')} onEscapeKeyDown={()=>{setCount(null);cancelHold();}}>
  <Dialog.Title>{title}</Dialog.Title><Dialog.Description>{t(screen==='sos'?'helpText':'elder.practice')}</Dialog.Description>
  {demo.failed&&<p role="alert">{t('vault.failed')}</p>}
  {!active&&['medicine','questions','alarm'].includes(screen??'')?<p>{t('elder.unlock')}</p>:<>
  {(screen==='medicine'||screen==='alarm')&&<>
   {scheduledDoses.length?<><p>{t('familyMode.chooseDose')}</p>{scheduledDoses.map(d=>{const medicine=demo.family.medicines.find(m=>m.id===d.medicineId)!;return <button className={'scheduled-dose secondary '+(target?.id===d.id?'selected':'')} key={d.id} aria-pressed={target?.id===d.id} onClick={()=>{setSelectedDose(d.id);setConfirmDose(false);}}>{medicine.photo?<img className="tablet-photo" src={medicine.photo} alt=""/>:<Pill/>}<span><strong>{medicine.name} · {medicine.strength}</strong><small>{d.time} · {t('familyMode.food_'+medicine.food)} · {d.units} {t('familyMode.unitsShort')}</small><small>{t('familyMode.dose_'+d.state)}</small></span></button>;})}</>:<><div className="practice-pill" aria-hidden="true"><Pill size={54}/></div><h3>{t('elder.tablet')}</h3><p>{t('elder.notPrescription')}</p></>}
   {(target??demo.routine.dose)?.state==='taken'?<p className="success-note"><Check/>{t(scheduledDoses.length?'familyMode.doseTaken':'elder.taken')}</p>:<>
    {confirmDose?<><p>{t(scheduledDoses.length?'familyMode.confirmDose':'elder.confirmTaken')}</p><button className="primary" disabled={demo.busy} onClick={()=>void take('tap')}>{t('elder.yes')}</button><button className="secondary" onClick={()=>setConfirmDose(false)}>{t('elder.no')}</button></>:<button className="primary" disabled={demo.busy||(scheduledDoses.length>0&&!target)} onClick={()=>void take('tap')}>{t('elder.markTaken')}</button>}
    {screen==='alarm'?<button className="secondary" disabled={demo.busy||((target??demo.routine.dose)?.snoozes??0)>=3} onClick={async()=>{if(await (target?demo.scheduledDose(target.id,'snooze'):demo.dose('snooze'))){setScreen('medicine');say('elder.snoozed');}}}>{t('elder.snooze')} ({(target??demo.routine.dose)?.snoozes??0}/3)</button>:<button className="secondary" disabled={demo.busy||(scheduledDoses.length>0&&!target)} onClick={()=>void (target?demo.scheduledDose(target.id,'remind'):demo.dose('remind'))}>{t('elder.tryAlarm')}</button>}
   </>}
   {demo.routine.pendingHelp&&<p role="status">{t('elder.pendingHelp')}</p>}<p className="capability-note">{t('elder.foreground')}</p>
  </>}
  {screen==='questions'&&<>
   {demo.routine.answers&&<p>{t('elder.saved')}</p>}{question<2?<><div className="question-step">{question+1} / 2</div><h3>{t(question===0?'elder.q1':'elder.q2')}</h3><div className="yes-no"><button className="primary" disabled={demo.busy} onClick={()=>void answer(1,'tap')}>{t('elder.yes')}</button><button className="secondary" disabled={demo.busy} onClick={()=>void answer(0,'tap')}>{t('elder.no')}</button></div></>:<p className="success-note"><Check/>{t('elder.saved')}</p>}
   <p>{t('elder.answersScope')}</p>
  </>}
  </>}
  {(screen==='sos'||screen==='family')&&<>
   {screen==='sos'&&!helpReady&&count===null&&<button className="primary sos-hold" onPointerDown={e=>{e.currentTarget.setPointerCapture(e.pointerId);cancelHold();hold.current=setTimeout(startSOS,2000);}} onPointerUp={cancelHold} onPointerCancel={cancelHold} onLostPointerCapture={cancelHold} onKeyDown={e=>{if((e.key===' '||e.key==='Enter')&&!e.repeat){e.preventDefault();cancelHold();hold.current=setTimeout(startSOS,2000);}}} onKeyUp={cancelHold} onBlur={cancelHold}>{t('elder.hold')}</button>}
   {count!==null&&<div role="status"><strong className="countdown-number">{count}</strong><p>{t('elder.countdown')}</p><button className="primary" onClick={()=>{setCount(null);setHelpReady(false);setScreen(null);stopSpeech();}}>{t('elder.cancel')}</button></div>}
   {(screen==='family'||helpReady)&&<><p>{t('elder.chooseContact')}</p>{demo.routine.contacts.length?demo.routine.contacts.map(c=><a className="secondary" key={c.id} href={'tel:'+c.phone}><Phone size={22}/>{c.name}</a>):<p>{t('elder.noContacts')}</p>}<p>{t('elder.noAuto')}</p></>}
   <a className="secondary" href="tel:108">{t('call108')}</a><p className="disclaimer">{t('disclaimer')}</p>
  </>}
  {screen==='voice'&&<>{!speechSupported(i18n.language)&&<p>{t('polish.voiceLanguages')}</p>}<p>{t('elder.voiceHelp')}</p><p>{t('elder.packText')}</p>{!pack&&<button className="secondary" disabled={voiceBusy||!speechSupported(i18n.language)} onClick={async()=>{setVoiceBusy(true);try{await installPack(i18n.language);setPack(true);say('elder.packReady');}catch{say('elder.packFailed');}finally{setVoiceBusy(false);}}}>{voiceBusy?t('vault.busy'):t('elder.installPack')}</button>}<button className="secondary" disabled={voiceBusy||!speechSupported(i18n.language)} onClick={()=>listenOnline()}>{t('elder.onlineVoice')}</button><p className="capability-note">{t('elder.onlinePrivacy')}</p></>}
  <div className="voice-actions"><button className="secondary" disabled={!pack||voiceBusy} aria-pressed={listening} onClick={()=>void listen()}><Mic size={22}/>{voiceBusy?t('vault.busy'):t(listening?'elder.stopMic':'elder.startMic')}</button><button className="secondary" onClick={()=>execute('read_screen')}><Volume2 size={22}/>{t('listen')}</button></div>
  {transcript&&<p className="transcript" aria-live="polite">{transcript}</p>}{feedback&&<p role="status">{feedback}</p>}
  <Dialog.Close className="secondary">{t('close')}</Dialog.Close>
 </Dialog.Content></Dialog.Portal></Dialog.Root>;
}

export function RoutineSettings({demo}:{demo:DemoController}){
 const {t}=useTranslation(),[name,setName]=useState(''),[phone,setPhone]=useState(''),[role,setRole]=useState<'family1'|'family2'|'asha'>('family1'),[message,setMessage]=useState('');
 if(!demo.unlocked||!demo.state.patient)return null;
 return <section className="settings-card"><h2>{t('elder.contactSetup')}</h2><p>{t('elder.contactPrivacy')}</p><form onSubmit={async e=>{e.preventDefault();if(await demo.contact(role,name,phone)){setName('');setPhone('');setMessage(t('elder.contactSaved'));}}}>
  <label>{t('elder.contactRole')}<select value={role} onChange={e=>setRole(e.target.value as typeof role)}><option value="family1">{t('elder.family1')}</option><option value="family2">{t('elder.family2')}</option><option value="asha">{t('roles.asha')}</option></select></label>
  <label>{t('elder.contactName')}<input value={name} maxLength={80} required onChange={e=>setName(e.target.value)}/></label>
  <label>{t('elder.contactPhone')}<input value={phone} type="tel" pattern="\+?[0-9]{7,15}" required onChange={e=>setPhone(e.target.value)}/></label>
  <button className="secondary" disabled={demo.busy}>{t('elder.saveContact')}</button></form>
  {message&&<p role="status">{message}</p>}<button className="secondary" onClick={()=>void deletePacks().then(()=>setMessage(t('elder.packsDeleted')))}>{t('elder.deletePacks')}</button>
 </section>;
}




