#!/usr/bin/env python3
"""Independent checks on the generated docs/ site. Standard library only.

Checks:
  1. Every HTML page: disclosure strip with the exact Associates sentence,
     directly under the masthead, and repeated in the footer.
  2. Every link to amazon.com or link.amazon has rel containing "sponsored",
     and is followed by a "(paid link)" label.
  3. Every internal link and fragment resolves to a file and id in docs/.
  4. Every external link host is on the allowlist.
  5. Every data table (class "data") has, in each body row, at least one
     link to an allowed official host.
  6. No price-like strings ("$" followed by a digit) in page text.
  7. No Amazon endorsement claims ("Amazon recommends", "Amazon's Choice",
     "endorsed by Amazon", and similar).
  8. Each page has a title, a meta description and a canonical link.
  9. sitemap.xml lists exactly the built pages; feed.xml items match guides.
 10. Tables marked "options" or "schema" are exempt from check 5.

Exit status is non-zero if any check fails.
"""
import glob
import json
import os
import posixpath
import re
import sys
import urllib.parse
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.environ.get("DOCS_DIR") or os.path.join(ROOT, "docs")
REG = os.path.join(ROOT, "register")

SENTENCE = "As an Amazon Associate I earn from qualifying purchases."
PAID = "(paid link)"
ALLOWED_HOSTS = {
    "amazon.com", "affiliate-program.amazon.com", "ftc.gov", "docs.github.com",
    "github.com", "developers.google.com", "search.google.com", "sitemaps.org",
    "www.sitemaps.org", "rssboard.org", "www.rssboard.org", "link.amazon",
}
ENDORSEMENT_PATTERNS = [
    r"amazon recommends",
    r"amazon'?s choice",
    r"endorsed by amazon",
    r"amazon endorses",
    r"amazon sponsors",
    r"approved by amazon",
    r"partnered with amazon",
]

errors = []
warnings = []


def err(msg):
    errors.append(msg)


def host_ok(host):
    return any(host == h or host.endswith("." + h) for h in ALLOWED_HOSTS)


def is_amazon_link(host):
    """Amazon shopping and product hosts. The Associates program site is not a shopping host."""
    if host == "affiliate-program.amazon.com" or host.endswith(".affiliate-program.amazon.com"):
        return False
    return host == "amazon.com" or host.endswith(".amazon.com") or host == "link.amazon"


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.links = []  # (href, rel, data-event, line_no)
        self.in_script = False
        self.in_style = False
        self.text = []
        self.title = None
        self.meta_desc = None
        self.canonical = None
        self.tables = []  # list of dicts: {class, rows: [list of row html snippets/links]}
        self._table_stack = []
        self._row = None
        self._in_tbody = False
        self._in_tag_title = False
        self._stack = []
        self.div_disclosure_positions = []
        self.header_closed = False
        self.first_after_header = None
        self.footer_disclosure = False
        self.in_footer = False
        self._pending_paid = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "script":
            self.in_script = True
        if tag == "style":
            self.in_style = True
        if tag == "title":
            self._in_tag_title = True
        if tag == "meta" and a.get("name") == "description":
            self.meta_desc = a.get("content", "")
        if tag == "link" and a.get("rel") == "canonical":
            self.canonical = a.get("href")
        if tag == "a" and a.get("href") is not None:
            self.links.append((a["href"], a.get("rel", ""), a.get("data-event", ""), self.getpos()[0]))
            self._pending_paid.append(len(self.links) - 1)
            self._open_a_href = a["href"]
        if tag == "table":
            cls = a.get("class", "")
            self._table_stack.append({"class": cls, "rows": []})
        if tag == "tbody" and self._table_stack:
            self._in_tbody = True
        if tag == "tr" and self._in_tbody and self._table_stack:
            self._row = []
        if tag == "header":
            self.header_closed = False
        if tag == "footer":
            self.in_footer = True
        if tag == "div" and "disclosure" in a.get("class", ""):
            if "disclosure-foot" in a.get("class", ""):
                self.footer_disclosure = True
            else:
                self.div_disclosure_positions.append(self.getpos()[0])
        self._stack.append(tag)

    def handle_endtag(self, tag):
        if tag == "script":
            self.in_script = False
        if tag == "style":
            self.in_style = False
        if tag == "title":
            self._in_tag_title = False
        if tag == "tbody":
            self._in_tbody = False
        if tag == "tr" and self._row is not None and self._table_stack:
            self._table_stack[-1]["rows"].append(self._row)
            self._row = None
        if tag == "table" and self._table_stack:
            self.tables.append(self._table_stack.pop())
        if tag == "footer":
            self.in_footer = False
        if tag == "a":
            # if no text followed the link, it's not a paid-label candidate
            self._pending_paid = []
        if tag in self._stack:
            while self._stack and self._stack[-1] != tag:
                self._stack.pop()
            if self._stack:
                self._stack.pop()

    def handle_data(self, data):
        if self._in_tag_title:
            self.title = (self.title or "") + data
        if self.in_script or self.in_style:
            return
        self.text.append(data)
        if self._row is not None and self._table_stack:
            pass
        # Collect link hrefs inside rows for check 5.
        if self._row is not None and self._table_stack:
            self._row.append(data)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def html_files():
    out = []
    for dirpath, _, files in os.walk(DOCS):
        for f in files:
            if f.endswith(".html"):
                out.append(os.path.join(dirpath, f))
    return sorted(out)


def rel_path(full):
    return os.path.relpath(full, DOCS).replace(os.sep, "/")


def resolve_internal(from_rel, href):
    """Return the docs-relative file a link points to, or None if external."""
    parts = urllib.parse.urlsplit(href)
    if parts.scheme or parts.netloc:
        return None
    path = parts.path
    base_dir = posixpath.dirname(from_rel)
    if path == "":
        return from_rel  # same-page fragment
    target = posixpath.normpath(posixpath.join(base_dir, path))
    if target.startswith("../"):
        return "__outside__"
    if os.path.isdir(os.path.join(DOCS, target)):
        target = posixpath.join(target, "index.html")
    return target


def main():
    if not os.path.isdir(DOCS):
        print("docs/ missing. Run scripts/build.py first.")
        return 2

    pages = {}
    files = html_files()
    for full in files:
        rel = rel_path(full)
        text = read(full)
        p = Page()
        p.feed(text)
        pages[rel] = (p, text)

    # 1. Disclosure strip
    for rel, (p, text) in pages.items():
        # The sentence must sit inside the strip under the masthead and inside the footer strip.
        top = re.search(r'<div class="disclosure"[^>]*>(.*?)</div>', text, re.S)
        foot = re.search(r'<div class="disclosure disclosure-foot"[^>]*>(.*?)</div>', text, re.S)
        if not top or SENTENCE not in top.group(1):
            err(f"{rel}: Associates sentence not inside the strip under the masthead")
        if not foot or SENTENCE not in foot.group(1):
            err(f"{rel}: Associates sentence not inside the footer strip")
        if not p.div_disclosure_positions:
            err(f"{rel}: no disclosure strip under masthead")
        else:
            # The strip must come right after </header>, i.e. before nav and main.
            i_head = text.find("</header>")
            i_strip = text.find('class="disclosure"')
            i_main = text.find("<main")
            if not (i_head != -1 and i_head < i_strip < i_main):
                err(f"{rel}: disclosure strip is not directly under the masthead")
        if rel != "404.html" and (p.title is None or p.title.strip() == ""):
            err(f"{rel}: missing <title>")
        if rel != "404.html" and not p.meta_desc:
            err(f"{rel}: missing meta description")
        if rel != "404.html" and not p.canonical:
            err(f"{rel}: missing canonical link")

    # 2. Sponsored and paid labels; 3. internal links; 4. external hosts
    for rel, (p, text) in pages.items():
        lines = text.split("\n")
        for href, rel_attr, event, _ in p.links:
            parts = urllib.parse.urlsplit(href)
            host = (parts.hostname or "").lower()
            if host and is_amazon_link(host):
                if "sponsored" not in rel_attr.split():
                    err(f"{rel}: Amazon link without rel=sponsored: {href[:90]}")
            if parts.scheme in ("http", "https"):
                if not host_ok(host):
                    err(f"{rel}: external host not on allowlist: {host} ({href[:80]})")
                continue
            if parts.scheme in ("mailto", "tel"):
                continue
            target = resolve_internal(rel, href)
            if target == "__outside__":
                err(f"{rel}: link escapes docs/: {href}")
                continue
            if target is None:
                continue
            if target not in pages and not os.path.exists(os.path.join(DOCS, target)):
                err(f"{rel}: broken internal link: {href}")
                continue
            if parts.fragment:
                tp = pages.get(target)
                if tp is None or parts.fragment not in tp[0].ids:
                    err(f"{rel}: broken fragment: {href}")

        # Paid label after each sponsored link: check the text that follows the link in the HTML.
        for m in re.finditer(r'<a [^>]*rel="sponsored"[^>]*>.*?</a>(.{0,160})', text, re.S):
            after = m.group(1)
            if PAID not in after:
                err(f"{rel}: sponsored link without '{PAID}' label nearby")

    # 5. Data tables: every body row has a link to an allowed official host.
    for rel, (p, text) in pages.items():
        for t in p.tables:
            cls = t["class"].split()
            if "options" in cls or "schema" in cls:
                continue
            if "data" not in cls:
                continue
        # Check rows directly from HTML for accuracy.
        for m in re.finditer(r'<table class="data"[^>]*>(.*?)</table>', text, re.S):
            tbody = re.search(r"<tbody>(.*?)</tbody>", m.group(1), re.S)
            if not tbody:
                continue
            for r in re.finditer(r"<tr>(.*?)</tr>", tbody.group(1), re.S):
                hrefs = re.findall(r'href="([^"]+)"', r.group(1))
                ok = False
                for h in hrefs:
                    hp = urllib.parse.urlsplit(h)
                    if hp.scheme in ("http", "https") and host_ok((hp.hostname or "").lower()):
                        ok = True
                        break
                if not ok:
                    err(f"{rel}: data table row without an official source link")

    # 6. No price-like strings in visible text
    for rel, (p, text) in pages.items():
        visible = " ".join(p.text)
        if re.search(r"\$\s?\d", visible):
            err(f"{rel}: price-like string found (prices must not be shown unverified)")

    # 7. No endorsement claims
    for rel, (p, text) in pages.items():
        visible = " ".join(p.text).lower()
        for pat in ENDORSEMENT_PATTERNS:
            if re.search(pat, visible):
                err(f"{rel}: endorsement-style claim matched /{pat}/")

    # 9. Sitemap and feed
    sm_path = os.path.join(DOCS, "sitemap.xml")
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    tree = ET.parse(sm_path)
    locs = [e.text for e in tree.getroot().findall("s:url/s:loc", ns)]
    base = None
    cfg = json.load(open(os.path.join(REG, "site.json"), encoding="utf-8"))
    base = cfg["base_url"].rstrip("/")
    expected = set()
    for rel in pages:
        if rel == "404.html":
            continue
        url = base + "/" + (rel[: -len("index.html")] if rel.endswith("index.html") else rel)
        expected.add(url)
    listed = set(locs)
    for u in expected - listed:
        err(f"sitemap missing {u}")
    for u in listed - expected:
        err(f"sitemap lists a page that is not built: {u}")
    for u in locs:
        path = urllib.parse.urlsplit(u).path.replace(urllib.parse.urlsplit(base).path, "", 1).lstrip("/")
        if path == "":
            path = "index.html"
        elif path.endswith("/"):
            path = path + "index.html"
        if path not in pages:
            err(f"sitemap URL does not map to a built page: {u}")
    if len(locs) != len(set(locs)):
        err("sitemap has duplicate URLs")

    feed = ET.parse(os.path.join(DOCS, "feed.xml")).getroot()
    items = feed.findall("./channel/item")
    guide_files = sorted(glob.glob(os.path.join(REG, "guides", "*.json")))
    slugs = []
    for g in guide_files:
        slugs.append(json.load(open(g, encoding="utf-8"))["slug"])
    feed_links = [i.findtext("link") for i in items]
    if len(items) != len(slugs):
        err(f"feed has {len(items)} items; {len(slugs)} guides exist")
    for s in slugs:
        want = f"{base}/guides/{s}/"
        if want not in feed_links:
            err(f"feed missing guide {s}")
        if f"{base}/guides/{s}/" not in listed:
            err(f"sitemap missing guide {s}")
    for pubd in [i.findtext("pubDate") for i in items]:
        if not pubd or not re.match(r"^[A-Z][a-z]{2}, \d{2} [A-Z][a-z]{2} \d{4} ", pubd):
            err(f"feed item pubDate not RFC 822: {pubd}")

    # Feed link check for pages: each feed link must be a built guide page.
    for link in feed_links:
        path = urllib.parse.urlsplit(link).path.replace(urllib.parse.urlsplit(base).path, "", 1).strip("/")
        if (path + "/index.html") not in pages:
            err(f"feed item links to a page not built: {link}")

    # Summary
    print(f"pages checked: {len(pages)}")
    print(f"sitemap URLs: {len(locs)}; feed items: {len(items)}")
    for w in warnings:
        print("WARN:", w)
    if errors:
        print(f"FAILED: {len(errors)} problem(s)")
        for e in errors:
            print(" -", e)
        return 1
    print("OK: all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
