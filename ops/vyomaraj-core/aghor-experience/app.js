'use strict';
const $=id=>document.getElementById(id),el=(tag,txt,cls)=>{const n=document.createElement(tag);if(txt!==undefined)n.textContent=txt;if(cls)n.className=cls;return n;};
let data;
function refs(ids,parent){for(const id of ids){const s=data.sources.find(s=>s.id===id);const a=el('a',s.title+' ↗','source-link');a.href=s.url;a.target='_blank';a.rel='noopener noreferrer';parent.append(a);}}
function card(item,title,tag,css){const c=el('article',undefined,'topic '+css);c.append(el('p',tag,'eyebrow'),el('h3',title),el('p',item.summary));refs(item.source_ids,c);return c;}
function chapters(){ $('chapter-list').replaceChildren();for(const [i,x] of data.chapters.entries()){if($('lens').value!=='all'&&x.classification!==$('lens').value)continue;$('chapter-list').append(card(x,`${i+1}. ${x.title}`,x.classification+' · PROPOSED · VIEW ONLY','chapter'));}}
function people(){ $('people').replaceChildren();for(const x of data.people){if($('era').value!=='all'&&x.era!==$('era').value)continue;const c=card(x,x.name,x.era,'person');c.append(el('p',x.evidence_status,'small'));$('people').append(c);}}
async function init(){try{const r=await fetch('/aghor/content.json');if(!r.ok)throw new Error();data=await r.json();
 for(const [select,values] of [['lens',data.chapters.map(x=>x.classification)],['era',data.people.map(x=>x.era)]])for(const v of new Set(values)){const o=el('option',v);o.value=v;$(select).append(o);}
 $('lens').onchange=chapters;$('era').onchange=people;chapters();people();
 for(const x of data.timeline){const c=el('article');c.append(el('h3',x.period),el('p',x.summary));refs(x.source_ids,c);$('timeline').append(c);}
 for(const x of data.practices){const c=card(x,x.title,x.kind,'practice');c.append(el('p','Entertainment and view only. No procedure supplied.','small'));$('practices').append(c);}
 for(const x of data.care){const c=card(x,x.title,'GENERAL INFORMATION · NOT A DIAGNOSIS','care-card');const list=el('ul');for(const step of x.safe_next_steps)list.append(el('li',step));c.append(list);$('care-list').append(c);}
 for(const x of data.sources){const c=el('article');const a=el('a',x.title+' ↗');a.href=x.url;a.target='_blank';a.rel='noopener noreferrer';c.append(a,el('p',x.source_type+' · '+x.review_basis));$('sources').append(c);}
 for(const rule of data.editorial_rules)$('rules').append(el('li',rule));
 }catch(e){$('error').hidden=false;}}
init();
