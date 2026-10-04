#!/usr/bin/env python3
"""Build/check the platform-configuration report from the open-items and auto-align plan."""
import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ITEMS = HERE / 'PLATFORM_OPEN_ITEMS_2026_10_04.json'
PLAN = HERE / 'AUTO_ALIGN_NEXT_SESSION.json'
OUTPUT = HERE / 'PLATFORM_CONFIGURATION_CHECK_2026_10_04.md'


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def coverage(items_doc=None, plan=None):
    items_doc = items_doc or load(ITEMS)
    plan = plan or load(PLAN)
    item_ids = {item['id'] for item in items_doc['items']}
    by_item = {}
    for step in plan['steps']:
        for item_id in step.get('covers', []):
            by_item.setdefault(item_id, []).append(step['id'])
    problems = []
    if len(item_ids) != 41:
        problems.append(f'expected 41 open items, found {len(item_ids)}')
    for item_id in sorted(item_ids):
        paths = by_item.get(item_id, [])
        if len(paths) != 1:
            problems.append(f'{item_id} has {len(paths)} completion paths; expected exactly one')
    extras = set(by_item) - item_ids
    if extras:
        problems.append('plan covers unknown item ids: ' + ', '.join(sorted(extras)))
    return by_item, problems


def render(root=ROOT):
    items_doc = load(root / ITEMS.relative_to(ROOT))
    plan = load(root / PLAN.relative_to(ROOT))
    paths, problems = coverage(items_doc, plan)
    if problems:
        raise ValueError('; '.join(problems))
    steps = {step['id']: step for step in plan['steps']}
    lines = [
        '# Platform configuration check — 2026-10-04',
        '',
        '**Generated report.** The source list contains open owner/provider/platform checks; this report maps each one to a completion path. An assigned path is not proof of installation, provider access, owner approval or operational readiness.',
        '',
        f"Scope: {items_doc['scope']}",
        '',
        f"**{len(items_doc['items'])} open items · all {len(items_doc['items'])} have exactly one auto-align step.**",
        '',
        '## How it gets configured (auto-align plan)',
        '',
        'Use the step ids below in `AUTO_ALIGN_NEXT_SESSION_2026_10_04.md`. Each step defines an action, a verification, a `done_when` condition and a repository evidence path. The local runner does not configure accounts or services.',
        '',
        '| Item | Area | Open item | Completion step | Action path |',
        '|---|---|---|---|---|',
    ]
    for item in items_doc['items']:
        step_id = paths[item['id']][0]
        lines.append(f"| `{item['id']}` | {item['area']} | {item['item']} | `{step_id}` | {steps[step_id]['title']} |")
    lines += [
        '',
        '## Owner and execution boundaries',
        '',
        '- Owner decisions, provider access, studio installation, real-media review, DR provisioning and live probes require explicit owner action.',
        '- The checked-in local preview and Git snapshot evidence are not substitutes for independent production DR, runtime backup/restore or an approved business window.',
        '- Evidence must be added to the step\'s repository path and reviewed before a status changes to DONE.',
        '- No prices, plan limits or earnings projections are part of this report.',
        '',
        f"Source items: `{ITEMS.relative_to(ROOT).as_posix()}`",
        f"Completion plan: `{PLAN.relative_to(ROOT).as_posix()}`",
        '',
    ]
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='verify only; never write')
    args = parser.parse_args()
    try:
        _, problems = coverage()
        if problems:
            raise ValueError('; '.join(problems))
        text = render()
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(1, f'FAIL: {exc}\n')
    if args.check:
        current = OUTPUT.read_text(encoding='utf-8') if OUTPUT.is_file() else ''
        if current != text:
            parser.exit(1, f'FAIL: {OUTPUT.name} is out of date; regenerate from its sources\n')
    else:
        OUTPUT.write_text(text, encoding='utf-8')
    print(f'OK: {len(load(ITEMS)["items"])} open platform items have completion paths')


if __name__ == '__main__':
    main()
