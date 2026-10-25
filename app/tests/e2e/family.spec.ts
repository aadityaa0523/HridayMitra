import {test,expect,type Page} from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
async function setup(page:Page){
 await page.goto('/');await page.getByRole('button',{name:'Open demo',exact:true}).click();
 await page.getByRole('button',{name:'Settings',exact:true}).filter({visible:true}).click();
 await page.getByLabel('PIN (6–12 digits)',{exact:true}).fill('246810');await page.getByLabel('Confirm PIN',{exact:true}).fill('246810');
 await page.getByRole('checkbox',{name:'I agree to store synthetic demo data on this phone.'}).check();
 await page.getByRole('button',{name:'Create demo vault'}).click();await page.getByRole('button',{name:'Load five-month demo'}).click();
 await expect(page.getByText('164 synthetic days stored')).toBeVisible();
}
async function role(page:Page,name:string){
 await page.getByRole('button',{name:'Settings',exact:true}).filter({visible:true}).click();
 await page.getByRole('button',{name,exact:true}).click();
}
async function detail(page:Page){await page.getByRole('button').filter({has:page.getByRole('heading',{name:'Demo elder 01',exact:true})}).click();}
test('family schedule connects to elder dose, stock and offline calendar',async({page,context})=>{
 test.setTimeout(90000);await setup(page);await page.getByRole('button',{name:'Family',exact:true}).click();await detail(page);
 await page.getByRole('button',{name:'Medicine manager',exact:true}).click();await page.getByRole('button',{name:'Add medicine',exact:true}).click();
 await page.getByLabel('Medicine name',{exact:true}).fill('Demo tablet');await page.getByLabel('Strength from prescription').fill('Demo strength');
 await page.getByLabel('Times, separated by commas (24-hour)').fill('08:00');await page.getByLabel('Tablets remaining',{exact:true}).fill('10');
 await page.getByRole('checkbox',{name:'I copied the medicine and schedule from the existing prescription.'}).check();await page.getByRole('button',{name:'Save medicine',exact:true}).click();
 await expect(page.getByText('Medicine saved. It is available in Saathi mode.')).toBeVisible();
 await role(page,'Saathi');await page.getByRole('button',{name:/My medicines/}).click();
 await expect(page.getByRole('dialog').getByText('Demo tablet · Demo strength')).toBeVisible();
 await page.getByRole('button',{name:'Try reminder now',exact:true}).click();await expect(page.getByRole('heading',{name:'Medicine reminder',exact:true})).toBeVisible();
 await page.getByRole('button',{name:/Snooze 10 minutes/}).click();await page.getByRole('button',{name:'Taken',exact:true}).click();
 await expect(page.getByRole('dialog').getByText('Dose marked taken. Stock updated.').first()).toBeVisible();await page.getByRole('button',{name:'Close',exact:true}).click();
 await role(page,'Family');await detail(page);await expect(page.getByText('1 / 1',{exact:true})).toBeVisible();
 await page.getByRole('button',{name:'30 days',exact:true}).click();await expect(page.locator('.trend-card')).toHaveCount(5);
 expect((await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze()).violations).toEqual([]);
 await page.getByRole('button',{name:'Medicine manager',exact:true}).click();await expect(page.getByText(/Tablets remaining: 9/)).toBeVisible();
 await expect(page.getByTestId('offline-status')).toHaveText('App ready offline');await context.setOffline(true);await page.reload();
 await page.getByRole('button',{name:'Settings',exact:true}).filter({visible:true}).click();await page.getByLabel('PIN (6–12 digits)',{exact:true}).fill('246810');await page.getByRole('button',{name:'Unlock records',exact:true}).click();await expect(page.getByText('164 synthetic days stored')).toBeVisible();
 await page.getByRole('button',{name:'Home',exact:true}).filter({visible:true}).click();await detail(page);await page.getByRole('button',{name:'Medicine manager',exact:true}).click();await expect(page.getByText(/Tablets remaining: 9/)).toBeVisible();
});
test('family records a plan checklist and response without clearing a red alert',async({page})=>{
 test.setTimeout(90000);await setup(page);await page.getByRole('button',{name:'Next red-alert day',exact:true}).click();await page.getByRole('button',{name:'Family',exact:true}).click();await detail(page);
 await page.getByLabel('Elder phone number',{exact:true}).fill('+910000000001');await page.getByLabel('Red plan steps',{exact:true}).fill('Contact the care team\nKeep the prescription ready');
 await page.getByRole('checkbox',{name:'Contact details are correct; any plan text copies existing clinician instructions.'}).check();await page.getByRole('button',{name:'Save care details',exact:true}).click();await expect(page.getByText('Care details saved with an audit entry.')).toBeVisible();
 await expect(page.locator('.plan-missing').getByText('Contact the care team',{exact:true})).toBeVisible();
 await page.getByRole('button',{name:'Open care alert',exact:true}).click();await page.getByRole('checkbox',{name:'Contact the care team',exact:true}).check();await page.getByRole('button',{name:"I'm checking (1)",exact:true}).click();
 await expect(page.getByText('Response saved. Delivery remains pending on this phone.')).toBeVisible();await expect(page.getByRole('link',{name:'Call elder',exact:true})).toHaveAttribute('href','tel:+910000000001');
 await page.getByRole('button',{name:'Patient is fine (3)',exact:true}).click();await expect(page.locator('.alert-panel.red')).toBeVisible();
 await expect(page.getByRole('button',{name:'Patient is fine (3)',exact:true})).toHaveAttribute('aria-pressed','true');
 expect((await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze()).violations).toEqual([]);
});
test('second elder is independent and Hindi family screens are usable',async({page})=>{
 test.setTimeout(90000);await setup(page);await page.getByRole('button',{name:'Family',exact:true}).click();
 await page.getByRole('button',{name:'Add another demo elder',exact:true}).click();await expect(page.getByRole('heading',{name:'Demo elder 02',exact:true})).toBeVisible();
 await page.getByRole('button').filter({has:page.getByRole('heading',{name:'Demo elder 02',exact:true})}).click();await expect(page.getByRole('heading',{name:'Demo elder 02',exact:true}).first()).toBeVisible();
 await page.getByRole('button',{name:'Medicine manager',exact:true}).click();await expect(page.getByText('No medicines recorded',{exact:true})).toBeVisible();
 await page.getByRole('button',{name:'हिन्दी',exact:true}).click();await expect(page.getByRole('heading',{name:'दवा प्रबंधन',exact:true})).toBeVisible();
 expect(await page.locator('body').evaluate(el=>el.scrollWidth<=window.innerWidth)).toBe(true);
});
test('foreground clock queues a scheduled alarm that opens only in Saathi mode',async({page})=>{
 test.setTimeout(90000);await setup(page);await page.clock.install({time:new Date('2026-10-25T05:31:00Z')});
 await page.getByRole('button',{name:'Family',exact:true}).click();await detail(page);
 await page.getByRole('button',{name:'Medicine manager',exact:true}).click();await page.getByRole('button',{name:'Add medicine',exact:true}).click();
 await page.getByLabel('Medicine name',{exact:true}).fill('Clock demo tablet');await page.getByLabel('Strength from prescription').fill('Demo strength');await page.getByLabel('Tablets remaining',{exact:true}).fill('5');
 await page.getByRole('checkbox',{name:'I copied the medicine and schedule from the existing prescription.'}).check();await page.getByRole('button',{name:'Save medicine',exact:true}).click();await expect(page.getByText('Medicine saved. It is available in Saathi mode.')).toBeVisible();
 await page.clock.fastForward(61000);await expect(page.getByRole('dialog')).toHaveCount(0);
 await role(page,'Saathi');await page.clock.fastForward(2100);await expect(page.getByRole('heading',{name:'Medicine reminder',exact:true})).toBeVisible();
 await expect(page.getByRole('dialog').getByText('Clock demo tablet · Demo strength')).toBeVisible();
});
