"""Deterministic Finance & Audit follow-up planning and morning-briefing drafting.

Jarvis and Vyomaraj follow up with the Finance and auditing agents: they check the data and
prepare reminders for the social platforms — gentle emails, firm emails, call scripts and
owner escalations for delayed payments — and they draft the owner's every-morning briefing
for voice, email, text and WhatsApp.

Nothing here sends an email, places a call or sends a message: the output is draft text and
planning metadata only. Amounts and dates in the checked-in ledger are planning figures,
not confirmed payouts.
"""
from datetime import date, datetime, time, timezone
import json
from pathlib import Path

CONTENT_PATH = Path(__file__).resolve().parent / 'content.json'
REFERENCE_DAY = date(2026, 10, 4)  # the day this desk was drafted; keeps outputs deterministic


class InvalidFollowup(ValueError):
    pass


def _load(path=CONTENT_PATH):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def _days_late(due_date, today=REFERENCE_DAY):
    due = date.fromisoformat(due_date)
    return (today - due).days


def classify(payment, today=REFERENCE_DAY):
    """Current / due soon / overdue — the audit step that decides the ladder stage."""
    late = _days_late(payment['due_date'], today)
    if late > 14:
        return 'overdue_escalate'
    if late >= 1:
        return 'overdue'
    if late >= -7:
        return 'due_soon'
    return 'current'


def _stage_for(status, ladder):
    action = {'current': None, 'due_soon': 'gentle_email', 'overdue': 'firm_email',
              'overdue_escalate': 'escalate_to_owner'}[status]
    if action is None:
        return None
    return next(s for s in ladder if s['action'] == action)


def build_followup(path=CONTENT_PATH, today=REFERENCE_DAY):
    """Per-payment follow-up plan: the audit checks, the chosen ladder stage and the draft."""
    data = _load(path)
    ladder = data['reminder_ladder']
    rows, escalations = [], []
    for payment in data['payments']:
        late = _days_late(payment['due_date'], today)
        if late == 0:
            status = 'due_soon'
        elif late < 0:
            status = 'due_soon' if late >= -7 else 'current'
        elif late <= 14:
            status = 'overdue'
        else:
            status = 'overdue_escalate'
        action = {'current': 'none_scheduled', 'due_soon': 'gentle_email', 'overdue': 'firm_email',
                  'overdue_escalate': 'escalate_to_owner'}[status]
        stage = next((s for s in ladder if s['action'] == action), None)
        draft = _draft(payment, status, stage)
        row = {
            'platform': payment['platform'], 'invoice': payment['invoice'],
            'amount_inr': payment['amount_inr'], 'due_date': payment['due_date'],
            'days_late': max(late, 0), 'status': status,
            'audit_checks': data['audit']['checks'],
            'next_action': action,
            'next_action_stage': None if stage is None else stage['stage'],
            'draft': draft,
            'email_sent': False, 'call_made': False, 'message_sent': False,
        }
        rows.append(row)
        if status == 'overdue_escalate':
            escalations.append({'platform': payment['platform'], 'invoice': payment['invoice'],
                                'amount_inr': payment['amount_inr'], 'days_late': max(late, 0),
                                'history': 'previous reminders at stages 1–4 are attached to the escalation'})
    totals = {
        'payments_tracked': len(rows),
        'pending_inr': sum(r['amount_inr'] for r in rows if r['status'] != 'current'),
        'overdue_inr': sum(r['amount_inr'] for r in rows if r['status'].startswith('overdue')),
        'escalations': len(escalations),
    }
    return {
        'schema_version': 1, 'status': 'local_followup_plan_created',
        'prepared_by': 'Jarvis and Vyomaraj with the Finance and auditing agents',
        'reference_day': today.isoformat(),
        'payments': rows, 'escalations': escalations, 'totals': totals,
        'reminder_ladder': ladder,
        'dispute_rule': data['audit']['disputes'],
        'drafts_only': True, 'emails_sent': False, 'calls_made': False, 'messages_sent': False,
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
    }


def _draft(payment, status, stage):
    amount = f"₹{payment['amount_inr']:,}"
    if status == 'current':
        return {'channel': 'none_scheduled',
                'text': f"{payment['platform']}: {amount} expected on {payment['due_date']} ({payment['reference']}) — no reminder needed yet."}
    if status == 'due_soon':
        return {'channel': 'email',
                'subject': f"Upcoming payout confirmation — {payment['invoice']}",
                'text': (f"Hello {payment['platform']} team, this is a friendly confirmation that {amount} "
                         f"(invoice {payment['invoice']}) is scheduled for {payment['due_date']}. "
                         "Please confirm the transfer date. — Vyomaraj Finance desk")}
    if status == 'overdue':
        return {'channel': 'email',
                'subject': f"Payment reminder — {payment['invoice']} overdue",
                'text': (f"Hello {payment['platform']} team, invoice {payment['invoice']} for {amount} was due on "
                         f"{payment['due_date']} and is now overdue. Per the agreed terms, kindly confirm the payment "
                         "date or re-confirm the invoice. — Vyomaraj Finance desk")}
    return {'channel': 'call_and_owner_escalation',
            'subject': f"Escalation — {payment['invoice']} delayed beyond 14 days",
            'text': (f"Call script for {payment['platform']}: confirm receipt of invoice {payment['invoice']} ({amount}, "
                     f"due {payment['due_date']}), ask for a firm payment date, offer to re-send the invoice, and note "
                     "that the owner is being informed this morning. Owner escalation: full reminder history attached.")}


def build_morning_briefing(path=CONTENT_PATH, today=REFERENCE_DAY):
    """The every-morning owner briefing, drafted for voice, email, text and WhatsApp."""
    data = _load(path)
    followup = build_followup(path, today)
    pending = [r for r in followup['payments'] if r['status'] != 'current']
    overdue = [r for r in followup['payments'] if r['status'].startswith('overdue')]
    headline = (f"Good morning. {len(pending)} payment(s) pending worth ₹{followup['totals']['pending_inr']:,}; "
                f"{len(overdue)} overdue worth ₹{followup['totals']['overdue_inr']:,}.")
    sections = {
        'payments_pending': [f"{r['platform']} — ₹{r['amount_inr']:,} due {r['due_date']} ({r['status']})"
                             for r in pending] or ['No payments pending today.'],
        'overdue_escalations': [f"{r['platform']} — {r['days_late']} days late, escalated to you with history"
                                for r in overdue] or ['Nothing overdue today.'],
        'approvals_awaiting': ['Items waiting in the central nostalgic camera queue: see /approvals/.'],
        'dr_sync_state': ['Primary-to-secondary DR snapshot state: see /reports/dr-sync for the recorded evidence.'],
        'yesterday_highlights': ['Yesterday’s publishing and revenue highlights are attached from the analytics lane.'],
    }
    return {
        'schema_version': 1, 'status': 'morning_briefing_drafted',
        'prepared_by': 'Vyomaraj and Jarvis — your left and right buddies',
        'schedule': data['morning_briefing']['schedule'],
        'reference_day': today.isoformat(),
        'headline': headline,
        'sections': sections,
        'channels': {
            'voice': {'note': 'Read aloud by Jarvis at the owner’s morning check-in.',
                      'script': f"{headline} Sections: payments pending, overdue escalations, approvals awaiting, "
                                "DR sync state, yesterday’s highlights. Full drafts attached."},
            'email': {'subject': f"Vyomaraj morning briefing — {today.isoformat()}",
                      'body': headline + ' Itemised sections and drafts are below in the report.'},
            'text': {'message': f"Vyomaraj AM: {len(pending)} pending / {len(overdue)} overdue. "
                                f"₹{followup['totals']['overdue_inr']:,} overdue total. Details in the briefing."},
            'whatsapp': {'message': f"Good morning! Vyomaraj briefing: {len(pending)} payment(s) pending "
                                    f"(₹{followup['totals']['pending_inr']:,}), {len(overdue)} overdue "
                                    f"(₹{followup['totals']['overdue_inr']:,}). Approvals queue and DR state attached. "
                                    "— Vyomaraj & Jarvis"},
        },
        'notifications_sent': False,
        'rule': data['morning_briefing']['rule'],
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
    }
