#!/usr/bin/env python3
"""
analytics_sink.py — the self-hosted event collector.

Standard library only. One process serves the static site and collects events.

What it stores per event:
    ts        ISO-8601 timestamp from the server, not the client
    ev        event id, validated against the allowlist
    path      the page path
    sid       a salted hash of the browser's rotating session id
    fields    only the fields the event definition lists

What it never stores:
    the client IP address, the user agent, cookies, referrer URLs,
    advertising identifiers, email addresses, or anything else identifying

The salt lives in the environment (AFFIL3_ANALYTICS_SALT) and never reaches the
browser, so a stored sid cannot be reversed into the value the browser sent.

Usage:
    python3 tools/analytics_sink.py                 # serve on 0.0.0.0:8787
    python3 tools/analytics_sink.py --port 9000
    python3 tools/analytics_sink.py --no-static     # collector only
    python3 tools/analytics_sink.py --summary       # print a summary and exit
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import secrets
import sys
import threading
from collections import Counter, defaultdict
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(ROOT, "data", "config.json")

# The event allowlist. Anything not in here is rejected with a 400.
def load_allowlist() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as fh:
        cfg = json.load(fh)
    return {e["id"]: e for e in cfg["measurement"]["events"]}


ALLOWED = load_allowlist()
FIELDS = {k: set(v["params"]) for k, v in ALLOWED.items()}

PATH_RE = re.compile(r"^[A-Za-z0-9/._~%\-\[\]@!$&'()*+,;=:]{0,400}$")
MAX_BODY = 8 * 1024

_write_lock = threading.Lock()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def salted_hash(value: str, salt: str) -> str:
    return hashlib.sha256((salt + ":" + value).encode("utf-8")).hexdigest()[:32]


def validate(record: dict) -> tuple[bool, str]:
    if not isinstance(record, dict):
        return False, "body must be a JSON object"
    ev = record.get("ev")
    if ev not in ALLOWED:
        return False, "unknown event id"
    path = record.get("path", "")
    if not isinstance(path, str) or not PATH_RE.match(path):
        return False, "path is not a valid page path"
    sid = record.get("sid", "")
    if not isinstance(sid, str) or len(sid) > 128:
        return False, "sid is not a valid session id"
    for key in record:
        if key in ("v", "sid", "ev", "path", "ts"):
            continue
        if key not in FIELDS[ev]:
            return False, f"field '{key}' is not part of event '{ev}'"
    return True, ""


def append_event(record: dict, out_path: str, salt: str) -> dict:
    stored = {
        "ts": now_iso(),
        "ev": record["ev"],
        "path": record.get("path", ""),
        "sid": salted_hash(record.get("sid", ""), salt),
    }
    for key, value in record.items():
        if key in ("v", "sid", "ev", "path", "ts"):
            continue
        if isinstance(value, (int, float, str, bool)):
            stored[key] = value[:200] if isinstance(value, str) else value
    with _write_lock:
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
        with open(out_path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(stored, ensure_ascii=False) + "\n")
    return stored


def summarise(out_path: str) -> dict:
    counts = Counter()
    by_path = defaultdict(Counter)
    days = Counter()
    if not os.path.exists(out_path):
        return {"events": {}, "paths": {}, "days": {}, "total": 0}
    with open(out_path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            counts[rec.get("ev", "?")] += 1
            by_path[rec.get("path", "?")][rec.get("ev", "?")] += 1
            days[str(rec.get("ts", ""))[:10]] += 1
    return {
        "events": dict(counts),
        "paths": {k: dict(v) for k, v in by_path.items()},
        "days": dict(days),
        "total": sum(counts.values()),
    }


class Handler(SimpleHTTPRequestHandler):
    server_version = "Affil3Collector"
    sys_version = ""
    static_root = ROOT
    serve_static = True

    # ---- helpers ---------------------------------------------------------
    def log_message(self, fmt, *args):  # noqa: A003
        if os.environ.get("AFFIL3_QUIET") == "1":
            return
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _cors(self):
        origin = self.headers.get("Origin", "")
        # Reflect the origin only if it is the site we expect, otherwise send none.
        allowed = os.environ.get("AFFIL3_ALLOWED_ORIGIN", "")
        if allowed and origin == allowed:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Access-Control-Allow-Credentials", "false")
        self.send_header("Vary", "Origin")

    def _json(self, code: int, payload: dict):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    # ---- routes ----------------------------------------------------------
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self._cors()
        self.end_headers()

    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/api/health":
            self._json(200, {"ok": True, "events": sorted(ALLOWED), "ts": now_iso()})
            return
        if path == "/api/summary":
            self._json(200, summarise(self.server.out_path))
            return
        if not self.serve_static:
            self._json(404, {"error": "not found"})
            return
        super().do_GET()

    def do_POST(self):
        path = self.path.split("?")[0]
        if path != "/api/collect":
            self._json(404, {"error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = 0
        if length <= 0 or length > MAX_BODY:
            self._json(400, {"error": "empty or oversized body"})
            return
        raw = self.rfile.read(length)
        try:
            record = json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._json(400, {"error": "body is not valid JSON"})
            return
        ok, why = validate(record)
        if not ok:
            self._json(400, {"error": why})
            return
        stored = append_event(record, self.server.out_path, self.server.salt)
        self._json(202, {"ok": True, "sid": stored["sid"], "ts": stored["ts"]})

    def translate_path(self, path):
        path = path.split("?", 1)[0].split("#", 1)[0]
        rel = path.lstrip("/")
        if rel in ("", "index.html"):
            rel = "index.html"
        full = os.path.join(self.static_root, rel)
        if os.path.isdir(full):
            full = os.path.join(full, "index.html")
        return full


def main() -> int:
    parser = argparse.ArgumentParser(description="Self-hosted analytics collector")
    parser.add_argument("--port", type=int, default=int(os.environ.get("AFFIL3_PORT", "8787")))
    parser.add_argument("--host", default=os.environ.get("AFFIL3_HOST", "0.0.0.0"))
    parser.add_argument("--out", default=os.environ.get("AFFIL3_EVENTS", os.path.join(ROOT, "data", "events.ndjson")))
    parser.add_argument("--no-static", action="store_true", help="collector only, do not serve files")
    parser.add_argument("--summary", action="store_true", help="print a summary of the event log and exit")
    args = parser.parse_args()

    if args.summary:
        print(json.dumps(summarise(args.out), indent=2))
        return 0

    salt = os.environ.get("AFFIL3_ANALYTICS_SALT")
    if not salt:
        # A random per-process salt still prevents reversal of the stored hash,
        # but it changes on restart, so a stable salt is better for continuity.
        salt = secrets.token_hex(16)
        sys.stderr.write(
            "warning: AFFIL3_ANALYTICS_SALT is not set; using an ephemeral salt. "
            "Set it in the environment so ids stay comparable across restarts.\n")

    Handler.serve_static = not args.no_static
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    server.out_path = args.out
    server.salt = salt
    sys.stderr.write(f"collector listening on http://{args.host}:{args.port}  events -> {args.out}\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        sys.stderr.write("\nstopping\n")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
