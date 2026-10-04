"""Deterministic post-deployment change management for a live Vyomaraj.

Owner instruction → ShriYantra alignment → Vyomaraj/Jarvis coordination with all agents →
version-controlled change → separate testing → owner permission → upgrade, with a backup
plan that rolls back and continues on the current version if anything goes wrong.

Planning metadata only: this module never edits a repository, restarts a service, touches
the running business or performs a rollback by itself.
"""
from datetime import datetime, timezone
import json
from pathlib import Path

CONTENT_PATH = Path(__file__).resolve().parent / 'content.json'
KINDS = ('feature', 'fix', 'upgrade', 'rollback')


class InvalidChange(ValueError):
    pass


def _load(path=CONTENT_PATH):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def plan_change(instruction, path=CONTENT_PATH):
    """Turn an owner instruction into a full change record with permission gate and rollback."""
    if not isinstance(instruction, dict):
        raise InvalidChange('Instruction must be a JSON object.')
    allowed = {'instruction', 'kind', 'affected_agents', 'affected_lanes'}
    if set(instruction) - allowed:
        raise InvalidChange('Unknown instruction fields.')
    text = instruction.get('instruction')
    if not isinstance(text, str) or not 5 <= len(text) <= 500:
        raise InvalidChange('State the instruction in 5–500 characters of plain text.')
    kind = instruction.get('kind', 'feature')
    if kind not in KINDS:
        raise InvalidChange(f'Kind must be one of {", ".join(KINDS)}.')
    agents = instruction.get('affected_agents', [])
    lanes = instruction.get('affected_lanes', [])
    for value, label in ((agents, 'affected_agents'), (lanes, 'affected_lanes')):
        if (not isinstance(value, list) or len(value) > 12
                or any(not isinstance(x, str) or not x for x in value)):
            raise InvalidChange(f'{label} must be a list of up to 12 names.')
    data = _load(path)
    slug = _slug(text)
    record = {
        'schema_version': 1, 'status': 'change_planned_awaiting_owner_permission',
        'change_id': f'CHG-{slug[:40]}',
        'instruction': text, 'kind': kind,
        'authority_chain': {
            'owner': 'Deepak Goyal — Owner (authority: ShriYantra)',
            'alignment': 'Vyomaraj/Bharath and Jarvis/Laxman align with ShriYantra before planning',
            'arena_role': 'executes approved tasks; not the owner and not the authority root',
            'shriyantra_aligned': True},
        'coordination': {
            'coordinators': ['Vyomaraj/Bharath (central intelligence)', 'Jarvis/Laxman (coordination)'],
            'affected_agents': agents or ['all agents are informed of the change'],
            'affected_lanes': lanes or ['lane owners confirm scope'],
            'agents_coordinated': True},
        'version_control': {
            'branch': f'upgrade/{slug[:30]}',
            'rule': data['policy']['version_control'],
            'commits_required': 'each change is committed on the branch with a reviewable history',
            'history_deleted': False},
        'testing_plan': [{'stage': s['stage'], 'name': s['name'], 'rule': s['rule'],
                          'result': 'pending_separate_execution'}
                         for s in data['testing_stages']],
        'permission_gate': {'status': 'PENDING_OWNER_PERMISSION',
                            'rule': data['policy']['permission_gate']},
        'upgrade_plan': {
            'steps': ['snapshot the current running version (backup first)',
                      'apply the change on the upgrade branch',
                      'run the separate testing stages and check the results',
                      'ask the owner for permission',
                      'upgrade the live system only after permission',
                      'verify the business is healthy post-upgrade'],
            'zero_business_impact': data['policy']['zero_business_impact'],
            'running_business_interrupted': False},
        'rollback_plan': {**data['rollback_plan'], 'engaged': False},
        'planned_at_utc': datetime.now(timezone.utc).isoformat(),
        'applied': False, 'rolled_back': False, 'live_system_touched': False,
    }
    return record


def apply_permission(record, decision, path=CONTENT_PATH):
    """The owner decides on a planned change. Nothing is applied by this function."""
    if not isinstance(record, dict) or record.get('status') != 'change_planned_awaiting_owner_permission':
        raise InvalidChange('Only a planned change awaiting permission can be decided.')
    if decision == 'approve':
        return {**record, 'status': 'upgrade_scheduled_with_rollback_ready',
                'permission_gate': {**record['permission_gate'],
                                    'status': 'OWNER_APPROVED',
                                    'decided_by': 'Deepak Goyal — Owner (authority: ShriYantra)'},
                'applied': False, 'live_system_touched': False,
                'decided_at_utc': datetime.now(timezone.utc).isoformat()}
    if decision == 'reject':
        return {**record, 'status': 'not_applied_current_version_continues',
                'permission_gate': {**record['permission_gate'],
                                    'status': 'OWNER_REJECTED',
                                    'decided_by': 'Deepak Goyal — Owner (authority: ShriYantra)'},
                'applied': False, 'rolled_back': False, 'live_system_touched': False,
                'decided_at_utc': datetime.now(timezone.utc).isoformat()}
    raise InvalidChange('Decision must be approve or reject.')


def report_failure(record, stage, path=CONTENT_PATH):
    """A post-upgrade verification failed: the backup plan engages and the current version continues."""
    if not isinstance(record, dict) or record.get('status') != 'upgrade_scheduled_with_rollback_ready':
        raise InvalidChange('Only a scheduled upgrade can report a failure.')
    if not isinstance(stage, str) or not stage:
        raise InvalidChange('State the failing stage.')
    data = _load(path)
    return {
        'schema_version': 1, 'status': 'backup_plan_engaged_rolled_back',
        'change_id': record['change_id'], 'failed_stage': stage,
        'action': 'rollback to the snapshotted previous version; continue with the current version',
        'rollback_plan': {**data['rollback_plan'], 'engaged': True},
        'business_impact': 'none claimed by planning alone — the current version keeps serving while the change is repaired',
        'history': 'version control retains the full history; no commit is deleted',
        'owner_notified': {'policy': 'Vyomaraj and Jarvis always notify the owner', 'sent': False},
        'reported_at_utc': datetime.now(timezone.utc).isoformat(),
    }


def _slug(text):
    keep = set('abcdefghijklmnopqrstuvwxyz0123456789-')
    slug = ''.join(c if c in keep else '-' for c in text.lower())
    while '--' in slug:
        slug = slug.replace('--', '-')
    return slug.strip('-') or 'change'
