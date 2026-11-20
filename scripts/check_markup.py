#!/usr/bin/env python3
"""Structural check: every page must parse with balanced elements.

A generated page with an unclosed <td> renders as a wall of run-on text in some browsers, which is
exactly the kind of defect a "polished" claim has to survive. This is a cheap, dependency-free pass.
"""
from __future__ import annotations
import pathlib
import sys
from html.parser import HTMLParser

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param",
        "source", "track", "wbr"}


class Balance(HTMLParser):
    def __init__(self, name: str):
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, int]] = []
        self.errors: list[str] = []
        self.name = name

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append((tag, self.getpos()[0]))

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack:
            self.errors.append(f"{self.name}:{self.getpos()[0]} stray </{tag}>")
            return
        open_tag, line = self.stack.pop()
        if open_tag != tag:
            self.errors.append(
                f"{self.name}:{self.getpos()[0]} </{tag}> closes <{open_tag}> opened at line {line}"
            )


def main() -> int:
    root = pathlib.Path(__file__).resolve().parents[1]
    pages = sorted(root.glob("*.html")) + sorted((root / "guides").glob("*.html"))
    bad = 0
    for p in pages:
        parser = Balance(p.name)
        parser.feed(p.read_text(encoding="utf-8"))
        leftover = [f"  {p.name}: <{t}> opened at line {ln} never closed" for t, ln in parser.stack]
        msgs = parser.errors + leftover
        if msgs:
            bad += 1
            print("\n".join(msgs))
        else:
            print(f"  ok   {p.relative_to(root)}")
    if bad:
        print(f"{bad} page(s) with unbalanced markup")
        return 1
    print(f"all {len(pages)} pages balanced")
    return 0


if __name__ == "__main__":
    sys.exit(main())
