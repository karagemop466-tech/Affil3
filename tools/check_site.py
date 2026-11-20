#!/usr/bin/env python3
"""Gate the build. Fails CI if the site breaks a rule we said we would keep.

Checks
 1. Every internal link resolves to a file that exists.
 2. No currency or price text anywhere in the generated HTML.
 3. No star rating or review count pattern.
 4. Every outbound Amazon link carries tag=<TRACKING_ID>.
 5. Every page carries the required Associates statement.
 6. Every spec row on a product page cites a source ID that exists.
 7. The retained editorial archive is noindex and its sitemap contains no archive URLs.
"""

from __future__ import annotations

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = ROOT / "editorial"
DATA = ROOT / "data" / "register"
TRACKING_ID = "shopnow047c-20"
STATEMENT = "As an Amazon Associate I earn from qualifying purchases."

errors: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def html_files() -> list[pathlib.Path]:
    return sorted(DOCS.rglob("*.html"))


def main() -> int:
    if not DOCS.exists():
        print("FAIL: editorial/ has not been built. Run tools/build.py first.")
        return 1

    source_ids = {s["id"] for s in json.load(open(DATA / "sources.json"))["sources"]}
    pages = html_files()
    if not pages:
        err("no HTML files were generated")
        return report()

    products = json.load(open(DATA / "products.json"))["products"]
    product_pages = {f"products/{p['id'].lower()}/index.html" for p in products}

    # 1. internal links + 4/5/6 content rules
    for page in pages:
        rel = page.relative_to(DOCS).as_posix()
        text = page.read_text(encoding="utf-8")

        base = page.parent
        # Anchors are checked too, not just paths. A link to a fragment that does not
        # exist on the target page resolves to a real file and silently lands the reader
        # at the top of it, which is how every #Sxx source citation on this site was
        # broken without any gate noticing.
        for href in re.findall(r'(?:href|src)="([^"]+)"', text):
            if href.startswith(("//", "http", "mailto:", "data:", "javascript:")):
                continue
            path_part, _, frag = href.partition("#")
            if not path_part:
                if frag and f'id="{frag}"' not in text and frag != "main":
                    err(f"broken in-page anchor: {rel} -> {href}")
                continue
            candidate = (base / path_part).resolve()
            if path_part.endswith("/") or candidate.is_dir():
                candidate = candidate / "index.html"
            try:
                candidate.relative_to(DOCS.resolve())
            except ValueError:
                # The archive notice links back to the root publication, which sits
                # outside this subtree but inside the repository. Allow it when the
                # target really exists; anything else is still an escaping link.
                try:
                    candidate.relative_to(DOCS.resolve().parent)
                    if not candidate.exists():
                        err(f"link escapes the site root: {rel} -> {href}")
                except ValueError:
                    err(f"link escapes the site root: {rel} -> {href}")
                continue
            if not candidate.exists():
                err(f"broken internal link: {rel} -> {href}")
            elif frag and candidate.suffix == ".html" and frag != "main":
                target = candidate.read_text(encoding="utf-8")
                if f'id="{frag}"' not in target:
                    err(f"broken anchor target: {rel} -> {href}")

        # This is a review archive, not a second publication for search engines.
        if '<meta name="robots" content="noindex,follow">' not in text:
            err(f"editorial archive page is not noindex: {rel}")

        # 5. required statement on every page
        if STATEMENT not in text:
            err(f"missing Associates statement: {rel}")

        # 2. no price text. Allow the words "price" in the button label and the words
        #    "no prices" in prose; reject an actual currency amount.
        for m in re.finditer(r"[$£€]\s?\d", text):
            snippet = text[max(0, m.start() - 60): m.start() + 40].replace("\n", " ")
            err(f"currency amount found in {rel}: ...{snippet}...")
            break

        # 3. no star rating / review count
        for pattern in (r"\d+(?:\.\d+)?\s*out of 5\s*stars", r"★", r"☆",
                        r'"aggregateRating"', r"ratingValue", r"reviewCount"):
            if re.search(pattern, text, re.IGNORECASE):
                err(f"rating pattern '{pattern}' found in {rel}")

        # 4. Two different things must not be confused.
        #    A product CTA (class="btn") must carry the tag, or it must not exist.
        #    A citation to an Amazon policy page or a listing is evidence, not a sell,
        #    and must be marked rel="nofollow" so it is never treated as a Special Link.
        for anchor in re.finditer(r"<a\b([^>]*)>", text):
            attrs = anchor.group(1)
            href_m = re.search(r'href="([^"]+)"', attrs)
            if not href_m:
                continue
            url = href_m.group(1)
            if "amazon." not in url:
                continue
            is_cta = 'class="btn"' in attrs
            is_cite = "cite" in attrs and "nofollow" in attrs
            if is_cta and TRACKING_ID not in url:
                err(f"product CTA without tracking tag in {rel}: {url}")
            elif not is_cta and not is_cite:
                err(f"unmarked amazon anchor in {rel}: {url} (needs the tag as a CTA, or class=cite rel=nofollow as evidence)")

        # 6. spec source citations on product pages
        if rel in product_pages:
            for sid in re.findall(r'class="srclink"[^>]*>(S\d+)<', text):
                if sid not in source_ids:
                    err(f"unknown source id {sid} cited on {rel}")

    # 7. Archive pages are noindex and must not appear in the sitemap.
    sitemap = (DOCS / "sitemap.xml").read_text(encoding="utf-8")
    if "<url>" in sitemap:
        err("noindex editorial archive sitemap must not contain URLs")

    # extra: feed and sitemap parse as XML
    import xml.etree.ElementTree as ET
    for name in ("sitemap.xml", "feed.xml"):
        try:
            ET.parse(DOCS / name)
        except ET.ParseError as exc:
            err(f"{name} is not valid XML: {exc}")

    return report()


def report() -> int:
    pages = len(html_files()) if DOCS.exists() else 0
    if errors:
        print(f"FAIL: {len(errors)} problem(s) across {pages} page(s)\n")
        for msg in errors[:80]:
            print("  -", msg)
        if len(errors) > 80:
            print(f"  ... and {len(errors) - 80} more")
        return 1
    print(f"PASS: {pages} pages checked")
    print("  - internal links resolve")
    print("  - no currency amounts")
    print("  - no star ratings or review counts")
    print("  - no untagged product CTA renders; source citations are explicitly nofollow")
    print("  - Associates statement present on every page")
    print("  - every cited source id exists")
    print("  - archive pages are noindex and omitted from its sitemap; feed and sitemap parse as XML")
    return 0


if __name__ == "__main__":
    sys.exit(main())
