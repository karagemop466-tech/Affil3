#!/usr/bin/env python3
"""Table-source coverage report: every row of every findings table
(class="data sourced" — verification, link register, compare, flagged,
compliance, sources) must cite an official source. Governance tables
(class="data meta" — tasks, questions, suggestions, events, ledger) are
internal management records and are exempt from external citations.
Exit 3 under --strict if any sourced table is under 100% coverage.

Official source domains (the register's publishers + submitted links + repo):
  amazon.com, advertising.amazon.com, affiliate-program.amazon.com,
  ftc.gov, developers.google.com, docs.github.com, link.amazon, github.com
"""
import importlib.util
import pathlib
import re
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
OFFICIAL = ("amazon.com", "advertising.amazon.com", "affiliate-program.amazon.com",
            "ftc.gov", "developers.google.com", "docs.github.com", "link.amazon", "github.com")

def official_hits(row):
    hits = []
    for m in re.finditer(r'href="(https://[^"]+)"', row):
        url = m.group(1)
        host = url.split("/", 3)[2] if "//" in url else ""
        if any(host == d or host.endswith("." + d) or host == d for d in OFFICIAL):
            hits.append(url)
    return hits

failures = 0
report = []
spec = importlib.util.spec_from_file_location("build_site", ROOT / "scripts" / "build_site.py")
bs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bs)
with tempfile.TemporaryDirectory() as td:
    PAGE_SET = sorted(bs.build(td).keys())
for rel in PAGE_SET:
    f = ROOT / "legacy" / "editions" / "counter" / rel
    html = f.read_text()
    for ti, m in enumerate(re.finditer(r"<table class=\"data sourced\">.*?</table>", html, re.S)):
        rows = re.findall(r"<tr>.*?</tr>", m.group(0), re.S)[1:]
        covered = 0
        for row in rows:
            if "<em>No rows yet.</em>" in row:
                covered += 1
                continue
            if official_hits(row):
                covered += 1
        pct = (100.0 * covered / len(rows)) if rows else 100.0
        report.append((rel, ti + 1, covered, len(rows), pct))
        if pct < 100.0:
            failures += 1

for rel, ti, cov, tot, pct in report:
    print(f"{rel} table #{ti}: {cov}/{tot} rows with official source ({pct:.0f}%)")

if failures and "--strict" in sys.argv:
    print(f"link_report --strict: FAILED — {failures} table(s) under-covered")
    sys.exit(3)
print("link_report: OK" + ("" if not failures else f" ({failures} table(s) under-covered, not strict)"))
