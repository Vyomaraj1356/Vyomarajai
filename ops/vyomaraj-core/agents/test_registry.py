import copy
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import rebuild_registry as r

class RegistryTests(unittest.TestCase):
    def setUp(self):
        self.source=json.loads(r.SNAPSHOT.read_text());self.rules=json.loads((r.HERE/'RECONCILIATION_RULES.json').read_text())
        self.data=r.build(self.source,self.rules)
    def test_current_totals(self):
        self.assertEqual(self.data['totals']['sub_agents'],128);self.assertEqual(self.data['totals']['main_agents'],13)
        self.assertEqual(self.data['totals']['uncounted_parent_headings'],6)
    def test_education_finance_transfer(self):
        cats={c['id']:c for c in self.data['categories']}
        self.assertEqual((cats['EDU']['name'],cats['EDU']['sub_agents'],cats['FINANCE']['sub_agents']),('Education',16,7))
        scheme=[a for a in self.data['agents'] if a['id']=='EDU-GOV-S1'];self.assertEqual(len(scheme),1)
        self.assertEqual(scheme[0]['parent_id'],'EDU');self.assertFalse(any(a['name']=='Government Schemes' and a['category_id']!='EDU' for a in self.data['agents']))
    def test_all_six_hubs_uncounted(self):
        self.assertEqual({h['name'] for h in self.data['headings']},{'Comedy hub','Cartoon','Music','Movie','Wit','Shayari'})
        self.assertTrue(all(not h['counted'] for h in self.data['headings']))
        self.assertFalse(any(a['name'] in {'Comedy hub','Cartoon','Music','Movie','Wit','Shayari'} for a in self.data['agents']))
    def test_child_ids_preserved(self):
        ids={a['id'] for a in self.data['agents']}
        for prefix,count in [('AI',2),('CARTOON',3),('COM',8),('MOVIE',6),('MUS',6),('SHAYARI',1),('WIT',1),('HASYA',1),('LIQUOR',1),('BAR',1)]:
            self.assertTrue({f'ENT-{prefix}-S{i}' for i in range(1,count+1)}<=ids)
    def test_correct_hub_edges(self):
        parents={a['id']:a['parent_id'] for a in self.data['agents']}
        self.assertEqual(parents['ENT-MUS-S1'],'ENT-HUB-MUS');self.assertEqual(parents['ENT-MOVIE-S6'],'ENT-HUB-MOVIE')
        self.assertEqual(parents['ENT-LIQUOR-S1'],'ENTERTAINMENT');self.assertEqual(parents['ENT-BAR-S1'],'ENTERTAINMENT')
    def test_indicom_criticism_distinct(self):
        names=[a['name'] for a in self.data['agents'] if a['category_id']=='ENTERTAINMENT' and a['name']]
        self.assertEqual(names,['INDICOM','Criticism gate'])
    def test_no_names_coined_for_unknowns(self):
        unnamed=[a for a in self.data['agents'] if a['name'] is None]
        self.assertEqual(len(unnamed),86);self.assertTrue(all(a['name_status']=='UNKNOWN' for a in unnamed))
        self.assertEqual(sum(a['name'] is not None for a in self.data['agents']),42)
    def test_grantha_six_stay_unassigned(self):
        for i in range(8,14):self.assertIsNone(next(a for a in self.data['agents'] if a['id']==f'EDU-S{i}')['name'])
    def test_platform_serial_not_source_s20(self):
        a=next(a for a in self.data['agents'] if a['id']=='PLATFORM-UNMAPPED')
        self.assertEqual(a['serial'],20);self.assertIsNone(a['source_slot']);self.assertIsNone(a['name'])
    def test_serials_contiguous_per_category(self):
        for c in self.data['categories']:
            self.assertEqual([a['serial'] for a in self.data['agents'] if a['category_id']==c['id']],list(range(1,c['sub_agents']+1)))
    def test_products_not_fabricated(self):
        self.assertIsNone(self.data['totals']['active_products']);self.assertEqual(self.data['totals']['historical_reported_products'],421)
        self.assertTrue(all(c['active_product_count'] is None for c in self.data['categories']))
    def test_source_snapshot_unchanged(self):
        self.assertEqual(hashlib.sha256(r.SNAPSHOT.read_bytes()).hexdigest(),'9e301bfcb1c6e8b23c1bea4fbdcf0d9d12d4c457fe62d7ef60e3161ac3a908a9')
        self.assertEqual(hashlib.sha256((r.CORE/'experience/CONTENT_CATALOG.json').read_bytes()).hexdigest(),'86f2fc0a5b5c9adb606b5f72aa5047fa8ed0bf5bc6c7d9bcd9c82dbcf5b95f70')
    def test_repeatable_outputs(self):
        for path,text in r.outputs().items():self.assertEqual(path.read_text(),text,path.name)
    def test_duplicate_category_exact_removed(self):
        self.source['categories'].append(copy.deepcopy(self.source['categories'][0]));d=r.build(self.source,self.rules)
        self.assertEqual(d['totals']['main_agents'],13);self.assertEqual(len(d['count_reconciliation']['exact_duplicate_records_removed']),1)
    def test_conflicting_category_not_silently_deleted(self):
        c=copy.deepcopy(self.source['categories'][0]);c['products']=900;self.source['categories'].append(c)
        with self.assertRaisesRegex(ValueError,'Conflicting duplicate'):r.build(self.source,self.rules)
    def test_education_duplicate_exact_removed(self):
        rows=self.source['rosters']['EDU']['entries'];rows.append(copy.deepcopy(rows[0]));d=r.build(self.source,self.rules)
        self.assertEqual(d['totals']['sub_agents'],128);self.assertEqual(len(d['count_reconciliation']['exact_duplicate_records_removed']),1)
    def test_education_duplicate_conflict_refused(self):
        rows=self.source['rosters']['EDU']['entries'];new=copy.deepcopy(rows[0]);new['name']='Different';rows.append(new)
        with self.assertRaisesRegex(ValueError,'Conflicting duplicate'):r.build(self.source,self.rules)
    def test_entertainment_group_duplicate_removed(self):
        rows=self.source['rosters']['ENTERTAINMENT']['groups'];rows.append(copy.deepcopy(rows[2]));d=r.build(self.source,self.rules)
        self.assertEqual(d['totals']['sub_agents'],128)
    def test_platform_and_named_roster_duplicates_removed(self):
        self.source['rosters']['PLATFORM']['lanes'].append('YouTube');self.source['rosters']['WAR'].append('PAST')
        d=r.build(self.source,self.rules);self.assertEqual(len(d['count_reconciliation']['exact_duplicate_records_removed']),2)
    def test_dangling_parent_refused(self):
        self.data['agents'][0]['parent_id']='NONEXISTENT'
        with self.assertRaisesRegex(ValueError,'Missing parent'):r.validate(self.data)
    def test_cross_category_parent_refused(self):
        self.data['agents'][0]['parent_id']='ENT-HUB-MUS'
        with self.assertRaisesRegex(ValueError,'Cross-category'):r.validate(self.data)
    def test_duplicate_serial_refused(self):
        self.data['agents'][1]['serial']=1
        with self.assertRaisesRegex(ValueError,'Serial'):r.validate(self.data)
    def test_heading_not_counted_as_agent(self):
        self.data['headings'][0]['counted']=True
        with self.assertRaisesRegex(ValueError,'heading'):r.validate(self.data)
    def test_topic_owner_and_no_duplicates(self):
        ownership=json.loads((r.HERE/'CONTENT_OWNERSHIP_CURRENT.json').read_text());index=r.content_index(ownership,self.data)
        edu=[a for a in index['records'] if a['owner_category']=='EDU'];self.assertEqual(len(edu),21)
        self.assertEqual(len({a['id'] for a in index['records']}),len(index['records']))
        self.assertEqual(sum(a['id']=='EDU-TOPIC-government-schemes' for a in edu),1)
    def test_wrong_education_owner_refused(self):
        ownership=json.loads((r.HERE/'CONTENT_OWNERSHIP_CURRENT.json').read_text());ownership['education_topics'][0]['owner_category']='ENTERTAINMENT'
        with self.assertRaisesRegex(ValueError,'outside EDU'):r.content_index(ownership,self.data)
    def test_conflicting_topic_does_not_disappear(self):
        ownership=json.loads((r.HERE/'CONTENT_OWNERSHIP_CURRENT.json').read_text());row=copy.deepcopy(ownership['education_topics'][0]);row['title']='Different';ownership['education_topics'].append(row)
        with self.assertRaisesRegex(ValueError,'Conflicting duplicate'):r.content_index(ownership,self.data)
    def test_source_and_current_json_separate(self):
        self.assertNotEqual(r.SNAPSHOT,r.ACTIVE);self.assertEqual(self.source['totals']['sub_agents'],133)
    def test_privacy_metadata_only_reads(self):
        original=Path.read_text;paths=[]
        allowed={r.HERE/'RECONCILIATION_RULES.json',r.HERE/'CONTENT_OWNERSHIP_CURRENT.json',r.CORE/'experience/CONTENT_CATALOG.json'}
        allowed|={r.CORE/directory/'content.json' for directory,keys in r.PACKS.values()}
        def guarded(path,*args,**kwargs):
            self.assertIn(path,allowed);paths.append(path);return original(path,*args,**kwargs)
        with patch.object(Path,'read_text',guarded):out=r.outputs()
        self.assertEqual(set(paths),allowed)
        serialized=''.join(out.values());self.assertNotIn('PRIMARY_TOKEN',serialized);self.assertNotIn('devices.json',serialized)

if __name__=='__main__':unittest.main()
