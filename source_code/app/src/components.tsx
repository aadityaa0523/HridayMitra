import type { ReactNode } from 'react';
import { useTranslation } from 'react-i18next';
import { Mic, CircleCheck, CircleAlert, CircleX, Clock3 } from 'lucide-react';
export type HealthStatus='unknown'|'locked'|'learning'|'green'|'amber'|'red';
export function StatusOrb({status}:{status:HealthStatus}) {
 const {t}=useTranslation();
 const Icon=status==='green'?CircleCheck:status==='amber'?CircleAlert:status==='red'?CircleX:Clock3;
 return <div className={'status-orb '+status} role="img" aria-label={t('status.'+status)}><Icon size={74} strokeWidth={1.5}/><span>{t('status.'+status)}</span></div>;
}
export function BigActionButton({icon,children,detail,onClick,tone='plain'}:{icon:ReactNode;children:ReactNode;detail?:string;onClick:()=>void;tone?:string}) {
 return <button className={'big-action '+tone} onClick={onClick}><span className="action-icon" aria-hidden="true">{icon}</span><span><strong>{children}</strong>{detail&&<small>{detail}</small>}</span><span className="arrow" aria-hidden="true">↗</span></button>;
}
export function MicButton({onClick}:{onClick:()=>void}) {
 const {t}=useTranslation();
 return <button className="mic-button" onClick={onClick} aria-label={t('voice.button')}><Mic size={32}/></button>;
}
