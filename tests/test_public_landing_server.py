import hashlib
import importlib.util
import json
import threading
import unittest
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "ops/vyomaraj-core/experience/public_landing_server.py"
spec = importlib.util.spec_from_file_location("public_landing_server", MODULE_PATH)
preview = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preview)


class AssetLinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        for attribute in ("href", "src"):
            if values.get(attribute):
                self.urls.append(values[attribute])


class PublicLandingServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), preview.PublicLandingHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def request_json(self, body, *, path="/api/plan", headers=None):
        raw = body if isinstance(body, bytes) else json.dumps(body).encode("utf-8")
        request_headers = {"Content-Type": "application/json", "Accept": "application/json"}
        request_headers.update(headers or {})
        request = urllib.request.Request(self.url + path, data=raw, headers=request_headers, method="POST")
        try:
            response = urllib.request.urlopen(request)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            payload = response.read()
            return response.status, response.headers, json.loads(payload) if payload else None

    def request_get_json(self, path):
        request = urllib.request.Request(self.url + path, headers={"Accept": "application/json"})
        try:
            response = urllib.request.urlopen(request)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            payload = response.read()
            return response.status, response.headers, json.loads(payload) if payload else None

    def test_public_shell_and_sandbox_host_are_served_with_security_headers(self):
        request = urllib.request.Request(self.url + "/", headers={"Host": "5310-preview.test"})
        with urllib.request.urlopen(request) as response:
            body = response.read().decode("utf-8")
            self.assertEqual(response.status, 200)
            self.assertIn("Content-Security-Policy", response.headers)
            self.assertIn("X-Content-Type-Options", response.headers)
            self.assertEqual(response.headers["X-Robots-Tag"], "noindex, nofollow")
            self.assertIn("LIVE SANDBOX DEMO · NOT PRODUCTION", body)
            self.assertIn("Browse the local library", body)
        with urllib.request.urlopen(self.url + "/index.html") as response:
            public_shell = response.read().decode("utf-8")
            self.assertIn("Authority that stays human", public_shell)
            self.assertIn("./demo.html", public_shell)

    def test_demo_page_assets_are_explicitly_allowlisted_and_served_exactly(self):
        for route in ("/demo.html", "/demo.css", "/demo.js"):
            with self.subTest(route=route), urllib.request.urlopen(self.url + route) as response:
                self.assertEqual(response.status, 200)
                self.assertEqual(response.read(), (ROOT / route.lstrip("/")).read_bytes())
                self.assertIn("no-store", response.headers["Cache-Control"])
        with urllib.request.urlopen(self.url + "/demo.html") as response:
            html = response.read().decode("utf-8")
        self.assertIn("LIVE SANDBOX DEMO · NOT PRODUCTION", html)
        self.assertIn("Browse the local library", html)
        self.assertIn("No model / AI call", html)
        self.assertIn("Neither the request nor the result is stored.", html)
        self._assert_catalog_exposes_real_local_entries_sources_and_review_limits()

    def _assert_catalog_exposes_real_local_entries_sources_and_review_limits(self):
        status, headers, bhakti = self.request_get_json("/api/catalog?experience=bhakti")
        self.assertEqual(status, 200)
        self.assertTrue(headers["Content-Type"].startswith("application/json"))
        self.assertEqual(headers["Cache-Control"], "no-store")
        self.assertNotIn("Access-Control-Allow-Origin", headers)
        self.assertLessEqual(int(headers["Content-Length"]), preview.MAX_RESPONSE_BYTES)
        self.assertEqual(bhakti["status"], "local_catalog_loaded")
        self.assertEqual(bhakti["item_count"], 35)
        self.assertEqual(len(bhakti["items"]), 35)
        self.assertEqual(bhakti["experience"], "bhakti")
        self.assertFalse(bhakti["ai_calls_made"])
        self.assertFalse(bhakti["publishing_enabled"])
        self.assertFalse(bhakti["production_deployed"])
        kamakhya = next(item for item in bhakti["items"] if item["id"] == "kamakhya")
        self.assertIn("religious legend", kamakhya["description"])
        self.assertTrue(kamakhya["source_references"])
        fruit = next(item for item in bhakti["items"] if item["id"] == "fruit")
        self.assertIn("banana", fruit["ingredients"])
        self.assertTrue(bhakti["review_gates"])

        status, _headers, liquor = self.request_get_json("/api/catalog?experience=liquor-bar")
        self.assertEqual(status, 200)
        self.assertEqual(liquor["item_count"], 19)
        tadi = next(item for item in liquor["items"] if item["id"] == "tadi-local")
        self.assertEqual(tadi["content_status"], "research_candidate")
        self.assertIn("must not be treated as interchangeable", tadi["description"])
        self.assertEqual(tadi["source_references"], [])
        chana = next(item for item in liquor["items"] if item["id"] == "chana")
        self.assertIn("chickpeas", chana["ingredients"])
        self.assertTrue(chana["steps"])
        event = next(item for item in liquor["items"] if item["id"] == "spirit-goa")
        self.assertEqual(event["content_status"], "historical_edition_only")
        self.assertTrue(event["source_references"])
        self.assertIn("upcoming", liquor["review_gates"][1])
        self.assertIn("allergens", liquor["review_gates"][-1])

    def _assert_catalog_rejects_unapproved_queries_and_write_methods(self):
        for path in (
            "/api/catalog", "/api/catalog?experience=", "/api/catalog?experience=music",
            "/api/catalog?format=json", "/api/catalog?experience=bhakti&topic_id=overview",
            "/api/catalog?experience=bhakti&experience=liquor-bar",
        ):
            with self.subTest(path=path):
                status, _headers, result = self.request_get_json(path)
                self.assertEqual(status, 400)
                self.assertIn("error", result)
        status, headers, result = self.request_json({"experience": "bhakti"}, path="/api/catalog")
        self.assertEqual(status, 405)
        self.assertEqual(headers["Allow"], "GET")
        self.assertIn("read-only", result["error"])
        for method in ("HEAD", "OPTIONS"):
            request = urllib.request.Request(
                self.url + "/api/catalog?experience=bhakti", method=method
            )
            with self.subTest(method=method), self.assertRaises(urllib.error.HTTPError) as error:
                urllib.request.urlopen(request)
            error.exception.close()
            self.assertEqual(error.exception.code, 405)
            self.assertEqual(error.exception.headers["Allow"], "GET")

    def test_architecture_and_audit_routes_are_explicitly_allowlisted(self):
        expected = {
            "/ops/vyomaraj-core/handover/ARCHITECTURE_DIAGRAM_2026_10_06.svg": "image/svg+xml",
            "/ops/vyomaraj-core/handover/GO_LIVE_GAPS_AND_PLATFORM_2026_10_06.md": "text/plain",
            "/ops/vyomaraj-core/handover/INTEGRATION_ALIGNMENT_AND_RELEASE_AUDIT_2026_10_07.md": "text/plain",
            "/ops/vyomaraj-core/handover/PEER_ARCHITECTURE_AND_HEARTBEAT_2026_10_07.md": "text/plain",
        }
        for route, content_type in expected.items():
            with self.subTest(route=route), urllib.request.urlopen(self.url + route) as response:
                self.assertEqual(response.status, 200)
                self.assertTrue(response.headers["Content-Type"].startswith(content_type))
                self.assertGreater(int(response.headers["Content-Length"]), 0)

    def test_every_allowlisted_public_asset_matches_its_source(self):
        for route, (source, content_type) in preview.ROUTES.items():
            with self.subTest(route=route), urllib.request.urlopen(self.url + route) as response:
                self.assertEqual(response.status, 200)
                expected = source.read_bytes()
                self.assertTrue(response.headers["Content-Type"].startswith(content_type))
                self.assertEqual(response.read(), expected)

    def test_legacy_landing_route_redirects_to_the_public_shell(self):
        with urllib.request.urlopen(self.url + "/landing.html") as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(response.geturl(), self.url + "/index.html")
            self.assertIn("Authority that stays human", response.read().decode("utf-8"))

    def test_all_shell_links_manifest_icons_and_offline_cache_resolve(self):
        with urllib.request.urlopen(self.url + "/") as response:
            parser = AssetLinkParser()
            parser.feed(response.read().decode("utf-8"))
        base = self.url + "/"
        local_routes = set()
        local_netloc = urlsplit(self.url).netloc
        for raw in parser.urls:
            target = urlsplit(urljoin(base, raw))
            if target.netloc == local_netloc and target.path:
                local_routes.add(target.path)

        with urllib.request.urlopen(self.url + "/manifest.webmanifest") as response:
            manifest = json.loads(response.read())
        for icon in manifest.get("icons", []):
            target = urlsplit(urljoin(base, icon["src"]))
            local_routes.add(target.path)

        # The service worker intentionally caches only the public shell; planner POSTs are never cached.
        local_routes.update(("/", "/index.html", "/launch.css", "/launch.js", "/manifest.webmanifest",
                             "/offline.html", "/assets/vyomaraj-icon.svg", "/assets/vyomaraj-icon-192.png",
                             "/assets/vyomaraj-icon-512.png"))
        for route in sorted(local_routes):
            with self.subTest(route=route), urllib.request.urlopen(self.url + route) as response:
                self.assertEqual(response.status, 200)
                response.read()

    def test_bhakti_plan_is_ephemeral_local_and_has_human_review_gates(self):
        status, headers, plan = self.request_json({
            "experience": "bhakti", "topic_id": "sati-daksha", "recipe_id": "coconut", "mode": "4d"
        })
        self.assertEqual(status, 200)
        self.assertTrue(headers["Content-Type"].startswith("application/json"))
        self.assertEqual(headers["Cache-Control"], "no-store")
        self.assertNotIn("Access-Control-Allow-Origin", headers)
        self.assertLessEqual(int(headers["Content-Length"]), preview.MAX_RESPONSE_BYTES)
        self.assertEqual(plan["status"], "local_plan_created")
        self.assertEqual(plan["experience"], "bhakti")
        self.assertEqual(plan["topic"]["id"], "sati-daksha")
        self.assertEqual(plan["recipe"]["id"], "coconut")
        self.assertIsNone(plan["provider"])
        self.assertFalse(plan["ai_calls_made"])
        self.assertFalse(plan["publishing_enabled"])
        self.assertFalse(plan["production_deployed"])
        self.assertTrue(plan["review_gates"])

    def test_liquor_bar_plan_is_local_and_uses_only_its_fixed_content_pack(self):
        status, _headers, plan = self.request_json({
            "experience": "liquor-bar", "topic_id": "tadi-local", "recipe_id": "chana",
            "mode": "5d", "diet": "plant-based"
        })
        self.assertEqual(status, 200)
        self.assertEqual(plan["topic"]["id"], "tadi-local")
        self.assertEqual(plan["recipe"]["id"], "chana")
        self.assertIsNone(plan["provider"])
        self.assertFalse(plan["ai_calls_made"])
        self.assertFalse(plan["publishing_enabled"])

    def test_endpoint_rejects_other_experiences_unknown_fields_and_malformed_values(self):
        invalid = (
            {"experience": "film", "format": "short"},
            {"experience": "music", "item_ids": ["demo"]},
            {"experience": "bhakti", "provider": "external"},
            {"experience": [], "topic_id": "overview"},
            {"experience": "bhakti", "topic_id": "not-a-known-topic"},
            {"experience": "liquor-bar", "recipe_id": "not-a-known-recipe"},
        )
        for payload in invalid:
            with self.subTest(payload=payload):
                status, _headers, result = self.request_json(payload)
                self.assertEqual(status, 400)
                self.assertIn("error", result)

    def test_endpoint_rejects_duplicate_json_fields(self):
        status, _headers, result = self.request_json(
            b'{"experience":"bhakti","experience":"film"}'
        )
        self.assertEqual(status, 400)
        self.assertIn("Duplicate", result["error"])

    def test_endpoint_enforces_method_query_content_type_and_body_size(self):
        with self.assertRaises(urllib.error.HTTPError) as error:
            urllib.request.urlopen(self.url + "/api/plan")
        error.exception.close()
        self.assertEqual(error.exception.code, 405)
        self.assertEqual(error.exception.headers["Allow"], "POST")
        for method in ("HEAD", "OPTIONS"):
            request = urllib.request.Request(self.url + "/api/plan", method=method)
            with self.subTest(method=method), self.assertRaises(urllib.error.HTTPError) as method_error:
                urllib.request.urlopen(request)
            method_error.exception.close()
            self.assertEqual(method_error.exception.code, 405)
            self.assertNotIn("Access-Control-Allow-Origin", method_error.exception.headers)

        cases = (
            (b"{}", {"Content-Type": "text/plain"}, "/api/plan", 415),
            (b"{}", {}, "/api/plan?topic=sensitive", 400),
            (b"{}", {}, "/not-allowlisted", 404),
            (b"{}", {"Content-Encoding": "gzip"}, "/api/plan", 415),
            (b"x" * (preview.MAX_REQUEST_BYTES + 1), {}, "/api/plan", 413),
        )
        for body, headers, path, expected in cases:
            with self.subTest(path=path, expected=expected):
                status, _response_headers, result = self.request_json(body, headers=headers, path=path)
                self.assertEqual(status, expected)
                self.assertIn("error", result)
        self._assert_catalog_rejects_unapproved_queries_and_write_methods()

    def test_private_repository_and_binary_paths_are_not_served(self):
        for path in (
            "/README.md", "/.git/config", "/ops/jarvis/jarvis.env",
            "/ops/jarvis/devices.json", "/Vyomaraj-App.apk",
            "/ops/vyomaraj-core/bhakti-experience/content.json",
            "/ops/vyomaraj-core/liquor-bar/content.json",
            "/ops/vyomaraj-core/handover/../../../../README.md",
            "/ops/vyomaraj-core/handover/DR_SYNC_RESULTS_2026_10_04.md",
        ):
            with self.subTest(path=path), self.assertRaises(urllib.error.HTTPError) as error:
                urllib.request.urlopen(self.url + path)
            error.exception.close()
            self.assertEqual(error.exception.code, 404)

    def test_post_is_not_a_supported_operation_outside_the_demo_route(self):
        request = urllib.request.Request(self.url + "/", data=b"x", method="POST",
                                         headers={"Content-Type": "application/json"})
        with self.assertRaises(urllib.error.HTTPError) as error:
            urllib.request.urlopen(request)
        error.exception.close()
        self.assertEqual(error.exception.code, 404)

    def test_planning_requests_do_not_modify_source_packs_registry_or_owner_state(self):
        paths = (
            ROOT / "ops/vyomaraj-core/bhakti-experience/content.json",
            ROOT / "ops/vyomaraj-core/liquor-bar/content.json",
            ROOT / "ops/vyomaraj-core/agents/AGENT_REGISTRY_CURRENT.json",
            ROOT / "ops/vyomaraj-core/approvals",
        )

        def fingerprint(path):
            if path.is_file():
                return hashlib.sha256(path.read_bytes()).hexdigest()
            return tuple(sorted(child.name for child in path.iterdir()))

        before = {path: fingerprint(path) for path in paths}
        status, _headers, _plan = self.request_json({"experience": "bhakti", "topic_id": "overview"})
        bhakti_status, _headers, _catalog = self.request_get_json("/api/catalog?experience=bhakti")
        liquor_status, _headers, _catalog = self.request_get_json("/api/catalog?experience=liquor-bar")
        after = {path: fingerprint(path) for path in paths}
        self.assertEqual(status, 200)
        self.assertEqual(bhakti_status, 200)
        self.assertEqual(liquor_status, 200)
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
