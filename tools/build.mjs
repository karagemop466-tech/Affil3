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
const OWNED = ['index.html', 'shop', 'compare', 'products', 'categories', 'guides', 'how-we-choose', 'executive-summary', 'sources', 'questions', 'suggestions',
  'flagged', 'ledger', 'measurement', 'compliance', 'about', 'workflow', 'privacy', 'design-brief',
  '404.html', 'feed.xml', 'sitemap.xml', 'robots.txt',
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
  ['/design-brief/', 'Design brief (next redesign)'],
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
const trackName = (id) => {
  const t = (suggestionsDoc.tracks || []).find((x) => x.id === id);
  return t ? t.name : id;
};
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

function page({ title, description, path: p, body, type = 'page', attrs = '', ogType = 'website', jsonld = '', ogImage = '/assets/img/hero.png', scripts = '' }) {
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
${scripts}
</body>
</html>
`;
}

// ---------- components ----------
// A short, shopper-facing spec line for a card: the number a buyer compares on, then the shape.
function specLine(p) {
  const bits = [];
  if (p.capacity_qt) bits.push(`${p.capacity_qt} qt`);
  else if (p.shape) bits.push(p.shape);
  if (p.capacity_qt && p.shape) bits.push(p.shape.toLowerCase());
  if (p.brand && p.brand.toLowerCase() !== (p.short_name || '').toLowerCase()) bits.push(p.brand);
  return bits.join(' · ');
}
function productCard(p, placement) {
  const title = p.name || displayName(p);
  const cat = catName(p.category);
  const note = p.lede || p.editorial_note || '';
  const fit = p.best_for && p.tradeoff ? `<p class="fit-line"><strong>Best for:</strong> ${esc(p.best_for)}<br><strong>Trade-off:</strong> ${esc(p.tradeoff)}</p>` : '';
  // On the front shelf the card is for a reader, so it carries the buyer's comparison line and
  // the product's own summary. The internal row code stays on the Shop table and the product page.
  const readerCard = placement === 'front-shelf';
  const kicker = readerCard ? (specLine(p) || cat) : `${cat} · ${p.id}`;
  if (tagged(p)) {
    return `<article class="card product" data-product-view="${esc(p.id)}">
  ${cardArt(p)}
  <div class="card-body">
    <p class="kicker">${esc(kicker)}</p>
    <h3>${esc(title)}</h3>
    ${note ? `<p class="muted small">${esc(note)}</p>` : ''}
    ${readerCard ? (p.fit_line ? `<p class="fit-line">${esc(p.fit_line)}</p>` : '') : fit}
    ${readerCard ? '' : `<p class="muted small">Observed ASIN <code>${esc(p.observed_asin)}</code></p>`}
    <p><a class="btn" href="${esc(tagged(p))}" rel="sponsored noopener" data-outbound data-product="${esc(p.id)}" data-placement="${esc(placement)}">View on Amazon</a></p>
    ${readerCard ? '' : `<p class="status">${esc(p.outbound_status)}</p>`}
  </div>
</article>`;
  }
  if (p.no_buy_link) {
    return `<article class="card product warn-card" data-product-view="${esc(p.id)}">
  ${cardArt(p)}
  <div class="card-body">
    <p class="kicker">${esc(cat)} · ${esc(p.id)}</p>
    <h3>${esc(p.name || displayName(p))}</h3>
    ${note ? `<p class="muted small">${esc(note)}</p>` : ''}
    <p class="status"><strong>No buy button on this card.</strong> ${esc(p.no_buy_link_reason || 'No manufacturer specification page exists for this model, so nothing here is stood behind yet.')} ${flagLinks(p.flags || [])}</p>
  </div>
</article>`;
  }
  return `<article class="card product warn-card" data-product-view="${esc(p.id)}">
  <div class="card-body">
    <p class="kicker">${esc(cat)} · ${esc(p.id)}</p>
    <h3>Link not resolved</h3>
    <p class="muted small">Submitted link: <code>${esc(p.submitted_token)}</code></p>
    <p class="status">No buy link is published. The link has not resolved to a product page in a verified session. An Amazon "Continue shopping" checkpoint is intermittent and is not by itself evidence that a link is dead. ${flagLinks(['FLG-004'])}</p>
  </div>
</article>`;
}

// A note that sits under the specification grid when the manufacturer page and the listing are
// about the same product but do not name it the same way. It is the difference between a
// confirmed specification and a family-page figure, so it is stated in full.
function matchNote(p) {
  if (!p.model_match_note) return '';
  return `<aside class="note-box"><p><strong>Read this before you compare the numbers.</strong> ${esc(p.model_match_note)}</p><p class="small">${flagLinks(p.flags || [])}</p></aside>`;
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
    // A table cell may end with a source citation like "(S10)" or "(S11, S23)". The IDs are
    // turned into links to the source register, so every row's evidence is one click away
    // and the citation can never drift away from the register entry it names.
    case 'table': return `<div class="table-wrap"><table class="checklist"><thead><tr>${b.headers.map((h) => `<th scope="col">${esc(h)}</th>`).join('')}</tr></thead><tbody>${b.rows.map((r) => `<tr>${r.map((c) => `<td>${citeCell(c)}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
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

// Row-level sources. S04 and S05 are register-wide records standing for "the observed listing"
// and "the submitted token"; the row's own values live in observed_final_url and submitted_token.
// Rendering the row's own values here is what stops a row citing a sibling product's page.
const rowSources = (p) => (p.sources || []).map((id) => {
  if (id === p.submitted_source_id) {
    return `<code>link.amazon/${esc(p.submitted_token)}</code> <span class="small muted">(submitted token, owner input)</span>`;
  }
  if (id === p.observed_source_id && p.observed_final_url) {
    return `${ext(p.observed_final_url, id, '')} <span class="small muted">(this row's observed listing)</span>`;
  }
  return srcLink(id);
}).join(' · ');
const guideSource = (id) => (id === 'S04'
  ? `<a href="${esc(href('/shop/'))}">S04</a> · observed Amazon product pages, one per row on the Shop table`
  : `${srcLink(id)} · ${esc(SOURCES[id] ? SOURCES[id].title : '')}`);

// The source list under a product: the row's own observed listing, its own submitted token, and
// the maker pages behind the specification grid. Every entry points at that exact source.
const productSourceList = (p) => {
  const ids = [...(p.sources || []), ...(p.spec_sources || []).filter((id) => !(p.sources || []).includes(id))];
  return ids.map((id) => {
    if (id === p.submitted_source_id) {
      return `<li><strong>${esc(id)}</strong> — <code>link.amazon/${esc(p.submitted_token)}</code> · ${esc(SOURCES[id] ? SOURCES[id].title : '')} <span class="small muted">(owner-supplied input for this row; shown as text, never as a published link)</span></li>`;
    }
    if (id === p.observed_source_id && p.observed_final_url) {
      const rec = SOURCES[id] || {};
      return `<li><strong>${esc(id)}</strong> — ${ext(p.observed_final_url, 'observed Amazon listing', '')} · ${esc(rec.title || '')} <span class="small muted">(this row's own listing, observed ${esc(dateLong(p.observed_date))})</span></li>`;
    }
    const rec = SOURCES[id];
    if (!rec) return `<li><strong>${esc(id)}</strong> — <span class="muted">missing from the source register</span></li>`;
    return `<li><strong>${esc(id)}</strong> — ${rec.url ? ext(rec.url, 'open source', '') : '<span class="muted">no link recorded</span>'} · ${esc(rec.title || '')}</li>`;
  }).join('');
};

const cellText = (v) => (v === '' || v == null ? '<span class="blank" aria-label="blank: unverified">&nbsp;</span>' : esc(v));

// Render a table cell, linking any source IDs it cites. The text is escaped first, then the
// citation markers are replaced with anchors, so no raw text can inject markup.
const citeCell = (c) => {
  const text = esc(c === undefined || c === null ? '' : String(c));
  return text.replace(/\((S\d\d(?:,\s*S\d\d)*)\)/g, (m, ids) => {
    const links = ids.split(/,\s*/).map((id) => {
      const rec = SOURCES[id.trim()];
      if (!rec) return `<span class="badge bad">${esc(id.trim())} (missing)</span>`;
      return `<a class="cite" href="${esc(href('/sources/'))}#${esc(id.trim())}">${esc(id.trim())}</a>`;
    }).join(', ');
    return `(${links})`;
  });
};

// ---------- pages ----------
const pages = [];
const add = (p) => pages.push(p);

// Home (publication front page: products first)
{
  const shelf = products.map((p) => productCard(p, 'front-shelf')).join('\n');
  const quickPick = products.map((p) => `<div class="qp-item">
  <p class="qp-product">${esc(p.short_name)}</p>
  <p class="qp-fit">${esc(p.fit_line)}</p>
  <p class="qp-links"><a class="btn" href="${esc(p.tagged_outbound_url)}" rel="sponsored noopener" data-outbound data-product="${esc(p.id)}" data-placement="front-quickpick">View on Amazon</a> · <a href="${esc(href('/guides/' + p.guide_slug + '/'))}">${esc(p.guide_title)}</a></p>
</div>`).join('\n');
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
    <h2>The shortlist</h2>
    <p>Five kitchen appliances, each one traced to the Amazon listing it actually lands on and to the manufacturer's own specification page. Where the two disagree, the disagreement is written down instead of smoothed over. Pick a shape, then read the guide that matches your kitchen.</p>
  </div>
  <div class="picks"><div class="shelf">${shelf}</div></div>
  <p class="shelf-note">Buttons open Amazon with our tracking ID in the link, and every one is marked sponsored. We do not publish prices or ratings, so nothing here goes stale. Want them side by side first? <a href="${esc(href('/compare/'))}">Compare all five in one table</a>. Sources are on every product page, in the <a href="${esc(href('/sources/'))}">source register</a>, and the open questions are on <a href="${esc(href('/flagged/'))}">Flagged for review</a>.</p>
</section>
<section class="band band-alt">
  <div class="band-head">
    <h2>Not sure which one? Pick by how you cook</h2>
    <p>One line per product, and the guide that matches your kitchen.</p>
  </div>
  <div class="quick-pick">${quickPick}</div>
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
    <h2>How we review</h2>
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
  add({
    path: '/shop/', title: 'Shop: all submitted products and findings',
    description: 'Every submitted product row: intended ASIN and listing fields (blank where unverified), observed redirect destinations kept separate, sources and flags.',
    body: `
<section class="page-head">
  <p class="kicker">Shop · 5 rows</p>
  <h1>All submitted products</h1>
  <p class="deck">One row per submitted link. <strong>Intended</strong> fields come only from an official source; none are confirmed yet, so they are blank. <strong>Observed</strong> fields are what the Amazon page showed on 2026-11-20 and are kept separate.</p>
</section>
<section>
  ${table(['ID', 'Category', 'Observed title and breadcrumb', 'Observed ASIN and page', 'Submitted link', 'Intended ASIN', 'Official listing URL', 'Confirmation date', 'Confirmation source', 'Buy link status', 'Confirmation status', 'Sources (official)'], rows, 'wide')}
</section>
<section class="band">
  <h2>What the table shows</h2>
  <ul class="findings">
    <li>All five submitted tokens are 9 characters. The observed Amazon product IDs are 10 characters. ${flagLinks(['FLG-001'])}</li>
    <li>${resolvedCount === 5 ? 'All five' : resolvedCount + ' of five'} short links resolved to a product page, and each product ID differs from the token in its link.${resolvedCount < 5 ? ' ' + unanswered.map((p) => `<code>${esc(p.submitted_token)}</code> has not resolved in a verified session, so no product is shown and no buy link is published. ${flagLinks(['FLG-004'])}`).join(' ') : ''} ${flagLinks(['FLG-002'])}</li>
    <li>Two destinations were transposed in an earlier register revision and were corrected after a retest; an independent fetch during the polish pass corroborated the corrected mapping. ${flagLinks(['FLG-022', 'FLG-028'])}</li>
    <li>${taggedCount} tagged ${taggedCount === 1 ? 'link is' : 'links are'} published with the tracking ID ${esc(cfg.trackingId)}. None has been tested in Associates Central. ${flagLinks(['FLG-005'])}</li>
    <li>The short links' compliance status is unresolved, not invalid. ${flagLinks(['FLG-003'])}</li>
    <li>No price, rating or availability is recorded. ${flagLinks(['FLG-016'])}</li>
  </ul>
</section>`,
  });
}

// Side-by-side comparison: the five products on published specifications only. A blank cell
// means the maker does not publish that figure; it is never filled in from another source.
{
  const specRow = (label, fn) => [label, ...products.map((p) => {
    const v = fn(p);
    return v ? esc(v) : '<span class="blank" aria-label="blank: not stated by the maker">&nbsp;</span>';
  })];
  const rows = [
    specRow('Shape', (p) => p.shape),
    specRow('Capacity', (p) => (p.capacity_qt ? `${p.capacity_qt} qt` : '')),
    specRow('Temperature', (p) => (p.temp_min_f && p.temp_max_f ? `${p.temp_min_f}–${p.temp_max_f} °F` : (p.temp_max_f ? `up to ${p.temp_max_f} °F` : ''))),
    specRow('Power', (p) => (p.power_w ? `${p.power_w} W` : '')),
    specRow('Voltage', (p) => p.voltage),
    specRow('Size', (p) => (p.dimensions_in ? `${p.dimensions_in} in` : '')),
    specRow('Weight', (p) => (p.weight_lb ? `${p.weight_lb} lb` : '')),
    specRow('Dishwasher', (p) => p.dishwasher_safe),
    specRow('Certified', (p) => p.certification),
    specRow('Warranty', (p) => p.warranty),
    specRow('Best for', (p) => p.best_for),
    specRow('Trade-off', (p) => p.tradeoff),
  ];
  const header = ['Specification', ...products.map((p) =>
    `<a href="${esc(href('/products/' + p.slug + '/'))}">${esc(p.short_name || p.name)}</a>`)];
  const buyRow = ['Buy', ...products.map((p) => tagged(p)
    ? `<a class="btn" href="${esc(tagged(p))}" rel="sponsored noopener" data-outbound data-product="${esc(p.id)}" data-placement="compare">View on Amazon</a>`
    : '<span class="muted small">No buy link published</span>')];
  add({
    path: '/compare/', title: 'Compare the five products side by side',
    description: 'The five submitted products on published specifications only. Blank cells mean the maker does not publish that figure.',
    body: `
<section class="page-head">
  <p class="kicker">Compare · 5 products</p>
  <h1>The five, side by side</h1>
  <p class="deck">Every figure below comes from the manufacturer's own specification page, or from the Amazon listing title where the maker publishes no page. A blank cell means the maker does not publish that number. Nothing here is filled in, and nothing is ranked.</p>
</section>
<section>
  ${table(header, [...rows, buyRow], 'wide')}
</section>
<section class="band">
  <h2>Where the sources disagree</h2>
  <ul class="findings">
    <li>The Emeril 26-quart oven-style fryer is listed by Amazon with 24 presets and by Emeril's own page with 25. Both numbers are published on its product page and the row is flagged. ${flagLinks(['FLG-023'])}</li>
    <li>The ThermoMaven listing does not name a model. The figures in its column are the manufacturer's published figures for the F1 Ace family, which matches the listing title feature for feature. They are labelled as family-page figures, not confirmed specifications of the listed unit. ${flagLinks(['FLG-025'])}</li>
    <li>The Chefman 8-quart listing and its maker's page agree on the model number and the temperature range, but disagree on wattage (1000 W vs 1700 W) and case size. The maker's figures are published and both differences are named. ${flagLinks(['FLG-026', 'FLG-027'])}</li>
  </ul>
</section>
<section class="band">
  <h2>How to read this table</h2>
  <p>Capacity is not a shared unit across these five: three are ovens with baskets, one is a handheld probe, and one is a wireless leave-in probe. The table compares what each maker publishes; it does not say which one to buy. For that, start with the question that matches your kitchen: <a href="${esc(href('/guides/'))}">the guides</a> are written as questions, and each one names the products it covers.</p>
</section>`,
  });
}

// Categories index + category pages
add({
  path: '/categories/', title: 'Categories',
  description: 'Product categories and the guides that cover each one.',
  body: `<section class="page-head"><p class="kicker">Categories</p><h1>Browse by category</h1><p class="deck">${CATEGORIES.length} clusters. Each cluster lists its products and the guides that cover them.</p></section>
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
  const jsonld = `<script type="application/ld+json">${JSON.stringify({
    '@context': 'https://schema.org', '@type': 'Article', headline: g.title, description: g.description,
    image: abs(g.image),
    datePublished: g.date, dateModified: cfg.lastReviewed, author: { '@type': 'Organization', name: cfg.author },
    publisher: { '@type': 'Organization', name: cfg.siteName }, mainEntityOfPage: abs(`/guides/${g.slug}/`),
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
  })}</script>`;
  const conflictTable = (() => {
    if (!p.observed_specs) return '';
    // Only rows a reader can compare. A row where one column is silent is an absence,
    // not a disagreement, and the spec grid above already shows it. Units are normalised
    // before comparing so "8 quarts" and "8 qt" are not reported as a conflict.
    const sais = (v) => !!v && !/^(?:not stated|n\/a|—|-)$/i.test(String(v).trim());
    const norm = (v) => String(v).toLowerCase()
      .replace(/\bquarts?\b/g, 'qt').replace(/\binches?\b/g, 'in')
      .replace(/\s+/g, '').replace(/(\d)(in|qt|w|v|°f)\b/g, '$1 $2');
    const LABEL = { model: 'Model', power: 'Power', temperature: 'Temperature', dimensions: 'Case size', capacity: 'Capacity', material: 'Finish' };
    const mine = {
      model: p.model,
      power: p.power_w ? `${p.power_w} W / ${p.voltage || ''}`.trim() : '',
      temperature: p.temp_min_f && p.temp_max_f ? `${p.temp_min_f}-${p.temp_max_f} °F` : (p.temp_max_f ? `up to ${p.temp_max_f} °F` : ''),
      dimensions: p.dimensions_in ? `${p.dimensions_in} in` : '',
      capacity: p.capacity_qt ? `${p.capacity_qt} qt` : '',
      material: p.material || '',
    };
    const rows = ['model', 'power', 'temperature', 'dimensions', 'capacity', 'material']
      .filter((k) => sais(p.observed_specs[k]) && sais(mine[k]))
      .map((k) => [LABEL[k], esc(p.observed_specs[k]), `<span class="muted">${esc(mine[k])}</span>`,
        norm(p.observed_specs[k]) === norm(mine[k]) ? '<span class="badge good">agrees</span>' : '<span class="badge flag">differs</span>']);
    const extras = Object.entries(p.observed_specs_extra || {}).map(([k, v]) => {
      const label = ({ display: 'Display', waterproof: 'Water resistance', certification: 'Certification', newer_model: 'Newer model' })[k] || k;
      const [listingSays, makerSays] = String(v).split(' vs ');
      return [label, esc(listingSays),
        makerSays ? `<span class="muted">${esc(makerSays).replace(/ \(listing\)$| \(manufacturer\)$/, '')}</span>`
                  : '<span class="muted">the maker publishes no successor notice</span>',
        k === 'newer_model' ? '<span class="badge flag">check before buying</span>' : '<span class="badge flag">differs</span>'];
    });
    if (!rows.length && !extras.length) return '';
    return `
<section class="band">
  <h2>Where the listing and the maker disagree</h2>
  <p>Both columns describe the same product. A retailer listing and a manufacturer page are two different
  claims about one object, so where they part company the gap is shown rather than averaged away. Nothing
  in the right-hand column came from the listing.</p>
  ${table(['Field', 'The listing states', 'The maker states', ''], [...rows, ...extras])}
  <p class="small">${flagLinks((p.flags || []).filter((f) => !['FLG-001', 'FLG-002', 'FLG-022', 'FLG-028', 'FLG-029'].includes(f)))}</p>
</section>`;
  })();
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
  ${matchNote(p)}
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
  <ul>${productSourceList(p)}</ul>
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
<li>A publication-style site with a products-first front page, a shop table, a side-by-side comparison page, ${CATEGORIES.length} category clusters, ${guides.length} question-led guides, disclosed editorial imagery, an RSS feed and a sitemap.</li>
<li>Dashboards for sources, questions, suggestions, flagged items, the campaign ledger (empty), measurement, compliance, the publishing workflow, and a privacy notice. All are linked from the footer.</li>
<li>A disclosure strip under the masthead on every page, repeated in the footer, using the statement required by Operating Agreement §5.</li>
<li>A privacy-preserving click counter in the browser and a self-hostable collector. The collector is inactive on the live site until an endpoint is set (FLG-009).</li>
<li>Automated checks (tools/verify.mjs) for disclosure presence, sponsored attributes, tags, sources, sitemap and feed coverage, and internal links, plus a CI workflow that re-runs the build and the gate on every push.</li>
</ul>
<h2>What is verified</h2>
<ul>
<li>The Associates disclosure statement, the Special Link and tag rules, and the anti-cloaking clause are read from the official Associates pages (S01, S02).</li>
<li>The rel="sponsored" guidance (S06), FTC disclosure guidance (S07, S08), and USDA temperatures (S10, S20) are read from official pages.</li>
<li>For each product, the observed Amazon ASIN, title and breadcrumb are read from the amazon.com page the link resolved to on 2026-11-20 (S04, S05).</li>
<li>An Amazon-owned ASIN definition has been located in Associates Central help (S18, excerpt; manual re-check pending, FLG-012).</li>
<li>The ThermoMaven manufacturer page was located on 2026-11-20 (S21). It states a 1-second instant read, NIST-certified ±0.5 °F accuracy, a 100% waterproof design and a lifetime warranty, matching the listing title feature for feature. The row now carries a buy button and a sourced specification set, labelled as family-page figures until the listing's model field confirms the F1 Ace (FLG-025, Q-14).</li>
</ul>
<h2>What is not verified, and why</h2>
<ul>
<li>The intended ASIN, official listing URL, confirmation date and source are blank for all five products. The submitted tokens are 9 characters, and the observed destinations differ from the tokens (FLG-001, FLG-002).</li>
<li>Two destinations were transposed in an earlier register revision and corrected after a retest, and one link first hit an intermittent checkpoint page before resolving (FLG-004, FLG-022, FLG-028). Manufacturer-page cross-checks added FLG-023 to FLG-027. Two of those were themselves corrected in a later pass: the ThermoMaven unit does have a maker page, which had been missed (FLG-025), and the Chefman 8 Qt conflict had been measured against the wrong Chefman page and is really a wattage and case-size difference (FLG-026). A 2026-11-20 re-fetch of two short links returned the Amazon home page rather than a product page, which is the same intermittent behaviour and does not establish that any link is dead (FLG-031). The status of the supplied short links is unresolved, not invalid (FLG-003).</li>
<li>No Special Link has been tested in Associates Central. The sandbox has no Associates login (FLG-005, gate G-02).</li>
<li>No prices, ratings, sales or commission figures are shown. The campaign ledger is empty and no conversion score or revenue forecast is presented.</li>
<li>Several reader-facing editions of this project are published under one domain. Only this root publication is in the sitemap; the others are excluded from the index and listed on the archive page (FLG-032, Q-15, S-11).</li>
</ul>
<h2>Evidence needed before expanding</h2>
<ol>
<li>Use the original enrolled link-generation record or campaign brief to confirm intended products separately from observed redirects (Q-01).</li>
<li>Confirm the account declares this site and that tracking ID shopnow047c-20 is on the account (Q-03, FLG-011).</li>
<li>Run gate G-02 in Associates Central for each product. Record the destination and tracking report separately from site click data (Q-04).</li>
<li>Choose options on the <a href="${esc(href('/suggestions/'))}">Suggestions</a> page. Nothing there is implemented until you choose.</li>
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
${suggestionsDoc.how_to_use ? `<section class="band"><h2>How to read this board</h2><p>${esc(suggestionsDoc.how_to_use)}</p></section>` : ''}
${suggestionsDoc.tracks && suggestionsDoc.tracks.length ? `<section class="band"><h2>The tracks</h2>
<p class="muted small">These are the groups the rows fall into, in the order they unblock each other. Each card below names the track it belongs to.</p>
<div class="findings">
${suggestionsDoc.tracks.map((t) => `<li><strong>${esc(t.name)}</strong> — ${esc(t.why)}</li>`).join('\n')}
</div>
</section>` : ''}
${suggestionsDoc.sequence && suggestionsDoc.sequence.length ? `<section class="band"><h2>The order to decide them in</h2>
<p class="muted small">This is the sequence the register proposes, with the reason each step comes before the next.</p>
${table(['Order', 'Decision', 'Why it comes here'], suggestionsDoc.sequence.map((st) => [
  String(st.order),
  `<a href="#${esc(st.id)}"><strong>${esc(st.id)}</strong></a>`,
  esc(st.why),
]), 'wide')}
</section>` : ''}
<div data-decision-board>
<div class="choice-grid">
${suggestionsDoc.suggestions.map((s) => `<section class="choice-card" id="${esc(s.id)}">
  <p class="kicker">${esc(s.id)} · ${esc(s.topic)}${s.track ? ` · ${esc(trackName(s.track))}` : ''}</p>
  <p class="choice-current">Current: <span class="badge">${esc(s.current)}</span></p>
  <ul class="opts">${s.options.map((o) => `<li><strong>${esc(o.id)}.</strong> ${esc(o.label)}<br><span class="muted small">Tradeoff: ${esc(o.tradeoff)}</span></li>`).join('')}</ul>
  <p class="choice-rec"><strong>Session recommendation:</strong> ${esc(s.recommendation)}</p>
</section>`).join('\n')}
</div>
</div>
<section class="band"><h2>Your decision draft</h2>
<p>Pick an option on each card you want to change and the draft below updates. It is a note for you to paste elsewhere — nothing is sent, stored or implemented by this page.</p>
<p class="small muted" data-decision-status>Updated from your selections above.</p>
<textarea data-decision-output rows="12" readonly aria-label="Decision draft"></textarea>
<p><button class="btn btn-ghost" type="button" data-decision-copy>Copy the draft</button></p>
</section>
<section class="band"><h2>How to choose</h2><p>Reply with the suggestion ID and option letter (for example “S-03 B”). Only the choices you name are implemented; the site keeps showing the current option for everything else. Decisions that need your credentials first are listed on the <a href="${esc(href('/questions/'))}">questions page</a>.</p></section>`,
  scripts: '<script src="' + href('/assets/decision.js') + '" defer></script>',
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
    ['G-13', "Specifications cross-checked against the maker's own pages; conflicts flagged, never smoothed over", 'Manufacturer-page register (S11–S15, S21, S23) + retest', 'Passed — conflicts published (FLG-023…FLG-027)'],
  ])}
<div class="prose"><p class="small">Automated gates are enforced by <code>tools/verify.mjs</code> and re-run by the CI workflow on every push; a failing gate stops the change from being published. Source wording for §2 of the Participation Requirements was read from search excerpts of the official page, and should be re-checked (see the source register).</p></div>`,
});

// Workflow (publishing cadence + who does what)
add({
  path: '/workflow/', title: 'Publishing workflow',
  description: 'How a guide gets made, the cadence, the pre-publish gates, and the parallel-session coordination rules.',
  body: `<section class="page-head"><p class="kicker">Workflow</p><h1>How a guide gets made</h1><p class="deck">The pipeline from a reader question to a published, source-linked guide, and the gates it passes on the way.</p></section>
<div class="prose">
<h2>The cadence</h2>
<p>Current proposal: one new guide every two weeks (suggestion S-05 option A). A faster cadence or a pre-review batch of ten posts are on the decision board; nothing changes until you choose. At the current count, the site has ${guides.length} original guides — below the “at least 10 posts” rule of thumb Amazon's application-review help page mentions (S19, FLG-007). Guide count alone does not establish approval.</p>
<h2>From question to page</h2>
<ol>
<li><strong>Pick the question.</strong> The next topic comes from measured queries once analytics is on (S-03); until then, from the buyer questions in our guides' comments of fact — the decision board tracks this (S-02, Q-09).</li>
<li><strong>Answer it honestly.</strong> Facts come from official sources only (the observed listings on the Shop table, USDA food-safety pages, Amazon's own help pages). Opinion and reasoning are labeled as such.</li>
<li><strong>Link every claim.</strong> Each guide's Sources section lists the exact source IDs used; the <a href="${esc(href('/sources/'))}">source register</a> records how each one was checked.</li>
<li><strong>Pass the gates.</strong> The build re-runs <code>tools/verify.mjs</code>: disclosure above the fold, sponsored attributes, tagged links, no prices, sitemap and feed coverage, no broken internal links. A failing check blocks the change (see <a href="${esc(href('/compliance/'))}">Compliance</a>).</li>
<li><strong>Publish and index.</strong> The new guide is added to the sitemap and the RSS feed automatically at build time. Search Console submission is an owner step (FLG-013, SG-29).</li>
</ol>
<h2>Parallel-session coordination</h2>
<p>This repository may be worked on by several agent sessions at once. The shared task board is <code>COORDINATION.md</code> at the repository root: tasks are claimed there, scopes do not overlap, and shared outputs (registers, navigation, the front page) are integrated only by a final integration pass that re-verifies everything. Conflicts are resolved without discarding the other session's work, and the resolution is logged.</p>
<h2>What is automated, and what is not</h2>
<ul>
<li>Automated: site generation, the compliance gate, link checking, sitemap/feed updates, drift detection in CI.</li>
<li>Human-gated: Associates Central link validation (G-02), Search Console verification, analytics-endpoint deployment, option choices on the decision board, any ledger import.</li>
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

// ---------------- DESIGN BRIEF ----------------
// Re-added by session 66f2548a after the second main advance dropped it. Rendered from
// data/design-brief.json, and DESIGN-BRIEF.md is written from the same object in the write step,
// so the page and the markdown file cannot disagree.
{
  const db = read('data/design-brief.json');
  add({
    path: '/design-brief/', title: 'Design brief: making this read like a publication',
    description: 'The brief to hand whoever designs this site next: diagnosed problems with evidence and where each now stands, invariants no art direction may relax, prescriptions with before-and-after copy, a forbidden list, a sequence, and the prompt itself.',
    body: `<section class="page-head"><p class="kicker">Design brief · ${db.diagnosis.length} problems · ${db.invariants.length} invariants · ${db.prescriptions.length} prescriptions</p>
<h1>${esc(db.title)}</h1>
<p class="deck">${esc(db.purpose)}</p>
<p class="note">${esc(db.status)}</p></section>
<section class="band"><h2>What was wrong, with evidence</h2>
<p class="muted small">Several of these were fixed while this brief was being written, by this branch and by others working in parallel. Each row says so where it applies; a diagnosis that quietly stops being true is as bad as one that was never accurate.</p>
${db.diagnosis.map((x) => `<article class="flag-card" id="${esc(x.id)}">
<p class="flag-head"><span class="badge">${esc(x.id)}</span> <strong>${esc(x.problem)}</strong>${x.fixed ? ' <span class="badge good">addressed</span>' : ''}</p>
<p><strong>Evidence.</strong> ${esc(x.evidence)}</p>
${x.fixed ? `<p class="small muted"><strong>Where it stands now.</strong> ${esc(x.fixed)}</p>` : ''}
<p class="small muted"><strong>Why it reads as generated.</strong> ${esc(x.why_it_reads_as_generated)}</p>
</article>`).join('\n')}</section>
<section class="band"><h2>Invariants: what no redesign may change</h2>
<p class="small muted">Each is either enforced by the build gate or required by the Associates Program Policies and Operating Agreement. An art direction that breaks one is not a bolder art direction, it is a failed build.</p>
<ol class="invariants">${db.invariants.map((i) => `<li>${esc(i)}</li>`).join('\n')}</ol></section>
<section class="band"><h2>Prescriptions</h2>
${db.prescriptions.map((x) => `<article class="flag-card" id="${esc(x.id)}">
<p class="flag-head"><span class="badge">${esc(x.id)}</span> <strong>${esc(x.area)}</strong> <span class="badge">${esc(x.effort)}</span></p>
<p><strong>Rule.</strong> ${esc(x.rule)}</p>
<p class="beforeafter"><span class="ba-label">Before</span> ${esc(x.before)}</p>
<p class="beforeafter"><span class="ba-label">After</span> ${esc(x.after)}</p>
<p class="small muted"><strong>Checkable?</strong> ${esc(x.checkable)}</p>
</article>`).join('\n')}</section>
<section class="band"><h2>Forbidden</h2>
<p class="small muted">Patterns that make copy read as machine-written. The last one is the test that matters.</p>
<ul class="forbidden">${db.forbidden.map((f) => `<li>${esc(f)}</li>`).join('\n')}</ul></section>
<section class="band"><h2>Sequence</h2>
${table(['Step', 'Do this', 'Depends on'], db.sequence.map((s) => [String(s.step), esc(s.do), esc(s.depends || '—')]), 'wide')}</section>
<section class="band"><h2>The prompt to hand the next session</h2>
<p class="small muted">Also written to <code>DESIGN-BRIEF.md</code> in the repository from this same JSON document, so the page and the file cannot drift apart.</p>
<pre class="prompt-block">${esc(db.prompt)}</pre></section>`,
  });
}

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
fs.copyFileSync(path.join(ROOT, 'src/assets/decision.js'), path.join(OUT, 'assets/decision.js'));
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

fs.writeFileSync(path.join(OUT, 'robots.txt'), `User-agent: *\nAllow: /\nDisallow: /editorial/\nDisallow: /legacy/\nDisallow: /crisp-index/\n\nSitemap: ${abs('/sitemap.xml')}\n`);

// DESIGN-BRIEF.md is generated from the same object that renders /design-brief/, so the markdown
// file and the published page cannot disagree. That is the principle behind S-14 applied to itself.
{
  const db = read('data/design-brief.json');
  const L = [];
  L.push(`# ${db.title}`, '');
  L.push(`> Generated from \`data/design-brief.json\` by \`tools/build.mjs\`. The published page is`);
  L.push(`> \`${cfg.siteUrl}/design-brief/\`. Edit the JSON and rebuild; do not edit this file directly.`, '');
  L.push(db.purpose, '');
  L.push(`**Status:** ${db.status}`, '');
  L.push('## What was wrong, with evidence', '');
  L.push('Several of these were fixed while this brief was being written, by this branch and by others');
  L.push('working in parallel. Each row says so where it applies; a diagnosis that quietly stops being');
  L.push('true is as bad as one that was never accurate.', '');
  for (const x of db.diagnosis) {
    L.push(`### ${x.id}. ${x.problem}${x.fixed ? ' — addressed' : ''}`, '');
    L.push(`**Evidence.** ${x.evidence}`, '');
    if (x.fixed) L.push(`**Where it stands now.** ${x.fixed}`, '');
    L.push(`**Why it reads as generated.** ${x.why_it_reads_as_generated}`, '');
  }
  L.push('## Invariants: what no redesign may change', '');
  L.push('Each of these is either enforced by `tools/verify.mjs` or required by the Associates Program');
  L.push('Policies and Operating Agreement. An art direction that breaks one is not a bolder art');
  L.push('direction, it is a failed build.', '');
  db.invariants.forEach((i, n) => L.push(`${n + 1}. ${i}`));
  L.push('', '## Prescriptions', '');
  for (const x of db.prescriptions) {
    L.push(`### ${x.id}. ${x.area}`, '');
    L.push(`**Rule.** ${x.rule}`, '');
    L.push(`- **Before.** ${x.before}`);
    L.push(`- **After.** ${x.after}`);
    L.push(`- **Effort.** ${x.effort}`);
    L.push(`- **Checkable?** ${x.checkable}`, '');
  }
  L.push('## Forbidden', '');
  L.push('Patterns that make copy read as machine-written. The last one is the test that matters.', '');
  db.forbidden.forEach((f) => L.push(`- ${f}`));
  L.push('', '## Sequence', '', '| Step | Do this | Depends on |', '|---|---|---|');
  db.sequence.forEach((st) => L.push(`| ${st.step} | ${st.do.replace(/\|/g, '\\|')} | ${st.depends || '—'} |`));
  L.push('', '## The prompt to hand the next session', '', '```', db.prompt, '```', '');
  fs.writeFileSync(path.join(ROOT, 'DESIGN-BRIEF.md'), L.join('\n'));
}

console.log(`Built ${written.length} pages, ${feedItems.length} feed items, ${sitemapPages.length} sitemap URLs at the repository root`);
