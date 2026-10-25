import {test,expect,type Page} from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import path from 'node:path';
async function setup(page:Page){
 await page.goto('/');await page.getByRole('button',{name:'Open demo',exact:true}).click();await page.getByRole('button',{name:'Settings',exact:true}).filter({visible:true}).click();
 await page.getByLabel('PIN (6–12 digits)',{exact:true}).fill('246810');await page.getByLabel('Confirm PIN',{exact:true}).fill('246810');await page.getByRole('checkbox',{name:'I agree to store synthetic demo data on this phone.'}).check();
 await page.getByRole('button',{name:'Create demo vault'}).click();await page.getByRole('button',{name:'Load five-month demo'}).click();await expect(page.getByText('164 synthetic days stored')).toBeVisible();await page.getByRole('button',{name:'Next red-alert day',exact:true}).click();await page.getByRole('button',{name:'ASHA',exact:true}).click();
}
async function openVisit(page:Page){await page.getByRole('button').filter({has:page.getByRole('heading',{name:'Demo elder 01',exact:true})}).click();}
async function fillVisit(page:Page){
 await page.getByLabel('BP systolic (mmHg, optional)',{exact:true}).fill('120');await page.getByLabel('BP diastolic (mmHg, optional)',{exact:true}).fill('80');await page.getByRole('radio',{name:'1',exact:true}).check();
 await page.getByLabel('Breathless at rest?',{exact:true}).selectOption('no');await page.getByLabel('Needed extra pillows?',{exact:true}).selectOption('yes');await page.getByLabel('Visit notes',{exact:true}).fill('Synthetic visit notes. Review at PHC.');
 await page.getByLabel('Visit outcome',{exact:true}).selectOption('referred');await page.getByLabel('Reason for referral / follow-up',{exact:true}).fill('Care team review requested.');
}
test('ASHA saves an offline visit and family sees follow-up closure after reload',async({page,context})=>{
 test.setTimeout(90000);await setup(page);await openVisit(page);await fillVisit(page);
 expect((await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze()).violations).toEqual([]);
 await expect(page.getByTestId('offline-status')).toHaveText('App ready offline');await context.setOffline(true);
 await page.getByRole('button',{name:'Save visit and mark seen',exact:true}).click();await expect(page.getByRole('heading',{name:'Visit saved offline',exact:true})).toBeVisible();await expect(page.getByText('Seen by ASHA',{exact:true}).first()).toBeVisible();
 await page.reload();await page.getByRole('button',{name:'Settings',exact:true}).filter({visible:true}).click();await page.getByLabel('PIN (6–12 digits)',{exact:true}).fill('246810');await page.getByRole('button',{name:'Unlock records',exact:true}).click();await expect(page.getByText('164 synthetic days stored')).toBeVisible();
 await page.getByRole('button',{name:'Family',exact:true}).click();await openVisit(page);await page.getByRole('button',{name:'Open care alert',exact:true}).click();await expect(page.getByText(/Seen by ASHA/)).toBeVisible();await expect(page.locator('.alert-panel.red')).toBeVisible();
});
test('Hindi referral PDF and QR export work after an offline reload',async({page,context},testInfo)=>{
 test.setTimeout(120000);await page.addInitScript(()=>{Object.defineProperty(navigator,'canShare',{value:()=>true,configurable:true});Object.defineProperty(navigator,'share',{value:async(data:ShareData)=>{(window as unknown as {sharedName?:string}).sharedName=data.files?.[0]?.name;},configurable:true});});await setup(page);await openVisit(page);await fillVisit(page);await page.getByRole('button',{name:'Save visit and mark seen',exact:true}).click();await expect(page.getByRole('heading',{name:'Visit saved offline',exact:true})).toBeVisible();
 await page.getByRole('button',{name:'हिन्दी',exact:true}).click();await expect(page.getByTestId('offline-status')).toHaveText('ऐप ऑफ़लाइन तैयार है');await context.setOffline(true);await page.reload();
 await page.getByRole('button',{name:'सेटिंग',exact:true}).filter({visible:true}).click();await page.locator('input[type=password]').fill('246810');await page.getByRole('button',{name:'रिकॉर्ड खोलें',exact:true}).click();
 await page.getByRole('button',{name:'होम',exact:true}).filter({visible:true}).click();await openVisit(page);await page.getByRole('button',{name:/रेफ़र किया/}).click();
 await page.getByRole('checkbox',{name:'मैंने सामग्री जाँची है और इसे सुरक्षित रिकॉर्ड से बाहर निकालने या दिखाने की अनुमति देता हूँ।'}).check();
 const downloaded=page.waitForEvent('download');await page.getByRole('button',{name:'पीडीएफ़ डाउनलोड करें',exact:true}).click();const pdf=await downloaded;await pdf.saveAs(testInfo.outputPath('asha-referral-hi.pdf'));
 await page.getByRole('button',{name:'रेफ़रल क्यूआर दिखाएँ',exact:true}).click();await expect(page.getByRole('img',{name:'छोटे रेफ़रल सारांश का क्यूआर',exact:true})).toBeVisible();
 await page.getByRole('button',{name:'पीडीएफ़ साझा करें',exact:true}).click();expect(await page.evaluate(()=>(window as unknown as {sharedName?:string}).sharedName)).toMatch(/^saathi-referral-.*\.pdf$/);
 expect((await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze()).violations).toEqual([]);
});
test('village filtering and weekly PDF/SMS draft use the selected week',async({page},testInfo)=>{
 test.setTimeout(90000);await setup(page);await openVisit(page);await page.getByText('Village, house and PHC contact',{exact:true}).click();await page.getByLabel('Village',{exact:true}).fill('Demo village');await page.getByLabel('House / landmark',{exact:true}).fill('House 4');await page.getByLabel('PHC phone number',{exact:true}).fill('+910000000001');await page.getByRole('button',{name:'Save location and contact',exact:true}).click();await expect(page.getByText('Location and contact saved.',{exact:true})).toBeVisible();
 await page.getByRole('button',{name:'ASHA visit list',exact:true}).click();await page.getByLabel('Filter by village',{exact:true}).selectOption('Demo village');await expect(page.locator('.asha-list>button')).toHaveCount(1);
 await page.getByRole('checkbox',{name:'I reviewed this content and consent to exporting or showing it outside the encrypted vault.'}).check();await page.getByLabel('PHC phone number',{exact:true}).fill('+910000000001');await expect(page.getByRole('link',{name:'Open PHC SMS draft',exact:true})).toHaveAttribute('href',/^sms:\+910000000001\?body=/);
 const downloaded=page.waitForEvent('download');await page.getByRole('button',{name:'Download PDF',exact:true}).click();await (await downloaded).saveAs(testInfo.outputPath('asha-weekly-en.pdf'));
 await page.getByLabel('Filter by village',{exact:true}).selectOption('__unknown');await expect(page.getByText('No elders match this village.',{exact:true})).toBeVisible();
});
