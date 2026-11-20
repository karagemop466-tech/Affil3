#!/usr/bin/env python3
"""One-time (re-runnable) integration patch for pages this session does not own.

Kept in the repo rather than run as a throwaway shell loop, so that whichever session ends up as
integrator can re-run it over any page added later instead of hand-editing navigation in nine
files. It does exactly three mechanical things:

  1. adds the four new pages to the main nav and the footer nav of every existing page;
  2. appends their <url> entries to sitemap.xml;
  3. leaves a marker comment so a second run is a no-op (idempotent).

It never rewrites body copy, so it cannot destroy another session's prose.
"""
from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
MARK = "<!-- nav:43565031 -->"
NEW = [
    ("shop.html", "Shop"),
    ("verification.html", "Link evidence"),
    ("suggestions.html", "Decision room"),
    ("questions.html", "Open questions"),
]

NEW_BLOCK_MAIN = "\n".join(f'    <a href="{h}">{l}</a>{MARK}' for h, l in NEW)
NEW_BLOCK_SUB = "\n".join(f'    <a href="../{h}">{l}</a>{MARK}' for h, l in NEW)


def patch_html(path: pathlib.Path) -> None:
    txt = path.read_text(encoding="utf-8")
    if MARK in txt:
        return
    block = NEW_BLOCK_SUB if "guides/" in str(path.relative_to(ROOT)) else NEW_BLOCK_MAIN
    before = len(txt)

    # insert after the Products entry of each nav group (main nav and footer nav)
    def anchor(m: re.Match) -> str:
        return m.group(0) + "\n" + block

    txt = re.sub(
        r'<a href="(\.\./)?products\.html">Products</a>\s*$', anchor, txt, flags=re.M
    )
    if len(txt) == before:  # no Products entry (guides subpages): anchor on Home instead
        txt = re.sub(r'<a href="(\.\./)?index\.html"[^>]*>Home</a>\s*$', anchor, txt, flags=re.M)
    path.write_text(txt)
    print(f"  nav  {path.relative_to(ROOT)}")


def patch_sitemap() -> None:
    path = ROOT / "sitemap.xml"
    txt = path.read_text(encoding="utf-8")
    if "suggestions.html" in txt:
        return
    base = re.search(r"<loc>(https?://[^<]+?)/?", txt).group(1)
    urls = "\n".join(
        f"  <url>\n    <loc>{base}/{h}</loc>\n    <lastmod>2026-11-20</lastmod>\n  </url>"
        for h, _ in NEW
    )
    txt = txt.replace("</urlset>", urls + "\n</urlset>")
    path.write_text(txt)
    print(f"  site  {path.relative_to(ROOT)}")


def main() -> int:
    pages = sorted(ROOT.glob("*.html")) + sorted((ROOT / "guides").glob("*.html"))
    for p in pages:
        if p.name in {h for h, _ in NEW}:
            continue
        patch_html(p)
    patch_sitemap()
    return 0


if __name__ == "__main__":
    sys.exit(main())
