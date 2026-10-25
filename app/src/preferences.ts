export type Role='elder'|'family'|'asha'|'doctor';
export const roles:Role[]=['elder','family','asha','doctor'];
export function storedRole(value:string|null):Role {return roles.includes(value as Role)?value as Role:'elder';}
export function savePreference(key:string,value:string):boolean {
 try {localStorage.setItem('saathi.'+key,value);return true;} catch {return false;}
}

