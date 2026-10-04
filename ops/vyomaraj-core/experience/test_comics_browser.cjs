const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const path=require('node:path');
const base=(process.env.VYOMARAJ_PREVIEW_URL||'http://127.0.0.1:4176').replace(/\/$/,'');
const shots=process.env.COMICS_SCREENSHOT_DIR;
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.TEST_CHROMIUM_EXECUTABLE||undefined,headless:true});
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1000},reducedMotion:'reduce'});const errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  await page.goto(base+'/comics/');await page.waitForFunction(()=>!document.getElementById('plan').disabled);
  assert.equal(await page.locator('.card').count(),12);assert.equal(await page.locator('.agent').count(),3);
  assert.equal(await page.locator('.edition-chip').count(),18); // 6 original titles × 3 language editions
  assert.equal(await page.locator('.version-chip').count(),12); // 6 originals × past + future chips
  if(shots)await page.screenshot({path:path.join(shots,'comics-desktop.png')});
  await page.selectOption('#era','proposal');assert.equal(await page.locator('.card').count(),6);
  await page.selectOption('#era','heritage');assert.equal(await page.locator('.card').count(),6);
  assert.equal(await page.locator('.edition-chip').count(),0); // heritage context only: no editions claimed
  await page.locator('#reset').click();await page.locator('#search').fill('Vayu');assert.equal(await page.locator('.card').count(),1);
  await page.locator('#add-vayu-sena').click();assert.equal(await page.locator('#reference-count').textContent(),'1');
  await page.selectOption('#format','issue');assert.equal(await page.locator('#panels').inputValue(),'32');
  await page.selectOption('#primary-language','hi');
  await page.locator('#plan').click();await page.waitForFunction(()=>!document.getElementById('download-plan').hidden);
  const dlPromise=page.waitForEvent('download');await page.locator('#download-plan').click();const dl=await dlPromise;
  const stream=await dl.createReadStream(),chunks=[];for await(const c of stream)chunks.push(c);
  const plan=JSON.parse(Buffer.concat(chunks));
  assert.equal(plan.experience,'comics');assert.equal(plan.primary_language,'hi');
  assert.equal(plan.sample_captions_language,'Hindi');
  assert.deepEqual(plan.language_matrix.editions.map(e=>e.language),['hi','en','hinglish']);
  assert.ok(plan.language_matrix.editions.every(e=>e.title&&e.tagline));
  assert.ok(plan.version_lineage.past.length>0);assert.ok(plan.version_lineage.future.length>0);
  assert.ok(plan.canonical_agent_ids.includes('ENT-CARTOON-S1'));assert.ok(plan.canonical_agent_ids.includes('ENT-CARTOON-S3'));
  assert.equal(plan.owner_gate.status,'PENDING_OWNER_PERMISSION');
  assert.equal(plan.panels,32);assert.equal(plan.panel_budget.reduce((n,b)=>n+b.budget_panels,0),32);
  assert.equal(plan.ai_calls_made,false);assert.equal(plan.publishing_enabled,false);
  await page.selectOption('#versions','future');assert.equal(await page.locator('#download-plan').isVisible(),false);
  await page.locator('#plan').click();await page.waitForFunction(()=>!document.getElementById('download-plan').hidden);
  assert.ok((await page.locator('#outline').textContent()).includes('LANGUAGE MATRIX'));
  assert.ok((await page.locator('#outline').textContent()).includes('OWNER GATE'));
  await page.setViewportSize({width:390,height:844});await page.goto(base+'/comics/');
  await page.waitForFunction(()=>document.querySelectorAll('.card').length===12);
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  if(shots)await page.screenshot({path:path.join(shots,'comics-mobile.png')});
  await page.goto(base+'/reports/contents');assert.ok((await page.locator('body').textContent()).includes('Chitra Katha'));
  await page.goto(base+'/approvals/');await page.waitForFunction(()=>document.querySelectorAll('#queue-select option').length>1);
  assert.ok((await page.locator('body').textContent()).includes('NOSTALGIC'));
  assert.deepEqual(errors,[]);console.log('PASS comics desktop/mobile: 12 entries (6 heritage-context + 6 originals), trilingual edition chips, past+future version chips, hi primary language plan with full language matrix, ENT-CARTOON routing, owner gate, contents report, approvals queue reachable, no overflow or JS errors.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
