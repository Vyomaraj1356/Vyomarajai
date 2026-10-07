const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const path=require('node:path');
const base=(process.env.VYOMARAJ_PREVIEW_URL||'http://127.0.0.1:4176').replace(/\/$/,'');
const shots=process.env.RESEARCH_SCREENSHOT_DIR;
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.TEST_CHROMIUM_EXECUTABLE||undefined,headless:true});
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1100}});const errors=[],remote=[];
  page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(!r.url().startsWith(base))remote.push(r.url());});
  await page.goto(base+'/research/');await page.waitForFunction(()=>!document.getElementById('run').disabled);
  assert.equal(await page.locator('#profile option').count(),6);assert.equal(await page.locator('.tool').count(),6);
  assert.ok((await page.locator('#tools').textContent()).includes('Not configured'));
  assert.ok(await page.locator('#owner-approval-token').count());
  await page.selectOption('#profile','marathi-theatre');assert.ok((await page.locator('#route').textContent()).includes('ENT-MOVIE-S4'));
  const before=await page.evaluate(async()=>await(await fetch('/api/research/status')).json());
  const denied=page.waitForResponse(r=>r.url().endsWith('/api/research/run')&&r.request().method()==='POST');
  await page.locator('#run').click();const response=await denied;assert.equal(response.status(),401);
  const challenge=await response.json();assert.equal(challenge.error,'owner_approval_required');
  assert.equal(challenge.required.action,'research.run');assert.equal(challenge.required.scope,'research.run');
  await page.waitForFunction(()=>document.getElementById('message').textContent.includes('No work was changed'));
  const after=await page.evaluate(async()=>await(await fetch('/api/research/status')).json());
  assert.deepEqual(after.jobs.map(j=>j.id),before.jobs.map(j=>j.id));
  assert.ok((await page.locator('body').textContent()).includes('not configured'));
  if(shots)await page.screenshot({path:path.join(shots,'research-desktop.png'),fullPage:true});
  await page.goto(base+'/reports/research');assert.ok((await page.locator('body').textContent()).includes('Zero fresh internet leads'));
  assert.ok((await page.locator('body').textContent()).includes('DR remains BLOCKED'));
  await page.goto(base+'/reports/contents');assert.ok((await page.locator('body').textContent()).includes('/research/'));
  for(const app of ['film','music','bhakti','pairings']){await page.goto(base+'/'+app+'/');assert.ok(await page.locator('a[href="/research/"]').count()>0);}
  await page.setViewportSize({width:390,height:844});await page.goto(base+'/research/');await page.waitForFunction(()=>!document.getElementById('run').disabled);
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  if(shots)await page.screenshot({path:path.join(shots,'research-mobile.png'),fullPage:true});
  assert.deepEqual(errors,[]);assert.deepEqual(remote,[]);
  console.log('PASS research Chromium: desktop/mobile, six profiles, deterministic routes, fail-closed owner gate (401) with no queued job mutation, no external browser requests, safe navigation, no overflow or JavaScript errors.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
