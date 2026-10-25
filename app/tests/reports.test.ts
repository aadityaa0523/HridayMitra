import 'fake-indexeddb/auto';
import {beforeEach,afterEach,it,expect} from 'vitest';
import {Vault} from '../src/data/vault';
import {seedDemo,snapshot} from '../src/data/model';
import {loadFamily,dayShift} from '../src/family/model';
import {emptyAsha} from '../src/asha/model';
import {emptyDoctor} from '../src/doctor/model';
import {buildReport,reportTypes,fhirBundle,personalBand} from '../src/reports/model';
import {encodeTransfer,TransferReceiver,validateReport} from '../src/reports/transfer';
let v:Vault;
beforeEach(async()=>{v=new Vault('reports-'+crypto.randomUUID());await v.create('123456',true);await seedDemo(v);});
afterEach(async()=>{v.lock();await v.db.delete();});
it('all nine reports respect patient and replay cutoff and keep missing data explicit',async()=>{
 const state=await snapshot(v),f=await loadFamily(v),p=state.patient!,date=state.checkins[45].date;
 const other={...f.rows[0],id:'other-row',patientId:'other',date,raw:{...f.rows[0].raw,weight_kg:9999},result:{...f.rows[0].result,gated:{...f.rows[0].result.gated,weight_kg:9999}}};f.rows.push(other);
 for(const type of reportTypes){const r=buildReport(f,emptyAsha(),emptyDoctor(),p,date,type,'hi','Demo author');expect(r.sections.length).toBeGreaterThan(0);expect(r.patientId).toBe(p.id);expect(JSON.stringify(r)).not.toMatch(/(?<![\d.])9999(?![\d.])/);for(const c of r.charts)expect(c.points.every(x=>x.date<=date)).toBe(true);expect(validateReport(r)).toEqual(r);}
 const r=buildReport(f,emptyAsha(),emptyDoctor(),p,date,'device','en','Demo');expect(JSON.stringify(r)).toContain('Battery: unknown');
 expect(()=>buildReport(f,emptyAsha(),emptyDoctor(),p,date,'daily','en','')).toThrow();
});
it('personal bands require six historical values and exclude last six days',async()=>{
 const s=await snapshot(v),rows=s.checkins,date=rows[60].date;
 expect(personalBand(rows.slice(0,3),date,'weight_kg')).toBeNull();const band=personalBand(rows,date,'weight_kg');expect(band).not.toBeNull();
 const changed=rows.map(r=>r.date>=dayShift(date,-6)?{...r,result:{...r.result,gated:{...r.result.gated,weight_kg:99999}}}:r);expect(personalBand(changed,date,'weight_kg')).toEqual(band);
});
it('reports unanswered engine alerts even when no family response has been saved',async()=>{
 const s=await snapshot(v),f=await loadFamily(v),row=s.checkins.find(r=>r.result.data&&!r.result.guest&&r.result.light===2)!;
 expect(f.alerts).toHaveLength(0);const report=buildReport(f,emptyAsha(),emptyDoctor(),s.patient!,row.date,'alert','en','Demo');
 expect(JSON.stringify(report.sections)).toContain('Trigger '+row.date);expect(JSON.stringify(report.sections)).toContain('Family response: Not recorded');expect(JSON.stringify(report.sections)).not.toContain('undefined');
});
it('FHIR maps six measured signals, excludes nulls, guests, other patients and future dates',async()=>{
 const s=await snapshot(v),p=s.patient!,row=s.checkins.find(r=>!r.result.guest&&r.result.gated.weight_kg!==null)!,end=row.date;
 const bundle=fhirBundle([row,{...row,id:'future',date:dayShift(end,1)},{...row,id:'guest',result:{...row.result,guest:true}},{...row,id:'other',patientId:'other'}],p,end,end);
 const entries=bundle.entry.slice(1).map(x=>x.resource as Record<string,any>);expect(entries.length).toBeGreaterThan(0);expect(entries.length).toBeLessThanOrEqual(6);
 expect(entries.find(x=>x.code.coding?.[0].code==='29463-7')?.valueQuantity.value).toBe(Math.round(row.result.gated.weight_kg!*100)/100);expect(entries.every(x=>x.subject.reference==='Patient/'+p.id&&x.effectiveDateTime===end)).toBe(true);expect(entries.some(x=>x.code.text.includes('bioimpedance'))).toBe(true);expect(bundle.entry[0].resource.resourceType).toBe('Patient');
});
it('compressed multipart transfer tolerates reordering and duplicates and rejects corruption or mixed sessions',async()=>{
 const s=await snapshot(v),r=buildReport(await loadFamily(v),emptyAsha(),emptyDoctor(),s.patient!,s.checkins[80].date,'monthly','hi','Demo');
 const frames=await encodeTransfer(r);expect(frames.length).toBeGreaterThan(1);const receiver=new TransferReceiver();expect(await receiver.add(frames.at(-1)!)).toBeNull();expect(await receiver.add(frames.at(-1)!)).toBeNull();let result;for(const f of frames.slice(0,-1).reverse())result=await receiver.add(f);expect(result).toEqual(r);
 const other=JSON.parse(frames[0]);other.id='another';await expect(receiver.add(JSON.stringify(other))).rejects.toThrow('Different');
 const bad=new TransferReceiver(),tampered=frames.map(x=>{const f=JSON.parse(x);f.hash='a'.repeat(64);return JSON.stringify(f);});for(const frame of tampered.slice(0,-1))await bad.add(frame);await expect(bad.add(tampered.at(-1)!)).rejects.toThrow('Checksum');
 await expect(new TransferReceiver().add('{"v":1}')).rejects.toThrow();expect(()=>validateReport({...r,charts:[{label:'bad',points:[{date:'x',value:Infinity}],band:null}]})).toThrow();
});
