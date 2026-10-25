import {test,expect} from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('encrypted demo survives offline reload, rejects wrong PIN and erases cleanly',async({page,context})=>{
 test.setTimeout(60000);
 await page.goto('/');
 await page.getByRole('button',{name:'Open demo',exact:true}).click();
 await expect(page.getByTestId('offline-status')).toHaveText('App ready offline',{timeout:30000});
 await page.getByRole('button',{name:'Settings',exact:true}).filter({visible:true}).click();
 await page.getByLabel('PIN (6–12 digits)',{exact:true}).fill('246810');
 await page.getByLabel('Confirm PIN',{exact:true}).fill('246810');
 await page.getByRole('checkbox',{name:'I agree to store synthetic demo data on this phone.'}).check();
 await page.getByRole('button',{name:'Create demo vault'}).click();
 await page.getByRole('button',{name:'Load five-month demo'}).click();
 await expect(page.getByText('164 synthetic days stored')).toBeVisible();
 await page.getByRole('button',{name:'Next red-alert day'}).click();
 await expect(page.getByLabel('Replay date',{exact:true})).not.toHaveValue('30');
 const selected=await page.getByLabel('Replay date',{exact:true}).inputValue();
 expect(Number(selected)).toBeGreaterThan(30);
 const raw=await page.evaluate(async()=>new Promise<string>((resolve,reject)=>{
  const request=indexedDB.open('saathi-demo-vault');request.onerror=()=>reject(request.error);request.onsuccess=()=>{
   const db=request.result;const tx=db.transaction(['patients','checkins'],'readonly');
   const values:unknown[]=[];
   for(const store of ['patients','checkins']){const r=tx.objectStore(store).getAll();r.onsuccess=()=>values.push(r.result);}
   tx.oncomplete=()=>{db.close();resolve(JSON.stringify(values));};tx.onerror=()=>reject(tx.error);
  };
 }));
 expect(raw).not.toContain('Demo elder');expect(raw).not.toContain('weight_kg');
 await page.getByRole('button',{name:'Home',exact:true}).filter({visible:true}).click();
 await expect(page.getByRole('img',{name:'Needs prompt attention'})).toBeVisible();
 await expect(page.getByText('No doctor’s plan has been recorded.')).toBeVisible();
 const a11y=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();
 expect(a11y.violations).toEqual([]);
 await context.setOffline(true);await page.reload();
 await expect(page.getByRole('img',{name:'Records locked'})).toBeVisible();
 await expect(page.getByText('Demo elder 01',{exact:true})).toHaveCount(0);
 await page.getByRole('button',{name:'Settings',exact:true}).filter({visible:true}).click();
 await page.getByLabel('PIN (6–12 digits)',{exact:true}).fill('999999');
 await page.getByRole('button',{name:'Unlock records',exact:true}).click();
 await expect(page.getByRole('alert')).toContainText('Check your PIN');
 await page.getByLabel('PIN (6–12 digits)',{exact:true}).fill('246810');
 await page.getByRole('button',{name:'Unlock records',exact:true}).click();
 await expect(page.getByLabel('Replay date',{exact:true})).toHaveValue(selected);
 await page.getByRole('checkbox',{name:'Delete all demo records and the PIN from this phone.'}).check();
 await page.getByRole('button',{name:'Delete demo data',exact:true}).click();
 await expect(page.getByRole('button',{name:'Create demo vault'})).toBeVisible();
});
