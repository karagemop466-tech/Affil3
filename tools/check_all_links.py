#!/usr/bin/env python3
"""Internal link integrity for the published tree. Exit 2 on a broken internal
link. External http(s) links are listed as 'externals' for manual review — this
gate never touches the network, so it cannot hallucinate reachability.
"""
import pathlib
import re
import sys
import urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent.parent
skip = {".git", "node_modules", "server", "scripts", "tools", "content", "data", "docs", "assets"}
broken = []
externals = set()

def resolve(base_file, href):
    href = href.split("#")[0].split("?")[0]
    if not href:
        return None
    if href.startswith(("http://", "https://", "mailto:", "tel:")):
        externals.add(href)
        return None
    target = (base_file.parent / urllib.parse.unquote(href)).resolve()
    return target

for f in sorted(ROOT.rglob("*.html")):
    if any(part in skip for part in f.relative_to(ROOT).parts[:-1]):
        continue
    html = f.read_text()
    for attr in ("href", "src"):
        for m in re.finditer(attr + r'="([^"]+)"', html):
            raw = m.group(1)
            t = resolve(f, raw)
            if t is None:
                continue
            if t.is_dir():
                t = t / "index.html"
            if not t.exists():
                broken.append((str(f.relative_to(ROOT)), raw))

for page, raw in broken:
    print(f"BROKEN: {page} -> {raw}")
print(f"check_all_links: {len(broken)} broken internal link(s); {len(externals)} external link(s) recorded for manual review")
if broken:
    sys.exit(2)
