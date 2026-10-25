import {describe,it,expect} from 'vitest';
import {storedRole} from '../src/preferences';
describe('role restoration',()=>{it('rejects invalid and missing persisted roles',()=>{expect(storedRole('administrator')).toBe('elder');expect(storedRole(null)).toBe('elder');});it('keeps supported role',()=>expect(storedRole('asha')).toBe('asha'));});
