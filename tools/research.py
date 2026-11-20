#!/usr/bin/env python3
"""
research.py — product research through the Amazon Creators API.

Why the Creators API and not PA-API 5: PA-API 5 is deprecated and now returns an
HTTP 403 with an AccessDeniedException. The Creators API is the supported
successor.

  https://affiliate-program.amazon.com/creatorsapi/docs/en-us/paapiv5-deprecation
  https://affiliate-program.amazon.com/creatorsapi/docs/en-us/get-started/using-curl
  https://affiliate-program.amazon.com/creatorsapi/docs/en-us/introduction

This tool never invents a value. If the credentials are missing or the API
refuses the call, it says so and writes nothing. Results are written to
data/research/ with the date they were fetched, so a snapshot always says how
old it is.

Credentials come from the environment, never from the repository:

    export AFFIL3_LWA_CLIENT_ID=...
    export AFFIL3_LWA_CLIENT_SECRET=...
    export AFFIL3_PARTNER_TAG=shopnow047c-20
    export AFFIL3_MARKETPLACE=www.amazon.com

Usage:
    python3 tools/research.py --check
    python3 tools/research.py --items B0CDY277D3,B08DKYBTPH
    python3 tools/research.py --search "dual basket air fryer"
    python3 tools/research.py --node 17659096011
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API_BASE = "https://creatorsapi.amazon"
TOKEN_ENDPOINTS = {
    "NA": "https://api.amazon.com/auth/o2/token",
    "EU": "https://api.amazon.co.uk/auth/o2/token",
    "FE": "https://api.amazon.co.jp/auth/o2/token",
}
SCOPE = "creatorsapi::default"
OUT_DIR = os.path.join(ROOT, "data", "research")


def env(name: str) -> str:
    return os.environ.get(name, "").strip()


def get_token() -> str:
    client_id = env("AFFIL3_LWA_CLIENT_ID")
    client_secret = env("AFFIL3_LWA_CLIENT_SECRET")
    region = env("AFFIL3_LWA_REGION") or "NA"
    if not client_id or not client_secret:
        raise SystemExit(
            "No API credentials found.\n"
            "Set AFFIL3_LWA_CLIENT_ID and AFFIL3_LWA_CLIENT_SECRET in the environment.\n"
            "Creators API access also requires enrolment and at least 10 qualifying sales\n"
            "in the past 30 days:\n"
            "  https://affiliate-program.amazon.com/creatorsapi/docs/en-us/introduction"
        )
    endpoint = TOKEN_ENDPOINTS.get(region.upper(), TOKEN_ENDPOINTS["NA"])
    payload = json.dumps({
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": SCOPE,
    }).encode("utf-8")
    request = urllib.request.Request(
        endpoint, data=payload, method="POST",
        headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:400]
        raise SystemExit(f"token request failed: HTTP {exc.code}\n{detail}")
    token = body.get("access_token")
    if not token:
        raise SystemExit(f"no access_token in the response: {body}")
    return token


def call(operation: str, payload: dict, token: str) -> dict:
    marketplace = env("AFFIL3_MARKETPLACE") or "www.amazon.com"
    partner_tag = env("AFFIL3_PARTNER_TAG")
    if not partner_tag:
        raise SystemExit("AFFIL3_PARTNER_TAG is not set; it is the Associates tracking ID.")
    body = dict(payload)
    body.setdefault("marketplace", marketplace)
    body["partnerTag"] = partner_tag
    request = urllib.request.Request(
        f"{API_BASE}/catalog/v1/{operation}", data=json.dumps(body).encode("utf-8"),
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "x-marketplace": marketplace,
        })
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:600]
        raise SystemExit(f"{operation} failed: HTTP {exc.code}\n{detail}")


def save(operation: str, payload: dict, result: dict) -> str:
    os.makedirs(OUT_DIR, exist_ok=True)
    stamp = date.today().isoformat()
    name = f"{operation.lower()}-{stamp}.json"
    path = os.path.join(OUT_DIR, name)
    snapshot = {
        "fetched_on": stamp,
        "operation": operation,
        "request": {k: v for k, v in payload.items() if k != "resources"},
        "response": result,
    }
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(snapshot, fh, indent=2, ensure_ascii=False)
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Creators API research")
    parser.add_argument("--check", action="store_true", help="check credentials and API reachability")
    parser.add_argument("--items", help="comma-separated ASINs for GetItems")
    parser.add_argument("--search", help="keyword for SearchItems")
    parser.add_argument("--node", help="browse node id for SearchItems")
    parser.add_argument("--resources", default="itemInfo.title,itemInfo.features,browseNodeInfo.browseNodes",
                        help="comma-separated Creators API resources")
    args = parser.parse_args()

    token = get_token()
    print("credentials accepted; access token acquired")

    if args.check:
        print("Creators API is reachable with the supplied credentials.")
        return 0

    resources = [r.strip() for r in args.resources.split(",") if r.strip()]

    if args.items:
        asins = [a.strip().upper() for a in args.items.split(",") if a.strip()]
        if len(asins) > 10:
            print("GetItems accepts at most 10 itemIds per call.", file=sys.stderr)
            return 2
        payload = {"itemIds": asins, "itemIdType": "ASIN", "resources": resources}
        result = call("getItems", payload, token)
        path = save("getItems", payload, result)
        print(f"wrote {path}")
        for item in result.get("itemsResult", {}).get("items", []):
            print(f"  {item.get('asin')}  {item.get('itemInfo', {}).get('title', {}).get('displayValue', '')}")
        return 0

    if args.search or args.node:
        payload = {"resources": resources}
        if args.search:
            payload["keywords"] = args.search
        if args.node:
            payload["browseNodeId"] = args.node
        result = call("searchItems", payload, token)
        path = save("searchItems", payload, result)
        print(f"wrote {path}")
        for item in result.get("searchResult", {}).get("items", []):
            print(f"  {item.get('asin')}  {item.get('itemInfo', {}).get('title', {}).get('displayValue', '')}")
        return 0

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
