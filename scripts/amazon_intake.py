#!/usr/bin/env python3
"""Validate a submitted Amazon affiliate link without claiming compliance.

Resolves the redirect target (observed fact) and reports it, while keeping the
product-intent fields blank: a redirect target is not proof of intended product.
Human confirmation is required to fill intended_asin / intended_listing_url /
confirmation_date / intended_source. Exit 0 when validation ran (regardless of
network reachability, which is reported honestly). Standard library only.
"""
import argparse
import json
import os
import sys
import urllib.request
import urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def resolve(url):
    opener = urllib.request.build_opener(NoRedirect)
    req = urllib.request.Request(url, headers={"User-Agent": "affil3-intake/1.0"})
    try:
        with opener.open(req, timeout=15) as resp:
            return resp.status, resp.geturl(), None
    except urllib.error.HTTPError as e:
        loc = e.headers.get("Location") if e.headers else None
        return e.code, loc, None
    except Exception as e:
        return None, None, f"{type(e).__name__}: {e}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--link", required=True, help="submitted link to validate")
    ap.add_argument("--validate-only", action="store_true")
    ap.add_argument("--offline", action="store_true", help="skip network; just print the token analysis")
    args = ap.parse_args()

    token = args.link.rstrip("/").rsplit("/", 1)[-1]
    record = {
        "submitted_link": args.link,
        "submitted_token": token,
        "token_length": len(token),
        "token_is_asin_format": len(token) == 10,
        "observed_redirect_target": None,
        "observed_redirect_url": None,
        "observed_note": None,
        # Intent fields stay blank until the owner confirms — never merged with observation.
        "intended_asin": None,
        "intended_listing_url": None,
        "confirmation_date": None,
        "intended_source": None,
    }

    if args.offline:
        record["observed_note"] = "offline mode: network resolution skipped"
    else:
        status, final_url, err = resolve(args.link)
        if err:
            record["observed_note"] = f"resolution failed from this host: {err}"
        elif status and 300 <= status < 400:
            record["observed_note"] = f"redirect not followed (status {status}); final URL not captured"
        elif final_url:
            # capture the dp token from the final URL if present
            match = __import__("re").search(r"/dp/([A-Z0-9]{10})", final_url)
            record["observed_redirect_url"] = final_url
            record["observed_redirect_target"] = match.group(1) if match else None
            if not match:
                record["observed_note"] = "resolved, but no 10-char dp token found in final URL"
        else:
            record["observed_note"] = f"resolution returned status {status}"

    print(json.dumps(record, indent=2))
    print()
    print("NOTE: intent fields are intentionally blank. Confirm the intended product with the owner")
    print("before filling intended_asin / intended_listing_url / confirmation_date / intended_source.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
