import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('welcome, unknown status, amulet and accessible dialogs',async({page})=>{
 await page.goto('/');
 await expect(page.getByRole('heading',{name:'Your daily care companion'})).toBeVisible();
 await page.getByRole('button',{name:'Open demo',exact:true}).click();
 await expect(page.getByRole('img',{name:'Not checked yet'})).toBeVisible();
 await expect(page.getByText('Wearable amulet',{exact:true})).toBeVisible();
 await page.getByRole('button',{name:'Check-in now',exact:true}).click();
 await expect(page.getByRole('dialog')).toContainText('unlock records');
 await page.getByRole('button',{name:'Close',exact:true}).click();
 await expect(page.getByRole('dialog')).toHaveCount(0);
 const results=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();
 expect(results.violations).toEqual([]);
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth)).toBe(true);
});

test('Hindi and navigation survive a truly offline reload',async({page,context})=>{
 await page.goto('/');
 await page.getByRole('button',{name:'हिन्दी',exact:true}).click();
 await page.getByRole('button',{name:'डेमो खोलें',exact:true}).click();
 await expect(page.getByTestId('offline-status')).toHaveText('ऐप ऑफ़लाइन तैयार है',{timeout:30000});
 await page.evaluate(async()=>{await navigator.serviceWorker.ready; if(!navigator.serviceWorker.controller) await new Promise<void>(resolve=>navigator.serviceWorker.addEventListener('controllerchange',()=>resolve(),{once:true}));});
 await context.setOffline(true);
 await page.reload();
 await expect(page.getByRole('heading',{name:'साथी में आपका स्वागत है'})).toBeVisible();
 await expect(page.locator('html')).toHaveAttribute('lang','hi');
 await page.getByRole('button',{name:'सेटिंग',exact:true}).filter({visible:true}).click();
 await page.getByRole('button',{name:'आशा',exact:true}).click();
 await expect(page.getByRole('heading',{name:'आशा',exact:true})).toBeVisible();
 await page.reload();
 await expect(page.getByRole('heading',{name:'आशा',exact:true})).toBeVisible();
});

test('help never claims delivery, install manifest contains raster icons',async({page})=>{
 await page.goto('/');
 await page.getByRole('button',{name:'Open demo',exact:true}).click();
 await page.getByRole('button',{name:/Get help/}).click();
 await expect(page.getByRole('dialog')).toContainText('cannot send alerts');
 await expect(page.getByRole('link',{name:'Open dialler: 108'})).toHaveAttribute('href','tel:108');
 await page.getByRole('button',{name:'Close',exact:true}).click();
 const href=await page.locator('link[rel="manifest"]').getAttribute('href');
 const manifest=await (await page.request.get(href!)).json();
 expect(manifest.display).toBe('standalone');
 expect(manifest.icons.map((icon:{sizes:string})=>icon.sizes)).toEqual(['192x192','512x512']);
});
