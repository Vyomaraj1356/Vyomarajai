'use strict';
const $ = id => document.getElementById(id);
const state = {data:null, selected:null, mode:'3d', step:0, scope:'all'};
function el(tag, text, cls) { const n=document.createElement(tag); if(text!==undefined)n.textContent=text; if(cls)n.className=cls; return n; }
function sourceLinks(ids, parent) {
  ids.forEach(id=>{const s=state.data.sources.find(x=>x.id===id); if(!s)return;
    const a=el('a',s.citation.match(/^\[\d+\]/)[0]+' '+s.title,'source-link');
    a.href=s.url;a.target='_blank';a.rel='noopener noreferrer';parent.append(a);
  });
}
function availableSnacks() {
  const diet=$('diet').value;const excluded=[...document.querySelectorAll('input[name=exclude]:checked')].map(x=>x.value);
  return state.data.snacks.filter(s=>{
    const ok=diet==='all'||diet==='pescatarian'||(diet==='vegetarian'&&['vegetarian','plant-based'].includes(s.diet))||s.diet===diet;
    return ok&&!s.allergens.some(a=>excluded.includes(a));
  });
}
function renderList() {
  const snacks=availableSnacks();
  if(!snacks.some(s=>s.id===state.selected)){state.selected=snacks[0]?.id||null;state.step=0;}
  $('snack-list').replaceChildren();$('empty').hidden=snacks.length>0;
  snacks.forEach(s=>{const b=el('button',s.name,'snack-button');b.setAttribute('aria-pressed',String(s.id===state.selected));b.onclick=()=>{state.selected=s.id;state.step=0;renderList();};$('snack-list').append(b);});
  renderSnack();
}
function renderPlate(s) {
  $('food').replaceChildren();
  if(!s)return;
  for(let i=0;i<29;i++){
    const t=i*2.39996,r=Math.sqrt(i/29)*36,x=45+Math.cos(t)*r,y=44+Math.sin(t)*r;
    const n=el('span',undefined,i%6===0?'food-piece garnish':'food-piece');
    n.style.cssText=`left:${x}%;top:${y}%;width:${i%6===0?17:12}%;height:${i%6===0?8:12}%;--food-color:${s.color};transform:rotate(${i*39}deg) translateZ(8px);`;
    $('food').append(n);
  }
}
function renderSnack() {
  const s=state.data.snacks.find(x=>x.id===state.selected);
  document.querySelector('.selected-info').hidden=!s;document.querySelector('.scene').hidden=!s;
  document.querySelector('.rotation').hidden=!s;
  if(!s){$('sequence').hidden=true;return;}
  $('snack-name').textContent=s.name;$('snack-region').textContent=s.region+' · '+s.diet;
  $('pairing').textContent=s.pairing_style;$('nutrition').textContent=s.nutrition_note;
  $('allergens').textContent='Listed allergens: '+(s.allergens.join(', ')||'none in this proposed recipe')+'. Check labels and cross-contact.';
  $('ingredients').replaceChildren(...s.ingredients.map(i=>el('span',i)));
  $('zero').textContent=s.non_alcoholic_pairing;
  $('procedure').replaceChildren(...s.procedure.map(p=>el('li',p)));
  $('personal').textContent=`Your plate: ${$('diet').selectedOptions[0].textContent}; ${$('flavour').selectedOptions[0].textContent.toLowerCase()}. ${$('flavour').value==='gentle'?'Keep chilli optional and preserve the base flavours.':'Adjust chilli to personal tolerance; more heat is not a better or healthier pairing.'} This is a preference aid, not medical advice.`;
  renderPlate(s);renderMode();
}
function renderMode() {
  const descriptions={
    '3d':'Explore · Rotate an illustrative CSS-perspective plate. Not an AI-generated 3D asset.',
    '4d':'Sequence · A time-based preparation story, advanced at your pace. “4D” is our project convention.',
    '5d':'Personalise · Use diet, allergen and spice controls. “5D” adds context, not physical sensory dimensions.'
  };
  $('mode-note').textContent=descriptions[state.mode];
  document.querySelectorAll('[data-mode]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.mode===state.mode)));
  const s=state.data.snacks.find(x=>x.id===state.selected);
  $('sequence').hidden=state.mode!=='4d'||!s;$('personal').hidden=state.mode!=='5d';
  if(s){state.step=Math.min(state.step,s.procedure.length-1);$('step-count').textContent=`STEP ${state.step+1} / ${s.procedure.length}`;$('step-text').textContent=s.procedure[state.step];$('previous').disabled=state.step===0;$('next').disabled=state.step===s.procedure.length-1;}
}
function renderTraditions() {
  $('traditions').replaceChildren();
  state.data.traditions.filter(t=>state.scope==='all'||t.scope===state.scope).forEach(t=>{
    const card=el('article',undefined,'tradition');
    card.append(el('span',t.research_status==='research_candidate'?'Research candidate':'Source-backed overview','badge'+(t.research_status==='research_candidate'?' candidate':'')),el('p',t.region,'eyebrow'),el('h3',t.name),el('p',t.history));
    const d=el('details'),summary=el('summary','Style, specifications & process overview');d.append(summary,el('p','Ingredient base: '+t.base),el('p','Style: '+t.style));
    const ol=el('ol');t.process_overview.forEach(p=>ol.append(el('li',p)));d.append(ol,el('p','ABV / licensed producer / local legal age: not verified.'),el('p',t.specification_note));card.append(d);sourceLinks(t.source_ids,card);$('traditions').append(card);
  });
  document.querySelectorAll('[data-scope]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.scope===state.scope)));
}
function renderEvents() {
  $('events').replaceChildren();
  state.data.events.forEach(e=>{
    const card=el('article',undefined,'event');
    const label=e.date_status==='historical_edition_only'?'PAST EDITION':e.start?'PUBLISHED DATE SNAPSHOT':'DATES UNCONFIRMED';
    card.append(el('span',label,'badge'),el('h3',e.name),el('p',e.region),el('p',e.start?`${e.start} → ${e.end}`:'No dates supplied','date'),el('p',e.note));sourceLinks(e.source_ids,card);$('events').append(card);
  });
}
async function init() {
  try {
    const response=await fetch('content.json');if(!response.ok)throw new Error('content');state.data=await response.json();
    $('diet').onchange=renderList;document.querySelectorAll('input[name=exclude]').forEach(i=>i.onchange=renderList);
    $('flavour').onchange=renderSnack;
    $('reset').onclick=()=>{$('diet').value='all';$('flavour').value='gentle';document.querySelectorAll('input[name=exclude]').forEach(i=>i.checked=false);renderList();};
    $('rotate').oninput=()=>{$('plate').style.setProperty('--angle',$('rotate').value+'deg');$('angle').textContent=$('rotate').value+'°';};
    document.querySelectorAll('[data-mode]').forEach(b=>b.onclick=()=>{state.mode=b.dataset.mode;renderMode();});
    document.querySelectorAll('[data-scope]').forEach(b=>b.onclick=()=>{state.scope=b.dataset.scope;renderTraditions();});
    $('previous').onclick=()=>{state.step=Math.max(0,state.step-1);renderMode();};
    $('next').onclick=()=>{const s=state.data.snacks.find(x=>x.id===state.selected);if(s)state.step=Math.min(s.procedure.length-1,state.step+1);renderMode();};
    $('adult').onchange=()=>{$('heritage-content').hidden=!$('adult').checked;$('events').hidden=!$('adult').checked;$('event-gate').hidden=$('adult').checked;};
    state.data.research_backlog.forEach(b=>$('backlog').append(el('li',`${b.name} · ${b.region} — research candidate; source and local review pending.`)));
    state.data.chapter_mapping.liquor.forEach(c=>$('liquor-chapters').append(el('li',c.title)));
    state.data.chapter_mapping.bar.forEach(c=>$('bar-chapters').append(el('li',c.title)));
    state.data.sources.forEach(s=>{const li=el('li');sourceLinks([s.id],li);$('sources').append(li);});
    $('health-text').textContent=state.data.safety.health;sourceLinks(state.data.safety.health_source_ids,$('health-source'));
    renderList();renderTraditions();renderEvents();
    try {
      const status=await fetch('/api/status');const config=await status.json();
      if(status.ok&&config.status==='local_preview_planning_only'){
        $('local-integration').hidden=false;
        $('pairing-plan').onclick=async()=>{
          if(!$('adult').checked){$('pairing-plan-status').textContent='For an alcohol-related culture plan, first acknowledge the applicable local legal-age statement above. Food recipes remain available without this.';return;}
          $('pairing-plan').disabled=true;
          try {
            const response=await fetch('/api/plan',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({experience:'liquor-bar',topic_id:'overview',recipe_id:state.selected,mode:state.mode,diet:$('diet').value,exclude_allergens:[...document.querySelectorAll('input[name=exclude]:checked')].map(x=>x.value)})});
            const plan=await response.json();if(!response.ok)throw new Error(plan.error||'Plan unavailable.');
            const url=URL.createObjectURL(new Blob([JSON.stringify(plan,null,2)],{type:'application/json'}));const a=el('a');a.href=url;a.download='vyomaraj-jarvis-pairings-plan.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
            $('pairing-plan-status').textContent='Local plan downloaded. No AI call, publishing or DR action occurred.';
          }catch(e){$('pairing-plan-status').textContent=e.message;}finally{$('pairing-plan').disabled=false;}
        };
      }
    }catch(e){/* Standalone food preview remains usable without the integrated API. */}
  }catch(e){$('error').hidden=false;}
}
init();
