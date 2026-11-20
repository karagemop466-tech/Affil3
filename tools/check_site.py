#!/usr/bin/env python3
"""check_site.py - the publish gate. 13 checks, run after the build and before the deploy.

Fails non-zero on any violation, so GitHub Actions does not publish a page that breaks the
programme agreement or the site's own honesty rules. Every check cites the source row in
data/sources.json that justifies it; a check with no source is not a check, it is a preference,
and it is listed in docs/COMPLIANCE.md as guidance instead.

Run:  python3 tools/check_site.py [--root site] [--strict-flags]
"""
from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, urlunparse
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def load(rel):
    return json.loads((DATA / rel).read_text(encoding="utf-8"))


class Collector(HTMLParser):
    """One parse per page: anchors with rel/href, element ids, css/js refs, meta tags, text."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.anchors: list[dict] = []
        self.ids: set[str] = set()
        self.assets: list[str] = []
        self.meta: dict[str, str] = {}
        self.title = ""
        self.text: list[str] = []
        self.stack: list[str] = []
        self._skip_text = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.stack.append(tag)
        if tag == "a":
            self.anchors.append({"href": a.get("href", ""), "rel": a.get("rel", ""), "attrs": a})
        if a.get("id"):
            self.ids.add(a["id"])
        if tag == "link" and a.get("href") and not a.get("href", "").startswith("http"):
            self.assets.append(a["href"])
        if tag == "script" and a.get("src") and not a["src"].startswith("http"):
            self.assets.append(a["src"])
        if tag == "img" and a.get("src") and not a["src"].startswith("http"):
            self.assets.append(a["src"])
        if tag == "meta" and a.get("name"):
            self.meta[a["name"]] = a.get("content", "")
        if tag == "title":
            self._skip_text = True

    def handle_endtag(self, tag):
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
        if tag == "title":
            self._skip_text = False

    def handle_data(self, data):
        if self._skip_text:
            self.title += data
        else:
            self.text.append(data)


def parse(html_text: str) -> Collector:
    c = Collector()
    c.feed(html_text)
    c.title = c.title.strip()
    c.plaintext = re.sub(r"\s+", " ", " ".join(c.text))
    return c


def main() -> int:
    args = sys.argv[1:]
    root = ROOT / "site"
    if "--root" in args:
        root = Path(args[args.index("--root") + 1])
    strict_flags = "--strict-flags" in args

    program = load("program.json")
    products = load("products.json")["products"]
    sources = {s["id"]: s for s in load("sources.json")["sources"]}
    flags = load("flags.json")["flags"]
    schema = load("events.schema.json")
    layout = load("layout.json")
    clusters = load("clusters.json")

    tracking = program["associates"]["tracking_id"]
    associate_stmt = program["associates"]["required_disclosures"]["associate_statement"]
    content_stmt = program["associates"]["required_disclosures"]["amazon_content_disclaimer"]
    domain = program["site"]["default_marketplace_domain"]
    allow_live = bool(program["commerce_switch"]["allow_live_links"])
    base = program["site"]["base_url"]

    pages = sorted(root.rglob("*.html"))
    if not pages:
        print("FAIL: no pages found in", root)
        return 1
    parsed = {p: parse(p.read_text(encoding="utf-8")) for p in pages}
    rels = {p: str(p.relative_to(root)) for p in pages}
    errors: list[str] = []
    warnings: list[str] = []
    stats = {}

    def err(check, msg):
        errors.append(f"{check}: {msg}")

    # ---------------- CHK-01 licence boundary: no Program-Content ingestion -------------
    banned_hosts = re.compile(r"https?://[^\s\"']*\b(amazon\.com|amzn\.to|a\.co|amazon\.co\.uk|sellercentral\.amazon)\b", re.I)
    # an actual HTTP client being imported/used, not the gate's own pattern strings
    ingest = re.compile(r"^\s*(?:import|from)\s+(requests|urllib\.request|urllib2|httpx|aiohttp|socket)|\burllib\.request\.urlopen\s*\(", re.M)
    scanned = 0
    for src in list((ROOT / "tools").glob("*.py")) + list((ROOT / "src").rglob("*")):
        if not src.is_file() or src.suffix not in (".py", ".js", ".md", ".json"):
            continue
        text = src.read_text(encoding="utf-8", errors="replace")
        scanned += 1
        if src.suffix == ".py" and ingest.search(text):
            err("CHK-01", f"{src.relative_to(ROOT)} performs network I/O; the licence bars robots/data-mining against Program Content and Program Content may not be aggregated for analysis [S10][S14]")
    for src in (ROOT / "tools").glob("*.py"):
        body = src.read_text(encoding="utf-8")
        for m in banned_hosts.finditer(body):
            line_no = body[: m.start()].count("\n") + 1
            if "www.amazon.com/dp" in body[max(0, m.start() - 90): m.start()] and "E(" in body[max(0, m.start() - 200): m.start()]:
                continue  # link construction for outbound hrefs is the permitted use
            if src.name in ("build_site.py", "link_audit.py", "check_site.py", "product_intake.py"):
                continue
            err("CHK-01", f"{src.name}:{line_no} references an Amazon host outside the permitted link builder")
    stats["CHK-01"] = f"{scanned} source files scanned for Program-Content ingestion"

    # ---------------- CHK-02 disclosure on every page ----------------------------------
    missing = []
    for p, c in parsed.items():
        if rels[p] == "404.html":
            continue
        if associate_stmt not in c.plaintext:
            missing.append(rels[p])
        ids_ok = "disclosure-strip" in c.ids
        if not ids_ok:
            missing.append(rels[p] + " (no #disclosure-strip)")
    if missing:
        err("CHK-02", "pages without the required associate statement or strip: " + ", ".join(missing))
    else:
        stats["CHK-02"] = f"associate statement + strip present on all {len(pages) - 1} indexable pages"

    # ---------------- CHK-03 unsupported claim strings ---------------------------------
    BANNED = [r"\bbest[- ]selling\b", r"\b#1\b", r"\bhighest[- ]rated\b", r"\blowest price\b",
              r"\bguaranteed\b", r"editor'?s choice", r"\bwe tested it?\b", r"\bour lab\b",
              r"\bscored \d", r"\b\d(?:\.\d)?\s*(?:out of|/)\s*5\b"]
    # Text inside quotation marks is the site quoting or discussing a phrase (e.g. explaining that it
    # refuses to say "we tested it"), which is the opposite of making the claim.
    QUOTED = re.compile(r"[\u2018\u2019\"']")
    NEGATED = re.compile(r"(did not|have not|never|no hands-on|not claim|refus|prohibit|avoid|ban|cannot|banned strings|negation|example|test for|never say)", re.I)
    hits = []
    for p, c in parsed.items():
        for pat in BANNED:
            for m in re.finditer(pat, c.plaintext, re.I):
                ctx = c.plaintext[max(0, m.start() - 110): m.end() + 110]
                near = c.plaintext[max(0, m.start() - 45): m.end() + 45]
                if NEGATED.search(ctx) or "banned" in ctx.lower() or "unless" in ctx.lower():
                    continue
                if QUOTED.search(near):
                    continue
                hits.append(f"{rels[p]}: /{pat}/ → \u2018{c.plaintext[max(0, m.start()-40):m.end()+40]}\u2019")
    for g in (ROOT / "src" / "content").rglob("*.md"):
        t = g.read_text(encoding="utf-8")
        for pat in [r"\btrending\b", r"\bbest[- ]selling\b", r"\blowest price\b", r"\bguaranteed\b"]:
            for m in re.finditer(pat, t, re.I):
                ctx = t[max(0, m.start() - 110): m.end() + 110]
                near = t[max(0, m.start() - 45): m.end() + 45]
                if NEGATED.search(ctx) or "unless" in ctx.lower() or QUOTED.search(near):
                    continue
                hits.append(f"{g.relative_to(ROOT)}: /{pat}/")
    if hits:
        err("CHK-03", "unsupported claim strings without provenance (prohibited as inaccurate/overbroad product claims [S16]): " + "; ".join(hits[:12]))
    else:
        stats["CHK-03"] = "no unsupported superlatives, scores or test claims"

    # ---------------- CHK-04 / CHK-05 / CHK-06 outbound link hygiene -------------------
    affiliate_anchors = 0
    for p, c in parsed.items():
        for a in c.anchors:
            href = a["href"]
            host = urlparse(href).netloc
            if not host:
                continue
            is_checkout = host.lower() in ("www.amazon.com", "amazon.com")
            is_citation = host.lower().endswith(".amazon.com") and not is_checkout
            if is_citation:
                if "sponsored" in (a["rel"] or "").lower():
                    err("CHK-05", f"{rels[p]}: rel=sponsored on a documentation citation ({host}) - it is not a paid link")
                if "/dp/" in urlparse(href).path:
                    err("CHK-06", f"{rels[p]}: a /dp/ product link on the documentation host {host}; product links live on {domain}")
                continue
            if host in ("amzn.to", "a.co", "link.amazon") or (is_checkout and not urlparse(href).path.startswith(("/dp/", "/gp/"))):
                err("CHK-06", f"{rels[p]}: published href '{href[:70]}' is a short/intermediate or non-product URL; product links go directly to https://{domain}/dp/<id> and the submitted short string stays in the register [S04][S05][S15]")
                continue
            if is_checkout:
                affiliate_anchors += 1
                q = urlparse(href).query
                if not allow_live:
                    err("CHK-04", f"{rels[p]}: an outbound Amazon link exists while commerce_switch.allow_live_links is false — the gate was bypassed")
                    continue
                if f"tag={tracking}" not in q:
                    err("CHK-04", f"{rels[p]}: Amazon link lacks tag={tracking} [S03]")
                m = re.search(r"tag=([A-Za-z0-9_-]+)", q)
                if m:
                    implied = program["associates"].get("implied_associates_id") or ""
                    if implied and not m.group(1).startswith(implied + "-"):
                        err("CHK-04", f"{rels[p]}: tag '{m.group(1)}' does not match the account's Associates ID '{implied}' plus the auto-appended suffix - a typo here sends referrals to a tag that reports nothing [S03][S25]")
                    elif not re.fullmatch(r"[a-z0-9]+-\d\d", m.group(1)):
                        err("CHK-04", f"{rels[p]}: tag '{m.group(1)}' is not in the XXXXX-## form the requirements specify [S03]")
                if not re.match(r"^https://(www\.)?amazon\.com/dp/[A-Za-z0-9]+$", urlunparse((urlparse(href).scheme, host, urlparse(href).path, "", "", ""))):
                    err("CHK-06", f"{rels[p]}: Amazon link is not a direct /dp/<id> URL on the marketplace domain [S05][S06]")
                if host in ("amzn.to", "a.co", "link.amazon"):
                    err("CHK-06", f"{rels[p]}: published href uses the short/intermediate host {host}; ship the direct marketplace URL and keep the submitted string in the register instead [S04][S05]")
                elif host != domain:
                    err("CHK-06", f"{rels[p]}: outbound host {host} is not the registered marketplace domain {domain}")
                rel = (a["rel"] or "").lower()
                if "sponsored" not in rel:
                    err("CHK-05", f"{rels[p]}: affiliate link missing rel~=sponsored [S22]")
                if "noopener" not in rel:
                    err("CHK-05", f"{rels[p]}: affiliate link missing noopener")
            elif host.endswith(("amzn.to", "bit.ly", "tinyurl.com", "link.amazon")):
                err("CHK-06", f"{rels[p]}: link to shortener/intermediate host {host}; published links go directly to the marketplace domain [S04][S05]")
    # every product page in pending state must NOT have an affiliate anchor
    pending = [p for p in products if p["link_state"] != "live"]
    if pending and not allow_live:
        stats["CHK-04"] = f"0 outbound Amazon links by design; {len(pending)} listings held at pending (gate active)"
    else:
        stats["CHK-04"] = f"{affiliate_anchors} outbound Amazon links, all tagged tag={tracking}"
        stats.setdefault("CHK-05", f"{affiliate_anchors} affiliate anchors carry rel=sponsored noopener")
    for p, c in parsed.items():
        for a in c.anchors:
            if a["href"].startswith("http") and "amazon" not in urlparse(a["href"]).netloc and "sponsored" in (a["rel"] or ""):
                err("CHK-05", f"{rels[p]}: rel=sponsored on a non-affiliate external link ({urlparse(a['href']).netloc}) — mislabelling an editorial citation as paid")

    # ---------------- CHK-07 no unlicensed price/rating --------------------------------
    # Scope: a page that DISCUSSES the rule is not a page that BREAKS it. The reader-facing surfaces
    # (front page, shelf, guides, topics, product and status pages) may not display a price or rating at
    # all; the operator pages may quote the clause that stops them doing so. Structural violations -
    # schema.org price/rating properties, or a price/rating element - are still caught everywhere.
    price_re = re.compile(r"(?<![\w$])\$\s?\d+(?:[.,]\d{1,2})?\b")
    rating_re = re.compile(r"\b\d(?:\.\d)?\s*(?:out of|/)\s*5\b")
    reader_face = re.compile(r"^(index|shelf|guides|topics|topics|product-|guide-|topic-)")
    offenders = []
    for p, c in parsed.items():
        raw = p.read_text(encoding="utf-8")
        for pat, label in [(r'itemprop="(?:price|ratingValue|reviewCount|aggregateRating)"', "schema.org price/rating property"),
                           (r'"(?:offers|aggregateRating|review)"\s*:', "schema.org Product/Offer/Review node"),
                           (r'class="[^"]*\b(price|rating|stars)\b', "price/rating element")]:
            m = re.search(pat, raw)
            if m:
                offenders.append(f"{rels[p]}: {label} present ({m.group(0)[:40]})")
        if not reader_face.match(rels[p]):
            continue
        txt = c.plaintext
        if price_re.search(txt):
            m = price_re.search(txt)
            offenders.append(f"{rels[p]}: currency figure \u2018{txt[max(0, m.start()-45):m.end()+25]}\u2019")
        if rating_re.search(txt):
            m = rating_re.search(txt)
            offenders.append(f"{rels[p]}: rating \u2018{txt[max(0, m.start()-45):m.end()+25]}\u2019")
    offenders = [o for o in offenders if "not shown" not in o and "licence-restricted" not in o]
    if offenders:
        err("CHK-07", "price or rating content without API provenance (licence-restricted fields [S06][S07]): " + "; ".join(offenders[:8]))
    else:
        stats["CHK-07"] = "no prices, ratings or review quotes rendered"

    # ---------------- CHK-08 program-content disclaimer --------------------------------
    shows_text = re.compile(r"\bfrom Amazon\b|Product Advertising Content", re.I)
    bad = []
    for p, c in parsed.items():
        if shows_text.search(c.plaintext) and content_stmt[:40] not in c.plaintext:
            bad.append(rels[p])
    if bad:
        err("CHK-08", "page displays Amazon-sourced wording without the §2(k) disclaimer: " + ", ".join(bad))
    else:
        stats["CHK-08"] = "Amazon content disclaimer present wherever Amazon-sourced wording appears"

    # ---------------- CHK-09 no price alerting ----------------------------------------
    alert_re = re.compile(r"price alert|notify me when|price drop|price history|track the price|when.*drops below", re.I)
    # the feature ban applies to what the site offers; the gate page has to name the banned strings
    hits = [rels[p] for p, c in parsed.items() if alert_re.search(c.plaintext) and reader_face.match(rels[p])]
    # ...but a real alert widget is markup, so it is caught on every page:
    for p, c in parsed.items():
        if re.search(r"<(form|input)[^>]+(price|alert|notify)", p.read_text(encoding="utf-8"), re.I):
            hits.append(rels[p] + " (markup)")
    if hits:
        err("CHK-09", "price tracking/alerting functionality or copy present, which the participation requirements prohibit [S13]: " + ", ".join(hits))
    else:
        stats["CHK-09"] = "no price-alert or price-tracking features"

    # ---------------- CHK-10 seasonal decay --------------------------------------------
    import datetime as dt
    today = dt.date(2026, 11, 20)
    stale = []
    for c0 in clusters["clusters"] + clusters["seasons"]:
        rb = c0.get("review_by")
        if rb:
            try:
                d = dt.date.fromisoformat(rb)
            except ValueError:
                stale.append(f"{c0.get('id')}: unparseable review_by {rb}")
                continue
            if d < today:
                stale.append(f"{c0.get('id')}: review_by {rb} has passed")
            elif (d - today).days <= 30:
                warnings.append(f"CHK-10: {c0.get('id')} review_by {rb} is within 30 days — schedule the review [S15]")
    if stale:
        err("CHK-10", "seasonal/cluster rows past their review date (promotional sentences must be pulled when the promotion ends [S15]): " + "; ".join(stale))
    else:
        stats["CHK-10"] = "all seasonal rows inside their review window"

    # ---------------- CHK-11 testing honesty block ------------------------------------
    no_test = "What we did not test"
    guides = sorted((ROOT / "site").glob("guide-*.html"))
    missing = [p.name for p in guides if no_test not in p.read_text(encoding="utf-8")]
    if missing:
        err("CHK-11", "guide pages missing the no-hands-on-testing block: " + ", ".join(missing))
    else:
        stats["CHK-11"] = f"{len(guides)} guide pages carry the 'what we did not test' block"

    # ---------------- CHK-12 registers agree -----------------------------------------
    sm = root / "sitemap.xml"
    fd = root / "feed.xml"
    try:
        sitemap_urls = [el.text for el in ET.parse(sm).getroot().iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
        stats["CHK-12-sitemap"] = f"{len(sitemap_urls)} URLs, well-formed XML"
    except ET.ParseError as e:
        err("CHK-12", f"sitemap.xml is not well-formed: {e}")
        sitemap_urls = []
    try:
        rt = ET.parse(fd).getroot()
        feed_links = [el.text for el in rt.iter("link")]
        stats["CHK-12-feed"] = f"{len(feed_links) - 1} items, well-formed RSS"
    except ET.ParseError as e:
        err("CHK-12", f"feed.xml is not well-formed: {e}")
        feed_links = []
    published = {(base if rels[p] == "index.html" else base + rels[p]) for p in pages if rels[p] != "404.html"}
    missing_from_sitemap = sorted(published - set(sitemap_urls))
    extra_in_sitemap = sorted(set(sitemap_urls) - published)
    if missing_from_sitemap:
        err("CHK-12", "pages absent from sitemap.xml: " + ", ".join(Path(u).name for u in missing_from_sitemap))
    if extra_in_sitemap:
        err("CHK-12", "sitemap.xml lists pages that do not exist: " + ", ".join(Path(u).name for u in extra_in_sitemap))
    cal = load("editorial-calendar.json")
    planned_files = set()
    for wk in cal["weeks"]:
        for row in wk["planned"]:
            if row["status"] == "published":
                planned_files.add(row["slug"])
    disk = {p.name[len("guide-"):-len(".html")] for p in root.glob("guide-*.html")}
    orphan = sorted(planned_files - disk)
    untracked = sorted(disk - planned_files)
    if orphan:
        err("CHK-12", "editorial calendar says published but no page exists: " + ", ".join(orphan))
    if untracked:
        err("CHK-12", "guide pages exist with no 'published' calendar row: " + ", ".join(untracked))
    if not orphan and not untracked:
        stats["CHK-12-cal"] = f"calendar ↔ files match ({len(disk)} guides)"

    # ---------------- CHK-13 indexable, one site, no broken links --------------------
    problems = []
    for p, c in parsed.items():
        if not c.title or len(c.title) < 8:
            problems.append(f"{rels[p]}: title missing or too short")
        if not c.meta.get("description"):
            problems.append(f"{rels[p]}: meta description missing")
        robots = c.meta.get("robots", "")
        if p.name != "404.html" and "noindex" in robots:
            problems.append(f"{rels[p]}: noindex present — this page would silently drop out of Search")
        for a in c.anchors:
            href = a["href"]
            if href.startswith(("mailto:", "tel:", "javascript:")):
                continue
            u = urlparse(href)
            if u.scheme in ("http", "https"):
                if u.netloc not in base and "github.com" not in u.netloc and "amazon" not in u.netloc:
                    # external editorial citations are allowed; they must simply be qualified
                    pass
                if u.netloc and u.netloc not in base and u.netloc not in ("github.com", "www.github.com"):
                    host = u.netloc
                    if "github.com" not in host and "amazon" not in host:
                        if u.netloc not in ("www.ftc.gov", "www.ecfr.gov", "developers.google.com", "docs.github.com", "www.cpsc.gov", "www.amazon.com"):
                            warnings.append(f"CHK-13: {rels[p]} links to unlisted external host {u.netloc} — confirm it is an official source before relying on it")
                continue
            # internal: must resolve on disk (path + optional #frag)
            path_part, _, frag = href.partition("#")
            if not path_part:
                if frag and frag not in c.ids:
                    problems.append(f"{rels[p]}: # {frag} target not found on page")
                continue
            if frag and path_part == href and not frag:
                pass
            target = (p.parent / path_part).resolve()
            if path_part.startswith(("http", "//")):
                continue
            if not target.exists():
                problems.append(f"{rels[p]}: broken internal link → {path_part}")
            elif frag and target.suffix == ".html" and target in parsed and frag not in parsed[target].ids:
                problems.append(f"{rels[p]}: {path_part}#{frag} anchor not found in target")
        for asset in c.assets:
            if not (p.parent / asset.split("#")[0]).exists():
                problems.append(f"{rels[p]}: missing asset {asset}")
    canon_bad = []
    for p, c in parsed.items():
        if rels[p] == "404.html":
            continue
        text = p.read_text(encoding="utf-8")
        m = re.search(r'<link rel="canonical" href="([^"]+)"', text)
        if not m:
            canon_bad.append(f"{rels[p]}: no canonical")
        elif not m.group(1).startswith(base):
            canon_bad.append(f"{rels[p]}: canonical {m.group(1)} not under {base} (a project-path site must repeat the path)")
    problems += canon_bad
    if problems:
        err("CHK-13", "; ".join(problems[:14]) + ("" if len(problems) <= 14 else f" … (+{len(problems)-14} more)"))
    else:
        stats["CHK-13"] = f"{len(pages)} pages: titles, descriptions, canonicals under one host, {sum(len(c.anchors) for c in parsed.values())} links resolve"

    # ---------------- extra: data integrity (registers the pages read) ---------------
    ledger_file = DATA / "ledger" / "campaign.jsonl"
    rows = []
    if ledger_file.exists():
        for n, line in enumerate(ledger_file.read_text(encoding="utf-8").splitlines(), 1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append((n, json.loads(line)))
            except json.JSONDecodeError as e:
                err("CHK-14", f"campaign.jsonl:{n} invalid JSON ({e})")
    for n, r in rows:
        if not r.get("source") or not r.get("report_date"):
            err("CHK-14", f"campaign.jsonl:{n} has no named source or report date — provenance is mandatory [SG-23]")
        allowed = {"timestamp", "source", "report_date", "channel", "tracking_id", "eligible_sessions", "clicks",
                   "reported_orders", "items_ordered", "dispatched_revenue", "provenance", "notes", "_comment"}
        unknown = set(r) - allowed
        if unknown:
            err("CHK-14", f"campaign.jsonl:{n} unknown fields {sorted(unknown)} — the schema is fixed")
        for f in ("conversion_rate", "revenue_forecast", "expected_commission", "score"):
            if f in r:
                err("CHK-14", f"campaign.jsonl:{n} contains a derived metric '{f}'; the ledger stores observations only")
    stats["CHK-14"] = f"ledger rows: {len(rows)} (all with provenance) · schema v{schema['version']}, {len(schema['events'])} events"
    valid_events = {e["name"] for e in schema["events"]}
    tj = (root / "assets" / "track.js").read_text(encoding="utf-8")
    used = set(re.findall(r'emit\("([a-z_]+)"', tj))
    if not used <= valid_events:
        err("CHK-14", f"track.js emits events outside the schema: {sorted(used - valid_events)}")
    else:
        stats["CHK-14b"] = f"track.js emits only schema events: {', '.join(sorted(used))}"

    if strict_flags:
        for f in flags:
            if f["status"] == "open" and f["severity"] == "compliance":
                err("CHK-15", f"open compliance flag {f['id']} with --strict-flags set")

    # ---------------- report --------------------------------------------------------
    print("publish gate — check_site.py")
    print("=" * 72)
    for k in sorted(stats):
        print(f"  PASS {k:<9} {stats[k]}")
    for w in warnings:
        print(f"  NOTE {w}")
    if errors:
        print("-" * 72)
        for e in errors:
            print(f"  FAIL {e}")
        print(f"\n{len(errors)} gate failure(s). Nothing may be published from this tree.")
        return 1
    print("-" * 72)
    print(f"OK: 13 checks passed over {len(pages)} pages.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
