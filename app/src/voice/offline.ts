import {speechSupported} from '../i18n/languages';
import type {Model,KaldiRecognizer} from 'vosk-browser/dist/model';

const PACK_CACHE='saathi-voice-packs-v1';
export const modelURL=(lang:string)=>{if(!speechSupported(lang))throw new Error('Unsupported recognition language');return new URL('/models/'+(lang==='hi'?'hi':'en')+'.bin',location.href).href;};
export async function hasPack(lang:string){if(!speechSupported(lang))return false;return Boolean(await (await caches.open(PACK_CACHE)).match(modelURL(lang)));}
export async function installPack(lang:string){
 const url=modelURL(lang),response=await fetch(url+'?download=1');
 if(!response.ok)throw new Error('Model not available');
 const blob=await response.blob();if(blob.size<1000000||blob.size>100000000)throw new Error('Invalid model');
 const magic=new Uint8Array(await blob.slice(0,2).arrayBuffer());if(magic[0]!==31||magic[1]!==139)throw new Error('Invalid archive');
 const manifestResponse=await fetch('/models/manifest.json');if(!manifestResponse.ok)throw new Error('Missing model manifest');
 const manifest=await manifestResponse.json();const expected=manifest[lang.startsWith('hi')?'hi':'en'];
 const digest=[...new Uint8Array(await crypto.subtle.digest('SHA-256',await blob.arrayBuffer()))].map(x=>x.toString(16).padStart(2,'0')).join('');
 if(!expected||expected.sha256!==digest||expected.bytes!==blob.size)throw new Error('Model verification failed');
 await (await caches.open(PACK_CACHE)).put(url,new Response(blob,{headers:{'Content-Type':'application/gzip'}}));
 // Fetch the runtime while online, so its service-worker runtime cache is ready.
 await import('vosk-browser');
}
export async function deletePacks(){await caches.delete(PACK_CACHE);indexedDB.deleteDatabase('/vosk');}
export class OfflineVoice{
 private model:Model|null=null;
 private recognizer:KaldiRecognizer|null=null;
 private stream:MediaStream|null=null;
 private audio:AudioContext|null=null;
 private processor:ScriptProcessorNode|null=null;
 private epoch=0;
 private cancelLoad:(()=>void)|null=null;
 async start(lang:string,onText:(text:string,final:boolean)=>void){
  this.stop();const epoch=this.epoch;
  const packed=await (await caches.open(PACK_CACHE)).match(modelURL(lang));
  if(!packed)throw new Error('Install language pack first');
  // Stable URL avoids duplicate extracted models in Vosk IndexedDB storage.
  // The service worker serves only explicitly installed, verified packs.
  try{
   const {Model}=await import('vosk-browser');
   if(epoch!==this.epoch)return false;
   const model=new Model(modelURL(lang),-2);this.model=model;
   await new Promise<void>((resolve,reject)=>{
    const timeout=setTimeout(()=>reject(new Error('Model load timed out')),90000);
    const done=(error?:Error)=>{clearTimeout(timeout);this.cancelLoad=null;if(error)reject(error);else resolve();};
    this.cancelLoad=()=>done(new Error('Cancelled'));
    model.on('load',message=>{if('result' in message&&message.result===true)done();else done(new Error('Model load failed'));});
    model.on('error',()=>done(new Error('Model load failed')));
   });
   if(epoch!==this.epoch){model.terminate();return false;}
   this.model=model;
   const stream=await navigator.mediaDevices.getUserMedia({video:false,audio:{channelCount:1,echoCancellation:true,noiseSuppression:true}});
   if(epoch!==this.epoch){stream.getTracks().forEach(t=>t.stop());return false;}
   this.stream=stream;
   const audio=new AudioContext();this.audio=audio;await audio.resume();
   const recognizer=new model.KaldiRecognizer(audio.sampleRate);this.recognizer=recognizer;
   recognizer.on('result',m=>{if(epoch===this.epoch&&'result' in m&&'text' in m.result&&m.result.text)onText(m.result.text,true);});
   recognizer.on('partialresult',m=>{if(epoch===this.epoch&&'result' in m&&'partial' in m.result)onText(m.result.partial,false);});
   const node=audio.createScriptProcessor(4096,1,1);this.processor=node;
   node.onaudioprocess=e=>{if(epoch===this.epoch)recognizer.acceptWaveform(e.inputBuffer);};
   audio.createMediaStreamSource(stream).connect(node);
   const silent=audio.createGain();silent.gain.value=0;node.connect(silent);silent.connect(audio.destination);return true;
  }catch(error){if(epoch===this.epoch)this.stop();throw error;}

 }
 stop(){this.epoch++;this.cancelLoad?.();this.cancelLoad=null;this.processor?.disconnect();if(this.processor)this.processor.onaudioprocess=null;this.stream?.getTracks().forEach(t=>t.stop());void this.audio?.close();this.recognizer?.remove();this.model?.terminate();this.processor=null;this.stream=null;this.audio=null;this.model=null;this.recognizer=null;}
}

