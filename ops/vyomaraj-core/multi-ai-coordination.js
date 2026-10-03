// Metadata-only compatibility surface, not a provider or device-control client.
// Replaces a corrupted Git diagnostic. Historical versions fabricated LIVE/load
// values and claimed to switch sessions without actually connecting providers.
(function (root) {
  'use strict';
  const PLATFORMS = Object.freeze([
    ['arena', 'Arena.ai'], ['primary', 'GitHub primary'],
    ['secondary', 'GitHub recovery repository'], ['local', 'Local preview'],
    ['chatgpt', 'ChatGPT'], ['claude', 'Claude'], ['gemini', 'Gemini']
  ].map(([id, name]) => Object.freeze({ id, name, status: 'UNVERIFIED', load: null })));
  function getHealth() {
    return {
      mode: 'metadata_only', operational: false,
      platforms: PLATFORMS.map(p => ({ ...p })),
      agentCounts: { main: 13, sub: 133, products: 421, source: 'registry_reported_not_runtime' },
      currentLoad: null, confidence: 'UNVERIFIED'
    };
  }
  function blocked() {
    return { ok: false, status: 'BLOCKED', reason: 'No provider/session-transfer executor is configured.' };
  }
  root.VyomarajCoordination = Object.freeze({
    PLATFORMS, getHealth,
    detectOverload: () => ({ status: 'UNKNOWN', reason: 'No measured load telemetry.' }),
    switchPlatform: blocked, shareLoadWith: blocked
  });
})(typeof window !== 'undefined' ? window : globalThis);
