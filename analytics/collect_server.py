#!/usr/bin/env python3
"""Minimal, self-hosted event receiver for the Countertop Journal.

Stores DAILY COUNTS ONLY, per (date, event, path, product). It keeps no IP addresses, user agents,
referrers, cookies or user identifiers. Accepts only the five event names in data/analytics_events.json.

Run:   python3 analytics/collect_server.py --port 8787 --out analytics/counts.json
Set:   analytics_endpoint in data/site.json to the public HTTPS URL of this server, then rebuild.

GitHub Pages cannot run this process. It must be hosted elsewhere (FLG-004, SUG-02).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ALLOWED_EVENTS = {"page_view", "disclosure_impression", "product_impression", "guide_view", "outbound_click"}
PRODUCT_RE = __import__("re").compile(r"^P\d{2}$")
MAX_BODY = 1024
_lock = threading.Lock()


def clean_path(p: str) -> str | None:
    if not isinstance(p, str) or not p.startswith("/") or len(p) > 200:
        return None
    return p.split("?")[0].split("#")[0]


def validate(payload: dict) -> tuple[str, str, str] | None:
    if set(payload) - {"e", "p", "t"}:
        return None
    e = payload.get("e")
    if e not in ALLOWED_EVENTS:
        return None
    p = clean_path(payload.get("p"))
    if p is None:
        return None
    t = payload.get("t", "") or ""
    if t and not (isinstance(t, str) and PRODUCT_RE.match(t)):
        return None
    return e, p, t


def record(out: pathlib.Path, event: tuple[str, str, str], today: str) -> None:
    e, p, t = event
    key = f"{today}|{e}|{p}|{t}"
    with _lock:
        data = json.loads(out.read_text()) if out.exists() else {}
        data[key] = data.get(key, 0) + 1
        tmp = out.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=1, sort_keys=True))
        tmp.replace(out)


class Handler(BaseHTTPRequestHandler):
    out: pathlib.Path = pathlib.Path("counts.json")
    origin: str = "*"

    server_version = "CountertopCollect/1"
    sys_version = ""

    def log_message(self, *_args):  # no request logging: no IPs or agents written anywhere
        return

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", self.origin)
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_POST(self):
        if self.headers.get("DNT") == "1" or self.headers.get("Sec-GPC") == "1":
            self.send_response(204)
            self._cors()
            self.end_headers()
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = -1
        if length < 0 or length > MAX_BODY:
            self.send_response(413)
            self._cors()
            self.end_headers()
            return
        raw = self.rfile.read(length)
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            payload = None
        event = validate(payload) if isinstance(payload, dict) else None
        if event is None:
            self.send_response(400)
            self._cors()
            self.end_headers()
            return
        record(self.out, event, dt.datetime.now(dt.timezone.utc).date().isoformat())
        self.send_response(204)
        self._cors()
        self.end_headers()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=8787)
    ap.add_argument("--out", default="analytics/counts.json")
    ap.add_argument("--origin", default="https://karagemop466-tech.github.io",
                    help="Allowed CORS origin (the public site origin).")
    args = ap.parse_args()
    Handler.out = pathlib.Path(args.out)
    Handler.origin = args.origin
    ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
