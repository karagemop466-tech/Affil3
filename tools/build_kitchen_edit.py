#!/usr/bin/env python3
"""Build every HTML page of the ShopNow Kitchen Edit site from content fragments.

- Single shared layout guarantees the disclosure strip appears above the fold on
  EVERY page and the required Associates statement appears in EVERY footer.
- `--check` mode regenerates into a temp dir and exits 1 if committed pages differ
  (CI freshness gate). Run with no args to write pages in place.

This build ships as the self-contained `/kitchen-edit/` surface of the site
(see README "What is published"). The canonical product register and site-wide
gates remain the root publication (data/*.json + tools/build.mjs + tools/verify.mjs).

Usage:  python3 tools/build_kitchen_edit.py [--check]
"""
import json
import os
import shutil
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.join(REPO, "kitchen-edit")
BASE = "https://karagemop466-tech.github.io/Affil3/kitchen-edit/"
ROOT_SITE = "https://karagemop466-tech.github.io/Affil3/"

PAGES = {
    # output path (relative): fragment key, title, description, kind
    "index.html": ("index", "ShopNow Kitchen Edit — Air fryers, ovens & kitchen gear, chosen with the boring questions asked first",
        "A reader-supported kitchen shop and guide: dual-basket air fryers, oven-style air fryers, family-size baskets and the tools that make them honest. Every pick carries its sourcing.", "home"),
    "guides/index.html": ("guides/index", "Guides — ShopNow Kitchen Edit",
        "Question-shaped buying guides for air fryers and multi-function kitchen appliances: basket vs oven styles, capacity checklists, cleanup and counter-space trade-offs.", "section"),
    "guides/basket-or-oven-air-fryer.html": ("guides/basket-or-oven-air-fryer", "Basket or oven-style air fryer: what should you compare? — ShopNow Kitchen Edit",
        "The real differences between basket air fryers and oven-style air fryers: timing, capacity shape, cleanup, counter space and the questions to ask before you pick a side.", "guide"),
    "guides/air-fryer-capacity-checklist.html": ("guides/air-fryer-capacity-checklist", "A no-hype checklist for comparing air fryer capacity — ShopNow Kitchen Edit",
        "Quarts lie a little. Use this checklist to compare air fryer capacity by portions per basket, shape, and what you actually cook — without trusting the big number on the box.", "guide"),
    "guides/cleanup-and-counter-space.html": ("guides/cleanup-and-counter-space", "How to assess cleanup and counter-space trade-offs — ShopNow Kitchen Edit",
        "The two costs no spec sheet leads with: what you'll wash, and what you'll give up on the counter. A practical way to weigh dishwasher-safe parts, coatings and footprint.", "guide"),
    "guides/multifunction-appliance-questions.html": ("guides/multifunction-appliance-questions", "Questions to ask before buying a multi-function kitchen appliance — ShopNow Kitchen Edit",
        "Air fryer ovens, combos and 12-in-1 counters: the questions that separate appliances you'll use weekly from appliances you'll store in the garage.", "guide"),
    "products/index.html": ("products/index", "Shop the picks — ShopNow Kitchen Edit",
        "The current shortlist: dual-basket air fryers, oven-style air fryers, family-size baskets and a smart thermometer — each with its confirmation record and full sourcing.", "section"),
    "products/p1.html": ("products/p1", "Dual-basket air fryer — listing pending confirmation — ShopNow Kitchen Edit",
        "Product-intent record and category notes for the submitted dual-basket air fryer link. Listing identity pending confirmation in the enrolled Associates workflow.", "product"),
    "products/p2.html": ("products/p2", "French-door air-fryer toaster oven — listing pending confirmation — ShopNow Kitchen Edit",
        "Product-intent record and category notes for the submitted French-door multi-function air fryer oven link. Listing identity pending confirmation.", "product"),
    "products/p3.html": ("products/p3", "Family-size basket air fryer — listing pending confirmation — ShopNow Kitchen Edit",
        "Product-intent record and category notes for the submitted family-size basket air fryer link. Listing identity pending confirmation.", "product"),
    "products/p4.html": ("products/p4", "Listing destination not yet observed — ShopNow Kitchen Edit",
        "Product-intent record for the submitted link whose destination could not be observed (Amazon checkpoint interstitial on the observation date). Nothing inferred.", "product"),
    "products/p5.html": ("products/p5", "Wireless smart meat thermometer — listing pending confirmation — ShopNow Kitchen Edit",
        "Product-intent record and category notes for the submitted wireless smart meat thermometer link. Listing identity pending confirmation.", "product"),
    "summary/index.html": ("summary/index", "Executive summary — ShopNow Kitchen Edit",
        "The whole project on one page: what this site is, the tracking ID, what was verified from official sources, what stays flagged, and what happens next.", "section"),
    "sourcing/index.html": ("sourcing/index", "How we research — source register — ShopNow Kitchen Edit",
        "Every official source this site relies on, with what was verified, when, and the exact language observed. Blank beats invented.", "section"),
    "analysis/index.html": ("analysis/index", "Findings & analysis — ShopNow Kitchen Edit",
        "What the verification and observation passes found: niche signals, the tracking gap, the identifier mismatch, and what each finding means for the next decision.", "section"),
    "flagged/index.html": ("flagged/index", "Flagged for review — ShopNow Kitchen Edit",
        "Every open irregularity and unverified item, with source links, in one place. Flags do not block publication; they wait for a human with the right account access.", "section"),
    "compliance/index.html": ("compliance/index", "Compliance gate — ShopNow Kitchen Edit",
        "The publishing workflow: automated checks that run in CI, and the manual gates — Special Link verification, API policy, endorsement context, claims review — before anything ships.", "section"),
    "analytics/index.html": ("analytics/index", "Analytics & campaign ledger — ShopNow Kitchen Edit",
        "The five defined events, the privacy contract, the endpoint decision, and the empty-but-defined campaign ledger schema. No conversion scores, no revenue forecasts.", "section"),
    "dashboard/index.html": ("dashboard/index", "Working dashboard — ShopNow Kitchen Edit",
        "The maintainer's hub: event queue viewer and export, the Associates link pre-check tool, and pointers into every register.", "section"),
    "suggestions/index.html": ("suggestions/index", "Suggestion review board — ShopNow Kitchen Edit",
        "Suggestions reviewed before implementation: what each changes, the evidence, the options, impact/effort/risk, and the decision needed. Choose the best path here first.", "section"),
    "questions/index.html": ("questions/index", "Decision readiness — questions before decisions — ShopNow Kitchen Edit",
        "The clear list of questions that must be answered before decisions can reasonably be made: what we know from official sources, what's missing, and how to discover it.", "section"),
    "about/index.html": ("about/index", "About & editorial standards — ShopNow Kitchen Edit",
        "Who writes this site, what we will and won't publish, the imagery policy, and how reader support works.", "section"),
    "search-console/index.html": ("search-console/index", "Search Console readiness — ShopNow Kitchen Edit",
        "The exact steps to verify the site in Google Search Console and submit the sitemap, with the meta-tag placeholder already in place.", "section"),
    "404.html": ("404", "Page not found — ShopNow Kitchen Edit",
        "That page doesn't exist. The shop front and every dashboard surface are one click away.", "misc"),
}

NAV = [
    ("Guides", "guides/index.html"),
    ("Shop the picks", "products/index.html"),
    ("How we research", "sourcing/index.html"),
    ("About", "about/index.html"),
]

DASHBOARD_LINKS = [
    ("Executive summary", "summary/index.html"),
    ("Suggestion review board", "suggestions/index.html"),
    ("Decision-readiness questions", "questions/index.html"),
    ("Flagged for review", "flagged/index.html"),
    ("Findings & analysis", "analysis/index.html"),
    ("Analytics & campaign ledger", "analytics/index.html"),
    ("Working dashboard", "dashboard/index.html"),
    ("Compliance gate", "compliance/index.html"),
    ("Source register", "sourcing/index.html"),
    ("Search Console setup", "search-console/index.html"),
    ("RSS feed", "feed.xml"),
]

DISCLOSURE_TEMPLATE = (
    '<div class="disclosure" data-disclosure-strip><div class="wrap">'
    '<span><strong>Reader-supported:</strong> I get commissions for purchases made through links in this post. '
    '<em>As an Amazon Associate I earn from qualifying purchases.</em> '
    'Every pick carries its sourcing — see <a href="{p}sourcing/index.html">how we research</a> and our '
    '<a href="{p}compliance/index.html">compliance gate</a>.</span>'
    '</div></div>'
)


def rel_prefix(out_path):
    depth = out_path.count("/")
    return "../" * depth


def layout(out_path, title, desc, body, jsonld_blocks=()):
    p = rel_prefix(out_path)
    canonical = BASE if out_path == "index.html" else BASE + out_path
    links = "\n".join(
        '<li><a href="%s%s">%s</a></li>' % (p, href, label) for label, href in DASHBOARD_LINKS
    )
    nav_links = "\n".join(
        '<a href="%s%s">%s</a>' % (p, href, label) for label, href in NAV
    )
    ld = "\n".join('<script type="application/ld+json">%s</script>' % json.dumps(b, indent=1) for b in jsonld_blocks)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
<meta property="og:site_name" content="ShopNow Kitchen Edit">
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{BASE}assets/img/og-default.jpg">
<meta name="twitter:card" content="summary_large_image">
<!-- Google Search Console HTML-tag verification: paste the generated meta tag on the next line (see search-console/index.html) -->
<link rel="icon" type="image/svg+xml" href="{p}assets/img/favicon.svg">
<link rel="alternate" type="application/rss+xml" title="ShopNow Kitchen Edit — Guides" href="{p}feed.xml">
<link rel="stylesheet" href="{p}assets/css/site.css">
<script src="{p}assets/js/site-config.js" defer></script>
<script src="{p}assets/js/analytics.js" defer></script>
<script src="{p}assets/js/site.js" defer></script>
{ld}
</head>
<body>
<header class="masthead">
  <div class="wrap">
    <a class="brand" href="{p}index.html">
      <span class="mark" aria-hidden="true">S</span>
      <span class="name">ShopNow Kitchen Edit<span class="tagline">Air fryers &amp; kitchen gear — chosen with the boring questions asked first</span></span>
    </a>
    <nav class="nav" aria-label="Primary">{nav_links}
      <a class="cta" href="{p}products/index.html">Shop the picks</a>
    </nav>
  </div>
</header>
{DISCLOSURE_TEMPLATE.format(p=p)}
<main>
{body}
</main>
<footer class="site">
  <div class="wrap cols">
    <div>
      <div class="brand-line">ShopNow Kitchen Edit</div>
      <p>A small, reader-supported publication about air fryers, multi-function ovens and the
      tools that keep them honest. We publish what we can source, leave blank what we can't,
      and review every suggestion before it changes the site.</p>
      <p class="note">All site imagery is AI-generated illustration, not product photography.</p>
    </div>
    <div>
      <h4>Read &amp; shop</h4>
      <ul>
        <li><a href="{p}products/index.html">Shop the picks</a></li>
        <li><a href="{p}guides/index.html">Buying guides</a></li>
        <li><a href="{p}guides/basket-or-oven-air-fryer.html">Basket vs oven-style</a></li>
        <li><a href="{p}guides/air-fryer-capacity-checklist.html">Capacity checklist</a></li>
        <li><a href="{p}about/index.html">About &amp; standards</a></li>
      </ul>
    </div>
    <div>
      <h4>Project dashboard</h4>
      <ul>
{links}
      </ul>
    </div>
    <div>
      <h4>Canonical register</h4>
      <p>The root publication is this site's register and compliance home:
      <a href="{p}../index.html">Affil3 root publication</a> ·
      <a href="{p}../flagged/index.html">root Flagged-for-Review</a> ·
      <a href="{p}../sources/index.html">root source register</a>.
      Outbound destinations and tracking status for every product are governed by the
      canonical register there (<code>data/products.json</code>).</p>
    </div>
    <div>
      <h4>Stay in the loop</h4>
      <p>New guides land in the <a href="{p}feed.xml">RSS feed</a> first. Prefer email?
      The capture form below records interest locally until the newsletter decision lands.</p>
      <form data-capture="footer">
        <input type="email" placeholder="you@example.com" aria-label="Email for future newsletter" required>
        <button class="btn btn-primary" type="submit">Keep me posted</button>
      </form>
    </div>
  </div>
  <div class="legal">
    <div class="wrap">
      <span class="assoc-statement">As an Amazon Associate we earn from qualifying purchases.</span>
      <span>Product CTAs are marked <code>rel="sponsored"</code> and open Amazon in a new tab.
      Listing identities and prices are shown only when confirmed; otherwise the record says so.
      © 2026 ShopNow Kitchen Edit. Editorial content — not sponsored by any manufacturer.</span>
    </div>
  </div>
</footer>
</body>
</html>
"""


def jsonld_for(out_path, title, desc, kind):
    org = {
        "@type": "Organization",
        "name": "ShopNow Kitchen Edit",
        "url": BASE,
        "logo": {"@type": "ImageObject", "url": BASE + "assets/img/favicon.svg"},
    }
    blocks = []
    if kind == "home":
        blocks.append({
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": "ShopNow Kitchen Edit",
            "url": BASE,
            "description": desc,
            "publisher": org,
        })
        blocks.append({"@context": "https://schema.org", "@type": "Organization", **org})
    elif kind == "guide":
        blocks.append({
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": title.split(" — ShopNow")[0],
            "description": desc,
            "datePublished": "2026-11-20",
            "dateModified": "2026-11-20",
            "author": {"@type": "Organization", "name": "ShopNow Kitchen Edit Editorial Team"},
            "publisher": org,
            "mainEntityOfPage": {"@type": "WebPage", "@id": BASE + out_path},
        })
    if out_path != "index.html":
        blocks.append({
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": BASE},
                {"@type": "ListItem", "position": 2, "name": title.split(" — ShopNow")[0][:120], "item": BASE + out_path},
            ],
        })
    return blocks


def build(outdir):
    frag_root = os.path.join(ROOT, "src")
    for out_path, (frag_key, title, desc, kind) in PAGES.items():
        frag_path = os.path.join(frag_root, frag_key + ".html")
        if not os.path.exists(frag_path):
            raise SystemExit("missing fragment: %s" % frag_path)
        with open(frag_path, encoding="utf-8") as fh:
            body = fh.read()
        dest = os.path.join(outdir, out_path)
        os.makedirs(os.path.dirname(dest) or outdir, exist_ok=True)
        with open(dest, "w", encoding="utf-8") as fh:
            fh.write(layout(out_path, title, desc, body, jsonld_for(out_path, title, desc, kind)))
    # static extras copied from assets-static dir if present (none currently)


def main():
    if "--check" in sys.argv:
        tmp = tempfile.mkdtemp()
        build(tmp)
        diffs = []
        for out_path in PAGES:
            new = os.path.join(tmp, out_path)
            old = os.path.join(ROOT, out_path)
            with open(new, encoding="utf-8") as fh:
                new_txt = fh.read()
            old_txt = open(old, encoding="utf-8").read() if os.path.exists(old) else None
            if old_txt != new_txt:
                diffs.append(out_path)
        shutil.rmtree(tmp)
        if diffs:
            print("STALE PAGES (regenerate with: python3 tools/build_pages.py):")
            for d in diffs:
                print("  -", d)
            sys.exit(1)
        print("pages fresh: %d checked" % len(PAGES))
        return
    build(ROOT)
    print("built %d pages" % len(PAGES))


if __name__ == "__main__":
    main()
