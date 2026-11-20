#!/usr/bin/env python3
"""Crawl every published page under docs/ and check for broken links.

- Internal links (relative) must resolve to an existing file.
- External links are probed with a HEAD request. Hosts blocked from this
  sandbox are reported as 'unreachable-from-sandbox' (warning, not failure).
Exit code: 0 = no broken internal links; 1 = broken internal link found.
Standard library only.
"""
import argparse
import glob
import os
import re
import sys
import urllib.request
import urllib.error
from urllib.parse import urljoin, urlparse

DOCS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs")
HREF_RE = re.compile(r'href=["\']([^"\']+)["\']', re.IGNORECASE)


def pages():
    return sorted(glob.glob(os.path.join(DOCS, "**", "*.html"), recursive=True))


def resolve_internal(base_file, href):
    base_dir = os.path.dirname(base_file)
    target = urljoin("file://" + base_dir + "/", href)
    path = urlparse(target).path
    # strip leading slash (we resolved against base_dir) — handle both
    if urlparse(target).netloc:
        return None  # absolute URL
    return os.path.normpath(os.path.join(base_dir, urlparse(target).path))


def probe_external(url):
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "affil3-link-checker"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, None
    except urllib.error.HTTPError as e:
        # Some sites reject HEAD; treat a 4xx/5xx as unreachable-from-sandbox warning
        return e.code, "HTTPError"
    except Exception as e:
        return None, type(e).__name__


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-external", action="store_true", help="skip external probes")
    args = ap.parse_args()

    broken = []
    warnings = []
    checked = 0

    for page in pages():
        with open(page, encoding="utf-8") as fh:
            content = fh.read()
        rel_page = os.path.relpath(page, DOCS)
        for href in HREF_RE.findall(content):
            if href.startswith(("#", "mailto:", "tel:", "javascript:")):
                continue
            if href.startswith("http"):
                if args.no_external:
                    continue
                status, err = probe_external(href)
                checked += 1
                if status is None:
                    warnings.append((rel_page, href, f"unreachable-from-sandbox ({err})"))
                elif status >= 400:
                    warnings.append((rel_page, href, f"HTTP {status}"))
                continue
            # internal
            target = resolve_internal(page, href)
            if target is None:
                continue
            checked += 1
            if not os.path.exists(target):
                broken.append((rel_page, href, target))

    print(f"Checked {checked} links across {len(pages())} pages.")
    for rel_page, href, target in broken:
        print(f"BROKEN  {rel_page} -> {href} (resolved to missing {target})")
    for rel_page, href, why in warnings:
        print(f"WARN    {rel_page} -> {href} ({why})")
    if broken:
        print(f"RESULT: {len(broken)} broken internal links")
        return 1
    print("RESULT: no broken internal links")
    return 0


if __name__ == "__main__":
    sys.exit(main())
