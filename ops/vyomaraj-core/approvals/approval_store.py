"""Private, transactional SQLite persistence for owner approval decisions.

Only decision metadata is stored. Bearer tokens and signatures are never persisted.
The store is a single-host operational slice; it is not a distributed control plane.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import stat
import uuid

HERE = Path(__file__).resolve().parent
QUEUE_PATH = HERE / 'content.json'
DEFAULT_PATH = Path(os.environ.get(
    'VYOMARAJ_APPROVALS_DB', Path.home() / '.local/state/vyomaraj/approvals.sqlite3'
)).expanduser()
ZERO_HASH = '0' * 64
TARGET_SHA_RE = re.compile(r'^[0-9a-f]{64}$')


def verify_audit_rows(rows):
    previous_hash = ZERO_HASH
    for row in rows:
        if row['previous_hash'] != previous_hash:
            return {'valid': False, 'event_count': len(rows), 'tip_hash': previous_hash}
        calculated = hashlib.sha256(
            (previous_hash + '\n' + row['event_json']).encode('utf-8')
        ).hexdigest()
        if calculated != row['event_hash']:
            return {'valid': False, 'event_count': len(rows), 'tip_hash': previous_hash}
        previous_hash = row['event_hash']
    return {'valid': True, 'event_count': len(rows), 'tip_hash': previous_hash}


class ApprovalStoreError(RuntimeError):
    """Base error for local approval persistence."""


class InvalidApproval(ApprovalStoreError):
    """The item or requested decision is invalid for its current state."""


class ApprovalReplay(ApprovalStoreError):
    """A one-time approval JTI was already consumed."""


class ApprovalStore:
    def __init__(self, path=DEFAULT_PATH, source_path=QUEUE_PATH):
        self.path = Path(path).expanduser().absolute()
        self.source_path = Path(source_path)
        self._prepare_private_path()
        self._initialize()

    def _prepare_private_path(self):
        parent = self.path.parent
        parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        mode = stat.S_IMODE(parent.stat().st_mode)
        if mode & 0o077:
            raise ApprovalStoreError('Approval state directory must be owner-only (mode 0700).')
        if not self.path.exists():
            fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            os.close(fd)
        mode = stat.S_IMODE(self.path.stat().st_mode)
        if mode & 0o077:
            raise ApprovalStoreError('Approval database must be owner-only (mode 0600).')

    def _connect(self):
        connection = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        connection.row_factory = sqlite3.Row
        connection.execute('PRAGMA busy_timeout=10000')
        connection.execute('PRAGMA foreign_keys=ON')
        connection.execute('PRAGMA journal_mode=WAL')
        self._tighten_file_modes()
        return connection

    def _tighten_file_modes(self):
        for candidate in (self.path, Path(str(self.path) + '-wal'), Path(str(self.path) + '-shm')):
            try:
                if candidate.exists():
                    os.chmod(candidate, 0o600)
            except OSError:
                # Fail closed on the next open if the primary database permissions drift.
                pass

    def _initialize(self):
        try:
            seed = json.loads(self.source_path.read_text(encoding='utf-8'))
        except (OSError, json.JSONDecodeError) as exc:
            raise ApprovalStoreError('Approval queue seed data is unavailable or invalid.') from exc
        connection = self._connect()
        try:
            connection.execute('BEGIN IMMEDIATE')
            connection.execute('''CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY, value TEXT NOT NULL
            )''')
            connection.execute('''CREATE TABLE IF NOT EXISTS queue_items (
                item_id TEXT PRIMARY KEY, position INTEGER NOT NULL,
                status TEXT NOT NULL, body_json TEXT NOT NULL,
                updated_at_utc TEXT NOT NULL
            )''')
            connection.execute('''CREATE TABLE IF NOT EXISTS consumed_approvals (
                jti_sha256 TEXT PRIMARY KEY, consumed_at_utc TEXT NOT NULL
            )''')
            connection.execute('''CREATE TABLE IF NOT EXISTS decisions (
                decision_id TEXT PRIMARY KEY, item_id TEXT NOT NULL,
                recorded_at_utc TEXT NOT NULL, record_json TEXT NOT NULL,
                audit_event_id TEXT NOT NULL, audit_event_hash TEXT NOT NULL,
                FOREIGN KEY(item_id) REFERENCES queue_items(item_id)
            )''')
            connection.execute('''CREATE TABLE IF NOT EXISTS audit_events (
                seq INTEGER PRIMARY KEY AUTOINCREMENT, event_id TEXT UNIQUE NOT NULL,
                recorded_at_utc TEXT NOT NULL, actor_subject TEXT NOT NULL,
                action TEXT NOT NULL, target_sha256 TEXT NOT NULL,
                previous_hash TEXT NOT NULL, event_json TEXT NOT NULL,
                event_hash TEXT UNIQUE NOT NULL
            )''')
            seeded = connection.execute(
                "SELECT value FROM metadata WHERE key='seeded_v1'"
            ).fetchone()
            if seeded is None:
                now = datetime.now(timezone.utc).isoformat()
                for position, item in enumerate(seed.get('queue', [])):
                    if not isinstance(item, dict) or not isinstance(item.get('id'), str):
                        raise ApprovalStoreError('Approval seed includes an invalid queue item.')
                    body = json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
                    connection.execute(
                        'INSERT INTO queue_items(item_id,position,status,body_json,updated_at_utc) '
                        'VALUES(?,?,?,?,?)',
                        (item['id'], position, item['status'], body, now),
                    )
                connection.execute(
                    'INSERT INTO metadata(key,value) VALUES(?,?)',
                    ('seeded_v1', now),
                )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
            self._tighten_file_modes()

    def _metadata(self):
        try:
            data = json.loads(self.source_path.read_text(encoding='utf-8'))
            return data
        except (OSError, json.JSONDecodeError) as exc:
            raise ApprovalStoreError('Approval queue metadata is unavailable or invalid.') from exc

    def queue(self):
        """Return the seed queue with statuses and last decisions from local SQLite."""
        data = self._metadata()
        connection = self._connect()
        try:
            rows = connection.execute(
                'SELECT body_json FROM queue_items ORDER BY position,item_id'
            ).fetchall()
            items = [json.loads(row['body_json']) for row in rows]
        finally:
            connection.close()
        return {
            'schema_version': 1,
            'camera': data['camera'],
            'queue': items,
            'counts': {
                'awaiting_owner': sum(1 for item in items if item['status'] == 'awaiting_owner'),
                'total': len(items),
            },
            'notifications': data['notifications'],
            'publishing': data['publishing'],
            'publishing_enabled': False,
            'audit': {
                'event_count': self._audit_count(),
                'tip_hash': self._audit_tip(),
                'integrity_verified': self.verify_audit_chain()['valid'],
            },
        }

    def _audit_count(self):
        connection = self._connect()
        try:
            return connection.execute('SELECT COUNT(*) FROM audit_events').fetchone()[0]
        finally:
            connection.close()

    def _audit_tip(self):
        connection = self._connect()
        try:
            row = connection.execute(
                'SELECT event_hash FROM audit_events ORDER BY seq DESC LIMIT 1'
            ).fetchone()
            return row['event_hash'] if row else ZERO_HASH
        finally:
            connection.close()

    def open_review(self, item_id):
        """Load one current item from the database and open its local review payload."""
        data = self._metadata()
        connection = self._connect()
        try:
            row = connection.execute(
                'SELECT status,body_json FROM queue_items WHERE item_id=?', (item_id,)
            ).fetchone()
        finally:
            connection.close()
        if row is None:
            raise InvalidApproval('Unknown queue item.')
        if row['status'] != 'awaiting_owner':
            raise InvalidApproval('Item is not awaiting the owner.')
        item = json.loads(row['body_json'])
        return {
            'schema_version': 1,
            'camera': {**data['camera'], 'shutter': 'open', 'state': 'review_playing'},
            'item': {
                'id': item['id'], 'lane': item['lane'], 'title': item['title'],
                'languages': item['languages'], 'version_line': item['version_line'],
                'created_by': item['created_by'], 'status': 'owner_review_in_progress',
            },
            'review_payload': {**item['review_payload'],
                               'playback_scope': 'local_described_metadata_no_media_hosted'},
            'available_decisions': ['approve', 'reject', 'rework', 'submit'],
            'voice_instructions': data['voice_instructions'],
            'opened_at_utc': datetime.now(timezone.utc).isoformat(),
        }

    def item(self, item_id):
        connection = self._connect()
        try:
            row = connection.execute(
                'SELECT status,body_json FROM queue_items WHERE item_id=?', (item_id,)
            ).fetchone()
            return json.loads(row['body_json']) if row else None
        finally:
            connection.close()

    def persist_decision(self, item_id, record, *, jti, target_sha256):
        """Consume a one-time JTI, update the queue, and append an audit event atomically."""
        if not isinstance(record, dict) or record.get('item_id') != item_id:
            raise InvalidApproval('Decision record does not match the queue item.')
        if not isinstance(jti, str) or not jti or len(jti) > 256:
            raise InvalidApproval('Verified one-time approval identifier is invalid.')
        if not isinstance(target_sha256, str) or not TARGET_SHA_RE.fullmatch(target_sha256):
            raise InvalidApproval('Approval target hash is invalid.')
        status_by_decision = {
            'approve': 'owner_approved_for_publishing_gate_not_published',
            'reject': 'rejected_by_owner',
            'rework': 'owner_rework_requested',
            'submit': 'owner_instructions_submitted',
        }
        decision = record.get('decision')
        if decision not in status_by_decision:
            raise InvalidApproval('Decision is not supported.')
        jti_hash = hashlib.sha256(jti.encode('utf-8')).hexdigest()
        event_id = uuid.uuid4().hex
        decision_id = uuid.uuid4().hex
        recorded_at = record.get('recorded_at_utc') or datetime.now(timezone.utc).isoformat()
        actor = record.get('decided_by')
        if not isinstance(actor, str) or not actor:
            raise InvalidApproval('Verified owner subject is required.')

        connection = self._connect()
        try:
            connection.execute('BEGIN IMMEDIATE')
            row = connection.execute(
                'SELECT status,body_json FROM queue_items WHERE item_id=?', (item_id,)
            ).fetchone()
            if row is None:
                raise InvalidApproval('Unknown queue item.')
            if row['status'] != 'awaiting_owner':
                raise InvalidApproval('Item is not awaiting the owner.')
            audit_rows = connection.execute(
                'SELECT previous_hash,event_json,event_hash FROM audit_events ORDER BY seq'
            ).fetchall()
            audit_state = verify_audit_rows(audit_rows)
            if not audit_state['valid']:
                raise ApprovalStoreError('Audit chain integrity failure; new decisions are disabled.')
            try:
                connection.execute(
                    'INSERT INTO consumed_approvals(jti_sha256,consumed_at_utc) VALUES(?,?)',
                    (jti_hash, datetime.now(timezone.utc).isoformat()),
                )
            except sqlite3.IntegrityError as exc:
                raise ApprovalReplay('This owner approval has already been used.') from exc

            previous_hash = audit_state['tip_hash']
            event = {
                'schema_version': 1,
                'event_id': event_id,
                'recorded_at_utc': recorded_at,
                'actor_subject': actor,
                'action': 'approval.decide',
                'target_sha256': target_sha256,
                'item_id': item_id,
                'decision': decision,
                'publication_status': 'NOT_PUBLISHED',
            }
            event_json = json.dumps(
                event, ensure_ascii=False, sort_keys=True, separators=(',', ':'),
            )
            event_hash = hashlib.sha256(
                (previous_hash + '\n' + event_json).encode('utf-8')
            ).hexdigest()
            persisted_record = {
                **record,
                'status': 'owner_decision_recorded_locally',
                'persistence': {
                    'store': 'private_local_sqlite',
                    'audit_event_id': event_id,
                    'audit_event_hash': event_hash,
                    'publication_enabled': False,
                    'notification_sent': False,
                },
            }
            item = json.loads(row['body_json'])
            item['status'] = status_by_decision[decision]
            item['last_decision'] = persisted_record
            item['updated_at_utc'] = recorded_at
            connection.execute(
                'UPDATE queue_items SET status=?,body_json=?,updated_at_utc=? WHERE item_id=?',
                (item['status'], json.dumps(item, ensure_ascii=False, sort_keys=True,
                                            separators=(',', ':')), recorded_at, item_id),
            )
            connection.execute(
                'INSERT INTO audit_events(event_id,recorded_at_utc,actor_subject,action,'
                'target_sha256,previous_hash,event_json,event_hash) VALUES(?,?,?,?,?,?,?,?)',
                (event_id, recorded_at, actor, 'approval.decide', target_sha256,
                 previous_hash, event_json, event_hash),
            )
            connection.execute(
                'INSERT INTO decisions(decision_id,item_id,recorded_at_utc,record_json,'
                'audit_event_id,audit_event_hash) VALUES(?,?,?,?,?,?)',
                (decision_id, item_id, recorded_at,
                 json.dumps(persisted_record, ensure_ascii=False, sort_keys=True,
                            separators=(',', ':')), event_id, event_hash),
            )
            connection.commit()
            return persisted_record
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
            self._tighten_file_modes()

    def verify_audit_chain(self):
        connection = self._connect()
        try:
            rows = connection.execute(
                'SELECT previous_hash,event_json,event_hash FROM audit_events ORDER BY seq'
            ).fetchall()
        finally:
            connection.close()
        return verify_audit_rows(rows)

    def status(self):
        return {
            'database_initialized': self.path.is_file(),
            'audit': self.verify_audit_chain(),
            'publishing_enabled': False,
            'provider_configured': False,
            'production_deployed': False,
        }
