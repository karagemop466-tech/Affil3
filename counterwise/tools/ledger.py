"""Append rows to the campaign ledger, with the gate that the brief asks for.

The automation-friendly half (clicks, sessions) is written by machines. The Amazon-side half
(orders, commission, product category) may only come from an authorized first-party report, and
this tool refuses to write those numbers without a named source and a named retriever. That is
the entire design: automate arithmetic, gate claims.

    python3 tools/ledger.py status
    python3 tools/ledger.py append --date 2026-12-01 --channel search --clicks 41 \\
        --source "Associates Central → Reports → Earnings" --by arena-c7a56e3d
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from site_common import DATA, load  # noqa: E402

LEDGER = DATA / "ledger" / "campaign_ledger.csv"
COLUMNS = [
    "date",
    "source",
    "channel",
    "eligible_sessions",
    "clicks",
    "reported_orders",
    "reported_commission",
    "product_category_as_reported",
    "retrieved_by",
    "provenance_note",
]
CHANNELS = ("search", "social", "newsletter", "direct", "other")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class Refused(Exception):
    pass


def read_rows() -> list[dict]:
    if not LEDGER.exists():
        return []
    with LEDGER.open(encoding="utf-8") as fh:
        return [dict(r) for r in csv.DictReader(fh)]


def attribution_of(referred: str) -> str:
    """The documented, deliberately coarse rule from data/ledger/README.md."""
    host = (referred or "").lower()
    if "newsletter" in host or "utm_source=newsletter" in host:
        return "newsletter"
    if any(k in host for k in ("google.", "bing.", "duckduckgo", "yandex", "search.")):
        return "search"
    if any(k in host for k in ("facebook", "instagram", "reddit", "pinterest", "t.co", "twitter", "youtube", "tiktok", "linkedin")):
        return "social"
    if not host or host == "-":
        return "direct"
    return "other"


def validate(row: dict) -> dict:
    if not DATE_RE.match(row.get("date", "")):
        raise Refused("date must be YYYY-MM-DD (UTC), because the report period is what a row means")
    if row.get("channel") and row["channel"] not in CHANNELS:
        raise Refused(f"channel must be one of {CHANNELS}")
    numbers = ("eligible_sessions", "clicks", "reported_orders")
    for key in numbers:
        val = row.get(key, "")
        if val and not re.match(r"^\d+$", str(val)):
            raise Refused(f"{key} must be a non-negative whole number, not {val!r}")
    if row.get("reported_commission") and not re.match(r"^\d+(\.\d+)?$", str(row["reported_commission"])):
        raise Refused("reported_commission must be a plain decimal with no currency symbol")
    money_or_orders = any(row.get(k) for k in ("reported_orders", "reported_commission", "product_category_as_reported"))
    if money_or_orders:
        if not row.get("source"):
            raise Refused(
                "orders, commission and category are Amazon-side numbers: name the report they came from. "
                "This is the gate the brief asks for; nothing here may be modelled from clicks."
            )
        if not row.get("provenance_note"):
            raise Refused("an Amazon-side row needs a provenance note: export filename, screenshot path or report id")
        if row.get("retrieved_by") in ("", "agent-unattended", "automation"):
            raise Refused(
                "an unattended agent may not record what Amazon reports. Run the fetch yourself, or point a "
                "scheduled workflow at an authorized export and name that workflow in retrieved_by."
            )
    if not row.get("retrieved_by"):
        raise Refused("every row names who pulled it")
    return row


def append(row: dict) -> None:
    validate(row)
    exists = LEDGER.exists() and LEDGER.stat().st_size > 0
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=COLUMNS, lineterminator="\n")
        if not exists:
            writer.writeheader()
        writer.writerow({k: row.get(k, "") for k in COLUMNS})


def status() -> int:
    rows = read_rows()
    print(f"ledger: {len(rows)} row(s) in {LEDGER.relative_to(LEDGER.parents[1])}")
    if not rows:
        print(
            "  empty, which is the accurate state: no clicks have been counted and no Amazon report\n"
            "  has been read into a row. See FLG-010 and the metrics page."
        )
        return 0
    for r in rows:
        print("  ", {k: v for k, v in r.items() if v})
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status", help="how many rows exist")

    a = sub.add_parser("append", help="add one row, if it can survive the provenance rule")
    a.add_argument("--date", required=True)
    a.add_argument("--channel", default="", choices=list(CHANNELS) + [""])
    a.add_argument("--eligible-sessions", default="")
    a.add_argument("--clicks", default="")
    a.add_argument("--reported-orders", default="")
    a.add_argument("--reported-commission", default="")
    a.add_argument("--category", default="", help="product category string, verbatim from the report")
    a.add_argument("--source", default="", help="the exact report the numbers came from")
    a.add_argument("--by", required=True, help="who retrieved it")
    a.add_argument("--note", default="", help="export file, screenshot path or report id")

    g = sub.add_parser("attribute", help="apply the documented channel rule to a referrer")
    g.add_argument("referrer")

    args = ap.parse_args(argv)
    if args.cmd == "status":
        return status()
    if args.cmd == "attribute":
        print(args.referrer or "(none)", "->", attribution_of(args.referrer))
        return 0
    row = {
        "date": args.date,
        "channel": args.channel,
        "eligible_sessions": args.eligible_sessions,
        "clicks": args.clicks,
        "reported_orders": args.reported_orders,
        "reported_commission": args.reported_commission,
        "product_category_as_reported": args.category,
        "retrieved_by": args.by,
        "source": args.source,
        "provenance_note": args.note,
    }
    try:
        append(row)
    except Refused as exc:
        print(f"REFUSED: {exc}")
        return 1
    print("appended:", {k: v for k, v in row.items() if v})
    return 0


if __name__ == "__main__":
    sys.exit(main())
