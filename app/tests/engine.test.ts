import {describe,it,expect} from 'vitest';
import vectors from '../../docs/app/engine_test_vectors.json';
import {evaluate,emptyInput,type Inputs} from '../src/engine';
import {dailyHistory,evaluateDaily,type Reading} from '../src/engine/daily';
describe('frozen Python parity',()=>{
 for(const patient of [...vectors.patients,...vectors.cases,...vectors.referencePatients]){
  for(const threshold of [7,6]){
   it(patient.id+' threshold '+threshold,()=>{
    const results=evaluate(patient.days.map(d=>d.input as Inputs),threshold);
    results.forEach((actual,i)=>{
     const expected=patient.days[i].expected;
     expect(actual.S).toBeCloseTo(expected.S,3);
     expect(actual.light).toBe(threshold===7?expected.light:expected.sensitiveLight);
     expect(actual.guest).toBe(expected.guest);
     expect(actual.learning).toBe(expected.learning);
     expect(actual.data).toBe(expected.data);
    });
   });
  }
 }
});
const row=(date:string,id=date):Reading=>({date,patientId:'p1',eventId:id,input:emptyInput(),source:'manual'});
it('inserts missing calendar days and deduplicates identical replayed events',()=>{
 const first=row('2026-01-01'),last=row('2026-01-04');
 expect(dailyHistory([last,first,first])).toHaveLength(4);
 expect(dailyHistory([last,first])[1].input).toEqual(emptyInput());
});
it('rejects same-day conflicts, mixed patients and impossible dates',()=>{
 expect(()=>dailyHistory([row('2026-01-01','a'),row('2026-01-01','b')])).toThrow();
 expect(()=>dailyHistory([row('2026-02-30')])).toThrow();
 expect(()=>dailyHistory([row('2026-01-01'),{...row('2026-01-02'),patientId:'p2'}])).toThrow();
});
it('preserves device-authored results without replacing them',()=>{
 const result={...evaluate([emptyInput()])[0],light:2 as const,S:123};
 expect(evaluateDaily([{...row('2026-01-01'),source:'device',deviceResult:result}])[0].result).toEqual(result);
});
it('does not mutate raw data and remains causal',()=>{
 const input=vectors.patients[0].days.map(x=>x.input as Inputs),copy=structuredClone(input);
 const full=evaluate(input),prefix=evaluate(input.slice(0,50));
 expect(prefix).toEqual(full.slice(0,50));expect(input).toEqual(copy);
});
it('rejects nonfinite readings and invalid thresholds',()=>{
 expect(()=>evaluate([{...emptyInput(),weight_kg:NaN}])).toThrow();
 expect(()=>evaluate([emptyInput()],4)).toThrow();
});

