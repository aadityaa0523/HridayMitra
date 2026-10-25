import clips from './clips.hi.json';
const normalize=(s:string)=>s.replace(/\s+/g,' ').trim();
export function clipSequence(text:string):string[]|null{
 const value=normalize(text),exact=clips.find(c=>normalize(c.text)===value);if(exact)return [exact.url];
 // Every fragment must match. Never substitute a generic recording for a plan,
 // medicine name, numeric reading, delivery claim or other dynamic content.
 const parts=value.split(/\.\s+/).filter(Boolean),urls=parts.map(p=>clips.find(c=>normalize(c.text).replace(/[.]$/,'')===p.replace(/[.]$/,''))?.url);
 return parts.length>1&&urls.every(Boolean)?urls as string[]:null;
}
let current:HTMLAudioElement|null=null,epoch=0;
export function isSpeaking(){return Boolean(current)||Boolean(window.speechSynthesis?.speaking);}
export function stopSpeech(){epoch++;current?.pause();current=null;window.speechSynthesis?.cancel();}
export async function playClips(urls:string[]){
 stopSpeech();const generation=epoch;
 try{for(const url of urls){if(generation!==epoch)return false;const audio=new Audio(url);current=audio;
  await new Promise<void>((resolve,reject)=>{audio.onended=()=>resolve();audio.onerror=()=>reject(Error('Audio unavailable'));audio.onpause=()=>{if(generation!==epoch)resolve();};audio.play().catch(reject);});
 }
 return generation===epoch;}finally{if(generation===epoch)current=null;}
}
export async function speakOffline(text:string,lang:string){
 stopSpeech();const voice=window.speechSynthesis?.getVoices().find(v=>v.localService&&v.lang.toLowerCase().startsWith(lang));
 if(voice){const utterance=new SpeechSynthesisUtterance(text);utterance.voice=voice;utterance.lang=voice.lang;utterance.rate=.85;window.speechSynthesis.speak(utterance);return 'local' as const;}
 const urls=lang==='hi'?clipSequence(text):null;if(!urls)return 'unavailable' as const;
 await playClips(urls);return 'clip' as const;
}
