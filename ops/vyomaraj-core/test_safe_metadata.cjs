const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
function load(filename) {
  const context = { window: {} };
  vm.runInNewContext(fs.readFileSync(path.join(__dirname, filename), 'utf8'), context);
  return context.window;
}
test('coordination has no fabricated health or automatic actions', () => {
  const api = load('multi-ai-coordination.js').VyomarajCoordination;
  const health = api.getHealth();
  assert.equal(health.operational, false);
  assert.equal(health.currentLoad, null);
  assert.ok(health.platforms.every(p => p.status === 'UNVERIFIED' && p.load === null));
  assert.equal(api.switchPlatform().status, 'BLOCKED');
  assert.equal(api.shareLoadWith(['chatgpt']).status, 'BLOCKED');
  assert.equal(api.detectOverload().status, 'UNKNOWN');
});
test('coordination snapshots cannot mutate platform declarations', () => {
  const api = load('multi-ai-coordination.js').VyomarajCoordination;
  api.getHealth().platforms[0].status = 'LIVE';
  assert.equal(api.getHealth().platforms[0].status, 'UNVERIFIED');
});
test('Shriyantra is branding, not a security implementation', () => {
  const symbol = load('shriyantra-protection.js').Shriyantra;
  assert.equal(symbol.mode, 'branding_only');
  assert.equal(symbol.protection.status, 'NOT_IMPLEMENTED');
  assert.ok(Object.isFrozen(symbol.protection));
});
