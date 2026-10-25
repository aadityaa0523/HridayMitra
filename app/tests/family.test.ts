import 'fake-indexeddb/auto';
import {afterEach,beforeEach,it,expect} from 'vitest';
import {Vault} from '../src/data/vault';
import {seedDemo,snapshot,addDemoPatient,selectPatient} from '../src/data/model';
import {loadFamily,saveMedicine,scheduledAction,changeMedicine,dosesFor,adherence,refillDays,respondAlert,checkReminders,saveCareDetails,windowRows,streak,dayShift} from '../src/family/model';
let v:Vault;
beforeEach(async()=>{v=new Vault('family-'+crypto.randomUUID());await v.create('123456',true);await seedDemo(v);});
afterEach(async()=>{v.lock();await v.db.delete();});
const input={name:'Test tablet',strength:'Demo strength',times:['08:00','20:00'],units:1,stock:12,food:'after' as const};
const patientId='synthetic-patient-1';
it('keeps four elders isolated and preserves the shared replay position',async()=>{
 for(let i=0;i<3;i++)await addDemoPatient(v);
 await expect(addDemoPatient(v)).rejects.toThrow();
 const before=await snapshot(v);await selectPatient(v,'synthetic-patient-2');const after=await snapshot(v);
 expect(after.patients).toHaveLength(4);expect(after.cursor).toBe(before.cursor);expect(after.checkins.every(r=>r.patientId===after.patient?.id)).toBe(true);
 await expect(selectPatient(v,'unknown')).rejects.toThrow();
});
it('takes a scheduled dose once, updates stock atomically, and retains taken history on archive',async()=>{
 const date=(await snapshot(v)).checkins[30].date;await saveMedicine(v,patientId,date,input);
 let data=await loadFamily(v);const m=data.medicines[0],d=dosesFor(data,patientId,date)[0];
 expect(refillDays(m)).toBe(6);expect(dosesFor(data,patientId,dayShift(date,-1))).toHaveLength(0);
 await scheduledAction(v,patientId,date,d.id,'take','voice',1000);await scheduledAction(v,patientId,date,d.id,'take','tap',2000);
 data=await loadFamily(v);expect(data.medicines[0].stock).toBe(11);expect(data.doses[0].source).toBe('voice');expect(adherence(data,patientId,date)).toMatchObject({taken:1,total:2});
 await changeMedicine(v,patientId,m.id,'archive',date);data=await loadFamily(v);expect(dosesFor(data,patientId,date).map(x=>x.state)).toEqual(['taken']);
 expect(JSON.stringify(await v.db.table('medicines').toArray())).not.toContain('Test tablet');
});
it('rejects cross-patient, insufficient stock, unsafe photo and invalid schedules',async()=>{
 const date=(await snapshot(v)).checkins[30].date;
 await expect(saveMedicine(v,'unknown',date,input)).rejects.toThrow();
 for(const times of [['25:00'],['08:00','08:00'],[]])await expect(saveMedicine(v,patientId,date,{...input,times})).rejects.toThrow();
 await expect(saveMedicine(v,patientId,date,{...input,photo:'https://tracker.invalid/photo.png'})).rejects.toThrow();
 await saveMedicine(v,patientId,date,{...input,stock:0});const data=await loadFamily(v),d=dosesFor(data,patientId,date)[0];
 await expect(scheduledAction(v,'other',date,d.id,'take')).rejects.toThrow();await expect(scheduledAction(v,patientId,date,d.id,'take')).rejects.toThrow();
 expect((await loadFamily(v)).doses).toHaveLength(0);
 await changeMedicine(v,patientId,data.medicines[0].id,'refill',date,30);expect((await loadFamily(v)).medicines[0].stock).toBe(30);
});
it('queues an alert response without changing or clearing the device light, including fine response',async()=>{
 const state=await snapshot(v),red=state.checkins.find(r=>r.result.light===2)!;
 await saveCareDetails(v,patientId,'+910000000001','Call care team','Contact clinician');
 await respondAlert(v,patientId,red.id,1,['Contact clinician']);await respondAlert(v,patientId,red.id,3,['Contact clinician']);
 const data=await loadFamily(v);expect(data.alerts[0].response).toBe(3);expect(data.alerts[0].checked).toEqual(['Contact clinician']);expect(data.pending[0]).toMatchObject({digit:3,delivery:'not-sent',status:'pending'});
 expect(data.rows.find(r=>r.id===red.id)?.result).toEqual(red.result);
 await expect(respondAlert(v,'other',red.id,2)).rejects.toThrow();await expect(respondAlert(v,patientId,red.id,1,['Invented step'])).rejects.toThrow();
 const audit=await v.all<{action:string}>('audit');expect(audit.filter(x=>x.action==='family-alert-response')).toHaveLength(2);
});
it('does not invent a missed check-in before 11, queues once after 11, and expires third snooze',async()=>{
 const date='2026-12-01';await checkReminders(v,patientId,date,'10:59',0);expect((await loadFamily(v)).pending).toHaveLength(0);
 await checkReminders(v,patientId,date,'11:00',0);await checkReminders(v,patientId,date,'12:00',1);expect((await loadFamily(v)).pending).toHaveLength(1);
 await saveMedicine(v,patientId,date,input);await checkReminders(v,patientId,date,'08:00',10);let data=await loadFamily(v),dose=dosesFor(data,patientId,date)[0];expect(data.doses).toHaveLength(1);
 for(let i=0;i<3;i++)await scheduledAction(v,patientId,date,dose.id,'snooze','tap',1000*i);
 await checkReminders(v,patientId,date,'08:00',602000);data=await loadFamily(v);expect(data.doses[0].state).toBe('missed');expect(data.pending.some(x=>x.type==='missed-dose')).toBe(true);
});
it('uses calendar windows and guest-free streaks without future readings',async()=>{
 const state=await snapshot(v),date=state.checkins[30].date;
 expect(windowRows(state.checkins,date,7)).toHaveLength(7);expect(windowRows(state.checkins,date,30).every(r=>r.date<=date)).toBe(true);
 const rows=state.checkins.slice(0,3).map(r=>({...r,result:{...r.result,data:true,guest:false}}));expect(streak(rows,rows[2].date)).toBe(3);rows[1].result.guest=true;expect(streak(rows,rows[2].date)).toBe(1);
});
