#!/usr/bin/env python3
"""events.py - the event schema, its validator, and the local report.

Single source of truth for what may be recorded: data/events.schema.json. Anything the collector
receives that is not in that file is rejected and counted, never quietly stored.

Why the collector is this narrow: the Participation Requirements prohibit artificially generating
clicks or impressions [S12], so no test harness may fire events into the stream; and the site
owner is responsible for third-party tracking disclosure [S19], so we record the minimum that
answers the question being asked and disclose exactly that in the privacy page.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "data" / "events.schema.json"
LEDGER_DIR = ROOT / "data" / "ledger"
EVENTS = LEDGER_DIR / "events.jsonl"
UNREJECTED = LEDGER_DIR / "events.rejected.log"

UNIVERSAL = {"ts", "ev", "path", "sid", "v"}
IDENTITYISH = re.compile(r"(ip|ua|useragent|email|cookie|fingerprint|client_id|clientId|session_id_persist|uid)", re.I)


def schema():
    s = json.loads(SCHEMA.read_text(encoding="utf-8"))
    return {e["name"]: e for e in s["events"]}, s["version"]


def validate(obj: dict) -> tuple[bool, str]:
    kinds, version = schema()
    if not isinstance(obj, dict):
        return False, "not an object"
    ev = obj.get("ev")
    if ev not in kinds:
        return False, f"unknown event '{ev}'"
    for k in ("path", "sid"):
        if not isinstance(obj.get(k), str) or not obj[k]:
            return False, f"missing {k}"
    if not isinstance(obj.get("v"), int) or obj["v"] != version:
        return False, f"schema version must be {version}"
    allowed = UNIVERSAL | set(kinds[ev]["extra_fields"])
    extra = set(obj) - allowed
    if extra:
        return False, f"fields outside the schema for {ev}: {sorted(extra)}"
    for k in obj:
        if IDENTITYISH.search(k):
            return False, f"field '{k}' looks like an identifier; this schema forbids it"
    if isinstance(obj.get("sid"), str) and len(obj["sid"]) > 40:
        return False, "sid too long to be ephemeral"
    return True, ""


def accept(payload: bytes, now_iso: str) -> tuple[bool, str]:
    """Store one event. The timestamp is set here, from the server clock, never trusted from the client."""
    if len(payload) > 2048:
        return False, "payload over 2KB"
    try:
        obj = json.loads(payload.decode("utf-8"))
    except Exception as e:  # malformed input is a rejection, not a crash
        return False, f"invalid json ({e})"
    ok, why = validate(obj)
    if not ok:
        _reject(why, obj)
        return False, why
    obj["ts"] = now_iso
    LEDGER_DIR.mkdir(parents=True, exist_ok=True)
    with EVENTS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "\n")
    return True, "ok"


def _reject(why: str, obj):
    LEDGER_DIR.mkdir(parents=True, exist_ok=True)
    with UNREJECTED.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"why": why, "keys": sorted(obj) if isinstance(obj, dict) else str(obj)[:80]}, ensure_ascii=False) + "\n")


def report() -> int:
    if not EVENTS.exists():
        print(f"no event stream at {EVENTS.relative_to(ROOT)} yet.")
        print("  correct state: the site's measurement.endpoint is unconfigured, so nothing is collected.")
        print("  to see it work: python3 tools/collect_server.py --port 8099   (then interact with the site as a reader)")
        return 0
    kinds, version = schema()
    rows, bad = [], 0
    for line in EVENTS.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            bad += 1
    c = Counter(r.get("ev") for r in rows)
    print(f"{len(rows)} events (schema v{version}) · {bad} unparseable line(s)")
    for name in kinds:
        print(f"  {name:<30}{c.get(name, 0)}")
    for other in sorted(set(c) - set(kinds)):
        print(f"  {other:<30}{c[other]}  <- outside schema; investigate")
    paths = Counter(r.get("path") for r in rows)
    print("top paths:")
    for p, n in paths.most_common(8):
        print(f"  {n:>5}  {p}")
    clicks = [r for r in rows if r.get("ev") == "outbound_click"]
    if clicks:
        by_slot = Counter(r.get("product_slot") for r in clicks)
        print(f"outbound clicks: {len(clicks)} across {len(by_slot)} slots -> " + ", ".join(f"slot {k}:{v}" for k, v in by_slot.most_common()))
        tagged = sum(1 for r in clicks if r.get("tag_present") is True)
        print(f"  tag_present on {tagged}/{len(clicks)} clicks (a shortfall here means a mis-built link, not a reader problem)")
    if UNREJECTED.exists():
        n = len(UNREJECTED.read_text(encoding='utf-8').splitlines())
        print(f"  {n} rejected payloads logged in data/ledger/{UNREJECTED.name}")
    print("\nNote: counts only. No conversion rate is computed here - orders arrive from Amazon's reports,")
    print("on a window that stays open for 89 days, and belong in the campaign ledger with a source line.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "validate":
        ok, why = validate(json.loads(sys.stdin.read()))
        print("valid" if ok else f"INVALID: {why}")
        sys.exit(0 if ok else 1)
    sys.exit(report())
