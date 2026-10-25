// Reproducible local mobile audit. No special app route or altered app behavior.
import lighthouse from 'lighthouse';
import {launch} from 'chrome-launcher';
import {chromium} from 'playwright';
import {mkdir,writeFile} from 'node:fs/promises';
import path from 'node:path';
const url=process.env.PLAYWRIGHT_BASE_URL||'http://127.0.0.1:4180';
const out=path.resolve('../../phase9-qa');await mkdir(out,{recursive:true});
for(const scenario of ['welcome','elder-home']){
 const chrome=await launch({chromeFlags:['--headless=new','--no-first-run']});
 try{
  if(scenario==='elder-home'){
   const browser=await chromium.connectOverCDP('http://127.0.0.1:'+chrome.port);
   const page=await browser.contexts()[0].newPage();await page.goto(url);await page.evaluate(()=>{localStorage.setItem('saathi.started','true');localStorage.setItem('saathi.role','elder');localStorage.setItem('saathi.language','hi');});await page.close();
  }
  const result=await lighthouse(url,{port:chrome.port,output:['json','html'],onlyCategories:['performance','accessibility','best-practices','seo'],formFactor:'mobile',disableStorageReset:scenario==='elder-home',throttling:{rttMs:150,throughputKbps:1638.4,cpuSlowdownMultiplier:4},logLevel:'error'});
  await writeFile(path.join(out,'lighthouse-'+scenario+'.report.json'),result.report[0]);await writeFile(path.join(out,'lighthouse-'+scenario+'.report.html'),result.report[1]);
  console.log(scenario,JSON.stringify(Object.fromEntries(Object.entries(result.lhr.categories).map(([key,value])=>[key,value.score]))));
 }finally{await chrome.kill();}
}
