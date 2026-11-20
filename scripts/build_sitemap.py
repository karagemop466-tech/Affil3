#!/usr/bin/env python3
"""Build docs/sitemap.xml from the checked-in site tree.

Walks crisp-index/ for *.html, converts each to a site URL, and writes a sitemap.
Run --check to verify every live page is present in the sitemap (exit 1 on violation).
Standard library only.
"""
import argparse
import os
import sys
from datetime import date, datetime, timezone
from urllib.parse import quote

DOCS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "crisp-index")


def html_pages():
    pages = []
    for root, _dirs, files in os.walk(DOCS):
        for f in files:
            if f.endswith(".html"):
                full = os.path.join(root, f)
                rel = os.path.relpath(full, DOCS).replace(os.sep, "/")
                pages.append(rel)
    return sorted(pages)


def to_url(rel, base):
    url = base.rstrip("/") + "/" + quote(rel)
    # clean double slashes inside path segments (base may end with /)
    url = url.replace("//", "/")
    return url


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default="https://karagemop466-tech.github.io/Affil3")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    pages = html_pages()
    today = date.today().isoformat()

    if args.check:
        sitemap = os.path.join(DOCS, "sitemap.xml")
        if not os.path.exists(sitemap):
            print("sitemap.xml missing")
            return 1
        with open(sitemap, encoding="utf-8") as fh:
            content = fh.read()
        missing = [p for p in pages if to_url(p, args.base_url) not in content and quote(p) not in content]
        if missing:
            for m in missing:
                print("MISSING from sitemap:", m)
            return 1
        print(f"OK: {len(pages)} pages all present in sitemap.xml")
        return 0

    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for rel in pages:
        lines.append("  <url>")
        lines.append(f"    <loc>{to_url(rel, args.base_url)}</loc>")
        lines.append(f"    <lastmod>{today}</lastmod>")
        lines.append("    <changefreq>weekly</changefreq>")
        lines.append("    <priority>0.8</priority>")
        lines.append("  </url>")
    lines.append("</urlset>")

    out = os.path.join(DOCS, "sitemap.xml")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"Wrote {out} with {len(pages)} URLs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
