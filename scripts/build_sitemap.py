#!/usr/bin/env python3
"""Gate the Crisp Index sitemap (crisp-index/sitemap.xml).

The sitemap is written by tools/build_site.py (the Crisp Index generator). This script does
NOT write it: an earlier version of this script overwrote the file with malformed URLs
(`https:/...`) that pointed at paths outside crisp-index/. Run without --check, it now refuses.

--check verifies, by exact <loc> comparison:
  * every indexable page under crisp-index/ (noindex pages excluded) has its exact URL listed;
  * every listed <loc> is a well-formed https URL under the site base and points at a file that exists.
Exit 0 on success, 1 on violation, 2 when run without --check.
Standard library only.
"""
import argparse
import os
import re
import sys
from urllib.parse import quote, urlsplit

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "crisp-index")
BASE = "https://karagemop466-tech.github.io/Affil3"
PREFIX = "crisp-index"


def is_noindex(full):
    # A page that asks not to be indexed (e.g. the 404 page) does not belong in a sitemap.
    with open(full, encoding="utf-8", errors="replace") as fh:
        head = fh.read(20000).lower()
    return 'name="robots" content="noindex' in head.replace("'", '"')


def indexable_pages():
    pages = []
    for root, _dirs, files in os.walk(DOCS):
        for f in files:
            if f.endswith(".html"):
                full = os.path.join(root, f)
                if is_noindex(full):
                    continue
                rel = os.path.relpath(full, DOCS).replace(os.sep, "/")
                pages.append(rel)
    return sorted(pages)


def expected_url(rel):
    return f"{BASE}/{PREFIX}/{quote(rel)}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    if not args.check:
        print("Refusing to write crisp-index/sitemap.xml here. Regenerate it with tools/build_site.py.",
              file=sys.stderr)
        return 2

    sitemap = os.path.join(DOCS, "sitemap.xml")
    if not os.path.exists(sitemap):
        print("sitemap.xml missing")
        return 1
    with open(sitemap, encoding="utf-8") as fh:
        locs = re.findall(r"<loc>(.*?)</loc>", fh.read())
    listed = set(locs)

    problems = []
    for rel in indexable_pages():
        if expected_url(rel) not in listed:
            problems.append(f"MISSING from sitemap: {rel}")
    for loc in locs:
        parts = urlsplit(loc)
        if parts.scheme != "https" or parts.netloc != "karagemop466-tech.github.io" or not loc.startswith(BASE + "/"):
            problems.append(f"MALFORMED or foreign <loc>: {loc}")
            continue
        path = parts.path[len(urlsplit(BASE).path) + 1:]
        if not path.startswith(PREFIX + "/"):
            problems.append(f"<loc> outside {PREFIX}/: {loc}")
            continue
        target = os.path.join(ROOT, path)
        if not os.path.isfile(target) and not os.path.isfile(os.path.join(target, "index.html")):
            problems.append(f"<loc> points at no file: {loc}")
    if problems:
        for p in problems:
            print(p)
        return 1
    print(f"OK: {len(indexable_pages())} indexable pages, {len(locs)} <loc> entries, all exact and resolvable")
    return 0


if __name__ == "__main__":
    sys.exit(main())
