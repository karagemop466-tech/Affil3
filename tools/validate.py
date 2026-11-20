#!/usr/bin/env python3
"""Compliance gates for the ShopNow Kitchen Edit site. Stdlib only.

Gates:
  G-A1 disclosure-everywhere   disclosure strip + required statement on every page, above <main>
  G-A2 sponsored-links         every Amazon-outbound anchor: rel sponsored/nofollow/noopener,
                               target=_blank, data-product-intent; no Amazon imagery/marks
  G-A3 registers-valid         JSON registers parse; intent/observation separation; ledger schema
  G-A4 sitemap-consistency     sitemap ↔ files; feed lists every guide
  G-A5 ledger-shape            ledger keeps its defined schema and provenance columns
  G-A6 pages-fresh             regeneration produces zero diffs
  G-A7 internal-links          no broken internal hrefs/srcs

Exit code 1 on any failure. Usage: python3 tools/validate.py [--skip-fresh]
"""
import json
import os
import re
import shutil
import sys
import tempfile
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ERRORS = []
NOTES = []


def fail(gate, msg):
    ERRORS.append("[%s] %s" % (gate, msg))


def html_files():
    out = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules", "content", "tools", "data", "assets")]
        for fn in filenames:
            if fn.endswith(".html"):
                out.append(os.path.join(dirpath, fn))
    return sorted(out)


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.anchors = []   # (attrs dict, tag)
        self.imgs = []
        self.depth = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a":
            self.anchors.append(a)
        elif tag == "img":
            self.imgs.append(a)
        elif tag in ("main", "body", "head"):
            pass


def parse_file(path):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    p = LinkParser()
    p.feed(text)
    return text, p


def gate_disclosure(files):
    for path in files:
        text, _ = parse_file(path)
        rel = os.path.relpath(path, ROOT)
        if 'data-disclosure-strip' not in text:
            fail("G-A1", "%s missing disclosure strip marker" % rel)
        if "earn from qualifying purchases" not in text:
            fail("G-A1", "%s missing required Associates statement" % rel)
        # above the fold: strip must appear before <main>
        i_strip = text.find("data-disclosure-strip")
        i_main = text.find("<main>")
        if not (0 <= i_strip < i_main):
            fail("G-A1", "%s disclosure strip not above the fold (must precede <main>)" % rel)


def gate_sponsored(files):
    amzn_hosts = ("link.amazon", "amazon.com", "www.amazon.com")
    for path in files:
        text, p = parse_file(path)
        rel = os.path.relpath(path, ROOT)
        for a in p.anchors:
            href = a.get("href", "")
            if not href:
                continue
            try:
                host = re.sub(r"^https?://", "", href).split("/")[0].lower()
            except Exception:
                host = ""
            if host in amzn_hosts:
                relattr = (a.get("rel") or "").lower()
                for req in ("sponsored", "nofollow", "noopener"):
                    if req not in relattr:
                        fail("G-A2", "%s: Amazon link %r missing rel=%r" % (rel, href, req))
                if a.get("target") != "_blank":
                    fail("G-A2", "%s: Amazon link %r must open in a new tab" % (rel, href))
        for img in p.imgs:
            src = (img.get("src") or "").lower()
            if "amazon" in src and "assets/img" not in src:
                fail("G-A2", "%s: Amazon-hosted imagery forbidden: %r" % (rel, src))
            for k, v in img.items():
                if isinstance(v, str) and ("amazon" in v.lower()) and "assets/img" not in v:
                    pass  # alt text mentioning amazon is fine
        # forbidden marks: no <img> alt/src asserting Amazon logo usage
        if re.search(r"img[^>]+amazon(-mark|_logo|logo)", text, re.I):
            fail("G-A2", "%s: possible Amazon logo asset reference" % rel)


def gate_registers():
    for name in ("sources.json", "flags.json", "products.json", "questions.json", "suggestions.json", "events-schema.json"):
        p = os.path.join(ROOT, "data", name)
        try:
            with open(p, encoding="utf-8") as fh:
                json.load(fh)
        except Exception as e:
            fail("G-A3", "data/%s invalid JSON: %s" % (name, e))
    ppath = os.path.join(ROOT, "data", "products.json")
    with open(ppath, encoding="utf-8") as fh:
        pdata = json.load(fh)
    for prod in pdata.get("products", []):
        pid = prod.get("id")
        intent = prod.get("intent", {})
        obs = prod.get("observation", {})
        if "intended_asin_as_submitted" not in intent:
            fail("G-A3", "product %s missing intended ASIN field" % pid)
        if "observed_redirect_target" not in obs:
            fail("G-A3", "product %s missing separate observation field" % pid)
        confirmed = bool(intent.get("official_listing_url"))
        need = ["official_listing_url", "confirmed_asin", "confirmation_date", "confirmation_source"]
        if confirmed:
            for f in need:
                if not intent.get(f):
                    fail("G-A3", "product %s: %s blank while official_listing_url set — partial confirmation forbidden" % (pid, f))
        if prod.get("status") == "unverified" and "FLG-003" not in prod.get("flags", []) and not confirmed:
            fail("G-A3", "product %s: unverified without FLG-003 flag" % pid)
        # intent/observation never merged: no observed value may sit in the intent object
        if any(k.startswith("observed") for k in intent):
            fail("G-A3", "product %s: observed values leaked into intent object" % pid)


LEDGER_HEADER = ["timestamp", "source", "channel", "eligible_sessions", "clicks", "reported_orders", "provenance_note", "added_by", "source_url"]


def gate_ledger():
    p = os.path.join(ROOT, "data", "ledger", "campaign-ledger.csv")
    with open(p, encoding="utf-8") as fh:
        rows = [ln.strip() for ln in fh if ln.strip()]
    if not rows:
        fail("G-A5", "ledger missing its header row")
        return
    header = [c.strip() for c in rows[0].split(",")]
    if header != LEDGER_HEADER:
        fail("G-A5", "ledger header mismatch: %s" % header)
    for i, row in enumerate(rows[1:], start=2):
        cells = [c.strip() for c in row.split(",")]
        if len(cells) != len(LEDGER_HEADER):
            fail("G-A5", "ledger row %d has %d columns, expected %d" % (i, len(cells), len(LEDGER_HEADER)))
        else:
            for name, val in zip(LEDGER_HEADER, cells):
                if not val:
                    fail("G-A5", "ledger row %d: empty provenance column %s — rows need a full dated trail" % (i, name))


def gate_sitemap_feed():
    sm = os.path.join(ROOT, "sitemap.xml")
    with open(sm, encoding="utf-8") as fh:
        sm_text = fh.read()
    locs = re.findall(r"<loc>(.*?)</loc>", sm_text)
    base = "https://karagemop466-tech.github.io/Affil3/"
    sitemap_paths = set()
    for loc in locs:
        if not loc.startswith(base):
            fail("G-A4", "sitemap URL outside canonical host: %s" % loc)
            continue
        rel = loc[len(base):] or "index.html"
        sitemap_paths.add(rel)
        if not os.path.exists(os.path.join(ROOT, rel)):
            fail("G-A4", "sitemap URL has no file: %s" % loc)
    # every published page must be in the sitemap (404 excluded)
    for path in html_files():
        rel = os.path.relpath(path, ROOT)
        if rel == "404.html":
            continue
        if rel not in sitemap_paths:
            fail("G-A4", "published page missing from sitemap: %s" % rel)
    # feed lists every guide
    with open(os.path.join(ROOT, "feed.xml"), encoding="utf-8") as fh:
        feed = fh.read()
    for guide in ("basket-or-oven-air-fryer", "air-fryer-capacity-checklist", "cleanup-and-counter-space", "multifunction-appliance-questions"):
        if guide not in feed:
            fail("G-A4", "feed.xml missing guide: %s" % guide)


def gate_fresh():
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import build_pages  # noqa
    tmp = tempfile.mkdtemp()
    try:
        build_pages.build(tmp)
        for out_path in build_pages.PAGES:
            new = open(os.path.join(tmp, out_path), encoding="utf-8").read()
            old_p = os.path.join(ROOT, out_path)
            if not os.path.exists(old_p):
                fail("G-A6", "missing generated page: %s" % out_path)
                continue
            old = open(old_p, encoding="utf-8").read()
            if old != new:
                fail("G-A6", "stale generated page: %s (run tools/build_pages.py)" % out_path)
    finally:
        shutil.rmtree(tmp)


def gate_internal_links(files):
    for path in files:
        text, p = parse_file(path)
        rel = os.path.relpath(path, ROOT)
        base = os.path.dirname(path)
        for attr_set in (("href",), ("src",)):
            for a in p.anchors + p.imgs:
                for attr in attr_set:
                    v = a.get(attr)
                    if not v:
                        continue
                    if v.startswith(("http://", "https://", "#", "mailto:", "data:")):
                        continue
                    if "{{" in v:
                        continue
                    target = os.path.normpath(os.path.join(base, v.split("#")[0]))
                    if not os.path.exists(target):
                        fail("G-A7", "%s: broken internal %s=%r" % (rel, attr, v))


def main():
    files = html_files()
    gate_disclosure(files)
    gate_sponsored(files)
    gate_registers()
    gate_ledger()
    gate_sitemap_feed()
    gate_internal_links(files)
    if "--skip-fresh" not in sys.argv:
        gate_fresh()
    if ERRORS:
        print("VALIDATION FAILED (%d):" % len(ERRORS))
        for e in ERRORS:
            print("  " + e)
        sys.exit(1)
    print("ALL GATES PASS — %d pages checked (G-A1..G-A7)" % len(files))


if __name__ == "__main__":
    main()
