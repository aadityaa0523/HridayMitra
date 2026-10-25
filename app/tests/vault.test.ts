import 'fake-indexeddb/auto';
import {afterEach,it,expect} from 'vitest';
import {Vault,Database} from '../src/data/vault';
import {seedDemo,snapshot} from '../src/data/model';
const vaults:Vault[]=[];
const create=()=>{const v=new Vault('test-'+crypto.randomUUID());vaults.push(v);return v;};
afterEach(async()=>{for(const v of vaults.splice(0)){v.lock();await v.db.delete();}});
it('requires consent, encrypts fields and restores only with the correct PIN',async()=>{
 const v=create();
 await expect(v.create('123456',false)).rejects.toThrow();
 await v.create('123456',true);
 await v.write([{kind:'patients',id:'p',value:{name:'Secret Patient',weight:62}}],'test',{});
 const stored=await v.db.table('patients').toArray();
 expect(JSON.stringify(stored)).not.toContain('Secret Patient');
 const nonce=stored[0].iv;
 await v.write([{kind:'patients',id:'p',value:{name:'Secret Patient',weight:63}}],'update',{});
 expect((await v.db.table('patients').get('p')).iv).not.toEqual(nonce);
 v.lock();await expect(v.all('patients')).rejects.toThrow();
 await expect(v.unlock('654321')).rejects.toThrow();
 expect(v.unlocked).toBe(false);
 await v.unlock('123456');
 expect(await v.all('patients')).toEqual([{name:'Secret Patient',weight:63}]);
});
it('detects ciphertext tampering and locks the vault',async()=>{
 const v=create();await v.create('123456',true);
 await v.write([{kind:'patients',id:'p',value:{name:'Demo'}}],'test',{});
 const row=await v.db.table('patients').get('p');row.cipher[0]^=1;await v.db.table('patients').put(row);
 await expect(v.all('patients')).rejects.toThrow();expect(v.unlocked).toBe(false);
});
it('authenticates record identity and rolls back conflicting batches',async()=>{
 const v=create();await v.create('123456',true);
 const before=await v.db.table('audit').count();
 await expect(v.write([{kind:'patients',id:'same',value:{name:'A'}},{kind:'patients',id:'same',value:{name:'B'}}],'collision',{},true)).rejects.toThrow();
 expect(await v.db.table('patients').count()).toBe(0);
 expect(await v.db.table('audit').count()).toBe(before);
 await v.write([{kind:'patients',id:'a',value:{name:'A'}}],'test',{});
 const row=await v.db.table('patients').get('a');
 await v.db.table('patients').put({...row,id:'b'});
 await expect(v.all('patients')).rejects.toThrow();
});
it('seeds atomically and idempotently; deletion removes all records and metadata',async()=>{
 const v=create();await v.create('123456',true);await seedDemo(v);await seedDemo(v);
 const state=await snapshot(v);
 expect(state.checkins).toHaveLength(164);expect(state.auditCount).toBe(2);
 expect(await v.db.table('patients').count()).toBe(1);
 expect(state.checkins.some(x=>x.result.light===2)).toBe(true);
 await v.erase();expect(await v.exists()).toBe(false);
 for(const table of v.db.tables)expect(await table.count()).toBe(0);
});
it('upgrades version 1 without deleting existing encrypted records',async()=>{
 const name='migration-'+crypto.randomUUID();
 const old=new Database(name);await old.delete();
 const Dexie=(await import('dexie')).default;
 const legacy=new Dexie(name);legacy.version(1).stores({meta:'id',patients:'id'});
 await legacy.table('patients').put({id:'sentinel',cipher:[1],iv:[2],version:1});legacy.close();
 const next=new Vault(name);vaults.push(next);await next.db.open();
 expect(await next.db.table('patients').get('sentinel')).toEqual({id:'sentinel',cipher:[1],iv:[2],version:1});
 expect(next.db.tables.some(x=>x.name==='outbox')).toBe(true);
});

