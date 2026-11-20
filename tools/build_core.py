#!/usr/bin/env python3
"""The Crisp Index — build core: data loading, shared chrome, sitemap/feed/robots.

Stdlib-only. Deterministic output into docs/ (GitHub Pages source).
"""
import html
import json
import os
import posixpath
import re
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "crisp-index")
DATA = os.path.join(ROOT, "data", "93cee724")

BUILD_TS = "2026-11-20T09:00:00Z"
FEED_DATE = "Thu, 20 Nov 2026 09:00:00 GMT"


def load_data():
    def load(name):
        with open(os.path.join(DATA, name), encoding="utf-8") as f:
            return json.load(f)

    return {
        "site": load("site.json"),
        "products": load("products.json"),
        "flags": load("flags.json"),
        "questions": load("questions.json"),
        "suggestions": load("suggestions.json"),
        "ledger": load("ledger.json"),
        "sources": load("sources.json"),
    }


def esc(s):
    return html.escape(str(s), quote=True)


class Ctx:
    def __init__(self, data):
        self.d = data
        self.site = data["site"]
        self.current = "index.html"
        self.sources_by_id = {s["id"]: s for s in data["sources"]["sources"]}
        self.flags_by_id = {f["id"]: f for f in data["flags"]["flags"]}
        self.products_by_id = {p["id"]: p for p in data["products"]["products"]}

    # ---- paths -------------------------------------------------------
    def rel(self, target):
        """Deferred relative href: body HTML is built before the page path is
        known, so emit a placeholder and resolve it in shell()."""
        return f"\x00REL:{target}\x00"

    def abs(self, target):
        return self.site["base_url"] + target

    # ---- components --------------------------------------------------
    def chip(self, text, cls="chip-neutral"):
        return f'<span class="chip {cls}">{esc(text)}</span>'

    def src(self, sid, label=None):
        s = self.sources_by_id.get(sid)
        if not s:
            return f'<span class="unverified">missing source {esc(sid)}</span>'
        title = f'{s["title"]} — {s["org"]}, accessed {s["accessed"]}'
        href = s["url"]
        # Citations that land on product pages are still product links: keep the
        # full sponsored rel set there too.
        if "amazon.com/dp/" in href or "link.amazon/" in href:
            rel = "sponsored nofollow noopener"
            tci = ' data-tci="outbound"'
        else:
            rel = "noopener"
            tci = ""
        return (
            f'<a class="src" href="{esc(href)}" rel="{rel}"{tci} target="_blank" '
            f'title="{esc(title)}">{esc(label or sid)}</a>'
        )

    def srcs(self, ids):
        return " ".join(self.src(i) for i in ids)

    def flag(self, fid, label=None):
        return (
            f'<a class="chip chip-flag" href="{esc(self.rel("workshop/flagged.html"))}#{esc(fid)}" '
            f'title="Open the Flagged for Review register">{esc(label or fid)}</a>'
        )

    def sponsored_cta(self, product, label=None, extra_cls=""):
        """Outbound product link: rel=sponsored, visible Sponsored chip, analytics hook."""
        p = product
        label = label or "Check today’s price on Amazon"
        return (
            f'<a class="btn {extra_cls}" href="{esc(p["site_outbound_url"])}" '
            f'rel="sponsored nofollow noopener" target="_blank" '
            f'data-tci="outbound" data-product="{esc(p["id"])}">'
            f'{esc(label)} <span class="chip chip-sponsored">Sponsored</span></a>'
        )

    def blank_unverified(self, flag_id="FLG-010"):
        return f'<span class="unverified">— unverified</span> {self.flag(flag_id)}'

    def external(self, url, label):
        if "amazon.com/dp/" in url or "link.amazon/" in url:
            rel, tci = "sponsored nofollow noopener", ' data-tci="outbound"'
        else:
            rel, tci = "noopener", ""
        return f'<a href="{esc(url)}" rel="{rel}"{tci} target="_blank">{esc(label)}</a>'


def breadcrumb_html(ctx, trail):
    """trail: list of (label, site-path or None)."""
    parts = [f'<a href="{esc(ctx.rel("index.html"))}">Home</a>']
    for label, path in trail:
        parts.append('<span class="sep">/</span>')
        if path:
            parts.append(f'<a href="{esc(ctx.rel(path))}">{esc(label)}</a>')
        else:
            parts.append(f"<span>{esc(label)}</span>")
    return f'<nav class="breadcrumb" aria-label="Breadcrumb">{"".join(parts)}</nav>'


def disclosure_strip(ctx):
    stmt = ctx.site["exact_associates_statement"]
    return (
        '<div class="disclosure-strip" role="note" aria-label="Affiliate disclosure">'
        f"<p><strong>{esc(stmt)}</strong> "
        "Links marked "
        f'<span class="chip chip-sponsored">Sponsored</span> are affiliate links — '
        "the price you pay never changes. "
        f'<a href="{esc(ctx.rel("disclosure/index.html"))}">Full disclosure</a></p></div>'
    )


def masthead_html(ctx):
    links = []
    for item in ctx.site["nav"]:
        current = ""
        if ctx.current == item["path"] or (
            item["path"] != "index.html" and ctx.current.startswith(posixpath.dirname(item["path"]) + "/")
        ):
            current = ' aria-current="page"'
        links.append(
            f'<a href="{esc(ctx.rel(item["path"]))}"{current}>{esc(item["label"])}</a>'
        )
    return (
        '<header class="masthead"><div class="masthead-inner">'
        f'<a class="brand" href="{esc(ctx.rel("index.html"))}">'
        '<span class="brand-mark">The <em>Crisp</em> Index</span>'
        f'<span class="brand-tag">{esc(ctx.site["tagline"])}</span></a>'
        '<button class="nav-toggle" aria-expanded="false" aria-controls="main-nav">Menu</button>'
        f'<nav class="main-nav" id="main-nav" aria-label="Primary">{"".join(links)}</nav>'
        "</div></header>"
    )


def footer_html(ctx):
    shop_links = [
        ("Buyer’s guides", "guides/index.html"),
        ("Compare air fryer shapes", "compare/index.html"),
        ("The Test Queue", "products/index.html"),
        ("Holiday hosting 2026", "guides/holiday-hosting-countertop.html"),
        ("RSS feed", "feed.xml"),
    ]
    shop = "".join(
        f'<li><a href="{esc(ctx.rel(p))}">{esc(l)}</a></li>' for l, p in shop_links
    )
    workshop = "".join(
        f'<li><a href="{esc(ctx.rel(item["path"]))}">{esc(item["label"])}</a></li>'
        for item in ctx.site["footer_workshop"]
    )
    stmt = ctx.site["exact_associates_statement"]
    return f"""<footer class="site-footer"><div class="wrap">
  <div class="footer-grid">
    <div class="footer-brand">
      <span class="brand-mark">The <em>Crisp</em> Index</span>
      <p>{esc(ctx.site["mission"])}</p>
      <p><a href="{esc(ctx.rel('disclosure/index.html'))}">Disclosure &amp; affiliate policy</a> ·
         <a href="{esc(ctx.rel('about/index.html'))}#corrections">Corrections</a></p>
    </div>
    <div>
      <h4>Shop &amp; read</h4>
      <ul>{shop}</ul>
    </div>
    <div>
      <h4>The Workshop</h4>
      <ul>{workshop}</ul>
    </div>
  </div>
  <div class="footer-disclosure">
    <p><strong>{esc(stmt)}</strong> Disclosure repeated in full on every page and under every
    product link, per the Amazon Associates Operating Agreement
    (<a href="https://affiliate-program.amazon.com/help/operating/agreement" rel="noopener" target="_blank">S-01</a>)
    and FTC guidance
    (<a href="https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers" rel="noopener" target="_blank">S-04</a>).
    Product facts come from the linked listings; anything we could not confirm from an official
    source is left blank and flagged on the <a href="{esc(ctx.rel('workshop/flagged.html'))}">Flagged for Review</a> page.</p>
  </div>
  <div class="footer-bottom">
    <span>© 2026 The Crisp Index</span>
    <span>Published from San Francisco, California</span>
    <span>Tracking ID {esc(ctx.site['tracking_id'])}</span>
    <span>Site build {esc(ctx.site['build_date'])}</span>
    <a href="{esc(ctx.rel('sitemap.xml'))}">Sitemap</a>
  </div>
</div></footer>"""


def resolve_rel_placeholders(html_text, page_path):
    cur_dir = posixpath.dirname(page_path) or "."

    def _sub(m):
        return posixpath.relpath(m.group(1), cur_dir)

    return re.sub(r"\x00REL:([^\x00]+)\x00", _sub, html_text)


def shell(ctx, page):
    ctx.current = page["path"]
    body = page["body"](ctx) if callable(page["body"]) else page["body"]
    jsonld = ""
    for obj in page.get("jsonld", []):
        jsonld += (
            '<script type="application/ld+json">'
            + json.dumps(obj, ensure_ascii=False)
            + "</script>\n"
        )
    og_image = page.get("og_image")
    og_tags = ""
    if og_image:
        og_tags = (
            f'<meta property="og:image" content="{esc(ctx.abs(og_image))}">\n'
            f'<meta name="twitter:image" content="{esc(ctx.abs(og_image))}">\n'
        )
    title = f'{page["title"]} · {ctx.site["brand"]}'
    crumbs = page.get("breadcrumb")
    crumb_html = breadcrumb_html(ctx, crumbs) if crumbs else ""
    robots = '<meta name="robots" content="noindex">\n' if page.get("noindex") else ""
    return resolve_rel_placeholders(f"""<!DOCTYPE html>
<html lang="{esc(ctx.site['locale'])}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(page['description'])}">
<link rel="canonical" href="{esc(ctx.abs(page['path']))}">
<link rel="alternate" type="application/rss+xml" title="{esc(ctx.site['brand'])} feed" href="{esc(ctx.abs('feed.xml'))}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(page['description'])}">
<meta property="og:url" content="{esc(ctx.abs(page['path']))}">
<meta property="og:type" content="{esc(page.get('og_type', 'website'))}">
<meta property="og:site_name" content="{esc(ctx.site['brand'])}">
<meta name="twitter:card" content="summary_large_image">
{og_tags}{robots}{jsonld}<link rel="stylesheet" href="{esc(ctx.rel('assets/css/site.css'))}">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
{masthead_html(ctx)}
{disclosure_strip(ctx)}
<main id="main">
{crumb_html}
{body}
</main>
{footer_html(ctx)}
<script src="{esc(ctx.rel('site-config.js'))}"></script>
<script src="{esc(ctx.rel('assets/js/analytics.js'))}"></script>
<script src="{esc(ctx.rel('assets/js/site.js'))}"></script>
</body>
</html>
""", page["path"])


def feed_xml(ctx, feed_items):
    items = []
    for it in feed_items:
        items.append(f"""    <item>
      <title>{esc(it['title'])}</title>
      <link>{esc(ctx.abs(it['path']))}</link>
      <guid isPermaLink="true">{esc(ctx.abs(it['path']))}</guid>
      <pubDate>{FEED_DATE}</pubDate>
      <description>{esc(it['description'])}</description>
      <category>{esc(it.get('category', 'Guides'))}</category>
    </item>""")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{esc(ctx.site['brand'])}</title>
    <link>{esc(ctx.site['base_url'])}</link>
    <atom:link href="{esc(ctx.abs('feed.xml'))}" rel="self" type="application/rss+xml"/>
    <description>{esc(ctx.site['mission'])}</description>
    <language>en-us</language>
    <lastBuildDate>{FEED_DATE}</lastBuildDate>
{chr(10).join(items)}
  </channel>
</rss>
"""


def sitemap_xml(ctx, sitemap_pages):
    urls = []
    for p in sitemap_pages:
        urls.append(f"""  <url>
    <loc>{esc(ctx.abs(p['path']))}</loc>
    <lastmod>2026-11-20</lastmod>
    <changefreq>{esc(p['changefreq'])}</changefreq>
    <priority>{p['priority']}</priority>
  </url>""")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls)}
</urlset>
"""


ROBOTS_TXT = f"""User-agent: *
Allow: /

Sitemap: https://karagemop466-tech.github.io/Affil3/sitemap.xml
"""

NOTFOUND_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Page not found · The Crisp Index</title>
<meta name="description" content="This page is not on the menu — back to The Crisp Index front page and the buyer's guides.">
<meta name="robots" content="noindex">
<link rel="stylesheet" href="assets/css/site.css">
</head>
<body>
<header class="masthead"><div class="masthead-inner">
<a class="brand" href="index.html"><span class="brand-mark">The <em>Crisp</em> Index</span>
<span class="brand-tag">Straight answers for the countertop kitchen</span></a>
</div></header>
<div class="disclosure-strip"><p><strong>As an Amazon Associate I earn from qualifying purchases.</strong>
Links marked Sponsored are affiliate links — the price you pay never changes.
<a href="disclosure/index.html">Full disclosure</a></p></div>
<main id="main" class="wrap center-page">
<p class="eyebrow">404</p>
<h1>This page went cold.</h1>
<p class="lede" style="margin:0 auto">The link you followed is not on the menu. Try the front page,
or head straight for the buyer’s guides.</p>
<p class="hero-actions" style="justify-content:center">
<a class="btn" href="index.html">Back to the front page</a>
<a class="btn btn-ghost" href="guides/index.html">Browse buyer’s guides</a>
</p>
</main>
<footer class="site-footer"><div class="wrap"><div class="footer-disclosure">
<p><strong>As an Amazon Associate I earn from qualifying purchases.</strong></p>
</div></div></footer>
</body>
</html>
"""


def write_docs(relpath, text):
    full = os.path.join(DOCS, relpath)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(text)


def build():
    data = load_data()
    ctx = Ctx(data)

    import content_public
    import content_workshop

    pages = content_public.pages(ctx) + content_workshop.pages(ctx)

    feed_items, sitemap_pages = [], []
    for page in pages:
        write_docs(page["path"], shell(ctx, page))
        if page.get("feed"):
            feed_items.append({"path": page["path"], **page["feed"]})
        sm = page.get("sitemap")
        if sm:
            sitemap_pages.append({"path": page["path"], **sm})

    write_docs("feed.xml", feed_xml(ctx, feed_items))
    write_docs("sitemap.xml", sitemap_xml(ctx, sitemap_pages))
    write_docs("robots.txt", ROBOTS_TXT)
    write_docs("404.html", NOTFOUND_HTML)
    write_docs(".nojekyll", "")

    print(f"built {len(pages)} pages -> docs/")
    print(f"feed items: {len(feed_items)}, sitemap urls: {len(sitemap_pages)}")


if __name__ == "__main__":
    build()
