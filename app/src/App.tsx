import {speakOffline,stopSpeech} from './voice/speech';
import {lazy,Suspense} from 'react';
import {languages,speechSupported} from './i18n/languages';
import {setLanguage} from './i18n';
import {DisplaySettings,initialTheme,type Theme} from './accessibility';
const Devices=lazy(()=>import('./device/Devices').then(m=>({default:m.Devices})));
const Reports=lazy(()=>import('./reports/Reports').then(m=>({default:m.Reports})));
const DoctorExperience=lazy(()=>import('./doctor/DoctorExperience').then(m=>({default:m.DoctorExperience})));
import {planText} from './doctor/SharedCare';
const AshaExperience=lazy(()=>import('./asha/AshaExperience').then(m=>({default:m.AshaExperience})));
const FamilyExperience=lazy(()=>import('./family/FamilyExperience').then(m=>({default:m.FamilyExperience})));
import type {ElderScreen} from './elder/ElderExperience';
const ElderExperience=lazy(()=>import('./elder/ElderExperience').then(m=>({default:m.ElderExperience})));
const RoutineSettings=lazy(()=>import('./elder/ElderExperience').then(m=>({default:m.RoutineSettings})));
import {useDemo} from './data/useDemo';
import {DemoPanel,DemoSummary,displayStatus} from './data/DemoPanel';
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import * as Dialog from '@radix-ui/react-dialog';
import { useRegisterSW } from 'virtual:pwa-register/react';
import { HeartPulse, Home, Users, Settings, Volume2, ArrowRight, Pill, Phone, ShieldPlus, Bluetooth, Watch, Check, Download, X, Stethoscope, ClipboardList, Sprout, WifiOff } from 'lucide-react';
import { BigActionButton, MicButton, StatusOrb } from './components';
import { roles, storedRole, savePreference, type Role } from './preferences';

type InstallEvent=Event & {prompt:()=>Promise<void>;userChoice:Promise<{outcome:string}>};
type Page='home'|'team'|'settings'|'reports'|'devices';
function readPref(key:string) {try{return localStorage.getItem('saathi.'+key);}catch{return null;}}
export function App() {
 const {t,i18n}=useTranslation();
 const demo=useDemo();
 const [theme,setTheme]=useState<Theme>(initialTheme);
 const active=demo.unlocked&&demo.state.patient!==null;
 const [welcome,setWelcome]=useState(readPref('started')!=='true');
 const [role,setRole]=useState<Role>(storedRole(readPref('role')));
 const [page,setPage]=useState<Page>('home');
 useEffect(()=>{document.documentElement.dataset.theme=role==='elder'?'contrast':theme;},[theme,role]);
 const [elderScreen,setElderScreen]=useState<ElderScreen>(null);
 const [modal,setModal]=useState<string|null>(null);
 const [notice,setNotice]=useState('');
 const [online,setOnline]=useState(navigator.onLine);
 const [controlled,setControlled]=useState(Boolean(navigator.serviceWorker?.controller));
 const [install,setInstall]=useState<InstallEvent|null>(null);
 const {offlineReady:[ready],needRefresh:[refresh],updateServiceWorker}=useRegisterSW();
 useEffect(()=>{
  const update=()=>setOnline(navigator.onLine);
  const capture=(event:Event)=>{event.preventDefault();setInstall(event as InstallEvent);};
  const control=()=>setControlled(Boolean(navigator.serviceWorker?.controller));
  navigator.serviceWorker?.addEventListener('controllerchange',control);
  window.addEventListener('online',update);window.addEventListener('offline',update);window.addEventListener('beforeinstallprompt',capture);
  return ()=>{navigator.serviceWorker?.removeEventListener('controllerchange',control);window.removeEventListener('online',update);window.removeEventListener('offline',update);window.removeEventListener('beforeinstallprompt',capture);};
 },[]);
 useEffect(()=>{if(!active)return;const id=setInterval(()=>{if(document.visibilityState==='visible'&&!demo.busy){const time=new Intl.DateTimeFormat('en-GB',{timeZone:'Asia/Kolkata',hour:'2-digit',minute:'2-digit',hourCycle:'h23'}).format(new Date());void demo.reminders(time);}},60000);return()=>clearInterval(id);},[active,demo.state.patient?.id,demo.state.cursor,demo.busy,demo.family.doses,demo.family.medicines]);
 useEffect(()=>{stopSpeech();window.scrollTo({top:0,left:0,behavior:'instant'});},[page,role]);
 useEffect(()=>{document.documentElement.lang=i18n.language;stopSpeech();},[i18n.language]);
 function persist(key:string,value:string){if(!savePreference(key,value))setNotice(t('localWarning'));}
 function language(lang:string){void setLanguage(lang).then(()=>persist('language',lang)).catch(()=>setNotice(t('polish.languageFailed')));}
 function chooseRole(next:Role){setRole(next);persist('role',next);setPage('home');}
 function speak(text:string,lang=i18n.language){
  void speakOffline(text,lang).then(result=>{if(result==='unavailable')setNotice(t('polish.audioUnavailable'));}).catch(()=>setNotice(t('voice.failed')));
 }
 useEffect(()=>{return()=>stopSpeech();},[]);
 useEffect(()=>{const hide=()=>stopSpeech();window.addEventListener('pagehide',hide);return()=>window.removeEventListener('pagehide',hide);},[]);
 async function installApp(){if(install){await install.prompt();await install.userChoice;setInstall(null);}else setModal('install');}
 const roleIcons={elder:HeartPulse,family:Users,asha:ClipboardList,doctor:Stethoscope};
 const RoleIcon=roleIcons[role];
 const dialogText=modal==='check'?t('checkPending'):modal==='medicine'?t('medPending'):modal==='family'?t('familyPending'):modal==='voice'?t('voice.text'):modal==='sos'?t('helpText'):t('installHelp');
 const dialogTitle=modal==='voice'?t('voice.title'):modal==='sos'?t('helpTitle'):modal==='install'?t('installTitle'):t('pendingTitle');
 return <div data-theme={role==='elder'?'contrast':theme} className={role==='elder'?'app elder':'app'}>
  <a className="skip-link" href="#main">{t('skip')}</a>
  {welcome?<main className="welcome" id="main">
   <div className="wordmark"><span className="logo"><HeartPulse/></span><span>{t('brand')}<small>{t('by')}</small></span></div>
   <div className="welcome-art" aria-hidden="true"><div className="art-orbit"/><HeartPulse size={80} strokeWidth={1.3}/><span className="art-leaf"><Sprout/></span></div>
   <span className="eyebrow">{t('tagline')}</span><h1>{t('welcome')}</h1><p>{t('intro')}</p>
   <fieldset className="language-picker"><legend>{t('choose')}</legend>
    {languages.map(([code,label])=><div className={'language-choice '+(i18n.language===code?'selected':'')} key={code}><button lang={code} aria-pressed={i18n.language===code} onClick={()=>language(code)}>{label}{i18n.language===code&&<Check size={22}/>}</button><button className="listen-language" aria-label={code==='hi'?'हिन्दी सुनें':code==='en'?'Listen in English':'Listen: '+label} onClick={()=>speak(code==='hi'?'नमस्ते। हिंदी चुनें।':code==='en'?'Welcome. Choose English.':label,code)}><Volume2 size={22}/></button></div>)}
   </fieldset>
   <button className="primary start" onClick={()=>{persist('started','true');setWelcome(false);}}>{t('start')}<ArrowRight/></button>
   {!speechSupported(i18n.language)&&<p className="translation-notice">{t('polish.draft')} <span lang="en">Needs review</span></p>}<p className="welcome-note">{t('demo')}<br/>{t('privacy')}</p>
  </main>:<>
   <aside className="sidebar">
    <div className="wordmark"><span className="logo"><HeartPulse/></span><span>{t('brand')}<small>{t('by')}</small></span></div>
    <p className="side-tag">{t('tagline')}</p>
    <nav aria-label={t('home')}>{(['home','team','settings'] as Page[]).map(item=>{const Icon=item==='home'?Home:item==='team'?Users:Settings;return <button key={item} className={page===item?'active':''} aria-current={page===item?'page':undefined} onClick={()=>setPage(item)}><Icon size={23}/>{t(item)}</button>;})}</nav>
    <div className="side-bottom"><div className="soft-symbol"><Sprout size={32}/></div><strong>{t('learn')}</strong><p>{t('learnText')}</p><span className="phase-label">{t('phase')}</span></div>
   </aside>
   <div className="workspace">
    <header className="topbar"><span className="mobile-brand"><HeartPulse size={27}/>{t('brand')}</span><span className="desktop-title">{t('foundation')}</span><div className="top-actions"><span className="connection">{online?<span className="connection-dot"/>:<WifiOff size={16}/>}<span>{online?t('online'):t('offline')}</span></span><button className="language-toggle" onClick={()=>language(i18n.language==='en'?'hi':'en')}>{t('switchLanguage')}</button></div></header>
    <main id="main" className="content">
     <div className="demo-label"><span/>{t('demo')}</div>{!speechSupported(i18n.language)&&<p className='translation-notice' role='note'>{t('polish.draft')} <span lang='en'>Needs review</span></p>}{demo.routine.pendingHelp&&<p className="pending-notice" role="status">{t('elder.pendingHelp')}</p>}
     {role!=='elder'&&<button className='secondary' onClick={()=>setPage('reports')}>{i18n.language==='hi'?'रिपोर्ट':'Reports'}</button>}<button className='secondary' onClick={()=>setPage('devices')}>{i18n.language==='hi'?'उपकरण कनेक्शन':'Device connection'}</button>{page==='devices'?<Suspense fallback={<p role="status">{t('polish.loading')}</p>}><Devices demo={demo}/></Suspense>:page==='reports'?<Suspense fallback={<p role="status">{t('polish.loading')}</p>}><Reports demo={demo}/></Suspense>:page==='home'?<>
      <div className="page-heading"><div><p>{t('greeting')}</p><h1>{role==='elder'?t('name'):t('roles.'+role)}</h1></div><button className="read-button" aria-label={t('read')} onClick={()=>speak(role==='elder'?[t('greeting'),active?t('vault.historical'):t('checkText'),active?t('status.'+displayStatus(demo.state.checkins[demo.state.cursor])):'',active?planText(demo.state.patient?.plan,demo.state.checkins[demo.state.cursor]?.result.light??0,t):'',t('disclaimer')].filter(Boolean).join('. '):active?[demo.state.patient?.name,t('vault.historical'),demo.state.checkins[demo.state.cursor]?.date,t('status.'+displayStatus(demo.state.checkins[demo.state.cursor])),t('disclaimer')].filter(Boolean).join('. '):t('emptyText'))}><Volume2 size={22}/><span>{t('listen')}</span></button></div>
      {role==='elder'?<div className="home-grid">
       {active?<DemoSummary demo={demo}/>:<>       <section className="check-card" aria-labelledby="check-title"><div className="card-heading"><span className="eyebrow">{t('today')}</span><HeartPulse size={23}/></div><StatusOrb status={demo.exists&&!demo.unlocked?'locked':'unknown'}/><h2 id="check-title">{t('checkTitle')}</h2><p>{demo.exists&&!demo.unlocked?t('vault.locked'):t('checkText')}</p><button className="primary" onClick={()=>setModal('check')}>{t('check')}<ArrowRight size={24}/></button><p className="disclaimer">{t('disclaimer')}</p></section></>}
       <div className="actions-column">{active&&<BigActionButton icon={<ClipboardList/>} onClick={()=>setElderScreen('questions')}>{t('elder.questions')}</BigActionButton>}<BigActionButton icon={<Pill/>} detail={t('medicineDetail')} onClick={()=>setElderScreen('medicine')}>{t('medicines')}</BigActionButton><BigActionButton icon={<Phone/>} detail={t('familyDetail')} onClick={()=>setElderScreen('family')}>{t('family')}</BigActionButton><BigActionButton icon={<ShieldPlus/>} detail={t('sosDetail')} tone="help" onClick={()=>setElderScreen('sos')}>{t('sos')}</BigActionButton><div className="routine"><Sprout size={30}/><div><h2>{t('routine')}</h2><p>{t('routineText')}</p></div></div></div>
       <section className="devices-card"><h2>{t('devices')}</h2><div className="device-grid">{[{label:'platform',Icon:Bluetooth},{label:'amulet',Icon:Watch}].map(({label,Icon})=><div className="device" key={label}><span className="device-icon"><Icon size={25}/></span><div><strong>{t(label)}</strong><span>{t('notConnected')}</span></div></div>)}</div><p>{t('devicesText')}</p></section>
      </div>:role==='family'?<Suspense fallback={<p role="status">{t('polish.loading')}</p>}><FamilyExperience demo={demo} openSettings={()=>setPage('settings')}/></Suspense>:role==='asha'?<Suspense fallback={<p role="status">{t('polish.loading')}</p>}><AshaExperience demo={demo} openSettings={()=>setPage('settings')}/></Suspense>:role==='doctor'?<Suspense fallback={<p role="status">{t('polish.loading')}</p>}><DoctorExperience demo={demo} openSettings={()=>setPage('settings')}/></Suspense>:active?<DemoSummary demo={demo}/>:<section className="role-preview"><div className="role-illustration"><RoleIcon size={64}/></div><span className="eyebrow">{t('roles.'+role)}</span><h2>{t('emptyTitle')}</h2><p>{t('emptyText')}</p><div className="next-card"><span className="eyebrow">{t('next')}</span><strong>{t(role+'Next')}</strong></div><p className="disclaimer">{t('disclaimer')}</p></section>}
     </>:page==='team'?<><div className="page-heading"><h1>{t('teamTitle')}</h1></div><p>{t('teamText')}</p><div className="role-grid">{roles.map(r=>{const Icon=roleIcons[r];return <button className="role-card" key={r} onClick={()=>chooseRole(r)}><Icon size={32}/><strong>{t('roles.'+r)}</strong><span>{t('roleDescriptions.'+r)}</span><ArrowRight size={22}/></button>;})}</div></>:<><div className="page-heading"><h1>{t('settings')}</h1></div><DemoPanel demo={demo}/><DisplaySettings onTheme={setTheme}/><Suspense fallback={<p role="status">{t('polish.loading')}</p>}><RoutineSettings demo={demo}/></Suspense><section className="settings-card"><h2>{t('role')}</h2><p>{t('roleHelp')}</p><div className="role-options">{roles.map(r=><button key={r} aria-pressed={role===r} onClick={()=>chooseRole(r)}>{t('roles.'+r)}</button>)}</div><h2>{t('language')}</h2><div className="role-options">{languages.map(([code,label])=><button key={code} lang={code} aria-pressed={i18n.language===code} onClick={()=>language(code)}>{label}{!speechSupported(code)&&<small> · {t('polish.needsReview')}</small>}</button>)}</div><p>{t('noRecords')}</p><p>{t('speechLocal')}</p><button className="secondary" onClick={()=>setWelcome(true)}>{t('setupAgain')}</button><button className="secondary" onClick={()=>void installApp()}><Download size={20}/>{t('install')}</button></section></>}
     <footer className="footer"><div><span className={'ready-dot '+(ready||controlled?'ready':'')}/><span data-testid="offline-status">{ready||controlled?t('offlineReady'):t('preparing')}</span></div><p>{t('disclaimer')} {t('emergency')}</p></footer>
    </main>
    <nav className="mobile-nav" aria-label={t('home')}>{(['home','team','settings'] as Page[]).map(item=>{const Icon=item==='home'?Home:item==='team'?Users:Settings;return <button key={item} aria-current={page===item?'page':undefined} onClick={()=>setPage(item)}><Icon size={24}/><span>{t(item)}</span></button>;})}{role==='elder'&&page==='home'&&<MicButton onClick={()=>setElderScreen('voice')}/>}</nav>
   </div>
   {role==='elder'&&page==='home'&&<div className="voice-dock"><MicButton onClick={()=>setElderScreen('voice')}/></div>}
  </>}
  {notice&&<div className="notice" role="status"><span>{notice}</span><button aria-label={t('close')} onClick={()=>setNotice('')}><X/></button></div>}
  {refresh&&<div className="update-banner" role="status">{t('update')}<button onClick={()=>void updateServiceWorker(true)}>{t('reload')}</button></div>}
  {!welcome&&role==='elder'&&<Suspense fallback={<p role='status'>{t('polish.loading')}</p>}><ElderExperience enabled={role==='elder'} demo={demo} screen={elderScreen} setScreen={setElderScreen} speak={speak}/></Suspense>}
  <Dialog.Root open={modal!==null} onOpenChange={open=>{if(!open)setModal(null);}}>
   <Dialog.Portal><Dialog.Overlay className="dialog-overlay"/><Dialog.Content className="dialog-content"><Dialog.Title>{dialogTitle}</Dialog.Title><Dialog.Description>{dialogText}</Dialog.Description>
    {modal==='check'&&<button className="primary" onClick={()=>{setModal(null);setRole('family');setPage('settings');}}>{t('vault.open')}</button>}
    {modal==='sos'&&<><a className="primary" href="tel:108">{t('call108')}<Phone size={22}/></a><p className="disclaimer">{t('disclaimer')}</p></>}
    {modal==='voice'&&<button className="primary" onClick={()=>speak([active?t('vault.historical'):t('checkText'),active?t('status.'+displayStatus(demo.state.checkins[demo.state.cursor])):'',active?planText(demo.state.patient?.plan,demo.state.checkins[demo.state.cursor]?.result.light??0,t):'',t('disclaimer')].filter(Boolean).join('. '))}><Volume2/>{t('read')}</button>}
    <Dialog.Close className="secondary">{t('close')}</Dialog.Close>
   </Dialog.Content></Dialog.Portal>
  </Dialog.Root>
 </div>;
}







