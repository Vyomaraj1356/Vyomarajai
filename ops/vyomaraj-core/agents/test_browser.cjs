const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const path=require('node:path');
const base=(process.env.VYOMARAJ_PREVIEW_URL||'http://127.0.0.1:4176').replace(/\/$/,'');
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.TEST_CHROMIUM_EXECUTABLE||undefined,headless:true});
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1050}});const errors=[],external=[];
  page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(!r.url().startsWith(base))external.push(r.url());});
  await page.goto(base+'/agents/');await page.waitForFunction(()=>document.querySelectorAll('.slot').length===128);
  assert.equal(await page.locator('.category').count(),13);assert.equal(await page.locator('.group').count(),6);
  assert.equal(await page.locator('.slot').count(),128);assert.equal(await page.locator('.topic').count(),173);
  assert.equal(await page.locator('.slot:not(.named)').count(),86);
  assert.ok(await page.locator('.slot:not(.named)').evaluateAll(nodes=>nodes.every(n=>/^\d+$/.test(n.textContent))));
  assert.equal(new Set(await page.locator('.slot').evaluateAll(nodes=>nodes.map(n=>n.dataset.agentId))).size,128);
  await page.selectOption('#category','ENTERTAINMENT');assert.equal(await page.locator('.slot').count(),32);assert.equal(await page.locator('.group').count(),6);
  assert.equal(await page.locator('.slot.named').count(),2);
  assert.equal(await page.locator('[data-heading-id="ENT-HUB-MOVIE"] .slot').count(),6);
  assert.equal(await page.locator('[data-heading-id="ENT-HUB-MUS"] .slot').count(),6);
  await page.selectOption('#category','FINANCE');assert.equal(await page.locator('.slot').count(),7);assert.equal(await page.locator('.topic').count(),0);
  await page.goto(base+'/education/');await page.waitForFunction(()=>document.querySelectorAll('.slot').length===16);
  assert.equal(await page.locator('#category').inputValue(),'EDU');assert.equal(await page.locator('.slot:not(.named)').count(),6);
  assert.equal(await page.locator('.topic').count(),21);assert.equal(await page.locator('[data-agent-id="EDU-GOV-S1"]').count(),1);
  assert.ok(await page.locator('.topic').evaluateAll(nodes=>nodes.every(n=>n.dataset.owner==='EDU')));
  assert.equal(await page.locator('.audit-id').count(),0);await page.locator('#ids').check();assert.equal(await page.locator('.audit-id').count(),16);
  await page.locator('#ids').uncheck();await page.locator('#search').fill('Govt Schemes');assert.equal(await page.locator('.slot').count(),1);assert.equal(await page.locator('.topic').count(),1);
  await page.locator('#search').fill('');
  if(process.env.AGENTS_SCREENSHOT_DIR)await page.screenshot({path:path.join(process.env.AGENTS_SCREENSHOT_DIR,'education-desktop.png')});
  const downloadPromise=page.waitForEvent('download');await page.getByText('Download current registry JSON ↓',{exact:true}).click();
  const dl=await downloadPromise,stream=await dl.createReadStream(),chunks=[];for await(const c of stream)chunks.push(c);const data=JSON.parse(Buffer.concat(chunks));
  assert.equal(data.totals.sub_agents,128);assert.equal(data.totals.active_products,null);
  assert.equal(data.agents.find(a=>a.id==='PLATFORM-UNMAPPED').source_slot,null);
  await page.goto(base+'/reports/');assert.ok((await page.locator('body').textContent()).includes('128 counted'));
  await page.goto(base+'/reports/agents');assert.equal(await page.locator('tr').filter({hasText:'Education slots'}).locator('td').nth(2).textContent(),'16');
  await page.goto(base+'/reports/history');assert.ok((await page.locator('body').textContent()).includes('HISTORICAL SNAPSHOT — NOT THE CURRENT ROSTER'));
  for(const app of ['film','music','bhakti','pairings','research']){await page.goto(base+'/'+app+'/');assert.ok(await page.locator('a[href="/agents/"]').count()>0);assert.ok(await page.locator('a[href="/education/"]').count()>0);}
  await page.goto(base+'/music/');await page.waitForFunction(()=>document.querySelectorAll('.agent').length===6);assert.deepEqual(await page.locator('.agent h3').allTextContents(),['1','2','3','4','5','6']);
  await page.goto(base+'/film/');await page.waitForFunction(()=>document.querySelectorAll('.agent').length===6);assert.deepEqual(await page.locator('.agent h3').allTextContents(),['1','2','3','4','5','6']);
  await page.setViewportSize({width:390,height:844});await page.goto(base+'/education/');await page.waitForFunction(()=>document.querySelectorAll('.slot').length===16);
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  if(process.env.AGENTS_SCREENSHOT_DIR)await page.screenshot({path:path.join(process.env.AGENTS_SCREENSHOT_DIR,'education-mobile.png')});
  assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
  console.log('PASS current hierarchy/Education Chromium: 13 categories, 128 unique slots, six uncounted hubs, serial-only unnamed entries, Education/Govt Schemes ownership, filters/audit IDs, registry download, current/historical reports, five-app navigation, numbered Music/Movie cards, mobile no overflow, no JS errors or external requests.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
