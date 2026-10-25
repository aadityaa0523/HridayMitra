import 'fake-indexeddb/auto';
import {readFileSync} from 'node:fs';
import {beforeEach,afterEach,it,expect,vi} from 'vitest';
import {Vault} from '../src/data/vault';
import {seedDemo,snapshot} from '../src/data/model';
import {LineDecoder,parseLine,UUID,type Packet} from '../src/device/protocol';
import {createLinked,ingest,loadDevices,saveStatus} from '../src/device/model';
import {simulator} from '../src/device/simulator';
import {connectBLE,connectSerial} from '../src/device/transport';
let v:Vault;
beforeEach(async()=>{v=new Vault('device-'+crypto.randomUUID());await v.create('123456',true);await seedDemo(v);});
afterEach(async()=>{v.lock();await v.db.delete();vi.unstubAllGlobals();});
const wire={t:'checkin',id:'P001',weight_kg:62,pulse_bpm:72,spo2:97,light:2,S:8,learning:0,guest:0,why:'वज़न बढ़ा'};
it('decodes fragmented UTF-8 lines, nan tokens and multiple records, and bounds malformed data',()=>{
 const d=new LineDecoder(),bytes=new TextEncoder().encode(JSON.stringify(wire)+'\n'+JSON.stringify({...wire,weight_kg:null})+'\n');let lines:string[]=[];for(let i=0;i<bytes.length;i+=7)lines.push(...d.push(bytes.slice(i,i+7)));expect(lines).toHaveLength(2);expect((parseLine(lines[0]) as Packet).why).toBe(wire.why);
 const legacy=parseLine(JSON.stringify(wire).replace('"weight_kg":62','"weight_kg":nan')) as Packet;expect(legacy.raw.weight_kg).toBeNull();expect(legacy.result.light).toBe(2);expect(parseLine('{"t":"selftest","battery_mv":-1,"signal":99,"problems":""}')).toMatchObject({battery_mv:null,signal:99});
 for(const bad of [{...wire,light:3},{...wire,guest:2},{...wire,weight_kg:-1},{...wire,date:'2026-02-30'},{...wire,breathless:3}])expect(()=>parseLine(JSON.stringify(bad))).toThrow();expect(()=>d.push(new TextEncoder().encode('a'.repeat(8200)))).toThrow();expect(d.push(new TextEncoder().encode('{}\n'))).toEqual(['{}']);
});
it('requires explicit binding and date; atomically preserves device results and rejects conflicts or other identities',async()=>{
 await createLinked(v,'P001','ble');const s=await snapshot(v),pid=s.patient!.id,p=parseLine(JSON.stringify(wire)) as Packet;
 await expect(ingest(v,pid,'ble',[p],'')).rejects.toThrow();await ingest(v,pid,'ble',[p],'2026-10-25');const saved=(await snapshot(v)).checkins[0];expect(saved.result.light).toBe(2);expect(saved.source).toBe('device');expect(saved.deviceWhy).toBe(wire.why);
 await ingest(v,pid,'ble',[p],'2026-10-25');expect((await snapshot(v)).checkins).toHaveLength(1);
 await expect(ingest(v,pid,'ble',[{...p,id:'P002'}],'2026-10-26')).rejects.toThrow();await expect(ingest(v,pid,'simulator',[p],'2026-10-26')).rejects.toThrow();
 await expect(ingest(v,pid,'ble',[{...p,date:'2026-10-26'},{...p,result:{...p.result,light:0}}],'2026-10-25')).rejects.toThrow();expect((await snapshot(v)).checkins).toHaveLength(1);
 expect((await v.all('checkins')).length).toBe(165);
});
it('simulator uses the same protocol and preserves stable, worsening, recovery and dated history',async()=>{
 const received:Packet[]=[];let scenario:'stable'|'worsening'|'recovery'='stable';const link=simulator('P001',()=>scenario,line=>{const m=parseLine(line);if(m.t==='checkin')received.push(m);});
 await link.send('checkin');expect(received.at(-1)?.result.light).toBe(0);scenario='worsening';await link.send('checkin');expect(received.at(-1)?.result.light).toBe(2);scenario='recovery';await link.send('checkin');expect(received.at(-1)?.result.light).toBe(0);expect(received.every(x=>Boolean(x.date))).toBe(true);
 await createLinked(v,'P001','simulator');const pid=(await snapshot(v)).patient!.id;await ingest(v,pid,'simulator',received,'');expect((await snapshot(v)).checkins).toHaveLength(3);
 await saveStatus(v,pid,'simulator',{t:'selftest',battery_mv:3950,signal:18,problems:'Simulated'});expect((await loadDevices(v)).events).toHaveLength(1);
 await link.close();await expect(link.send('checkin')).rejects.toThrow();
});
it('BLE subscribes to the required UUIDs, reassembles notifications, writes commands and cleans up',async()=>{
 class C extends EventTarget{value=new DataView(new ArrayBuffer(0));writes:string[]=[];async startNotifications(){}async readValue(){return new DataView(new TextEncoder().encode('{"t":"status","battery_mv":null,"signal":null}').buffer);}async writeValueWithResponse(b:Uint8Array){this.writes.push(new TextDecoder().decode(b));}emit(text:string){this.value=new DataView(new TextEncoder().encode(text).buffer);this.dispatchEvent(new Event('characteristicvaluechanged'));}}
 const chars=Object.fromEntries(Object.values(UUID).map(x=>[x,new C()])),ids:string[]=[],disconnect=vi.fn(),device=Object.assign(new EventTarget(),{gatt:{connected:true,connect:async()=>({getPrimaryService:async(id:string)=>{ids.push(id);return {getCharacteristic:async(id:string)=>{ids.push(id);return chars[id];}};}}),disconnect}}),requestDevice=vi.fn(async()=>device);vi.stubGlobal('navigator',{bluetooth:{requestDevice}});vi.stubGlobal('isSecureContext',true);
 const lines:string[]=[],lost=vi.fn(),link=await connectBLE(s=>lines.push(s),lost);chars[UUID.reports].emit('{"t":');chars[UUID.reports].emit('"ready"}\n');expect(lines.at(-1)).toBe('{"t":"ready"}');expect([...ids].sort()).toEqual(Object.values(UUID).sort());await link.send('checkin');await link.send('{"since":"2026-01-01"}',true);expect(chars[UUID.commands].writes).toEqual(['checkin']);expect(chars[UUID.history].writes).toHaveLength(1);await link.close();chars[UUID.reports].emit('{}\n');device.dispatchEvent(new Event('gattserverdisconnected'));expect(lost).not.toHaveBeenCalled();expect(disconnect).toHaveBeenCalled();
});
it('serial uses 115200, newline commands and cancels the reader before closing',async()=>{
 let control:ReadableStreamDefaultController<Uint8Array>;const output:string[]=[],close=vi.fn(async()=>{}),open=vi.fn(async()=>{}),port={open,close,readable:new ReadableStream<Uint8Array>({start(c){control=c;}}),writable:new WritableStream<Uint8Array>({write(bytes){output.push(new TextDecoder().decode(bytes));}})};vi.stubGlobal('navigator',{serial:{requestPort:async()=>port}});vi.stubGlobal('isSecureContext',true);const lines:string[]=[],link=await connectSerial(s=>lines.push(s),()=>{});control!.enqueue(new TextEncoder().encode('{"t":"ready"}\n'));await new Promise(r=>setTimeout(r,0));await link.send('selftest');expect(open).toHaveBeenCalledWith({baudRate:115200});expect(lines).toEqual(['{"t":"ready"}']);expect(output).toEqual(['selftest\n']);await link.close();expect(close).toHaveBeenCalled();await expect(link.send('checkin')).rejects.toThrow();
});
it('connection cancellation and unsupported browsers never create a successful link',async()=>{
 vi.stubGlobal('isSecureContext',true);vi.stubGlobal('navigator',{});await expect(connectBLE(()=>{},()=>{})).rejects.toThrow('unavailable');await expect(connectSerial(()=>{},()=>{})).rejects.toThrow('unavailable');
 vi.stubGlobal('navigator',{bluetooth:{requestDevice:async()=>{throw new DOMException('Cancelled','NotFoundError');}}});await expect(connectBLE(()=>{},()=>{})).rejects.toThrow('Cancelled');
 const disconnect=vi.fn(),device=Object.assign(new EventTarget(),{gatt:{connected:true,disconnect,connect:async()=>{throw Error('GATT failure');}}});vi.stubGlobal('navigator',{bluetooth:{requestDevice:async()=>device}});await expect(connectBLE(()=>{},()=>{})).rejects.toThrow('GATT failure');expect(disconnect).toHaveBeenCalled();
});

it('parses every check-in the real firmware produced in the software-in-the-loop month',()=>{
 // reports/sil_checkins.jsonl is written by tests/sil (the stool firmware compiled on the laptop); nan = "no reading"
 const lines=readFileSync(new URL('../../reports/sil_checkins.jsonl',import.meta.url),'utf8').split(/\r?\n/).filter(Boolean);
 expect(lines.length).toBeGreaterThan(25);
 const packets=lines.map(l=>parseLine(l.trim().slice(l.indexOf('"report":')+9,-1)) as Packet);
 expect(packets.every(p=>p.t==='checkin'&&/^P00[12]$/.test(p.id)&&p.date&&p.event_id)).toBe(true);
 expect(packets.filter(p=>p.raw.leg_ewi!==null).length).toBeGreaterThan(25);
 expect(packets.every(p=>p.extras?.ref_ratio!==undefined)).toBe(true);
});
