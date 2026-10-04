"""Offline checks for the Finance & Audit desk: reminder ladder, drafts and morning briefing."""
import unittest
from datetime import date

import finance_followup as desk


class FollowupTests(unittest.TestCase):
    def test_classification_matches_the_ladder(self):
        cases = {(20, 'overdue_escalate'), (15, 'overdue_escalate'), (14, 'overdue'),
                 (1, 'overdue'), (0, 'due_soon'), (-3, 'due_soon'), (-8, 'current')}
        for offset, expected in cases:
            payment = {'due_date': date.fromordinal(date(2026, 10, 4).toordinal() - offset).isoformat()}
            self.assertEqual(desk.classify(payment), expected, offset)

    def test_followup_plan_covers_every_payment_with_a_next_action(self):
        plan = desk.build_followup()
        self.assertEqual(plan['status'], 'local_followup_plan_created')
        self.assertEqual(len(plan['payments']), 5)
        allowed = {'current', 'due_soon', 'overdue', 'overdue_escalate'}
        for row in plan['payments']:
            self.assertIn(row['status'], allowed)
            self.assertIn(row['next_action'], {'none_scheduled', 'gentle_email', 'firm_email',
                                               'escalate_to_owner'})
            self.assertEqual(row['email_sent'], False)
            self.assertEqual(row['call_made'], False)
            self.assertTrue(row['draft']['text'])
        self.assertEqual(plan['totals']['payments_tracked'], 5)

    def test_overdue_payments_escalate_with_history(self):
        plan = desk.build_followup()
        escalations = plan['escalations']
        self.assertTrue(escalations, 'the 2026-08 brand collab is more than 14 days late in the ledger')
        for esc in escalations:
            self.assertGreater(esc['days_late'], 14)
            self.assertIn('history', esc)
        self.assertEqual(plan['totals']['escalations'], len(escalations))
        self.assertEqual(plan['totals']['overdue_inr'],
                         sum(r['amount_inr'] for r in plan['payments'] if r['status'].startswith('overdue')))

    def test_every_stage_has_a_draft_and_nothing_is_sent(self):
        plan = desk.build_followup()
        self.assertTrue(plan['drafts_only'])
        self.assertFalse(plan['emails_sent'] or plan['calls_made'] or plan['messages_sent'])
        self.assertIn('dispute', plan['dispute_rule'])

    def test_reference_day_is_pinned(self):
        plan = desk.build_followup(today=date(2026, 10, 4))
        self.assertEqual(plan['reference_day'], '2026-10-04')
        by_invoice = {r['invoice']: r for r in plan['payments']}
        self.assertEqual(by_invoice['META-BONUS-2026-09']['status'], 'due_soon')
        self.assertEqual(by_invoice['TG-SUB-2026-10']['status'], 'overdue')
        self.assertEqual(by_invoice['ADS-2026-09']['status'], 'current')


class MorningBriefingTests(unittest.TestCase):
    def test_briefing_is_drafted_for_all_four_channels(self):
        briefing = desk.build_morning_briefing()
        self.assertEqual(briefing['status'], 'morning_briefing_drafted')
        self.assertEqual(set(briefing['channels']), {'voice', 'email', 'text', 'whatsapp'})
        self.assertIn('every morning', briefing['schedule'])
        self.assertFalse(briefing['notifications_sent'])
        for channel in briefing['channels'].values():
            self.assertTrue(channel.get('script') or channel.get('body') or channel.get('message'))

    def test_briefing_names_the_buddies_and_carries_the_sections(self):
        briefing = desk.build_morning_briefing()
        self.assertIn('left and right buddies', briefing['prepared_by'])
        self.assertEqual(set(briefing['sections']), {'payments_pending', 'overdue_escalations',
                                                     'approvals_awaiting', 'dr_sync_state',
                                                     'yesterday_highlights'})
        self.assertIn('Good morning', briefing['headline'])

    def test_briefing_numbers_match_the_followup_plan(self):
        briefing = desk.build_morning_briefing()
        plan = desk.build_followup()
        self.assertIn(f"{len(plan['payments']) - sum(1 for r in plan['payments'] if r['status']=='current')}", briefing['headline'])
        self.assertIn(f"₹{plan['totals']['overdue_inr']:,}", briefing['headline'])


if __name__ == '__main__':
    unittest.main()
