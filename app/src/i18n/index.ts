import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import en from './en.json';
import hi from './hi.json';
import {languageCode} from './languages';
let language=languageCode(null);
try { language=languageCode(localStorage.getItem('saathi.language')); } catch { /* Preferences can remain session-only. */ }
const files=import.meta.glob<{default:Record<string,unknown>}>(['./*.json','!./en.json','!./hi.json']);
export async function setLanguage(code:string){
 const next=languageCode(code);
 if(!i18n.hasResourceBundle(next,'translation')){const resource=await files['./'+next+'.json']();i18n.addResourceBundle(next,'translation',resource.default);}
 await i18n.changeLanguage(next);
}
i18n.use(initReactI18next).init({resources:{en:{translation:en},hi:{translation:hi}},lng:language==='hi'?'hi':'en',fallbackLng:'en',interpolation:{escapeValue:false}}).then(()=>{if(language!=='en'&&language!=='hi')return setLanguage(language);});
export default i18n;

