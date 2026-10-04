'use strict';
const $=id=>document.getElementById(id);
const state={data:null,followup:null,briefing:null,channel:'voice'};
function el(tag,text,cls){const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;}
function save(data,name){const u=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));const a=el('a');a.href=u;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(u),1000);}
const statusLabels={current:'current',due_soon:'due soon',overdue:'overdue',overdue_escalate:'overdue 14+ days'};
async function load(){try{const r=await fetch('content.json');if(!r.ok)throw new Error('Content');state.data=await r.json();
 const lr=await fetch('/api/finance/briefing',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({request:'followup_and_briefing'})});
 const plan=await lr.json();if(!lr.ok)throw new Error(plan.error||'Follow-up plan unavailable');
 state.followup=plan.followup;state.briefing=plan.briefing;
 $('totals').replaceChildren(
  el('span',`Payments tracked: ${plan.followup.totals.payments_tracked}`),
  el('span',`Pending: ₹${plan.followup.totals.pending_inr.toLocaleString('en-IN')}`),
  el('span',`Overdue: ₹${plan.followup.totals.overdue_inr.toLocaleString('en-IN')}`),
  el('span',`Escalations: ${plan.followup.totals.escalations}`));
 const wrap=$('payments');wrap.replaceChildren();
 for(const p of plan.followup.payments){const c=el('article',undefined,'card');
  c.append(el('span',`${statusLabels[p.status]} · ${p.days_late} day(s) late · next: ${p.next_action}`,'meta'),
   el('h3',p.platform),el('p',`₹${p.amount_inr.toLocaleString('en-IN')} · invoice ${p.invoice} · due ${p.due_date}`),
   el('p',p.draft.text,'small'));
  wrap.append(c);}
 const ladder=$('ladder-steps');ladder.replaceChildren();
 for(const step of state.data.reminder_ladder){const c=el('article',undefined,'ladder-step');
  c.append(el('span',`STAGE ${step.stage} · ${step.when}`,'meta'),el('h3',step.action.replace(/_/g,' ')),el('p',step.tone));ladder.append(c);}
 renderChannel();
 for(const tab of document.querySelectorAll('.tab'))tab.onclick=()=>{state.channel=tab.dataset.channel;for(const t of document.querySelectorAll('.tab'))t.setAttribute('aria-selected',String(t===tab));renderChannel();};
 $('download-briefing').disabled=false;$('briefing-status').textContent='Drafted locally. Nothing was sent.';
 $('download-briefing').onclick=()=>save({followup:state.followup,briefing:state.briefing},'vyomaraj-morning-briefing.json');
}catch(e){$('error').hidden=false;}}
function renderChannel(){const b=state.briefing;if(!b)return;const body=$('briefing-body');body.replaceChildren(el('p',b.headline,'headline'));
 const ch=b.channels[state.channel];
 if(state.channel==='voice')body.append(el('pre',ch.script));
 else if(state.channel==='email')body.append(el('p',`Subject: ${ch.subject}`,'strong'),el('pre',ch.body));
 else body.append(el('pre',ch.message));
 const ul=el('ul');for(const [name,lines] of Object.entries(b.sections)){ul.append(el('li',`${name.replace(/_/g,' ')}: ${lines.join(' | ')}`));}
 body.append(el('p','SECTIONS','eyebrow'),ul);}
load();
