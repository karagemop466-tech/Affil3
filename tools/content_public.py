#!/usr/bin/env python3
"""The Crisp Index — reader-facing pages (shop/publication surface).

Every outbound product link is rel="sponsored nofollow noopener" with a visible
Sponsored chip. Every checkable fact carries a source link; unconfirmed values
are blank and flagged. Prose is deliberately question-shaped and hype-free.
"""
from build_core import esc

ARTICLE_DATE = "November 20, 2026"
AUTHOR = "The Crisp Index Editorial Desk"


# --------------------------------------------------------------------------
# shared partials
# --------------------------------------------------------------------------

def product_card(ctx, p, note=None):
    obs = p["observed"]
    if obs["status"] == "resolved":
        name = p["display_name"]
        kicker = esc(p["category_note"].replace(" (observed breadcrumb)", ""))
        title_line = (
            f'<p class="fine">Verbatim listing title: “{esc(obs["listing_title_verbatim"])}” '
            f'{ctx.src(p["sources"][0])}</p>'
        )
        state = f'{ctx.chip("Listing observed " + obs["date"], "chip-ok")}'
    else:
        name = "Submitted link 4 — identity pending your confirmation"
        kicker = "Verification in progress"
        title_line = (
            f'<p class="fine">Our own fetches of this link returned an Amazon checkpoint page on '
            f'{esc(obs["date"])} {ctx.src(p["sources"][0])}. A separate dated retest later resolved it '
            f'to a ThermoMaven instant-read meat thermometer {ctx.src("S-15", "cross-session retest")} — '
            f'recorded as corroboration, not merged into our observation. Nothing about the intended '
            f'product is assumed.</p>'
        )
        state = f'{ctx.chip("Destination resolved elsewhere", "chip-flag")}'
    chips = "".join(ctx.chip(c) for c in p["listing_claims_verbatim"][:5])
    img_html = ""
    if p.get("card_image"):
        img_html = (
            f'<img class="card-img" src="{esc(ctx.rel(p["card_image"]))}" '
            f'alt="{esc(p["card_image_alt"])}" loading="lazy">'
        )
    else:
        img_html = (
            '<div class="card-img" style="background:var(--amber-bg);display:flex;align-items:center;'
            'justify-content:center"><span class="chip chip-flag">Image pending identity check</span></div>'
        )
    foot_note = note or (
        "Price varies — we don’t cache prices. Outbound link marked Sponsored; "
        "it may earn us a commission."
    )
    return f"""<article class="card product-card">
  {img_html}
  <div class="card-body">
    <span class="card-kicker">{kicker}</span>
    <h3>{esc(name)}</h3>
    {title_line}
    <div class="chip-row">{chips} {state}</div>
    <div class="card-foot">
      {ctx.sponsored_cta(p)}
      <p class="price-note">{foot_note}</p>
    </div>
  </div>
</article>"""


def guide_card(ctx, path, img, kicker, title, desc):
    return f"""<article class="card">
  <img class="card-img" src="{esc(ctx.rel(img))}" alt="" loading="lazy">
  <div class="card-body">
    <span class="card-kicker">{esc(kicker)}</span>
    <h3><a href="{esc(ctx.rel(path))}">{esc(title)}</a></h3>
    <p>{esc(desc)}</p>
    <div class="card-foot"><a class="btn btn-ghost" href="{esc(ctx.rel(path))}">Read the guide</a></div>
  </div>
</article>"""


def capture_band(ctx, headline, blurb):
    return f"""<section class="section"><div class="wrap">
  <div class="band">
    <div>
      <p class="eyebrow" style="color:#e8b08e">The Counter Note</p>
      <h2>{esc(headline)}</h2>
      <p>{esc(blurb)}</p>
    </div>
    <div>
      <form class="capture-form" novalidate>
        <input type="email" name="email" placeholder="you@example.com" aria-label="Email address" required>
        <button class="btn" type="submit">Keep me posted</button>
      </form>
      <p class="capture-note">One short dispatch per issue. No spam, no list sharing. Reader
      capture opens with our first issue — status is tracked in the Suggestions queue.</p>
    </div>
  </div>
</div></section>"""


def article_meta_row(ctx, cluster_label, read_time, extra=""):
    return (
        f'<div class="article-meta"><span>By {esc(AUTHOR)}</span>'
        f"<span>{esc(ARTICLE_DATE)}</span>"
        f"<span>{esc(read_time)}</span>"
        f"<span>Cluster: {esc(cluster_label)}</span>{extra}</div>"
    )


def related_row(ctx, links):
    items = "".join(
        f'<li><a href="{esc(ctx.rel(path))}">{esc(label)}</a></li>' for label, path in links
    )
    return (
        f'<div class="callout"><h3>Keep reading</h3><ul>{items}</ul></div>'
    )


def article_jsonld(path, headline, description, image):
    return {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": headline,
        "description": description,
        "author": {"@type": "Organization", "name": AUTHOR},
        "publisher": {"@type": "Organization", "name": "The Crisp Index"},
        "datePublished": "2026-11-20",
        "image": "https://karagemop466-tech.github.io/Affil3/" + image,
        "mainEntityOfPage": "https://karagemop466-tech.github.io/Affil3/" + path,
    }


def breadcrumb_jsonld(items):
    out = []
    for i, (name, path) in enumerate(items, start=1):
        out.append(
            {
                "@type": "ListItem",
                "position": i,
                "name": name,
                "item": "https://karagemop466-tech.github.io/Affil3/" + path,
            }
        )
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": out}


# --------------------------------------------------------------------------
# pages
# --------------------------------------------------------------------------

def pages(ctx):
    return [
        front_page(ctx),
        guides_hub(ctx),
        guide_basket_or_oven(ctx),
        guide_capacity(ctx),
        guide_cleanup(ctx),
        guide_multifunction(ctx),
        guide_holiday(ctx),
        compare_page(ctx),
        products_page(ctx),
        about_page(ctx),
        disclosure_page(ctx),
    ]


def front_page(ctx):
    ps = ctx.d["products"]["products"]
    body = f"""
<section class="hero"><div class="wrap hero-grid">
  <div>
    <p class="eyebrow">Countertop kitchen · Buyer’s guides</p>
    <h1>Buy the air fryer you’ll actually keep.</h1>
    <p class="lede">Question-first buying guides for air fryers, countertop ovens, and the gadgets
    between. We compare the trade-offs that decide a purchase — capacity you can use, cleanup you’ll
    live with, counter space you don’t have. No hype, no invented test labs.</p>
    <div class="hero-actions">
      <a class="btn" href="{esc(ctx.rel('guides/index.html'))}">Read the buyer’s guides</a>
      <a class="btn btn-ghost" href="{esc(ctx.rel('products/index.html'))}">See the test queue</a>
    </div>
    <p class="hero-note">{ctx.chip('Disclosure', 'chip-sponsored')} Every product link on this site is
    marked <strong>Sponsored</strong> and may earn us a commission from qualifying purchases — the
    price you pay never changes.</p>
  </div>
  <div>
    <img class="hero-img" src="{esc(ctx.rel('assets/img/hero-countertop.jpg'))}"
      alt="A basket-style air fryer, a French-door countertop oven, and a wireless probe thermometer on a sunlit kitchen counter (original illustration)">
  </div>
</div></section>

<section class="section section-alt"><div class="wrap">
  <div class="section-head">
    <div>
      <p class="eyebrow">Season · November–December 2026</p>
      <h2>Holiday hosting, countertop edition</h2>
      <p>When the main oven is spoken for, the appliances that earn counter space are the ones that
      solve a specific hosting problem. Here’s how to plan for it.</p>
    </div>
    <a class="btn btn-ghost" href="{esc(ctx.rel('guides/holiday-hosting-countertop.html'))}">Open the seasonal guide</a>
  </div>
</div></section>

<section class="section"><div class="wrap">
  <div class="section-head">
    <div>
      <p class="eyebrow">Start here</p>
      <h2>Buyer’s guides built around real questions</h2>
      <p>Each guide is a decision tool: what to compare, what to ignore, and which questions to take
      to any listing.</p>
    </div>
    <a class="btn btn-ghost" href="{esc(ctx.rel('guides/index.html'))}">All guides</a>
  </div>
  <div class="card-grid">
    {guide_card(ctx, 'guides/basket-or-oven-style-air-fryer.html', 'assets/img/guide-basket-vs-oven.jpg',
                'Compare · 7 min', 'Basket or oven-style air fryer: what should you compare?',
                'Two shapes, two sets of trade-offs. Start from what you actually cook, not from the box art.')}
    {guide_card(ctx, 'guides/air-fryer-capacity-checklist.html', 'assets/img/guide-capacity.jpg',
                'Checklist · 6 min', 'A no-hype checklist for comparing air fryer capacity',
                'Quarts are volume, not servings. What to measure instead — and the questions that matter.')}
    {guide_card(ctx, 'guides/cleanup-and-counter-space.html', 'assets/img/guide-cleanup.jpg',
                'Living with it · 6 min', 'How to assess cleanup and counter-space trade-offs',
                'The two costs no product photo shows: the daily wipe-down and the permanent footprint.')}
    {guide_card(ctx, 'guides/questions-multifunction-appliance.html', 'assets/img/guide-multifunction.jpg',
                'Questions · 7 min', 'Questions to ask before buying a multi-function kitchen appliance',
                '“Multi-function” is a listing word. Here’s how to find out what you’re really getting.')}
  </div>
</div></section>

<section class="section section-alt"><div class="wrap">
  <div class="section-head">
    <div>
      <p class="eyebrow">The Test Queue</p>
      <h2>What’s on the bench right now</h2>
      <p>Five submitted links, checked one by one. Where a listing was observed, we quote it verbatim
      and link the source; where it wasn’t, we say so.</p>
    </div>
    <a class="btn btn-ghost" href="{esc(ctx.rel('products/index.html'))}">Full queue &amp; source notes</a>
  </div>
  <div class="card-grid">
    {product_card(ctx, ps[0])}
    {product_card(ctx, ps[1])}
    {product_card(ctx, ps[2])}
  </div>
</div></section>

<section class="section"><div class="wrap">
  <div class="section-head"><div>
    <p class="eyebrow">How this works</p>
    <h2>Published like a magazine, sourced like a register</h2>
  </div></div>
  <div class="card-grid">
    <article class="card"><div class="card-body">
      <span class="card-kicker">Step 1</span>
      <h3>We verify the listing first</h3>
      <p>Every product starts as a submitted link. We record what it says it is — and what it
      actually resolves to — in two separate fields, then publish both.</p>
      <div class="card-foot"><a class="btn btn-ghost" href="{esc(ctx.rel('workshop/register.html'))}">See the register</a></div>
    </div></article>
    <article class="card"><div class="card-body">
      <span class="card-kicker">Step 2</span>
      <h3>We compare trade-offs, not hype</h3>
      <p>Guides are written as questions and checklists you can take shopping. When we can’t confirm
      a value from an official source, it stays blank and flagged.</p>
      <div class="card-foot"><a class="btn btn-ghost" href="{esc(ctx.rel('about/index.html'))}">Our methodology</a></div>
    </div></article>
    <article class="card"><div class="card-body">
      <span class="card-kicker">Step 3</span>
      <h3>You decide with a checklist</h3>
      <p>Each guide ends with the questions to ask before spending money. The goal is the right
      purchase for your kitchen — not the biggest one.</p>
      <div class="card-foot"><a class="btn btn-ghost" href="{esc(ctx.rel('compare/index.html'))}">Open the compare hub</a></div>
    </div></article>
  </div>
</div></section>

{capture_band(ctx, 'Get the next guide before your next purchase',
             'A short note when we publish a new buyer’s guide or seasonal checklist. That’s the whole deal.')}
"""
    return {
        "path": "index.html",
        "title": "Buyer’s guides for air fryers & countertop kitchens",
        "description": "Question-first buying guides for air fryers, countertop ovens, and kitchen gadgets. Verified sources, honest trade-offs, every affiliate link disclosed.",
        "section": "home",
        "og_image": "assets/img/hero-countertop.jpg",
        "jsonld": [
            {
                "@context": "https://schema.org",
                "@type": "WebSite",
                "name": ctx.site["brand"],
                "url": ctx.site["base_url"],
                "description": ctx.site["mission"],
                "publisher": {"@type": "Organization", "name": ctx.site["brand"]},
            },
            {
                "@context": "https://schema.org",
                "@type": "Organization",
                "name": ctx.site["brand"],
                "url": ctx.site["base_url"],
                "description": ctx.site["mission"],
            },
        ],
        "body": body,
        "sitemap": {"priority": "1.0", "changefreq": "weekly"},
    }


def guides_hub(ctx):
    body = f"""
<div class="wrap article-header">
  <p class="eyebrow">Buyer’s guides</p>
  <h1>Every guide starts with a question a real buyer asks</h1>
  <p class="lede">Organized in three clusters: choosing a shape, living with the machine, and buying
  well in season. Start anywhere — each guide stands alone and points to the next decision.</p>
</div>
<section class="section"><div class="wrap">
  <h2>Cluster 1 · Choosing the shape</h2>
  <div class="card-grid two">
    {guide_card(ctx, 'guides/basket-or-oven-style-air-fryer.html', 'assets/img/guide-basket-vs-oven.jpg',
                'Compare · 7 min', 'Basket or oven-style air fryer: what should you compare?',
                'The first fork in the road: shape. It decides capacity, cleanup, and what you can cook without thinking.')}
    {guide_card(ctx, 'guides/air-fryer-capacity-checklist.html', 'assets/img/guide-capacity.jpg',
                'Checklist · 6 min', 'A no-hype checklist for comparing air fryer capacity',
                'Capacity figures are the most quoted and least understood number on the listing.')}
  </div>
  <h2 style="margin-top:2em">Cluster 2 · Living with it</h2>
  <div class="card-grid two">
    {guide_card(ctx, 'guides/cleanup-and-counter-space.html', 'assets/img/guide-cleanup.jpg',
                'Living with it · 6 min', 'How to assess cleanup and counter-space trade-offs',
                'The long-term costs of ownership, assessed before you buy instead of after.')}
    {guide_card(ctx, 'guides/questions-multifunction-appliance.html', 'assets/img/guide-multifunction.jpg',
                'Questions · 7 min', 'Questions to ask before buying a multi-function kitchen appliance',
                'When one machine claims six jobs, the right questions separate overlap from real value.')}
  </div>
  <h2 style="margin-top:2em">Cluster 3 · Buying in season</h2>
  <div class="card-grid two">
    {guide_card(ctx, 'guides/holiday-hosting-countertop.html', 'assets/img/season-holiday.jpg',
                'Seasonal · 7 min', 'Holiday hosting on a countertop: what actually earns its place',
                'A hosting-season plan for kitchens whose main oven is already booked.')}
  </div>
</div></section>
{capture_band(ctx, 'Never miss a guide', 'New checklists and seasonal guides, straight to your inbox when they publish.')}
"""
    return {
        "path": "guides/index.html",
        "title": "Buyer’s guides",
        "description": "Question-shaped buyer’s guides for air fryers, countertop ovens, and multi-function kitchen appliances — with checklists you can take shopping.",
        "section": "guides",
        "breadcrumb": [("Buyer’s guides", "guides/index.html")],
        "jsonld": [breadcrumb_jsonld([("Home", "index.html"), ("Buyer’s guides", "guides/index.html")])],
        "body": body,
        "sitemap": {"priority": "0.9", "changefreq": "weekly"},
        "feed": {
            "title": "Buyer’s guides — all of them",
            "description": "The full cluster of question-shaped buying guides.",
            "category": "Guides",
        },
    }


def guide_basket_or_oven(ctx):
    path = "guides/basket-or-oven-style-air-fryer.html"
    ps = ctx.d["products"]["products"]
    body = f"""
<div class="wrap article-header article">
  <p class="eyebrow">Compare · Choosing the shape</p>
  <h1>Basket or oven-style air fryer: what should you compare?</h1>
  {article_meta_row(ctx, 'Choosing the shape', '7 min read')}
</div>
<div class="wrap article">
  <img class="article-hero-img" src="{esc(ctx.rel('assets/img/guide-basket-vs-oven.jpg'))}"
    alt="A basket-style air fryer and a French-door countertop oven side by side on a kitchen counter (original illustration)">
  <p class="lede">This is the first fork in the road, and it’s worth slowing down for. Basket-style and
  oven-style machines both move hot air fast — but they disagree about almost everything else:
  footprint, capacity shape, how you interact with food mid-cook, and what cleanup looks like on a
  Tuesday night.</p>

  <h2>Start with what you actually cook</h2>
  <p>Before any spec comparison, answer honestly:</p>
  <ul>
    <li>Is dinner usually <strong>one thing</strong> (fries, wings, a sheet of vegetables) or
    <strong>a plate</strong> (protein + two sides)?</li>
    <li>Do you cook from frozen on weeknights, or mostly reheat and roast?</li>
    <li>How often do you want to <strong>check or shake</strong> food while it cooks — and how often
    will you actually do it?</li>
    <li>Is this machine a <strong>second oven</strong> (holiday overflow, summer heat relief) or the
    main event?</li>
  </ul>
  <p>Those four answers usually decide the shape. The specs just confirm it.</p>

  <h2>The trade-offs, side by side</h2>
  <div class="table-scroll"><table class="data">
    <thead><tr><th>What to compare</th><th>Basket style</th><th>Oven style</th></tr></thead>
    <tbody>
      <tr><td><strong>Capacity shape</strong></td>
        <td>Deep and compact; great for tumbling foods, awkward for flat batches</td>
        <td>Wide and shallow; racks give you layers and flat surface area</td></tr>
      <tr><td><strong>Mid-cook interaction</strong></td>
        <td>Shake the basket — fast, but you open the whole chamber</td>
        <td>Peek through the door or slide a rack out; less heat loss per check</td></tr>
      <tr><td><strong>Footprint</strong></td>
        <td>Smaller counter claim, usually no door swing to plan for</td>
        <td>Taller and deeper; door clearance and front loading space matter</td></tr>
      <tr><td><strong>Cleanup</strong></td>
        <td>One basket (or two) plus a crumb tray; typically fewer parts</td>
        <td>Racks, trays, sometimes a spit — more surface area to wash</td></tr>
      <tr><td><strong>Learning curve</strong></td>
        <td>Low: dial or presets, set and shake</td>
        <td>Higher: rack positions, tray choices, more functions to learn</td></tr>
      <tr><td><strong>Best at</strong></td>
        <td>Crisp, tossable food; fast preheat; small households</td>
        <td>Batch and layered cooking; pizza, toast, bake, rotisserie-style jobs</td></tr>
    </tbody>
  </table></div>
  <p class="fine">Comparison framework — not a test result. We publish measured performance claims
  only when a documented hands-on method exists (see <a href="{esc(ctx.rel('about/index.html'))}">methodology</a>).</p>

  <h2>What each shape is quietly bad at</h2>
  <p>Honest lists are the useful ones:</p>
  <ul>
    <li><strong>Basket machines</strong> punish flat foods — anything that wants a single layer gets
    crowded fast, and crowding is the enemy of crisp. Two-basket models help, but they split one
    machine’s heat and attention.</li>
    <li><strong>Oven-style machines</strong> ask for more of your kitchen: counter depth, door swing,
    and a place for the accessories. They also heat a bigger box — useful for batches, wasteful for
    two chicken cutlets.</li>
  </ul>

  <h2>Questions to take to any listing</h2>
  <ul class="checklist">
    <li>What fits <em>in one layer</em> at the capacity they advertise? Ask what the usable area is, not just the volume.</li>
    <li>Which parts go in the dishwasher — basket only, or racks and trays too? (Observed listings on our queue say “Dishwasher Safe Frying Baskets” and similar — treat it as a claim to check part by part.)</li>
    <li>What is the footprint <em>with the door open</em>, or with both baskets out?</li>
    <li>How loud is the fan at the setting you’ll use nightly? Listing pages rarely say; owner questions and reviews do.</li>
    <li>What happens after the warranty year? Parts availability is a real ownership question.</li>
  </ul>

  <h2>Where the queue stands today</h2>
  <p>Two basket-style machines and one French-door oven-style model are on
  <a href="{esc(ctx.rel('products/index.html'))}">our test queue</a> right now, with their observed
  listings quoted verbatim: {ctx.sponsored_cta(ps[0], 'See the 6-quart dual basket on Amazon')} and
  {ctx.sponsored_cta(ps[1], 'See the 26QT French door on Amazon')}. Both links are sponsored and each
  earns us a commission from qualifying purchases.</p>

  {related_row(ctx, [
      ('A no-hype checklist for comparing air fryer capacity', 'guides/air-fryer-capacity-checklist.html'),
      ('How to assess cleanup and counter-space trade-offs', 'guides/cleanup-and-counter-space.html'),
      ('The compare hub: build your shortlist', 'compare/index.html'),
  ])}
</div>
"""
    return {
        "path": path,
        "title": "Basket or oven-style air fryer: what should you compare?",
        "description": "A decision guide to basket-style vs oven-style air fryers: capacity shape, cleanup, counter space, and the questions to take to any listing.",
        "section": "guides",
        "og_image": "assets/img/guide-basket-vs-oven.jpg",
        "og_type": "article",
        "breadcrumb": [("Buyer’s guides", "guides/index.html"), ("Basket or oven-style", None)],
        "jsonld": [
            article_jsonld(path, "Basket or oven-style air fryer: what should you compare?",
                           "Decision guide to basket vs oven-style air fryers.", "assets/img/guide-basket-vs-oven.jpg"),
            breadcrumb_jsonld([("Home", "index.html"), ("Buyer’s guides", "guides/index.html"), ("Basket or oven-style air fryer", path)]),
        ],
        "body": body,
        "sitemap": {"priority": "0.8", "changefreq": "monthly"},
        "feed": {
            "title": "Basket or oven-style air fryer: what should you compare?",
            "description": "Two shapes, two sets of trade-offs — start from what you actually cook.",
            "category": "Compare",
        },
    }


def guide_capacity(ctx):
    path = "guides/air-fryer-capacity-checklist.html"
    body = f"""
<div class="wrap article-header article">
  <p class="eyebrow">Checklist · Choosing the shape</p>
  <h1>A no-hype checklist for comparing air fryer capacity</h1>
  {article_meta_row(ctx, 'Choosing the shape', '6 min read')}
</div>
<div class="wrap article">
  <img class="article-hero-img" src="{esc(ctx.rel('assets/img/guide-capacity.jpg'))}"
    alt="An air fryer basket viewed from above with food spaced for airflow (original illustration)">
  <p class="lede">Capacity is the most quoted number on any air fryer listing — and the least
  understood. “8 quarts” is a volume. It is not a serving count, not a batch guarantee, and not a
  promise about how much food will actually crisp. Here’s how to compare capacity without falling
  for the number.</p>

  <h2>What a capacity figure does tell you</h2>
  <p>It’s a rough sense of how much air the chamber holds. Two machines with the same figure can cook
  very differently depending on shape (deep basket vs wide rack), how the heat moves, and how much
  clearance the manufacturer demands around the food.</p>

  <h2>What it doesn’t</h2>
  <ul>
    <li><strong>It isn’t servings.</strong> Family-size claims on listings are marketing language; the
    number behind them isn’t standardized.</li>
    <li><strong>It isn’t usable area.</strong> Air needs to move around food. A crowded basket steams;
    it doesn’t crisp. Whatever the volume says, the food has to fit in one layer (or a thin one) to
    cook the way you’re imagining.</li>
    <li><strong>It isn’t shared.</strong> On dual-basket machines, the headline figure is often the sum
    of two smaller baskets — each of which cooks independently.</li>
    <li><strong>It isn’t counter space.</strong> Big capacity has a footprint, a height (check cabinet
    clearance), and sometimes a door swing.</li>
  </ul>

  <h2>The checklist</h2>
  <ul class="checklist">
    <li><strong>Measure your counter</strong> — width, depth, and the vertical gap to any cabinet above. Tape it out before you shop.</li>
    <li><strong>List your top five meals</strong> for this machine. Write down the largest single item (a whole small chicken? a 12-inch frozen pizza? two layers of fries?).</li>
    <li><strong>Match shape to meal</strong>: tumbling food → basket; flat and layered → racks.</li>
    <li><strong>Decide single vs dual zone</strong> — two baskets let you finish two foods together (look for a finish-together feature on the listing), but each zone is smaller.</li>
    <li><strong>Ask what fits in one layer</strong> at the advertised capacity. If the listing can’t answer, assume the real number is smaller.</li>
    <li><strong>Check the accessories in the box</strong> — racks and trays change what fits; splitters can double layers or halve your usable space.</li>
    <li><strong>Plan for the gap factor</strong>: budget for less than the headline capacity every time. If dinner is one item for two people, a smaller machine with usable space beats a big one that’s always crowded.</li>
  </ul>

  <h2>How this shows up on real listings</h2>
  <p>On <a href="{esc(ctx.rel('products/index.html'))}">our test queue</a>, capacity language ranges
  from “6 Quart” with two “3Qt” baskets, to “8 Qt XL”, to a “26QT” French-door oven — three
  different numbers answering three different questions. That’s exactly why the shape question comes
  <a href="{esc(ctx.rel('guides/basket-or-oven-style-air-fryer.html'))}">first</a>. Listing wording is
  quoted verbatim in the register with its source link; none of it is independently tested yet, and
  we say so.</p>

  <h2>Skip the purchase if…</h2>
  <ul>
    <li>…you can’t name the largest thing you’d realistically cook in it.</li>
    <li>…it only fits your counter with the door or baskets permanently open.</li>
    <li>…the listing answers capacity with adjectives (“family size”, “XL”) instead of measurements.</li>
  </ul>

  {related_row(ctx, [
      ('Basket or oven-style: what should you compare?', 'guides/basket-or-oven-style-air-fryer.html'),
      ('Cleanup and counter-space trade-offs', 'guides/cleanup-and-counter-space.html'),
      ('Holiday hosting on a countertop', 'guides/holiday-hosting-countertop.html'),
  ])}
</div>
"""
    return {
        "path": path,
        "title": "A no-hype checklist for comparing air fryer capacity",
        "description": "Quarts are volume, not servings. A practical checklist for comparing air fryer capacity honestly — plus the questions to ask before you buy.",
        "section": "guides",
        "og_image": "assets/img/guide-capacity.jpg",
        "og_type": "article",
        "breadcrumb": [("Buyer’s guides", "guides/index.html"), ("Capacity checklist", None)],
        "jsonld": [
            article_jsonld(path, "A no-hype checklist for comparing air fryer capacity",
                           "A practical checklist for comparing air fryer capacity honestly.", "assets/img/guide-capacity.jpg"),
            breadcrumb_jsonld([("Home", "index.html"), ("Buyer’s guides", "guides/index.html"), ("Air fryer capacity checklist", path)]),
        ],
        "body": body,
        "sitemap": {"priority": "0.8", "changefreq": "monthly"},
        "feed": {
            "title": "A no-hype checklist for comparing air fryer capacity",
            "description": "Quarts are volume, not servings — what to measure instead.",
            "category": "Checklists",
        },
    }


def guide_cleanup(ctx):
    path = "guides/cleanup-and-counter-space.html"
    body = f"""
<div class="wrap article-header article">
  <p class="eyebrow">Living with it · Ownership costs</p>
  <h1>How to assess cleanup and counter-space trade-offs</h1>
  {article_meta_row(ctx, 'Living with it', '6 min read')}
</div>
<div class="wrap article">
  <img class="article-hero-img" src="{esc(ctx.rel('assets/img/guide-cleanup.jpg'))}"
    alt="An air fryer basket and crisping tray on a dishwasher rack (original illustration)">
  <p class="lede">Nobody returns an air fryer because the fries were bad. They return it because it
  was a nuisance to clean, or because it ate the counter. Both costs are knowable before you buy —
  if you go looking for them.</p>

  <h2>Cost one: the cleanup you’ll actually do</h2>
  <p>Separate the daily job from the weekly one:</p>
  <ul>
    <li><strong>Daily:</strong> the basket, tray, or rack that touches food. If that part isn’t easy —
    awkward shape, coating you’re afraid to scrub — the machine loses.</li>
    <li><strong>Weekly or so:</strong> heating elements, crumb trays, doors and glass, the greasy
    corners you only notice on Sunday.</li>
    <li><strong>Seasonally:</strong> deep-clean the fan intake area and any splatter zones behind the
    tray. Cheaper machines make this impossible. Ask before you buy.</li>
  </ul>
  <h3>Read “dishwasher-safe” claims carefully</h3>
  <p>Observed listings on our queue advertise “Dishwasher-Safe Frying Baskets” — note it’s the
  <em>baskets</em> (quoted verbatim in the <a href="{esc(ctx.rel('workshop/register.html'))}">register</a>).
  Listing claims are manufacturer wording, not our test result. Three questions to ask:</p>
  <ul>
    <li>Which specific parts are dishwasher-safe — and on which rack?</li>
    <li>What does the manufacturer say about nonstick care and detergent? Coatings have a lifespan;
    the manual is the only source that matters.</li>
    <li>What happens to the finish after a year of dishwasher cycles? Owner Q&amp;A threads on the
    listing are the honest place to look.</li>
  </ul>

  <h2>Cost two: the footprint you’ll live with</h2>
  <h3>The tape test</h3>
  <ul class="checklist">
    <li>Tape the machine’s width and depth on the counter — many listings publish dimensions in the
    product information table at the bottom of the page.</li>
    <li>Add the <strong>door swing</strong> (oven-style) or <strong>basket pull-out</strong>
    (basket-style). If the tape zone overlaps the sink, stove, or your only prep space, it’s a no.</li>
    <li>Measure <strong>vertical clearance</strong> to the cabinet above — you need room to lift a
    basket or open a door, not just to fit the box.</li>
    <li>Check the <strong>heat clearance</strong> the manual demands on each side; machines that hug
    the wall need less space but live hotter.</li>
    <li>Open the cabinets: where do the racks, trays, and the second basket live when they’re not in
    the machine? Accessories without a home become clutter with a receipt.</li>
  </ul>

  <h2>Where the queue stands today</h2>
  <p>The queue currently holds one “Easy View Windows” dual-basket machine, one French-door
  “Multi-Function” oven, one “XL Nonstick Dishwasher-Safe Basket” air fryer, and a probe thermometer
  — all wording quoted from the observed listings with sources in the
  <a href="{esc(ctx.rel('products/index.html'))}">test queue</a>. Which parts survive your dishwasher
  is a question we ask before we recommend keeping any of them.</p>

  <h2>Skip the purchase if…</h2>
  <ul>
    <li>…the food-contact parts are “hand wash only” and you know yourself.</li>
    <li>…the machine fits on paper but not with the door open.</li>
    <li>…the accessories have no storage and you don’t have a drawer to spare.</li>
  </ul>

  {related_row(ctx, [
      ('A no-hype checklist for comparing air fryer capacity', 'guides/air-fryer-capacity-checklist.html'),
      ('Questions before buying a multi-function appliance', 'guides/questions-multifunction-appliance.html'),
      ('Holiday hosting on a countertop', 'guides/holiday-hosting-countertop.html'),
  ])}
</div>
"""
    return {
        "path": path,
        "title": "How to assess cleanup and counter-space trade-offs",
        "description": "The ownership costs no product photo shows: daily cleanup, dishwasher-safety claims, counter footprint, door swing, and accessory storage — assessed before you buy.",
        "section": "guides",
        "og_image": "assets/img/guide-cleanup.jpg",
        "og_type": "article",
        "breadcrumb": [("Buyer’s guides", "guides/index.html"), ("Cleanup & counter space", None)],
        "jsonld": [
            article_jsonld(path, "How to assess cleanup and counter-space trade-offs",
                           "Ownership costs assessed before you buy.", "assets/img/guide-cleanup.jpg"),
            breadcrumb_jsonld([("Home", "index.html"), ("Buyer’s guides", "guides/index.html"), ("Cleanup and counter space", path)]),
        ],
        "body": body,
        "sitemap": {"priority": "0.8", "changefreq": "monthly"},
        "feed": {
            "title": "How to assess cleanup and counter-space trade-offs",
            "description": "The two costs no product photo shows.",
            "category": "Ownership",
        },
    }


def guide_multifunction(ctx):
    path = "guides/questions-multifunction-appliance.html"
    body = f"""
<div class="wrap article-header article">
  <p class="eyebrow">Questions · Ownership costs</p>
  <h1>Questions to ask before buying a multi-function kitchen appliance</h1>
  {article_meta_row(ctx, 'Living with it', '7 min read')}
</div>
<div class="wrap article">
  <img class="article-hero-img" src="{esc(ctx.rel('assets/img/guide-multifunction.jpg'))}"
    alt="A multi-function countertop oven with racks, trays, an air-fry basket, and a rotisserie spit (original illustration)">
  <p class="lede">“Multi-Function.” “4-in-1.” “10-in-1.” Listing titles on our queue use all of
  these — we quote them verbatim in the register, with sources. They’re marketing words, not specs.
  The purchase question underneath is simple: <em>which of these functions will I actually use, and
  what do I give up for the rest?</em></p>

  <h2>Question 1: What does each function replace?</h2>
  <p>Make two columns: <strong>replaces</strong> and <strong>adds</strong>. A toaster oven that also
  air-fries replaces two appliances — that’s real value in a small kitchen. A sixth preset that
  performs one rarely-used setting adds nothing but button surface. If a function doesn’t replace
  something or unlock a meal you cook often, it isn’t a reason to buy.</p>

  <h2>Question 2: What’s in the box, and where does it live?</h2>
  <p>Multi-function usually means accessories: racks, trays, baskets, sometimes a rotisserie spit.
  Two observations from real listings we track: one “26QT French Door Multi-Function” model ships
  “Six Cooking Accessories Included”; one “TurboFry 4-in-1” lists air fry, bake, dehydrate, and
  frozen modes on the box (all verbatim, all sourced in the
  <a href="{esc(ctx.rel('workshop/register.html'))}">register</a>). Every included part is a part you
  store, wash, and eventually lose. Count the drawer space first.</p>

  <h2>Question 3: How many jobs can it really do at once?</h2>
  <p>Functions listed together are usually alternatives, not simultaneous. A machine that air-fries
  and bakes does one at a time unless it has independent zones. If your real need is “dinner and
  sides together,” look for dual-zone or finish-together features — and ask what each zone’s true
  usable size is (<a href="{esc(ctx.rel('guides/air-fryer-capacity-checklist.html'))}">capacity checklist</a>).</p>

  <h2>Question 4: Controls or presets?</h2>
  <ul>
    <li><strong>Presets</strong> lower the learning curve but lock in someone else’s time and
    temperature for foods that don’t exist in your kitchen.</li>
    <li><strong>Manual controls</strong> (time + temperature you set) age better and let you follow
    any recipe — including the ones on a bag of frozen fries.</li>
    <li>Ask whether presets can be overridden. Machines that force presets force guesswork.</li>
  </ul>

  <h2>Question 5: What’s the failure math?</h2>
  <p>One machine doing six jobs is one machine whose failure takes six jobs offline. Check the
  warranty length and, more importantly, <em>parts availability</em>: baskets, trays, and heating
  elements are the parts that wear. A brand’s replacement-parts store is a better predictor of
  ownership cost than any feature list.</p>

  <h2>Question 6: Does “multi-function” inflate the price of the one function you want?</h2>
  <p>Sometimes the single-purpose machine cooks better and costs less. The honest way to decide is
  the replace/adds list from Question 1: if the extras don’t earn their price, buy the simpler tool
  and spend the difference on a good <a href="{esc(ctx.rel('products/index.html'))}">probe
  thermometer</a> — the cheapest upgrade to any kitchen’s results.</p>

  <div class="callout"><h3>The five-minute version</h3>
  <ul>
    <li>Functions must replace something or unlock a meal you cook often.</li>
    <li>Count accessories as storage cost, not bonus value.</li>
    <li>Ask what runs simultaneously — and at what size.</li>
    <li>Prefer override-able controls over locked presets.</li>
    <li>Check warranty and replacement parts before the feature list wins you over.</li>
  </ul></div>

  {related_row(ctx, [
      ('Basket or oven-style air fryer: what should you compare?', 'guides/basket-or-oven-style-air-fryer.html'),
      ('Cleanup and counter-space trade-offs', 'guides/cleanup-and-counter-space.html'),
      ('The compare hub: build your shortlist', 'compare/index.html'),
  ])}
</div>
"""
    return {
        "path": path,
        "title": "Questions to ask before buying a multi-function kitchen appliance",
        "description": "Multi-function is a listing word, not a spec. The questions that separate real value from overlap before you buy a multi-function kitchen appliance.",
        "section": "guides",
        "og_image": "assets/img/guide-multifunction.jpg",
        "og_type": "article",
        "breadcrumb": [("Buyer’s guides", "guides/index.html"), ("Multi-function questions", None)],
        "jsonld": [
            article_jsonld(path, "Questions to ask before buying a multi-function kitchen appliance",
                           "The questions that separate real value from overlap.", "assets/img/guide-multifunction.jpg"),
            breadcrumb_jsonld([("Home", "index.html"), ("Buyer’s guides", "guides/index.html"), ("Multi-function appliance questions", path)]),
        ],
        "body": body,
        "sitemap": {"priority": "0.8", "changefreq": "monthly"},
        "feed": {
            "title": "Questions to ask before buying a multi-function kitchen appliance",
            "description": "“Multi-function” is a listing word — here are the questions that matter.",
            "category": "Questions",
        },
    }


def guide_holiday(ctx):
    path = "guides/holiday-hosting-countertop.html"
    ps = ctx.d["products"]["products"]
    body = f"""
<div class="wrap article-header article">
  <p class="eyebrow">Seasonal · Holiday hosting 2026</p>
  <h1>Holiday hosting on a countertop: what actually earns its place</h1>
  {article_meta_row(ctx, 'Buying in season', '7 min read')}
</div>
<div class="wrap article">
  <img class="article-hero-img" src="{esc(ctx.rel('assets/img/season-holiday.jpg'))}"
    alt="A holiday kitchen counter at dusk with a countertop oven, warm string lights, and roasted vegetables (original illustration)">
  <p class="lede">Hosting season has one hard constraint: oven real estate. The machines that earn a
  place on the counter in December are the ones that solve a specific problem in your specific
  kitchen. Here’s the plan we’d run — and the queue items that map to it.</p>

  <h2>Step 1: Write the meal before you shop</h2>
  <p>List the menu with times. The spreadsheet of one column matters more than any appliance spec:
  <em>which dish owns the main oven, and for how long</em>. Whatever is displaced — sides, rolls,
  reheating, appetizers — is the job description for a countertop appliance. If nothing is displaced,
  you don’t need one this year.</p>

  <h2>Step 2: Match the displaced job to a shape</h2>
  <ul>
    <li><strong>Batched sides and tossable food</strong> (roast vegetables, potatoes, wings): a
    dual-basket machine keeps two sides moving and finishing together.</li>
    <li><strong>Flat, layered, or tall food</strong> (rolls, a small bird, sheet-pan dinners, pizza):
    a French-door oven-style machine takes racks and trays and frees the main oven entirely.</li>
    <li><strong>The centerpiece protein</strong>: whatever cooks it, doneness is the risk. A wireless
    probe thermometer turns “I think it’s ready” into a number — including while guests arrive and
    the kitchen gets loud.</li>
  </ul>

  <h2>Step 3: Run the hosting-day timeline</h2>
  <ul class="checklist">
    <li>Write each dish’s cook time and temperature, then stack them against the appliances you’ll
    actually have.</li>
    <li>Plan the <strong>holding window</strong> — food that finishes early needs a low-temperature
    home; a countertop oven at its lowest setting often beats a cold stovetop.</li>
    <li>Decide who checks what. Machines with windows and loud done-tones reduce the number of times
    anyone opens a door and drops the temperature.</li>
    <li>Pre-assign cleanup: one machine, one owner, one wash plan (see the
    <a href="{esc(ctx.rel('guides/cleanup-and-counter-space.html'))}">cleanup guide</a>).</li>
    <li>Do one dry run before the big day. Appliances are recipes too.</li>
  </ul>

  <h2>Step 4: What earns its place</h2>
  <p>The test is brutal and useful: <em>does this machine own a job on the hosting-day timeline that
  nothing else can do as well?</em> If it’s just “extra cooking power,” a second oven rack or a
  neighbor’s slow cooker might be cheaper. If it owns the displaced job — that’s a purchase with a
  reason.</p>

  <h2>On the queue for this season</h2>
  <p>Three shapes and one safety net: a dual-basket
  {ctx.sponsored_cta(ps[0], '6-quart dual basket', 'btn-ghost')}, a French-door
  {ctx.sponsored_cta(ps[1], '26QT oven-style', 'btn-ghost')}, an
  {ctx.sponsored_cta(ps[2], '8-quart XL basket', 'btn-ghost')}, and the
  {ctx.sponsored_cta(ps[4], 'wireless probe thermometer', 'btn-ghost')}. Each link is marked
  Sponsored and may earn us a commission. Listing wording and sources are in the
  <a href="{esc(ctx.rel('products/index.html'))}">test queue</a>; nothing here is a test result.</p>

  {related_row(ctx, [
      ('Basket or oven-style air fryer: what should you compare?', 'guides/basket-or-oven-style-air-fryer.html'),
      ('A no-hype checklist for comparing air fryer capacity', 'guides/air-fryer-capacity-checklist.html'),
      ('Questions before buying a multi-function appliance', 'guides/questions-multifunction-appliance.html'),
  ])}
</div>
"""
    return {
        "path": path,
        "title": "Holiday hosting on a countertop: what actually earns its place",
        "description": "A hosting-season plan for kitchens whose main oven is booked: match displaced jobs to appliance shapes, run the timeline, and buy only what earns its place.",
        "section": "guides",
        "og_image": "assets/img/season-holiday.jpg",
        "og_type": "article",
        "breadcrumb": [("Buyer’s guides", "guides/index.html"), ("Holiday hosting 2026", None)],
        "jsonld": [
            article_jsonld(path, "Holiday hosting on a countertop: what actually earns its place",
                           "A hosting-season plan for booked ovens.", "assets/img/season-holiday.jpg"),
            breadcrumb_jsonld([("Home", "index.html"), ("Buyer’s guides", "guides/index.html"), ("Holiday hosting 2026", path)]),
        ],
        "body": body,
        "sitemap": {"priority": "0.8", "changefreq": "weekly"},
        "feed": {
            "title": "Holiday hosting on a countertop: what actually earns its place",
            "description": "The seasonal plan for kitchens whose main oven is already booked.",
            "category": "Seasonal",
        },
    }


def compare_page(ctx):
    ps = ctx.d["products"]["products"]
    rows = []
    for p in ps:
        obs = p["observed"]
        if obs["status"] == "resolved":
            name = f'<a href="{esc(ctx.rel("products/index.html"))}#{esc(p["id"])}">{esc(p["display_name"])}</a>'
            shape = esc(p["category_note"].replace(" (observed breadcrumb)", ""))
            claim = esc(", ".join(p["listing_claims_verbatim"][:3]))
            state = f'{ctx.chip("Observed " + obs["date"], "chip-ok")}'
        else:
            name = f'<a href="{esc(ctx.rel("products/index.html"))}#{esc(p["id"])}">Submitted link 4 — identity unconfirmed</a>'
            shape = f'<span class="unverified">unverified</span>'
            claim = f'<span class="unverified">—</span> {ctx.flag("FLG-004")}'
            state = f'{ctx.chip("Awaiting check", "chip-flag")}'
        rows.append(
            f"<tr><td>{name}</td><td>{shape}</td><td>{claim}</td><td>{state}</td>"
            f'<td class="src-cell">{ctx.srcs(p["sources"][:1])}</td></tr>'
        )
    body = f"""
<div class="wrap article-header">
  <p class="eyebrow">Compare</p>
  <h1>Build a shortlist from trade-offs, not trophies</h1>
  <p class="lede">We don’t hand out “best overall” awards — nobody has earned one here yet. What we
  offer is faster: the decision framework, the shape matrix, and the queue cross-referenced against
  both.</p>
</div>
<section class="section"><div class="wrap">
  <h2>The shape matrix</h2>
  <div class="table-scroll"><table class="data">
    <thead><tr><th>If your kitchen needs…</th><th>Start with</th><th>Then read</th></tr></thead>
    <tbody>
      <tr><td>Fast weeknight crisping for 1–3 people, minimal counter claim</td><td>Basket style</td>
        <td><a href="{esc(ctx.rel('guides/air-fryer-capacity-checklist.html'))}">Capacity checklist</a></td></tr>
      <tr><td>Two foods finishing together (sides night, game day, kids + adults)</td><td>Dual basket</td>
        <td><a href="{esc(ctx.rel('guides/basket-or-oven-style-air-fryer.html'))}">Basket vs oven-style</a></td></tr>
      <tr><td>A second oven: racks, trays, pizza, batch baking</td><td>Oven style (French door / convection)</td>
        <td><a href="{esc(ctx.rel('guides/cleanup-and-counter-space.html'))}">Cleanup &amp; counter space</a></td></tr>
      <tr><td>Replacing two appliances with one</td><td>Multi-function oven-style</td>
        <td><a href="{esc(ctx.rel('guides/questions-multifunction-appliance.html'))}">Multi-function questions</a></td></tr>
      <tr><td>Confidence with meat, bread, and holiday proteins</td><td>Probe thermometer (any shape)</td>
        <td><a href="{esc(ctx.rel('guides/holiday-hosting-countertop.html'))}">Holiday hosting</a></td></tr>
    </tbody>
  </table></div>

  <h2 style="margin-top:2em">The decision path</h2>
  <ol>
    <li><strong>Answer the shape question</strong> — what do you cook most? (guide 1)</li>
    <li><strong>Measure twice</strong> — counter, cabinet height, and the largest meal. (guide 2)</li>
    <li><strong>Price the invisible costs</strong> — cleanup parts and storage. (guide 3)</li>
    <li><strong>Interrogate the feature list</strong> — replace vs add. (guide 4)</li>
    <li><strong>Take your checklist to the listings</strong> — the queue below is where our current
    sources are, verbatim and linked.</li>
  </ol>

  <h2 style="margin-top:2em">Queue cross-reference</h2>
  <div class="table-scroll"><table class="data">
    <thead><tr><th>Queue item</th><th>Observed category</th><th>Listing wording (verbatim, excerpt)</th><th>State</th><th>Source</th></tr></thead>
    <tbody>
      {''.join(rows)}
    </tbody>
  </table></div>
  <p class="fine">“Listing wording” is manufacturer copy quoted from the observed listing title — not
  an independent claim by The Crisp Index. Unconfirmed values stay blank and flagged, per our
  <a href="{esc(ctx.rel('about/index.html'))}">verification rule</a>.</p>
</div></section>
"""
    return {
        "path": "compare/index.html",
        "title": "Compare air fryers and countertop ovens",
        "description": "A decision framework for comparing basket, dual-basket, oven-style, and multi-function air fryers — shape matrix, decision path, and the verified queue cross-reference.",
        "section": "compare",
        "breadcrumb": [("Compare", None)],
        "jsonld": [breadcrumb_jsonld([("Home", "index.html"), ("Compare", "compare/index.html")])],
        "body": body,
        "sitemap": {"priority": "0.9", "changefreq": "weekly"},
    }


def products_page(ctx):
    ps = ctx.d["products"]["products"]
    cards = "".join(f'<div style="grid-column:span 1">{product_card(ctx, p)}</div>' for p in ps)
    rows = []
    for p in ps:
        obs = p["observed"]
        if obs["status"] == "resolved":
            intended_cell = (
                f'{esc(p["intended"]["asin"])}<br><span class="fine">{esc(p["intended"]["listing_url"])} '
                f'{ctx.src(p["intended"]["source_ref"], "brief")}</span>'
            )
            observed_cell = (
                f'{esc(obs["asin"])}<br><span class="fine">{esc(obs["final_url"])} · '
                f'{esc(obs["date"])}</span>'
            )
            title_cell = f'“{esc(obs["listing_title_verbatim"])}”'
            cat_cell = esc(obs["category_breadcrumb_verbatim"])
        else:
            intended_cell = (
                f'{esc(p["intended"]["asin"])}<br><span class="fine">{esc(p["intended"]["listing_url"])} '
                f'{ctx.src(p["intended"]["source_ref"], "brief")}</span>'
            )
            observed_cell = (
                f'<span class="unverified">— unverified</span> {ctx.flag("FLG-004")}<br>'
                f'<span class="fine">checkpoint interstitial, {esc(obs["date"])} · 2 attempts</span>'
            )
            title_cell = f'<span class="unverified">— unverified</span>'
            cat_cell = f'<span class="unverified">— unverified</span>'
        price_cell = f'<span class="unverified">— blank</span> {ctx.flag("FLG-010")}'
        flags_cell = " ".join(ctx.flag(f) for f in p["flags"])
        rows.append(
            f'<tr id="{esc(p["id"])}">'
            f'<td><strong>{esc(p["id"])}</strong><br><span class="fine">{esc(p["submitted_link"])}</span></td>'
            f"<td>{intended_cell}</td>"
            f"<td>{observed_cell}</td>"
            f"<td>{title_cell}</td>"
            f"<td>{cat_cell}</td>"
            f"<td>{price_cell}</td>"
            f'<td class="src-cell">{ctx.srcs(p["sources"][:1])}</td>'
            f"<td>{flags_cell}</td>"
            f"</tr>"
        )
    body = f"""
<div class="wrap article-header">
  <p class="eyebrow">The Test Queue</p>
  <h1>Five links on the bench</h1>
  <p class="lede">This is the shop window and the source book in one place: the machines we’re
  tracking right now, with every observed fact linked to where it came from. Prices are never cached —
  the buttons go straight to Amazon’s current listing.</p>
</div>
<section class="section"><div class="wrap">
  <div class="card-grid">
    {product_card(ctx, ps[0])}
    {product_card(ctx, ps[1])}
    {product_card(ctx, ps[2])}
  </div>
  <div class="card-grid" style="margin-top:22px">
    {product_card(ctx, ps[3])}
    {product_card(ctx, ps[4])}
  </div>
</div></section>

<section class="section section-alt"><div class="wrap">
  <div class="section-head"><div>
    <p class="eyebrow">Source notes</p>
    <h2>What we verified — and what we didn’t</h2>
    <p>Intended identifiers come from the submitted links themselves. Observed listings come from
    following each submitted link on 2026-11-20. The two columns are never merged. Values we couldn’t
    confirm from an official source are blank and flagged — never inferred.</p>
  </div>
  <a class="btn btn-ghost" href="{esc(ctx.rel('workshop/register.html'))}">Open the full register</a></div>
  <div class="table-scroll"><table class="data">
    <thead><tr>
      <th>Queue item</th><th>Intended identifier &amp; URL</th><th>Observed redirect target</th>
      <th>Listing title (verbatim)</th><th>Category breadcrumb (verbatim)</th><th>Price</th>
      <th>Source</th><th>Flags</th>
    </tr></thead>
    <tbody>
      {''.join(rows)}
    </tbody>
  </table></table></div>
  <p class="fine">Observation method and record-separation policy are documented on the
  <a href="{esc(ctx.rel('workshop/register.html'))}">product register</a> page. Items marked
  <em>unverified</em> are listed on <a href="{esc(ctx.rel('workshop/flagged.html'))}">Flagged for
  Review</a> with the action needed to close them.</p>
</div></section>

<section class="section"><div class="wrap">
  <div class="callout">
    <h3>How the queue works</h3>
    <ol>
      <li><strong>A link is submitted</strong> — its intended identifier and URL are recorded exactly
      as given, with the date and source.</li>
      <li><strong>The link is followed once</strong> — the destination is recorded in a separate
      observed field. If Amazon’s checkpoint page appears, the field stays blank and a flag opens.</li>
      <li><strong>The listing is quoted verbatim</strong> — titles and category paths, each with its
      source link. Manufacturer wording is labeled as such; it is not our test result.</li>
      <li><strong>Nothing scales before validation</strong> — one link per product must pass the
      Associates workflow test (destination + tracking report) before any link counts as final.</li>
    </ol>
  </div>
</div></section>
"""
    return {
        "path": "products/index.html",
        "title": "The Test Queue — products we’re tracking",
        "description": "The five submitted links, verified one by one: intended identifiers, observed Amazon listing targets, verbatim titles, sources, and flags — with sponsored links to current listings.",
        "section": "products",
        "breadcrumb": [("The Test Queue", None)],
        "jsonld": [breadcrumb_jsonld([("Home", "index.html"), ("The Test Queue", "products/index.html")])],
        "body": body,
        "sitemap": {"priority": "0.9", "changefreq": "weekly"},
    }


def about_page(ctx):
    body = f"""
<div class="wrap article-header article">
  <p class="eyebrow">About</p>
  <h1>A small publication with a strict source rule</h1>
  <p class="lede">The Crisp Index is written and edited by {esc(AUTHOR)} — an editorial team
  identity, not a fictional persona. We publish buying guidance for countertop kitchens, and we fund
  it with clearly marked affiliate links. Those are the only two promises that matter: useful
  guidance, and an honest money story.</p>
</div>
<div class="wrap article">
  <h2>Methodology</h2>
  <ol>
    <li><strong>Register first.</strong> Every product enters the
    <a href="{esc(ctx.rel('workshop/register.html'))}">source register</a> with its submitted link,
    intended identifier, and source date — before it appears anywhere reader-facing.</li>
    <li><strong>Observe, then quote.</strong> We follow each submitted link once and record the
    destination in a separate field. Listing titles and category paths are quoted verbatim with
    source links. We never merge what a link says with where it goes.</li>
    <li><strong>Blank beats invented.</strong> If a value can’t be confirmed from an official source,
    it stays blank and gets a flag. Prices and ratings are volatile, so we don’t cache them at all.</li>
    <li><strong>Guides before verdicts.</strong> Our guides are decision frameworks and checklists.
    We publish “best of” verdicts only when a documented hands-on testing method exists — and today
    it doesn’t, so we don’t.</li>
  </ol>

  <h2>What we don’t do</h2>
  <ul>
    <li>No paid placements, ever. If a brand ever pays for coverage, it will be labeled as such in
    the same strip as our affiliate disclosure.</li>
    <li>No invented testing. No fake lab coats, no stock-photo “our team”, no made-up personas.</li>
    <li>No cached prices, no unverified ratings, no guessed specs.</li>
    <li>No urgency theater. Guides stay up to date or get corrected.</li>
  </ul>

  <h2 id="corrections">Corrections policy</h2>
  <p>Found an error, a stale claim, or a listing that changed? Say so — every guide page links back
  here, and corrections are logged with the date, what changed, and why. Since our claim is
  “sourced,” being wrong is a bug with a paper trail.</p>
  <p><a class="btn btn-ghost" data-tci="feedback" href="{esc(ctx.rel('workshop/questions.html'))}">Report an issue or suggest a topic</a></p>

  <h2>How the site is funded</h2>
  <p>Commission income from qualifying purchases through links marked
  {ctx.chip('Sponsored', 'chip-sponsored')} — following the Amazon Associates
  <a href="https://affiliate-program.amazon.com/help/operating/agreement" rel="noopener" target="_blank">Operating
  Agreement</a> and FTC disclosure guidance. Full detail lives on the
  <a href="{esc(ctx.rel('disclosure/index.html'))}">disclosure page</a>. Affiliate income never buys
  a ranking, a verdict, or a quieter flag.</p>

  <h2>Editorial roadmap</h2>
  <p>We publish on a two-guides-per-month cadence with seasonal anchors, and choose upcoming topics
  from measured search queries once Search Console is connected — not from instinct. The proposal
  queue (<a href="{esc(ctx.rel('workshop/suggestions.html'))}">Suggestions &amp; decisions</a>) is
  where that gets decided in the open.</p>
</div>
"""
    return {
        "path": "about/index.html",
        "title": "About & methodology",
        "description": "Who writes The Crisp Index, how every claim is sourced and verified, our corrections policy, and how the site is funded through disclosed affiliate links.",
        "section": "about",
        "breadcrumb": [("About", None)],
        "jsonld": [breadcrumb_jsonld([("Home", "index.html"), ("About", "about/index.html")])],
        "body": body,
        "sitemap": {"priority": "0.6", "changefreq": "monthly"},
    }


def disclosure_page(ctx):
    stmt = ctx.site["exact_associates_statement"]
    body = f"""
<div class="wrap article-header article">
  <p class="eyebrow">Disclosure</p>
  <h1>Disclosure &amp; affiliate policy</h1>
  <p class="lede">Short version: we earn commissions from some links; you never pay more because of
  them; and every one of those links is labeled.</p>
</div>
<div class="wrap article">
  <div class="callout">
    <h2 style="margin-top:0">The required statement</h2>
    <p style="font-size:1.15rem"><strong>{esc(stmt)}</strong></p>
    <p class="fine">This statement appears above the fold on every page of this site (the amber strip
    under the masthead), again in every footer, and on this page — per the Amazon Associates
    Operating Agreement, Section 5
    {ctx.src('S-01', 'S-01 · Operating Agreement')} and Associates help
    {ctx.src('S-02', 'S-02 · Associates help')}.</p>
  </div>

  <h2>What “Sponsored” means here</h2>
  <ul>
    <li>Every outbound product link carries a visible {ctx.chip('Sponsored', 'chip-sponsored')} chip
    and the <code>rel="sponsored"</code> attribute — the standard machine-readable signal for
    affiliate links.</li>
    <li>If you buy through one of those links, we may earn a commission on qualifying purchases.
    The price you pay is identical either way.</li>
    <li>Links to source documents (Amazon help pages, FTC guidance) are <em>not</em> affiliate links.</li>
  </ul>

  <h2>Why the disclosure sits up top</h2>
  <p>FTC guidance says material connections must be disclosed where people will see them — hard to
  miss, in plain language, with the endorsement itself — not buried on an about page
  {ctx.src('S-04', 'S-04 · FTC Disclosures 101')}. The FTC’s Endorsement Guides further require that
  endorsements be truthful and not misleading {ctx.src('S-05', 'S-05 · FTC Endorsement Guides')}.
  That’s why the amber strip is on every page and the chip is on every product button.</p>

  <h2>What we show — and don’t show — about products</h2>
  <ul>
    <li>Product names and category paths are <strong>quoted verbatim</strong> from the observed Amazon
    listings, each with its source link. Where a label is shortened for layout, the verbatim title is
    shown right beside it.</li>
    <li><strong>Prices and ratings are never displayed.</strong> They change constantly; we don’t
    cache them and we don’t verify them in real time. The buttons say “Check today’s price” because
    that’s the only honest price.</li>
    <li><strong>Product images on this site are original illustrations</strong>, not listing photos.
    We don’t hotlink Amazon imagery outside the approved tools.</li>
    <li>Manufacturer claims (capacities, “dishwasher-safe,” feature names) are labeled as listing
    wording. They are not our test results.</li>
  </ul>

  <h2>Link compliance status</h2>
  <p>The submitted short links and their exact compliance status are unresolved and are tracked as
  {ctx.flag('FLG-003')} — we do not claim they are invalid. Until each link passes the one-per-product
  Associates workflow test (destination + tracking report), all product URLs are marked provisional
  {ctx.flag('FLG-005')}. See the <a href="{esc(ctx.rel('workshop/flagged.html'))}">Flagged for
  Review</a> register for details and actions.</p>

  <h2>Questions?</h2>
  <p>See <a href="{esc(ctx.rel('workshop/questions.html'))}">open questions</a> or the
  <a href="{esc(ctx.rel('about/index.html'))}#corrections">corrections policy</a>. This page is
  reviewed whenever the Operating Agreement or FTC guidance changes; last review 2026-11-20.</p>
</div>
"""
    return {
        "path": "disclosure/index.html",
        "title": "Disclosure & affiliate policy",
        "description": "How The Crisp Index earns commissions: the required Amazon Associates statement, sponsored-link labeling, what we display about products, and our link compliance status.",
        "section": "disclosure",
        "breadcrumb": [("Disclosure & affiliate policy", None)],
        "jsonld": [breadcrumb_jsonld([("Home", "index.html"), ("Disclosure", "disclosure/index.html")])],
        "body": body,
        "sitemap": {"priority": "0.6", "changefreq": "monthly"},
    }
