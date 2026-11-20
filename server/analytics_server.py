#!/usr/bin/env python3
"""Self-hosted analytics endpoint for The Countertop Edit.

Accepts POST /api/collect with JSON events from docs/assets/analytics.js and
appends one JSON line per event to events.jsonl. Deliberately stores NO IP
addresses and NO user identifiers — privacy-preserving by design.

Usage:
    python3 server/analytics_server.py --port 8080

Deploy behind your own host/reverse proxy; bind 0.0.0.0 only on trusted
networks. Standard library only.
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "events.jsonl")
ALLOWED_EVENTS = {"page_view", "product_view", "guide_view", "outbound_click", "conversion"}


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body=b""):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        if body:
            self.wfile.write(body)

    def do_OPTIONS(self):
        self._send(204)

    def do_POST(self):
        if self.path.rstrip("/") != "/api/collect":
            self._send(404, b'{"error":"not found"}')
            return
        length = int(self.headers.get("Content-Length", 0) or 0)
        if length == 0 or length > 16384:
            self._send(400, b'{"error":"bad request"}')
            return
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            self._send(400, b'{"error":"invalid json"}')
            return
        event = payload.get("event")
        if event not in ALLOWED_EVENTS:
            self._send(400, b'{"error":"unknown event"}')
            return
        # Keep only the event, path, channel, and link-level fields. Never log
        # IP addresses, user agents, or anything that could identify a person.
        record = {
            "ts": payload.get("ts") or datetime.now(timezone.utc).isoformat(),
            "event": event,
            "path": payload.get("path"),
            "channel": payload.get("channel"),
        }
        for key in ("product", "guide", "target", "rel"):
            if payload.get(key) is not None:
                record[key] = payload[key]
        with open(LOG, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record) + "\n")
        self._send(200, b'{"ok":true}')

    def log_message(self, fmt, *args):  # keep logs clean; no request details
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=8080)
    args = ap.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Analytics endpoint listening on http://{args.host}:{args.port}/api/collect")
    print(f"Events appended to {LOG} (no IP addresses stored)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
