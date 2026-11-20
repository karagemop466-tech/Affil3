#!/usr/bin/env node
// Static site generator for Affil3 — an editorial buying guide.
// No dependencies. Reads data/*.json and src/assets, writes the site at the repo root.
// Run: node tools/build.mjs   (then node tools/verify.mjs)
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const OUT = ROOT;
const OWNED = ['index.html', 'shop', 'products', 'categories', 'guides', 'how-we-choose', 'executive-summary',
  'sources', 'questions', 'suggestions', 'flagged', 'ledger', 'measurement', 'compliance', 'about',
  '404.html', 'feed.xml', 'sitemap.xml', 'robots.txt', 'assets/style.css', 'assets/analytics.js', '.nojekyll'];

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
  { slug: 'air-fryers', name: 'Air fryers', tagline: 'Basket-style, with the drawer you shake',
    blurb: 'Basket air fryers, chosen for the number of drawers and the room they take on the counter.',
    guide: 'basket-or-oven-style-air-fryer-what-should-you-compare' },
  { slug: 'air-fryer-ovens', name: 'Countertop ovens', tagline: 'Doors, racks and a whole meal at once',
    blurb: 'Oven-style air fryers and toaster ovens: bigger footprint, more levels, more at once.',
    guide: 'questions-to-ask-before-buying-a-multi-function-kitchen-appliance' },
  { slug: 'cooking-thermometers', name: 'Thermometers', tagline: 'The number that decides when to pull it',
    blurb: 'Instant-read spot checks and leave-in wireless probes, with the USDA targets that go with them.',
    guide: 'is-your-meat-thermometer-telling-you-the-right-number' },
];
const catOf = (slug) => CATEGORIES.find((c) => c.slug === slug) || { name: slug, blurb: '' };
const inCat = (slug) => products.filter((p) => p.category === slug);

const PRODUCT_IMAGE = {
  P01: 'hero-counter.jpg',
  P02: 'oven-french-door.jpg',
  P03: 'basket-turbofry-8qt.jpg',
  P04: 'thermometer-instant-read.jpg',
  P05: 'hero-thermometer.jpg',
};
const GALLERY = [
  { file: 'guide-cleanup.jpg', alt: 'A clean air fryer basket and crisper tray drying on a linen towel beside a soft brush.' },
  { file: 'guide-basket-vs-oven.jpg', alt: 'A basket air fryer of fries next to a countertop oven holding roasted vegetables.' },
  { file: 'guide-questions.jpg', alt: 'A kitchen table with a blank notebook, a mug and a whole chicken waiting to be cooked.' },
];

const DASHBOARDS = [
  ['/executive-summary/', 'Executive summary'],
  ['/shop/', 'The full comparison table'],
  ['/sources/', 'Source register'],
  ['/questions/', 'Open questions'],
  ['/suggestions/', 'Suggestions to review'],
  ['/flagged/', 'Flagged for review'],
  ['/ledger/', 'Campaign ledger'],
  ['/measurement/', 'Measurement'],
  ['/compliance/', 'Disclosure and compliance'],
  ['/about/', 'About and corrections'],
];
const NAV = [
  ['/shop/', 'The picks'],
  ['/guides/', 'Buying guides'],
  ['/categories/', 'Categories'],
  ['/about/', 'How we choose'],
];

// ---------- helpers ----------
const esc = (s = '') => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const href = (p) => cfg.basePath + p;
const abs = (p) => cfg.siteUrl + p;
const asset = (p) => cfg.basePath + '/assets/' + p;
const hostOf = (u) => { try { return new URL(u).hostname; } catch { return ''; } };
const isAmazon = (u) => /(^|\.)amazon\.com$/.test(hostOf(u)) || hostOf(u) === 'link.amazon';
const relFor = (u) => (isAmazon(u) ? 'sponsored noopener' : 'noopener external');
const ext = (u, text, attrs = '') => `<a href="${esc(u)}" rel="${relFor(u)}"${attrs}>${esc(text)}</a>`;
const srcLink = (id) => {
  const s = SOURCES[id];
  if (!s) return `<span class="badge bad">${esc(id)} missing</span>`;
  return s.url ? `<a href="${esc(s.url)}" rel="${relFor(s.url)}">${esc(id)}</a>` : `<span>${esc(id)}</span>`;
};
const flagLinks = (ids = []) => ids.map((f) => `<a class="badge flag" href="${href('/flagged/')}#${esc(f)}">${esc(f)}</a>`).join(' ');
const dateLong = (iso) => new Date(iso + 'T00:00:00Z').toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric', timeZone: 'UTC' });
const rfc822 = (iso) => new Date(iso + 'T00:00:00Z').toUTCString();
const cellText = (v) => (v === '' || v == null ? '<span class="blank" aria-label="blank: not confirmed">&nbsp;</span>' : esc(v));
const img = (file, alt, cls = '') => `<img src="${esc(asset('img/' + file))}" alt="${esc(alt)}"${cls ? ` class="${cls}"` : ''} loading="lazy" decoding="async">`;

const titled = (t) => (/[.?!]$/.test(t) ? t : t);

function page({ title, description, path: p, body, type = 'page', attrs = '', ogType = 'website', jsonld = '', hero = '' }) {
  const canonical = abs(p);
  const fullTitle = p === '/' ? title : `${title} — ${cfg.siteName}`;
  return `<!doctype html>
<html lang="${cfg.language}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(fullTitle)}</title>
<meta name="description" content="${esc(description)}">
<link rel="canonical" href="${esc(canonical)}">
<meta property="og:title" content="${esc(title)}">
<meta property="og:description" content="${esc(description)}">
<meta property="og:url" content="${esc(canonical)}">
<meta property="og:type" content="${ogType}">
<meta property="og:site_name" content="${esc(cfg.siteName)}">
<meta property="og:image" content="${esc(abs(hero ? `/assets/img/${hero}` : '/assets/img/hero-counter.jpg'))}">
<meta name="twitter:card" content="summary_large_image">
<meta name="analytics-endpoint" content="${esc(cfg.analyticsEndpoint || '')}">
<link rel="stylesheet" href="${esc(asset('style.css'))}">
<link rel="alternate" type="application/rss+xml" title="${esc(cfg.siteName)} — buying guides" href="${esc(abs('/feed.xml'))}">
${jsonld}
</head>
<body data-page="${esc(type)}" ${attrs}>
<a class="skip" href="#main">Skip to content</a>
<header class="masthead">
  <div class="wrap">
    <div class="masthead-top">
      <a class="wordmark" href="${esc(href('/'))}">${esc(cfg.siteName)}<span class="dot">.</span><small>Kitchen buying guides</small></a>
      <p class="masthead-issue"><b>Independent</b> · checked ${esc(dateLong(cfg.lastReviewed))}</p>
    </div>
    <nav class="nav" aria-label="Main">
      ${NAV.map(([u, t]) => `<a href="${esc(href(u))}"${p === u || (u !== '/' && p.startsWith(u)) ? ' aria-current="page"' : ''}>${esc(t)}</a>`).join('\n      ')}
    </nav>
  </div>
</header>
<div class="disclosure-strip" role="note" aria-label="Affiliate disclosure">
  <div class="wrap"><strong>Disclosure.</strong> <span>${esc(cfg.disclosureStrip)}</span> <a href="${esc(href('/compliance/'))}">How we disclose</a></div>
</div>
<main id="main">
${body}
</main>
<footer class="site-footer">
  <div class="wrap">
    <div class="foot-top">
      <div>
        <a class="wordmark" href="${esc(href('/'))}">${esc(cfg.siteName)}<span class="dot">.</span></a>
        <p class="foot-blurb">${esc(cfg.footerBlurb)}</p>
      </div>
      <div>
        <h2 class="foot-h">Records and dashboards</h2>
        <ul class="foot-links">
          ${DASHBOARDS.map(([u, t]) => `<li><a href="${esc(href(u))}">${esc(t)}</a></li>`).join('\n          ')}
          <li><a href="${esc(href('/feed.xml'))}">RSS feed</a></li>
          <li><a href="${esc(href('/legacy/archive/'))}">Archived editions</a></li>
          <li><a href="${esc(href('/sitemap.xml'))}">Sitemap</a></li>
        </ul>
      </div>
    </div>
    <p class="disclosure-footer"><strong>Disclosure.</strong> ${esc(cfg.associatesStatement)} Some links here are affiliate links and are marked sponsored. ${esc(cfg.imageDisclosure)}</p>
    <p class="fine">${esc(cfg.siteName)} is not sponsored by, endorsed by, or affiliated with Amazon.com, Inc. or any brand named on this site. Prices and availability are not shown here. Product photography is editorial illustration, not the reviewed unit. Last checked ${esc(dateLong(cfg.lastReviewed))}. Source links appear on every claim, and the full register is in the footer.</p>
  </div>
</footer>
<script src="${esc(asset('analytics.js'))}" defer></script>
</body>
</html>
`;
}

// ---------- components ----------
function pickCard(p) {
  const c = catOf(p.category);
  const hasLink = !!p.tagged_outbound_url && !p.no_buy_link;
  const specs = [
    p.capacity_qt ? `<span><b>${esc(p.capacity_qt)} qt</b></span>` : '',
    p.temp_max_f ? `<span>to <b>${esc(p.temp_max_f)} °F</b></span>` : '',
    p.shape ? `<span>${esc(p.shape)}</span>` : '',
  ].filter(Boolean).join('');
  return `<a class="pick" href="${esc(href('/products/' + p.slug + '/'))}">
  ${p.flags.includes('FLG-025') ? '<span class="pick-flag">No source page</span>' : ''}
  <div class="pick-media">${img(PRODUCT_IMAGE[p.id], p.name)}</div>
  <div class="pick-body">
    <span class="pick-brand">${esc(p.brand)} · ${esc(c.name)}</span>
    <span class="pick-name">${esc(p.short_name)}</span>
    <p class="pick-fit">${esc(p.fit_line)}</p>
    <div class="pick-spec">${specs || `<span>Specifications pending</span>`}</div>
    <span class="pick-cta">${hasLink ? 'Read the verdict' : 'Read why there is no link'}</span>
  </div>
</a>`;
}

function featureCard(p, g) {
  return `<a class="feature" href="${esc(href('/guides/' + g.slug + '/'))}" style="text-decoration:none">
  <div class="feature-media">${img(g.image, g.image_alt)}</div>
  <div class="feature-body">
    <p class="kicker">${esc(catOf(g.category).name)} <span class="sep">|</span> Buying guide</p>
    <h2>${esc(g.title)}</h2>
    <p>${esc(g.deck)}</p>
    <span class="pick-cta">Read the guide</span>
  </div>
</a>`;
}

function storyRow(g) {
  return `<article class="story">
  <div class="story-thumb">${img(g.image, g.image_alt)}</div>
  <div>
    <p class="story-meta">${esc(catOf(g.category).name)}</p>
    <h3><a href="${esc(href('/guides/' + g.slug + '/'))}">${esc(g.title)}</a></h3>
    <p>${esc(g.deck)}</p>
  </div>
</article>`;
}

function buyBox(p, placement = 'product-page') {
  if (p.no_buy_link) {
    return `<div class="buybox hidden-link">
    <p><strong>No buy button on this page.</strong> ${esc(p.no_buy_link_reason)}</p>
    <p class="small">The listing this unit was observed on is recorded on the <a href="${esc(href('/shop/'))}">comparison table</a> with its source link.</p>
  </div>`;
  }
  return `<div class="buybox">
    <a class="btn" href="${esc(p.tagged_outbound_url)}" rel="sponsored noopener" data-outbound data-product="${esc(p.id)}" data-placement="${esc(placement)}">Check the current price on Amazon</a>
    <span class="btn-note">Affiliate link, marked sponsored. Opens the ${esc(p.brand)} listing on Amazon.com. We do not display prices because they change and we do not use Amazon price data.</span>
  </div>`;
}

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

function inlineProduct(id) {
  const p = products.find((x) => x.id === id);
  if (!p) return '';
  return `<aside class="inline-product">
  ${img(PRODUCT_IMAGE[p.id], p.name)}
  <div>
    <p class="kicker">${esc(p.brand)} · ${esc(catOf(p.category).name)}</p>
    <h3>${esc(p.name)}</h3>
    <p>${esc(p.fit_line)} ${p.no_buy_link ? 'No buy button: no manufacturer source page exists for it yet.' : ''}</p>
    <a class="small" href="${esc(href('/products/' + p.slug + '/'))}" style="font-weight:650">Specifications, trade-offs and sources →</a>
  </div>
</aside>`;
}

function table(headers, rows, cls = '') {
  return `<div class="table-wrap"><table class="${cls}"><thead><tr>${headers.map((h) => `<th scope="col">${esc(h)}</th>`).join('')}</tr></thead><tbody>${rows.map((r) => `<tr>${r.map((c) => `<td>${c}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
}

function renderBlock(b) {
  switch (b.type) {
    case 'p': return `<p>${esc(b.text)}</p>`;
    case 'note': return `<div class="note">${esc(b.text)}</div>`;
    case 'h2': return `<h2 id="${esc(b.text.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, ''))}">${esc(b.text)}</h2>`;
    case 'h3': return `<h3>${esc(b.text)}</h3>`;
    case 'ul': return `<ul>${b.items.map((i) => `<li>${esc(i)}</li>`).join('')}</ul>`;
    case 'ol': return `<ol>${b.items.map((i) => `<li>${esc(i)}</li>`).join('')}</ol>`;
    case 'product': return inlineProduct(b.id);
    case 'table': {
      const body = `<div class="table-wrap"><table>${
        b.caption ? `<caption>${esc(b.caption)}</caption>` : ''
      }<thead><tr>${b.headers.map((h) => `<th scope="col">${esc(h)}</th>`).join('')}</tr></thead><tbody>${
        b.rows.map((r) => `<tr>${r.map((c) => `<td>${esc(c)}</td>`).join('')}</tr>`).join('')
      }</tbody></table></div>`;
      return body;
    }
    default: throw new Error('unknown block type: ' + b.type);
  }
}

// ---------- pages ----------
const pages = [];
const add = (p) => pages.push(p);
const byId = (id) => products.find((p) => p.id === id);
const guideBySlug = (s) => guides.find((g) => g.slug === s);

// ---------------- HOME ----------------
{
  const lead = guideBySlug('basket-or-oven-style-air-fryer-what-should-you-compare');
  const rest = guides.filter((g) => g !== lead);
  const catTiles = CATEGORIES.map((c) => `<a class="cat" href="${esc(href('/categories/' + c.slug + '/'))}">
      <span class="count">${inCat(c.slug).length} ${inCat(c.slug).length === 1 ? 'pick' : 'picks'}</span>
      <h3>${esc(c.name)}</h3><p>${esc(c.tagline)}</p>
    </a>`).join('\n    ');

  add({
    path: '/', type: 'home', hero: 'hero-counter.jpg',
    title: 'Kitchen gear worth the counter space',
    description: 'Five kitchen appliances compared by manufacturer specification, with a buying guide for each shape and every fact traced to a source.',
    jsonld: `<script type="application/ld+json">${JSON.stringify({
      '@context': 'https://schema.org', '@type': 'WebSite', name: cfg.siteName, url: abs('/'),
      publisher: { '@type': 'Organization', name: cfg.author },
    })}</script>`,
    body: `
<div class="wrap">
<section class="hero">
  <div class="hero-copy">
    <p class="kicker">Buying guides <span class="sep">|</span> Air fryers and thermometers</p>
    <h1>Good gear, for the kitchen you actually have.</h1>
    <p class="deck">Five appliances worth a counter spot, compared the boring way: capacity, footprint, temperature and cleanup, taken from the makers' own specification pages. No prices we cannot keep current. No ratings we did not verify.</p>
    <a class="btn" href="${esc(href('/shop/'))}">Compare all five</a>
    <div class="hero-note">
      <span class="pill good">Every spec sourced</span>
      <span class="pill flag">Links not yet tested</span>
      <span class="pill">Updated ${esc(dateLong(cfg.lastReviewed))}</span>
    </div>
  </div>
  <figure class="hero-figure">
    ${img('hero-counter.jpg', 'A basket of crisp rosemary potatoes fresh from an air fryer on a dark walnut counter.')}
    <figcaption>Illustration, not the reviewed unit. We do not use manufacturer photography.</figcaption>
  </figure>
</section>

<section class="band">
  <div class="band-head">
    <h2>The five picks</h2>
    <a class="more" href="${esc(href('/shop/'))}">Full table with every source →</a>
  </div>
  <div class="picks">
    ${products.map(pickCard).join('\n    ')}
  </div>
</section>

<section class="band">
  <div class="band-head">
    <h2>Start with a guide</h2>
    <a class="more" href="${esc(href('/guides/'))}">All five guides →</a>
  </div>
  ${featureCard(null, lead)}
  <div class="stories" style="margin-top:26px">
    ${rest.map(storyRow).join('\n    ')}
  </div>
</section>

<section class="band">
  <div class="band-head">
    <h2>Browse by what you cook</h2>
  </div>
  <div class="cats">
    ${catTiles}
  </div>
</section>

<section class="band">
  <div class="band-head"><h2>What this site is, and is not</h2></div>
  <div class="prose">
    <p>We did not test these appliances. There is no test kitchen behind this page. What we did is read the manufacturer's own specification sheet for each unit, record it with the date and the link, and put them beside each other so the differences are visible. Where a maker is silent, or contradicts itself, the cell stays empty and the reason is logged on the <a href="${esc(href('/flagged/'))}">flagged for review</a> page instead of being guessed.</p>
    <p>That makes this a good place to shortlist and a bad place to decide alone. The specifications are checkable. The feel of a drawer, the noise of a fan, and the honesty of a non-stick coating are not, and nobody should pretend otherwise.</p>
  </div>
</section>

<section class="band">
  <div class="band-head"><h2>From the workshop</h2><a class="more" href="${esc(href('/about/'))}">How we choose →</a></div>
  <div class="picks">
    ${GALLERY.map((g) => `<figure style="margin:0">
      ${img(g.file, g.alt)}
      <figcaption class="small muted" style="margin-top:8px">${esc(g.alt)}</figcaption>
    </figure>`).join('\n    ')}
  </div>
</section>
</div>`,
  });
}

// ---------------- SHOP / COMPARISON ----------------
{
  const rows = products.map((p) => [
    `<strong>${esc(p.id)}</strong><br><span class="small muted">${esc(p.brand)}</span>`,
    `<a href="${esc(href('/products/' + p.slug + '/'))}"><strong>${esc(p.short_name)}</strong></a>`,
    esc(p.shape),
    p.capacity_qt ? `${esc(p.capacity_qt)} qt` : cellText(''),
    p.temp_max_f ? `${esc(p.temp_max_f)} °F` : cellText(''),
    p.dimensions_in ? `${esc(p.dimensions_in)} in` : cellText(''),
    p.dishwasher_safe ? 'Yes' : cellText(''),
    p.observed_title ? ext(p.observed_final_url, 'listing', '') : cellText(''),
    p.tagged_outbound_url && !p.no_buy_link
      ? ext(p.tagged_outbound_url, 'Amazon', ` data-outbound data-product="${p.id}" data-placement="shop-table"`)
      : '<span class="small muted">withheld</span>',
    flagLinks(p.flags),
  ]);
  const sourceRows = products.map((p) => [
    `<strong>${esc(p.id)}</strong>`,
    `<a href="${esc(p.submitted_url || '#')}" rel="sponsored noopener"><code>${esc(p.submitted_token || '—')}</code></a>`,
    cellText(p.intended_asin),
    cellText(p.official_listing_url),
    cellText(p.confirmation_date),
    p.observed_asin ? `<code>${esc(p.observed_asin)}</code>` : '<span class="muted">none observed</span>',
    p.observed_date ? esc(dateLong(p.observed_date)) : '',
    (p.sources || []).map(srcLink).join(', '),
  ]);

  add({
    path: '/shop/', type: 'shop',
    title: 'The five picks, side by side',
    description: 'Capacity, temperature, footprint and cleanup for all five products, plus the source register showing exactly which fields are confirmed and which are not.',
    body: `
<div class="wrap">
<section class="page-head">
  <p class="kicker">The picks <span class="sep">|</span> 5 products</p>
  <h1>Five appliances, side by side</h1>
  <p class="deck">The short version first. Every number in the top table comes from the maker's own specification page; a dash means the maker did not state it, and we would rather show a dash than borrow a number from a reseller.</p>
</section>
${table(['', 'Product', 'Shape', 'Capacity', 'Max temp', 'Size (in)', 'Dishwasher', 'Listing', 'Buy', 'Flags'], rows, 'wide')}
<div class="prose"><div class="note">Two links are still unresolved. One of the five supplied short links never reached a product page, and the ThermoMaven unit has no manufacturer page for its specifications, so it carries no buy button. Both are explained on the <a href="${esc(href('/flagged/'))}">flagged for review</a> page.</div></div>

<section class="band">
  <h2>The source register behind the table</h2>
  <p class="deck" style="font-size:17px">This is the audit trail. <strong>Intended</strong> fields are only filled from an owner confirmation or an official Associates record, and none of them are confirmed yet, so they are blank. <strong>Observed</strong> fields are what the Amazon page actually served on the date shown, kept in a separate column on purpose.</p>
  ${table(['ID', 'Submitted link', 'Intended ASIN', 'Official listing URL', 'Confirmed on', 'Observed ASIN', 'Observed', 'Sources'], sourceRows, 'wide')}
  <p class="small muted">Kept as two separate fields deliberately: what the submitted link was meant to point at, and what it actually reaches. They are allowed to differ, and here they do.</p>
</section>

<section class="band">
  <h2>What we would tell a friend</h2>
  <div class="facts">
    <div class="fact"><h4>If two things cook at once</h4><p>${esc(byId('P01').short_name)}. Two independent 3 qt baskets with a setting that lands them together.</p></div>
    <div class="fact"><h4>If it is one big pile</h4><p>${esc(byId('P03').short_name)}. Eight quarts in a single basket, and a burst of heat at the end.</p></div>
    <div class="fact"><h4>If a whole meal goes in</h4><p>${esc(byId('P02').short_name)}. 26 quarts and two levels, if the counter depth is there.</p></div>
    <div class="fact"><h4>If you want your hands free</h4><p>${esc(byId('P05').short_name)}. A leave-in probe that reports while the lid stays shut.</p></div>
  </div>
  <p><a class="btn" href="${esc(href('/guides/basket-or-oven-style-air-fryer-what-should-you-compare/'))}">Read the shape guide first</a></p>
</section>
</div>`,
  });
}

// ---------------- PRODUCT PAGES ----------------
for (const p of products) {
  const c = catOf(p.category);
  const g = guideBySlug(p.guide_slug);
  const facts = [
    ['Best for', p.best_for],
    ['The trade-off', p.tradeoff],
    ['Cleanup', p.dishwasher_safe || 'Not stated by the manufacturer. Check the manual before assuming a part is washable.'],
    ['What we could not verify', p.no_buy_link ? 'Everything: no manufacturer page exists for this model, so no specification is published.' : (Object.keys(p.blank_reason || {}).length ? Object.values(p.blank_reason).join(' ') : 'No gaps: every field above came from the manufacturer page.')],
  ];
  const jsonld = `<script type="application/ld+json">${JSON.stringify({
    '@context': 'https://schema.org', '@type': 'Product', name: p.name, brand: { '@type': 'Brand', name: p.brand },
    description: p.lede, url: abs('/products/' + p.slug + '/'),
    isPartOf: { '@type': 'WebSite', name: cfg.siteName, url: abs('/') },
  })}</script>`;
  add({
    path: `/products/${p.slug}/`, type: 'product', ogType: 'article', jsonld, hero: PRODUCT_IMAGE[p.id],
    attrs: `data-product-view="${esc(p.id)}"`,
    title: p.name,
    description: `${p.short_name}: ${p.lede} Specifications from the manufacturer page, with every gap and conflict recorded.`,
    body: `
<div class="wrap">
<nav class="small" aria-label="Breadcrumb" style="margin-bottom:18px"><a href="${esc(href('/shop/'))}">The picks</a> <span class="muted">/</span> <a href="${esc(href('/categories/' + c.slug + '/'))}">${esc(c.name)}</a> <span class="muted">/</span> <span class="muted">${esc(p.short_name)}</span></nav>
<section class="pd-hero">
  <figure style="margin:0">
    ${img(PRODUCT_IMAGE[p.id], p.name)}
    <figcaption class="small muted" style="margin-top:9px">Editorial illustration, not the reviewed unit.</figcaption>
  </figure>
  <div>
    <p class="kicker">${esc(p.brand)} <span class="sep">|</span> ${esc(c.name)}</p>
    <h1 style="font-size:clamp(30px,3.6vw,44px)">${esc(p.name)}</h1>
    <p class="deck">${esc(p.lede)}</p>
    ${buyBox(p)}
    <p class="small muted">${p.tagged_outbound_url && !p.no_buy_link ? `The link carries our Associates tag and is marked sponsored. It has not yet been confirmed in a tracking report (${flagLinks(['FLG-005'])}), so treat it as provisional.` : `No outbound link is published for this product. ${esc(p.note || '')}`}</p>
  </div>
</section>

<section class="band">
  <h2>The specifications we could confirm</h2>
  <p>From <a href="${esc((SOURCES[(p.spec_sources || [])[0]] || {}).url || '#')}" rel="noopener external">${esc((SOURCES[(p.spec_sources || [])[0]] || {}).publisher || 'the manufacturer')}</a>, fetched ${esc(dateLong(p.observed_date))}. Where the page is silent, the cell reads “not stated”.</p>
  ${specGrid(p)}
  <p class="small muted">${esc(p.capacity_note || '')} ${p.dimensions_order ? `Dimensions are shown as ${esc(p.dimensions_order)}.` : ''}</p>
  ${p.observed_specs ? `<h3 style="margin-top:34px">What the Amazon listing states</h3>
  <p>These figures come from the listing's own copy, not from the manufacturer. They are kept in a separate column on purpose, because on this listing they describe a different model from the manufacturer page. Read them as evidence of the conflict, not as specifications of the product.</p>
  ${table(['Field', 'Listing states', 'Manufacturer states'], [
    ['Model', esc(p.observed_specs.model), esc(p.model || '')],
    ['Power', esc(p.observed_specs.power), '<span class="muted">1700 W / 120 V (S12)</span>'],
    ['Temperature', esc(p.observed_specs.temperature), '<span class="muted">up to 450 °F on Hi-Fry (S12)</span>'],
    ['Size', esc(p.observed_specs.dimensions), '<span class="muted">not stated (S12)</span>'],
    ['Capacity', esc(p.observed_specs.capacity), '<span class="muted">8 qt / 7.57 L</span>'],
    ['Material', esc(p.observed_specs.material), '<span class="muted">matte black (S12)</span>'],
  ])}
  <p class="small">${flagLinks(p.flags.filter((f) => ['FLG-026', 'FLG-027'].includes(f)))}</p>` : ''}
</section>

<section class="band">
  <h2>Who it suits, and what it costs you</h2>
  <div class="facts">
    ${facts.map(([h, v]) => `<div class="fact"><h4>${esc(h)}</h4><p>${esc(v)}</p></div>`).join('\n    ')}
  </div>
</section>

${g ? `<section class="band">
  <h2>The guide that covers this one</h2>
  <a class="feature" href="${esc(href('/guides/' + g.slug + '/'))}" style="text-decoration:none">
    <div class="feature-media">${img(g.image, g.image_alt)}</div>
    <div class="feature-body">
      <p class="kicker">${esc(c.name)} <span class="sep">|</span> Buying guide</p>
      <h2 style="font-size:26px">${esc(g.title)}</h2>
      <p>${esc(g.deck)}</p>
      <span class="pick-cta">Read the guide</span>
    </div>
  </a>
</section>` : ''}

<section class="band">
  <h2>Where this came from</h2>
  <ul class="small">
    ${(p.sources || []).map((id) => {
      const s = SOURCES[id];
      if (!s) return `<li>${esc(id)}</li>`;
      const u = id === 'S05' ? p.submitted_url : id === 'S04' ? p.observed_final_url : s.url;
      return `<li><strong>${esc(id)}</strong> — ${esc(s.title)}, ${esc(s.publisher)}. ${u ? ext(u, 'Open source', '') : ''} <span class="muted">(${esc(s.status)})</span></li>`;
    }).join('\n    ')}
  </ul>
  <p class="source-line">Observed on the Amazon listing on ${esc(dateLong(p.observed_date))}: “${esc(p.observed_title)}”. That title is a snapshot and can change. The intended product is still unconfirmed, so it is recorded separately on the <a href="${esc(href('/shop/'))}">comparison table</a>.</p>
</section>

<nav class="page-nav">
  <span><a href="${esc(href('/shop/'))}">← All five picks</a></span>
  <span>${(() => { const i = products.indexOf(p); const nx = products[i + 1]; return nx ? `<a href="${esc(href('/products/' + nx.slug + '/'))}">${esc(nx.short_name)} →</a>` : `<a href="${esc(href('/guides/'))}">Buying guides →</a>`; })()}</span>
</nav>
</div>`,
  });
}

// ---------------- CATEGORIES ----------------
add({
  path: '/categories/', type: 'categories',
  title: 'Browse by category',
  description: 'Three clusters: basket air fryers, countertop ovens and thermometers. Each with its picks and the guide that covers it.',
  body: `<div class="wrap">
<section class="page-head"><p class="kicker">Categories</p><h1>Three shapes, three jobs</h1>
<p class="deck">Everything here is organised by the job the appliance does, not by brand. Start with the job.</p></section>
<div class="cats">
${CATEGORIES.map((c) => `<a class="cat" href="${esc(href('/categories/' + c.slug + '/'))}">
  <span class="count">${inCat(c.slug).length} picks · ${guides.filter((g) => g.category === c.slug).length} guide</span>
  <h3>${esc(c.name)}</h3><p>${esc(c.blurb)}</p></a>`).join('\n')}
</div>
</div>`,
});

for (const c of CATEGORIES) {
  const list = inCat(c.slug);
  const gs = guides.filter((g) => g.category === c.slug);
  add({
    path: `/categories/${c.slug}/`, type: 'category', attrs: `data-category="${esc(c.slug)}"`,
    title: c.name,
    description: `${c.name}: ${c.blurb}`,
    body: `<div class="wrap">
<section class="page-head">
  <p class="kicker">Category</p>
  <h1>${esc(c.name)}</h1>
  <p class="deck">${esc(c.blurb)}</p>
</section>
<div class="picks">${list.map(pickCard).join('\n')}</div>
${gs.length ? `<section class="band"><div class="band-head"><h2>The guides</h2></div><div class="stories">${gs.map(storyRow).join('\n')}</div></section>` : ''}
<p class="band"><a class="more" href="${esc(href('/shop/'))}">See all five picks side by side →</a></p>
</div>`,
  });
}

// ---------------- GUIDES ----------------
add({
  path: '/guides/', type: 'guides',
  title: 'Buying guides',
  description: 'Question-led buying guides for air fryers, countertop ovens and thermometers, built on manufacturer specifications rather than opinion.',
  body: `<div class="wrap">
<section class="page-head"><p class="kicker">Buying guides</p><h1>Five questions worth asking before you buy</h1>
<p class="deck">Each guide starts with a real question and answers it with specifications you can check. None of them ranks a brand, and none of them claims we tested anything.</p></section>
<div class="stories">
${guides.map(storyRow).join('\n')}
</div>
</div>`,
});

for (const g of guides) {
  const related = products.filter((p) => p.category === g.category || (g.cluster_links || []).includes(p.category));
  const jsonld = `<script type="application/ld+json">${JSON.stringify({
    '@context': 'https://schema.org', '@type': 'Article', headline: g.title, description: g.description,
    datePublished: g.date, dateModified: cfg.lastReviewed,
    author: { '@type': 'Organization', name: cfg.author },
    publisher: { '@type': 'Organization', name: cfg.siteName },
    mainEntityOfPage: abs(`/guides/${g.slug}/`), image: abs(`/assets/img/${g.image}`),
  })}</script>`;
  add({
    path: `/guides/${g.slug}/`, type: 'guide', ogType: 'article', jsonld, attrs: `data-guide="${esc(g.slug)}"`, hero: g.image,
    title: g.title,
    description: g.description,
    body: `<div class="wrap">
<article class="article">
  <header class="article-head">
    <p class="kicker">${esc(catOf(g.category).name)} <span class="sep">|</span> Buying guide</p>
    <h1>${esc(g.title)}</h1>
    <p class="deck">${esc(g.deck)}</p>
    <div class="byline">
      <span>By ${esc(cfg.author)}</span><span class="sep">·</span>
      <span>Published ${esc(dateLong(g.date))}</span><span class="sep">·</span>
      <span>Specifications checked ${esc(dateLong(cfg.lastReviewed))}</span><span class="sep">·</span>
      <span>${g.body.filter((b) => b.type === 'h2').length} sections</span>
    </div>
  </header>
  <figure class="article-hero">
    ${img(g.image, g.image_alt)}
    <figcaption>Editorial illustration. We do not use manufacturer photography or pictures of units we have not handled.</figcaption>
  </figure>
  <div class="prose">
    ${g.body.map(renderBlock).join('\n    ')}
  </div>

  ${related.length ? `<section class="band"><div class="band-head"><h2>The picks in this guide</h2></div><div class="picks">${related.map(pickCard).join('')}</div></section>` : ''}

  <section class="band sources">
    <h2>Sources for this guide</h2>
    <ul>
      ${g.sources.map((id) => {
        const s = SOURCES[id];
        if (!s) return `<li>${esc(id)}</li>`;
        return `<li><strong>${esc(id)}</strong> — ${esc(s.title)}, ${esc(s.publisher)}. ${s.url ? ext(s.url, 'Open source', '') : ''} <span class="muted">(${esc(s.status)})</span></li>`;
      }).join('\n      ')}
    </ul>
    <p class="small"><a href="${esc(href('/sources/'))}">Full source register</a> · <a href="${esc(href('/flagged/'))}">What is still unresolved</a></p>
  </section>

  <nav class="page-nav">
    <span><a href="${esc(href('/guides/'))}">← All guides</a></span>
    <span>${(() => { const i = guides.indexOf(g); const nx = guides[i + 1]; return nx ? `<a href="${esc(href('/guides/' + nx.slug + '/'))}">${esc(nx.title)} →</a>` : `<a href="${esc(href('/shop/'))}">The five picks →</a>`; })()}</span>
  </nav>
</article>
</div>`,
  });
}

// ---------------- HOW WE CHOOSE (public landing for policy) ----------------
add({
  path: '/how-we-choose/', type: 'about',
  title: 'How we choose products and check facts',
  description: 'The editorial rules behind every page: what we verify, what we refuse to publish, and how corrections work.',
  body: `<div class="wrap">
<section class="page-head"><p class="kicker">Editorial policy</p><h1>How this site decides what to say</h1>
<p class="deck">Six rules. They are the reason some cells in our tables are empty.</p></section>
<div class="prose">
<h2>1. A specification needs a manufacturer page</h2>
<p>Capacity, wattage, dimensions and dishwasher claims come from the maker's own product page, fetched on the date shown next to the table. If the maker does not state it, the cell says “not stated”. We do not fill gaps from reseller listings or from other reviews.</p>
<h2>2. We do not publish prices</h2>
<p>Prices change hourly and Amazon's Program Policies only let a site display price data that Amazon itself serves or that comes through its API. We do neither, so every buy button says “check the current price on Amazon” and links out. ${srcLink('S03')}</p>
<h2>3. We do not publish star ratings</h2>
<p>Ratings are a snapshot of a rolling average. Quoting one without the date and the sample is misleading, and keeping it current is a full-time job. Read them on the listing, where they are live.</p>
<h2>4. We say what we have not tested</h2>
<p>Nobody here has cooked in any of these appliances. Everything is a specification comparison. Where that leaves a real question open, such as how evenly a unit browns, we say so rather than inventing an answer. ${srcLink('S07')}</p>
<h2>5. When two official pages disagree, we publish neither number</h2>
<p>Two of the makers on this site contradict themselves. Rather than pick the friendlier figure, both are recorded on the <a href="${esc(href('/flagged/'))}">flagged for review</a> page with the links, and the field stays blank.</p>
<h2>6. Corrections are public</h2>
<p>If a number here is wrong, it gets fixed and the fix gets logged, not quietly swapped. The route for that is on the <a href="${esc(href('/about/'))}">About page</a>.</p>
<div class="note">The short version: a number you can check is worth more than a paragraph you cannot.</div>
</div>
<p class="band"><a class="btn" href="${esc(href('/shop/'))}">See the table this produces</a></p>
</div>`,
});

// ---------------- EXECUTIVE SUMMARY ----------------
{
  const verified = products.filter((p) => (p.spec_sources || []).length).length;
  add({
    path: '/executive-summary/', type: 'summary',
    title: 'Executive summary',
    description: 'What is built, what is verified, what is blocked, and the four decisions needed from the owner.',
    body: `<div class="wrap">
<section class="page-head"><p class="kicker">Executive summary <span class="sep">|</span> ${esc(dateLong(cfg.lastReviewed))}</p><h1>Where this stands</h1>
<p class="deck">One page for the owner. Everything below is reproducible from the repository and the source links.</p></section>

<div class="tiles">
  <div class="tile"><span class="n">5</span><div class="t">products tracked</div><div class="d">Every one submitted by the owner. None added by us.</div></div>
  <div class="tile"><span class="n">${verified}</span><div class="t">with a manufacturer spec page</div><div class="d">One has none, so its specifications are blank.</div></div>
  <div class="tile"><span class="n">${guides.length}</span><div class="t">buying guides</div><div class="d">Question-led, each with its sources listed.</div></div>
  <div class="tile"><span class="n">${flagsDoc.flags.length}</span><div class="t">open flags</div><div class="d">Published with sources, none of them blocking.</div></div>
</div>

<div class="prose">
<h2>What is built</h2>
<ul>
<li>A publication-style site: front page, five product pages, three category pages, five guides, a comparison table and a source register.</li>
<li>A disclosure strip above the fold on every page, repeated in the footer, using the exact wording required by the Associates Operating Agreement ${srcLink('S01')}.</li>
<li>A privacy-preserving click counter and a self-hostable collector. The collector is not deployed, so nothing is being measured yet ${flagLinks(['FLG-009'])}.</li>
<li>A publishing gate (<code>tools/verify.mjs</code>) that fails the build if a page loses its disclosure, an Amazon link loses <code>rel="sponsored"</code>, a row loses its source, or an internal link breaks.</li>
<li>A campaign ledger with a defined schema and zero rows. No conversion score and no revenue forecast appear anywhere on this site.</li>
</ul>

<h2>What is verified</h2>
<ul>
<li>The disclosure requirement, the tagged-link rule and the price-display restriction, each read from the official Associates pages on 2026-11-20 ${srcLink('S01')} ${srcLink('S02')} ${srcLink('S03')}.</li>
<li><code>rel="sponsored"</code> on outbound affiliate links, per Google's guidance ${srcLink('S06')}.</li>
<li>The endorsement-disclosure rule, read from 16 CFR 255.5 on eCFR ${srcLink('S07')}.</li>
<li>Manufacturer specifications for four of five products, each on the maker's own page ${srcLink('S11')} ${srcLink('S12')} ${srcLink('S13')} ${srcLink('S14')}.</li>
<li>USDA safe minimum internal temperatures, quoted from FSIS ${srcLink('S10')}.</li>
</ul>

<h2>What is not verified, and why</h2>
<ul>
<li><strong>Which product each submitted short link was meant to reach.</strong> The links resolve, but the observed destination is not the same as the owner's intent, and the mapping changed between fetch rounds ${flagLinks(['FLG-001', 'FLG-002'])}.</li>
<li><strong>Whether the buy links credit a sale.</strong> No link has been clicked inside an enrolled Associates session ${flagLinks(['FLG-005'])}.</li>
<li><strong>The ThermoMaven specifications.</strong> No manufacturer page exists for that model ${flagLinks(['FLG-025'])}.</li>
<li><strong>Whether the Associates account is active and declares this site</strong> ${flagLinks(['FLG-008'])}.</li>
</ul>

<h2>Four decisions only the owner can make</h2>
<ol>
<li>Confirm which product each supplied short link was meant to reach. This closes the largest gap on the site.</li>
<li>Test one Special Link per product in Associates Central, then confirm the click appears in a report.</li>
<li>Deploy the analytics collector, or decide to run with no measurement for now.</li>
<li>Pick a publishing cadence, or the feed will not grow.</li>
</ol>
<p>Each of those is written up with its trade-offs on the <a href="${esc(href('/suggestions/'))}">suggestions page</a>.</p>

<h2>What this build cannot do</h2>
<p>It cannot read Amazon prices, sales, or Associates reports, because that needs authorized API access the build does not have. It does not scrape Amazon. Any figure that would require that data is absent on purpose, not forgotten.</p>
</div>
</div>`,
  });
}

// ---------------- SOURCES ----------------
add({
  path: '/sources/', type: 'sources',
  title: 'Source register',
  description: 'Every source used on this site, what it was used for, how it was checked, and the exact wording relied on.',
  body: `<div class="wrap">
<section class="page-head"><p class="kicker">Source register</p><h1>Every source, and how far to trust it</h1>
<p class="deck">${esc(sourcesDoc.note)}</p></section>
${table(['ID', 'Source', 'Publisher', 'How it was checked', 'Used for', 'Status', 'Link'], sourcesDoc.sources.map((s) => [
    `<strong id="${esc(s.id)}">${esc(s.id)}</strong>`,
    esc(s.title), esc(s.publisher), esc(s.method), esc(s.used_for),
    `<span class="badge ${s.status === 'verified' ? 'good' : s.status === 'excerpt' ? 'flag' : ''}">${esc(s.status)}</span>`,
    s.url ? ext(s.url, 'Open', '') : '<span class="muted">none</span>',
  ]), 'wide')}
<section class="band"><div class="prose">
<h2>How to read the status column</h2>
<ul>
<li><strong>verified</strong>: the full page was retrieved and read on the date shown.</li>
<li><strong>excerpt</strong>: only a search-result excerpt of the official page was available. Re-check the exact wording before relying on it.</li>
<li><strong>observed</strong>: a value read off a live Amazon page on a dated fetch. Useful as evidence of what happened that day, and capable of changing tomorrow.</li>
</ul>
<p>No third-party blog, review site or reseller listing is cited as a source anywhere on this site. Where a number could not be traced to one of the sources above, it is missing from the page rather than borrowed.</p>
</div></section>
</div>`,
});

// ---------------- FLAGGED ----------------
add({
  path: '/flagged/', type: 'flagged',
  title: 'Flagged for review',
  description: 'Every irregularity and unconfirmed value, with the source links and the single manual step that would close it.',
  body: `<div class="wrap">
<section class="page-head"><p class="kicker">Flagged for review</p><h1>What we could not confirm</h1>
<p class="deck">${esc(flagsDoc.note)}</p></section>
<div class="status-box"><strong>Nothing here blocks the site.</strong> Each item is a gap between what a reader might assume and what we can actually show. The manual step in each card is the fastest way to close it.</div>
${flagsDoc.flags.map((f) => `<section class="flag-card${f.status === 'resolved' ? ' is-resolved' : ''}" id="${esc(f.id)}">
  <p class="flag-head"><span class="badge flag">${esc(f.id)}</span> <span class="badge sev-${esc(f.severity)}">${esc(f.severity)}</span> <strong>${esc(f.title)}</strong>${f.status === 'resolved' ? ' <span class="badge good">resolved</span>' : ''}</p>
  <p>${esc(f.detail)}</p>
  ${f.status === 'resolved' && f.resolution ? `<p class="manual"><strong>Resolution:</strong> ${esc(f.resolution)}</p>` : ''}
  ${f.sources.length ? `<p class="small"><strong>Sources:</strong> ${f.sources.map(srcLink).join(', ')}</p>` : ''}
  ${f.manual_step ? `<p class="manual"><strong>What would close it:</strong> ${esc(f.manual_step)}</p>` : ''}
</section>`).join('\n')}
</div>`,
});

// ---------------- QUESTIONS ----------------
add({
  path: '/questions/', type: 'questions',
  title: 'Open questions',
  description: 'What is known, what is not, how each gap can be closed, and whether it blocks progress.',
  body: `<div class="wrap">
<section class="page-head"><p class="kicker">Open questions</p><h1>What we know, what we do not, and how to find out</h1>
<p class="deck">${esc(questions.note)}</p></section>
<h2>Established</h2>
${table(['ID', 'Statement', 'Sources'], questions.known.map((k) => [`<strong>${esc(k.id)}</strong>`, esc(k.statement), (k.sources || []).map(srcLink).join(', ') || '<span class="muted">none</span>']), 'wide')}
<h2>Open</h2>
${table(['ID', 'Question', 'Why it matters', 'How to close it', 'Blocks?', 'Sources'], questions.unknown.map((q) => [
    `<strong>${esc(q.id)}</strong>`, esc(q.question), esc(q.why_it_matters), esc(q.how_to_close),
    q.blocking ? '<span class="badge sev-high">yes</span>' : '<span class="badge sev-low">no</span>',
    (q.sources || []).map(srcLink).join(', ') || '<span class="muted">none</span>',
  ]), 'wide')}
<h2>Ways to discover what is missing</h2>
${table(['ID', 'Method', 'Closes'], questions.discovery.map((d) => [`<strong>${esc(d.id)}</strong>`, esc(d.suggestion), (d.closes || []).map(esc).join(', ') || '<span class="muted">none</span>']), 'wide')}
</div>`,
});

// ---------------- SUGGESTIONS ----------------
add({
  path: '/suggestions/', type: 'suggestions',
  title: 'Suggestions to choose between',
  description: 'The decisions waiting on the owner, each with its trade-offs. Nothing is implemented until an option is chosen.',
  body: `<div class="wrap">
<section class="page-head"><p class="kicker">Decision board</p><h1>Choose a path before anything changes</h1>
<p class="deck">${esc(suggestionsDoc.note)}</p></section>
${suggestionsDoc.suggestions.map((s) => `<section class="flag-card" id="${esc(s.id)}" style="border-left-color:var(--accent)">
  <p class="flag-head"><span class="badge">${esc(s.id)}</span> <strong>${esc(s.topic)}</strong> <span class="badge good">current: ${esc(s.current)}</span></p>
  <ul class="opts">
    ${s.options.map((o) => `<li><strong>${esc(o.id)}.</strong> ${esc(o.label)} <span class="muted small">Trade-off: ${esc(o.tradeoff)}</span></li>`).join('\n    ')}
  </ul>
  <p class="manual"><strong>Our recommendation:</strong> ${esc(s.recommendation)}</p>
</section>`).join('\n')}
<div class="prose"><div class="note">To decide, reply with the suggestion ID and the letter, for example “S-03 B”. The site keeps working with whatever is current until then.</div></div>
</div>`,
});

// ---------------- LEDGER ----------------
add({
  path: '/ledger/', type: 'ledger',
  title: 'Campaign ledger',
  description: 'An empty ledger with a defined schema and a provenance rule. Rows are added only from authorized first-party reports.',
  body: `<div class="wrap">
<section class="page-head"><p class="kicker">Campaign ledger</p><h1>Starting from nothing, on purpose</h1>
<p class="deck">${esc(ledger.status)}</p></section>
<div class="status-box">${esc(ledger.rule)}</div>
${table(ledger.columns.map((c) => c.name), [ledger.columns.map(() => '<span class="muted">—</span>')], 'wide')}
<p class="small muted">Rows: ${ledger.rows.length}. No conversion score, revenue forecast or optimization is presented anywhere on this site.</p>
<h2>Column meanings</h2>
${table(['Column', 'What goes in it'], ledger.columns.map((c) => [`<code>${esc(c.name)}</code>`, esc(c.meaning)]))}
</div>`,
});

// ---------------- MEASUREMENT ----------------
add({
  path: '/measurement/', type: 'measurement',
  title: 'Measurement',
  description: 'The five events the site records, the privacy rules, and the honest current state: inactive until an endpoint is deployed.',
  body: `<div class="wrap">
<section class="page-head"><p class="kicker">Measurement</p><h1>What we record, and what we refuse to</h1>
<p class="deck">${esc(events.status)}</p></section>
<div class="status-box"><strong>Live status:</strong> ${cfg.analyticsEndpoint ? 'An endpoint is configured; events are being sent.' : `Inactive. No endpoint is configured, so the browser sends nothing and no traffic figure exists. ${flagLinks(['FLG-009'])}`}</div>
${table(['Event', 'Fires when', 'Properties'], events.events.map((e) => [`<code>${esc(e.name)}</code>`, esc(e.fires), e.properties.map((p) => `<code>${esc(p)}</code>`).join(' ')]), 'wide')}
<h2>Privacy</h2>
<p>${esc(events.privacy)}</p>
<p class="small muted">Not collected: ${esc(events.not_collected.join(', '))}.</p>
<h2>Why clicks are not routed through a redirect</h2>
<p>${esc(events.why_no_redirect)} ${srcLink('S02')}</p>
<h2>How a click actually earns</h2>
<p>A qualifying purchase begins when a reader clicks a tagged link and ends at the first of: 24 hours, an order, or a click on somebody else's link. If the item goes into the cart first, the window extends to 89 days. ${srcLink('S17')}</p>
</div>`,
});

// ---------------- COMPLIANCE ----------------
add({
  path: '/compliance/', type: 'compliance',
  title: 'Disclosure and compliance',
  description: 'The exact disclosure wording, where it appears, the link rules applied, and the gates that must pass before scaling.',
  body: `<div class="wrap">
<section class="page-head"><p class="kicker">Compliance</p><h1>Disclosure, links and gates</h1></section>
<div class="prose">
<h2>The required statement</h2>
<p>Operating Agreement §5 requires the Site to state, clearly and prominently: <strong>“${esc(cfg.associatesStatement)}”</strong> ${srcLink('S01')}</p>
<p>That sentence appears in the disclosure strip directly under the masthead on every page of this site, and again in the footer. The FTC's Endorsement Guides require a material connection to be disclosed clearly and conspicuously, and treat an affiliate commission as exactly that kind of connection; a disclosure buried on an About page is not enough ${srcLink('S07')} ${srcLink('S08')}.</p>
<h2>How outbound links are handled</h2>
<ul>
<li>Every link to an Amazon host carries <code>rel="sponsored"</code>, which is what Google asks for on paid and affiliate links ${srcLink('S06')}.</li>
<li>Buy links carry the tracking ID <code>${esc(cfg.trackingId)}</code> as a tag parameter, which is the tagging rule in the Program Policies ${srcLink('S02')}.</li>
<li>No redirect, no cloaking and no link shortener sits between the reader and Amazon. The click counter records the click in the browser and lets the link go straight out ${srcLink('S02')}.</li>
<li>No price, star rating or availability figure is published, because Amazon's rules only permit that when Amazon serves the data or it arrives through its API ${srcLink('S03')}.</li>
</ul>
<h2>Gates before this scales</h2>
</div>
${table(['Gate', 'Check', 'Method', 'Status'], [
    ['G-01', 'Disclosure above the fold on every page, repeated in the footer', 'Automated in the build', '<span class="badge good">passing</span>'],
    ['G-02', 'One Special Link per product tested in Associates Central, destination and report confirmed', 'Manual, needs Associates login', `<span class="badge sev-high">pending</span> ${flagLinks(['FLG-005'])}`],
    ['G-03', 'Every Amazon-hosted link carries rel="sponsored"', 'Automated in the build', '<span class="badge good">passing</span>'],
    ['G-04', 'Every outbound product link uses the tag ' + cfg.trackingId, 'Automated in the build', '<span class="badge good">passing</span>'],
    ['G-05', 'No redirect or cloaking page generated', 'Automated in the build', '<span class="badge good">passing</span>'],
    ['G-06', 'No price, rating or availability displayed', 'Automated in the build', '<span class="badge good">passing</span>'],
    ['G-07', 'Every product row has at least one official source link', 'Automated in the build', '<span class="badge good">passing</span>'],
    ['G-08', 'Ledger rows only from authorized first-party reports', 'Manual', '<span class="badge sev-low">no rows yet</span>'],
    ['G-09', 'Only the five defined events are sent; no cookies', 'Automated in the build', '<span class="badge good">passing</span>'],
    ['G-10', 'Sitemap and feed cover every guide; no broken internal links', 'Automated in the build', '<span class="badge good">passing</span>'],
  ], 'wide')}
<div class="prose"><p class="small">The automated gates run on every build in <code>tools/verify.mjs</code> and a failing gate stops the site from being published.</p></div>
</div>`,
});

// ---------------- ABOUT ----------------
add({
  path: '/about/', type: 'about',
  title: 'About and corrections',
  description: 'Who publishes this site, how products get here, how facts are checked, and how to get something corrected.',
  body: `<div class="wrap">
<section class="page-head"><p class="kicker">About</p><h1>Who is behind this</h1></section>
<div class="prose">
<p>${esc(cfg.siteName)} is an independent kitchen buying guide. It is published by the ${esc(cfg.author)} and it is written for people standing in a kitchen with a tape measure, not for people shopping for entertainment.</p>
<h2>How products get here</h2>
<p>Only products submitted by the site owner are listed. Nothing was added from our own research, and no brand paid for placement. If that changes, it will say so on the page where it happens.</p>
<h2>What we actually do</h2>
<p>We read each maker's specification page, record the values with the date and link, and put the units beside each other so the differences are visible. Where a maker is silent or contradicts itself, we leave the value out and log why on the <a href="${esc(href('/flagged/'))}">flagged for review</a> page.</p>
<h2>What we do not do</h2>
<ul>
<li>We do not claim to have tested anything. There is no test kitchen.</li>
<li>We do not publish prices or star ratings ${srcLink('S03')}.</li>
<li>We do not use manufacturer photography. The images are editorial illustrations and are labelled as such ${flagLinks(['FLG-015'])}.</li>
<li>We do not run trackers other than our own click counter, which stores no cookies and no personal data.</li>
</ul>
<h2>Corrections</h2>
<p>If a number here is wrong, open an issue in the <a href="https://github.com/karagemop466-tech/Affil3/issues" rel="noopener external">project repository</a>. Corrections are made in the data file, re-verified against the source, and logged. Nothing gets quietly edited.</p>
<h2>About the byline</h2>
<p>Pages are published under a team byline, not a person's name, because there is no named editor yet. That is a weakness, and it is logged rather than papered over ${flagLinks(['FLG-014'])}.</p>
</div>
<p class="band"><a class="btn" href="${esc(href('/how-we-choose/'))}">The six editorial rules</a></p>
</div>`,
});

// ---------------- 404 ----------------
add({
  path: '/404.html', type: '404', noSitemap: true,
  title: 'Page not found',
  description: 'That page does not exist.',
  body: `<div class="wrap"><section class="page-head"><p class="kicker">404</p><h1>That page went missing</h1>
<p class="deck">It may have been moved. The picks, the guides and the comparison table are all still where they were.</p>
<p><a class="btn" href="${esc(href('/shop/'))}">Back to the five picks</a></p></section></div>`,
});

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
const written = [];
for (const p of pages) {
  const file = p.path.endsWith('.html') ? path.join(OUT, p.path) : path.join(OUT, p.path, 'index.html');
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, linkPolicy(page(p)));
  written.push({ path: p.path, file: path.relative(ROOT, file), noSitemap: !!p.noSitemap });
}

fs.mkdirSync(path.join(OUT, 'assets'), { recursive: true });
fs.copyFileSync(path.join(ROOT, 'src/assets/style.css'), path.join(OUT, 'assets/style.css'));
fs.copyFileSync(path.join(ROOT, 'src/assets/analytics.js'), path.join(OUT, 'assets/analytics.js'));
fs.writeFileSync(path.join(OUT, '.nojekyll'), '');

// sitemap
const sitemapPages = written.filter((w) => !w.noSitemap);
fs.writeFileSync(path.join(OUT, 'sitemap.xml'), `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${sitemapPages.map((w) => `  <url><loc>${esc(abs(w.path))}</loc><lastmod>${cfg.lastReviewed}</lastmod></url>`).join('\n')}
</urlset>
`);

// feed
const feedItems = [...guides].sort((a, b) => (a.date < b.date ? 1 : -1));
fs.writeFileSync(path.join(OUT, 'feed.xml'), `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
  <title>${esc(cfg.siteName)} — buying guides</title>
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

fs.writeFileSync(path.join(OUT, 'robots.txt'), `User-agent: *\nAllow: /\nDisallow: /editorial/\nDisallow: /legacy/\nDisallow: /crisp-index/\nDisallow: /docs/\n\nSitemap: ${abs('/sitemap.xml')}\n`);

console.log(`Built ${written.length} pages, ${feedItems.length} feed items, ${sitemapPages.length} sitemap URLs at the repository root`);
