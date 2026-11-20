#!/usr/bin/env python3
"""Validation gate for the Affil3 site and its data. Exits 1 on any failure.

Checks:
  1. Every page has the Associates statement in the disclosure strip and in the footer.
  2. Every link to an Amazon host carries rel="sponsored".
  3. Every internal link resolves to a file under docs/.
  4. Every row of a 'needs-source' table has an official-source link, or is marked
     unverified with an explicit marker (UNVERIFIED, PROPOSED, Brief only, owner brief).
  5. No banned claim phrases appear.
  6. Sitemap lists every HTML page; feed.xml and sitemap.xml parse; robots.txt exists.
  7. Data integrity: every referenced source ID exists; no price is shown without a source;
     every intended ASIN and observed target is stored in separate fields.
Standard library only.
"""
import html.parser
import json
import pathlib
import re
import sys
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
DATA = ROOT / "data"
SITE_BASE = "https://karagemop466-tech.github.io/Affil3/"
STATEMENT = "As an Amazon Associate I earn from qualifying purchases."
AMAZON_HOSTS = {"amazon.com", "www.amazon.com", "link.amazon"}
OFFICIAL_HOSTS = {
    "amazon.com", "www.amazon.com", "affiliate-program.amazon.com", "sell.amazon.com",
    "ftc.gov", "www.ftc.gov", "developers.google.com", "docs.github.com",
    "github.com", "www.sitemaps.org", "creativecommons.org",
}
UNVERIFIED_MARKERS = ["unverified", "proposed", "brief only", "owner brief"]
BANNED = ["best-selling", "amazon's choice", "amazon recommends", "official amazon partner",
          "guaranteed", "#1 pick", "best price"]

failures = []
def fail(where, msg):
    failures.append(f"{where}: {msg}")

class PageParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []           # (href, rel)
        self.tables = []          # dicts: class, rows
        self._table_stack = []
        self._row = None
        self._in_tbody = False
        self.disclosure_text = ""
        self._in_disclosure = 0
        self.footer_text = ""
        self._in_footer = 0
        self.body_text = ""
        self._cur_table_row_text = ""

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = a.get("class", "") or ""
        if tag == "div" and "disclosure" in cls.split():
            self._in_disclosure += 1
        if tag == "footer" and "site-footer" in cls.split():
            self._in_footer += 1
        if tag == "table":
            self._table_stack.append({"class": cls, "rows": []})
        elif tag == "tbody":
            self._in_tbody = True
        elif tag == "tr" and self._table_stack and self._in_tbody:
            self._row = {"class": cls, "hrefs": [], "text": ""}
        elif tag == "a":
            href = a.get("href")
            rel = a.get("rel", "") or ""
            if href is not None:
                self.links.append((href, rel))
                if self._row is not None:
                    self._row["hrefs"].append(href)

    def handle_endtag(self, tag):
        if tag == "div" and self._in_disclosure:
            self._in_disclosure -= 1
        if tag == "footer" and self._in_footer:
            self._in_footer -= 1
        if tag == "tbody":
            self._in_tbody = False
        if tag == "tr" and self._row is not None and self._table_stack:
            self._table_stack[-1]["rows"].append(self._row)
            self._row = None
        if tag == "table" and self._table_stack:
            self.tables.append(self._table_stack.pop())

    def handle_data(self, data):
        if self._in_disclosure:
            self.disclosure_text += data
        if self._in_footer:
            self.footer_text += data
        if self._row is not None:
            self._row["text"] += data
        self.body_text += data

def check_pages():
    pages = sorted(DOCS.rglob("*.html"))
    if not pages:
        fail("docs", "no HTML pages found; run scripts/build_site.py")
        return pages
    for page in pages:
        rel = page.relative_to(DOCS).as_posix()
        p = PageParser()
        p.feed(page.read_text(encoding="utf-8"))

        # 1. disclosure strip and footer
        if STATEMENT not in p.disclosure_text:
            fail(rel, "disclosure strip does not contain the Associates statement")
        if STATEMENT not in p.footer_text:
            fail(rel, "footer does not contain the Associates statement")

        # 2 + 3. links
        for href, rel_attr in p.links:
            u = urlparse(href)
            if u.scheme in ("http", "https"):
                host = u.netloc.lower()
                if host in AMAZON_HOSTS and "sponsored" not in rel_attr.split():
                    fail(rel, f"Amazon link missing rel=sponsored: {href[:90]}")
                continue
            if u.scheme or href.startswith("#") or href == "":
                continue
            target = (page.parent / u.path).resolve() if u.path else page
            if u.path.endswith("/") or (target.is_dir()):
                target = target / "index.html"
            if not target.exists():
                fail(rel, f"broken internal link: {href}")

        # 4. table rows
        for t in p.tables:
            if "needs-source" not in t["class"].split():
                continue
            for r in t["rows"]:
                if "unverified" in r["class"].split():
                    if not any(m in r["text"].lower() for m in UNVERIFIED_MARKERS):
                        fail(rel, f"unverified row lacks a marker: {r['text'][:80]!r}")
                    continue
                official = [h for h in r["hrefs"] if urlparse(h).netloc.lower() in OFFICIAL_HOSTS]
                if not official:
                    fail(rel, f"table row has no official-source link: {r['text'][:80]!r}")

        # 5. banned phrases (visible text only)
        low = p.body_text.lower()
        for b in BANNED:
            if b in low:
                fail(rel, f"banned claim phrase present: {b!r}")
    return pages

def check_sitemap_feed_robots(pages):
    sm = DOCS / "sitemap.xml"
    if not sm.exists():
        fail("sitemap.xml", "missing")
    else:
        try:
            ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            locs = {e.text for e in ET.parse(sm).getroot().findall("s:url/s:loc", ns)}
        except ET.ParseError as e:
            fail("sitemap.xml", f"does not parse: {e}")
            locs = set()
        for page in pages:
            url = SITE_BASE + page.relative_to(DOCS).as_posix()
            if url not in locs:
                fail("sitemap.xml", f"missing page {url}")
        for loc in locs:
            if not loc.startswith(SITE_BASE):
                fail("sitemap.xml", f"URL outside site base: {loc}")
    feed = DOCS / "feed.xml"
    if not feed.exists():
        fail("feed.xml", "missing")
    else:
        try:
            items = ET.parse(feed).getroot().findall("channel/item")
            if len(items) < 1:
                fail("feed.xml", "no items")
            for it in items:
                link = it.findtext("link", "")
                if not link.startswith(SITE_BASE):
                    fail("feed.xml", f"item link outside site base: {link}")
                elif not (DOCS / link[len(SITE_BASE):]).exists():
                    fail("feed.xml", f"item link does not exist: {link}")
        except ET.ParseError as e:
            fail("feed.xml", f"does not parse: {e}")
    if not (DOCS / "robots.txt").exists():
        fail("robots.txt", "missing")
    if not (DOCS / ".nojekyll").exists():
        fail(".nojekyll", "missing (GitHub Pages would run Jekyll)")
    if not (DOCS / "index.html").exists():
        fail("index.html", "missing entry page")

def check_data():
    sources = {s["id"]: s for s in json.loads((DATA / "sources.json").read_text(encoding="utf-8"))["sources"]}
    products = json.loads((DATA / "products.json").read_text(encoding="utf-8"))["products"]
    flags = json.loads((DATA / "flags.json").read_text(encoding="utf-8"))["flags"]
    questions = json.loads((DATA / "questions.json").read_text(encoding="utf-8"))["questions"]
    suggestions = json.loads((DATA / "suggestions.json").read_text(encoding="utf-8"))["suggestions"]
    analysis = json.loads((DATA / "analysis.json").read_text(encoding="utf-8"))["findings"]
    guides = json.loads((DATA / "guides.json").read_text(encoding="utf-8"))["guides"]

    def refs(where, ids):
        for i in ids:
            if i not in sources:
                fail(where, f"unknown source id {i}")

    for p in products:
        pid = p["id"]
        for key in ("intended_asin", "observed_redirect_target", "observed_asin", "asin_match", "confirmation_date", "source_ids"):
            if key not in p:
                fail(f"products.json {pid}", f"missing field {key}")
        refs(f"products.json {pid}", p.get("source_ids", []))
        if p.get("price"):
            fail(f"products.json {pid}", "a price is set but no price source is recorded; prices must stay blank unless verified")
        if p.get("official_listing_url") and not p["official_listing_url"].startswith("https://www.amazon.com/dp/"):
            fail(f"products.json {pid}", "official_listing_url is not an amazon.com /dp/ URL")
        if p.get("observed_asin") and p["observed_asin"] == p["intended_asin"]:
            fail(f"products.json {pid}", "observed ASIN equals intended ASIN but MATCH is not recorded; check asin_match")
    for f in flags:
        refs(f["id"], f.get("source_ids", []))
    for q in questions:
        refs(q["id"], q.get("source_ids", []))
    for s in suggestions:
        refs(s["id"], s.get("source_ids", []))
    for a in analysis:
        refs(a["id"], a.get("source_ids", []))
        if a.get("flag") and a["flag"] not in {f["id"] for f in flags}:
            fail(a["id"], f"references unknown flag {a['flag']}")
    for g in guides:
        refs(g["slug"], g.get("source_ids", []))
        if not (DOCS / "guides" / f"{g['slug']}.html").exists():
            fail(g["slug"], "guide page not generated")
    # Every intended ASIN must be in the separate observed field, never merged
    for p in products:
        if p["asin_match"] == "MISMATCH" and p["observed_asin"] in ("", p["intended_asin"]):
            fail(f"products.json {p['id']}", "MISMATCH requires a different observed ASIN")

def main():
    pages = check_pages()
    check_sitemap_feed_robots(pages)
    check_data()
    if failures:
        print(f"FAILED — {len(failures)} problem(s):")
        for f in failures:
            print("  -", f)
        sys.exit(1)
    print(f"OK — {len(pages)} pages checked: statement present on all; Amazon links sponsored; "
          f"no broken internal links; every needs-source row has an official link or is marked unverified; "
          f"sitemap/feed/robots valid; data references resolve.")

if __name__ == "__main__":
    main()
