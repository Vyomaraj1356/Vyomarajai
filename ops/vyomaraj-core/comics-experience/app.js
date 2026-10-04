'use strict';
const $=id=>document.getElementById(id);
const state={data:null,refs:[],ready:false,plan:null,version:0};
const limits={strip:[3,6],oneshot:[8,32],issue:[24,64],'graphic-novel':[96,240]};
const langNames={hi:'Hindi',en:'English',hinglish:'Hinglish'};
function el(tag,text,cls){const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;}
function sources(ids,node){for(const id of ids){const s=state.data.sources.find(s=>s.id===id);const a=el('a',s.citation.match(/^\[\d+\]/)[0]+' '+s.title,'source');a.href=s.url;a.target='_blank';a.rel='noopener noreferrer';node.append(a);}}
function save(data,name){const u=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));const a=el('a');a.href=u;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(u),1000);}
function invalidate(){state.version++;state.plan=null;$('download-plan').hidden=true;$('plan-status').textContent='';$('plan').disabled=!state.ready;$('outline').replaceChildren(el('h3','Ready for your next issue plan.'),el('p','Select a format, seed and primary language. All three editions are always included.'));}
function editions(i){const wrap=el('div',undefined,'editions');for(const code of ['hi','en','hinglish']){const e=i.language_editions&&i.language_editions[code];const chip=el('span',e?`${langNames[code]}: ${e.title} — ${e.tagline}`:`${langNames[code]} edition planned`,'edition-chip');chip.lang=code==='hi'?'hi':code==='en'?'en':undefined;wrap.append(chip);}return wrap;}
function versions(i){const wrap=el('div',undefined,'versions');if(!i.versions){wrap.append(el('span','Context reference — no version line.','small'));return wrap;}
 const past=el('span',`Past (preserved): ${i.versions.past.map(v=>'v'+v.edition+' '+v.label).join(' · ')}`,'version-chip past');
 const future=el('span',`Future (plannable): ${i.versions.future.map(v=>'v'+v.edition+' '+v.label).join(' · ')}`,'version-chip future');
 wrap.append(past,future);return wrap;}
function collection(){const q=$('search').value.trim().toLowerCase();const rows=state.data.items.filter(i=>($('kind').value==='all'||i.kind===$('kind').value)&&($('era').value==='all'||i.era===$('era').value)&&($('language-filter').value==='all'||(i.language_editions&&i.language_editions[$('language-filter').value]))&&[i.title,i.summary,i.kind].join(' ').toLowerCase().includes(q));
 $('collection').replaceChildren();$('count').textContent=`${rows.length} of ${state.data.items.length} starter entries`;$('empty').hidden=rows.length>0;
 for(const i of rows){const selected=state.refs.includes(i.id),c=el('article',undefined,'card'+(selected?' selected':''));
  c.append(el('span',`${i.kind} / ${i.era} / ${i.language}`,'meta'),el('h3',i.title),el('p',i.summary));
  if(i.credits)c.append(el('p',i.credits,'artist'));
  if(i.language_editions)c.append(editions(i));
  if(i.versions)c.append(versions(i));
  sources(i.source_ids,c);
  c.append(el('p',i.kind==='heritage-reference'?'Heritage context only · no copy or adaptation':'Original proposal · no artwork rendered','small'));
  const b=el('button',selected?'Remove reference −':'Add research reference +','text-button add');b.id='add-'+i.id;b.disabled=!selected&&state.refs.length>=6;b.setAttribute('aria-pressed',String(selected));
  b.onclick=()=>{state.refs=selected?state.refs.filter(x=>x!==i.id):[...state.refs,i.id];invalidate();collection();$('reference-count').textContent=state.refs.length;$('selected').textContent=state.refs.length?'Research context only: '+state.refs.map(id=>state.data.items.find(i=>i.id===id).title).join(' · '):'No references selected. You can still plan an original issue.';$(b.id)?.focus({preventScroll:true});};
  c.append(b);$('collection').append(c);}}
function formatChanged(){const f=state.data.formats.find(f=>f.id===$('format').value);$('panels').min=limits[f.id][0];$('panels').max=limits[f.id][1];$('panels').value=f.default_panels;invalidate();}
async function plan(){if(!$('panels').reportValidity())return;invalidate();const version=state.version;$('plan').disabled=true;$('plan-status').textContent='Preparing a local trilingual issue plan…';
 try{const r=await fetch('/api/plan',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({experience:'comics',item_ids:[...state.refs],format:$('format').value,primary_language:$('primary-language').value,versions:$('versions').value,seed:$('seed').value,panels:$('panels').valueAsNumber})});
  const p=await r.json();if(version!==state.version)return;if(!r.ok)throw new Error(p.error||'Plan unavailable');state.plan=p;
  $('outline').replaceChildren(el('p','ORIGINAL ISSUE PLAN · NOT FINISHED ARTWORK','eyebrow'),el('h3',p.original_seed.title),el('p',p.original_seed.premise));
  const lm=el('div',undefined,'outline-block');lm.append(el('p','LANGUAGE MATRIX — all three editions, always','strong'));for(const e of p.language_matrix.editions){const row=el('p',`${langNames[e.language]}: ${e.title} — ${e.tagline}`);row.lang=e.language==='hi'?'hi':undefined;lm.append(row);}
  const vl=el('div',undefined,'outline-block');vl.append(el('p','VERSION LINEAGE — past preserved, future plannable','strong'));
  if(p.version_lineage.past)for(const v of p.version_lineage.past)vl.append(el('p',`Past v${v.edition}: ${v.label} (${v.status})`));
  if(p.version_lineage.future)for(const v of p.version_lineage.future)vl.append(el('p',`Future v${v.edition}: ${v.label} (${v.status})`));
  const caps=el('div',undefined,'outline-block');caps.append(el('p',`SAMPLE CAPTIONS — ${p.sample_captions_language}`,'strong'));const pre=el('pre',p.sample_captions.join('\n'));pre.lang=p.sample_captions_language==='Hindi'?'hi':undefined;caps.append(pre);
  const gates=el('details');gates.append(el('summary','Review gates and owner gate'));const ul=el('ul');p.review_gates.forEach(g=>ul.append(el('li',g)));ul.append(el('li','Owner gate: '+p.owner_gate.status+' — '+p.owner_gate.rule));gates.append(ul);
  $('outline').append(lm,vl,caps,gates);$('download-plan').hidden=false;$('plan-status').textContent='Local Vyomaraj → Jarvis trilingual plan ready. No AI call or artwork rendering.';
 }catch(e){if(version===state.version)$('plan-status').textContent=e.message;}finally{if(version===state.version)$('plan').disabled=!state.ready;}}
async function init(){try{const r=await fetch('content.json');if(!r.ok)throw new Error('Content');state.data=await r.json();
  for(const kind of [...new Set(state.data.items.map(i=>i.kind))]){const o=el('option',kind);o.value=kind;$('kind').append(o);}
  for(const f of state.data.formats){const o=el('option',f.title);o.value=f.id;$('format').append(o);}
  $('format').value='strip';$('format').onchange=formatChanged;formatChanged();
  for(const id of ['primary-language','versions','seed','panels'])$(id).oninput=invalidate;
  $('search').oninput=collection;for(const id of ['kind','era','language-filter'])$(id).onchange=collection;
  $('reset').onclick=()=>{$('search').value='';for(const id of ['kind','era','language-filter'])$(id).value='all';collection();};
  $('plan').onclick=plan;$('download-plan').onclick=()=>{if(state.plan)save(state.plan,'vyomaraj-comics-issue-plan.json');};
  for(const a of state.data.agents){const c=el('article',undefined,'agent');c.dataset.agentId=a.slot;c.append(el('span','EXISTING POSITION','slot'),el('h3',a.slot.split('-S').pop()),el('p','Proposed function: '+a.proposed_label,'small'));$('agents').append(c);}
  for(const s of state.data.sources){const li=el('li');sources([s.id],li);li.append(el('p',s.review_basis,'small'));$('sources').append(li);}
  state.data.backlog.forEach(x=>$('backlog').append(el('li',x)));
  collection();
  try{const response=await fetch('/api/status');const c=await response.json();state.ready=response.ok&&c.status==='local_preview_planning_only'&&c.experiences.includes('comics');}catch(e){state.ready=false;}
  $('runtime').textContent=state.ready?'Local comics routing and Vyomaraj/Jarvis handoff available. Artwork rendering and publishing providers: not connected.':'Planning endpoint unavailable; discovery and local previews remain separate.';
  invalidate();
 }catch(e){$('error').hidden=false;}}
init();
