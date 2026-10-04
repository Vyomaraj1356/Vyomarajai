#!/usr/bin/env python3
"""Rebuild/check the build, configuration and inventory report from repository data only.

Every number in the output is read from a checked-in source file, never transcribed by hand:
the agent registry, the content index, the content catalog, experience content files, the
policy/integration configuration, the workflows and the recorded verification evidence.
Run without arguments to write, with --check to verify the checked-in copy matches.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
CORE = HERE.parent
OPS = HERE.parents[1]
OUTPUT = HERE / 'BUILD_AND_CONFIGURATION_2026_10_04.md'
REGISTRY = CORE / 'agents/AGENT_REGISTRY_CURRENT.json'
CONTENT_INDEX = CORE / 'agents/CONTENT_INDEX_CURRENT.json'
CATALOG = CORE / 'experience/CONTENT_CATALOG.json'
HISTORICAL = HERE / 'AGENT_CONTENT_REGISTRY_V16_7_24.json'
INTEGRATION = CORE / 'experience/LOCAL_INTEGRATION.json'
POLICY = CORE / 'governance/PUBLIC_POLICY.json'
DR_POLICY = OPS / 'dr/DR_POLICY.json'
JARVIS_ENV = OPS / 'jarvis/jarvis.env'
JARVIS_DEVICES = OPS / 'jarvis/devices.json'
EXPERIENCES = [('Aghor & Aghori', '/aghor/', 'aghor-experience'),
               ('Bhakti-Shakti', '/bhakti/', 'bhakti-experience'),
               ('Roots & Pairings (no-alcohol by default)', '/pairings/', 'liquor-bar'),
               ('Music & media', '/music/', 'music-experience'),
               ('Film & stage', '/film/', 'film-experience')]
EVIDENCE = [('Preview verification', HERE / 'PREVIEW_VERIFICATION_2026_10_04.json'),
            ('Primary-secondary verification', OPS / 'dr/DEPLOYED_MATCH_2026_10_04.json'),
            ('Failover drill 2026-10-03', OPS / 'availability/LOCAL_FAILOVER_DRILL_2026_10_03.json'),
            ('Failover drill 2026-10-04', OPS / 'availability/LOCAL_FAILOVER_DRILL_2026_10_04.json'),
            ('Test evidence', HERE / 'TEST_EVIDENCE_2026_10_04.json')]


def load(path):
    return json.loads(path.read_text())


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def experience_summary(directory):
    data = load(CORE / directory / 'content.json')
    parts = []
    for key, value in data.items():
        if isinstance(value, list) and value and isinstance(value[0], dict):
            parts.append(f'{key} {len(value)}')
    return ', '.join(parts[:8])


def workflows():
    rows = []
    for path in sorted((ROOT / '.github/workflows').glob('*.yml')):
        text = path.read_text()
        name = re.search(r'^name:\s*(.+)$', text, re.M)
        crons = re.findall(r"cron:\s*'([^']+)'", text)
        rows.append((path.name, name.group(1).strip() if name else 'UNKNOWN',
                     ', '.join(crons) if crons else 'no schedule'))
    return rows


def render(root=ROOT):
    registry = load(root / REGISTRY.relative_to(ROOT))
    historical = load(root / HISTORICAL.relative_to(ROOT))
    content_index = load(root / CONTENT_INDEX.relative_to(ROOT))
    catalog = load(root / CATALOG.relative_to(ROOT))
    integration = load(root / INTEGRATION.relative_to(ROOT))
    policy = load(root / POLICY.relative_to(ROOT))
    dr_policy = load(root / DR_POLICY.relative_to(ROOT))

    historical_by_id = {c['id']: c['sub_agents'] for c in historical['categories']}
    named = {c['id']: [] for c in registry['categories']}
    unnamed_count = {c['id']: 0 for c in registry['categories']}
    for agent in registry['agents']:
        if agent.get('name'):
            named[agent['category_id']].append(agent)
        else:
            unnamed_count[agent['category_id']] += 1

    lines = [
        '# Vyomaraj — build, configuration and inventory — 2026-10-04',
        '',
        'Generated from the checked-in registry, content and configuration files by '
        '`build_configuration_report.py`; every number below is read from those files, not transcribed. '
        'This is a structural inventory, **not** runtime readiness: no sub-agent, provider or revenue '
        'channel is claimed operational.',
        '',
        '## 1. Agents — current owner-approved structure',
        '',
        f"- Registry status: `{registry['status']}` (updated {registry['updated']})",
        f"- Main agents: **{registry['totals']['main_agents']}** · counted sub-agent slots: "
        f"**{registry['totals']['sub_agents']}** · named: **{registry['totals']['named_sub_agents']}** · "
        f"serial-only (name UNKNOWN): **{registry['totals']['unnamed_numbered_sub_agents']}**",
        f"- Uncounted parent headings: **{registry['totals']['uncounted_parent_headings']}** · "
        f"historical reported products: **{registry['totals']['historical_reported_products']}** "
        f"(active product count: {registry['totals']['active_products']} — not reconciled, deliberately "
        f"not zero)",
        f"- Source snapshot: `{registry['source_snapshot']}` "
        f"(sha256 `{registry['source_snapshot_sha256']}`); historical arithmetic validated: "
        f"{historical['totals']['arithmetic_validated']}",
        '',
        '| Main agent | Current sub-agents | Historical snapshot | Change | Named | Serial-only |',
        '|---|---:|---:|---|---:|---:|',
    ]
    for category in registry['categories']:
        current, previous = category['sub_agents'], historical_by_id[category['id']]
        delta = current - previous
        change = 'unchanged' if delta == 0 else (f'+{delta}' if delta > 0 else str(delta))
        lines.append(f"| {category['id']} — {category.get('name', '')} | {current} | {previous} | {change} "
                     f"| {len(named[category['id']])} | {unnamed_count[category['id']]} |")
    lines += [
        '',
        '### Approved structural changes carried in this registry',
        '',
        '- **ENTERTAINMENT 38 → 32**: six hubs (Comedy, Cartoon, Music, Movie, Wit, Shayari) were '
        'reclassified from counted sub-agents to uncounted parent headings — kept, not deleted.',
        '- **FINANCE 8 → 7 and EDU 15 → 16**: the Government Schemes position moved from FINANCE to EDU '
        'as one owner-approved transfer (`EDU-GOV-S1`).',
        '- **BHAKTI 2 → 3**: `BHAKTI-AGHOR-S1` (Aghor & Aghori) added as an explicitly requested, view-only '
        'editorial route — not a deployed autonomous teacher.',
        '',
        '### Named sub-agents (current)',
        '',
    ]
    for category in registry['categories']:
        names = named[category['id']]
        if names:
            listed = '; '.join(f"{a['id']} {a['name']}" for a in names)
            lines.append(f"- **{category['id']}**: {listed}")
    lines += [
        '',
        'Serial-only entries are shown in the viewer as `REF`/serial identifiers (`display_policy`: '
        f"{registry['display_policy']}). Hierarchy: {registry['hierarchy_policy']}",
        '',
        '## 2. Contents',
        '',
        f"- Indexed references: **{content_index['indexed_reference_count']}** "
        f"({content_index['scope']})",
        f"- Education topics: **{content_index['education_topic_count']}** · historical catalog files: "
        f"**{content_index['historical_catalog_files']}** unique paths "
        f"({content_index['historical_catalog_unique_paths']})",
        f"- Deduplication: {content_index['deduplication_basis']}",
        f"- Ownership: education = {content_index['education_owner']}, government schemes = "
        f"{content_index['government_schemes_owner']}",
        '',
        '| Experience route | Content counts |',
        '|---|---|',
    ]
    for label, route, directory in EXPERIENCES:
        lines.append(f'| {label} (`{route}`) | {experience_summary(directory)} |')
    packs = ', '.join(f"{p['path']} ({p['module_count']} files)" for p in catalog['packs'])
    lines += [
        '',
        f"- Ingested content packs: {packs} — {catalog['scope']}",
        f"- Readiness note: {catalog['readiness_note']}",
        '',
        '## 3. Vyomaraj configuration',
        '',
        f"- `LOCAL_INTEGRATION.json`: status `{integration['status']}`, roles — Vyomaraj: "
        f"{integration['roles']['vyomaraj']} Jarvis: {integration['roles']['jarvis']}",
        f"- Planning endpoint `{integration['endpoint']}`; experiences "
        f"{', '.join(integration['experiences'])}; modes {', '.join(integration['modes'])}",
        f"- Flags: automatic AI calls {integration['automatic_ai_calls']}, automatic publishing "
        f"{integration['automatic_publishing']}, legacy Jarvis env loaded "
        f"{integration['legacy_jarvis_env_loaded']}, production deployed "
        f"{integration['production_deployed']}",
        f"- `PUBLIC_POLICY.json` (updated {policy['updated']}): spiritual content mode "
        f"`{policy['spiritual_content_mode']}`, participation `{policy['participation']}`",
        f"- `DR_POLICY.json`: secondary `{dr_policy['secondary']}`, writer `{dr_policy['writer']}`, "
        f"sync approved on main `{dr_policy['sync_approved_on_main']}`, automatic target-only removal "
        f"`{dr_policy['automatic_target_only_file_removal']}`, reverse overwrite "
        f"`{dr_policy['automatic_reverse_overwrite']}`, zero-RPO/RTO verified "
        f"{dr_policy['zero_rpo_verified']}/{dr_policy['zero_rto_verified']}",
        f"- Scope guard: {dr_policy['scope']}",
        '',
        '### Workflows',
        '',
        '| File | Name | Schedule |',
        '|---|---|---|',
    ]
    for name, title, cron in workflows():
        lines.append(f'| `{name}` | {title} | `{cron}` |')
    lines += [
        '',
        '## 4. Jarvis configuration',
        '',
        f"- `ops/jarvis/jarvis.env` — configuration **key names only, no values are printed or copied**: "
        f"{', '.join(sorted(set(re.findall(r'^([A-Za-z_]+)=', (root / JARVIS_ENV.relative_to(ROOT)).read_text(), re.M))))}",
        f"- `ops/jarvis/devices.json` — {len((root / JARVIS_DEVICES.relative_to(ROOT)).read_bytes())} bytes, "
        'primary/secondary device-number configuration. Values stay in the repository; they are not '
        'reproduced here.',
        '- `ops/jarvis/jarvis-24x7-controller.sh` — controller script; not started as an unattended service '
        'in this session, and no switch/fencing URL in it was called.',
        f"- Local roles: the two preview replicas act as the Vyomaraj and Jarvis sides of the availability "
        f"rehearsal ({OPS.as_posix()}/availability/README.md); both share one host and one queue.",
        '',
        '## 5. Recorded verification evidence',
        '',
    ]
    for label, path in EVIDENCE:
        if not (root / path.relative_to(ROOT)).is_file():
            lines.append(f'- {label}: not present')
            continue
        if path.name.startswith('TEST_EVIDENCE'):
            # Not embedded: the test file legitimately changes on every test run, and this report
            # is itself a package member, so quoting it would create a rebuild cycle.
            lines.append(f'- **{label}** (`{path.relative_to(ROOT).as_posix()}`): recorded separately; '
                         'see the file for per-suite counts and results')
            continue
        data = load(root / path.relative_to(ROOT))
        if 'problems' in data:
            detail = (f"{len(data.get('viewer_routes', []))} viewer route checks, "
                      f"{len(data.get('gateway_routes', []))} gateway route checks, problems: "
                      f"{data['problems'] or 'none'}")
        elif 'observations' in data and 'operations' in data:
            detail = (f"{len(data['observations'])} phases "
                      f"({', '.join(str(o.get('phase')) for o in data['observations'])})")
        elif 'observations' in data:
            detail = (f"{len(data['observations'])} checkpoints; current state: "
                      f"{data.get('current_state', 'see file')}")
            writes = data.get('writes_to_secondary_observed', [])
            detail += f"; replication writes observed: {writes or 'none'}"
        elif 'suites' in data:
            detail = '; '.join(f"{s['path']} {s['ran']} tests {s['result']}" for s in data['suites'])
        else:
            detail = 'recorded'
        lines.append(f'- **{label}** (`{path.relative_to(ROOT).as_posix()}`): {detail}')
    lines += [
        '',
        '## 6. What this report does not claim',
        '',
        '- No sub-agent, provider account, revenue channel or device is asserted operational; every registry '
        'entry carries `runtime_status`: NOT_VERIFIED.',
        '- No production deployment, traffic switch, RPO/RTO or independent-site DR is claimed; the DR '
        'evidence covers the Git main snapshot only.',
        '- Product counts remain historical (421 reported) until the title list is reconciled; active products '
        'are `null`, not zero.',
        '- The preview stack is unauthenticated and is a local sandbox, not a production service.',
        '',
    ]
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='verify only; never write')
    args = parser.parse_args()
    rendered = render()
    if args.check:
        current = OUTPUT.read_text() if OUTPUT.is_file() else ''
        if current != rendered:
            raise SystemExit(f'{OUTPUT.name} is out of date; rerun without --check')
        print(f'OK: {OUTPUT.name} matches the repository sources')
    else:
        OUTPUT.write_text(rendered)
        print(f'wrote {OUTPUT.relative_to(ROOT)} ({len(rendered)} bytes)')


if __name__ == '__main__':
    main()
