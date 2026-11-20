#!/usr/bin/env python3
"""
check_site.py — the release gate.

Fails the build if the published site breaks any of the rules this desk works to.
Every rule below is traceable to a source; the rule id maps to the source in
data/sources.json.

Usage:
    python3 tools/check_site.py            # check the generated site
    python3 tools/check_site.py --strict   # also fail on warnings
"""

from __future__ import annotations

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sitekit import ROOT, esc, load_json  # noqa: E402

CFG = load_json("config.json")
BASE = CFG["site"]["base_url"].rstrip("/")
DISCLOSURE = CFG["affiliate"]["disclosure"]["operating_agreement_sentence"]
TAG = CFG["affiliate"]["tracking_id"]

errors: list[str] = []
warnings: list[str] = []


def err(rule: str, path: str, message: str) -> None:
    errors.append(f"[{rule}] {path}: {message}")


def warn(rule: str, path: str, message: str) -> None:
    warnings.append(f"[{rule}] {path}: {message}")


def html_files() -> list[str]:
    out = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in {".git", "tools", "__pycache__", ".venv", "node_modules"}]
        for name in filenames:
            if name.endswith(".html"):
                out.append(os.path.relpath(os.path.join(dirpath, name), ROOT))
    return sorted(out)


def rel_to_url(rel: str) -> str:
    rel = rel.replace(os.sep, "/")
    if rel.endswith("/index.html"):
        return "/" + rel[: -len("index.html")]
    if rel == "index.html":
        return "/"
    return "/" + rel


HREF_RE = re.compile(r'href="([^"]+)"')
ANCHOR_TAG_RE = re.compile(r'<a\b[^>]*?href="(?P<href>[^"]+)"[^>]*>', re.I)
ANCHOR_RE = re.compile(r'href="(#[^"]+)"')
AMAZON_HREF_RE = re.compile(r'href="(https?://[^"]*amazon[^"]*)"([^>]*)>')
PRICE_RE = re.compile(r"[$£€]\s?\d")
RATING_RE = re.compile(r"\b\d(?:\.\d)?\s*(?:out of 5|stars|★)")
REVIEW_COUNT_RE = re.compile(r"\b\d[\d,]*\s+(?:customer\s+)?reviews\b", re.I)

ALLOWED_EXTERNAL = {
    "amazon.com", "www.amazon.com", "affiliate-program.amazon.com",
    "ftc.gov", "www.ftc.gov", "developers.google.com", "docs.github.com",
    "github.com", "www.github.com", "schema.org",
}


def main() -> int:
    files = html_files()
    if not files:
        err("G0", "-", "no HTML pages found")
        return report()

    built = set()
    for rel in files:
        url = rel_to_url(rel)
        built.add(url)
        if url.endswith(".html"):
            built.add(url[:-5])

    # ---- rule G1: disclosure present on every page ------------------------
    for rel in files:
        with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
            html = fh.read()
        if DISCLOSURE not in html:
            err("G1", rel, "the required Amazon Associates disclosure sentence is missing")
        # it must appear above the fold: check it sits before the first <main>
        main_at = html.find("<main")
        disc_at = html.find(DISCLOSURE)
        if main_at == -1:
            err("G1", rel, "no <main> element found")
        elif disc_at == -1 or disc_at > main_at:
            err("G1", rel, "the disclosure does not appear before the main content")
        if html.count(DISCLOSURE) < 2:
            warn("G1", rel, "the disclosure sentence appears only once (footer repetition expected)")

    # ---- rule G2: outbound product links are Special Links ---------------
    for rel in files:
        with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
            html = fh.read()
        for m in AMAZON_HREF_RE.finditer(html):
            url, tail = m.group(1), m.group(2)
            if "link.amazon" in url or "amzn.to" in url:
                err("G2", rel, f"submitted short link published as an outbound link: {url}")
                continue
            host = url.split("/")[2].lower()
            if host != "www.amazon.com":
                # Amazon's own program documentation is a reference, not a
                # monetised link, so it is not required to carry the tag.
                if "affiliate-program.amazon.com" not in host:
                    err("G2", rel, f"unexpected Amazon host for a link: {url}")
                continue
            if "/dp/" not in url:
                err("G2", rel, f"Amazon shopping link does not point at a product detail page: {url}")
                continue
            if f"tag={TAG}" not in url:
                err("G2", rel, f"Amazon link is missing the Associates tag parameter: {url}")
                continue
            if 'rel="sponsored nofollow"' not in tail:
                err("G2", rel, f"Amazon product link is not marked sponsored nofollow: {url}")
                continue
            if "data-product=" not in tail:
                err("G2", rel, f"Amazon product link carries no data-product attribute: {url}")
                continue
            if "aria-label=" not in tail:
                warn("G2", rel, f"Amazon product link has no aria-label: {url}")

    # ---- rule G3: no submitted short link anywhere in an href -------------
    for rel in files:
        with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
            html = fh.read()
        for href in HREF_RE.findall(html):
            if "link.amazon" in href or "amzn.to" in href:
                err("G3", rel, f"href points at a redirecting short link: {href}")

    # ---- rule G4: internal links resolve ---------------------------------
    for rel in files:
        with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
            html = fh.read()
        for href in HREF_RE.findall(html):
            if href.startswith(("http://", "https://", "mailto:", "tel:", "#")):
                continue
            target = href.split("#")[0].split("?")[0]
            if not target:
                continue
            if target.startswith("/"):
                resolved = target
            else:
                base = os.path.dirname(rel)
                resolved = "/" + os.path.normpath(os.path.join(base, target)).replace(os.sep, "/")
            if resolved.endswith("/"):
                resolved += "index.html"
            if resolved.startswith("//data/"):
                continue  # published data files are served as-is
            if not os.path.exists(os.path.join(ROOT, resolved.lstrip("/"))):
                err("G4", rel, f"broken internal link: {href}")

    # ---- rule G5: external links are on the allowlist --------------------
    for rel in files:
        with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
            html = fh.read()
        for m in ANCHOR_TAG_RE.finditer(html):
            href = m.group("href")
            if not href.startswith(("http://", "https://")):
                continue
            host = href.split("/")[2].lower()
            if host not in ALLOWED_EXTERNAL:
                err("G5", rel, f"external link to an unexpected host: {host}")

    # ---- rule G6: every page has title, description, canonical -----------
    for rel in files:
        with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
            html = fh.read()
        if "<title>" not in html:
            err("G6", rel, "no <title>")
        if 'name="description"' not in html:
            err("G6", rel, "no meta description")
        if 'rel="canonical"' not in html:
            err("G6", rel, "no canonical link")
        if 'property="og:image"' not in html:
            warn("G6", rel, "no og:image")

    # ---- rule G7: sitemap and feed cover the published pages -------------
    sitemap_path = os.path.join(ROOT, "sitemap.xml")
    with open(sitemap_path, encoding="utf-8") as fh:
        sitemap = fh.read()
    for rel in files:
        url = rel_to_url(rel)
        if url in ("/404.html",):
            continue
        if url.endswith(".html") and not url.endswith("/index.html"):
            continue
        if f"<loc>{BASE}{esc(url)}</loc>" not in sitemap:
            err("G7", rel, "page is not listed in sitemap.xml")
    feed_path = os.path.join(ROOT, "feed.xml")
    with open(feed_path, encoding="utf-8") as fh:
        feed = fh.read()
    guides = load_json("guides.json")["guides"]
    for g in guides:
        if f"{BASE}/guides/{g['slug']}/</link>" not in feed:
            err("G7", f"guides/{g['slug']}", "guide is not listed in feed.xml")

    # ---- rule G8: no published prices and no published ratings -----------
    for rel in files:
        with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
            html = fh.read()
        text = re.sub(r"<[^>]+>", " ", html)
        text = re.sub(r"\s+", " ", text)
        for m in PRICE_RE.finditer(text):
            snippet = text[max(0, m.start() - 60): m.end() + 60]
            if "USD" in snippet or "price" in snippet.lower():
                err("G8", rel, f"a currency figure appears in page text: …{snippet.strip()}…")
        for m in RATING_RE.finditer(text):
            snippet = text[max(0, m.start() - 70): m.end() + 70]
            err("G8", rel, f"a star rating appears in page text: …{snippet.strip()}…")
        for m in REVIEW_COUNT_RE.finditer(text):
            snippet = text[max(0, m.start() - 70): m.end() + 70]
            err("G8", rel, f"a review count appears in page text: …{snippet.strip()}…")

    # ---- rule G9: the product register keeps intent and observation apart -
    products = load_json("products.json")["products"]
    for p in products:
        intent = p["intent"]
        if intent["intended_asin"] or intent["intended_listing_url"]:
            if not (intent["confirmation_date"] and intent["intended_source"]):
                err("G9", f"products/{p['id']}",
                    "an intended ASIN is present without a confirmation date and source")
        observed = p["observed_redirect"]["target_asin"]
        if observed == intent["intended_asin"]:
            err("G9", f"products/{p['id']}",
                "the intended ASIN and the observed redirect target are identical values "
                "recorded in both fields")

    # ---- rule G10: the ledger ships empty --------------------------------
    ledger = os.path.join(ROOT, "data", "ledger.csv")
    with open(ledger, encoding="utf-8") as fh:
        rows = [ln for ln in fh.read().strip().splitlines() if ln.strip()]
    if len(rows) > 1:
        warn("G10", "data/ledger.csv",
             f"the ledger has {len(rows) - 1} data rows; every row must come from an "
             "authorised first-party report")

    # ---- rule G11: every product page carries its source link ------------
    for p in products:
        page = os.path.join(ROOT, "products", p["id"], "index.html")
        if not os.path.exists(page):
            err("G11", f"products/{p['id']}", "no product page was generated")
            continue
        with open(page, encoding="utf-8") as fh:
            html = fh.read()
        if p["observed_redirect"]["target_url"] not in html:
            err("G11", f"products/{p['id']}", "the official listing URL is not on the page")
        if p["observed_redirect"]["observed_on"] not in html:
            err("G11", f"products/{p['id']}", "the observation date is not on the page")

    return report()


def report() -> int:
    for w in warnings:
        print("WARN  " + w)
    for e in errors:
        print("FAIL  " + e)
    print()
    if errors:
        print(f"{len(errors)} violation(s), {len(warnings)} warning(s)")
        return 1
    if warnings and "--strict" in sys.argv:
        print(f"0 violations, {len(warnings)} warning(s) (strict mode)")
        return 1
    print(f"0 violations, {len(warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
