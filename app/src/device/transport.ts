import {UUID,LineDecoder} from './protocol';
export type Link={kind:'ble'|'serial'|'simulator';send:(text:string,history?:boolean)=>Promise<void>;close:()=>Promise<void>};
type Characteristic=EventTarget&{value?:DataView;startNotifications:()=>Promise<unknown>;readValue:()=>Promise<DataView>;writeValueWithResponse:(bytes:Uint8Array)=>Promise<void>};
type Device=EventTarget&{name?:string;gatt:{connected:boolean;connect:()=>Promise<{getPrimaryService:(uuid:string)=>Promise<{getCharacteristic:(uuid:string)=>Promise<Characteristic>}>}>;disconnect:()=>void}};
export type DeviceNavigator=Navigator&{bluetooth?:{requestDevice:(options:unknown)=>Promise<Device>};serial?:{requestPort:()=>Promise<Port>}};
type Port={open:(options:{baudRate:number})=>Promise<void>;close:()=>Promise<void>;readable:ReadableStream<Uint8Array>|null;writable:WritableStream<Uint8Array>|null};
export async function connectBLE(onLine:(line:string)=>void,onDisconnect:()=>void):Promise<Link>{
 const nav=navigator as DeviceNavigator;if(!nav.bluetooth||!isSecureContext)throw Error('BLE unavailable');
 const device=await nav.bluetooth.requestDevice({filters:[{services:[UUID.service]}]}),listeners:{c:Characteristic;fn:EventListener}[]=[],decoder=new LineDecoder();
 const cleanup=()=>{for(const {c,fn} of listeners)c.removeEventListener('characteristicvaluechanged',fn);device.removeEventListener('gattserverdisconnected',disconnected);};
 const disconnected=()=>{cleanup();onDisconnect();};device.addEventListener('gattserverdisconnected',disconnected);
 try{const server=await device.gatt.connect(),service=await server.getPrimaryService(UUID.service),reports=await service.getCharacteristic(UUID.reports),status=await service.getCharacteristic(UUID.status),write=await service.getCharacteristic(UUID.commands),history=await service.getCharacteristic(UUID.history);
  const report:EventListener=e=>{try{const v=(e.target as Characteristic).value!;for(const line of decoder.push(new Uint8Array(v.buffer,v.byteOffset,v.byteLength)))onLine(line);}catch{onLine('{"t":"error","message":"Invalid BLE frame"}');}};
  const state:EventListener=e=>{const v=(e.target as Characteristic).value!;onLine(new TextDecoder().decode(new Uint8Array(v.buffer,v.byteOffset,v.byteLength)));};
  for(const [c,fn] of [[reports,report],[status,state]] as const){c.addEventListener('characteristicvaluechanged',fn);listeners.push({c,fn});await c.startNotifications();}
  const v=await status.readValue();if(v.byteLength)onLine(new TextDecoder().decode(v));
  if(!device.gatt.connected)throw Error('Disconnected during pairing');
  return {kind:'ble',send:async(text,isHistory=false)=>{if(!device.gatt.connected)throw Error('Disconnected');const bytes=new TextEncoder().encode(text);if(bytes.length>180)throw Error('Command exceeds GATT limit');await (isHistory?history:write).writeValueWithResponse(bytes);},close:async()=>{cleanup();device.gatt.disconnect();}};
 }catch(e){cleanup();device.gatt.disconnect();throw e;}
}
export async function connectSerial(onLine:(line:string)=>void,onDisconnect:()=>void):Promise<Link>{
 const api=(navigator as DeviceNavigator).serial;if(!api||!isSecureContext)throw Error('Serial unavailable');const port=await api.requestPort();await port.open({baudRate:115200});
 if(!port.readable||!port.writable){await port.close();throw Error('No serial streams');}const reader=port.readable.getReader(),writer=port.writable.getWriter(),decoder=new LineDecoder();let closed=false,chain=Promise.resolve();
 const loop=(async()=>{try{while(!closed){const {done,value}=await reader.read();if(done)break;for(const line of decoder.push(value))onLine(line);}}catch{if(!closed)onLine('{"t":"error","message":"Serial stream failed"}');}finally{reader.releaseLock();if(!closed){closed=true;await chain.catch(()=>{});writer.releaseLock();await port.close().catch(()=>{});onDisconnect();}}})();
 return {kind:'serial',send:(text)=>{if(closed)return Promise.reject(Error('Disconnected'));chain=chain.then(()=>writer.write(new TextEncoder().encode(text+'\n')));return chain;},close:async()=>{if(closed)return;closed=true;await reader.cancel().catch(()=>{});await loop;await chain.catch(()=>{});writer.releaseLock();await port.close();}};
}
