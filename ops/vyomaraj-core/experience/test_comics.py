"""Offline checks for the Chitra Katha comics lane: trilingual editions, version lineage,
deterministic planning and honest no-copy/no-publish claims."""
import json
import unittest

import local_planner as planner
import comics_planner


class ComicsContentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(planner.PACKS['comics'].read_text())

    def test_existing_slots_names_and_proposals(self):
        self.assertEqual([a['slot'] for a in self.data['agents']], [f'ENT-CARTOON-S{i}' for i in range(1, 4)])
        self.assertTrue(all(a['canonical_name'] == 'UNKNOWN' for a in self.data['agents']))
        self.assertTrue(all(a['assignment_status'] == 'proposed_functional_binding' for a in self.data['agents']))
        self.assertEqual(self.data['ownership']['additional_agents_created'], 0)
        self.assertEqual(self.data['ownership']['existing_group'], 'ENT-CARTOON-S1-S3')

    def test_ids_sources_resolve(self):
        self.assertEqual(len(self.data['items']), 12)
        self.assertEqual(len({i['id'] for i in self.data['items']}), 12)
        sources = {s['id'] for s in self.data['sources']}
        for item in self.data['items']:
            self.assertTrue(set(item['source_ids']) <= sources)

    def test_every_original_carries_all_three_languages_and_both_version_scopes(self):
        required = {'hi', 'en', 'hinglish'}
        originals = [i for i in self.data['items'] if i['era'] == 'proposal']
        self.assertEqual(len(originals), 6)
        for item in originals:
            self.assertEqual(set(item['language_editions']), required)
            for edition in item['language_editions'].values():
                self.assertTrue(edition['title'] and edition['tagline'])
            self.assertTrue(item['versions']['past'], 'past editions must be preserved')
            self.assertTrue(item['versions']['future'], 'future editions must be plannable')
            self.assertTrue(all(v['status'] == 'preserved_in_history' for v in item['versions']['past']))
            self.assertTrue(all(v['status'] == 'plannable' for v in item['versions']['future']))
        self.assertEqual(self.data['language_policy']['required_edition_languages'], ['hi', 'en', 'hinglish'])

    def test_heritage_references_are_context_only(self):
        heritage = [i for i in self.data['items'] if i['kind'] == 'heritage-reference']
        self.assertEqual(len(heritage), 6)
        for item in heritage:
            self.assertNotIn('language_editions', item)
            self.assertIn('reference only', item['rights'].lower())

    def test_seeds_carry_three_language_captions_and_versions(self):
        for seed in self.data['original_seeds'].values():
            self.assertEqual(set(seed['captions']), {'English', 'Hindi', 'Hinglish'})
            self.assertEqual(set(seed['editions']), {'hi', 'en', 'hinglish'})
            self.assertTrue(seed['versions']['past'] and seed['versions']['future'])

    def test_no_media_or_connected_provider_claims(self):
        self.assertFalse(any(self.data['scope'].values()))
        self.assertEqual(len(self.data['formats']), 4)


class ComicsPlanTests(unittest.TestCase):
    def plan(self, **kw):
        request = {'experience': 'comics', **kw}
        return comics_planner.build_comics_plan(request, planner.PACKS['comics'])

    def test_valid_plan_with_defaults(self):
        plan = self.plan()
        self.assertEqual(plan['status'], 'local_plan_created')
        self.assertEqual(plan['experience'], 'comics')
        self.assertEqual(plan['format'], 'strip')
        self.assertEqual(plan['primary_language'], 'en')
        self.assertEqual(plan['panels'], 4)

    def test_language_matrix_always_covers_all_three_languages(self):
        for language in ('hi', 'en', 'hinglish'):
            plan = self.plan(primary_language=language)
            self.assertEqual([e['language'] for e in plan['language_matrix']['editions']], ['hi', 'en', 'hinglish'])
            self.assertEqual(plan['sample_captions_language'],
                             {'hi': 'Hindi', 'en': 'English', 'hinglish': 'Hinglish'}[language])

    def test_version_lineage_scopes(self):
        plan = self.plan(versions='past')
        self.assertIn('past', plan['version_lineage'])
        self.assertNotIn('future', plan['version_lineage'])
        plan = self.plan(versions='future')
        self.assertNotIn('past', plan['version_lineage'])
        self.assertIn('future', plan['version_lineage'])
        plan = self.plan(versions='all')
        self.assertTrue(plan['version_lineage']['past'])
        self.assertTrue(plan['version_lineage']['future'])
        self.assertIn('preserved', plan['version_lineage']['past'][0]['status'])
        self.assertEqual(plan['version_lineage']['future'][0]['status'], 'plannable')

    def test_agent_routing_uses_existing_cartoon_slots(self):
        plan = self.plan(item_ids=['amar-chitra-katha'], format='issue')
        self.assertEqual(plan['canonical_agent_ids'], ['ENT-CARTOON-S1', 'ENT-CARTOON-S3'])
        plan = self.plan(item_ids=['meter-down'], format='strip')
        self.assertEqual(sorted(plan['canonical_agent_ids']), ['ENT-CARTOON-S2', 'ENT-CARTOON-S3'])
        self.assertTrue(all(a['canonical_name'] == 'UNKNOWN' for a in plan['proposed_agent_bindings']))

    def test_owner_gate_is_pending(self):
        plan = self.plan()
        self.assertEqual(plan['owner_gate']['status'], 'PENDING_OWNER_PERMISSION')
        self.assertIn('nostalgic camera', plan['owner_gate']['queue'])

    def test_panel_budgets_add_up(self):
        for fmt, panels in (('strip', 5), ('oneshot', 16), ('issue', 33), ('graphic-novel', 100)):
            plan = self.plan(format=fmt, panels=panels)
            self.assertEqual(sum(b['budget_panels'] for b in plan['panel_budget']), panels)
            self.assertEqual(plan['panel_budget'][-1]['panel_numbers'][-1], panels)

    def test_invalid_requests_are_refused(self):
        for bad in ({'item_ids': 'nope'}, {'item_ids': ['unknown-id']}, {'format': 'webtoon'},
                    {'primary_language': 'mr'}, {'versions': 'yesterday'}, {'seed': 'copied-story'},
                    {'panels': 'four'}, {'format': 'strip', 'panels': 30},
                    {'format': 'issue', 'panels': 10}, {'surprise': 1}):
            with self.assertRaises(comics_planner.InvalidComicsPlan, msg=repr(bad)):
                self.plan(**bad)

    def test_no_publishing_or_provider_claims(self):
        plan = self.plan()
        self.assertIsNone(plan['provider'])
        for key in ('ai_calls_made', 'artwork_rendered', 'publishing_enabled', 'media_hosted',
                    'legacy_device_config_loaded', 'production_deployed', 'dr_sync_verified'):
            self.assertFalse(plan[key], key)
        self.assertIn('no published character', plan['review_gates'][0].lower())


class ComicsRoutingTests(unittest.TestCase):
    def test_local_planner_routes_comics_and_validates_registry(self):
        plan = planner.build_plan({'experience': 'comics', 'item_ids': ['vayu-sena'], 'format': 'issue'})
        self.assertEqual(plan['experience'], 'comics')
        registry = json.loads((planner.CORE / 'agents/AGENT_REGISTRY_CURRENT.json').read_text())
        agents = {a['id'] for a in registry['agents']}
        self.assertTrue(set(plan['canonical_agent_ids']) <= agents)

    def test_local_planner_rejects_unknown_comics_fields(self):
        with self.assertRaises(planner.InvalidPlan):
            planner.build_plan({'experience': 'comics', 'format': 'strip', 'evil': True})

    def test_integration_status_lists_comics(self):
        integration = json.loads((planner.CORE / 'experience/LOCAL_INTEGRATION.json').read_text())
        self.assertIn('comics', integration['experiences'])
        self.assertEqual(integration['comics_agent_assignment_status'],
                         'proposed_bindings_to_existing_three_slots')


if __name__ == '__main__':
    unittest.main()
