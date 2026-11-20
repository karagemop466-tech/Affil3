#!/usr/bin/env python3
"""Re-check the official listing URLs recorded in data/products.json.

Probes each listing URL and prints a verification table. Unreachable hosts
from this sandbox are reported honestly (unreachable-from-sandbox) rather than
silently treated as verified. Standard library only.
"""
import json
import os
import sys
import urllib.request
import urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "products.json")


def probe(url):
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "affil3-source-verify/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status, None
    except urllib.error.HTTPError as e:
        return e.code, "HTTPError"
    except Exception as e:
        return None, type(e).__name__


def main():
    with open(DATA, encoding="utf-8") as fh:
        data = json.load(fh)
    print(f"{'ID':<6} {'Source URL':<46} Status")
    print("-" * 78)
    failures = 0
    for p in data["products"]:
        url = p.get("official_listing_url") or p.get("observed_redirect_url")
        if not url:
            print(f"{p['id']:<6} {'(no listing URL - unverified row)':<46} SKIPPED")
            failures += 1
            continue
        status, err = probe(url)
        if status and 200 <= status < 400:
            print(f"{p['id']:<6} {url:<46} OK (HTTP {status})")
        else:
            print(f"{p['id']:<6} {url:<46} UNVERIFIED-FROM-SANDBOX ({status or err})")
            failures += 1
    print()
    print(f"{failures} source(s) could not be confirmed from this host (network sandbox).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
