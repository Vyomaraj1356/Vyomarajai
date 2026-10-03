'use strict';
const $=id=>document.getElementById(id),el=(tag,txt,cls)=>{const n=document.createElement(tag);if(txt!==undefined)n.textContent=txt;if(cls)n.className=cls;return n;};
let registry,index,ownership;
function slot(a){const n=el('div',undefined,'slot'+(a.name?' named':''));n.dataset.agentId=a.id;n.append(el('span',String(a.serial),'serial'));if(a.name)n.append(el('span',a.name,'agent-name'));n.setAttribute('aria-label',`Position ${a.serial}${a.name?' '+a.name:''}`);if($('ids').checked){n.append(el('span',a.id,'audit-id'));if(a.source_reported_chapter_count)n.append(el('span',`${a.source_reported_chapter_count} source-reported chapters; titles not inferred`,'chapters'));}return n;}
function render(){
 const filter=$('category').value,q=$('search').value.trim().toLocaleLowerCase().replace(/\bgovt\b/g,'government'),show=c=>filter==='all'||filter===c.id;
 const matches=(a,c)=>!q||[a.name||'',c.name,c.id,...registry.headings.filter(h=>h.id===a.parent_id).map(h=>h.name),...ownership.education_topics.filter(t=>t.slot_id===a.id).map(t=>t.title)].some(s=>s.toLocaleLowerCase().includes(q));
 $('roster').replaceChildren();let count=0;
 for(const c of registry.categories.filter(show)){
  const agents=registry.agents.filter(a=>a.category_id===c.id&&matches(a,c));if(!agents.length)continue;count+=agents.length;
  const section=el('details',undefined,'category');section.dataset.category=c.id;section.open=filter!=='all'||!!q;
  const summary=el('summary');summary.append(el('h3',c.name),el('span',`${c.sub_agents} counted slots${c.headings?' · '+c.headings+' uncounted headings':''}`));section.append(summary);
  const body=el('div',undefined,'category-body');const direct=el('div',undefined,'slots');for(const a of agents.filter(a=>a.parent_id===c.id))direct.append(slot(a));if(direct.childNodes.length)body.append(direct);
  for(const h of registry.headings.filter(h=>h.category_id===c.id)){
   const children=agents.filter(a=>a.parent_id===h.id);if(!children.length)continue;
   const group=el('div',undefined,'group');group.dataset.headingId=h.id;const heading=el('h4',h.name);heading.append(el('small','Parent heading only · not an extra agent'));group.append(heading);
   const slots=el('div',undefined,'slots');for(const a of children)slots.append(slot(a));group.append(slots);body.append(group);
  }
  if(c.id==='EDU')body.append(el('p','Positions 8–13 share the source group label “Bharat Grantha, Chanakya and the Granthas”. Individual names and content assignments remain unassigned.','small'));
  if(c.id==='PLATFORM')body.append(el('p','Display position 20 is only a serial. Its historical source slot remains unmapped; this does not assign it to S20.','small'));
  section.append(body);$('roster').append(section);
 }
 $('status').textContent=`${count} matching counted positions. Headings are excluded; names have not been invented.`;
 $('topics').replaceChildren();const topics=index.records.filter(r=>(filter==='all'||r.owner_category===filter)&&(!q||r.title.toLocaleLowerCase().includes(q)||r.owner_category.toLocaleLowerCase().includes(q)||registry.categories.find(c=>c.id===r.owner_category).name.toLocaleLowerCase().includes(q)));
 $('content-title').textContent=filter==='EDU'?'Education, in its own place.':'The reference index.';$('content-count').textContent=topics.length+' references';
 for(const r of topics){
  const card=el('article',undefined,'topic');card.dataset.owner=r.owner_category;card.dataset.topicId=r.id;
  card.append(el('p',registry.categories.find(c=>c.id===r.owner_category).name+' / REFERENCE','eyebrow'),el('h3',r.title));
  const educational=ownership.education_topics.find(t=>t.id===r.id);if(educational)card.append(el('p',educational.summary));
  const details=el('details'),sum=el('summary','Source metadata');details.append(sum);
  for(const ref of r.source_refs)details.append(el('p',ref.path+' · '+ref.locator));
  details.append(el('p','Reference only. Not a recovered full text, a new agent or verified scheme advice.'));card.append(details);$('topics').append(card);
 }
}
async function load(){try{
 [registry,index,ownership]=await Promise.all(['AGENT_REGISTRY_CURRENT.json','CONTENT_INDEX_CURRENT.json','CONTENT_OWNERSHIP_CURRENT.json'].map(async name=>{const r=await fetch('/agents/'+name);if(!r.ok)throw new Error('Metadata unavailable');return r.json();}));
 for(const c of registry.categories){const o=el('option',c.name+' ('+c.sub_agents+')');o.value=c.id;$('category').append(o);}
 if(location.pathname.startsWith('/education/')){$('category').value='EDU';$('hero-title').replaceChildren(el('span','Education.'),el('br'),el('em','Knowledge, with a clear home.'));$('hero-copy').textContent='Sixteen positions, including Government Schemes. Existing educational topics now have one explicit owner: Education. Six shared Grantha positions remain numbered and unnamed.';document.title='Education · Vyomaraj';}
 $('category').addEventListener('change',render);$('search').addEventListener('input',render);$('ids').addEventListener('change',render);render();
 }catch(e){$('status').textContent='Current directory unavailable. Please reload; no substitute roster has been invented.';}}
load();
