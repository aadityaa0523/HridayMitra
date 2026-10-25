export const languages=[['en','English'],['hi','हिन्दी'],['ta','தமிழ்'],['te','తెలుగు'],['kn','ಕನ್ನಡ'],['mr','मराठी'],['bn','বাংলা'],['gu','ગુજરાતી'],['ml','മലയാളം'],['or','ଓଡ଼ିଆ']] as const;
export type Language=typeof languages[number][0];
export const languageCode=(value:string|null):Language=>languages.some(([code])=>code===value)?value as Language:'en';
export const speechSupported=(lang:string)=>lang==='en'||lang==='hi';
