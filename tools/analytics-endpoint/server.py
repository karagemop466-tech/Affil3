#!/usr/bin/env python3
"""The Crisp Index — reference analytics endpoint (stdlib only).

POST /e   {event, path, ts, ref?} -> 204 (appends to events.jsonl)
GET /stats -> aggregate counts JSON
GET /     -> service banner

Privacy contract (README.md): no IP, no user agent, no cookies are stored.
Bind behind TLS before production use.
"""
import json
import os
from collections import Counter
from http.server import BaseHTTPRequestHandler, HTTPServer

EVENTS = {"page_view", "outbound_click", "guide_read", "newsletter_signup", "feedback_click"}
LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "events.jsonl")


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body=b"", ctype="text/plain"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if body:
            self.wfile.write(body)

    def do_OPTIONS(self):
        self._send(204)

    def do_POST(self):
        if self.path != "/e":
            return self._send(404)
        try:
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length) or b"{}")
        except (ValueError, json.JSONDecodeError):
            return self._send(400, b"bad json")
        event = str(data.get("event", ""))
        if event not in EVENTS:
            return self._send(400, b"unknown event")
        row = {
            "event": event,
            "path": str(data.get("path", ""))[:200],
            "ts": data.get("ts"),
            "ref": str(data.get("ref", ""))[:120] or None,
        }
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
        self._send(204)

    def do_GET(self):
        if self.path == "/stats":
            counts = Counter()
            if os.path.exists(LOG):
                with open(LOG, encoding="utf-8") as f:
                    for line in f:
                        try:
                            counts[json.loads(line)["event"]] += 1
                        except (ValueError, KeyError):
                            continue
            self._send(200, json.dumps(dict(counts)).encode(), "application/json")
        else:
            self._send(200, b"tci-count")

    def log_message(self, *_args):
        pass  # no request logging (privacy contract)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8787"))
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
