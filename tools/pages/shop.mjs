// Reader-facing pages: front page, category desks, guides, collections, product pages.
import { page, breadcrumb, paidLink, SITE, jsonLdOrg, jsonLdWebSite } from "../lib/layout.mjs";
import { md } from "../lib/md.mjs";

const CATEGORIES = [
  {
    slug: "air-fryers",
    label: "Air fryers",
    headline: "Three shapes, one question",
    blurb:
      "Dual basket, single basket and oven style are different products wearing the same name. This desk compares them by the job they do, not by the size of the number on the box.",
    ids: ["chefman-6qt-dual-basket", "chefman-turbofry-8qt", "emeril-26qt-french-door"],
  },
  {
    slug: "thermometers",
    label: "Thermometers",
    headline: "The tool that answers the timer's question",
    blurb:
      "A timer measures the clock. A probe measures the food. This is the smallest, cheapest item on the desk and the one that changes the most cooking decisions.",
    ids: ["chef-iq-sense-thermometer"],
  },
];

const COLLECTIONS = [
  {
    slug: "countertop-season",
    no: "01",
    title: "Countertop season",
    blurb: "The appliances that earn permanent counter space, judged on clearance, cleanup and whether they replace something.",
    ids: ["chefman-6qt-dual-basket", "chefman-turbofry-8qt", "emeril-26qt-french-door"],
  },
  {
    slug: "cook-and-check",
    no: "02",
    title: "Cook and check",
    blurb: "Instruments rather than appliances. Small, cheap and the ones you reach for every time.",
    ids: ["chef-iq-sense-thermometer"],
  },
  {
    slug: "the-short-list",
    no: "03",
    title: "The short list",
    blurb: "If you are starting from nothing: one basket, one oven, one probe. Three decisions, in order.",
    ids: ["chefman-turbofry-8qt", "emeril-26qt-french-door", "chef-iq-sense-thermometer"],
  },
];

function monogram(p) {
  const initials = (p.short_name || p.working_name)
    .split(/\s+/)
    .filter((w) => /^[A-Za-z0-9]/.test(w))
    .slice(0, 2)
    .map((w) => w[0].toUpperCase())
    .join("");
  return initials || "··";
}

export function productCard(p, { compact = false } = {}) {
  const specs = (p.attributes_from_listing || [])
    .slice(0, compact ? 2 : 4)
    .map((a) => `<li><span>${a.name}</span>${a.value}</li>`)
    .join("");

  const pairs = [
    p.best_for ? `<div><dt>Right for</dt><dd>${p.best_for}</dd></div>` : "",
    p.consider_before_buying ? `<div><dt>Check first</dt><dd>${p.consider_before_buying}</dd></div>` : "",
  ].filter(Boolean).join("");

  return `<article class="product">
  <div class="product__head">
    <div class="monogram" aria-hidden="true">${monogram(p)}</div>
    <div>
      <div class="product__brand">${p.brand}</div>
      <h3 class="product__name"><a href="${SITE.base}/products/${p.slug}/" style="text-decoration:none">${p.short_name}</a></h3>
    </div>
  </div>
  <div class="product__body">
    <p class="verdict">${p.editorial_angle}</p>
    ${specs ? `<ul class="specs">${specs}</ul>` : ""}
    ${pairs ? `<dl class="pair">${pairs}</dl>` : ""}
  </div>
  <div class="product__foot">
    ${paidLink(p.tagged_url)}
    <a href="${SITE.base}/products/${p.slug}/" style="font-size:.8rem;color:var(--ink-3);text-decoration:none">Read the reasoning →</a>
  </div>
</article>`;
}

function guideCard(g) {
  const url = `${SITE.base}/buying-guides/${g.meta.slug}/`;
  return `<a class="guide-card" href="${url}">
  <div class="guide-card__kicker">${g.meta.kicker}</div>
  <h3>${g.meta.title}</h3>
  <p>${g.meta.dek || g.meta.description}</p>
  <div class="guide-card__meta"><span>${g.meta.reading}</span><span>Published ${g.meta.published}</span></div>
</a>`;
}

function captureBlock() {
  return `<section class="section wrap">
  <div class="capture" id="newsletter">
    <div>
      <h2>One guide when it publishes. Nothing else.</h2>
      <p>No offers, no countdowns, no discount codes. We write a guide when we can verify it, and we send it when it ships. That is the whole promise.</p>
    </div>
    <div>
      <form data-capture>
        <label class="visually-hidden" for="cap-email">Email address</label>
        <input id="cap-email" type="email" name="email" placeholder="you@example.com" autocomplete="email" required>
        <button class="btn" type="submit">Notify me</button>
      </form>
      <p class="capture__fine" data-capture-note>No list is connected yet. Submissions are not stored until an endpoint is configured — see the <a href="${SITE.base}/review/flagged-for-review/" style="color:#c9bdb0">known gaps</a>.</p>
    </div>
  </div>
</section>`;
}

function shelfRow(products) {
  return `<div class="grid-products">${products.map((p) => productCard(p)).join("")}</div>`;
}

/* ------------------------------------------------------------------ front */
function front({ DATA, GUIDES, published, addRoute }) {
  const lead = GUIDES[0];
  const rest = GUIDES.slice(1, 4);

  addRoute("/", { priority: 1.0, changefreq: "weekly" });

  const body = `
<section class="hero">
  <div class="wrap hero__grid">
    <div>
      <p class="kicker kicker--plain">Issue 01 · Countertop season · ${SITE.published}</p>
      <h1>The kitchen counter is the <em>only</em> appliance showroom you actually live in.</h1>
      <p class="hero__sub">Four appliances, one instrument, and a set of honest answers about which ones deserve the space. We publish the reasoning, the gaps, and the questions we could not close.</p>
      <div class="hero__actions">
        <a class="btn btn--primary" href="${SITE.base}/buying-guides/">Read the lead guide</a>
        <a class="btn btn--ghost" href="#the-shelf">See the shelf</a>
      </div>
    </div>
    <aside class="note">
      <div class="note__label">From the desk</div>
      <p>“Most air fryer advice is a listicle ranking things nobody has tested. We are trying something harder: show the shape of each decision, say what we verified, and let you pick.”</p>
      <div class="note__by">
        <span class="avatar" aria-hidden="true">SN</span>
        <span><b>ShopNow Labs</b><br>Countertop buying desk</span>
      </div>
    </aside>
  </div>
</section>

<section class="section wrap" aria-labelledby="lead-h">
  <p class="kicker">The lead guide</p>
  <div style="display:grid;grid-template-columns:minmax(0,1.4fr) minmax(0,1fr);gap:clamp(1.5rem,4vw,3rem);align-items:start" class="lead-split">
    <div>
      <h2 id="lead-h" style="text-wrap:balance"><a href="${SITE.base}/buying-guides/${lead.meta.slug}/" style="text-decoration:none">${lead.meta.title}</a></h2>
      <p class="lede">${lead.meta.dek}</p>
      <p><a class="btn btn--ghost" href="${SITE.base}/buying-guides/${lead.meta.slug}/">Read the guide →</a></p>
    </div>
    <div class="stack-sm">
      <div class="callout" style="margin:0">
        <span class="callout__label">What this site will not do</span>
        <p class="small" style="margin:0">We do not print prices, because Amazon permits price display only through its own link or its API. We do not use listing photography. We do not rank products we have not explained.</p>
      </div>
      <div class="callout callout--warn" style="margin:0">
        <span class="callout__label">Two things still open</span>
        <p class="small" style="margin:0">One submitted product link never resolved, and the supplied short links did not carry a visible tag. Both are published on the <a href="${SITE.base}/review/flagged-for-review/">known gaps page</a> rather than quietly dropped.</p>
      </div>
    </div>
  </div>
</section>

<section class="section section--paper2" id="the-shelf" aria-labelledby="shelf-h">
  <div class="wrap">
    <div class="row-between" style="margin-bottom:1.5rem">
      <div>
        <p class="kicker">The shelf</p>
        <h2 id="shelf-h" style="margin:0">What we actually recommend looking at</h2>
      </div>
      <a href="${SITE.base}/air-fryers/" class="btn btn--ghost btn--sm">All air fryers →</a>
    </div>
    ${shelfRow(published.filter((p) => p.category_slug === "air-fryers"))}
    <div style="margin-top:1.25rem">
      ${shelfRow(published.filter((p) => p.category_slug === "thermometers"))}
    </div>
    <p class="small muted" style="margin-top:1rem">Every link here is paid and opens Amazon in a new tab. ${SITE.assoc}</p>
  </div>
</section>

<section class="section wrap" aria-labelledby="guides-h">
  <p class="kicker">Buying guides</p>
  <h2 id="guides-h">Questions worth answering before you spend</h2>
  <div class="guides" style="margin-top:1.5rem">
    ${rest.map(guideCard).join("")}
    <a class="guide-card" href="${SITE.base}/buying-guides/" style="background:var(--ember-wash);border-color:#f0d6c6">
      <div class="guide-card__kicker">All six</div>
      <h3>Browse the full guide index</h3>
      <p>Shape, capacity, cleanup, multi-function, doneness and the first six things to cook.</p>
      <div class="guide-card__meta"><span>6 guides</span></div>
    </a>
  </div>
</section>

<section class="section section--paper2" aria-labelledby="coll-h">
  <div class="wrap">
    <p class="kicker">Collections</p>
    <h2 id="coll-h">Grouped the way people actually shop</h2>
    <div class="collections" style="margin-top:1.5rem">
      ${COLLECTIONS.map(
        (c) => `<a class="collection${c.no === "01" ? " collection--ember" : ""}" href="${SITE.base}/collections/#${c.slug}">
        <div><span class="collection__no">${c.no}</span><h3>${c.title}</h3><p>${c.blurb}</p></div>
        <span class="collection__arrow" aria-hidden="true">→</span>
      </a>`
      ).join("")}
    </div>
  </div>
</section>

<section class="section wrap" aria-labelledby="trust-h">
  <div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1.5rem" class="trust-row">
    <div>
      <p class="kicker">How we pick</p>
      <h3 id="trust-h">Design against job, not against a ranking</h3>
      <p class="small muted">We start from what you cook and what fits on your counter, then match the appliance shape to it. Where a listing does not state a specification, we say so instead of filling it in.</p>
      <p class="small"><a href="${SITE.base}/how-we-pick/">Our method →</a></p>
    </div>
    <div>
      <p class="kicker">What we verified</p>
      <h3>Every claim has a source</h3>
      <p class="small muted">Compliance statements are quoted from Amazon's Operating Agreement, the Associates Program Policies, the FTC Endorsement Guides and 16 CFR 255.5. The source register lists each one with the date it was read.</p>
      <p class="small"><a href="${SITE.base}/review/sources/">Source register →</a></p>
    </div>
    <div>
      <p class="kicker">What we don't know</p>
      <h3>Twelve open questions, one page</h3>
      <p class="small muted">Which product is behind the unresolved link, whether the tag attributes, what anyone searches for. Listed with the step that would close each one.</p>
      <p class="small"><a href="${SITE.base}/review/questions/">Open questions →</a></p>
    </div>
  </div>
</section>

${captureBlock()}
`;

  return page({
    path: "/",
    title: `${SITE.name} — a countertop buying desk for air fryers and probes`,
    description:
      "An independent countertop buying desk. Question-shaped guides to air fryer shape, capacity, cleanup and doneness, with every compliance claim sourced and every gap published.",
    body,
    jsonLd: {
      "@context": "https://schema.org",
      "@graph": [
        jsonLdOrg(),
        jsonLdWebSite(),
        {
          "@type": "CollectionPage",
          "@id": `${SITE.url}/#page`,
          name: "ShopNow Labs front page",
          isPartOf: { "@id": `${SITE.url}/#site` },
          about: "Countertop cooking appliances",
        },
      ],
    },
  });
}

/* ------------------------------------------------------------- category */
function categoryPage(cat, { DATA, GUIDES, published, addRoute }) {
  const items = cat.ids.map((id) => published.find((p) => p.id === id)).filter(Boolean);
  const related = GUIDES.filter((g) => g.meta.products.some((id) => cat.ids.includes(id))).slice(0, 3);

  addRoute(`/${cat.slug}/`, { priority: 0.9, changefreq: "weekly" });

  const rows = items
    .map(
      (p) => `<tr>
      <td><a href="${SITE.base}/products/${p.slug}/">${p.short_name}</a><br><span class="id">${p.intended_asin}</span></td>
      <td>${p.attributes_from_listing.slice(0, 2).map((a) => `${a.name}: <strong>${a.value}</strong>`).join("<br>") || "—"}</td>
      <td>${p.best_for || "—"}</td>
      <td>${p.consider_before_buying || "—"}</td>
      <td>${paidLink(p.tagged_url, "Amazon", { small: true })}</td>
    </tr>`
    )
    .join("");

  const body = `${breadcrumb([["Home", "/"], [cat.label, null]])}
<section class="article-head wrap">
  <p class="kicker">The ${cat.label.toLowerCase()} desk</p>
  <h1>${cat.headline}</h1>
  <p class="lede">${cat.blurb}</p>
  <div class="article-head__meta"><span>${items.length} products</span><span>Updated ${SITE.published}</span><span>${SITE.assoc}</span></div>
</section>

<section class="section wrap">
  <h2 class="visually-hidden">Products on this desk</h2>
  ${shelfRow(items)}
</section>

<section class="section section--tight section--paper2">
  <div class="wrap">
    <p class="kicker">The same products, in a table</p>
    <h2 style="font-size:1.4rem">Scan, then read</h2>
    <div class="tablewrap" style="margin-top:1rem">
      <table class="data">
        <thead><tr><th>Product / ASIN</th><th>Stated specs</th><th>Right for</th><th>Check first</th><th>Listing</th></tr></thead>
        <tbody>${rows}</tbody>
      </table>
    </div>
    <p class="tiny muted" style="margin-top:.8rem">Specifications are as stated on each Amazon listing on ${SITE.published}. No price or star rating is shown: see <a href="${SITE.base}/review/flagged-for-review/">why</a>.</p>
  </div>
</section>

${
    related.length
      ? `<section class="section wrap">
  <p class="kicker">Read before you choose</p>
  <div class="guides">${related.map(guideCard).join("")}</div>
</section>`
      : ""
  }`;

  return page({
    path: `/${cat.slug}/`,
    title: `${cat.label} — ${SITE.name}`,
    description: cat.blurb,
    body,
    current: `/${cat.slug}/`,
    jsonLd: {
      "@context": "https://schema.org",
      "@type": "CollectionPage",
      name: cat.headline,
      description: cat.blurb,
      url: `${SITE.url}/${cat.slug}/`,
      isPartOf: { "@id": `${SITE.url}/#site` },
    },
  });
}

/* --------------------------------------------------------------- guides */
function guideIndex({ GUIDES, addRoute }) {
  addRoute("/buying-guides/", { priority: 0.9, changefreq: "weekly" });
  const body = `${breadcrumb([["Home", "/"], ["Buying guides", null]])}
<section class="article-head wrap">
  <p class="kicker">The guide index</p>
  <h1>Six questions, answered properly</h1>
  <p class="lede">Each guide starts from a decision a buyer actually faces, works through the trade-off, and only then points at a product. None of them claims to be a test we did not run.</p>
  <div class="article-head__meta"><span>6 guides</span><span>Published ${SITE.published}</span><span><a href="${SITE.base}/feed.xml">RSS</a></span></div>
</section>
<section class="section wrap">
  <h2 style="margin-bottom:1.25rem">The six guides</h2>
  <div class="guides">${GUIDES.map(guideCard).join("")}</div>
</section>
${captureBlock()}`;

  return page({
    path: "/buying-guides/",
    title: `Buying guides — ${SITE.name}`,
    description: "Six question-shaped buying guides to air fryer shape, capacity, cleanup, multi-function appliances, doneness and first-week cooking.",
    body,
    current: "/buying-guides/",
    jsonLd: {
      "@context": "https://schema.org",
      "@type": "CollectionPage",
      name: "Buying guides",
      url: `${SITE.url}/buying-guides/`,
      isPartOf: { "@id": `${SITE.url}/#site` },
      hasPart: GUIDES.map((g) => ({
        "@type": "Article",
        headline: g.meta.title,
        url: `${SITE.url}/buying-guides/${g.meta.slug}/`,
      })),
    },
  });
}

function guidePage(g, { published, addRoute, GUIDES }) {
  const idx = GUIDES.findIndex((x) => x.meta.slug === g.meta.slug);
  const prev = GUIDES[idx - 1];
  const next = GUIDES[idx + 1];
  const url = `/buying-guides/${g.meta.slug}/`;
  addRoute(url, { priority: 0.8, changefreq: "monthly" });

  const items = g.meta.products.map((id) => published.find((p) => p.id === id)).filter(Boolean);

  const body = `${breadcrumb([["Home", "/"], ["Buying guides", "/buying-guides/"], [g.meta.kicker, null]])}
<article>
<header class="article-head wrap">
  <p class="kicker">${g.meta.kicker}</p>
  <h1 style="max-width:20ch">${g.meta.title}</h1>
  <p class="lede">${g.meta.dek}</p>
  <div class="byline">
    <span class="avatar" aria-hidden="true">SN</span>
    <span>By <b>${SITE.author}</b> · Published <b>${g.meta.published}</b> · ${g.meta.reading} read</span>
  </div>
  <div class="article-head__meta"><span>${SITE.ftc}</span></div>
</header>

<div class="section wrap" style="display:grid;grid-template-columns:minmax(0,1fr) 19rem;gap:clamp(1.5rem,4vw,3.5rem);align-items:start" class="guide-split">
  <div class="prose">
    ${md(g.body, { base: SITE.base })}
  </div>
  <aside style="position:sticky;top:1.5rem">
    <div class="note" style="margin-bottom:1rem">
      <div class="note__label">Products named in this guide</div>
      ${items
        .map(
          (p) => `<div style="padding:.7rem 0;border-bottom:1px solid var(--rule)">
        <div class="product__brand">${p.brand}</div>
        <a href="${SITE.base}/products/${p.slug}/" style="font-family:var(--display);font-size:.98rem;text-decoration:none;display:block;margin-bottom:.4rem">${p.short_name}</a>
        ${paidLink(p.tagged_url, "Amazon", { small: true })}
      </div>`
        )
        .join("")}
      <p class="tiny muted" style="margin-top:.8rem">${SITE.assoc} Every link is a paid link.</p>
    </div>
    <div class="callout" style="margin:0">
      <span class="callout__label">Corrections</span>
      <p class="small" style="margin:0">Something wrong on this page? The correction policy and the contact route are on <a href="${SITE.base}/editorial-standards/">editorial standards</a>.</p>
    </div>
  </aside>
</div>

<nav class="pager wrap" aria-label="Guide pagination">
  ${prev ? `<a href="${SITE.base}/buying-guides/${prev.meta.slug}/">← ${prev.meta.kicker}</a>` : "<span></span>"}
  ${next ? `<a href="${SITE.base}/buying-guides/${next.meta.slug}/">${next.meta.kicker} →</a>` : `<a href="${SITE.base}/buying-guides/">All guides →</a>`}
</nav>
</article>`;

  return page({
    path: url,
    title: `${g.meta.title} — ${SITE.name}`,
    description: g.meta.description,
    body,
    current: "/buying-guides/",
    jsonLd: {
      "@context": "https://schema.org",
      "@type": "Article",
      headline: g.meta.title,
      description: g.meta.description,
      datePublished: g.meta.published,
      dateModified: g.meta.published,
      url: `${SITE.url}${url}`,
      author: { "@type": "Organization", name: SITE.author, url: `${SITE.url}/editorial-standards/` },
      publisher: { "@id": `${SITE.url}/#org` },
      isPartOf: { "@id": `${SITE.url}/#site` },
      about: items.map((p) => ({ "@type": "Product", name: p.working_name, brand: p.brand })),
    },
  });
}

/* ---------------------------------------------------------- product page */
function productPage(p, { published, addRoute, GUIDES }) {
  const url = `/products/${p.slug}/`;
  addRoute(url, { priority: 0.7, changefreq: "weekly" });
  const guides = GUIDES.filter((g) => g.meta.products.includes(p.id));

  const specs = (p.attributes_from_listing || [])
    .map((a) => `<tr><th scope="row">${a.name}</th><td>${a.value}${a.note ? ` <span class="muted tiny">— ${a.note}</span>` : ""}</td></tr>`)
    .join("");

  const observations = (p.listing_observations || [])
    .map((o) => `<p><strong>${o.label}:</strong> ${o.value}${o.detail ? ` <span class="muted">${o.detail}</span>` : ""}</p>`)
    .join("");

  const body = `${breadcrumb([["Home", "/"], [p.category, `/${p.category_slug}/`], [p.short_name, null]])}
<article>
<header class="article-head wrap">
  <div class="product__brand">${p.brand} · ${p.category}</div>
  <h1 style="margin-top:.3rem">${p.working_name}</h1>
  <p class="lede">${p.editorial_angle}</p>
  <div class="article-head__meta">
    <span>ASIN ${p.intended_asin}</span>
    <span>Verified ${p.confirmation_date}</span>
    <span>${SITE.assoc}</span>
  </div>
</header>

<section class="section wrap" style="display:grid;grid-template-columns:minmax(0,1.5fr) minmax(0,1fr);gap:clamp(1.5rem,4vw,3rem);align-items:start">
  <div class="prose">
    <h2>What it is</h2>
    <p>${p.best_for ? `This is the appliance for ${p.best_for.charAt(0).toLowerCase() + p.best_for.slice(1)}` : ""} It is not the answer for everyone on this desk, and the point of this page is to make that clear rather than to sell it.</p>

    <h3>What the listing says</h3>
    <p>Every specification below was read from the Amazon product detail page on ${p.confirmation_date}. Nothing here has been inferred, and nothing has been carried over from a similar model.</p>

    ${
      p.amazon_review_summary_observed
        ? `<div class="callout"><span class="callout__label">What Amazon's review summary reports</span><p class="small" style="margin:0">${p.amazon_review_summary_observed}</p></div><p class="tiny muted">That is a description of what the listing's review-summary widget displayed, not an independent test. ${p.amazon_review_summary_note || ""}</p>`
        : `<div class="callout callout--warn"><span class="callout__label">Not captured</span><p class="small" style="margin:0">${p.amazon_review_summary_note}</p></div>`
    }

    ${
      observations
        ? `<h3>Other things shown on the listing</h3>${observations}`
        : ""
    }

    <h3>The honest objection</h3>
    <p>${p.consider_before_buying}</p>
    <p>If that objection is a dealbreaker for how you cook, no amount of convenience elsewhere will fix it. That is not a flaw in this review; it is the review.</p>

    <h3>Where it fits on the desk</h3>
    <p>${p.category === "Air fryers"
      ? `This is one of three shapes in the <a href="${SITE.base}/air-fryers/">air fryer desk</a>. The shape you should start from is decided by <a href="${SITE.base}/buying-guides/basket-or-oven-air-fryer/">the basket-or-oven question</a>, not by this page.`
      : `This sits beside the appliances rather than replacing one. Its job is described in <a href="${SITE.base}/buying-guides/knowing-when-food-is-done/">the doneness guide</a>.`}</p>

    ${guides.length ? `<h3>Guides that discuss it</h3><ul>${guides.map((g) => `<li><a href="${SITE.base}/buying-guides/${g.meta.slug}/">${g.meta.title}</a></li>`).join("")}</ul>` : ""}
  </div>

  <aside style="position:sticky;top:1.5rem">
    <div class="note">
      <div class="note__label">At a glance</div>
      <table class="prose" style="width:100%;font-size:.82rem;margin:.4rem 0 1rem">
        <tbody>${specs || "<tr><td>No specifications were stated in the retrieved listing text.</td></tr>"}</tbody>
      </table>
      ${paidLink(p.tagged_url, "Check on Amazon")}
      <p class="tiny muted" style="margin-top:.7rem">Opens the Amazon listing in a new tab. ${SITE.assoc} Price in USD is shown on Amazon, not here.</p>
    </div>
    <div class="callout callout--verify" style="margin-top:1rem">
      <span class="callout__label">Identity check</span>
      <p class="tiny" style="margin:0">Intended ASIN <code>${p.intended_asin}</code>. The submitted short link resolved to <a href="${p.observed_redirect_target}" rel="nofollow noopener" target="_blank">this observed address</a>. Both are recorded on the <a href="${SITE.base}/review/product-register/">product register</a>.</p>
    </div>
  </aside>
</section>
</article>`;

  return page({
    path: url,
    title: `${p.working_name} — ${SITE.name}`,
    description: `${p.short_name}: ${p.editorial_angle} Specifications as stated on the Amazon listing, verified ${p.confirmation_date}.`,
    body,
    jsonLd: {
      "@context": "https://schema.org",
      "@type": "Product",
      name: p.working_name,
      brand: { "@type": "Brand", name: p.brand },
      sku: p.intended_asin,
      description: p.editorial_angle,
      review: {
        "@type": "Review",
        author: { "@type": "Organization", name: SITE.author },
        datePublished: p.confirmation_date,
        reviewBody: `${p.editorial_angle} ${p.consider_before_buying}`,
        publisher: { "@id": `${SITE.url}/#org` },
      },
    },
  });
}

/* ----------------------------------------------------------- collections */
function collectionsPage({ published, addRoute }) {
  addRoute("/collections/", { priority: 0.6, changefreq: "monthly" });
  const body = `${breadcrumb([["Home", "/"], ["Collections", null]])}
<section class="article-head wrap">
  <p class="kicker">Collections</p>
  <h1>Grouped the way people shop</h1>
  <p class="lede">Seasonal and situational groupings rather than a single ranked list. A collection is an editorial framing, and each one says why those products sit together.</p>
</section>
${COLLECTIONS.map((c) => {
  const items = c.ids.map((id) => published.find((p) => p.id === id)).filter(Boolean);
  return `<section class="section section--tight wrap" id="${c.slug}">
    <p class="kicker">Collection ${c.no}</p>
    <h2>${c.title}</h2>
    <p class="lede" style="margin-bottom:1.5rem">${c.blurb}</p>
    ${shelfRow(items)}
  </section>`;
}).join("")}`;

  return page({
    path: "/collections/",
    title: `Collections — ${SITE.name}`,
    description: "Seasonal and situational groupings of countertop appliances and instruments, each with the reason the items sit together.",
    body,
    current: "/collections/",
  });
}

/* --------------------------------------------------------------- export */
export function buildShop(ctx) {
  const { out, addRoute, DATA, GUIDES, published } = ctx;

  out("index.html", front(ctx));
  for (const cat of CATEGORIES) out(`${cat.slug}/index.html`, categoryPage(cat, ctx));
  out("buying-guides/index.html", guideIndex(ctx));
  for (const g of GUIDES) out(`buying-guides/${g.meta.slug}/index.html`, guidePage(g, ctx));
  for (const p of published) out(`products/${p.slug}/index.html`, productPage(p, ctx));
  out("collections/index.html", collectionsPage(ctx));
}

export { CATEGORIES, COLLECTIONS };
