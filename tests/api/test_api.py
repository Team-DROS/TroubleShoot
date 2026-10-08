import unittest

from fastapi.testclient import TestClient

from troubleshoot.api.app import create_app
from troubleshoot.runtime.session import SessionManager
from fixtures import FixtureProvider

TOKEN = "test-session-token-" + "x" * 32


class APITests(unittest.TestCase):
    def setUp(self):
        self.manager = SessionManager({"ollama": FixtureProvider(action=False)}, simulation=True)
        self.client = TestClient(create_app(self.manager, TOKEN), base_url="http://127.0.0.1:8765")
        self.client.__enter__()
        self.auth = {"Authorization": f"Bearer {TOKEN}"}

    def tearDown(self):
        self.client.__exit__(None, None, None)

    def test_all_api_surfaces_require_auth(self):
        for path in ("status", "targets", "runs/fake", "runs/fake/events"):
            self.assertEqual(self.client.get("/api/" + path).status_code, 401)
        for path in ("runs", "runs/fake/decision", "runs/fake/cancel"):
            self.assertEqual(self.client.post("/api/" + path, json={}).status_code, 401)

    def test_cross_origin_and_dns_rebinding_rejected(self):
        for header in ({"Origin": "https://evil.example"}, {"Host": "evil.example"},
                       {"Sec-Fetch-Site": "cross-site"}, {"Origin": "null"}):
            response = self.client.get("/api/status", headers={**self.auth, **header})
            self.assertEqual(response.status_code, 403)

    def test_status_distinguishes_fixture(self):
        response = self.client.get("/api/status", headers=self.auth)
        self.assertTrue(response.json()["simulation"])
        self.assertEqual(response.json()["default_provider"], "ollama")
        self.assertEqual(response.headers["cache-control"], "no-store")

    def test_run_sse_completion_and_resume(self):
        response = self.client.post("/api/runs", json={"complaint": "Synthetic"}, headers=self.auth)
        self.assertEqual(response.status_code, 202)
        url = f"/api/runs/{response.json()['run_id']}/events"
        result = self.client.get(url, headers=self.auth)
        self.assertIn("event: complete", result.text)
        self.assertIn('"verdict": "unresolved"', result.text)
        result = self.client.get(url, headers={**self.auth, "Last-Event-ID": "2"})
        self.assertEqual(result.text, "")

    def test_strict_input_and_consent(self):
        for payload in ({"complaint": "a", "extra": 1},
                        {"complaint": "a", "provider": "gemma_api"},
                        {"complaint": "a", "cloud_consent": "false"},
                        {"complaint": "a", "target": {}}, {"complaint": "a" * 20_000}):
            self.assertEqual(self.client.post("/api/runs", json=payload, headers=self.auth).status_code, 400)

    def test_missing_provider_and_vision_fail_honestly(self):
        self.manager.providers.clear()
        result = self.client.post("/api/runs", json={"complaint": "Synthetic"}, headers=self.auth)
        self.assertEqual(result.status_code, 503)
        self.assertEqual(result.json()["error"], "provider_unavailable")

    def test_unknown_run_and_bad_cursor(self):
        self.assertEqual(self.client.get("/api/runs/nope", headers=self.auth).status_code, 404)
