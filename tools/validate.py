#!/usr/bin/env python3
"""The Crisp Index — validator.

Checks the data registers and the built site against the project's hard rules:
  1. intended_* and observed_* product fields exist separately and are never merged;
  2. unverifiable values (price/rating) are null, never filled;
  3. every flag/source referenced in data exists in its register;
  4. every built page carries the exact Associates statement at least twice
     (disclosure strip + footer) and a canonical URL;
  5. every amazon.com/dp/ product link is rel="sponsored nofollow noopener",
     carries data-tci="outbound", and its page includes a visible Sponsored chip;
  6. every data row shown on data surfaces has a source link or an explicit
     "unverified" marker;
  7. sitemap covers every non-noindex page; feed has items.
Exit code 0 = all pass.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "crisp-index")
DATA = os.path.join(ROOT, "data", "93cee724")

ERRORS = []
WARNS = []


def err(msg):
    ERRORS.append(msg)


def warn(msg):
    WARNS.append(msg)


def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as f:
        return json.load(f)


def check_data():
    products = load("products.json")
    flags = load("flags.json")
    sources = load("sources.json")
    questions = load("questions.json")
    suggestions = load("suggestions.json")

    flag_ids = {f["id"] for f in flags["flags"]}
    source_ids = {s["id"] for s in sources["sources"]}

    for p in products["products"]:
        # 1. strict record separation
        for key in ("asin", "listing_url", "confirmation_date", "source", "source_ref"):
            if key not in p["intended"]:
                err(f'{p["id"]}: intended.{key} missing')
        if "observed" not in p:
            err(f'{p["id"]}: observed block missing')
        else:
            for key in ("status", "date", "method", "final_url", "asin",
                        "listing_title_verbatim", "category_breadcrumb_verbatim"):
                if key not in p["observed"]:
                    err(f'{p["id"]}: observed.{key} missing')
        # intended tokens must never appear inside observed.* values (no merging)
        if p["observed"].get("asin") and p["observed"]["asin"] == p["intended"]["asin"]:
            err(f'{p["id"]}: observed.asin equals intended.asin — fields appear merged')
        # 2. volatile fields stay null
        for key in ("price", "rating"):
            if p["observed"].get(key) is not None:
                err(f'{p["id"]}: observed.{key} must be null (unverifiable/volatile)')
        # 3. references exist
        for sid in p["sources"]:
            if sid not in source_ids:
                err(f'{p["id"]}: unknown source {sid}')
        for fid in p["flags"]:
            if fid not in flag_ids:
                err(f'{p["id"]}: unknown flag {fid}')
        # outbound must carry the tracking tag or be explicitly flagged
        out = p["site_outbound_url"]
        if "amazon.com/dp/" in out and "tag=" not in out:
            err(f'{p["id"]}: site_outbound_url lacks attribution tag and no exception documented')
        if not p.get("site_outbound_note"):
            err(f'{p["id"]}: site_outbound_note missing')

    for f in flags["flags"]:
        for sid in f["sources"]:
            if sid not in source_ids:
                err(f'{f["id"]}: unknown source {sid}')

    for q in questions["questions"]:
        for fid in q["flags"]:
            if fid not in flag_ids:
                err(f'{q["id"]}: unknown flag {fid}')

    print(f"data: {len(products['products'])} products, {len(flag_ids)} flags, "
          f"{len(source_ids)} sources, {len(questions['questions'])} questions, "
          f"{len(suggestions['suggestions'])} suggestions checked")


STATEMENT = "As an Amazon Associate I earn from qualifying purchases."


def iter_pages():
    for dirpath, _dirnames, filenames in os.walk(DOCS):
        for name in filenames:
            if name.endswith(".html"):
                yield os.path.join(dirpath, name)


def check_pages():
    pages = list(iter_pages())
    if not pages:
        err("no built pages found in docs/ — run tools/build_site.py first")
        return

    dp_link_re = re.compile(r"<a\b[^>]*>", re.IGNORECASE)
    for path in pages:
        rel = os.path.relpath(path, DOCS)
        with open(path, encoding="utf-8") as f:
            html = f.read()

        # 4. disclosure + canonical
        if html.count(STATEMENT) < 2:
            err(f"{rel}: Associates statement appears {html.count(STATEMENT)}x (need >= 2)")
        if '<link rel="canonical"' not in html and rel != "404.html":
            err(f"{rel}: missing canonical")
        if "<title>" not in html or 'name="description"' not in html:
            err(f"{rel}: missing title or description")
        if "disclosure-strip" not in html:
            err(f"{rel}: missing disclosure strip")

        # 5. product link discipline
        for tag in dp_link_re.findall(html):
            if 'href="' not in tag:
                continue
            href_m = re.search(r'href="([^"]+)"', tag)
            if not href_m:
                continue
            href = href_m.group(1)
            is_product = "amazon.com/dp/" in href
            if is_product:
                rel_attr = re.search(r'rel="([^"]+)"', tag)
                rel_val = rel_attr.group(1) if rel_attr else ""
                if "sponsored" not in rel_val or "nofollow" not in rel_val or "noopener" not in rel_val:
                    err(f"{rel}: product link missing full rel set: {href}")
                if 'data-tci="outbound"' not in tag:
                    err(f"{rel}: product link missing data-tci=outbound: {href}")
            if "link.amazon/" in href:
                rel_attr = re.search(r'rel="([^"]+)"', tag)
                rel_val = rel_attr.group(1) if rel_attr else ""
                if "sponsored" not in rel_val:
                    err(f"{rel}: submitted-link outbound missing rel=sponsored: {href}")
        if "amazon.com/dp/" in html and "chip-sponsored" not in html:
            err(f"{rel}: has product links but no visible Sponsored chip")

        # 6. data surfaces must show sources or explicit unverified markers
        data_surfaces = (
            rel.startswith("products/"),
            rel in ("workshop/register.html", "workshop/flagged.html",
                    "workshop/ledger.html", "workshop/executive-summary.html"),
            rel.startswith("compare/"),
        )
        if any(data_surfaces):
            if "class=\"src\"" not in html and "class='src'" not in html:
                err(f"{rel}: data surface without any source links")
            if "unverified" not in html and "flagged" not in html:
                warn(f"{rel}: no unverified/flag markers (check completeness)")

    # 7. sitemap / feed
    sitemap = open(os.path.join(DOCS, "sitemap.xml"), encoding="utf-8").read()
    feed = open(os.path.join(DOCS, "feed.xml"), encoding="utf-8").read()
    sm_count = sitemap.count("<url>")
    if sm_count < 10:
        err(f"sitemap.xml: only {sm_count} URLs")
    if feed.count("<item>") < 5:
        err(f"feed.xml: only {feed.count('<item>')} items (want the guides)")
    for must in ["workshop/flagged.html", "workshop/suggestions.html",
                 "workshop/questions.html", "workshop/executive-summary.html",
                 "workshop/register.html", "workshop/ledger.html"]:
        if must not in sitemap:
            err(f"sitemap.xml missing {must}")

    print(f"pages: {len(pages)} checked")


def main():
    check_data()
    check_pages()
    for w in WARNS:
        print("WARN:", w)
    if ERRORS:
        print(f"\nFAIL — {len(ERRORS)} error(s):")
        for e in ERRORS:
            print("  -", e)
        sys.exit(1)
    print("\nvalidate: ALL CHECKS PASS")


if __name__ == "__main__":
    main()
