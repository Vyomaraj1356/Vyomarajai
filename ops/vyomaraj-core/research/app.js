'use strict';
const $=id=>document.getElementById(id);
const el=(tag,value,cls)=>{const n=document.createElement(tag);if(value!==undefined)n.textContent=value;if(cls)n.className=cls;return n;};
let status=null,records=[],offset=0,timer=null,busy=false;
const labels={catalog:'Existing editorial catalogue',musicbrainz:'MusicBrainz',loc:'Library of Congress',openlibrary:'Open Library',searxng:'SearXNG',ollama:'Ollama · optional AI'};
async function api(path,data,ownerToken){const headers={'Content-Type':'application/json'};if(ownerToken)headers.Authorization='Bearer '+ownerToken;const r=await fetch('/api/research/'+path,data?{method:'POST',headers,body:JSON.stringify(data)}:{});const body=await r.json();if(!r.ok){const required=body.required;throw new Error(required?`No work was changed. Obtain a one-time owner token for ${required.action}, scope ${required.scope}, target ${required.target}. The trusted issuer must be configured out of band.`:(body.detail||body.error||'request_failed'));}return body;}
function takeOwnerToken(){const input=$('owner-approval-token');const token=input.value.trim();input.value='';return token;}
function route(){const p=status?.profiles.find(x=>x.id===$('profile').value);$('route').textContent=p?`${p.slot} · proposed functional route · canonical name UNKNOWN · sources: ${p.providers.map(x=>labels[x]).join(', ')}`:'';}
function renderRecords(){
 $('records').replaceChildren();const visible=records.filter(r=>$('filter').value==='all'||r.review_status===$('filter').value);
 $('empty').hidden=visible.length>0;$('empty').textContent=status?.total_records?'No matching review states on this page. Change the filter or page.':'No leads yet. Queue a research pass above.';
 for(const r of visible){
  const card=el('article',undefined,'card');card.dataset.id=r.id;
  card.append(el('p',`${labels[r.provider]||r.provider} / ${r.provider_date||'date unverified'}`,'eyebrow'),el('h3',r.title),el('span',r.review_status.replaceAll('_',' '),'badge'));
  if(r.description)card.append(el('p',r.description));
  const source=el('a','Open source reference ↗','source');const u=new URL(r.source_url);if(['https:','http:'].includes(u.protocol)){source.href=u.href;source.target='_blank';source.rel='noopener noreferrer';card.append(source);}
  card.append(el('p',`${r.proposed_slots.join(' / ')} · PROPOSED · name UNKNOWN`),el('p',`Rights UNKNOWN · availability NOT VERIFIED. First seen ${new Date(r.first_seen).toLocaleDateString()}. No media imported.`));
  if(r.ai_note)card.append(el('p',`AI advisory, unverified: ${r.ai_note.summary}`,'note'));
  const actions=el('div',undefined,'actions');
  for(const [decision,label] of [['accepted_metadata_only','Accept metadata'],['rejected','Reject'],['pending_review','Reset review']]){
   const button=el('button',label,decision==='accepted_metadata_only'?'':'quiet');button.disabled=!$('ack').checked||r.review_status===decision;
   button.addEventListener('click',async()=>{button.disabled=true;try{await api('review',{record_id:r.id,decision,acknowledge_metadata_only:$('ack').checked},takeOwnerToken());$('message').textContent='Owner-authorized local review saved. Rights remain UNKNOWN; no content was published.';await refresh();}catch(e){$('message').textContent='Review not saved: '+e.message;renderRecords();}});actions.append(button);
  }card.append(actions);$('records').append(card);
 }
 $('count').textContent=`${status?.total_records||0} leads`;$('page').textContent=`Records ${records.length?offset+1:0}–${offset+records.length}`;
 $('previous').disabled=offset===0;$('next').disabled=offset+100>=(status?.total_records||0);
}
function renderStatus(){
 const selected=$('profile').value;if(!$('profile').options.length){for(const p of status.profiles){const o=el('option',p.label);o.value=p.id;$('profile').append(o);}if(selected)$('profile').value=selected;}
 $('run').disabled=busy;route();$('tools').replaceChildren();
 for(const name of Object.keys(labels)){
  const last=status.jobs.map(j=>j.result.sources?.[name]).find(Boolean);
  const box=el('div',undefined,'tool');box.append(el('b',labels[name]));
  let note=last?`${last.status}${last.reason?' · '+last.reason:''}${last.cached?' · 24h cache':''}`:'Not yet checked';
  if(name==='searxng'&&!status.optional_tools.searxng_configured)note='Not configured · local service required';
  if(name==='ollama'&&!status.optional_tools.ollama_configured)note='Not configured · model/service required';
  box.append(el('p',note));$('tools').append(box);
 }
 $('runs').replaceChildren();
 for(const j of status.jobs.slice(0,8)){
  const details=el('details',undefined,'run'),summary=el('summary');
  summary.append(el('span',j.state,'badge '+j.state),el('b',status.profiles.find(p=>p.id===j.profile)?.label||j.profile),el('span',new Date(j.created*1000).toLocaleString()));details.append(summary);
  const list=el('ul');for(const [name,r] of Object.entries(j.result.sources||{}))list.append(el('li',`${labels[name]||name}: ${r.status}${r.reason?' — '+r.reason:''}${r.records!==undefined?' · '+r.records+' leads':''}${r.cached?' · cached':''}`));
  if(j.result.error)list.append(el('li',j.result.error));
  list.append(el('li',`${j.result.new_records||0} new queue records. No media downloaded or content published.`));details.append(list);$('runs').append(details);
 }
}
async function refresh(){clearTimeout(timer);try{const [s,r]=await Promise.all([api('status'),api('records?offset='+offset)]);status=s;records=r.records;renderStatus();renderRecords();if(status.jobs.some(j=>['queued','running'].includes(j.state)))timer=setTimeout(refresh,3000);}catch(e){$('message').textContent='Local service unavailable: '+e.message;$('run').disabled=true;}}
$('run').addEventListener('click',async()=>{busy=true;$('run').disabled=true;try{const job=await api('run',{profile:$('profile').value},takeOwnerToken());$('message').textContent=job.reused?'Existing pass reused. Queue de-duplication and cache prevent repeated provider requests.':'Research queued. Follow each source result below; a blocked source is not a successful search.';await refresh();}catch(e){$('message').textContent='Research not queued: '+e.message;}finally{busy=false;$('run').disabled=!status;}});
$('profile').addEventListener('change',route);$('ack').addEventListener('change',renderRecords);$('filter').addEventListener('change',renderRecords);$('refresh').addEventListener('click',refresh);
$('previous').addEventListener('click',()=>{offset=Math.max(0,offset-100);refresh();});$('next').addEventListener('click',()=>{offset+=100;refresh();});
refresh().then(()=>{if(status)$('message').textContent='Local queue ready. Provider connections are reported separately below.';});
