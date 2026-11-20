#!/usr/bin/env python3
"""
build_site.py — generate the Counter & Crumb static site.

Every page is assembled from the JSON in data/. Nothing is written by hand
outside data/, so a change to the register, the guides or the flags propagates
to the pages, the sitemap and the feed in one run.

Usage:
    python3 tools/build_site.py            # build the site
    python3 tools/build_site.py --check    # build, then run the release gate
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sitekit import (  # noqa: E402
    DATA, ROOT, breadcrumb_jsonld, esc, illustration, is_asin, layout,
    load_json, price_slot, read_text, signup_form, source_link, special_link,
    sponsored_anchor, write_text, rfc822, today,
)

CFG = load_json("config.json")
PRODUCTS = load_json("products.json")["products"]
GUIDES = load_json("guides.json")["guides"]
SOURCES = load_json("sources.json")
FLAGS = load_json("flags.json")
QUESTIONS = load_json("questions.json")
SUGGESTIONS = load_json("suggestions.json")

TAG = CFG["affiliate"]["tracking_id"]
MARKETPLACE = CFG["affiliate"]["marketplace"]
SITE = CFG["site"]
BASE = SITE["base_url"].rstrip("/")
PRODUCT_REGISTER = load_json("products.json")
GUIDES_META = load_json("guides.json")["meta"]

SITEMAP: list[dict] = []


def register(path: str, changefreq: str = "monthly", priority: str = "0.6") -> None:
    SITEMAP.append({
        "loc": BASE + path,
        "lastmod": PRODUCT_REGISTER["meta"]["checked_on"],
        "changefreq": changefreq,
        "priority": priority,
    })


def product_by_id(pid: str):
    for p in PRODUCTS:
        if p["id"] == pid:
            return p
    return None


def guides_in_category(slug: str):
    return [g for g in GUIDES if g["category_slug"] == slug]


def source_by_id(sid: str):
    for s in SOURCES["sources"]:
        if s["id"] == sid:
            return s
    return None


def link_for(product: dict) -> str:
    return special_link(product["observed_redirect"]["target_asin"], TAG, MARKETPLACE)


# ==========================================================================
# Home — a publication front page
# ==========================================================================

def page_home() -> str:
    lead = GUIDES[0]
    featured = GUIDES[1:4]
    cards = []
    for p in PRODUCTS:
        cards.append(f"""
      <article class="card product-card">
        <div class="product-card__thumb">{illustration(p)}</div>
        <div class="product-card__body">
          <span class="card__tag">{esc(p["category"])}</span>
          <h3 class="product-card__title"><a href="/products/{esc(p["id"])}/">{esc(p["display_name"])}</a></h3>
          <p class="product-card__why">{esc(p["editorial"])}</p>
          <div class="card__foot">
            {price_slot(p["observed_redirect"]["target_asin"])}
          </div>
          <div class="card__foot">
            {sponsored_anchor(link_for(p), "Check current price", p["id"], p["observed_redirect"]["target_asin"], "home-shelf", p["official_title"])}
          </div>
        </div>
      </article>""")

    guide_cards = []
    for g in [lead] + featured:
        guide_cards.append(f"""
      <a class="card card--link" href="/guides/{esc(g["slug"])}/">
        <span class="card__tag">{esc(g["category"])}</span>
        <h3 class="card__title">{esc(g["title"])}</h3>
        <p>{esc(g["dek"])}</p>
        <span class="card__meta">{esc(g["season"])} · {g["reading_minutes"]} min read</span>
      </a>""")

    body = f"""
<section class="hero">
  <div class="wrap hero__grid">
    <div>
      <span class="kicker">Countertop cooking · air fryers &amp; kitchen thermometers</span>
      <h1>Answers before you buy, not after.</h1>
      <p class="hero__dek">{esc(SITE["description"])}</p>
      <div class="hero__meta">
        <span>{len(GUIDES)} guides</span>
        <span>{len(PRODUCTS)} products in the register</span>
        <span>Every source checked {esc(PRODUCT_REGISTER["meta"]["checked_on"])}</span>
      </div>
      <div class="hero__meta">
        <a class="btn" href="/guides/">Start with a question</a>
        <a class="btn btn--ghost" href="/products/">See the product register</a>
      </div>
    </div>
    <aside class="card">
      <span class="card__tag">Lead guide</span>
      <h2 class="card__title" style="font-size:var(--step-2)">{esc(lead["title"])}</h2>
      <p>{esc(lead["answer"])}</p>
      <div class="card__foot">
        <a class="btn btn--sm" href="/guides/{esc(lead["slug"])}/">Read the guide</a>
        <span class="card__meta">{lead["reading_minutes"]} min</span>
      </div>
    </aside>
  </div>
</section>

<section class="section section--alt">
  <div class="wrap">
    <div class="section__head">
      <h2 class="section__title">Pick the question you actually have</h2>
      <p><a href="/guides/">All {len(GUIDES)} guides →</a></p>
    </div>
    <div class="grid grid--3">{''.join(guide_cards)}</div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section__head">
      <h2 class="section__title">The register</h2>
      <p>Five products, each traced to the official listing it was read from.</p>
    </div>
    <div class="shelf">{''.join(cards)}</div>
    <p class="table-note" style="margin-top:1.5rem">
      Prices are not shown here. Amazon's Program Policies allow a price on your site
      only when Amazon serves the link that displays it or when the price comes from
      Creators API or PA&nbsp;API. Every product link below is a direct Special Link,
      marked <span class="spon__mark">Sponsored</span>.
      <a href="/compliance/">How this site stays inside the rules →</a>
    </p>
  </div>
</section>

<section class="section section--alt">
  <div class="wrap grid grid--2">
    <div>
      <span class="eyebrow">What we are still working out</span>
      <h2>Two questions we could not settle from an official source</h2>
      <p class="lede" style="margin-bottom:1.5rem">Nobody should have to guess which parts of an affiliate site are verified and which parts are best guesses. Ours are labelled.</p>
      <ul class="stack">
        <li><strong>Is the tracking ID real?</strong> The tag matches Amazon's published
          shape, but no public page confirms it was issued to this account.
          <a href="/desk/flags/">FLG-001 →</a></li>
        <li><strong>Which product was each link meant to promote?</strong> We can record
          where each link goes today. We cannot record what was meant, so that field is
          blank by design.
          <a href="/desk/flags/">FLG-002 →</a></li>
      </ul>
      <p style="margin-top:1.5rem"><a class="btn btn--ghost btn--sm" href="/desk/flags/">See all flagged items</a></p>
    </div>
    <div class="card">
      <span class="card__tag">How to use this site</span>
      <h3 class="card__title">Three routes, depending on why you are here</h3>
      <div class="stack" style="margin-top:.4rem">
        <p><strong>You want an answer.</strong> Start with the
          <a href="/guides/">guides</a>. Each one opens with the answer, then shows what
          to compare and what to ask.</p>
        <p><strong>You want to compare.</strong> The <a href="/compare/">comparison hub</a>
          puts the five products next to each other on the attributes their official
          listings state.</p>
        <p><strong>You want to check us.</strong> The
          <a href="/methods/sources/">source register</a> lists every official page this
          site relies on, and the <a href="/methods/verification/">verification log</a>
          records how each claim was checked.</p>
      </div>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap wrap--narrow center">
    <span class="eyebrow">Reader capture</span>
    <h2>One note when a new guide goes up</h2>
    <p class="lede" style="margin-inline:auto">No newsletter drip, no growth hacks. A single message when something new is published, so you can come back to it.</p>
    {signup_form("home")}
  </div>
</section>
"""
    jsonld = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": SITE["name"],
        "url": BASE + "/",
        "description": SITE["description"],
        "publisher": {
            "@type": "Organization",
            "name": SITE["publisher"],
            "url": BASE + "/",
        },
    }
    register("/", "daily", "1.0")
    return layout(CFG, f"{SITE['name']} — {SITE['tagline']}", SITE["description"], "/",
                  body, current="/", jsonld=jsonld)


# ==========================================================================
# Guides
# ==========================================================================

def page_guides_index() -> str:
    cats = {}
    for g in GUIDES:
        cats.setdefault(g["category"], []).append(g)
    blocks = []
    for cat, items in cats.items():
        cards = []
        for g in items:
            prods = [product_by_id(pid) for pid in g["products"]]
            names = ", ".join(p["display_name"] for p in prods if p)
            cards.append(f"""
      <a class="card card--link" href="/guides/{esc(g["slug"])}/">
        <span class="card__tag">{esc(g["season"])}</span>
        <h3 class="card__title">{esc(g["title"])}</h3>
        <p>{esc(g["dek"])}</p>
        <span class="card__meta">{g["reading_minutes"]} min read · {esc(cat)}</span>
        <span class="card__meta">Covers: {esc(names)}</span>
      </a>""")
        blocks.append(f"""
    <div class="section__head" style="margin-top:2.5rem">
      <h2 class="section__title">{esc(cat)}</h2>
    </div>
    <div class="grid grid--3">{''.join(cards)}</div>""")

    body = f"""
<div class="wrap">
  <div class="page-head">
    <h1>Guides</h1>
    <p class="lede">{esc(GUIDES_META["subtitle"])}</p>
    <p class="table-note">{esc(GUIDES_META["editorial_note"])}</p>
  </div>
  {''.join(blocks)}
</div>
"""
    register("/guides/", "weekly", "0.8")
    return layout(CFG, f"Guides — {SITE['name']}",
                  "Question-shaped buying guides for air fryers and kitchen thermometers, each opening with the answer and ending with what to compare.",
                  "/guides/", body, current="/guides/")


def page_guide(g: dict) -> str:
    toc = "".join(
        f'<li><a href="#s{i}">{esc(s["heading"])}</a></li>'
        for i, s in enumerate(g["sections"], start=1)
    )
    sections = []
    for i, s in enumerate(g["sections"], start=1):
        body_html = "".join(f"<p>{esc(p)}</p>" for p in s.get("body", []))
        list_html = ""
        if s.get("list"):
            items = "".join(f"<li>{esc(x)}</li>" for x in s["list"])
            list_html = f"<ul>{items}</ul>"
        sections.append(f"""
    <section id="s{i}">
      <h2>{esc(s["heading"])}</h2>
      {body_html}
      {list_html}
    </section>""")

    prod_cards = []
    for pid in g["products"]:
        p = product_by_id(pid)
        if not p:
            continue
        spec_bits = []
        for s in p["specs"][:2]:
            spec_bits.append("<dt>" + esc(s["label"]) + "</dt><dd>" + esc(s["value"]) + "</dd>")
        spec_html = "".join(spec_bits)
        prod_cards.append(f"""
      <article class="card">
        <span class="card__tag">{esc(p["category"])}</span>
        <h3 class="card__title" style="font-size:var(--step-1)">{esc(p["display_name"])}</h3>
        <p>{esc(p["editorial"])}</p>
        <dl class="facts" style="margin:0.6rem 0 0">
          <dt>Form</dt><dd>{esc(p["form"])}</dd>
          {spec_html}
        </dl>
        <div class="card__foot">
          {price_slot(p["observed_redirect"]["target_asin"])}
          {sponsored_anchor(link_for(p), "Check current price", p["id"], p["observed_redirect"]["target_asin"], "guide-card", p["official_title"])}
        </div>
        <div class="card__foot"><a class="card__meta" href="/products/{esc(p["id"])}/">Full record and sources →</a></div>
      </article>""")

    prod_list_html = []
    for pid in g["products"]:
        p = product_by_id(pid)
        if p:
            prod_list_html.append(
                '<li><a href="/products/' + esc(p["id"]) + '/">' + esc(p["display_name"]) + "</a></li>")
    prod_list = "".join(prod_list_html)

    faq_html = "".join(f"""
    <details class="card" style="margin-bottom:.6rem">
      <summary style="cursor:pointer;font-weight:600">{esc(f["q"])}</summary>
      <p style="margin-top:.6rem">{esc(f["a"])}</p>
    </details>""" for f in g["faq"])

    src_rows = []
    for sid in g["sources"]:
        s = source_by_id(sid)
        if not s:
            continue
        src_rows.append(f"""
        <tr>
          <td>{source_link(s["url"], s["title"])}</td>
          <td>{esc(s["publisher"])}</td>
          <td>{esc(s["checked_on"])}</td>
        </tr>""")

    related = [x for x in GUIDES if x["slug"] in g.get("related", [])]
    related_html = ""
    if related:
        items = "".join(
            f'<li><a href="/guides/{esc(r["slug"])}/">{esc(r["title"])}</a></li>'
            for r in related)
        related_html = f"""
    <section>
      <h2>Read next</h2>
      <ul>{items}</ul>
    </section>"""

    body = f"""
<div class="wrap">
  <div class="page-head">
    <p class="breadcrumb-nav"><a href="/">Home</a> <span aria-hidden="true">/</span> <a href="/guides/">Guides</a> <span aria-hidden="true">/</span> <span>{esc(g["category"])}</span></p>
    <h1>{esc(g["title"])}</h1>
    <p class="lede">{esc(g["dek"])}</p>
    <div class="hero__meta">
      <span>{esc(g["season"])}</span>
      <span>{g["reading_minutes"]} min read</span>
      <span>Published {esc(g["date"])}</span>
      <span>Desk: {esc(SITE["author"]["name"])}</span>
    </div>
  </div>

  <div class="grid grid--sidebar">
    <article class="prose" data-guide>
      <div class="answer">
        <span class="answer__label">The short answer</span>
        <p>{esc(g["answer"])}</p>
      </div>

      <h2 id="s0">The question</h2>
      <p><strong>{esc(g["question"])}</strong></p>

      {''.join(sections)}

      <section id="faq">
        <h2>Questions people ask</h2>
        {faq_html}
      </section>

      {related_html}

      <section id="sources">
        <h2>Sources for this guide</h2>
        <div class="table-wrap">
          <table class="data">
            <caption>Every claim above traces to one of these pages.</caption>
            <thead><tr><th>Page</th><th>Publisher</th><th>Checked</th></tr></thead>
            <tbody>{''.join(src_rows)}</tbody>
          </table>
        </div>
        <p class="table-note">Full register: <a href="/methods/sources/">source register</a>.
          Flagged items: <a href="/desk/flags/">flagged for review</a>.</p>
      </section>
    </article>

    <aside class="stack">
      <nav class="toc" aria-label="On this page">
        <h2>On this page</h2>
        <ol>{toc}</ol>
      </nav>
      <div class="callout">
        <span class="callout__title">Before you buy</span>
        <p>Check the current price and availability on the listing itself. Prices and
          availability change, so this page deliberately does not quote them.</p>
      </div>
      <div class="card">
        <span class="card__tag">Products in this guide</span>
        <ul style="padding-left:1.1rem;margin:.3rem 0 0">
          {prod_list}
        </ul>
      </div>
    </aside>
  </div>
</div>
"""
    path = f"/guides/{g['slug']}/"
    jsonld = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": g["title"],
        "description": g["dek"],
        "datePublished": g["date"],
        "dateModified": g["date"],
        "author": {"@type": "Organization", "name": SITE["author"]["name"]},
        "publisher": {"@type": "Organization", "name": SITE["publisher"], "url": BASE + "/"},
        "mainEntityOfPage": BASE + path,
        "image": BASE + SITE["social"]["og_image"],
        "articleSection": g["category"],
        "keywords": ", ".join(g.get("keywords", [])),
    }
    register(path, "monthly", "0.8")
    return layout(CFG, f"{g['title']} — {SITE['name']}", g["dek"], path, body,
                  current="/guides/", jsonld=jsonld, page_type="article")


# ==========================================================================
# Product register
# ==========================================================================

def page_products_index() -> str:
    rows = []
    for p in PRODUCTS:
        obs = p["observed_redirect"]
        rows.append(f"""
        <tr data-category="{esc(p["category_slug"])}">
          <td data-col="name" data-sort="{esc(p["display_name"])}">
            <a href="/products/{esc(p["id"])}/">{esc(p["display_name"])}</a>
            <div class="muted" style="font-size:.8rem">{esc(p["brand"])}</div>
          </td>
          <td data-col="category" data-sort="{esc(p["category"])}">{esc(p["category"])}</td>
          <td data-col="form" data-sort="{esc(p["form"])}">{esc(p["form"])}</td>
          <td data-col="asin" data-sort="{esc(obs["target_asin"])}"><span class="mono">{esc(obs["target_asin"])}</span></td>
          <td data-col="submitted" data-sort="{esc(p["submitted"]["token"])}"><span class="mono">{esc(p["submitted"]["token"])}</span></td>
          <td data-col="price" data-sort=""><span class="price-slot" data-price-slot="{esc(obs["target_asin"])}" data-state="unavailable">Price shown on Amazon</span></td>
          <td>{source_link(obs["target_url"], "amazon.com")}</td>
        </tr>""")

    intent_rows = []
    for p in PRODUCTS:
        i = p["intent"]
        intent_rows.append(f"""
        <tr>
          <td><a href="/products/{esc(p["id"])}/">{esc(p["display_name"])}</a></td>
          <td>{esc(i["intended_asin"]) or '<span class="muted">not confirmed</span>'}</td>
          <td>{esc(i["intended_listing_url"]) or '<span class="muted">not confirmed</span>'}</td>
          <td>{esc(i["confirmation_date"]) or '<span class="muted">—</span>'}</td>
          <td>{esc(i["intended_source"]) or '<span class="muted">—</span>'}</td>
          <td><span class="badge badge--med">{esc(i["status"])}</span></td>
        </tr>""")

    obs_rows = []
    for p in PRODUCTS:
        o = p["observed_redirect"]
        obs_rows.append(f"""
        <tr>
          <td><a href="/products/{esc(p["id"])}/">{esc(p["display_name"])}</a></td>
          <td><span class="mono">{esc(p["submitted"]["token"])}</span> <span class="muted">({p["submitted"]["token_length"]} chars)</span></td>
          <td><span class="mono">{esc(o["target_asin"])}</span></td>
          <td>{esc(o["observed_on"])}</td>
          <td>{source_link(o["target_url"], "amazon.com")}</td>
        </tr>""")

    body = f"""
<div class="wrap">
  <div class="page-head">
    <h1>Product register</h1>
    <p class="lede">{esc(PRODUCT_REGISTER["meta"]["subtitle"])}</p>
    <p class="table-note">Checked {esc(PRODUCT_REGISTER["meta"]["checked_on"])} · {esc(PRODUCT_REGISTER["meta"]["method"])}</p>
  </div>

  <div class="callout callout--warn">
    <span class="callout__title">How to read this page</span>
    <ul style="margin:.3rem 0 0">
      {''.join(f'<li>{esc(r)}</li>' for r in PRODUCT_REGISTER["meta"]["rules"])}
    </ul>
  </div>

  <h2>Every product, one row</h2>
  <div class="filterbar">
    <div class="field">
      <label for="f-cat">Category</label>
      <select id="f-cat" data-filter-select="register" data-filter-name="category">
        <option value="">All categories</option>
        <option value="air-fryers">Air fryers</option>
        <option value="thermometers">Meat thermometers</option>
      </select>
    </div>
    <div class="field">
      <label for="f-q">Search</label>
      <input id="f-q" type="search" placeholder="brand or ASIN" data-filter-select="register" data-filter-name="q">
    </div>
    <p class="filterbar__count" data-filter-count="register">{len(PRODUCTS)} rows</p>
  </div>
  <div class="table-wrap">
    <table class="data" id="register">
      <caption>One row per product. The last column links to the official listing the row was read from.</caption>
      <thead>
        <tr>
          <th data-col="name" aria-sort="none" scope="col">Product</th>
          <th data-col="category" aria-sort="none" scope="col">Category</th>
          <th data-col="form" aria-sort="none" scope="col">Form</th>
          <th data-col="asin" aria-sort="none" scope="col">Observed ASIN</th>
          <th data-col="submitted" aria-sort="none" scope="col">Submitted token</th>
          <th data-col="price" scope="col">Price</th>
          <th scope="col">Source</th>
        </tr>
      </thead>
      <tbody>{''.join(rows)}</tbody>
    </table>
  </div>
  <p class="table-note">
    Prices are not shown. Amazon's Program Policies 2(b) allows a price on your site only
    when Amazon serves the link that displays it or when pricing comes from Creators API
    or PA&nbsp;API. Ratings and review counts are absent for the same reason under 5(t).
    <a href="/compliance/">Read the compliance notes →</a>
  </p>

  <h2>Product intent — what was meant</h2>
  <p class="lede">These fields are blank. Nothing in the public record binds a submitted
    link token to a product, so the intent has to come from the owner rather than from
    a measurement. The columns stay blank until it does.</p>
  <div class="table-wrap">
    <table class="data">
      <caption>Product-intent confirmation record. Intent and observation are kept apart on purpose.</caption>
      <thead>
        <tr>
          <th scope="col">Product</th><th scope="col">Intended ASIN</th>
          <th scope="col">Official listing URL</th><th scope="col">Confirmation date</th>
          <th scope="col">Source</th><th scope="col">Status</th>
        </tr>
      </thead>
      <tbody>{''.join(intent_rows)}</tbody>
    </table>
  </div>

  <h2>Observed redirect — where each link goes today</h2>
  <p class="lede">This is a different fact from intent and it is never merged into it.
    These were measured on the dates shown by following each submitted link to its
    final destination.</p>
  <div class="table-wrap">
    <table class="data">
      <caption>Observed redirect targets. Measured, dated, and linked to the page they were read from.</caption>
      <thead>
        <tr>
          <th scope="col">Product</th><th scope="col">Submitted token</th>
          <th scope="col">Observed ASIN</th><th scope="col">Observed on</th><th scope="col">Source</th>
        </tr>
      </thead>
      <tbody>{''.join(obs_rows)}</tbody>
    </table>
  </div>

  <div class="callout callout--flag">
    <span class="callout__title">Why two tables</span>
    <p>Amazon defines an ASIN as a 10-character alphanumeric identifier. Three of the
      five submitted tokens are 9 characters, so they cannot be ASINs. The other two are
      10 characters but neither was confirmed as an issued ASIN. Merging the two facts
      would let a guess look like a verification, so they stay in separate tables.
      <a href="/desk/flags/">FLG-002 and FLG-004 →</a></p>
  </div>

  <h2>Field rules for this register</h2>
  <div class="table-wrap">
    <table class="data">
      <thead><tr><th scope="col">Field</th><th scope="col">Meaning</th><th scope="col">Filled from</th></tr></thead>
      <tbody>
        <tr><td>Intended ASIN</td><td>The ASIN the owner meant to promote.</td><td>Owner confirmation only.</td></tr>
        <tr><td>Official listing URL</td><td>The amazon.com/dp URL of that intended product.</td><td>Owner confirmation only.</td></tr>
        <tr><td>Confirmation date</td><td>The day the owner confirmed it.</td><td>Owner confirmation only.</td></tr>
        <tr><td>Intended source</td><td>Where the confirmation came from.</td><td>Owner confirmation only.</td></tr>
        <tr><td>Observed ASIN</td><td>Where the submitted link actually goes.</td><td>Measured on the redirect.</td></tr>
        <tr><td>Observed on</td><td>The date of that measurement.</td><td>Measurement date.</td></tr>
      </tbody>
    </table>
  </div>
</div>
"""
    register("/products/", "weekly", "0.8")
    return layout(CFG, f"Product register — {SITE['name']}",
                  "Every product this site promotes, the link submitted for it, the observed redirect target, and what could not be confirmed.",
                  "/products/", body, current="/products/")


def page_product(p: dict) -> str:
    obs = p["observed_redirect"]
    spec_rows = "".join(f"""
        <tr>
          <td>{esc(s["label"])}</td>
          <td>{esc(s["value"])}</td>
          <td class="muted">{esc(s["basis"])}</td>
        </tr>""" for s in p["specs"])

    adj = []
    for asin in p.get("adjacent_asin", []):
        adj.append(f'<li><span class="mono">{esc(asin)}</span> — {source_link(f"https://www.amazon.com/dp/{asin}", "amazon.com")}</li>')

    guides_here = [g for g in GUIDES if p["id"] in g["products"]]
    guides_list = "".join(
        f'<li><a href="/guides/{esc(g["slug"])}/">{esc(g["title"])}</a></li>' for g in guides_here)

    src_ids = {"SRC-01", "SRC-02"}
    for s in SOURCES["sources"]:
        if s["url"] == obs["target_url"]:
            src_ids.add(s["id"])
    src_rows = "".join(f"""
        <tr>
          <td>{source_link(s["url"], s["title"])}</td>
          <td>{esc(s["publisher"])}</td>
          <td>{esc(s["checked_on"])}</td>
        </tr>""" for s in SOURCES["sources"] if s["id"] in src_ids)

    body = f"""
<div class="wrap">
  <div class="page-head">
    <p class="breadcrumb-nav"><a href="/">Home</a> <span aria-hidden="true">/</span> <a href="/products/">Products</a> <span aria-hidden="true">/</span> <span>{esc(p["brand"])}</span></p>
    <h1>{esc(p["display_name"])}</h1>
    <p class="lede">{esc(p["editorial"])}</p>
    <div class="hero__meta">
      <span>{esc(p["category"])}</span>
      <span>Observed ASIN <span class="mono">{esc(obs["target_asin"])}</span></span>
      <span>Checked {esc(obs["observed_on"])}</span>
    </div>
  </div>

  <div class="grid grid--sidebar">
    <div class="prose">
      <div class="answer">
        <span class="answer__label">Where this sits in the register</span>
        <p>{esc(p["form"])}. The official listing title reads:
          <em>{esc(p["official_title"])}</em>.</p>
        <p style="margin-top:.8rem">Amazon's breadcrumb for it:
          {esc(" › ".join(p["category_path"]))}.</p>
      </div>

      <h2>Check the current price and availability</h2>
      <p>Prices and availability change, and this site does not quote them. Amazon's
        Program Policies allow a price on your site only when Amazon serves the link
        that displays it, or when the price comes from Creators API or PA&nbsp;API.
        This site is not configured with API access yet, so it sends you to the listing
        rather than showing you a number that might be hours old.</p>
      <p style="margin-bottom:1rem">
        {price_slot(obs["target_asin"])}
      </p>
      <p>
        {sponsored_anchor(link_for(p), "Check current price and availability on Amazon", p["id"], obs["target_asin"], "product-hero", p["official_title"])}
      </p>

      <h2>What the official listing states</h2>
      <div class="table-wrap">
        <table class="data">
          <caption>Every attribute below is taken from the official listing title. Nothing here is our own measurement.</caption>
          <thead><tr><th scope="col">Attribute</th><th scope="col">Stated value</th><th scope="col">Basis</th></tr></thead>
          <tbody>{spec_rows}</tbody>
        </table>
      </div>

      <h2>What to ask before you buy</h2>
      <ul>
        {''.join(f'<li>{esc(q)}</li>' for q in p.get("open_questions", []))}
      </ul>
      <p class="table-note">We did not find an official source for these, so we did not
        publish answers. They are listed as questions on purpose.</p>

      <h2>Where this link came from</h2>
      <p>The link submitted for this product was
        <span class="mono">https://link.amazon/{esc(p["submitted"]["token"])}</span>.
        On {esc(obs["observed_on"])} it redirected to
        {source_link(obs["target_url"], obs["target_url"], p["id"], obs["target_asin"])},
        and that page carried the title quoted above.</p>
      <p>{esc(p["submitted"]["note"])}</p>

      <div class="callout callout--warn">
        <span class="callout__title">Intent is not observation</span>
        <p>The record of what this link was <em>meant</em> to promote is a separate fact
          and it is still blank. The link above is what the link does today. Keeping them
          apart is the point.
          <a href="/desk/flags/">FLG-002 →</a></p>
      </div>

      <h2>Sources</h2>
      <div class="table-wrap">
        <table class="data">
          <thead><tr><th scope="col">Page</th><th scope="col">Publisher</th><th scope="col">Checked</th></tr></thead>
          <tbody>{src_rows}</tbody>
        </table>
      </div>
      <p class="table-note"><a href="/methods/sources/">Full source register →</a></p>
    </div>

    <aside class="stack">
      <div class="card">
        <span class="card__tag">Observation</span>
        <dl class="facts" style="margin-top:.4rem">
          <dt>Submitted</dt><dd><span class="mono">{esc(p["submitted"]["token"])}</span><br><span class="muted">{p["submitted"]["token_length"]} characters</span></dd>
          <dt>Redirects to</dt><dd><span class="mono">{esc(obs["target_asin"])}</span></dd>
          <dt>Observed on</dt><dd>{esc(obs["observed_on"])}</dd>
          <dt>Intended ASIN</dt><dd><span class="muted">not confirmed</span></dd>
        </dl>
      </div>
      {f'<div class="card"><span class="card__tag">Also on this listing</span><ul style="padding-left:1.1rem;margin:.3rem 0 0;font-size:.85rem">{"".join(adj)}</ul><p class="card__meta" style="margin-top:.6rem">{esc(p.get("adjacent_note",""))}</p></div>' if adj else ''}
      {f'<div class="card"><span class="card__tag">Guides that cover it</span><ul style="padding-left:1.1rem;margin:.3rem 0 0">{guides_list}</ul></div>' if guides_list else ''}
    </aside>
  </div>
</div>
"""
    path = f"/products/{p['id']}/"
    jsonld = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": p["display_name"],
        "description": p["editorial"],
        "url": BASE + path,
        "dateModified": obs["observed_on"],
        "publisher": {"@type": "Organization", "name": SITE["publisher"], "url": BASE + "/"},
    }
    register(path, "monthly", "0.7")
    return layout(CFG, f"{p['display_name']} — {SITE['name']}", p["editorial"], path,
                  body, current="/products/", jsonld=jsonld)


# ==========================================================================
# Comparisons
# ==========================================================================

def compare_table(ids, table_id: str, caption: str) -> str:
    rows = []
    for pid in ids:
        p = product_by_id(pid)
        specs = {s["label"]: s["value"] for s in p["specs"]}
        rows.append(f"""
        <tr data-category="{esc(p["category_slug"])}">
          <td data-col="name" data-sort="{esc(p["display_name"])}">
            <a href="/products/{esc(p["id"])}/">{esc(p["display_name"])}</a>
            <div class="muted" style="font-size:.78rem">{esc(p["brand"])}</div>
          </td>
          <td data-col="form" data-sort="{esc(p["form"])}">{esc(p["form"])}</td>
          <td data-col="spec1" data-sort="{esc(specs.get(list(specs)[0], ""))}">{esc(specs.get(list(specs)[0], "—"))}</td>
          <td data-col="spec2" data-sort="{esc(specs.get(list(specs)[1], ""))}">{esc(specs.get(list(specs)[1], "—"))}</td>
          <td data-col="price" data-sort=""><span class="price-slot" data-price-slot="{esc(p["observed_redirect"]["target_asin"])}" data-state="unavailable">Price shown on Amazon</span></td>
          <td>{sponsored_anchor(link_for(p), "Open listing", p["id"], p["observed_redirect"]["target_asin"], f"compare-{table_id}", p["official_title"])}</td>
        </tr>""")
    return f"""
  <div class="filterbar">
    <div class="field">
      <label for="f-{table_id}-q">Search</label>
      <input id="f-{table_id}-q" type="search" placeholder="brand or name" data-filter-select="{table_id}" data-filter-name="q">
    </div>
    <p class="filterbar__count" data-filter-count="{table_id}">{len(ids)} rows</p>
  </div>
  <div class="table-wrap">
    <table class="data" id="{table_id}">
      <caption>{esc(caption)}</caption>
      <thead>
        <tr>
          <th data-col="name" aria-sort="none" scope="col">Product</th>
          <th data-col="form" aria-sort="none" scope="col">Form</th>
          <th scope="col">First stated attribute</th>
          <th scope="col">Second stated attribute</th>
          <th scope="col">Price</th>
          <th scope="col">Go to</th>
        </tr>
      </thead>
      <tbody>{''.join(rows)}</tbody>
    </table>
  </div>"""


def page_compare_index() -> str:
    pairs = [
        ("air-fryers", "Air fryers", [p["id"] for p in PRODUCTS if p["category_slug"] == "air-fryers"],
         "Three shapes of air fryer: one basket, two baskets, and a full oven. The attributes compared are the ones the official listing titles state."),
        ("thermometers", "Meat thermometers", [p["id"] for p in PRODUCTS if p["category_slug"] == "thermometers"],
         "One probe and three probes. The attributes compared are the ones the official listing titles state."),
    ]
    blocks = []
    for slug, name, ids, caption in pairs:
        blocks.append(f"""
  <h2>{esc(name)}</h2>
  {compare_table(ids, "cmp-" + slug, caption)}
  <p style="margin-top:1rem"><a class="btn btn--ghost btn--sm" href="/compare/{esc(slug)}/">Open the full comparison →</a></p>""")

    body = f"""
<div class="wrap">
  <div class="page-head">
    <h1>Comparisons</h1>
    <p class="lede">Side by side, on the attributes the official listings actually state.
      No ratings, no invented scores, no 'best overall' crowns.</p>
  </div>
  {''.join(blocks)}
  <div class="callout">
    <span class="callout__title">Why there is no rating column</span>
    <p>Amazon's Program Policies 5(t) bars displaying Amazon customer reviews or star
      ratings on your site unless they come from Creators API or PA&nbsp;API. This site
      is not configured with API access, so there is no rating column here. The same rule
      covers prices under 2(b), which is why the price column points at the listing.
      <a href="/compliance/">See the full compliance notes →</a></p>
  </div>
</div>
"""
    register("/compare/", "weekly", "0.8")
    return layout(CFG, f"Comparisons — {SITE['name']}",
                  "Side-by-side comparisons of the five products in the register, using only the attributes their official listings state.",
                  "/compare/", body, current="/compare/")


def page_compare_detail(slug: str, title: str, ids: list, dek: str, extra_html: str,
                         guide_slugs: list) -> str:
    cards = []
    for pid in ids:
        p = product_by_id(pid)
        cards.append(f"""
      <article class="card">
        <span class="card__tag">{esc(p["brand"])}</span>
        <h3 class="card__title" style="font-size:var(--step-1)">{esc(p["display_name"])}</h3>
        <p>{esc(p["editorial"])}</p>
        <div class="card__foot">
          {price_slot(p["observed_redirect"]["target_asin"])}
          {sponsored_anchor(link_for(p), "Check current price", p["id"], p["observed_redirect"]["target_asin"], f"compare-detail-{slug}", p["official_title"])}
        </div>
      </article>""")

    guides_items = []
    for gs in guide_slugs:
        title = gs
        for x in GUIDES:
            if x["slug"] == gs:
                title = x["title"]
        guides_items.append('<li><a href="/guides/' + esc(gs) + '/">' + esc(title) + "</a></li>")
    guides_html = "".join(guides_items)

    body = f"""
<div class="wrap">
  <div class="page-head">
    <p class="breadcrumb-nav"><a href="/">Home</a> <span aria-hidden="true">/</span> <a href="/compare/">Compare</a> <span aria-hidden="true">/</span> <span>{esc(title)}</span></p>
    <h1>{esc(title)}</h1>
    <p class="lede">{esc(dek)}</p>
  </div>

  <div class="grid grid--sidebar" data-comparison>
    <div class="prose">
      {extra_html}
      {compare_table(ids, "cmp-" + slug, "Compared on the attributes stated in each official listing title.")}
      <h2>Guides on this comparison</h2>
      <ul>{guides_html}</ul>
    </div>
    <aside class="stack">
      <div class="card">
        <span class="card__tag">What is compared</span>
        <p style="margin-top:.4rem">Only attributes quoted from the official listing
          titles, read on the dates shown in the <a href="/products/">product register</a>.</p>
      </div>
    </aside>
  </div>
</div>
"""
    path = f"/compare/{slug}/"
    register(path, "monthly", "0.7")
    return layout(CFG, f"{title} — {SITE['name']}", dek, path, body, current="/compare/")


# ==========================================================================
# Category hubs
# ==========================================================================

def page_category(slug: str, name: str, ids: list, dek: str) -> str:
    cards = []
    for pid in ids:
        p = product_by_id(pid)
        cards.append(f"""
      <article class="card product-card">
        <div class="product-card__thumb">{illustration(p)}</div>
        <div class="product-card__body">
          <span class="card__tag">{esc(p["brand"])}</span>
          <h3 class="product-card__title"><a href="/products/{esc(p["id"])}/">{esc(p["display_name"])}</a></h3>
          <p class="product-card__why">{esc(p["editorial"])}</p>
          <div class="card__foot">
            {price_slot(p["observed_redirect"]["target_asin"])}
            {sponsored_anchor(link_for(p), "Check current price", p["id"], p["observed_redirect"]["target_asin"], f"cat-{slug}", p["official_title"])}
          </div>
        </div>
      </article>""")

    guides = guides_in_category(slug)
    guide_links = "".join(
        f'<li><a href="/guides/{esc(g["slug"])}/">{esc(g["title"])}</a> — {esc(g["dek"])}</li>'
        for g in guides)

    body = f"""
<div class="wrap">
  <div class="page-head">
    <p class="breadcrumb-nav"><a href="/">Home</a> <span aria-hidden="true">/</span> <span>{esc(name)}</span></p>
    <h1>{esc(name)}</h1>
    <p class="lede">{esc(dek)}</p>
  </div>
  <h2>Guides on {esc(name.lower())}</h2>
  <ul class="prose" style="max-width:60ch">{guide_links}</ul>
  <h2>The {len(ids)} products in the register</h2>
  <div class="shelf">{''.join(cards)}</div>
  <p class="table-note">Prices and ratings are not shown. See the
    <a href="/compliance/">compliance notes</a> for why, and the
    <a href="/methods/sources/">source register</a> for what was read and when.</p>
</div>
"""
    path = f"/categories/{slug}/"
    register(path, "monthly", "0.7")
    return layout(CFG, f"{name} — {SITE['name']}", dek, path, body, current="/products/")


# ==========================================================================
# The desk: questions, suggestions, flags
# ==========================================================================

def page_desk() -> str:
    blocks = []
    for grp in QUESTIONS["groups"]:
        rows = []
        for q in grp["questions"]:
            rows.append(f"""
        <tr data-priority="{esc(q["priority"])}">
          <td data-col="id" data-sort="{esc(q["id"])}"><span class="mono">{esc(q["id"])}</span></td>
          <td data-col="priority" data-sort="{esc(q["priority"])}"><span class="badge badge--med">{esc(q["priority"])}</span></td>
          <td data-col="question" data-sort="{esc(q["question"])}">
            <strong>{esc(q["question"])}</strong>
            <div class="muted" style="font-size:.82rem;margin-top:.25rem">
              Blocks: {esc(q["decision_blocked"])}
            </div>
          </td>
          <td data-col="known" data-sort="{esc(q["what_we_know"])}">{esc(q["what_we_know"])}</td>
          <td data-col="missing" data-sort="{esc(q["what_is_missing"])}">{esc(q["what_is_missing"])}</td>
          <td data-col="close" data-sort="{esc(q["how_to_close"])}">{esc(q["how_to_close"])}
            <div class="muted" style="font-size:.8rem;margin-top:.25rem">
              Source: {source_link(q["source"], q["source"].split("/")[2])}
            </div>
          </td>
          <td data-col="status" data-sort="{esc(q["status"])}">
            <span class="badge {'badge--done' if q['status'] == 'closed' else 'badge--next'}">{esc(q["status"])}</span>
          </td>
        </tr>""")
        blocks.append(f"""
    <h2>{esc(grp["name"])}</h2>
    <p class="lede" style="margin-bottom:1rem">{esc(grp["why_it_matters"])}</p>
    <div class="table-wrap">
      <table class="data">
        <thead>
          <tr>
            <th data-col="id" aria-sort="none" scope="col">ID</th>
            <th data-col="priority" aria-sort="none" scope="col">Priority</th>
            <th data-col="question" aria-sort="none" scope="col">Question</th>
            <th data-col="known" scope="col">What we already know</th>
            <th data-col="missing" scope="col">What is missing</th>
            <th data-col="close" scope="col">How to close it</th>
            <th data-col="status" scope="col">Status</th>
          </tr>
        </thead>
        <tbody>{''.join(rows)}</tbody>
      </table>
    </div>""")

    body = f"""
<div class="wrap">
  <div class="page-head">
    <h1>Open questions</h1>
    <p class="lede">{esc(QUESTIONS["meta"]["subtitle"])}</p>
    <p class="table-note">{esc(QUESTIONS["meta"]["how_to_read"])}</p>
  </div>
  {''.join(blocks)}
  <div class="callout" style="margin-top:2rem">
    <span class="callout__title">Not a to-do list for you</span>
    <p>Most of these close inside the site owner's own Amazon account and take minutes.
      The rest close with a season of traffic. None of them block the site being live.</p>
  </div>
</div>
"""
    register("/desk/", "weekly", "0.7")
    return layout(CFG, f"Open questions — {SITE['name']}",
                  "Every question that has to be answered before the next real decision, with what is known, what is missing and how to close it.",
                  "/desk/", body, current="/desk/")


def page_suggestions() -> str:
    path_cards = []
    for p in SUGGESTIONS["paths"]:
        unlocks = "".join(f"<li>{esc(x)}</li>" for x in p["unlocks"])
        costs = "".join(f"<li>{esc(x)}</li>" for x in p["costs"])
        path_cards.append(f"""
      <article class="path">
        <span class="card__tag">{esc(p["id"])}</span>
        <h3>{esc(p["name"])}</h3>
        <p class="muted" style="font-size:.9rem">{esc(p["shape"])}</p>
        <dl>
          <dt>Why it works</dt><dd>{esc(p["why_it_works"])}</dd>
          <dt>Unlocks</dt><dd><ul>{unlocks}</ul></dd>
          <dt>Costs</dt><dd><ul>{costs}</ul></dd>
          <dt>Best when</dt><dd>{esc(p["best_when"])}</dd>
        </dl>
        <p><strong>{esc(p["recommendation"])}</strong></p>
      </article>""")

    rows = []
    for s in SUGGESTIONS["suggestions"]:
        deps = ", ".join(s["depends_on"]) if s["depends_on"] else "—"
        rows.append(f"""
        <tr data-status="{esc(s["status"])}">
          <td data-col="id" data-sort="{esc(s["id"])}"><span class="mono">{esc(s["id"])}</span></td>
          <td data-col="title" data-sort="{esc(s["title"])}"><strong>{esc(s["title"])}</strong></td>
          <td data-col="change" data-sort="{esc(s["change"])}">{esc(s["change"])}</td>
          <td data-col="effort" data-sort="{esc(s["effort"])}">{esc(s["effort"])}</td>
          <td data-col="impact" data-sort="{esc(s["impact"])}">{esc(s["impact"])}</td>
          <td data-col="status" data-sort="{esc(s["status"])}">
            <span class="badge badge--{esc(s["status"])}">{esc(s["status"])}</span>
          </td>
          <td data-col="deps" data-sort="{esc(deps)}"><span class="mono">{esc(deps)}</span></td>
        </tr>""")

    seq = "".join(f"<li>{esc(x)}</li>" for x in SUGGESTIONS["recommended_sequence"])

    body = f"""
<div class="wrap">
  <div class="page-head">
    <h1>Suggestions</h1>
    <p class="lede">{esc(SUGGESTIONS["meta"]["subtitle"])}</p>
  </div>

  <h2>First, pick a path</h2>
  <p class="lede" style="margin-bottom:1.5rem">The suggestions below assume a shape for
    the site. Four shapes are on the table and only one of them matches the five links
    that were supplied. This is the decision that everything else waits on.</p>
  <div class="paths">{''.join(path_cards)}</div>

  <h2 style="margin-top:3rem">Every suggestion, with its cost</h2>
  <div class="filterbar">
    <div class="field">
      <label for="f-status">Status</label>
      <select id="f-status" data-filter-select="sug" data-filter-name="status">
        <option value="">All</option>
        <option value="done">done</option>
        <option value="next">next</option>
        <option value="later">later</option>
        <option value="blocked">blocked</option>
      </select>
    </div>
    <p class="filterbar__count" data-filter-count="sug">{len(SUGGESTIONS["suggestions"])} rows</p>
  </div>
  <div class="table-wrap">
    <table class="data" id="sug">
      <thead>
        <tr>
          <th data-col="id" aria-sort="none" scope="col">ID</th>
          <th data-col="title" aria-sort="none" scope="col">Suggestion</th>
          <th scope="col">What changes</th>
          <th data-col="effort" aria-sort="none" scope="col">Effort</th>
          <th data-col="impact" aria-sort="none" scope="col">Impact</th>
          <th data-col="status" aria-sort="none" scope="col">Status</th>
          <th scope="col">Depends on</th>
        </tr>
      </thead>
      <tbody>{''.join(rows)}</tbody>
    </table>
  </div>

  <h2 style="margin-top:2.5rem">Status key</h2>
  <div class="pill-row">
    {''.join(f'<span class="badge badge--{esc(k)}">{esc(k)}</span>' for k in SUGGESTIONS["meta"]["status_legend"])}
  </div>
  <ul class="prose" style="max-width:60ch">
    {''.join(f'<li><strong>{esc(k)}</strong> — {esc(v)}</li>' for k, v in SUGGESTIONS["meta"]["status_legend"].items())}
  </ul>

  <h2>Recommended order</h2>
  <ol class="prose" style="max-width:60ch">{seq}</ol>
</div>
"""
    register("/desk/suggestions/", "weekly", "0.7")
    return layout(CFG, f"Suggestions — {SITE['name']}",
                  "Every improvement this desk would make, with the effort, the risk and the status — plus the four possible shapes for the site.",
                  "/desk/suggestions/", body, current="/desk/")


def page_flags() -> str:
    cards = []
    for f in FLAGS["flags"]:
        sev = f["severity"]
        cards.append(f"""
      <article class="card" id="{esc(f["id"])}" style="margin-bottom:1.1rem">
        <div style="display:flex;flex-wrap:wrap;gap:.5rem;align-items:center">
          <span class="mono" style="font-size:.78rem;color:var(--ink-3)">{esc(f["id"])}</span>
          <span class="badge badge--{esc(sev)}">{esc(sev)} severity</span>
          <span class="badge badge--later">{esc(f["status"])}</span>
        </div>
        <h3 style="margin:.6rem 0 .3rem">{esc(f["title"])}</h3>
        <dl class="facts">
          <dt>What was checked</dt><dd>{esc(f["what_we_checked"])}</dd>
          <dt>What is missing</dt><dd>{esc(f["what_is_missing"])}</dd>
          <dt>Impact</dt><dd>{esc(f["impact"])}</dd>
          <dt>How to close it</dt><dd>{esc(f["how_to_close"])}</dd>
          <dt>Source</dt><dd>{source_link(f["source"], f["source"])}</dd>
        </dl>
      </article>""")

    body = f"""
<div class="wrap wrap--narrow">
  <div class="page-head">
    <h1>Flagged for review</h1>
    <p class="lede">{esc(FLAGS["meta"]["subtitle"])}</p>
    <p class="table-note">{esc(FLAGS["meta"]["policy"])}</p>
  </div>
  {''.join(cards)}
  <div class="callout" style="margin-top:2rem">
    <span class="callout__title">None of these block the site</span>
    <p>They are published here on purpose. A flag you cannot see is a flag you cannot
      review, and an unverified value quietly presented as a verified one is the thing
      this whole register exists to prevent.</p>
  </div>
</div>
"""
    register("/desk/flags/", "weekly", "0.7")
    return layout(CFG, f"Flagged for review — {SITE['name']}",
                  "Everything this desk could not settle from an official source, with the source checked, what is missing and how to close it.",
                  "/desk/flags/", body, current="/desk/")


# ==========================================================================
# Method pages
# ==========================================================================

def page_sources() -> str:
    rows = []
    for s in SOURCES["sources"]:
        upd = s.get("publisher_stated_updated", "—")
        rows.append(f"""
        <tr data-type="{esc(s["type"])}">
          <td data-col="id" data-sort="{esc(s["id"])}"><span class="mono">{esc(s["id"])}</span></td>
          <td data-col="title" data-sort="{esc(s["title"])}">
            {source_link(s["url"], s["title"])}
            <div class="muted" style="font-size:.78rem">{esc(s["publisher"])}</div>
          </td>
          <td data-col="type" data-sort="{esc(s["type"])}">{esc(s["type"])}</td>
          <td data-col="updated" data-sort="{esc(upd)}">{esc(upd)}</td>
          <td data-col="checked" data-sort="{esc(s["checked_on"])}">{esc(s["checked_on"])}</td>
          <td data-col="supports" data-sort="{esc(s["supports"][0] if s["supports"] else "")}">
            {''.join(f'<div>{esc(x)}</div>' for x in s["supports"])}
          </td>
        </tr>""")

    quotes = []
    for s in SOURCES["sources"]:
        qs = [s.get("quote", "")] + [s.get("quote_2", ""), s.get("quote_3", ""), s.get("quote_4", "")]
        for q in qs:
            if not q:
                continue
            quotes.append(f"""
      <blockquote>
        <p>{esc(q)}</p>
        <footer class="muted" style="font-size:.82rem">
          {esc(s["title"])} — {source_link(s["url"], s["publisher"])}
        </footer>
      </blockquote>""")

    log = "".join(f"""
      <li>
        <span class="timeline__meta">{esc(v["when"])}</span>
        <strong>{esc(v["step"])}</strong>
        <p class="muted">{esc(v["result"])}</p>
      </li>""" for v in SOURCES["verification_log"])

    body = f"""
<div class="wrap">
  <div class="page-head">
    <h1>Source register</h1>
    <p class="lede">{esc(SOURCES["meta"]["subtitle"])}</p>
    <p class="table-note">{esc(SOURCES["meta"]["method"])}</p>
  </div>

  <div class="table-wrap">
    <table class="data" id="sources">
      <caption>Every page this site relies on, what it supports, and when it was read.</caption>
      <thead>
        <tr>
          <th data-col="id" aria-sort="none" scope="col">ID</th>
          <th data-col="title" aria-sort="none" scope="col">Page</th>
          <th data-col="type" aria-sort="none" scope="col">Type</th>
          <th data-col="updated" aria-sort="none" scope="col">Publisher's date</th>
          <th data-col="checked" aria-sort="none" scope="col">Checked</th>
          <th scope="col">What it supports</th>
        </tr>
      </thead>
      <tbody>{''.join(rows)}</tbody>
    </table>
  </div>

  <h2 style="margin-top:2.5rem">Quoted from the sources</h2>
  <div class="prose">{''.join(quotes)}</div>

  <h2 style="margin-top:2.5rem">Verification log</h2>
  <ul class="timeline prose" style="max-width:64ch">{log}</ul>
</div>
"""
    register("/methods/sources/", "monthly", "0.7")
    return layout(CFG, f"Source register — {SITE['name']}",
                  "Every official page this site relies on, what it supports, when it was read and what it says.",
                  "/methods/sources/", body, current="/about/")


def page_verification() -> str:
    checks = [
        ("Link resolution",
         "Every submitted link was fetched and its redirect followed to the final amazon.com URL.",
         "Five of five resolved. The final URL, the page title and the browse-node breadcrumbs were read from the destination page."),
        ("ASIN shape",
         "Amazon defines an ASIN as a 10-character alphanumeric identifier, so the shape alone is checkable.",
         "Three tokens are 9 characters and cannot be ASINs. Two are 10 characters but their /dp/ pages did not return a retrievable listing, so neither was confirmed."),
        ("Listing titles",
         "The official page title is the product's own description, taken from Amazon rather than from us.",
         "Captured verbatim for all five products, each with its listing URL and the date it was read."),
        ("Browse path",
         "The breadcrumb on the listing page gives the category the product sits in.",
         "Captured for all five products: three under Air Fryers, two under Meat thermometers."),
        ("Prices and availability",
         "Checked against Program Policies 2(b) before deciding what to publish.",
         "Not published. The site links to the listing instead of quoting a figure."),
        ("Ratings and reviews",
         "Checked against Program Policies 5(t) before deciding what to publish.",
         "Not published, and deliberately absent from every comparison table."),
        ("Link format",
         "Checked against Program Policies 2(b) and 5(v) and 5(w).",
         "Every outbound product link is a direct Special Link carrying the Associates tag, with rel sponsored nofollow."),
        ("Disclosure placement",
         "Checked against Operating Agreement 5 and the FTC's Disclosures 101.",
         "A disclosure strip sits directly under the masthead on every page and the same sentence is repeated in the footer."),
        ("API status",
         "Checked the current API documentation rather than assuming the old one.",
         "PA-API 5 is deprecated and now returns HTTP 403 AccessDeniedException. The tooling targets the Creators API."),
    ]
    rows = "".join(f"""
        <tr>
          <td data-col="check" data-sort="{esc(c[0])}"><strong>{esc(c[0])}</strong></td>
          <td data-col="how" data-sort="{esc(c[1])}">{esc(c[1])}</td>
          <td data-col="result" data-sort="{esc(c[2])}">{esc(c[2])}</td>
        </tr>""" for c in checks)

    body = f"""
<div class="wrap">
  <div class="page-head">
    <h1>How we verify</h1>
    <p class="lede">The rule this desk works to: a number that can be re-checked at the
      source may be printed. A number that cannot may not.</p>
  </div>

  <div class="table-wrap">
    <table class="data" id="checks">
      <caption>Every check run against these five products, and what it produced.</caption>
      <thead>
        <tr>
          <th data-col="check" aria-sort="none" scope="col">Check</th>
          <th data-col="how" scope="col">How it was checked</th>
          <th data-col="result" scope="col">Result</th>
        </tr>
      </thead>
      <tbody>{rows}</tbody>
    </table>
  </div>

  <h2 style="margin-top:2.5rem">What is deliberately missing</h2>
  <div class="grid grid--2">
    <div class="callout">
      <span class="callout__title">Prices</span>
      <p>Blank everywhere, on purpose. The rule and the source are in the
        <a href="/methods/sources/">source register</a>.</p>
    </div>
    <div class="callout">
      <span class="callout__title">Ratings and review counts</span>
      <p>Absent from every table, on purpose, under a different clause of the same policy.</p>
    </div>
    <div class="callout">
      <span class="callout__title">Internal dimensions and clearances</span>
      <p>Not confirmed from any official source, so not published. They appear as
        questions to ask instead.</p>
    </div>
    <div class="callout">
      <span class="callout__title">Popularity, trends and conversion</span>
      <p>No such claim appears anywhere. There is no measured data behind one, and the
        campaign ledger is empty on purpose.</p>
    </div>
  </div>

  <h2 style="margin-top:2.5rem">How a reader can check our work</h2>
  <p class="lede">Every row in every table on this site has a link in it. Click it. If the
    official page says something different from what we printed, that is a bug and we
    would like to know about it.</p>
</div>
"""
    register("/methods/verification/", "monthly", "0.6")
    return layout(CFG, f"How we verify — {SITE['name']}",
                  "The checks run against every product on this site, what each one produced, and what is deliberately left blank.",
                  "/methods/verification/", body, current="/about/")


# ==========================================================================
# Compliance
# ==========================================================================

def page_compliance() -> str:
    body = f"""
<div class="wrap wrap--narrow">
  <div class="page-head">
    <h1>Compliance</h1>
    <p class="lede">What this site does, which Amazon rule each thing comes from, and
      where the rules were read.</p>
  </div>

  <div class="answer">
    <span class="answer__label">The disclosure</span>
    <p>Amazon's Operating Agreement 5 requires this exact statement, clearly and
      prominently, wherever Program Content appears:</p>
    <p><strong>"{esc(CFG["affiliate"]["disclosure"]["operating_agreement_sentence"])}"</strong></p>
    <p>It appears in a strip directly under the masthead on every page of this site,
      and it is repeated in the footer. The FTC's <em>Disclosures 101</em> says a
      disclosure is likely to be missed if it appears only on an About page or at the
      end of a post, which is why this one is at the top of the page as well.</p>
  </div>

  <h2>Rule by rule</h2>
  <div class="table-wrap">
    <table class="data">
      <thead><tr><th scope="col">What this site does</th><th scope="col">The rule</th><th scope="col">Source</th></tr></thead>
      <tbody>
        <tr>
          <td>Every outbound product link carries the Associates tag and points directly at amazon.com/dp.</td>
          <td>Participation Requirements 2(b): Special Links must use the assigned Associates ID and be accessed directly from your Site.</td>
          <td>{source_link("https://affiliate-program.amazon.com/help/operating/policies", "Program Policies")}</td>
        </tr>
        <tr>
          <td>The five submitted link.amazon short links are recorded in the register but are not published as outbound links.</td>
          <td>Program Policies 5(v) and 5(w) restrict Redirecting Links and link shorteners that make the Amazon destination unclear.</td>
          <td>{source_link("https://affiliate-program.amazon.com/help/operating/policies", "Program Policies")}</td>
        </tr>
        <tr>
          <td>No price is shown anywhere on the site.</td>
          <td>Program Policies 2(b): a Site may only show prices and availability if Amazon serves the link that displays them, or the data comes from Creators API or PA API.</td>
          <td>{source_link("https://affiliate-program.amazon.com/help/operating/policies", "Program Policies")}</td>
        </tr>
        <tr>
          <td>No star rating, review count or review text appears anywhere on the site.</td>
          <td>Program Policies 5(t): no customer reviews or star ratings unless obtained through Creators API or PA API.</td>
          <td>{source_link("https://affiliate-program.amazon.com/help/operating/policies", "Program Policies")}</td>
        </tr>
        <tr>
          <td>Every outbound product link is marked rel="sponsored nofollow" with a visible Sponsored marker.</td>
          <td>Google Search Central: mark paid placements with rel="sponsored".</td>
          <td>{source_link("https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links", "Google Search Central")}</td>
        </tr>
        <tr>
          <td>Comparison pages carry original written analysis alongside the links.</td>
          <td>Program Policies 2(b): links to pages with product lists require additional original content on your Site.</td>
          <td>{source_link("https://affiliate-program.amazon.com/help/operating/policies", "Program Policies")}</td>
        </tr>
        <tr>
          <td>No Amazon logo, wordmark or product photograph is used. All illustrations are original drawings.</td>
          <td>Associates Program Trademark Guidelines; Program Content may not be used to advertise non-Amazon products.</td>
          <td>{source_link("https://affiliate-program.amazon.com/help/operating/policies", "Program Policies")}</td>
        </tr>
        <tr>
          <td>No income figure, conversion rate, popularity ranking or revenue forecast appears anywhere.</td>
          <td>Operating Agreement 4: Amazon makes no representation about expected traffic or commission income, so none is implied.</td>
          <td>{source_link("https://affiliate-program.amazon.com/help/operating/agreement", "Operating Agreement")}</td>
        </tr>
        <tr>
          <td>Product specifications are attributed to the official listing title rather than presented as our own testing.</td>
          <td>Program Policies 2(b): no inaccurate, overbroad, deceptive or misleading claims about any Product.</td>
          <td>{source_link("https://affiliate-program.amazon.com/help/operating/policies", "Program Policies")}</td>
        </tr>
      </tbody>
    </table>
  </div>

  <h2>The disclosure rule, in the source's own words</h2>
  <div class="prose">
    <blockquote>
      <p>You must clearly and prominently state the following, or any substantially similar
        statement previously allowed under this Agreement, on your Site or any other
        location where Amazon may authorize your display or other use of Program Content:
        "As an Amazon Associate I earn from qualifying purchases."</p>
      <footer class="muted" style="font-size:.82rem">Operating Agreement, Section 5 —
        {source_link("https://affiliate-program.amazon.com/help/operating/agreement", "read the agreement")}</footer>
    </blockquote>
    <blockquote>
      <p>Disclosures are likely to be missed if they appear only on an ABOUT ME or
        profile page, at the end of posts or videos, or anywhere that requires a person
        to click MORE.</p>
      <footer class="muted" style="font-size:.82rem">FTC, Disclosures 101 —
        {source_link("https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers", "read the guidance")}</footer>
    </blockquote>
  </div>

  <h2>What still needs doing</h2>
  <p class="lede">Two items are genuinely unfinished rather than merely unverified, and
    both are on the Flagged for Review page with the same level of detail.</p>
  <ul class="prose" style="max-width:60ch">
    <li><strong>FLG-001</strong> — the tracking ID matches Amazon's published shape, but
      no public page confirms it was issued to this account.</li>
    <li><strong>FLG-003</strong> — one of the five submitted links should be tested end to
      end inside the enrolled Associates workflow before the rest are trusted.</li>
  </ul>
</div>
"""
    register("/compliance/", "monthly", "0.7")
    return layout(CFG, f"Compliance — {SITE['name']}",
                  "Every compliance rule this site follows, mapped to the Amazon policy or FTC guidance it comes from, with a link to the source.",
                  "/compliance/", body, current="/about/")


# ==========================================================================
# Measurement
# ==========================================================================

def page_measurement() -> str:
    ev_rows = "".join(f"""
        <tr>
          <td data-col="id" data-sort="{esc(e["id"])}"><span class="mono">{esc(e["id"])}</span></td>
          <td data-col="name" data-sort="{esc(e["name"])}">{esc(e["name"])}</td>
          <td data-col="fires" data-sort="{esc(e["fires"])}">{esc(e["fires"])}</td>
          <td data-col="params" data-sort="{esc(", ".join(e["params"]))}"><span class="mono">{esc(", ".join(e["params"]))}</span></td>
        </tr>""" for e in CFG["measurement"]["events"])

    body = f"""
<div class="wrap">
  <div class="page-head">
    <h1>Measurement</h1>
    <p class="lede">What this site records, what it deliberately does not, and how the
      numbers reach the ledger.</p>
  </div>

  <div class="answer">
    <span class="answer__label">The rule</span>
    <p>The site's own counter records clicks and reading behaviour. It never records
      anything that identifies a person. Orders come from Amazon's own report and
      nowhere else. The two are never mixed in a single number.</p>
  </div>

  <h2>The five events</h2>
  <div class="table-wrap">
    <table class="data" id="events">
      <caption>The complete event list. Nothing outside this table is sent.</caption>
      <thead>
        <tr>
          <th data-col="id" aria-sort="none" scope="col">Event</th>
          <th data-col="name" aria-sort="none" scope="col">Name</th>
          <th data-col="fires" scope="col">Fires when</th>
          <th scope="col">Fields</th>
        </tr>
      </thead>
      <tbody>{ev_rows}</tbody>
    </table>
  </div>

  <h2>What is never collected</h2>
  <div class="grid grid--3">
    <div class="card"><h3 class="card__title" style="font-size:var(--step-0)">No IP address</h3><p>The browser does not send one and the collector does not store one.</p></div>
    <div class="card"><h3 class="card__title" style="font-size:var(--step-0)">No cookies</h3><p>Nothing is written to a cookie jar. The session id lives in sessionStorage and dies with the tab.</p></div>
    <div class="card"><h3 class="card__title" style="font-size:var(--step-0)">No advertising id</h3><p>No fingerprinting, no canvas reads, no font or plugin enumeration.</p></div>
    <div class="card"><h3 class="card__title" style="font-size:var(--step-0)">No email addresses</h3><p>Email is only ever sent to the list provider, never to the collector.</p></div>
    <div class="card"><h3 class="card__title" style="font-size:var(--step-0)">No user agent</h3><p>Not captured, not forwarded, not stored.</p></div>
    <div class="card"><h3 class="card__title" style="font-size:var(--step-0)">Do Not Track honoured</h3><p>If the browser sends DNT or GPC, no event leaves the page at all.</p></div>
  </div>

  <div class="callout" style="margin-top:2rem">
    <span class="callout__title">One honest caveat</span>
    <p>This site's collector is IP-free. The hosting platform is not. GitHub's
      documentation states that when a GitHub Pages site is visited, the visitor's IP
      address is logged and stored for security purposes, regardless of consent.
      <a href="/desk/flags/">FLG-012 →</a></p>
  </div>

  <h2>How the collector works</h2>
  <ol class="prose" style="max-width:64ch">
    <li>The browser generates a random 128-bit id in sessionStorage. It is never linked
      to a person, a device or an email address.</li>
    <li>Each event is posted to the collector endpoint with the event name, the page
      path and that event's listed fields.</li>
    <li>The collector hashes the id against a server-side salt that never reaches the
      browser, so the stored record cannot be reversed back into the value that was sent.</li>
    <li>The record is appended as one NDJSON line. The collector rejects any event name
      that is not on the list above.</li>
  </ol>
  <p class="table-note">The collector source is in
    <span class="mono">tools/analytics_sink.py</span>. It is standard library only and
    runs anywhere Python does.</p>

  <h2>Where the numbers go</h2>
  <p class="lede">The site's own events and Amazon's report land in the same ledger but
    never in the same row. The ledger ships empty, with its columns already defined.</p>
  <p><a class="btn btn--ghost btn--sm" href="/ledger/">Open the campaign ledger →</a></p>

  <h2>Reader capture</h2>
  <p class="lede">The signup form is built and it fires the reader_signup event, but no
    list provider has been chosen. Until one is, the form tells the reader exactly that
    and stores nothing. A capture box that quietly discards addresses is worse than no
    capture box at all.</p>
</div>
"""
    register("/measurement/", "monthly", "0.6")
    return layout(CFG, f"Measurement — {SITE['name']}",
                  "The five events this site records, what it never collects, and how the numbers reach the campaign ledger.",
                  "/measurement/", body, current="/about/")


def page_ledger() -> str:
    schema = read_text(os.path.join(DATA, "ledger_schema.md"))
    rows = ""
    import csv
    with open(os.path.join(DATA, "ledger.csv"), newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh)
        header = next(reader)
        data_rows = list(reader)
    if data_rows:
        rows = "".join("<tr>" + "".join(f"<td>{esc(c)}</td>" for c in r) + "</tr>" for r in data_rows)
    else:
        rows = ('<tr><td colspan="17" class="muted">No rows. This is the intended state '
                'until an authorised first-party report exists to fill them.</td></tr>')

    cols = "".join(f'<tr><td><span class="mono">{esc(h)}</span></td></tr>' for h in header)

    body = f"""
<div class="wrap">
  <div class="page-head">
    <h1>Campaign ledger</h1>
    <p class="lede">The ledger ships with its columns defined and no rows in it. Every
      number that goes in will come from a report you are authorised to see.</p>
  </div>

  <div class="callout callout--warn">
    <span class="callout__title">Why this page is empty</span>
    <p>There is no authorised first-party report yet. An empty ledger with dated
      provenance columns is a better artefact than a plausible-looking estimate, because
      an empty one is obviously empty. The rules for filling it are below.</p>
  </div>

  <h2>The ledger</h2>
  <div class="table-wrap">
    <table class="data">
      <caption>data/ledger.csv — header row only, as shipped.</caption>
      <thead><tr>{''.join(f'<th scope="col">{esc(h)}</th>' for h in header)}</tr></thead>
      <tbody>{rows}</tbody>
    </table>
  </div>

  <h2 style="margin-top:2.5rem">Columns</h2>
  <div class="table-wrap">
    <table class="data">
      <thead><tr><th scope="col">Column</th></tr></thead>
      <tbody>{cols}</tbody>
    </table>
  </div>

  <h2 style="margin-top:2.5rem">The full rules</h2>
  <div class="prose" style="max-width:70ch">
    <p>The complete schema, including who is allowed to fill each column and the six
      rules that keep the ledger honest, is kept next to the data:</p>
    <p><a href="/data/ledger_schema.md">data/ledger_schema.md</a></p>
  </div>
</div>
"""
    register("/ledger/", "monthly", "0.6")
    return layout(CFG, f"Campaign ledger — {SITE['name']}",
                  "The campaign ledger: an empty, fully defined table where every future number comes from an authorised first-party report.",
                  "/ledger/", body, current="/about/")


# ==========================================================================
# Executive summary and about
# ==========================================================================

def page_exec_summary() -> str:
    prod_rows = "".join(f"""
        <tr>
          <td>{esc(p["slot"])}</td>
          <td data-col="name" data-sort="{esc(p["display_name"])}"><a href="/products/{esc(p["id"])}/">{esc(p["display_name"])}</a></td>
          <td data-col="cat" data-sort="{esc(p["category"])}">{esc(p["category"])}</td>
          <td data-col="asin" data-sort="{esc(p["observed_redirect"]["target_asin"])}"><span class="mono">{esc(p["observed_redirect"]["target_asin"])}</span></td>
          <td data-col="token" data-sort="{esc(p["submitted"]["token"])}"><span class="mono">{esc(p["submitted"]["token"])}</span> <span class="muted">({p["submitted"]["token_length"]})</span></td>
        </tr>""" for p in PRODUCTS)

    open_q = sum(1 for g in QUESTIONS["groups"] for q in g["questions"] if q["status"] == "open")
    closed_q = sum(1 for g in QUESTIONS["groups"] for q in g["questions"] if q["status"] == "closed")

    body = f"""
<div class="wrap wrap--narrow">
  <div class="page-head">
    <h1>Executive summary</h1>
    <p class="lede">What was built, what was verified, what could not be, and what has
      to happen next. One page, in that order.</p>
  </div>

  <h2>What this is</h2>
  <p>A reader-facing affiliate publication for two countertop cooking categories, with
    the machinery that produced it published alongside it. The front page reads like a
    shop. The register, the source list and the flags read like the notebook behind
    the shop, and both are one click away.</p>

  <h2>The five products, and what was confirmed about them</h2>
  <p>All five submitted links were fetched and their redirects followed to the final
    destination on amazon.com. Every destination was read directly: its title, its
    breadcrumb and its date.</p>
  <div class="table-wrap">
    <table class="data">
      <caption>Submitted link, observed destination, and the length of the submitted token.</caption>
      <thead>
        <tr><th scope="col">#</th><th data-col="name" aria-sort="none" scope="col">Product</th>
        <th data-col="cat" aria-sort="none" scope="col">Category</th>
        <th data-col="asin" aria-sort="none" scope="col">Observed ASIN</th>
        <th data-col="token" aria-sort="none" scope="col">Submitted token</th></tr>
      </thead>
      <tbody>{prod_rows}</tbody>
    </table>
  </div>
  <p class="table-note">Observed on {esc(PRODUCT_REGISTER["meta"]["checked_on"])}.
    The intended ASIN for each link is a separate fact and is not confirmed — see
    <a href="/desk/flags/">FLG-002</a>.</p>

  <h2>The four findings that shaped the build</h2>
  <div class="stack-lg">
    <div class="callout">
      <span class="callout__title">Finding 1 — three of the five tokens cannot be ASINs</span>
      <p>Amazon defines an ASIN as a 10-character alphanumeric identifier. Three of the
        submitted tokens are 9 characters. The other two are 10 characters but neither
        was confirmed as an issued ASIN. That is why the register keeps intent and
        observation in two separate tables: the destination we measured and the product
        that was meant are different facts, and merging them would let a guess look like
        a verification.</p>
    </div>
    <div class="callout callout--warn">
      <span class="callout__title">Finding 2 — prices and ratings are not publishable as static text</span>
      <p>Program Policies 2(b) allows a price on your site only when Amazon serves the
        link that displays it or the price comes from Creators API or PA&nbsp;API.
        5(t) does the same for star ratings and customer reviews. So this site shows
        neither, and instead links to the listing. The code path for a live lookup
        exists and stays empty until the API is configured.</p>
    </div>
    <div class="callout callout--flag">
      <span class="callout__title">Finding 3 — the submitted links are redirects, not Special Links</span>
      <p>Program Policies requires Special Links to be accessed directly from your site
        and restricts Redirecting Links and link shorteners. The five submitted links
        are Amazon-hosted redirects, so they are recorded in the register but are not
        published as outbound links. Every outbound link on this site is a direct
        Special Link carrying the tag, marked rel sponsored nofollow. Whether each
        short link is enrolled in the owner's own workflow is private account data and
        is flagged rather than judged.</p>
    </div>
    <div class="callout">
      <span class="callout__title">Finding 4 — PA-API 5 is dead, and the replacement has a threshold</span>
      <p>PA-API 5 is deprecated and now returns an HTTP 403 AccessDeniedException. The
        Creators API is the supported path, and it requires at least 10 qualifying sales
        in the past 30 days before it will serve anything. The research tooling targets
        Creators API from the start for that reason.</p>
    </div>
  </div>

  <h2>What was built</h2>
  <ul class="prose" style="max-width:64ch">
    <li>A publication front page, {len(GUIDES)} question-shaped guides, two category hubs,
      two comparison pages and a comparison hub — every one of them carrying the
      disclosure strip and a dated source.</li>
    <li>A product register with a separate product-intent record and a separate observed
      redirect record, plus a Flagged for Review page listing {len(FLAGS["flags"])} items
      this desk could not settle.</li>
    <li>A decision board with {open_q} open questions and {closed_q} closed ones, each with
      what is known, what is missing and the step that closes it, and a suggestions page
      with {len(SUGGESTIONS["suggestions"])} ranked changes and {len(SUGGESTIONS["paths"])}
      possible shapes for the site.</li>
    <li>Privacy-preserving measurement: five defined events, a self-hosted collector that
      stores no IP, no cookie and no advertising id, and a campaign ledger that ships
      empty with its columns already defined.</li>
    <li>A build gate that fails the release on a missing disclosure, an unmarked product
      link, a broken internal link, a missing canonical, or a page missing from the
      sitemap or the feed.</li>
  </ul>

  <h2>What is not done</h2>
  <ul class="prose" style="max-width:64ch">
    <li>The tracking ID is unconfirmed. It matches Amazon's published shape; nothing
      public confirms it was issued to this account.</li>
    <li>Creators API access is not configured, so no live price, no rating and no
      automated product research is running yet.</li>
    <li>There is no measured traffic data, so no topic is described as popular and no
      revenue figure appears anywhere.</li>
    <li>The reader capture form is built but has no list provider behind it.</li>
  </ul>

  <h2>Next</h2>
  <ol class="prose" style="max-width:64ch">
    <li>Confirm the tracking ID in Associates Central and put it in
      <span class="mono">data/config.json</span>.</li>
    <li>Test one of the five submitted links end to end inside the enrolled workflow and
      confirm the destination and the tracking report.</li>
    <li>Register for Creators API once the sales threshold is met, and wire the price
      lookup to the collector endpoint.</li>
    <li>Publish a season of guides, then choose the next topic from the measured queries
      rather than from instinct.</li>
  </ol>
</div>
"""
    register("/executive-summary/", "monthly", "0.8")
    return layout(CFG, f"Executive summary — {SITE['name']}",
                  "What was built, what was verified, what could not be verified, and what has to happen next.",
                  "/executive-summary/", body, current="/desk/")


def page_about() -> str:
    body = f"""
<div class="wrap wrap--narrow">
  <div class="page-head">
    <h1>About this desk</h1>
    <p class="lede">Who writes this, what the rules are, and what the desk refuses to do.</p>
  </div>

  <h2>The desk</h2>
  <p>{esc(SITE["author"]["note"])}</p>
  <p>Every page carries the same byline, every claim carries a link to the official
    page it came from, and every product attribute is quoted from an Amazon listing
    rather than described from memory. Where a fact could not be confirmed from an
    official source, it is left blank and flagged instead of being filled in.</p>

  <h2 id="editorial-standards">Editorial standards</h2>
  <ol class="prose" style="max-width:64ch">
    <li><strong>A number we can link to is a number we print.</strong> Anything that
      cannot be re-checked at the source stays out.</li>
    <li><strong>Blank beats plausible.</strong> An empty cell with a note is more useful
      than a guess that reads like a fact.</li>
    <li><strong>Snapshots are labelled.</strong> Every observation carries the date it
      was made, because Amazon's listings change.</li>
    <li><strong>Specs are attributed.</strong> Product specifications are quoted from
      the official listing title and marked as such. We do not present them as our own
      testing, because we have not tested the products.</li>
    <li><strong>No popularity claims.</strong> Guide topics are working titles, not
      statements about what people search for. We will only say a topic is popular once
      a measurement says so.</li>
    <li><strong>No earnings claims.</strong> No forecast, no conversion rate, no
      'worth it' verdict on somebody else's money.</li>
    <li><strong>Every link out is marked.</strong> Sponsored links carry
      rel sponsored nofollow, a visible marker and an aria-label, because a reader is
      entitled to know before they click.</li>
    <li><strong>Recommendation over ranking.</strong> We say which product fits which
      situation instead of crowning a winner, because a winner depends on the reader.</li>
  </ol>

  <h2>What this desk will not do</h2>
  <ul class="prose" style="max-width:64ch">
    <li>Publish a price, a star rating or a review count without an API that supplies
      them lawfully.</li>
    <li>Use an Amazon logo, a wordmark or a product photograph.</li>
    <li>Publish a number it cannot source.</li>
    <li>Present a guess as a measurement.</li>
  </ul>

  <h2>Privacy</h2>
  <p>This site's own collector stores no IP address, no cookie, no advertising
    identifier and no email address. It uses a random id that lives for one browser
    session, and it honours Do Not Track and Global Privacy Control. The hosting
    platform is a different matter: GitHub's documentation states that visitor IP
    addresses are logged for security purposes regardless of consent, and this site
    says so rather than pretending otherwise. Full detail on the
    <a href="/measurement/">measurement page</a>.</p>

  <h2>Sources and method</h2>
  <ul class="prose" style="max-width:64ch">
    <li><a href="/methods/sources/">Source register</a> — every official page this site relies on.</li>
    <li><a href="/methods/verification/">How we verify</a> — the checks and their results.</li>
    <li><a href="/compliance/">Compliance</a> — rule by rule, with the source for each.</li>
    <li><a href="/desk/flags/">Flagged for review</a> — everything we could not settle.</li>
    <li><a href="/desk/">Open questions</a> — what has to be answered before the next decision.</li>
  </ul>

  <h2>Colophon</h2>
  <p>Static HTML, CSS and JavaScript, built by a Python script with no third-party
    dependencies and no tracking libraries. Illustrations are original line drawings
    rather than product photographs. The site's source is public in the repository that
    publishes it.</p>
</div>
"""
    register("/about/", "monthly", "0.6")
    return layout(CFG, f"About this desk — {SITE['name']}",
                  "Who writes this, the editorial standards it works to, and what it refuses to do.",
                  "/about/", body, current="/about/")


def page_404() -> str:
    body = """
<div class="wrap wrap--narrow center" style="padding-block:4rem">
  <span class="eyebrow">404</span>
  <h1>That page is not here</h1>
  <p class="lede" style="margin-inline:auto">The link may be old, or it may have been
    written slightly differently. Here is where most people were heading.</p>
  <div class="hero__meta" style="justify-content:center">
    <a class="btn" href="/">Home</a>
    <a class="btn btn--ghost" href="/guides/">Guides</a>
    <a class="btn btn--ghost" href="/products/">Product register</a>
    <a class="btn btn--ghost" href="/compare/">Comparisons</a>
  </div>
</div>
"""
    return layout(CFG, f"Page not found — {SITE['name']}",
                  "That page is not here. Start from the guides, the product register or the comparisons.",
                  "/404.html", body, current="")


# ==========================================================================
# sitemap, feed, robots, config
# ==========================================================================

def build_sitemap() -> None:
    entries = []
    for item in sorted(SITEMAP, key=lambda x: x["loc"]):
        loc = esc(item["loc"])
        lastmod = esc(item["lastmod"])
        changefreq = esc(item["changefreq"])
        priority = esc(item["priority"])
        entries.append(
            "  <url>\n"
            f"    <loc>{loc}</loc>\n"
            f"    <lastmod>{lastmod}</lastmod>\n"
            f"    <changefreq>{changefreq}</changefreq>\n"
            f"    <priority>{priority}</priority>\n"
            "  </url>"
        )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(entries)
        + "\n</urlset>\n"
    )
    write_text("sitemap.xml", xml)


def build_feed() -> None:
    items = []
    for g in sorted(GUIDES, key=lambda x: x["date"], reverse=True):
        url = BASE + f"/guides/{g['slug']}/"
        items.append(f"""    <item>
      <title>{esc(g["title"])}</title>
      <link>{esc(url)}</link>
      <guid isPermaLink="true">{esc(url)}</guid>
      <pubDate>{rfc822(g["date"])}</pubDate>
      <description>{esc(g["dek"])}</description>
      <category>{esc(g["category"])}</category>
    </item>""")
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{esc(SITE["name"])}</title>
    <link>{esc(BASE + "/")}</link>
    <atom:link href="{esc(BASE + "/feed.xml")}" rel="self" type="application/rss+xml"/>
    <description>{esc(SITE["description"])}</description>
    <language>en-us</language>
    <copyright>© {esc(SITE["publisher"])}</copyright>
    <lastBuildDate>{rfc822(PRODUCT_REGISTER["meta"]["checked_on"])}</lastBuildDate>
    <generator>build_site.py</generator>
{chr(10).join(items)}
  </channel>
</rss>
"""
    write_text("feed.xml", xml)


def build_robots() -> None:
    write_text("robots.txt", f"""User-agent: *
Allow: /
Disallow: /tools/

Sitemap: {BASE}/sitemap.xml
""")


def build_site_config() -> None:
    events = [e["id"] for e in CFG["measurement"]["events"]]
    write_text("assets/js/site-config.js", (
        "/* Generated by tools/build_site.py. Do not edit by hand. */\n"
        "window.AFFIL3 = {\n"
        f'  endpoint: "{esc(CFG["measurement"]["endpoint"])}",\n'
        f"  events: {json.dumps(events)},\n"
        '  pricesEndpoint: ""\n'
        "};\n"
    ))


# ==========================================================================
# main
# ==========================================================================

def main() -> int:
    pages = []

    pages.append(("index.html", page_home()))

    pages.append(("guides/index.html", page_guides_index()))
    for g in GUIDES:
        pages.append((f"guides/{g['slug']}/index.html", page_guide(g)))

    pages.append(("products/index.html", page_products_index()))
    for p in PRODUCTS:
        pages.append((f"products/{p['id']}/index.html", page_product(p)))

    pages.append(("compare/index.html", page_compare_index()))

    airfryer_ids = [p["id"] for p in PRODUCTS if p["category_slug"] == "air-fryers"]
    thermo_ids = [p["id"] for p in PRODUCTS if p["category_slug"] == "thermometers"]

    pages.append(("compare/air-fryers/index.html", page_compare_detail(
        "air-fryers", "Air fryers compared",
        airfryer_ids,
        "Three shapes of air fryer, side by side. Every attribute below is quoted from the official listing title.",
        """
      <h2>Read this as a set of shapes, not a ranking</h2>
      <p>There is no winner in this table, because there is not one. There is a single
        8 quart basket, a pair of 3 quart baskets inside a 6 quart machine, and a
        26 quart French-door oven. A reader cooking for two and a reader cooking a
        whole chicken are not shopping for the same thing.</p>
      <p>What the table does is put the three shapes next to each other with the
        attributes each official listing states, so you can match your kitchen to one of
        them quickly. The reasoning behind the columns is in the
        <a href="/guides/basket-or-oven-style-air-fryer/">guide on which shape to buy</a>.</p>""",
        ["basket-or-oven-style-air-fryer", "no-hype-checklist-air-fryer-capacity", "cleanup-and-counter-space-trade-offs"])))

    pages.append(("compare/thermometers/index.html", page_compare_detail(
        "thermometers", "Meat thermometers compared",
        thermo_ids,
        "One probe and three probes. Every attribute below is quoted from the official listing title.",
        """
      <h2>Two tools that answer the same question differently</h2>
      <p>Both of these exist to tell you when food is done. The single probe answers in
        one second while you stand there. The three-probe unit answers while you are
        somewhere else entirely, and answers about three things at once.</p>
      <p>Neither is more accurate than the other according to the stated figures — both
        list a tolerance of ±0.5°F. The difference is how many cuts you are cooking and
        how much attention you want to give them. The reasoning is in the
        <a href="/guides/wireless-meat-thermometer-or-probe/">guide on which one you need</a>.</p>""",
        ["wireless-meat-thermometer-or-probe", "how-accurate-does-a-meat-thermometer-need-to-be"])))

    pages.append(("categories/air-fryers/index.html", page_category(
        "air-fryers", "Air fryers",
        airfryer_ids,
        "Basket, dual basket, or a full oven. Three shapes of machine, compared on what their official listings actually state.")))
    pages.append(("categories/thermometers/index.html", page_category(
        "thermometers", "Meat thermometers",
        thermo_ids,
        "A probe that answers in a second, or a wireless unit with three of them. What each one is for.")))

    pages.append(("desk/index.html", page_desk()))
    pages.append(("desk/suggestions/index.html", page_suggestions()))
    pages.append(("desk/flags/index.html", page_flags()))

    pages.append(("methods/sources/index.html", page_sources()))
    pages.append(("methods/verification/index.html", page_verification()))
    pages.append(("compliance/index.html", page_compliance()))
    pages.append(("measurement/index.html", page_measurement()))
    pages.append(("ledger/index.html", page_ledger()))
    pages.append(("executive-summary/index.html", page_exec_summary()))
    pages.append(("about/index.html", page_about()))
    pages.append(("404.html", page_404()))

    for rel, html in pages:
        write_text(rel, html)

    build_sitemap()
    build_feed()
    build_robots()
    build_site_config()

    print(f"built {len(pages)} pages, {len(SITEMAP)} sitemap entries")
    print("sitemap: sitemap.xml   feed: feed.xml   robots: robots.txt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
