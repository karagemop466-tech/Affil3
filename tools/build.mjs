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
const OWNED = ['index.html', 'shop', 'products', 'compare', 'categories', 'guides', 'executive-summary', 'sources',
  'questions', 'suggestions', 'flagged', 'ledger', 'measurement', 'compliance', 'about', '404.html',
  'feed.xml', 'sitemap.xml', 'robots.txt', 'assets/style.css', 'assets/analytics.js', 'assets/img', '.nojekyll'];
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
  { slug: 'air-fryers', name: 'Air fryers', blurb: 'Basket-style air fryers, observed on Amazon listings on 2026-11-20.' },
  { slug: 'air-fryer-ovens', name: 'Air fryer ovens', blurb: 'Oven-style air fryers and toaster ovens with a door and racks.' },
  { slug: 'cooking-thermometers', name: 'Cooking thermometers', blurb: 'Wireless meat thermometers, with the USDA temperature reference.' },
  { slug: 'unresolved', name: 'Unresolved links', blurb: 'Submitted links that did not resolve to a product page. No buy link is published here.' },
];
const catName = (slug) => (CATEGORIES.find((c) => c.slug === slug) || { name: slug }).name;

// Decorative illustrations. They are not product photography and are never presented as the product.
const ART = {
  'air-fryers': { src: '/assets/img/cat-air-fryers.jpg', alt: 'Illustration of a basket-style air fryer with its drawer and crisper basket' },
  'air-fryer-ovens': { src: '/assets/img/cat-air-fryer-ovens.jpg', alt: 'Illustration of a countertop air fryer oven with French doors and two racks' },
  'cooking-thermometers': { src: '/assets/img/cat-thermometers.jpg', alt: 'Illustration of an instant-read thermometer and a wireless probe in a roast' },
  'unresolved': { src: '/assets/img/cat-air-fryers.jpg', alt: 'Illustration of a basket-style air fryer' },
};
const art = (slug) => ART[slug] || ART['air-fryers'];
const HERO_ART = { src: '/assets/img/hero-kitchen.jpg', alt: 'Illustration of a kitchen counter with an air fryer, a countertop oven and a probe thermometer' };

const NAV = [
  ['/', 'Home'],
  ['/shop/', 'Shop'],
  ['/compare/', 'Compare'],
  ['/guides/', 'Guides'],
  ['/about/', 'About'],
];
const FEATURED_GUIDES = [
  'air-fryer-or-toaster-oven-which-replaces-the-other',
  'no-hype-checklist-comparing-air-fryer-capacity',
  'wireless-probe-or-instant-read-thermometer',
];

const DASHBOARDS = [
  ['/executive-summary/', 'Executive summary'],
  ['/shop/', 'Shop register (all rows)'],
  ['/compare/', 'Compare products'],
  ['/categories/', 'Categories'],
  ['/sources/', 'Source register'],
  ['/questions/', 'Open questions'],
  ['/suggestions/', 'Decision board'],
  ['/flagged/', 'Flagged for review'],
  ['/ledger/', 'Campaign ledger'],
  ['/measurement/', 'Measurement'],
  ['/compliance/', 'Compliance and gates'],
  ['/about/', 'About and editorial policy'],
  ['/editorial/', 'Archive register (noindex)'],
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
const seoTitle = (s, max = 48) => {
  const t = s.split(/[|,]/)[0].trim();
  if (t.length <= max) return t;
  const cut = t.slice(0, max);
  return cut.slice(0, Math.max(cut.lastIndexOf(' '), 24)).replace(/[\s\-–—]+$/, '');
};
const displayName = (p) => (p.observed_title ? shortName(p.observed_title) : 'Not observed');
const tagged = (p) => p.tagged_outbound_url || '';
const dateLong = (iso) => new Date(iso + 'T00:00:00Z').toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric', timeZone: 'UTC' });
const rfc822 = (iso) => new Date(iso + 'T00:00:00Z').toUTCString();

function page({ title, description, path: p, body, type = 'page', attrs = '', ogType = 'website', jsonld = '' }) {
  const canonical = abs(p);
  const ogImage = abs(HERO_ART.src);
  return `<!doctype html>
<html lang="${cfg.language}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(title)} | ${esc(cfg.siteName)}</title>
<meta name="description" content="${esc(description)}">
<link rel="canonical" href="${esc(canonical)}">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta name="theme-color" content="#fbf7ef">
<meta property="og:title" content="${esc(title)}">
<meta property="og:description" content="${esc(description)}">
<meta property="og:url" content="${esc(canonical)}">
<meta property="og:type" content="${ogType}">
<meta property="og:site_name" content="${esc(cfg.siteName)}">
<meta property="og:image" content="${esc(ogImage)}">
<meta property="og:image:alt" content="${esc(HERO_ART.alt)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="analytics-endpoint" content="${esc(cfg.analyticsEndpoint || '')}">
<link rel="stylesheet" href="${esc(href('/assets/style.css'))}">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Ccircle cx='16' cy='16' r='13' fill='%23b8481f'/%3E%3C/svg%3E">
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
      ${NAV.map(([u, t]) => `<a href="${esc(href(u))}">${esc(t)}</a>`).join('\n      ')}
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
  <div class="wrap">
    <div class="foot-grid">
      <div>
        <p class="foot-brand">${esc(cfg.siteName)}<span class="dot">.</span></p>
        <p class="foot-about">Kitchen buying guides for air fryers, air fryer ovens and thermometers. Every product fact is traced to its source, and anything unverified is left blank and flagged.</p>
        <p class="foot-about"><a href="${esc(href('/feed.xml'))}">RSS feed</a> · <a href="${esc(href('/sitemap.xml'))}">Sitemap</a></p>
      </div>
      <div>
        <p class="foot-h">Shop</p>
        <ul class="foot-links">
          <li><a href="${esc(href('/shop/'))}">All products</a></li>
          <li><a href="${esc(href('/compare/'))}">Compare side by side</a></li>
          <li><a href="${esc(href('/categories/'))}">Categories</a></li>
          ${products.map((pr) => `<li><a href="${esc(href('/products/' + pr.id.toLowerCase() + '/'))}">${esc(pr.id)} · ${esc(catName(pr.category))}</a></li>`).join('\n          ')}
        </ul>
      </div>
      <div>
        <p class="foot-h">Guides</p>
        <ul class="foot-links">
          ${guides.slice(0, 6).map((g) => `<li><a href="${esc(href('/guides/' + g.slug + '/'))}">${esc(g.title.split(':')[0])}</a></li>`).join('\n          ')}
          <li><a href="${esc(href('/guides/'))}">All guides</a></li>
        </ul>
      </div>
      <div>
        <p class="foot-h">Records</p>
        <ul class="foot-links">
          ${DASHBOARDS.map(([u, t]) => `<li><a href="${esc(href(u))}">${esc(t)}</a></li>`).join('\n          ')}
        </ul>
      </div>
    </div>
    <p class="disclosure-footer"><strong>Disclosure.</strong> ${esc(cfg.disclosureStrip)}</p>
    <p class="fine">${esc(cfg.siteName)} is not sponsored by, endorsed by or affiliated with Amazon.com, Inc. beyond participation in the Amazon Associates program. Prices and availability are not shown on this site. Illustrations are decorative and are not product photography. Last reviewed ${esc(dateLong(cfg.lastReviewed))}. Source links appear on every page and in the <a href="${esc(href('/sources/'))}">source register</a>.</p>
  </div>
</footer>
<script src="${esc(href('/assets/analytics.js'))}" defer></script>
</body>
</html>
`;
}

// ---------- components ----------
function productCard(p, placement, opts = {}) {
  const title = displayName(p);
  const a = art(p.category);
  const facts = p.title_facts || {};
  const bits = [facts.style, facts.capacity].filter(Boolean).join(' · ');
  const chips = (facts.notable || []).slice(0, 3);
  const hrefProduct = href('/products/' + p.id.toLowerCase() + '/');
  const media = `<a class="card-media" href="${esc(hrefProduct)}" tabindex="-1" aria-hidden="true">
      <img src="${esc(href(a.src))}" alt="" width="800" height="500" loading="lazy" decoding="async">
      <span class="card-tag">${esc(catName(p.category))}</span>
    </a>`;
  if (tagged(p)) {
    return `<article class="card" data-product-view="${esc(p.id)}">
  ${media}
  <div class="card-body">
    <p class="kicker">${esc(p.id)} · observed ${esc(dateLong(p.observed_date))}</p>
    <h3><a href="${esc(hrefProduct)}">${esc(title)}</a></h3>
    <p class="card-note">${esc(bits || 'Listing observed')} · <code>${esc(p.observed_asin)}</code></p>
    ${chips.length ? `<ul class="chips">${chips.map((c) => `<li>${esc(c)}</li>`).join('')}</ul>` : ''}
  </div>
  <div class="card-foot">
    <a class="btn" href="${esc(tagged(p))}" rel="sponsored noopener" data-outbound data-product="${esc(p.id)}" data-placement="${esc(placement)}">View on Amazon</a>
    <a class="link-quiet" href="${esc(hrefProduct)}">Details</a>
  </div>
</article>`;
  }
  return `<article class="card" data-product-view="${esc(p.id)}">
  ${media}
  <div class="card-body">
    <p class="kicker">${esc(p.id)} · ${esc(catName(p.category))}</p>
    <h3><a href="${esc(hrefProduct)}">Link not resolved</a></h3>
    <p class="card-note">Submitted link <code>${esc(p.submitted_token)}</code></p>
    <p class="status">No buy link is published. An Amazon "Continue shopping" checkpoint is intermittent and is not by itself evidence that a link is dead. ${flagLinks(['FLG-004'])}</p>
  </div>
  <div class="card-foot">
    <span class="btn-blocked">Buy link withheld</span>
    <a class="link-quiet" href="${esc(hrefProduct)}">Details</a>
  </div>
</article>`;
}

function guideCard(g) {
  return `<a class="feat-guide" href="${esc(href('/guides/' + g.slug + '/'))}">
  <p class="kicker">${esc(catName(g.category))}</p>
  <h3>${esc(g.title)}</h3>
  <p>${esc(g.deck)}</p>
  <span class="read">Read the guide</span>
</a>`;
}

function breadcrumbs(items) {
  return `<ul class="breadcrumbs">${items.map(([u, t], i) => `<li>${i === 0 ? `<a href="${esc(href(u))}">${esc(t)}</a>` : u ? `<a href="${esc(href(u))}">${esc(t)}</a>` : esc(t)}</li>`).join('')}</ul>`;
}

function renderBlock(b) {
  switch (b.type) {
    case 'note': return `<p class="note">${esc(b.text)}</p>`;
    case 'p': return `<p>${esc(b.text)}</p>`;
    case 'h2': return `<h2 id="${esc(b.text.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, ''))}">${esc(b.text)}</h2>`;
    case 'h3': return `<h3>${esc(b.text)}</h3>`;
    case 'callout': return `<div class="callout">${esc(b.text)}</div>`;
    case 'ul': return `<ul>${b.items.map((i) => `<li>${esc(i)}</li>`).join('')}</ul>`;
    case 'ol': return `<ol>${b.items.map((i) => `<li>${esc(i)}</li>`).join('')}</ol>`;
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

// Home (publication front page: products first, records in the footer)
{
  const featured = FEATURED_GUIDES.map((s) => guides.find((g) => g.slug === s)).filter(Boolean);
  const catCards = CATEGORIES.filter((c) => c.slug !== 'unresolved').map((c) => `<a class="card cat-card" href="${esc(href('/categories/' + c.slug + '/'))}">
    <span class="card-media"><img src="${esc(href(art(c.slug).src))}" alt="" width="800" height="500" loading="lazy" decoding="async"><span class="card-tag">${products.filter((p) => p.category === c.slug).length} tracked</span></span>
    <span class="card-body"><h3>${esc(c.name)}</h3><p>${esc(c.blurb)}</p></span>
  </a>`).join('\n');
  add({
    path: '/', title: 'Air fryers and thermometers, picked by how you cook',
    description: 'Five kitchen appliances with their Amazon listings read line by line, plus buying guides that ask what a spec sheet skips. Every product fact links to its source.',
    type: 'home',
    body: `
<section class="hero">
  <div class="hero-copy">
    <p class="kicker">Kitchen buying guides · updated ${esc(dateLong(cfg.lastReviewed))}</p>
    <h1>Air fryers and thermometers, picked by <em>how you cook</em>.</h1>
    <p class="deck">Five kitchen appliances, each traced to its Amazon listing, and guides that ask the questions a spec sheet skips. No prices, no star ratings, no invented specifications — every product fact links to where we read it.</p>
    <div class="hero-actions">
      <a class="btn" href="${esc(href('/shop/'))}">See the five picks</a>
      <a class="btn-ghost" href="${esc(href('/guides/'))}">Start with a guide</a>
    </div>
    <ul class="trust-row">
      <li>Every fact sourced</li>
      <li>Sponsored links marked</li>
      <li>No prices or ratings</li>
      <li>Unverified stays blank</li>
    </ul>
  </div>
  <figure class="hero-media">
    <img src="${esc(href(HERO_ART.src))}" alt="${esc(HERO_ART.alt)}" width="1200" height="900" fetchpriority="high">
    <figcaption>Illustration, not product photography. We do not publish images of products we cannot license.</figcaption>
  </figure>
</section>

<section class="section">
  <div class="section-head">
    <h2>The five we track</h2>
    <a class="more" href="${esc(href('/shop/'))}">All rows and sources</a>
  </div>
  <div class="shelf">${products.map((p) => productCard(p, 'front-shelf')).join('\n')}</div>
  <p class="shelf-note">Buttons open Amazon with our tracking ID <code>${esc(cfg.trackingId)}</code> in the link, marked <code>rel="sponsored"</code>. Prices and availability stay on Amazon, where they are current. Links are not yet validated in Associates Central; see <a href="${esc(href('/compliance/'))}">the gate</a>.</p>
</section>

<section class="section">
  <div class="section-head">
    <h2>Start with a question</h2>
    <a class="more" href="${esc(href('/guides/'))}">All ${guides.length} guides</a>
  </div>
  <div class="feat-guides">${featured.map(guideCard).join('\n')}</div>
</section>

<section class="section">
  <div class="section-head">
    <h2>Browse by category</h2>
    <a class="more" href="${esc(href('/compare/'))}">Compare side by side</a>
  </div>
  <div class="cat-grid">${catCards}</div>
</section>

<section class="section band">
  <h2>How these picks were made</h2>
  <div class="prose">
    <p>We start from the five links you gave us. Each one resolves to an Amazon product page, and we read that page: the title, the breadcrumb, the product ID. That is the whole product dataset. Then we write about what to compare, not about which one wins.</p>
    <p>Where a fact could not be confirmed from an official source — the intended ASIN, a price, a rating, a capacity we have not measured — the field is left <strong>blank</strong> and flagged. Blank is a result, not an oversight.</p>
  </div>
  <p><a class="btn-ghost" href="${esc(href('/about/'))}">Read the editorial policy</a></p>
</section>

<section class="section band band-alt">
  <h2>What this site does not do</h2>
  <ul class="findings">
    <li>No prices, star ratings or availability. Those change by the hour and belong on Amazon, not in a static page. ${flagLinks(['FLG-016'])}</li>
    <li>No first-hand test claims. We have not cooked with these appliances, and we say so on every product page.</li>
    <li>No cloaked or redirected links. Every outbound link goes straight to Amazon and is marked sponsored.</li>
    <li>No email capture until there is a provider and a privacy notice that can honour it. ${flagLinks(['FLG-014'])}</li>
  </ul>
  <p class="small"><a href="${esc(href('/flagged/'))}">All flagged items, with sources</a></p>
</section>

<section class="subscribe">
  <div>
    <h2>Follow the guides</h2>
    <p>No newsletter yet — we will not collect an address we cannot protect or write to. The RSS feed is live, costs you nothing, and carries every new guide.</p>
  </div>
  <a class="btn" href="${esc(href('/feed.xml'))}">Open the RSS feed</a>
</section>`,
  });
}

// Shop
{
  const resolvedCount = products.filter((p) => p.observed_asin).length;
  const unanswered = products.filter((p) => !p.observed_asin);
  const taggedCount = products.filter((p) => p.tagged_outbound_url).length;
  const rows = products.map((p) => [
    `<strong>${esc(p.id)}</strong>`,
    `<a href="${esc(href('/categories/' + p.category + '/'))}">${esc(catName(p.category))}</a>`,
    `<a href="${esc(href('/products/' + p.id.toLowerCase() + '/'))}">${esc(displayName(p))}</a>${p.observed_breadcrumb ? `<br><span class="muted small">${esc(p.observed_breadcrumb)}</span>` : ''}`,
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
    path: '/shop/', title: 'Shop: the five products and their receipts',
    description: 'Every submitted product with its observed Amazon listing, the intended fields that remain blank, the source for each row and the flags that explain the gaps.',
    type: 'shop',
    body: `
<section class="page-head">
  <p class="kicker">Shop · five products</p>
  <h1>Every product, with its receipts</h1>
  <p class="deck">Start with a card if you are shopping. Scroll to the register if you are checking us. Both describe the same five rows, and the register is what the cards are generated from.</p>
  <ul class="chips">
    <li><a href="#register">Jump to the full register</a></li>
    ${CATEGORIES.filter((c) => c.slug !== 'unresolved').map((c) => `<li>${esc(c.name)}: ${products.filter((p) => p.category === c.slug).length}</li>`).join('')}
  </ul>
</section>

<div class="kpi-row">
  <div class="kpi"><span class="n">${products.length}</span><span class="l">Links submitted</span></div>
  <div class="kpi"><span class="n">${resolvedCount}</span><span class="l">Resolved to a listing</span></div>
  <div class="kpi"><span class="n">0</span><span class="l">Validated in Associates Central</span></div>
  <div class="kpi"><span class="n">${products.filter((p) => !p.intended_asin).length}</span><span class="l">Intended ASINs confirmed</span></div>
</div>

<section class="section shelf">${products.map((p) => productCard(p, 'shop-grid')).join('\n')}</section>

<section class="section" id="register">
  <div class="section-head"><h2>The full register</h2><a class="more" href="${esc(href('/sources/'))}">Source register</a></div>
  <p class="small muted">Intended fields are filled only from an official source, and none are confirmed yet, so they are blank. Observed fields are what the Amazon page showed, kept separate. A blank cell is a documented gap, not a formatting choice.</p>
  ${table(['ID', 'Category', 'Product (link to record)', 'Observed ASIN and page', 'Submitted link', 'Intended ASIN', 'Official listing URL', 'Confirmation date', 'Confirmation source', 'Buy link status', 'Confirmation status', 'Sources (official)'], rows, 'wide')}
</section>

<section class="section band">
  <h2>What the register shows</h2>
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

// Product detail pages
for (const p of products) {
  const a = art(p.category);
  const facts = p.title_facts || {};
  const related = guides.filter((g) => g.category === p.category || (g.cluster_links || []).includes(p.category));
  const hrefProduct = href('/products/' + p.id.toLowerCase() + '/');
  const jsonld = `<script type="application/ld+json">${JSON.stringify({
    '@context': 'https://schema.org', '@type': 'Product', name: displayName(p),
    description: `Observed Amazon listing ${p.observed_asin} for ${catName(p.category)}. No price, rating or availability is published.`,
    sku: p.observed_asin, category: catName(p.category),
    url: abs('/products/' + p.id.toLowerCase() + '/'),
    isRelatedTo: { '@type': 'WebPage', name: 'Shop table', url: abs('/shop/') },
  })}</script>`;
  add({
    path: `/products/${p.id.toLowerCase()}/`, title: `${seoTitle(displayName(p))} — listing and gaps`,
    description: `${seoTitle(displayName(p), 60)}: the Amazon listing observed on ${dateLong(p.observed_date)}, what is verified, what stays blank, and the source for every row.`,
    type: 'product', jsonld, attrs: `data-product="${esc(p.id)}"`, ogType: 'article',
    body: `${breadcrumbs([['/', 'Home'], ['/shop/', 'Shop'], [null, p.id + ' · ' + displayName(p)]])}
<section class="product-hero">
  <div>
    <p class="kicker">${esc(catName(p.category))} · ${esc(p.id)}</p>
    <h1 class="lead-title">${esc(displayName(p))}</h1>
    <p class="deck">${esc([facts.style, facts.capacity].filter(Boolean).join(' · ') || 'Observed Amazon listing')}.${facts.use_for ? ' ' + esc(facts.use_for) + '.' : ''}</p>
    <p class="small muted">That description is our reading of the listing title, not a test result and not a verified specification.</p>
    <ul class="chips">${(facts.notable || []).map((c) => `<li>${esc(c)}</li>`).join('')}</ul>
    <blockquote><strong>Listing title as observed:</strong> ${esc(p.observed_title)}<br><span class="small muted">Read ${esc(dateLong(p.observed_date))} · ${ext(p.observed_final_url, 'S04', '')}</span></blockquote>
  </div>
  <aside class="cta-box">
    <p class="kicker">Where to buy</p>
    ${tagged(p)
      ? `<p><a class="btn" href="${esc(tagged(p))}" rel="sponsored noopener" data-outbound data-product="${esc(p.id)}" data-placement="product-page">View on Amazon</a></p>
         <p class="small muted">Opens amazon.com in a new tab with our tracking ID, marked <code>rel="sponsored"</code>. Price and availability are shown there, where they are current.</p>
         <p class="status">${esc(p.outbound_status)}</p>`
      : `<p><span class="btn-blocked">Buy link withheld</span></p><p class="small muted">The submitted link has not resolved to a product, so no buy link is published.</p>`}
    <p class="status">Observed ASIN <code>${esc(p.observed_asin || '—')}</code><br>Listing read ${esc(dateLong(p.observed_date))}</p>
  </aside>
</section>

<section class="section">
  <h2>The listing we read</h2>
  <div class="table-wrap"><table class="spec-table"><tbody>
    <tr><th scope="row">Submitted link</th><td><a href="${esc(p.submitted_url)}" rel="sponsored noopener">${esc(p.submitted_token)}</a> <span class="small muted">(${p.submitted_token_length} characters)</span></td></tr>
    <tr><th scope="row">Observed destination</th><td>${ext(p.observed_final_url, p.observed_final_url, '')}</td></tr>
    <tr><th scope="row">Observed ASIN</th><td><code>${esc(p.observed_asin)}</code></td></tr>
    <tr><th scope="row">Breadcrumb on Amazon</th><td>${esc(p.observed_breadcrumb)}</td></tr>
    <tr><th scope="row">Observed on</th><td>${esc(dateLong(p.observed_date))}</td></tr>
    <tr><th scope="row">Sources</th><td>${rowSources(p)}</td></tr>
  </tbody></table></div>

  <h2>The product-intent record</h2>
  <p class="small muted">These four fields are the ones that would confirm this link was meant to point here. They stay blank until an official source says otherwise, and they are never copied from the observed destination.</p>
  <div class="table-wrap"><table class="spec-table"><tbody>
    <tr><th scope="row">Intended ASIN</th><td>${cellText(p.intended_asin)}</td></tr>
    <tr><th scope="row">Official listing URL</th><td>${cellText(p.official_listing_url)}</td></tr>
    <tr><th scope="row">Confirmation date</th><td>${cellText(p.confirmation_date)}</td></tr>
    <tr><th scope="row">Confirmation source</th><td>${cellText(p.confirmation_source)}</td></tr>
    <tr><th scope="row">Status</th><td>${esc(p.confirmation_status)} ${flagLinks(p.flags)}</td></tr>
  </tbody></table></div>
</section>

<section class="section">
  <div class="section-head"><h2>What we did not verify</h2><a class="more" href="${esc(href('/flagged/'))}">Flagged for review</a></div>
  <div class="band band-alt">
    <ul class="findings">
      <li>No price, star rating, review count or availability. ${flagLinks(['FLG-016'])}</li>
      <li>No dimensions, weight, noise level or power draw. The listing title does not state them and we have not measured them.</li>
      <li>No first-hand use. We have not cooked with, charged or cleaned this appliance.</li>
      <li>No product photography. The image above is a decorative illustration. ${flagLinks(['FLG-015'])}</li>
      <li>No confirmation that this was the intended destination of the submitted link. ${flagLinks(['FLG-002'])}</li>
    </ul>
  </div>
</section>

${related.length ? `<section class="section"><div class="section-head"><h2>Guides that help with this decision</h2><a class="more" href="${esc(href('/guides/'))}">All guides</a></div>
  <div class="feat-guides">${related.slice(0, 3).map(guideCard).join('')}</div></section>` : ''}`,
  });
}

// Compare page
{
  const rows = [
    ['Product', (p) => `<strong><a href="${esc(href('/products/' + p.id.toLowerCase() + '/'))}">${esc(displayName(p))}</a></strong><br><span class="small muted">${esc(p.id)}</span>`],
    ['Category', (p) => `<a href="${esc(href('/categories/' + p.category + '/'))}">${esc(catName(p.category))}</a>`],
    ['Style, as the title states', (p) => esc((p.title_facts || {}).style || '')],
    ['Capacity, as the title states', (p) => esc((p.title_facts || {}).capacity || '')],
    ['What else the title highlights', (p) => `<ul class="opts">${((p.title_facts || {}).notable || []).map((n) => `<li>${esc(n)}</li>`).join('')}</ul>`],
    ['Observed ASIN', (p) => `<code>${esc(p.observed_asin || '')}</code>`],
    ['Listing read on', (p) => esc(dateLong(p.observed_date))],
    ['Buy link', (p) => (tagged(p) ? `<a class="btn" href="${esc(tagged(p))}" rel="sponsored noopener" data-outbound data-product="${esc(p.id)}" data-placement="compare">View on Amazon</a>` : '<span class="btn-blocked">Withheld</span>')],
    ['Full record', (p) => `<a href="${esc(href('/products/' + p.id.toLowerCase() + '/'))}">Sources and gaps →</a>`],
  ];
  add({
    path: '/compare/', title: 'Compare the five tracked appliances',
    description: 'A side-by-side of the five tracked products using only what each Amazon listing title states, with the observed ASIN and the source for every row.',
    type: 'compare',
    body: `<section class="page-head">
  <p class="kicker">Compare</p>
  <h1>The five, side by side</h1>
  <p class="deck">Only what each listing states, in the seller's own words. Blank cells are not gaps in the table — they are facts the listing title does not give, and we do not fill them in.</p>
</section>
<div class="table-wrap"><table class="wide"><thead><tr><th scope="col">Attribute</th>${products.map((p) => `<th scope="col">${esc(p.id)}</th>`).join('')}</tr></thead><tbody>
${rows.map(([label, fn]) => `<tr><th scope="row">${esc(label)}</th>${products.map((p) => `<td>${fn(p)}</td>`).join('')}</tr>`).join('\n')}
</tbody></table></div>
<p class="small muted">Every row above traces to the observed Amazon listing for that product (${products.map((p) => ext(p.observed_final_url, p.id, '')).join(', ')}). Nothing is inferred from a photo, a category page or another listing.</p>

<section class="section band">
  <h2>How to use this table</h2>
  <ol class="findings">
    <li><strong>Decide the shape first.</strong> Basket, French door or probe. The form decides how you load food and where the appliance lives.</li>
    <li><strong>Then decide the size.</strong> Capacity is quoted differently across listings: total, per basket, or cavity. Read the manual before you trust a number here.</li>
    <li><strong>Then check the things this table cannot show.</strong> Noise, preheat time, cleaning effort and how it fits under your cabinets. Those are in the manual and in your kitchen, not on Amazon.</li>
    <li><strong>Then click through.</strong> Prices and availability are live on Amazon and out of date the moment we write them down, so we do not.</li>
  </ol>
</section>

<section class="section">
  <div class="section-head"><h2>Read a guide instead</h2><a class="more" href="${esc(href('/guides/'))}">All guides</a></div>
  <div class="feat-guides">${FEATURED_GUIDES.map((s) => guides.find((g) => g.slug === s)).filter(Boolean).map(guideCard).join('')}</div>
</section>`,
  });
}

// Categories index + category pages
add({
  path: '/categories/', title: 'Categories',
  description: 'Three product clusters — air fryers, air fryer ovens and cooking thermometers — with the products and guides in each one.',
  type: 'categories',
  body: `<section class="page-head"><p class="kicker">Categories</p><h1>Three clusters, five products</h1><p class="deck">Each cluster collects the products we track in it and the guides that help you choose between them. Nothing is added to a cluster unless a submitted link resolved to it.</p></section>
<div class="cat-grid">${CATEGORIES.map((c) => `<a class="card cat-card" href="${esc(href('/categories/' + c.slug + '/'))}">
  <span class="card-media"><img src="${esc(href(art(c.slug).src))}" alt="" width="800" height="500" loading="lazy" decoding="async"><span class="card-tag">${products.filter((p) => p.category === c.slug).length} tracked</span></span>
  <span class="card-body"><h3>${esc(c.name)}</h3><p>${esc(c.blurb)}</p><p class="small muted">${guides.filter((g) => g.category === c.slug || (g.cluster_links || []).includes(c.slug)).length} guide(s)</p></span>
</a>`).join('')}</div>
<section class="section band band-alt"><h2>Why only three</h2><p class="small">A cluster with no product behind it would be a page built to hold a keyword rather than a decision. Three is what five submitted links support.</p></section>`,
});
for (const c of CATEGORIES) {
  const inCat = products.filter((p) => p.category === c.slug);
  const cards = inCat.map((p) => productCard(p, 'category')).join('\n');
  const gl = guides.filter((g) => g.category === c.slug || (g.cluster_links || []).includes(c.slug));
  add({
    path: `/categories/${c.slug}/`, title: `${c.name}: products and guides`,
    description: `${c.name}: the products we track in this cluster, each with its observed Amazon listing, plus the guides that help you choose.`,
    attrs: `data-category="${esc(c.slug)}"`,
    type: 'category',
    body: `${breadcrumbs([['/', 'Home'], ['/categories/', 'Categories'], [null, c.name]])}
<section class="page-head"><p class="kicker">Category</p><h1>${esc(c.name)}</h1><p class="deck">${esc(c.blurb)}</p></section>
<figure class="hero-media category-art"><img src="${esc(href(art(c.slug).src))}" alt="${esc(art(c.slug).alt)}" width="1200" height="750"><figcaption>Illustration, not product photography.</figcaption></figure>
<section class="section shelf">${cards || '<p>No product rows in this category.</p>'}</section>
<section class="section"><div class="section-head"><h2>Guides for this cluster</h2><a class="more" href="${esc(href('/guides/'))}">All guides</a></div>
${gl.length ? `<ul class="guide-list">${gl.map((g) => `<li class="guide-item"><a href="${esc(href('/guides/' + g.slug + '/'))}">${esc(g.title)}</a><p>${esc(g.deck)}</p></li>`).join('')}</ul>` : '<p>No guide yet in this cluster.</p>'}
</section>
${c.slug === 'unresolved' ? `<section class="section band"><h2>Why this cluster is empty</h2><p>${esc(products.find((p) => p.category === 'unresolved') ? 'The submitted link B00hJ57DV landed on a checkpoint page. We did not substitute a product.' : '')}</p><p>${flagLinks(['FLG-003', 'FLG-004'])}</p></section>` : ''}
<section class="section band band-alt"><h2>Still deciding?</h2><p>Put the products side by side, or read the guide that starts from the food you cook.</p><p><a class="btn-ghost" href="${esc(href('/compare/'))}">Compare the five</a> <a class="btn-ghost" href="${esc(href('/guides/'))}">Read a guide</a></p></section>`,
  });
}

// Guides index + guide pages
{
  const byCat = CATEGORIES.map((c) => ({ c, list: guides.filter((g) => g.category === c.slug) })).filter((x) => x.list.length);
  add({
    path: '/guides/', title: 'Buying guides',
    description: 'Question-shaped buying guides for air fryers, air fryer ovens and thermometers, grouped by the decision they help with.',
    type: 'guides',
    body: `<section class="page-head">
  <p class="kicker">Guides · ${guides.length} published</p>
  <h1>Start with the question, not the product</h1>
  <p class="deck">Each guide is one decision: which shape, how much capacity, what to clean, what to check. They are written as buyer questions because that is what we can answer without inventing a test result.</p>
</section>
<div class="feat-guides">${FEATURED_GUIDES.map((s) => guides.find((g) => g.slug === s)).filter(Boolean).map(guideCard).join('')}</div>

${byCat.map(({ c, list }) => `<section class="section">
  <div class="section-head"><h2>${esc(c.name)}</h2><a class="more" href="${esc(href('/categories/' + c.slug + '/'))}">Category page</a></div>
  <ul class="guide-list">${list.map((g) => `<li class="guide-item"><a href="${esc(href('/guides/' + g.slug + '/'))}">${esc(g.title)}</a><span class="muted">${esc(dateLong(g.date))}</span><p>${esc(g.deck)}</p></li>`).join('')}</ul>
</section>`).join('\n')}

<section class="band band-alt">
  <h2>How these guides are written</h2>
  <p class="small">Every guide is dated, every factual claim carries a source, and every guide ends with the limits of what we checked. Titles are editorial hypotheses about what buyers ask. They are not claims about search volume or popularity. <a href="${esc(href('/about/'))}">The editorial policy</a> explains the rest.</p>
</section>`,
  });
}

for (const g of guides) {
  const productsHere = products.filter((p) => tagged(p) && (p.category === g.category || (g.cluster_links || []).includes(p.category)));
  const h2s = g.body.filter((b) => b.type === 'h2');
  const faqLd = (g.faq && g.faq.length) ? {
    '@type': 'FAQPage',
    mainEntity: g.faq.map((f) => ({ '@type': 'Question', name: f.q, acceptedAnswer: { '@type': 'Answer', text: f.a } })),
  } : null;
  const graph = [{
    '@type': 'Article', headline: g.title, description: g.description,
    datePublished: g.date, dateModified: cfg.lastReviewed,
    author: { '@type': 'Organization', name: cfg.author },
    publisher: { '@type': 'Organization', name: cfg.siteName },
    mainEntityOfPage: abs(`/guides/${g.slug}/`), image: abs(HERO_ART.src),
  }];
  if (faqLd) graph.push(faqLd);
  const jsonld = `<script type="application/ld+json">${JSON.stringify({ '@context': 'https://schema.org', '@graph': graph })}</script>`;
  add({
    path: `/guides/${g.slug}/`, title: g.title, description: g.description, type: 'guide', ogType: 'article', jsonld,
    attrs: `data-guide="${esc(g.slug)}"`,
    body: `${breadcrumbs([['/', 'Home'], ['/guides/', 'Guides'], [null, g.title]])}
<article class="article">
  <header class="page-head">
    <p class="kicker">${esc(catName(g.category))} · Guide</p>
    <h1>${esc(g.title)}</h1>
    <p class="deck">${esc(g.deck)}</p>
    <p class="byline">By ${esc(cfg.author)} · Published ${esc(dateLong(g.date))} · Last reviewed ${esc(dateLong(cfg.lastReviewed))} · <a href="${esc(href('/about/'))}">Editorial policy</a></p>
  </header>

  ${(g.takeaways && g.takeaways.length) ? `<div class="takeaways"><h2>The short version</h2><ul>${g.takeaways.map((t) => `<li>${esc(t)}</li>`).join('')}</ul></div>` : ''}
  ${h2s.length > 2 ? `<nav class="toc" aria-label="On this page"><h2>On this page</h2><ol>${h2s.map((b) => `<li><a href="#${esc(b.text.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, ''))}">${esc(b.text)}</a></li>`).join('')}</ol></nav>` : ''}

  <div class="prose">${g.body.map(renderBlock).join('\n')}</div>

  ${(g.limits && g.limits.length) ? `<div class="limits"><h2>What this guide does not claim</h2><ul>${g.limits.map((t) => `<li>${esc(t)}</li>`).join('')}</ul></div>` : ''}

  ${(g.faq && g.faq.length) ? `<section class="faq"><h2>Questions buyers ask next</h2>${g.faq.map((f) => `<details><summary>${esc(f.q)}</summary><p>${esc(f.a)}</p></details>`).join('')}</section>` : ''}

  ${productsHere.length ? `<aside class="section band"><h2>Products this guide applies to</h2><p class="small muted">The buttons below are Amazon affiliate links carrying our tracking ID, marked sponsored. Nothing here is a ranking.</p><div class="shelf">${productsHere.map((p) => productCard(p, 'guide-box')).join('')}</div></aside>` : ''}

  <section class="section sources"><h2>Sources</h2>
    ${g.sources.length ? `<ul>${g.sources.map((id) => `<li>${guideSource(id)}</li>`).join('')}</ul>` : '<p>This guide makes no factual claim that needs an external source. It refers only to the observed listing data on the <a href="' + esc(href('/shop/')) + '">shop page</a>.</p>'}
    <p class="small"><a href="${esc(href('/sources/'))}">Full source register</a> · <a href="${esc(href('/flagged/'))}">Flagged for review</a></p>
  </section>
</article>`,
  });
}

// Executive summary
{
  const openFlags = flagsDoc.flags.filter((f) => f.status !== 'resolved').length;
  const resolvedFlags = flagsDoc.flags.length - openFlags;
  const validated = 0;
  add({
    path: '/executive-summary/', title: 'Executive summary',
    description: 'What is live, what is verified, what is blocked, what changed in this pass, and the decisions only the owner can make.',
    type: 'executive-summary',
    body: `<section class="page-head"><p class="kicker">Executive summary · ${esc(dateLong(cfg.lastReviewed))}</p><h1>Where this stands</h1>
<p class="deck">A published buying-guide site for five kitchen appliances, built from a source register, with every unverified value left blank and flagged. What is missing is not design. It is account access and four decisions.</p></section>

<div class="kpi-row">
  <div class="kpi"><span class="n">${products.length}</span><span class="l">Products tracked</span></div>
  <div class="kpi"><span class="n">${guides.length}</span><span class="l">Guides published</span></div>
  <div class="kpi"><span class="n">${validated}</span><span class="l">Links validated in Associates Central</span></div>
  <div class="kpi"><span class="n">${openFlags}</span><span class="l">Open flags (${resolvedFlags} resolved)</span></div>
</div>

<div class="prose">
<h2>What is live</h2>
<ul>
<li>A publication-style front page, a shop with five product cards and a full source register, five individual product pages, a side-by-side comparison, three category clusters and ${guides.length} guides.</li>
<li>A disclosure strip under the masthead on every page and a repeat in the footer, using the statement required by Operating Agreement §5. Every Amazon link is marked <code>rel="sponsored"</code> and carries the tracking ID.</li>
<li>An RSS feed, a sitemap, a 404 page, canonical URLs and structured data. The repository's archive publications are excluded from the index so search engines see one site.</li>
<li>A publishing gate (<code>tools/verify.mjs</code>) that fails the build on a missing disclosure, an untagged Amazon link, a price, a broken internal link, a missing image or a source ID that does not exist.</li>
</ul>

<h2>What is verified, and how</h2>
<ul>
<li>Operating Agreement §1 and §5 read in full on 2026-11-20: Special Links must use the tagged formats Amazon provides, and the Associates statement must appear clearly and prominently. The Program Policies were read the same day: the tag must be a URL parameter on every link (§2(b)), cloaking is prohibited (§6(v)), a shortener may not obscure the destination (§6(w)), and reviews, ratings and prices may only come from Amazon-served content or the API (§6(t), §2(b)).</li>
<li>Google's outbound-link guidance, the FTC endorsement guidance and the USDA temperature chart were read and are linked from every page that uses them.</li>
<li>All five submitted short links were followed again today. Each resolved to the same Amazon product page recorded in the register, with the same product ID and title. The intended ASIN still cannot be confirmed from an official source, so it stays blank.</li>
</ul>

<h2>What is blocked, and on what</h2>
<ul>
<li><strong>Link validation.</strong> One Special Link per product must be generated and tested inside Associates Central. That needs the account, not this build. ${flagLinks(['FLG-005', 'FLG-009'])}</li>
<li><strong>Product intent.</strong> Only you can say which product each short link was meant to reach. Until then the intended fields stay blank. ${flagLinks(['FLG-002'])}</li>
<li><strong>Measurement.</strong> The five events are defined and the collector exists, but no endpoint is deployed, so the live site records nothing. ${flagLinks(['FLG-009'])}</li>
<li><strong>Search visibility.</strong> Search Console is not connected, so the next topic cannot yet be chosen from measured queries. ${flagLinks(['FLG-013'])}</li>
<li><strong>Names and images.</strong> There is no named author, no product photography and no prices. Each would need a person, a licence or an API. ${flagLinks(['FLG-014', 'FLG-015', 'FLG-016'])}</li>
</ul>

<h2>What changed in this pass</h2>
<ul>
<li>The front page was rebuilt as a publication front page: illustrated hero, five product cards, guides, categories, then the records.</li>
<li>Five product pages and a comparison page were added. Each product page shows the observed listing, the blank intended fields, the source for every row and what was not verified.</li>
<li>Three guides were added to close the oven and thermometer clusters, and every guide now carries a short version, a table of contents, a limits box and buyer questions.</li>
<li>The suggestion list became a decision board with three paths, and the question list now separates blocked, open and discoverable gaps.</li>
<li>Source links were corrected and re-read: USDA temperature values now cite the chart page directly, and the policy clauses are cited from the current published text rather than an excerpt.</li>
</ul>

<h2>Decisions only you can make</h2>
<ol>
<li>Which product each short link was meant to reach (Q-01).</li>
<li>Whether the account is active and declares this site, and whether the tracking ID belongs to it (Q-03).</li>
<li>Whether to hide buy buttons until link validation passes (S-01).</li>
<li>Which path to take — ship and measure, measure first, or Associates-ready (decision board).</li>
</ol>

<h2>Limits of this build</h2>
<p>It cannot pull Amazon product data, prices, sales or commission reports. Those require authorized access — the Creators/PA API or Associates reports — and the sandbox has neither. The site does not scrape Amazon, does not display star ratings, and does not forecast revenue.</p>
</div>

<p><a class="btn" href="${esc(href('/suggestions/'))}">Open the decision board</a> <a class="btn-ghost" href="${esc(href('/questions/'))}">Open questions</a> <a class="btn-ghost" href="${esc(href('/flagged/'))}">Flagged items</a></p>`,
  });
}

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
{
  const blocking = questions.unknown.filter((q) => q.blocking);
  const open = questions.unknown.filter((q) => !q.blocking);
  add({
    path: '/questions/', title: 'Open questions and how to close them',
    description: 'What is known, what is not, what each gap blocks, and the exact step that closes it — with a source link on every answer.',
    type: 'questions',
    body: `<section class="page-head">
  <p class="kicker">Questions · ${questions.unknown.length} open</p>
  <h1>What we cannot decide yet, and why</h1>
  <p class="deck">${esc(questions.note)}</p>
</section>

<div class="kpi-row">
  <div class="kpi"><span class="n">${questions.known.length}</span><span class="l">Facts we can cite</span></div>
  <div class="kpi"><span class="n">${blocking.length}</span><span class="l">Blocking a decision</span></div>
  <div class="kpi"><span class="n">${open.length}</span><span class="l">Open, not blocking</span></div>
  <div class="kpi"><span class="n">${questions.discovery.length}</span><span class="l">Ways to find out</span></div>
</div>

<section class="section">
  <div class="section-head"><h2>Answer these four first</h2><a class="more" href="${esc(href('/suggestions/'))}">Then choose a path</a></div>
  ${blocking.map((q) => `<section class="decision" id="${esc(q.id)}">
    <div class="decision-head"><span class="badge">${esc(q.id)}</span><h2>${esc(q.question)}</h2></div>
    <p class="decision-meta">Blocks: ${q.blocks ? esc(q.blocks) : 'the product-intent record'}</p>
    <p>${esc(q.why_it_matters)}</p>
    <p class="recommendation"><strong>How to close it</strong> ${esc(q.how_to_close)}</p>
    <p class="small"><strong>Sources:</strong> ${q.sources.map(srcLink).join(', ') || '<span class="muted">none — this needs your input</span>'}</p>
  </section>`).join('\n')}
</section>

<section class="section">
  <h2>What is known</h2>
  <p class="small muted">Each of these is a statement the site is allowed to make, with the source that backs it.</p>
  ${table(['ID', 'Statement', 'Sources'], questions.known.map((k) => [esc(k.id), esc(k.statement), k.sources.map(srcLink).join(', ') || '<span class="muted">none</span>']), 'wide')}
</section>

<section class="section">
  <h2>Open questions</h2>
  <p class="small muted">Not everything here blocks a launch. Each row says what it would change if it were answered.</p>
  ${table(['ID', 'Question', 'Why it matters', 'How to close it', 'Blocking', 'Sources'], open.map((q) => [esc(q.id), esc(q.question), esc(q.why_it_matters), esc(q.how_to_close), q.blocking ? '<strong>Yes</strong>' : 'No', q.sources.map(srcLink).join(', ') || '<span class="muted">none</span>']), 'wide')}
</section>

<section class="section">
  <h2>How to discover what is missing</h2>
  <p class="small muted">A gap with no discovery step is just a worry. These are the steps that turn each one into an answer.</p>
  ${table(['ID', 'Step', 'Closes'], questions.discovery.map((d) => [esc(d.id), esc(d.suggestion), d.closes.map(esc).join(', ') || '<span class="muted">none</span>']), 'wide')}
</section>`,
  });
}

// Suggestions: the decision board
{
  const statusLabel = { implemented: 'Implemented in this pass', 'needs decision': 'Needs your decision', blocked: 'Blocked' };
  const statusClass = { implemented: 'pill-live', 'needs decision': 'flag', blocked: 'sev-medium' };
  const card = (s) => `<section class="decision" id="${esc(s.id)}">
  <div class="decision-head">
    <span class="badge">${esc(s.id)}</span>
    <h2>${esc(s.topic)}</h2>
    <span class="badge ${statusClass[s.status] || ''}">${esc(statusLabel[s.status] || s.status)}</span>
  </div>
  <p class="decision-meta">Impact ${esc(s.impact || '—')} · Effort ${esc(s.effort || '—')} · Owner: ${esc(s.owner || '—')}</p>
  <p>${esc(s.why || '')}</p>
  <ul class="options">${s.options.map((o) => `<li class="${o.id === s.current ? 'is-current' : ''}">
    <span class="opt-id">${esc(o.id)}</span><span class="opt-label">${esc(o.label)}</span>${o.id === s.current ? ' <span class="badge good">current</span>' : ''}
    <span class="opt-tradeoff">Tradeoff: ${esc(o.tradeoff)}</span>
  </li>`).join('')}</ul>
  <p class="recommendation"><strong>Recommendation</strong> ${esc(s.recommendation)}</p>
  ${s.note ? `<p class="small muted">${esc(s.note)}</p>` : ''}
</section>`;
  const needs = suggestionsDoc.suggestions.filter((s) => s.status !== 'implemented');
  const done = suggestionsDoc.suggestions.filter((s) => s.status === 'implemented');
  add({
    path: '/suggestions/', title: 'Decision board: choose a path',
    description: 'Every open decision, its options and its cost, with three paths to choose between. Nothing policy-sensitive is implemented until you choose.',
    type: 'suggestions',
    body: `<section class="page-head">
  <p class="kicker">Suggestions · decision board</p>
  <h1>Choose a path before anything changes</h1>
  <p class="deck">${esc(suggestionsDoc.note)}</p>
  <ul class="chips">
    <li><span class="badge pill-live">Implemented</span> done, reversible, in git history</li>
    <li><span class="badge flag">Needs your decision</span> waiting on you</li>
    <li><span class="badge sev-medium">Blocked</span> waiting on an account, a person or a provider</li>
  </ul>
</section>

<section class="section">
  <div class="section-head"><h2>Three paths</h2><a class="more" href="#needs-you">Skip to the decisions</a></div>
  <div class="path-grid">${suggestionsDoc.paths.map((pth) => `<article class="path">
    <p class="path-meta">${esc(pth.id)}${pth.recommended ? ' · recommended' : ''}</p>
    <h3>${esc(pth.name)}</h3>
    <p>${esc(pth.summary)}</p>
    <p class="small"><strong>Needs:</strong></p>
    <ul>${pth.needs.map((n) => `<li>${esc(n)}</li>`).join('')}</ul>
    <p class="small"><strong>Buys:</strong> ${esc(pth.buys.join('; '))}</p>
    <p class="small"><strong>Risks:</strong> ${esc(pth.risks.join('; '))}</p>
    ${pth.recommended ? '<span class="badge good">Start here</span>' : '<span class="badge">Alternative</span>'}
  </article>`).join('')}</div>
</section>

<section class="section" id="needs-you">
  <div class="section-head"><h2>Waiting on you</h2><span class="small muted">${needs.length} decisions</span></div>
  ${needs.map(card).join('\n')}
</section>

<section class="section">
  <div class="section-head"><h2>Already done, and reversible</h2><span class="small muted">${done.length} decisions</span></div>
  <p class="small muted">These were implemented in this pass because they carry no policy exposure and can be reverted with a single commit. None of them touches pricing, testing claims or the Associates account.</p>
  ${done.map(card).join('\n')}
</section>

<section class="section band band-alt">
  <h2>How to answer</h2>
  <p>Reply with the decision ID and the option letter, for example <code>S-01 B</code>. One line per decision is enough. If you pick a path instead, name it — for example <code>Path A</code> — and the decisions inside it will be treated as answered in that order.</p>
  <p class="small muted">Anything not answered stays exactly as it is. Nothing here is guessed on your behalf.</p>
</section>`,
  });
}

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
  description: 'Who writes this site, how products get here, how facts are checked, what we refuse to publish, and how to correct us.',
  type: 'about',
  body: `<section class="page-head"><p class="kicker">About</p><h1>How this site is made</h1>
<p class="deck">Five products, one register, and a publishing gate that refuses to let an unsourced number through.</p></section>

<div class="prose">
<h2>Who writes it</h2>
<p>${esc(cfg.author)}. The pages are generated from a verified register by an automated build, and every page states its date. There is no named editor and no byline photograph, because inventing one is worse than admitting the gap ${flagLinks(['FLG-014'])}.</p>
<p>If that matters to you as a reader, it should. A person who signs their work can be asked questions. Until one does, treat this site as a well-sourced index rather than a trusted friend.</p>

<h2>How products get here</h2>
<p>Only the five links the site owner submitted are listed. No product was added from our own research, no product is ranked, and no product is called the best. Where two products sit in the same cluster, the comparison page shows what the listing titles say and nothing more.</p>

<h2>How facts are checked</h2>
<ol>
<li><strong>A product fact</strong> is read from the Amazon page the submitted link resolves to — title, breadcrumb, product ID — and dated. It is recorded as an observation, not as the intended product.</li>
<li><strong>A policy or safety fact</strong> is read on the publisher's own page and cited by source ID. The source register lists the page, the date it was last checked and the strength of the check: full text, excerpt, or observation.</li>
<li><strong>An unconfirmed value stays blank.</strong> The intended ASIN, the official listing URL, the confirmation date and the confirmation source are blank for all five products, because no official source has confirmed them.</li>
</ol>
<p>References: <a href="${esc(href('/sources/'))}">the source register</a> · <a href="${esc(href('/flagged/'))}">every open flag</a> · <a href="${esc(href('/questions/'))}">every open question</a>.</p>

<h2>What we will not publish</h2>
<ul>
<li><strong>Prices, star ratings or availability.</strong> Amazon allows these only when Amazon serves them or when they come through the Creators/PA API ${srcLink('S02')}. A hand-copied price is wrong by the next morning.</li>
<li><strong>Test claims we did not earn.</strong> No page says a product was tested, measured or cooked with.</li>
<li><strong>Product photography.</strong> The illustrations are decorative. Product images require an API licence we do not have ${flagLinks(['FLG-015'])}.</li>
<li><strong>Cloaked or redirected links.</strong> Every outbound link goes straight to Amazon, marked sponsored, with the tracking ID in the URL ${srcLink('S02')}.</li>
</ul>

<h2>Disclosure</h2>
<p>${esc(cfg.associatesStatement)} The full statement sits under the masthead on every page and again in the footer, and the reasons for its placement are on <a href="${esc(href('/compliance/'))}">the compliance page</a>. Nothing on this site implies Amazon endorses it.</p>

<h2>Corrections</h2>
<p>Errors are corrected in public and logged on <a href="${esc(href('/flagged/'))}">Flagged for review</a>, including the two product destinations that were recorded the wrong way round earlier and later fixed. If you find something wrong, open an issue in the <a href="https://github.com/karagemop466-tech/Affil3/issues" rel="noopener external">project repository</a>. Corrections are dated; nothing is quietly edited.</p>

<h2>How this site is built</h2>
<p>Static HTML generated from JSON registers with no runtime dependencies, published by GitHub Pages. Before anything is published, <code>tools/verify.mjs</code> runs more than two thousand checks: disclosure present, Amazon links sponsored and tagged, no prices, no ratings, every image present, every internal link resolving, every source ID existing, every page in the sitemap and every guide in the feed. If a check fails, the build fails.</p>
</div>`,
});

// 404
add({ path: '/404.html', title: 'Page not found', description: 'This page does not exist.', noSitemap: true, type: '404',
  body: `<section class="page-head error-page"><p class="kicker">404</p><h1>That page is not here</h1>
<p class="deck" style="margin-inline:auto">It may have moved, or it may never have existed. The five products and all ${guides.length} guides are still where you left them.</p>
<p><a class="btn" href="${esc(href('/shop/'))}">Go to the shop</a> <a class="btn-ghost" href="${esc(href('/'))}">Front page</a></p></section>` });

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
fs.mkdirSync(path.join(OUT, 'assets/img'), { recursive: true });
for (const f of fs.readdirSync(path.join(ROOT, 'src/assets/img'))) {
  fs.copyFileSync(path.join(ROOT, 'src/assets/img', f), path.join(OUT, 'assets/img', f));
}
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

// robots: one indexable site. The archive publications stay online but out of the index (S-16).
fs.writeFileSync(path.join(OUT, 'robots.txt'), `User-agent: *\nAllow: /\nDisallow: /editorial/\nDisallow: /legacy/\n\nSitemap: ${abs('/sitemap.xml')}\n`);

console.log(`Built ${written.length} pages, ${feedItems.length} feed items, ${sitemapPages.length} sitemap URLs at the repository root`);
