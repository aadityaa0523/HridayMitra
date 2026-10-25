import type {TFunction} from 'i18next';
export function copyKey(text:string){let n=2166136261;for(const c of text){n^=c.charCodeAt(0);n=Math.imul(n,16777619);}return 'c'+(n>>>0).toString(16);}
export function translateCopy(t:TFunction,en:string,hi:string,language:string){return language==='hi'?hi:language==='en'?en:t('extra.'+copyKey(en),{defaultValue:en});}
