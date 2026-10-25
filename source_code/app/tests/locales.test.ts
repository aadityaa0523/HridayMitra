import { expect, it } from 'vitest';
import en from '../src/i18n/en.json';
import hi from '../src/i18n/hi.json';
import {languageCode,speechSupported,languages} from '../src/i18n/languages';
import {clipSequence} from '../src/voice/speech';
import {modelURL} from '../src/voice/offline';
import {matchIntent} from '../src/voice/intents';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import clips from '../src/voice/clips.hi.json';
function keys(value:Record<string,unknown>, prefix=''):string[]{return Object.entries(value).flatMap(([key,item])=>typeof item==='object'&&item!==null?keys(item as Record<string,unknown>,prefix+key+'.'):[prefix+key]).sort();}
it('Hindi includes every English translation key',()=>expect(keys(hi)).toEqual(keys(en)));
it('all ten offline language files have complete keys, review metadata and intact interpolation',()=>{
 const flat=(obj:Record<string,unknown>,prefix=''):Record<string,string>=>Object.fromEntries(Object.entries(obj).flatMap(([k,v])=>typeof v==='object'&&v!==null?Object.entries(flat(v as Record<string,unknown>,prefix+k+'.')):[[prefix+k,String(v)]]));
 const source=flat(en);expect(languages).toHaveLength(10);
 for(const [code] of languages){const value=JSON.parse(readFileSync(new URL('../src/i18n/'+code+'.json',import.meta.url),'utf8').replace(/^\uFEFF/,''));expect(keys(value),code).toEqual(keys(en));expect(value._meta.status).toBe('needs review');const target=flat(value);for(const key in source)expect((target[key].match(/\{\{[^}]+\}\}/g)||[]).sort(),code+':'+key).toEqual((source[key].match(/\{\{[^}]+\}\}/g)||[]).sort());}
});
it('Hindi fallback clips have verified bytes and never substitute generic speech for unknown clinical text',()=>{
 expect(clips.length).toBeGreaterThanOrEqual(40);expect(new Set(clips.map(c=>c.key)).size).toBe(clips.length);
 for(const clip of clips){const bytes=readFileSync(new URL('../public'+clip.url,import.meta.url));expect(bytes.length).toBe(clip.bytes);expect(createHash('sha256').update(bytes).digest('hex')).toBe(clip.sha256);expect(clipSequence(clip.text)).toEqual([clip.url]);}
 expect(clipSequence(hi.greeting+'. '+hi.vault.historical+'. '+hi.status.red+'. '+hi.disclaimer)).toHaveLength(4);
 expect(clipSequence('Change medicine to 2 tablets')).toBeNull();expect(clipSequence(hi.status.red+'. Custom clinician instructions')).toBeNull();
});
it('unsupported recognition languages never silently select English',()=>{
 expect(languageCode('ta')).toBe('ta');expect(languageCode('invalid')).toBe('en');expect(speechSupported('ta')).toBe(false);expect(()=>modelURL('ta')).toThrow();expect(matchIntent('medicine taken','ta')).toBeNull();
});
