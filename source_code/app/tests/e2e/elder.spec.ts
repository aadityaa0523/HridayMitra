import {test,expect} from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
async function setup(page:import('@playwright/test').Page){
 await page.goto('/');await page.getByRole('button',{name:'Open demo',exact:true}).click();
 await page.getByRole('button',{name:'Settings',exact:true}).filter({visible:true}).click();
 await page.getByLabel('PIN (6–12 digits)',{exact:true}).fill('246810');await page.getByLabel('Confirm PIN',{exact:true}).fill('246810');
 await page.getByRole('checkbox',{name:'I agree to store synthetic demo data on this phone.'}).check();
 await page.getByRole('button',{name:'Create demo vault'}).click();await page.getByRole('button',{name:'Load five-month demo'}).click();
 await expect(page.getByText('164 synthetic days stored')).toBeVisible();
 await page.getByRole('button',{name:'Home',exact:true}).filter({visible:true}).click();
}
test('elder answers and dose survive offline reload',async({page,context})=>{
 test.setTimeout(60000);await setup(page);
 await page.getByRole('button',{name:/Daily questions/}).click();
 await page.getByRole('button',{name:'Yes',exact:true}).click();
 await page.getByRole('button',{name:'No',exact:true}).click();
 await expect(page.getByRole('dialog').getByText('Your practice answers are saved.',{exact:true}).first()).toBeVisible();
 await page.getByRole('button',{name:'Close',exact:true}).click();
 await page.getByRole('button',{name:/My medicines/}).click();
 await page.getByRole('button',{name:'Taken',exact:true}).click();
 await expect(page.getByRole('dialog').getByText('Practice dose marked taken.',{exact:true}).first()).toBeVisible();
 expect((await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze()).violations).toEqual([]);
 await page.getByRole('button',{name:'Close',exact:true}).click();
 await expect(page.getByTestId('offline-status')).toHaveText('App ready offline');
 await context.setOffline(true);await page.reload();
 await page.getByRole('button',{name:'Settings',exact:true}).filter({visible:true}).click();
 await page.getByLabel('PIN (6–12 digits)',{exact:true}).fill('246810');await page.getByRole('button',{name:'Unlock records',exact:true}).click();
 await expect(page.getByText('164 synthetic days stored')).toBeVisible();
 await page.getByRole('button',{name:'Home',exact:true}).filter({visible:true}).click();
 await page.getByRole('button',{name:/My medicines/}).click();
 await expect(page.getByRole('dialog').getByText('Practice dose marked taken.',{exact:true}).first()).toBeVisible();
});
test('SOS ignores short press and supports countdown cancellation',async({page})=>{
 await page.goto('/');await page.getByRole('button',{name:'Open demo',exact:true}).click();
 await page.getByRole('button',{name:/Get help/}).click();
 await page.getByRole('button',{name:'Hold for 2 seconds'}).click();
 await expect(page.getByRole('button',{name:'Cancel',exact:true})).toHaveCount(0);
 await page.clock.install();
 const hold=page.getByRole('button',{name:'Hold for 2 seconds'});
 await hold.dispatchEvent('keydown',{key:'Enter',repeat:false});
 await page.clock.fastForward(2100);
 await expect(page.getByRole('button',{name:'Cancel',exact:true})).toBeVisible();
 await page.getByRole('button',{name:'Cancel',exact:true}).click();
 await page.clock.fastForward(6000);
 await expect(page.getByRole('dialog')).toHaveCount(0);
 expect(page.url()).toContain('http://127.0.0.1');
});
test('foreground reminder snoozes rather than marking a dose taken',async({page})=>{
 test.setTimeout(60000);await setup(page);
 await page.getByRole('button',{name:/My medicines/}).click();
 await page.getByRole('button',{name:'Try reminder now'}).click();
 await expect(page.getByRole('heading',{name:'Practice medicine reminder',exact:true})).toBeVisible();
 await page.getByRole('button',{name:/Snooze 10 minutes/}).click();
 await expect(page.getByRole('heading',{name:'My medicines',exact:true})).toBeVisible();
 await expect(page.getByRole('button',{name:'Taken',exact:true})).toBeVisible();
 await expect(page.getByText('Reminder snoozed for ten minutes.',{exact:true})).toBeVisible();
});

