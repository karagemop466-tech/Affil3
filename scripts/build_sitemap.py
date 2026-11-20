#!/usr/bin/env python3
"""Rebuild sitemap.xml from the checked-in HTML tree.

  python3 scripts/build_sitemap.py           # rewrite sitemap.xml
  python3 scripts/build_sitemap.py --check   # exit 1 if the file is stale
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE_URL = "https://karagemop466-tech.github.io/Affil3"
LASTMOD = "2026-11-20"
skip = {".git", "node_modules", "server", "scripts", "tools", "content", "data", "docs", "assets"}

paths = []
for f in sorted(ROOT.rglob("*.html")):
    if any(part in skip for part in f.relative_to(ROOT).parts[:-1]):
        continue
    rel = f.relative_to(ROOT)
    if rel.name == "404.html":
        continue
    if rel == pathlib.Path("index.html"):
        paths.append("/")
    else:
        paths.append("/" + str(rel.parent).replace("\\", "/") + "/")

xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
       '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
       + "\n".join(f"  <url><loc>{SITE_URL}{p}</loc><lastmod>{LASTMOD}</lastmod></url>" for p in paths)
       + "\n</urlset>\n")

out = ROOT / "sitemap.xml"
if "--check" in sys.argv:
    if not out.exists() or out.read_text() != xml:
        print("build_sitemap --check: sitemap.xml is stale — run scripts/build_sitemap.py")
        sys.exit(1)
    print("build_sitemap --check: OK")
else:
    out.write_text(xml)
    print(f"build_sitemap: wrote {len(paths)} urls")
