'use strict';
const $=id=>document.getElementById(id);
const state={data:null,queue:[],ready:false,plan:null,version:0,mediaURL:null};
function el(tag,text,cls){const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;}
function link(title,url){const a=el('a',title);a.href=url;a.target='_blank';a.rel='noopener noreferrer';return a;}
function sourceLinks(ids,node){for(const id of ids){const s=state.data.sources.find(s=>s.id===id);const a=link(s.citation.match(/^\[\d+\]/)[0]+' '+s.title,s.url);a.className='source';node.append(a);}}
function invalidate(){state.version++;state.plan=null;$('download').hidden=true;$('rundown').hidden=true;$('plan-status').textContent='';$('plan').disabled=!state.ready||state.queue.length===0;}
function renderCollection(){
 const q=$('search').value.trim().toLowerCase();const rows=state.data.items.filter(i=>($('kind').value==='all'||i.kind===$('kind').value)&&($('era').value==='all'||i.era===$('era').value)&&($('region').value==='all'||i.region===$('region').value)&&[i.title,i.summary,i.language,...i.artists].join(' ').toLowerCase().includes(q));
 $('collection').replaceChildren();$('count').textContent=`${rows.length} of ${state.data.items.length} starter cards`;$('empty').hidden=rows.length>0;
 for(const i of rows){const selected=state.queue.includes(i.id);const c=el('article',undefined,'card'+(selected?' selected':''));
  c.append(el('span',`${i.kind} / ${i.era} / ${i.region}`,'meta'),el('h3',i.title));
  if(i.artists.length)c.append(el('div',i.artists.join(' · '),'artist'));
  c.append(el('p',i.summary),el('p',[i.record_type,i.year,i.language].filter(Boolean).join(' · '),'small'));sourceLinks(i.source_ids,c);
  if(i.publisher_url){const a=link('Open chart publisher ↗',i.publisher_url);a.className='source';c.append(a);}
  if(!i.source_ids.length)c.append(el('span','PROPOSED PRODUCTION FORMAT','badge'));
  const b=el('button',selected?'Remove from plan −':'Add to plan +','text-button add');b.id='add-'+i.id;b.setAttribute('aria-pressed',String(selected));b.disabled=!selected&&state.queue.length>=8;b.onclick=()=>{toggle(i.id);$(b.id)?.focus({preventScroll:true});};c.append(b);$('collection').append(c);
 }
}
function toggle(id){if(state.queue.includes(id))state.queue=state.queue.filter(x=>x!==id);else if(state.queue.length<8)state.queue.push(id);invalidate();renderQueue();renderCollection();}
function renderQueue(){
 $('queue').replaceChildren();$('queue-count').textContent=state.queue.length;$('queue-empty').hidden=state.queue.length>0;
 state.queue.forEach((id,index)=>{const i=state.data.items.find(i=>i.id===id);const li=el('li');li.append(el('span',`${index+1}. ${i.title}`));const actions=el('div',undefined,'actions');
  for(const [text,label,step] of [['↑','Move up',-1],['↓','Move down',1]]){const b=el('button',text);b.setAttribute('aria-label',label+' '+i.title);b.disabled=index+step<0||index+step>=state.queue.length;b.onclick=()=>{const next=index+step;[state.queue[index],state.queue[next]]=[state.queue[next],state.queue[index]];invalidate();renderQueue();};actions.append(b);}
  const remove=el('button','×');remove.setAttribute('aria-label','Remove '+i.title);remove.onclick=()=>toggle(id);actions.append(remove);li.append(actions);$('queue').append(li);
 });
 $('chart-add').disabled=!state.queue.includes('ifpi2025')&&state.queue.length>=8;$('chart-add').textContent=state.queue.includes('ifpi2025')?'Remove chart from plan −':'Add this dated chart to my plan +';
}
function renderPlan(plan){$('rundown').replaceChildren(el('h3',`${plan.duration_minutes}-minute ${plan.mode} plan`),el('p','Editorial budgets—not recording durations or a rendered broadcast.','small'));const list=el('ol');for(const segment of plan.rundown){const li=el('li',segment.title||segment.type.replaceAll('_',' '));li.append(el('small',`${Math.floor(segment.start_seconds/60)}:${String(segment.start_seconds%60).padStart(2,'0')} · ${segment.budget_seconds}s budget`),el('p',segment.cue||segment.text));list.append(li);}const detail=el('details');detail.append(el('summary','Source and release review gates'));const gates=el('ul');plan.review_gates.forEach(g=>gates.append(el('li',g)));detail.append(gates);$('rundown').append(list,detail);$('rundown').hidden=false;}
async function prepare(){
 invalidate();const version=state.version;$('plan').disabled=true;$('plan-status').textContent='Preparing a local music-agent handoff…';
 try{const response=await fetch('/api/plan',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({experience:'music',item_ids:[...state.queue],mode:$('mode').value,duration_minutes:Number($('duration').value)})});const plan=await response.json();if(version!==state.version)return;if(!response.ok)throw new Error(plan.error||'Plan unavailable.');state.plan=plan;renderPlan(plan);$('download').hidden=false;$('plan-status').textContent='Local plan created. Proposed agent bindings; no AI call, streaming or publication.';}catch(e){if(version===state.version)$('plan-status').textContent=e.message;}finally{if(version===state.version)$('plan').disabled=!state.ready||!state.queue.length;}
}
function download(){if(!state.plan)return;const u=URL.createObjectURL(new Blob([JSON.stringify(state.plan,null,2)],{type:'application/json'}));const a=el('a');a.href=u;a.download='vyomaraj-music-programme-plan.json';a.click();setTimeout(()=>URL.revokeObjectURL(u),1000);}
function clearMedia(){for(const id of ['audio-player','video-player']){const p=$(id);p.pause();p.removeAttribute('src');p.load();p.hidden=true;}if(state.mediaURL)URL.revokeObjectURL(state.mediaURL);state.mediaURL=null;$('media-file').value='';$('media-status').textContent='No local file selected. Catalogue links do not grant playback rights.';}
function openMedia(){
 const file=$('media-file').files[0];clearMedia();if(!file)return;
 if(!$('permission').checked){$('media-status').textContent='Confirm permission before previewing a file.';return;}
 if(!/^(audio|video)\//.test(file.type)||file.size>100*1024*1024){$('media-status').textContent='Choose a recognised audio/video file no larger than 100 MB.';return;}
 state.mediaURL=URL.createObjectURL(file);const p=$(file.type.startsWith('audio/')?'audio-player':'video-player');p.src=state.mediaURL;p.hidden=false;p.load();$('media-status').textContent=file.name+' · local browser preview only; not uploaded.';
}
async function init(){
 try{const response=await fetch('content.json');if(!response.ok)throw new Error('Content unavailable');state.data=await response.json();
 for(const region of [...new Set(state.data.items.map(i=>i.region))].sort()){const o=el('option',region);o.value=region;$('region').append(o);}
 $('search').oninput=renderCollection;for(const id of ['kind','era','region'])$(id).onchange=renderCollection;
 $('reset').onclick=()=>{$('search').value='';for(const id of ['kind','era','region'])$(id).value='all';renderCollection();};
 $('nostalgia').onclick=()=>{$('reset').click();$('kind').value='radio';renderCollection();$('discover').scrollIntoView();};
 for(const a of state.data.agents){const c=el('article',undefined,'agent');c.dataset.agentId=a.slot;c.append(el('span','EXISTING POSITION','slot'),el('h3',a.slot.split('-S').pop()),el('p','Proposed function: '+a.proposed_label),el('p',a.function));$('agents-list').append(c);}
 for(const row of state.data.chart_snapshot.entries){const li=el('li');const box=el('div');box.append(el('strong',row.title),el('small',row.artist));li.append(box);$('top-list').append(li);}
 $('chart-caption').textContent='This example uses the IFPI 2025 annual global singles chart. It is not a 2026 weekly ranking.';sourceLinks(state.data.chart_snapshot.source_ids,$('chart-source'));$('chart-add').onclick=()=>toggle('ifpi2025');
 state.data.sources.forEach(s=>{const li=el('li');li.append(link(s.citation.match(/^\[\d+\]/)[0]+' '+s.title,s.url),el('p',s.review_basis,'small'));$('sources').append(li);});state.data.backlog.forEach(t=>$('backlog').append(el('li',t)));
 $('mode').onchange=$('duration').onchange=invalidate;$('plan').onclick=prepare;$('download').onclick=download;
 $('permission').onchange=()=>{$('media-file').disabled=!$('permission').checked;if(!$('permission').checked)clearMedia();};$('media-file').onchange=openMedia;$('clear-media').onclick=clearMedia;
 for(const id of ['audio-player','video-player'])$(id).onerror=()=>{if($(id).getAttribute('src'))$('media-status').textContent='This file could not be decoded. Try a browser-supported audio/video format. Nothing was uploaded.';};window.addEventListener('pagehide',clearMedia);
 renderCollection();renderQueue();
 try{const r=await fetch('/api/status');const c=await r.json();state.ready=r.ok&&c.experiences.includes('music')&&c.status==='local_preview_planning_only';}catch(e){state.ready=false;}
 $('runtime').textContent=state.ready?'Local music routing + Vyomaraj/Jarvis handoff available. External AI and streaming providers: not connected.':'Planning endpoint unavailable. Discovery remains viewable; no integration success claimed.';invalidate();
 }catch(e){$('error').hidden=false;}
}
init();
