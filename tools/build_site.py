#!/usr/bin/env python3
"""Build the Countertop Journal static site into docs/ (GitHub Pages source).

Inputs : data/*.json, data/campaign_ledger.csv, content/guides/*.md, content/pages/*.md, assets/
Outputs: docs/** (regenerated from scratch on every run)

Stdlib only. Fails loudly on unknown link tokens, missing source rows, or malformed data,
so a broken reference cannot be published silently.

Link tokens accepted in Markdown content:
  [text]({{link:P01}})     -> submitted short link for product P01 (sponsored)
  [text]({{link:SRC-11}})  -> source register URL for SRC-11
  [text](@/some/path/)     -> internal page, resolved relative to the current page
"""
from __future__ import annotations

import csv
import datetime as dt
import email.utils
import html
import json
import pathlib
import re
import shutil
import sys
from urllib.parse import urlsplit

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
CONTENT = ROOT / "content"
ASSETS = ROOT / "assets"
OUT = ROOT / "docs"


def load(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


SITE = load("site.json")
PRODUCTS = load("products.json")["products"]
PMAP = {p["id"]: p for p in PRODUCTS}
SOURCES = load("sources.json")["sources"]
SMAP = {s["id"]: s for s in SOURCES}
FINDINGS = load("findings.json")["findings"]
QUESTIONS = load("questions.json")["questions"]
SUGGESTIONS = load("suggestions.json")["suggestions"]
FLAGS = load("flags.json")["flags"]
EVENTS = load("analytics_events.json")
CATS = {c["id"]: c for c in SITE["categories"]}
CLUSTERS = {c["id"]: c for c in SITE["clusters"]}
BUILD_DATE = SITE["build_date"]
BASE = SITE["base_url"]
ENDPOINT = SITE.get("analytics_endpoint", "")
SITE_NAME = SITE["name"]
DISCLOSURE = SITE["associates_statement"]
TRACKING_ID = SITE["tracking_id"]


class BuildError(Exception):
    pass


# ---------------------------------------------------------------- helpers

def esc(value) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def fdate(iso: str) -> str:
    if not iso:
        return ""
    d = dt.date.fromisoformat(iso)
    return f"{d.day} {d.strftime('%b')} {d.year}"


def rfc822(iso: str) -> str:
    d = dt.date.fromisoformat(iso)
    return email.utils.format_datetime(dt.datetime(d.year, d.month, d.day, 12, 0, tzinfo=dt.timezone.utc))


def host_of(url: str) -> str:
    return (urlsplit(url).hostname or "").lower()


def is_amazon(url: str) -> bool:
    h = host_of(url)
    return h == "link.amazon" or h == "amazon.com" or h.endswith(".amazon.com")


def ext_link(url: str, label: str, cls: str = "", extra: str = "") -> str:
    """External anchor. Amazon links always carry rel=sponsored (Google's paid/affiliate value)."""
    rel = "sponsored noopener" if is_amazon(url) else "noopener external"
    klass = f' class="{cls}"' if cls else ""
    return (f'<a href="{esc(url)}" rel="{rel}" target="_blank"{klass}{extra}>{esc(label)}</a>')


def badge(text: str, kind: str | None = None) -> str:
    kind = kind or status_kind(text)
    return f'<span class="badge badge--{kind}">{esc(text)}</span>'


def status_kind(s: str) -> str:
    low = (s or "").lower()
    if low in ("destination_confirmed",):
        return "ok"
    if low == "unverified":
        return "warn"
    if "flag" in low:
        return "flag"
    if low.startswith("verified") or low.startswith("destination confirmed") or low.startswith("read"):
        return "ok"
    if any(k in low for k in ("unverified", "not retrieved", "not in repository", "not done",
                              "not deployed", "needs review", "not confirmed", "not recorded")):
        return "warn"
    if "awaiting" in low or "decide" in low or "proposed" in low:
        return "decide"
    return "muted"


def src_ids_linked(text: str) -> str:
    """Escape text, then turn SRC-NN ids into links to the source register URL."""
    escaped = esc(text)

    def repl(m):
        sid = m.group(0)
        if sid in SMAP:
            return ext_link(SMAP[sid]["url"], sid)
        return sid

    return re.sub(r"SRC-\d{2}", repl, escaped)


def product_status_badge(p: dict) -> str:
    if p["status"] == "destination_confirmed":
        return badge("Destination confirmed", "ok")
    return badge("Unverified: checkpoint page", "warn")


def listing_terms(p: dict) -> list[str]:
    core = p.get("listing_title") or ""
    if not core:
        return []
    parts = [t.strip() for t in re.split(r"\s*\|\s*|,\s+", core) if t.strip()]
    terms = []
    for t in parts[1:]:  # first part is the name, already shown as display_name
        if len(t) > 48:
            continue
        terms.append(t)
        if len(terms) == 4:
            break
    return terms


# ---------------------------------------------------------------- guides

def parse_front_matter(text: str):
    if not text.startswith("---\n"):
        raise BuildError("content file is missing front matter")
    end = text.index("\n---\n", 4)
    header = text[4:end]
    body = text[end + 5:]
    meta = {}
    for line in header.splitlines():
        if not line.strip():
            continue
        key, _, value = line.partition(":")
        value = value.strip()
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        meta[key.strip()] = value
    return meta, body


def load_guides():
    guides = []
    for path in sorted((CONTENT / "guides").glob("*.md")):
        meta, body = parse_front_matter(path.read_text(encoding="utf-8"))
        for key in ("title", "slug", "description", "cluster", "published", "status", "products", "sources"):
            if key not in meta:
                raise BuildError(f"{path.name}: missing front matter key '{key}'")
        if meta["cluster"] not in CLUSTERS:
            raise BuildError(f"{path.name}: unknown cluster '{meta['cluster']}'")
        for pid in [x.strip() for x in meta["products"].split(",") if x.strip()]:
            if pid not in PMAP:
                raise BuildError(f"{path.name}: unknown product '{pid}'")
        for sid in [x.strip() for x in meta["sources"].split(",") if x.strip()]:
            if sid not in SMAP:
                raise BuildError(f"{path.name}: unknown source '{sid}'")
        meta["body"] = body
        meta["file"] = path.name
        meta["words"] = len(re.findall(r"\w+", body))
        meta["read_minutes"] = max(1, round(meta["words"] / 220))
        guides.append(meta)
    guides.sort(key=lambda g: (g["published"], g["slug"]))
    return guides


# ---------------------------------------------------------------- markdown

INLINE = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)|\*\*([^*]+)\*\*|`([^`]+)`")


def resolve_href(url: str, path: str):
    """Return (href, is_external) for a Markdown link target, relative to the page at `path`."""
    depth = path.count("/")
    root = "../" * depth
    if url.startswith("{{link:") and url.endswith("}}"):
        key = url[len("{{link:"):-2]
        if key in PMAP:
            return PMAP[key]["submitted_url"], True
        if key in SMAP:
            return SMAP[key]["url"], True
        raise BuildError(f"unknown link token {url} in {path}")
    if url.startswith("@/"):
        target = url[2:]
        if not target.endswith("/") and "." not in target.rsplit("/", 1)[-1]:
            target += "/"
        return root + target, False
    return url, url.startswith("http")


def inline(text: str, path: str) -> str:
    out = []
    pos = 0
    for m in INLINE.finditer(text):
        out.append(esc(text[pos:m.start()]))
        if m.group(1) is not None:
            href, external = resolve_href(m.group(2), path)
            label = m.group(1)
            if external:
                out.append(ext_link(href, label))
            else:
                out.append(f'<a href="{esc(href)}">{esc(label)}</a>')
        elif m.group(3) is not None:
            out.append(f"<strong>{esc(m.group(3))}</strong>")
        elif m.group(4) is not None:
            out.append(f"<code>{esc(m.group(4))}</code>")
        pos = m.end()
    out.append(esc(text[pos:]))
    return "".join(out)


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def md_to_html(md: str, path: str) -> str:
    lines = md.splitlines()
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            i += 1
            continue
        if line.startswith("## "):
            text = line[3:].strip()
            out.append(f'<h2 id="{slugify(text)}">{inline(text, path)}</h2>')
            i += 1
        elif line.startswith("### "):
            text = line[4:].strip()
            out.append(f"<h3>{inline(text, path)}</h3>")
            i += 1
        elif re.match(r"^- \[[ xX]\] ", line):
            items = []
            while i < len(lines) and re.match(r"^- \[[ xX]\] ", lines[i]):
                items.append(re.sub(r"^- \[[ xX]\] ", "", lines[i]))
                i += 1
            out.append('<ul class="checklist">' + "".join(
                f'<li><span class="box" aria-hidden="true"></span>{inline(t, path)}</li>' for t in items) + "</ul>")
        elif re.match(r"^[-*] ", line):
            items = []
            while i < len(lines) and re.match(r"^[-*] ", lines[i]):
                items.append(re.sub(r"^[-*] ", "", lines[i]))
                i += 1
            out.append("<ul>" + "".join(f"<li>{inline(t, path)}</li>" for t in items) + "</ul>")
        elif re.match(r"^\d+\. ", line):
            items = []
            while i < len(lines) and re.match(r"^\d+\. ", lines[i]):
                items.append(re.sub(r"^\d+\. ", "", lines[i]))
                i += 1
            out.append("<ol>" + "".join(f"<li>{inline(t, path)}</li>" for t in items) + "</ol>")
        elif line.startswith("> "):
            quoted = []
            while i < len(lines) and lines[i].startswith("> "):
                quoted.append(lines[i][2:])
                i += 1
            out.append(f"<blockquote><p>{inline(' '.join(quoted), path)}</p></blockquote>")
        else:
            para = []
            while i < len(lines) and lines[i].strip() and not re.match(
                    r"^(## |### |[-*] |\d+\. |> |- \[)", lines[i]):
                para.append(lines[i].strip())
                i += 1
            out.append(f"<p>{inline(' '.join(para), path)}</p>")
    return "\n".join(out)


def load_md_page(name: str):
    meta, body = parse_front_matter((CONTENT / "pages" / f"{name}.md").read_text(encoding="utf-8"))
    return meta, body


# ---------------------------------------------------------------- page chrome

NAV = [("Products", "products/"), ("Categories", "categories/"), ("Guides", "guides/"), ("About", "about/")]
DASHBOARDS = [("Sources", "sources/"), ("Findings", "findings/"), ("Questions", "questions/"),
              ("Suggestions", "suggestions/"), ("Flagged for Review", "flagged-for-review/"),
              ("Ledger &amp; analytics", "ledger/"), ("Executive summary", "executive-summary/")]
SITE_LINKS = [("Products", "products/"), ("Categories", "categories/"), ("Guides", "guides/"),
              ("Disclosure", "disclosure/"), ("Privacy", "privacy/"), ("About", "about/"),
              ("RSS feed", "feed.xml"), ("Sitemap", "sitemap.xml")]


def masthead(root: str, active: str) -> str:
    nav_items = []
    for label, target in NAV:
        cur = ' aria-current="page"' if active == target else ""
        nav_items.append(f'<a href="{root}{target}"{cur}>{label}</a>')
    return f"""<header class="masthead">
  <div class="mast-inner wrap">
    <p class="edition">Buyer guides &middot; {fdate(BUILD_DATE)} &middot; Sponsored links are marked</p>
    <a class="wordmark" href="{root}">{esc(SITE_NAME)}</a>
    <p class="dek">{esc(SITE["tagline"])}</p>
    <nav class="navgroup" aria-label="Main">{"".join(nav_items)}</nav>
  </div>
</header>
<aside class="disclosure-strip" id="disclosure" aria-label="Affiliate disclosure">
  <div class="wrap"><strong>Disclosure.</strong> {esc(DISCLOSURE)} Links to Amazon are sponsored.
  <a href="{root}disclosure/">Full disclosure</a></div>
</aside>"""


def footer(root: str) -> str:
    site = "".join(f'<li><a href="{root}{t}">{l}</a></li>' for l, t in SITE_LINKS)
    dash = "".join(f'<li><a href="{root}{t}">{l}</a></li>' for l, t in DASHBOARDS)
    return f"""<footer class="site-footer">
  <div class="disclosure-strip footer-strip"><div class="wrap"><strong>Disclosure.</strong> {esc(DISCLOSURE)}
  Links to Amazon are sponsored (<code>rel="sponsored"</code>) and may earn us a commission at no extra cost to you.
  We do not show prices or star ratings. <a href="{root}disclosure/">Full disclosure</a></div></div>
  <div class="wrap foot-grid">
    <section><h2>Site</h2><ul>{site}</ul></section>
    <section><h2>Dashboards</h2><ul>{dash}</ul></section>
    <section><h2>Build</h2>
      <p>Built {fdate(BUILD_DATE)} from <a href="{esc(SITE["repo_url"])}" rel="noopener external">the repository</a>.</p>
      <p>Associates tracking ID <code>{esc(TRACKING_ID)}</code>: format checked, account not yet confirmed
      (<a href="{root}flagged-for-review/">FLG-001</a>).</p>
    </section>
  </div>
</footer>"""


def head(p: dict) -> str:
    url = BASE + ("" if p["path"] == "index.html" else p["path"].replace("index.html", ""))
    jsonld = ""
    if p.get("jsonld"):
        payload = json.dumps(p["jsonld"], ensure_ascii=False).replace("</", "<\\/")
        jsonld = f'<script type="application/ld+json">{payload}</script>'
    canonical = "" if p.get("noindex") else f'<link rel="canonical" href="{esc(url)}">'
    robots = '<meta name="robots" content="noindex">' if p.get("noindex") else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(p["title"])} · {esc(SITE_NAME)}</title>
<meta name="description" content="{esc(p["description"])}">
{robots}
{canonical}
<meta property="og:site_name" content="{esc(SITE_NAME)}">
<meta property="og:type" content="{'article' if p.get('og_type') == 'article' else 'website'}">
<meta property="og:title" content="{esc(p["title"])}">
<meta property="og:description" content="{esc(p["description"])}">
<meta property="og:url" content="{esc(url)}">
<meta name="affil3-endpoint" content="{esc(ENDPOINT)}">
<link rel="stylesheet" href="{'../' * p['path'].count('/')}assets/css/site.css">
<link rel="alternate" type="application/rss+xml" title="{esc(SITE_NAME)} guides" href="{'../' * p['path'].count('/')}feed.xml">
{jsonld}
</head>
"""


def render(p: dict) -> str:
    root = "../" * p["path"].count("/")
    body = masthead(root, p.get("active", "")) + f'\n<main id="main" class="wrap">\n{p["body"]}\n</main>\n' + footer(root)
    return (head(p) + f"<body class=\"{esc(p.get('body_class', 'page'))}\">\n" + body +
            f'\n<script src="{root}assets/js/measure.js" defer></script>\n</body>\n</html>\n')


# ---------------------------------------------------------------- components

def product_card(p: dict) -> str:
    cat = CATS.get(p["category"], {}).get("name", "")
    verified = p["status"] == "destination_confirmed"
    terms = listing_terms(p)
    pills = "".join(f'<li>{esc(t)}</li>' for t in terms)
    pills_html = f'<ul class="pills" aria-label="Named in the listing">{pills}</ul>' if pills else ""
    cta = "View on Amazon &#8599;" if verified else "Open submitted link &#8599;"
    asin = p["intended_asin"] or "Not confirmed"
    form = p["form"] or "Not confirmed"
    checked = fdate(p["confirmation_date"]) if p["confirmation_date"] else "Not confirmed"
    return f"""<article class="pcard{'' if verified else ' pcard--open'}" data-product="{esc(p['id'])}">
  <p class="kicker">{esc(cat)} <span class="pid">{esc(p['id'])}</span></p>
  <h3>{esc(p['display_name'])}</h3>
  {pills_html}
  <dl class="facts">
    <div><dt>ASIN</dt><dd>{esc(asin)}</dd></div>
    <div><dt>Form</dt><dd>{esc(form)}</dd></div>
    <div><dt>Checked</dt><dd>{esc(checked)}</dd></div>
  </dl>
  <div class="pcard-foot">{product_status_badge(p)}
    <a class="btn" href="{esc(p['submitted_url'])}" rel="sponsored noopener" target="_blank" data-product="{esc(p['id'])}">{cta}</a>
  </div>
  <p class="fine">Sponsored link. Prices and star ratings are not shown.</p>
</article>"""


def guide_card(g: dict, root: str) -> str:
    cl = CLUSTERS[g["cluster"]]["name"]
    return f"""<article class="gcard">
  <p class="kicker">{esc(cl)} <span class="pid">{esc(g['status'])}</span></p>
  <h3><a href="{root}guides/{esc(g['slug'])}/">{esc(g['title'])}</a></h3>
  <p>{esc(g['description'])}</p>
  <p class="meta">{fdate(g['published'])} &middot; {g['read_minutes']} min read</p>
</article>"""


def simple_table(headers: list[str], rows: list[list[str]], cls: str = "") -> str:
    th = "".join(f"<th scope=\"col\">{esc(h)}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return (f'<div class="table-wrap"><table class="{cls}"><thead><tr>{th}</tr></thead>'
            f"<tbody>{body}</tbody></table></div>")


def page_header(kicker: str, title: str, dek: str = "") -> str:
    d = f'<p class="dek-lead">{esc(dek)}</p>' if dek else ""
    return f'<section class="page-head"><p class="kicker">{esc(kicker)}</p><h1>{esc(title)}</h1>{d}</section>'


# ---------------------------------------------------------------- pages

def page_home(guides):
    verified = [p for p in PRODUCTS if p["status"] == "destination_confirmed"]
    n_total = len(PRODUCTS)
    n_ok = len(verified)
    cards = "".join(product_card(p) for p in PRODUCTS)
    gcards = "".join(guide_card(g, "") for g in guides)
    tiles = "".join(
        f"""<a class="tile" href="categories/{esc(c['id'])}/"><p class="kicker">{esc(c['kicker'])}</p>
        <h3>{esc(c['name'])}</h3><p>{esc(c['blurb'])}</p>
        <p class="meta">{sum(1 for p in PRODUCTS if p['category'] == c['id'])} listing(s)</p></a>"""
        for c in SITE["categories"])
    body = f"""
<section class="hero">
  <p class="kicker">The listings first</p>
  <h1>{n_total} submitted listings. Each link opened and checked.</h1>
  <p class="lead">{n_ok} of {n_total} links open to an Amazon listing that we could read and record. One is still unconfirmed and is marked as such. Start with a card, then read the guide that fits it.</p>
</section>
<section class="block">
  <div class="section-head"><h2>The listings</h2><a href="products/">Full register &rarr;</a></div>
  <div class="pgrid">{cards}</div>
</section>
<section class="block">
  <div class="section-head"><h2>Start with a question</h2><a href="guides/">All guides &rarr;</a></div>
  <div class="ggrid">{gcards}</div>
</section>
<section class="block">
  <div class="section-head"><h2>Browse by category</h2><a href="categories/">All categories &rarr;</a></div>
  <div class="tiles">{tiles}</div>
</section>
<section class="block how">
  <h2>How each row is checked</h2>
  <ol>
    <li>Open the submitted link and note where it ends up.</li>
    <li>Read the listing title, the category path and the ASIN in the address.</li>
    <li>Record the destination in its own field. It is never merged with the ASIN.</li>
    <li>Leave any value blank if it cannot be read on an official page, and flag it.</li>
  </ol>
  <p class="small">See the <a href="sources/">source register</a>, the <a href="findings/">findings</a> and the <a href="flagged-for-review/">items flagged for review</a>.</p>
</section>"""
    return {
        "path": "index.html", "title": "Buyer questions for the kitchen counter",
        "description": SITE["tagline"], "active": "", "body": body, "body_class": "home",
        "jsonld": {"@context": "https://schema.org", "@type": "WebSite", "name": SITE_NAME,
                   "url": BASE, "description": SITE["tagline"]},
    }


def page_products():
    headers = ["ID", "Product (display)", "Listing title (as read)", "Category", "ASIN (from listing)",
               "Official listing URL", "Confirmed", "Source", "Observed redirect target (separate field)",
               "Associates tag in observed target", "Submitted link", "Status"]
    rows = []
    for p in PRODUCTS:
        cat = CATS.get(p["category"], {}).get("name", "")
        listing = esc(p["listing_title"]) if p["listing_title"] else "<span class=\"blank\">Not confirmed</span>"
        asin = esc(p["intended_asin"]) if p["intended_asin"] else "<span class=\"blank\">Not confirmed</span>"
        official = ext_link(p["official_listing_url"], p["official_listing_url"]) if p["official_listing_url"] \
            else "<span class=\"blank\">Not confirmed</span>"
        conf = esc(fdate(p["confirmation_date"])) if p["confirmation_date"] else "<span class=\"blank\">Not confirmed</span>"
        source = ext_link(p["source_url"], "Source " + "\u2197") if p["source_url"] else "<span class=\"blank\">None</span>"
        redirect = f"<code class=\"wrapcode\">{esc(p['observed_redirect_target'])}</code>" if p["observed_redirect_target"] else "<span class=\"blank\">None</span>"
        tag = p["tag_in_observed_target"]
        tagc = "Not observed" if tag is False else ("Not applicable" if tag is None else "Observed")
        tagc_html = badge("Not observed (flag)" if tag is False else "Not applicable", "flag" if tag is False else "muted")
        rows.append([esc(p["id"]), esc(p["display_name"]), listing, esc(cat), asin, official, conf, source,
                     redirect, tagc_html, ext_link(p["submitted_url"], p["submitted_url"]),
                     product_status_badge(p)])
    basis = "".join(
        f"<li><strong>{esc(p['id'])}</strong> ASIN basis: {esc(p['intended_asin_basis'])} "
        f"Tag note: {esc(p['tag_note'])}</li>" for p in PRODUCTS)
    body = page_header("Dashboard · Product register",
                       "Product register: one row per submitted link",
                       "Confirmed fields come from the official Amazon page each link opened on 20 Nov 2026. Blank means not confirmed. Prices and star ratings are not recorded.") + f"""
<section class="block">
  {simple_table(headers, rows, "register")}
  <p class="small">Source column: each row links to the official page it was read from (sponsored where it is an Amazon link).
  The submitted short link is kept as submitted. No value was inferred. Full rules: <a href="{'{root}'}about/">About</a>.</p>
</section>
<section class="block">
  <h2>Notes per row</h2>
  <ul class="notes">{basis}</ul>
  <p class="small">Not recorded by design: prices, availability, star ratings and review counts (Participation Requirements 2(b), 6(t)). See <a href="../findings/">F-07</a>.</p>
</section>"""
    body = body.replace("{root}", "../")
    return {"path": "products/index.html", "title": "Product register",
            "description": "One row per submitted Amazon link: ASIN, listing URL, confirmation date, source and observed redirect target, each in its own field.",
            "active": "products/", "body": body}


def page_categories():
    tiles = []
    for c in SITE["categories"]:
        items = [p for p in PRODUCTS if p["category"] == c["id"]]
        conf = sum(1 for p in items if p["status"] == "destination_confirmed")
        tiles.append(f"""<a class="tile" href="{esc(c['id'])}/"><p class="kicker">{esc(c['kicker'])}</p>
        <h3>{esc(c['name'])}</h3><p>{esc(c['blurb'])}</p>
        <p class="meta">{len(items)} listing(s) &middot; {conf} confirmed</p></a>""")
    body = page_header("Categories", "Browse by category",
                       "Each category page has its own cards and its own register table.") + \
        f'<section class="block"><div class="tiles">{"".join(tiles)}</div></section>'
    return {"path": "categories/index.html", "title": "Categories",
            "description": "Browse the product categories: air fryers and ovens, kitchen thermometers, and items awaiting verification.",
            "active": "categories/", "body": body}


def page_category(c: dict):
    items = [p for p in PRODUCTS if p["category"] == c["id"]]
    cards = "".join(product_card(p) for p in items) or "<p>No listings yet.</p>"
    headers = ["ID", "Product", "ASIN", "Status", "Source"]
    rows = []
    for p in items:
        rows.append([esc(p["id"]), esc(p["display_name"]),
                     esc(p["intended_asin"]) if p["intended_asin"] else "<span class=\"blank\">Not confirmed</span>",
                     product_status_badge(p), ext_link(p["source_url"], "Source \u2197")])
    body = page_header(f"Category · {len(items)} listing(s)", c["name"], c["blurb"]) + f"""
<section class="block"><div class="pgrid">{cards}</div></section>
<section class="block"><h2>Entries in this category</h2>{simple_table(headers, rows)}</section>
<section class="block"><p class="small">Guides for this category: {"; ".join(f'<a href="../../guides/{esc(g["slug"])}/">{esc(g["title"])}</a>' for g in GUIDES if g["cluster"] == CLUSTER_FOR_CAT.get(c["id"], "")) or "none yet"}.</p></section>"""
    return {"path": f"categories/{c['id']}/index.html", "title": c["name"],
            "description": c["blurb"], "active": "categories/", "body": body}


def page_guides(guides):
    sections = []
    for cl in SITE["clusters"]:
        items = [g for g in guides if g["cluster"] == cl["id"]]
        if not items:
            continue
        cards = "".join(guide_card(g, "../") for g in items)
        sections.append(f'<section class="block"><div class="section-head"><h2>{esc(cl["name"])}</h2></div>'
                        f'<p class="small">{esc(cl["blurb"])}</p><div class="ggrid">{cards}</div></section>')
    cad = SITE["cadence"]
    body = page_header("Guides · question-shaped", "Buyer guides, one question at a time",
                       "Each guide starts with a question a buyer should answer first. None of them reports hands-on testing.") + \
        "".join(sections) + f"""
<section class="block cadence">
  <h2>Publishing cadence</h2>
  <p>One new guide every {cad['period_days']} days. Last published {fdate(cad['last_published'])}. Next planned {fdate(cad['next_planned'])}.</p>
  <p class="small">{esc(cad['status'])} The rule and option list are in <a href="../suggestions/">Suggestions</a> (SUG-03).</p>
  <p class="small"><strong>Season:</strong> late-autumn and holiday cooking. We have no search or sales data yet to say what is in demand (Q-09). Topics are not chosen by season alone.</p>
</section>"""
    return {"path": "guides/index.html", "title": "Guides",
            "description": "Question-shaped buyer guides for air fryers, multi-function appliances and wireless meat thermometers.",
            "active": "guides/", "body": body}


def page_guide(g: dict):
    path = f"guides/{g['slug']}/index.html"
    root = "../../"
    md_html = md_to_html(g["body"], path)
    cl = CLUSTERS[g["cluster"]]["name"]
    srcs = "".join(f"<li>{ext_link(SMAP[s]['url'], s + ' · ' + SMAP[s]['title'])}</li>"
                   for s in [x.strip() for x in g["sources"].split(",")])
    related = "".join(f'<li><a href="{root}guides/{esc(o["slug"])}/">{esc(o["title"])}</a></li>'
                      for o in GUIDES if o["slug"] != g["slug"])
    working = ("Working title. An editorial hypothesis, not a claim about popularity, search volume or product quality."
               if g["status"] == "Working title" else
               "Proposed working title. Chosen by the editorial team; awaiting owner review (SUG-09).")
    body = f"""<article class="article">
  <header class="article-head">
    <p class="kicker">{esc(cl)} <span class="pid">{esc(g['status'])}</span></p>
    <h1>{esc(g['title'])}</h1>
    <p class="dek-lead">{esc(g['description'])}</p>
    <p class="byline">By the Editorial team &middot; Published {fdate(g['published'])} &middot; {g['read_minutes']} min read</p>
    <p class="note-box">{esc(working)} We have not tested these products. Everything quoted comes from listing text or public guidance.</p>
  </header>
  <div class="prose">{md_html}</div>
</article>
<section class="block">
  <h2>Sources for this guide</h2>
  <ul class="notes">{srcs}</ul>
</section>
<section class="block">
  <h2>More guides</h2>
  <ul class="notes">{related}</ul>
</section>"""
    jsonld = {"@context": "https://schema.org", "@type": "Article", "headline": g["title"],
              "description": g["description"], "datePublished": g["published"], "dateModified": g["published"],
              "author": {"@type": "Organization", "name": "Countertop Journal editorial team"},
              "publisher": {"@type": "Organization", "name": SITE_NAME},
              "mainEntityOfPage": BASE + f"guides/{g['slug']}/"}
    return {"path": path, "title": g["title"], "description": g["description"], "active": "guides/",
            "body": body, "og_type": "article", "jsonld": jsonld, "body_class": "guide-page"}


def page_sources():
    rows = []
    for s in SOURCES:
        result = s["result"]
        rows.append([esc(s["id"]), esc(s["title"]), esc(s["publisher"]),
                     ext_link(s["url"], s["url"]), esc(s["used_for"]), esc(fdate(s["checked"])),
                     badge(result.split(".")[0] if result else "", "warn" if result.lower().startswith("not retrieved") else "ok")
                     + f'<p class="small">{esc(result)}</p>'])
    body = page_header("Dashboard · Sources", "Source register",
                       "Every row links to the page it was read from. 'Not retrieved' rows never support a value.") + \
        f'<section class="block">{simple_table(["ID", "Source", "Publisher", "Link", "Used for", "Checked", "Result"], rows, "wide")}</section>'
    return {"path": "sources/index.html", "title": "Source register", "active": "",
            "description": "Official and primary sources used to check each value, with the date read and the result.", "body": body}


def linkify_text(s: str) -> str:
    return src_ids_linked(s)


def page_findings():
    rows = []
    for f in FINDINGS:
        rows.append([esc(f["id"]), esc(f["finding"]), esc(f["evidence"]), linkify_text(f["source"]),
                     badge(f["status"]), esc(f["implication"])])
    body = page_header("Dashboard · Findings", "Findings and analysis",
                       "What the record shows, what it does not, and what follows. Each finding names its source.") + \
        f'<section class="block">{simple_table(["ID", "Finding", "Evidence", "Source", "Status", "Implication"], rows, "wide")}</section>'
    return {"path": "findings/index.html", "title": "Findings", "active": "",
            "description": "Findings from the repository and listing review, with the evidence and the source for each.", "body": body}


def page_questions():
    rows = []
    for q in QUESTIONS:
        rows.append([esc(q["id"]), esc(q["question"]), linkify_text(q["known"]), esc(q["missing"]),
                     esc(q["how"]), esc(q["blocks"])])
    body = page_header("Dashboard · Questions", "Questions before any decision",
                       "What we know, what is missing, how to find it out, and which decision it blocks.") + \
        f'<section class="block">{simple_table(["ID", "Question", "What we know", "What is missing", "How to find out", "Blocks"], rows, "wide")}</section>'
    return {"path": "questions/index.html", "title": "Questions", "active": "",
            "description": "Open questions, the information still missing, and how to find it out before a decision.", "body": body}


def page_suggestions():
    rows = []
    for s in SUGGESTIONS:
        opts = "".join(f"<li><strong>{esc(k)}.</strong> {esc(v)}</li>" for k, v in s["options"].items())
        rows.append([esc(s["id"]), esc(s["area"]), esc(s["suggestion"]), f'<ul class="opts">{opts}</ul>',
                     esc(s["recommended"]), esc(s["effort"]), esc(s["risk"]), badge(s["status"], "decide"),
                     linkify_text(s["source"])])
    body = page_header("Dashboard · Suggestions", "Suggestions: choose before anything changes",
                       "Nothing here is implemented until you choose an option. Reply with the ID and letter, for example 'SUG-01: A'.") + f"""
<section class="block">{simple_table(["ID", "Area", "Suggestion", "Options", "Recommended (default, not decided)", "Effort", "Risk", "Status", "Source"], rows, "wide")}</section>"""
    return {"path": "suggestions/index.html", "title": "Suggestions", "active": "",
            "description": "Suggestions for review with options and a recommended default. Nothing changes until the owner chooses.", "body": body}


def page_flags():
    rows = []
    for f in FLAGS:
        rows.append([esc(f["id"]), esc(f["item"]), esc(f["why"]), linkify_text(", ".join(f["sources"])),
                     badge(f["status"], "warn"), badge("No: published for review", "muted")])
    body = page_header("Flagged for Review", "Flagged for Review",
                       "Irregularities and unverified items. They are published here with source links so you can review them after the site is live. They do not block the merge.") + \
        f'<section class="block">{simple_table(["ID", "Item", "Why flagged", "Sources", "Status", "Blocks merge?"], rows, "wide")}</section>'
    return {"path": "flagged-for-review/index.html", "title": "Flagged for Review", "active": "",
            "description": "Items flagged for review, with reasons and source links. These do not block publication.", "body": body}


def page_ledger():
    with open(DATA / "campaign_ledger.csv", encoding="utf-8") as fh:
        reader = csv.reader(fh)
        header = next(reader)
        data_rows = [r for r in reader if any(c.strip() for c in r)]
    if data_rows:
        raise BuildError("campaign ledger has rows; they must come from first-party reports with provenance")
    defs = [
        ("timestamp_utc", "When the figures were pulled (UTC).", "Required."),
        ("source_report", "Name of the first-party report, e.g. the Associates tracking report.", "Required."),
        ("channel", "Where the traffic came from.", "Required."),
        ("eligible_sessions", "Sessions the report counts as eligible.", "Copied from the report only."),
        ("clicks", "Clicks as the report states them.", "Copied from the report only."),
        ("reported_orders", "Orders as the report states them.", "Copied from the report only."),
        ("provenance_url", "Link to the report or export.", "Required. No row without it."),
        ("notes", "Anything the report says about the figures.", "Optional."),
    ]
    def_rows = [[esc(a), esc(b), esc(c)] for a, b, c in defs]
    ev_rows = []
    for e in EVENTS["events"]:
        ev_rows.append([f"<code>{esc(e['name'])}</code>", esc(e["fires"]), esc(e["payload"]),
                        badge("Not receiving: no endpoint configured" if not ENDPOINT else "Configured", "flag" if not ENDPOINT else "ok")])
    privacy = "".join(f"<li>{esc(r)}</li>" for r in EVENTS["privacy_rules"])
    body = page_header("Dashboard · Ledger &amp; analytics", "Campaign ledger and measurement",
                       "The ledger is empty on purpose. No click, conversion or revenue figure is shown until a first-party report exists.") + f"""
<section class="block">
  <h2>Campaign ledger <span class="pid">0 rows</span></h2>
  {simple_table(header, [], "wide")}
  <p class="small">Source file: <code>data/campaign_ledger.csv</code>. Rows are added only from authorized first-party reports, with a dated provenance link.</p>
  {simple_table(["Column", "Meaning", "Rule"], def_rows)}
</section>
<section class="block">
  <h2>Five defined events</h2>
  <p class="small">Names carried over from the prior measurement plan. Definitions to be confirmed (FLG-012).</p>
  {simple_table(["Event", "Fires when", "Payload", "Status"], ev_rows, "wide")}
  <p class="small">Setup: the receiver in <code>analytics/collect_server.py</code> is tested locally. It is not hosted, and GitHub Pages cannot run it (FLG-004, SUG-02).</p>
</section>
<section class="block"><h2>Privacy rules for measurement</h2><ul class="notes">{privacy}</ul></section>"""
    return {"path": "ledger/index.html", "title": "Ledger and analytics", "active": "",
            "description": "Empty campaign ledger with defined columns, five measurement events, and their current status.", "body": body}


def page_md(name: str, path: str, active: str = ""):
    meta, body = load_md_page(name)
    html_body = md_to_html(body, path)
    kicker = {"about": "About", "disclosure": "Disclosure", "privacy": "Privacy",
              "executive-summary": "Dashboard · Executive summary"}.get(name, "")
    body_html = f'<article class="article"><header class="article-head"><p class="kicker">{esc(kicker)}</p>' \
                f'<h1>{esc(meta["title"])}</h1><p class="dek-lead">{esc(meta["description"])}</p></header>' \
                f'<div class="prose">{html_body}</div></article>'
    return {"path": path, "title": meta["title"], "description": meta["description"],
            "active": active, "body": body_html}


def page_404():
    body = f"""<section class="page-head"><p class="kicker">Not found</p><h1>This page is not here.</h1>
<p class="dek-lead">The link may be old. Try one of these:</p></section>
<section class="block"><ul class="notes">
<li><a href="{BASE}">Home</a></li><li><a href="{BASE}products/">Product register</a></li>
<li><a href="{BASE}guides/">Guides</a></li><li><a href="{BASE}disclosure/">Disclosure</a></li>
<li><a href="{BASE}flagged-for-review/">Flagged for Review</a></li></ul></section>"""
    return {"path": "404.html", "title": "Page not found", "description": "This page does not exist.",
            "active": "", "body": body, "noindex": True}


# ---------------------------------------------------------------- feeds

GUIDES: list[dict] = []
CLUSTER_FOR_CAT = {"air-fryers": "air-fryers", "thermometers": "thermometers"}


def build_feed():
    items = []
    for g in sorted(GUIDES, key=lambda g: g["published"], reverse=True):
        link = f"{BASE}guides/{g['slug']}/"
        items.append(f"""  <item>
    <title>{esc(g['title'])}</title>
    <link>{esc(link)}</link>
    <guid isPermaLink="true">{esc(link)}</guid>
    <pubDate>{rfc822(g['published'])}</pubDate>
    <description>{esc(g['description'])}</description>
  </item>""")
    last = rfc822(BUILD_DATE)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
  <title>{esc(SITE_NAME)}: buyer guides</title>
  <link>{esc(BASE)}</link>
  <description>{esc(SITE['tagline'])}</description>
  <language>en-us</language>
  <lastBuildDate>{last}</lastBuildDate>
  <docs>https://www.rssboard.org/rss-specification</docs>
  <generator>tools/build_site.py</generator>
{chr(10).join(items)}
</channel>
</rss>
"""


def build_sitemap(paths: list[str]):
    urls = []
    for p in paths:
        loc = BASE + ("" if p == "index.html" else p.replace("index.html", ""))
        urls.append(f"  <url>\n    <loc>{esc(loc)}</loc>\n    <lastmod>{BUILD_DATE}</lastmod>\n  </url>")
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + "\n".join(urls) + "\n</urlset>\n")


# ---------------------------------------------------------------- redirects
# URLs published by the prior session (db77ec4). Each gets a small redirect stub so existing links keep working.
LEGACY_REDIRECTS = {
    "index.html": "",
    "products.html": "products/",
    "about.html": "about/",
    "disclosure.html": "disclosure/",
    "privacy.html": "privacy/",
    "flagged.html": "flagged-for-review/",
    "guides/air-fryer-basket-oven.html": "guides/basket-or-oven-style-air-fryer/",
    "guides/air-fryer-capacity-checklist.html": "guides/air-fryer-capacity-checklist/",
    "guides/air-fryer-cleanup-counter-space.html": "guides/cleanup-and-counter-space-tradeoffs/",
    "guides/multi-function-appliance-questions.html": "guides/multi-function-kitchen-appliance-questions/",
}


def redirect_stub(target_rel: str) -> str:
    target = BASE + target_rel
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>Moved · {esc(SITE_NAME)}</title>
<meta name="robots" content="noindex">
<link rel="canonical" href="{esc(target)}">
<meta http-equiv="refresh" content="0; url={esc(target)}">
</head><body><p>This page has moved to <a href="{esc(target)}">{esc(target)}</a>.</p></body></html>
"""


# ---------------------------------------------------------------- main

def main() -> int:
    global GUIDES
    GUIDES = load_guides()
    if OUT.exists():
        for child in OUT.iterdir():
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
    OUT.mkdir(parents=True)

    pages: list[dict] = [
        page_home(GUIDES),
        page_products(),
        page_categories(),
        *[page_category(c) for c in SITE["categories"]],
        page_guides(GUIDES),
        *[page_guide(g) for g in GUIDES],
        page_sources(),
        page_findings(),
        page_questions(),
        page_suggestions(),
        page_flags(),
        page_ledger(),
        page_md("executive-summary", "executive-summary/index.html", "executive-summary/"),
        page_md("disclosure", "disclosure/index.html", "disclosure/"),
        page_md("privacy", "privacy/index.html", "privacy/"),
        page_md("about", "about/index.html", "about/"),
    ]
    indexable = [p for p in pages]
    for p in pages:
        target = OUT / p["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render(p), encoding="utf-8")
    not_found = page_404()
    (OUT / "404.html").write_text(render(not_found), encoding="utf-8")

    (OUT / "feed.xml").write_text(build_feed(), encoding="utf-8")
    (OUT / "sitemap.xml").write_text(build_sitemap([p["path"] for p in indexable]), encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {BASE}sitemap.xml\n", encoding="utf-8")
    for legacy, target_rel in LEGACY_REDIRECTS.items():
        stub = OUT / legacy
        stub.parent.mkdir(parents=True, exist_ok=True)
        stub.write_text(redirect_stub(target_rel), encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")

    shutil.copytree(ASSETS, OUT / "assets")
    print(f"built {len(indexable)} pages + 404 into {OUT.relative_to(ROOT)}/")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BuildError as exc:
        print(f"BUILD FAILED: {exc}", file=sys.stderr)
        sys.exit(1)
