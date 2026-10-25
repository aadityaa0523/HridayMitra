import {useTranslation} from 'react-i18next';
import {savePreference} from './preferences';
import {useState} from 'react';
import {playClips,stopSpeech} from './voice/speech';
export type Theme='light'|'dark'|'contrast';
export function initialTheme():Theme{try{const x=localStorage.getItem('saathi.theme');return x==='dark'||x==='contrast'?x:'light';}catch{return 'light';}}
export function DisplaySettings({onTheme}:{onTheme:(theme:Theme)=>void}){
 const {t}=useTranslation(),[theme,setTheme]=useState(initialTheme),[large,setLarge]=useState(()=>{try{return localStorage.getItem('saathi.large')==='true';}catch{return false;}});
 return <section className="settings-card"><h2>{t('polish.display')}</h2><label>{t('polish.theme')}<select aria-label={t('polish.theme')} value={theme} onChange={e=>{const value=e.target.value as Theme;setTheme(value);savePreference('theme',value);onTheme(value);}}>{(['light','dark','contrast'] as Theme[]).map(x=><option key={x} value={x}>{t('polish.'+x)}</option>)}</select></label><label className="check-label"><input type="checkbox" checked={large} onChange={e=>{setLarge(e.target.checked);savePreference('large',String(e.target.checked));document.documentElement.dataset.large=String(e.target.checked);}}/>{t('polish.large')}</label><p>{t('polish.elderContrast')}</p><h2>{t('polish.audio')}</h2><p>{t('polish.audioHelp')}</p><button className="secondary" onClick={()=>void playClips(['/audio/hi/greeting.mp3']).catch(()=>{})}>{t('polish.playAudio')}</button><button className="secondary" onClick={stopSpeech}>{t('polish.stopAudio')}</button></section>;
}
