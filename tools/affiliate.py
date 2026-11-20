#!/usr/bin/env python3
"""
affiliate.py — link management for the Associates program.

Three jobs:

  1. Build Special Links in the parameter shape Amazon's own API returns.
  2. Resolve a submitted link to its observed destination and report it, without
     ever merging that observation into the product's intent record.
  3. Audit every link this site publishes and fail if one is not a direct,
     tagged Special Link.

Usage:
    python3 tools/affiliate.py --product chefman-dual-basket-6qt
    python3 tools/affiliate.py --link https://link.amazon/B04G1MEwY
    python3 tools/affiliate.py --audit
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sitekit import is_asin, load_json  # noqa: E402

CFG = load_json("config.json")
PRODUCTS = load_json("products.json")["products"]
TAG = CFG["affiliate"]["tracking_id"]
MARKETPLACE = CFG["affiliate"]["marketplace"]

ASIN_RE = re.compile(r"/dp/([A-Z0-9]{10})", re.I)
REDIRECTING_HOSTS = {"link.amazon", "amzn.to", "a.co", "amzn.eu"}


def special_link(asin: str, tag: str = TAG, marketplace: str = MARKETPLACE) -> str:
    """A direct Special Link in the shape the Creators API itself returns.

    Source: https://affiliate-program.amazon.com/creatorsapi/docs/en-us/get-started/using-curl
    """
    if not is_asin(asin):
        raise ValueError(f"not a 10-character ASIN: {asin!r}")
    return f"https://{marketplace}/dp/{asin}?tag={tag}&linkCode=ogi&th=1&psc=1&language=en_US"


def resolve(url: str, timeout: int = 20) -> dict:
    """Follow a submitted link and report where it lands.

    This is an observation. It is never written back into the intent fields.
    """
    request = urllib.request.Request(
        url, method="GET", headers={"User-Agent": "Mozilla/5.0 (compatible; Affil3LinkAudit/1.0)"})
    opener = urllib.request.build_opener(urllib.request.HTTPRedirectHandler)
    try:
        with opener.open(request, timeout=timeout) as response:
            final = response.geturl()
            status = response.status
    except urllib.error.HTTPError as exc:
        final = exc.geturl() if hasattr(exc, "geturl") else ""
        status = exc.code
    except Exception as exc:  # network errors are reported, not guessed around
        return {"ok": False, "error": str(exc), "submitted": url}

    match = ASIN_RE.search(final)
    observed_asin = match.group(1).upper() if match else ""
    host = final.split("/")[2].lower() if "//" in final else ""
    return {
        "ok": True,
        "submitted": url,
        "status": status,
        "final_url": final,
        "final_host": host,
        "observed_asin": observed_asin,
        "is_direct_product_link": bool(observed_asin) and host in ("www.amazon.com", "amazon.com"),
        "is_redirecting": host in REDIRECTING_HOSTS,
        "carries_our_tag": f"tag={TAG}" in final,
    }


def audit() -> int:
    """Check every link this site publishes."""
    problems = []
    checked = 0
    for root, dirs, names in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in {".git", "tools", "__pycache__"}]
        for name in names:
            if not name.endswith(".html"):
                continue
            path = os.path.join(root, name)
            rel = os.path.relpath(path, ROOT)
            with open(path, encoding="utf-8") as fh:
                html = fh.read()
            for match in re.finditer(r'<a\b[^>]*href="(https?://[^"]+)"([^>]*)>', html):
                url, tail = match.group(1), match.group(2)
                if "amazon.com/dp/" not in url:
                    continue
                checked += 1
                if f"tag={TAG}" not in url:
                    problems.append(f"{rel}: missing tag -> {url}")
                if 'rel="sponsored nofollow"' not in tail:
                    problems.append(f"{rel}: not marked sponsored -> {url}")
                if "data-product=" not in tail:
                    problems.append(f"{rel}: no data-product -> {url}")
            if "link.amazon" in html:
                problems.append(f"{rel}: contains a link.amazon URL")

    print(f"checked {checked} published Amazon product links")
    if problems:
        for p in problems:
            print("FAIL  " + p)
        print(f"\n{len(problems)} problem(s)")
        return 1
    print("0 problems")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Affiliates link management")
    parser.add_argument("--product", help="print the Special Link for a product id")
    parser.add_argument("--link", help="resolve a submitted link and report the observation")
    parser.add_argument("--audit", action="store_true", help="audit every published link")
    args = parser.parse_args()

    if args.audit:
        return audit()

    if args.product:
        for p in PRODUCTS:
            if p["id"] == args.product:
                asin = p["observed_redirect"]["target_asin"]
                print(f"{p['display_name']}")
                print(f"  observed ASIN : {asin}")
                print(f"  special link  : {special_link(asin)}")
                print(f"  intended ASIN : {p['intent']['intended_asin'] or '(not confirmed)'}")
                return 0
        print(f"no product with id {args.product!r}", file=sys.stderr)
        return 2

    if args.link:
        result = resolve(args.link)
        print(json.dumps(result, indent=2))
        if result.get("observed_asin"):
            print(f"\nspecial link for the observed target:\n  {special_link(result['observed_asin'])}")
        return 0

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
