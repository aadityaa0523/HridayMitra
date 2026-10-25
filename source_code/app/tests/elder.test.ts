import 'fake-indexeddb/auto';
import {it,expect,afterEach} from 'vitest';
import {matchIntent,phrases,type Intent} from '../src/voice/intents';
import {nextDose,actDose,loadRoutine,saveAnswers,saveContact} from '../src/elder/routine';
import {Vault} from '../src/data/vault';
for(const [lang,dict] of Object.entries(phrases))for(const [intent,list] of Object.entries(dict)){
 it(lang+' '+intent+' vocabulary',()=>{expect(list.length).toBeGreaterThanOrEqual(6);for(const p of list)expect(matchIntent(p,lang)).toBe(intent as Intent);});
}
it('rejects negated and fuzzy consequential commands',()=>{
 for(const text of ['I did not take my medicine','do not mark medicine taken','i took no medicine','hell','yess'])expect(matchIntent(text,'en')).toBeNull();
 expect(matchIntent('दवा नहीं ली','hi')).toBeNull();
 expect(matchIntent('ruk jao','hi')).toBe('cancel');
});
it('snoozes exactly three times, then expires; taken is idempotent',()=>{
 let d=nextDose(null,'p','2026-01-01','remind',0);
 for(let i=1;i<=3;i++){d=nextDose(d,'p','2026-01-01','snooze',i*1000);expect(d.snoozes).toBe(i);expect(d.dueAt).toBe(i*1000+600000);}
 expect(()=>nextDose(d,'p','2026-01-01','snooze',5000)).toThrow();
 d=nextDose(d,'p','2026-01-01','expire',603000);expect(d.state).toBe('missed');
 d=nextDose(d,'p','2026-01-01','take',604000,'voice');expect(d.source).toBe('voice');
 expect(nextDose(d,'p','2026-01-01','take',605000)).toEqual(d);
 expect(()=>nextDose(d,'another','2026-01-01','take',605000)).toThrow();
});
let vault:Vault|undefined;
afterEach(async()=>{if(vault){await vault.db.delete();vault=undefined;}});
it('persists routines encrypted, scopes dates, and queues without claiming delivery',async()=>{
 vault=new Vault('routine-'+crypto.randomUUID());await vault.create('123456',true);
 await actDose(vault,'p','2026-01-01','remind','tap',0);
 for(let i=1;i<=3;i++)await actDose(vault,'p','2026-01-01','snooze','tap',i*1000);
 await actDose(vault,'p','2026-01-01','expire','tap',603000);
 await saveAnswers(vault,'p','2026-01-01',1,0,'voice');
 await saveContact(vault,'p','family1','Test family','+910000000001');
 const state=await loadRoutine(vault,'p','2026-01-01');
 expect(state.pendingHelp).toBe(true);expect(state.answers?.breathless).toBe(1);expect(state.dose?.state).toBe('missed');
 expect((await loadRoutine(vault,'p','2026-01-02')).dose).toBeNull();
 expect(JSON.stringify(await vault.db.table('contacts').toArray())).not.toContain('Test family');
 await expect(saveContact(vault,'p','asha','bad','javascript:alert(1)')).rejects.toThrow();
});

