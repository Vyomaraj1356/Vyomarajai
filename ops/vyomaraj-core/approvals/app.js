'use strict';
const $=id=>document.getElementById(id);
const state={queue:null,review:null,decision:null};
function el(tag,text,cls){const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;}
function save(data,name){const u=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));const a=el('a');a.href=u;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(u),1000);}
function setShutter(open){$('shutter-art').classList.toggle('open',open);$('lens-note').textContent=open?'SHUTTER OPEN · REVIEW PLAYING':'SHUTTER CLOSED · PICK FROM THE QUEUE';}
async function loadQueue(){try{const r=await fetch('content.json');if(!r.ok)throw new Error('Content');const data=await r.json();state.queue=data;
 const awaiting=data.queue.filter(i=>i.status==='awaiting_owner');
 const select=$('queue-select');select.replaceChildren(el('option','— pick an item to open the shutter —',''));
 for(const item of awaiting){const o=el('option',`${item.title} · ${item.lane}`);o.value=item.id;select.append(o);}
 $('queue-status').textContent=awaiting.length?`${awaiting.length} item(s) awaiting the owner. ${data.notifications.policy}. Publishing gate: ${data.publishing.gate}.`:'Queue is empty.';
 select.onchange=()=>{if(select.value)openReview(select.value);else closeReview();};
}catch(e){$('error').hidden=false;}}
function closeReview(){$('camera').hidden=true;state.review=null;state.decision=null;$('download-decision').hidden=true;setShutter(false);}
async function openReview(id){const item=state.queue.queue.find(i=>i.id===id);if(!item)return;
 state.decision=null;$('download-decision').hidden=true;$('decision-status').textContent='';$('voice-instruction').value='';
 state.review=item;$('camera').hidden=false;
 $('review-title').textContent=item.title;
 $('review-meta').textContent=`Lane: ${item.lane} · Languages: ${item.languages.join(', ')} · Version line: ${item.version_line}`;
 $('review-lane').textContent=(item.lane.toUpperCase())+' · CREATED BY VYOMARAJ + JARVIS · AWAITING OWNER';
 $('video-note').textContent='VIDEO — '+item.review_payload.video_note;
 $('sound-note').textContent='SOUND — '+item.review_payload.sound_note;
 $('review-desc').textContent=item.review_payload.description;
 $('review-duration').textContent=`REVIEW PAYLOAD · ~${item.review_payload.duration_seconds}s DESCRIBED · NO MEDIA HOSTED`;
 setShutter(true);
 $('camera').scrollIntoView({behavior:'smooth'});
}
async function decide(decision){if(!state.review)return;$('decision-status').textContent='Recording the owner decision…';
 for(const b of document.querySelectorAll('.decision-buttons button'))b.disabled=true;
 try{const r=await fetch('/api/approvals/decide',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({item_id:state.review.id,decision,voice_instruction:$('voice-instruction').value||null})});
  const record=await r.json();if(!r.ok)throw new Error(record.error||'Decision unavailable');state.decision=record;
  $('decision-status').textContent=`Decision recorded: ${decision.toUpperCase()} — ${record.outcome}. ${record.cycle}`;
  $('download-decision').hidden=false;setShutter(false);
  await loadQueue();const select=$('queue-select');select.value='';
 }catch(e){$('decision-status').textContent=e.message;}finally{for(const b of document.querySelectorAll('.decision-buttons button'))b.disabled=false;}}
function init(){$('download-decision').onclick=()=>{if(state.decision)save(state.decision,'vyomaraj-owner-decision.json');};
 for(const [id,decision] of [['decide-approve','approve'],['decide-reject','reject'],['decide-rework','rework'],['decide-submit','submit']])$(id).onclick=()=>decide(decision);
 loadQueue();}
init();
