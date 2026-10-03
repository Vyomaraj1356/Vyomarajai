'use strict';
const $=id=>document.getElementById(id);
const state={data:null,mode:'3d',step:0,topic:'overview',recipe:null,plan:null,ready:false,version:0};
function el(tag,text,cls){const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;}
function sources(ids,parent){ids.forEach(id=>{const s=state.data.sources.find(x=>x.id===id);if(!s)return;const a=el('a',s.citation.match(/^\[\d+\]/)[0]+' '+s.title,'source-link');a.href=s.url;a.target='_blank';a.rel='noopener noreferrer';parent.append(a);});}
function invalidate(){state.version++;state.plan=null;$('download').hidden=true;$('plan-preview').hidden=true;$('plan-status').textContent='';$('plan').disabled=!state.ready;}
function selectTopic(id,title){state.topic=id;$('topic-title').textContent=title;invalidate();document.querySelectorAll('[data-topic]').forEach(n=>n.classList.toggle('selected',n.dataset.topic===id));$('handoff').scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'});}
function topicButton(id,title){const b=el('button','Use in my local plan ↗','text-button');b.onclick=()=>selectTopic(id,title);return b;}
function renderStories(){
 $('story-list').replaceChildren();const filter=$('story-filter').value;
 state.data.stories.forEach((s,i)=>{if(filter!=='all'&&s.category!==filter)return;
  const c=el('article',undefined,'story');c.dataset.topic=s.id;c.classList.toggle('selected',s.id===state.topic);
  c.append(el('span',String(i+1).padStart(2,'0'),'number'),el('p',s.evidence_type+' · PROPOSED CHAPTER','eyebrow'),el('h3',s.title),el('p',s.summary));sources(s.source_ids,c);c.append(topicButton(s.id,s.title));$('story-list').append(c);
 });
}
function renderAvatars(){state.data.avatars.forEach(a=>{const c=el('article',undefined,'avatar');c.dataset.topic=a.id;c.append(el('span','TRADITIONAL NARRATIVE','badge'),el('h3',a.name),el('p',a.form));const details=el('details');details.append(el('summary','List variations'),el('p',a.note));c.append(details);sources(a.source_ids,c);c.append(topicButton(a.id,a.name));$('avatar-list').append(c);});}
function renderPeethas(){
 const rows=state.data.peethas.filter(p=>$('region').value==='all'||p.region===$('region').value);$('peetha-list').replaceChildren();$('peetha-count').textContent=rows.length+' of 9 starter profiles';
 rows.forEach(p=>{const c=el('article',undefined,'peetha');c.dataset.topic=p.id;c.classList.toggle('selected',p.id===state.topic);c.append(el('span',p.category,'badge'),el('p',p.location,'eyebrow'),el('h3',p.name),el('p',p.list_tradition,'classification'),el('p',p.history_overview));const details=el('details');details.append(el('summary','Origin, context & limitations'),el('p',p.origin_note),el('p','Bhairava / body-part assignment / live timings: not verified in this pack. Confirm temple-specific rules.'));c.append(details);sources(p.source_ids,c);c.append(topicButton(p.id,p.name));$('peetha-list').append(c);});
}
function renderRecipes(){
 const matches=state.data.recipes.filter(r=>($('diet').value!=='plant-based'||r.diet==='plant-based')&&(!$('no-milk').checked||!r.allergens.includes('milk')));
 if(!matches.some(r=>r.id===state.recipe)){state.recipe=matches[0]?.id||null;state.step=0;}
 $('recipe').replaceChildren(...matches.map(r=>{const o=el('option',r.name);o.value=r.id;return o;}));$('recipe').value=state.recipe;renderFood();
}
function renderFood(){
 const r=state.data.recipes.find(x=>x.id===state.recipe);if(!r)return;
 $('recipe-note').textContent=r.note;$('recipe-title').textContent=r.name;$('ingredients').replaceChildren(...r.ingredients.map(i=>el('span',i)));
 $('procedure').replaceChildren(...r.procedure.map(p=>el('li',p)));
 $('allergen-note').textContent='Listed allergens: '+(r.allergens.join(', ')||'none in this proposed recipe')+'. Not an allergy-free guarantee; check every ingredient and cross-contact.';
 $('food-pieces').replaceChildren();
 if(r.id==='yogurt'){const base=el('span');base.style.cssText='position:absolute;inset:12%;border-radius:50%;background:#fff8e9;box-shadow:inset 2px 3px 8px #9e855f33';$('food-pieces').append(base);}
 for(let i=0;i<24;i++){
  const a=i*2.39996,rad=Math.sqrt(i/24)*(r.id==='yogurt'?26:35);const p=el('span',undefined,'food-piece');
  let color=r.color,shape='border-radius:50%;';
  if(r.id==='fruit'){color=['#e5cb80','#f1ddb1','#71864f'][i%3];shape=i%3===1?'border-radius:65% 10% 65% 10%;border-right:3px solid #b86245;':'border-radius:50%;';}
  if(r.id==='coconut'){color=i%2?'#bd9857':'#f6eedc';shape=i%2?'border-radius:45%;':'border-radius:15% 15% 55% 55%;border-bottom:3px solid #805a3b;';}
  if(r.id==='yogurt'){color=i%2?'#e4c980':'#f0dab3';shape='border-radius:50%;';}
  p.style.cssText=`left:${44+Math.cos(a)*rad}%;top:${44+Math.sin(a)*rad}%;width:12%;height:12%;--food-color:${color};transform:rotate(${i*31}deg) translateZ(7px);${shape}`;$('food-pieces').append(p);
 }
 $('personal-note').textContent='Your choices: '+$('diet').selectedOptions[0].textContent+($('no-milk').checked?' · listed milk excluded':'')+'. These preferences do not establish ritual or clinical suitability.';
 renderMode();
}
function renderMode(){
 const notes={'3d':'Explore a rotatable CSS-perspective plate—not an AI-generated 3D mesh.','4d':'Add a time sequence: advance each preparation step yourself.','5d':'Add context: personalise topic, region, diet and listed-allergen preferences.'};
 $('mode-note').textContent=notes[state.mode];document.querySelectorAll('[data-mode]').forEach(b=>b.setAttribute('aria-pressed',String(state.mode===b.dataset.mode)));
 $('sequence').hidden=state.mode!=='4d';$('personal-note').hidden=state.mode!=='5d';
 const r=state.data.recipes.find(x=>x.id===state.recipe);if(!r)return;state.step=Math.min(state.step,r.procedure.length-1);
 $('step-count').textContent=`STEP ${state.step+1} / ${r.procedure.length}`;$('step-text').textContent=r.procedure[state.step];$('previous').disabled=state.step===0;$('next').disabled=state.step===r.procedure.length-1;
}
async function makePlan(){
 invalidate();const version=state.version;$('plan').disabled=true;$('plan-status').textContent='Preparing a local, source-linked handoff…';
 try{const response=await fetch('/api/plan',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({experience:'bhakti',topic_id:state.topic,recipe_id:state.recipe,mode:state.mode,diet:$('diet').value,exclude_allergens:$('no-milk').checked?['milk']:[]})});const plan=await response.json();if(version!==state.version)return;if(!response.ok)throw new Error(plan.error||'Unable to create plan.');state.plan=plan;$('plan-status').textContent='Local Vyomaraj → Jarvis handoff created. Human review required; no AI call or publication occurred.';$('plan-preview').textContent=JSON.stringify({topic:plan.topic,category:plan.category_id,mode:plan.mode,recipe:plan.recipe,status:plan.status,ai_calls_made:plan.ai_calls_made},null,2);$('plan-preview').hidden=false;$('download').hidden=false;
 }catch(e){if(version===state.version)$('plan-status').textContent=e.message;}finally{if(version===state.version)$('plan').disabled=!state.ready;}
}
function download(){if(!state.plan)return;const url=URL.createObjectURL(new Blob([JSON.stringify(state.plan,null,2)],{type:'application/json'}));const a=el('a');a.href=url;a.download='vyomaraj-jarvis-bhakti-plan.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
async function init(){
 try{const response=await fetch('content.json');if(!response.ok)throw new Error('content');state.data=await response.json();
 $('story-filter').onchange=renderStories;$('region').onchange=renderPeethas;
 $('diet').onchange=$('no-milk').onchange=()=>{invalidate();renderRecipes();};$('recipe').onchange=()=>{state.recipe=$('recipe').value;state.step=0;invalidate();renderFood();};
 $('rotate').oninput=()=>{$('plate').style.setProperty('--angle',$('rotate').value+'deg');$('angle').textContent=$('rotate').value+'°';};
 document.querySelectorAll('[data-mode]').forEach(b=>b.onclick=()=>{state.mode=b.dataset.mode;invalidate();renderMode();});
 $('previous').onclick=()=>{state.step=Math.max(0,state.step-1);renderMode();};$('next').onclick=()=>{const r=state.data.recipes.find(x=>x.id===state.recipe);state.step=Math.min(r.procedure.length-1,state.step+1);renderMode();};
 $('tv-summary').textContent=state.data.television.summary;sources(state.data.television.source_ids,$('tv-source'));$('tv-plan').onclick=()=>selectTopic('mahadev-tv',state.data.television.title);
 state.data.research_backlog.forEach(t=>$('backlog').append(el('li',t)));state.data.editorial_rules.forEach(t=>$('rules').append(el('li',t)));state.data.sources.forEach(s=>{const li=el('li');sources([s.id],li);$('sources').append(li);});
 $('plan').onclick=makePlan;$('download').onclick=download;renderStories();renderAvatars();renderPeethas();renderRecipes();
 try{const r=await fetch('/api/status');const config=await r.json();state.ready=r.ok&&config.status==='local_preview_planning_only';}catch(e){state.ready=false;}
 $('runtime-status').textContent=state.ready?'Local planning API connected. AI provider: not configured.':'Planning endpoint unavailable. Content remains viewable; no integration success claimed.';$('plan').disabled=!state.ready;
 }catch(e){$('error').hidden=false;}
}
init();
