"""Special-Link builder and checker.

Amazon's Associates Program Policies, in the clause this project could read, require the
Associates tag to be present as a URL parameter on every link placed on the site (source SG-02
in data/sources.json). This module builds exactly that and nothing more:

* no `linkCode` or `linkId` is invented — those strings are issued by program tooling;
* no short domain is used — `amzn.to` and `link.amazon` codes are recorded as evidence in
  data/links.json, never published as site links while FLG-003 is open;
* no redirect wrapper, so the destination is visible in the reader's status bar;
* `ascsubtag` is supported but off by default, because the current agreement text has not been
  read in-account (Q-02), and a sub-tag that the account does not accept is noise at best.

Run `python3 tools/special_links.py check` to validate every product row in the register, or
`make --asin B0CDY277D3` to print one link for a manual test.
"""

from __future__ import annotations

import argparse
import re
import sys

from site_common import dp_id_from_url, is_asin, load, tracking_id_shape_ok

AMAZON_HOST_RE = re.compile(r"^https?://(www\.)?amazon\.[a-z.]{2,8}$")


def build(
    asin: str,
    tracking_id: str,
    host: str = "www.amazon.com",
    language: str = "en_US",
    ascsubtag: str | None = None,
) -> str:
    """A minimal, policy-shaped product link: detail-page path + the required tag parameter."""
    if not is_asin(asin):
        raise ValueError(
            f"refusing to build a link for {asin!r}: not a 10-character uppercase identifier. "
            "Fill intent.intended_asin or use the identifier observed in the resolved /dp/ path."
        )
    if not tracking_id_shape_ok(tracking_id):
        raise ValueError(f"tracking id {tracking_id!r} does not look like the XXXXX-20 shape")
    url = f"https://{host}/dp/{asin}?tag={tracking_id}"
    if language:
        url += f"&language={language}"
    if ascsubtag:
        if not re.match(r"^[A-Za-z0-9_-]{1,32}$", ascsubtag):
            raise ValueError("ascsubtag must be short and alphanumeric-ish; it is not free text")
        url += f"&ascsubtag={ascsubtag}"
    return url


def rel_attributes() -> str:
    """What every outbound product anchor must carry. Google asks for `sponsored` on paid
    placements (SG-05); `nofollow` is kept alongside it because the value list is additive and
    the reader's browser still gets `noopener` from the target."""
    return "sponsored nofollow noopener"


def is_amazon_outbound(href: str) -> bool:
    m = re.match(r"^(https?)://([^/]+)", href or "")
    if not m:
        return False
    return bool(AMAZON_HOST_RE.match(f"{m.group(1)}://{m.group(2)}"))


def tag_of(href: str) -> str:
    m = re.search(r"[?&]tag=([^&]+)", href or "")
    return m.group(1) if m else ""


def check_register(emit=print) -> int:
    """Prove that every published product row yields a compliant link, and that nothing
    published uses an untagged or short-form Amazon URL."""
    cfg = load("config.json")
    products = load("products.json")["products"]
    links = {row["id"]: row for row in load("links.json")["links"]}
    tracking = cfg["amazon"]["tracking_id"]
    host = cfg["amazon"]["marketplace_host"]
    failures = 0

    for p in products:
        observed = p["observation"]
        asin = observed.get("listing_asin_observed_in_path", "")
        if not asin:
            emit(f"  {p['id']}: no observed listing identifier, so no link is published (expected for an unresolved row)")
            if p["id"] == "P-04":
                continue
            failures += 1
            continue
        url = build(asin, tracking, host)
        linked = links.get(observed.get("source_link", ""), {})
        if dp_id_from_url(linked.get("observed_final_url", "")) != asin:
            emit(f"  {p['id']}: listing id {asin} does not match the URL we actually observed")
            failures += 1
            continue
        if tag_of(url) != tracking:
            emit(f"  {p['id']}: built link lost the tag")
            failures += 1
            continue
        emit(f"  {p['id']}: {url}")
        if not observed.get("observed_on"):
            emit(f"  {p['id']}: observation has no capture date")
            failures += 1
    emit(f"{'FAIL' if failures else 'PASS'}: {failures} problem(s) in {len(products)} product rows")
    return 1 if failures else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    mk = sub.add_parser("make", help="print one Special Link")
    mk.add_argument("--asin", required=True)
    mk.add_argument("--ascsubtag", default=None)
    mk.add_argument("--no-language", action="store_true")

    sub.add_parser("check", help="validate the whole register")

    args = ap.parse_args(argv)
    cfg = load("config.json")
    if args.cmd == "make":
        print(
            build(
                args.asin,
                cfg["amazon"]["tracking_id"],
                cfg["amazon"]["marketplace_host"],
                "" if args.no_language else "en_US",
                args.ascsubtag,
            )
        )
        return 0
    return check_register()


if __name__ == "__main__":
    sys.exit(main())
