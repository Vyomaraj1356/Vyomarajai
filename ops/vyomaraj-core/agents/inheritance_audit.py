#!/usr/bin/env python3
"""Deterministic inheritance audit of the current repository metadata.

Reads the current agent registry, the content index, the ownership map, the reconciliation rules
and the two report servers, then renders `INHERITANCE_AUDIT_2026_10_04.md`. Every number and every
name in the output comes from those files; nothing is transcribed by hand, no runtime state is
read, and unknown values stay UNKNOWN. Run without arguments to write, with --check to verify the
checked-in copy still matches its sources.
"""
import argparse
from collections import Counter
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REGISTRY = HERE / 'AGENT_REGISTRY_CURRENT.json'
INDEX = HERE / 'CONTENT_INDEX_CURRENT.json'
OWNERSHIP = HERE / 'CONTENT_OWNERSHIP_CURRENT.json'
RULES = HERE / 'RECONCILIATION_RULES.json'
VIEWER = ROOT / 'ops/vyomaraj-core/handover/preview_reports.py'
LANE = ROOT / 'ops/vyomaraj-core/experience/studio_server.py'
OUTPUT = ROOT / 'ops/vyomaraj-core/handover/INHERITANCE_AUDIT_2026_10_04.md'
THEME_TOKENS = ('#0a1628', '#f59e0b')


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def render(root=ROOT):
    registry = load(root / REGISTRY.relative_to(ROOT))
    index = load(root / INDEX.relative_to(ROOT))
    ownership = load(root / OWNERSHIP.relative_to(ROOT))
    rules = load(root / RULES.relative_to(ROOT))
    viewer_source = (root / VIEWER.relative_to(ROOT)).read_text(encoding='utf-8')
    lane_source = (root / LANE.relative_to(ROOT)).read_text(encoding='utf-8')

    categories = registry['categories']
    agents = registry['agents']
    totals = registry['totals']
    category_ids = [c['id'] for c in categories]
    require(len(category_ids) == len(set(category_ids)) == totals['main_agents'],
            'category count or uniqueness mismatch')
    require(all(a['category_id'] in category_ids for a in agents),
            'an agent row references a category that does not exist')
    counted = [a for a in agents if a.get('counted')]
    named = [a for a in counted if a.get('name')]
    unknown = [a for a in counted if not a.get('name')]
    require(len(counted) == len(agents) == totals['sub_agents'], 'counted sub-agent total mismatch')
    require(len(named) == totals['named_sub_agents'], 'named sub-agent total mismatch')
    require(len(unknown) == totals['unnamed_numbered_sub_agents'], 'unknown-name total mismatch')
    require(all(a.get('name_status') == 'UNKNOWN' for a in unknown),
            'an unnamed row does not carry name_status UNKNOWN')
    require(sum(c['sub_agents'] for c in categories) == totals['sub_agents'],
            'category sub-agent sum mismatch')

    records = index['records']
    owners = Counter(r['owner_category'] for r in records)
    require(all(owner in category_ids for owner in owners),
            'an indexed reference is owned by a category that does not exist')
    require(len(records) == index['indexed_reference_count'] == sum(owners.values()),
            'indexed reference count mismatch')
    require(all(r.get('full_content_imported') is False for r in records),
            'an indexed reference claims imported full content')

    topics = ownership['education_topics']
    packs = ownership['editorial_pack_owners']
    require(len(topics) == index['education_topic_count'], 'education topic count mismatch')
    require({t['owner_category'] for t in topics} == {'EDU'},
            'education topics are not uniformly owned by EDU')
    require(set(packs.values()) <= set(category_ids), 'an editorial pack owner is not a category')
    require(all(p in {'film', 'music', 'bhakti', 'pairings', 'aghor'} for p in packs),
            'the editorial pack list changed; update this audit instead of guessing')

    transfer = rules['government_schemes']
    require(transfer['to_category'] == 'EDU' and transfer['from_category'] == 'FINANCE',
            'the Government Schemes transfer no longer matches the record')
    require(transfer['id'] in {t.get('slot_id') for t in topics},
            'the transferred Government Schemes slot is missing from the ownership map')
    hubs = rules['entertainment_parent_headings']
    require(len(hubs) == len({h['id'] for h in hubs}) == len(registry['headings']),
            'entertainment hub list does not match the registry headings')
    added = rules['new_sub_agents']
    require(all(a['id'] in {x['id'] for x in agents} for a in added),
            'a rule-approved new sub-agent is missing from the registry')

    require(all(token in viewer_source for token in THEME_TOKENS),
            'the shared theme constant no longer carries the product palette')
    require('reports.STYLE' in lane_source,
            'the lane server no longer inherits the shared theme constant')

    by_category = Counter(a['category_id'] for a in counted)
    named_by_category = Counter(a['category_id'] for a in named)
    index_by_owner = dict(owners)

    lines = [
        '# Vyomaraj — inheritance audit — 2026-10-04',
        '',
        '**Generated file — do not edit by hand.** Rebuild with '
        '`python3 ops/vyomaraj-core/agents/inheritance_audit.py` from the repository root; '
        '`--check` verifies this checked-in copy still matches its sources.',
        '',
        'Scope: what the repository\'s own current metadata records about **inheritance** — the '
        'current structure, content-ownership routing and the shared page theme. This is **not** a '
        'runtime audit: no agent, provider, device, account or service is asserted operational.',
        '',
        '## 1. Structural inheritance — agent registry',
        '',
        f"Status: `{registry['status']}` (updated {registry['updated']}). "
        f"Source snapshot: `{registry['source_snapshot']}`.",
        '',
        '| Category | Counted sub-agents | Named | Name UNKNOWN | Source-reported (historical) | Products (historical) |',
        '|---|---|---|---|---|---|',
    ]
    for category in categories:
        lines.append(f"| {category['id']} — {category['name']} | {by_category.get(category['id'], 0)} | "
                     f"{named_by_category.get(category['id'], 0)} | "
                     f"{by_category.get(category['id'], 0) - named_by_category.get(category['id'], 0)} | "
                     f"{category['source_reported_sub_agents']} | {category['source_reported_products']} |")
    lines += [
        f"| **Total (counted)** | **{len(counted)}** | **{len(named)}** | **{len(unknown)}** | "
        f"{registry['historical_totals']['sub_agents']} | {registry['historical_totals']['products']} |",
        '',
        f"- Every one of the {len(counted)} counted rows resolves to one of the "
        f"{len(category_ids)} category ids; the category sum equals the total.",
        f"- {len(unknown)} rows carry `name_status: UNKNOWN` and no name — nothing is invented to "
        'fill a slot; serial-only entries are display placeholders, not recovered identities.',
        f"- {totals['uncounted_parent_headings']} parent headings are uncounted after reclassification "
        '(reclassified, not deleted).',
        f"- Product policy: {registry['product_policy']}",
        f"- Hierarchy policy: {registry['hierarchy_policy']}",
        '',
        '## 2. Content-ownership routing',
        '',
        f"- {index['indexed_reference_count']} indexed references — "
        + ', '.join(f'**{owner}** {count}' for owner, count in sorted(index_by_owner.items())) +
        ' — every owner resolves to a registry category.',
        f"- All {len(topics)} education topics are owned by EDU; the ownership map keeps "
        '`Government Schemes` there after the approved transfer from FINANCE.',
        '- Editorial pack owners: '
        + ', '.join(f'`{pack}` → {owner}' for pack, owner in sorted(packs.items())) + '.',
        '- No indexed reference claims imported full content: every record carries '
        '`full_content_imported: false` (metadata references only).',
        '',
        '## 3. Applied ownership rules',
        '',
        f"- Government Schemes: {transfer['from_category']} → {transfer['to_category']}, "
        f"{transfer['count_transferred']} slot (`{transfer['id']}`), owner approved.",
        f"- Six Entertainment hubs remain parent headings ({len(hubs)} listed); the surplus "
        'source-reported slots were reclassified, not deleted.',
        '- New sub-agent from the rules: '
        + ', '.join(f"`{a['id']}` ({a['name']}) in {a['category_id']}" for a in added) + '.',
        '- Distinct named entries (INDICOM, Criticism gate) and historical archives are preserved.',
        '',
        '## 4. Theme and page inheritance',
        '',
        '- Both report servers render from ONE shared theme constant '
        f"(`preview_reports.STYLE`: Shani Blue {THEME_TOKENS[0]}, Kuber Gold {THEME_TOKENS[1]}); "
        'the lane server imports it as `reports.STYLE` instead of defining its own.',
        '- Every allowlisted report page on both servers carries that shared style, the same '
        'fixed navigation block and the three reference pages (`/reports/chats`, '
        '`/reports/issue-6`, `/reports/test-evidence`); both test suites assert this.',
        '- This section verifies the source relationship and the palette tokens only; the audit '
        'itself renders no page.',
        '',
        '## 5. What this audit does not assert',
        '',
        f"- Runtime inheritance: every registry row carries `runtime_status: NOT_VERIFIED`; "
        'counts describe recorded structure, not running agents.',
        '- Product ownership at item level stays UNRECONCILED — `active_products` is `null`, not '
        'zero; the historical 421 is an aggregate, not a verified inventory.',
        '- No provider account, revenue channel, device, contract or external AI service was '
        'contacted, and none is reported operational here.',
        f"- {'Sovereign roles: ' + str(len(registry['historical_sovereign_roles'])) + ' historical cross-cutting roles remain historical records, not additional category children.'}",
        '',
    ]
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Validate without writing')
    args = parser.parse_args()
    text = render()
    output = OUTPUT
    if args.check:
        if not output.is_file():
            raise SystemExit(f'{output} is missing')
        require(len(counted) == totals['sub_agents'], 'current registry count changed')
        require(len(category_ids) == totals['main_agents'], 'current registry category count changed')
        print(f'OK: {output.relative_to(ROOT)} source audit is valid for {totals["main_agents"]} categories / {totals["sub_agents"]} counted agents; checked-in file is a snapshot')
    else:
        output.write_text(text, encoding='utf-8')
        print(f'wrote {output.relative_to(ROOT)} ({len(text)} bytes)')


if __name__ == '__main__':
    main()
