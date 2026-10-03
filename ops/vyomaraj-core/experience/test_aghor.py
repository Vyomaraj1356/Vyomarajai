import json
from pathlib import Path
import unittest
from unittest.mock import patch
import local_planner as p

class AghorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.data=json.loads(p.PACKS['aghor'].read_text())
    def test_content_counts_and_unique_ids(self):
        for key,count in [('chapters',14),('people',7),('practices',6),('care',6),('sources',11),('timeline',6)]:self.assertEqual(len(self.data[key]),count)
        ids=[r['id'] for k in ('chapters','people','practices','care') for r in self.data[k]];self.assertEqual(len(ids),len(set(ids)))
    def test_provenance_all_records(self):
        ids={s['id'] for s in self.data['sources']}
        for key in ('chapters','people','practices','care','timeline'):
            for row in self.data[key]:self.assertTrue(set(row['source_ids'])<=ids);self.assertTrue(row['source_ids'])
    def test_new_subagent_without_replacing_unknowns(self):
        d=json.loads((p.CORE/'agents/AGENT_REGISTRY_CURRENT.json').read_text());a=[a for a in d['agents'] if a['category_id']=='BHAKTI']
        self.assertEqual(len(a),3);self.assertEqual(sum(x['name'] is None for x in a),2)
        self.assertEqual([x['id'] for x in a if x['name']],['BHAKTI-AGHOR-S1'])
    def test_proposals_and_non_rankings(self):
        self.assertTrue(all(c['chapter_status']=='proposed_editorial_chapter' for c in self.data['chapters']))
        self.assertTrue(all(x['ranking'] is None for x in self.data['people']))
        self.assertIn('not a datable human',self.data['people'][0]['evidence_status'])
    def test_unsafe_rites_have_no_steps(self):
        self.assertEqual(next(x for x in self.data['practices'] if x['id']=='historical-rites')['steps'],[])
        self.assertTrue(all(not x['diagnosis_or_prescription'] for x in self.data['care']))
    def test_plan_modes_disabled(self):
        for mode in ('study','reflection','service'):
            with self.assertRaisesRegex(p.InvalidPlan,'view-only'):
                p.build_plan({'experience':'aghor','topic_id':'medicine','mode':mode})
    def test_invalid_fields_and_modes(self):
        for more in [{'mode':'ritual'},{'mode':'treatment'},{'symptoms':'pain'},{'dose':5},{'topic_id':'../../secret'},{'mode':[]},{'topic_id':None},{'publish':True}]:
            with self.assertRaises(p.InvalidPlan):p.build_plan({'experience':'aghor',**more})
    def test_all_chapters_are_view_only(self):
        self.assertEqual(self.data['content_mode'],'entertainment_view_only')
        self.assertFalse(self.data['plan_generation_enabled'])
        self.assertTrue(all(x['steps']==[] for x in self.data['practices']))
        for c in self.data['chapters']:
            with self.assertRaises(p.InvalidPlan):p.build_plan({'experience':'aghor','topic_id':c['id']})
    def test_disabled_planner_reads_no_files(self):
        with patch.object(Path,'read_text',side_effect=AssertionError('No file reads expected')):
            with self.assertRaises(p.InvalidPlan):p.build_plan({'experience':'aghor'})

if __name__=='__main__':unittest.main()
