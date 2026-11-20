"""A stdlib event sink for the five events in data/events.json.

    python3 tools/collector.py serve --port 8099        # run it
    python3 tools/collector.py tail --last 20           # read what it took
    python3 tools/collector.py stats                     # daily rollup, no user-level grouping

It is deliberately boring and small: one POST route, an allowlist of five event names, an
append-only JSONL file per UTC day, no IP address read from the socket, no cookie, no user
agent string kept, no cross-day identifier of any kind. That is the whole feature set — the
brief asked for a privacy-preserving click counter, and the shortest way to preserve privacy is
to not collect the things that need protecting.

Set `measurement.endpoint` in data/config.json to the host running this, rebuild, and the front
end starts sending. Until then the pages queue locally and nothing reaches this process, which
is the state the published site is in (FLG-010).
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
import time
from collections import Counter, defaultdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from site_common import DATA, load  # noqa: E402

MAX_BODY = 4096
ALLOWED = tuple(e["name"] for e in load("events.json")["events"])
ALLOWED_KEYS = {
    e["name"]: set(e["properties"].keys()) | {"page", "kind"}
    for e in load("events.json")["events"]
}
PAGE_RE = re.compile(r"^/[A-Za-z0-9._/-]{0,160}$")
SAFE_ID_RE = re.compile(r"^[A-Za-z0-9_:.,-]{0,40}$")
RATE_WINDOW_SECONDS = 1.0
RATE_MAX_PER_WINDOW = 40  # per source path, not per person: we do not identify people


class Sink:
    def __init__(self, directory: Path):
        self.dir = directory
        self.dir.mkdir(parents=True, exist_ok=True)
        self._hits: list[float] = []
        self.rejected: Counter[str] = Counter()

    def path_for(self, day: str) -> Path:
        return self.dir / f"events-{day}.jsonl"

    def accept(self, payload: dict) -> tuple[bool, str]:
        now = time.monotonic()
        self._hits = [t for t in self._hits if now - t < RATE_WINDOW_SECONDS]
        if len(self._hits) >= RATE_MAX_PER_WINDOW:
            self.rejected["rate"] += 1
            return False, "rate"
        self._hits.append(now)

        if not isinstance(payload, dict):
            self.rejected["shape"] += 1
            return False, "shape"
        name = payload.get("event")
        if name not in ALLOWED:
            self.rejected["unknown-event"] += 1
            return False, "unknown-event"
        page = payload.get("page", "")
        if not isinstance(page, str) or not PAGE_RE.match(page) or "?" in page:
            self.rejected["bad-page"] += 1  # a query string could smuggle a token into the log
            return False, "bad-page"
        props = payload.get("props") or {}
        if not isinstance(props, dict):
            self.rejected["bad-props"] += 1
            return False, "bad-props"
        clean: dict = {"page": page}
        for key, value in props.items():
            if key not in ALLOWED_KEYS[name]:
                self.rejected["extra-property"] += 1
                continue
            if isinstance(value, bool) or (isinstance(value, (int, float)) and not isinstance(value, bool)):
                clean[key] = value
            elif isinstance(value, str) and SAFE_ID_RE.match(value):
                clean[key] = value
            elif isinstance(value, list) and all(isinstance(v, str) and SAFE_ID_RE.match(v) for v in value):
                clean[key] = value[:4]
            else:
                self.rejected["dropped-property"] += 1
        ts = payload.get("ts", "")
        if not isinstance(ts, str) or not re.match(r"^\d{4}-\d{2}-\d{2}T", ts):
            ts = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
        record = {"ts": ts, "event": name, "props": clean}
        day = ts[:10]
        with self.path_for(day).open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
        return True, "ok"


def make_handler(sink: Sink):
    class Handler(BaseHTTPRequestHandler):
        server_version = "counterwise-collector/1"

        def _send(self, code: int, body: bytes = b"", ctype: str = "application/json") -> None:
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            # The site may be on a different host once the domain question (Q-07) settles; a
            # wildcard is safe here because nothing identifying is ever returned.
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Headers", "content-type")
            self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            if body:
                self.wfile.write(body)

        def do_OPTIONS(self):  # noqa: N802 - preflight
            self._send(204)

        def do_POST(self):  # noqa: N802
            if self.path.rstrip("/") not in ("/e", "/event", "/api/event"):
                self._send(404, json.dumps({"error": "no such route"}).encode())
                return
            try:
                length = int(self.headers.get("Content-Length") or 0)
            except ValueError:
                length = 0
            if length <= 0 or length > MAX_BODY:
                sink.rejected["size"] += 1
                self._send(413 if length > MAX_BODY else 400, json.dumps({"error": "bad size"}).encode())
                return
            raw = self.rfile.read(length)
            try:
                payload = json.loads(raw.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                sink.rejected["unparseable"] += 1
                self._send(400, json.dumps({"error": "unparseable"}).encode())
                return
            ok, why = sink.accept(payload)
            self._send(202 if ok else 422, json.dumps({"ok": ok, "why": why}).encode())

        def do_GET(self):  # noqa: N802
            if self.path.startswith("/healthz"):
                day = dt.date.today().isoformat()
                f = sink.path_for(day)
                n = sum(1 for _ in f.open()) if f.exists() else 0
                self._send(200, json.dumps({"ok": True, "today": n, "rejected": dict(sink.rejected)}).encode())
                return
            self._send(404, json.dumps({"error": "not found"}).encode())

        def log_message(self, fmt: str, *args) -> None:  # never write client addresses
            sys.stderr.write("%s\n" % (fmt % args))

    return Handler


def serve(host: str, port: int, directory: Path) -> None:
    sink = Sink(directory)
    httpd = ThreadingHTTPServer((host, port), make_handler(sink))
    print(
        f"Counterwise collector on http://{host}:{port} · events {ALLOWED}\n"
        f"writing {directory}/events-YYYY-MM-DD.jsonl · no IPs, no cookies, no user-agent storage\n"
        "Ctrl-C to stop.",
        flush=True,
    )
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    finally:
        httpd.server_close()


def tail(directory: Path, last: int) -> None:
    files = sorted(directory.glob("events-*.jsonl"))
    lines: list[str] = []
    for f in files[-3:]:
        lines.extend(f.read_text(encoding="utf-8").splitlines())
    for line in lines[-last:]:
        print(line)
    if not lines:
        print("(no events yet — which is the expected state while the endpoint is unset)")


def stats(directory: Path) -> None:
    per_day: dict[str, Counter] = defaultdict(Counter)
    for f in sorted(directory.glob("events-*.jsonl")):
        day = f.stem.replace("events-", "")
        for line in f.read_text(encoding="utf-8").splitlines():
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            per_day[day][rec.get("event", "?")] += 1
    if not per_day:
        print("no event files yet")
        return
    for day in sorted(per_day):
        print(day, dict(per_day[day]))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    dir_default = str(DATA / "ledger")

    s = sub.add_parser("serve", help="run the endpoint")
    s.add_argument("--host", default="0.0.0.0")
    s.add_argument("--port", type=int, default=8099)
    s.add_argument("--dir", default=dir_default)

    t = sub.add_parser("tail", help="print recent accepted events")
    t.add_argument("--dir", default=dir_default)
    t.add_argument("--last", type=int, default=20)

    st = sub.add_parser("stats", help="per-day event counts")
    st.add_argument("--dir", default=dir_default)

    args = ap.parse_args(argv)
    directory = Path(args.dir)
    if args.cmd == "serve":
        serve(args.host, args.port, directory)
        return 0
    if args.cmd == "tail":
        tail(directory, args.last)
        return 0
    stats(directory)
    return 0


if __name__ == "__main__":
    sys.exit(main())
