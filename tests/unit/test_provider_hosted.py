import json
import unittest

import httpx

from troubleshoot.providers.gemma_api import GemmaAPI
from troubleshoot.runtime.ports import RuntimeFailure


def request(**options):
    return {"request": {"complaint": "Synthetic symptom", "provider": "gemma_api",
                        "cloud_consent": True, **options},
            "observation": None, "operations": {}}


def response(output=None, **overrides):
    return {"candidates": [{"finishReason": "STOP", "content": {"parts": [
        {"text": json.dumps(output or {"summary": "Synthetic diagnosis", "action": None})}]}, **overrides}]}


class HostedTests(unittest.IsolatedAsyncioTestCase):
    async def test_valid_response_and_backend_header(self):
        def handler(req):
            self.assertEqual(req.headers["x-goog-api-key"], "synthetic-key")
            self.assertNotIn("synthetic-key", str(req.url))
            self.assertEqual(req.url.host, "generativelanguage.googleapis.com")
            self.assertEqual(json.loads(req.content)["generationConfig"]["thinkingConfig"]["thinkingLevel"], "minimal")
            return httpx.Response(200, json=response())
        provider = GemmaAPI("synthetic-key", transport=httpx.MockTransport(handler))
        self.assertEqual(provider.status()["readiness"], "unverified")
        self.assertIsNone((await provider.decide(request()))["action"])
        self.assertEqual(provider.status()["readiness"], "responding")

    async def test_missing_key_and_non_gemma_model(self):
        for provider, code in ((GemmaAPI(""), "missing_api_key"),
                               (GemmaAPI("fake", "gemini-anything"), "unsupported_model")):
            with self.assertRaises(RuntimeFailure) as caught:
                await provider.decide(request())
            self.assertEqual(caught.exception.code, code)

    async def test_consent_checked_before_network(self):
        def handler(req):
            self.fail("Network must not be reached without consent")
        provider = GemmaAPI("fake", transport=httpx.MockTransport(handler))
        for payload in (request(cloud_consent=False), request(provider="ollama"),
                        {**request(), "images": [{"mime_type": "image/png", "data": b"synthetic"}]}):
            with self.assertRaises(RuntimeFailure):
                await provider.decide(payload)

    async def test_explicit_image_consent_and_inline_image(self):
        def handler(req):
            body = json.loads(req.content)
            self.assertEqual(body["contents"][0]["parts"][1]["inlineData"]["mimeType"], "image/png")
            return httpx.Response(200, json=response())
        provider = GemmaAPI("fake", transport=httpx.MockTransport(handler))
        payload = request(vision_enabled=True, cloud_images_consent=True)
        payload["images"] = [{"mime_type": "image/png", "data": b"synthetic image transport fixture"}]
        await provider.decide(payload)

    async def test_status_codes_are_safe_and_specific(self):
        for status, code in ((401, "hosted_auth_failed"), (403, "hosted_auth_failed"),
                             (404, "model_unavailable"), (429, "hosted_quota"),
                             (500, "hosted_unavailable"), (302, "hosted_unavailable")):
            provider = GemmaAPI("fake", transport=httpx.MockTransport(
                lambda req: httpx.Response(status, text="private upstream error")))
            with self.assertRaises(RuntimeFailure) as caught:
                await provider.decide(request())
            self.assertEqual(str(caught.exception), code)

    async def test_malformed_and_truncated_output(self):
        for payload in ({}, response({"summary": "Synthetic", "action": None, "shell": "bad"}),
                        response(finishReason="MAX_TOKENS"), response({"summary": "Synthetic", "action": {}})):
            provider = GemmaAPI("fake", transport=httpx.MockTransport(lambda req: httpx.Response(200, json=payload)))
            with self.assertRaises(RuntimeFailure) as caught:
                await provider.decide(request())
            self.assertEqual(caught.exception.code, "malformed_decision")

    async def test_timeout_and_oversize(self):
        def timeout(req):
            raise httpx.ReadTimeout("private request detail")
        for handler, code in ((timeout, "hosted_timeout"),
                              (lambda req: httpx.Response(200, content=b"x" * 65_537), "hosted_response_too_large")):
            with self.assertRaises(RuntimeFailure) as caught:
                await GemmaAPI("fake", transport=httpx.MockTransport(handler)).decide(request())
            self.assertEqual(caught.exception.code, code)


    async def test_fenced_json_but_no_surrounding_prose(self):
        for output, valid in (("```json\n{\"summary\":\"Ready\",\"action\":null}\n```", True),
                              ("Run this: {\"summary\":\"Ready\",\"action\":null}", False)):
            payload = response()
            payload["candidates"][0]["content"]["parts"][0]["text"] = output
            provider = GemmaAPI("fake", transport=httpx.MockTransport(lambda req: httpx.Response(200, json=payload)))
            if valid:
                self.assertIsNone((await provider.decide(request()))["action"])
            else:
                with self.assertRaises(RuntimeFailure):
                    await provider.decide(request())


    async def test_diagnosis_excludes_mutations_and_supplies_argument_schema(self):
        def handler(req):
            context = json.loads(json.loads(req.content)["contents"][0]["parts"][0]["text"])
            self.assertNotIn("start_spooler", context["operations"])
            self.assertFalse(context["operations"]["spooler_status"]["arguments_schema"]["additionalProperties"])
            return httpx.Response(200, json=response())
        payload = request(mode="diagnose")
        payload["operations"] = {"spooler_status": {"mutates": False}, "start_spooler": {"mutates": True}}
        await GemmaAPI("fake", transport=httpx.MockTransport(handler)).decide(payload)


    async def test_temporary_busy_retries_once_then_accepts_valid_decision(self):
        calls = []
        def handler(req):
            calls.append(req)
            return httpx.Response(503) if len(calls) == 1 else httpx.Response(200, json=response())
        provider = GemmaAPI("fake", transport=httpx.MockTransport(handler))
        self.assertIsNone((await provider.decide(request()))["action"])
        self.assertEqual(len(calls), 2)

    async def test_persistent_busy_stops_after_two_attempts(self):
        calls = []
        def handler(req):
            calls.append(req)
            return httpx.Response(503)
        with self.assertRaises(RuntimeFailure) as caught:
            await GemmaAPI("fake", transport=httpx.MockTransport(handler)).decide(request())
        self.assertEqual(caught.exception.code, "hosted_busy")
        self.assertEqual(len(calls), 2)
