'use strict';
const $ = id => document.getElementById(id);
const state = {queue: null, review: null, decision: null};
function el(tag, text, cls) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (cls) node.className = cls;
  return node;
}
function save(data, name) {
  const url = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'}));
  const link = el('a'); link.href = url; link.download = name; link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
function setShutter(open) {
  $('shutter-art').classList.toggle('open', open);
  $('lens-note').textContent = open ? 'SHUTTER OPEN · REVIEW PLAYING' : 'SHUTTER CLOSED · PICK FROM THE QUEUE';
}
function errorMessage(data) {
  if (data?.required) {
    return `No decision was stored. Obtain a short-lived signed owner token for action ${data.required.action}, scope ${data.required.scope}, target ${data.required.target}; paste it below and retry. The issuer must be configured outside this application.`;
  }
  return data?.detail || data?.error || 'Request unavailable.';
}
async function loadQueue() {
  try {
    const response = await fetch('/api/approvals/queue', {cache: 'no-store'});
    const data = await response.json();
    if (!response.ok) throw new Error(errorMessage(data));
    state.queue = data;
    const awaiting = data.queue.filter(item => item.status === 'awaiting_owner');
    const select = $('queue-select');
    select.replaceChildren(el('option', '— pick an item to open the shutter —'));
    for (const item of awaiting) {
      const option = el('option', `${item.title} · ${item.lane}`);
      option.value = item.id; select.append(option);
    }
    $('queue-status').textContent = awaiting.length
      ? `${awaiting.length} item(s) awaiting the owner. ${data.notifications.policy}. Publishing gate: ${data.publishing.gate}. Local audit events: ${data.audit.event_count}; integrity ${data.audit.integrity_verified ? 'verified' : 'FAILED'}.`
      : 'Queue is empty.';
    select.onchange = () => { if (select.value) openReview(select.value); else closeReview(); };
  } catch (error) {
    $('queue-status').textContent = `Approval service unavailable: ${error.message}`;
    for (const button of document.querySelectorAll('.decision-buttons button')) button.disabled = true;
  }
}
function closeReview() {
  $('camera').hidden = true; state.review = null; state.decision = null;
  $('download-decision').hidden = true; setShutter(false);
}
async function openReview(id) {
  try {
    const response = await fetch(`/api/approvals/review/${encodeURIComponent(id)}`, {cache: 'no-store'});
    const review = await response.json();
    if (!response.ok) throw new Error(errorMessage(review));
    state.review = review.item; state.decision = null;
    $('download-decision').hidden = true; $('decision-status').textContent = '';
    $('owner-approval-token').value = '';
    $('camera').hidden = false;
    $('review-title').textContent = review.item.title;
    $('review-meta').textContent = `Lane: ${review.item.lane} · Languages: ${review.item.languages.join(', ')} · Version line: ${review.item.version_line}`;
    $('review-lane').textContent = `${review.item.lane.toUpperCase()} · LOCAL REVIEW PAYLOAD · AWAITING OWNER`;
    $('video-note').textContent = 'VIDEO — ' + review.review_payload.video_note;
    $('sound-note').textContent = 'SOUND — ' + review.review_payload.sound_note;
    $('review-desc').textContent = review.review_payload.description;
    $('review-duration').textContent = `REVIEW PAYLOAD · ~${review.review_payload.duration_seconds}s DESCRIBED · NO MEDIA HOSTED`;
    setShutter(true); $('camera').scrollIntoView({behavior: 'smooth'});
    for (const button of document.querySelectorAll('.decision-buttons button')) button.disabled = false;
  } catch (error) {
    $('decision-status').textContent = `Review unavailable: ${error.message}`;
  }
}
async function decide(decision) {
  if (!state.review) return;
  $('decision-status').textContent = 'Verifying the one-time owner decision…';
  for (const button of document.querySelectorAll('.decision-buttons button')) button.disabled = true;
  const token = $('owner-approval-token').value.trim();
  $('owner-approval-token').value = '';
  const body = {item_id: state.review.id, decision, voice_instruction: $('voice-instruction').value || null};
  const headers = {'Content-Type': 'application/json'};
  if (token) headers.Authorization = `Bearer ${token}`;
  try {
    const response = await fetch('/api/approvals/decide', {method: 'POST', headers, body: JSON.stringify(body)});
    const record = await response.json();
    if (!response.ok) throw new Error(errorMessage(record));
    state.decision = record;
    $('decision-status').textContent = `Decision stored locally: ${decision.toUpperCase()} — ${record.outcome}. ${record.cycle} Audit event ${record.persistence.audit_event_id}; not published.`;
    $('download-decision').hidden = false; setShutter(false);
    await loadQueue(); $('queue-select').value = '';
  } catch (error) {
    $('decision-status').textContent = error.message;
  } finally {
    for (const button of document.querySelectorAll('.decision-buttons button')) button.disabled = false;
  }
}
function init() {
  $('download-decision').onclick = () => {
    if (state.decision) save(state.decision, 'vyomaraj-owner-decision.json');
  };
  for (const [id, decision] of [['decide-approve', 'approve'], ['decide-reject', 'reject'],
                                 ['decide-rework', 'rework'], ['decide-submit', 'submit']]) {
    $(id).onclick = () => decide(decision);
  }
  loadQueue();
}
init();
