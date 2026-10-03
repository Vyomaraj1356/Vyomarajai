#!/usr/bin/env python3
"""Rebuild/check a metadata-only handover; never load runtime or module bodies."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
REGISTRY = Path('ops/vyomaraj-core/handover/AGENT_CONTENT_REGISTRY_V16_7_24.json')
CATALOG = Path('ops/vyomaraj-core/experience/CONTENT_CATALOG.json')
OUTPUT = Path('ops/vyomaraj-core/handover/HANDOVER_ALL_UPDATES_2026_10_03.txt')
SOURCE_COMMIT = '7b7dd403c79266d3250e6b334a7598a5432adc17'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def render(root=ROOT):
    registry_bytes = (root / REGISTRY).read_bytes()
    catalog_bytes = (root / CATALOG).read_bytes()
    registry = json.loads(registry_bytes)
    catalog = json.loads(catalog_bytes)
    categories = registry['categories']
    rosters = registry['rosters']
    totals = registry['totals']
    require(len(categories) == totals['main_agents'] == 13, 'Main-agent count mismatch')
    require(len({c['id'] for c in categories}) == 13, 'Duplicate category')
    require(sum(c['sub_agents'] for c in categories) == totals['sub_agents'] == 133,
            'Sub-agent count mismatch')
    require(sum(c['products'] for c in categories) == totals['products'] == 421,
            'Product count mismatch')
    paths = []
    for pack in catalog['packs']:
        require(len(pack['files']) == pack['module_count'], 'Module count mismatch')
        for filename in pack['files']:
            require(Path(filename).name == filename and filename.endswith('.json'),
                    'Invalid catalog filename')
            path = Path(pack['path']) / filename
            require(path.parts[:1] == ('ops',) and '..' not in path.parts,
                    'Invalid catalog directory')
            require((root / path).resolve().is_relative_to(root.resolve()),
                    'Catalog path escapes repository')
            require((root / path).is_file(), f'Missing catalog file: {path}')
            paths.append(path.as_posix())
    require(len(paths) == len(set(paths)) == 32, 'Expected 32 unique cataloged files')

    lines = [
        'VYOMARAJ — ALL UPDATES HANDOVER — 2026-10-03',
        '=' * 64,
        'STATUS: RECONSTRUCTED FROM VERIFIED GIT SOURCE FILES',
        'This is NOT the recovered original 365-line notepad.',
        'The exact original was not found in the inspected sources.',
        'Scope: available roster and catalog metadata, not all private chats or updates.',
        '',
        '1. RECOVERY AND PROVENANCE',
        'Source repository: Vyomaraj1356/Vyomarajai',
        'Source branch: arena/live-preview-reconciled-20261002 (PR #3)',
        f'Source commit: {SOURCE_COMMIT}',
        'Original session branch: arena/01a0f634-vyomarajai (PR #1, closed).',
        'PR #1 directs subsequent work to the reconciled PR #3 branch.',
        'Both source JSON files were restored byte-for-byte from the source commit.',
        'Only those metadata files and this recovery documentation/tooling were added.',
        'Application code, workflows, archives and runtime/device files were not imported.',
        'The Arena session link could not be loaded through the available access.',
        'Remote branches, fetched full Git history and local ZIP entries were inspected.',
        'Missing evidence is not proof that the original file never existed.',
        'No deployment, provider connectivity, device health or DR sync is asserted.',
        '',
        'Source registry: ' + REGISTRY.as_posix(),
        'Registry SHA-256: ' + hashlib.sha256(registry_bytes).hexdigest(),
        'Source catalog: ' + CATALOG.as_posix(),
        'Catalog SHA-256: ' + hashlib.sha256(catalog_bytes).hexdigest(),
        '',
        '2. VERIFIED CATEGORY ARITHMETIC (NOT RUNTIME STATUS)',
        'Registry release: ' + registry['release'] + ' / build ' + str(registry['build']),
        'Registry snapshot: ' + registry['snapshot_date'],
        'Category | Sub-agents | Products | Description',
    ]
    for c in categories:
        lines.append(f"{c['id']} | {c['sub_agents']} | {c['products']} | {c['description']}")
    lines += [
        'TOTAL: 13 main-agent categories | 133 sub-agents | 421 products',
        'Counts are registry-reported; arithmetic is checked, operational readiness is not.',
        '',
        '3. ROSTER — NO INFERRED NAMES OR SLOT ASSIGNMENTS',
        'UNKNOWN means an individual name was not supplied.',
        'UNMAPPED means an individual slot assignment was not supplied.',
        'Grouped names and lane order do not establish individual slot mappings.',
    ]
    for c in categories:
        cid = c['id']
        lines += ['', f"{cid} — {c['sub_agents']} sub-agents / {c['products']} products"]
        roster = rosters.get(cid)
        if roster is None:
            lines += [f"Names: UNKNOWN ({c['sub_agents']} individuals).",
                      'Slots: UNMAPPED; the registry supplies category counts only.']
        elif cid == 'EDU':
            for entry in roster['entries']:
                if entry.get('mapping_status'):
                    lines += [f"{entry['slot']}: supplied group label: {entry['name']}",
                              'Individual names: UNKNOWN; individual assignments: UNMAPPED.']
                else:
                    suffix = f" | chapters: {entry['chapters']}" if 'chapters' in entry else ''
                    lines.append(f"{entry['slot']}: {entry['name']}{suffix}")
        elif cid == 'ENTERTAINMENT':
            require(sum(g['count'] for g in roster['groups']) == c['sub_agents'],
                    'Entertainment group count mismatch')
            for group in roster['groups']:
                lines.append(f"{group['ids']} | count: {group['count']}")
                if 'names' in group:
                    require(len(group['names']) == group['count'], 'Group name count mismatch')
                    lines.append('Supplied names in source order: ' + '; '.join(group['names']))
                else:
                    lines.append('Individual names: UNKNOWN; source group IDs retained above.')
                if 'chapter_count' in group:
                    lines.append('Registry chapter_count: ' + str(group['chapter_count']))
        elif cid == 'PLATFORM':
            require(len(roster['lanes']) + roster['unmapped_slot_count'] == c['sub_agents'],
                    'Platform lane count mismatch')
            require(roster['unmapped_slot_id'] is None, 'Platform mapping needs review')
            lines.append('Named lanes (no numeric slot IDs supplied):')
            lines.extend('- ' + lane for lane in roster['lanes'])
            lines += ['Remaining name: UNKNOWN (1). Remaining slot: UNMAPPED.',
                      'The source does not identify which slot is missing; do not label it S20.']
        else:
            require(isinstance(roster, list) and len(roster) == c['sub_agents'],
                    f'Unexpected roster: {cid}')
            lines.append('Supplied names: ' + '; '.join(roster))
            lines.append('Numeric slot IDs: UNMAPPED (not supplied by the registry).')
    lines += [
        '',
        '4. CONTENT READINESS — SEPARATE, UNRECONCILED OWNER-REPORTED FIGURES',
    ]
    for key in ('active_content_products_reported', 'placeholder_videos_shared',
                'pending_products_requiring_chapters', 'planned_products_requiring_chapters'):
        lines.append(f"{key}: {registry['content_readiness'][key]}")
    lines += [
        'These figures are NOT reconciled to 421. Overlap and status definitions are unknown.',
        'They are not independently verified active products, deployments or published videos.',
        '',
        '5. CATALOG — EXACTLY 32 JSON FILENAMES, NOT 421 PRODUCT TITLES',
        'Only cataloged filenames are listed below; JSON bodies are not reproduced or loaded.',
        'These are file/module names, NOT all 421 product titles.',
        'Complete product-title list: UNKNOWN / not supplied.',
        'Product-to-module and product-to-slot mapping: UNMAPPED / not supplied.',
        'Catalog inventory date: ' + catalog['inventory_date'],
    ]
    for pack in catalog['packs']:
        lines += ['', f"{pack['id']} | directory: {pack['path']} | files: {pack['module_count']}"]
        lines.extend('- ' + filename for filename in pack['files'])
        lines.append('Source ingestion policy: ' + pack['ingestion_mode'])
    lines += [
        '',
        '6. PRIVACY AND OPERATIONAL BOUNDARIES',
        'No populated environment, runtime, device, credential or private contact values included.',
        'The generator reads only the two restored metadata JSON files.',
        'Catalog paths are checked for existence; their bodies are never read.',
        'Hanuman configuration filenames are metadata, not runtime evidence.',
        'No external provider, publishing, device-control or recovery action was executed.',
        'No source code, controller, ZIP member or shell script from another branch was executed.',
        'No main-branch merge, remote push or secondary-repository write was performed.',
        '',
        '7. REMAINING GAPS AND NEXT ACTIONS',
        '- Original 365-line notepad: NOT RECOVERED; this is an explicit reconstruction.',
        '- Missing individual names: UNKNOWN until supported by further source evidence.',
        '- EDU S8-S13: retain the group label; individual names UNKNOWN / mapping UNMAPPED.',
        '- PLATFORM: retain 19 lane names; remaining name UNKNOWN / slot UNMAPPED.',
        '- Full 421-title product catalog and product mappings: not supplied.',
        '- Reconcile readiness figures only when overlap/status rules are available.',
        '- Registry integration blockers are historical, not current secret-store checks.',
        '- Live integrations, deployment, legal compliance and DR sync require separate verification.',
        '- Preserve the historical archives; this recovery does not rewrite their contents.',
        '',
        '8. REPEATABLE VALIDATION',
        'Run from the repository root:',
        'python ops/vyomaraj-core/handover/rebuild_handover.py --check',
        'Checks: category totals, grouped counts, unique catalog paths, file existence,',
        'and exact agreement of this notepad with deterministic metadata-only output.',
        'This validation does not certify missing source material, runtime state or legal compliance.',
        '',
        'END OF RECONSTRUCTED HANDOVER',
    ]
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Validate without writing')
    args = parser.parse_args()
    try:
        text = render()
        output = ROOT / OUTPUT
        if args.check:
            require(output.read_bytes() == text.encode('utf-8'),
                    'Handover differs from source metadata; rebuild and review')
        else:
            output.write_text(text, encoding='utf-8')
        print(f"PASS: 13 categories, 133 sub-agents, 421 product count, 32 catalog files; {len(text.splitlines())} lines")
    except (ValueError, KeyError, OSError, TypeError) as exc:
        parser.exit(1, f'FAIL: {exc}\n')


if __name__ == '__main__':
    main()
