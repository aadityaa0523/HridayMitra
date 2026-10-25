import {test,expect} from '@playwright/test';

test('English and Hindi Vosk models initialize with networking disabled',async({browser})=>{
 test.setTimeout(240000);
 for(const lang of ['en','hi']){
  const context=await browser.newContext({permissions:['microphone']});
  const page=await context.newPage();
  await page.goto('/');await page.getByRole('button',{name:'Open demo',exact:true}).click();
  await expect(page.getByTestId('offline-status')).toHaveText('App ready offline');
  await page.getByRole('button',{name:'Voice commands',exact:true}).filter({visible:true}).click();
  if(lang==='hi'){
   await page.getByRole('button',{name:'Close',exact:true}).click();
   await page.getByRole('button',{name:'हिन्दी',exact:true}).click();
   await page.getByRole('button',{name:'बोलकर निर्देश',exact:true}).filter({visible:true}).click();
  }
  await page.getByRole('button',{name:lang==='en'?'Install offline language pack':'ऑफ़लाइन भाषा पैक जोड़ें',exact:true}).click();
  await expect(page.getByRole('button',{name:lang==='en'?'Start microphone':'माइक चालू करें',exact:true})).toBeEnabled({timeout:120000});
  await context.setOffline(true);
  await page.reload();
  await page.getByRole('button',{name:lang==='en'?'Voice commands':'बोलकर निर्देश',exact:true}).filter({visible:true}).click();
  await page.getByRole('button',{name:lang==='en'?'Start microphone':'माइक चालू करें',exact:true}).click();
  await expect(page.getByRole('button',{name:lang==='en'?'Stop microphone':'माइक बंद करें',exact:true})).toBeVisible({timeout:90000});
  await page.getByRole('button',{name:lang==='en'?'Stop microphone':'माइक बंद करें',exact:true}).click();
  await context.close();
 }
});
