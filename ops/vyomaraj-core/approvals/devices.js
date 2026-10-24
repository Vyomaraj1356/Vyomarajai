'use strict';
(() => {
 const $=id=>document.getElementById(id);
 let cameraStream=null,micStream=null,recorder=null,chunks=[],audioContext=null,micFrame=null,recordedUrl=null;
 const report={schema:'vyomaraj-device-test/1',created_at:null,environment:{user_agent:navigator.userAgent,secure_context:window.isSecureContext},camera:{status:'NOT_TESTED'},recording:{status:'NOT_TESTED',uploaded:false,published:false},audio_output:{status:'NOT_TESTED'},microphone:{status:'NOT_TESTED'},dolby:{status:'NOT_VERIFIED'},limitations:['Browser-visible device checks only; no OS driver or licence verification.','No upload, publication, or external network call is performed.']};
 function status(id,text,good=false){$(id).textContent=text;$(id).className='device-status '+(good?'good':'');}
 function overall(text){$('overall-status').textContent=text;report.created_at=new Date().toISOString();}
 async function enumerate(){
  if(!navigator.mediaDevices?.enumerateDevices){status('device-list','Device enumeration unavailable in this browser/context.');return;}
  try{
   const devices=await navigator.mediaDevices.enumerateDevices(),groups={videoinput:[],audioinput:[],audiooutput:[]};
   for(const d of devices)if(groups[d.kind])groups[d.kind].push({deviceId:d.deviceId,label:d.label||'(label hidden until permission)',kind:d.kind});
   for(const pair of [['videoinput','camera-select'],['audiooutput','output-select']]){
    const kind=pair[0],select=$(pair[1]),old=select.value;select.replaceChildren(new Option(kind==='videoinput'?'Select camera':'Default system output',''));
    for(const d of groups[kind])select.add(new Option(d.label,d.deviceId));if(old)select.value=old;
   }
   status('device-list',JSON.stringify({camera_count:groups.videoinput.length,microphone_count:groups.audioinput.length,audio_output_count:groups.audiooutput.length,devices:groups},null,2),true);
   report.inventory={counts:{camera:groups.videoinput.length,microphone:groups.audioinput.length,audio_output:groups.audiooutput.length},devices:groups};
   overall('Inventory refreshed. Browser-visible device count does not prove production connectivity.');
  }catch(e){status('device-list','Enumeration failed: '+e.message);}
 }
 function stopCamera(){if(cameraStream)cameraStream.getTracks().forEach(t=>t.stop());cameraStream=null;$('preview').srcObject=null;$('stop-camera').disabled=true;$('start-record').disabled=true;}
 async function startCamera(){
  if(!navigator.mediaDevices?.getUserMedia){status('camera-status','BLOCKED: getUserMedia unavailable; use supported browser over HTTPS/localhost.');return;}
  stopCamera();const dims=$('resolution-select').value.split('x').map(Number),deviceId=$('camera-select').value,video={width:{ideal:dims[0]},height:{ideal:dims[1]},frameRate:{ideal:30,max:60}};
  if(deviceId)video.deviceId={exact:deviceId};
  try{
   cameraStream=await navigator.mediaDevices.getUserMedia({video,audio:false});$('preview').srcObject=cameraStream;await $('preview').play();
   const track=cameraStream.getVideoTracks()[0],s=track.getSettings();report.camera={status:'VERIFIED_IN_BROWSER_TEST',label:track.label||'Browser camera',settings:{width:s.width||null,height:s.height||null,frameRate:s.frameRate||null,deviceId:s.deviceId||null},permission:'granted'};
   $('stop-camera').disabled=false;$('start-record').disabled=!window.MediaRecorder;
   status('camera-status',JSON.stringify({result:'PASS',track:track.label,actual_resolution:[s.width||null,s.height||null],frame_rate:s.frameRate||null,requested:dims,note:'Local browser test only.'},null,2),true);
   await enumerate();overall('Camera preview passed in this browser session; production deployment is not established.');
  }catch(e){report.camera={status:'FAILED_OR_BLOCKED',error:e.name||'Error'};status('camera-status',e.name+': '+e.message);overall('Camera test failed or was blocked; no success inferred.');}
 }
 async function startRecord(){
  if(!cameraStream){status('record-status','Start the camera first.');return;}
  const preferred=$('record-format').value,opts=MediaRecorder.isTypeSupported(preferred)?{mimeType:preferred}:{};
  try{
   chunks=[];recorder=new MediaRecorder(cameraStream,opts);recorder.ondataavailable=e=>{if(e.data?.size)chunks.push(e.data);};
   recorder.onstop=()=>{const blob=new Blob(chunks,{type:recorder.mimeType||'video/webm'});if(recordedUrl)URL.revokeObjectURL(recordedUrl);recordedUrl=URL.createObjectURL(blob);$('recorded-preview').src=recordedUrl;$('download-recording').href=recordedUrl;$('download-recording').download='vyomaraj-local-camera-test.'+(blob.type.includes('mp4')?'mp4':'webm');$('download-recording').hidden=false;report.recording={status:'VERIFIED_LOCAL_RECORDING',mime_type:blob.type,bytes:blob.size,uploaded:false,published:false};status('record-status','Local recording ready: '+blob.size+' bytes ('+blob.type+'). Nothing uploaded or published.',true);overall('Local recording passed. Review and publishing gates remain separate.');};
   recorder.start();$('start-record').disabled=true;$('stop-record').disabled=false;status('record-status','Recording locally. Select Stop when ready.');
  }catch(e){status('record-status','Recording failed: '+e.message);}
 }
 function stopRecord(){if(recorder&&recorder.state!=='inactive')recorder.stop();$('stop-record').disabled=true;$('start-record').disabled=!cameraStream;}
 async function testAudio(){
  try{const Ctx=window.AudioContext||window.webkitAudioContext;if(!Ctx)throw new Error('Web Audio API unavailable');audioContext ||= new Ctx();await audioContext.resume();const dest=$('output-select').value;if(dest&&typeof audioContext.setSinkId==='function')await audioContext.setSinkId(dest);
   const osc=audioContext.createOscillator(),gain=audioContext.createGain();osc.type='sine';osc.frequency.value=440;gain.gain.setValueAtTime(.0001,audioContext.currentTime);gain.gain.exponentialRampToValueAtTime(.12,audioContext.currentTime+.05);gain.gain.setValueAtTime(.12,audioContext.currentTime+.35);gain.gain.exponentialRampToValueAtTime(.0001,audioContext.currentTime+.5);osc.connect(gain).connect(audioContext.destination);osc.start();osc.stop(audioContext.currentTime+.52);
   report.audio_output={status:'TEST_TONE_SENT_TO_BROWSER_AUDIO_GRAPH',sample_rate:audioContext.sampleRate,sink_selection_supported:typeof audioContext.setSinkId==='function',selected_output:dest||'system default',dolby:'NOT_VERIFIED'};
   status('audio-status','Test tone sent to browser output. Confirm physically that you heard it. This cannot confirm Dolby.',true);overall('Audio test tone sent. Physical confirmation and Dolby vendor verification remain required.');
  }catch(e){report.audio_output={status:'FAILED_OR_BLOCKED',error:e.name||'Error'};status('audio-status','Audio test failed: '+e.message);}
 }
 async function startMic(){
  try{micStream=await navigator.mediaDevices.getUserMedia({audio:true,video:false});const Ctx=window.AudioContext||window.webkitAudioContext;audioContext ||= new Ctx();await audioContext.resume();const source=audioContext.createMediaStreamSource(micStream),analyser=audioContext.createAnalyser();analyser.fftSize=256;source.connect(analyser);const data=new Uint8Array(analyser.frequencyBinCount);
   const tick=()=>{analyser.getByteTimeDomainData(data);let sum=0;for(const v of data){const n=(v-128)/128;sum+=n*n;}$('mic-level').value=Math.min(1,Math.sqrt(sum/data.length)*4);micFrame=requestAnimationFrame(tick);};tick();
   report.microphone={status:'VERIFIED_IN_BROWSER_TEST',device:micStream.getAudioTracks()[0]?.label||'Browser microphone',permission:'granted'};$('stop-mic').disabled=false;status('audio-status','Microphone active. Speak and watch the level meter; input is not recorded or transmitted.',true);await enumerate();
  }catch(e){report.microphone={status:'FAILED_OR_BLOCKED',error:e.name||'Error'};status('audio-status','Microphone test failed: '+e.name+': '+e.message);}
 }
 function stopMic(){if(micFrame)cancelAnimationFrame(micFrame);micFrame=null;if(micStream)micStream.getTracks().forEach(t=>t.stop());micStream=null;$('mic-level').value=0;$('stop-mic').disabled=true;}
 $('enumerate').addEventListener('click',enumerate);$('start-camera').addEventListener('click',startCamera);$('stop-camera').addEventListener('click',stopCamera);$('start-record').addEventListener('click',startRecord);$('stop-record').addEventListener('click',stopRecord);$('test-audio').addEventListener('click',testAudio);$('test-mic').addEventListener('click',startMic);$('stop-mic').addEventListener('click',stopMic);
 $('export-report').addEventListener('click',()=>{report.created_at=new Date().toISOString();const blob=new Blob([JSON.stringify(report,null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='vyomaraj-device-test-report.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
 window.addEventListener('pagehide',()=>{stopCamera();stopMic();if(recordedUrl)URL.revokeObjectURL(recordedUrl);if(audioContext)audioContext.close();});enumerate();
})();