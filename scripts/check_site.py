#!/usr/bin/env python3
"""Content gates for the Crisp & Counter site. Exit 1 on any violation.

Checks (each maps to a compliance gate on desk/compliance/):
  1. every page carries the disclosure strip and the Amazon Associate statement
  2. every outbound amazon.com product anchor is rel="sponsored" and labeled
  3. every row of every data table carries an official-source link
  4. unresolved products render no affiliate CTA
  5. no placeholder text (TODO / lorem / FIXME) in published pages
  6. sitemap lists every published page; feed carries every guide
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
ERRORS = []

def pages():
    skip = {".git", "node_modules", "server", "scripts", "tools", "content", "data", "docs", "assets"}
    for f in sorted(ROOT.rglob("*.html")):
        if any(part in skip for part in f.relative_to(ROOT).parts[:-1]):
            continue
        yield f

def check(cond, msg):
    if not cond:
        ERRORS.append(msg)

DISCLOSURE_MARK = "Crisp &amp; Counter is reader-supported"
ASSOCIATE_MARK = "As an Amazon Associate we earn from qualifying purchases"

html_files = list(pages())
check(len(html_files) >= 18, f"expected >= 18 published pages, found {len(html_files)}")

for f in html_files:
    rel = f.relative_to(ROOT)
    html = f.read_text()
    check(DISCLOSURE_MARK in html, f"{rel}: missing disclosure strip under masthead")
    check(ASSOCIATE_MARK in html, f"{rel}: missing Amazon Associate statement in footer")

    for m in re.finditer(r"<a\b[^>]*>", html):
        tag = m.group(0)
        if 'href="https://www.amazon.com/dp/' in tag or 'href="https://link.amazon/' in tag:
            check("sponsored" in tag, f"{rel}: amazon link without rel=sponsored: {tag[:90]}")
            if "/dp/" in tag and "tag=" in tag:
                check("data-aff=" in tag, f"{rel}: affiliate CTA missing data-aff: {tag[:90]}")
                check(ASSOCIATE_MARK in html, f"{rel}: CTA page missing associate statement")

    for m in re.finditer(r"<table class=\"data sourced\">.*?</table>", html, re.S):
        rows = re.findall(r"<tr>.*?</tr>", m.group(0), re.S)
        rows = rows[1:]  # skip header
        for i, row in enumerate(rows):
            if "<em>No rows yet.</em>" in row:
                continue
            check("https://" in row, f"{rel}: sourced table row {i+1} has no source link: {row[:80]}")

    for bad in ("TODO", "FIXME", "lorem ipsum", "Lorem ipsum"):
        check(bad not in html, f"{rel}: placeholder text '{bad}'")

# 4 — unresolved products must not carry an affiliate CTA
shop = (ROOT / "shop" / "index.html")
if shop.exists():
    s = shop.read_text()
    check("Link pending verification" in s, "shop/index.html: unresolved product must show pending-verification state")
    check('data-aff="P4"' not in s, "shop/index.html: P4 must not carry an affiliate CTA while unresolved")

# 6 — sitemap + feed coverage
sm = ROOT / "sitemap.xml"
check(sm.exists(), "sitemap.xml missing")
if sm.exists():
    sitemap = sm.read_text()
    for f in html_files:
        rel = f.relative_to(ROOT)
        if rel.name == "404.html":
            continue
        path = "/" + str(rel.parent).replace("\\", "/") + "/"
        path = path.replace("/./", "/")
        if rel == pathlib.Path("index.html"):
            path = "/"
        check(f"<loc>https://karagemop466-tech.github.io/Affil3{path}</loc>" in sitemap,
              f"sitemap.xml missing {path}")

feed = ROOT / "feed.xml"
check(feed.exists(), "feed.xml missing")
if feed.exists():
    fx = feed.read_text()
    check("<channel>" in fx and "</channel>" in fx, "feed.xml: missing channel")
    guides = list((ROOT / "content" / "guides").glob("*.md"))
    items = fx.count("<item>")
    check(items == len(guides), f"feed.xml: {items} items but {len(guides)} guides exist")

if ERRORS:
    print(f"CHECK FAILED — {len(ERRORS)} violation(s):")
    for e in ERRORS:
        print(" -", e)
    sys.exit(1)
print(f"check_site: OK ({len(html_files)} pages, all gates pass)")
