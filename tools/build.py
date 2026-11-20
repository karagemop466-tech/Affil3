#!/usr/bin/env python3
"""Build the static site into docs/ from the verified JSON registers.

Design constraints enforced here, not by convention:
  * No price text is ever emitted. Checked again by tools/check_site.py.
  * No star rating or review count is never emitted.
  * An outbound Amazon button is emitted only if its URL carries tag=<TRACKING_ID>.
    Today that means zero buttons plus an explicit explanation on every product page.
  * Every spec row prints its source ID and access date.
"""

from __future__ import annotations

import html
import json
import os
import re
import pathlib
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "register"
DOCS = ROOT / "editorial"
SITE = "https://karagemop466-tech.github.io/Affil3/editorial"
TRACKING_ID = "shopnow047c-20"
BRAND = "Countertop & Co."
LEDGER = "https://github.com/karagemop466-tech/Affil3"
ROOT_SITE = "https://karagemop466-tech.github.io/Affil3"
PR_URL = "https://github.com/karagemop466-tech/Affil3/pulls"
ACCESSED = "2026-11-20"
ANALYTICS_ENDPOINT = os.environ.get("ANALYTICS_ENDPOINT", "").strip()

DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."


def load(name: str) -> dict:
    with open(DATA / f"{name}.json", encoding="utf-8") as fh:
        return json.load(fh)


def e(value) -> str:
    """HTML-escape anything, including None -> ''."""
    if value is None:
        return ""
    return html.escape(str(value), quote=True)


def dims(value: str) -> str:
    """Render a dimension string readably: prefer the source order, name the axes."""
    import re as _re
    text = str(value)
    labels = {"D": "depth", "W": "width", "H": "height"}
    parts = [x for x in _re.split(r"\s*x\s*", text.replace("\u00d7", " x ")) if x.strip()]
    if len(parts) == 3:
        nums, axes = [], []
        for part in parts:
            m = _re.match(r"([\d.]+)\s*([DWH]?)", part.strip())
            if not m:
                return e(text)
            nums.append(m.group(1))
            axes.append(labels.get(m.group(2), ""))
        joined = " \u00d7 ".join(nums)
        axis_txt = " \u00d7 ".join(a for a in axes if a)
        suffix = f' <span class="small muted">({axis_txt})</span>' if axis_txt else ""
        return f'<span class="dims">{joined} in.</span>{suffix}'
    return e(text)


def yesno(value):
    if value is True:
        return "Yes"
    if value is False:
        return "No"
    return None


# --------------------------------------------------------------------------
# chrome
# --------------------------------------------------------------------------

NAV = [
    ("/", "Start here"),
    ("/air-fryers/", "Air fryers"),
    ("/air-fryer-ovens/", "Oven-style"),
    ("/thermometers/", "Thermometers"),
    ("/guides/", "Guides"),
]


def head(title: str, desc: str, rel: str, extra: str = "") -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{SITE}{rel}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="website">
<meta name="robots" content="index,follow">
<link rel="stylesheet" href="/assets/site.css">
<link rel="alternate" type="application/rss+xml" title="{BRAND}" href="/feed.xml">
{extra}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
"""


def masthead(rel: str, current: str) -> str:
    links = "".join(
        f'<a class="navlink{" on" if href == current else ""}" href="{href}">{e(label)}</a>'
        for href, label in NAV
    )
    return f"""<header class="masthead">
  <div class="wrap masthead-inner">
    <a class="wordmark" href="/">{e(BRAND)}<span class="dot">.</span></a>
    <nav class="nav" aria-label="Sections">{links}</nav>
  </div>
</header>
<div class="disclosure-strip" id="disclosure" role="note">
  <div class="wrap">
    <strong>Paid links.</strong> {e(DISCLOSURE)} Every product link on this site is an affiliate link.
  </div>
</div>
<main id="main">
"""


def footer(rel: str) -> str:
    return f"""</main>
<footer class="footer">
  <div class="wrap">
    <div class="footer-disclosure">
      <p><strong>{e(DISCLOSURE)}</strong></p>
      <p class="small">{BRAND} is an independent publication. It is not endorsed by, sponsored by, or
      affiliated with Amazon.com, Inc. or any brand named here beyond participation in the
      Amazon Associates program. Product names and marks belong to their owners.</p>
    </div>
    <div class="footer-cols">
      <div>
        <h4>The shop</h4>
        <a href="/air-fryers/">Air fryers</a>
        <a href="/air-fryer-ovens/">Oven-style air fryers</a>
        <a href="/thermometers/">Thermometers</a>
        <a href="/guides/">Guides</a>
      </div>
      <div>
        <h4>The record</h4>
        <a href="/dashboard/">Dashboard</a>
        <a href="/sources/">Source register</a>
        <a href="/flagged/">Flagged for review</a>
        <a href="/questions/">Open questions</a>
        <a href="/suggestions/">Suggestions</a>
        <a href="/disclosure/">Disclosure &amp; method</a>
      </div>
      <div>
        <h4>Elsewhere in this publication</h4>
        <a href="{ROOT_SITE}/">The shop index (root site)</a>
        <a href="{ROOT_SITE}/flagged/">Root site flags</a>
        <a href="{ROOT_SITE}/executive-summary/">Root executive summary</a>
      </div>
      <div>
        <h4>Feeds</h4>
        <a href="/feed.xml">RSS</a>
        <a href="/sitemap.xml">Sitemap</a>
        <a href="{LEDGER}">Repository</a>
      </div>
    </div>
    <p class="colophon small">Verified against official sources on {ACCESSED}. Specifications carry a
    source and an access date because they change. No prices and no star ratings appear on this site;
    see <a href="/disclosure/">why</a>.</p>
  </div>
</footer>
<script src="/assets/analytics.js" defer></script>
</body>
</html>
"""


# --------------------------------------------------------------------------
# components
# --------------------------------------------------------------------------

def link_button(product: dict) -> str:
    url = product.get("affiliate_url")
    if url and f"tag={TRACKING_ID}" in url:
        return (
            f'<a class="btn" rel="sponsored nofollow noopener" target="_blank" '
            f'href="{e(url)}" data-product="{e(product["id"])}" data-outbound="1">'
            f'Check current price at Amazon <span class="paid">(paid link)</span></a>'
        )
    # Refusal is the correct behaviour. See R06 / FLG-003.
    return (
        '<div class="btn-blocked">'
        '<span class="btn-dead">Outbound link withheld</span>'
        '<span class="small">This link has no <code>tag=' + e(TRACKING_ID) + '</code> parameter, so it '
        'would not credit a sale. It is not shown rather than shown broken. '
        f'<a href="/flagged/#FLG-003">See FLG-003</a>.</span></div>'
    )


LABELS = {
    "capacity_qt": "Capacity (qt)",
    "capacity_l": "Capacity (litres)",
    "temp_min_f": "Minimum temperature (\u00b0F)",
    "temp_max_f": "Maximum temperature (\u00b0F)",
    "watts": "Power (W)",
    "volts": "Voltage (V)",
    "dimensions_in": "External dimensions (in.)",
    "weight_lb": "Weight (lb)",
    "baskets": "Number of baskets",
    "probes_included": "Probes included",
    "sensors_internal": "Internal sensors",
    "sensors_ambient": "Ambient sensors",
    "ambient_max_f": "Ambient sensor limit (\u00b0F)",
    "inserted_probe_max_f": "Inserted probe limit (\u00b0F)",
    "probe_length_in": "Probe length (in.)",
    "probe_diameter_in": "Probe diameter (in.)",
    "presets": "Preset / function count",
    "dishwasher_safe_basket": "Dishwasher-safe basket",
    "dishwasher_safe": "Dishwasher safe",
    "viewing_window": "Viewing window",
    "warranty_years": "Warranty (years)",
    "certification": "Certification",
    "connectivity": "Connectivity",
    "charging": "Charging",
    "probe_battery_hours": "Probe battery (hours)",
    "read_time_sec": "Read time (seconds)",
    "accuracy_f": "Accuracy",
    "nist_certified": "NIST certified",
    "waterproof": "Water resistance",
    "sensor_type": "Sensor type",
    "display": "Display",
    "magnet": "Magnet",
    "leave_in_rated": "Can be left in the oven",
}


def label_for(key: str) -> str:
    if key in LABELS:
        return LABELS[key]
    words = key.replace("_", " ")
    return words[0].upper() + words[1:]


def spec_rows(product: dict, sources: dict) -> str:
    out = []
    for key, item in product.get("specs", {}).items():
        if not isinstance(item, dict):
            continue
        value = item.get("value")
        if isinstance(value, bool):
            value = yesno(value)
        note = item.get("note")

        if value is None:
            rendered = ('<span class="unverified">not stated on any official page '
                        '&mdash; left blank, not guessed</span>')
            if note:
                rendered += f'<div class="note">{e(note)}</div>'
        else:
            if key == "dimensions_in":
                rendered = dims(value)
            elif key == "capacity_qt":
                rendered = f'<span class="num">{e(value)}</span>'
            elif key in ("watts", "volts", "weight_lb", "capacity_l"):
                rendered = f'<span class="num">{e(value)}</span>'
            elif key == "probe_battery_hours":
                rendered = f'<span class="num">{e(value)}</span>'
            else:
                rendered = e(value)
            if item.get("listing_only"):
                rendered += ' <span class="tag-listing">listing only</span>'
            if note:
                rendered += f'<div class="note">{e(note)}</div>'

        src = item.get("source")
        src_html = ""
        if src and src in sources:
            s = sources[src]
            src_html = (f'<a class="srclink cite" href="{e(s["url"])}" rel="nofollow noopener" '
                        f'target="_blank">{e(src)}</a>')
        out.append(
            f'<tr><th scope="row">{e(label_for(key))}</th><td>{rendered}</td>'
            f'<td class="src">{src_html}<span class="srcd">{ACCESSED}</span></td></tr>'
        )
    if not out:
        out.append('<tr><td colspan="3" class="muted">No specification rows exist for this entry.</td></tr>')
    return "".join(out)


def intent_record(product: dict, sources: dict) -> str:
    """The product-intent confirmation record: intended vs observed, never merged."""
    redirect = product.get("observed_redirect")
    redirect_html = (
        f'<a class="cite" href="{e(redirect)}" rel="nofollow noopener" target="_blank">{e(redirect)}</a>'
        if redirect
        else '<span class="unverified">no product page reached</span>'
    )
    tag_state = product.get("redirect_had_tag")
    tag_html = {True: "present", False: '<span class="bad">absent</span>', None: "not observable"}[tag_state]
    return f"""<table class="table intent">
<caption>Product-intent confirmation record</caption>
<thead><tr><th scope="col">Field</th><th scope="col">Value</th></tr></thead>
<tbody>
<tr><th scope="row">Intended ASIN</th><td><span class="unverified">not supplied</span>
  <div class="note">The submitted link carried a 9-character short code, not a 10-character ASIN. Nothing is inferred from the observed target.</div></td></tr>
<tr><th scope="row">Submitted short link</th><td><a class="cite" href="{e(product['supplied_link'])}" rel="nofollow noopener" target="_blank">{e(product['supplied_link'])}</a></td></tr>
<tr><th scope="row">Official listing URL</th><td>{redirect_html}</td></tr>
<tr><th scope="row">Observed redirect target</th><td>{redirect_html}
  <div class="note">Recorded separately on purpose. The observed target is evidence, not intent.</div></td></tr>
<tr><th scope="row">Tracking tag on observed target</th><td>{tag_html} (expected <code>tag={e(TRACKING_ID)}</code>)</td></tr>
<tr><th scope="row">Confirmation date</th><td>{ACCESSED}</td></tr>
<tr><th scope="row">Source</th><td>{', '.join(e(s) for s in product.get('sources', []))}</td></tr>
</tbody></table>"""


def thermo_fact(product: dict, key: str, suffix: str) -> str:
    item = product["specs"].get(key, {})
    value = item.get("value") if isinstance(item, dict) else None
    if value is None:
        return '<span class="unverified">unverified</span>'
    return f"{e(value)}{suffix}"


def product_card(product: dict, sources: dict) -> str:
    if product["identity_status"] != "resolved":
        return f"""<article class="card card-unresolved">
  <div class="card-eyebrow">Slot {product['slot']}</div>
  <h3>Nothing published for this slot</h3>
  <p>The supplied link does not resolve to a product. A name, brand, and specification set cannot
  be confirmed, so none is shown.</p>
  <p class="small"><a class="cite" href="{e(product['supplied_link'])}" rel="nofollow noopener" target="_blank">{e(product['supplied_link'])}</a>
  &middot; <a href="/flagged/#FLG-004">FLG-004</a></p>
</article>"""

    if product["category"] == "thermometers":
        return f"""<article class="card">
  <div class="card-eyebrow">{e(product['brand'])} &middot; {e(product['category_label'])}</div>
  <h3><a href="/products/{e(product['id'].lower())}/">{e(product['name'])}</a></h3>
  <p class="lede">{e(product['one_liner'])}</p>
  <dl class="keyfacts">
    <div><dt>Best for</dt><dd>{e(product['best_for'])}</dd></div>
    <div><dt>Read</dt><dd>{thermo_fact(product, 'read_time_sec', ' sec')}</dd></div>
    <div><dt>Accuracy</dt><dd>{thermo_fact(product, 'accuracy_f', '')}</dd></div>
    <div><dt>Heat limit</dt><dd>{thermo_fact(product, 'ambient_max_f', ' &deg;F ambient')}</dd></div>
  </dl>
  {link_button(product)}
  <p class="card-link"><a href="/products/{e(product['id'].lower())}/">The full comparison &rarr;</a></p>
</article>"""

    cap_v = product["specs"].get("capacity_qt", {}).get("value")
    tmax_v = product["specs"].get("temp_max_f", {}).get("value")
    foot_v = product["specs"].get("dimensions_in", {}).get("value")
    cap = f"{cap_v} qt" if cap_v else "&mdash;"
    tmax = f"{tmax_v} &deg;F" if tmax_v else "&mdash;"
    foot = dims(foot_v) if foot_v else "&mdash;"
    return f"""<article class="card">
  <div class="card-eyebrow">{e(product['brand'])} &middot; {e(product['category_label'])}</div>
  <h3><a href="/products/{e(product['id'].lower())}/">{e(product['name'])}</a></h3>
  <p class="lede">{e(product['one_liner'])}</p>
  <dl class="keyfacts">
    <div><dt>Best for</dt><dd>{e(product['best_for'])}</dd></div>
    <div><dt>Capacity</dt><dd>{cap}</dd></div>
    <div><dt>Top temp</dt><dd>{tmax}</dd></div>
    <div><dt>Footprint</dt><dd>{foot}</dd></div>
  </dl>
  {link_button(product)}
  <p class="card-link"><a href="/products/{e(product['id'].lower())}/">The full comparison &rarr;</a></p>
</article>"""


def compare_table(products: list[dict], sources: dict, keys: list[str]) -> str:
    resolved = [p for p in products if p["identity_status"] == "resolved"]
    if not resolved:
        return ""
    head_cells = "".join(
        f'<th scope="col"><a href="/products/{e(p["id"].lower())}/">{e(p["brand"])}<br>'
        f'<span class="th-sub">{e(p["name"])}</span></a></th>'
        for p in resolved
    )
    rows = []
    for key in keys:
        if all(
            not (isinstance(p["specs"].get(key), dict) and p["specs"].get(key, {}).get("value") is not None)
            for p in resolved
        ):
            continue  # a row of nothing but blanks teaches the reader nothing
        cells = []
        for p in resolved:
            item = p["specs"].get(key, {})
            value = item.get("value") if isinstance(item, dict) else None
            if isinstance(value, bool):
                value = yesno(value)
            if value is None:
                cells.append('<td><span class="unverified">unverified</span></td>')
            else:
                cells.append(f'<td>{e(value)}</td>')
        rows.append(f'<tr><th scope="row">{e(label_for(key))}</th>{"".join(cells)}</tr>')
    return f"""<div class="table-scroll"><table class="table compare">
<thead><tr><th scope="col">What differs</th>{head_cells}</tr></thead>
<tbody>{''.join(rows)}</tbody></table></div>
<p class="small muted">Cells reading &ldquo;unverified&rdquo; mean no official page stated the value.
They are not zero and not &ldquo;no&rdquo;. Values are as published on {ACCESSED}.</p>"""


# --------------------------------------------------------------------------
# pages
# --------------------------------------------------------------------------

def page_home(products, sources, suggestions, flags) -> str:
    resolved = [p for p in products if p["identity_status"] == "resolved"]
    lead = resolved[0]
    cards = "".join(product_card(p, sources) for p in products)
    picks = "".join(
        f'<a class="pick" href="/products/{e(p["id"].lower())}/">'
        f'<span class="pick-brand">{e(p["brand"])}</span>'
        f'<span class="pick-name">{e(p["name"])}</span>'
        f'<span class="pick-fit">{e(p["best_for"])}</span></a>'
        for p in resolved
    )
    return (
        head(
            f"{BRAND} — air fryers and thermometers, compared by specification",
            "Five submitted products, four resolved to real listings. Compare air fryer shapes, "
            "capacities, and counter footprints using manufacturer specifications, with every value sourced and dated.",
            "/",
        )
        + masthead("/", "/")
        + f"""
<section class="hero wrap">
  <p class="kicker">Air fryers &middot; oven-style &middot; thermometers</p>
  <h1>Pick the shape first. The brand is the easy part.</h1>
  <p class="sub">Most air fryer advice starts with a brand. It should start with whether you need two
  baskets, one big basket, or a small oven. Here is what each one actually is, with the specifications
  that decide it &mdash; sourced, dated, and honest about the gaps.</p>
  <div class="picks">{picks}</div>
</section>

<section class="wrap section">
  <div class="section-head">
    <h2>Start with the one that fits</h2>
    <p>All five submitted links resolved to a real listing when checked. One of them served a checkpoint page
    on the first attempt and a product on the second, so it is marked time-dependent. <a href="/flagged/#FLG-004">FLG-004</a>.</p>
  </div>
  <div class="cards">{cards}</div>
</section>

<section class="wrap section band">
  <div class="section-head">
    <h2>The question that stops most returns</h2>
    <p>Does it fit where you plan to put it? Depth and height are the two numbers people skip.</p>
  </div>
  <div class="two-col">
    {compare_table([x for x in products if x["category"] in ("air-fryers", "air-fryer-ovens")], sources, ["capacity_qt", "temp_max_f", "dimensions_in", "watts", "baskets", "presets"])}
    <aside class="aside">
      <h3>Measure before you click</h3>
      <p>Counter depth, cabinet clearance, and the space the door or drawer needs when open. The
      numbers above are the manufacturer's published external dimensions.</p>
      <p class="small">An oven-style unit at 16.9 in. deep needs a deeper counter than a basket unit at
      13.4 in. That single row decides more purchases than wattage does.</p>
      <p><a class="btn-quiet" href="/guides/basket-or-oven-style/">Basket or oven-style: what to compare &rarr;</a></p>
    </aside>
  </div>
</section>

<section class="wrap section">
  <div class="section-head">
    <h2>Guides</h2>
    <p>Question-shaped, answerable from the register. New ones land on a schedule, not in a dump.</p>
  </div>
  <div class="guide-list">
    <a class="guide" href="/guides/basket-or-oven-style/"><span class="guide-k">Compare</span>
      <h3>Basket or oven-style air fryer: what should you compare?</h3>
      <p>Zones, racks, door swing, and the counter depth each one really needs.</p></a>
    <a class="guide" href="/guides/air-fryer-capacity/"><span class="guide-k">Checklist</span>
      <h3>A no-hype checklist for comparing air fryer capacity</h3>
      <p>Quarts are not comparable across shapes. Here is how to read the number.</p></a>
    <a class="guide" href="/guides/cleanup-and-counter-space/"><span class="guide-k">Trade-offs</span>
      <h3>How to assess cleanup and counter-space trade-offs</h3>
      <p>Two baskets or one chamber, dishwasher-safe parts, and where the crumbs go.</p></a>
    <a class="guide" href="/guides/multi-function-appliance/"><span class="guide-k">Before you buy</span>
      <h3>Questions to ask before buying a multi-function kitchen appliance</h3>
      <p>What &ldquo;10-in-1&rdquo; actually promises, and what it costs you in counter.</p></a>
  </div>
</section>

<section class="wrap section">
  <div class="section-head">
    <h2>Where this site is still unsure</h2>
    <p>Seven irregularities, listed with their source links. Reading them is the fastest way to judge
    whether the rest of the site is worth trusting.</p>
  </div>
  <ul class="flaglist">
    {''.join(f'<li><a href="/flagged/#{e(f["id"])}"><span class="flagid">{e(f["id"])}</span> {e(f["title"])}</a> <span class="sev sev-{e(f["severity"])}">{e(f["severity"])}</span></li>' for f in flags)}
  </ul>
  <p><a class="btn-quiet" href="/flagged/">Read all seven &rarr;</a></p>
</section>
"""
        + footer("/")
    )


def page_product(product, products, sources) -> str:
    rel = f"/products/{product['id'].lower()}/"
    if product["identity_status"] != "resolved":
        return (
            head("Unresolved entry — nothing published", "This submitted link does not resolve to a product.", rel)
            + masthead(rel, "")
            + f"""<div class="wrap section">
<h1>Nothing published for this slot</h1>
<p class="sub">The supplied link resolves to an Amazon interstitial, and a catalog search for the code
returns no results. No product is named here, because naming one would mean inventing it.</p>
{intent_record(product, sources)}
<p><a href="/flagged/#FLG-004">FLG-004 &rarr;</a></p>
</div>"""
            + footer(rel)
        )

    model_line = f"Model {e(product['model'])}" if product["model"] else "Model number not stated by the manufacturer"
    pros = "".join(f"<li>{e(x)}</li>" for x in product["tradeoffs"]["pros"])
    cons = "".join(f"<li>{e(x)}</li>" for x in product["tradeoffs"]["cons"])
    questions = "".join(f"<li>{e(q)}</li>" for q in product["questions_answered"])
    others = [
        p for p in products
        if p["category"] == product["category"] and p["id"] != product["id"] and p["identity_status"] == "resolved"
    ]
    others_html = "".join(
        f'<a class="pick" href="/products/{e(o["id"].lower())}/"><span class="pick-brand">{e(o["brand"])}</span>'
        f'<span class="pick-name">{e(o["name"])}</span><span class="pick-fit">{e(o["best_for"])}</span></a>'
        for o in others
    )
    return (
        head(
            f"{product['brand']} {product['name']} — specifications and trade-offs",
            product["one_liner"][:250],
            rel,
            extra=f'<script type="application/ld+json">{json.dumps(product_ld(product))}</script>',
        )
        + masthead(rel, f"/{product['category']}/")
        + f"""
<div class="wrap section">
  <p class="breadcrumb"><a href="/{e(product['category'])}/">{e(product['category_label'])}</a>
    <span>/</span> {e(product['brand'])}</p>
  <h1>{e(product['brand'])} {e(product['name'])}</h1>
  <p class="sub">{e(product['one_liner'])}</p>
  <p class="metaline">{model_line} &middot; specifications verified {ACCESSED} &middot;
  sourced from the manufacturer and the Amazon listing</p>
  {link_button(product)}

  <div class="two-col">
    <div>
      <h2>What the specifications say</h2>
      <p class="small muted">Every row cites the page it came from. A blank row means no official page
      stated the value &mdash; it is left blank rather than guessed.</p>
      <table class="table specs">
        <caption class="sr-only">Verified specifications</caption>
        <thead><tr><th scope="col">Specification</th><th scope="col">Value</th><th scope="col">Source</th></tr></thead>
        <tbody>{spec_rows(product, sources)}</tbody>
      </table>
    </div>
    <aside class="aside">
      <h3>Suits you if</h3>
      <p>{e(product['best_for'])}</p>
      <h3>Skip it if</h3>
      <p>{e(product['tradeoffs']['skip_if'] or 'Not stated.')}</p>
      <h3>Questions this answers</h3>
      <ul class="plain">{questions}</ul>
    </aside>
  </div>

  <div class="two-col">
    <div>
      <h2>What you gain</h2>
      <ul class="tick">{pros}</ul>
    </div>
    <div>
      <h2>What it costs you</h2>
      <ul class="cross">{cons}</ul>
    </div>
  </div>

  <h2>The product-intent record</h2>
  <p class="small muted">Kept as two separate fields on purpose: what the submitted link was meant to
  point at, and what it actually reaches. They are allowed to disagree in public.</p>
  {intent_record(product, sources)}

  <h2>Official pages</h2>
  <ul class="plain">
    <li><a class="cite" href="{e(product['official_url'])}" rel="nofollow noopener" target="_blank">Manufacturer product page</a>
      <span class="small muted">specification source, accessed {ACCESSED}</span></li>
  </ul>

  {'<h2>Compare with</h2><div class="picks">' + others_html + '</div>' if others_html else ''}
</div>
"""
        + footer(rel)
    )


def product_ld(product: dict) -> dict:
    """schema.org Product without offers/price and without aggregateRating, by policy."""
    return {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": f"{product['brand']} {product['name']}",
        "brand": {"@type": "Brand", "name": product["brand"]},
        "model": product.get("model") or "",
        "description": product["one_liner"],
        "url": f"{SITE}/products/{product['id'].lower()}/",
    }


def page_category(slug, label, blurb, products, sources) -> str:
    rel = f"/{slug}/"
    listed = [p for p in products if p["category"] == slug]
    cards = "".join(product_card(p, sources) for p in listed)
    if not cards:
        cards = '<p class="muted">No verified product in this category yet.</p>'
    keys = ["capacity_qt", "temp_max_f", "dimensions_in", "watts", "baskets", "presets", "warranty_years"]
    return (
        head(f"{label} — compared by specification", blurb, rel)
        + masthead(rel, rel)
        + f"""<div class="wrap section">
<p class="breadcrumb"><a href="/">Start here</a> <span>/</span> {e(label)}</p>
<h1>{e(label)}</h1>
<p class="sub">{e(blurb)}</p>
{compare_table(listed, sources, keys)}
<div class="cards">{cards}</div>
</div>"""
        + footer(rel)
    )


GUIDES = [
    {
        "slug": "basket-or-oven-style",
        "kicker": "Compare",
        "title": "Basket or oven-style air fryer: what should you compare?",
        "desc": "Two baskets, one basket, or a small oven. The four differences that actually change your cooking.",
        "body": """
<p class="standfirst">The first decision is not the brand. It is whether you are buying a drawer you
pull out or a small oven you open. Those two shapes solve different problems, and the wrong one is why
air fryers get returned.</p>

<h2>1. Zones, not quarts</h2>
<p>A 6-quart dual-basket unit is not a 6-quart cooking space. It is two 3-quart spaces with a fixed
divider. A 26-quart oven is one large space you can put racks in. If you often cook one big item, the
dual basket is the wrong purchase even though the total number looks similar.</p>
<p>What to do: count how many foods you cook <em>at the same time</em>, then ask whether they need
different temperatures. Two foods, two temperatures, one appliance &rarr; two zones. One food, big
batch &rarr; one large chamber.</p>

<h2>2. The counter number nobody checks</h2>
<p>Depth is the spec that decides whether the appliance ends up in a cupboard. A basket unit in this
register is 13.38 in. deep. An oven-style unit is 16.9 in. deep and 14.8 in. tall. Add clearance for
the door swing or the drawer pull.</p>

<h2>3. Access and cleaning</h2>
<p>Two removable nonstick baskets rinse in a sink. An oven has racks, a tray, and interior walls. The
basket is easier for daily small cooking. The oven is easier for a full meal. Neither is easier for
everything, and any page that says otherwise is selling rather than explaining.</p>

<h2>4. The temperature ceiling</h2>
<p>Published ceilings in this register run from 400&nbsp;&deg;F to 450&nbsp;&deg;F on basket units, with
the oven rated higher for broiling. A 50-degree difference matters for a crisp finish and matters
almost not at all for reheating.</p>

<h2>What this does not tell you</h2>
<p>It does not tell you which one cooks better. That requires using both, and this site does not
pretend otherwise. It tells you which one fits the way you cook, which is the question you can
actually answer before you buy.</p>
""",
    },
    {
        "slug": "air-fryer-capacity",
        "kicker": "Checklist",
        "title": "A no-hype checklist for comparing air fryer capacity",
        "desc": "Why quarts are not comparable across shapes, and the four questions that make the number meaningful.",
        "body": """
<p class="standfirst">Quarts are the most quoted and least comparable number on an air fryer box. Here
is how to turn it into something you can use.</p>

<h2>Ask four questions about the same number</h2>
<ol>
<li><strong>Is it one chamber or several?</strong> Six quarts as two 3-quart baskets cannot hold what
six quarts as one basket holds.</li>
<li><strong>What shape is the chamber?</strong> A tall narrow basket and a wide flat one hold different
foods at the same volume.</li>
<li><strong>How many people is it for?</strong> The manufacturer states a serving range for some models
and not others. Where it is stated, quote it; where it is not, do not invent it.</li>
<li><strong>Does the basket come out?</strong> Capacity you cannot lift out and wash is capacity you
use once.</li>
</ol>

<h2>Read the dimension line, not the capacity line</h2>
<p>Two 8-quart units can differ by more than an inch in every direction. The external dimensions decide
whether it fits; the internal capacity decides whether the food fits. You need both, and most listings
lead with only the second.</p>

<h2>Where this site leaves a blank</h2>
<p>If a manufacturer does not publish a serving range or a preset count, the row stays empty here and
is marked unverified. An empty row is information: it means the number you saw elsewhere came from
somewhere other than the manufacturer.</p>
""",
    },
    {
        "slug": "cleanup-and-counter-space",
        "kicker": "Trade-offs",
        "title": "How to assess cleanup and counter-space trade-offs",
        "desc": "Dishwasher-safe parts, basket count, and the real cost of leaving an appliance out.",
        "body": """
<p class="standfirst">An air fryer that lives in a cupboard gets used half as often as one that lives on
the counter. That is a specification problem, not a discipline problem.</p>

<h2>Cleaning, by part count</h2>
<p>A single-basket unit has one basket and one tray. A dual-basket unit has two of each. That is twice
the washing for the ability to cook two foods at once &mdash; worth it if you use both zones, wasted
effort if you usually use one.</p>
<p>Oven-style units add racks and a drip tray, and the interior walls need wiping. Check whether the
manufacturer states dishwasher safety for each removable part; if it is stated for the basket but not
the tray, treat the tray as hand-wash.</p>

<h2>Counter space, measured honestly</h2>
<p>Put a tape on the counter. Subtract the appliance depth. Subtract the clearance the door or drawer
needs. What is left is your actual working space. Many kitchens have the footprint but not the
clearance.</p>

<h2>The under-cabinet test</h2>
<p>Height plus the lid or door arc is the number that matters if the appliance sits under cabinets.
A tall unit that fits the counter may not fit the gap.</p>

<h2>What to do with this</h2>
<p>Compare the depth and height rows on each product page here before anything else. They are the two
rows a return is usually about.</p>
""",
    },
    {
        "slug": "multi-function-appliance",
        "kicker": "Before you buy",
        "title": "Questions to ask before buying a multi-function kitchen appliance",
        "desc": "What a function count actually promises, and what you pay for it in counter space.",
        "body": """
<p class="standfirst">&ldquo;10-in-1&rdquo; is a count of buttons, not a measure of how well any one of
them works. Six questions will tell you more than the function list does.</p>

<h2>The six questions</h2>
<ol>
<li><strong>Which two functions will I actually use weekly?</strong> If you cannot name two, the count is
marketing.</li>
<li><strong>Does the function I care about have a published temperature range?</strong> A mode without a
stated range is a label.</li>
<li><strong>What does it displace?</strong> A multi-function oven usually replaces a toaster. If you
still need the toaster, you have bought counter space, not saved it.</li>
<li><strong>What is in the box today?</strong> Accessory lists change between channels and between
production runs. Ask for the current list by model number.</li>
<li><strong>What is the warranty period, and who honours it?</strong> One year from the manufacturer is
the common answer; confirm it rather than assume it.</li>
<li><strong>What does the manufacturer not publish?</strong> A missing wattage or preset count is a
reason to wait, not a reason to fill in the gap yourself.</li>
</ol>

<h2>Why this site leaves gaps visible</h2>
<p>Because on at least one product in this register, the manufacturer's own page contradicted itself on
the preset count, and on another the wattage disagreed between the manufacturer page and the retailer
listing. Those are published on the Flagged for Review page rather than smoothed over.</p>
""",
    },
]


def page_guide(g, products) -> str:
    rel = f"/guides/{g['slug']}/"
    others = "".join(
        f'<a class="guide" href="/guides/{e(o["slug"])}/"><span class="guide-k">{e(o["kicker"])}</span>'
        f'<h3>{e(o["title"])}</h3></a>'
        for o in GUIDES if o["slug"] != g["slug"]
    )
    return (
        head(g["title"], g["desc"], rel, extra=f'<script type="application/ld+json">{json.dumps(article_ld(g))}</script>')
        + masthead(rel, "/guides/")
        + f"""<article class="wrap section prose">
<p class="breadcrumb"><a href="/guides/">Guides</a> <span>/</span> {e(g['kicker'])}</p>
<h1>{e(g['title'])}</h1>
<p class="metaline">Published {ACCESSED} &middot; written from manufacturer specifications, not from hands-on testing
&middot; <a href="/disclosure/">how this site works</a></p>
{g['body']}
<div class="callout">
<p><strong>This is a specification comparison, not a product test.</strong> Nobody here has used these
appliances. The value is in reading the official documentation carefully and showing you where it is
incomplete or contradictory &mdash; not in pretending to have cooked with them.</p>
</div>
</article>
<div class="wrap section">
  <h2>Keep reading</h2>
  <div class="guide-list">{others}</div>
</div>"""
        + footer(rel)
    )


def article_ld(g) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": g["title"],
        "description": g["desc"],
        "datePublished": ACCESSED,
        "dateModified": ACCESSED,
        "author": {"@type": "Organization", "name": BRAND},
        "publisher": {"@type": "Organization", "name": BRAND},
        "mainEntityOfPage": f"{SITE}/guides/{g['slug']}/",
    }


def page_guides_index(products) -> str:
    cards = "".join(
        f'<a class="guide" href="/guides/{e(g["slug"])}/"><span class="guide-k">{e(g["kicker"])}</span>'
        f'<h3>{e(g["title"])}</h3><p>{e(g["desc"])}</p></a>'
        for g in GUIDES
    )
    return (
        head("Guides", "Question-shaped guides answered from verified manufacturer specifications.", "/guides/")
        + masthead("/guides/", "/guides/")
        + f"""<div class="wrap section">
<h1>Guides</h1>
<p class="sub">Four guides, each answering a question you can settle before you buy. Every claim traces
to a manufacturer page, and every gap is left visible.</p>
<div class="guide-list">{cards}</div>
<h2>The cadence</h2>
<p class="small muted">One guide every two weeks, added to the sitemap and the feed in the same commit.
Topic selection moves from editorial judgment to measured queries once Search Console data exists.
That is a proposal, not a fact &mdash; see <a href="/suggestions/#SG-11">SG-11</a>.</p>
</div>"""
        + footer("/guides/")
    )


def page_sources(sources) -> str:
    rows = "".join(
        f"""<tr>
<td><span class="sid">{e(s['id'])}</span></td>
<td><a class="cite" href="{e(s['url'])}" rel="nofollow noopener" target="_blank">{e(s['title'])}</a>
<div class="note">{e(s.get('supports',''))}</div></td>
<td>{e(s['org'])}</td>
<td><span class="tier tier-{e(s['tier'])}">{e(s['tier'])}</span></td>
<td class="nowrap">{e(s['accessed'])}</td></tr>"""
        for s in sources
    )
    return (
        head("Source register", "Every source used on this site, with what it supports and when it was read.", "/sources/")
        + masthead("/sources/", "")
        + f"""<div class="wrap section">
<h1>Source register</h1>
<p class="sub">Nineteen sources. Each one was opened on {ACCESSED}. Third-party review sites were read
while orienting but are never cited for a value &mdash; if a number is not on a manufacturer page, an
Amazon listing, or a government site, it does not appear on this site.</p>
<table class="table sources">
<thead><tr><th scope="col">ID</th><th scope="col">Source</th><th scope="col">Publisher</th>
<th scope="col">Tier</th><th scope="col">Accessed</th></tr></thead>
<tbody>{rows}</tbody></table>
<h2>Tiers, defined</h2>
<ul class="plain">
<li><span class="tier tier-official">official</span> The publisher's own product page. Usable as a citation.</li>
<li><span class="tier tier-official_help">official_help</span> Amazon policy, government guidance, or vendor help documentation. Usable as a citation.</li>
<li><span class="tier tier-listing">listing</span> A retailer detail page. Used for identity; specs from here are marked listing-only.</li>
<li><span class="tier tier-not_used">not_used</span> Review sites, aggregators, affiliate blogs. Never cited for a value.</li>
</ul>
</div>"""
        + footer("/sources/")
    )


def page_flags(flags, products) -> str:
    by_id = {p["id"]: p for p in products}
    items = []
    for f in flags:
        p = by_id.get(f["product"])
        thing = f"{p['brand']} {p['name']}" if p and p.get("name") else ("All products" if f["product"] == "all" else "Unresolved entry")
        srcs = ", ".join(f'<a href="#{e(x)}">{e(x)}</a>' for x in f["sources"])
        items.append(f"""<article class="flag" id="{e(f['id'])}">
<div class="flag-head">
  <span class="flagid">{e(f['id'])}</span>
  <span class="sev sev-{e(f['severity'])}">{e(f['severity'])}</span>
  <span class="small muted">{e(thing)}</span>
</div>
<h3>{e(f['title'])}</h3>
<p>{e(f['detail'])}</p>
<p class="small"><strong>What closes it:</strong> {e(f['action'])}</p>
<p class="small"><strong>Sources:</strong> {srcs}</p>
</article>""")
    return (
        head("Flagged for review", "Seven irregularities found during verification, published with their source links.", "/flagged/")
        + masthead("/flagged/", "")
        + f"""<div class="wrap section">
<h1>Flagged for review</h1>
<p class="sub">These are the places where the official sources disagree, where a submitted link does not
resolve, or where there is simply no data yet. They are published rather than resolved quietly, because
a site that hides its gaps cannot be audited.</p>
<p class="small muted">None of these block publication. Each one names what would close it.</p>
<div class="flags">{''.join(items)}</div>
</div>"""
        + footer("/flagged/")
    )


def page_questions(qs) -> str:
    have = [q for q in qs if q["status"] == "have"]
    dont = [q for q in qs if q["status"] != "have"]

    def render(group):
        out = []
        for q in group:
            answer = (
                f'<p>{e(q["answer"])}</p>' if q["answer"]
                else '<p class="unverified">No official source answers this yet. Nothing is asserted here.</p>'
            )
            src = f' <a class="srclink" href="#{e(q["source"])}">{e(q["source"])}</a>' if q["source"] else ""
            out.append(f"""<article class="q">
<div class="q-head"><span class="qid">{e(q['id'])}</span>
<span class="badge badge-{'have' if q['status']=='have' else 'dont'}">{'have' if q['status']=='have' else "don't have"}</span></div>
<h3>{e(q['question'])}</h3>
{answer}{src}
<p class="small"><strong>Why it matters:</strong> {e(q['consequence'])}</p>
<p class="small"><strong>Owner:</strong> {e(q['owner'])} &middot; <strong>How it closes:</strong> {e(q['how_to_close'])}</p>
</article>""")
        return "".join(out)

    return (
        head("Open questions", "Twenty-four questions, what is known, what is missing, and what would close each one.", "/questions/")
        + masthead("/questions/", "")
        + f"""<div class="wrap section">
<h1>Open questions</h1>
<p class="sub">Before a decision can reasonably be made, these have to be settled. Each carries what is
known, what is missing, and the specific step that closes it &mdash; so a missing answer reads as a to-do
rather than a dead end.</p>
<h2>Answered by an official source <span class="count">{len(have)}</span></h2>
<div class="qlist">{render(have)}</div>
<h2>Not answered anywhere yet <span class="count">{len(dont)}</span></h2>
<p class="small muted">These are the ones that block a decision. Several can be closed in minutes by the
account holder; they are not research problems, they are access problems.</p>
<div class="qlist">{render(dont)}</div>
</div>"""
        + footer("/questions/")
    )


def page_suggestions(sg) -> str:
    groups = {}
    for s in sg["suggestions"]:
        groups.setdefault(s["category"], []).append(s)
    blocks = []
    for cat, items in groups.items():
        cards = []
        for s in items:
            status_class = "st-shipped" if s["status"] == "shipped" else ("st-blocked" if s["status"] == "blocked" else "st-proposed")
            cards.append(f"""<article class="sugg" id="{e(s['id'])}">
<div class="sugg-head">
  <span class="sid">{e(s['id'])}</span>
  <span class="pill {status_class}">{e(s['status'])}</span>
  <span class="pill">impact: {e(s['impact'])}</span>
  <span class="pill">effort: {e(s['effort'])}</span>
</div>
<h3>{e(s['title'])}</h3>
<p><strong>The problem.</strong> {e(s['problem'])}</p>
<p><strong>The proposal.</strong> {e(s['proposal'])}</p>
<p><strong>The trade-off.</strong> {e(s['tradeoff'])}</p>
<p class="small"><strong>Decision needed:</strong> {e(s['decision_needed'])}</p>
{f'<p class="small blocked">Blocked by {e(s["blocked_by"])}</p>' if s.get('blocked_by') else ''}
{f'<p class="small">{e(s["note"])}</p>' if s.get('note') else ''}
</article>""")
        blocks.append(f'<h2>{e(cat)}</h2><div class="suggs">{"".join(cards)}</div>')

    return (
        head("Suggestions review queue", "Fourteen proposals with trade-offs, held for a decision rather than implemented silently.", "/suggestions/")
        + masthead("/suggestions/", "")
        + f"""<div class="wrap section">
<h1>Suggestions review queue</h1>
<p class="sub">A section built for reviewing before implementing. Each proposal states the problem it
solves, what it costs, and the specific decision it needs from you. Three are already shipped and
labelled as such; the rest do nothing until you choose.</p>
<div class="callout">
<p><strong>How to decide.</strong> Read impact and effort together. A high-impact, low-effort item that
you disagree with is still worth rejecting explicitly, because an unanswered proposal becomes a
default. Write the decision into <code>data/suggestions.json</code> under <code>decided</code> and the
next build renders it as an outcome.</p>
</div>
<div class="shipped">
<h2>Already shipped in this build</h2>
<ul class="tick">{''.join(f'<li>{e(x)}</li>' for x in sg['already_shipped'])}</ul>
</div>
{''.join(blocks)}
</div>"""
        + footer("/suggestions/")
    )


def page_dashboard(products, ledger, compliance, flags) -> str:
    resolved = [p for p in products if p["identity_status"] == "resolved"]
    rows = "".join(
        f"""<tr><th scope="row">{e(p['id'])}</th><td>{e(p['brand'])} {e(p['name'])}</td>
<td>{e(p['model']) if p['model'] else '<span class="unverified">not stated</span>'}</td>
<td><a href="/products/{e(p['id'].lower())}/">review</a></td>
<td>{'resolved' if p['identity_status']=='resolved' else '<span class="bad">unresolved</span>'}</td>
<td>{'<span class="bad">absent</span>' if p['redirect_had_tag'] is False else 'not observable'}</td>
<td>{len(p['specs'])} fields / {sum(1 for v in p['specs'].values() if isinstance(v, dict) and v.get('value') is None)} blank</td></tr>"""
        for p in products
    )
    rule_rows = "".join(
        f"""<tr><th scope="row">{e(r['id'])}</th><td>{e(r['requirement'])}</td>
<td><span class="pill st-{'shipped' if r['status']=='met' else 'blocked'}">{e(r['status'])}</span></td>
<td class="small">{e(r['where_enforced'])}</td><td><a class="srclink" href="#{e(r['source'])}">{e(r['source'])}</a></td></tr>"""
        for r in compliance["rules"]
    )
    event_rows = "".join(
        f"<tr><th scope=\"row\">{e(ev['name'])}</th><td>{e(ev['when'])}</td><td class=\"small\">{e(', '.join(ev['fields']))}</td></tr>"
        for ev in compliance["events"]
    )
    return (
        head("Dashboard", "Status of every entry, every compliance rule, and every measurement event. No fabricated metrics.", "/dashboard/")
        + masthead("/dashboard/", "")
        + f"""<div class="wrap section">
<h1>Dashboard</h1>
<p class="sub">Status, not scores. There is no traffic history, no conversion rate, and no revenue
figure here, because none exists yet. Showing a zero would be a claim; showing nothing is accurate.</p>

<h2>Entries</h2>
<div class="table-scroll"><table class="table dash">
<thead><tr><th scope="col">ID</th><th scope="col">Product</th><th scope="col">Model</th>
<th scope="col">Page</th><th scope="col">Identity</th><th scope="col">Tracking tag</th><th scope="col">Spec coverage</th></tr></thead>
<tbody>{rows}</tbody></table></div>

<h2>Campaign ledger</h2>
<p class="small muted">Schema defined, rows empty. Columns: {e(', '.join(ledger['columns']))}.
Populated only from an authorized first-party report, with the report name and export date recorded in
<code>provenance</code>. <a href="/flagged/#FLG-007">FLG-007</a>.</p>
<table class="table"><thead><tr><th scope="col">date</th><th scope="col">source</th><th scope="col">channel</th>
<th scope="col">eligible sessions</th><th scope="col">clicks</th><th scope="col">reported orders</th></tr></thead>
<tbody><tr><td colspan="6" class="muted">No rows. No authorized report has been entered.</td></tr></tbody></table>

<h2>Compliance rules</h2>
<div class="table-scroll"><table class="table dash">
<thead><tr><th scope="col">ID</th><th scope="col">Requirement</th><th scope="col">Status</th>
<th scope="col">Where enforced</th><th scope="col">Source</th></tr></thead>
<tbody>{rule_rows}</tbody></table></div>
<p class="small muted">One rule is <em>blocked</em> rather than met: the tracking tag. That single block
is why no outbound button renders on this site. <a href="/flagged/#FLG-003">FLG-003</a>.</p>

<h2>The five events</h2>
<table class="table"><thead><tr><th scope="col">Event</th><th scope="col">Fires when</th><th scope="col">Fields recorded</th></tr></thead>
<tbody>{event_rows}</tbody></table>
<p class="small muted">{e(compliance['event_notes'])}</p>

<h2>Flagged items</h2>
<table class="table"><thead><tr><th scope="col">ID</th><th scope="col">Severity</th><th scope="col">Title</th></tr></thead>
<tbody>{''.join(f'<tr><td><a href="/flagged/#{e(f["id"])}">{e(f["id"])}</a></td><td><span class="sev sev-{e(f["severity"])}">{e(f["severity"])}</span></td><td>{e(f["title"])}</td></tr>' for f in flags)}</tbody></table>
</div>"""
        + footer("/dashboard/")
    )


def page_disclosure(compliance, sources) -> str:
    quote_rows = "".join(
        f"""<tr><th scope="row">{e(r['id'])}</th><td>{e(r['requirement'])}
<blockquote>{e(r['quote'])}</blockquote></td>
<td><a class="srclink" href="#{e(r['source'])}">{e(r['source'])}</a></td>
<td><span class="pill st-{'shipped' if r['status']=='met' else 'blocked'}">{e(r['status'])}</span></td></tr>"""
        for r in compliance["rules"]
    )
    return (
        head("Disclosure and method", "How this site earns, what it will not display, and how each value is sourced.", "/disclosure/")
        + masthead("/disclosure/", "")
        + f"""<div class="wrap section prose">
<h1>Disclosure and method</h1>
<div class="bigdisclose">
<p><strong>{e(DISCLOSURE)}</strong></p>
<p>This page exists so that the disclosure is not only in a footer. It is repeated under the masthead on
every page, it appears in the footer on every page, and it is on this page twice.</p>
</div>

<h2>What we do not display, and why</h2>
<p><strong>No prices.</strong> Amazon's Program Policies allow a site to show prices and availability only
if Amazon serves the link that displays them, or if the data comes from the Creators API or the Product
Advertising API. This site does neither, so it shows no price at all. Every button says &ldquo;check
current price at Amazon&rdquo; and sends you to the source.</p>
<p><strong>No star ratings or review counts.</strong> The same policies restrict displaying customer
reviews and star ratings to those obtained through the Product Advertising API. None appear here.</p>
<p><strong>No price tracking or alerts.</strong> The policies prohibit price tracking and price alerting
functionality. This site stores no price at all.</p>

<h2>What we do display</h2>
<p>Specifications published by the manufacturer, each with a source ID and the date it was read. Where
two official pages disagree, the field is left blank and the conflict is published on the
<a href="/flagged/">Flagged for review</a> page.</p>

<h2>Tracked outbound links</h2>
<p>Every outbound product link must carry <code>tag={e(TRACKING_ID)}</code> as a URL parameter. The build
refuses to render a button that lacks it. Right now that means no outbound button renders, because the
supplied links carry no tag. That is described on
<a href="/flagged/#FLG-003">FLG-003</a> rather than worked around.</p>

<h2>Measurement</h2>
<p>Five events, no cookies, no identifiers, no fingerprinting: page views, outbound product clicks, guide
reads, suggestion votes, and disclosure views. The endpoint is unset in this build, so nothing is
recorded. When it is set, the privacy policy must name it before traffic arrives.</p>

<h2>Editorial position</h2>
<p>This site compares published specifications. It does not test products and never claims to. Where a
recommendation depends on hands-on experience, the site says so instead of implying experience it does
not have &mdash; which is also what the FTC's Endorsement Guides require of an endorser.</p>

<h2>Rule-by-rule record</h2>
<div class="table-scroll"><table class="table rules">
<thead><tr><th scope="col">ID</th><th scope="col">Requirement and quoted basis</th>
<th scope="col">Source</th><th scope="col">Status</th></tr></thead>
<tbody>{quote_rows}</tbody></table></div>
</div>"""
        + footer("/disclosure/")
    )


def page_404() -> str:
    return (
        head("Not found", "That page does not exist.", "/404.html")
        + masthead("/404.html", "")
        + """<div class="wrap section"><h1>Not found</h1>
<p class="sub">That page does not exist. Start from <a href="/">the front page</a> or
<a href="/guides/">the guides</a>.</p></div>"""
        + footer("/404.html")
    )


# --------------------------------------------------------------------------
# feeds and checks
# --------------------------------------------------------------------------

def sitemap() -> str:
    urls = ["/", "/air-fryers/", "/air-fryer-ovens/", "/thermometers/", "/guides/", "/sources/",
            "/flagged/", "/questions/", "/suggestions/", "/dashboard/", "/disclosure/"]
    urls += [f"/products/{p}/" for p in ("p1", "p2", "p3", "p4", "p5")]
    urls += [f"/guides/{g['slug']}/" for g in GUIDES]
    body = "".join(
        f"<url><loc>{SITE}{u}</loc><lastmod>{ACCESSED}</lastmod>"
        f"<changefreq>{'weekly' if u in ('/', '/guides/') else 'monthly'}</changefreq>"
        f"<priority>{'1.0' if u == '/' else '0.7' if u.startswith('/guides/') else '0.5'}</priority></url>"
        for u in urls
    )
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + body + "</urlset>\n")


def feed() -> str:
    items = "".join(
        f"<item><title>{e(g['title'])}</title><link>{SITE}/guides/{g['slug']}/</link>"
        f"<guid isPermaLink=\"true\">{SITE}/guides/{g['slug']}/</guid>"
        f"<pubDate>Thu, 20 Nov 2026 08:00:00 +0000</pubDate>"
        f"<description>{e(g['desc'])}</description></item>"
        for g in GUIDES
    )
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel>'
            f"<title>{e(BRAND)}</title><link>{SITE}/</link>"
            f"<description>Air fryers and thermometers, compared by published specification.</description>"
            f"<language>en-us</language>{items}</channel></rss>\n")


def relativise(text: str, depth: int) -> str:
    """Rewrite root-absolute hrefs/srcs into depth-relative ones.

    The site is published under a project subpath (github.io/Affil3/), so a
    leading slash would escape the project. Every internal reference is made
    relative instead, which also means the site works from any mount point.
    """
    prefix = "" if depth == 0 else "../" * depth

    def href_sub(m):
        target = m.group(2)
        if target == "/":
            return f'{m.group(1)}="{prefix or "./"}"'
        return f'{m.group(1)}="{prefix}{target.lstrip("/")}"'

    text = re.sub(r'(href|src)="(/[^"]*)"', href_sub, text)
    # keep canonical/og/feed absolute where they already point at SITE
    return text


def write(rel: str, text: str) -> None:
    cleaned = rel.lstrip("/")
    if cleaned in ("", "/"):
        cleaned = "index.html"
    path = DOCS / cleaned
    path.parent.mkdir(parents=True, exist_ok=True)
    if cleaned.endswith(".html"):
        depth = len(pathlib.PurePosixPath(cleaned).parts) - 1
        text = relativise(text, depth)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    if DOCS.exists():
        shutil.rmtree(DOCS)
    (DOCS / "assets").mkdir(parents=True)

    src = load("sources")["sources"]
    sources = {s["id"]: s for s in src}
    pdata = load("products")
    products = pdata["products"]
    flags = pdata["flags"]
    compliance = load("compliance")
    suggestions = load("suggestions")
    questions = load("questions")["questions"]
    ledger = load("campaign-ledger")

    write("/", page_home(products, sources, suggestions, flags))
    for p in products:
        write(f"/products/{p['id'].lower()}/index.html", page_product(p, products, sources))
    write("/air-fryers/index.html", page_category(
        "air-fryers", "Air fryers",
        "Drawer-style units. One basket for a big batch, two baskets for two foods at two temperatures.",
        products, sources))
    write("/air-fryer-ovens/index.html", page_category(
        "air-fryer-ovens", "Oven-style air fryers",
        "Racks and french doors. The choice when the basket is the bottleneck and counter depth is not.",
        products, sources))
    write("/thermometers/index.html", page_category(
        "thermometers", "Thermometers",
        "Probe thermometers. Read how the heat rating splits between the tip in the meat and the air around it.",
        products, sources))
    write("/guides/index.html", page_guides_index(products))
    for g in GUIDES:
        write(f"/guides/{g['slug']}/index.html", page_guide(g, products))
    write("/sources/index.html", page_sources(src))
    write("/flagged/index.html", page_flags(flags, products))
    write("/questions/index.html", page_questions(questions))
    write("/suggestions/index.html", page_suggestions(suggestions))
    write("/dashboard/index.html", page_dashboard(products, ledger, compliance, flags))
    write("/disclosure/index.html", page_disclosure(compliance, sources))
    write("/404.html", page_404())
    write("/sitemap.xml", sitemap())
    write("/feed.xml", feed())
    # robots.txt and .nojekyll are owned by the root-site session. Do not write them.
    # Request logged in COORDINATION.md: point the root robots.txt sitemap line at
    # /editorial/sitemap.xml so this subtree is discoverable.

    for asset in ("site.css", "analytics.js"):
        shutil.copyfile(ROOT / "tools" / "assets" / asset, DOCS / "assets" / asset)

    if ANALYTICS_ENDPOINT:
        js = (DOCS / "assets" / "analytics.js").read_text(encoding="utf-8")
        (DOCS / "assets" / "analytics.js").write_text(
            js.replace('var ENDPOINT = "";', f'var ENDPOINT = "{ANALYTICS_ENDPOINT}";'), encoding="utf-8")

    print(f"built {len(list(DOCS.rglob('*.html')))} html files into editorial/")
    print(f"analytics endpoint: {ANALYTICS_ENDPOINT or '(unset - records nothing)'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
