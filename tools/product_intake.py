#!/usr/bin/env python3
"""product_intake.py - build a product-intent confirmation record for each submitted link.

What this tool is for, and what it is emphatically not for:

  IS     : normalise a submitted link into a record with the intended identifier, the derived
           candidate listing URL, the confirmation date, the method and the source; keep the
           observed redirect target in a SEPARATE field; refuse to write anything unconfirmed.
  IS NOT : a way to look things up. It never opens a socket to Amazon. The licence excludes robots
           and data-mining against Program Content and bars aggregating/analysing Product
           Advertising Content without written approval [S10][S11][S14], so "resolve the link" is a
           human action whose result is typed in. The tool's job is to make that result auditable.

Usage:
  python3 tools/product_intake.py scan                      # validate + report every record
  python3 tools/product_intake.py add https://link.amazon/XXXXXXXXX
  python3 tools/product_intake.py confirm --slot 1 \
      --observed-redirect 'https://www.amazon.com/dp/B0XXXXXXXX' \
      --title 'Exact listing title as printed' --method SiteStripe --date 2026-11-22
  python3 tools/product_intake.py link --slot 1             # print the compliant outbound href
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRODUCTS = ROOT / "data" / "products.json"
PROGRAM = ROOT / "data" / "program.json"
# Amazon's documented product-page pattern. Used to build a *candidate* URL for a human to click,
# never to assert that anything exists there.
DP = "https://www.amazon.com/dp/{ident}"
IDENT_RE = re.compile(r"[A-Za-z0-9]{6,16}$")


def load():
    return json.loads(PRODUCTS.read_text(encoding="utf-8")), json.loads(PROGRAM.read_text(encoding="utf-8"))


def save(doc):
    PRODUCTS.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def parse_identifier(url: str) -> str:
    tail = url.rstrip("/").split("/")[-1].split("?")[0]
    if not IDENT_RE.match(tail):
        raise SystemExit(f"FATAL: '{tail}' is not a plausible identifier (alphanumeric, 6-16 chars). Refusing to store it as an ASIN.")
    return tail


def report(doc, program) -> int:
    tracking = program["associates"]["tracking_id"]
    rows = doc["products"]
    print(f"product-intent register · {len(rows)} records · gate: allow_live_links={program['commerce_switch']['allow_live_links']}")
    print("-" * 108)
    print(f"{'slot':<5}{'intended id':<14}{'len':<5}{'confirmed url':<16}{'observed redirect':<19}{'link':<9}{'flags':<12}name")
    n_live = 0
    for p in rows:
        n_live += 1 if p["link_state"] == "live" else 0
        print(f"{p['slot']:<5}{p['intended_asin']:<14}{p['intended_asin_char_count']:<5}"
              f"{(p['official_listing_url'] or 'BLANK')[:14]:<16}{(p['observed_redirect_target'] or 'BLANK')[:17]:<19}"
              f"{p['link_state']:<9}{','.join(p['flags']):<12}{(p['product_name'] or 'unconfirmed')[:28]}")
    print("-" * 108)
    print(f"{n_live}/{len(rows)} confirmed · {len(rows) - n_live} held at pending")
    problems = []
    for p in rows:
        if p["intended_asin_char_count"] != len(p["intended_asin"]):
            problems.append(f"slot {p['slot']}: stored char count disagrees with the string")
        if p["link_state"] == "live" and not p["official_listing_url"]:
            problems.append(f"slot {p['slot']}: link_state=live with no confirmed listing URL — a live link requires a dated confirmation")
        if p["link_state"] == "live" and not p["observed_redirect_target"]:
            problems.append(f"slot {p['slot']}: link_state=live but the observed redirect was never recorded (FLG-003 cannot be closed without it)")
        if p["confirmation"]["status"] == "confirmed" and not p["confirmation"]["date"]:
            problems.append(f"slot {p['slot']}: status=confirmed without a date")
        for f in ("product_name", "brand", "price", "rating"):
            if p.get(f) and not p.get("_provenance", {}).get(f):
                problems.append(f"slot {p['slot']}: field '{f}' has a value with no provenance entry — refusing to treat it as verified")
    if problems:
        print("\n".join("  FAIL " + x for x in problems))
        return 1
    print("  OK   every record's intended/observed fields are separate, dated and provenance-checked")
    print(f"  note compliant outbound form is {program['site']['default_marketplace_domain']}/dp/<id>?tag={tracking}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("scan")
    addp = sub.add_parser("add")
    addp.add_argument("url")
    addp.add_argument("--section", default="unsorted")
    cp = sub.add_parser("confirm")
    cp.add_argument("--slot", type=int, required=True)
    cp.add_argument("--observed-redirect", default="")
    cp.add_argument("--title", default="")
    cp.add_argument("--brand", default="")
    cp.add_argument("--category", default="")
    cp.add_argument("--listing-url", default="", help="the official listing URL, read off the address bar")
    cp.add_argument("--method", default="", help="how it was confirmed, e.g. SiteStripe | manual click | Associates Product Links tool")
    cp.add_argument("--date", required=True)
    cp.add_argument("--by", default="", help="who confirmed it (initials are enough)")
    lp = sub.add_parser("link")
    lp.add_argument("--slot", type=int, required=True)
    a = ap.parse_args()

    doc, program = load()
    rows = doc["products"]

    if a.cmd == "scan":
        return report(doc, program)

    if a.cmd == "add":
        ident = parse_identifier(a.url)
        host = urlparse_host(a.url)
        rec = {
            "slot": max(r["slot"] for r in rows) + 1 if rows else 1,
            "slug": ident.lower(),
            "submitted_url": a.url,
            "submitted_host": host,
            "intended_asin": ident,
            "intended_asin_char_count": len(ident),
            "candidate_listing_url": DP.format(ident=ident),
            "candidate_listing_url_basis": "mechanical transform of the supplied identifier into the /dp/ pattern; not verified to resolve",
            "official_listing_url": None,
            "confirmation": {"date": None, "method": None, "confirmed_by": None, "evidence": None, "status": "pending"},
            "observed_redirect_target": None,
            "observed_redirect_note": "not observed - record it with the confirm subcommand",
            "product_name": None, "brand": None, "category_from_listing": None,
            "assumed_shelf_section": a.section,
            "assumed_shelf_section_basis": "operator-supplied at intake time",
            "price": None, "availability": None, "rating": None, "review_count": None, "commission_rate": None,
            "link_state": "pending",
            "flags": ["FLG-002", "FLG-003"],
            "why_no_fields": "nothing confirmed from an official source yet",
            "notes": f"added by {Path(sys.argv[0]).name} on intake",
        }
        rows.append(rec)
        save(doc)
        print(f"added slot {rec['slot']} · {ident} ({len(ident)} chars) · status pending · link_state pending")
        print("next: confirm inside the enrolled account, then re-run scan")
        return 0

    if a.cmd == "confirm":
        p = next((r for r in rows if r["slot"] == a.slot), None)
        if not p:
            raise SystemExit(f"FATAL: no record at slot {a.slot}")
        if not a.method:
            raise SystemExit("FATAL: --method is required. A confirmation without a stated method is not a confirmation.")
        try:
            __import__("datetime").date.fromisoformat(a.date)
        except ValueError:
            raise SystemExit(f"FATAL: --date must be ISO YYYY-MM-DD, got '{a.date}'")
        p["observed_redirect_target"] = a.observed_redirect or None
        if a.listing_url:
            p["official_listing_url"] = a.listing_url
        if a.title:
            p["product_name"] = a.title
            p["_provenance"] = {**p.get("_provenance", {}), "product_name": f"{a.method} on {a.date}"}
        if a.brand:
            p["brand"] = a.brand
            p["_provenance"] = {**p.get("_provenance", {}), "brand": f"{a.method} on {a.date}"}
        if a.category:
            p["category_from_listing"] = a.category
            p["_provenance"] = {**p.get("_provenance", {}), "category_from_listing": f"{a.method} on {a.date}"}
        p["confirmation"] = {"date": a.date, "method": a.method, "confirmed_by": a.by or "unspecified",
                             "evidence": "read from the address bar after following the submitted link" if a.observed_redirect else "no redirect recorded - see FLG-003",
                             "status": "confirmed" if (a.observed_redirect and a.listing_url) else "partial"}
        # price/rating/commission deliberately not settable here: licence-restricted fields [S06][S07]
        p["link_state"] = "live" if (p["official_listing_url"] and p["observed_redirect_target"] and p["confirmation"]["status"] == "confirmed") else "pending"
        p["flags"] = [f for f in p["flags"] if not (p["link_state"] == "live" and f in ("FLG-002", "FLG-005"))]
        save(doc)
        print(f"slot {a.slot}: confirmation {p['confirmation']['status']} on {a.date} via {a.method}; link_state={p['link_state']}")
        if p["link_state"] == "pending":
            print("  still pending because official_listing_url and/or observed_redirect_target are missing")
        print("  reminder: do not place a test order through your own links (prohibited) [S12]")
        return report(doc, program)

    if a.cmd == "link":
        p = next((r for r in rows if r["slot"] == a.slot), None)
        if not p:
            raise SystemExit(f"FATAL: no record at slot {a.slot}")
        if p["link_state"] != "live":
            raise SystemExit(f"FATAL: slot {a.slot} is not confirmed (link_state={p['link_state']}). Refusing to emit a Special Link.")
        dom = program["site"]["default_marketplace_domain"]
        print(f"https://{dom}/dp/{p['intended_asin']}?tag={program['associates']['tracking_id']}")
        print('markup: <a rel="sponsored nofollow noopener" data-affiliate data-slot="%s">Check the current price on Amazon</a>' % p["slot"])
        return 0
    return 0


def urlparse_host(url: str) -> str:
    m = re.match(r"^[a-z]+://([^/]+)", url)
    return m.group(1) if m else "unparsed"


if __name__ == "__main__":
    sys.exit(main())
