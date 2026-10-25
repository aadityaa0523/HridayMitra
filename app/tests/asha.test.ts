import 'fake-indexeddb/auto';
import {beforeEach,afterEach,it,expect} from 'vitest';
import {Vault} from '../src/data/vault';
import {seedDemo,snapshot,addDemoPatient} from '../src/data/model';
import {loadFamily,respondAlert,saveMedicine,dayShift} from '../src/family/model';
import {saveVisit,loadAsha,todayList,weeklySummary,saveLocation,readingSummary,recordExport,type VisitInput} from '../src/asha/model';
import {qrPayload,referralLines} from '../src/asha/reports';
import i18next from 'i18next';
import en from '../src/i18n/en.json';
let v:Vault;
beforeEach(async()=>{v=new Vault('asha-'+crypto.randomUUID());await v.create('123456',true);await seedDemo(v);});
afterEach(async()=>{v.lock();await v.db.delete();});
const pid='synthetic-patient-1';
async function input():Promise<VisitInput>{const s=await snapshot(v),row=s.checkins.find(r=>r.result.light===2)!;return {id:crypto.randomUUID(),patientId:pid,date:row.date,bpSys:120,bpDia:80,weight:null,edema:1,breathlessRest:false,pillows:false,medicinesSeen:{},notes:'Private visit notes',outcome:'referred',referralReason:'Care team review requested'};}
it('saves encrypted once and marks an alert seen without changing the engine result',async()=>{
 const visit=await input(),before=await loadFamily(v),row=before.rows.find(r=>r.date===visit.date)!;
 await respondAlert(v,pid,row.id,1,[]);await saveVisit(v,visit);await saveVisit(v,visit);
 const visits=(await loadAsha(v)).visits,data=await loadFamily(v);expect(visits).toHaveLength(1);expect(data.rows.find(r=>r.id===row.id)?.result).toEqual(row.result);
 expect(data.alerts[0]).toMatchObject({response:1,seenByAsha:{visitId:visit.id},escalation:'stopped-local'});expect(data.pending.find(x=>x.type==='asha-seen')).toMatchObject({delivery:'not-sent'});
 await respondAlert(v,pid,row.id,3,[]);expect((await loadFamily(v)).alerts[0].seenByAsha?.visitId).toBe(visit.id);
 expect(JSON.stringify(await v.db.table('visits').toArray())).not.toContain('Private visit notes');
 v.lock();await v.unlock('123456');expect((await loadAsha(v)).visits[0].notes).toBe('Private visit notes');
});
it('rejects incomplete or invalid observations without saving or closing an alert',async()=>{
 const visit=await input();for(const patch of [{bpSys:70,bpDia:90},{bpDia:null},{weight:-1},{edema:4},{outcome:'referred',referralReason:''},{photo:'https://outside.invalid/ankle.jpg'},{patientId:'other'},{date:'2026-02-31'}])await expect(saveVisit(v,{...visit,...patch} as VisitInput)).rejects.toThrow();
 expect((await loadAsha(v)).visits).toHaveLength(0);expect((await loadFamily(v)).alerts).toHaveLength(0);
});
it('requires a yes/no observation for each applicable medicine and rejects another patient medicine',async()=>{
 const visit=await input();await saveMedicine(v,pid,visit.date,{name:'Demo tablet',strength:'Demo',times:['08:00'],food:'after',units:1,stock:5});
 await expect(saveVisit(v,visit)).rejects.toThrow();const m=(await loadFamily(v)).medicines[0];await saveVisit(v,{...visit,medicinesSeen:{[m.id]:false}});
 await expect(saveVisit(v,{...visit,id:crypto.randomUUID(),medicinesSeen:{foreign:true}})).rejects.toThrow();
});
it('sorts red, amber, stale check-in and green using no future rows and filters village',async()=>{
 await addDemoPatient(v);await addDemoPatient(v);await addDemoPatient(v);let data=await loadFamily(v);const date=data.rows[40].date;
 data.rows=data.patients.map((p,i)=>({...data.rows[40],id:p.id,patientId:p.id,date:i===2?dayShift(date,-2):date,result:{...data.rows[40].result,data:true,guest:false,light:([0,1,0,2] as const)[i]}}));
 data.patients[0].village='Demo village';expect(todayList(data,[],date).map(x=>x.patient.id)).toEqual([data.patients[3].id,data.patients[1].id,data.patients[2].id,data.patients[0].id]);
 expect(todayList(data,[],date,'Demo village')).toHaveLength(1);expect(todayList(data,[],date,'__unknown')).toHaveLength(3);
 data.rows.push({...data.rows[0],id:'future',date:dayShift(date,1),result:{...data.rows[0].result,light:2}});expect(todayList(data,[],date).find(x=>x.patient.id===data.patients[0].id)?.row?.id).not.toBe('future');
});
it('counts exactly seven calendar days and separates visit counts from unique elders',async()=>{
 const visit=await input(),data=await loadFamily(v);const visits=[{...visit,at:'',date:visit.date},{...visit,at:'',id:'v2',date:dayShift(visit.date,-6)},{...visit,at:'',id:'old',date:dayShift(visit.date,-7)},{...visit,at:'',id:'future',date:dayShift(visit.date,1)}];
 const s=weeklySummary(data,visits,visit.date);expect(s.visits).toBe(2);expect(s.eldersVisited).toBe(1);expect(s.referrals).toBe(2);expect(s.start).toBe(dayShift(visit.date,-6));
 const summary=readingSummary(data.rows,visit.date);expect(summary.latest!.date<=visit.date).toBe(true);expect(summary.days).toBeLessThanOrEqual(30);
});
it('saves location, validates PHC phone and records only export metadata',async()=>{
 await saveLocation(v,pid,'Demo village','House 4','+910000000001');await expect(saveLocation(v,pid,'Village','House','javascript:bad')).rejects.toThrow();
 expect((await snapshot(v)).patient?.village).toBe('Demo village');await recordExport(v,pid,'2026-01-01','referral','a'.repeat(64),'qr');
 const reports=await v.all<{sha256:string;channel:string}>('reports');expect(reports[0]).toMatchObject({sha256:'a'.repeat(64),channel:'qr'});await expect(recordExport(v,pid,'2026-01-01','weekly','wrong')).rejects.toThrow();
});
it('builds bounded QR content and a referral using observations and only past readings',async()=>{
 const visit={...await input(),at:''},data=await loadFamily(v);visit.referralReason='हिंदी कारण '.repeat(60);const payload=qrPayload(data,visit);expect(new TextEncoder().encode(payload).length).toBeLessThan(1600);expect(JSON.parse(payload).demo).toBe(true);
 const instance=i18next.createInstance();await instance.init({lng:'en',resources:{en:{translation:en}}});const lines=referralLines(data,visit,instance.t);expect(lines).toContain('Blood pressure: 120 / 80 mmHg');expect(lines.some(l=>l.includes('Private visit notes'))).toBe(true);
});
