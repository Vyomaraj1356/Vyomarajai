const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const path=require('node:path');
const base=(process.env.VYOMARAJ_PREVIEW_URL||'http://127.0.0.1:4176').replace(/\/$/,'');
const shot=process.env.MUSIC_SCREENSHOT_DIR;
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.TEST_CHROMIUM_EXECUTABLE||undefined,headless:true});
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1000},reducedMotion:'reduce'});const errors=[],posts=[];
  page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(r.method()==='POST')posts.push(r.url());});
  await page.goto(base+'/music/');await page.waitForFunction(()=>document.getElementById('runtime').textContent.includes('available'));
  assert.equal(await page.locator('.card').count(),39);assert.equal(await page.locator('.agent').count(),6);
  if(shot)await page.screenshot({path:path.join(shot,'music-desktop.png')});
  await page.locator('#nostalgia').click();assert.equal(await page.locator('.card').count(),7);
  await page.locator('#add-binaca').click();await page.locator('#reset').click();
  await page.locator('#search').fill('Arijit');assert.ok(await page.locator('.card').count()>=1);
  await page.locator('#add-tumhiho').click();await page.locator('#reset').click();
  await page.selectOption('#kind','video');assert.equal(await page.locator('.card').count(),4);
  await page.locator('#add-hateyou-video').click();await page.locator('#chart-add').click();
  await page.locator('button[aria-label="Move up Tum Hi Ho · soundtrack recording"]').click();
  assert.ok((await page.locator('#queue li').first().textContent()).includes('Tum Hi Ho'));
  await page.selectOption('#mode','video');await page.selectOption('#duration','15');await page.locator('#plan').click();
  await page.waitForFunction(()=>!document.getElementById('download').hidden);
  assert.ok((await page.locator('#rundown').textContent()).includes('15-minute video plan'));
  const promise=page.waitForEvent('download');await page.locator('#download').click();const download=await promise;
  assert.equal(download.suggestedFilename(),'vyomaraj-music-programme-plan.json');
  const stream=await download.createReadStream();const chunks=[];for await(const chunk of stream)chunks.push(chunk);
  const plan=JSON.parse(Buffer.concat(chunks));assert.equal(plan.item_ids[0],'tumhiho');assert.equal(plan.chart_snapshot.period,'2025');assert.equal(plan.streaming_connected,false);
  await page.selectOption('#duration','30');assert.equal(await page.locator('#download').isVisible(),false);
  // Browser-only media: a generated silent WAV, then a generated solid-colour WebM. No commercial assets.
  assert.equal(await page.locator('#media-file').isDisabled(),true);await page.locator('#permission').check();
  const wav=Buffer.alloc(16044);wav.write('RIFF');wav.writeUInt32LE(16036,4);wav.write('WAVEfmt ',8);wav.writeUInt32LE(16,16);wav.writeUInt16LE(1,20);wav.writeUInt16LE(1,22);wav.writeUInt32LE(8000,24);wav.writeUInt32LE(16000,28);wav.writeUInt16LE(2,32);wav.writeUInt16LE(16,34);wav.write('data',36);wav.writeUInt32LE(16000,40);
  const before=posts.length;
  await page.locator('#media-file').setInputFiles({name:'test-silence.wav',mimeType:'audio/wav',buffer:wav});
  await page.waitForFunction(()=>document.getElementById('audio-player').readyState>=1);
  assert.ok(await page.locator('#audio-player').isVisible());assert.ok(await page.locator('#audio-player').evaluate(p=>p.paused));
  assert.ok(await page.locator('#audio-player').evaluate(async p=>{await p.play();const started=!p.paused;p.pause();return started;}));
  const video=await page.evaluate(()=>new Promise(resolve=>{
   const c=document.createElement('canvas');c.width=64;c.height=64;const ctx=c.getContext('2d');ctx.fillStyle='#345c48';ctx.fillRect(0,0,64,64);
   const stream=c.captureStream(5),chunks=[],r=new MediaRecorder(stream,{mimeType:'video/webm;codecs=vp8'});
   r.ondataavailable=e=>chunks.push(e.data);r.onstop=async()=>resolve(Array.from(new Uint8Array(await new Blob(chunks).arrayBuffer())));
   let frame=0;r.start();const timer=setInterval(()=>{ctx.fillStyle=frame++%2?'#345c48':'#658a72';ctx.fillRect(0,0,64,64);},100);
   setTimeout(()=>{clearInterval(timer);r.stop();stream.getTracks().forEach(t=>t.stop());},1200);
  }));
  await page.locator('#media-file').setInputFiles({name:'test-original.webm',mimeType:'video/webm',buffer:Buffer.from(video)});
  await page.waitForFunction(()=>document.getElementById('video-player').readyState>=1);
  assert.ok(await page.locator('#video-player').isVisible());assert.ok(await page.locator('#video-player').evaluate(p=>p.paused));
  assert.ok(await page.locator('#video-player').evaluate(async p=>{await p.play();const started=!p.paused;p.pause();return started;}));
  assert.equal(await page.locator('#audio-player').isVisible(),false);assert.equal(posts.length,before);
  await page.locator('#permission').uncheck();assert.equal(await page.locator('#video-player').getAttribute('src'),null);
  assert.equal(await page.locator('#media-file').isDisabled(),true);
  await page.goto(base+'/reports/music');assert.ok((await page.locator('body').textContent()).includes('ENT-MUS-S1'));
  await page.setViewportSize({width:390,height:844});await page.goto(base+'/music/');await page.waitForFunction(()=>document.querySelectorAll('.card').length===39);
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  if(shot)await page.screenshot({path:path.join(shot,'music-mobile.png')});
  await page.selectOption('#region','India');await page.selectOption('#era','modern');assert.ok(await page.locator('.card').count()>0);
  assert.deepEqual(errors,[]);console.log('PASS music desktop/mobile: filters, six proposed bindings, queue reorder, API/download, stale-plan invalidation, real local audio/video decoding and playback, no autoplay/upload, permission revoke, reports, no overflow/JS errors.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
