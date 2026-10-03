import json
from pathlib import Path
import unittest
import studio_server as server

class GovernanceTests(unittest.TestCase):
    def test_policy_allowlist(self):
        path,mime=server.ASSETS['/policy.json']
        self.assertEqual(path,server.CORE/'governance/PUBLIC_POLICY.json')
        self.assertEqual(mime,'application/json')
    def test_no_contract_execution_or_income_claim(self):
        d=json.loads((server.CORE/'governance/PUBLIC_POLICY.json').read_text())
        self.assertFalse(d['legal']['acceptance_collected']);self.assertFalse(d['earning']['guaranteed_income'])
        self.assertFalse(d['earning']['payment_or_payout_service_connected'])
        self.assertFalse(d['aghor']['plan_generation_enabled'])
    def test_report_routes_exist(self):
        for route in ['/sovereign/','/contracts/','/reports/policy']:
            self.assertEqual(server.REPORTS[route],server.reports.REPORTS[route])
            self.assertTrue((server.CORE/'handover'/server.REPORTS[route]).is_file())
    def test_historical_contracts_not_public_assets(self):
        for path,mime in server.ASSETS.values():
            self.assertNotEqual(path.name,'SOCIAL_PLATFORMS_CONTRACTS.json')
            self.assertNotEqual(path.name,'CONTENT_CREATOR_COLLABS.json')
    def test_view_only_markup(self):
        text=(server.CORE/'aghor-experience/index.html').read_text()
        self.assertNotIn('id="make-plan"',text);self.assertNotIn('id="download"',text)
        self.assertIn('/sovereign/',text);self.assertIn('/contracts/',text)
    def test_metadata_distinguishes_viewer_and_planner(self):
        d=json.loads((server.CORE/'experience/LOCAL_INTEGRATION.json').read_text())
        self.assertIn('aghor',d['experiences']);self.assertNotIn('aghor',d['plannable_experiences'])

if __name__=='__main__':unittest.main()
