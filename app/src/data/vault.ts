import Dexie, {type Table} from 'dexie';
export const collections=['patients','contacts','checkins','alerts','medicines','doses','visits','labs','notes','reports','audit','settings','outbox'] as const;
export type Collection=typeof collections[number];
export type Envelope={id:string;iv:number[];cipher:number[];version:1};
type Metadata={id:'vault';salt:number[];iterations:310000;verifier:Envelope;version:1};
export class Database extends Dexie {
 meta!:Table<Metadata,string>;
 constructor(name='saathi-demo-vault'){
  super(name);
  const original=Object.fromEntries(collections.filter(x=>x!=='alerts'&&x!=='outbox').map(x=>[x,'id']));
  this.version(1).stores({meta:'id',...original});
  this.version(2).stores({alerts:'id',outbox:'id'});
 }
}
const encoder=new TextEncoder(),decoder=new TextDecoder();
async function derive(pin:string,salt:number[]){
 const material=await crypto.subtle.importKey('raw',encoder.encode(pin),'PBKDF2',false,['deriveKey']);
 return crypto.subtle.deriveKey({name:'PBKDF2',hash:'SHA-256',salt:new Uint8Array(salt),iterations:310000},material,{name:'AES-GCM',length:256},false,['encrypt','decrypt']);
}
async function seal(key:CryptoKey,kind:string,id:string,value:unknown):Promise<Envelope>{
 const iv=crypto.getRandomValues(new Uint8Array(12));
 const cipher=await crypto.subtle.encrypt({name:'AES-GCM',iv,additionalData:encoder.encode('saathi:v1:'+kind+':'+id)},key,encoder.encode(JSON.stringify(value)));
 return {id,iv:[...iv],cipher:[...new Uint8Array(cipher)],version:1};
}
async function unseal<T>(key:CryptoKey,kind:string,row:Envelope):Promise<T>{
 if(row.version!==1)throw new Error('Unsupported record version');
 const plain=await crypto.subtle.decrypt({name:'AES-GCM',iv:new Uint8Array(row.iv),additionalData:encoder.encode('saathi:v1:'+kind+':'+row.id)},key,new Uint8Array(row.cipher));
 return JSON.parse(decoder.decode(plain)) as T;
}
export class Vault{
 readonly db:Database;
 private key:CryptoKey|null=null;
 private epoch=0;
 constructor(name?:string){this.db=new Database(name);}
 get unlocked(){return this.key!==null;}
 lock(){this.key=null;this.epoch++;}
 async exists(){return Boolean(await this.db.meta.get('vault'));}
 private session(){if(!this.key)throw new Error('Vault locked');return {key:this.key,epoch:this.epoch};}
 private check(epoch:number){if(epoch!==this.epoch||!this.key)throw new Error('Session ended');}
 async create(pin:string,consent:boolean){
  if(!consent||!/^\d{6,12}$/.test(pin))throw new Error('PIN and consent required');
  if(await this.exists())throw new Error('Vault already exists');
  const epoch=this.epoch,salt=[...crypto.getRandomValues(new Uint8Array(16))],key=await derive(pin,salt);
  const verifier=await seal(key,'meta','vault',{marker:'Saathi vault v1'});
  const id=crypto.randomUUID(),audit=await seal(key,'audit',id,{id,at:new Date().toISOString(),actor:'demo-caregiver',action:'consent',version:'synthetic-demo-v1',details:'Synthetic data only; shared-phone demo roles are not authenticated identities.'});
  if(epoch!==this.epoch)throw new Error('Session ended');
  await this.db.transaction('rw',this.db.meta,this.db.table('audit'),async()=>{
   if(await this.db.meta.get('vault'))throw new Error('Vault already exists');
   await this.db.meta.add({id:'vault',salt,iterations:310000,version:1,verifier});
   await this.db.table('audit').add(audit);
  });
  if(epoch===this.epoch)this.key=key;
 }
 async unlock(pin:string){
  this.lock();const epoch=this.epoch;
  const meta=await this.db.meta.get('vault');if(!meta||meta.version!==1||meta.iterations!==310000)throw new Error('Vault unavailable');
  const key=await derive(pin,meta.salt),check=await unseal<{marker:string}>(key,'meta',meta.verifier);
  if(check.marker!=='Saathi vault v1'||epoch!==this.epoch)throw new Error('Unlock failed');
  this.key=key;
 }
 async all<T>(kind:Collection):Promise<T[]>{
  const {key,epoch}=this.session(),rows=await this.db.table<Envelope>(kind).toArray();
  try{const values=await Promise.all(rows.map(row=>unseal<T>(key,kind,row)));this.check(epoch);return values;}
  catch(error){this.lock();throw error;}
 }
 async write(entries:{kind:Collection;id:string;value:unknown}[],action:string,details:unknown,addOnly=false,actor='demo-caregiver'){
  const {key,epoch}=this.session(),id=crypto.randomUUID();
  const all=[...entries,{kind:'audit' as Collection,id,value:{id,at:new Date().toISOString(),actor,action,details}}];
  // Crypto finishes before opening the IndexedDB transaction.
  const encrypted=await Promise.all(all.map(async item=>({...item,row:await seal(key,item.kind,item.id,item.value)})));
  this.check(epoch);
  await this.db.transaction('rw',[...new Set(all.map(x=>x.kind))].map(k=>this.db.table(k)),async()=>{
   this.check(epoch);
   for(const item of encrypted){if(addOnly)await this.db.table(item.kind).add(item.row);else await this.db.table(item.kind).put(item.row);}
  });
  this.check(epoch);
 }
 async erase(){
  this.session();this.lock();
  await this.db.transaction('rw',this.db.tables,async()=>{for(const table of this.db.tables)await table.clear();});
 }
}

