#!/usr/bin/env python3
"""collect_server.py - the self-hosted, cookieless event collector.

One stdlib file, one append-only JSONL file, no database, no cookies, no IP logging.
Built for a site hosted on GitHub Pages, which cannot run this: deploy it wherever a process can
run (a container, a tiny VM, a PaaS) and put its HTTPS URL in data/program.json -> measurement.endpoint.
Until you do, the site records nothing remotely - which is a valid state, not a broken one.

Design notes that matter more than the code:
  * No IP address is read or stored. `client_address` is never touched. If you add logging, add it
    somewhere else; this file is the reason we can say "we do not know who visited".
  * No Set-Cookie, ever, so the disclosure obligation about our own cookies stays empty [S19].
  * Origin must match the published site, so this is not an open beacon for someone else's traffic.
  * A rejected payload is logged as its key names only, never as its content.
  * Do not point a load test, a crawler or a CI job at this. Synthetic clicks and impressions are
    prohibited [S12] and would poison the only evidence the project has.

Run:  python3 tools/collect_server.py --host 0.0.0.0 --port 8099 --origin karagemop466-tech.github.io
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import events  # noqa: E402  (same directory; validated against data/events.schema.json)

CONFIG = {"origin": "", "out": None}


class Handler(BaseHTTPRequestHandler):
    server_version = "CounterTestedCollector/1"
    protocol_version = "HTTP/1.1"

    def _cors(self):
        origin = self.headers.get("Origin", "")
        allowed = CONFIG["origin"]
        # sendBeacon/fetch(no-cors) never need CORS headers; we only add them when the operator
        # has explicitly named an origin, so a stray cross-site POST cannot use us.
        if allowed and origin and origin.endswith(allowed):
            return [("Access-Control-Allow-Origin", origin), ("Vary", "Origin")]
        return []

    def do_OPTIONS(self):  # preflight, if and only if an origin was configured
        self.send_response(204)
        for k, v in self._cors():
            self.send_header(k, v)
        self.send_header("Access-Control-Allow-Methods", "POST")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_POST(self):
        if not self.path.startswith("/e"):
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0 or length > 2048:
            self.send_error(413 if length > 2048 else 400, "payload size")
            return
        body = self.rfile.read(length)
        now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
        ok, why = events.accept(body, now)
        self.send_response(204 if ok else 422)
        for k, v in self._cors():
            self.send_header(k, v)
        self.send_header("Content-Length", "0")
        self.end_headers()
        if not ok:
            sys.stderr.write(f"rejected: {why}\n")

    def do_GET(self):
        """Health check only. Deliberately not an API: nothing here reads visitor data out."""
        if self.path.startswith("/healthz"):
            payload = json.dumps({"ok": True, "writes_to": str(CONFIG["out"]), "schema_version": events.schema()[1],
                                  "note": "no read endpoint by design; use python3 tools/events.py report on the host"}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        self.send_error(404)

    def log_message(self, fmt, *args):
        # Access logs would record the client address. We do not want them, so this is the whole
        # logging policy: nothing per-request is written anywhere.
        pass


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1", help="0.0.0.0 to publish it; 127.0.0.1 for local testing")
    ap.add_argument("--port", type=int, default=8099)
    ap.add_argument("--out", default=str(events.EVENTS))
    ap.add_argument("--origin", default="", help="hostname suffix allowed to post, e.g. karagemop466-tech.github.io")
    a = ap.parse_args()
    CONFIG["origin"] = a.origin
    CONFIG["out"] = a.out
    httpd = ThreadingHTTPServer((a.host, a.port), Handler)
    kinds, version = events.schema()
    print(f"collector on http://{a.host}:{a.port}/e  -> {a.out}")
    print(f"  schema v{version}: {', '.join(sorted(kinds))}")
    print("  no cookies · no IP logging · no read API · payloads > 2KB rejected")
    if a.host == "0.0.0.0" and not a.origin:
        print("  WARNING: bound to all interfaces with no --origin. Set the site's host or keep it local.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
