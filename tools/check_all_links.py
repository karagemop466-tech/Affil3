#!/usr/bin/env python3
"""Internal link integrity for the published tree. Exit 2 on a broken internal
link. External http(s) links are listed as 'externals' for manual review — this
gate never touches the network, so it cannot hallucinate reachability.
"""
import importlib.util
import pathlib
import re
import sys
import tempfile
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

spec = importlib.util.spec_from_file_location("build_site", ROOT / "scripts" / "build_site.py")
bs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bs)
with tempfile.TemporaryDirectory() as td:
    PAGE_SET = sorted(bs.build(td).keys())
for rel in PAGE_SET:
    f = ROOT / "legacy" / "editions" / "counter" / rel
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
                broken.append((rel, raw))

for page, raw in broken:
    print(f"BROKEN: {page} -> {raw}")
print(f"check_all_links: {len(broken)} broken internal link(s); {len(externals)} external link(s) recorded for manual review")
if broken:
    sys.exit(2)
