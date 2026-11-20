"""Re-capture the listings this site depends on, and rewrite the observation half of the register.

This is the refresh loop behind S-18 (90-day staleness) and the only sanctioned way to change an
`observation.*` field. It never touches `intent.*`: confirmation of what a link was *meant* to
promote is a human act performed inside the Associates account, and no fetch can produce it.

    python3 tools/resolve_links.py            # try to re-fetch every supplied link
    python3 tools/resolve_links.py --offline  # validate the register without any network use
    python3 tools/resolve_links.py --plan     # print the exact URL list it would fetch

From a sandbox or CI runner with no outbound access to amazon.com the run reports
`egress: blocked` for each row and changes nothing. A blocked verification is recorded as a
blocked verification — the tool never writes "unverified" into a field and calls it resolved.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from site_common import DATA, load  # noqa: E402

UA = "Mozilla/5.0 (compatible; CounterwiseVerification/1.0; +https://github.com/karagemop466-tech/Affil3)"
TIMEOUT = 20
TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.S | re.I)


def fetch(url: str) -> tuple[str, str, str]:
    """Return (final_url, title, error)."""
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.8"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:  # noqa: S310 - fixed amazon hosts
            body = resp.read(400_000).decode("utf-8", "replace")
            return resp.geturl(), (TITLE_RE.search(body).group(1).strip() if TITLE_RE.search(body) else ""), ""
    except urllib.error.HTTPError as exc:
        return url, "", f"HTTP {exc.code}"
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return url, "", f"egress: blocked ({type(exc).__name__})"


def plan() -> list[str]:
    return [l["supplied_url"] for l in load("links.json")["links"]]


def run(offline: bool = False) -> int:
    today = dt.date.today().isoformat()
    changes: list[dict] = []
    for url in plan():
        if offline:
            print(f"skip (offline): {url}")
            continue
        final, title, err = fetch(url)
        if err:
            print(f"blocked: {url} -> {err}")
            changes.append({"url": url, "error": err, "attempted": today})
            continue
        asin = (re.search(r"/dp/([A-Za-z0-9]{10})", final) or ["", ""])[1]
        blocked = "checkpoint" in final or not title.startswith("Amazon.com")
        print(f"{'interstitial' if blocked else 'ok'}: {url}\n   -> {final[:110]}\n   title: {title[:110]}")
        changes.append(
            {
                "url": url,
                "final_url": final,
                "listing_asin": asin,
                "title": title,
                "intercepted": blocked,
                "captured": today,
            }
        )
    out = DATA / "ledger" / f"recapture-{today}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"changes": changes, "note": "raw recapture output; a human or the integration session promotes rows into data/links.json observation fields"}, indent=2), encoding="utf-8")
    print(f"\nwrote {out.relative_to(DATA.parent)} · {len(changes)} row(s)")
    if any(c.get("error") for c in changes):
        print("some rows could not be verified from here. The register keeps them as they are: blank where blank, flagged where flagged.")
        return 2
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--offline", action="store_true", help="no network; validate the register only")
    ap.add_argument("--plan", action="store_true", help="print the URL list and exit")
    args = ap.parse_args(argv)
    if args.plan:
        for u in plan():
            print(u)
        return 0
    return run(args.offline)


if __name__ == "__main__":
    sys.exit(main())
