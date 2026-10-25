import 'fake-indexeddb/auto';
import {beforeEach,afterEach,it,expect} from 'vitest';
import {Vault} from '../src/data/vault';
import {seedDemo,snapshot,addDemoPatient} from '../src/data/model';
import {loadFamily,saveCareDetails} from '../src/family/model';
import {loadDoctor,savePlan,setSensitivity,saveLab,saveNote,assignPHC,asOfPatient,thresholdFor,sensitivityPreview,timeline} from '../src/doctor/model';
import {loadRoutine} from '../src/elder/routine';
import {loadAsha,saveDraft,saveVisit,saveExample,removeExample,type DraftFields} from '../src/asha/model';
let v:Vault;
const pid='synthetic-patient-1',author='Dr Demo';
beforeEach(async()=>{v=new Vault('doctor-'+crypto.randomUUID());await v.create('123456',true);await seedDemo(v);});
afterEach(async()=>{v.lock();await v.db.delete();});
const plan={amber:'Contact care team',red:'Seek recorded care-team instructions',dryWeightKg:60,fluidLimitL:1.5,saltAdvice:'Copy existing advice',followUp:'2026-12-01'};
it('versions named plans, applies only as of replay date and preserves legacy instructions',async()=>{
 const state=await snapshot(v),date=state.checkins[30].date,beforeDate=state.checkins[29].date;
 await saveCareDetails(v,pid,'','Old amber','Old red');await savePlan(v,pid,date,author,plan);
 const raw=(await snapshot(v)).patient!,data=await loadDoctor(v);expect(data.plans).toHaveLength(1);expect((await loadRoutine(v,pid,date)).pendingHelp).toBe(false);
 expect(asOfPatient(raw,data,date).plan).toMatchObject({source:'clinician',doctorName:author,fluidLimitL:1.5});expect(asOfPatient(raw,data,beforeDate).plan?.amber).toEqual(['Old amber']);
 expect(data.audit.find(a=>a.action==='doctor-plan-saved')?.actor).toBe(author);
 await saveCareDetails(v,pid,'+910000000001','Attempted overwrite','Attempted overwrite');expect((await snapshot(v)).patient?.plan?.amber).toEqual(['Contact care team']);
 expect((await loadFamily(v)).pending.some(p=>p.type==='doctor-plan')).toBe(true);
});
it('validates plans and follow-up dates without inventing defaults',async()=>{
 const date=(await snapshot(v)).checkins[30].date;
 for(const bad of [{amber:''},{red:''},{dryWeightKg:-1},{fluidLimitL:0},{followUp:'2020-01-01'}])await expect(savePlan(v,pid,date,author,{...plan,...bad})).rejects.toThrow();
 await expect(savePlan(v,pid,date,'',plan)).rejects.toThrow();await expect(savePlan(v,'other',date,author,plan)).rejects.toThrow();expect((await loadDoctor(v)).plans).toHaveLength(0);
});
it('audits threshold 7 to 6 with name and never overwrites frozen results',async()=>{
 const state=await snapshot(v),date=state.checkins[30].date,original=state.checkins.map(r=>r.result);
 await setSensitivity(v,pid,date,author,'high');await setSensitivity(v,pid,date,author,'high');const data=await loadDoctor(v),raw=(await snapshot(v)).patient!;
 expect(data.sensitivities).toHaveLength(1);expect(thresholdFor(asOfPatient(raw,data,date))).toBe(6);expect(thresholdFor(asOfPatient(raw,data,state.checkins[29].date))).toBe(7);
 expect(sensitivityPreview(state.checkins,date,6)?.threshold).toBe(6);expect((await snapshot(v)).checkins.map(r=>r.result)).toEqual(original);
 expect(data.audit.find(a=>a.action==='doctor-sensitivity-changed')?.actor).toBe(author);await setSensitivity(v,pid,date,author,'standard');expect((await loadDoctor(v)).sensitivities).toHaveLength(2);
});
it('stores immutable labs with exact units and notes, rejects future/cross-patient input',async()=>{
 const date=(await snapshot(v)).checkins[30].date,lab={id:'lab1',date,test:'K' as const,value:4.2,unit:'mmol/L'};
 await saveLab(v,pid,date,author,lab);await saveLab(v,pid,date,author,lab);await saveNote(v,pid,date,author,{id:'note1',date,text:'Private clinical note'});
 await expect(saveLab(v,pid,date,author,{...lab,id:'bad',unit:'mg/dL'})).rejects.toThrow();await expect(saveLab(v,pid,date,author,{...lab,id:'bad',date:'2030-01-01'})).rejects.toThrow();await expect(saveNote(v,'other',date,author,{id:'bad',date,text:'No'})).rejects.toThrow();
 const data=await loadDoctor(v);expect(data.labs).toHaveLength(1);expect(data.notes[0].doctorName).toBe(author);expect(JSON.stringify(await v.db.table('notes').toArray())).not.toContain('Private clinical note');
 v.lock();await v.unlock('123456');expect((await loadDoctor(v)).notes[0].text).toBe('Private clinical note');
});
it('builds patient-scoped timelines without future results and records PHC assignment',async()=>{
 const s=await snapshot(v),date=s.checkins[30].date;await assignPHC(v,pid,date,author,'Demo PHC','+910000000001');expect((await snapshot(v)).patient?.phcName).toBe('Demo PHC');
 await addDemoPatient(v);await saveNote(v,pid,date,author,{id:'note',date,text:'Timeline note'});const items=timeline(await loadFamily(v),await loadDoctor(v),[],pid,date);
 expect(items.every(i=>i.date<=date)).toBe(true);expect(items.filter(i=>i.kind==='checkin')).toHaveLength(31);expect(items.some(i=>i.note?.text==='Timeline note')).toBe(true);expect(items.some(i=>i.row?.patientId==='synthetic-patient-2')).toBe(false);
});
it('restores encrypted ASHA drafts and clears the draft atomically on final save',async()=>{
 const date=(await snapshot(v)).checkins[30].date,fields:DraftFields={sys:'120',dia:'80',weight:'',edema:'1',breath:'no',pillows:'no',seen:{},notes:'Draft private notes',outcome:'fine',reason:''};
 await saveDraft(v,pid,date,'visit1',fields);v.lock();await v.unlock('123456');expect((await loadAsha(v)).drafts[0].fields.notes).toBe('Draft private notes');expect(JSON.stringify(await v.db.table('settings').toArray())).not.toContain('Draft private notes');
 await saveVisit(v,{id:'visit1',patientId:pid,date,bpSys:120,bpDia:80,weight:null,edema:1,breathlessRest:false,pillows:false,medicinesSeen:{},notes:fields.notes,outcome:'fine',referralReason:''});expect((await loadAsha(v)).drafts).toHaveLength(0);expect((await loadAsha(v)).visits).toHaveLength(1);
});
it('requires review attribution for local reference photos and supports removal',async()=>{
 const photo='data:image/png;base64,aGVsbG8=';
 await expect(saveExample(v,1,photo,'','Source')).rejects.toThrow();await expect(saveExample(v,1,'https://outside.invalid/photo',author,'Source')).rejects.toThrow();
 await saveExample(v,1,photo,author,'Consented training reference');expect((await loadAsha(v)).examples[0].reviewedBy).toBe(author);
 await removeExample(v,1,author);expect((await loadAsha(v)).examples).toHaveLength(0);
});
