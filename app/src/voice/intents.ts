import en from './intents.en.json';
import hi from './intents.hi.json';
export type Intent=keyof typeof en;
export const phrases={en,hi};
export const normalize=(s:string)=>s.normalize('NFKC').toLowerCase().replace(/[^\p{L}\p{N}\p{M}\s]/gu,' ').replace(/\s+/g,' ').trim();
function similarity(a:string,b:string){
 const row=Array.from({length:b.length+1},(_,i)=>i);
 for(let i=1;i<=a.length;i++){let diagonal=row[0];row[0]=i;for(let j=1;j<=b.length;j++){const old=row[j];row[j]=Math.min(row[j]+1,row[j-1]+1,diagonal+(a[i-1]===b[j-1]?0:1));diagonal=old;}}
 return 1-row[b.length]/Math.max(a.length,b.length,1);
}
export function matchIntent(text:string,lang:string):Intent|null{
 const input=normalize(text);if(!input||!['en','hi'].includes(lang))return null;
 const dictionary=lang.startsWith('hi')?hi:en;
 for(const [intent,list] of Object.entries(dictionary))if(list.some(p=>normalize(p)===input))return intent as Intent;
 // Consequential actions, yes/no and negated speech never fuzzy-match.
 if(/\b(no|not|never|don't|didnt|nahi|nahin|mat)\b|नहीं|नही|मत/.test(input))return null;
 const safe:Intent[]=['status_today','medicine_next','read_screen','repeat','go_home','water_left'];
 const ranked=safe.map(intent=>({intent,score:Math.max(...dictionary[intent].map(p=>similarity(input,normalize(p))))})).sort((a,b)=>b.score-a.score);
 return ranked[0].score>=.8&&ranked[0].score-(ranked[1]?.score??0)>=.08?ranked[0].intent:null;
}


