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


def record_decision(item_id, decision, voice_instruction=None, path=QUEUE_PATH):
    """Record the owner's decision. Rework returns the item to the creating agents and the
    same approval cycle repeats; nothing is published by this function."""
    if decision not in DECISIONS:
        raise InvalidApproval('Decision must be approve, reject, rework or submit.')
    if voice_instruction is not None and (not isinstance(voice_instruction, str)
                                          or not 1 <= len(voice_instruction) <= 500):
        raise InvalidApproval('Voice instruction must be 1–500 characters of plain text.')
    data = _load(path)
    item = next((i for i in data['queue'] if i['id'] == item_id), None)
    if item is None:
        raise InvalidApproval('Unknown queue item.')
    if item['status'] != 'awaiting_owner':
        raise InvalidApproval('Item is not awaiting the owner.')
    outcome = {
        'approve': 'approved_for_publishing_gate',
        'reject': 'rejected_with_reason',
        'rework': 'rework_requested_returns_to_creating_agents',
        'submit': 'submitted_with_instructions_stays_in_cycle',
    }[decision]
    record = {
        'schema_version': 1,
        'item_id': item['id'], 'lane': item['lane'], 'title': item['title'],
        'decision': decision, 'outcome': outcome,
        'decided_by': 'Deepak Goyal — Owner (authority: ShriYantra)',
        'camera': {'id': data['camera']['id'], 'shutter': 'closed_on_decision'},
        'voice_instruction': voice_instruction,
        'cycle': ('Rework: creating agents revise the item with the attached instruction, resubmit it, '
                  'and the same camera approval cycle repeats.')
                if decision in ('rework', 'submit') else
                 ('Approved: the item proceeds to the publishing gate, which stays '
                  'PENDING_OWNER_PERMISSION and records this approval.')
                if decision == 'approve' else
                 'Rejected: the reason is kept and the creating agents are notified.',
        'notifications': {'policy': data['notifications']['policy'],
                          'channels': data['notifications']['channels'],
                          'sent': False},
        'publishing_enabled': False,
        'media_hosted': False,
        'recorded_at_utc': datetime.now(timezone.utc).isoformat(),
    }
    return record
