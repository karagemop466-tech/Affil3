#!/usr/bin/env node
// Static site generator for Affil3 / ShopNow Kitchen. No dependencies. Reads data/*.json and src/assets, writes the site at the repo root.
// Run: node tools/build.mjs   (then node tools/verify.mjs)
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
// Output goes to the repository root (GitHub Pages serves main at /). Only the paths in OWNED are
// replaced; every other file (data/, src/, tools/, legacy/, COORDINATION.md, ...) is left alone.
const OUT = ROOT;
const OWNED = ['index.html', 'shop', 'products', 'categories', 'guides', 'how-we-choose', 'executive-summary', 'sources', 'questions', 'suggestions',
  'flagged', 'ledger', 'measurement', 'compliance', 'about', 'workflow', 'privacy', '404.html', 'feed.xml', 'sitemap.xml', 'robots.txt',
  'assets/style.css', 'assets/analytics.js', 'assets/img', '.nojekyll'];
const read = (p) => JSON.parse(fs.readFileSync(path.join(ROOT, p), 'utf8'));

const cfg = read('data/config.json');
const productsDoc = read('data/products.json');
const products = productsDoc.products;
const sourcesDoc = read('data/sources.json');
const SOURCES = Object.fromEntries(sourcesDoc.sources.map((s) => [s.id, s]));
const flagsDoc = read('data/flags.json');
const FLAGS = Object.fromEntries(flagsDoc.flags.map((f) => [f.id, f]));
const questions = read('data/questions.json');
const suggestionsDoc = read('data/suggestions.json');
const guides = read('data/guides.json').guides;
const events = read('data/events.json');
const ledger = read('data/ledger.json');
const decisionPaths = read('data/decision-paths.json').paths;
const cadence = read('data/cadence.json');

const CATEGORIES = [
  { slug: 'air-fryers', name: 'Air fryers', tagline: 'Basket-style, with the drawer you shake', blurb: 'Basket air fryers, chosen for the number of drawers and the room they take on the counter.', img: '/assets/img/guide-basket-vs-oven.png' },
  { slug: 'air-fryer-ovens', name: 'Countertop ovens', tagline: 'Doors, racks and a whole meal at once', blurb: 'Oven-style air fryers and toaster ovens: bigger footprint, more levels, more at once.', img: '/assets/img/guide-multifunction.png' },
  { slug: 'cooking-thermometers', name: 'Thermometers', tagline: 'The number that decides when to pull it', blurb: 'Instant-read spot checks and leave-in wireless probes, with the USDA targets that go with them.', img: '/assets/img/guide-thermometer.png' },
];
// Editorial product imagery (from the parallel register session; editorial illustration, not the reviewed units).
const PRODUCT_IMAGE = {
  P01: '/assets/img/hero-counter.jpg',
  P02: '/assets/img/oven-french-door.jpg',
  P03: '/assets/img/basket-turbofry-8qt.jpg',
  P04: '/assets/img/thermometer-instant-read.jpg',
  P05: '/assets/img/guide-thermometer.png',
};
const catName = (slug) => (CATEGORIES.find((c) => c.slug === slug) || { name: slug }).name;
const catImg = (slug) => (CATEGORIES.find((c) => c.slug === slug) || { img: '' }).img;

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
  ['/workflow/', 'Publishing workflow'],
  ['/about/', 'About and editorial policy'],
  ['/privacy/', 'Privacy notice'],
];

// ---------- helpers ----------
const esc = (s = '') => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const href = (p) => cfg.basePath + p;
const abs = (p) => cfg.siteUrl + p;
const hostOf = (u) => { try { return new URL(u).hostname; } catch { return ''; } };
const hostCount = new Set(sourcesDoc.sources.map((s) => hostOf(s.url)).filter(Boolean)).size;
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
const dateLong = (iso) => new Date(iso + 'T00:00:00Z').toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric', timeZone: 'UTC' });
const rfc822 = (iso) => new Date(iso + 'T00:00:00Z').toUTCString();
const slugId = (t = '') => t.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');

// An editorial illustration block. Every image on the site is AI-generated artwork and is
// labeled as such at the point of use; the credit line comes from data/config.json.
function figure(src, alt, caption = '') {
  const credit = caption ? `<figcaption>${esc(caption)}</figcaption>` : '';
  return `<figure class="figure"><img src="${esc(href(src))}" alt="${esc(alt)}" loading="lazy" width="1536" height="1024">${credit}</figure>`;
}
// Small labeled artwork used on product cards (kept visually separate from the buy button).
function cardArt(p) {
  const src = PRODUCT_IMAGE[p.id] || catImg(p.category);
  if (!src) return '';
  return `<div class="card-art"><img src="${esc(href(src))}" alt="Editorial illustration for ${esc(p.name || p.id)}; not the reviewed unit" loading="lazy" width="768" height="512"><span class="art-tag">Illustration</span></div>`;
}

function page({ title, description, path: p, body, type = 'page', attrs = '', ogType = 'website', jsonld = '', ogImage = '/assets/img/hero.png' }) {
  const canonical = abs(p);
  const ogImg = abs(ogImage);
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
<meta property="og:image" content="${esc(ogImg)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="${esc(title)}">
<meta name="twitter:description" content="${esc(description)}">
<meta name="twitter:image" content="${esc(ogImg)}">
<meta name="analytics-endpoint" content="${esc(cfg.analyticsEndpoint || '')}">
<link rel="icon" type="image/svg+xml" href="${esc(href('/assets/img/favicon.svg'))}">
<link rel="stylesheet" href="${esc(href('/assets/style.css'))}">
<link rel="alternate" type="application/rss+xml" title="${esc(cfg.siteName)} guides" href="${esc(abs('/feed.xml'))}">
${jsonld}
</head>
<body data-page="${esc(type)}" ${attrs}>
<a class="skip" href="#main">Skip to content</a>
<header class="masthead">
  <div class="wrap masthead-inner">
    <a class="brand" href="${esc(href('/'))}"><svg class="brand-mark" viewBox="0 0 64 64" aria-hidden="true" focusable="false"><rect width="64" height="64" rx="14" fill="currentColor"/><g fill="none" stroke="#FAF6EF" stroke-width="4" stroke-linecap="round"><path d="M20 26 h24 a6 6 0 0 1 6 6 v10 a8 8 0 0 1 -8 8 h-20 a8 8 0 0 1 -8 -8 v-10 a6 6 0 0 1 6 -6 z"/><path d="M24 26 v-6 a4 4 0 0 1 4 -4 h8 a4 4 0 0 1 4 4 v6"/><path d="M22 38 h20"/></g></svg><span>${esc(cfg.siteName)}</span></a>
    <p class="tagline">${esc(cfg.tagline)}</p>
    <nav class="nav" aria-label="Main">
      <a href="${esc(href('/shop/'))}">Shop</a>
      <a href="${esc(href('/guides/'))}">Guides</a>
      <a href="${esc(href('/categories/'))}">Categories</a>
      <a href="${esc(href('/about/'))}">About</a>
    </nav>
  </div>
</header>
<div class="disclosure-strip" role="note" aria-label="Affiliate disclosure">
  <div class="wrap"><strong>Disclosure.</strong> ${esc(cfg.disclosureStrip)} <a href="${esc(href('/compliance/'))}">How we disclose</a></div>
</div>
<main id="main" class="wrap">
${body}
</main>
<footer class="site-footer">
  <div class="wrap footer-grid">
    <div class="footer-col footer-about">
      <p class="footer-brand">${esc(cfg.siteName)}</p>
      <p class="small muted">${esc(cfg.footerBlurb || 'Independent kitchen buying guides. We track a small shelf of appliances, we read the official listings, and we show our sources.')} ${esc(cfg.brandNote)}</p>
      <p class="small muted"><a href="${esc(href('/feed.xml'))}">RSS feed</a> · <a href="${esc(href('/legacy/archive/'))}">Archived editions</a> · <a href="${esc(href('/sitemap.xml'))}">Sitemap</a></p>
    </div>
    <div class="footer-col">
      <h2 class="foot-h">Guides</h2>
      <ul class="foot-links">
        <li><a href="${esc(href('/guides/'))}">All guides</a></li>
        ${guides.slice(0, 3).map((g) => `<li><a href="${esc(href('/guides/' + g.slug + '/'))}">${esc(g.title)}</a></li>`).join('\n        ')}
      </ul>
    </div>
    <div class="footer-col">
      <h2 class="foot-h">Dashboards and records</h2>
      <ul class="foot-links">
        ${DASHBOARDS.map(([u, t]) => `<li><a href="${esc(href(u))}">${esc(t)}</a></li>`).join('\n        ')}
      </ul>
    </div>
  </div>
  <div class="wrap footer-legal">
    <p class="disclosure-footer"><strong>Disclosure.</strong> ${esc(cfg.disclosureStrip)}</p>
    <p class="fine">${esc(cfg.siteName)} is not sponsored by or affiliated with Amazon.com, Inc. Prices and availability are not shown on this site. Illustrations are AI-generated and labeled at the point of use. Last reviewed ${esc(dateLong(cfg.lastReviewed))}. Source links are listed on each page and in the <a href="${esc(href('/sources/'))}">source register</a>.</p>
  </div>
</footer>
<script src="${esc(href('/assets/analytics.js'))}" defer></script>
</body>
</html>
`;
}

// ---------- components ----------
function productCard(p, placement) {
  const title = p.name || displayName(p);
  const cat = catName(p.category);
  const note = p.lede || p.editorial_note || '';
  const fit = p.best_for && p.tradeoff ? `<p class="fit-line"><strong>Best for:</strong> ${esc(p.best_for)}<br><strong>Trade-off:</strong> ${esc(p.tradeoff)}</p>` : '';
  if (tagged(p)) {
    return `<article class="card product" data-product-view="${esc(p.id)}">
  ${cardArt(p)}
  <div class="card-body">
    <p class="kicker">${esc(cat)}${p.shape ? ` · ${esc(p.shape)}` : ''}</p>
    <h3>${esc(title)}</h3>
    ${note ? `<p class="muted small">${esc(note)}</p>` : ''}
    ${placement === 'front-shelf' ? '' : fit}
    ${placement === 'front-shelf' ? '' : `<p class="muted small">Observed ASIN <code>${esc(p.observed_asin)}</code></p>`}
    <p><a class="btn" href="${esc(tagged(p))}" rel="sponsored noopener" data-outbound data-product="${esc(p.id)}" data-placement="${esc(placement)}">View on Amazon</a></p>
    ${placement === 'front-shelf' ? '' : `<p class="status">${esc(p.outbound_status)}</p>`}
  </div>
</article>`;
  }
  if (p.no_buy_link) {
    return `<article class="card product warn-card" data-product-view="${esc(p.id)}">
  ${cardArt(p)}
  <div class="card-body">
    <p class="kicker">${esc(cat)}${p.shape ? ` · ${esc(p.shape)}` : ''}</p>
    <h3>${esc(p.name || displayName(p))}</h3>
    ${note ? `<p class="muted small">${esc(note)}</p>` : ''}
    <p class="status"><strong>No buy button on this card.</strong> ${esc(p.no_buy_link_reason || 'No manufacturer specification page exists for this model, so nothing here is stood behind yet.')} ${flagLinks(p.flags || [])}</p>
  </div>
</article>`;
  }
  return `<article class="card product warn-card" data-product-view="${esc(p.id)}">
  <div class="card-body">
    <p class="kicker">${esc(cat)}</p>
    <h3>Link not resolved</h3>
    <p class="muted small">Submitted link: <code>${esc(p.submitted_token)}</code></p>
    <p class="status">No buy link is published. The link has not resolved to a product page in a verified session. An Amazon "Continue shopping" checkpoint is intermittent and is not by itself evidence that a link is dead. ${flagLinks(['FLG-004'])}</p>
  </div>
</article>`;
}

function renderBlock(b, gslug = '') {
  switch (b.type) {
    case 'note': return `<p class="note">${esc(b.text)}</p>`;
    case 'p': return `<p>${esc(b.text)}</p>`;
    case 'h2': return `<h2 id="${esc(slugId(b.text))}">${esc(b.text)}</h2>`;
    case 'h3': return `<h3>${esc(b.text)}</h3>`;
    case 'ul': return `<ul>${b.items.map((i) => `<li>${esc(i)}</li>`).join('')}</ul>`;
    case 'ol': return `<ol>${b.items.map((i) => `<li>${esc(i)}</li>`).join('')}</ol>`;
    case 'img': return figure(b.src, b.alt, b.caption || '');
    case 'table': return `<div class="table-wrap"><table class="checklist"><thead><tr>${b.headers.map((h) => `<th scope="col">${esc(h)}</th>`).join('')}</tr></thead><tbody>${b.rows.map((r) => `<tr>${r.map((c) => `<td>${esc(c)}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
    case 'faq': return `<section class="faq"><h2 id="${esc(slugId('Questions readers ask next'))}">Questions readers ask next</h2>${b.items.map((i) => `<details class="faq-item"><summary>${esc(i.q)}</summary><p>${esc(i.a)}</p></details>`).join('\n')}</section>`;
    case 'cta': return `<aside class="cta-band"><div><p class="cta-text">${esc(b.text)}</p></div><a class="btn btn-ghost" href="${esc(href(b.href))}">${esc(b.label)}</a></aside>`;
    default: throw new Error('unknown block ' + b.type + (gslug ? ' in guide ' + gslug : ''));
  }
}

// Specification grid. A field the maker does not state renders as a labelled "not stated" cell;
// the count of those cells must match the data exactly (verified by tools/verify.mjs).
function specGrid(p) {
  const rows = [
    ['Model', p.model],
    ['Capacity', p.capacity_qt ? `${p.capacity_qt} qt` : ''],
    ['Temperature', p.temp_min_f && p.temp_max_f ? `${p.temp_min_f}–${p.temp_max_f} °F` : (p.temp_max_f ? `up to ${p.temp_max_f} °F` : '')],
    ['Power', p.power_w ? `${p.power_w} W` : ''],
    ['Voltage', p.voltage],
    ['Size', p.dimensions_in ? `${p.dimensions_in} in` : ''],
    ['Weight', p.weight_lb ? `${p.weight_lb} lb` : ''],
    ['Dishwasher', p.dishwasher_safe],
    ['Certified', p.certification],
    ['Warranty', p.warranty],
  ];
  const cells = rows.map(([k, v]) => `<div class="spec"><dt>${esc(k)}</dt>${v
    ? `<dd>${esc(v)}</dd>`
    : `<dd class="na" title="Not stated on the manufacturer page">not stated</dd>`}</div>`).join('\n    ');
  return `<dl class="spec-grid">\n    ${cells}\n  </dl>`;
}

function buyBox(p, placement = 'product-page') {
  if (p.no_buy_link) {
    return `<div class="buybox hidden-link">
    <p><strong>No buy button on this page.</strong> ${esc(p.no_buy_link_reason)}</p>
    <p class="small">The listing this unit was observed on is recorded on the <a href="${esc(href('/shop/'))}">comparison table</a> with its source link.</p>
  </div>`;
  }
  return `<div class="buybox">
    <a class="btn btn-primary" href="${esc(p.tagged_outbound_url)}" rel="sponsored noopener" data-outbound data-product="${esc(p.id)}" data-placement="${esc(placement)}">Check it on Amazon</a>
    <span class="btn-note">Affiliate link, marked sponsored. Opens the ${esc(p.brand || 'manufacturer')} listing on Amazon.com. We do not display prices because they change and we do not use Amazon price data.</span>
  </div>`;
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

// ---------- decision paths ----------
// A path is written only from fields that already exist in the product register, and it
// cites the source that supplied those figures. It never ranks, scores or recommends.
const byId = Object.fromEntries(products.map((p) => [p.id, p]));
const pathSources = (ids = []) => ids.map((id) => {
  if (id === 'S04') {
    const first = byId[(decisionPaths.find((dp) => dp.sources.includes(id)) || {}).product_ids?.[0]];
    return `<a href="${esc(href('/shop/'))}">S04</a> <span class="small muted">observed listing pages, one per row</span>`;
  }
  if (id === 'S16') return srcLink('S16');
  return srcLink(id);
}).join(' \u00b7 ');

function decisionPathCards() {
  return `<div class="path-grid">${decisionPaths.map((dp) => {
    const rows = dp.product_ids.map((pid) => byId[pid]).filter(Boolean);
    const names = rows.map((p) => `<a class="path-product" href="${esc(href('/products/' + p.slug + '/'))}">${esc(p.short_name || p.name)}</a>`).join('<span class="path-sep"> or </span>');
    const pending = rows.filter((p) => p.no_buy_link);
    return `<article class="card path-card" id="${esc(dp.id)}">
  <div class="card-body">
    <h3>${esc(dp.situation)}</h3>
    <p class="path-because">${esc(dp.because)}</p>
    <p class="path-products">${names}</p>
    <p class="small muted">${esc(dp.why_this_row)}</p>
    ${dp.tradeoff ? `<p class="path-tradeoff"><strong>The trade-off:</strong> ${esc(dp.tradeoff)}</p>` : ''}
    ${pending.length ? `<p class="path-pending"><strong>Note:</strong> ${pending.map((p) => esc(p.short_name || p.name)).join(', ')} is listed here as context only; no submitted link resolved to it, so no buy button is published. ${flagLinks(['FLG-001', 'FLG-025'])}</p>` : ''}
    <p class="small muted path-src">Sources: ${pathSources(dp.sources)}</p>
  </div>
</article>`;
  }).join('\n')}</div>`;
}

// At-a-glance table: the decision columns first, in one readable grid. Every value is copied
// from the register; a value the maker does not state stays visibly empty rather than guessed.
function atGlanceTable() {
  const rows = products.map((p) => [
    `<a href="${esc(href('/products/' + p.slug + '/'))}"><strong>${esc(p.short_name || p.name)}</strong></a><br><span class="small muted">${esc(p.brand || '')}</span>`,
    esc(catName(p.category)),
    p.capacity_qt ? `${esc(p.capacity_qt)} qt` : cellText(''),
    (p.temp_min_f && p.temp_max_f) ? `${esc(p.temp_min_f)}\u2013${esc(p.temp_max_f)} \u00b0F` : (p.temp_max_f ? `up to ${esc(p.temp_max_f)} \u00b0F` : cellText('')),
    p.power_w ? `${esc(p.power_w)} W` : cellText(''),
    p.dimensions_in ? `${esc(p.dimensions_in)} in` : cellText(''),
    esc(p.best_for || ''),
    esc(p.tradeoff || ''),
    p.no_buy_link ? `<span class="badge bad">no confirmed link</span>` : `<a class="btn btn-small" href="${esc(p.tagged_outbound_url)}" rel="sponsored noopener" data-outbound data-product="${esc(p.id)}" data-placement="at-a-glance">Check it on Amazon</a>`,
    rowSources(p),
  ]);
  return table(['Product', 'Category', 'Stated capacity', 'Stated temperature', 'Stated power', 'Stated size', 'Best for', 'The trade-off', 'Buy', 'Sources (official)'], rows, 'wide');
}

// ---------- pages ----------
const pages = [];
const add = (p) => pages.push(p);

// Home (publication front page: products first)
{
  const shelf = products.map((p) => productCard(p, 'front-shelf')).join('\n');
  const newestGuides = [...guides].slice(0, 3);
  const guideCards = newestGuides.map((g) => `<a class="card guide-card" href="${esc(href('/guides/' + g.slug + '/'))}">
  <div class="guide-card-art"><img src="${esc(href(g.image))}" alt="" loading="lazy" width="768" height="512"></div>
  <div class="card-body"><p class="kicker">${esc(catName(g.category))} · ${esc(dateLong(g.date))}</p><h3>${esc(g.title)}</h3><p class="muted small">${esc(g.deck)}</p><p class="read-more">Read the guide →</p></div>
</a>`).join('\n');
  const catCards = CATEGORIES.filter((c) => c.slug !== 'unresolved').map((c) => `<a class="card cat-card" href="${esc(href('/categories/' + c.slug + '/'))}"><h3>${esc(c.name)}</h3><p>${esc(c.blurb)}</p></a>`).join('\n');
  const jsonld = `<script type="application/ld+json">${JSON.stringify({
    '@context': 'https://schema.org', '@type': 'WebSite', name: cfg.siteName, alternateName: cfg.priorName,
    url: cfg.siteUrl + '/', description: cfg.tagline,
  })}</script>`;
  add({
    path: '/', title: 'Kitchen gear, explained like a friend would',
    description: 'Air fryers, oven-style cookers and smart thermometers, explained in plain English. Every product links straight to its Amazon listing and every claim says where it came from.',
    type: 'home',
    ogImage: '/assets/img/hero.png',
    jsonld,
    body: `
<section class="hero">
  <div class="hero-copy">
    <p class="kicker">Independent kitchen buying guides · Updated ${esc(dateLong(cfg.lastReviewed))}</p>
    <h1>Kitchen gear, explained like a friend would</h1>
    <p class="deck">We track a small shelf of air fryers, oven-style cookers and a smart thermometer. Every pick links straight to its Amazon listing, and every claim on this site says where it came from. No hype, no invented ratings, no mystery methods.</p>
    <div class="hero-ctas">
      <a class="btn btn-primary" href="${esc(href('/shop/'))}">Browse the shelf</a>
      <a class="btn btn-ghost" href="${esc(href('/guides/'))}">Start with a question</a>
    </div>
  </div>
  <div class="hero-figure">
    <img src="${esc(href('/assets/img/hero.png'))}" alt="Editorial illustration of a basket-style air fryer with its drawer open beside a bowl of crispy bites and fresh herbs on a wooden counter; not the reviewed unit" width="1536" height="1024">
    <p class="credit">Illustration: AI-generated for ${esc(cfg.siteName)}. It is artwork, not a product photo.</p>
  </div>
</section>
<section class="band" id="shelf">
  <a id="picks" class="picks-anchor" aria-hidden="true"></a>
  <div class="band-head">
    <h2>On the shelf this month</h2>
    <p>Five appliances, picked because they answer five different cooking problems: two foods at once, a whole meal at once, one enormous batch, a quick spot check, and a cook you never have to stand over. Every specification comes from the maker's own page, and where the listing and the maker disagree, we say so on that product's page.</p>
  </div>
  <div class="picks"><div class="shelf">${shelf}</div></div>
  <p class="shelf-note">Buttons open the listing on Amazon with our tracking ID in the link. Links are marked sponsored. We do not show prices or ratings anywhere on this site. See the <a href="${esc(href('/compliance/'))}">disclosure policy</a> and the <a href="${esc(href('/flagged/'))}">open flags</a>.</p>
</section>
<section class="band band-alt" id="which">
  <div class="band-head">
    <h2>Which one is right for you?</h2>
    <p>Start from what you are cooking, not from the spec sheet. Each shortcut below names the trade-off as plainly as the benefit, and links to the page the figure came from.</p>
  </div>
  ${decisionPathCards()}
  <p class="shelf-note">These are shortcuts, not scores. We do not rank products, and we do not publish a best-of list, because a ranking would have to hide the trade-offs. Every figure above links to the page it came from.</p>
</section>
<section class="band band-alt">
  <div class="band-head">
    <h2>Start with a question, not a product</h2>
    <p>Each guide answers one question a real buyer asks, in the order you would ask it.</p>
  </div>
  <div class="guide-grid">${guideCards}</div>
  <p><a class="text-link" href="${esc(href('/guides/'))}">All five guides →</a></p>
</section>
<section class="band">
  <div class="band-head">
    <h2>Browse by category</h2>
  </div>
  <div class="cat-grid">${catCards}</div>
</section>
<section class="band band-alt">
  <div class="band-head">
    <h2>How these pages are made</h2>
    <p>Three rules, applied to every page on this site.</p>
  </div>
  <div class="steps">
    <div class="step"><span class="step-n">1</span><h3>Read the official page</h3><p>Every product fact comes from the observed Amazon listing or another official source, linked on the spot. If a value cannot be confirmed, the cell stays blank and the row is flagged.</p></div>
    <div class="step"><span class="step-n">2</span><h3>Say what we do not know</h3><p>Unverified things are labeled unverified. Open questions live on the <a href="${esc(href('/questions/'))}">questions page</a>; irregularities live on <a href="${esc(href('/flagged/'))}">Flagged for review</a>. Nothing is hidden in a footnote.</p></div>
    <div class="step"><span class="step-n">3</span><h3>Disclose, then link</h3><p>The disclosure is at the top of every page, and every Amazon link is marked sponsored. As an Amazon Associate we earn from qualifying purchases, and we say so before you reach a single buy button.</p></div>
  </div>
</section>
<section class="band seasonal">
  <div class="seasonal-copy">
    <p class="kicker">Late November, in the kitchen</p>
    <h2>The month of the big roast</h2>
    <p>Holiday cooking season is thermometer season. If one appliance earns counter space this month, it is the one that tells you whether the bird is done, and the one that frees up oven space. Our guides keep working all year; the timing is yours.</p>
    <div class="hero-ctas">
      <a class="btn btn-ghost" href="${esc(href('/guides/is-your-meat-thermometer-telling-you-the-right-number/'))}">Thermometer questions, answered</a>
      <a class="btn btn-ghost" href="${esc(href('/guides/questions-to-ask-before-buying-a-multi-function-kitchen-appliance/'))}">Is a combo appliance worth it?</a>
    </div>
  </div>
  <div class="seasonal-art"><img src="${esc(href('/assets/img/guide-thermometer.png'))}" alt="" loading="lazy" width="768" height="512"></div>
</section>
<section class="band band-alt whatsite">
  <div class="band-head">
    <h2>What this site is</h2>
    <p>An independent buying guide for a shortlist of five kitchen appliances submitted by the site's owner. We read the Amazon listing and the manufacturer's own specification pages for each one, we publish what we could and could not confirm, and we flag every conflict between the two instead of smoothing it over. We are not a test kitchen: nothing here is hands-on measurement, and no price, rating or availability is republished. <a href="${esc(href('/how-we-choose/'))}">How we choose and check</a> · <a href="${esc(href('/flagged/'))}">What is currently flagged</a></p>
  </div>
</section>`,
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
  const shopJsonld = `<script type="application/ld+json">${JSON.stringify({
    '@context': 'https://schema.org', '@type': 'ItemList',
    name: 'Submitted product rows', numberOfItems: products.length,
    itemListElement: products.map((p, i) => ({
      '@type': 'ListItem', position: i + 1, name: p.name, url: abs('/products/' + p.slug + '/'),
    })),
  })}</script>
  <script type="application/ld+json">${JSON.stringify({
    '@context': 'https://schema.org', '@type': 'BreadcrumbList',
    itemListElement: [
      { '@type': 'ListItem', position: 1, name: 'Home', item: abs('/') },
      { '@type': 'ListItem', position: 2, name: 'Shop', item: abs('/shop/') },
    ],
  })}</script>`;
  add({
    path: '/shop/', title: 'Shop: all submitted products and findings',
    description: 'Every submitted product row: intended ASIN and listing fields (blank where unverified), observed redirect destinations kept separate, sources and flags.',
    jsonld: shopJsonld,
    body: `
<section class="page-head">
  <p class="kicker">Shop · 5 rows</p>
  <h1>All submitted products</h1>
  <p class="deck">One row per submitted link. <strong>Intended</strong> fields come only from an official source; none are confirmed yet, so they are blank. <strong>Observed</strong> fields are what the Amazon page showed on 2026-11-20 and are kept separate.</p>
</section>
<section>
  <h2>At a glance</h2>
  <p class="small muted">The columns a buyer actually compares: capacity, heat, power, footprint, what the unit is for, and what it costs you to live with. Every value is copied from the row's own source; a figure the maker does not publish stays empty. Nothing here is a price, a rating or a score.</p>
  ${atGlanceTable()}
</section>
<section class="band">
  <h2>Situation first</h2>
  <p class="small muted">The same register, read the other way round: from what you are cooking to the row that fits.</p>
  ${decisionPathCards()}
</section>
<section class="band">
  <h2>Full register</h2>
  <p class="small muted">One row per submitted link, with the intended and observed fields kept apart.</p>
  ${table(['ID', 'Category', 'Observed title and breadcrumb', 'Observed ASIN and page', 'Submitted link', 'Intended ASIN', 'Official listing URL', 'Confirmation date', 'Confirmation source', 'Buy link status', 'Confirmation status', 'Sources (official)'], rows, 'wide')}
</section>
<section class="band">
  <h2>What the table shows</h2>
  <ul class="findings">
    <li>All five submitted tokens are 9 characters. The observed Amazon product IDs are 10 characters. ${flagLinks(['FLG-001'])}</li>
    <li>${resolvedCount === 5 ? 'All five' : resolvedCount + ' of five'} short links resolved to a product page, and each product ID differs from the token in its link.${resolvedCount < 5 ? ' ' + unanswered.map((p) => `<code>${esc(p.submitted_token)}</code> has not resolved in a verified session, so no product is shown and no buy link is published. ${flagLinks(['FLG-004'])}`).join(' ') : ''} ${flagLinks(['FLG-002'])}</li>
    <li>Two destinations were transposed in an earlier register revision and were corrected after a retest. ${flagLinks(['FLG-022', 'FLG-028'])}</li>
    <li>All five observed listings were re-read directly on 2026-11-20, and each page's own title matched the title in this table. ${flagLinks(['FLG-030'])}</li>
    <li>The short-link step itself did not reproduce on the last check: two reached the Amazon home page and three were unreachable from the check environment. The token-to-listing mapping is therefore treated as unverified, not as proven. It does not affect the buy links, which point at the observed listings below rather than at the short links. ${flagLinks(['FLG-031'])}</li>
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
    ogImage: c.img || '/assets/img/hero.png',
    body: `${c.img ? `<section class="cat-hero"><img src="${esc(href(c.img))}" alt="Illustration for the ${esc(c.name)} category; not the reviewed unit" width="768" height="512"><p class="credit">Illustration: AI-generated. ${esc(cfg.imageDisclosure || '')}</p></section>` : ''}
<section class="page-head"><p class="kicker">Category</p><h1>${esc(c.name)}</h1><p class="deck">${esc(c.tagline ? c.tagline + '. ' : '')}${esc(c.blurb)}</p></section>
<section class="shelf">${cards || '<p>No product rows in this category.</p>'}</section>
<section class="band"><h2>Guides for this cluster</h2>
${gl.length ? `<ul class="guide-list">${gl.map((g) => `<li class="guide-item"><a href="${esc(href('/guides/' + g.slug + '/'))}">${esc(g.title)}</a><p>${esc(g.deck)}</p></li>`).join('')}</ul>` : '<p>No guide yet in this cluster.</p>'}
</section>`,
  });
}

// Guides index + guide pages
add({
  path: '/guides/', title: 'Guides',
  description: 'Question-led buying guides for air fryers, air fryer ovens and cooking thermometers.',
  body: `<section class="page-head"><p class="kicker">Guides</p><h1>Buying guides, by question</h1>
<p class="deck">Each guide starts with a question buyers ask. Working titles are editorial hypotheses, not claims about popularity or search volume.</p></section>
<div class="guide-grid">${guides.map((g) => `<a class="card guide-card" href="${esc(href('/guides/' + g.slug + '/'))}">
  <div class="guide-card-art"><img src="${esc(href(g.image))}" alt="" loading="lazy" width="768" height="512"></div>
  <div class="card-body"><p class="kicker">${esc(catName(g.category))} · ${esc(dateLong(g.date))}</p><h3>${esc(g.title)}</h3><p class="muted small">${esc(g.deck)}</p><p class="read-more">Read the guide →</p></div>
</a>`).join('\n')}</div>`,
});
for (const g of guides) {
  const productsHere = products.filter((p) => tagged(p) && (p.category === g.category || (g.cluster_links || []).includes(p.category)));
  const faqBlock = (g.body || []).find((b) => b.type === 'faq');
  const faqItems = (faqBlock && faqBlock.items) || [];
  const jsonld = `<script type="application/ld+json">${JSON.stringify({
    '@context': 'https://schema.org', '@type': 'Article', headline: g.title, description: g.description,
    image: abs(g.image),
    datePublished: g.date, dateModified: cfg.lastReviewed, author: { '@type': 'Organization', name: cfg.author },
    publisher: { '@type': 'Organization', name: cfg.siteName }, mainEntityOfPage: abs(`/guides/${g.slug}/`),
  })}</script>
  <script type="application/ld+json">${JSON.stringify({
    '@context': 'https://schema.org', '@type': 'FAQPage',
    mainEntity: faqItems.map((i) => ({
      '@type': 'Question', name: i.q,
      acceptedAnswer: { '@type': 'Answer', text: i.a },
    })),
  })}</script>
  <script type="application/ld+json">${JSON.stringify({
    '@context': 'https://schema.org', '@type': 'BreadcrumbList',
    itemListElement: [
      { '@type': 'ListItem', position: 1, name: 'Home', item: abs('/') },
      { '@type': 'ListItem', position: 2, name: 'Guides', item: abs('/guides/') },
      { '@type': 'ListItem', position: 3, name: g.title, item: abs(`/guides/${g.slug}/`) },
    ],
  })}</script>`;
  add({
    path: `/guides/${g.slug}/`, title: g.title, description: g.description, type: 'guide', ogType: 'article', jsonld,
    attrs: `data-guide="${esc(g.slug)}"`,
    ogImage: g.image,
    body: `<article class="article">
  <header class="page-head">
    <p class="kicker">${esc(catName(g.category))} · Guide</p>
    <h1>${esc(g.title)}</h1>
    <p class="deck">${esc(g.deck)}</p>
    <p class="byline">By ${esc(cfg.author)} · Published ${esc(dateLong(g.date))} · Last reviewed ${esc(dateLong(cfg.lastReviewed))}</p>
  </header>
  <figure class="article-hero"><img src="${esc(href(g.image))}" alt="${esc(g.image_alt || 'Editorial illustration for this guide; not the reviewed unit')}" width="1536" height="1024"><figcaption>${esc(g.image_alt || 'Editorial illustration')} — editorial illustration, not the reviewed unit.</figcaption></figure>
  <div class="prose">${g.body.filter((b, i) => !(b.type === 'img' && i === 0)).map((b) => renderBlock(b, g.slug)).join('\n')}</div>
  ${productsHere.length ? `<aside class="band"><h2>Products in this cluster</h2><p class="small muted">The buttons below are Amazon affiliate links with our tracking ID. Links are marked sponsored.</p><div class="shelf">${productsHere.map((p) => productCard(p, 'guide-box')).join('')}</div></aside>` : ''}
  <section class="band sources"><h2>Sources for this guide</h2>
    ${g.sources.length ? `<ul>${g.sources.map((id) => `<li>${guideSource(id)}</li>`).join('')}</ul>` : '<p>This guide makes no factual claim that needs an external source. It refers only to the observed listing data on the Shop page.</p>'}
    <p class="small"><a href="${esc(href('/sources/'))}">Full source register</a></p>
  </section>
</article>`,
  });
}

// Product detail pages (specifications from the manufacturer page, gaps as labelled "not stated")
for (const p of products) {
  const c = CATEGORIES.find((x) => x.slug === p.category) || { name: p.category };
  const facts = [
    ['Best for', p.best_for],
    ['The trade-off', p.tradeoff],
    ['Cleanup', p.dishwasher_safe || 'Not stated by the manufacturer. Check the manual before assuming a part is washable.'],
    ['What we could not verify', p.no_buy_link ? 'Everything: no manufacturer page exists for this model, so no specification is published.' : (Object.keys(p.blank_reason || {}).length ? Object.values(p.blank_reason).join(' ') : 'No gaps in the table above: every field came from the manufacturer page or is labelled not stated.')],
  ];
  const jsonld = `<script type="application/ld+json">${JSON.stringify({
    '@context': 'https://schema.org', '@type': 'Product', name: p.name, brand: { '@type': 'Brand', name: p.brand },
    description: p.lede, url: abs('/products/' + p.slug + '/'),
  })}</script>
  <script type="application/ld+json">${JSON.stringify({
    '@context': 'https://schema.org', '@type': 'BreadcrumbList',
    itemListElement: [
      { '@type': 'ListItem', position: 1, name: 'Home', item: abs('/') },
      { '@type': 'ListItem', position: 2, name: 'Shop', item: abs('/shop/') },
      { '@type': 'ListItem', position: 3, name: catName(p.category), item: abs('/categories/' + p.category + '/') },
      { '@type': 'ListItem', position: 4, name: p.name, item: abs('/products/' + p.slug + '/') },
    ],
  })}</script>`;
  const conflictTable = p.observed_specs ? `
<section class="band">
  <h2>The listing and the maker disagree</h2>
  <p>These figures come from the listing's own copy, not from the manufacturer. They are kept in a separate table on purpose, because on this listing they describe a different model from the manufacturer page. Read them as evidence of the conflict, not as specifications of the product.</p>
  ${table(['Field', 'Listing states', 'Manufacturer states'], [
    ['Model', esc(p.observed_specs.model || ''), esc(p.model || '')],
    ['Power', esc(p.observed_specs.power || ''), p.power_w ? esc(p.power_w + ' W') : '<span class="muted">not stated</span>'],
    ['Temperature', esc(p.observed_specs.temperature || ''), p.temp_max_f ? esc('up to ' + p.temp_max_f + ' °F') : '<span class="muted">not stated</span>'],
    ['Size', esc(p.observed_specs.dimensions || ''), p.dimensions_in ? esc(p.dimensions_in + ' in') : '<span class="muted">not stated</span>'],
    ['Capacity', esc(p.observed_specs.capacity || ''), p.capacity_qt ? esc(p.capacity_qt + ' qt') : '<span class="muted">not stated</span>'],
    ['Material', esc(p.observed_specs.material || ''), '<span class="muted">not stated</span>'],
  ])}
  <p class="small">${flagLinks((p.flags || []).filter((f) => ['FLG-026', 'FLG-027'].includes(f)))}</p>
</section>` : '';
  add({
    path: `/products/${p.slug}/`, type: 'product', ogType: 'article', jsonld,
    ogImage: PRODUCT_IMAGE[p.id] || '/assets/img/hero.png',
    attrs: `data-product-view="${esc(p.id)}"`,
    title: p.name,
    description: `${p.short_name || p.name}: ${p.lede || ''} Specifications from the manufacturer page, with every gap and conflict recorded.`,
    body: `
<nav class="crumbs small muted" aria-label="Breadcrumb"><a href="${esc(href('/shop/'))}">The picks</a> / <a href="${esc(href('/categories/' + p.category + '/'))}">${esc(c.name)}</a> / ${esc(p.short_name || p.name)}</nav>
<section class="pd-hero">
  <figure class="pd-figure">
    <img src="${esc(href(PRODUCT_IMAGE[p.id] || '/assets/img/hero.png'))}" alt="Editorial illustration for ${esc(p.name)}; not the reviewed unit" width="768" height="512">
    <figcaption class="credit">Editorial illustration, not the reviewed unit.</figcaption>
  </figure>
  <div>
    <p class="kicker">${esc(p.brand || '')} · ${esc(c.name)}</p>
    <h1>${esc(p.name)}</h1>
    <p class="deck">${esc(p.lede || '')}</p>
    ${buyBox(p)}
    <p class="small muted">${p.tagged_outbound_url && !p.no_buy_link ? `The link carries our Associates tag and is marked sponsored. It has not yet been confirmed in a tracking report (${flagLinks(['FLG-005'])}), so treat it as provisional.` : 'No outbound link is published for this product.'}</p>
  </div>
</section>
<section class="band">
  <h2>The specifications we could confirm</h2>
  ${specGrid(p)}
  <p class="small muted">${esc(p.capacity_note || '')}${p.model_note ? ' ' + esc(p.model_note) : ''}${p.dimensions_order ? ' Dimensions are shown as ' + esc(p.dimensions_order) + '.' : ''}</p>
  ${conflictTable}
</section>
<section class="band band-alt">
  <h2>Who it suits, and what it costs you</h2>
  <div class="facts">
    ${facts.map(([h, v]) => `<div class="fact"><h3>${esc(h)}</h3><p>${esc(v || '')}</p></div>`).join('\n    ')}
  </div>
</section>
<section class="band sources">
  <h2>Sources for this product</h2>
  <ul>${(p.sources || []).map((id) => `<li><strong>${esc(id)}</strong> — ${SOURCES[id] && SOURCES[id].url ? ext(SOURCES[id].url, 'open source', '') : '<span class="muted">no link recorded</span>'} · ${esc(SOURCES[id] ? SOURCES[id].title : '')}</li>`).join('')}${(p.spec_sources || []).filter((id) => !(p.sources || []).includes(id)).map((id) => `<li><strong>${esc(id)}</strong> — ${SOURCES[id] && SOURCES[id].url ? ext(SOURCES[id].url, 'open source', '') : '<span class="muted">no link recorded</span>'} · ${esc(SOURCES[id] ? SOURCES[id].title : '')}</li>`).join('')}</ul>
  <p class="small"><a href="${esc(href('/sources/'))}">Full source register</a> · <a href="${esc(href('/flagged/'))}">${(p.flags || []).length} open flag(s) on this row</a></p>
</section>`,
  });
}

// How we choose
add({
  path: '/how-we-choose/', title: 'How we choose and check',
  description: 'The selection and verification rules behind the shortlist: what gets listed, what gets checked, what gets flagged.',
  body: `<section class="page-head"><p class="kicker">Method</p><h1>How we choose and check</h1><p class="deck">The rules every product row and every guide on this site must pass.</p></section>
<div class="prose">
<h2>What gets listed</h2>
<p>Only appliances the site's owner submitted. We do not add products from our own research, and we do not rank or score them, because we hold no authorized performance data. Five rows, each with its submitted link, its observed Amazon destination, and its manufacturer specification sources.</p>
<h2>How each row is checked</h2>
<ol>
<li><strong>Observe the listing.</strong> Each submitted short link is fetched and the final Amazon page recorded (title, breadcrumb, /dp/ identifier). Observations are dated and never copied into the intended-product fields.</li>
<li><strong>Check the maker.</strong> Where the manufacturer publishes a specification page, its figures populate the product page's specification grid. Where the maker is silent, the cell reads <em>not stated</em> — never filled in.</li>
<li><strong>Record conflicts.</strong> Where the listing and the maker disagree, both readings are published side by side and the row is flagged (see FLG-023 through FLG-027 on the <a href="${esc(href('/flagged/'))}">flag page</a>).</li>
<li><strong>Withhold what we cannot stand behind.</strong> No prices, ratings, availability, or hands-on test claims. If a maker publishes no specification page at all, every specification is withheld (FLG-025).</li>
<li><strong>Link everything.</strong> Every row and guide carries its source IDs, linked in the <a href="${esc(href('/sources/'))}">source register</a>.</li>
</ol>
<h2>What would change a row</h2>
<p>A confirmation from the owner about the intended product behind each link (Q-01), or a manufacturer page appearing for a model we could not verify. Corrections are logged on the <a href="${esc(href('/flagged/'))}">Flagged for review</a> page with their dates.</p>
</div>`,
});

// Executive summary
add({
  path: '/executive-summary/', title: 'Executive summary',
  description: 'Executive summary: what is built, what is verified, what is blocked, and the decisions needed.',
  body: `<section class="page-head"><p class="kicker">Executive summary · ${esc(dateLong(cfg.lastReviewed))}</p><h1>Where this stands</h1></section>
<div class="prose">
<h2>What is built</h2>
<ul>
<li>A publication-style site with a products-first front page, a shop table, three category clusters, five question-led guides, disclosed editorial imagery, an RSS feed and a sitemap.</li>
<li>Dashboards for sources, questions, suggestions, flagged items, the campaign ledger (empty), measurement, compliance, the publishing workflow, and a privacy notice. All are linked from the footer.</li>
<li>One live, indexable publication. Four earlier parallel editions were archived under <code>legacy/editions/</code> with their builders, data and tests intact rather than deleted, and <code>robots.txt</code> disallows <code>/legacy/</code> so search engines see a single site (S-01, option D).</li>
<li>A disclosure strip under the masthead on every page, repeated in the footer, using the statement required by Operating Agreement §5.</li>
<li>A privacy-preserving click counter in the browser and a self-hostable collector. The collector is inactive on the live site until an endpoint is set (FLG-009).</li>
<li>Automated checks (tools/verify.mjs) for disclosure presence, sponsored attributes, tags, sources, sitemap and feed coverage, and internal links, plus a CI workflow that re-runs the build and the gate on every push.</li>
</ul>
<h2>What is verified</h2>
<p class="small muted">Every source below was fetched in full on ${esc(dateLong(cfg.lastReviewed))}, and the source register records how and when. A gate in <code>tools/verify.mjs</code> refuses any source that does not.</p>
<ul>
<li><strong>Amazon's own rules.</strong> The Operating Agreement statement requirement, the Special Link and tag rules, the anti-cloaking clause, and the Participation Requirements are read from the official Associates pages (S01, S02, S03, S17).</li>
<li><strong>Amazon's own definitions.</strong> Associates Central help defines an ASIN as “the 10-digit code that Amazon uses to denote specific products” and documents the simple text link format (S18). This settles FLG-001: the five submitted tokens are 9 characters, so none is an ASIN.</li>
<li><strong>Amazon's stated bar for a site.</strong> The application review help page states the qualified-sales requirement, the public-availability requirement, the “at least 10 posts” content rule of thumb, and the 60-day recency expectation (S19).</li>
<li><strong>Disclosure law and search guidance.</strong> The FTC endorsement guides (S07, S08, including the affiliate-link example at 16 CFR 255.5 Example 11), Google's outbound-link and spam policies (S06, S09), and the USDA temperature guidance (S10, S20) are read from the official pages.</li>
<li><strong>Manufacturer specifications.</strong> Every published specification is read from the maker's own page (S11–S15) or, for the one unit with no maker page, withheld entirely (FLG-025). Where the listing and the maker disagree, both figures are shown side by side (FLG-024, FLG-026).</li>
<li><strong>The observed listings.</strong> All five observed ASINs were re-read directly on ${esc(dateLong(cfg.lastReviewed))}, and each page's own title matches the title in the register (see the dated observation record).</li>
</ul>
<h2>What is not verified, and why</h2>
<ul>
<li><strong>Which product was meant.</strong> The intended ASIN, official listing URL, confirmation date and source are blank for all five products. The tokens are not ASINs (FLG-001), and the token-to-listing mapping did not reproduce on the last check — two links reached the Amazon home page and three were unreachable from the check environment (FLG-031). It is unverified, not disproven.</li>
<li><strong>Whether a click earns anything.</strong> No Special Link has been tested in Associates Central, so tag attribution is unproven (FLG-005, gate G-02). The status of the supplied short links is unresolved, not invalid (FLG-003).</li>
<li><strong>Content volume.</strong> Amazon describes a rule of thumb of at least 10 posts; this site publishes five guides (FLG-032).</li>
<li><strong>Claim stability.</strong> Two destinations were transposed in an earlier register revision and corrected after a retest (FLG-022). Manufacturer-page cross-checks produced FLG-023 to FLG-027, including one tracked unit whose listing and maker page describe two different machines (FLG-026).</li>
<li>No Special Link has been tested in Associates Central. The sandbox has no Associates login (FLG-005, gate G-02).</li>
<li>No prices, ratings, sales or commission figures are shown. The campaign ledger is empty and no conversion score or revenue forecast is presented.</li>
</ul>
<h2>Evidence needed before expanding</h2>
<ol>
<li>Use the original enrolled link-generation record or campaign brief to confirm intended products separately from observed redirects (Q-01).</li>
<li>Confirm the account declares this site and that tracking ID shopnow047c-20 is on the account (Q-03, FLG-011).</li>
<li>Run gate G-02 in Associates Central for each product. Record the destination and tracking report separately from site click data (Q-04).</li>
<li>Choose options on the <a href="${esc(href('/suggestions/'))}">Suggestions</a> page. Nine decisions are still open; S-01 is settled and recorded as implemented.</li>
</ol>
<h2>Measure before expanding</h2>
<p>Use <a href="https://developers.google.com/search/docs/monitor-debug/search-console-start" rel="noopener external">Google Search Console</a> for queries and impressions, the site collector for outbound clicks, and Amazon Associates reports (${srcLink('S02')}) for reported orders. A site click is not an order. Compare dated reporting windows, and leave the ledger empty until authorized data is available.</p>
<h2>Limits</h2>
<p>This build cannot pull Amazon product data, prices or sales reports. Those require authorized access (for example the Product Advertising API or Associates reports), which the sandbox does not have. The site does not scrape Amazon.</p>
</div>`,
});

// Sources
add({
  path: '/sources/', title: 'Source register',
  description: 'Every source used, how it was checked, and its status.',
  body: `<section class="page-head"><p class="kicker">Source register</p><h1>Sources and how they were checked</h1><p class="deck">${esc(sourcesDoc.note)}</p></section>
<section class="band">
  <h2>At a glance</h2>
  <p class="small muted">${sourcesDoc.sources.length} sources, ${hostCount} distinct hosts. Every one was read on ${esc(dateLong(cfg.lastReviewed))}. The five marketplace rows (S04, S05, S16) are pages this site observed directly rather than documents it was given.</p>
  ${table(['ID', 'Source', 'What it settles', 'Link'], sourcesDoc.sources.map((s) => [
    `<a href="#${esc(s.id)}"><strong>${esc(s.id)}</strong></a>`,
    `<strong>${esc(s.title)}</strong><br><span class="small muted">${esc(s.publisher)}</span>`,
    esc(s.used_for),
    s.url ? ext(s.url, hostOf(s.url), '') : '<span class="muted">none</span>',
  ]), 'wide')}
</section>
<section class="band band-alt">
  <h2>How each one was checked</h2>
  <p class="small muted">The exact wording relied on, and how the page was reached. A source with no quote is used for context only, not for a factual claim.</p>
  <div class="src-list">
  ${sourcesDoc.sources.map((s) => `<article class="src-card" id="${esc(s.id)}">
    <p class="src-head"><span class="badge">${esc(s.id)}</span> <strong>${esc(s.title)}</strong></p>
    <dl class="src-meta">
      <div><dt>Publisher</dt><dd>${esc(s.publisher)}</dd></div>
      <div><dt>Checked</dt><dd>${esc(s.last_checked || '')}</dd></div>
      <div><dt>How</dt><dd>${esc(s.method)}</dd></div>
      <div><dt>Status</dt><dd>${esc(s.status)}</dd></div>
    </dl>
    ${s.quote ? `<blockquote class="src-quote">${esc(s.quote)}</blockquote>` : ''}
    <p class="small">${ext(s.url, 'Open the official page →')}</p>
  </article>`).join('\n')}
  </div>
</section>`,
});

// Questions
add({
  path: '/questions/', title: 'Questions and gaps',
  description: 'What is known, what is not, and how each gap can be closed before a decision is made.',
  body: `<section class="page-head"><p class="kicker">Questions</p><h1>What we know, what we do not, and how to close the gap</h1><p class="deck">${esc(questions.note)}</p></section>
<h2>Known</h2>
${table(['ID', 'Statement', 'Sources'], questions.known.map((k) => [esc(k.id), esc(k.statement), k.sources.map(srcLink).join(', ') || '<span class="muted">none</span>']))}
<h2>Unknown: answer these before deciding</h2>
${table(['ID', 'Question', 'Why it matters', 'How to close it', 'Blocks scaling?', 'Sources'], questions.unknown.map((q) => [esc(q.id), esc(q.question), esc(q.why_it_matters), esc(q.how_to_close), q.blocking ? '<strong>Yes</strong>' : 'No', q.sources.map(srcLink).join(', ') || '<span class="muted">none</span>']), 'wide')}
<h2>Ways to discover missing information</h2>
${table(['ID', 'Suggestion', 'Closes'], questions.discovery.map((d) => [esc(d.id), esc(d.suggestion), d.closes.map(esc).join(', ') || '<span class="muted">none</span>']))}`,
});

// Suggestions (decision board: review, then choose)
add({
  path: '/suggestions/', title: 'Suggestions: choose a path',
  description: 'Options for the next decisions. Nothing is implemented until the owner chooses.',
  body: `<section class="page-head"><p class="kicker">Decision board</p><h1>Suggestions awaiting a choice</h1><p class="deck">${esc(suggestionsDoc.note)}</p></section>
<div class="choice-grid">
${suggestionsDoc.suggestions.map((s) => `<section class="choice-card${s.status === 'implemented' ? ' is-done' : ''}" id="${esc(s.id)}">
  <p class="kicker">${esc(s.id)} · ${esc(s.topic)}</p>
  <p class="choice-current">Decided: <span class="badge ${s.status === 'implemented' ? 'good' : ''}">${esc(s.current)}</span>${s.status === 'implemented' ? ' <span class="badge good">implemented</span>' : ' <span class="badge">open — awaiting your call</span>'}</p>
  ${s.status === 'implemented' && s.implemented_in ? `<p class="small muted">Landed in ${esc(s.implemented_in)}.</p>` : ''}
  <ul class="opts">${s.options.map((o) => `<li><strong>${esc(o.id)}.</strong> ${esc(o.label)}<br><span class="muted small">Tradeoff: ${esc(o.tradeoff)}</span>${o.cost ? `<br><span class="muted small">Cost to do it: ${esc(o.cost)}</span>` : ''}${o.reversible ? `<br><span class="muted small">Reversible: ${esc(o.reversible)}</span>` : ''}</li>`).join('')}</ul>
  <p class="choice-rec"><strong>Session recommendation:</strong> ${esc(s.recommendation)}</p>
  <dl class="choice-meta">
    ${s.blocking ? `<div><dt>What it holds up</dt><dd>${esc(s.blocking)}</dd></div>` : ''}
    ${s.meas ? `<div><dt>How you would know it worked</dt><dd>${esc(s.meas)}</dd></div>` : ''}
    ${s.cost ? `<div><dt>Cost of the recommended path</dt><dd>${esc(s.cost)}</dd></div>` : ''}
    ${s.evidence ? `<div><dt>Why it is settled</dt><dd>${esc(s.evidence)}</dd></div>` : ''}
  </dl>
</section>`).join('\n')}
</div>
<section class="band"><h2>How to choose</h2><p>Nine decisions are open. Reply with the suggestion ID and option letter (for example “S-03 B”). Only the choices you name are implemented; the site keeps showing the current option for everything else. Decisions that need your credentials first are listed on the <a href="${esc(href('/questions/'))}">questions page</a>, and every irregularity found so far is on <a href="${esc(href('/flagged/'))}">Flagged for review</a>.</p></section>`,
});

// Flagged for review
add({
  path: '/flagged/', title: 'Flagged for review',
  description: 'Irregularities and unverified items, with the sources and the manual step that would close each one.',
  body: `<section class="page-head"><p class="kicker">Flagged for review</p><h1>Flagged for review</h1><p class="deck">${esc(flagsDoc.note)} Flags do not block publication.</p></section>
${(() => {
    const open = flagsDoc.flags.filter((f) => f.status !== 'resolved');
    const done = flagsDoc.flags.filter((f) => f.status === 'resolved');
    const bySev = (sev) => open.filter((f) => f.severity === sev).length;
    const row = (f) => [`<a href="#${esc(f.id)}">${esc(f.id)}</a>`, `<span class="badge sev-${esc(f.severity)}">${esc(f.severity)}</span>`, esc(f.title), f.sources.length ? f.sources.map(srcLink).join(', ') : '<span class="muted">none</span>'];
    return `<section class="band band-alt">
  <h2>Open items first</h2>
  <p class="small muted">${open.length} open, ${done.length} resolved and kept for the audit trail. Sorted by severity, then by id. Every row links to the full entry, its official sources, and the manual step that would close it.</p>
  <div class="flag-stats">
    <div class="flag-stat"><span class="n">${bySev('high')}</span><span class="l">high</span></div>
    <div class="flag-stat"><span class="n">${bySev('medium')}</span><span class="l">medium</span></div>
    <div class="flag-stat"><span class="n">${bySev('low')}</span><span class="l">low</span></div>
    <div class="flag-stat"><span class="n">${done.length}</span><span class="l">resolved</span></div>
  </div>
  ${table(['ID', 'Severity', 'What is wrong', 'Official sources'], [...open].sort((a, b) => {
    const rank = { high: 0, medium: 1, low: 2 };
    return (rank[a.severity] ?? 3) - (rank[b.severity] ?? 3) || a.id.localeCompare(b.id);
  }).map(row), 'wide')}
</section>
<section class="band">
  <h2>Resolved, kept for the trail</h2>
  <p class="small muted">These were real problems. They are listed so a reader can see what changed rather than take the current state on faith.</p>
  ${table(['ID', 'Severity when raised', 'What was wrong', 'Official sources'], done.map(row), 'wide')}
</section>
<section class="band band-alt">
  <h2>Every entry in full</h2>`; })()}
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
<h2>The five events</h2>
${table(['Event', 'Fires when', 'Properties'], events.events.map((e) => [`<code>${esc(e.name)}</code>`, esc(e.fires), e.properties.map((p) => `<code>${esc(p)}</code>`).join(' ')]))}
<h2>Privacy</h2>
<p>${esc(events.privacy)}</p>
<p>Not collected: ${esc(events.not_collected.join(', '))}.</p>
<p class="small muted">Read the <a href="${esc(href('/privacy/'))}">privacy notice</a> for the plain-English version.</p>
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
<li>Illustrations are AI-generated and labeled at the point of use; they are never presented as product photos, and product claims never rest on them.</li>
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
    ['G-11', 'Generated files match the registers (no hand-edited HTML drift)', 'Automated (CI re-runs build and compares)', 'Passed (automated)'],
    ['G-12', 'Observed product destinations cross-checked by an independent retest', 'Retest register + independent fetch; corrections logged', 'Passed (FLG-022 corrected, FLG-028 corroborated)'],
    ['G-13', "Specifications cross-checked against the maker's own pages; conflicts flagged, never smoothed over", 'Manufacturer-page register (S11–S16) + retest', 'Passed — conflicts published (FLG-023…FLG-027)'],
  ])}
<h2>What Amazon says it looks for</h2>
<p>The following is quoted from Associates Central's own help page for the application review, fetched in full on 2026-11-20 ${srcLink('S19')}. It is listed here because it sets a bar the site can be measured against, rather than a claim about this site's standing.</p>
<ul>
<li><strong>Qualified sales before review:</strong> “we require at least three within the first 180 days”, and “personal orders do not qualify”. Whether three have occurred is unknown; the <a href="${esc(href('/ledger/'))}">ledger</a> is empty and no authorized report exists.</li>
<li><strong>Original content:</strong> “All Sites must have robust original content (even when advertising is removed) - a good rule of thumb is at least 10 posts.” This site currently publishes ${guides.length} guides. That is below the rule of thumb, and it is recorded as a known gap rather than argued away ${flagLinks(['FLG-032'])}.</li>
<li><strong>Recency:</strong> “Content on your website must be recent (generally within the last 60 days). You must own your website.” The site states its last review date in the masthead of every page.</li>
<li><strong>Tagged links:</strong> special “tagged” links must be embedded in the Amazon product links on the declared sites. This site carries the tag ${esc(cfg.trackingId)}, but no link has been tested in Associates Central, so attribution is unproven ${flagLinks(['FLG-005'])}.</li>
</ul>
<h2>What the ASIN definition settles</h2>
<p>The same help system defines an ASIN as “the 10-digit code that Amazon uses to denote specific products” and documents the simple text link format <code>amazon.com/dp/ASIN/ref=nosim?tag=YOURASSOCIATEID</code> ${srcLink('S18')}. That resolves the open point behind FLG-001: the five submitted tokens are 9 characters, so none of them is an ASIN, and they cannot be used directly in the documented link format. It does not say the tokens are invalid or non-compliant — that remains FLG-003. ${flagLinks(['FLG-001'])}</p>
<div class="prose"><p class="small">Automated gates are enforced by <code>tools/verify.mjs</code> and re-run by the CI workflow on every push; a failing gate stops the change from being published. The Participation Requirements wording quoted above was read from the official page itself on 2026-11-20, not from a search excerpt.</p></div>`,
});

// Workflow (publishing cadence + who does what)
add({
  path: '/workflow/', title: 'Publishing workflow',
  description: 'How a guide gets made, the cadence register, the pre-publish gates, and the parallel-session coordination rules.',
  body: `<section class="page-head"><p class="kicker">Workflow</p><h1>How a guide gets made</h1><p class="deck">The pipeline from a reader question to a published, source-linked guide, the gates it passes on the way, and the topics actually queued.</p></section>
<div class="prose">
<h2>The cadence, and why it is that slow</h2>
<p>${esc(cadence.cadence.current)}, starting ${esc(dateLong(cadence.cadence.starts))}. ${esc(cadence.cadence.why_this_cadence)}</p>
<p>The cadence changes when a measured trigger fires, not when the schedule feels slow: ${esc(cadence.cadence.measured_trigger_to_change)}</p>
<p>Topics are chosen like this: ${esc(cadence.cadence.how_topics_are_chosen)}</p>
<div class="cadence-stats">
  <div class="flag-stat"><span class="n">${guides.length}</span><span class="l">published</span></div>
  <div class="flag-stat"><span class="n">${cadence.queued.length}</span><span class="l">queued</span></div>
  <div class="flag-stat"><span class="n">${10 - guides.length > 0 ? 10 - guides.length : 0}</span><span class="l">to the 10-post mark</span></div>
</div>
<h2>The queue</h2>
<table class="checklist"><thead><tr><th scope="col">ID</th><th scope="col">Working title</th><th scope="col">Shape</th><th scope="col">Why this one</th><th scope="col">Sources it would need</th></tr></thead><tbody>
${cadence.queued.map((t) => `<tr><td><strong>${esc(t.id)}</strong></td><td><strong>${esc(t.title)}</strong>${t.blocked_by ? `<br><span class="small muted">Open question: ${esc(t.blocked_by)}</span>` : ''}</td><td>${esc(t.shape)}</td><td>${esc(t.why_this_one)}</td><td>${t.sources_needed.map(srcLink).join(', ')}</td></tr>`).join('\n')}
</tbody></table>
<p class="small muted">Working titles are editorial hypotheses. They are not claims about search volume, ranking, or product superiority, and no such claim is made anywhere on this site.</p>
<h2>What this publication will not do</h2>
<ul>
${cadence.not_doing.map((n) => `<li><strong>${esc(n.topic)}.</strong> ${esc(n.why_not)}</li>`).join('\n')}
</ul>
<h2>From question to page</h2>
<ol>
<li><strong>Pick the question.</strong> From measured queries once Search Console is verified (discovery task D-09 ${flagLinks(['FLG-013'])}), and from the queue above before then.</li>
<li><strong>Read the primary sources in full.</strong> The manufacturer's page and the listing, both in full. A guide that cites a search excerpt is not finished.</li>
<li><strong>Write down the conflict.</strong> If two official pages disagree, the guide publishes the disagreement rather than picking a winner. That rule produced most of what is distinctive on this site.</li>
<li><strong>Pass the gates.</strong> The build re-runs <code>tools/verify.mjs</code>: disclosure above the fold, sponsored attributes, tagged links, no prices, every source fetched and dated, sitemap and feed coverage, no broken internal links. A failing check blocks the change (see <a href="${esc(href('/compliance/'))}">Compliance</a>).</li>
<li><strong>Publish and index.</strong> The guide is added to the sitemap and the RSS feed automatically at build time.</li>
</ol>
<h2>Parallel-session coordination</h2>
<p>This repository may be worked on by several agent sessions at once. The shared task board is <code>COORDINATION.md</code> at the repository root: tasks are claimed there, scopes do not overlap, and shared outputs (registers, navigation, the front page) are integrated only by a final integration pass that re-verifies everything. Conflicts are resolved without discarding the other session's work, and the resolution is logged.</p>
<h2>What is automated, and what is not</h2>
<ul>
<li><strong>Automated:</strong> site generation, the compliance gate, the source-freshness gate, link checking, sitemap and feed updates, build-drift detection in CI.</li>
<li><strong>Requires the owner's credentials:</strong> Associates Central link validation (gate G-02 ${flagLinks(['FLG-005'])}), Search Console verification, analytics-endpoint deployment, any ledger import.</li>
<li><strong>Requires a judgment:</strong> which question to answer next, and whether a conflict is worth publishing. Neither is delegated.</li>
</ul>
</div>`,
});

// Privacy notice
add({
  path: '/privacy/', title: 'Privacy notice',
  description: 'What this site collects (currently: nothing), how affiliate links work, and what would change if analytics is turned on.',
  body: `<section class="page-head"><p class="kicker">Privacy</p><h1>Privacy notice</h1><p class="deck">Plain-English version; the technical details live on the <a href="${esc(href('/measurement/'))}">measurement page</a>.</p></section>
<div class="prose">
<h2>What we collect today</h2>
<p>Nothing. No cookies are set by this site, no analytics runs, no data leaves your browser. The measurement script is present but inert: it sends nothing until an analytics endpoint is configured (FLG-009), and it checks your browser's Do Not Track setting before it would ever send anything.</p>
<h2>If measurement is turned on later</h2>
<p>Only five events would be recorded (page views, category views, product views, outbound clicks, and a 75%-read signal on guides), aggregated per day. No cookies, no IP addresses, no user agents, no fingerprinting, no account data, nothing you type. The project rule: if analytics is enabled, this page is updated first, and the change is recorded in the repository history.</p>
<h2>Affiliate links</h2>
<p>Product buttons link to Amazon with our Associates tracking ID (a tag parameter in the URL). Amazon's own systems handle anything that happens after you leave this site; their use of that click is governed by Amazon's privacy practices, not by this notice. We never route clicks through a redirect, and we never see which reader clicked what.</p>
<h2>Questions or requests</h2>
<p>Open an issue in the <a href="https://github.com/karagemop466-tech/Affil3/issues" rel="noopener external">project repository</a>. Corrections are logged on the <a href="${esc(href('/flagged/'))}">Flagged for review</a> page.</p>
</div>`,
});

// About
add({
  path: '/about/', title: 'About and editorial policy',
  description: 'Who writes this site, how products are chosen, how facts are checked, and how to correct them.',
  body: `<section class="page-head"><p class="kicker">About</p><h1>About ${esc(cfg.siteName)}</h1></section>
<div class="prose">
<h2>Who writes it</h2>
<p>${esc(cfg.author)}. No named author or credentials are listed yet (FLG-014). Named authors will appear once a real person is confirmed.</p>
<p>${esc(cfg.brandNote)}</p>
<h2>How products are chosen</h2>
<p>Only the five products submitted by the site owner are listed. No product was added from our own research, and none is ranked or scored, because we have no authorized performance data to rank with.</p>
<h2>How facts are checked</h2>
<p>Each fact on a product row carries a source link to an official page. If a value cannot be confirmed from an official source, the cell stays blank and the row is flagged. We do not infer values. Listing-title specifications (a quart figure, a temperature rating, a preset count) are quoted as claims made by the listing, not as measurements of ours.</p>
<h2>About the illustrations</h2>
<p>${esc(cfg.imageryCredit)}</p>
<h2>Corrections</h2>
<p>If something is wrong, open an issue in the <a href="https://github.com/karagemop466-tech/Affil3/issues" rel="noopener external">project repository</a>. Corrections are logged on the <a href="${esc(href('/flagged/'))}">Flagged for review</a> page.</p>
</div>`,
});

// 404
add({ path: '/404.html', title: 'Page not found', description: 'This page does not exist.', noSitemap: true,
  body: `<section class="page-head"><h1>Page not found</h1><p class="deck">Try the <a href="${esc(href('/'))}">front page</a>, the <a href="${esc(href('/shop/'))}">shop table</a>, or the <a href="${esc(href('/guides/'))}">guides</a>.</p></section>` });

// ---------- outbound link policy ----------
// Program Policies 2(b): the tag must be a URL parameter on every link to an Amazon retail site.
// 6(v),(w): nothing may obscure where a link goes, and a shortener may not hide it — so a link.amazon
// short link is shown as text rather than as a clickable link. Documentation hosts
// (affiliate-program, sell) are references, not retail links, and are left alone.
const DOC_HOSTS = new Set(['affiliate-program.amazon.com', 'sell.amazon.com', 'developer.amazon.com', 'advertising.amazon.com']);
const isRetailAmazon = (host) => /(^|\.)amazon\.com$/.test(host) && !DOC_HOSTS.has(host);
function linkPolicy(html) {
  let out = html;
  // 1. A short link cannot carry the tag: render its anchor as plain code.
  out = out.replace(/<a\b[^>]*href="(https:\/\/link\.amazon\/[^"]*)"[^>]*>([\s\S]*?)<\/a>/g,
    (_m, url, inner) => `<code>${url.replace(/^https:\/\/link\.amazon\//, 'link.amazon/')}</code>`);
  // 2. Every retail Amazon link carries the tag and the sponsored rel.
  out = out.replace(/<a\b([^>]*)>/g, (m, attrs) => {
    const h = (attrs.match(/href="([^"]*)"/) || [])[1];
    if (!h) return m;
    let host = '';
    try { host = new URL(h).hostname; } catch { return m; }
    if (!isRetailAmazon(host)) return m;
    let next = attrs;
    if (!/[?&]tag=/.test(h)) {
      const url = new URL(h);
      url.searchParams.set('tag', cfg.trackingId);
      next = next.replace(/href="[^"]*"/, `href="${esc(url.toString())}"`);
    }
    const rel = (next.match(/rel="([^"]*)"/) || [])[1] || '';
    const parts = rel.split(/\s+/).filter(Boolean);
    if (!parts.includes('sponsored')) parts.push('sponsored');
    if (!parts.includes('noopener')) parts.push('noopener');
    const relAttr = `rel="${parts.join(' ')}"`;
    next = /rel="[^"]*"/.test(next) ? next.replace(/rel="[^"]*"/, relAttr) : `${next} ${relAttr}`;
    return `<a${next}>`;
  });
  return out;
}

// ---------- write ----------
for (const o of OWNED) fs.rmSync(path.join(OUT, o), { recursive: true, force: true });
fs.mkdirSync(OUT, { recursive: true });
const written = [];
for (const p of pages) {
  const file = p.path.endsWith('.html') ? path.join(OUT, p.path) : path.join(OUT, p.path, 'index.html');
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, linkPolicy(page(p)));
  written.push({ path: p.path, file: path.relative(ROOT, file), noSitemap: !!p.noSitemap });
}

// Assets
fs.mkdirSync(path.join(OUT, 'assets'), { recursive: true });
fs.copyFileSync(path.join(ROOT, 'src/assets/style.css'), path.join(OUT, 'assets/style.css'));
fs.copyFileSync(path.join(ROOT, 'src/assets/analytics.js'), path.join(OUT, 'assets/analytics.js'));
fs.cpSync(path.join(ROOT, 'src/assets/img'), path.join(OUT, 'assets/img'), { recursive: true });
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

fs.writeFileSync(path.join(OUT, 'robots.txt'), `User-agent: *\nAllow: /\nDisallow: /legacy/\n\nSitemap: ${abs('/sitemap.xml')}\n`);

console.log(`Built ${written.length} pages, ${feedItems.length} feed items, ${sitemapPages.length} sitemap URLs at the repository root`);
