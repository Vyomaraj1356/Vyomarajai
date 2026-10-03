const {chromium}=require('playwright');
// Optional executable override for constrained sandboxes; otherwise use Playwright's installed browser.
const base=(process.env.VYOMARAJ_PREVIEW_URL||'http://127.0.0.1:4176').replace(/\/$/,'');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.TEST_CHROMIUM_EXECUTABLE||undefined,headless:true});
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1000},reducedMotion:'reduce'});const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(base+'/');await page.waitForFunction(()=>!document.getElementById('plan').disabled);
  assert.equal(await page.locator('.story').count(),12);assert.equal(await page.locator('.peetha').count(),9);
  await page.selectOption('#story-filter','Shiv–Shakti');assert.equal(await page.locator('.story').count(),2);
  await page.selectOption('#region','Maharashtra');assert.equal(await page.locator('.peetha').count(),4);
  await page.locator('#rotate').focus();await page.locator('#rotate').press('End');assert.equal(await page.locator('#angle').textContent(),'180°');
  await page.locator('[data-mode="4d"]').click();await page.locator('#next').click();assert.equal(await page.locator('#step-count').textContent(),'STEP 2 / 4');
  await page.locator('[data-mode="5d"]').click();await page.selectOption('#diet','plant-based');assert.equal(await page.locator('#recipe option').count(),2);
  await page.locator('#no-milk').check();await page.locator('#tv-plan').click();assert.equal(await page.locator('#topic-title').textContent(),'Devon Ke Dev… Mahadev');
  await page.locator('#plan').click();await page.waitForFunction(()=>!document.getElementById('download').hidden);
  assert.ok((await page.locator('#plan-preview').textContent()).includes('local_plan_created'));
  const downloadPromise=page.waitForEvent('download');await page.locator('#download').click();assert.equal((await downloadPromise).suggestedFilename(),'vyomaraj-jarvis-bhakti-plan.json');
  await page.selectOption('#recipe','coconut');assert.equal(await page.locator('#download').isVisible(),false);
  await page.goto(base+'/reports/bhakti');assert.ok((await page.locator('body').textContent()).includes('Shakti Peetha'));
  await page.goto(base+'/pairings/');await page.waitForFunction(()=>!document.getElementById('local-integration').hidden);
  assert.equal(await page.locator('.snack-button').count(),8);await page.locator('#adult').check();
  const pairDownload=page.waitForEvent('download');await page.locator('#pairing-plan').click();assert.equal((await pairDownload).suggestedFilename(),'vyomaraj-jarvis-pairings-plan.json');
  await page.setViewportSize({width:390,height:844});await page.goto(base+'/bhakti/');await page.waitForFunction(()=>!document.getElementById('plan').disabled);
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth));
  await page.locator('#food').scrollIntoViewIfNeeded();
  assert.deepEqual(errors,[]);console.log('PASS: real Chromium desktop/mobile; story/region filters, modes, recipes, both plan APIs/downloads, stale-plan invalidation, report rendering, no horizontal overflow or JS errors.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
