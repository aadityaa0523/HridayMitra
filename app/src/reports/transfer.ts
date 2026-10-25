import type {Report} from './model';
import {reportTypes} from './model';
export const MAX_TRANSFER=240000;
export async function digest(bytes:Uint8Array){return [...new Uint8Array(await crypto.subtle.digest('SHA-256',new Uint8Array(bytes)))].map(x=>x.toString(16).padStart(2,'0')).join('');}
export function base64(bytes:Uint8Array){let s='';for(const x of bytes)s+=String.fromCharCode(x);return btoa(s);}
export function unbase64(text:string){return Uint8Array.from(atob(text),x=>x.charCodeAt(0));}
export async function encodeTransfer(report:Report){
 const raw=new TextEncoder().encode(JSON.stringify(report));if(raw.length>MAX_TRANSFER)throw new Error('Report too large for QR');
 const bytes=new Uint8Array(await new Response(new Blob([raw]).stream().pipeThrough(new CompressionStream('gzip'))).arrayBuffer()),hash=await digest(bytes),body=base64(bytes),parts=body.match(/.{1,650}/g)!;
 if(parts.length>120)throw new Error('Use file sharing for this report');
 return parts.map((part,index)=>JSON.stringify({v:1,id:report.id,hash,i:index,n:parts.length,data:part}));
}
export function validateReport(value:unknown):Report{
 const r=value as Report;
 if(!r||r.version!==1||r.synthetic!==true||!reportTypes.includes(r.type)||!['en','hi'].includes(r.language)||!Array.isArray(r.sections)||!Array.isArray(r.charts)||r.sections.length>100||r.charts.length>30)throw new Error('Invalid report');
 for(const key of ['id','patientId','patientName','date','start','generatedAt','author'] as const)if(typeof r[key]!=='string'||r[key].length>200)throw new Error('Invalid header');
 for(const s of r.sections)if(typeof s.title!=='string'||!Array.isArray(s.lines)||s.lines.length>2000||s.lines.some(x=>typeof x!=='string'||x.length>10000))throw new Error('Invalid content');
 for(const c of r.charts)if(typeof c.label!=='string'||!Array.isArray(c.points)||c.points.length>4000||c.points.some(p=>typeof p.date!=='string'||(p.value!==null&&(typeof p.value!=='number'||!Number.isFinite(p.value))))||(c.band!==null&&(!Array.isArray(c.band)||c.band.length!==2||c.band.some(n=>!Number.isFinite(n)))))throw new Error('Invalid chart');
 return r;
}
export class TransferReceiver{
 private frames=new Map<number,string>();private session='';private count=0;private hash='';
 get progress(){return {received:this.frames.size,total:this.count};}
 async add(text:string):Promise<Report|null>{
  if(text.length>1500)throw new Error('Oversized frame');const f=JSON.parse(text);
  if(f.v!==1||typeof f.id!=='string'||f.id.length>80||typeof f.hash!=='string'||!/^[a-f0-9]{64}$/.test(f.hash)||!Number.isInteger(f.n)||f.n<1||f.n>120||!Number.isInteger(f.i)||f.i<0||f.i>=f.n||typeof f.data!=='string'||!/^[A-Za-z0-9+/=]{1,650}$/.test(f.data))throw new Error('Invalid frame');
  if(this.session&&(this.session!==f.id||this.hash!==f.hash||this.count!==f.n))throw new Error('Different transfer: reset first');
  if(this.frames.has(f.i)&&this.frames.get(f.i)!==f.data)throw new Error('Conflicting duplicate');
  this.session=f.id;this.count=f.n;this.hash=f.hash;this.frames.set(f.i,f.data);if(this.frames.size!==this.count)return null;
  const bytes=unbase64(Array.from({length:this.count},(_,i)=>this.frames.get(i)!).join(''));if(await digest(bytes)!==this.hash)throw new Error('Checksum mismatch');
  const reader=new Blob([new Uint8Array(bytes)]).stream().pipeThrough(new DecompressionStream('gzip')).getReader();const chunks:Uint8Array[]=[];let size=0;
  while(true){const {value,done}=await reader.read();if(done)break;size+=value.length;if(size>MAX_TRANSFER){await reader.cancel();throw new Error('Expanded report too large');}chunks.push(value);}
  const report=validateReport(JSON.parse(await new Blob(chunks as BlobPart[]).text()));if(report.id!==this.session)throw new Error('Wrong report identity');return report;
 }
}
