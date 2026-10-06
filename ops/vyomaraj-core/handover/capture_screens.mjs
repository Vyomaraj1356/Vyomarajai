// Real page capture for Vyomaraj — headless Chromium via puppeteer-core.
//
// The sandbox has no browser installed and cannot reach the browser CDNs, so this uses the
// self-contained Chromium that ships inside the @sparticuz/chromium npm tarball, plus the
// Amazon-Linux NSS/NSPR libraries unpacked from that same package (LD_LIBRARY_PATH below).
//
// Reproduce (needs the servers running):
//   mkdir -p /tmp/shot && cd /tmp/shot && npm init -y && npm i puppeteer-core @sparticuz/chromium
//   python3 -c "import brotli;open('/tmp/al2023.tar','wb').write(brotli.decompress(open('node_modules/@sparticuz/chromium/bin/al2023.tar.br','rb').read()))"
//   mkdir -p /tmp/al2023 && tar xf /tmp/al2023.tar -C /tmp/al2023
//   cp ops/vyomaraj-core/handover/capture_screens.mjs /tmp/shot/ && cd /tmp/shot \
//     && VYOMARAJ_SCREENSHOT_DIR=/home/user/Vyomarajai/ops/vyomaraj-core/handover/screenshots node capture_screens.mjs
//
// This records what the pages really look like. It also records failed sub-requests, because a
// page that quietly depends on a CDN script must not be photographed as if it were complete.
import puppeteer from 'puppeteer-core';
import chromium from '@sparticuz/chromium';
import { writeFileSync, mkdirSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';

// Run from a directory that has puppeteer-core installed; point the output back at the repo.
const OUT = (process.env.VYOMARAJ_SCREENSHOT_DIR || new URL('./screenshots/', import.meta.url).pathname)
  .replace(/\/?$/, '/');
mkdirSync(OUT, { recursive: true });

const TARGETS = [
  ['product-page', 'http://127.0.0.1:3000/', 1440, 900, false],
  ['product-landing', 'http://127.0.0.1:3000/landing.html', 1440, 900, true],
  ['flow-diagram', 'http://127.0.0.1:3000/flow-diagram.html', 1440, 1000, true],
  ['reports-home', 'http://127.0.0.1:4174/', 1440, 900, true],
  ['report-network-diagram', 'http://127.0.0.1:4174/reports/network-diagram', 1440, 900, true],
  ['report-stack', 'http://127.0.0.1:4174/reports/stack', 1440, 900, false],
  ['report-go-live', 'http://127.0.0.1:4174/reports/go-live', 1440, 900, false],
  ['lane-music', 'http://127.0.0.1:4181/music/', 1440, 900, false],
  ['gallery-real-captures', 'http://127.0.0.1:4174/reports/screenshots', 1440, 1000, true],
  ['report-market-readiness', 'http://127.0.0.1:4174/reports/market-readiness', 1440, 900, false],
  ['gateway-home', 'http://127.0.0.1:4176/', 1440, 900, false],
];

const browser = await puppeteer.launch({
  args: [...chromium.args, '--no-sandbox', '--disable-dev-shm-usage'],
  executablePath: await chromium.executablePath(),
  env: { ...process.env, LD_LIBRARY_PATH: '/tmp/al2023/lib' },
  headless: 'shell',
});
const version = await browser.version();
const records = [];

for (const [name, url, w, h, fullPage] of TARGETS) {
  const page = await browser.newPage();
  const failed = [];
  page.on('requestfailed', r => failed.push({ url: r.url(), error: (r.failure() || {}).errorText }));
  await page.setViewport({ width: w, height: h, deviceScaleFactor: 1 });
  let status = 0, title = '', error = null;
  try {
    const resp = await page.goto(url, { waitUntil: 'networkidle2', timeout: 45000 });
    status = resp ? resp.status() : 0;
    title = await page.title();
    await new Promise(r => setTimeout(r, 1000));
  } catch (e) {
    error = String(e).slice(0, 200);
  }
  // JPEG keeps the repository and the transfer packages small; PNG of the 28k-pixel-tall flow
  // page alone was 17 MB. Quality 82 is still sharp enough to read every label.
  const file = `${OUT}${name}.jpg`;
  await page.screenshot({ path: file, fullPage, type: 'jpeg', quality: 82 });
  const bytes = readFileSync(file);
  records.push({
    name, url, http_status: status, title,
    viewport: `${w}x${h}`, full_page: fullPage, format: 'jpeg q82',
    file: `screenshots/${name}.jpg`, bytes: bytes.length,
    sha256: createHash('sha256').update(bytes).digest('hex'),
    failed_requests: failed, error,
  });
  console.log(`${name.padEnd(24)} ${String(status).padEnd(4)} ${String(bytes.length).padStart(9)} B  ${title.slice(0, 46)}${failed.length ? '  FAILED:' + failed.length : ''}`);
  await page.close();
}

writeFileSync(OUT + 'SCREENSHOT_CAPTURE_RAW.json', JSON.stringify({
  captured_at_utc: new Date().toISOString(),
  browser: version, method: 'headless chromium (puppeteer-core), deviceScaleFactor 2',
  note: 'PNGs written next to this file; failed_requests lists sub-requests the sandbox could not reach.',
  screenshots: records,
}, null, 2) + '\n');

await browser.close();
console.log(`\nwrote ${records.length} screenshots + SCREENSHOT_CAPTURE_RAW.json (browser: ${version})`);
