'use strict';
const $=id=>document.getElementById(id);
const state={data:null,record:null,final:null};
function el(tag,text,cls){const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;}
function save(data,name){const u=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));const a=el('a');a.href=u;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(u),1000);}
async function load(){try{const r=await fetch('content.json');if(!r.ok)throw new Error('Content');state.data=await r.json();
 const list=$('sample-list');list.replaceChildren();
 for(const s of state.data.sample_instructions){const b=el('button',s.instruction,'sample');b.onclick=()=>{$('instruction').value=s.instruction;$('kind').value=s.kind;$('lanes').value=s.affected_lanes.join(', ');updatePlanButton();};list.append(b);}
 const steps=$('lifecycle-steps');steps.replaceChildren();
 for(const [n,step] of state.data.policy && [['1','Instruction — local proposal only'],['2','Alignment — verified owner approval required'],['3','Coordination — agents listed for review; none contacted'],['4','Version control — proposed branch name; not created'],['5','Separate testing — plan listed; tests not run by this desk'],['6','Permission — action-bound signed owner token required'],['7','Upgrade — blocked; no runtime adapter is configured'],['8','Failure — rollback recommendation only; not executed']]){const c=el('article',undefined,'life-step');c.append(el('span','STEP '+n,'meta'),el('h3',step.split(' — ')[0]),el('p',step));steps.append(c);}
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
  $('record-meta').textContent=`${record.kind} · proposed branch name ${record.version_control.branch} (not created) · ${record.permission_gate.status}`;
  const body=$('record-body');body.replaceChildren();
  body.append(block('AUTHORITY CHAIN',[`${record.authority_chain.owner}`,record.authority_chain.alignment,'Arena: '+record.authority_chain.arena_role]),
   block('COORDINATION',['Coordinators: '+record.coordination.coordinators.join(' + '),'Affected: '+(record.coordination.affected_agents.join(', ')||'all agents')]),
   block('VERSION CONTROL',[record.version_control.branch,record.version_control.rule]),
   block('SEPARATE TESTING',record.testing_plan.map(t=>`Stage ${t.stage} — ${t.name}: ${t.rule} (${t.result})`)),
   block('UPGRADE PLAN',record.upgrade_plan.steps),
   block('PROPOSED ROLLBACK CHECKLIST — NOT EXECUTABLE HERE',[record.rollback_plan.backup_first+'; '+record.rollback_plan.action,record.rollback_plan.data]));
  $('decision-status').textContent='';$('download-record').hidden=false;
  $('record').scrollIntoView({behavior:'smooth'});
  $('plan-status').textContent='Change planned. Nothing is applied — your permission is the gate.';
 }catch(e){$('plan-status').textContent=e.message;}}
function block(title,lines){const b=el('div',undefined,'record-block');b.append(el('p',title,'eyebrow'));for(const line of lines)b.append(el('p',line));return b;}
function takeOwnerToken(){const input=$('owner-approval-token');const token=input.value.trim();input.value='';return token;}
function ownerError(body){const required=body.required;return required?`No change was made. Obtain a one-time owner token for ${required.action}, scope ${required.scope}, target ${required.target}. The trusted issuer must be configured out of band.`:(body.detail||body.error||'Decision unavailable');}
async function decide(decision){if(!state.record)return;$('decision-status').textContent='Verifying the action-bound owner decision…';
 try{const token=takeOwnerToken(),headers={'Content-Type':'application/json'};if(token)headers.Authorization=`Bearer ${token}`;
  const r=await fetch('/api/upgrades/plan',{method:'POST',headers,body:JSON.stringify({record:state.record,decision})});
  const out=await r.json();if(!r.ok)throw new Error(ownerError(out));state.final=out;
  $('decision-status').textContent=`Owner decision verified for the plan only. Status: ${out.status}. No durable upgrade record, branch, schedule, runtime change or publication was created.`;
 }catch(e){$('decision-status').textContent=e.message;}}
async function simulateFailure(){if(!state.final||state.final.status!=='owner_approved_change_plan_not_applied'){$('decision-status').textContent='First obtain a verified owner approval for this plan. No simulated rollback is available.';return;}
 $('decision-status').textContent='Preparing a rollback recommendation only…';
 try{const token=takeOwnerToken(),headers={'Content-Type':'application/json'};if(token)headers.Authorization=`Bearer ${token}`;
  const body={record:state.final,failure:'post-upgrade verification'};
  const r=await fetch('/api/upgrades/plan',{method:'POST',headers,body:JSON.stringify(body)});
  const out=await r.json();if(!r.ok)throw new Error(ownerError(out));state.final=out;
  $('decision-status').textContent=`${out.status}. No rollback or service action was executed. Business impact remains unknown; verify with the actual operator.`;
 }catch(e){$('decision-status').textContent=e.message;}}
load();
