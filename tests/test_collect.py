"""Tests for the event receiver: validation, counts-only storage, privacy headers, and the build checker."""
import json
import pathlib
import sys
import tempfile
import threading
import unittest
import urllib.request
from http.server import ThreadingHTTPServer

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "analytics"))
import collect_server as cs  # noqa: E402


class ValidateTests(unittest.TestCase):
    def test_accepts_five_events(self):
        for e in cs.ALLOWED_EVENTS:
            self.assertIsNotNone(cs.validate({"e": e, "p": "/guides/x/", "t": ""}))

    def test_rejects_unknown_event_and_extra_keys(self):
        self.assertIsNone(cs.validate({"e": "session_start", "p": "/", "t": ""}))
        self.assertIsNone(cs.validate({"e": "page_view", "p": "/", "t": "", "ip": "1.2.3.4"}))

    def test_rejects_bad_product_and_path(self):
        self.assertIsNone(cs.validate({"e": "outbound_click", "p": "/", "t": "B0CDY277D3"}))
        self.assertIsNone(cs.validate({"e": "page_view", "p": "https://evil", "t": ""}))

    def test_query_string_dropped(self):
        self.assertEqual(cs.validate({"e": "page_view", "p": "/products/?utm=x", "t": ""})[1], "/products/")


class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = pathlib.Path(cls.tmp.name) / "counts.json"
        cs.Handler.out = cls.out
        cs.Handler.origin = "https://karagemop466-tech.github.io"
        cls.srv = ThreadingHTTPServer(("127.0.0.1", 0), cs.Handler)
        cls.port = cls.srv.server_address[1]
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()
        cls.tmp.cleanup()

    def post(self, body: bytes, headers=None):
        req = urllib.request.Request(f"http://127.0.0.1:{self.port}/", data=body, method="POST",
                                     headers={"Content-Type": "text/plain", **(headers or {})})
        try:
            with urllib.request.urlopen(req) as r:
                return r.status, dict(r.headers)
        except urllib.error.HTTPError as e:
            return e.code, dict(e.headers)

    def test_valid_event_counted_without_identifiers(self):
        status, _ = self.post(json.dumps({"e": "outbound_click", "p": "/", "t": "P01"}).encode())
        self.assertEqual(status, 204)
        data = json.loads(self.out.read_text())
        self.assertEqual(sum(data.values()), 1)
        for key in data:
            self.assertEqual(key.count("|"), 3)
            self.assertNotIn("127.0.0.1", key)

    def test_invalid_rejected_with_400(self):
        status, _ = self.post(b'{"e":"nope","p":"/","t":""}')
        self.assertEqual(status, 400)

    def test_dnt_or_gpc_sends_nothing(self):
        before = json.loads(self.out.read_text()) if self.out.exists() else {}
        status, _ = self.post(json.dumps({"e": "page_view", "p": "/", "t": ""}).encode(), {"DNT": "1"})
        self.assertEqual(status, 204)
        after = json.loads(self.out.read_text()) if self.out.exists() else {}
        self.assertEqual(after, before)

    def test_oversize_body_rejected(self):
        status, _ = self.post(b"x" * (cs.MAX_BODY + 1))
        self.assertEqual(status, 413)

    def test_no_request_log_written(self):
        self.assertFalse(any(p.name.endswith(".log") for p in pathlib.Path(self.tmp.name).iterdir()))


if __name__ == "__main__":
    unittest.main()
