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
  await page.selectOption('#profile','marathi-theatre');assert.ok((await page.locator('#route').textContent()).includes('ENT-MOVIE-S4'));
  const queued=page.waitForResponse(r=>r.url().endsWith('/api/research/run')&&r.request().method()==='POST');
  await page.locator('#run').click();const job=await(await queued).json();await page.waitForFunction(()=>document.querySelectorAll('.card').length>0);
  // A real queued pass; network failures must still yield source-status evidence, not fiction.
  await page.waitForFunction(async id=>{const s=await(await fetch('/api/research/status')).json();return s.jobs.some(j=>j.id===id&&!['queued','running'].includes(j.state)&&j.result.sources?.openlibrary);},job.id,{timeout:90000});
  await page.locator('#refresh').click();await page.waitForFunction(()=>document.querySelectorAll('.card').length>0);
  const card=page.locator('.card').first();assert.equal(await card.getByRole('button',{name:'Accept metadata',exact:true}).isDisabled(),true);
  await page.locator('#ack').check();await card.getByRole('button',{name:'Accept metadata',exact:true}).click();
  await page.waitForFunction(()=>document.querySelector('.card .badge')?.textContent==='accepted metadata only');
  assert.ok((await card.textContent()).includes('Rights UNKNOWN'));
  await page.selectOption('#filter','accepted_metadata_only');assert.ok(await page.locator('.card').count()>=1);
  const downloadPromise=page.waitForEvent('download');await page.getByText('Export metadata JSON ↓',{exact:true}).click();
  const dl=await downloadPromise;const stream=await dl.createReadStream(),chunks=[];for await(const c of stream)chunks.push(c);
  const exported=JSON.parse(Buffer.concat(chunks));assert.equal(exported.scope,'unverified_metadata_not_media_or_licences');
  assert.ok(exported.records.some(r=>r.review_status==='accepted_metadata_only'));assert.ok(exported.records.every(r=>r.rights_status==='UNKNOWN'&&r.media_url===null));
  await page.locator('.card').first().getByRole('button',{name:'Reset review',exact:true}).click();
  await page.waitForFunction(()=>document.querySelectorAll('.card').length===0);await page.selectOption('#filter','all');
  if(shots)await page.screenshot({path:path.join(shots,'research-desktop.png'),fullPage:true});
  const source=page.locator('.card .source').first();assert.equal(await source.getAttribute('rel'),'noopener noreferrer');
  await page.goto(base+'/reports/research');assert.ok((await page.locator('body').textContent()).includes('Zero fresh internet leads'));
  assert.ok((await page.locator('body').textContent()).includes('DR remains BLOCKED'));
  await page.goto(base+'/reports/contents');assert.ok((await page.locator('body').textContent()).includes('/research/'));
  for(const app of ['film','music','bhakti','pairings']){await page.goto(base+'/'+app+'/');assert.ok(await page.locator('a[href="/research/"]').count()>0);}
  await page.setViewportSize({width:390,height:844});await page.goto(base+'/research/');await page.waitForFunction(()=>!document.getElementById('run').disabled);
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  if(shots)await page.screenshot({path:path.join(shots,'research-mobile.png'),fullPage:true});
  assert.deepEqual(errors,[]);assert.deepEqual(remote,[]);
  console.log('PASS research real Chromium: desktop/mobile, six profiles, actual queue pass/source evidence, acknowledgement gate, accept/filter/reset, JSON export with UNKNOWN rights/no media, safe source links, all-four navigation, consolidated reports, no browser external requests, overflow or JS errors.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
