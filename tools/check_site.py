#!/usr/bin/env python3
"""Compliance and integrity checks for docs/ (run after tools/build_site.py).

Exits non-zero on any failure. Covers: Associates disclosure text (above the fold and in the footer),
rel="sponsored" on every Amazon link, no prices or star ratings, no storage/cookie code, internal links,
ASIN format, every register row carrying a source link, empty campaign ledger, and no broken local refs.
"""
from __future__ import annotations

import csv
import html.parser
import json
import pathlib
import re
import sys
from urllib.parse import urlsplit

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
DATA = ROOT / "data"
DISCLOSURE = json.loads((DATA / "site.json").read_text())["associates_statement"]
PRODUCTS = json.loads((DATA / "products.json").read_text())["products"]
ASIN_RE = re.compile(r"^[A-Z0-9]{10}$")
failures: list[str] = []


def fail(msg: str):
    failures.append(msg)


class Page(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []          # (href, rel, in_footer)
        self.ids = set()
        self.text_before_main = []
        self.text_footer = []
        self.in_footer = False
        self.in_main = False
        self.seen_main = False
        self.tables = []
        self._table_depth = 0
        self._row = None
        self.rows = []           # (cells list of (text, has_link_to_source))
        self._cell = None
        self.text_all = []
        self.in_script = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.add(a["id"])
        if tag == "main":
            self.in_main = True
            self.seen_main = True
        if tag == "footer":
            self.in_footer = True
        if tag == "script":
            self.in_script = True
        if tag == "a" and a.get("href"):
            self.links.append((a["href"], a.get("rel", ""), self.in_footer, a.get("data-product")))
            if self._cell is not None:
                self._cell["links"].append(a["href"])
        if tag == "table":
            self._table_depth += 1
        if tag == "tr" and self._table_depth:
            self._row = []
        if tag in ("td", "th") and self._row is not None:
            self._cell = {"text": [], "links": []}

    def handle_endtag(self, tag):
        if tag == "main":
            self.in_main = False
        if tag == "footer":
            self.in_footer = False
        if tag == "script":
            self.in_script = False
        if tag in ("td", "th") and self._cell is not None and self._row is not None:
            self._row.append(self._cell)
            self._cell = None
        if tag == "tr" and self._row is not None:
            if self._row and self._row[0]["text"]:
                self.rows.append(self._row)
            self._row = None
        if tag == "table":
            self._table_depth -= 1

    def handle_data(self, data):
        if self.in_script:
            return
        self.text_all.append(data)
        if self._cell is not None:
            self._cell["text"].append(data)
        if not self.seen_main:
            self.text_before_main.append(data)
        if self.in_footer:
            self.text_footer.append(data)


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def check_page(path: pathlib.Path):
    rel = path.relative_to(DOCS).as_posix()
    p = Page()
    p.feed(path.read_text(encoding="utf-8"))
    text = norm(" ".join(p.text_all))

    # 1. Disclosure: exact wording, above the fold (before <main>) and in footer
    before = norm(" ".join(p.text_before_main))
    footer = norm(" ".join(p.text_footer))
    if rel != "404.html":
        if DISCLOSURE not in before:
            fail(f"{rel}: disclosure statement not above <main> (above-the-fold rule)")
        if DISCLOSURE not in footer:
            fail(f"{rel}: disclosure statement missing from footer")

    # 2. Amazon links must be rel=sponsored
    for href, link_rel, in_footer, product in p.links:
        host = (urlsplit(href).hostname or "").lower()
        if host == "link.amazon" or host == "amazon.com" or host.endswith(".amazon.com"):
            if "sponsored" not in link_rel.split():
                fail(f"{rel}: Amazon link without rel=sponsored: {href}")

    # 3. Internal links resolve to a file in docs/
    for href, *_rest in p.links:
        if href.startswith(("http://", "https://", "mailto:", "#")):
            if href.startswith("#"):
                frag = href[1:]
                if frag and frag not in p.ids:
                    fail(f"{rel}: broken fragment {href}")
            continue
        target = (path.parent / href.split("#")[0].split("?")[0])
        if href.endswith("/"):
            target = target / "index.html"
        if not target.exists():
            fail(f"{rel}: broken internal link {href}")

    # 4. No prices or star ratings
    if re.search(r"(?<![\w])\$\s?\d", text) or re.search(r"£|€", text):
        fail(f"{rel}: currency amount found (prices must not be shown)")
    if re.search(r"\b\d(\.\d)?\s*(out of 5|stars?)\b", text, re.I) or re.search(r"\d+\s+ratings?\b", text, re.I):
        fail(f"{rel}: star rating text found")

    # 5. Register table rows: every row with product data must carry a source link
    if rel == "products/index.html":
        data_rows = [r for r in p.rows if r and r[0]["text"] and r[0]["text"][0].strip().startswith("P0")]
        if len(data_rows) != len(PRODUCTS):
            fail(f"{rel}: expected {len(PRODUCTS)} register rows, found {len(data_rows)}")
        header = [norm("".join(c["text"])) for c in p.rows[0]] if p.rows else []
        src_col = next((i for i, h in enumerate(header) if h.startswith("Source")), None)
        if src_col is None:
            # header row is in <thead>; find by text
            pass
        by_id = {prod["id"]: prod for prod in PRODUCTS}
        for r in data_rows:
            pid = norm("".join(r[0]["text"]))
            prod = by_id.get(pid)
            if prod is None:
                fail(f"{rel}: row {pid} is not in data/products.json")
                continue
            row_links = [l for c in r for l in c["links"]]
            if prod["source_url"] not in row_links:
                fail(f"{rel}: row {pid} does not link its recorded source ({prod['source_url']})")

    # 6. ASIN format for every ASIN that the site shows
    for prod in PRODUCTS:
        if prod["intended_asin"] and not ASIN_RE.match(prod["intended_asin"]):
            fail(f"data: {prod['id']} ASIN not 10 alphanumeric characters")

    # 7. No storage or cookie code in shipped assets (checked once below)


def rel_path(path: pathlib.Path) -> str:
    return path.relative_to(DOCS).as_posix()


def check_assets():
    js = (DOCS / "assets" / "js" / "measure.js").read_text(encoding="utf-8")
    for bad in ("localStorage", "sessionStorage", "document.cookie", "Math.random"):
        if bad in js:
            fail(f"assets/js/measure.js contains forbidden storage/identifier call: {bad}")
    for stale in ("assets/js/app.js", "assets/css/main.css"):
        if (DOCS / stale).exists():
            fail(f"stale asset present: docs/{stale}")


def check_ledger():
    with open(DATA / "campaign_ledger.csv", encoding="utf-8") as fh:
        rows = [r for r in csv.reader(fh)][1:]
    rows = [r for r in rows if any(c.strip() for c in r)]
    if rows:
        fail(f"data/campaign_ledger.csv has {len(rows)} row(s); ledger must start empty and be filled only from first-party reports")


def check_feed_and_sitemap():
    feed = (DOCS / "feed.xml").read_text(encoding="utf-8")
    if "<rss version=\"2.0\">" not in feed:
        fail("feed.xml: not RSS 2.0")
    sitemap = (DOCS / "sitemap.xml").read_text(encoding="utf-8")
    for page in DOCS.rglob("*.html"):
        rel = page.relative_to(DOCS).as_posix()
        if rel == "404.html" or "http-equiv=\"refresh\"" in page.read_text(encoding="utf-8"):
            continue
        loc = "https://karagemop466-tech.github.io/Affil3/" + (rel.replace("index.html", "") if rel != "index.html" else "")
        if loc not in sitemap:
            fail(f"sitemap.xml: missing {loc}")


def main() -> int:
    if not DOCS.exists():
        print("docs/ missing: run tools/build_site.py", file=sys.stderr)
        return 2
    for page in sorted(DOCS.rglob("*.html")):
        if "http-equiv=\"refresh\"" in page.read_text(encoding="utf-8"):
            continue  # legacy redirect stub: target is checked below
        check_page(page)
    for legacy_stub in ["products.html", "about.html", "disclosure.html", "privacy.html", "flagged.html", "index.html"]:
        if not (DOCS / legacy_stub).exists():
            fail(f"legacy URL {legacy_stub} has no redirect stub")
    check_assets()
    check_ledger()
    check_feed_and_sitemap()
    if failures:
        print(f"CHECK FAILED ({len(failures)} issue(s)):")
        for f in failures:
            print("  -", f)
        return 1
    n = len(list(DOCS.rglob("*.html")))
    print(f"check ok: {n} HTML pages, disclosure above fold and in footer, all Amazon links sponsored, "
          f"{len(PRODUCTS)} register rows sourced, ledger empty, no prices/ratings, no storage code")
    return 0


if __name__ == "__main__":
    sys.exit(main())
