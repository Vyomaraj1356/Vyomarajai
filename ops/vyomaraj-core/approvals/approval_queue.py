"""Deterministic owner-approval queue for the central nostalgic camera.

Vyomaraj and Jarvis route finished, verified work into this queue; the owner picks an item
from the dropdown, the wooden shutter opens, the review payload plays, and the owner records
a decision (approve / reject / rework / submit), optionally with a voice instruction. Rework
returns the item to the creating agents and it comes back through the same cycle.

Everything here is planning metadata: no media is hosted or streamed, no notification is
sent, nothing is published, and no external call is made.
"""
from datetime import datetime, timezone
import json
from pathlib import Path

QUEUE_PATH = Path(__file__).resolve().parent / 'content.json'
DECISIONS = ('approve', 'reject', 'rework', 'submit')


class InvalidApproval(ValueError):
    pass


def _load(path=QUEUE_PATH):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def build_queue(path=QUEUE_PATH):
    """Queue view for the dropdown: items awaiting the owner, in queue order."""
    data = _load(path)
    return {
        'schema_version': 1,
        'camera': data['camera'],
        'dropdown': [ {'id': item['id'], 'label': f"{item['title']} · {item['lane']}"}
                      for item in data['queue'] if item['status'] == 'awaiting_owner' ],
        'counts': {
            'awaiting_owner': sum(1 for i in data['queue'] if i['status'] == 'awaiting_owner'),
            'total': len(data['queue'])},
        'notifications_policy': data['notifications']['policy'],
        'publishing_enabled': False,
    }


def open_review(item_id, path=QUEUE_PATH):
    """The owner picked an item: the wooden shutter opens and the review payload plays."""
    data = _load(path)
    item = next((i for i in data['queue'] if i['id'] == item_id), None)
    if item is None:
        raise InvalidApproval('Unknown queue item.')
    if item['status'] != 'awaiting_owner':
        raise InvalidApproval('Item is not awaiting the owner.')
    return {
        'schema_version': 1,
        'camera': {**data['camera'], 'shutter': 'open', 'state': 'review_playing'},
        'item': {
            'id': item['id'], 'lane': item['lane'], 'title': item['title'],
            'languages': item['languages'], 'version_line': item['version_line'],
            'created_by': item['created_by'], 'status': 'owner_review_in_progress'},
        'review_payload': {**item['review_payload'],
                           'playback_scope': 'local_described_metadata_no_media_hosted'},
        'available_decisions': list(DECISIONS),
        'voice_instructions': data['voice_instructions'],
        'opened_at_utc': datetime.now(timezone.utc).isoformat(),
    }


def build_decision_record(item, decision, voice_instruction=None, *, decided_by,
                          camera, notifications, recorded_at_utc=None):
    """Build metadata for a cryptographically verified owner decision.

    This pure function does not persist the decision, notify anyone, or publish.
    """
    if decision not in DECISIONS:
        raise InvalidApproval('Decision must be approve, reject, rework or submit.')
    if voice_instruction is not None and (not isinstance(voice_instruction, str)
                                          or not 1 <= len(voice_instruction) <= 500):
        raise InvalidApproval('Voice instruction must be 1–500 characters of plain text.')
    if not isinstance(decided_by, str) or not decided_by.strip() or len(decided_by) > 200:
        raise InvalidApproval('A verified owner subject is required.')
    if not isinstance(item, dict) or not item.get('id'):
        raise InvalidApproval('Queue item is invalid.')
    outcome = {
        'approve': 'owner_approved_for_publishing_gate_not_published',
        'reject': 'rejected_with_reason',
        'rework': 'rework_requested_returns_to_creating_agents',
        'submit': 'submitted_with_instructions_stays_in_cycle',
    }[decision]
    cycle = {
        'approve': ('Owner approval is recorded locally. A separate release authorization is still '
                    'required; nothing was published.'),
        'reject': 'Rejected. No notification was sent automatically.',
        'rework': ('Rework is requested. No creating agent was notified automatically; '
                   'the item remains in the local owner-review workflow.'),
        'submit': ('Instructions are recorded locally. No creating agent was notified automatically; '
                   'the item remains in the local owner-review workflow.'),
    }[decision]
    return {
        'schema_version': 1,
        'status': 'owner_decision_record_prepared_not_persisted',
        'item_id': item['id'], 'lane': item['lane'], 'title': item['title'],
        'decision': decision, 'outcome': outcome,
        'decided_by': decided_by.strip(),
        'authority': 'verified_owner_subject_via_ShriYantra',
        'camera': {'id': camera['id'], 'shutter': 'closed_on_decision'},
        'voice_instruction': voice_instruction,
        'cycle': cycle,
        'notifications': {'policy': notifications['policy'],
                          'channels': notifications['channels'], 'sent': False},
        'publishing_enabled': False,
        'publication_status': 'NOT_PUBLISHED',
        'media_hosted': False,
        'recorded_at_utc': recorded_at_utc or datetime.now(timezone.utc).isoformat(),
    }


def record_decision(item_id, decision, voice_instruction=None, path=QUEUE_PATH, *, decided_by):
    """Build a decision record from the frozen queue fixture; no persistence/effect occurs."""
    data = _load(path)
    item = next((i for i in data['queue'] if i['id'] == item_id), None)
    if item is None:
        raise InvalidApproval('Unknown queue item.')
    if item['status'] != 'awaiting_owner':
        raise InvalidApproval('Item is not awaiting the owner.')
    return build_decision_record(
        item, decision, voice_instruction, decided_by=decided_by,
        camera=data['camera'], notifications=data['notifications'],
    )
