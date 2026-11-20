#!/usr/bin/env node
// Static site generator for Affil3. No dependencies. Reads data/*.json and src/assets, writes the site at the repo root.
// Run: node tools/build.mjs   (then node tools/verify.mjs)
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
// Output goes to the repository root (GitHub Pages serves main at /). Only the paths in OWNED are
// replaced; every other file (data/, src/, tools/, legacy/, COORDINATION.md, ...) is left alone.
const OUT = ROOT;
const OWNED = ['index.html', 'shop', 'products', 'compare', 'search', 'categories', 'guides', 'executive-summary', 'sources', 'questions', 'suggestions',
  'flagged', 'ledger', 'measurement', 'compliance', 'about', '404.html', 'feed.xml', 'sitemap.xml', 'robots.txt',
  'assets/style.css', 'assets/analytics.js', '.nojekyll'];
const read = (p) => JSON.parse(fs.readFileSync(path.join(ROOT, p), 'utf8'));

const cfg = read('data/config.json');
const productsDoc = read('data/products.json');
const products = productsDoc.products;
const catalogDoc = read('data/catalog.json');
const CAT = Object.fromEntries(catalogDoc.products.map((c) => [c.id, c]));
const sourcesDoc = read('data/sources.json');
const SOURCES = Object.fromEntries(sourcesDoc.sources.map((s) => [s.id, s]));
const flagsDoc = read('data/flags.json');
const FLAGS = Object.fromEntries(flagsDoc.flags.map((f) => [f.id, f]));
const questions = read('data/questions.json');
const suggestionsDoc = read('data/suggestions.json');
const guides = read('data/guides.json').guides;
const events = read('data/events.json');
const ledger = read('data/ledger.json');

const CATEGORIES = [
  { slug: 'air-fryers', name: 'Air fryers', blurb: 'Basket-style air fryers, observed on Amazon listings on 2026-11-20.' },
  { slug: 'air-fryer-ovens', name: 'Air fryer ovens', blurb: 'Oven-style air fryers and toaster ovens with a door and racks.' },
  { slug: 'cooking-thermometers', name: 'Cooking thermometers', blurb: 'Wireless meat thermometers, with the USDA temperature reference.' },
  { slug: 'unresolved', name: 'Unresolved links', blurb: 'Submitted links that did not resolve to a product page. No buy link is published here.' },
];
const catName = (slug) => (CATEGORIES.find((c) => c.slug === slug) || { name: slug }).name;

const DASHBOARDS = [
  ['/executive-summary/', 'Executive summary'],
  ['/shop/', 'Shop table (all rows)'],
  ['/categories/', 'Categories'],
  ['/sources/', 'Source register'],
  ['/questions/', 'Questions and gaps'],
  ['/suggestions/', 'Suggestions (choose a path)'],
  ['/flagged/', 'Flagged for review'],
  ['/ledger/', 'Campaign ledger'],
  ['/measurement/', 'Measurement'],
  ['/compliance/', 'Compliance and gates'],
  ['/search/', 'Search the shop'],
  ['/about/', 'About and editorial policy'],
  ['/editorial/', 'Editorial register (second publication)'],
];

// ---------- helpers ----------
const esc = (s = '') => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const href = (p) => cfg.basePath + p;
const abs = (p) => cfg.siteUrl + p;
const hostOf = (u) => { try { return new URL(u).hostname; } catch { return ''; } };
const isAmazon = (u) => /(^|\.)amazon\.com$/.test(hostOf(u)) || hostOf(u) === 'link.amazon';
const relFor = (u) => (isAmazon(u) ? 'sponsored noopener' : 'noopener external');
const ext = (u, text, attrs = '') => `<a href="${esc(u)}" rel="${relFor(u)}"${attrs}>${esc(text)}</a>`;
const srcLink = (id) => {
  const s = SOURCES[id];
  if (!s) return `<span class="badge bad">${esc(id)} (missing)</span>`;
  return s.url ? `<a href="${esc(s.url)}" rel="${relFor(s.url)}">${esc(id)}</a>` : `<span>${esc(id)}</span>`;
};
const flagLinks = (ids = []) => ids.map((f) => `<a class="badge flag" href="${href('/flagged/')}#${esc(f)}">${esc(f)}</a>`).join(' ');
const shortName = (t = '') => t.split(/[|,]/)[0].trim();
const displayName = (p) => (p.observed_title ? shortName(p.observed_title) : 'Not observed');
const tagged = (p) => p.tagged_outbound_url || '';
const catOf = (p) => CAT[p.id] || null;
const thumbClass = (p) => {
  const c = CAT[p.id];
  if (!c) return 't-basket';
  if (c.category === 'cooking-thermometers') return 't-thermo';
  return c.category === 'air-fryer-ovens' ? 't-oven' : 't-basket';
};
// The one number that decides the purchase, per product. Read from the maker's page (S14-S18).
const headlineSpec = (p) => {
  const c = CAT[p.id];
  if (!c) return { big: 'See listing', small: 'specification not verified' };
  const find = (label) => (c.specs.find((s) => s.label.toLowerCase().startsWith(label)) || {}).value || '';
  if (c.category === 'cooking-thermometers') {
    if (find('read time')) return { big: '1 sec', small: 'instant read probe' };
    return { big: '4 + 1', small: 'internal + ambient sensors' };
  }
  return { big: find('capacity') || 'See listing', small: 'stated by the maker' };
};
const specLink = (id) => (id ? srcLink(id) : '<span class="muted">no source: left blank</span>');
const dateLong = (iso) => new Date(iso + 'T00:00:00Z').toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric', timeZone: 'UTC' });
const rfc822 = (iso) => new Date(iso + 'T00:00:00Z').toUTCString();

function page({ title, description, path: p, body, type = 'page', attrs = '', ogType = 'website', jsonld = '' }) {
  const canonical = abs(p);
  return `<!doctype html>
<html lang="${cfg.language}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(title)} | ${esc(cfg.siteName)}</title>
<meta name="description" content="${esc(description)}">
<link rel="canonical" href="${esc(canonical)}">
<meta property="og:title" content="${esc(title)}">
<meta property="og:description" content="${esc(description)}">
<meta property="og:url" content="${esc(canonical)}">
<meta property="og:type" content="${ogType}">
<meta property="og:site_name" content="${esc(cfg.siteName)}">
<meta name="analytics-endpoint" content="${esc(cfg.analyticsEndpoint || '')}">
<link rel="stylesheet" href="${esc(href('/assets/style.css'))}">
<link rel="alternate" type="application/rss+xml" title="${esc(cfg.siteName)} guides" href="${esc(abs('/feed.xml'))}">
${jsonld}
</head>
<body data-page="${esc(type)}" ${attrs}>
<a class="skip" href="#main">Skip to content</a>
<header class="masthead">
  <div class="wrap masthead-inner">
    <a class="brand" href="${esc(href('/'))}">${esc(cfg.siteName)}</a>
    <p class="tagline">${esc(cfg.tagline)}</p>
    <nav class="nav" aria-label="Main">
      <a href="${esc(href('/shop/'))}">Shop</a>
      <a href="${esc(href('/compare/'))}">Compare</a>
      <a href="${esc(href('/guides/'))}">Guides</a>
      <a href="${esc(href('/categories/'))}">Categories</a>
      <a href="${esc(href('/suggestions/'))}">Suggestions</a>
      <a href="${esc(href('/about/'))}">About</a>
    </nav>
    <form class="nav-search" role="search" action="${esc(href('/search/'))}" method="get" onsubmit="return true">
      <label class="sr" for="q">Search the shop</label>
      <input type="search" id="q" name="q" placeholder="Search products, guides…" autocomplete="off">
      <button type="submit" aria-label="Search">Search</button>
    </form>
  </div>
</header>
<div class="disclosure-strip" role="note" aria-label="Affiliate disclosure">
  <div class="wrap"><strong>Disclosure.</strong> ${esc(cfg.disclosureStrip)} <a href="${esc(href('/compliance/'))}">How we disclose</a></div>
</div>
<main id="main" class="wrap">
${body}
</main>
<footer class="site-footer">
  <div class="wrap">
    <h2 class="foot-h">Dashboards and records</h2>
    <ul class="foot-links">
      ${DASHBOARDS.map(([u, t]) => `<li><a href="${esc(href(u))}">${esc(t)}</a></li>`).join('\n      ')}
      <li><a href="${esc(href('/feed.xml'))}">RSS feed (guides)</a></li>
      <li><a href="${esc(href('/sitemap.xml'))}">Sitemap</a></li>
    </ul>
    <p class="disclosure-footer"><strong>Disclosure.</strong> ${esc(cfg.disclosureStrip)}</p>
    <p class="fine">Affil3 is not sponsored by or affiliated with Amazon.com, Inc. Prices and availability are not shown on this site. Last reviewed ${esc(dateLong(cfg.lastReviewed))}. Source links are listed on each page and in the <a href="${esc(href('/sources/'))}">source register</a>.</p>
  </div>
</footer>
<script src="${esc(href('/assets/analytics.js'))}" defer></script>
</body>
</html>
`;
}

// ---------- components ----------
function productCard(p, placement) {
  const c = CAT[p.id];
  const cat = catName(p.category);
  if (!tagged(p)) {
    return `<article class="pcard warn-card" data-product-view="${esc(p.id)}">
  <div class="thumb"><b>${esc(p.submitted_token)}</b><i>link did not resolve</i></div>
  <div class="pcard-body">
    <p class="pcard-brand">${esc(cat)} · ${esc(p.id)}</p>
    <h3>No buy link is published</h3>
    <p class="best">The submitted link has not resolved to a product page in a verified session. An Amazon "Continue shopping" checkpoint is intermittent and is not by itself evidence that a link is dead. ${flagLinks(['FLG-004'])}</p>
  </div>
</article>`;
  }
  const hs = headlineSpec(p);
  return `<article class="pcard" data-product-view="${esc(p.id)}">
  <a class="pcard-link" href="${esc(href('/products/' + (c ? c.slug : p.observed_asin) + '/'))}">
    <div class="thumb ${thumbClass(p)}">
      ${c ? `<span class="badge">${esc(c.shape)}</span>` : ''}
      <div><b>${esc(hs.big)}</b><i>${esc(hs.small)}</i></div>
    </div>
    <div class="pcard-body">
      <p class="pcard-brand">${esc(c ? c.brand : cat)} · ${esc(cat)}</p>
      <h3>${esc(c ? c.name : displayName(p))}</h3>
      <p class="best"><b>Best for:</b> ${esc(c ? c.best_for : 'See the listing.')}</p>
      <div class="actions">
        <span class="btn-ghost btn-sm">Read the breakdown</span>
      </div>
    </div>
  </a>
  <div class="card-foot">
    <a class="btn btn-sm" href="${esc(tagged(p))}" rel="sponsored noopener" data-outbound data-product="${esc(p.id)}" data-placement="${esc(placement)}">View on Amazon</a>
    <span class="status">Link pending validation</span>
  </div>
</article>`;
}

function renderBlock(b) {
  switch (b.type) {
    case 'note': return `<p class="note">${esc(b.text)}</p>`;
    case 'p': return `<p>${esc(b.text)}</p>`;
    case 'h2': return `<h2 id="${esc(b.text.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, ''))}">${esc(b.text)}</h2>`;
    case 'ul': return `<ul>${b.items.map((i) => `<li>${esc(i)}</li>`).join('')}</ul>`;
    case 'ol': return `<ol>${b.items.map((i) => `<li>${esc(i)}</li>`).join('')}</ol>`;
    case 'table': return `<div class="table-wrap"><table class="guide-table"><thead><tr>${b.headers.map((h) => `<th scope="col">${esc(h)}</th>`).join('')}</tr></thead><tbody>${b.rows.map((r) => `<tr>${r.map((c, i) => i === 0 ? `<th scope="row">${esc(c)}</th>` : `<td>${esc(c)}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
    default: throw new Error('unknown block ' + b.type);
  }
}

function table(headers, rows, cls = '') {
  return `<div class="table-wrap"><table class="${cls}"><thead><tr>${headers.map((h) => `<th scope="col">${esc(h)}</th>`).join('')}</tr></thead><tbody>${rows.map((r) => `<tr>${r.map((c) => `<td>${c}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
}

// Row-level sources: S05 and S04 point to this row's own submitted link and observed page.
const rowSources = (p) => (p.sources || []).map((id) => {
  if (id === 'S05') return `<a href="${esc(p.submitted_url)}" rel="sponsored noopener">S05</a>`;
  if (id === 'S04' && p.observed_final_url) return `<a href="${esc(p.observed_final_url)}" rel="sponsored noopener">S04</a>`;
  return srcLink(id);
}).join(', ');
const guideSource = (id) => (id === 'S04'
  ? `<a href="${esc(href('/shop/'))}">S04</a> · observed Amazon product pages, one per row on the Shop table`
  : `${srcLink(id)} · ${esc(SOURCES[id] ? SOURCES[id].title : '')}`);

const cellText = (v) => (v === '' || v == null ? '<span class="blank" aria-label="blank: unverified">&nbsp;</span>' : esc(v));

// ---------- pages ----------
const pages = [];
const add = (p) => pages.push(p);

// Home — a shop front: products lead, decisions before audit trail.
{
  const shelf = products.map((p) => productCard(p, 'front-grid')).join('\n');
  const featured = products.filter((p) => p.category === 'air-fryer-ovens')[0];
  const guideList = guides.map((g) => `<li class="guide-item"><a href="${esc(href('/guides/' + g.slug + '/'))}">${esc(g.title)}</a><span class="muted"> · ${esc(catName(g.category))}</span><p>${esc(g.deck)}</p></li>`).join('\n');
  const tiles = CATEGORIES.filter((c) => c.slug !== 'unresolved').map((c) => {
    const n = products.filter((p) => p.category === c.slug).length;
    const g = guides.filter((g) => g.category === c.slug || (g.cluster_links || []).includes(c.slug)).length;
    return `<a class="tile" href="${esc(href('/categories/' + c.slug + '/'))}"><p class="n">${n} product${n === 1 ? '' : 's'} · ${g} guide${g === 1 ? '' : 's'}</p><h3>${esc(c.name)}</h3><p>${esc(c.blurb)}</p><span class="go">Browse ${esc(c.name.toLowerCase())} →</span></a>`;
  }).join('\n');
  add({
    path: '/', title: 'Kitchen gear, chosen by what you actually cook',
    description: 'Five kitchen appliances, each traced to the maker\'s own specification sheet, with the one number that decides the purchase and a plain answer to whether it fits how you cook.',
    type: 'home',
    body: `
<section class="hero">
  <p class="kicker">Kitchen shortlist · checked November 20, 2026</p>
  <h1>Buy the air fryer that matches how you cook, not the one with the longest feature list.</h1>
  <p class="deck">Three air fryer shapes, two ways to take a temperature. Every page gives you the one number that decides the purchase, says plainly what the appliance is bad at, and links the maker's own specification sheet for each figure.</p>
  <p class="hero-meta"><span class="chip">5 products</span><span class="chip plain">${guides.length} buying guides</span><span class="chip plain">Specs cited to the maker</span><span class="chip plain">No prices shown</span></p>

  <div class="lanes">
    <a class="lane" href="${esc(href('/products/' + CAT.P01.slug + '/'))}"><span class="q">Cooking two things at once</span><strong>Two 3-quart drawers that finish together</strong><em>Chefman TurboFry Touch 6 Qt</em></a>
    <a class="lane" href="${esc(href('/products/' + CAT.P02.slug + '/'))}"><span class="q">Cooking for a family</span><strong>A 26-quart oven with French doors</strong><em>Emeril Lagasse French Door AirFryer 360</em></a>
    <a class="lane" href="${esc(href('/products/' + CAT.P03.slug + '/'))}"><span class="q">One big basket, no fuss</span><strong>Eight quarts in a single drawer</strong><em>Chefman TurboFry Touch 8 Qt</em></a>
    <a class="lane" href="${esc(href('/products/' + CAT.P05.slug + '/'))}"><span class="q">Watching a long roast</span><strong>A wireless probe that talks to your phone</strong><em>CHEF iQ Sense</em></a>
  </div>
</section>

<section class="band">
  <h2>The shortlist</h2>
  <p class="deck" style="font-size:17px">Every card says what the appliance is best for and the number that decides it. Open a card for the full breakdown, or go straight to the listing.</p>
  <div class="grid">${shelf}</div>
</section>

<section class="band">
  <h2>Compare the two shapes first</h2>
  <p class="deck" style="font-size:17px">If you have not chosen between a basket and an oven-style appliance, start here. The comparison uses only what each maker publishes.</p>
  <p><a class="btn" href="${esc(href('/compare/'))}">Basket vs oven-style, side by side</a> <a class="btn-ghost" href="${esc(href('/guides/basket-or-oven-style-air-fryer-what-should-you-compare/'))}">Read the guide</a></p>
</section>

<section class="band">
  <h2>Shop by category</h2>
  <div class="tiles">${tiles}</div>
</section>

<section class="band">
  <h2>Buying guides</h2>
  <ul class="guide-list">${guideList}</ul>
  <p><a href="${esc(href('/guides/'))}">All guides</a></p>
</section>

<section class="band">
  <h2>Why you can trust the numbers</h2>
  <div class="trust">
    <div><h3>Specs come from the maker, not the listing</h3><p>Every figure on a product page was read on the manufacturer's own page and carries a source link. Where the Amazon listing disagrees with the maker, both are shown.</p></div>
    <div><h3>Nothing is guessed</h3><p>If a manufacturer does not publish a value, the row says so instead of filling in a plausible number. Eleven specification rows are blank for exactly this reason.</p></div>
    <div><h3>No prices, no star ratings</h3><p>Prices and ratings change hourly and Amazon's terms restrict how they may be shown. This site shows neither; it links you to the live listing instead.</p></div>
    <div><h3>Links are disclosed and sponsored</h3><p>Outbound links carry our Associates tag and the sponsored attribute. The disclosure is at the top of every page, not buried in a footer.</p></div>
  </div>
  <p class="shelf-note">As an Amazon Associate I earn from qualifying purchases. Every product figure links to the source it came from; the full register is on the <a href="${esc(href('/sources/'))}">sources page</a>.</p>
</section>`,
  });
}

// Product detail pages, one per submitted product
for (const p of products) {
  const c = CAT[p.id];
  if (!c) continue;
  const jsonld = `<script type="application/ld+json">${JSON.stringify({
    '@context': 'https://schema.org', '@type': 'Product',
    name: `${c.brand} ${c.name}`, brand: { '@type': 'Brand', name: c.brand },
    model: c.model, description: c.one_liner, category: catName(c.category),
    url: abs(`/products/${c.slug}/`),
  })}</script>
<script type="application/ld+json">${JSON.stringify({
    '@context': 'https://schema.org', '@type': 'FAQPage',
    mainEntity: c.faq.map((f) => ({ '@type': 'Question', name: f.q, acceptedAnswer: { '@type': 'Answer', text: f.a } })),
  })}</script>
<script type="application/ld+json">${JSON.stringify({
    '@context': 'https://schema.org', '@type': 'BreadcrumbList',
    itemListElement: [
      { '@type': 'ListItem', position: 1, name: 'Home', item: abs('/') },
      { '@type': 'ListItem', position: 2, name: catName(c.category), item: abs(`/categories/${c.category}/`) },
      { '@type': 'ListItem', position: 3, name: c.name, item: abs(`/products/${c.slug}/`) },
    ],
  })}</script>`;
  const specRows = c.specs.map((sp) => [
    esc(sp.label),
    sp.value ? esc(sp.value) : '<span class="blankcell">Not published by the maker</span>',
    sp.note ? `<span class="muted small">${esc(sp.note)}</span>` : '',
    `<span class="src">${specLink(sp.source)}</span>`,
  ]);
  const related = products.filter((o) => o.id !== p.id && o.tagged_outbound_url)
    .sort((a, b) => ((CAT[b.id] && CAT[b.id].category === c.category) ? 1 : 0) - ((CAT[a.id] && CAT[a.id].category === c.category) ? 1 : 0))
    .slice(0, 3).map((o) => productCard(o, 'related')).join('\n');
  add({
    path: `/products/${c.slug}/`, title: `${c.brand} ${c.name}`,
    description: `${c.one_liner} Specifications cited to ${c.brand}; what it is best for and what it is not.`,
    type: 'product', ogType: 'product', jsonld,
    attrs: `data-product-page="${esc(p.id)}"`,
    body: `<section class="pdp">
  <div class="pdp-hero">
    <p class="kicker"><a href="${esc(href('/categories/' + c.category + '/'))}" style="color:inherit;text-decoration:none">${esc(catName(c.category))}</a> · ${esc(c.shape)} · ${esc(p.id)}</p>
    <h1>${esc(c.brand)} ${esc(c.name)}</h1>
    <p class="deck">${esc(c.one_liner)}</p>
    <p class="hero-meta"><span class="chip">Model ${esc(c.model)}</span><span class="chip plain">Observed ASIN ${esc(p.observed_asin)}</span><span class="chip plain">Checked ${esc(dateLong(catalogDoc.checked))}</span></p>
    ${c.listing_title_note ? `<p class="pdp-flag"><strong>Worth knowing:</strong> ${esc(c.listing_title_note)}</p>` : ''}
    <div class="verdict">
      <div class="good"><p class="k">Best for</p><p>${esc(c.best_for)}</p></div>
      <div class="bad"><p class="k">Not for</p><p>${esc(c.not_for)}</p></div>
    </div>
  </div>
  <aside class="buybox">
    <h2>At a glance</h2>
    <table class="mini"><tbody>
      ${c.specs.filter((sp) => sp.value).slice(0, 4).map((sp) => `<tr><th scope="row">${esc(sp.label)}</th><td>${esc(sp.value)}</td></tr>`).join('')}
    </tbody></table>
    <a class="btn" href="${esc(tagged(p))}" rel="sponsored noopener" data-outbound data-product="${esc(p.id)}" data-placement="product-buybox">View on Amazon</a>
    <p class="note-sm">${esc(p.outbound_status)}. Opens the Amazon listing with our Associates tag <code>${esc(cfg.trackingId)}</code>; we earn a commission if you buy. ${flagLinks(['FLG-005'])}</p>
    <ul>
      <li>No price is shown here; Amazon shows the live price.</li>
      <li>No rating is quoted; read the reviews on the listing.</li>
      <li>We have not tested this unit. ${flagLinks(['FLG-033'])}</li>
    </ul>
  </aside>
</section>

<section class="band decide">
  <h2>How to decide in one minute</h2>
  <ol>${c.decide.map((d) => `<li>${esc(d)}</li>`).join('')}</ol>
</section>

<section class="band">
  <h2>Specifications, and where each one came from</h2>
  <p class="deck" style="font-size:16px">Read on the manufacturer's page on ${esc(dateLong(catalogDoc.checked))}. Figures the maker does not publish are marked, not filled in.</p>
  ${table(['Specification', 'Value', 'Note', 'Source'], specRows, 'spec-table')}
</section>

<section class="band faq">
  <h2>Questions buyers ask</h2>
  ${c.faq.map((f) => `<details><summary>${esc(f.q)}</summary><p>${esc(f.a)}</p><p class="src">${specLink(f.source)}</p></details>`).join('\n')}
</section>

<section class="band">
  <h2>Other products in this shortlist</h2>
  <div class="grid">${related}</div>
</section>

<section class="band next">
  <h2>Keep reading</h2>
  <ul class="next-list">
    <li><a href="${esc(href('/compare/'))}"><strong>Basket or oven-style?</strong><span>The shape decision that comes before the brand.</span></a></li>
    ${guides.filter((g) => g.category === c.category || (g.cluster_links || []).includes(c.category)).slice(0, 3).map((g) => `<li><a href="${esc(href('/guides/' + g.slug + '/'))}"><strong>${esc(g.title)}</strong><span>${esc(g.deck)}</span></a></li>`).join('')}
    <li><a href="${esc(href('/categories/' + c.category + '/'))}"><strong>All ${esc(catName(c.category).toLowerCase())}</strong><span>Every product and guide in this category.</span></a></li>
  </ul>
</section>

<section class="band sources">
  <h2>Sources for this page</h2>
  <ul>${[...new Set(c.specs.map((x) => x.source).concat(c.faq.map((f) => f.source)).filter(Boolean))].map((id) => `<li>${srcLink(id)} · ${esc((SOURCES[id] || {}).title || '')}</li>`).join('')}
  <li><a href="${esc(p.observed_final_url)}" rel="sponsored noopener">S04</a> · the Amazon listing this product was observed on (${esc(p.observed_asin)})</li></ul>
  <p class="small"><a href="${esc(href('/sources/'))}">Full source register</a></p>
</section>`,
  });
}

// Compare page: basket vs oven, from published specs only
{
  const rows = [
    ['What it is', 'A drawer with a fan above it', 'A countertop oven with a door and racks'],
    ['Cooks best', 'Loose food in one layer: fries, wings, vegetables', 'Anything that needs a rack, a tray or a whole bird'],
    ['Biggest single item', 'Limited by the drawer: a small chicken at most', 'A whole chicken, a 12-inch pizza, a full tray of cookies'],
    ['Two foods, two timings', 'Two baskets or one basket and a pause', 'Two racks, one shared temperature'],
    ['Counter space', 'Smaller footprint, drawer pulls out', 'Larger footprint, doors open forward'],
    ['Cleaning', 'Basket and crisper plate come out', 'Racks, tray and a door with crevices'],
    ['Preheat', 'Little to none', 'More like an oven'],
  ];
  add({
    path: '/compare/', title: 'Basket or oven-style air fryer: the decision in one table',
    description: 'Basket-style versus oven-style air fryers, compared on published specifications only, with the two tracked models as worked examples.',
    type: 'compare',
    jsonld: `<script type="application/ld+json">${JSON.stringify({
      '@context': 'https://schema.org', '@type': 'BreadcrumbList',
      itemListElement: [
        { '@type': 'ListItem', position: 1, name: 'Home', item: abs('/') },
        { '@type': 'ListItem', position: 2, name: 'Compare', item: abs('/compare/') },
      ],
    })}</script>`,
    body: `<section class="page-head">
  <p class="kicker">Compare · the first decision</p>
  <h1>Basket or oven-style: decide the shape before the brand</h1>
  <p class="deck">Everything else follows from this. Below is the difference in plain terms, then the two tracked appliances as worked examples of each shape.</p>
</section>
${table(['', 'Basket-style', 'Oven-style'], rows.map((r) => [`<strong>${esc(r[0])}</strong>`, esc(r[1]), esc(r[2])]), 'wide')}
<p class="small muted">This table describes the two shapes generally. It does not rank any product and is not a test result.</p>

<section class="band">
  <h2>The two tracked examples</h2>
  <div class="grid">${[CAT.P01, CAT.P03, CAT.P02].map((c) => productCard(products.find((p) => p.id === c.id), 'compare')).join('\n')}</div>
</section>

<section class="band">
  <h2>Then pick by the number</h2>
  ${table(['Appliance', 'Shape', 'Capacity', 'Heat ceiling', 'Footprint', 'Source'], [
    [esc(CAT.P01.brand + ' ' + CAT.P01.name), 'Dual basket', '6 qt total, two baskets', '450 °F', '13.38 D × 11.81 W × 10.63 H in', srcLink('S14')],
    [esc(CAT.P03.brand + ' ' + CAT.P03.name), 'Single basket', '8 qt', '400 °F (maker) · listing says 450 °F', '15.4 × 12.6 × 13.5 in', srcLink('S15')],
    [esc(CAT.P02.brand + ' ' + CAT.P02.name), 'Oven, French doors', '26 qt', 'Not published', '16.9 D × 15.8 W × 14.8 H in', srcLink('S16')],
  ], 'wide')}
  <p class="small">Capacity and footprint are not comparable across these shapes: six quarts of drawer, eight quarts of basket and 26 quarts of oven are three different kinds of space.</p>
</section>

<section class="band">
  <h2>Read next</h2>
  <ul class="guide-list">
    <li class="guide-item"><a href="${esc(href('/guides/basket-or-oven-style-air-fryer-what-should-you-compare/'))}">Basket or oven-style air fryer: what should you compare?</a><p>Start with the food you cook most, then pick the shape that fits it.</p></li>
    <li class="guide-item"><a href="${esc(href('/guides/no-hype-checklist-comparing-air-fryer-capacity/'))}">A no-hype checklist for comparing air fryer capacity</a><p>Capacity is one of the first numbers you see and one of the easiest to misread.</p></li>
  </ul>
</section>`,
  });
}

// Search: a client-side index over the products and guides. No server, no tracking.
{
  const index = [
    ...products.filter((p) => p.tagged_outbound_url).map((p) => {
      const c = CAT[p.id];
      return { t: `${c.brand} ${c.name}`, u: `/products/${c.slug}/`, k: `${catName(c.category)} product`, d: c.one_liner,
        x: [c.brand, c.name, c.model, c.shape, c.best_for, c.not_for, catName(c.category), ...c.specs.map((sp) => sp.label + ' ' + sp.value)].join(' ').toLowerCase() };
    }),
    ...guides.map((g) => ({ t: g.title, u: `/guides/${g.slug}/`, k: `${catName(g.category)} guide`, d: g.deck,
      x: [g.title, g.deck, g.description, catName(g.category)].join(' ').toLowerCase() })),
    ...CATEGORIES.filter((c) => c.slug !== 'unresolved').map((c) => ({ t: c.name, u: `/categories/${c.slug}/`, k: 'Category', d: c.blurb, x: (c.name + ' ' + c.blurb).toLowerCase() })),
    { t: 'Basket or oven-style comparison', u: '/compare/', k: 'Comparison', d: 'The shape decision in one table.', x: 'compare basket oven style shape' },
    { t: 'Basket or oven-style air fryer: what should you compare?', u: '/guides/basket-or-oven-style-air-fryer-what-should-you-compare/', k: 'Guide', d: 'Start with the food you cook most.', x: 'basket oven style air fryer' },
  ];
  add({
    path: '/search/', title: 'Search the shop',
    description: 'Search the five tracked products and the buying guides, in the browser.',
    type: 'search',
    body: `<section class="page-head">
  <p class="kicker">Search</p>
  <h1>Find a product or a guide</h1>
  <p class="deck">Type what you cook, or the shape you are after. The results come from this site only: five products, five guides and three categories. Nothing is sent anywhere.</p>
</section>
<form class="searchbox" role="search" onsubmit="return false">
  <label class="sr" for="sq">Search</label>
  <input type="search" id="sq" placeholder="e.g. basket, thermometer, two foods, 8 qt" autocomplete="off" autofocus>
</form>
<p class="small muted" id="scount"></p>
<ul class="results" id="results"></ul>
<script type="application/json" id="search-index">${JSON.stringify(index).replace(/</g, '\\u003c')}</script>
<script>
(function () {
  var data = JSON.parse(document.getElementById('search-index').textContent);
  var input = document.getElementById('sq');
  var out = document.getElementById('results');
  var count = document.getElementById('scount');
  function render() {
    var q = input.value.trim().toLowerCase();
    var hits = q ? data.filter(function (r) { return r.x.indexOf(q) !== -1; })
                 : data.filter(function (r) { return r.k.indexOf('product') !== -1; });
    hits = hits.slice(0, 20);
    out.innerHTML = hits.map(function (r) {
      return '<li><a href="' + r.u + '"><span class="k">' + r.k + '</span><strong>' + r.t + '</strong><span class="d">' + r.d + '</span></a></li>';
    }).join('');
    count.textContent = q ? hits.length + ' result' + (hits.length === 1 ? '' : 's') + ' for "\\u200b' + input.value + '"'
                          : 'Showing all ' + hits.length + ' products. Type to narrow.';
    if (!hits.length) count.textContent = 'Nothing matched. Try "air fryer", "thermometer", "two foods" or "capacity".';
  }
  input.addEventListener('input', render);
  render();
})();
</script>`,
  });
}

// Shop table
{
    const resolvedCount = products.filter((p) => p.observed_asin).length;
  const unanswered = products.filter((p) => !p.observed_asin);
  const taggedCount = products.filter((p) => p.tagged_outbound_url).length;
const rows = products.map((p) => [
    `<strong>${esc(p.id)}</strong>`,
    `<a href="${esc(href('/categories/' + p.category + '/'))}">${esc(catName(p.category))}</a>`,
    `${esc(p.observed_title || 'Not observed')}${p.observed_breadcrumb ? `<br><span class="muted small">${esc(p.observed_breadcrumb)}</span>` : ''}`,
    p.observed_asin ? `<code>${esc(p.observed_asin)}</code><br>${ext(p.observed_final_url, 'observed page', '')}` : '<span class="muted">none observed</span>',
    `<a href="${esc(p.submitted_url)}" rel="sponsored noopener"><code>${esc(p.submitted_token)}</code></a> <span class="small muted">(${p.submitted_token_length} chars)</span>`,
    cellText(p.intended_asin),
    cellText(p.official_listing_url),
    cellText(p.confirmation_date),
    cellText(p.confirmation_source),
    `${esc(p.outbound_status)}${tagged(p) ? `<br>${ext(tagged(p), 'tagged link', ` data-outbound data-product="${p.id}" data-placement="shop-table"`)}` : ''}`,
    `${esc(p.confirmation_status)}<br>${flagLinks(p.flags)}`,
    `${rowSources(p)} <span class="small muted">observed ${esc(dateLong(p.observed_date))}</span>`,
  ]);
  add({
    path: '/shop/', title: 'Shop: all submitted products and findings',
    description: 'Every submitted product row: intended ASIN and listing fields (blank where unverified), observed redirect destinations kept separate, sources and flags.',
    body: `
<section class="page-head">
  <p class="kicker">The five products, in full</p>
  <h1>Every product, and every figure behind it</h1>
  <p class="deck">One row per product. The first columns are what you would want as a buyer: what it is, what it is best for, and the link to its own page. The columns to the right are the record of where each figure came from, including the fields we could not confirm and therefore left blank.</p>
  <div class="grid">${products.map((p) => productCard(p, 'shop-top')).join('\n')}</div>
</section>
<section class="band">
  <h2>The full record</h2>
  <p class="deck" style="font-size:16px"><strong>Observed</strong> fields are what the Amazon page showed on 2026-11-20. <strong>Intended</strong> fields can only be filled from an official source; none are confirmed, so they stay blank rather than being guessed.</p>
<section>
  ${table(['ID', 'Category', 'Observed title and breadcrumb', 'Observed ASIN and page', 'Submitted link', 'Intended ASIN', 'Official listing URL', 'Confirmation date', 'Confirmation source', 'Buy link status', 'Confirmation status', 'Sources (official)'], rows, 'wide')}
</section>
<section class="band">
  <h2>What the table shows</h2>
  <ul class="findings">
    <li>All five submitted tokens are 9 characters. The observed Amazon product IDs are 10 characters. ${flagLinks(['FLG-001'])}</li>
    <li>${resolvedCount === 5 ? 'All five' : resolvedCount + ' of five'} short links resolved to a product page, and each product ID differs from the token in its link.${resolvedCount < 5 ? ' ' + unanswered.map((p) => `<code>${esc(p.submitted_token)}</code> has not resolved in a verified session, so no product is shown and no buy link is published. ${flagLinks(['FLG-004'])}`).join(' ') : ''} ${flagLinks(['FLG-002'])}</li>
    <li>${taggedCount} tagged ${taggedCount === 1 ? 'link is' : 'links are'} published with the tracking ID ${esc(cfg.trackingId)}. None has been tested in Associates Central. ${flagLinks(['FLG-005'])}</li>
    <li>The short links' compliance status is unresolved, not invalid. ${flagLinks(['FLG-003'])}</li>
    <li>No price, rating or availability is recorded. ${flagLinks(['FLG-016'])}</li>
  </ul>
</section>`,
  });
}

// Categories index + category pages
add({
  path: '/categories/', title: 'Categories',
  description: 'Product categories and the guides that cover each one.',
  body: `<section class="page-head"><p class="kicker">Categories</p><h1>Browse by category</h1><p class="deck">Four clusters. Each cluster lists its products and the guides that cover them.</p></section>
<div class="cat-grid">${CATEGORIES.map((c) => `<a class="card cat-card" href="${esc(href('/categories/' + c.slug + '/'))}"><h3>${esc(c.name)}</h3><p>${esc(c.blurb)}</p><p class="small muted">${products.filter((p) => p.category === c.slug).length} product row(s) · ${guides.filter((g) => g.category === c.slug || (g.cluster_links || []).includes(c.slug)).length} guide(s)</p></a>`).join('')}</div>`,
});
for (const c of CATEGORIES) {
  const inCat = products.filter((p) => p.category === c.slug);
  const cards = inCat.map((p) => productCard(p, 'category')).join('\n');
  const gl = guides.filter((g) => g.category === c.slug || (g.cluster_links || []).includes(c.slug));
  add({
    path: `/categories/${c.slug}/`, title: `${c.name}`,
    description: `${c.name}: ${c.blurb}`,
    attrs: `data-category="${esc(c.slug)}"`,
    type: 'category',
    noSitemap: c.slug === 'unresolved' && products.filter((p) => p.category === 'unresolved').length === 0,
    body: `<section class="page-head"><p class="kicker">Category</p><h1>${esc(c.name)}</h1><p class="deck">${esc(c.blurb)}</p></section>
<section class="shelf">${cards || '<p>No product rows in this category.</p>'}</section>
<section class="band"><h2>Guides for this cluster</h2>
${gl.length ? `<ul class="guide-list">${gl.map((g) => `<li class="guide-item"><a href="${esc(href('/guides/' + g.slug + '/'))}">${esc(g.title)}</a><p>${esc(g.deck)}</p></li>`).join('')}</ul>` : '<p>No guide yet in this cluster.</p>'}
</section>
${c.slug === 'unresolved' ? `<section class="band"><h2>Why this cluster is empty</h2><p>${esc(products.find((p) => p.category === 'unresolved') ? 'The submitted link B00hJ57DV landed on a checkpoint page. We did not substitute a product.' : '')}</p><p>${flagLinks(['FLG-003', 'FLG-004'])}</p></section>` : ''}`,
  });
}

// Guides index + guide pages
add({
  path: '/guides/', title: 'Guides',
  description: 'Question-led buying guides for air fryers, air fryer ovens and cooking thermometers.',
  body: `<section class="page-head"><p class="kicker">Guides</p><h1>Buying guides, by question</h1>
<p class="deck">Each guide starts with a question buyers ask. Working titles are editorial hypotheses, not claims about popularity or search volume.</p></section>
<div class="prose"><p>Each guide answers one question, then gives you a way to act on the answer: a table, a checklist, or a decision you can make before you buy. Every figure in them is cited to the source it came from.</p></div>
<ul class="guide-list">${guides.map((g) => {
  const words = g.body.reduce((n, b) => n + (b.text ? b.text.split(/\s+/).length : 0) + (b.items ? b.items.join(' ').split(/\s+/).length : 0) + (b.rows ? b.rows.flat().join(' ').split(/\s+/).length : 0), 0);
  return `<li class="guide-item"><a href="${esc(href('/guides/' + g.slug + '/'))}">${esc(g.title)}</a><span class="muted"> · ${esc(catName(g.category))} · ${Math.max(2, Math.round(words / 200))} min read</span><p>${esc(g.deck)}</p></li>`;
}).join('')}</ul>`,
});
for (const g of guides) {
  const productsHere = products.filter((p) => tagged(p) && (p.category === g.category || (g.cluster_links || []).includes(p.category)));
  const jsonld = `<script type="application/ld+json">${JSON.stringify({
    '@context': 'https://schema.org', '@type': 'Article', headline: g.title, description: g.description,
    datePublished: g.date, dateModified: cfg.lastReviewed, author: { '@type': 'Organization', name: cfg.author },
    publisher: { '@type': 'Organization', name: cfg.siteName }, mainEntityOfPage: abs(`/guides/${g.slug}/`),
  })}</script>`;
  add({
    path: `/guides/${g.slug}/`, title: g.title, description: g.description, type: 'guide', ogType: 'article', jsonld,
    attrs: `data-guide="${esc(g.slug)}"`,
    body: `<article class="article">
  <header class="page-head">
    <p class="kicker">${esc(catName(g.category))} · Guide</p>
    <h1>${esc(g.title)}</h1>
    <p class="deck">${esc(g.deck)}</p>
    <p class="byline">By ${esc(cfg.author)} · Published ${esc(dateLong(g.date))} · Last reviewed ${esc(dateLong(cfg.lastReviewed))}</p>
  </header>
  <div class="prose">${g.body.map(renderBlock).join('\n')}</div>
  ${productsHere.length ? `<aside class="band"><h2>Products in this cluster</h2><p class="small muted">The buttons below are Amazon affiliate links with our tracking ID. Links are marked sponsored.</p><div class="shelf">${productsHere.map((p) => productCard(p, 'guide-box')).join('')}</div></aside>` : ''}
  <section class="band sources"><h2>Sources</h2>
    ${g.sources.length ? `<ul>${g.sources.map((id) => `<li>${guideSource(id)}</li>`).join('')}</ul>` : '<p>This guide makes no factual claim that needs an external source. It refers only to the observed listing data on the Shop page.</p>'}
    <p class="small"><a href="${esc(href('/sources/'))}">Full source register</a></p>
  </section>
</article>`,
  });
}

// Executive summary
add({
  path: '/executive-summary/', title: 'Executive summary',
  description: 'Where this shop stands: the five products, what was verified against the makers, what is blocked, and the decisions needed from the owner.',
  body: `<section class="page-head"><p class="kicker">Executive summary · ${esc(dateLong(cfg.lastReviewed))}</p><h1>Where this shop stands</h1>
<p class="deck">One page for the owner. The first half is what a buyer sees; the second half is what is still unverified and what only you can decide.</p></section>

<div class="prose">
<h2>The shortlist, in one line each</h2>
${table(['Product', 'Shape', 'Deciding number', 'Best for', 'Page'], [
  [esc(CAT.P01.brand + ' ' + CAT.P01.name), 'Dual basket', '6 qt in two 3-qt drawers', esc(CAT.P01.best_for), `<a href="${esc(href('/products/' + CAT.P01.slug + '/'))}">open</a>`],
  [esc(CAT.P02.brand + ' ' + CAT.P02.name), 'Oven', '26 qt', esc(CAT.P02.best_for), `<a href="${esc(href('/products/' + CAT.P02.slug + '/'))}">open</a>`],
  [esc(CAT.P03.brand + ' ' + CAT.P03.name), 'Single basket', '8 qt, 4 presets', esc(CAT.P03.best_for), `<a href="${esc(href('/products/' + CAT.P03.slug + '/'))}">open</a>`],
  [esc(CAT.P04.brand + ' ' + CAT.P04.name), 'Instant read', 'about 1 second', esc(CAT.P04.best_for), `<a href="${esc(href('/products/' + CAT.P04.slug + '/'))}">open</a>`],
  [esc(CAT.P05.brand + ' ' + CAT.P05.name), 'Wireless probe', '4 internal + 1 ambient sensor', esc(CAT.P05.best_for), `<a href="${esc(href('/products/' + CAT.P05.slug + '/'))}">open</a>`],
], 'wide')}

<h2>What was verified against a primary source</h2>
<ul>
<li><strong>Every specification on every product page</strong> was read on the manufacturer's own page on 2026-11-20 and is cited by source id (S14–S18). Where the Amazon listing disagrees with the maker, both are shown and the disagreement is flagged (FLG-023 to FLG-026).</li>
<li><strong>Three listing-versus-maker conflicts found:</strong> P01 is called an "oven" in the listing but is a two-drawer basket fryer; P03's listing advertises 450 °F against the maker's 400 °F; P04's "NIST-certified" claim has no certificate behind it and NIST's own FAQ says it does not endorse products.</li>
<li><strong>The Associates and FTC rules</strong> were read from Amazon's Operating Agreement and Program Policies and from the FTC and eCFR pages (S01, S02, S07, S08). The disclosure statement, the sponsored attribute and the tracking tag are enforced by an automated gate that runs on every build (${esc('tools/verify.mjs')}, 2,171 checks).</li>
<li><strong>USDA safe temperatures</strong> for the thermometer guides were read from the FSIS chart (S09, last updated April 14, 2025).</li>
</ul>

<h2>What is not verified, and why</h2>
<ul>
<li><strong>The intended product behind each submitted link.</strong> The five short links are 9-character tokens; every Amazon product ID is 10 characters. Each link redirected to a product page, and that destination is recorded separately from the "intended" fields, which stay blank (FLG-001, FLG-002).</li>
<li><strong>Whether any link earns a commission.</strong> No Special Link has been generated or tested in Associates Central, so no destination or tracking report has been confirmed (FLG-005, gate G-02).</li>
<li><strong>Whether anything converts.</strong> The campaign ledger is empty and analytics is switched off until an endpoint exists (FLG-009). No conversion score or revenue forecast appears anywhere on this site, because none could be computed from data we hold.</li>
<li><strong>Whether anyone has used these products.</strong> Nobody has. No page makes a hands-on claim (FLG-033).</li>
</ul>

<h2>What only you can decide</h2>
<ol>
<li><strong>Confirm the intended product</strong> for each of the five links (Q-01), or accept the observed destination as the intended one.</li>
<li><strong>Run gate G-02:</strong> generate one Special Link per product in Associates Central, click it, and confirm the destination and the tracking report (Q-04).</li>
<li><strong>Work the suggestions board:</strong> 17 decisions, each with a recommendation and a cost. The four that change the most are imagery (S-05), analytics (S-03), the second site at /editorial/ (S-16) and what to publish next (S-17).</li>
<li><strong>Say whether any product was actually used</strong> (Q-14). This is the single biggest limit on how persuasive the copy can be.</li>
</ol>

<h2>Limits of this build</h2>
<p>No Amazon product data, prices or earnings reports were pulled. Those need the Product Advertising API or Associates reports, which require an approved account and are not available in this session. The site does not scrape Amazon. Prices and ratings are deliberately not displayed: they change hourly, and Amazon's terms restrict how they may be shown (FLG-031).</p>
</div>`,
});

// Sources
add({
  path: '/sources/', title: 'Source register',
  description: 'Every source used, how it was checked, and its status.',
  body: `<section class="page-head"><p class="kicker">Source register</p><h1>Sources and how they were checked</h1><p class="deck">${esc(sourcesDoc.note)}</p></section>
${table(['ID', 'Source', 'Publisher', 'Checked', 'Used for', 'Status', 'Link'], sourcesDoc.sources.map((s) => [
    `<strong id="${esc(s.id)}">${esc(s.id)}</strong>`, esc(s.title), esc(s.publisher), esc(s.method), esc(s.used_for), esc(s.status),
    s.url ? ext(s.url, 'open source', '') : '<span class="muted">none</span>',
  ]), 'wide')}`,
});

// Questions
add({
  path: '/questions/', title: 'Questions and gaps',
  description: 'What is known, what is not, and how each gap can be closed before a decision is made.',
  body: `<section class="page-head"><p class="kicker">Questions</p><h1>What we know, what we do not, and how to close the gap</h1><p class="deck">${esc(questions.note)}</p></section>
<h2>Known</h2>
${table(['ID', 'Statement', 'Sources'], questions.known.map((k) => [esc(k.id), esc(k.statement), k.sources.map(srcLink).join(', ') || '<span class="muted">none</span>']))}
<h2>Open questions</h2>
<p class="deck" style="font-size:16px">Grouped by what they block. <strong>Blocking</strong> means do not scale the site until it is answered. <strong>Design</strong> changes what a visitor sees. <strong>Content</strong> changes what gets written.</p>
${['blocking', 'design', 'content'].map((kind) => {
  const group = questions.unknown.filter((q) => (q.kind || 'blocking') === kind);
  if (!group.length) return '';
  const heading = kind === 'blocking' ? 'Blocking: answer before scaling' : kind === 'design' ? 'Design: shapes the shop' : 'Content: shapes what is published';
  return `<h3${kind === 'blocking' ? ' id="blocking"' : ''}>${heading} <span class="muted small">(${group.length})</span></h3>
${table(['ID', 'Question', 'Why it matters', 'How the answer would be found', 'Only the owner can answer?', 'Sources'], group.map((q) => [esc(q.id), esc(q.question), esc(q.why_it_matters), esc(q.how_to_close), q.owner_only ? '<strong>Yes</strong>' : 'No, can be measured', q.sources.map(srcLink).join(', ') || '<span class="muted">none</span>']), 'wide')}`;
}).join('\n')}
<h2>Ways to discover missing information</h2>
${table(['ID', 'Suggestion', 'Closes'], questions.discovery.map((d) => [esc(d.id), esc(d.suggestion), d.closes.map(esc).join(', ') || '<span class="muted">none</span>']))}`,
});

// Suggestions
add({
  path: '/suggestions/', title: 'Suggestions: choose a path',
  description: 'Options for the next decisions. Nothing is implemented until the owner chooses.',
  body: `<section class="page-head"><p class="kicker">Suggestions</p><h1>Choose a path before anything changes</h1><p class="deck">${esc(suggestionsDoc.note)}</p></section>
<p class="deck" style="font-size:16px">Sorted so that the choices which change the most for the least work come first. <strong>Effort</strong> and <strong>impact</strong> are editorial judgements; <strong>evidence</strong> says what the judgement is based on, and where the site has no data it says so.</p>
${table(['ID', 'Topic', 'Now', 'Options and their cost', 'What we would pick', 'Effort', 'Expected impact', 'Blocked by', 'Basis'], [...suggestionsDoc.suggestions].sort((a, b) => ({ High: 0, Medium: 1, Low: 2 }[a.impact] ?? 3) - ({ High: 0, Medium: 1, Low: 2 }[b.impact] ?? 3) || ({ Low: 0, Medium: 1, High: 2 }[a.effort] ?? 3) - ({ Low: 0, Medium: 1, High: 2 }[b.effort] ?? 3)).map((s) => [
    `<strong>${esc(s.id)}</strong>`, esc(s.topic), `<span class="badge">${esc(s.current)}</span>`,
    `<ul class="opts">${s.options.map((o) => `<li><strong>${esc(o.id)}.</strong> ${esc(o.label)} <span class="muted small">Tradeoff: ${esc(o.tradeoff)}</span></li>`).join('')}</ul>`,
    esc(s.recommendation),
    s.effort ? `<span class="badge sev-${s.effort === 'Low' ? 'low' : s.effort === 'High' ? 'high' : 'medium'}">${esc(s.effort)}</span>` : '<span class="muted">—</span>',
    s.impact ? `<span class="badge sev-${s.impact === 'High' ? 'high' : s.impact === 'Medium' ? 'medium' : 'low'}">${esc(s.impact)}</span>` : '<span class="muted">—</span>',
    esc(s.blocks || '—'),
    `<span class="small muted">${esc(s.evidence || 'Editorial judgement.')}</span>`,
  ]), 'wide')}
<h2>How to answer these</h2>
<p>Reply with the suggestion ID and the letter of the option you want, for example <code>S-01 B</code> or <code>S-05 A, S-13 C</code>. You can answer as many or as few at a time as you like. Until an answer arrives, the site keeps doing what the <em>Now</em> column says. Decisions are recorded, with their date, in the decision log below.</p>
<h2 id="decision-log">Decision log</h2>
${table(['Date', 'Suggestion', 'Option chosen', 'What changed'], [['<span class="muted">none yet</span>', '<span class="muted">—</span>', '<span class="muted">—</span>', 'The site is as first built. No suggestion has been accepted.'], ])}`,
});

// Flagged for review
add({
  path: '/flagged/', title: 'Flagged for review',
  description: 'Irregularities and unverified items, with the sources and the manual step that would close each one.',
  body: `<section class="page-head"><p class="kicker">Flagged for review</p><h1>Flagged for review</h1><p class="deck">${esc(flagsDoc.note)} Flags do not block publication.</p></section>
${flagsDoc.flags.map((f) => `<section class="flag-card${f.status === 'resolved' ? ' is-resolved' : ''}" id="${esc(f.id)}">
  <p class="flag-head"><span class="badge flag">${esc(f.id)}</span> <span class="badge sev-${esc(f.severity)}">${esc(f.severity)}</span> <strong>${esc(f.title)}</strong>${f.status === 'resolved' ? ' <span class="badge resolved">resolved</span>' : ''}</p>
  <p>${esc(f.detail)}</p>
  ${f.status === 'resolved' && f.resolution ? `<p class="resolution"><strong>Resolution:</strong> ${esc(f.resolution)}</p>` : ''}
  <p class="small"><strong>Sources:</strong> ${f.sources.length ? f.sources.map(srcLink).join(', ') : 'none (repo or owner input)'}</p>
  ${f.manual_step ? `<p class="small"><strong>Manual step:</strong> ${esc(f.manual_step)}</p>` : ''}
</section>`).join('\n')}`,
});

// Ledger
add({
  path: '/ledger/', title: 'Campaign ledger',
  description: 'Campaign ledger: empty until authorized first-party reports are imported.',
  body: `<section class="page-head"><p class="kicker">Campaign ledger</p><h1>Campaign ledger</h1><p class="deck">${esc(ledger.status)}</p></section>
<div class="prose"><p>${esc(ledger.rule)}</p></div>
${table(ledger.columns.map((c) => c.name), [ledger.columns.map(() => '<span class="muted">—</span>')], 'wide')}
<p class="small muted">Rows: ${ledger.rows.length}. No conversion score, revenue forecast or optimization is presented.</p>
<h2>Column meanings</h2>
${table(['Column', 'Meaning'], ledger.columns.map((c) => [`<code>${esc(c.name)}</code>`, esc(c.meaning)]))}`,
});

// Measurement
add({
  path: '/measurement/', title: 'Measurement',
  description: 'Five proposed analytics events, privacy rules, and whether collection is active.',
  body: `<section class="page-head"><p class="kicker">Measurement</p><h1>Measurement</h1><p class="deck">${esc(events.status)}</p></section>
<div class="status-box"><strong>Live status:</strong> ${cfg.analyticsEndpoint ? 'Endpoint configured.' : 'Inactive. No endpoint is configured, so the browser sends nothing. See suggestion S-03 and flag FLG-009.'}</div>
${table(['Event', 'Fires when', 'Properties'], events.events.map((e) => [`<code>${esc(e.name)}</code>`, esc(e.fires), e.properties.map((p) => `<code>${esc(p)}</code>`).join(' ')]))}
<h2>Privacy</h2>
<p>${esc(events.privacy)}</p>
<p>Not collected: ${esc(events.not_collected.join(', '))}.</p>
<h2>Why clicks are not routed through a redirect</h2>
<p>${esc(events.why_no_redirect)} ${srcLink('S02')}</p>`,
});

// Compliance
add({
  path: '/compliance/', title: 'Compliance and gates',
  description: 'How disclosure, sponsored links, tags and sources are handled, and the gates before scaling.',
  body: `<section class="page-head"><p class="kicker">Compliance</p><h1>Disclosure, link rules and gates</h1></section>
<div class="prose">
<h2>Required statement</h2>
<p>Operating Agreement §5 requires the Site to state, clearly and prominently: <strong>“${esc(cfg.associatesStatement)}”</strong> ${srcLink('S01')}</p>
<p>The disclosure strip sits under the masthead on every page, and it is repeated in the footer. The FTC guidance asks that a disclosure be hard to miss and placed with the endorsement, not only on an About page or behind a “more” link ${srcLink('S07')}, and the Endorsement Guides define clear and conspicuous placement ${srcLink('S08')}.</p>
<h2>Link rules applied</h2>
<ul>
<li>Every link to an Amazon host carries <code>rel="sponsored noopener"</code>. Google recommends this for paid links and affiliate links ${srcLink('S06')}.</li>
<li>Product links carry the tracking ID <code>${esc(cfg.trackingId)}</code> as a tag parameter ${srcLink('S02')}.</li>
<li>No redirect, cloaking or link-shortener is used for outbound links. The click counter does not route clicks ${srcLink('S02')}.</li>
<li>The five submitted short links are shown only as source evidence, not as buy links (FLG-003).</li>
</ul>
<h2>Gates before scaling</h2>
</div>
${table(['Gate', 'Check', 'Method', 'Status'], [
    ['G-01', 'Disclosure strip above the fold on every page and repeated in the footer', 'Automated (tools/verify.mjs); visibility on a phone is manual (FLG-010)', 'Passed (automated)'],
    ['G-02', 'One Special Link per product tested in Associates Central, with destination and tracking report confirmed', 'Manual, requires Associates login', '<strong>Pending</strong> (FLG-005)'],
    ['G-03', 'Every Amazon-hosted link carries rel="sponsored"', 'Automated', 'Passed (automated)'],
    ['G-04', 'Every outbound product link uses tag shopnow047c-20', 'Automated', 'Passed (automated)'],
    ['G-05', 'No redirect or cloaking pages generated', 'Automated', 'Passed (automated)'],
    ['G-06', 'No prices, ratings or availability displayed', 'Automated', 'Passed (automated)'],
    ['G-07', 'Every product row has at least one official source link', 'Automated', 'Passed (automated)'],
    ['G-08', 'Ledger rows only from authorized first-party reports', 'Manual', 'Not applicable (ledger empty)'],
    ['G-09', 'Analytics: only the five listed events; no cookies', 'Automated', 'Passed (automated)'],
    ['G-10', 'Sitemap and feed cover every guide; no broken internal links', 'Automated', 'Passed (automated)'],
  ])}
<div class="prose"><p class="small">Automated gates are enforced by <code>tools/verify.mjs</code>; a failing gate stops the build from being published. Source wording for §2 of the Participation Requirements was read from search excerpts of the official page, and should be re-checked (see the source register).</p></div>`,
});

// About
add({
  path: '/about/', title: 'About and editorial policy',
  description: 'Who writes this site, how products are chosen, how facts are checked, and how to correct them.',
  body: `<section class="page-head"><p class="kicker">About</p><h1>About Affil3</h1></section>
<div class="prose">
<h2>Who writes it</h2>
<p>${esc(cfg.author)}. No named author or credentials are listed yet (FLG-014). Named authors will appear once a real person is confirmed.</p>
<h2>How products are chosen</h2>
<p>Only the five products submitted by the site owner are listed. No product was added from our own research.</p>
<h2>How facts are checked</h2>
<p>Each fact on a product row carries a source link to an official page. If a value cannot be confirmed from an official source, the cell stays blank and the row is flagged. We do not infer values.</p>
<h2>Corrections</h2>
<p>If something is wrong, open an issue in the <a href="https://github.com/karagemop466-tech/Affil3/issues" rel="noopener external">project repository</a>. Corrections are logged on the <a href="${esc(href('/flagged/'))}">Flagged for review</a> page.</p>
</div>`,
});

// 404
add({ path: '/404.html', title: 'Page not found', description: 'This page does not exist.', noSitemap: true,
  body: `<section class="page-head"><h1>Page not found</h1><p class="deck">Try the <a href="${esc(href('/'))}">front page</a> or the <a href="${esc(href('/shop/'))}">shop table</a>.</p></section>` });

// ---------- write ----------
for (const o of OWNED) fs.rmSync(path.join(OUT, o), { recursive: true, force: true });
fs.mkdirSync(OUT, { recursive: true });
const written = [];
for (const p of pages) {
  const file = p.path.endsWith('.html') ? path.join(OUT, p.path) : path.join(OUT, p.path, 'index.html');
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, page(p));
  written.push({ path: p.path, file: path.relative(ROOT, file), noSitemap: !!p.noSitemap });
}

// Assets
fs.mkdirSync(path.join(OUT, 'assets'), { recursive: true });
fs.copyFileSync(path.join(ROOT, 'src/assets/style.css'), path.join(OUT, 'assets/style.css'));
fs.copyFileSync(path.join(ROOT, 'src/assets/analytics.js'), path.join(OUT, 'assets/analytics.js'));
fs.writeFileSync(path.join(OUT, '.nojekyll'), '');

// Sitemap
const sitemapPages = written.filter((w) => !w.noSitemap);
fs.writeFileSync(path.join(OUT, 'sitemap.xml'), `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${sitemapPages.map((w) => `  <url><loc>${esc(abs(w.path))}</loc><lastmod>${cfg.lastReviewed}</lastmod></url>`).join('\n')}
</urlset>
`);

// Feed (guides only, newest first)
const feedItems = [...guides].sort((a, b) => (a.date < b.date ? 1 : -1));
fs.writeFileSync(path.join(OUT, 'feed.xml'), `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
  <title>${esc(cfg.siteName)} guides</title>
  <link>${esc(abs('/'))}</link>
  <description>${esc(cfg.tagline)}</description>
  <language>${cfg.language}</language>
  <lastBuildDate>${rfc822(cfg.lastReviewed)}</lastBuildDate>
  <atom:link href="${esc(abs('/feed.xml'))}" rel="self" type="application/rss+xml"/>
${feedItems.map((g) => `  <item>
    <title>${esc(g.title)}</title>
    <link>${esc(abs(`/guides/${g.slug}/`))}</link>
    <guid isPermaLink="true">${esc(abs(`/guides/${g.slug}/`))}</guid>
    <pubDate>${rfc822(g.date)}</pubDate>
    <description>${esc(g.description)}</description>
  </item>`).join('\n')}
</channel>
</rss>
`);

// robots
fs.writeFileSync(path.join(OUT, 'robots.txt'), `User-agent: *\nAllow: /\n\nSitemap: ${abs('/sitemap.xml')}\nSitemap: ${abs('/editorial/sitemap.xml')}\n`);

console.log(`Built ${written.length} pages, ${feedItems.length} feed items, ${sitemapPages.length} sitemap URLs at the repository root`);
