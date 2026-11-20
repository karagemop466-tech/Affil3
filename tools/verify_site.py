#!/usr/bin/env python3
"""Whole-tree release gate. Exit 3 on any violation.

  1. build --check          checked-in tree matches a fresh render
  2. scripts/check_site.py  content/compliance gates
  3. tools/link_report.py --strict   every table row sourced
  4. tools/check_all_links.py        internal link integrity
"""
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
steps = [
    [sys.executable, str(ROOT / "scripts" / "build_site.py"), "--check"],
    [sys.executable, str(ROOT / "scripts" / "check_site.py")],
    [sys.executable, str(ROOT / "tools" / "link_report.py"), "--strict"],
    [sys.executable, str(ROOT / "tools" / "check_all_links.py")],
]
for cmd in steps:
    print("+", " ".join(cmd))
    r = subprocess.run(cmd, cwd=ROOT)
    if r.returncode != 0:
        print(f"verify_site: FAILED at {' '.join(cmd[-2:])} (exit {r.returncode})")
        sys.exit(3)
print("verify_site: OK — release gate passed")
