"""
sitekit — shared helpers for building the Counter & Crumb static site.

Standard library only. No third-party dependencies, so the build runs anywhere
Python 3.9+ is available and nothing has to be installed to reproduce the site.
"""

from __future__ import annotations

import html
import json
import os
import re
from datetime import date, datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

# --------------------------------------------------------------------------
# small helpers
# --------------------------------------------------------------------------

def esc(value) -> str:
    """Escape a value for use in HTML text or a double-quoted attribute."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return html.escape(str(value), quote=True)


def load_json(name: str):
    with open(os.path.join(DATA, name), "r", encoding="utf-8") as fh:
        return json.load(fh)


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def write_text(rel_path: str, content: str) -> None:
    full = os.path.join(ROOT, rel_path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as fh:
        fh.write(content)


def slugify(text: str) -> str:
    out = re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-")
    return out or "item"


def today() -> str:
    return date.today().isoformat()


def rfc822(iso_date: str) -> str:
    try:
        d = datetime.strptime(iso_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError:
        d = datetime.now(timezone.utc)
    return d.strftime("%a, %d %b %Y %H:%M:%S +0000")


# --------------------------------------------------------------------------
# affiliate link construction
# --------------------------------------------------------------------------

ASIN_RE = re.compile(r"^[A-Z0-9]{10}$")


def is_asin(value: str) -> bool:
    """Amazon defines an ASIN as a 10-character alphanumeric identifier.

    Source: https://affiliate-program.amazon.com/creatorsapi/docs/en-us/api-reference/operations/get-items
    """
    return bool(value) and bool(ASIN_RE.match(str(value).strip().upper()))


def special_link(asin: str, tag: str, marketplace: str = "www.amazon.com") -> str:
    """Build a direct Special Link.

    Parameter shape matches what the Creators API itself returns for
    detailPageURL, so the link format is Amazon's own rather than ours.

    Source: https://affiliate-program.amazon.com/creatorsapi/docs/en-us/get-started/using-curl
    """
    return (
        f"https://{marketplace}/dp/{asin}"
        f"?tag={tag}&linkCode=ogi&th=1&psc=1&language=en_US"
    )


def sponsored_anchor(url: str, label: str, product_id: str = "", asin: str = "",
                     placement: str = "body", title: str = "") -> str:
    """Render an outbound affiliate link, marked as sponsored in three ways.

    1. rel="sponsored nofollow"  — Google's guidance for paid placements.
    2. A visible "Sponsored" marker next to the label.
    3. An aria-label naming the destination.

    Source: https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links
    """
    aria = title or label
    bits = [
        f'<a class="spon" href="{esc(url)}" rel="sponsored nofollow" target="_blank"',
        'data-sponsored="1"',
    ]
    if product_id:
        bits.append(f'data-product="{esc(product_id)}"')
    if asin:
        bits.append(f'data-asin="{esc(asin)}"')
    bits.append(f'data-placement="{esc(placement)}"')
    bits.append(f'aria-label="Sponsored link to Amazon: {esc(aria)}"')
    bits.append(">")
    bits.append(f"<span>{esc(label)}</span>")
    bits.append('<span class="spon__mark">Sponsored</span>')
    bits.append("</a>")
    return " ".join(bits)


PRODUCT_URL_RE = re.compile(
    r"^https?://(?:www\.)?amazon\.com/dp/([A-Z0-9]{10})(?:[/?#].*)?$", re.I)

_CONFIG_CACHE = {}


def _tag() -> str:
    if "tag" not in _CONFIG_CACHE:
        with open(os.path.join(DATA, "config.json"), "r", encoding="utf-8") as fh:
            _CONFIG_CACHE["tag"] = json.load(fh)["affiliate"]["tracking_id"]
        _CONFIG_CACHE["marketplace"] = json.load(
            open(os.path.join(DATA, "config.json"), "r", encoding="utf-8"))["affiliate"]["marketplace"]
    return _CONFIG_CACHE["tag"]


def source_link(url: str, label: str = "Official listing", product_id: str = "",
                asin: str = "") -> str:
    """A citation link to an official source.

    A link to an Amazon shopping page becomes a tagged Special Link, marked as
    sponsored, because Amazon requires the Associates tag on links to an Amazon
    Site and because a link that can earn a commission has to read as one.

    A link to Amazon's own program documentation stays a plain reference: it
    cannot earn a commission and marking it sponsored would misdescribe it.
    """
    m = PRODUCT_URL_RE.match(url)
    if m:
        target_asin = asin or m.group(1).upper()
        tagged = special_link(target_asin, _tag(), _CONFIG_CACHE.get("marketplace", "www.amazon.com"))
        return sponsored_anchor(tagged, label, product_id or target_asin, target_asin,
                                "source", label)
    return (
        f'<a href="{esc(url)}" rel="noopener" target="_blank" '
        f'aria-label="Source: {esc(label)}">{esc(label)}</a>'
    )


# --------------------------------------------------------------------------
# SVG illustrations (drawn here, not copied from any product photograph)
# --------------------------------------------------------------------------

_SVG_STROKE = "#b23c12"
_SVG_FILL = "#fdeee6"
_SVG_LINE = "#191512"


def illustration(product: dict) -> str:
    """Return the inline SVG for a product card.

    These are original line illustrations drawn for this site. They are not
    product photographs and they are not derived from any manufacturer image.
    """
    form = (product.get("form") or "").lower()
    if "dual" in form:
        return _svg_dual_basket()
    if "oven" in form and "french" in form:
        return _svg_french_door()
    if "wireless" in form or "multi-probe" in form:
        return _svg_smart_probe()
    if "probe" in form:
        return _svg_probe()
    if "basket" in form:
        return _svg_basket()
    return _svg_basket()


def _svg_wrap(inner: str) -> str:
    return (
        '<svg viewBox="0 0 160 100" role="img" aria-label="Line illustration" '
        'fill="none" xmlns="http://www.w3.org/2000/svg">'
        + inner
        + "</svg>"
    )


def _svg_basket() -> str:
    return _svg_wrap(
        f'<rect x="30" y="22" width="100" height="58" rx="9" fill="{_SVG_FILL}" stroke="{_SVG_LINE}" stroke-width="2"/>'
        f'<path d="M38 34h84v34a6 6 0 0 1-6 6H44a6 6 0 0 1-6-6z" fill="#fff" stroke="{_SVG_STROKE}" stroke-width="2"/>'
        f'<path d="M56 46h48M56 56h48M56 66h30" stroke="{_SVG_STROKE}" stroke-width="1.6" stroke-linecap="round"/>'
        f'<rect x="52" y="76" width="56" height="8" rx="4" fill="{_SVG_FILL}" stroke="{_SVG_LINE}" stroke-width="1.6"/>'
        f'<circle cx="118" cy="29" r="4.5" fill="#fff" stroke="{_SVG_LINE}" stroke-width="1.6"/>'
    )


def _svg_dual_basket() -> str:
    return _svg_wrap(
        f'<rect x="24" y="24" width="112" height="54" rx="9" fill="{_SVG_FILL}" stroke="{_SVG_LINE}" stroke-width="2"/>'
        f'<rect x="34" y="36" width="42" height="32" rx="6" fill="#fff" stroke="{_SVG_STROKE}" stroke-width="2"/>'
        f'<rect x="84" y="36" width="42" height="32" rx="6" fill="#fff" stroke="{_SVG_STROKE}" stroke-width="2"/>'
        f'<path d="M42 46h26M42 55h26M92 46h26M92 55h26" stroke="{_SVG_STROKE}" stroke-width="1.5" stroke-linecap="round"/>'
        f'<rect x="52" y="74" width="56" height="8" rx="4" fill="#fff" stroke="{_SVG_LINE}" stroke-width="1.6"/>'
        f'<circle cx="118" cy="30" r="4.5" fill="#fff" stroke="{_SVG_LINE}" stroke-width="1.6"/>'
    )


def _svg_french_door() -> str:
    return _svg_wrap(
        f'<rect x="34" y="14" width="92" height="72" rx="7" fill="{_SVG_FILL}" stroke="{_SVG_LINE}" stroke-width="2"/>'
        f'<path d="M80 14v72" stroke="{_SVG_LINE}" stroke-width="2"/>'
        f'<path d="M74 14v72" stroke="{_SVG_STROKE}" stroke-width="1.4" stroke-dasharray="3 3"/>'
        f'<path d="M42 26h30v44H42zM88 26h30v44H88z" fill="#fff" stroke="{_SVG_STROKE}" stroke-width="1.6"/>'
        f'<path d="M50 44h14M96 44h14" stroke="{_SVG_STROKE}" stroke-width="1.5" stroke-linecap="round"/>'
        f'<rect x="52" y="82" width="56" height="7" rx="3.5" fill="#fff" stroke="{_SVG_LINE}" stroke-width="1.6"/>'
        f'<circle cx="46" cy="19" r="3.4" fill="#fff" stroke="{_SVG_LINE}" stroke-width="1.4"/>'
        f'<circle cx="114" cy="19" r="3.4" fill="#fff" stroke="{_SVG_LINE}" stroke-width="1.4"/>'
    )


def _svg_probe() -> str:
    return _svg_wrap(
        f'<rect x="26" y="34" width="62" height="34" rx="7" fill="#fff" stroke="{_SVG_LINE}" stroke-width="2"/>'
        f'<rect x="36" y="43" width="42" height="16" rx="3" fill="{_SVG_FILL}" stroke="{_SVG_STROKE}" stroke-width="1.6"/>'
        f'<path d="M40 51h34" stroke="{_SVG_STROKE}" stroke-width="1.4" stroke-linecap="round"/>'
        f'<path d="M88 51h18l22 6" stroke="{_SVG_LINE}" stroke-width="2.4" stroke-linecap="round"/>'
        f'<path d="M128 57l6 6-10 8" stroke="{_SVG_STROKE}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
        f'<circle cx="106" cy="51" r="3.2" fill="{_SVG_STROKE}"/>'
    )


def _svg_smart_probe() -> str:
    return _svg_wrap(
        f'<rect x="18" y="52" width="40" height="26" rx="7" fill="{_SVG_FILL}" stroke="{_SVG_LINE}" stroke-width="2"/>'
        f'<rect x="26" y="60" width="24" height="10" rx="2.5" fill="#fff" stroke="{_SVG_STROKE}" stroke-width="1.4"/>'
        f'<path d="M58 58c14-16 30-22 46-18" stroke="{_SVG_LINE}" stroke-width="1.8" stroke-linecap="round"/>'
        f'<path d="M58 68c12-12 24-16 36-14" stroke="{_SVG_LINE}" stroke-width="1.8" stroke-linecap="round"/>'
        f'<circle cx="112" cy="36" r="5" fill="#fff" stroke="{_SVG_STROKE}" stroke-width="2"/>'
        f'<circle cx="100" cy="48" r="4" fill="#fff" stroke="{_SVG_STROKE}" stroke-width="1.8"/>'
        f'<path d="M106 33l14-8M100 45l12-7" stroke="{_SVG_STROKE}" stroke-width="1.4" stroke-linecap="round" stroke-dasharray="2 3"/>'
    )


# --------------------------------------------------------------------------
# layout
# --------------------------------------------------------------------------

PRIMARY_NAV = [
    ("/", "Home"),
    ("/guides/", "Guides"),
    ("/products/", "Products"),
    ("/compare/", "Compare"),
]

FOOTER_NAV = [
    ("Read", [
        ("/guides/", "All guides"),
        ("/compare/", "Comparisons"),
        ("/categories/air-fryers/", "Air fryers"),
        ("/categories/thermometers/", "Meat thermometers"),
    ]),
    ("The desk", [
        ("/desk/", "Open questions"),
        ("/desk/suggestions/", "Suggestions"),
        ("/desk/flags/", "Flagged for review"),
        ("/executive-summary/", "Executive summary"),
    ]),
    ("The method", [
        ("/methods/sources/", "Source register"),
        ("/methods/verification/", "How we verify"),
        ("/compliance/", "Compliance"),
        ("/measurement/", "Measurement"),
        ("/ledger/", "Campaign ledger"),
    ]),
    ("About", [
        ("/about/", "About this desk"),
        ("/about/#editorial-standards", "Editorial standards"),
    ]),
]


def head_block(cfg: dict, title: str, description: str, path: str,
               page_type: str = "website", jsonld=None, extra_head: str = "") -> str:
    site = cfg["site"]
    base = site["base_url"].rstrip("/")
    canonical = base + path
    og = base + site["social"]["og_image"]
    parts = [
        "<!doctype html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f'<title>{esc(title)}</title>',
        f'<meta name="description" content="{esc(description)}">',
        f'<link rel="canonical" href="{esc(canonical)}">',
        '<meta name="robots" content="index, follow, max-image-preview:large">',
        f'<meta property="og:type" content="{esc(page_type)}">',
        f'<meta property="og:site_name" content="{esc(site["name"])}">',
        f'<meta property="og:title" content="{esc(title)}">',
        f'<meta property="og:description" content="{esc(description)}">',
        f'<meta property="og:url" content="{esc(canonical)}">',
        f'<meta property="og:image" content="{esc(og)}">',
        f'<meta property="og:locale" content="{esc(site["locale"])}">',
        f'<meta name="twitter:card" content="{esc(site["social"]["twitter_card"])}">',
        f'<meta name="twitter:title" content="{esc(title)}">',
        f'<meta name="twitter:description" content="{esc(description)}">',
        f'<meta name="twitter:image" content="{esc(og)}">',
        '<meta name="author" content="Counter &amp; Crumb desk">',
        '<link rel="alternate" type="application/rss+xml" title="Counter &amp; Crumb" href="/feed.xml">',
        '<link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml">',
        '<link rel="stylesheet" href="/assets/css/site.css">',
    ]
    if jsonld:
        parts.append('<script type="application/ld+json">' +
                     json.dumps(jsonld, indent=2, ensure_ascii=False) +
                     "</script>")
    if extra_head:
        parts.append(extra_head)
    parts.append("</head>")
    return "\n".join(parts)


def masthead(cfg: dict, current: str) -> str:
    site = cfg["site"]
    nav = []
    for href, label in PRIMARY_NAV:
        aria = ' aria-current="page"' if href == current else ""
        nav.append(f'<a href="{esc(href)}"{aria}>{esc(label)}</a>')
    return f"""
<header class="masthead">
  <div class="wrap masthead__inner">
    <a class="brand" href="/">
      <svg class="brand__mark" viewBox="0 0 40 40" role="img" aria-label="Counter and Crumb" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="1.5" y="1.5" width="37" height="37" rx="10" fill="#b23c12"/>
        <path d="M13 25c0-4.4 3.1-8 7-8s7 3.6 7 8" stroke="#fdeee6" stroke-width="2.4" stroke-linecap="round"/>
        <path d="M11 27.5h18" stroke="#fdeee6" stroke-width="2.4" stroke-linecap="round"/>
        <path d="M16 17.5c0-2 1.8-3.6 4-3.6s4 1.6 4 3.6" stroke="#fdeee6" stroke-width="2.2" stroke-linecap="round"/>
      </svg>
      <span class="brand__text">
        <span class="brand__name">Counter &amp; Crumb</span>
        <span class="brand__tag">A buyer's desk</span>
      </span>
    </a>
    <nav class="nav" aria-label="Primary">
      {''.join(nav)}
    </nav>
  </div>
</header>"""


def disclosure_strip(cfg: dict) -> str:
    d = cfg["affiliate"]["disclosure"]
    return f"""
<div class="disclosure" role="note" aria-label="Affiliate disclosure">
  <div class="wrap">
    <p><span class="disclosure__label">Disclosure</span>{esc(d["strip"])}</p>
  </div>
</div>"""


def footer(cfg: dict) -> str:
    site = cfg["site"]
    d = cfg["affiliate"]["disclosure"]
    cols = []
    for title, links in FOOTER_NAV:
        items = "".join(f'<li><a href="{esc(h)}">{esc(t)}</a></li>' for h, t in links)
        cols.append(f'<div><h2>{esc(title)}</h2><ul>{items}</ul></div>')
    return f"""
<footer class="footer">
  <div class="wrap">
    <div class="footer__grid">{''.join(cols)}</div>
    <div class="footer__bottom">
      <p class="footer__disclosure"><strong>{esc(d["operating_agreement_sentence"])}</strong> {esc(d["strip"])}</p>
      <p>© <span data-year>2026</span> {esc(site["publisher"])} · <a href="/feed.xml">RSS</a> · <a href="/sitemap.xml">Sitemap</a> · <a href="/methods/sources/">Sources</a></p>
    </div>
  </div>
</footer>
<button class="to-top" data-to-top type="button" aria-label="Back to top">↑</button>"""


def signup_form(placement: str = "footer") -> str:
    return f"""
<form class="signup" data-signup="{esc(placement)}" novalidate>
  <label class="visually-hidden" for="signup-email-{esc(placement)}">Email address</label>
  <input id="signup-email-{esc(placement)}" type="email" name="email" placeholder="you@example.com" autocomplete="email" required>
  <button class="btn btn--sm" type="submit">Keep me posted</button>
</form>
<p class="signup__note" data-signup-note>One short note when a new guide goes up. No more than that.</p>"""


def layout(cfg: dict, title: str, description: str, path: str, body: str,
           current: str = "", jsonld=None, extra_head: str = "",
           page_type: str = "website") -> str:
    head = head_block(cfg, title, description, path, page_type, jsonld, extra_head)
    extra = f'<script src="/assets/js/site-config.js" defer></script>\n<script src="/assets/js/analytics.js" defer></script>\n<script src="/assets/js/site.js" defer></script>'
    return (
        head
        + "\n"
        + masthead(cfg, current)
        + "\n"
        + disclosure_strip(cfg)
        + "\n<main id=\"main\">\n"
        + body
        + "\n</main>\n"
        + footer(cfg)
        + "\n"
        + extra
        + "\n</body>\n</html>\n"
    )


# --------------------------------------------------------------------------
# small building blocks used by several pages
# --------------------------------------------------------------------------

def breadcrumb(cfg: dict, trail):
    """trail: list of (label, href_or_None)"""
    base = cfg["site"]["base_url"].rstrip("/")
    items = []
    for index, (label, href) in enumerate(trail):
        if index:
            items.append('<span aria-hidden="true">/</span>')
        if href:
            items.append(f'<a href="{esc(href)}">{esc(label)}</a>')
        else:
            items.append(f"<span>{esc(label)}</span>")
    schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": label,
             "item": base + href if href else None}
            for i, (label, href) in enumerate(trail)
        ],
    }
    schema["itemListElement"] = [e for e in schema["itemListElement"] if e["item"]]
    return (
        '<nav class="breadcrumb-nav" aria-label="Breadcrumb">'
        + "".join(items)
        + "</nav>"
    ), schema


def breadcrumb_jsonld(trail, base: str):
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": label,
             "item": base + href}
            for i, (label, href) in enumerate(trail) if href
        ],
    }


def price_slot(asin: str) -> str:
    """A price cell that stays blank until the API can fill it.

    Amazon Program Policies 2(b): a Site may only show prices if Amazon serves the
    link that displays them, or if pricing is obtained through Creators API or
    PA API. Until one of those is true, this renders as an explicit placeholder
    rather than a number.
    """
    return (
        f'<span class="price-slot" data-price-slot="{esc(asin)}" data-state="unavailable">'
        "<span>Price shown on Amazon</span></span>"
    )


def empty_cell(note: str = "") -> str:
    if note:
        return f'<span class="muted">{esc(note)}</span>'
    return '<span class="muted" title="Not confirmed from an official source">—</span>'
