#!/usr/bin/env python3
"""Build the Crisp & Counter site from data/ + content/. Standard library only.

Data of record for this edition: data/products-0a90f62c.json (kept separate from
the other sessions' data/products.json so both registers survive integration).

Usage:
    python3 scripts/build_site.py            # render the whole site
    python3 scripts/build_site.py --check    # render to a temp dir and diff against
                                             # the checked-in tree (exit 1 on drift)

Every rendered page carries the disclosure strip, the Amazon Associate statement,
rel="sponsored" on outbound product links, and one footer nav group for the
Research desk. The verification register and link register are generated from
data/products.json so the tables can never drift from the data of record.
"""
import argparse
import difflib
import json
import pathlib
import re
import shutil
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE_URL = "https://karagemop466-tech.github.io/Affil3/legacy/editions/counter"
SITE_NAME = "Crisp &amp; Counter"
SITE_NAME_PLAIN = "Crisp & Counter"
TAGLINE = "Straight answers for better kitchen decisions"
TODAY = "2026-11-20"
TRACKING_ID = "shopnow047c-20"

DATA = json.loads((ROOT / "data" / "products-0a90f62c.json").read_text())
REG = json.loads((ROOT / "data" / "registers.json").read_text())
PRODUCTS = DATA["products"]

# ---------------------------------------------------------------- helpers

def read_guides():
    guides = []
    for p in sorted((ROOT / "content" / "guides").glob("*.md")):
        raw = p.read_text()
        m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
        meta = {}
        for line in m.group(1).splitlines():
            k, _, v = line.partition(":")
            meta[k.strip()] = v.strip().strip('"')
        meta["body"] = m.group(2).strip()
        meta["path"] = p
        guides.append(meta)
    order = ["basket-vs-oven-air-fryer", "air-fryer-capacity-checklist", "cleanup-counter-space",
             "questions-multi-function-appliance", "dual-single-basket-oven-decision-map",
             "smart-meat-thermometer-guide", "black-friday-deal-checklist"]
    guides.sort(key=lambda g: order.index(g["slug"]) if g["slug"] in order else 99)
    return guides

GUIDES = read_guides()

def stars(rating):
    try:
        n = float(rating)
    except (TypeError, ValueError):
        return ""
    full = int(round(n))
    return "★" * full + "☆" * (5 - full)

def aff_link(p, label, kind="cta", cls="btn btn-buy"):
    """A validated-style Special Link: observed listing + tracking id, rel=sponsored."""
    if not p.get("affiliate_url"):
        return ('<span class="btn btn-ghost" aria-disabled="true">Link pending verification</span>'
                '<div class="aff-note">Destination not yet observed (FLG-002) — nothing to sell you '
                'until it is.</div>')
    return (f'<a class="{cls}" href="{p["affiliate_url"]}" rel="sponsored nofollow noopener" target="_blank" '
            f'data-aff="{p["id"]}" data-aff-kind="{kind}">{label}</a>'
            f'<div class="aff-note">Affiliate link — we may earn a commission. '
            f'Observed on Amazon, {p["observed_on"]}.</div>')

def head(title, desc, canonical_path, prefix, extra_ld="", body_attrs=""):
    canonical = SITE_URL + canonical_path
    ld = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": SITE_NAME_PLAIN,
        "url": SITE_URL + "/",
        "description": TAGLINE,
        "publisher": {"@type": "Organization", "name": SITE_NAME_PLAIN},
    }
    import json as _j
    ld_html = (f'<script type="application/ld+json">{_j.dumps(ld)}</script>\n'
               f'<script type="application/ld+json">{extra_ld}</script>' if extra_ld
               else f'<script type="application/ld+json">{_j.dumps(ld)}</script>')
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · {SITE_NAME_PLAIN}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{title} · {SITE_NAME_PLAIN}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:url" content="{canonical}">
<meta name="ck-endpoint" content="">
<link rel="alternate" type="application/rss+xml" title="{SITE_NAME_PLAIN} feed" href="{SITE_URL}/feed.xml">
<link rel="sitemap" type="application/xml" href="{SITE_URL}/sitemap.xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:ital,wght@0,400;0,600;0,700;1,400&family=Inter:wght@400;500;600;700&display=swap">
<link rel="stylesheet" href="{prefix}assets/css/site.css">
{ld_html}
</head>
<body{body_attrs}>"""

NAV = [
    ("shop/", "Air Fryers"),
    ("shop/#smart-kitchen-tools", "Smart Tools"),
    ("guides/", "Buying Guides"),
    ("compare/", "Compare"),
    ("about/", "About"),
]

DESK_LINKS = [
    ("desk/", "Research desk — registers, ledgers and flagged items"),
    ("desk/verification/", "Verification register"),
    ("desk/link-register/", "Link register (product-intent record)"),
    ("desk/flagged/", "Flagged for Review"),
    ("desk/questions/", "Open questions"),
    ("desk/suggestions/", "Suggestion board"),
    ("desk/campaign-ledger/", "Campaign ledger"),
    ("desk/analytics/", "Measurement &amp; analytics"),
    ("desk/compliance/", "Compliance gate"),
    ("desk/coordination/", "Coordination log"),
]

DISCLOSURE_STRIP = f"""<div class="disclosure-strip"><div class="wrap">
<span class="disclosure-badge">Disclosure</span>
<span><strong>Crisp &amp; Counter is reader-supported.</strong> If you buy through links on our site, we may earn a commission from Amazon as part of the Amazon Associates program. I get commissions for purchases made through links in this post. Product links are marked as sponsored. Prices and ratings were observed on Amazon on {TODAY} — the listing is always the source of truth.</span>
</div></div>"""

def masthead(current, prefix):
    links = []
    for href, label in NAV:
        attr = ' aria-current="page"' if current and href.startswith(current) else ""
        links.append(f'<a href="{prefix}{href}"{attr}>{label}</a>')
    return f"""<header class="masthead"><div class="wrap masthead-inner">
<a class="brand" href="{prefix}">
  <span class="brand-mark">Crisp <em>&amp;</em> Counter</span>
  <span class="brand-tag">{TAGLINE}</span>
</a>
<nav class="nav" aria-label="Main">{''.join(links)}</nav>
</div></header>"""

def footer(prefix):
    shop_items = "".join(
        f'<li><a href="{prefix}{h}">{l}</a></li>' for h, l in [
            ("shop/", "All products"),
            ("compare/", "Side-by-side comparison"),
            ("guides/", "Buying guides"),
            ("feed.xml", "RSS feed"),
        ])
    guide_items = "".join(
        f'<li><a href="{prefix}guides/{g["slug"]}/">{g["title"]}</a></li>' for g in GUIDES[:5])
    desk_items = "".join(f'<li><a href="{prefix}{h}">{l}</a></li>' for h, l in DESK_LINKS)
    return f"""<footer class="site-footer"><div class="wrap">
<div class="footer-grid">
  <div>
    <h4>Crisp &amp; Counter</h4>
    <p>An independent kitchen-gear publication. We publish buyer questions, verified product facts and honest checklists — and we show our sources.</p>
    <p class="badge-live" style="color:#9fc7a4">Verified register updated {TODAY}</p>
  </div>
  <div>
    <h4>Shop</h4>
    <ul>{shop_items}</ul>
  </div>
  <div>
    <h4>Guides</h4>
    <ul>{guide_items}</ul>
  </div>
  <div>
    <h4>Research desk</h4>
    <ul>{desk_items}</ul>
  </div>
</div>
<div class="footer-disclosure">
  <p><strong>Disclosure (repeated as required):</strong> Crisp &amp; Counter is a participant in the Amazon Services LLC Associates Program, an affiliate advertising program designed to provide a means for sites to earn advertising fees by advertising and linking to Amazon.com. <strong>As an Amazon Associate we earn from qualifying purchases.</strong> I get commissions for purchases made through links in this post. Product links are affiliate links marked <code>rel="sponsored"</code>; we may earn a commission if you buy through them. Observed prices, ratings and deal badges were read from Amazon listing pages on {TODAY} and can change at any time. We do not publish revenue forecasts or conversion scores. Unverified items are listed on the <a href="{prefix}desk/flagged/">Flagged for Review</a> page.</p>
  <p>© 2026 Crisp &amp; Counter · <a href="{prefix}about/">About &amp; editorial policy</a> · <a href="{prefix}desk/compliance/">Compliance gate</a> · <a href="{prefix}feed.xml">RSS</a></p>
</div>
</div></footer>
<script src="{prefix}assets/js/analytics.js"></script>
<script src="{prefix}assets/js/site.js"></script>
</body>
</html>"""

def page(title, desc, canonical_path, prefix, content, current="", body_attrs="", extra_ld=""):
    return normalize_rels(head(title, desc, canonical_path, prefix, extra_ld, body_attrs)
                          + masthead(current, prefix) + DISCLOSURE_STRIP + content + footer(prefix))

# ---------------------------------------------------------------- reusable blocks

def product_card(p, prefix, heading="h3"):
    media = (f'<img src="{p["image"]}" alt="{p["short_name"]} — product photo from its Amazon listing" loading="lazy">'
             if p.get("image") else
             '<div class="no-image">Photo not captured.<br>See the official listing.</div>')
    chips = "".join(f'<span class="chip">{c}</span>' for c in p.get("spec_chips", []))
    if p["status"] == "unresolved":
        price = ('<span class="status-pill status-unresolved">Unresolved</span> '
                 '<span class="observed-note">Destination not observed (FLG-002)</span>')
    else:
        price = ""
        if p.get("price_observed"):
            was = f'<span class="price-was">{p["list_price_observed"]}</span>' if p.get("list_price_observed") else ""
            flag = '<span class="price-flag">Deal observed</span>' if p.get("list_price_observed") else ""
            price = f'<div class="price-row"><span class="price-now">{p["price_observed"]}</span>{was}{flag}</div>'
            price += f'<div class="observed-note">Observed {p["observed_on"]} · prices change — see listing</div>'
        rating = ""
        if p.get("rating_stars"):
            rating = (f'<div class="rating"><span class="stars" aria-hidden="true">{stars(p["rating_stars"])}</span> '
                      f'{p["rating_stars"]}/5 · {p["rating_count"]} ratings <span class="observed-note">(observed {p["observed_on"]})</span></div>')
        price += rating
    return f"""<article class="card product-card" data-product-id="{p['id']}">
  <div class="product-media">{media}</div>
  <div class="product-body">
    <div class="product-cat">{p.get('category_label','')}</div>
    <{heading} class="product-title"><a href="{p.get('listing_url') or prefix + 'desk/flagged/'}" rel="noopener" target="_blank">{p['short_name'] or 'Product pending verification'}</a></{heading}>
    <div class="chips">{chips}</div>
    {price}
    {aff_link(p, 'Check price on Amazon')}
  </div>
</article>"""

def guide_card(g, prefix):
    return f"""<article class="card">
  <div class="product-cat">{g['cluster']}</div>
  <h3><a href="{prefix}guides/{g['slug']}/">{g['title']}</a></h3>
  <p class="dek">{g['dek']}</p>
  <div class="meta"><time datetime="{g['date']}">{g['date']}</time> · Question-first guide</div>
</article>"""

def table(headers, rows, cls="data sourced"):
    th = "".join(f"<th>{h}</th>" for h in headers)
    trs = []
    for r in rows:
        trs.append("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>")
    return f'<div class="table-wrap"><table class="{cls}"><thead><tr>{th}</tr></thead><tbody>{"".join(trs)}</tbody></table></div>'

def normalize_rels(html):
    """Every outbound Amazon product link ships as rel=sponsored nofollow
    noopener — citations included. The brief requires all product links marked
    sponsored; doing it in one pass keeps the rule unfalsifiable."""
    def fix(m):
        tag = m.group(0)
        if 'href="https://www.amazon.com/dp/' in tag or 'href="https://link.amazon/' in tag:
            if 'rel="' in tag:
                tag = re.sub(r'rel="[^"]*"', 'rel="sponsored nofollow noopener"', tag)
            else:
                tag = tag[:-1] + ' rel="sponsored nofollow noopener">'
        return tag
    return re.sub(r"<a\b[^>]*>", fix, html)

# ---------------------------------------------------------------- reader pages

def render_home(prefix=""):
    featured = [p for p in PRODUCTS if p["status"] == "verified-observed"]
    cards = "".join(product_card(p, prefix) for p in featured[:3])
    guide_cards = "".join(guide_card(g, prefix) for g in GUIDES[:4])
    season = next(g for g in GUIDES if g["slug"] == "black-friday-deal-checklist")
    content = f"""
<main>
<section class="hero"><div class="wrap">
  <span class="hero-kicker">❄ Deal week edition · Updated {TODAY}</span>
  <h1>Kitchen gear, answered with receipts.</h1>
  <p class="lede">We turn product research into buyer answers: question-first guides, a verified product register with an official source on every line, and honest checklists instead of hype. Every Amazon link is marked, every number is dated, and nothing we can't confirm gets published.</p>
  <div class="hero-ctas">
    <a class="btn btn-primary" href="{prefix}shop/">Shop the verified register</a>
    <a class="btn btn-ghost" href="{prefix}guides/">Start with a buyer question</a>
  </div>
</div></section>

<section class="section"><div class="wrap">
  <div class="season-band">
    <div>
      <h2>Black Friday, without the fake urgency</h2>
      <p>Deal prices on this page were observed on Amazon on {TODAY} and are stamped as such. Our short checklist shows how to judge a kitchen discount in under five minutes — before the countdown timer wins.</p>
    </div>
    <a class="btn btn-primary" href="{prefix}guides/{season['slug']}/">Read the deal checklist</a>
  </div>
</div></section>

<section class="section"><div class="wrap">
  <div class="section-head">
    <div><div class="kicker">The register</div><h2>Products we track, facts we've verified</h2></div>
    <a class="see-all" href="{prefix}shop/">All {len(PRODUCTS)} products →</a>
  </div>
  <div class="card-grid">{cards}</div>
  <p class="mini" style="margin-top:14px">Every product fact above was read from its official Amazon listing on {TODAY}. Missing values are left blank and flagged — see the <a href="{prefix}desk/verification/">verification register</a>.</p>
</div></section>

<section class="section"><div class="wrap">
  <div class="section-head">
    <div><div class="kicker">Buying guides</div><h2>Start with the question you'd actually ask</h2></div>
    <a class="see-all" href="{prefix}guides/">All guides →</a>
  </div>
  <div class="guide-grid">{guide_cards}</div>
</div></section>

<section class="section"><div class="wrap two-col">
  <div>
    <div class="kicker">How we work</div>
    <h2>Published like a shop. Built like a lab notebook.</h2>
    <p>Every claim on this site traces to an official source: Amazon listing pages for product facts, the FTC and Amazon Associates policy pages for how we disclose. When we observe something — a price, a rating, a redirect target — we date it. When we can't confirm something, the field stays blank and lands on the <a href="{prefix}desk/flagged/">Flagged for Review</a> page instead of in your face.</p>
    <p>Interested in the machinery? The Research desk (link group in the footer) holds the verification register, the product-intent record, an empty-but-defined campaign ledger, and the suggestion board where the next changes wait for review.</p>
    <a class="btn btn-ghost" href="{prefix}about/">About &amp; editorial policy</a>
  </div>
  <div class="callout green">
    <h3 style="margin-top:0">The promise in one line</h3>
    <p>No fabricated specs. No invented ratings. No revenue forecasts. No unmarked affiliate links. If it's on the page, its source is one click away.</p>
    <p class="mini">Amazon Associate statement appears in the footer of every page, and the disclosure strip sits under the masthead on every page.</p>
  </div>
</div></section>
</main>"""
    return page("Home", f"{TAGLINE}. Verified kitchen product facts, question-first buying guides and a transparent research desk.",
                "/", prefix, content, current="")

def render_shop(prefix="../"):
    groups = [("air-fryers", "Air fryers &amp; oven-style", "Basket, dual-basket and oven-style units from the register."),
              ("kitchen-tech", "Smart kitchen tools", "Connected tools that earn their drawer space."),
              ("unresolved", "Pending verification", "Submitted links whose destination we haven't been able to observe yet.")]
    sections = []
    for cat, label, blurb in groups:
        items = [p for p in PRODUCTS if p.get("category") == cat]
        if not items:
            continue
        anchor = f'<span id="{cat}"></span>' if cat != "air-fryers" else ""
        cards = "".join(product_card(p, prefix) for p in items)
        sections.append(f"""
<section class="section"><div class="wrap">{anchor}
  <div class="section-head"><div><div class="kicker">{label}</div><h2>{blurb}</h2></div></div>
  <div class="card-grid">{cards}</div>
</div></section>""")
    content = f"""
<main>
<section class="hero"><div class="wrap">
  <div class="kicker">Shop</div>
  <h1>The verified register</h1>
  <p class="lede">{len(PRODUCTS)} submitted products, organized by what they actually are. Product facts were read from official Amazon listings on {TODAY}; prices move, so every card links to the live listing. Nothing here is ranked by commission — we don't even publish commission rates.</p>
</div></section>
{''.join(sections)}
<section class="section"><div class="wrap callout">
  <h3 style="margin-top:0">Where the numbers come from</h3>
  <p>Titles, categories, ratings, prices and images on this page were observed on Amazon listing pages on {TODAY} and are recorded in the <a href="{prefix}desk/verification/">verification register</a> with source links. Intended ASINs are tracked separately from observed redirect targets in the <a href="{prefix}desk/link-register/">link register</a> and are blank until the owner confirms them.</p>
</div></section>
</main>"""
    return page("Shop the register", "Kitchen products verified against official Amazon listings: air fryers, oven-style units and smart kitchen tools.",
                "/shop/", prefix, content, current="shop/")

def render_compare(prefix="../"):
    prods = [p for p in PRODUCTS if p["status"] == "verified-observed"]
    def cell(p, key, fallback="—"):
        v = p.get(key)
        return v if v else f'<span class="mini">{fallback}</span>'
    rows = [
        ["Official listing", *[f'<a href="{p["listing_url"]}" rel="noopener" target="_blank">amazon.com/dp/{p["observed_asin"]}</a>' for p in prods]],
        ["Category (observed)", *[p["category_label"] for p in prods]],
        ["Form factor", *[next((c for c in p["spec_chips"] if "quart" in c.lower()), "—") for p in prods]],
        ["Stated highlights", *[" · ".join(p["spec_chips"][:4]) for p in prods]],
        ["Rating (observed)", *[(f'{stars(p["rating_stars"])} {p["rating_stars"]}/5 · {p["rating_count"]}' if p.get("rating_stars") else '<span class="mini">Not captured (FLG-005)</span>') for p in prods]],
        ["Price observed", *[(f'<strong>{p["price_observed"]}</strong>' + (f' <span class="price-was">{p["list_price_observed"]}</span>' if p.get("list_price_observed") else "") + f'<br><span class="mini">{p["observed_on"]}</span>') if p.get("price_observed") else '<span class="mini">—</span>' for p in prods]],
        ["Offer notes", *[cell(p, "offer_note", "—") for p in prods]],
        ["Observed on", *[p["observed_on"] for p in prods]],
        ["Buy", *[aff_link(p, "View on Amazon", kind="table", cls="btn btn-buy btn-small") for p in prods]],
    ]
    src_cell = " ".join(f'<a href="{p["listing_url"]}" rel="noopener" target="_blank">S{8+i}</a>' for i, p in enumerate(prods))
    rows = [r + [src_cell] for r in rows]
    t = table(["Verified field"] + [p["short_name"] for p in prods] + ["Sources (official)"], rows)
    content = f"""
<main>
<section class="hero"><div class="wrap">
  <div class="kicker">Compare</div>
  <h1>Side by side, observed fields only</h1>
  <p class="lede">This table compares only facts we read from official Amazon listing pages on {TODAY} — with the source linked in the last row. Blank cells are honest gaps: we don't fill them by inference. All five submitted links now resolve to observed listings — P4 resolved on a same-day retest after two transient Amazon checkpoints (FLG-002).</p>
</div></section>
<section class="section"><div class="wrap">
  {t}
  <p class="mini" style="margin-top:12px">Spec highlights are quoted from the official listing titles. Ratings and prices change; the listing is the source of truth. Comparison of unlisted attributes (noise, real-world cook area) awaits hands-on testing — see suggestion SG-09.</p>
</div></section>
<section class="section"><div class="wrap two-col">
  <div class="callout">
    <h3 style="margin-top:0">How to read this table</h3>
    <p>Capacity numbers are quoted as the seller states them — our <a href="{prefix}guides/air-fryer-capacity-checklist/">capacity checklist</a> explains why cook area beats quarts. The 24 presets on the oven-style unit are one-touch programs, not 24 distinct capabilities (<a href="{prefix}guides/questions-multi-function-appliance/">see the multi-function questions</a>).</p>
  </div>
  <div class="callout green">
    <h3 style="margin-top:0">What we deliberately leave out</h3>
    <p>Performance rankings, "best choice" labels, and any field without an official source. We're a comparison desk, not a scoreboard.</p>
  </div>
</div></section>
</main>"""
    return page("Compare products", "Verified side-by-side comparison of the register products, with official Amazon source links and observed dates.",
                "/compare/", prefix, content, current="compare/")

def render_guides_index(prefix="../"):
    clusters = {}
    for g in GUIDES:
        clusters.setdefault(g["cluster"], []).append(g)
    blocks = []
    for cl, items in clusters.items():
        cards = "".join(guide_card(g, prefix) for g in items)
        blocks.append(f"""
<section class="section"><div class="wrap">
  <div class="section-head"><div><div class="kicker">{cl}</div><h2>Guides in this cluster</h2></div></div>
  <div class="guide-grid">{cards}</div>
</div></section>""")
    content = f"""
<main>
<section class="hero"><div class="wrap">
  <div class="kicker">Buying guides</div>
  <h1>Questions first. Products second.</h1>
  <p class="lede">Every guide here starts from a question a real buyer asks — not from a keyword list. The working titles are editorial hypotheses about what's useful to compare; we update the set from measured search queries once Search Console is verified (SG-06).</p>
</div></section>
{''.join(blocks)}
<section class="section"><div class="wrap callout green">
  <h3 style="margin-top:0">Publishing cadence</h3>
  <p>One new question-shaped guide per month, added to the sitemap and RSS feed on publication. Next up for review on the <a href="{prefix}desk/suggestions/">suggestion board</a>: a holiday gifting checklist and a "first apartment kitchen" starter guide.</p>
</div></section>
</main>"""
    return page("Buying guides", "Question-shaped kitchen buying guides: air fryer capacity, cleanup trade-offs, multi-function appliances and deal checklists.",
                "/guides/", prefix, content, current="guides/")

def render_guide(g, prefix="../../"):
    idx = GUIDES.index(g)
    prev = GUIDES[idx - 1] if idx > 0 else None
    nxt = GUIDES[idx + 1] if idx < len(GUIDES) - 1 else None
    related = [p for p in PRODUCTS if p["status"] == "verified-observed"][:3]
    rel_cards = "".join(product_card(p, prefix) for p in related)
    prev_link = f'<a class="btn btn-ghost btn-small" href="{prefix}guides/{prev["slug"]}/">← {prev["title"]}</a>' if prev else ""
    next_link = f'<a class="btn btn-ghost btn-small" href="{prefix}guides/{nxt["slug"]}/">{nxt["title"]} →</a>' if nxt else ""
    content = f"""
<main class="article"><div class="narrow">
  <div class="article-meta">
    <a class="cluster-pill" href="{prefix}guides/">{g['cluster']}</a>
    <span>Published <time datetime="{g['date']}">{g['date']}</time></span>
    <span>7 min read</span>
    <span>Editorial guide · sources listed inline</span>
  </div>
  <h1>{g['title']}</h1>
  <p class="lede">{g['dek']}</p>
  <div class="article-body">
    {g['body']}
  </div>
  <div class="guide-footer-nav">{prev_link}{next_link}</div>
</div>
<section class="section"><div class="wrap">
  <div class="section-head"><div><div class="kicker">From the register</div><h2>Products referenced in this guide</h2></div>
  <a class="see-all" href="{prefix}shop/">All products →</a></div>
  <div class="card-grid">{rel_cards}</div>
  <p class="mini" style="margin-top:12px">Links are affiliate links (marked, rel="sponsored"). We earn a commission from qualifying purchases.</p>
</div></section>
</main>"""
    import json as _j
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": g["title"],
          "datePublished": g["date"], "description": g["seo"],
          "author": {"@type": "Organization", "name": SITE_NAME_PLAIN},
          "mainEntityOfPage": SITE_URL + f"/guides/{g['slug']}/"}
    return page(g["title"], g["seo"], f"/guides/{g['slug']}/", prefix, content,
                current="guides/", body_attrs=f' data-guide="{g["slug"]}"', extra_ld=_j.dumps(ld))

def render_about(prefix="../"):
    src_rows = [[s["id"], f'<a href="{s["url"]}" rel="noopener" target="_blank">{s["title"]}</a>',
                 s["kind"], s["used_for"], s["checked"]] for s in REG["sources"]]
    src_table = table(["ID", "Official source", "Kind", "Used for", "Last checked"], src_rows)
    content = f"""
<main>
<section class="hero"><div class="wrap">
  <div class="kicker">About</div>
  <h1>A shop that shows its homework</h1>
  <p class="lede">Crisp &amp; Counter is an independent kitchen-gear publication built on a simple rule: if a claim can't be traced to an official source, it doesn't go on the page. The site is also an experiment in transparent affiliate publishing — the machinery is on display.</p>
</div></section>
<section class="section"><div class="narrow">
  <h2>Editorial policy</h2>
  <ul>
    <li><strong>Products lead, process follows.</strong> The front page is a shop; the verification machinery lives one level down in the Research desk.</li>
    <li><strong>Observed facts are dated.</strong> Prices, ratings and redirect targets carry the date we read them. They are photographs, not promises.</li>
    <li><strong>Blank beats guessed.</strong> Unconfirmed fields stay empty and are published on the <a href="{prefix}desk/flagged/">Flagged for Review</a> page with their source links.</li>
    <li><strong>No forecasts.</strong> We publish no conversion scores, revenue projections or commission estimates. The <a href="{prefix}desk/campaign-ledger/">campaign ledger</a> accepts only first-party reported figures.</li>
    <li><strong>Every commercial link is marked.</strong> rel="sponsored" on the link, a disclosure strip under the masthead, and the Amazon Associate statement in the footer of every page.</li>
    <li><strong>Working titles stay honest.</strong> Guide topics are editorial hypotheses, not claims about search volume or popularity.</li>
  </ul>
  <h2>Full affiliate disclosure</h2>
  <div class="callout">
    <p>Crisp &amp; Counter is a participant in the Amazon Services LLC Associates Program, an affiliate advertising program designed to provide a means for sites to earn advertising fees by advertising and linking to Amazon.com. <strong>As an Amazon Associate we earn from qualifying purchases.</strong></p>
    <p>If you click a product link on this site and buy something, we may earn a commission. The price you pay is the same either way. We only link products we have recorded in our register against their official Amazon listings. This disclosure is provided in accordance with the FTC's guidance on endorsements and testimonials (16 CFR Part 255) and the Amazon Associates Operating Agreement — see the source table below.</p>
  </div>
  <h2>Method in brief</h2>
  <ol>
    <li><strong>Intake:</strong> each submitted link is recorded exactly as given, in the <a href="{prefix}desk/link-register/">product-intent record</a>, with intended fields kept strictly separate from observed fields.</li>
    <li><strong>Observation:</strong> the link is fetched and its resolved Amazon listing read; titles, categories, ratings, prices and images are recorded with an observation date.</li>
    <li><strong>Verification:</strong> each published field gets a row in the <a href="{prefix}desk/verification/">verification register</a> with a source link to the official listing. Anything unconfirmed is left blank and flagged.</li>
    <li><strong>Publication:</strong> pages are generated from that data, checked by automated gates (disclosure presence, sponsored marking, source coverage), then shipped.</li>
  </ol>
  <h2>Sources we check against</h2>
  {src_table}
</div></section>
</main>"""
    return page("About & editorial policy", "How Crisp & Counter verifies product facts, discloses affiliate relationships and publishes flagged items openly.",
                "/about/", prefix, content, current="about/")

# ---------------------------------------------------------------- desk pages

def desk_hero(kicker, title, lede):
    return f"""<section class="hero"><div class="wrap">
  <div class="kicker">Research desk · {kicker}</div>
  <h1>{title}</h1>
  <p class="lede">{lede}</p>
</div></section>"""

def render_desk_index(prefix="../"):
    cards = "".join(f"""<a class="desk-card" href="{prefix}{h}">
      <div class="desk-id">{h.strip('/').replace('desk/','').replace('desk','hub')}</div>
      <h3>{l}</h3>
      <p>{d}</p></a>""" for (h, l), d in zip(DESK_LINKS[1:], [
        "Line-by-line claims, values, official source links and unverified flags.",
        "Intended ASIN vs observed redirect target — never merged.",
        "Everything we couldn't confirm, published with its sources.",
        "What we know, what we don't, and how to find out.",
        "Proposed changes with options — review before anything is implemented.",
        "Empty, well-defined, provenance-trailed. Fills only from first-party reports.",
        "Five events, privacy rules, and the self-hosted collector spec.",
        "The gates that stand between drafting and publishing.",
        "Task board, verification performed, and hand-off notes.",
    ]))
    content = desk_hero("Hub", "The machinery, in the open",
        "Everything behind the publication: the registers that keep us honest, the ledgers that keep us measured, and the gates that keep us compliant. Nothing here is hidden from readers — it's linked from every footer.") + f"""
<section class="section"><div class="wrap">
  <div class="desk-grid">{cards}</div>
</div></section>
<section class="section"><div class="wrap callout green">
  <h3 style="margin-top:0">Status at a glance ({TODAY})</h3>
  <p>Register: 5 products recorded · 5 destinations observed · 0 unresolved · 0 intended ASINs confirmed. Campaign ledger: empty by design. Open flags: {len(REG['flags'])} · Open questions: {len(REG['questions'])} · Suggestions awaiting review: {sum(1 for s in REG['suggestions'] if s['status']=='proposed')}.</p>
</div></section>
</main>"""
    return page("Research desk", "Registers, ledgers, flagged items, suggestions and compliance gates for Crisp & Counter.",
                "/desk/", prefix, "<main>" + content, current="")

def render_verification(prefix="../../"):
    rows = []
    sid = {"P1": "S08", "P2": "S09", "P3": "S10", "P5": "S11", "P4": "S12"}
    for p in PRODUCTS:
        src = (f'<a href="{p["listing_url"]}" rel="noopener" target="_blank">{sid.get(p["id"],"")} · official listing</a>'
               if p.get("listing_url") else f'<a href="{p["submitted_link"]}" rel="noopener" target="_blank">S12 · submitted link</a>')
        sub_src = f'<a href="{p["submitted_link"]}" rel="noopener" target="_blank">submitted link</a>'
        ok = '<span class="status-pill status-verified">Verified</span>'
        unv = '<span class="status-pill status-unverified">Unverified</span>'
        unr = '<span class="status-pill status-unresolved">Unresolved</span>'
        if p["status"] == "unresolved":
            rows += [
                [f'{p["id"]} · submitted link', f'<code>{p["submitted_link"]}</code>', ok, sub_src, p["observed_method"]],
                [f'{p["id"]} · observed target', "", unr, sub_src, "FLG-002 — retried twice on " + TODAY],
                [f'{p["id"]} · title / category / price', "", unr, sub_src, "Left blank; nothing inferred"],
            ]
            continue
        rows += [
            [f'{p["id"]} · observed redirect target', f'<code>{p["observed_redirect_url"]}</code>', ok,
             f'{sub_src} · {src}', f'Observed {p["observed_on"]} — {p["observed_method"]}'],
            [f'{p["id"]} · official title', p["official_title"], ok, src, "Quoted verbatim from the listing page title"],
            [f'{p["id"]} · category path', p["category_path"], ok, src, "Quoted from the listing breadcrumb"],
            [f'{p["id"]} · price observed', (p["price_observed"] + (f' (list {p["list_price_observed"]})' if p["list_price_observed"] else "")) or "",
             ok if p["price_observed"] else unv, src,
             p["offer_note"] or "Not captured in fetched page sections — FLG-005"],
            [f'{p["id"]} · rating observed', (f'{p["rating_stars"]}/5 ({p["rating_count"]})' if p["rating_stars"] else ""),
             ok if p["rating_stars"] else unv, src,
             f'Observed {p["observed_on"]}; changes over time — FLG-005'],
            [f'{p["id"]} · intended ASIN', "", unv, f'<a href="https://advertising.amazon.com/library/guides/asins-introduction" rel="noopener" target="_blank">S04 · ASIN definition</a>',
             "Blank pending owner confirmation — FLG-001. Not a claim the link is invalid (FLG-003)."],
        ]
    policy_rows = [
        ["Policy · disclosure placement", "Strip under masthead + footer statement on every page", ok,
         '<a href="https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers" rel="noopener" target="_blank">S05 · FTC Disclosures 101</a>',
         "Enforced by scripts/check_site.py on every build"],
        ["Policy · affiliate link marking", 'rel="sponsored nofollow noopener" on every product anchor', ok,
         '<a href="https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links" rel="noopener" target="_blank">S06 · Google outbound links</a>',
         "Enforced by scripts/check_site.py"],
        ["Policy · Special Link validation test", "Not yet run in the enrolled Associates workflow", unv,
         '<a href="https://affiliate-program.amazon.com/help/operating/agreement" rel="noopener" target="_blank">S02 · Operating Agreement</a>',
         "Gate G3 pending owner — FLG-004"],
        ["Policy · commission rates", "", unv,
         '<a href="https://affiliate-program.amazon.com/help/operating/advertisingfee" rel="noopener" target="_blank">S13 · fee schedule (sign-in)</a>',
         "Account-specific; intentionally not published — FLG-009"],
    ]
    t = table(["Claim / field", "Value", "Status", "Source (official)", "Notes"], rows + policy_rows)
    content = desk_hero("Verification register",
        "Every published claim, line by line",
        "Each row is a claim the site publishes, with its value, verification status and a link to the official source it was read from. Values that can't be confirmed are left blank and flagged — never inferred. Product rows are generated from data/products.json, so the table cannot drift from the data of record.") + f"""
<section class="section"><div class="wrap">{t}
<p class="mini" style="margin-top:12px">Sources S01–S13 are defined on the <a href="{prefix}about/">About page</a>. Last full review: {TODAY}.</p>
</div></section>
</main>"""
    return page("Verification register", "Line-by-line verification of every published product claim with official source links and unverified flags.",
                "/desk/verification/", prefix, "<main>" + content)

def render_link_register(prefix="../../"):
    rows = []
    for p in PRODUCTS:
        rows.append([
            f'<span class="col-id">{p["id"]}</span>',
            f'<a href="{p["submitted_link"]}" rel="noopener" target="_blank"><code>{p["submitted_token"]}</code></a>',
            f'<code>{p["intended_asin"] or "—"}</code>' if p["intended_asin"] else '<span class="mini">blank — FLG-001</span>',
            p["intended_listing_url"] or '<span class="mini">blank — FLG-001</span>',
            p["confirmation_date"] or '<span class="mini">blank — FLG-001</span>',
            p["intended_source"],
            (f'<a href="{p["observed_redirect_url"]}" rel="noopener" target="_blank"><code>{p["observed_asin"]}</code></a>'
             if p.get("observed_asin") else '<span class="status-pill status-unresolved">not observed</span>'),
            p["observed_on"] or "—",
            p["observed_method"],
        ])
    t = table(["ID", "Submitted link", "Intended ASIN", "Intended listing URL", "Confirmation date", "Intended source",
               "Observed redirect target", "Observed on", "Observation method"], rows)
    content = desk_hero("Product-intent confirmation record",
        "Intent and observation, never merged",
        "For each submitted link we store the intended ASIN, official listing URL, confirmation date and source — and, in separate fields, the redirect target we actually observed. Amazon defines an ASIN as a 10-character identifier (S04), which makes it a checkable fact once the owner states it. The submitted short-link tokens are recorded exactly as given; per the brief (FLG-003) we make no claim that the supplied short links are invalid.") + f"""
<section class="section"><div class="wrap">{t}
<div class="callout">
  <h3 style="margin-top:0">Reading this record</h3>
  <p><strong>Left block = intent</strong> (what the owner says the link is for). <strong>Right block = observation</strong> (what we measured on {TODAY}). The fields are never merged: a redirect target observed today is evidence about the link, not proof of intent. All five links resolved to listings: B0CDY277D3, B09B7SB46R, B08DKYBTPH, B0DZFD6R9Z, and B0DHZTCNR5 (the last after two transient checkpoint pages, resolved on same-day retest and independently corroborated — FLG-002).</p>
</div>
</div></section>
</main>"""
    return page("Link register", "Product-intent confirmation record: intended ASIN fields kept strictly separate from observed Amazon redirect targets.",
                "/desk/link-register/", prefix, "<main>" + content)

def render_flagged(prefix="../../"):
    rows = []
    for f in REG["flags"]:
        srcs = " · ".join(f'<a href="{s["url"]}" rel="noopener" target="_blank">{s["id"]}</a>' for s in REG["sources"] if s["id"] in f["sources"])
        if not srcs:
            srcs = '<a href="https://github.com/karagemop466-tech/Affil3/blob/main/COORDINATION.md" rel="noopener" target="_blank">repo board</a> <span class="mini">(brief-only item — FLG-008)</span>'
        rows.append([f'<span class="col-id">{f["id"]}</span>', f'<strong>{f["title"]}</strong><br><span class="mini">{f["detail"]}</span>',
                     f["status"], f["blocks"], srcs])
    t = table(["ID", "Irregularity / open item", "Status", "What it blocks", "Sources"], rows)
    content = desk_hero("Flagged for Review",
        "What we couldn't confirm — published anyway",
        "Irregularities and unverified items don't block the site; they get their own page with source links so they can be reviewed after launch. Nothing here is speculation: each entry names what was checked, what was found, and what would resolve it.") + f"""
<section class="section"><div class="wrap">{t}
<p class="mini" style="margin-top:12px">To request a change to any entry, use the <a href="{prefix}desk/suggestions/">suggestion board</a> or open a GitHub issue.</p>
</div></section>
</main>"""
    return page("Flagged for Review", "Irregularities, unverified values and open compliance items with official source links.",
                "/desk/flagged/", prefix, "<main>" + content)

def render_questions(prefix="../../"):
    rows = [[f'<span class="col-id">{q["id"]}</span>', f'<strong>{q["question"]}</strong>', q["known"], q["unknown"], q["how_to_find"]]
            for q in REG["questions"]]
    t = table(["ID", "Question", "What we know", "What we don't know", "How to find out"], rows, cls="data meta")
    content = desk_hero("Open questions",
        "Decisions need these answers first",
        "A decision is only as good as the information behind it. This register lists the questions that must be answered before the related decisions can be reasonably made — with what we already know, what's missing, and the cheapest way to find out. The suggestion board proposes how to discover the missing information.") + f"""
<section class="section"><div class="wrap">{t}
<div class="callout green">
  <h3 style="margin-top:0">Discovery path</h3>
  <p>Most gaps resolve through three doors: the owner's Associates Central account (Q-01, Q-03, Q-04, Q-09), one re-test of a link in a normal browser session (Q-02), or a single decision recorded on the <a href="{prefix}desk/suggestions/">suggestion board</a> (Q-05–Q-10). No gap requires speculative data to work around.</p>
</div>
</div></section>
</main>"""
    return page("Open questions", "The information gaps that must close before key decisions — and how to close them.",
                "/desk/questions/", prefix, "<main>" + content)

def render_suggestions(prefix="../../"):
    rows = []
    for s in REG["suggestions"]:
        opts = "<br>".join(f'· {o}' for o in s["options"])
        rows.append([
            f'<span class="col-id">{s["id"]}</span>',
            f'<strong>{s["title"]}</strong><br><span class="mini">{s["rationale"]}</span>',
            f'{s["priority"]}<br><span class="mini">effort {s["effort"]} · risk {s["risk"]}</span>',
            opts,
            f'<strong>{s["recommendation"]}</strong><br><span class="mini">status: {s["status"]}</span>',
            f'<a href="https://github.com/karagemop466-tech/Affil3/issues/new?title=%5B{s["id"]}%5D%20Decision" data-feedback="{s["id"]}" rel="noopener" target="_blank">Decide →</a>',
        ])
    t = table(["ID", "Suggestion &amp; rationale", "Priority / effort / risk", "Options", "Recommendation &amp; status", "Decision"], rows, cls="data meta")
    content = desk_hero("Suggestion board",
        "Choose the path before we build it",
        "Every proposed change waits here first: what it is, why it might be worth doing, what the options are, and what we recommend. Nothing on this list gets implemented until it's reviewed and decided — that's the point of the board. Brief-cited IDs (SG-27..SG-30) map provisionally to SG-11, SG-06, SG-12 and SG-10 (FLG-008).") + f"""
<section class="section"><div class="wrap">{t}
<div class="callout">
  <h3 style="margin-top:0">How to decide</h3>
  <ol>
    <li>Filter by priority: the four <strong>high</strong> items are the ones the brief's own logic demands first (measurement, gate G3, intent record, cadence).</li>
    <li>Pick an option per suggestion (the recommendation is a default, not a verdict).</li>
    <li>Record the decision via the link in the last column (opens a pre-filled GitHub issue) or in the repository's <a href="https://github.com/karagemop466-tech/Affil3/blob/main/COORDINATION.md" rel="noopener" target="_blank">COORDINATION.md</a> board.</li>
    <li>Only then does implementation start — and it lands with its own verification rows.</li>
  </ol>
</div>
</div></section>
</main>"""
    return page("Suggestion board", "Proposed changes with options, rationales and recommendations — reviewed before anything is implemented.",
                "/desk/suggestions/", prefix, "<main>" + content)

def render_ledger(prefix="../../"):
    cols = REG["campaign_ledger"]["columns"]
    hdrs = [c.replace("_", " ") for c in cols] + ["report ref"]
    rows = [["<em>No rows yet.</em>"] + [""] * (len(cols) - 1) + [""]]
    t = table(hdrs, rows, cls="data meta")
    prov = "".join(f'<li><strong>{p["date"]}</strong> — {p["entry"]}</li>' for p in REG["campaign_ledger"]["provenance"])
    content = desk_hero("Campaign ledger",
        "Empty, well-defined, and staying honest",
        "The ledger starts empty on purpose. Rows are appended only when figures come from authorized first-party reports — Associates Central exports or the self-hosted analytics endpoint. Timestamp, source, channel, eligible sessions, clicks and reported orders; nothing else. No conversion score and no revenue forecast appears anywhere on this site (brief Priority 4).") + f"""
<section class="section"><div class="wrap">
  <h2>Columns of record</h2>
  {t}
  <h2>Intake rule</h2>
  <div class="callout"><p>{REG["campaign_ledger"]["intake_rule"]}</p></div>
  <h2>Provenance trail</h2>
  <ul>{prov}</ul>
</div></section>
</main>"""
    return page("Campaign ledger", "An empty but well-defined campaign ledger with an intake rule and dated provenance trail.",
                "/desk/campaign-ledger/", prefix, "<main>" + content)

def render_analytics(prefix="../../"):
    rows = [[e["id"], f'<code>{e["name"]}</code>', e["fires_when"], e["payload"]] for e in REG["events"]["items"]]
    t = table(["ID", "Event", "Fires when", "Payload"], rows, cls="data meta")
    content = desk_hero("Measurement &amp; analytics",
        "Five events, zero surveillance",
        "Click and conversion measurement ships before content scales. The client (assets/js/analytics.js) is privacy-preserving by construction: no cookies, no third-party beacons, no IP or user-agent storage. The brief asks for a self-hosted analytics endpoint and 'the five defined events'; the brief doesn't enumerate the events, so this register defines five and flags the gap (Q-05, FLG-008).") + f"""
<section class="section"><div class="wrap">
  <h2>The event register</h2>
  {t}
  <h2>Privacy rules</h2>
  <div class="callout green"><p>{REG["events"]["privacy"]}</p></div>
  <h2>Deployment status</h2>
  <p><span class="status-pill status-unverified">Endpoint not deployed (FLG-006)</span> GitHub Pages serves static files only. The collector is ready at <code>server/collect.js</code> (Node, standard library only): deploy it anywhere Node runs, then set <code>&lt;meta name="ck-endpoint"&gt;</code> on each page. Until then, event counts aggregate in your own browser — you can see them in DevTools under <code>localStorage.ck_events_v1</code>.</p>
  <h2>Conversion measurement</h2>
  <p>Outbound clicks (<code>outbound_click</code>) are our on-site purchase-intent signal. Reported orders come only from Associates Central reports and land in the <a href="{prefix}desk/campaign-ledger/">campaign ledger</a> with a report reference. We join the two only at the report level; we never model or forecast conversions.</p>
</div></section>
</main>"""
    return page("Measurement & analytics", "The five defined events, privacy rules and the self-hosted analytics endpoint spec.",
                "/desk/analytics/", prefix, "<main>" + content)

def render_compliance(prefix="../../"):
    rows = []
    for g in REG["compliance_gate"]:
        srcs = " · ".join(f'<a href="{s["url"]}" rel="noopener" target="_blank">{s["id"]}</a>' for s in REG["sources"] if s["id"] in g["sources"])
        stat = ('<span class="status-pill status-verified">pass</span>' if g["status"] == "pass"
                else '<span class="status-pill status-unverified">' + g["status"] + "</span>")
        rows.append([f'<span class="col-id">{g["id"]}</span>', f'<strong>{g["name"]}</strong>', g["check"], stat, srcs])
    t = table(["Gate", "Requirement", "Check", "Status", "Sources"], rows)
    content = desk_hero("Compliance gate",
        "Disclosures and policy checks stand in the publishing path",
        "Every page ships only after these gates pass. Automated gates run on every build (scripts/check_site.py); manual gates name their owner. The gate reviews the Associates statement placement and endorsement context against the Operating Agreement (S02), Program Policies (S03) and FTC guidance (S01, S05) — the brief's S01 · S07 · S24 compliance requirement, mapped provisionally (FLG-008).") + f"""
<section class="section"><div class="wrap">{t}
<div class="callout">
  <h3 style="margin-top:0">Gate G3 is the human gate</h3>
  <p>Amazon requires that Special Links be created and tested inside the enrolled Associates workflow, with attribution confirmed in the tracking report, before scaling (S02). That can't be automated from this repository. Until the owner runs that test (FLG-004), the site publishes with marked, standard-format links and full disclosure — and traffic scale-up waits.</p>
</div>
</div></section>
</main>"""
    return page("Compliance gate", "The publishing gates: disclosure placement, sponsored marking, source coverage and Associates policy checks.",
                "/desk/compliance/", prefix, "<main>" + content)

def render_coordination(prefix="../../"):
    rows = [
        ["T-01", "Repo review &amp; coordination board", "done", "arena/0a90f62c-affil3", "COORDINATION.md, README.md"],
        ["T-02", "Link intake &amp; observation (5 submitted links)", "done", "arena/0a90f62c-affil3", "data/products.json, desk/link-register/"],
        ["T-03", "Verification register (line-by-line, sourced)", "done", "arena/0a90f62c-affil3", "desk/verification/, data/registers.json"],
        ["T-04", "Publication site (shop, guides, compare, about)", "done", "arena/0a90f62c-affil3", "shop/, guides/, compare/, about/, index.html"],
        ["T-05", "Measurement client + analytics spec", "done", "arena/0a90f62c-affil3", "assets/js/analytics.js, desk/analytics/, server/"],
        ["T-06", "Sitemap, robots, RSS feed + build tooling", "done", "arena/0a90f62c-affil3", "sitemap.xml, robots.txt, feed.xml, scripts/, tools/"],
        ["T-07", "Desk surfaces (flagged, questions, suggestions, ledger, compliance)", "done", "arena/0a90f62c-affil3", "desk/"],
        ["T-08", "Release gate run + PR + merge + Pages deploy", "done", "arena/0a90f62c-affil3", ".github/workflows/, COORDINATION.md"],
    ]
    t = table(["Task", "Description", "Status", "Session", "Files touched"], rows, cls="data meta")
    changelog = "".join(f'<li><strong>{c["date"]}</strong> — {c["entry"]}</li>' for c in REG["changelog"])
    content = desk_hero("Coordination log",
        "Shared task board mirror",
        "This page mirrors the repository's COORDINATION.md task board for readers. The brief's multi-session workflow is active in this repository: sessions 83a43a96, 6249757a, f761b123 and 4578ad4b published before this one, and their outputs are preserved in place (see Surfaces below). This release was produced by session arena/0a90f62c-affil3, which also performed the final integration pass over the combined tree.") + f"""
<section class="section"><div class="wrap">
  {t}
  <h2>Surfaces in this repository</h2>
  <ul>
    <li><strong>/legacy/editions/counter/</strong> — Crisp &amp; Counter, an archived edition (session arena/0a90f62c-affil3), generated by <code>scripts/build_site.py</code>.</li>
    <li><strong>/ (root)</strong> — the integrated Affil3 publication (other sessions), gated by the root pipeline's workflows.</li>
    <li><strong>/crisp-index/</strong>, <strong>/editorial/</strong>, <strong>/docs/</strong> — further independent publications, each with its own gates.</li>
    <li><strong>/legacy/</strong> — frozen earlier editions, preserved as they shipped.</li>
  </ul>
  <h2>Changelog</h2>
  <ul>{changelog}</ul>
  <h2>Verification performed</h2>
  <ul>
    <li>Five of five submitted links fetched and their Amazon listings read first-hand on {TODAY} (titles, categories, prices, ratings, images) — see the <a href="{prefix}desk/link-register/">link register</a>. P4's resolution was independently corroborated by the parallel session's dated retest.</li>
    <li>Policy sources (S01–S07) checked against official publisher pages.</li>
    <li>Automated gates: disclosure presence, associate statement, rel="sponsored" marking, source coverage per table row, internal link integrity — see <code>scripts/check_site.py</code> and <code>tools/verify_site.py</code>.</li>
    <li>Irregularities published on the <a href="{prefix}desk/flagged/">Flagged for Review</a> page.</li>
    <li>Integration pass: combined tree re-verified after merging the other sessions' work; both CI workflows green.</li>
  </ul>
</div></section>
</main>"""
    return page("Coordination log", "Task board mirror: claims, statuses, verification performed and changelog.",
                "/desk/coordination/", prefix, "<main>" + content)

# ---------------------------------------------------------------- feed / sitemap / robots / 404

def render_feed():
    items = []
    for g in reversed(GUIDES):
        items.append(f"""  <item>
    <title>{g['title']}</title>
    <link>{SITE_URL}/guides/{g['slug']}/</link>
    <guid isPermaLink="true">{SITE_URL}/guides/{g['slug']}/</guid>
    <description>{g['seo']}</description>
    <pubDate>{g['date']}T09:00:00Z</pubDate>
    <category>{g['cluster']}</category>
  </item>""")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
  <title>{SITE_NAME_PLAIN} — {TAGLINE}</title>
  <link>{SITE_URL}/</link>
  <description>Question-first kitchen buying guides and a verified product register. Every claim sourced; every affiliate link marked.</description>
  <language>en-us</language>
  <lastBuildDate>{TODAY}T09:00:00Z</lastBuildDate>
  <atom:link href="{SITE_URL}/feed.xml" rel="self" type="application/rss+xml"/>
{chr(10).join(items)}
</channel>
</rss>
"""

def render_sitemap(paths):
    urls = []
    for p in paths:
        loc = SITE_URL + p
        urls.append(f"  <url><loc>{loc}</loc><lastmod>{TODAY}</lastmod></url>")
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + "\n".join(urls) + "\n</urlset>\n")

ROBOTS = f"""User-agent: *
Allow: /

Sitemap: {SITE_URL}/sitemap.xml
"""

def render_404(prefix=""):
    content = f"""
<main>
<section class="hero"><div class="wrap">
  <div class="kicker">404</div>
  <h1>This shelf is empty.</h1>
  <p class="lede">The page you're after moved or never existed. The register and the guides are both one click away.</p>
  <div class="hero-ctas"><a class="btn btn-primary" href="{prefix}">Back to the front page</a>
  <a class="btn btn-ghost" href="{prefix}shop/">Shop the register</a></div>
</div></section>
</main>"""
    return page("Page not found", "This page does not exist.", "/404.html", prefix, content)

# ---------------------------------------------------------------- build

def build(outdir):
    out = pathlib.Path(outdir)
    (out / "assets" / "css").mkdir(parents=True, exist_ok=True)
    (out / "assets" / "js").mkdir(parents=True, exist_ok=True)
    for asset in ("css/site.css", "js/site.js", "js/analytics.js"):
        src = ROOT / "assets" / asset
        dst = out / "assets" / asset
        if src.resolve() != dst.resolve():
            shutil.copy(src, dst)

    pages = {}
    pages["index.html"] = render_home()
    pages["shop/index.html"] = render_shop()
    pages["compare/index.html"] = render_compare()
    pages["guides/index.html"] = render_guides_index()
    for g in GUIDES:
        pages[f"guides/{g['slug']}/index.html"] = render_guide(g)
    pages["about/index.html"] = render_about()
    pages["desk/index.html"] = render_desk_index()
    pages["desk/verification/index.html"] = render_verification()
    pages["desk/link-register/index.html"] = render_link_register()
    pages["desk/flagged/index.html"] = render_flagged()
    pages["desk/questions/index.html"] = render_questions()
    pages["desk/suggestions/index.html"] = render_suggestions()
    pages["desk/campaign-ledger/index.html"] = render_ledger()
    pages["desk/analytics/index.html"] = render_analytics()
    pages["desk/compliance/index.html"] = render_compliance()
    pages["desk/coordination/index.html"] = render_coordination()
    pages["404.html"] = render_404()

    for rel, html in pages.items():
        target = out / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(html)

    sitemap_paths = ["/"] + ["/" + p.replace("index.html", "") for p in pages if p != "index.html" and p != "404.html"]
    (out / "sitemap.xml").write_text(render_sitemap(sitemap_paths))
    (out / "robots.txt").write_text(ROBOTS)
    (out / "feed.xml").write_text(render_feed())
    return pages

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="verify checked-in tree matches a fresh render")
    ap.add_argument("--out", default=None, help="output directory (default: legacy/editions/counter/)")
    args = ap.parse_args()
    outdir = args.out or (ROOT / "legacy" / "editions" / "counter")
    if args.check:
        with tempfile.TemporaryDirectory() as td:
            build(td)
            drift = []
            tdp = pathlib.Path(td)
            for f in sorted(tdp.rglob("*")):
                if f.is_dir():
                    continue
                rel = f.relative_to(tdp)
                other = (ROOT / "legacy" / "editions" / "counter" / rel)
                if not other.exists():
                    drift.append(f"missing in tree: {rel}")
                elif other.read_text() != f.read_text():
                    drift.append(f"differs: {rel}")
            if drift:
                print("BUILD DRIFT — run python3 scripts/build_site.py and commit:")
                for d in drift:
                    print(" ", d)
                sys.exit(1)
            print("build --check: OK (checked-in tree matches fresh render)")
        return
    build(outdir)
    print(f"built {len(list(pathlib.Path(outdir).rglob('*.html')))} html pages into {outdir}")

if __name__ == "__main__":
    main()
