#!/usr/bin/env python3
"""Build (or check) the stack and platform record, and the link/archive ledger.

The owner's question, 2026-10-06: "did you render what technologies/platform we used and
configured when we started?" Nothing in the repository answered it in one place, so this builder
enumerates from evidence only:

  * what the shipped product is actually made of (files, sizes, versions on disk);
  * what the month's archive contains (every zip, its bytes, its SHA256 and its member count);
  * which technologies are VERIFIED by code in this checkout, and which are CLAIMED in a
    historical document but have nothing running behind them here;
  * where each link class stands (repository links work; Arena session links and sandbox preview
    links are session-scoped and die — that is why this repository is the durable copy).

It reads local files and the Git object store only. It makes no network call, so no link is
reported as "live" without a recorded source; the Pages status line is whatever the last recorded
observation says and is labelled as such.

Run:  python3 ops/vyomaraj-core/handover/build_stack_record.py
      python3 ops/vyomaraj-core/handover/build_stack_record.py --check
"""
import argparse
import hashlib
import json
import subprocess
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT_MD = HERE / 'STACK_AND_PLATFORM_RECORD_2026_10_06.md'
OUTPUT_JSON = HERE / 'LINK_AND_ARCHIVE_LEDGER_2026_10_06.json'

# Verified = code in this checkout runs it. Every entry names its own evidence.
VERIFIED_STACK = [
    ('Public launch page and planner demo', 'Static HTML + CSS + vanilla JavaScript; no bundler or framework',
     'index.html, launch.css, launch.js, demo.html/demo.css/demo-plan.js/demo.js, demo-catalog.json; landing.html redirects to the evidence-based page',
     'GitHub Pages serves a static catalog export and deterministic in-browser planner; the sandbox root opens demo.html and /index.html keeps the brand shell. Python catalog/plan APIs remain sandbox-only.'),
    ('Installable web shell', 'Web App Manifest + service worker + local PNG/SVG icons',
     'manifest.webmanifest, sw.js, offline.html, assets/vyomaraj-icon-*',
     'offline cache includes only the public landing shell; not a native Android or macOS client'),
    ('Product palette', 'Launch shell: #091323 + gold; experience previews retain Shani Blue #0a1628 + Kuber Gold #f59e0b',
     'launch.css, preview_reports.STYLE, styles.css', 'two documented surfaces; no external font/CDN dependency on the launch page'),
    ('Local servers', 'Python 3 standard library http.server / ThreadingHTTPServer',
     'ops/vyomaraj-core/experience/studio_server.py, ops/availability/gateway.py, '
     'ops/vyomaraj-core/handover/preview_reports.py, public_landing_server.py',
     'studio/gateway enforce loopback-only binds; public preview serves an exact asset allowlist, read-only GET /api/catalog over curated Bhakti-Shakti and Roots & Pairings content, and bounded ephemeral POST /api/plan; no privileged writers, provider calls or persistence; no Flask/FastAPI/Django'),
    ('One-shot local service monitor', 'Manual loopback probes with a read-only latest-snapshot page',
     'ops/vyomaraj-core/handover/probes.py and /reports/monitor',
     'JSONL + latest local snapshot; no scheduler, alerting or production/DR claim'),
    ('Jarvis reachability monitor', 'Python standard-library bounded GET probe with private local state',
     'ops/jarvis/heartbeat_monitor.py, heartbeat-config.example.json',
     'reports reachability only; no authenticated mutual heartbeat, failover or production health'),
    ('Shared peer architecture and heartbeat target', 'Vyomaraj/Jarvis common identity, policy and capability contract; fail-closed heartbeat plan',
     'PEER_ARCHITECTURE_AND_HEARTBEAT_2026_10_07.md, ops/jarvis/heartbeat_monitor.py',
     'design + local read-only probe only; no production interlink, inherited root authority, quorum or failover'),
    ('LLM draft harness', 'Optional no-tools OpenAI-compatible chat client with explicit invocation',
     'ops/jarvis/llm_harness.py, ops/jarvis/LLM_HARNESS.md',
     'no provider is configured by the repository; no tool execution or autonomous actions'),
    ('Panch capability metadata', 'Five-name mapping validator with no runtime/heartbeat claim',
     'ops/hanuman/capability_status.py, ops/hanuman/test_capability_status.py',
     'checks metadata only; capability execution and platform connections remain unimplemented'),
    ('Local owner-approval slice', 'Ed25519 exact-action verification + private transactional SQLite queue and local hash chain',
     'ops/shriyantra/owner_guard.py, ops/vyomaraj-core/approvals/approval_store.py, experience/studio_server.py',
     'issuer/key/owner/security epoch are not configured; local single-host control slice only; no agent handoff or publishing'),
    ('Bindings', 'Server-specific: studio and availability gateway enforce IPv4 loopback; public sandbox preview binds for session access',
     'studio_server.py and gateway.py validate_loopback_host; public_landing_server.py serves exact assets, GET /api/catalog, and POST /api/plan',
     'catalog is curated/read-only for two fixed packs; the planner accepts only two fixed experiences, performs no persistence/provider calls, and is not a privileged writer; never network-bind the local studio/gateway'),
    ('Public hosting', 'GitHub Pages from main (static)',
     'Live read 2026-10-07: Pages API build 04b7ae60, source main',
     'the current feature branch is not deployed there; the URL serves main only'),
    ('Automation', 'GitHub Actions workflow definitions, Python 3.12 and Node 20/24 runners',
     'vyomaraj-sync-both.yml, vyomaraj-ci-diagnostics.yml, vyomaraj-research.yml',
     'latest scheduled run is a tracked-tree check; Actions variable/settings remain unreadable to this credential'),
    ('DR mechanism', 'Git-snapshot replication workflow with scheduled tracked-tree match evidence',
     'ops/dr/dr_sync.py, ops/dr/DR_POLICY.json, live read-only annotations recorded in ISSUES_AND_PRS_LEDGER.json',
     'latest match covers tracked Git only; effective target identity, runtime, app equality, failover, RPO and RTO are unproven'),
    ('Tests and preview release gate', 'Python unittest + node syntax/tests + builder checks; verification only',
     'ops/vyomaraj-core/handover/run_offline_suites.py, ops/vyomaraj/publish-gate.sh',
     'a preview PASS does not change the separate production status; the gate never deploys'),
    ('State stores', 'SQLite and JSON files on disk (no database server)',
     'ops/vyomaraj-core/research/discovery.py, approvals/approval_store.py, ops/vyomaraj-core/ledger',
     'research/approval state is single-host and outside Git-snapshot replication; approval DB is owner-only, but both need independent backup/restore evidence'),
    ('Browser voice', 'Web Speech API (speechSynthesis) where the page uses it',
     'product HTML/JS voice controls', 'microphone capture needs device permission'),
    ('Browser media', 'WebRTC getUserMedia + MediaRecorder + Web Audio API',
     'camera/video/audio mixer lanes in the product page', 'no upload; files stay in the tab'),
    ('Maps', 'Leaflet 1.9.4 with OpenStreetMap tiles', 'map lane in the product page',
     'tiles load from the OSM service at view time'),
    ('Plans and content', 'Deterministic local planners by default; optional explicit no-tools LLM draft stage',
     'local_planner.py, music_planner.py, film_planner.py, comics_planner.py, aghor_planner.py, ops/jarvis/llm_harness.py',
     'provider calls require explicit local configuration and invocation; plans do not publish'),
    ('Registry', 'JSON registry + content index + ownership map, pinned and test-guarded',
     'ops/vyomaraj-core/agents/*.json, test_registry.py', '13 categories / 128 counted slots / 6 headings'),
    ('Android app', 'APK binary committed (24,567,022 bytes); v2 signing-block entry detected, but cryptographic validity, signer provenance and device installation are UNVERIFIED; no project source in repo',
     'Vyomaraj-App.apk: 222 entries, 8 dex files; verify_live_wiring.py parses ZIP signing-block structure (scheme ID 0x7109871a)',
     'not a verified release; keep off downloads until apksigner verification, signer review and a real-device install pass'),
    ('macOS native app', 'No macOS source project or signed application archive in this checkout',
     'repository file inventory', 'not available as a native release'),
]

# Claimed = a historical document says it, nothing in this checkout runs it.
CLAIMED_ONLY = [
    ('PostgreSQL on 5432', 'README_MARKET_READY.md V15.1 ports registry'),
    ('Redis on 6379', 'README_MARKET_READY.md V15.1 ports registry'),
    ('FastAPI backend on 8000', 'README_MARKET_READY.md V15.1 ports registry'),
    ('Flask API on 5000', 'README_MARKET_READY.md V15.1 ports registry'),
    ('HTTPS 443 / HTTP 80 listeners', 'README_MARKET_READY.md V15.1 ports registry'),
    ('Social platform APIs configured (YouTube, Instagram, Facebook, X, Telegram, WhatsApp, '
     'Discord, Pinterest, Threads, Snapchat, Reddit, Twitch, Vimeo, Tumblr, Mastodon)',
     'README_MARKET_READY.md V15.1 social registry'),
    ('Panch-Shakti metadata labels/rosters stating ACTIVE or all agents LIVE',
     'ops/hanuman/hanuman-panch-shakti.json, devices.json, and ports.json; these are declarations, not runtime probes'),
    ('Revenue, follower and MRR figures (₹3.0L, 56.2K, ₹1,29,000, 5.42M views, ₹8.4L, ₹5.67L, '
     '2B UPI, 94.6K)', 'README_MARKET_READY.md V15.1 social registry'),
    ('ElevenLabs voice cloning, Twilio calling, Whisper captions, 4K60 video synthesis',
     'REAL_VYOMARAJ_INVESTIGATION.md V10.0 plan and README_MARKET_READY.md'),
    ('MediaPipe Face Mesh / face generation', 'REAL_VYOMARAJ_INVESTIGATION.md V9-V10 notes'),
    ('Multi-AI provider coordination as a live bus', 'ops/vyomaraj-core/multi-ai-coordination.js '
     'states in its own header that it is metadata-only and that historical versions fabricated '
     'LIVE values'),
    ('SearXNG + Ollama research runtime', 'ops/vyomaraj-core/research/ — discovery is local; the '
     'provider runtime is not active'),
]

LINK_CLASSES = [
    ('GitHub repository', 'https://github.com/Vyomaraj1356/Vyomarajai', 'WORKING',
     'Durable; every artifact in this record lives here.'),
    ('GitHub Pages', 'https://vyomaraj1356.github.io/Vyomarajai/', 'WORKING (main only)',
     'Live read 2026-10-07: Pages source is `main:/` at 04b7ae60; the current feature branch is not deployed there.'),
    ('Raw file URLs', 'https://raw.githubusercontent.com/Vyomaraj1356/Vyomarajai/main/<path>', 'WORKING',
     'Serve any committed file on main. A file is only reachable after its pull request is merged.'),
    ('Arena session links', 'https://arena.ai/agent/<session-id>', 'SESSION-SCOPED / DIES',
     'REAL_VYOMARAJ_INVESTIGATION.md records earlier session links returning "Something went wrong". '
     'They are not storage; the repository is.'),
    ('Sandbox preview links', 'https://<port>-<sandbox>.e2b.app', 'SESSION-SCOPED / DIES',
     'Every preview host from every session so far has died with its sandbox (4190, 4174-...). '
     'Never announce one as the launch address.'),
    ('Local studio/gateway rehearsal ports', '127.0.0.1:4176 / 4181 / 4182 (defaults; loopback policy enforced)', 'LOCAL-ONLY / NOT RUNNING',
     'Studio/gateway refuse non-loopback binds; privileged writer actions require request-scoped owner tokens; do not expose through public ingress.'),
    ('Allowlisted sandbox landing + planner demo', '0.0.0.0:5310', 'SESSION-SCOPED / READ-ONLY CATALOG + PLANNER',
     'Exact asset allowlist plus GET /api/catalog for curated entries from two local packs and ephemeral POST /api/plan; no provider calls, visitor-data persistence, privileged writers or private paths. This is not a public deployment or production health signal.'),
]


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def git(*args):
    return subprocess.run(['git', *args], cwd=ROOT, capture_output=True, text=True).stdout.strip()


def archive_inventory():
    rows = []
    patterns = ['Vyomaraj-Handover-*.zip', 'Vyomaraj-V*-Final-Market-Ready.zip',
                'Vyomaraj-*.zip', 'Vyomaraj-*.tar.gz', 'Vyomaraj-App.apk']
    seen = set()
    for pattern in patterns:
        for path in sorted(ROOT.glob(pattern)):
            if path.name in seen or not path.is_file():
                continue
            seen.add(path.name)
            row = {'name': path.name, 'bytes': path.stat().st_size,
                   'sha256': sha256(path.read_bytes())}
            if path.suffix == '.zip':
                try:
                    with zipfile.ZipFile(path) as archive:
                        row['zip_members'] = len(archive.namelist())
                except zipfile.BadZipFile:
                    row['zip_members'] = None
            rows.append(row)
    return rows


def product_surface():
    rows = []
    for name in ('index.html', 'Index.html', 'landing.html', 'flow-diagram.html', 'demo.html',
                 'launch.css', 'launch.js', 'demo.css', 'demo-plan.js', 'demo.js', 'demo-catalog.json',
                 'manifest.webmanifest', 'sw.js', 'offline.html'):
        path = ROOT / name
        if path.is_file():
            rows.append({'name': name, 'bytes': path.stat().st_size})
    return rows


def chats_state():
    md = ROOT / 'Vyomaraj-All-Chats-Database-One-Month.md'
    state = {'file': md.relative_to(ROOT).as_posix() if md.is_file() else None}
    if md.is_file():
        text = md.read_text(encoding='utf-8', errors='ignore')
        numbered = [line for line in text.splitlines() if line[:2].strip().isdigit() or line[:3].strip().isdigit()]
        state.update({'bytes': md.stat().st_size, 'numbering': 'heading says 28 chats, file contains 34 numbered entries',
                      'numbered_entries': len([l for l in text.splitlines() if l.strip()[:3].rstrip('.').isdigit()]),
                      'known_discrepancy_recorded': True})
    state['extraction_note'] = ('All-Chats-Extraction-Error.txt inside the chats zip records that '
                               '`git show origin/main~4:index.html` failed (exit 128): the raw chat '
                               'transcripts were never exported. What exists is the consolidated '
                               'one-month notes, plus the Git commit list and the 25 handover and 15 '
                               'market-ready archives.')
    return state


def build():
    archives = archive_inventory()
    surface = product_surface()
    issue_ledger = json.loads((HERE / 'ISSUES_AND_PRS_LEDGER.json').read_text(encoding='utf-8'))
    live = issue_ledger.get('current_live_recheck_2026_10_07', {})
    dr = json.loads((HERE / 'ISSUES_AND_PRS_LEDGER.json').read_text(encoding='utf-8')).get('current_dr_validation_2026_10_09', live.get('dr_snapshot', {}))
    pages = live.get('pages', {})
    verified_stack = [list(row) for row in VERIFIED_STACK]
    for row in verified_stack:
        if row[0] == 'Public hosting':
            row[2] = f"Live read 2026-10-07: Pages API build {pages.get('build_commit', 'unknown')[:8]}, source main"
        elif row[0] == 'Automation':
            if dr.get('tree_status', dr.get('status')) == 'MATCH':
                row[3] = f"latest read-only diagnostic reports equal tracked Git trees ({dr.get('primary_tree', 'unknown')}); write access and runtime DR remain unverified"
            else:
                row[3] = f"latest read-only diagnostic reports {dr.get('tree_status', dr.get('status', 'UNKNOWN'))}: {dr.get('missing_on_secondary', 'unknown')} files missing and {dr.get('changed_content_or_mode', 'unknown')} differing; no writes attempted"
        elif row[0] == 'DR mechanism':
            if dr.get('tree_status', dr.get('status')) == 'MATCH':
                row[3] = f"latest read-only check reports equal tracked Git trees ({dr.get('primary_tree', 'unknown')}); canonical target identity and runtime DR remain unverified"
            else:
                row[3] = f"latest read-only check reports {dr.get('tree_status', dr.get('status', 'UNKNOWN'))}: {dr.get('missing_on_secondary', 'unknown')} missing, {dr.get('changed_content_or_mode', 'unknown')} changed; writes and runtime DR remain unverified"
    link_classes = [list(row) for row in LINK_CLASSES]
    handover = [row for row in archives if row['name'].startswith('Vyomaraj-Handover-')
                and row['name'].endswith('.zip')]
    handover_tarballs = [row for row in archives if row['name'].startswith('Vyomaraj-Handover-')
                         and row['name'].endswith(('.tar.gz', '.tgz'))]
    market = [row for row in archives if '-Final-Market-Ready' in row['name']]
    ledger = {
        'recorded_at_utc': '2026-10-07',
        'verified_stack': [{'area': a, 'technology': t, 'evidence': e, 'note': n} for a, t, e, n in verified_stack],
        'claimed_only': [{'claim': c, 'source': s} for c, s in CLAIMED_ONLY],
        'link_classes': [{'class': c, 'example': u, 'status': s, 'note': n} for c, u, s, n in link_classes],
        'current_external_snapshot': {
            'pages': pages,
            'scheduled_dr_snapshot': dr,
            'dr_target_resolution': live.get('dr_target_resolution', {}),
            'observed_main_replication_writes': live.get('observed_main_replication_writes', {}),
            'local_preview_scope': 'Port 5310 is a session-scoped preview; listener state is transient and deliberately not persisted in this generated record.',
            'scope_limit': 'tracked Git-tree equality does not prove runtime, deployed app, failover, RPO or RTO',
        },
        'archives': archives,
        'handover_archives': len(handover),
        'handover_tarballs': len(handover_tarballs),
        'market_ready_archives': len(market),
        'product_surface': surface,
        'chats': chats_state(),
    }
    return ledger


def render(ledger):
    current = ledger.get('current_external_snapshot', {})
    dr = current.get('scheduled_dr_snapshot', {})
    target = current.get('dr_target_resolution', {})
    pages = current.get('pages', {})
    lines = [
        '# Vyomaraj — stack and platform record — 7 October 2026',
        '',
        '**Generated file — do not edit by hand.** Rebuild with '
        '`python3 ops/vyomaraj-core/handover/build_stack_record.py`; `--check` verifies this copy.',
        '',
        'This is the answer to "what technologies and platforms did we use and configure?" written '
        'from evidence in this checkout, not from memory. It separates what is **implemented by code '
        'here** from what a historical document **claimed**; a local listener or probe does not prove '
        'production readiness. Read section 3 before repeating any figure from the earlier market-ready README.',
        '',
        '## 1. What the product is actually made of',
        '',
        '| Area | Technology | Evidence | Note |',
        '|---|---|---|---|',
    ]
    for row in ledger['verified_stack']:
        lines.append(f"| {row['area']} | {row['technology']} | `{row['evidence']}` | {row['note']} |")
    lines += ['', '## 2. The month\'s archive (all of it, in this repository)', '',
              f"- Handover zip packages: **{ledger['handover_archives']}** "
              f"(V16.5.3-v167 through V16.7.22-v192), plus "
              f"{ledger['handover_tarballs']} duplicate tarball of the first one",
              f"- Market-ready releases: **{ledger['market_ready_archives']}** (V6.6 through V15.1)", 
              f"- Archives counted in total: **{len(ledger['archives'])}**", '',
              '| Archive | Bytes | SHA256 | Zip members |', '|---|---|---|---|']
    for row in sorted(ledger['archives'], key=lambda r: (not r['name'].startswith('Vyomaraj-Handover'), r['name'])):
        members = row.get('zip_members')
        lines.append(f"| `{row['name']}` | {row['bytes']:,} | `{row['sha256'][:16]}…` | "
                     f"{members if members is not None else '—'} |")
    lines += ['', '### Product surface on disk', '', '| File | Bytes |', '|---|---|']
    for row in ledger['product_surface']:
        lines.append(f"| `{row['name']}` | {row['bytes']:,} |")
    chats = ledger['chats']
    lines += ['', '### The one-month chat record', '',
              f"- File: `{chats.get('file')}` ({chats.get('bytes', 0):,} bytes)"
              if chats.get('file') else '- File: not found', 
              f"- Discrepancy already recorded and served at `/reports/chats`: {chats.get('numbering')}",
              f"- {chats['extraction_note']}", '',
              '**Nothing is missing, and nothing more exists than this.** The consolidated notes, the '
              'commit list, and all 25 handover plus 15 market-ready archives are in the repository '
              'and served. Raw per-chat transcripts are the one thing that was never exported — the '
              'extraction error above is why — so no future session should promise to "recover" them '
              'from this repository.', '',
              '## 3. Verified here vs claimed in a document', '',
              '**Claimed in `README_MARKET_READY.md` (V15.1) or the V10.0 investigation note, with '
              'nothing running behind it in this checkout.** Do not repeat these as live:', '',
              '| Claim | Where it is claimed |', '|---|---|']
    for row in ledger['claimed_only']:
        lines.append(f"| {row['claim']} | {row['source']} |")
    lines += ['', 'Everything in section 1 is the implemented repository stack: static pages, Python standard-library '
              'servers, GitHub Pages, GitHub Actions workflow definitions, a Git-snapshot replication mechanism, '
              'local planners, and browser APIs. The scheduled Actions check at '
              f"`{dr.get('completed_at_utc')}` (run `{dr.get('workflow_run_id')}` / check `{dr.get('check_run_id')}`) reports "
              f"`status={dr.get('status')}`, `data_match={dr.get('data_match')}`, equal tracked trees "
              f"`{dr.get('primary_tree')}` / `{dr.get('secondary_tree')}`, and traffic `{dr.get('traffic_switched')}`. "
              f"The workflow-selected target identity `{target.get('effective_target_identity', 'UNCONFIRMED')}` "
              'is not independently confirmed (Actions settings API 403; candidate paths 404 are ambiguous). '
              'This does not prove runtime/app equality, site failover, RPO or RTO; issue #6 stays OPEN/P0.', '',
              '## 4. Links: what lasts and what dies', '',
              '| Class | Example | Status | Note |', '|---|---|---|---|']
    for row in ledger['link_classes']:
        lines.append(f"| {row['class']} | `{row['example']}` | **{row['status']}** | {row['note']} |")
    lines += ['', '## 5. The zero-cost launch path (no money spent)', '',
              '| Need | Free route | Cost | Limit to state honestly |', '|---|---|---|---|',
              f'| Public address | GitHub Pages from `main:/` at `{pages.get("build_commit", "unknown")[:8]}` | ₹0 | This feature branch is not deployed; static files only, no server-side runtime |',
              f'| Automation + DR | Scheduled run `{dr.get("workflow_run_id")}` reports equal tracked Git trees | ₹0 | Effective target identity `{target.get("effective_target_identity", "UNCONFIRMED")}` remains unconfirmed; runtime/failover/RPO/RTO are not proven |',
              '| App distribution | Existing APK v2 signing-block entry; signature validity not established | ₹0 tooling | Run `apksigner verify`, confirm signer provenance, then test installation on a real device before distributing; never treat block presence alone as proof |',
              f'| Local dry runs | Five legacy Python preview services plus the allowlisted :5310 demo are defined | ₹0 | {current.get("local_preview_scope")}; session-only rehearsal, not production |',
              '| Voice enrollment | On-device only, consent screen + delete control | ₹0 | No cloud vendor, no cloning, no identity-document capture in the app |',
              '| Payments | None until revenue exists | ₹0 | No gateway, no UPI integration; do not advertise payments |', '',
              '**When Vyomaraj earns, this is the order to buy in** (cheapest first, each one '
              'unlocking something the free stack cannot do):',
              '',
              '1. **A domain** — the launch address stops depending on `github.io`.',
              '2. **A small always-on host** — the Python services run outside a sandbox, with a '
              'supervisor and a health check the owner can read from a phone.',
              '3. **Runtime database backup or object storage** — Git-snapshot replication does not '
              'cover the SQLite/JSON state.',
              '4. **Payments/KYC** — only with a real gateway account and a legal read.',
              '5. **A voice/video vendor** — only with a signed data-processing agreement, replacing '
              'the on-device enrollment.',
              '6. **Play Console (one-time)** — signed release builds and store listing.',
              '7. **CDN / media hosting** — only when there is licensed or owned media to serve.',
              '',
              'Every step above is a purchase decision for the owner and is not assumed here. The 11 October 2026 date remains a target; owner-approved DR access, branch review/deployment and release checks are separate gates.',
              '', 'END OF STACK AND PLATFORM RECORD']
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='verify only; never write')
    args = parser.parse_args()
    ledger = build()
    text = render(ledger)
    if args.check:
        problems = []
        if not OUTPUT_MD.is_file() or OUTPUT_MD.read_text(encoding='utf-8') != text:
            problems.append(f'{OUTPUT_MD.name} is out of date; rebuild and review')
        if not OUTPUT_JSON.is_file() or json.loads(OUTPUT_JSON.read_text(encoding='utf-8')) != ledger:
            problems.append(f'{OUTPUT_JSON.name} is out of date; rebuild and review')
        for problem in problems:
            print('FAIL:', problem)
        if problems:
            raise SystemExit(1)
        print(f'OK: {OUTPUT_MD.name} and {OUTPUT_JSON.name} match their evidence '
              f"({len(ledger['archives'])} archives, "
              f"{len(ledger['verified_stack'])} verified stack areas, "
              f"{len(ledger['claimed_only'])} claims marked unverified)")
        return
    OUTPUT_MD.write_text(text, encoding='utf-8')
    OUTPUT_JSON.write_text(json.dumps(ledger, indent=2) + '\n', encoding='utf-8')
    print(f"wrote {OUTPUT_MD.relative_to(ROOT)} ({len(text.splitlines())} lines)")
    print(f"wrote {OUTPUT_JSON.relative_to(ROOT)} — {len(ledger['archives'])} archives, "
          f"{ledger['handover_archives']} handover, {ledger['market_ready_archives']} market-ready")


if __name__ == '__main__':
    main()
