'use strict';
const $=id=>document.getElementById(id);
const state={data:null,record:null,final:null};
function el(tag,text,cls){const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;}
function save(data,name){const u=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));const a=el('a');a.href=u;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(u),1000);}
async function load(){try{const r=await fetch('content.json');if(!r.ok)throw new Error('Content');state.data=await r.json();
 const list=$('sample-list');list.replaceChildren();
 for(const s of state.data.sample_instructions){const b=el('button',s.instruction,'sample');b.onclick=()=>{$('instruction').value=s.instruction;$('kind').value=s.kind;$('lanes').value=s.affected_lanes.join(', ');updatePlanButton();};list.append(b);}
 const steps=$('lifecycle-steps');steps.replaceChildren();
 for(const [n,step] of state.data.policy && [['1','Instruction — owner only, through ShriYantra'],['2','Alignment — Vyomaraj & Jarvis align with ShriYantra'],['3','Coordination — all affected agents informed'],['4','Version control — change branch, no history deleted'],['5','Separate testing — stages 1–4 checked and recorded'],['6','Permission — PENDING_OWNER_PERMISSION gate'],['7','Upgrade — snapshot first, apply, verify health'],['8','Failure — backup plan: rollback, current version continues']]){const c=el('article',undefined,'life-step');c.append(el('span','STEP '+n,'meta'),el('h3',step.split(' — ')[0]),el('p',step));steps.append(c);}
 $('instruction').oninput=updatePlanButton;
 $('plan-change').onclick=planChange;$('approve-change').onclick=()=>decide('approve');$('reject-change').onclick=()=>decide('reject');
 $('simulate-failure').onclick=simulateFailure;$('download-record').onclick=()=>{if(state.final)save(state.final,'vyomaraj-change-record.json');};
 updatePlanButton();
}catch(e){$('error').hidden=false;}}
function updatePlanButton(){$('plan-change').disabled=!($('instruction').value.trim().length>=5);}
async function planChange(){$('plan-status').textContent='Vyomaraj and Jarvis are aligning with ShriYantra…';
 try{const lanes=$('lanes').value.split(',').map(s=>s.trim()).filter(Boolean);
  const r=await fetch('/api/upgrades/plan',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({instruction:$('instruction').value.trim(),kind:$('kind').value,affected_lanes:lanes})});
  const record=await r.json();if(!r.ok)throw new Error(record.error||'Change plan unavailable');state.record=record;state.final=record;
  $('record').hidden=false;$('record-title').textContent=record.change_id;
  $('record-meta').textContent=`${record.kind} · branch ${record.version_control.branch} · ${record.permission_gate.status}`;
  const body=$('record-body');body.replaceChildren();
  body.append(block('AUTHORITY CHAIN',[`${record.authority_chain.owner}`,record.authority_chain.alignment,'Arena: '+record.authority_chain.arena_role]),
   block('COORDINATION',['Coordinators: '+record.coordination.coordinators.join(' + '),'Affected: '+(record.coordination.affected_agents.join(', ')||'all agents')]),
   block('VERSION CONTROL',[record.version_control.branch,record.version_control.rule]),
   block('SEPARATE TESTING',record.testing_plan.map(t=>`Stage ${t.stage} — ${t.name}: ${t.rule} (${t.result})`)),
   block('UPGRADE PLAN',record.upgrade_plan.steps),
   block('ROLLBACK PLAN — ALWAYS READY',[record.rollback_plan.backup_first+'; '+record.rollback_plan.action,record.rollback_plan.data]));
  $('decision-status').textContent='';$('download-record').hidden=false;
  $('record').scrollIntoView({behavior:'smooth'});
  $('plan-status').textContent='Change planned. Nothing is applied — your permission is the gate.';
 }catch(e){$('plan-status').textContent=e.message;}}
function block(title,lines){const b=el('div',undefined,'record-block');b.append(el('p',title,'eyebrow'));for(const line of lines)b.append(el('p',line));return b;}
async function decide(decision){if(!state.record)return;$('decision-status').textContent='Recording the owner decision…';
 try{const r=await fetch('/api/upgrades/plan',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({record:state.record,decision})});
  const out=await r.json();if(!r.ok)throw new Error(out.error||'Decision unavailable');state.final=out;
  $('decision-status').textContent=`${decision==='approve'?'Approved — upgrade scheduled with rollback ready.':'Rejected — not applied; the current version continues.'} Status: ${out.status}. Nothing was applied to any live system.`;
 }catch(e){$('decision-status').textContent=e.message;}}
async function simulateFailure(){if(!state.record)return;$('decision-status').textContent='Verification failed — engaging the backup plan…';
 try{const approved=await (await fetch('/api/upgrades/plan',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({record:state.record,decision:'approve'})})).json();
  const r=await fetch('/api/upgrades/plan',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({record:approved,failure:'post-upgrade verification'})});
  const out=await r.json();if(!r.ok)throw new Error(out.error||'Failure report unavailable');state.final=out;
  $('decision-status').textContent=`Backup plan engaged: rolled back to the snapshot; the current version continues. ${out.business_impact}`;
 }catch(e){$('decision-status').textContent=e.message;}}
load();
