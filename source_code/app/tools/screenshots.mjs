// README screenshots of the Saathi app: elder, family, ASHA and doctor on a red-alert day, phone size.
// Needs the production preview running:  npm run build && npm run preview -- --port 4173
// Run:  node tools/screenshots.mjs [baseURL]      Out: ../docs/app/screens/<role>.png
import { chromium } from '@playwright/test';
import { mkdirSync } from 'node:fs';

const base = process.argv[2] ?? 'http://localhost:4173';
const out = new URL('../../docs/app/screens/', import.meta.url);
mkdirSync(out, { recursive: true });
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 });
const settings = () => page.getByRole('button', { name: 'Settings', exact: true }).filter({ visible: true }).click();

await page.goto(base);
await page.getByRole('button', { name: 'Open demo', exact: true }).click();
await settings();
await page.getByLabel('PIN (6–12 digits)', { exact: true }).fill('246810');
await page.getByLabel('Confirm PIN', { exact: true }).fill('246810');
await page.getByRole('checkbox', { name: 'I agree to store synthetic demo data on this phone.' }).check();
await page.getByRole('button', { name: 'Create demo vault' }).click();
await page.getByRole('button', { name: 'Load five-month demo' }).click();
await page.getByText('164 synthetic days stored').waitFor();
await page.getByRole('button', { name: 'Next red-alert day', exact: true }).click();

for (const [role, label] of [['elder', 'Saathi'], ['family', 'Family'], ['asha', 'ASHA'], ['doctor', 'Doctor']]) {
  await settings();
  await page.getByRole('button', { name: label, exact: true }).click();
  await page.waitForTimeout(800);
  if (role !== 'elder') {                                            // open the patient's detail, the screen each role acts on
    await page.getByRole('button').filter({ has: page.getByRole('heading', { name: 'Demo elder 01', exact: true }) }).first().click();
    await page.waitForTimeout(800);
    await page.evaluate(() => window.scrollTo(0, 410));                // skip the shared header; start at the patient detail
  }
  await page.screenshot({ path: new URL(`${role}.png`, out).pathname.slice(1) });
  console.log('saved', role);
}
await browser.close();
