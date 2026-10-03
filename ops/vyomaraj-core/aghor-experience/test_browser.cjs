const {chromium}=require('playwright');const assert=require('node:assert/strict');const path=require('node:path');
const base=(process.env.VYOMARAJ_PREVIEW_URL||'http://127.0.0.1:4176').replace(/\/$/,'');
(async()=>{const browser=await chromium.launch({executablePath:process.env.TEST_CHROMIUM_EXECUTABLE||undefined,headless:true});try{
 const page=await browser.newPage({viewport:{width:1440,height:1050}});const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(base+'/aghor/');await page.waitForFunction(()=>document.querySelectorAll('.chapter').length===14);
 assert.equal(await page.locator('.chapter').count(),14);assert.equal(await page.locator('.person').count(),7);assert.equal(await page.locator('.practice').count(),6);assert.equal(await page.locator('.care-card').count(),6);assert.equal(await page.locator('#sources article').count(),11);
 if(process.env.AGHOR_SCREENSHOT_DIR)await page.screenshot({path:path.join(process.env.AGHOR_SCREENSHOT_DIR,'aghor-desktop.png')});
 await page.selectOption('#lens','Public health');assert.equal(await page.locator('.chapter').count(),1);
 assert.equal(await page.locator('#make-plan,#download,#topic,#mode').count(),0);
 assert.equal(await page.locator('#practices ol').count(),0);
 for(const mode of ['study','reflection','service','treatment']){
  const bad=await page.request.post(base+'/api/plan',{data:{experience:'aghor',mode}});assert.equal(bad.status(),400);assert.match((await bad.json()).error,/view-only/);
 }
 await page.locator('nav a[href="/sovereign/"]').click();assert.match(await page.locator('body').textContent(),/voluntary/i);
 await page.locator('nav a[href="/contracts/"]').click();assert.match(await page.locator('body').textContent(),/not signed, not executed/);
 const policy=await(await page.request.get(base+'/policy.json')).json();assert.equal(policy.aghor.plan_generation_enabled,false);assert.equal(policy.legal.acceptance_collected,false);assert.equal(policy.earning.guaranteed_income,false);
 await page.goto(base+'/reports/policy');assert.match(await page.locator('body').textContent(),/view-only/i);
 await page.goto(base+'/aghor/');await page.waitForFunction(()=>document.querySelectorAll('.chapter').length===14);
 await page.selectOption('#era','Sacred origin');assert.equal(await page.locator('.person').count(),2);
 assert.ok((await page.locator('#care-list').textContent()).includes('112'));assert.ok((await page.locator('#practices').textContent()).includes('No procedure supplied'));
 await page.goto(base+'/bhakti/');assert.equal(await page.locator('#aghor-agent a[href="/aghor/"]').count(),1);
 await page.goto(base+'/agents/');await page.waitForFunction(()=>document.querySelectorAll('.slot').length===128);await page.selectOption('#category','BHAKTI');assert.equal(await page.locator('.slot').count(),3);assert.equal(await page.locator('.slot:not(.named)').count(),2);
 const status=await(await page.request.get(base+'/api/availability')).json();assert.equal(status.production_dr_verified,false);assert.ok(status.replicas.every(r=>r.metadata_ready));
 await page.goto(base+'/reports/aghor');assert.ok((await page.locator('body').textContent()).includes('BHAKTI-AGHOR-S1'));
 await page.setViewportSize({width:390,height:844});await page.goto(base+'/aghor/');await page.waitForFunction(()=>document.querySelectorAll('.chapter').length===14);assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
 if(process.env.AGHOR_SCREENSHOT_DIR)await page.screenshot({path:path.join(process.env.AGHOR_SCREENSHOT_DIR,'aghor-mobile.png')});
 assert.deepEqual(errors,[]);console.log('PASS Aghor through real failover gateway: sourced chapters/profiles/practice/care, filters, view-only UI and API, Sovereign/Contracts policy, no plan/ritual execution, Bhakti/registry links, both replicas ready, mobile and no JS errors.');
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exit(1);});
