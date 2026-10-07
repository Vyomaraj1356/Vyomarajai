/*
 * Vyomaraj Reel Sprint — deterministic, local-only planning templates.
 * No network requests, analytics, storage, model calls, or publishing.
 */
(function (root) {
  'use strict';

  const MAX_LENGTH = 280;
  const SAMPLE_BRIEF = Object.freeze({
    businessName: 'Vyomaraj Demo Café',
    businessType: 'café',
    area: 'Pune — sample area',
    audience: 'people looking for a quiet coffee break',
    offer: 'filter coffee and a quiet reading corner',
    goal: 'visits',
    tone: 'warm and welcoming',
    cta: 'Check current details before visiting',
    facts: '',
    sources: ''
  });
  const WARNING_PATTERNS = [
    { pattern: /\b(best|number one|#1|no\. ?1|guaranteed|guarantee|cure|cures|heals|miracle|miracles|100%|risk.free)\b/i, label: 'Possible absolute, health, or guaranteed-result claim: verify with reliable evidence or remove.' },
    { pattern: /\b(cheapest|lowest price|most popular|award.winning|certified|organic|doctor.recommended)\b/i, label: 'Possible comparative, certification, or endorsement claim: verify permission and supporting evidence.' }
  ];

  const ANGLES = [
    {
      name: 'A closer look',
      goal: 'Awareness',
      hook: (v) => `A closer look at ${v.name}${v.area ? ` in ${v.area}` : ''}.`,
      voice: (v) => `Meet ${v.name}, a ${v.type}. ${v.offer}`,
      shots: ['Open with the storefront or a welcoming establishing shot.', 'Show one real detail of the offer.', 'End on the finished experience or space.'],
      caption: (v) => `${v.name}: ${v.offer} ${v.area ? `Find us in ${v.area}. ` : ''}${v.cta}`
    },
    {
      name: 'Behind the scenes',
      goal: 'Connection',
      hook: (v) => `Take a short look behind the scenes at ${v.name}.`,
      voice: (v) => `Show the real people, process, and small details behind ${v.offer} at ${v.name}. Keep every shot authentic to the team and the place.`,
      shots: ['Ask permission before filming staff or guests.', 'Capture one genuine preparation or service moment.', 'Finish with the actual item, service, or experience being offered.'],
      caption: (v) => `A little behind-the-scenes look at ${v.name}. ${v.cta}`
    },
    {
      name: 'Helpful FAQ',
      goal: 'Consideration',
      hook: (v) => `Considering ${v.name}? Here is a simple way to show what to expect.`,
      voice: (v) => `At ${v.name}, introduce ${v.offer}. Add one approved detail about timing, price, ingredients, access, or booking only if the business has verified it.`,
      shots: ['Show the question as on-screen text.', 'Answer with one business-approved fact, or leave the answer as a human-edit prompt.', 'Close with a clear way to ask the business a question.'],
      caption: (v) => `A quick guide to ${v.name}. Add current, verified details before posting. ${v.cta}`
    },
    {
      name: 'A local invitation',
      goal: 'Action',
      hook: (v) => `${v.audience}: looking for something new to try?`,
      voice: (v) => `${v.name} is sharing ${v.offer}. If it fits your plans, ${v.cta.toLowerCase()}.`,
      shots: ['Show the outside or a clear way to recognize the venue.', 'Show the offer as it is actually served or delivered.', "Finish with the business name and the owner's approved next step."],
      caption: (v) => `${v.audience}, save this idea for later. ${v.name} — ${v.offer} ${v.cta}`
    }
  ];

  function clean(value, fallback) {
    const text = String(value == null ? '' : value).trim().slice(0, MAX_LENGTH);
    return text || fallback;
  }

  function lines(value) {
    return String(value || '').split(/\r?\n/).map((line) => line.trim()).filter(Boolean).slice(0, 8);
  }

  function generateCampaign(input) {
    const v = {
      name: clean(input.businessName, 'Your business'),
      type: clean(input.businessType, 'small business'),
      area: clean(input.area, ''),
      audience: clean(input.audience, 'your local audience'),
      offer: clean(input.offer, 'your offer'),
      goal: clean(input.goal, 'visits'),
      tone: clean(input.tone, 'warm and welcoming'),
      cta: clean(input.cta, 'Ask the business for current details'),
      facts: lines(input.facts),
      sources: lines(input.sources)
    };

    const rawClaims = `${v.offer}\n${v.facts.join('\n')}`;
    const warnings = WARNING_PATTERNS.filter((entry) => entry.pattern.test(rawClaims)).map((entry) => entry.label);
    const sourceStatus = v.facts.length
      ? 'Owner-supplied facts are included for review; this planner has not independently checked them.'
      : 'No approved facts supplied. Keep the reel descriptive; do not add rankings, health, price, origin, or performance claims.';

    const reels = ANGLES.map((angle, index) => ({
      number: index + 1,
      title: angle.name,
      goal: angle.goal,
      hook: angle.hook(v),
      voiceover: angle.voice(v),
      tone: v.tone,
      duration: '20–30 seconds',
      shots: angle.shots,
      caption: angle.caption(v),
      cta: v.cta,
      review: sourceStatus,
      facts: v.facts,
      sources: v.sources,
      warnings
    }));

    const calendar = [
      'Day 1 — A closer look',
      'Day 3 — Behind the scenes',
      'Day 5 — Helpful FAQ',
      'Day 7 — A local invitation'
    ];
    return {
      businessName: v.name,
      businessType: v.type,
      area: v.area,
      audience: v.audience,
      offer: v.offer,
      goal: v.goal,
      calendar,
      reels,
      warnings,
      evidenceNote: sourceStatus,
      demo: input.demo === true,
      rightsNote: 'Use only original or licensed footage, music, logos, and likenesses. Get permission before filming identifiable staff or guests.',
      status: 'Template draft — human review required. Not generated by an AI model; not fact-checked or posted.'
    };
  }

  function make(tag, className, text) {
    const el = document.createElement(tag);
    if (className) el.className = className;
    if (text != null) el.textContent = text;
    return el;
  }

  function addSection(parent, heading, content, wide) {
    const section = make('section', `reel-section${wide ? ' wide' : ''}`);
    section.appendChild(make('h4', '', heading));
    if (Array.isArray(content)) {
      const list = make('ul');
      content.forEach((item) => list.appendChild(make('li', '', item)));
      section.appendChild(list);
    } else {
      section.appendChild(make('p', '', content));
    }
    parent.appendChild(section);
  }

  function renderCampaign(campaign, output) {
    output.replaceChildren();
    if (campaign.demo) {
      output.appendChild(make('p', 'demo-banner', 'FICTIONAL DEMO — Vyomaraj Demo Café and its offer are invented for testing. This is not a real client, endorsement, or performance result.'));
    }
    campaign.reels.forEach((reel) => {
      const card = make('article', 'reel-card');
      const head = make('div', 'reel-card-head');
      const label = make('div', 'reel-number');
      label.appendChild(make('span', 'number-chip', String(reel.number).padStart(2, '0')));
      label.appendChild(make('h3', '', reel.title));
      head.appendChild(label);
      head.appendChild(make('span', 'goal-chip', reel.goal));
      card.appendChild(head);

      const body = make('div', 'reel-body');
      addSection(body, 'Opening hook · 0–3s', reel.hook, true);
      addSection(body, 'Voiceover / on-screen copy', reel.voiceover, true);
      addSection(body, 'Shot plan', reel.shots, false);
      addSection(body, 'Caption', reel.caption, false);
      addSection(body, 'Call to action', reel.cta, false);
      addSection(body, 'Format & voice', `${reel.duration} · ${reel.tone}`, false);
      card.appendChild(body);
      card.appendChild(make('p', 'evidence-callout', reel.review));
      if (reel.warnings.length) card.appendChild(make('p', 'evidence-callout', reel.warnings.join(' ')));
      output.appendChild(card);
    });
  }

  function campaignText(campaign) {
    const chunks = [
      ...(campaign.demo ? ['FICTIONAL DEMO — this business and offer are invented; do not present as a real customer or result.', ''] : []),
      'VYOMARAJ REEL SPRINT — CAMPAIGN PLAN',
      `${campaign.businessName}${campaign.area ? ` · ${campaign.area}` : ''}`,
      `Audience: ${campaign.audience}`,
      `Offer: ${campaign.offer}`,
      '',
      'ONE-WEEK CALENDAR',
      ...campaign.calendar,
      '',
      'FOUR REEL BRIEFS'
    ];
    campaign.reels.forEach((reel) => {
      chunks.push('', `${String(reel.number).padStart(2, '0')} · ${reel.title} (${reel.goal})`);
      chunks.push(`Hook: ${reel.hook}`, `Voiceover: ${reel.voiceover}`, `Shots: ${reel.shots.join(' | ')}`);
      chunks.push(`Caption: ${reel.caption}`, `CTA: ${reel.cta}`, `Review: ${reel.review}`);
      if (reel.facts.length) chunks.push(`Owner-supplied facts (not independently verified): ${reel.facts.join(' | ')}`);
      if (reel.sources.length) chunks.push(`Source notes (not checked by tool): ${reel.sources.join(' | ')}`);
      if (reel.warnings.length) chunks.push(`Claim warning: ${reel.warnings.join(' ')}`);
    });
    chunks.push('', 'RIGHTS CHECK', campaign.rightsNote, '', 'STATUS', campaign.status);
    return chunks.join('\n');
  }

  function safeFilename(value) {
    return String(value || 'campaign').normalize('NFKD').replace(/[^a-zA-Z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 48).toLowerCase() || 'campaign';
  }

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { generateCampaign, campaignText, safeFilename, SAMPLE_BRIEF };
  }

  if (typeof document === 'undefined') return;
  const form = document.getElementById('campaign-form');
  if (!form) return;
  const sampleButton = document.getElementById('sample-button');
  const output = document.getElementById('campaign-output');
  const empty = document.getElementById('empty-state');
  const review = document.getElementById('review-note');
  const exportActions = document.getElementById('export-actions');
  const clearButton = document.getElementById('clear-button');
  let currentCampaign = null;

  sampleButton.addEventListener('click', () => {
    Object.entries(SAMPLE_BRIEF).forEach(([name, value]) => {
      const field = form.elements.namedItem(name);
      if (field) field.value = value;
    });
    form.dataset.demo = 'true';
    form.requestSubmit();
  });

  const clearDemoLabel = () => { delete form.dataset.demo; };
  form.addEventListener('input', clearDemoLabel);
  form.addEventListener('change', clearDemoLabel);

  form.addEventListener('submit', (event) => {
    event.preventDefault();
    if (!form.reportValidity()) return;
    const data = Object.fromEntries(new FormData(form).entries());
    data.demo = form.dataset.demo === 'true';
    currentCampaign = generateCampaign(data);
    renderCampaign(currentCampaign, output);
    empty.hidden = true;
    review.hidden = false;
    exportActions.hidden = false;
  });

  clearButton.addEventListener('click', () => {
    form.reset();
    delete form.dataset.demo;
    output.replaceChildren();
    currentCampaign = null;
    empty.hidden = false;
    review.hidden = true;
    exportActions.hidden = true;
    document.getElementById('business-name').focus();
  });

  document.getElementById('download-button').addEventListener('click', () => {
    if (!currentCampaign) return;
    const blob = new Blob([campaignText(currentCampaign)], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `vyomaraj-reel-plan-${safeFilename(currentCampaign.businessName)}.txt`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  });

  document.getElementById('print-button').addEventListener('click', () => window.print());
})(typeof globalThis !== 'undefined' ? globalThis : this);
