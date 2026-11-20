#!/usr/bin/env python3
"""The Crisp Index — internal link & anchor checker.

Walks every built HTML page, resolves internal hrefs/srcs against docs/, and
verifies the target file exists and (for #fragments) that the anchor id exists
in the target. External links are listed for manual review (not fetched here).
Exit code 0 = no broken internal links.
"""
import os
import re
import sys
from urllib.parse import urlparse, unquote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "crisp-index")

BROKEN = []
EXTERNAL = set()

tag_re = re.compile(r"<(?:a|img|link|script)\b[^>]*>", re.IGNORECASE)
href_re = re.compile(r'(?:href|src)="([^"]+)"')
id_re = re.compile(r'id="([^"]+)"')


def collect_ids(html):
    return set(id_re.findall(html))


def main():
    html_files = []
    for dirpath, _d, files in os.walk(DOCS):
        for name in files:
            if name.endswith(".html"):
                html_files.append(os.path.join(dirpath, name))

    id_cache = {}
    for path in html_files:
        with open(path, encoding="utf-8") as f:
            id_cache[path] = collect_ids(f.read())

    for path in html_files:
        rel = os.path.relpath(path, DOCS)
        with open(path, encoding="utf-8") as f:
            html = f.read()
        for tag in tag_re.findall(html):
            for url in href_re.findall(tag):
                if url.startswith(("http://", "https://")):
                    EXTERNAL.add(url)
                    continue
                if url.startswith(("mailto:", "tel:", "data:", "javascript:")):
                    continue
                if url.startswith("#"):
                    target, frag = path, url[1:]
                else:
                    parsed = urlparse(url)
                    target = os.path.normpath(
                        os.path.join(os.path.dirname(path), unquote(parsed.path))
                    )
                    frag = unquote(parsed.fragment) if parsed.fragment else ""
                if not os.path.exists(target):
                    BROKEN.append(f"{rel}: missing target {url}")
                    continue
                if frag and target.endswith(".html"):
                    if frag not in id_cache.get(target, set()):
                        BROKEN.append(f"{rel}: missing anchor #{frag} in "
                                      f"{os.path.relpath(target, DOCS)}")

    print(f"checked {len(html_files)} pages; {len(EXTERNAL)} unique external links "
          f"(listed for manual review)")
    for u in sorted(EXTERNAL):
        if "amazon" in u or "ftc.gov" in u or "affiliate-program" in u:
            print("  ext:", u)
    if BROKEN:
        print(f"\nFAIL — {len(BROKEN)} broken internal link(s):")
        for b in BROKEN:
            print("  -", b)
        sys.exit(1)
    print("\ncheck_links: NO BROKEN INTERNAL LINKS")


if __name__ == "__main__":
    main()
