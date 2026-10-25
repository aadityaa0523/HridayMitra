import type {Report} from '../reports/model';
import {emptyDevices,loadDevices,createLinked,ingest,saveStatus,type DeviceKind} from '../device/model';
import type {Packet,Status} from '../device/protocol';
export type SavedReport={id:string;patientId:string;date:string;type:string;createdAt:string;sha256:string;pdf:string;report:Report};
import {emptyDoctor,loadDoctor,asOfPatient,savePlan,setSensitivity,saveLab,saveNote,assignPHC,type LabTest} from '../doctor/model';
import {loadAsha,emptyAsha,saveVisit,saveLocation,recordExport,saveDraft,saveExample,removeExample,type DraftFields,type VisitInput} from '../asha/model';
import {loadFamily,emptyFamily,saveMedicine,changeMedicine,scheduledAction,respondAlert,checkReminders,saveCareDetails,type Medicine} from '../family/model';
import {loadRoutine,noRoutine,actDose,saveAnswers,saveContact,type CareContact} from '../elder/routine';
import {useCallback,useEffect,useRef,useState} from 'react';
import {Vault} from './vault';
import {blankSnapshot,moveCursor,seedDemo,snapshot,selectPatient,addDemoPatient} from './model';
export function useDemo(){
 const vault=useRef(new Vault()).current;
 const [devices,setDevices]=useState(emptyDevices);
 const [doctor,setDoctor]=useState(emptyDoctor);
 const [asha,setAsha]=useState(emptyAsha);
 const [family,setFamily]=useState(emptyFamily);
 const [routine,setRoutine]=useState(noRoutine);
 const [state,setState]=useState(blankSnapshot),[exists,setExists]=useState(false),[unlocked,setUnlocked]=useState(false),[busy,setBusy]=useState(false),[failed,setFailed]=useState(false);
 const generation=useRef(0),inFlight=useRef(false);
 const lock=useCallback(()=>{generation.current++;vault.lock();setState(blankSnapshot());setRoutine(noRoutine());setFamily(emptyFamily());setAsha(emptyAsha());setDoctor(emptyDoctor());setDevices(emptyDevices());setUnlocked(false);},[vault]);
 useEffect(()=>{let live=true;void vault.exists().then(x=>{if(live)setExists(x);}).catch(()=>{if(live)setFailed(true);});const hide=()=>lock();window.addEventListener('pagehide',hide);return()=>{live=false;window.removeEventListener('pagehide',hide);};},[vault,lock]);
 async function run(operation:()=>Promise<void>){
  if(inFlight.current)return false;
  inFlight.current=true;setBusy(true);setFailed(false);const current=generation.current;
  try{await operation();const next=await snapshot(vault);const routine=next.patient&&next.checkins.length?await loadRoutine(vault,next.patient.id,next.checkins[next.cursor].date):noRoutine();const family=await loadFamily(vault),asha=await loadAsha(vault),doctor=await loadDoctor(vault),devices=await loadDevices(vault);if(next.patient&&next.checkins.length){const date=next.checkins[next.cursor].date;next.patients=next.patients.map(p=>asOfPatient(p,doctor,date));next.patient=next.patients.find(p=>p.id===next.patient?.id)??null;family.patients=family.patients.map(p=>asOfPatient(p,doctor,date));}if(current===generation.current){setDoctor(doctor);setDevices(devices);setAsha(asha);setFamily(family);setRoutine(routine);setState(next);setExists(true);setUnlocked(vault.unlocked);return true;}return false;}
  catch{if(current===generation.current){setFailed(true);if(!vault.unlocked){setState(blankSnapshot());setRoutine(noRoutine());setFamily(emptyFamily());setAsha(emptyAsha());setDoctor(emptyDoctor());setDevices(emptyDevices());setUnlocked(false);}}return false;}
  finally{inFlight.current=false;setBusy(false);}
 }
 function selection(){if(!state.patient||!state.checkins[state.cursor])throw new Error('No selected patient');return {patientId:state.patient.id,date:state.checkins[state.cursor].date};}
 return {state,routine,family,asha,doctor,devices,exists,unlocked,busy,failed,lock,
  createLinked:(wireId:string,mode:DeviceKind)=>run(()=>createLinked(vault,wireId,mode)),
  deviceImport:(patientId:string,mode:DeviceKind,packets:Packet[],date:string)=>run(()=>{if(patientId!==state.patient?.id)throw Error('Wrong context');return ingest(vault,patientId,mode,packets,date);}),
  deviceStatus:(patientId:string,mode:DeviceKind,status:Status)=>run(()=>{if(patientId!==state.patient?.id)throw Error('Wrong context');return saveStatus(vault,patientId,mode,status);}),
  savedReports:async()=>{const {patientId,date}=selection();return (await vault.all<SavedReport>('reports')).filter(r=>r.patientId===patientId&&r.date<=date&&r.pdf&&r.report);},
  saveReport:(r:SavedReport)=>run(async()=>{const {patientId,date}=selection();if(r.patientId!==patientId||r.date!==date||r.pdf.length>12000000)throw new Error('Invalid report context');await vault.write([{kind:'reports',id:r.id,value:r}],'report-saved',{patientId,date,reportId:r.id,type:r.type,sha256:r.sha256},true,r.report.author);}),
  doctorPlan:(name:string,input:Parameters<typeof savePlan>[4])=>run(()=>{const {patientId,date}=selection();return savePlan(vault,patientId,date,name,input);}),
  sensitivity:(name:string,value:'standard'|'high')=>run(()=>{const {patientId,date}=selection();return setSensitivity(vault,patientId,date,name,value);}),
  lab:(name:string,input:{id:string;date:string;test:LabTest;value:number;unit:string})=>run(()=>{const {patientId,date}=selection();return saveLab(vault,patientId,date,name,input);}),
  note:(name:string,input:{id:string;date:string;text:string})=>run(()=>{const {patientId,date}=selection();return saveNote(vault,patientId,date,name,input);}),
  phc:(name:string,phc:string,phone:string)=>run(()=>{const {patientId,date}=selection();return assignPHC(vault,patientId,date,name,phc,phone);}),
  visitDraft:(id:string,fields:DraftFields)=>run(()=>{const {patientId,date}=selection();return saveDraft(vault,patientId,date,id,fields);}),
  example:(grade:0|1|2|3,photo:string,name:string,source:string)=>run(()=>saveExample(vault,grade,photo,name,source)),
  removeExample:(grade:0|1|2|3,name:string)=>run(()=>removeExample(vault,grade,name)),
  visit:(input:VisitInput)=>run(()=>{const {patientId,date}=selection();if(input.patientId!==patientId||input.date!==date)throw new Error('Wrong visit context');return saveVisit(vault,input);}),
  location:(village:string,house:string,phone:string)=>run(()=>{const {patientId}=selection();return saveLocation(vault,patientId,village,house,phone);}),
  recordExport:(type:'referral'|'weekly',hash:string,reportDate?:string,channel:'pdf'|'qr'|'sms'='pdf')=>run(()=>{const {patientId,date}=selection();return recordExport(vault,patientId,reportDate??date,type,hash,channel);}),
  careDetails:(phone:string,amber:string,red:string)=>run(()=>{const {patientId}=selection();return saveCareDetails(vault,patientId,phone,amber,red);}),
  select:(id:string)=>run(()=>selectPatient(vault,id)),
  addElder:()=>run(()=>addDemoPatient(vault)),
  saveMedicine:(input:Omit<Medicine,'id'|'patientId'|'active'|'startDate'>)=>run(()=>{const {patientId,date}=selection();return saveMedicine(vault,patientId,date,input);}),
  medicineChange:(id:string,action:'archive'|'refill',amount=0)=>run(()=>{const {patientId,date}=selection();return changeMedicine(vault,patientId,id,action,date,amount);}),
  scheduledDose:(id:string,action:'take'|'snooze'|'remind',source:'tap'|'voice'='tap')=>run(()=>{const {patientId,date}=selection();return scheduledAction(vault,patientId,date,id,action,source);}),
  respond:(id:string,response:1|2|3,checked:string[])=>run(()=>{const {patientId}=selection();return respondAlert(vault,patientId,id,response,checked);}),
  reminders:(time:string)=>run(()=>{const {patientId,date}=selection();return checkReminders(vault,patientId,date,time);}),
  dose:(action:'take'|'snooze'|'remind'|'expire',source:'tap'|'voice'='tap')=>run(()=>{const {patientId,date}=selection();return actDose(vault,patientId,date,action,source);}),
  answers:(breathless:0|1,orthopnea:0|1,source:'tap'|'voice')=>run(()=>{const {patientId,date}=selection();return saveAnswers(vault,patientId,date,breathless,orthopnea,source);}),
  contact:(role:CareContact['role'],name:string,phone:string)=>run(()=>{const {patientId}=selection();return saveContact(vault,patientId,role,name,phone);}),
  create:(pin:string,consent:boolean)=>run(()=>vault.create(pin,consent)),
  unlock:(pin:string)=>run(()=>vault.unlock(pin)),
  seed:()=>run(()=>seedDemo(vault)),
  move:(index:number)=>run(()=>moveCursor(vault,state,index)),
  erase:async()=>{if(inFlight.current)return;setBusy(true);try{await vault.erase();lock();setExists(false);setFailed(false);}catch{lock();setFailed(true);}finally{setBusy(false);}}
 };
}
export type DemoController=ReturnType<typeof useDemo>;



