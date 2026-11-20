#!/usr/bin/env python3
"""Build the Affil3 static site (GitHub Pages source: /docs) from /data.

Only the JSON/CSV files in data/ are treated as content. Every page is generated;
hand-editing docs/*.html will be overwritten on the next build.

Usage:  python3 scripts/build_site.py && python3 scripts/check_site.py
Standard library only.
"""
import csv
import datetime as dt
import email.utils
import html
import json
import pathlib
from urllib.parse import urlparse

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "docs"
SITE_BASE = "https://karagemop466-tech.github.io/Affil3/"
REPO_URL = "https://github.com/karagemop466-tech/Affil3"
COORD_URL = REPO_URL + "/blob/main/COORDINATION.md"
STATEMENT = "As an Amazon Associate I earn from qualifying purchases."
BRAND = "Affil3"
UPDATED = "2026-11-20"
PRODUCT_HOSTS = {"amazon.com", "www.amazon.com", "link.amazon"}

def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))

SOURCES = {s["id"]: s for s in load("sources.json")["sources"]}
PRODUCTS = load("products.json")["products"]
FLAGS = load("flags.json")["flags"]
QUESTIONS = load("questions.json")["questions"]
SUGGESTIONS = load("suggestions.json")["suggestions"]
ANALYSIS = load("analysis.json")["findings"]
GUIDES = load("guides.json")["guides"]
GUIDES_META = load("guides.json")
MEASURE = load("measurement.json")
LEDGER_HEADER = next(csv.reader((DATA / "campaign_ledger.csv").read_text(encoding="utf-8").splitlines()))

CATEGORIES = [
    ("air-fryers", "Air fryers", "air-fryers.html"),
    ("meat-thermometers", "Meat thermometers", "meat-thermometers.html"),
    ("uncategorized", "Uncategorized — pending verification", "uncategorized.html"),
]
CAT_TITLE = {slug: name for slug, name, _ in CATEGORIES}
PRODUCT_BY_ID = {p["id"]: p for p in PRODUCTS}

def esc(s):
    return html.escape(str(s or ""), quote=True)

def ext_link(url, text=None, cls=None):
    """Link helper. Any link to an Amazon host is marked sponsored (rel) per SRC-05."""
    host = urlparse(url).netloc.lower()
    if host in PRODUCT_HOSTS:
        rel = "sponsored noopener noreferrer"
    else:
        rel = "external noopener noreferrer"
    c = f' class="{cls}"' if cls else ""
    return f'<a href="{esc(url)}" rel="{rel}" target="_blank"{c}>{esc(text or url)}</a>'

def src_link(sid):
    s = SOURCES[sid]
    if s["tier"] == "user-supplied":
        return f'<span class="tag tag-neutral">{esc(sid)} · owner brief</span>'
    return ext_link(s["url"], f'{sid} · {s["publisher"]}')

def has_official(ids):
    return any(SOURCES[i]["tier"] != "user-supplied" for i in ids)

def src_links(ids):
    return "<br>".join(src_link(i) for i in ids) if ids else '<span class="tag tag-amber">Brief only — no official source</span>'

def badge(kind, text):
    return f'<span class="tag tag-{kind}">{esc(text)}</span>'

def match_badge(m):
    if m == "MISMATCH":
        return badge("bad", "ASIN mismatch")
    if m == "UNRESOLVED":
        return badge("amber", "Unresolved")
    if m == "MATCH":
        return badge("ok", "Match")
    return badge("neutral", m)

FORMAT_BADGE = badge("bad", "Fails 10-char format")

def tag_badge():
    return badge("neutral", "Tag not seen in target")

SPONSORED = '<span class="tag tag-sponsored">Sponsored · affiliate link</span>'

NAV = [
    ("Shop", "index.html"),
    ("Categories", "categories.html"),
    ("Guides", "guides/index.html"),
    ("Dashboard", "dashboard.html"),
    ("Review", "review.html"),
    ("About", "about.html"),
]

FOOTER_SURFACES = [
    ("Shop (front page)", "index.html"),
    ("Air fryers", "air-fryers.html"),
    ("Meat thermometers", "meat-thermometers.html"),
    ("Uncategorized", "uncategorized.html"),
    ("Guides", "guides/index.html"),
    ("Product records", "products.html"),
    ("Analysis & findings", "analysis.html"),
    ("Sources", "sources.html"),
    ("Measurement", "measurement.html"),
    ("Compliance", "compliance.html"),
    ("Executive summary", "executive-summary.html"),
    ("Questions to resolve", "questions.html"),
    ("Suggestions (choose a path)", "suggestions.html"),
    ("Flagged for Review", "flagged.html"),
    ("About", "about.html"),
    ("Feed (RSS)", "feed.xml"),
    ("Sitemap", "sitemap.xml"),
]

def page(path, title, body, desc, current, root):
    """Render one page. `path` is relative to docs/, `root` is '../' for nested pages."""
    nav_items = []
    for label, href in NAV:
        cur = ' aria-current="page"' if href == current else ""
        nav_items.append(f'<li><a href="{root}{href}"{cur}>{esc(label)}</a></li>')
    footer_items = "".join(f'<li><a href="{root}{h}">{esc(l)}</a></li>' for l, h in FOOTER_SURFACES)
    html_out = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} · {BRAND}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{SITE_BASE}{esc(path)}">
<link rel="stylesheet" href="{root}assets/style.css">
<link rel="alternate" type="application/rss+xml" title="{BRAND} guides" href="{root}feed.xml">
<script src="{root}assets/analytics.js" defer></script>
</head>
<body>
<header class="masthead">
  <div class="wrap">
    <a class="wordmark" href="{root}index.html">{BRAND}</a>
    <div class="dateline">Kitchen small appliances · Last updated {UPDATED}</div>
  </div>
  <div class="wrap nav">
    <ul>{''.join(nav_items)}</ul>
  </div>
</header>
<div class="disclosure" role="note" aria-label="Affiliate disclosure">
  <div class="wrap"><strong>Disclosure:</strong> {STATEMENT} Links marked “Sponsored” are Amazon Associates affiliate links. We may earn a commission from qualifying purchases. <a href="{root}compliance.html">How we handle links</a></div>
</div>
<main>
  <div class="wrap">
{body}
  </div>
</main>
<footer class="site-footer">
  <div class="wrap">
    <div class="disc"><strong>Disclosure:</strong> {STATEMENT} Links marked “Sponsored” are affiliate links, and we may earn a commission from qualifying purchases. Listing titles and categories are copied from Amazon pages observed on {UPDATED}; prices are not shown because they were not verified.</div>
    <h4>All pages</h4>
    <ul>{footer_items}</ul>
    <div class="legal">
      <p>Every value on this site is either linked to an official source or marked unverified. Source register: <a href="{root}sources.html">sources.html</a>. Project log: <a href="{COORD_URL}" target="_blank" rel="external noopener noreferrer">COORDINATION.md</a> · <a href="{REPO_URL}" target="_blank" rel="external noopener noreferrer">repository</a>.</p>
      <p>© {BRAND}. Not affiliated with, endorsed by, or sponsored by Amazon.com, Inc. or its affiliates. “Amazon” and product names are used only to identify listings.</p>
    </div>
  </div>
</footer>
</body>
</html>
"""
    target = OUT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html_out, encoding="utf-8")
    return path

def table(headers, rows, unverified=None, cls="data needs-source"):
    unverified = unverified or set()
    th = "".join(f"<th>{esc(h)}</th>" for h in headers)
    trs = []
    for i, r in enumerate(rows):
        c = ' class="unverified"' if i in unverified else ""
        trs.append(f"<tr{c}>" + "".join(f"<td>{x}</td>" for x in r) + "</tr>")
    return (f'<div class="table-wrap"><table class="{cls}"><thead><tr>{th}</tr></thead>'
            f"<tbody>{''.join(trs)}</tbody></table></div>")

def product_listing_title(p):
    return p.get("observed_title") or "Not reached"

def short_title(p):
    """Card display only: drop the 'Amazon.com: ' prefix and ' : Home & Kitchen' suffix.
    The verbatim title is kept on the product records page."""
    t = product_listing_title(p)
    if t.startswith("Amazon.com: "):
        t = t[len("Amazon.com: "):]
    if t.endswith(" : Home & Kitchen"):
        t = t[: -len(" : Home & Kitchen")]
    return t

# ---------- product cards and category tables ----------

def product_card(p):
    if p["asin_match"] == "UNRESOLVED":
        title = "Listing not verified"
        body_btn = '<span class="btn disabled" aria-disabled="true">Link not verified yet</span>'
        note = '<p class="card source">The link ended at an Amazon interstitial page. No product was reached.</p>'
    else:
        title = short_title(p)
        body_btn = (f'<a class="btn" href="{esc(p["submitted_url"])}" rel="sponsored noopener noreferrer" '
                    f'target="_blank" data-product="{esc(p["id"])}">View listing</a>')
        note = (f'<p class="source">Observed ASIN <code>{esc(p["observed_asin"])}</code> · '
                f'intended <code>{esc(p["intended_asin"])}</code></p>')
    return f"""<article class="card">
  <div>{SPONSORED}</div>
  <p class="title">{esc(title)}</p>
  {note}
  <div class="callout-row">{FORMAT_BADGE}{match_badge(p["asin_match"])}</div>
  <div class="foot">
    <span class="price">Price: not verified</span>
    {body_btn}
    <span class="source">Category: {esc(CAT_TITLE.get(p["category_slug"], ""))}</span>
  </div>
</article>"""

def category_table(slug):
    rows, flagged = [], set()
    for i, p in enumerate([x for x in PRODUCTS if x["category_slug"] == slug]):
        rows.append([
            f'<strong>{esc(p["id"])}</strong>',
            esc(product_listing_title(p)),
            f'<code>{esc(p["intended_asin"])}</code>',
            f'<code>{esc(p["observed_asin"]) or "—"}</code>',
            match_badge(p["asin_match"]),
            esc(p.get("observed_category") or "—"),
            '<span class="tag tag-amber">UNVERIFIED</span>',
            ext_link(SOURCES[p["source_ids"][0]]["url"], "Amazon listing (observed)") if p["asin_match"] != "UNRESOLVED"
              else ext_link(SOURCES["SRC-10"]["url"], "Amazon interstitial (observed)"),
        ])
        flagged.add(i)
    return table(["ID", "Listing title (as observed)", "Intended ASIN (from link)", "Observed ASIN",
                  "ASIN check", "Category (Amazon breadcrumb)", "Price", "Source (official)"], rows, unverified=flagged)

# ---------- pages ----------

def build_index():
    cards = "".join(product_card(p) for p in PRODUCTS)
    tiles = []
    for slug, name, href in CATEGORIES:
        n = sum(1 for p in PRODUCTS if p["category_slug"] == slug)
        tiles.append(f'<a class="tile" href="{href}"><div class="count">{n}</div><div class="label">{esc(name)}</div></a>')
    guides = "".join(
        f'<a class="tile" href="guides/{esc(g["slug"])}.html"><div class="label">Working title</div>'
        f'<h3>{esc(g["title"])}</h3><div class="label">{esc(g["summary"])}</div></a>' for g in GUIDES)
    body = f"""
    <p class="kicker">Front page · small kitchen appliances</p>
    <h1>Five listings, checked one at a time</h1>
    <p class="lede">Three air fryers and one meat thermometer are in this set so far. Each card below shows the listing as it was observed, with its ASIN check. Prices are not shown, because none could be verified from an official source.</p>
    <div class="note warn"><strong>Read this first.</strong> Four of the five submitted links reach a different Amazon product from the one identified in the link, and one reaches an Amazon interstitial page. The owner-supplied identifiers also fail the 10-character ASIN format. Details are on the <a href="flagged.html">Flagged for Review</a> page.</div>
    <h2>Shop the listings</h2>
    <div class="grid">{cards}</div>
    <h2>Categories</h2>
    <div class="tiles">{''.join(tiles)}</div>
    <h2>Guides <span class="cell-muted" style="font-size:15px;font-weight:400">(working titles — hypotheses, not claims)</span></h2>
    <div class="tiles">{guides}</div>
    <h2>How this site is checked</h2>
    <div class="prose"><ul>
      <li>Every value is linked to an official source, or it is left blank and marked unverified. Source register: <a href="sources.html">sources</a>.</li>
      <li>Links marked Sponsored carry <code>rel="sponsored"</code>. The rule and placement are on <a href="compliance.html">compliance</a>.</li>
      <li>Open items, decisions, and what is still missing: <a href="review.html">review</a>.</li>
    </ul></div>
"""
    return page("index.html", f"{BRAND} — Kitchen small appliances, checked", body,
                "Five Amazon listings under review, with ASIN checks, sources, and open questions.", "index.html", "")

def build_categories():
    rows = []
    for slug, name, href in CATEGORIES:
        n = sum(1 for p in PRODUCTS if p["category_slug"] == slug)
        rows.append([f'<a href="{href}">{esc(name)}</a>', str(n), ext_link(SOURCES["SRC-07"]["url"], "Amazon listing (observed)")])
    body = f"""
    <p class="kicker">Categories</p>
    <h1>Browse by category</h1>
    <p class="lede">Categories come from the Amazon breadcrumb shown on each observed listing. A product without an observed breadcrumb stays uncategorized.</p>
    {table(["Category", "Listings", "Source (official)"], rows)}
"""
    return page("categories.html", "Categories", body, "Browse listings by Amazon category.", "categories.html", "")

def build_category_page(slug, name, href):
    count = sum(1 for p in PRODUCTS if p["category_slug"] == slug)
    extra = ""
    if slug == "uncategorized":
        extra = ('<div class="note warn">This listing has no verified category. The identifier in its link is also unverified (FLG-01, FLG-03).</div>')
    body = f"""
    <p class="kicker">Category · {count} listing(s)</p>
    <h1>{esc(name)}</h1>
    <p class="lede">Each row shows the title as observed on Amazon and the ASIN check. Prices are left blank because they were not verified.</p>
    {extra}
    {category_table(slug)}
    <h2>Read the guides</h2>
    <p class="prose">Related guides: <a href="guides/index.html">all guides</a>.</p>
"""
    return page(href, f"{name}", body, f"{name}: observed Amazon listings with ASIN checks.", href, "")

def build_guides_index():
    items = "".join(
        f'<article class="card"><div>{badge("neutral", "Working title")}</div>'
        f'<p class="title"><a href="{esc(g["slug"])}.html">{esc(g["title"])}</a></p>'
        f'<p class="source">{esc(g["summary"])}</p></article>' for g in GUIDES)
    body = f"""
    <p class="kicker">Guides</p>
    <h1>Questions to answer before you buy</h1>
    <p class="lede">Each guide starts from a buyer question, not a product claim. The titles are working titles from the owner brief. They are hypotheses to test, not evidence that anyone is searching for them.</p>
    <div class="grid">{items}</div>
    <p class="meta">Feed: <a href="../feed.xml">RSS</a> · Publish date {GUIDES_META["publish_date"]} · {esc(GUIDES_META["byline"])}</p>
"""
    return page("guides/index.html", "Guides", body, "Buyer-question guides for small kitchen appliances.", "guides/index.html", "../")

def build_guide(g):
    qs = "".join(f"<li>{esc(q)}</li>" for q in g["questions"])
    checks = "".join(f"<li>{esc(c)}</li>" for c in g["listing_checks"])
    cat_href = next(h for s, _, h in CATEGORIES if s == g["category_slug"])
    related = ", ".join(f'<code>{esc(pid)}</code>' for pid in g["related_products"])
    body = f"""
    <p class="kicker">Guide · working title</p>
    <h1>{esc(g["title"])}</h1>
    <p class="meta">By {esc(GUIDES_META["byline"])} · Published {GUIDES_META["publish_date"]} · {badge("neutral", "Working title — hypothesis")}</p>
    <p class="lede">{esc(g["summary"])}</p>
    <h2>Questions to answer</h2>
    <ul class="prose">{qs}</ul>
    <h2>What to check on a listing</h2>
    <p class="prose">These checks use the listing titles as observed on {UPDATED}. They do not say any product is better than another.</p>
    <ul class="prose">{checks}</ul>
    <h2>Products referenced</h2>
    <p class="prose">{related} — see <a href="../{cat_href}">{esc(CAT_TITLE[g["category_slug"]])}</a>.</p>
    <h2>Sources</h2>
    <ul class="prose">{''.join(f"<li>{src_link(s)}</li>" for s in g["source_ids"])}</ul>
"""
    return page(f"guides/{g['slug']}.html", g["title"], body, g["summary"], "guides/index.html", "../")

def build_dashboard():
    cards = [
        ("Product records", "Intended ASIN, observed redirect target, and match status for each link.", "products.html"),
        ("Analysis & findings", "Counts computed from the records. No scores, forecasts, or popularity claims.", "analysis.html"),
        ("Sources", "Official sources used, with what each one supports.", "sources.html"),
        ("Measurement", "Five events (proposed), privacy design, and the empty campaign ledger.", "measurement.html"),
        ("Compliance", "Associates statement, disclosure placement, sponsored-link rule, and open items.", "compliance.html"),
    ]
    items = "".join(f'<article class="card"><h3><a href="{h}">{esc(t)}</a></h3><p class="source">{esc(d)}</p></article>' for t, d, h in cards)
    body = f"""
    <p class="kicker">Dashboard</p>
    <h1>Data behind the site</h1>
    <p class="lede">Every table here carries a source link. Values that could not be confirmed are left blank and marked unverified.</p>
    <div class="grid">{items}</div>
    <p class="meta">Working log: <a href="{COORD_URL}" target="_blank" rel="external noopener noreferrer">COORDINATION.md</a></p>
"""
    return page("dashboard.html", "Dashboard", body, "Dashboard: product records, analysis, sources, measurement, compliance.", "dashboard.html", "")

def build_products():
    rows, flagged = [], set()
    for i, p in enumerate(PRODUCTS):
        observed_target = p["observed_redirect_target"]
        if p["asin_match"] == "UNRESOLVED":
            target_cell = f'<code>{esc(observed_target)}</code>'
            src = ext_link(SOURCES["SRC-10"]["url"], "Amazon interstitial (observed)")
        else:
            target_cell = ext_link(observed_target, observed_target)
            src = ext_link(SOURCES[p["source_ids"][0]]["url"], "Amazon listing (observed)")
        rows.append([
            f'<strong>{esc(p["id"])}</strong>',
            f'<code>{esc(p["submitted_url"])}</code>',
            f'<code>{esc(p["intended_asin"])}</code><br>{FORMAT_BADGE}',
            f'<span class="tag tag-amber">UNVERIFIED</span><br><span class="cell-muted">{esc(p["official_listing_status"])}</span>',
            target_cell,
            f'<code>{esc(p["observed_asin"]) or "—"}</code>',
            match_badge(p["asin_match"]),
            f'{tag_badge()}',
            esc(p["confirmation_date"]),
            f'<span class="tag tag-amber">UNVERIFIED</span>',
            src,
        ])
        flagged.add(i)
    return table(["ID", "Submitted link (not linked)", "Intended ASIN (from link)", "Official listing URL",
                  "Observed redirect target (separate field)", "Observed ASIN", "ASIN check",
                  "tag= in target?", "Confirmed on", "Price", "Source (official)"], rows, unverified=flagged)

def build_products_page():
    body = f"""
    <p class="kicker">Dashboard · product-intent records</p>
    <h1>Product records</h1>
    <p class="lede">For each submitted link the intended ASIN and the observed redirect target are stored separately, and never merged. The official listing URL is blank because no listing page for the intended ASIN could be read.</p>
    <div class="note">The intended identifiers come from the submitted links. They are 9 characters long, not 10, which fails the ASIN format in <a href="sources.html">SRC-12</a>. Nothing has been corrected.</div>
    {build_products()}
    <h2>How to read this table</h2>
    <div class="prose"><ul>
      <li><strong>Intended ASIN</strong> — taken from the link path. It is what the owner intended, not a confirmed listing.</li>
      <li><strong>Observed redirect target</strong> — the URL reached by following the link on {UPDATED}, from a non-browser fetch. It may differ for a signed-in visitor.</li>
      <li><strong>ASIN check</strong> — MISMATCH means both ASINs exist and differ. UNRESOLVED means no product was reached.</li>
      <li><strong>tag=</strong> — whether the tracking ID <code>{esc(load("products.json")["tracking_id"]["value"])}</code> appears in the observed target. None does.</li>
    </ul></div>
"""
    return page("products.html", "Product records", body, "Product-intent confirmation records: intended ASIN, observed redirect target, and match.", "dashboard.html", "")

def build_analysis():
    rows, flagged = [], set()
    for i, f in enumerate(ANALYSIS):
        rows.append([
            f'<strong>{esc(f["id"])}</strong>',
            esc(f["finding"]),
            f'<strong>{esc(f["value"])}</strong>',
            esc(f["detail"]),
            src_links(f["source_ids"]),
            f'<a href="flagged.html#{esc(f["flag"])}">{esc(f["flag"])}</a>',
        ])
    body = f"""
    <p class="kicker">Dashboard · analysis</p>
    <h1>Analysis & findings</h1>
    <p class="lede">These counts are taken from the product records. They are not scores. The brief asks for no conversion score or revenue forecast, and none is shown.</p>
    <div class="note warn">Pricing, reviews and commission potential cannot be analysed from verified data yet. The commission schedule needs Associates sign-in (FLG-09). Prices are excluded (FLG-10).</div>
    {table(["ID", "Finding", "Value", "Detail", "Source (official)", "Flag"], rows)}
"""
    return page("analysis.html", "Analysis & findings", body, "Findings from the verified product records, with sources and flags.", "dashboard.html", "")

def build_sources():
    rows, unv = [], set()
    for i, s in enumerate(SOURCES.values()):
        if s["tier"] == "user-supplied":
            link = '<span class="tag tag-neutral">Owner brief — no official URL</span>'
            unv.add(i)
        else:
            link = ext_link(s["url"], s["url"])
        date = s.get("page_updated") or s.get("observed") or "—"
        rows.append([
            f'<strong>{esc(s["id"])}</strong>',
            esc(s["tier"]),
            esc(s["title"]),
            esc(s["publisher"]),
            link,
            esc(date),
            esc(s["supports"]),
        ])
    body = f"""
    <p class="kicker">Dashboard · sources</p>
    <h1>Source register</h1>
    <p class="lede">Each source was fetched and read on {UPDATED}. The <em>tier</em> column says what kind of source it is. Only official sources support a verified value.</p>
    <div class="note warn">Sources marked <em>observed</em> are live Amazon pages captured by a non-browser fetch. Re-check them before any decision.</div>
    {table(["ID", "Tier", "Title", "Publisher", "Link", "Date (page / observed)", "What it supports"], rows, unverified=unv)}
"""
    return page("sources.html", "Sources", body, "Source register: official sources read on 2026-11-20 with what each supports.", "dashboard.html", "")

def build_measurement():
    ev_rows = [[f'<code>{esc(e["name"])}</code>', esc(e["fields"]), '<span class="tag tag-amber">PROPOSED</span>'] for e in MEASURE["events"]]
    ev = table(["Event", "Fields recorded", "Status"], ev_rows, unverified=set(range(len(ev_rows))))
    ledger = table(LEDGER_HEADER, [["—"] * len(LEDGER_HEADER)], cls="data ledger")
    privacy = "".join(f"<li>{esc(x)}</li>" for x in MEASURE["privacy_design"])
    body = f"""
    <p class="kicker">Dashboard · measurement</p>
    <h1>Measurement</h1>
    <div class="note warn"><strong>Status:</strong> {esc(MEASURE["status"])} Measurement needs a server the owner controls. See <a href="questions.html">Q06–Q07</a> and <a href="suggestions.html">Suggestions S04</a>.</div>
    <h2>Five events (proposed)</h2>
    <p class="prose">The brief asks for five defined events but does not list them. These are proposals only.</p>
    {ev}
    <h2>Privacy design</h2>
    <ul class="prose">{privacy}</ul>
    <p class="meta">Source for disclosure obligations: {src_link("SRC-02")}</p>
    <h2>Campaign ledger</h2>
    <p class="prose">Empty by design. Rows are added only from authorized first-party reports (Associates or Search Console), with a timestamp and provenance. No conversion score or revenue forecast is presented.</p>
    {ledger}
    <p class="meta">Source data file: <code>data/campaign_ledger.csv</code></p>
"""
    return page("measurement.html", "Measurement", body, "Measurement status: gated endpoint, proposed events, and an empty campaign ledger.", "dashboard.html", "")

def build_compliance():
    rows = [
        ["Associates statement shown on every page", "Done", "Disclosure strip under the masthead and in the footer", "SRC-01"],
        ["Disclosure placed where it is hard to miss", "Done", "Strip sits between the masthead and the page content", "SRC-04"],
        ["Affiliate links marked sponsored (rel=\"sponsored\")", "Done", "Every link to amazon.com or link.amazon carries rel=\"sponsored\"", "SRC-05"],
        ["No prices or ratings shown without a permitted source", "Done", "Prices shown as 'not verified'", "SRC-02"],
        ["Original content on the Site", "Done", "Guides are question-led and make no product performance claims", "SRC-02"],
        ["No Amazon trademark in the domain or tag", "Done", "Domain is karagemop466-tech.github.io/Affil3", "SRC-02"],
        ["No Special Links in print or offline material", "Done", "Site only; no printed material produced", "SRC-02"],
        ["Program Content not altered", "Done", "No Amazon images are used", "SRC-02"],
        ["Special Links use the Associates ID", "PENDING", "Submitted links are not yet confirmed as Special Links (FLG-02, FLG-04)", "SRC-02"],
        ["Site identified in the Associates application", "PENDING", "Owner to confirm in Associates Central (FLG-05)", "SRC-02"],
        ["Cookie and data use disclosed", "PENDING", "No cookies set by site code; endpoint gated (FLG-11)", "SRC-02"],
        ["Status of link.amazon links", "UNRESOLVED", "No official ruling found (FLG-06)", "SRC-01"],
        ["Trademark Guidelines reviewed", "PENDING", "Not read in this session (FLG-13)", "SRC-02"],
        ["Commission rate schedule", "UNVERIFIED", "Sign-in required (FLG-09)", "SRC-03"],
    ]
    status_tag = {"Done": "ok", "PENDING": "amber", "UNRESOLVED": "bad", "UNVERIFIED": "amber"}
    rows = [[esc(r[0]), badge(status_tag[r[1]], r[1]), esc(r[2]), src_link(r[3])] for r in rows]
    body = f"""
    <p class="kicker">Dashboard · compliance</p>
    <h1>Compliance checklist</h1>
    <p class="lede">The required statement is quoted exactly. The disclosure is placed with the links, not only on an About page, as FTC guidance describes.</p>
    <div class="note"><strong>Required statement (Operating Agreement §5):</strong> “{esc(STATEMENT)}”</div>
    {table(["Requirement", "Status", "Where it is handled", "Source (official)"], rows)}
    <h2>What this checklist does not cover</h2>
    <p class="prose">This is not legal advice. It records what was checked against the official texts listed. Owner review is still needed for the open items.</p>
"""
    return page("compliance.html", "Compliance", body, "Compliance checklist for Amazon Associates and FTC disclosure.", "dashboard.html", "")

def build_review():
    items = [
        ("Executive summary", "What was found, what is verified, and what is blocked.", "executive-summary.html"),
        ("Questions to resolve", f"{len(QUESTIONS)} questions with what is known, what is missing, and how to find out.", "questions.html"),
        ("Suggestions — choose a path", f"{len(SUGGESTIONS)} suggestions with options. Nothing changes until you choose.", "suggestions.html"),
        ("Flagged for Review", f"{len(FLAGS)} irregularities and unverified items, with source links.", "flagged.html"),
    ]
    cards = "".join(f'<article class="card"><h3><a href="{h}">{esc(t)}</a></h3><p class="source">{esc(d)}</p></article>' for t, d, h in items)
    body = f"""
    <p class="kicker">Review</p>
    <h1>Review and decisions</h1>
    <p class="lede">Everything needing your attention is here. Items are published for review, and none of them blocks the site.</p>
    <div class="grid">{cards}</div>
"""
    return page("review.html", "Review", body, "Review: executive summary, questions, suggestions, and flagged items.", "review.html", "")

def build_exec():
    body = f"""
    <p class="kicker">Review · executive summary</p>
    <h1>Executive summary</h1>
    <p class="meta">Checked {UPDATED}. Every figure links to a source on the <a href="sources.html">source register</a>.</p>
    <h2>What was done</h2>
    <div class="prose"><ul>
      <li>Five submitted short links were followed and the destination recorded for each (see <a href="products.html">product records</a>).</li>
      <li>Each intended identifier was checked against the official ASIN format (<a href="sources.html">SRC-12</a>).</li>
      <li>The Associates Operating Agreement and Program Policies were read for the statement, link format, and price-display rules (<a href="sources.html">SRC-01, SRC-02</a>).</li>
      <li>The site was built as a static GitHub Pages site with a front page, category pages, guides, dashboard, and a review section.</li>
    </ul></div>
    <h2>What is verified</h2>
    <div class="prose"><ul>
      <li>Four of five observed destinations are Amazon product listings. Their titles, ASINs and category breadcrumbs were recorded.</li>
      <li>The required Associates statement and the FTC disclosure placement are implemented on every page.</li>
      <li>Every Amazon product link carries <code>rel="sponsored"</code>.</li>
    </ul></div>
    <h2>What is not verified, and why it matters</h2>
    <div class="prose"><ul>
      <li><strong>0 of 5</strong> intended identifiers pass the 10-character ASIN format. All five are 9 characters with lowercase letters. (<a href="flagged.html#FLG-01">FLG-01</a>)</li>
      <li><strong>4 of 5</strong> links reach a different ASIN than the one in the link; <strong>1 of 5</strong> reaches an interstitial. (<a href="flagged.html#FLG-02">FLG-02</a>, <a href="flagged.html#FLG-03">FLG-03</a>)</li>
      <li><strong>0 of 4</strong> observed destinations contain the tracking ID. (<a href="flagged.html#FLG-04">FLG-04</a>)</li>
      <li><strong>No</strong> prices, ratings, or commission rates are verified, so pricing and commission potential cannot be analysed yet. (<a href="flagged.html#FLG-09">FLG-09</a>, <a href="flagged.html#FLG-10">FLG-10</a>)</li>
      <li>The click counter and analytics endpoint are built but <strong>gated</strong>, because GitHub Pages cannot store events. (<a href="flagged.html#FLG-11">FLG-11</a>)</li>
    </ul></div>
    <h2>Decisions needed before scaling</h2>
    <div class="prose"><ol>
      <li>Confirm each intended identifier from its original listing (<a href="questions.html">Q01–Q02</a>).</li>
      <li>Confirm the tracking ID and Site registration in Associates Central (<a href="questions.html">Q03, Q05</a>).</li>
      <li>Decide the link approach: test one Special Link first, or hold (<a href="suggestions.html">S02</a>).</li>
      <li>Choose a measurement path and define the five events (<a href="suggestions.html">S04</a>, <a href="questions.html">Q06</a>).</li>
    </ol></div>
    <h2>Not done in this build</h2>
    <div class="prose"><ul>
      <li>No Associates test link was generated. That needs account access.</li>
      <li>No Search Console verification. That needs the owner's Google account.</li>
      <li>No self-hosted analytics endpoint. That needs a server.</li>
    </ul></div>
"""
    return page("executive-summary.html", "Executive summary", body, "Executive summary: verified facts, blocked items, and decisions needed.", "review.html", "")

def build_questions():
    rows, unv = [], set()
    for i, q in enumerate(QUESTIONS):
        if not has_official(q["source_ids"]):
            unv.add(i)
        rows.append([
            f'<strong>{esc(q["id"])}</strong>',
            esc(q["question"]),
            esc(q["have"]),
            esc(q["missing"]),
            esc(q["how_to_discover"]),
            src_links(q["source_ids"]),
            badge("bad", "Blocking") if q["blocking"] else badge("neutral", "Not blocking"),
        ])
    body = f"""
    <p class="kicker">Review · questions</p>
    <h1>Questions to resolve</h1>
    <p class="lede">These questions must be answered before some decisions can reasonably be made. Each one says what is known, what is missing, and how to find out.</p>
    {table(["ID", "Question", "What we have", "What is missing", "How to find out", "Source (official)", "Blocking"], rows, unverified=unv)}
"""
    return page("questions.html", "Questions to resolve", body, "Open questions, what is known and missing, and how to resolve each one.", "review.html", "")

def build_suggestions():
    rows, unv = [], set()
    for i, s in enumerate(SUGGESTIONS):
        if not has_official(s["source_ids"]):
            unv.add(i)
        opts = "<ul>" + "".join(
            f'<li><strong>{esc(o["id"])}</strong> · {esc(o["label"])} <span class="cell-muted">(effort: {esc(o["effort"])}; risk: {esc(o["risk"])})</span></li>'
            for o in s["options"]) + "</ul>"
        rows.append([
            f'<strong>{esc(s["id"])}</strong><br>{esc(s["title"])}',
            opts,
            esc(s["why"]),
            src_links(s["source_ids"]),
            esc(", ".join(s["depends_on"]) or "—"),
            badge("amber", "AWAITING YOUR CHOICE"),
        ])
    decision_log = table(["Suggestion", "Option chosen", "Chosen by", "Date"], [["—", "—", "—", "—"]], cls="data ledger")
    body = f"""
    <p class="kicker">Review · suggestions</p>
    <h1>Suggestions — choose a path</h1>
    <p class="lede">Each suggestion has options. Pick one for each before anything is implemented. Options are labelled A, B, C and give effort and risk.</p>
    <div class="note warn">No suggestion here has been implemented. Changes will follow only after an option is recorded in the decision log below.</div>
    {table(["Suggestion", "Options", "Why", "Source (official)", "Depends on", "Status"], rows, unverified=unv)}
    <h2>Decision log</h2>
    <p class="prose">Record each choice here. The log is empty until you choose.</p>
    {decision_log}
"""
    return page("suggestions.html", "Suggestions", body, "Suggestions with options; nothing is implemented until a path is chosen.", "review.html", "")

def build_flagged():
    rows, unv = [], set()
    for i, f in enumerate(FLAGS):
        if not has_official(f["source_ids"]):
            unv.add(i)
        sev = {"high": "bad", "medium": "amber", "low": "neutral"}[f["severity"]]
        srcs = src_links(f["source_ids"])
        rows.append([
            f'<a id="{esc(f["id"])}"></a><strong>{esc(f["id"])}</strong>',
            badge(sev, f["severity"]),
            f'<strong>{esc(f["title"])}</strong><br><span class="cell-muted">{esc(f["detail"])}</span>',
            srcs,
            f'<code>{esc(f["where"])}</code>',
            esc(f["action"]),
        ])
    body = f"""
    <p class="kicker">Review · flagged for review</p>
    <h1>Flagged for Review</h1>
    <p class="lede">Irregularities and unverified items, each with its source link. These do not block the site. Owner review is requested after the site is live.</p>
    {table(["ID", "Severity", "Irregularity", "Source (official / owner)", "Where", "Action requested"], rows, unverified=unv)}
"""
    return page("flagged.html", "Flagged for Review", body, "Irregularities and unverified items for owner review, with source links.", "review.html", "")

def build_about():
    body = f"""
    <p class="kicker">About</p>
    <h1>About {BRAND}</h1>
    <div class="prose">
    <p>{BRAND} is a buyer's guide for small kitchen appliances. It shows Amazon listings the owner has submitted, records how each link was checked, and explains what is still unknown.</p>
    <h2>Editorial rules</h2>
    <ul>
      <li>A value is shown only if it is linked to an official source. If it cannot be confirmed, it is left blank and marked unverified.</li>
      <li>Guides ask buyer questions. They make no claims about any product's quality, popularity, or search volume.</li>
      <li>Nothing is inferred from a related product on the same page.</li>
    </ul>
    <h2>Byline</h2>
    <p>Pages are signed “{esc(GUIDES_META["byline"])}” as a placeholder. No author has been named. The owner will choose the byline (<a href="flagged.html#FLG-15">FLG-15</a>).</p>
    <h2>How pages were made</h2>
    <p>Pages are generated from the data files in the repository. The build runs a check that every table row carries an official source link and that every Amazon link is marked sponsored. Source code: {ext_link(REPO_URL, "GitHub repository")}.</p>
    <h2>Contact</h2>
    <p>No contact address has been set. The owner will add one (<a href="questions.html">Q13</a>).</p>
    </div>
"""
    return page("about.html", f"About {BRAND}", body, f"About {BRAND}: editorial rules, byline, and how pages are built.", "about.html", "")

def build_sitemap(paths):
    urls = "".join(f"  <url><loc>{SITE_BASE}{p}</loc><lastmod>{UPDATED}</lastmod></url>\n" for p in paths)
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "</urlset>\n", encoding="utf-8")

def build_feed():
    pub = email.utils.format_datetime(dt.datetime(2026, 11, 20, 12, 0, tzinfo=dt.timezone.utc))
    items = []
    for g in GUIDES:
        link = f"{SITE_BASE}guides/{g['slug']}.html"
        items.append(f"""  <item>
    <title>{esc(g["title"])}</title>
    <link>{link}</link>
    <guid isPermaLink="true">{link}</guid>
    <pubDate>{pub}</pubDate>
    <description>{esc(g["summary"] + " Working title — hypothesis, not a product claim.")}</description>
  </item>
""")
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
  <title>{BRAND} guides</title>
  <link>{SITE_BASE}</link>
  <description>Buyer-question guides for small kitchen appliances. Working titles; no product performance claims.</description>
  <language>en-us</language>
  <lastBuildDate>{pub}</lastBuildDate>
{''.join(items)}</channel>
</rss>
"""
    (OUT / "feed.xml").write_text(xml, encoding="utf-8")

def clean_generated():
    for p in OUT.rglob("*.html"):
        p.unlink()
    for name in ("sitemap.xml", "feed.xml", "robots.txt"):
        (OUT / name).unlink(missing_ok=True)

def main():
    clean_generated()
    OUT.mkdir(exist_ok=True)
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    written = []
    written.append(build_index())
    written.append(build_categories())
    for slug, name, href in CATEGORIES:
        written.append(build_category_page(slug, name, href))
    written.append(build_guides_index())
    for g in GUIDES:
        written.append(build_guide(g))
    written += [
        build_dashboard(), build_products_page(), build_analysis(), build_sources(),
        build_measurement(), build_compliance(), build_review(), build_exec(),
        build_questions(), build_suggestions(), build_flagged(), build_about(),
    ]
    html_pages = sorted(p for p in written)
    build_sitemap(html_pages)
    build_feed()
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE_BASE}sitemap.xml\n", encoding="utf-8")
    print(f"built {len(written)} HTML pages, sitemap, feed, robots.txt into docs/")

if __name__ == "__main__":
    main()
