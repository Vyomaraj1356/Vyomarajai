'use strict';
const assert = require('node:assert/strict');
const { generateCampaign, campaignText, safeFilename, SAMPLE_BRIEF } = require('../products/vyomaraj-reel-sprint/app.js');

const plan = generateCampaign({
  businessName: 'Aundh Corner Café',
  businessType: 'café',
  area: 'Aundh',
  audience: 'people looking for a calm coffee break',
  offer: 'filter coffee and a quiet reading corner',
  goal: 'visits',
  tone: 'warm and welcoming',
  cta: 'Check today’s hours before visiting',
  facts: 'Open from 9 am to 8 pm',
  sources: 'https://example.invalid/hours'
});

assert.equal(plan.reels.length, 4, 'campaign must have exactly four briefs');
assert.equal(plan.calendar.length, 4, 'campaign calendar must contain four entries');
assert.deepEqual(plan.reels.map((item) => item.title), [
  'A closer look', 'Behind the scenes', 'Helpful FAQ', 'A local invitation'
]);
assert.ok(plan.reels.every((item) => item.voiceover.includes('Aundh Corner Café')));
assert.ok(plan.evidenceNote.includes('not independently checked'));
assert.ok(plan.rightsNote.includes('licensed'));

const demo = generateCampaign({ ...SAMPLE_BRIEF, demo: true });
assert.equal(demo.demo, true);
assert.ok(campaignText(demo).startsWith('FICTIONAL DEMO'));
assert.equal(demo.businessName, 'Vyomaraj Demo Café');

const risky = generateCampaign({
  businessName: 'Test Café',
  audience: 'local residents',
  offer: 'the best guaranteed cure for stress',
  facts: '',
  sources: ''
});
assert.ok(risky.warnings.length >= 1, 'unsupported absolute/health claims should trigger a warning');
assert.ok(risky.evidenceNote.includes('No approved facts supplied'));

const hostile = generateCampaign({
  businessName: '<img src=x onerror=alert(1)>',
  audience: 'test audience',
  offer: '<script>alert(1)</script>',
  cta: 'Visit'
});
assert.ok(campaignText(hostile).includes('<script>alert(1)</script>'));
assert.equal(safeFilename('Aundh Corner Café'), 'aundh-corner-cafe');
assert.equal(safeFilename('../../'), 'campaign');
console.log('Reel Sprint tests passed: 4-angle output, evidence labels, claim warning, export and safe filename.');
