#!/usr/bin/env python3
"""campaign_ledger.py - append provenance-checked rows to the campaign ledger.

The ledger exists so that a future decision rests on a dated observation instead of a memory.
It therefore refuses more than it accepts:

  * every row must name the first-party report it came from and the date it was read
  * unknown field names are rejected (the schema is the contract)
  * derived metrics are rejected: no conversion rate, no revenue forecast, no 'score'
  * nothing is ever invented: omit a number, leave it null, and it renders as blank on the site

Sources that are NOT acceptable: your own analytics export (measures clicks, not orders), any
third-party tracker, and anything scraped from Amazon (prohibited) [S10][S14]. The authorized
first-party source is Associates Central > Reports, or a report file you downloaded from it.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "data" / "ledger" / "campaign.jsonl"
PROGRAM = ROOT / "data" / "program.json"
FIELDS = ["timestamp", "source", "report_date", "channel", "tracking_id", "eligible_sessions",
          "clicks", "reported_orders", "items_ordered", "dispatched_revenue", "provenance", "notes"]
NUMERIC = {"eligible_sessions", "clicks", "reported_orders", "items_ordered", "dispatched_revenue"}
FORBIDDEN = {"conversion_rate", "ctr", "revenue_forecast", "expected_commission", "score", "eplevency", "projection", "revenue"}
CHANNELS = ["organic-search", "paid-search", "social", "email-solicited", "direct", "referral", "internal"]


def append_row(row: dict) -> None:
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("append", help="add one dated row")
    p.add_argument("--source", required=True, help="the report this was read from, e.g. 'Associates Central > Reports > Tracking report'")
    p.add_argument("--report-date", required=True, help="YYYY-MM-DD, the date the report covered or was read")
    p.add_argument("--channel", required=True, choices=CHANNELS)
    p.add_argument("--eligible-sessions", type=int)
    p.add_argument("--clicks", type=int)
    p.add_argument("--reported-orders", type=int)
    p.add_argument("--items-ordered", type=int)
    p.add_argument("--dispatched-revenue", type=float, help="only if your report states it; otherwise omit")
    p.add_argument("--who", default="", help="initials of the person who read the report")
    p.add_argument("--notes", default="")

    s = sub.add_parser("show", help="print the ledger as the site sees it")
    s.add_argument("--json", action="store_true")

    x = sub.add_parser("program", help="record account-program facts the site cannot read for itself")
    x.add_argument("--application-date")
    x.add_argument("--qualifying-sales", type=int)
    x.add_argument("--api-access", choices=["yes", "no", "unknown"])
    x.add_argument("--registered-site")
    x.add_argument("--marketplace")

    a = ap.parse_args()

    if a.cmd == "append":
        if not a.source.strip() or "report" not in a.source.lower():
            raise SystemExit("FATAL: --source must name the report you read (it is the provenance trail). Refusing.")
        try:
            d = dt.date.fromisoformat(a.report_date)
        except ValueError:
            raise SystemExit(f"FATAL: --report-date must be ISO YYYY-MM-DD, got '{a.report_date}'")
        if d > dt.date.today():
            raise SystemExit("FATAL: report date in the future.")
        row = {
            "timestamp": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
            "source": a.source, "report_date": a.report_date, "channel": a.channel,
            "tracking_id": json.loads(PROGRAM.read_text())["associates"]["tracking_id"],
            "eligible_sessions": a.eligible_sessions, "clicks": a.clicks,
            "reported_orders": a.reported_orders, "items_ordered": a.items_ordered,
            "dispatched_revenue": a.dispatched_revenue,
            "provenance": f"transcribed by {a.who or 'unspecified'} from {a.source} on {dt.date.today().isoformat()}",
            "notes": (a.notes + " " if a.notes else "") + "orders may still arrive up to 89 days after the click; see S18",
        }
        for k in FORBIDDEN:
            if k in row:
                raise SystemExit(f"FATAL: derived metric '{k}' cannot enter the ledger.")
        append_row(row)
        print("appended:", json.dumps(row, ensure_ascii=False)[:200], "...")
        return 0

    if a.cmd == "show":
        rows = [json.loads(l) for l in LEDGER.read_text(encoding="utf-8").splitlines() if l.strip()] if LEDGER.exists() else []
        if a.json:
            print(json.dumps(rows, indent=2, ensure_ascii=False))
            return 0
        print(f"{len(rows)} row(s) in {LEDGER.relative_to(ROOT)}")
        for r in rows:
            print(f"  {r['report_date']}  {r['channel']:<15} sessions={r['eligible_sessions']} clicks={r['clicks']} orders={r['reported_orders']}  <- {r['source']}")
        if not rows:
            print("  (empty is correct until a dated first-party report exists; the site renders it as blank, not as zero)")
        return 0

    if a.cmd == "program":
        doc = json.loads(PROGRAM.read_text(encoding="utf-8"))
        changed = []
        if a.application_date:
            doc["associates"]["join_clock"]["application_date"] = a.application_date
            changed.append("application_date")
        if a.qualifying_sales is not None:
            doc["associates"]["join_clock"]["qualifying_sales_on_board"] = a.qualifying_sales
            changed.append("qualifying_sales")
        if a.api_access:
            doc["associates"]["api_access"]["creators_or_pa_api_available"] = {"yes": True, "no": False, "unknown": None}[a.api_access]
            changed.append("api_access")
        if a.registered_site:
            doc["associates"]["registered_website_confirmed"] = a.registered_site
            changed.append("registered_website_confirmed")
        if a.marketplace:
            doc["associates"]["account_marketplace_confirmed"] = a.marketplace
            changed.append("account_marketplace_confirmed")
        if a.application_date:
            start = dt.date.fromisoformat(a.application_date)
            end = start + dt.timedelta(days=180)
            doc["associates"]["join_clock"]["deadline"] = end.isoformat()
            doc["associates"]["join_clock"]["days_remaining"] = (end - dt.date.today()).days
            changed.append("deadline/days_remaining")
        PROGRAM.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print("updated data/program.json:", ", ".join(changed) or "nothing")
        j = doc["associates"]["join_clock"]
        if j.get("days_remaining") is not None:
            print(f"  180-day window closes {j['deadline']} ({j['days_remaining']} days from today)")
            print("  rule: 3 qualifying sales inside that window or the application can be withdrawn [S17]")
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
