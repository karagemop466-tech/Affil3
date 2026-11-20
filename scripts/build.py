#!/usr/bin/env python3
"""Build the static site in docs/ from the register/ data files.

Standard library only. Every table row must carry source IDs that resolve to
an entry in register/sources.json on an allowed official host. The build stops
with an error if a row has no source, so a row cannot be published unsourced.

Run:  python3 scripts/build.py
Then: python3 scripts/checks.py
"""
import datetime
import email.utils
import glob
import html
import json
import os
import posixpath
import shutil
import sys
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REG = os.path.join(ROOT, "register")
OUT = os.path.join(ROOT, "docs")

ALLOWED_HOSTS = {
    "amazon.com",
    "affiliate-program.amazon.com",
    "ftc.gov",
    "docs.github.com",
    "github.com",
    "developers.google.com",
    "search.google.com",
    "sitemaps.org",
    "www.sitemaps.org",
    "rssboard.org",
    "www.rssboard.org",
    "link.amazon",
}

# Hosts that are Amazon-owned. Every link to these hosts is a product or
# Amazon-page link and gets rel="sponsored" (Google's paid-link value).
AMAZON_SPONSORED_SUFFIXES = ("amazon.com", "link.amazon")


def load(name):
    with open(os.path.join(REG, name), encoding="utf-8") as fh:
        return json.load(fh)


SITE = load("site.json")
BASE = SITE["base_url"].rstrip("/")
BUILD_DATE = SITE["build_date"]
BUILD_DT = datetime.date.fromisoformat(BUILD_DATE)
SOURCES = {s["id"]: s for s in load("sources.json")["sources"]}
PRODUCTS = load("products.json")["products"]
PBY = {p["id"]: p for p in PRODUCTS}
FLAGS = load("flags.json")["flags"]
QUESTIONS = load("questions.json")["questions"]
SUGGESTIONS = load("suggestions.json")
COMPLIANCE = load("compliance.json")["checks"]
REPO = load("repo-review.json")["rows"]
MEASURE = load("measurement.json")
LEDGER = load("ledger.json")
GUIDES = []
for f in sorted(glob.glob(os.path.join(REG, "guides", "*.json"))):
    with open(f, encoding="utf-8") as fh:
        GUIDES.append(json.load(fh))
GUIDES.sort(key=lambda g: g["published"], reverse=True)
GBY = {g["slug"]: g for g in GUIDES}

CUR = "index.html"  # path of the page being rendered (set per page)
PAGES = []  # (path, lastmod) for sitemap
ERRORS = []


def fail(msg):
    ERRORS.append(msg)


def esc(s):
    return html.escape(str(s), quote=True)


def host_ok(url):
    h = urllib.parse.urlsplit(url).hostname or ""
    return any(h == a or h.endswith("." + a) for a in ALLOWED_HOSTS)


def validate_sources():
    for sid, s in SOURCES.items():
        if not host_ok(s["url"]):
            fail(f"{sid}: host not on allowlist: {s['url']}")
        if s.get("official") is not True:
            fail(f"{sid}: not marked official")


def cite(ids, ctx):
    """Render source links for a row. Refuse rows with no valid source."""
    if not ids:
        fail(f"row has no source: {ctx}")
        return "<em>missing source</em>"
    out = []
    for sid in ids:
        if sid not in SOURCES:
            fail(f"{ctx}: unknown source {sid}")
            continue
        s = SOURCES[sid]
        out.append(
            f'<a href="{esc(s["url"])}"{rel_for(s["url"])} title="{esc(s["title"])}">{esc(sid)}</a>'
            + paid_tag(s["url"])
        )
    return " ".join(out)


def set_cur(path):
    global CUR
    CUR = path


AMAZON_SHOP_HOSTS = ("amazon.com", "link.amazon")


def is_shop_host(host):
    host = (host or "").lower()
    if host == "affiliate-program.amazon.com" or host.endswith(".affiliate-program.amazon.com"):
        return False
    return any(host == h or host.endswith("." + h) for h in AMAZON_SHOP_HOSTS)


def paid_tag(url):
    """Label placed after an Amazon shopping link, as the Associates help page asks."""
    return ' <span class="paid">(paid link)</span>' if is_shop_host(urllib.parse.urlsplit(url).hostname) else ""


def rel_for(url):
    """Amazon shopping and product pages are sponsored. Other official sources get no rel."""
    return ' rel="sponsored"' if is_shop_host(urllib.parse.urlsplit(url).hostname) else ""


def L(target):
    """Relative link from the current page to a target file in docs/."""
    return posixpath.relpath(target, posixpath.dirname(CUR) or ".")


def buy_link(pid, label):
    p = PBY[pid]
    return (
        f'<a class="buy" href="{esc(p["supplied_link"])}" rel="sponsored" '
        f'data-event="outbound_click" data-product-id="{esc(pid)}">{esc(label)}</a> '
        f'<span class="paid">(paid link)</span>'
    )


def inline_text(text):
    """Escape text and expand {{P-xx}} markers into sponsored product links."""
    out = []
    pos = 0
    while True:
        i = text.find("{{", pos)
        if i < 0:
            out.append(esc(text[pos:]))
            break
        j = text.find("}}", i)
        out.append(esc(text[pos:i]))
        pid = text[i + 2 : j]
        if pid not in PBY:
            fail(f"unknown product marker {pid} in {CUR}")
            out.append(esc(pid))
        else:
            out.append(buy_link(pid, PBY[pid]["short_name"]))
        pos = j + 2
    return "".join(out)


def clean_title(t):
    t = t.replace("Amazon.com: ", "", 1) if t.startswith("Amazon.com: ") else t
    if t.endswith(" : Home & Kitchen"):
        t = t[: -len(" : Home & Kitchen")]
    return t


def table(headers, rows, filter_id=None, kind="data"):
    head = "".join(f"<th scope=\"col\">{esc(h)}</th>" for h in headers)
    body = "".join(
        "<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows
    )
    fid = f' data-table="{filter_id}"' if filter_id else ""
    filt = ""
    if filter_id:
        filt = (
            f'<label class="filter">Filter rows <input type="search" data-filter="{filter_id}" '
            f'placeholder="Type to filter"></label>'
        )
    return (
        f'{filt}<div class="table-wrap"><table class="{kind}"{fid}>'
        f"<thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>"
    )


def pill(text, kind="neutral"):
    return f'<span class="pill pill-{kind}">{esc(text)}</span>'


NAV = [
    ("products/index.html", "Products"),
    ("categories/index.html", "Categories"),
    ("guides/index.html", "Guides"),
    ("executive-summary/index.html", "Executive summary"),
]

DASHBOARDS = [
    ("products/index.html", "Products table"),
    ("intent/index.html", "Product-intent record"),
    ("categories/index.html", "Categories"),
    ("guides/index.html", "Guides"),
    ("ledger/index.html", "Campaign ledger"),
    ("compliance/index.html", "Compliance gate"),
    ("measurement/index.html", "Measurement"),
    ("sources/index.html", "Source register"),
    ("questions/index.html", "Questions and gaps"),
    ("suggestions/index.html", "Suggestions"),
    ("flagged-review/index.html", "Flagged for Review"),
    ("repo-review/index.html", "Repository review"),
    ("executive-summary/index.html", "Executive summary"),
    ("disclosure/index.html", "Disclosure"),
]


def header_html():
    nav = "".join(
        '<a href="{}"{}>{}</a>'.format(esc(L(p)), ' aria-current="page"' if CUR == p else "", esc(t))
        for p, t in NAV
    )
    return (
        '<header class="mast">'
        '<div class="mast-inner">'
        f'<a class="brand" href="{esc(L("index.html"))}">{esc(SITE["name"])}</a>'
        f'<p class="tagline">{esc(SITE["tagline"])}</p>'
        "</div>"
        "</header>"
        '<div class="disclosure" role="note" aria-label="Affiliate disclosure">'
        f'<p><strong>Disclosure.</strong> {esc(SITE["disclosure_strip"])} '
        f'<span>{esc(SITE["disclosure_link_label"])}</span></p>'
        "</div>"
        f'<nav class="nav" aria-label="Main">{nav}</nav>'
    )


def footer_html():
    links = "".join(
        f'<li><a href="{esc(L(p))}">{esc(t)}</a></li>' for p, t in DASHBOARDS
    )
    return (
        '<div class="disclosure disclosure-foot" role="note">'
        f'<p><strong>Disclosure.</strong> {esc(SITE["disclosure_strip"])} '
        f'<span>{esc(SITE["disclosure_link_label"])}</span></p></div>'
        '<footer class="foot"><div class="foot-inner">'
        '<div><h2>Dashboards</h2><ul class="dash">' + links + "</ul></div>"
        '<div><h2>Feeds</h2><ul>'
        f'<li><a href="{esc(L("feed.xml"))}">RSS feed of guides</a></li>'
        f'<li><a href="{esc(L("sitemap.xml"))}">Sitemap</a></li>'
        f'<li><a href="{esc(L("robots.txt"))}">robots.txt</a></li>'
        "</ul></div>"
        "<div><h2>Status</h2><p>Built " + esc(BUILD_DATE) + ". Prices are not shown. "
        "Measurement is not recording (no endpoint). Verification: see "
        f'<a href="{esc(L("flagged-review/index.html"))}">Flagged for Review</a>.</p></div>'
        "</div></footer>"
    )


def layout(path, title, desc, body, jsonld=None, page_class=""):
    global CUR
    CUR = path
    url_path = path[: -len("index.html")] if path.endswith("index.html") else path
    canonical = f"{BASE}/{url_path}"
    ld = ""
    if jsonld:
        ld = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>'
    head = (
        '<!DOCTYPE html><html lang="en-US"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>{esc(title)}{'' if title == SITE['name'] else ' · ' + esc(SITE['name'])}</title>"
        f'<meta name="description" content="{esc(desc)}">'
        f'<link rel="canonical" href="{esc(canonical)}">'
        f'<link rel="alternate" type="application/rss+xml" title="{esc(SITE["name"])} guides" href="{esc(L("feed.xml"))}">'
        '<meta property="og:type" content="website">'
        f'<meta property="og:title" content="{esc(title)}">'
        f'<meta property="og:description" content="{esc(desc)}">'
        f'<meta property="og:url" content="{esc(canonical)}">'
        f'<link rel="stylesheet" href="{esc(L("assets/site.css"))}">'
        f"{ld}"
        "</head>"
    )
    page = (
        f'<body class="{page_class}">'
        '<a class="skip" href="#main">Skip to content</a>'
        + header_html()
        + f'<main id="main" class="wrap">{body}</main>'
        + footer_html()
        + f'<script src="{esc(L("assets/site.js"))}" defer></script>'
        + f'<script src="{esc(L("assets/measure.js"))}" defer></script>'
        + "</body></html>\n"
    )
    PAGES.append((path, BUILD_DATE))
    return head + page


def write(path, content):
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as fh:
        fh.write(content)


def status_kind(s):
    s = s.lower()
    if s.startswith("pass"):
        return "ok"
    if s.startswith("blocked") or "unresolved" in s or "open" in s or "flag" in s or "not" in s:
        return "warn"
    return "neutral"


# --------------------------------------------------------------------- pages


def product_card(p):
    unresolved = p["id"] == "P-04"
    kind = "warn" if unresolved else "ok"
    status = "Unresolved" if unresolved else "Observed on Amazon"
    title = "Not yet identified" if unresolved else clean_title(p["observed_title"])
    meta = (
        "Supplied link opened to an Amazon checkpoint page. No product named."
        if unresolved
        else f"Observed ASIN <code>{esc(p['observed_asin'])}</code> · {esc(p['observed_breadcrumb'].split(' › ')[-1])}"
    )
    detail = (
        f'<a href="{esc(L("products/" + p["page_slug"] + "/index.html"))}">Product details</a>'
    )
    return (
        '<article class="card">'
        f'<p class="kicker">{esc(p["category_label"])}</p>'
        f'<h3>{esc(title)}</h3>'
        f"<p class=\"meta\">{meta}</p>"
        f'<p>{pill(status, kind)} {pill("Price not verified", "neutral")}</p>'
        f'<p class="actions">{buy_link(p["id"], "Open supplied link")}</p>'
        f'<p class="more">{detail}</p>'
        "</article>"
    )


def page_home():
    set_cur("index.html")
    cards = "".join(product_card(p) for p in PRODUCTS)
    guide_cards = "".join(
        '<article class="card card-guide">'
        f'<p class="kicker">Guide · {esc(g["published"])}</p>'
        f'<h3><a href="{esc(L("guides/" + g["slug"] + "/index.html"))}">{esc(g["title"])}</a></h3>'
        f'<p>{esc(g["dek"])}</p></article>'
        for g in GUIDES
    )
    body = (
        '<section class="hero">'
        '<p class="eyebrow">Kitchen picks · Amazon listings</p>'
        "<h1>Five products from the brief, shown as the listings read</h1>"
        '<p class="dek">Three air fryers, a smart meat thermometer, and one link still to be identified. '
        "Titles and categories come from the Amazon pages read on "
        f"{esc(BUILD_DATE)}. No prices or ratings are shown.</p>"
        "</section>"
        '<section class="block"><div class="section-head"><h2>The products</h2>'
        f'<a href="{esc(L("products/index.html"))}">Full table</a></div>'
        f'<div class="grid">{cards}</div></section>'
        '<section class="block"><div class="section-head"><h2>Guides</h2>'
        f'<a href="{esc(L("guides/index.html"))}">All guides</a></div>'
        f'<div class="grid grid-guides">{guide_cards}</div></section>'
        '<section class="block split">'
        "<div><h2>Shop by category</h2><ul class=\"plain\">"
        f'<li><a href="{esc(L("categories/air-fryers/index.html"))}">Air fryers</a> · 3 products</li>'
        f'<li><a href="{esc(L("categories/meat-thermometers/index.html"))}">Meat thermometers</a> · 1 product</li>'
        f'<li><a href="{esc(L("categories/unresolved/index.html"))}">Unresolved</a> · 1 link</li>'
        "</ul></div>"
        "<div><h2>Before you click</h2>"
        "<p>Every product link on this site is a sponsored (paid) link. The site earns a commission "
        "on qualifying purchases made through those links. Product facts are dated and sourced; "
        'anything not confirmed is marked, and the open items are on the <a href="'
        f'{esc(L("flagged-review/index.html"))}">Flagged for Review</a> page.</p></div>'
        "</section>"
    )
    ld = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": SITE["name"],
        "url": BASE + "/",
        "description": SITE["tagline"],
    }
    return layout(
        "index.html",
        SITE["name"],
        "Kitchen buying guides and five product listings from Amazon, with dated, sourced facts and a clear affiliate disclosure.",
        body,
        jsonld=ld,
        page_class="home",
    )


def page_products():
    set_cur("products/index.html")
    rows = []
    for p in PRODUCTS:
        name = (
            "Not yet identified"
            if p["id"] == "P-04"
            else f'<a href="{esc(L("products/" + p["page_slug"] + "/index.html"))}">{esc(clean_title(p["observed_title"]))}</a>'
        )
        rows.append(
            [
                esc(p["id"]),
                name,
                esc(p["category_label"]),
                f"<code>{esc(p['observed_asin'])}</code>" if p["observed_asin"] else "—",
                "Not confirmed",
                "Not verified",
                esc(p["status"]),
                cite(p["source_ids"], p["id"]),
                buy_link(p["id"], "Open"),
            ]
        )
    body = (
        '<section class="page-head"><p class="eyebrow">Dashboard</p>'
        "<h1>Products</h1>"
        "<p>One row per supplied link. The observed ASIN is the code in the Amazon URL that the link opened. "
        "The intended ASIN is blank until the owner confirms it. Price is blank because it was not verified.</p></section>"
        + table(
            ["ID", "Product (as observed)", "Category", "Observed ASIN", "Intended ASIN", "Price", "Status", "Sources", "Link"],
            rows,
            filter_id="products",
        )
    )
    return layout(
        "products/index.html",
        "Products",
        "All five supplied product links, with observed Amazon titles, categories and sources.",
        body,
    )


def page_product(p):
    set_cur(f"products/{p['page_slug']}/index.html")
    facts = [
        ("Supplied link", buy_link(p["id"], p["supplied_link"])),
        ("Supplied code (length)", f"<code>{esc(p['supplied_code'])}</code> ({p['supplied_code_length']} characters)"),
        ("Intended ASIN", esc(p["intended_asin_status"])),
        ("Observed redirect target", f"<code>{esc(p['observed_redirect_target'])}</code>" if p["observed_redirect_target"] else "—"),
        ("Observed ASIN", f"<code>{esc(p['observed_asin'])}</code>" if p["observed_asin"] else "None"),
        ("Observed title", esc(p["observed_title"])),
        ("Observed category", esc(p["observed_breadcrumb"] or "None")),
        ("Price", "Not verified. Not shown."),
        ("Rating", "Not verified. Not shown."),
        ("Tracking parameter in observed URL", "No tag= parameter" if p["observed_tag_param"] is False else "Not applicable"),
        ("Observed on", esc(p["observed_on"])),
        ("Status", esc(p["status"])),
    ]
    rows = [[esc(k), v, cite(p["source_ids"], p["id"] + " " + k)] for k, v in facts]
    guides = [g for g in GUIDES if p["id"] in g["products"]]
    gl = "".join(
        f'<li><a href="{esc(L("guides/" + g["slug"] + "/index.html"))}">{esc(g["title"])}</a></li>' for g in guides
    ) or "<li>No guide yet.</li>"
    flags = [f for f in FLAGS if p["id"] in json.dumps(f) or f["id"] in ("FLG-R01", "FLG-R03")]
    fl = "".join(
        f'<li><a href="{esc(L("flagged-review/index.html"))}#{esc(f["id"])}">{esc(f["id"])}</a> · {esc(f["item"])}</li>'
        for f in flags
    )
    body = (
        '<section class="page-head"><p class="eyebrow">' + esc(p["category_label"]) + "</p>"
        f"<h1>{esc(p['short_name'])}</h1>"
        f"<p>{esc(clean_title(p['observed_title'])) if p['id'] != 'P-04' else 'No product title could be read from the supplied link.'}</p></section>"
        '<section class="block">' + table(["Field", "Value", "Sources"], rows) + "</section>"
        '<section class="block split"><div><h2>Sources</h2><p>' + cite(p["source_ids"], p["id"]) + "</p></div>"
        f'<div><h2>Guides that mention this product</h2><ul class="plain">{gl}</ul>'
        f"<h2>Open items</h2><ul class=\"plain\">{fl}</ul></div></section>"
    )
    return layout(
        f"products/{p['page_slug']}/index.html",
        p["short_name"],
        f"Observed Amazon facts for {p['short_name']}: title, category and ASIN as read on {BUILD_DATE}. Price not verified.",
        body,
        page_class="product",
    )


def page_categories():
    set_cur("categories/index.html")
    cats = {}
    for p in PRODUCTS:
        cats.setdefault(p["category_slug"], []).append(p)
    rows = []
    for slug, label in [
        ("air-fryers", "Air fryers"),
        ("meat-thermometers", "Meat thermometers"),
        ("unresolved", "Unresolved"),
    ]:
        items = cats.get(slug, [])
        n = len(items)
        ids = sorted({sid for it in items for sid in it["source_ids"]})
        rows.append(
            [
                f'<a href="{esc(L("categories/" + slug + "/index.html"))}">{esc(label)}</a>',
                str(n),
                esc("Amazon breadcrumb, as observed" if slug != "unresolved" else "No product identified"),
                cite(ids, "category " + slug),
            ]
        )
    body = (
        '<section class="page-head"><p class="eyebrow">Dashboard</p><h1>Categories</h1>'
        "<p>Products grouped by the Amazon breadcrumb observed on each page. "
        "A product with no breadcrumb is grouped as unresolved.</p></section>"
        + table(["Category", "Products", "Basis", "Sources"], rows)
    )
    return layout("categories/index.html", "Categories", "Products grouped by observed Amazon category.", body)


def page_category(slug, label, desc):
    set_cur(f"categories/{slug}/index.html")
    items = [p for p in PRODUCTS if p["category_slug"] == slug]
    rows = []
    for p in items:
        rows.append(
            [
                f'<a href="{esc(L("products/" + p["page_slug"] + "/index.html"))}">{esc(p["id"])}</a>',
                esc(clean_title(p["observed_title"])) if p["id"] != "P-04" else "Not yet identified",
                f"<code>{esc(p['observed_asin'])}</code>" if p["observed_asin"] else "—",
                esc(p["observed_breadcrumb"] or "—"),
                cite(p["source_ids"], p["id"]),
            ]
        )
    body = (
        f'<section class="page-head"><p class="eyebrow">Category</p><h1>{esc(label)}</h1><p>{esc(desc)}</p></section>'
        + table(["ID", "Product (as observed)", "Observed ASIN", "Breadcrumb", "Sources"], rows)
        + f'<p class="back"><a href="{esc(L("categories/index.html"))}">All categories</a></p>'
    )
    return layout(f"categories/{slug}/index.html", label, desc, body)


def page_guides_index():
    set_cur("guides/index.html")
    items = "".join(
        '<article class="card card-guide">'
        f'<p class="kicker">Published {esc(g["published"])}</p>'
        f'<h3><a href="{esc(L("guides/" + g["slug"] + "/index.html"))}">{esc(g["title"])}</a></h3>'
        f'<p>{esc(g["dek"])}</p>'
        f'<p class="meta">{esc(g["status"])}</p></article>'
        for g in GUIDES
    )
    body = (
        '<section class="page-head"><p class="eyebrow">Guides</p><h1>Questions buyers ask</h1>'
        "<p>These titles are working titles, chosen as questions a buyer might ask. They are not based on "
        "search or traffic data, which the site does not yet have (Q-12).</p></section>"
        f'<div class="grid grid-guides">{items}</div>'
        '<section class="block"><h2>Publishing</h2><p>Four guides were published together on '
        f'{esc(BUILD_DATE)}. No cadence has been set (Q-11). Each guide is in the sitemap and in the '
        f'<a href="{esc(L("feed.xml"))}">RSS feed</a>.</p></section>'
    )
    return layout("guides/index.html", "Guides", "Question-shaped buying guides for the supplied products.", body)


def inline_block(b):
    t = b["type"]
    if t == "p":
        return f"<p>{inline_text(b['text'])}</p>"
    if t == "h2":
        return f"<h2>{esc(b['text'])}</h2>"
    if t == "ul":
        return "<ul>" + "".join(f"<li>{inline_text(i)}</li>" for i in b["items"]) + "</ul>"
    fail(f"unknown block type {t}")
    return ""


def page_guide(g):
    set_cur(f"guides/{g['slug']}/index.html")
    body_html = "".join(inline_block(b) for b in g["body"])
    prods = "".join(
        f'<li>{esc(PBY[pid]["short_name"])} · {buy_link(pid, "Open supplied link")}</li>' for pid in g["products"]
    )
    body = (
        '<article class="article">'
        '<p class="eyebrow">Guide · working title</p>'
        f'<h1>{esc(g["title"])}</h1>'
        f'<p class="dek">{esc(g["dek"])}</p>'
        f'<p class="meta">Published {esc(g["published"])} · {esc(g["status"])}</p>'
        f'<div class="prose">{body_html}</div>'
        '<section class="block"><h2>Products in this guide</h2>'
        f'<ul class="plain">{prods}</ul></section>'
        '<section class="block"><h2>Sources</h2><p>'
        + cite(g["source_ids"], g["slug"])
        + "</p></section>"
        f'<p class="back"><a href="{esc(L("guides/index.html"))}">All guides</a></p>'
        "</article>"
    )
    ld = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": g["title"],
        "description": g["dek"],
        "datePublished": g["published"],
        "dateModified": g["published"],
        "publisher": {"@type": "Organization", "name": SITE["name"]},
        "mainEntityOfPage": f"{BASE}/guides/{g['slug']}/",
    }
    return layout(
        f"guides/{g['slug']}/index.html",
        g["title"],
        g["dek"],
        body,
        jsonld=ld,
        page_class="guide",
    )


def page_intent():
    set_cur("intent/index.html")
    intent_rows = []
    observed_rows = []
    for p in PRODUCTS:
        intent_rows.append(
            [
                esc(p["id"]),
                f"<code>{esc(p['supplied_code'])}</code>",
                "Not confirmed",
                "Not confirmed",
                "Not confirmed",
                "Not confirmed",
                esc(p["intended_asin_status"]),
                cite(p["source_ids"], p["id"] + " intent"),
            ]
        )
        observed_rows.append(
            [
                esc(p["id"]),
                f"<code>{esc(p['observed_redirect_target'])}</code>" if p["observed_redirect_target"] else "—",
                f"<code>{esc(p['observed_asin'])}</code>" if p["observed_asin"] else "—",
                esc(p["observed_on"]),
                cite(p["source_ids"], p["id"]),
            ]
        )
    body = (
        '<section class="page-head"><p class="eyebrow">Dashboard</p><h1>Product-intent confirmation record</h1>'
        "<p>Two separate records. The intent record holds what the owner intended to link. "
        "The observed record holds what Amazon returned on the check date. The two are not merged. "
        "No intended ASIN is filled in from an observed one.</p></section>"
        '<section class="block"><h2>A. Intent record</h2>'
        + table(
            ["ID", "Supplied code", "Intended ASIN", "Official listing URL", "Confirmation date", "Confirmation source", "Note", "Sources"],
            intent_rows,
            filter_id="intent",
        )
        + "</section>"
        '<section class="block"><h2>B. Observed redirect record</h2>'
        + table(["ID", "Observed redirect target", "Observed ASIN", "Observed on", "Sources"], observed_rows, filter_id="observed")
        + "</section>"
    )
    return layout(
        "intent/index.html",
        "Product-intent confirmation record",
        "Intended ASINs and observed redirect targets, kept in separate fields.",
        body,
    )


def page_ledger():
    set_cur("ledger/index.html")
    cols = [[esc(c["name"]), esc(c["meaning"])] for c in LEDGER["columns"]]
    rules = "".join(f"<li>{esc(r)}</li>" for r in LEDGER["rules"])
    body = (
        '<section class="page-head"><p class="eyebrow">Dashboard</p><h1>Campaign ledger</h1>'
        f'<p>{esc(LEDGER["status"])}</p></section>'
        '<section class="block"><h2>Columns</h2>'
        + table(["Column", "What goes in it"], cols, kind="schema")
        + '</section><section class="block"><h2>Rows</h2>'
        + '<p class="empty">No rows. No authorized first-party report has been supplied (Q-18).</p>'
        + table(["timestamp", "source", "channel", "eligible_sessions", "clicks", "reported_orders", "provenance_note"], [])
        + '<p class="meta">Sources: '
        + cite(LEDGER["source_ids"], "ledger")
        + "</p></section>"
        f'<section class="block"><h2>Rules</h2><ul class="plain">{rules}</ul></section>'
    )
    return layout("ledger/index.html", "Campaign ledger", "Empty campaign ledger with its column rules.", body)


def page_compliance():
    set_cur("compliance/index.html")
    rows = []
    for c in COMPLIANCE:
        rows.append(
            [
                esc(c["id"]),
                esc(c["requirement"]),
                esc(c["method"]),
                pill(c["status"], status_kind(c["status"])),
                cite(c["source_ids"], c["id"]),
            ]
        )
    body = (
        '<section class="page-head"><p class="eyebrow">Dashboard</p><h1>Compliance gate</h1>'
        "<p>Each row is a requirement from the Associates documents or the FTC guidance, the way it is "
        "checked, and the result. Automated rows fail the build if they break.</p></section>"
        + table(["ID", "Requirement", "How it is checked", "Status", "Sources"], rows, filter_id="compliance")
    )
    return layout("compliance/index.html", "Compliance gate", "Disclosure, link and policy checks, with sources.", body)


def page_measurement():
    set_cur("measurement/index.html")
    rows = []
    for e in MEASURE["events"]:
        rows.append(
            [
                f"<code>{esc(e['name'])}</code>",
                esc(e["fires_when"]),
                esc(e["fields"]),
                pill(e["status"], "warn"),
                cite(e["source_ids"], e["name"]),
            ]
        )
    rules = "".join(f"<li>{esc(r)}</li>" for r in MEASURE["privacy_rules"])
    body = (
        '<section class="page-head"><p class="eyebrow">Dashboard</p><h1>Measurement</h1>'
        f'<p>{esc(MEASURE["status"])}</p></section>'
        '<section class="block"><h2>Events</h2>'
        + table(["Event", "Fires when", "Fields", "Status", "Sources"], rows)
        + "</section>"
        f'<section class="block"><h2>Privacy rules in the code</h2><ul class="plain">{rules}</ul></section>'
        '<section class="block"><h2>Endpoint</h2><p>None configured. Choose an option on the '
        f'<a href="{esc(L("suggestions/index.html"))}">Suggestions</a> page (S-02).</p></section>'
    )
    return layout("measurement/index.html", "Measurement", "Click and event measurement: defined events, status and privacy rules.", body)


def page_sources():
    set_cur("sources/index.html")
    rows = []
    for s in SOURCES.values():
        status = s["status"]
        rows.append(
            [
                esc(s["id"]),
                f'<a href="{esc(s["url"])}"{rel_for(s["url"])}>{esc(s["title"])}</a>{paid_tag(s["url"])}',
                esc(s["publisher"]),
                pill(status, "ok" if status == "fetched" else "warn"),
                esc(s["page_says"]),
                esc(s["supports"]),
            ]
        )
    fetched = sum(1 for s in SOURCES.values() if s["status"] == "fetched")
    body = (
        '<section class="page-head"><p class="eyebrow">Dashboard</p><h1>Source register</h1>'
        f"<p>{len(SOURCES)} sources. {fetched} were fetched and read during this session. "
        f"{len(SOURCES) - fetched} are not verified and are marked as such.</p></section>"
        + table(["ID", "Source", "Publisher", "Status", "What the page says", "Supports"], rows, filter_id="sources")
    )
    return layout("sources/index.html", "Source register", "Every source the site cites, with status and what it supports.", body)


def page_questions():
    set_cur("questions/index.html")
    rows = []
    for q in QUESTIONS:
        rows.append(
            [
                esc(q["id"]),
                esc(q["question"]),
                esc(q["known"]),
                pill(q["status"], status_kind(q["status"])),
                esc(q["discover_by"]),
                esc(q["suggestion"] or "—"),
                "Yes" if q["owner_action"] else "No",
                cite(q["source_ids"], q["id"]),
            ]
        )
    body = (
        '<section class="page-head"><p class="eyebrow">Dashboard</p><h1>Questions and gaps</h1>'
        "<p>What is needed before a decision can reasonably be made. For each question: what we know, "
        "its status, and how to find out. Where a choice is needed, it appears on the Suggestions page.</p></section>"
        + table(["ID", "Question", "What we know", "Status", "How to find out", "Suggestion", "Owner action", "Sources"], rows, filter_id="questions")
    )
    return layout("questions/index.html", "Questions and gaps", "Open questions, what is known, and how to find out.", body)


def page_suggestions():
    set_cur("suggestions/index.html")
    cards = []
    for s in SUGGESTIONS["suggestions"]:
        opts = table(
            ["Option", "Choice", "Trade-off"],
            [[f"<strong>{esc(o['id'])}</strong>", esc(o["label"]), esc(o["tradeoff"])] for o in s["options"]],
            kind="options",
        )
        cards.append(
            f'<article class="suggest" id="{esc(s["id"])}">'
            f'<p class="kicker">{esc(s["id"])} · {esc(s["topic"])}</p>'
            f'<h3>{esc(s["suggestion"])}</h3>'
            f'<p><strong>Evidence.</strong> {esc(s["evidence"])} {cite(s["source_ids"], s["id"])}</p>'
            + opts
            + f'<p><strong>Recommendation.</strong> {esc(s["recommendation"])}</p>'
            + f'<p>{pill(s["decision"], "warn")} <span class="meta">Not implemented.</span></p>'
            + "</article>"
        )
    body = (
        '<section class="page-head"><p class="eyebrow">Dashboard</p><h1>Suggestions</h1>'
        f'<p>{esc(SUGGESTIONS["how_to_choose"])}</p></section>'
        + "".join(cards)
    )
    return layout("suggestions/index.html", "Suggestions", "Options to choose from before anything changes.", body)


def page_flagged():
    set_cur("flagged-review/index.html")
    rows = []
    for f in FLAGS:
        rows.append(
            [
                f'<span id="{esc(f["id"])}"></span>' + esc(f["id"]),
                esc(f["type"]),
                pill(f["severity"], "warn" if f["severity"] == "High" else "neutral"),
                esc(f["item"]),
                esc(f["detail"]),
                esc(f["owner_action"]),
                cite(f["source_ids"], f["id"]),
                esc(f["status"]),
            ]
        )
    body = (
        '<section class="page-head"><p class="eyebrow">Review</p><h1>Flagged for Review</h1>'
        "<p>Irregularities, unverified values and blocked steps. Under the brief, these do not block the site. "
        "Each row names the owner action and cites its sources, so the owner can review them and ask for changes.</p></section>"
        + table(["ID", "Type", "Severity", "Item", "Detail", "Owner action", "Sources", "Status"], rows, filter_id="flags")
    )
    return layout("flagged-review/index.html", "Flagged for Review", "Irregularities, unverified items and blocked steps, with sources.", body)


def page_repo():
    set_cur("repo-review/index.html")
    rows = []
    for r in REPO:
        rows.append(
            [
                esc(r["id"]),
                esc(r["item"]),
                esc(r["finding"]),
                esc(r["flag"] or "—"),
                cite(r["source_ids"], r["id"]),
            ]
        )
    body = (
        '<section class="page-head"><p class="eyebrow">Review</p><h1>Repository review</h1>'
        "<p>The repository as read on the check date, line by line. Findings only; no files were changed to fix them in this review.</p></section>"
        + table(["ID", "Item", "Finding", "Flag", "Sources"], rows, filter_id="repo")
    )
    return layout("repo-review/index.html", "Repository review", "What the repository contains, its branches and its Pages settings.", body)


def page_exec():
    set_cur("executive-summary/index.html")
    n_src = len(SOURCES)
    n_fetched = sum(1 for s in SOURCES.values() if s["status"] == "fetched")
    n_flags = len(FLAGS)
    n_high = sum(1 for f in FLAGS if f["severity"] == "High")
    n_q = len(QUESTIONS)
    n_s = len(SUGGESTIONS["suggestions"])
    body = (
        '<section class="page-head"><p class="eyebrow">Summary</p><h1>Executive summary</h1>'
        f"<p>Status as of {esc(BUILD_DATE)}. Read this first.</p></section>"
        '<section class="block prose">'
        "<h2>What the site is</h2>"
        "<p>A static buyer-guide site with five supplied Amazon links, four short guides, category pages, "
        "and dashboards for sources, flags, questions and suggestions. It is built from the register files "
        "in this repository, and every table row cites an official source.</p>"
        "<h2>What we confirmed</h2><ul>"
        "<li>Four of the five supplied short links open to an Amazon product page. Each page's title, category and ASIN were read on the check date.</li>"
        "<li>Three are air fryers (P-01, P-02, P-03). One is a smart meat thermometer (P-05).</li>"
        "<li>The Associates Operating Agreement requires the sentence 'As an Amazon Associate I earn from qualifying purchases.' on the site. It appears under the masthead of every page and in the footer.</li>"
        "<li>The FTC asks that disclosures be hard to miss and placed with the recommendation. The site places them that way.</li>"
        "</ul>"
        "<h2>What we did not confirm</h2><ul>"
        "<li>The intended ASIN for any supplied link. Each supplied code is 9 characters; every observed Amazon URL used a 10-character code.</li>"
        "<li>The destination of P-04. Its short link returns a checkpoint page.</li>"
        "<li>Attribution to the selected tracking ID shopnow047c-20. The observed URLs carry no tag= parameter.</li>"
        "<li>Prices, ratings, availability and commission rates. The rate schedule redirected to sign-in.</li>"
        "</ul>"
        "<h2>What is blocked</h2><ul>"
        "<li>Validated Special Links (T-LINK). This needs an enrolled Associates login, which this session does not have.</li>"
        "<li>A measurement endpoint. GitHub Pages cannot run one, and the five events are not defined in the brief.</li>"
        "<li>Search Console. Verification needs the account holder.</li>"
        "</ul>"
        "<h2>What needs a decision</h2>"
        f"<p>{n_s} suggestions await a choice on the <a href=\"{esc(L('suggestions/index.html'))}\">Suggestions</a> page. "
        f"The most important is hosting: GitHub's limits describe a restriction on sites primarily directed at commercial transactions (FLG-R09).</p>"
        "<h2>Numbers</h2>"
        + table(
            ["Measure", "Value", "Where", "Sources"],
            [
                ["Supplied links", "5", '<a href="' + esc(L("products/index.html")) + '">Products</a>', cite(["SRC-12", "SRC-13", "SRC-14", "SRC-15", "SRC-16"], "exec supplied")],
                ["Intended ASINs confirmed", "0 of 5", '<a href="' + esc(L("intent/index.html")) + '">Intent record</a>', cite(["SRC-22", "SRC-12", "SRC-13", "SRC-14", "SRC-15"], "exec intent")],
                ["Observed product pages", "4 of 5", '<a href="' + esc(L("products/index.html")) + '">Products</a>', cite(["SRC-12", "SRC-13", "SRC-14", "SRC-15", "SRC-16"], "exec observed")],
                ["Prices verified", "0 of 5", '<a href="' + esc(L("products/index.html")) + '">Products</a>', cite(["SRC-12", "SRC-13", "SRC-14", "SRC-15"], "exec price")],
                ["Sources registered", f"{n_src} ({n_fetched} fetched)", '<a href="' + esc(L("sources/index.html")) + '">Sources</a>', cite(["SRC-17"], "exec sources")],
                ["Flagged items", f"{n_flags} ({n_high} high)", '<a href="' + esc(L("flagged-review/index.html")) + '">Flagged for Review</a>', cite(["SRC-17"], "exec flags")],
                ["Open questions", str(n_q), '<a href="' + esc(L("questions/index.html")) + '">Questions</a>', cite(["SRC-17"], "exec questions")],
                ["Campaign ledger rows", "0", '<a href="' + esc(L("ledger/index.html")) + '">Ledger</a>', cite(["SRC-01", "SRC-02"], "exec ledger")],
            ],
        )
        + "<h2>What the numbers do not say</h2>"
        "<p>There is no conversion rate, no revenue forecast and no commission estimate. None could be supported by an authorized report.</p>"
        "</section>"
    )
    return layout(
        "executive-summary/index.html",
        "Executive summary",
        "Executive summary: what the site is, what was confirmed, what is blocked, and what needs a decision.",
        body,
    )


def page_disclosure():
    set_cur("disclosure/index.html")
    body = (
        '<section class="page-head"><p class="eyebrow">Policy</p><h1>Disclosure</h1>'
        "<p>How this site earns money and how it labels that.</p></section>"
        '<section class="block prose">'
        "<h2>Associate statement</h2>"
        f"<p><strong>{esc(SITE['disclosure_strip'])}</strong></p>"
        "<p>This sentence is the wording required by Section 5 of the Associates Program Operating Agreement " + cite(["SRC-01"], "disclosure") + ". It appears under the masthead of every page and in the footer.</p>"
        "<h2>Sponsored links</h2>"
        "<p>Every link to Amazon on this site is marked as sponsored for search engines and labelled '(paid link)' "
        "beside the link. The Associates Help page gives '(paid link)' as an example of a clear link-level disclosure " + cite(["SRC-03"], "disclosure") + ".</p>"
        "<h2>What is not claimed</h2>"
        "<p>This site does not say Amazon supports, sponsors or endorses it, and does not show commission figures. "
        "Product statements are limited to what the listing says. Prices and ratings are not shown.</p>"
        "<h2>FTC</h2>"
        "<p>The FTC asks that a material connection be disclosed where it is hard to miss and placed with the recommendation " + cite(["SRC-05"], "disclosure") + ".</p>"
        "</section>"
    )
    return layout("disclosure/index.html", "Disclosure", "How this site labels affiliate links and what it does not claim.", body)


def page_404():
    global CUR
    CUR = "404.html"
    body = (
        '<section class="page-head"><h1>Page not found</h1>'
        f'<p>The page you asked for is not on this site. Start at <a href="{esc(L("index.html"))}">the front page</a>.</p></section>'
    )
    head = layout("404.html", "Page not found", "Page not found.", body)
    PAGES.remove(("404.html", BUILD_DATE))
    return head


# ------------------------------------------------------------- feeds and maps


def feed_xml():
    items = []
    for g in GUIDES:
        link = f"{BASE}/guides/{g['slug']}/"
        d = datetime.date.fromisoformat(g["published"])
        pub = email.utils.format_datetime(datetime.datetime(d.year, d.month, d.day, 0, 0, tzinfo=datetime.timezone.utc))
        items.append(
            "<item>"
            f"<title>{esc(g['title'])}</title>"
            f"<link>{esc(link)}</link>"
            f'<guid isPermaLink="true">{esc(link)}</guid>'
            f"<pubDate>{esc(pub)}</pubDate>"
            f"<description>{esc(g['dek'])}</description>"
            "</item>"
        )
    last = email.utils.format_datetime(datetime.datetime(BUILD_DT.year, BUILD_DT.month, BUILD_DT.day, tzinfo=datetime.timezone.utc))
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0"><channel>'
        f"<title>{esc(SITE['name'])} guides</title>"
        f"<link>{esc(BASE + '/guides/')}</link>"
        f"<description>{esc(SITE['tagline'])}</description>"
        "<language>en-us</language>"
        f"<lastBuildDate>{esc(last)}</lastBuildDate>"
        "<docs>https://www.rssboard.org/rss-specification</docs>"
        + "".join(items)
        + "</channel></rss>\n"
    )


def sitemap_xml():
    urls = []
    for path, lastmod in sorted(PAGES):
        if path == "404.html":
            continue
        loc = f"{BASE}/" + (path[: -len("index.html")] if path.endswith("index.html") else path)
        urls.append(f"<url><loc>{esc(loc)}</loc><lastmod>{esc(lastmod)}</lastmod></url>")
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>\n"
    )


# ------------------------------------------------------------------- main


def main():
    validate_sources()
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    with open(os.path.join(OUT, ".nojekyll"), "w") as fh:
        fh.write("")

    # Assets
    os.makedirs(os.path.join(OUT, "assets"), exist_ok=True)
    shutil.copy(os.path.join(ROOT, "scripts", "assets", "site.css"), os.path.join(OUT, "assets", "site.css"))
    shutil.copy(os.path.join(ROOT, "scripts", "assets", "site.js"), os.path.join(OUT, "assets", "site.js"))
    shutil.copy(os.path.join(ROOT, "scripts", "assets", "measure.js"), os.path.join(OUT, "assets", "measure.js"))

    write("index.html", page_home())
    write("products/index.html", page_products())
    for p in PRODUCTS:
        write(f"products/{p['page_slug']}/index.html", page_product(p))
    write("categories/index.html", page_categories())
    write("categories/air-fryers/index.html", page_category("air-fryers", "Air fryers", "Three air fryers from the supplied links, with observed titles and breadcrumbs."))
    write("categories/meat-thermometers/index.html", page_category("meat-thermometers", "Meat thermometers", "One smart meat thermometer from the supplied links."))
    write("categories/unresolved/index.html", page_category("unresolved", "Unresolved", "The supplied link that did not resolve to a product."))
    write("guides/index.html", page_guides_index())
    for g in GUIDES:
        write(f"guides/{g['slug']}/index.html", page_guide(g))
    write("intent/index.html", page_intent())
    write("ledger/index.html", page_ledger())
    write("compliance/index.html", page_compliance())
    write("measurement/index.html", page_measurement())
    write("sources/index.html", page_sources())
    write("questions/index.html", page_questions())
    write("suggestions/index.html", page_suggestions())
    write("flagged-review/index.html", page_flagged())
    write("repo-review/index.html", page_repo())
    write("executive-summary/index.html", page_exec())
    write("disclosure/index.html", page_disclosure())
    write("404.html", page_404())

    write("feed.xml", feed_xml())
    write("sitemap.xml", sitemap_xml())
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n")

    if ERRORS:
        print("BUILD FAILED:")
        for e in ERRORS:
            print(" -", e)
        sys.exit(1)
    print(f"built {len(PAGES) + 1} pages into docs/ ({len(GUIDES)} guides, {len(PRODUCTS)} products)")


if __name__ == "__main__":
    main()
