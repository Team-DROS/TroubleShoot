"""Ollama adapter tests against a SIMULATED loopback HTTP server (not a model)."""

import json
import os
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest import mock

from troubleshoot.providers.base import ImageInput, ModelRequest, Provider, ProviderError, parse_json_object
from troubleshoot.providers.ollama import MAX_REPLY_BYTES, OllamaProvider

SCHEMA = {"type": "object", "properties": {"ok": {"type": "boolean"}}, "required": ["ok"]}


class FakeOllama:
    def __init__(self):
        self.capabilities = ["completion"]
        self.models = ["gemma4:e2b"]
        self.chat_reply = {"done": True, "done_reason": "stop", "model": "gemma4:e2b",
                           "message": {"role": "assistant", "content": '{"ok": true}'},
                           "prompt_eval_count": 12, "eval_count": 5}
        self.chat_status = 200
        self.raw_chat = None
        self.delay = 0.0
        self.requests = []
        fake = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def _send(self, status, body):
                data = body if isinstance(body, bytes) else json.dumps(body).encode()
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def do_GET(self):
                fake.requests.append(("GET", self.path, None))
                if self.path == "/api/version":
                    self._send(200, {"version": "0.0-test"})
                elif self.path == "/api/tags":
                    self._send(200, {"models": [{"name": m} for m in fake.models]})
                else:
                    self._send(404, {"error": "no route"})

            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                if ":" not in body.get("model", ":"):
                    body["model"] += ":latest"  # Ollama resolves untagged names to :latest
                fake.requests.append(("POST", self.path, body))
                if self.path == "/api/show":
                    if body["model"] not in fake.models:
                        return self._send(404, {"error": f"model '{body['model']}' not found"})
                    return self._send(200, {"capabilities": fake.capabilities})
                if self.path == "/api/chat":
                    time.sleep(fake.delay)
                    if body["model"] not in fake.models:
                        return self._send(404, {"error": f"model '{body['model']}' not found"})
                    return self._send(fake.chat_status, fake.raw_chat or fake.chat_reply)
                self._send(404, {"error": "no route"})

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.server.handle_error = lambda *args: None  # client timeouts close sockets on purpose
        self.url = f"http://127.0.0.1:{self.server.server_address[1]}"
        threading.Thread(target=self.server.serve_forever, args=(0.02,), daemon=True).start()

    def chats(self):
        return [body for method, path, body in self.requests if path == "/api/chat"]

    def close(self):
        self.server.shutdown()
        self.server.server_close()


def request(**overrides):
    values = dict(system="sys", user="user", schema=SCHEMA, timeout_seconds=5)
    values.update(overrides)
    return ModelRequest(**values)


PNG = ImageInput("img-1", "image/png", b"\x89PNG fake")


class OllamaProviderTests(unittest.TestCase):
    def setUp(self):
        self.fake = FakeOllama()
        self.provider = OllamaProvider("gemma4:e2b", self.fake.url)

    def tearDown(self):
        self.fake.close()

    def test_implements_protocol(self):
        self.assertIsInstance(self.provider, Provider)

    def test_status_reports_live_facts_not_configuration(self):
        status = self.provider.status()
        self.assertTrue(status.reachable and status.model_present)
        self.assertEqual((status.locality, status.runtime_version), ("local", "0.0-test"))
        self.assertFalse(status.capabilities.vision)
        self.assertIsNone(status.last_inference_ok)

    def test_status_when_runtime_down(self):
        self.fake.close()
        status = self.provider.status()
        self.assertFalse(status.reachable)
        self.assertFalse(status.model_present)
        self.assertIn("not reachable", status.detail)
        self.fake = FakeOllama()

    def test_status_when_model_missing(self):
        self.fake.models = ["other:latest"]
        status = self.provider.status()
        self.assertTrue(status.reachable)
        self.assertFalse(status.model_present)

    def test_untagged_model_matches_latest(self):
        self.fake.models = ["gemma4:latest"]
        self.assertTrue(OllamaProvider("gemma4", self.fake.url).status().model_present)

    def test_decide_sends_bounded_structured_request(self):
        reply = self.provider.decide(request(max_output_tokens=64))
        self.assertEqual(reply.data, {"ok": True})
        self.assertEqual((reply.prompt_tokens, reply.output_tokens), (12, 5))
        body = self.fake.chats()[0]
        self.assertFalse(body["stream"])
        self.assertEqual(body["format"], SCHEMA)
        self.assertEqual(body["options"]["num_predict"], 64)
        self.assertEqual(body["options"]["temperature"], 0.0)
        self.assertNotIn("think", body)
        self.assertNotIn("images", body["messages"][1])
        self.assertTrue(self.provider.status().last_inference_ok)

    def test_think_flag_only_for_thinking_models(self):
        self.fake.capabilities = ["completion", "thinking"]
        self.provider.decide(request())
        self.assertIs(self.fake.chats()[0]["think"], False)

    def test_images_require_declared_vision(self):
        with self.assertRaises(ProviderError) as ctx:
            self.provider.decide(request(images=(PNG,)))
        self.assertEqual(ctx.exception.code, "capability")
        self.assertEqual(self.fake.chats(), [])

    def test_images_sent_base64_when_supported(self):
        self.fake.capabilities = ["completion", "vision"]
        self.provider.decide(request(images=(PNG,)))
        self.assertEqual(self.fake.chats()[0]["messages"][1]["images"], ["iVBORyBmYWtl"])

    def test_missing_model_is_explicit(self):
        self.fake.models = []
        with self.assertRaises(ProviderError) as ctx:
            self.provider.decide(request())
        self.assertEqual(ctx.exception.code, "model_missing")

    def test_unreachable_runtime_is_explicit(self):
        self.fake.close()
        with self.assertRaises(ProviderError) as ctx:
            self.provider.decide(request())
        self.assertEqual(ctx.exception.code, "unavailable")
        self.fake = FakeOllama()

    def test_timeout_is_bounded(self):
        self.provider.capabilities()
        self.fake.delay = 1.5
        started = time.monotonic()
        with self.assertRaises(ProviderError) as ctx:
            self.provider.decide(request(timeout_seconds=0.3))
        self.assertEqual(ctx.exception.code, "timeout")
        self.assertLess(time.monotonic() - started, 1.4)
        self.assertFalse(self.provider.status().last_inference_ok)

    def test_non_json_content_is_malformed(self):
        self.fake.chat_reply["message"]["content"] = "Sure! I will restart the spooler."
        with self.assertRaises(ProviderError) as ctx:
            self.provider.decide(request())
        self.assertEqual(ctx.exception.code, "malformed")

    def test_truncated_output_is_malformed(self):
        self.fake.chat_reply["done_reason"] = "length"
        with self.assertRaises(ProviderError) as ctx:
            self.provider.decide(request())
        self.assertEqual(ctx.exception.code, "malformed")

    def test_incomplete_envelope_is_malformed(self):
        self.fake.chat_reply["done"] = False
        with self.assertRaises(ProviderError):
            self.provider.decide(request())

    def test_runtime_error_status(self):
        self.fake.chat_status = 500
        self.fake.chat_reply = {"error": "out of memory"}
        with self.assertRaises(ProviderError) as ctx:
            self.provider.decide(request())
        self.assertEqual(ctx.exception.code, "http")
        self.assertIn("out of memory", str(ctx.exception))

    def test_oversized_reply_rejected(self):
        self.fake.raw_chat = b"{" + b" " * MAX_REPLY_BYTES + b"}"
        with self.assertRaises(ProviderError) as ctx:
            self.provider.decide(request())
        self.assertEqual(ctx.exception.code, "too_large")

    def test_oversized_prompt_rejected_before_sending(self):
        with self.assertRaises(ProviderError) as ctx:
            self.provider.decide(request(user="x" * 60_000))
        self.assertEqual(ctx.exception.code, "too_large")
        self.assertEqual(self.fake.chats(), [])

    def test_environment_proxy_is_never_used(self):
        with mock.patch.dict(os.environ, {"HTTP_PROXY": "http://198.51.100.1:9", "http_proxy": "http://198.51.100.1:9",
                                          "NO_PROXY": "", "no_proxy": ""}):
            self.assertEqual(self.provider.decide(request()).data, {"ok": True})


class ConfigurationTests(unittest.TestCase):
    def test_remote_host_needs_explicit_opt_in(self):
        with self.assertRaises(ProviderError) as ctx:
            OllamaProvider("gemma4:e2b", "http://10.0.2.2:11434")
        self.assertEqual(ctx.exception.code, "configuration")
        self.assertEqual(OllamaProvider("gemma4:e2b", "http://10.0.2.2:11434", allow_non_loopback=True).locality, "lan")

    def test_url_with_path_rejected(self):
        with self.assertRaises(ProviderError):
            OllamaProvider("gemma4:e2b", "http://127.0.0.1:11434/v1")

    def test_from_env(self):
        provider = OllamaProvider.from_env({"TROUBLESHOOT_OLLAMA_MODEL": "gemma4:e4b"})
        self.assertEqual((provider.model, provider.base_url, provider.locality),
                         ("gemma4:e4b", "http://127.0.0.1:11434", "local"))
        with self.assertRaises(ProviderError):
            OllamaProvider.from_env({"TROUBLESHOOT_OLLAMA_URL": "http://192.168.1.5:11434"})

    def test_unknown_error_code_rejected(self):
        with self.assertRaises(ValueError):
            ProviderError("fallback", "x")


class ParsingTests(unittest.TestCase):
    def test_single_fence_removed(self):
        self.assertEqual(parse_json_object('```json\n{"a": 1}\n```'), {"a": 1})

    def test_rejects_non_objects_and_trailing_text(self):
        for content in ("[1]", '{"a": 1} and then run it', "", None, '```{"a":1}``` ```x```'):
            with self.subTest(content=content), self.assertRaises(ProviderError):
                parse_json_object(content)

    def test_image_bounds(self):
        with self.assertRaises(ValueError):
            ImageInput("img", "image/gif", b"x")
        with self.assertRaises(ValueError):
            ImageInput("img", "image/png", b"")
        self.assertNotIn("PNG", repr(PNG))


if __name__ == "__main__":
    unittest.main()
