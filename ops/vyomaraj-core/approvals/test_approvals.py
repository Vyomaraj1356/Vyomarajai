"""Offline checks for the owner approval queue (central nostalgic camera)."""
import json
import unittest
from pathlib import Path

import approval_queue as queue


class ApprovalQueueContentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(Path(queue.QUEUE_PATH).read_text())

    def test_governing_principle_chain_is_recorded(self):
        principle = self.data['governing_principle']
        for fragment in ('You (Owner)', 'ShriYantra', 'Vyomaraj/Bharath', 'Jarvis/Laxman',
                         'agents and sub-agents', 'approved publishing', 'social platforms',
                         'analytics and monetization', 'learning and improvement',
                         'Hermes guards integrity', 'Arena executes approved tasks'):
            self.assertIn(fragment, principle)

    def test_camera_is_the_wooden_nostalgic_one(self):
        self.assertIn('wooden', self.data['camera']['style'].lower())
        self.assertIn('shutter', self.data['camera']['interaction'].lower())
        self.assertIn('dropdown', self.data['camera']['interaction'].lower())
        self.assertIn('video and sound play', self.data['camera']['interaction'])

    def test_queue_items_are_awaiting_owner_with_review_payloads(self):
        self.assertTrue(self.data['queue'])
        for item in self.data['queue']:
            self.assertEqual(item['status'], 'awaiting_owner')
            self.assertTrue(item['review_payload']['video_note'])
            self.assertTrue(item['review_payload']['sound_note'])
            self.assertIn('vyomaraj', item['created_by'])
            self.assertIn('jarvis', item['created_by'])

    def test_nothing_publishes_and_notifications_are_recorded_not_sent(self):
        self.assertFalse(self.data['publishing']['enabled'])
        self.assertEqual(self.data['publishing']['gate'], 'PENDING_OWNER_PERMISSION')
        self.assertFalse(self.data['notifications']['sent_in_preview'])


class ApprovalQueueBehaviourTests(unittest.TestCase):
    def test_build_queue_lists_dropdown_items(self):
        view = queue.build_queue()
        self.assertEqual(view['counts']['awaiting_owner'], len(view['dropdown']))
        self.assertEqual(view['counts']['total'], 3)
        self.assertFalse(view['publishing_enabled'])
        self.assertIn('Vyomaraj and Jarvis always notify the owner', view['notifications_policy'])
        for entry in view['dropdown']:
            self.assertTrue(entry['id'] and entry['label'])

    def test_open_review_opens_the_shutter_and_plays_the_payload(self):
        review = queue.open_review('comics-monsoon-post-issue')
        self.assertEqual(review['camera']['shutter'], 'open')
        self.assertEqual(review['camera']['state'], 'review_playing')
        self.assertEqual(review['item']['id'], 'comics-monsoon-post-issue')
        self.assertIn('video_note', review['review_payload'])
        self.assertIn('no_media_hosted', review['review_payload']['playback_scope'])
        self.assertEqual(sorted(review['available_decisions']), ['approve', 'reject', 'rework', 'submit'])

    def test_open_review_rejects_unknown_or_wrong_state_items(self):
        with self.assertRaises(queue.InvalidApproval):
            queue.open_review('not-a-thing')
        with self.assertRaises(queue.InvalidApproval):
            queue.open_review('')

    def test_all_four_decisions_are_recorded_with_owner_and_shriyantra(self):
        outcomes = {}
        for decision in ('approve', 'reject', 'rework', 'submit'):
            record = queue.record_decision('comics-monsoon-post-issue', decision)
            outcomes[decision] = record['outcome']
            self.assertEqual(record['decision'], decision)
            self.assertEqual(record['camera']['shutter'], 'closed_on_decision')
            self.assertIn('Owner', record['decided_by'])
            self.assertIn('ShriYantra', record['decided_by'])
            self.assertFalse(record['publishing_enabled'])
            self.assertFalse(record['notifications']['sent'])
        self.assertEqual(outcomes['approve'], 'approved_for_publishing_gate')
        self.assertEqual(outcomes['reject'], 'rejected_with_reason')
        self.assertEqual(outcomes['rework'], 'rework_requested_returns_to_creating_agents')
        self.assertEqual(outcomes['submit'], 'submitted_with_instructions_stays_in_cycle')

    def test_rework_and_submit_repeat_the_same_cycle(self):
        for decision in ('rework', 'submit'):
            record = queue.record_decision('film-monsoon-outline', decision,
                                           voice_instruction='Make the ending quieter.')
            self.assertIn('same camera approval cycle repeats', record['cycle'])
            self.assertEqual(record['voice_instruction'], 'Make the ending quieter.')

    def test_invalid_decisions_and_instructions_are_refused(self):
        with self.assertRaises(queue.InvalidApproval):
            queue.record_decision('comics-monsoon-post-issue', 'publish-anyway')
        with self.assertRaises(queue.InvalidApproval):
            queue.record_decision('comics-monsoon-post-issue', 'approve', voice_instruction='')
        with self.assertRaises(queue.InvalidApproval):
            queue.record_decision('comics-monsoon-post-issue', 'approve', voice_instruction='x' * 501)
        with self.assertRaises(queue.InvalidApproval):
            queue.record_decision('unknown-item', 'approve')


if __name__ == '__main__':
    unittest.main()
