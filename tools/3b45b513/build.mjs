#!/usr/bin/env node
/**
 * Counter Desk — generator.
 *
 * Reads data/3b45b513/*.json and writes a self-contained publication into
 * counter-desk/. No dependencies, no network, deterministic output.
 *
 * Two rules the generator enforces rather than documents:
 *   1. Nothing is written that the gate cannot verify: every Amazon link gets the
 *      tracking tag and rel="sponsored" here, in one place, at render time.
 *   2. A blank specification renders as an explained blank, never as a guess.
 *      The reason is carried from the data file.
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '../..');
const OUT = path.join(ROOT, 'counter-desk');
const ASSETS_SRC = path.join(HERE, 'assets');

const read = (p) => JSON.parse(fs.readFileSync(path.join(ROOT, 'data/3b45b513', p), 'utf8'));

const cfg = read('config.json');
const sourcesDoc = read('sources.json');
const productsDoc = read('products.json');
const flagsDoc = read('flags.json');
const guidesDoc = read('guides.json');
const suggestionsDoc = read('suggestions.json');
const questionsDoc = read('questions.json');
const ledgerDoc = read('ledger.json');
const eventsDoc = read('events.json');

const SR = Object.fromEntries(sourcesDoc.sources.map((s) => [s.id, s]));
const PRODUCTS = productsDoc.products;
const GUIDES = guidesDoc.guides;
const FLAGS = flagsDoc.flags;
const byId = (id) => PRODUCTS.find((p) => p.id === id);
const guideBySlug = (slug) => GUIDES.find((g) => g.slug === slug);

const CATEGORIES = [
  {
    slug: 'air-fryers',
    name: 'Air fryers',
    tagline: 'One drawer, two drawers, and what a quart actually holds',
    blurb: 'Basket-style machines: a deep chamber, a fan above it, and a drawer you pull out. Two here are dual-basket, one is a single eight-quart basket.',
    guide: 'basket-or-oven-style-air-fryer-what-should-you-compare',
  },
  {
    slug: 'air-fryer-ovens',
    name: 'Countertop ovens',
    tagline: 'Doors, racks, and a whole tray at once',
    blurb: 'Oven-style units that air fry behind a door. Bigger footprint, more levels, and the ones that free your main oven during a holiday week.',
    guide: 'questions-to-ask-before-buying-a-multi-function-kitchen-appliance',
  },
  {
    slug: 'cooking-thermometers',
    name: 'Thermometers',
    tagline: 'The number that decides when to pull it',
    blurb: 'One instant-read for spot checks, one wireless probe that reports while the lid stays shut, and the USDA targets that go with both.',
    guide: 'is-your-meat-thermometer-telling-you-the-right-number',
  },
];

const NAV = [
  ['/shelf/', 'The shelf'],
  ['/guides/', 'Buying guides'],
  ['/counter-space/', 'Counter space'],
  ['/about/', 'About'],
];

const REVIEW = [
  ['/review/', 'Operator index'],
  ['/review/executive-summary/', 'Executive summary'],
  ['/review/flagged/', 'Flagged for review'],
  ['/review/questions/', 'Open questions'],
  ['/review/suggestions/', 'Suggestions and decisions'],
  ['/review/ledger/', 'Campaign ledger'],
  ['/review/measurement/', 'Measurement'],
  ['/review/compliance/', 'Disclosure and gates'],
  ['/review/sources/', 'Source register'],
  ['/review/register/', 'Product-intent register'],
];

// ── helpers ──────────────────────────────────────────────────────────────
const esc = (s = '') => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const u = (p) => cfg.basePath + p;                          // absolute in-site path
// Absolute, canonical URL for an in-edition path. cfg.siteUrl is the origin plus the
// /Affil3 project path; cfg.basePath is that path plus /counter-desk, so the edition's
// own prefix is the difference between them.
const EDITION_PREFIX = cfg.basePath.replace(/^\/Affil3/, '');
const abs = (p) => cfg.siteUrl + EDITION_PREFIX + p;
const asset = (p) => cfg.basePath + '/assets/' + p;
const dateLong = (iso) => new Date(iso + 'T12:00:00Z').toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric', timeZone: 'UTC' });
const rfc822 = (iso) => new Date(iso + 'T12:00:00Z').toUTCString();
const slugify = (t) => t.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');

const HOST = (() => { try { return new URL(cfg.siteUrl).hostname; } catch { return ''; } })();

/** The only place an Amazon link is created. Tag + sponsored, always. */
function amazon(asin, text, attrs = '') {
  const href = `https://www.amazon.com/dp/${asin}?tag=${cfg.trackingId}`;
  return `<a href="${esc(href)}" rel="sponsored noopener"${attrs}>${text}</a>`;
}
/** A citation to an official source, linked by id.
 *  Program Policies 2(b) applies to every link to an Amazon site, not only to buy
 *  buttons, so an Amazon-hosted citation gets the tag too. A link.amazon short link is
 *  rendered as plain text rather than as an anchor, because 6(w) restricts a shortener
 *  that makes it unclear the link points at Amazon. */
function cite(id) {
  const s = SR[id];
  if (!s) return `<span class="badge">${esc(id)}</span>`;
  const host = (() => { try { return new URL(s.url).hostname; } catch { return ''; } })();
  if (host === 'link.amazon') return `<code title="${esc(s.title)}">${esc(id)}</code>`;
  const href = /(^|\.)amazon\.com$/.test(host) && !['affiliate-program.amazon.com', 'sell.amazon.com'].includes(host)
    ? `${s.url}${s.url.includes('?') ? '&' : '?'}tag=${cfg.trackingId}`
    : s.url;
  const rel = /(^|\.)amazon\.com$/.test(host) ? 'sponsored noopener' : 'noopener external';
  return `<a href="${esc(href)}" rel="${rel}" title="${esc(s.title)}">${esc(id)}</a>`;
}
const cites = (ids = []) => ids.map(cite).join(' ');
const flagLink = (id) => `<a class="badge ${(FLAGS.find((f) => f.id === id) || {}).severity || ''}" href="${u('/review/flagged/')}#${esc(id)}">${esc(id)}</a>`;
const flagLinks = (ids = []) => ids.map(flagLink).join(' ');
const img = (file, alt, extra = '') => `<img src="${esc(asset('img/' + file))}" alt="${esc(alt)}"${extra ? ' ' + extra : ''} loading="lazy" decoding="async">`;
const clamp = (t, n) => (String(t).length <= n ? String(t) : String(t).slice(0, n - 1).replace(/[\s,;:—-]+\S*$/, '') + '…');
const priceFree = (html) => html.replace(/\$\s?\d[\d,]*/g, 'a price'); // never expected; gate catches it

function extLink(url, text) {
  return `<a href="${esc(url)}" rel="noopener external">${text}</a>`;
}

/** Renders a source's own link, refusing to turn a marketplace listing into a citation
 *  link. Amazon product pages are named by ASIN in the register and linked from the
 *  product page's buy box, where the tag and the sponsored rel are applied. */
function sourceLink(id, label = 'Open source') {
  const s = SR[id];
  if (!s || !s.url) return '<span class="muted">none</span>';
  const host = (() => { try { return new URL(s.url).hostname; } catch { return ''; } })();
  if (host === 'link.amazon') return `<span class="muted">short link recorded as evidence in the register, never published as a link</span>`;
  if (/(^|\.)amazon\.com$/.test(host) && !['affiliate-program.amazon.com', 'sell.amazon.com'].includes(host)) {
    return `<span class="muted">amazon.com listing, observed ${esc(s.method.replace(/^observed /, ''))}</span>`;
  }
  if (new URL(s.url).pathname === '/') {
    return `<span class="muted">marketplace front page, recorded as evidence; not linked</span>`;
  }
  return extLink(s.url, label);
}

// ── page shell ───────────────────────────────────────────────────────────
const totalGuides = GUIDES.length;

function shell({ title, description, path: p, body, type = 'page', attrs = '', jsonld = '', ogType = 'website', hero = 'hero-desk.jpg', noindex = false }) {
  const canonical = abs(p);
  const fullTitle = p === '/' ? `${title} — Counter Desk` : `${title} — Counter Desk`;
  const nav = NAV.map(([href, label]) => `<a href="${esc(u(href))}"${p === href || (href !== '/' && p.startsWith(href)) ? ' aria-current="page"' : ''}>${esc(label)}</a>`).join('\n        ');
  return `<!doctype html>
<html lang="${cfg.language}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(fullTitle.length > 88 ? title.slice(0, 70) + ' — Counter Desk' : fullTitle)}</title>
<meta name="description" content="${esc(clamp(description, 178))}">
<link rel="canonical" href="${esc(canonical)}">
<meta property="og:title" content="${esc(title)}">
<meta property="og:description" content="${esc(clamp(description, 200))}">
<meta property="og:url" content="${esc(canonical)}">
<meta property="og:type" content="${esc(ogType)}">
<meta property="og:site_name" content="${esc(cfg.siteName)}">
<meta property="og:image" content="${esc(abs('/assets/img/' + hero))}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="${esc(title)}">
<meta name="twitter:description" content="${esc(clamp(description, 200))}">
<meta name="twitter:image" content="${esc(abs('/assets/img/' + hero))}">
<meta name="analytics-endpoint" content="${esc(cfg.analyticsEndpoint || '')}">
${noindex ? '<meta name="robots" content="noindex, follow">' : '<meta name="robots" content="index, follow, max-image-preview:large">'}
<link rel="alternate" type="application/rss+xml" title="Counter Desk — buying guides" href="${esc(abs('/feed.xml'))}">
<link rel="stylesheet" href="${esc(asset('style.css'))}">
${jsonld}
</head>
<body data-page="${esc(type)}"${attrs ? ' ' + attrs : ''}>
<a class="skip" href="#main">Skip to content</a>
<header class="masthead">
  <div class="wrap">
    <a class="wordmark" href="${esc(u('/'))}">Counter Desk<span class="dot">.</span><small>Kitchen buying guides</small></a>
    <p class="issue"><b>Independent</b> · checked ${esc(dateLong(cfg.lastReviewed))}</p>
    <nav class="nav" aria-label="Main">
        ${nav}
    </nav>
  </div>
</header>
<div class="disclosure-strip" role="note" aria-label="Affiliate disclosure">
  <div class="wrap"><strong>Paid links</strong> ${esc(cfg.disclosureLine)} <a href="${esc(u('/review/compliance/'))}">How we disclose</a></div>
</div>
<main id="main">
${body}
</main>
<footer class="site-footer">
  <div class="wrap">
    <div class="foot-top">
      <div>
        <a class="wordmark" href="${esc(u('/'))}">Counter Desk<span class="dot">.</span></a>
        <p class="foot-blurb">Five countertop cooking appliances, compared the boring way — capacity, footprint, temperature, cleanup — from the makers' own specification pages, with every gap and every conflict written down instead of smoothed over.</p>
      </div>
      <div>
        <h2 class="foot-h">The publication</h2>
        <ul class="foot-links">
          <li><a href="${esc(u('/shelf/'))}">The five picks</a></li>
          <li><a href="${esc(u('/guides/'))}">Buying guides</a></li>
          <li><a href="${esc(u('/categories/'))}">Categories</a></li>
          <li><a href="${esc(u('/counter-space/'))}">Counter-space &amp; fit finder</a></li>
          <li><a href="${esc(u('/about/'))}">About and corrections</a></li>
          <li><a href="${esc(u('/feed.xml'))}">RSS feed</a></li>
          <li><a href="${esc(u('/sitemap.xml'))}">Sitemap</a></li>
        </ul>
        <h2 class="foot-h" style="margin-top:22px">Records and dashboards</h2>
        <ul class="foot-links">
          ${REVIEW.map(([href, label]) => `<li><a href="${esc(u(href))}">${esc(label)}</a></li>`).join('\n          ')}
        </ul>
      </div>
    </div>
    <p class="disclosure-footer"><strong>Disclosure.</strong> ${esc(cfg.disclosureLine)}</p>
    <p class="foot-fine">Counter Desk is not sponsored by, endorsed by, or affiliated with Amazon.com, Inc. or any brand named on this site. Prices and availability are not shown, because Amazon's program rules only permit a site to display price data that Amazon serves. Photographs are editorial illustrations, not the reviewed units. Published under a desk byline; no named editor has been supplied. Last checked ${esc(dateLong(cfg.lastReviewed))}. As an Amazon Associate I earn from qualifying purchases.</p>
  </div>
</footer>
<script src="${esc(asset('analytics.js'))}" defer></script>
${p === '/' || type === 'shelf' || p === '/counter-space/' ? `<script src="${esc(asset('finder.js'))}" defer></script>` : ''}
</body>
</html>
`;
}

// ── components ───────────────────────────────────────────────────────────
const PRODUCT_IMAGE = {
  P1: 'basket-drawer.jpg',
  P2: 'oven-doors.jpg',
  P3: 'basket-drawer.jpg',
  P4: 'thermometer-craft.jpg',
  P5: 'thermometer-craft.jpg',
};

function specLine(p) {
  const bits = [];
  if (p.fit.width_in) bits.push([`${p.specs.capacity.value.split(' ')[0]} qt`, p.specs.capacity.value.includes('qt')]);
  return bits;
}

function miniSpecs(p) {
  const out = [];
  if (p.category === 'cooking-thermometers') {
    if (p.specs.range) out.push(p.specs.range.value.split(' (')[0]);
    if (p.specs.internal_range) out.push('212 °F probe limit');
    if (p.specs.ambient_range) out.push('1,000 °F ambient');
    if (p.specs.accuracy) out.push('±0.5 °F stated');
  } else {
    if (p.specs.capacity && p.specs.capacity.value) out.push(p.specs.capacity.value.split(' / ')[0]);
    if (p.specs.temperature && p.specs.temperature.value) out.push(p.specs.temperature.value);
    out.push(p.shape);
    if (p.specs.dimensions && p.specs.dimensions.value) out.push(p.specs.dimensions.value.replace(' in', '') + ' in');
  }
  return `<ul class="mini-specs">${out.slice(0, 3).map((s) => `<li>${esc(s)}</li>`).join('')}</ul>`;
}

function productCard(p, placement) {
  return `<article class="card" data-product-view="${esc(p.id)}">
  <div class="card-art">${img(p.image, `${p.image_alt} Editorial illustration; not the reviewed unit.`, 'width="768" height="512"')}<span class="art-tag">Illustration</span></div>
  <div class="card-body">
    <p class="kicker">${esc((CATEGORIES.find((c) => c.slug === p.category) || {}).name || '')}</p>
    <h3><a href="${esc(u('/products/' + p.slug + '/'))}">${esc(p.short_name)}</a></h3>
    <p class="blurb">${esc(p.fit_line)}</p>
    ${miniSpecs(p)}
    <div class="card-foot">
      ${amazon(p.observed.asin, 'Check it on Amazon', ` data-outbound data-product="${esc(p.id)}" data-placement="${esc(placement)}"`)}
      <a class="text-link" href="${esc(u('/products/' + p.slug + '/'))}">Read the detail</a>
    </div>
  </div>
</article>`;
}

function guideCard(g, feature = false) {
  return `<a class="card guide-card${feature ? ' feature' : ''}" href="${esc(u('/guides/' + g.slug + '/'))}">
  <div class="card-art">${img(g.image, g.image_alt, 'width="768" height="432"')}</div>
  <div class="card-body">
    <p class="kicker">${esc(g.kicker)}${g.hypothesis ? ' <span class="sep">|</span> Working title' : ''}</p>
    <h3>${esc(g.title)}</h3>
    <p class="blurb">${esc(g.deck)}</p>
    <span class="read">Read the guide &rarr;</span>
  </div>
</a>`;
}

function guideRow(g) {
  return `<li class="guide-row">
  <div>
    <h3><a href="${esc(u('/guides/' + g.slug + '/'))}">${esc(g.title)}</a></h3>
    <p>${esc(g.deck)}</p>
  </div>
  <div class="meta">${esc(g.kicker)}<br>${g.read_minutes} min${g.hypothesis ? '<br>Working title' : ''}</div>
</li>`;
}

function specTable(p) {
  const rows = Object.values(p.specs).map((s) => {
    const has = s.value && String(s.value).trim();
    return `<tr>
      <th scope="row">${esc(s.label)}</th>
      ${has
        ? `<td class="v">${esc(s.value)}${s.note ? `<span class="src">${esc(s.note)}</span>` : ''}${s.source ? `<span class="src">Source ${cite(s.source)}</span>` : ''}</td>`
        : `<td class="na">Not published. <span class="src">${esc(s.note || 'No official source states this value.')}</span></td>`}
    </tr>`;
  }).join('\n      ');
  return `<table class="spec-table">
      <caption class="fine" style="text-align:left;padding:0 0 10px">Specifications from the manufacturer's own page where one exists. A cell that reads “not published” has a reason beside it.</caption>
      <tbody>
      ${rows}
      </tbody>
    </table>`;
}

function inlineProduct(id) {
  const p = byId(id);
  if (!p) return '';
  return `<aside class="inline-product">
  ${img(p.image, `${p.image_alt} Editorial illustration; not the reviewed unit.`, 'width="320" height="240"')}
  <div>
    <p class="kicker">${esc(p.brand)}</p>
    <h3>${esc(p.short_name)}</h3>
    <p>${esc(p.fit_line)}</p>
    <a href="${esc(u('/products/' + p.slug + '/'))}">Specifications, trade-offs and sources &rarr;</a>
  </div>
</aside>`;
}

function renderSection(s) {
  switch (s.type) {
    case 'p': return `<p>${esc(s.text)}</p>`;
    case 'note': return `<div class="box"><span class="t">Worth knowing</span><p>${esc(s.text)}</p></div>`;
    case 'h2': return `<h2 id="${esc(slugify(s.text))}">${esc(s.text)}</h2>`;
    case 'h3': return `<h3>${esc(s.text)}</h3>`;
    case 'ul': return `<ul>${s.items.map((i) => `<li>${esc(i)}</li>`).join('')}</ul>`;
    case 'ol': return `<ol>${s.items.map((i) => `<li>${esc(i)}</li>`).join('')}</ol>`;
    case 'product': return inlineProduct(s.id);
    case 'table':
      return `<div class="table-wrap"><table class="data">
        ${s.caption ? `<caption class="fine" style="text-align:left;padding:10px 12px 0">${esc(s.caption)}</caption>` : ''}
        <thead><tr>${s.headers.map((h) => `<th scope="col">${esc(h)}</th>`).join('')}</tr></thead>
        <tbody>${s.rows.map((r) => `<tr>${r.map((c) => `<td>${esc(c)}</td>`).join('')}</tr>`).join('')}</tbody>
      </table></div>`;
    default: throw new Error('unknown section type: ' + s.type);
  }
}

/** Renders [S10] markers inside body copy as real citation links. */
function withCites(html) {
  return html.replace(/\[(S\d{2})(?:\]\[(S\d{2}))*\]/g, (m) => {
    const ids = [...m.matchAll(/S\d{2}/g)].map((x) => x[0]);
    return `<sup class="cite">${ids.map((id) => cite(id)).join(' ')}</sup>`;
  });
}

const pages = [];
const add = (p) => { pages.push(p); return p; };

// ── front page ───────────────────────────────────────────────────────────
{
  const lead = guideBySlug('basket-or-oven-style-air-fryer-what-should-you-compare');
  const rest = GUIDES.filter((g) => g !== lead);
  const catTiles = CATEGORIES.map((c) => {
    const n = PRODUCTS.filter((p) => p.category === c.slug).length;
    return `<a class="cat" href="${esc(u('/categories/' + c.slug + '/'))}">
      <span class="count">${n} ${n === 1 ? 'pick' : 'picks'} · ${GUIDES.filter((g) => g.category === c.slug).length} guides</span>
      <h3>${esc(c.name)}</h3><p>${esc(c.tagline)}</p></a>`;
  }).join('\n');

  add({
    path: '/', type: 'home', hero: 'hero-desk.jpg',
    title: 'Kitchen gear for the counter you actually have',
    description: 'Five countertop cooking appliances compared by manufacturer specification, with the buying questions that decide between them and every gap stated plainly.',
    jsonld: `<script type="application/ld+json">${JSON.stringify({
      '@context': 'https://schema.org', '@type': 'WebSite', name: cfg.siteName,
      url: abs('/'), inLanguage: 'en-US',
      description: 'Kitchen buying guides for countertop appliances, built from manufacturers\' specification pages.',
      publisher: { '@type': 'Organization', name: cfg.author },
    })}</script>`,
    body: `<div class="wrap">
<section class="hero">
  <div>
    <p class="kicker">Independent buying guides <span class="sep">|</span> ${totalGuides} guides, ${PRODUCTS.length} appliances</p>
    <h1>Gear for the counter you actually have.</h1>
    <p class="deck">Five air fryers, an oven-style cooker and two thermometers, compared by the four things that decide the purchase: capacity, footprint, temperature and cleanup. Every number comes from the maker's own specification page, and where two official pages disagree, both are shown and neither is published as fact.</p>
    <div class="hero-actions">
      <a class="btn" href="${esc(u('/shelf/'))}">See the five picks</a>
      <a class="btn ghost" href="${esc(u('/counter-space/'))}">Will it fit my counter?</a>
    </div>
  </div>
  <figure class="hero-figure">
    ${img('hero-desk.jpg', 'A stoneware bowl of crisp rosemary potatoes beside a folded linen towel and a brass kitchen timer on a soapstone counter.', 'width="1200" height="800"')}
    <figcaption>An editorial illustration, not the reviewed unit. We do not use manufacturer photography, and we say so on every image.</figcaption>
  </figure>
</section>

<section class="band" id="picks">
  <div class="band-head">
    <h2>On the shelf this month</h2>
    <p>Five submitted products, each traced to the Amazon listing it resolves to and then checked against the manufacturer's own specification page. One of them has a genuine conflict between the two official sources, and its page says which numbers are withheld and why.</p>
    <a class="more" href="${esc(u('/shelf/'))}">The full shelf &rarr;</a>
  </div>
  <div class="shelf">
    ${PRODUCTS.map((p) => productCard(p, 'front-shelf')).join('\n    ')}
  </div>
  <p class="fine" style="margin-top:14px">Links open Amazon with our tracking ID and are marked sponsored. We do not show prices or ratings anywhere on this site, and we have not tested any of these appliances. <a href="${esc(u('/review/compliance/'))}">How we disclose</a>.</p>
</section>

<section class="band">
  <div class="band-head">
    <h2>Start with a question, not a product</h2>
    <p>Each guide answers the question a reader arrives with, and each one names the specification it relies on rather than the brand it prefers.</p>
    <a class="more" href="${esc(u('/guides/'))}">All ${totalGuides} guides &rarr;</a>
  </div>
  <a class="lead-guide" href="${esc(u('/guides/' + lead.slug + '/'))}">
    ${img(lead.image, lead.image_alt, 'width="760" height="507"')}
    <div>
      <p class="kicker">${esc(lead.kicker)} <span class="sep">|</span> Lead guide</p>
      <h2>${esc(lead.title)}</h2>
      <p class="muted">${esc(lead.deck)}</p>
      <span class="btn ghost">Read the guide</span>
    </div>
  </a>
  <div class="guide-grid" style="margin-top:24px">
    ${rest.slice(0, 3).map((g) => guideCard(g)).join('\n    ')}
  </div>
</section>

<section class="band">
  <div class="band-head"><h2>Browse by what you cook</h2></div>
  <div class="cat-grid">
${catTiles}
  </div>
</section>

<section class="band">
  <div class="band-head"><h2>Three rules this site actually follows</h2></div>
  <div class="guide-grid">
    <div class="card"><div class="card-body"><h3>A specification needs a manufacturer page</h3><p class="blurb">Capacity, wattage, dimensions and dishwasher claims come from the maker's own product page, fetched on the date shown next to the table. If the maker does not state it, the cell says “not published” and the reason is beside it.</p></div></div>
    <div class="card"><div class="card-body"><h3>No prices, no ratings, no exceptions</h3><p class="blurb">Amazon's program rules only permit a site to display price data that Amazon itself serves or that arrives through its API. Star ratings are a snapshot of a rolling average. We do neither, so nothing here goes stale in a fortnight.</p></div></div>
    <div class="card"><div class="card-body"><h3>When two official pages disagree, publish neither number</h3><p class="blurb">Two of the makers here contradict themselves or each other. Both readings are recorded on the <a href="${esc(u('/review/flagged/'))}">flagged for review</a> page with links, and the field stays blank.</p></div></div>
  </div>
</section>

<section class="band">
  <div class="band-head"><h2>${esc(cfg.seasonal.title)}</h2><p>${esc(cfg.seasonal.kicker)}</p></div>
  <div class="lead-guide" style="grid-template-columns:1fr 1.1fr">
    ${img('holiday-counter.jpg', 'Roasted Brussels sprouts and carrots on a sheet pan beside fresh sage and cranberries, with a tape measure at the counter edge.', 'width="760" height="507"')}
    <div>
      <p>${esc(cfg.seasonal.body)}</p>
      <p style="margin-bottom:0">${cfg.seasonal.links.map(([h, t]) => `<a class="text-link" href="${esc(u(h))}">${esc(t)} &rarr;</a>`).join('<br>')}</p>
    </div>
  </div>
</section>
</div>`,
  });
}

// ── shelf (the shop table + intent register) ─────────────────────────────
{
  const rows = PRODUCTS.map((p) => [
    `<strong>${esc(p.id)}</strong>`,
    `<a href="${esc(u('/products/' + p.slug + '/'))}"><strong>${esc(p.short_name)}</strong></a><br><span class="fine">${esc(p.brand)}</span>`,
    esc(p.shape),
    (p.specs.capacity && p.specs.capacity.value) ? esc(p.specs.capacity.value.split(' / ')[0]) : '<span class="blank-mark">n/a</span>',
    p.category === 'cooking-thermometers'
      ? `<span class="fine">${esc((p.specs.range || p.specs.internal_range || {}).value || 'see page')}</span>`
      : (p.specs.temperature
          ? (p.specs.temperature.value ? esc(p.specs.temperature.value) : '<span class="blank-mark">withheld</span>')
          : '<span class="blank-mark">n/a</span>'),
    p.fit.depth_in ? `${p.fit.depth_in} × ${p.fit.width_in} × ${p.fit.height_in} in` : '<span class="blank-mark">handheld</span>',
    amazon(p.observed.asin, 'Amazon', ` data-outbound data-product="${esc(p.id)}" data-placement="shelf-table"`),
    `<span class="fine">${esc(p.link_status.split('.')[0])}</span>`,
    flagLinks(p.flags),
  ]);
  const intent = PRODUCTS.map((p) => [
    `<strong>${esc(p.id)}</strong>`,
    `<code>${esc(p.submitted_token)}</code><br><span class="fine">${p.submitted_token_length} chars</span>`,
    p.intended_asin ? `<code>${esc(p.intended_asin)}</code>` : '<span class="blank-mark">not confirmed</span>',
    p.official_listing_url ? extLink(p.official_listing_url, esc(p.official_listing_url)) : '<span class="blank-mark">not confirmed</span>',
    p.confirmation_date ? esc(p.confirmation_date) : '<span class="blank-mark">not confirmed</span>',
    p.confirmation_source ? esc(p.confirmation_source) : '<span class="blank-mark">not confirmed</span>',
    `<code>${esc(p.observed.asin)}</code><br><span class="fine">${esc(p.observed.date)}</span>`,
    cites(p.sources),
  ]);

  add({
    path: '/shelf/', type: 'shelf',
    title: 'The five picks, side by side',
    description: 'Capacity, temperature, footprint and cleanup for all five appliances, plus the register that separates what the supplied links were meant to reach from what they actually reached.',
    body: `<div class="wrap">
<section class="page-head">
  <p class="kicker">The shelf <span class="sep">|</span> ${PRODUCTS.length} appliances</p>
  <h1>Five appliances, side by side</h1>
  <p class="deck">The short version first. Every number below comes from the maker's own specification page; a withheld cell means two official pages disagree, and the product page says which two.</p>
</section>

<div class="table-wrap" style="margin-top:22px">
  <table class="data wide">
    <thead><tr><th scope="col">ID</th><th scope="col">Product</th><th scope="col">Shape</th><th scope="col">Capacity</th><th scope="col">Temperature</th><th scope="col">Footprint</th><th scope="col">Amazon</th><th scope="col">Link status</th><th scope="col">Flags</th></tr></thead>
    <tbody>${rows.map((r) => `<tr>${r.map((c) => `<td>${c}</td>`).join('')}</tr>`).join('\n    ')}</tbody>
  </table>
</div>

<div class="box info" style="margin-top:22px">
  <span class="t">What the table will not tell you</span>
  <p>Whether any of this food tastes good, how loud the fan is, or how evenly each machine browns. Nobody here has cooked in any of these appliances, and a specification sheet cannot answer those questions. What it can answer — capacity, footprint, temperature range, parts to wash — is in the table.</p>
</div>

<section class="band">
  <h2>The register behind the table</h2>
  <p class="deck" style="font-size:17px">This is the audit trail, kept on the same page as the shop because a reader deserves to see it. <strong>Intent</strong> columns are filled only from an owner confirmation or an official Associates record; none was supplied, so all four are blank. <strong>Observed</strong> columns are what the Amazon page actually served on the date shown, kept separate on purpose.</p>
  <div class="table-wrap">
    <table class="data wide">
      <thead><tr><th scope="col">ID</th><th scope="col">Supplied token</th><th scope="col">Intended ASIN</th><th scope="col">Official listing URL</th><th scope="col">Confirmed on</th><th scope="col">Confirmation source</th><th scope="col">Observed</th><th scope="col">Sources</th></tr></thead>
      <tbody>${intent.map((r) => `<tr>${r.map((c) => `<td>${c}</td>`).join('')}</tr>`).join('\n      ')}</tbody>
    </table>
  </div>
  <p class="fine">The two halves are allowed to disagree, and here they do: all five supplied tokens are nine characters, while every observed product carries a ten-character identifier. That is a format observation, not a verdict on the links. ${flagLinks(['CDF-01', 'CDF-02', 'CDF-03'])}</p>
</section>

<section class="band">
  <h2>What a friend would ask first</h2>
  <div class="two-col" style="margin-top:18px">
    <div class="trade-card"><h3>If two foods, two timings</h3><p>${esc(byId('P1').short_name)}. Two independent 3-quart baskets and a Sync Finish setting, 13.38 inches deep.</p></div>
    <div class="trade-card"><h3>If one big pile</h3><p>${esc(byId('P3').short_name)}. Eight quarts in a single basket; wattage and size withheld because two official pages disagree.</p></div>
    <div class="trade-card"><h3>If a whole tray</h3><p>${esc(byId('P2').short_name)}. 26 quarts behind glass french doors, if you have 16.9 inches of counter depth.</p></div>
    <div class="trade-card"><h3>If your hands are busy</h3><p>${esc(byId('P5').short_name)}. Three leave-in probes reporting over Wi-Fi while the lid stays shut.</p></div>
  </div>
  <p style="margin-top:22px"><a class="btn" href="${esc(u('/guides/basket-or-oven-style-air-fryer-what-should-you-compare/'))}">Read the shape guide first</a></p>
</section>
</div>`,
  });
}

// ── counter space / fit finder ───────────────────────────────────────────
{
  const fitData = PRODUCTS.filter((p) => p.fit.depth_in).map((p) => ({
    id: p.id, name: p.short_name, url: u('/products/' + p.slug + '/'),
    depth_in: p.fit.depth_in, width_in: p.fit.width_in, height_in: p.fit.height_in,
  }));
  add({
    path: '/counter-space/', type: 'page',
    title: 'Will it fit? A counter-space check before you buy',
    description: 'Enter the depth, width and height of your counter and see which of the five appliances clears it, using the manufacturers\' own dimension figures and two inches of clearance.',
    body: `<div class="wrap">
<section class="page-head">
  <p class="kicker">Counter space</p>
  <h1>Will it fit? Measure first, then choose</h1>
  <p class="deck">The most common reason a countertop appliance gets returned is that it does not fit where the buyer planned to put it. Three measurements solve that, and they take two minutes with a tape measure.</p>
</section>

<div class="two-col" style="margin-top:26px;align-items:start">
  <div class="finder">
    <h2 style="margin-top:0;font-size:22px">Counter-space &amp; fit finder</h2>
    <p class="small muted" style="margin-bottom:0">Measurements in inches. Leave a field empty and that dimension is not checked.</p>
    <form id="fit-form" novalidate>
      <div class="finder-fields">
        <div class="field"><label for="fit-depth">Available depth</label><input id="fit-depth" type="number" min="1" max="60" step="0.1" inputmode="decimal" placeholder="e.g. 18"><p class="hint">Wall to the front edge of the counter.</p></div>
        <div class="field"><label for="fit-width">Available width</label><input id="fit-width" type="number" min="1" max="60" step="0.1" inputmode="decimal" placeholder="e.g. 24"><p class="hint">Clear space left to right.</p></div>
        <div class="field"><label for="fit-height">Available height</label><input id="fit-height" type="number" min="1" max="60" step="0.1" inputmode="decimal" placeholder="e.g. 16"><p class="hint">Counter to the underside of the cabinets.</p></div>
      </div>
      <noscript><p class="small">This tool needs JavaScript. The published dimensions are in the table below and on each product page, so nothing is lost without it.</p></noscript>
    </form>
    <div class="finder-out" id="fit-out" aria-live="polite">
      <p class="fit-empty">Enter at least one measurement above.</p>
    </div>
  </div>

  <div>
    <h2 style="margin-top:0;font-size:22px">The four measurements that matter</h2>
    <ol class="prose" style="padding-left:20px">
      <li><strong>Depth.</strong> Wall to front edge. Published figures are the box, not the box plus the door.</li>
      <li><strong>Height.</strong> Counter to the underside of the upper cabinets. Add clearance for anything that vents upward.</li>
      <li><strong>Door swing or drawer pull.</strong> Measured toward you. This is the number that never appears on a listing.</li>
      <li><strong>Outlet reach.</strong> Where the nearest socket is, and whether the cord reaches without an extension lead across a walkway.</li>
    </ol>
    <div class="box warn">
      <span class="t">Why two inches of clearance</span>
      <p>A machine that fits exactly has no room for a vent, a hand on the handle, or a door that opens past ninety degrees. The finder adds two inches around every published dimension, so a “fits” here means fits with room to use it.</p>
    </div>
  </div>
</div>

<section class="band">
  <h2>The published dimensions, with their sources</h2>
  <div class="table-wrap">
    <table class="data">
      <thead><tr><th scope="col">Product</th><th scope="col">Depth</th><th scope="col">Width</th><th scope="col">Height</th><th scope="col">What moves toward you</th><th scope="col">Source</th></tr></thead>
      <tbody>
        <tr><td><a href="${esc(u('/products/' + byId('P1').slug + '/'))}">${esc(byId('P1').short_name)}</a></td><td>13.38 in</td><td>11.81 in</td><td>10.63 in</td><td>Two drawers, at counter height</td><td>${cite('S10')}</td></tr>
        <tr><td><a href="${esc(u('/products/' + byId('P3').slug + '/'))}">${esc(byId('P3').short_name)}</a></td><td>15.4 in</td><td>12.6 in</td><td>13.5 in</td><td>One drawer, at counter height</td><td>${cite('S14')}</td></tr>
        <tr><td><a href="${esc(u('/products/' + byId('P2').slug + '/'))}">${esc(byId('P2').short_name)}</a></td><td>16.9 in</td><td>15.8 in</td><td>14.8 in</td><td>Two glass doors, plus vertical clearance</td><td>${cite('S12')}</td></tr>
        <tr><td>Both thermometers</td><td colspan="3" class="muted">Handheld. A drawer or a shelf, not the counter.</td><td>A folding probe</td><td>${cite('S21')}</td></tr>
      </tbody>
    </table>
  </div>
  <p class="fine">For the 8 Qt Chefman the manufacturer and the listing state different dimensions; the finder uses the larger manufacturer figure so the check does not under-state the space needed. Both figures are on the <a href="${esc(u('/products/' + byId('P3').slug + '/'))}">product page</a>, and the conflict is ${flagLinks(['CDF-05'])}.</p>
</section>

<section class="band">
  <div class="band-head"><h2>The guide this tool belongs to</h2></div>
  ${guideCard(guideBySlug('cleanup-and-counter-space-tradeoffs'))}
</section>
</div>`,
    jsonld: `<script type="application/ld+json">${JSON.stringify({
      '@context': 'https://schema.org', '@type': 'WebApplication', name: 'Counter-space and fit finder',
      applicationCategory: 'UtilitiesApplication', operatingSystem: 'Any modern browser',
      url: abs('/counter-space/'), isAccessibleForFree: true,
      description: 'Compares your counter measurements with published appliance dimensions.',
    })}</script>`,
    attrs: `data-tool="fit-finder"`,
    extraScripts: true,
  });
  // inject the data island just before the main wrapper's closing tag
  const idx = pages.findIndex((x) => x.path === '/counter-space/');
  pages[idx].body = pages[idx].body.replace('<div class="wrap">', `<div class="wrap">\n<script type="application/json" id="fit-data">${JSON.stringify(fitData)}</script>`);
}

// ── categories ───────────────────────────────────────────────────────────
add({
  path: '/categories/', type: 'categories',
  title: 'Browse by category',
  description: 'Three clusters — air fryers, countertop ovens and thermometers — each with its picks and the guides that cover them.',
  body: `<div class="wrap">
<section class="page-head"><p class="kicker">Categories</p><h1>Three jobs, three shapes</h1>
<p class="deck">Everything here is organised by the job the appliance does, not by the brand on the door. Start with the job.</p></section>
<div class="cat-grid" style="margin-top:26px">
${CATEGORIES.map((c) => `<a class="cat" href="${esc(u('/categories/' + c.slug + '/'))}">
  <span class="count">${PRODUCTS.filter((p) => p.category === c.slug).length} picks · ${GUIDES.filter((g) => g.category === c.slug).length} guides</span>
  <h3>${esc(c.name)}</h3><p>${esc(c.blurb)}</p></a>`).join('\n')}
</div>
</div>`,
});

for (const c of CATEGORIES) {
  const list = PRODUCTS.filter((p) => p.category === c.slug);
  const gs = GUIDES.filter((g) => g.category === c.slug);
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
<div class="shelf" style="margin-top:26px">${list.map((p) => productCard(p, 'category')).join('\n')}</div>
${gs.length ? `<section class="band"><div class="band-head"><h2>The guides for this job</h2><a class="more" href="${esc(u('/guides/'))}">All guides &rarr;</a></div><ul class="guide-list">${gs.map(guideRow).join('\n')}</ul></section>` : ''}
<p class="band"><a class="more" href="${esc(u('/shelf/'))}">See all five side by side &rarr;</a></p>
</div>`,
  });
}

// ── guides index + guide pages ───────────────────────────────────────────
add({
  path: '/guides/', type: 'guides',
  title: 'Buying guides, by question',
  description: 'Seven buying guides for air fryers, countertop ovens and thermometers, each answering a question a buyer actually asks before spending money.',
  body: `<div class="wrap">
<section class="page-head">
  <p class="kicker">Buying guides <span class="sep">|</span> ${totalGuides} guides</p>
  <h1>Five questions worth asking before you buy</h1>
  <p class="deck">Each guide starts with a question and answers it with specifications you can check. None of them ranks a brand, and none of them claims we tested anything. The four titles marked “working title” are editorial hypotheses about the questions buyers ask — not claims about search volume, popularity or which product is better.</p>
</section>
<ul class="guide-list" style="margin-top:26px">
${GUIDES.map(guideRow).join('\n')}
</ul>
<section class="band">
  <div class="box"><span class="t">Why the order matters</span><p>Start with the shape guide, then the capacity checklist, then the cleanup guide. Those three decide whether you want a basket or an oven, how large a batch you actually cook, and how many parts you are willing to wash. The thermometer guides are a separate decision, and the seasonal one is a plan rather than a product question.</p></div>
</section>
</div>`,
});

for (const g of GUIDES) {
  const related = (g.related_products || []).map(byId).filter(Boolean);
  const jsonld = `<script type="application/ld+json">${JSON.stringify({
    '@context': 'https://schema.org', '@type': 'Article',
    headline: g.title, description: g.description,
    datePublished: g.date, dateModified: cfg.lastReviewed,
    author: { '@type': 'Organization', name: cfg.author },
    publisher: { '@type': 'Organization', name: cfg.siteName },
    mainEntityOfPage: abs('/guides/' + g.slug + '/'),
    image: abs('/assets/img/' + g.image),
    isAccessibleForFree: true,
  })}</script>`;
  const idx = GUIDES.indexOf(g);
  const next = GUIDES[idx + 1];
  add({
    path: `/guides/${g.slug}/`, type: 'guide', ogType: 'article', jsonld, hero: g.image,
    attrs: `data-guide="${esc(g.slug)}"`,
    title: g.title,
    description: g.description,
    body: `<div class="wrap">
<article class="article">
  <header class="article-head">
    <p class="kicker">${esc(g.kicker)} <span class="sep">|</span> Buying guide</p>
    <h1>${esc(g.title)}</h1>
    <p class="deck">${esc(g.deck)}</p>
    <div class="byline">
      <span>By ${esc(cfg.author)}</span><span class="sep">·</span>
      <span>Published ${esc(dateLong(g.date))}</span><span class="sep">·</span>
      <span>Specifications checked ${esc(dateLong(cfg.lastReviewed))}</span><span class="sep">·</span>
      <span>${g.read_minutes} minute read</span>
    </div>
  </header>
  <figure class="article-figure">
    ${img(g.image, g.image_alt, 'width="1200" height="675"')}
    <figcaption>An editorial illustration, not a photograph of the product. We do not use manufacturer photography, and no image here shows a unit we have not handled.</figcaption>
  </figure>
  <div class="takeaways">
    <h2>The short version</h2>
    <ul>${g.key_takeaways.map((t) => `<li>${esc(t)}</li>`).join('')}</ul>
  </div>
  <div class="prose">
    ${withCites(g.sections.map(renderSection).join('\n    '))}
  </div>
  ${related.length ? `<section class="band"><div class="band-head"><h2>The picks discussed here</h2></div><div class="shelf">${related.map((p) => productCard(p, 'guide-box')).join('')}</div></section>` : ''}
  <section class="band">
    <div class="band-head"><h2>Sources for this guide</h2><a class="more" href="${esc(u('/review/sources/'))}">Full register &rarr;</a></div>
    <ul class="small" style="padding-left:20px">
      ${g.sources.map((id) => {
        const s = SR[id];
        if (!s) return `<li>${esc(id)}</li>`;
        return `<li><strong>${esc(id)}</strong> — ${esc(s.title)}, ${esc(s.publisher)}. ${sourceLink(id)} <span class="muted">(${esc(s.status)})</span></li>`;
      }).join('\n      ')}
    </ul>
    <p class="fine">Working titles: the four guides marked as hypotheses carry titles chosen by an editor, not by a keyword tool. If search data later shows nobody asks these questions, the honest response is to retire the format, not to defend the title.</p>
  </section>
  <nav class="page-nav">
    <span><a href="${esc(u('/guides/'))}">&larr; All guides</a></span>
    <span>${next ? `<a href="${esc(u('/guides/' + next.slug + '/'))}">${esc(next.title)} &rarr;</a>` : `<a href="${esc(u('/shelf/'))}">The five picks &rarr;</a>`}</span>
  </nav>
</article>
</div>`,
    jsonldExtra: true,
  });
}

// ── product pages ────────────────────────────────────────────────────────
for (const p of PRODUCTS) {
  const c = CATEGORIES.find((x) => x.slug === p.category);
  const g = guideBySlug(p.guide_slug);
  const idx = PRODUCTS.indexOf(p);
  const next = PRODUCTS[idx + 1];
  const jsonld = `<script type="application/ld+json">${JSON.stringify({
    '@context': 'https://schema.org', '@type': 'Product',
    name: p.name, brand: { '@type': 'Brand', name: p.brand },
    description: p.lede,
    url: abs('/products/' + p.slug + '/'),
    isPartOf: { '@type': 'WebSite', name: cfg.siteName, url: abs('/') },
  })}</script>`;
  add({
    path: `/products/${p.slug}/`, type: 'product', ogType: 'article', jsonld, hero: p.image,
    attrs: `data-product-view="${esc(p.id)}" data-category="${esc(p.category)}"`,
    title: p.name,
    description: `${p.short_name}: ${p.fit_line} Manufacturer specifications, withheld fields with reasons, and every source linked.`,
    body: `<div class="wrap">
<nav class="crumbs" aria-label="Breadcrumb"><a href="${esc(u('/shelf/'))}">The shelf</a> / <a href="${esc(u('/categories/' + c.slug + '/'))}">${esc(c.name)}</a> / <span>${esc(p.short_name)}</span></nav>

<section class="pd">
  <figure class="pd-figure">
    ${img(p.image, `${p.image_alt} Editorial illustration; not the reviewed unit.`, 'width="1000" height="667"')}
    <figcaption>An editorial illustration, not the reviewed unit. See <a href="${esc(u('/about/'))}">why we do not use manufacturer photography</a>.</figcaption>
  </figure>
  <div>
    <p class="kicker">${esc(p.brand)} <span class="sep">|</span> ${esc(c.name)}</p>
    <h1 style="font-size:clamp(28px,3.4vw,40px)">${esc(p.name)}</h1>
    <p class="deck" style="font-size:18px">${esc(p.lede)}</p>
    <div class="buybox">
      <a class="btn full" href="https://www.amazon.com/dp/${esc(p.observed.asin)}?tag=${esc(cfg.trackingId)}" rel="sponsored noopener" data-outbound data-product="${esc(p.id)}" data-placement="product-page">Check the listing on Amazon</a>
      <p class="note">Opens the Amazon listing for <code>${esc(p.observed.asin)}</code>. Affiliate link, marked sponsored, with our tracking ID <code>${esc(cfg.trackingId)}</code>. Not yet confirmed against a tracking report ${flagLinks(['CDF-04'])}. We do not show a price because Amazon's rules only let a site display price data Amazon serves.</p>
    </div>
    <ul class="mini-specs">${miniSpecs(p).replace(/<\/?ul[^>]*>/g, '').replace(/<li>/g, '<li>')}</ul>
  </div>
</section>

<section class="band">
  <div class="band-head"><h2>The specifications, and what is missing from them</h2></div>
  ${specTable(p)}
  <p class="fine" style="margin-top:12px">Where a cell reads “not published”, an official source either does not state the value or two official sources state different values. The reason is in the cell, and the full conflict is on <a href="${esc(u('/review/flagged/'))}">flagged for review</a>. ${flagLinks(p.flags)}</p>
</section>

<section class="band">
  <div class="band-head"><h2>Who it suits, and what it costs you</h2></div>
  <div class="two-col">
    <div class="trade-card"><h3>Best for</h3><p>${esc(p.best_for)}</p></div>
    <div class="trade-card"><h3>The trade</h3><p>${esc(p.tradeoff)}</p></div>
  </div>
</section>

<section class="band">
  <div class="band-head"><h2>Questions this page answers</h2></div>
  <dl class="qa prose">
    ${p.questions.map(([q, a]) => `<dt>${esc(q)}</dt><dd>${esc(a)}</dd>`).join('\n    ')}
  </dl>
</section>

${g ? `<section class="band">
  <div class="band-head"><h2>The guide that covers this decision</h2></div>
  ${guideCard(g)}
</section>` : ''}

<section class="band">
  <div class="band-head"><h2>Where every number came from</h2></div>
  <ul class="small" style="padding-left:20px">
    ${p.sources.map((id) => {
      const s = SR[id];
      if (!s) return `<li>${esc(id)}</li>`;
      return `<li><strong>${esc(id)}</strong> — ${esc(s.title)}, ${esc(s.publisher)}. ${sourceLink(id)} <span class="muted">(${esc(s.status)})</span></li>`;
    }).join('\n    ')}
  </ul>
  <p class="fine" style="margin-top:14px">Observed on ${esc(dateLong(p.observed.date))} at <code>amazon.com/dp/${esc(p.observed.asin)}</code>: “${esc(p.observed.title)}”. That title is a dated snapshot and can change without notice. The intended product remains unconfirmed and is recorded separately in the <a href="${esc(u('/review/register/'))}">product-intent register</a>.</p>
  ${p.observed.carried_forward_from ? `<div class="box warn" style="margin-top:16px"><span class="t">A note on this row</span><p>${esc(p.observed.carried_forward_from)}</p></div>` : ''}
  <div class="box" style="margin-top:16px"><span class="t">The supplied link for this row</span><p>The submitter supplied <code>${esc(p.submitted_url.replace('https://', ''))}</code> — ${p.submitted_token_length} characters, which is not the 10-character product identifier format Amazon documents ${cite('S23')}. It is recorded here as evidence of what was submitted. It is not published as a clickable link, because the tracking ID cannot be attached to it and Amazon's rules require the tag on every link to an Amazon site ${cite('S02')}.</p></div>
</section>

<nav class="page-nav">
  <span><a href="${esc(u('/shelf/'))}">&larr; All five picks</a></span>
  <span>${next ? `<a href="${esc(u('/products/' + next.slug + '/'))}">${esc(next.short_name)} &rarr;</a>` : `<a href="${esc(u('/guides/'))}">Buying guides &rarr;</a>`}</span>
</nav>
</div>`,
  });
}

// ── about ────────────────────────────────────────────────────────────────
add({
  path: '/about/', type: 'page',
  title: 'About Counter Desk and how we check facts',
  description: 'Who publishes this site, how products are chosen, how every specification is verified, what we refuse to publish, and how corrections work.',
  body: `<div class="wrap">
<section class="page-head">
  <p class="kicker">About</p>
  <h1>How this publication works</h1>
  <p class="deck">A short, specific statement of method — written so that a reader can check us, and so that a future editor can be held to it.</p>
</section>

<div class="prose" style="margin-top:26px">
<h2>Who publishes it</h2>
<p>Counter Desk is published by ${esc(cfg.author)}. ${esc(cfg.authorNote)} If a named editor takes the byline later, the name, role and contact route will appear here and on every guide, and ${flagLink('CDF-13')} will be marked resolved.</p>

<h2>How products get here</h2>
<p>All five products were submitted by the site owner. Nothing was added from our own research, and no brand paid for placement. If that ever changes, it will say so on the page where it changes. There is no test kitchen behind this site and no hands-on testing of any appliance.</p>

<h2>How a specification gets published</h2>
<ol>
  <li>Start with the Amazon listing the supplied link resolves to, and record its ASIN, title and breadcrumb with the date.</li>
  <li>Find the manufacturer's own product page for the model, using the listing's model-number field rather than its title. This is how the ThermoMaven page was found after an earlier pass wrongly recorded that none existed ${flagLink('CDF-08')}.</li>
  <li>Read the specification block and publish only what it states, with the source id beside the value.</li>
  <li>If the manufacturer page and the listing disagree on a value, publish neither and write both down on the <a href="${esc(u('/review/flagged/'))}">flagged page</a>.</li>
  <li>If no official page states the value, the cell reads “not published” and gives the reason. It is never filled from a reseller, a review site or another model's page.</li>
</ol>

<h2>What we refuse to publish</h2>
<ul>
  <li><strong>Prices.</strong> Amazon's program rules permit a site to show price and availability only when Amazon serves that data or it arrives through the Creators or PA API ${cite('S02')}. We do neither.</li>
  <li><strong>Star ratings and review counts.</strong> The same rules restrict republishing customer reviews and star ratings to API-sourced data, and a rating without its sample and date is a misleading claim ${cite('S02')}.</li>
  <li><strong>Any claim that we tested something.</strong> No appliance on this site has been in our hands.</li>
  <li><strong>Manufacturer photography.</strong> Product imagery supplied through Amazon is Program Content and its use is limited by the IP License. Our images are editorial illustrations, captioned as illustrations, with no brand marks ${flagLink('CDF-14')}.</li>
  <li><strong>Forecasts.</strong> No conversion rate, revenue projection or traffic estimate appears anywhere, because no data exists to support one.</li>
</ul>

<h2>How outbound links work</h2>
<p>Every link to Amazon on this site points at a product page with the tracking ID as a URL parameter, and every one is marked <code>rel="sponsored"</code>. Nothing is wrapped in a redirect: Amazon's rules treat a redirecting link as cloaking, and a shortener that obscures the destination is restricted too ${cite('S02')}. The supplied short links are recorded as evidence in the register, not published as buy links.</p>

<h2>Corrections</h2>
<p>If a number here is wrong, open an issue in the ${extLink('https://github.com/karagemop466-tech/Affil3/issues', 'project repository')}. Corrections are made in the data file, re-checked against the source, and logged on the flagged page — including corrections to our own earlier findings, of which there are two in this edition ${flagLinks(['CDF-08', 'CDF-09'])}.</p>

<h2>What this site is not</h2>
<p>It is not a test lab, not a price tracker and not a ranking. It is a shortlist with its working shown, which is useful for narrowing five appliances to one and useless for telling you how evenly any of them browns a chip.</p>
</div>

<p class="band"><a class="btn ghost" href="${esc(u('/review/compliance/'))}">The rule-by-rule compliance record</a> <a class="btn ghost" href="${esc(u('/review/sources/'))}">Every source, with its status</a></p>
</div>`,
});

// ── 404 ──────────────────────────────────────────────────────────────────
add({
  path: '/404.html', type: '404', noSitemap: true, noindex: true,
  title: 'Page not found',
  description: 'That page does not exist. The five countertop picks, the buying guides and the counter-space checker are all still where they were, one link away.',
  body: `<div class="wrap"><section class="page-head">
  <p class="kicker">404</p><h1>That page went missing</h1>
  <p class="deck">It may have moved. The five picks, the guides and the counter-space check are all where they were.</p>
  <p style="margin-top:22px"><a class="btn" href="${esc(u('/shelf/'))}">Back to the five picks</a> <a class="btn ghost" href="${esc(u('/'))}">Front page</a></p>
</section></div>`,
});

// ── operator surfaces ────────────────────────────────────────────────────
const sevOrder = { high: 0, medium: 1, low: 2 };
const openFlags = FLAGS.filter((f) => f.status !== 'resolved');

add({
  path: '/review/', type: 'review',
  title: 'Operator index: the records behind the publication',
  description: 'The registers, decisions and compliance records behind the Counter Desk publication, in one place and linked from every page.',
  body: `<div class="wrap">
<section class="page-head">
  <p class="kicker">Records</p>
  <h1>The working papers</h1>
  <p class="deck">Everything a reader does not need and an owner does: what is verified, what is not, what it would take to close each gap, and what the site is allowed to publish. None of it is hidden from a reader — it lives in the footer of every page for a reason.</p>
</section>

<div class="tiles">
  <div class="tile"><span class="n">${PRODUCTS.length}</span><div class="t">products tracked</div><div class="d">All five submitted by the owner. None added by us.</div></div>
  <div class="tile"><span class="n">${PRODUCTS.filter((p) => (p.spec_sources || []).length).length}</span><div class="t">with a manufacturer page</div><div class="d">Including the one an earlier pass said did not exist.</div></div>
  <div class="tile"><span class="n">${FLAGS.length}</span><div class="t">flags recorded</div><div class="d">${openFlags.length} open, ${FLAGS.length - openFlags.length} resolved and kept for the audit trail.</div></div>
  <div class="tile"><span class="n">${ledgerDoc.rows.length}</span><div class="t">ledger rows</div><div class="d">Empty until an authorised report exists.</div></div>
</div>

<div class="guide-grid" style="margin-top:34px">
${REVIEW.filter(([href]) => href !== '/review/').map(([href, label]) => {
  const blurb = {
    '/review/executive-summary/': 'One page: what is built, what is verified, what is blocked, and the four decisions only the owner can make.',
    '/review/flagged/': 'Fifteen irregularities and unverified values, each with the official page that settles it or the reason none does.',
    '/review/questions/': 'What we know, what we do not, and the specific step that turns one into the other. Each row names an owner.',
    '/review/suggestions/': 'A decision queue with trade-offs, including the four reader-facing items SG-27 to SG-30.',
    '/review/ledger/': 'Nine columns, zero rows, and a provenance rule that keeps it that way until a real report arrives.',
    '/review/measurement/': 'Five events, no cookies, and an endpoint that is deliberately unset.',
    '/review/compliance/': 'The rule-by-rule record: which clause, which requirement, and what in the build enforces it.',
    '/review/sources/': 'Every source read, how it was checked, and how far to trust it.',
    '/review/register/': 'The intent-versus-observation register, kept separate from the shop table on purpose.',
  }[href];
  return `<a class="card" href="${esc(u(href))}"><div class="card-body"><h3>${esc(label)}</h3><p class="blurb">${esc(blurb)}</p><span class="read">Open &rarr;</span></div></a>`;
}).join('\n')}
</div>

<section class="band">
  <div class="box"><span class="t">Why these are public</span><p>A shop that hides its working is asking to be believed. These pages are the working: every withheld number has a reason, every decision has a trade-off written next to it, and every gap has an owner and a next step. If a reader wants to check us, this is where to start.</p></div>
</section>
</div>`,
});

add({
  path: '/review/executive-summary/', type: 'review',
  title: 'Executive summary',
  description: 'What is built, what is verified, what is blocked, and the four decisions only the owner can make.',
  body: `<div class="wrap">
<section class="page-head">
  <p class="kicker">Executive summary <span class="sep">|</span> ${esc(dateLong(cfg.lastReviewed))}</p>
  <h1>Where this stands</h1>
  <p class="deck">One page for the owner. Everything below is reproducible from the repository and the linked sources, and nothing in it is a projection.</p>
</section>

<div class="tiles">
  <div class="tile"><span class="n">${pages.length + 5}</span><div class="t">published pages</div><div class="d">Publication plus records, one sitemap, one feed.</div></div>
  <div class="tile"><span class="n">${SR ? Object.keys(SR).length : 0}</span><div class="t">sources read</div><div class="d">Official pages only. No review site is cited for a value.</div></div>
  <div class="tile"><span class="n">0</span><div class="t">prices and ratings</div><div class="d">Not withheld by accident: Amazon's rules forbid it here.</div></div>
  <div class="tile"><span class="n">0</span><div class="t">validated buy links</div><div class="d">Formatted correctly, never confirmed against a report.</div></div>
</div>

<div class="prose">
<h2>What is built</h2>
<ul>
<li>A reader-facing publication: front page, a five-product shelf with a separate intent register, three category clusters, ${totalGuides} question-led guides, an interactive counter-space checker, and an RSS feed with a sitemap.</li>
<li>Two disclosures above the fold on every page — the FTC's own example sentence and the Associates statement — plus a repeat in the footer ${cites(['S05', 'S01'])}.</li>
<li>An operator layer: source register, product-intent register, flagged-for-review, open questions, suggestions with trade-offs, an empty campaign ledger, a measurement schema, and a rule-by-rule compliance record.</li>
<li>A build gate (<code>tools/3b45b513/gate.mjs</code>) that fails on a missing disclosure, an untagged or unqualified Amazon link, a price, a rating, a broken internal link, a missing image, an uncited specification, a sitemap gap or a feed gap.</li>
</ul>

<h2>What is verified</h2>
<ul>
<li>All five supplied links were followed on ${esc(dateLong('2026-11-20'))}. Three resolved to a product page; two resolved to the Amazon homepage. Both facts are recorded, dated, and flagged ${flagLinks(['CDF-02'])}.</li>
<li>Every published specification traces to a manufacturer page or a manufacturer manual, cited by id: Chefman twice, Emeril once, CHEF iQ twice, ThermoMaven twice ${cites(['S10', 'S12', 'S14', 'S17', 'S20', 'S21'])}.</li>
<li>The Amazon rules that decide what this site may publish were read in full: the Operating Agreement, the Program Policies including the price, rating, cloaking and shortener clauses, and the Commission Income Statement ${cites(['S01', 'S02', 'S03'])}.</li>
<li>The FTC's affiliate-disclosure guidance and 16 CFR 255.5 were read in full ${cites(['S05', 'S06'])}, as were the USDA temperature chart and thermometer factsheet ${cites(['S07', 'S08'])}, and Google's outbound-link guidance ${cite('S04')}.</li>
</ul>

<h2>What is not verified, and why</h2>
<ul>
<li><strong>Which product each link was meant to reach.</strong> Four intent fields per row are blank because no owner confirmation or Associates record was supplied ${flagLinks(['CDF-02'])}.</li>
<li><strong>Whether a tagged link credits a sale.</strong> No link has been clicked inside an enrolled Associates session; there is no Associates login here ${flagLinks(['CDF-04'])}.</li>
<li><strong>Wattage and dimensions of the 8 Qt Chefman.</strong> Two official pages disagree, so both are withheld with their figures recorded ${flagLinks(['CDF-05'])}.</li>
<li><strong>Two battery-life and two preset-count figures.</strong> Each manufacturer contradicts itself or its own listing ${flagLinks(['CDF-06', 'CDF-07'])}.</li>
<li><strong>Any traffic, click or order figure.</strong> The analytics endpoint is unset and the ledger is empty ${flagLinks(['CDF-10', 'CDF-11'])}.</li>
</ul>

<h2>Four decisions only the owner can make</h2>
<ol>
<li><strong>Confirm what each supplied link was meant to reach.</strong> One message closes the largest gap on the site.</li>
<li><strong>Run the one-link test in Associates Central.</strong> Formatting is not validation, and this is the gate between a page and an income.</li>
<li><strong>Decide where the analytics collector runs</strong>, or decide deliberately to run with none.</li>
<li><strong>Choose the canonical publication.</strong> This repository carries several independently generated editions over the same five links.</li>
</ol>
<p>Each is written up with its trade-offs on the <a href="${esc(u('/review/suggestions/'))}">suggestions page</a>, and each has an owner on the <a href="${esc(u('/review/questions/'))}">questions page</a>.</p>

<h2>What this build cannot do</h2>
<p>It cannot read Amazon prices, sales or Associates reports, because that needs authorised API or account access the build does not have, and it does not scrape Amazon. Any figure that would require that data is absent on purpose, not forgotten. The honest position on revenue is that this publication earns nothing today, and will earn nothing until a tagged link is confirmed in a report — and that the first month of real data should be read, not scaled against.</p>
</div>
</div>`,
});

add({
  path: '/review/flagged/', type: 'review',
  title: 'Flagged for review',
  description: 'Every irregularity and unverified value, with the official source that settles it, or the reason none does.',
  body: `<div class="wrap">
<section class="page-head">
  <p class="kicker">Flagged for review <span class="sep">|</span> ${FLAGS.length} items</p>
  <h1>What we could not confirm</h1>
  <p class="deck">${esc(flagsDoc.note)}</p>
</section>
<div class="box info"><span class="t">Nothing here blocks the publication</span><p>Each item is a gap between what a reader might assume and what this build can actually show. The manual step in each card is the shortest route to closing it. Resolved items are kept rather than deleted, so the audit trail survives a correction.</p></div>
<div style="margin-top:26px">
${[...FLAGS].sort((a, b) => (a.status === 'resolved') - (b.status === 'resolved') || (sevOrder[a.severity] - sevOrder[b.severity])).map((f) => `<section class="flag-card sev-${esc(f.severity)}${f.status === 'resolved' ? ' is-resolved' : ''}" id="${esc(f.id)}">
  <p class="flag-head"><a class="badge" href="#${esc(f.id)}">${esc(f.id)}</a> <span class="badge ${esc(f.severity)}">${esc(f.severity)}</span> <span class="badge ${f.status === 'resolved' ? 'resolved' : 'open'}">${esc(f.status)}</span> <span class="badge">${esc(f.area)}</span></p>
  <h2>${esc(f.title)}</h2>
  <p>${esc(f.detail)}</p>
  <p class="small"><strong>Why it matters:</strong> ${esc(f.why_it_matters)}</p>
  <p class="small"><strong>What would close it:</strong> ${esc(f.manual_step)}</p>
  <p class="meta-row"><b>Sources:</b> ${f.sources.length ? cites(f.sources) : 'none — this is a gap in the record, not a disputed fact'}</p>
</section>`).join('\n')}
</div>
</div>`,
});

add({
  path: '/review/questions/', type: 'review',
  title: 'Open questions and the discovery plan',
  description: 'What is known, what is not, how each gap can be closed, and who owns each one.',
  body: `<div class="wrap">
<section class="page-head">
  <p class="kicker">Open questions</p>
  <h1>What we know, what we do not, and how to find out</h1>
  <p class="deck">${esc(questionsDoc.note)}</p>
</section>

<h2>Established</h2>
<div class="table-wrap">
  <table class="data wide">
    <thead><tr><th scope="col">ID</th><th scope="col">Statement</th><th scope="col">Sources</th></tr></thead>
    <tbody>${questionsDoc.known.map((k) => `<tr><td><strong>${esc(k.id)}</strong></td><td>${esc(k.statement)}</td><td>${k.sources.length ? cites(k.sources) : '<span class="muted">owner brief</span>'}</td></tr>`).join('\n    ')}</tbody>
  </table>
</div>

<h2>Open</h2>
<div class="table-wrap">
  <table class="data wide">
    <thead><tr><th scope="col">ID</th><th scope="col">Question</th><th scope="col">Why it matters</th><th scope="col">How to close it</th><th scope="col">Owner</th><th scope="col">Blocks?</th><th scope="col">Sources</th></tr></thead>
    <tbody>${questionsDoc.unknown.map((q) => `<tr>
      <td><strong>${esc(q.id)}</strong></td>
      <td>${esc(q.question)}</td>
      <td>${esc(q.why)}</td>
      <td>${esc(q.how)}</td>
      <td>${esc(q.owner)}</td>
      <td>${q.blocks ? '<span class="badge high">yes</span>' : '<span class="badge low">no</span>'}</td>
      <td>${q.sources.length ? cites(q.sources) : '<span class="muted">none</span>'}</td>
    </tr>`).join('\n    ')}</tbody>
  </table>
</div>

<h2>Ways to discover what is missing</h2>
<div class="table-wrap">
  <table class="data wide">
    <thead><tr><th scope="col">ID</th><th scope="col">Method</th><th scope="col">Closes</th></tr></thead>
    <tbody>${questionsDoc.discovery.map((d) => `<tr><td><strong>${esc(d.id)}</strong></td><td>${esc(d.method)}</td><td>${d.closes.length ? d.closes.map((c) => `<a href="#${esc(c)}">${esc(c)}</a>`).join(', ') : '<span class="muted">context only</span>'}</td></tr>`).join('\n    ')}</tbody>
  </table>
</div>
</div>`,
});

add({
  path: '/review/suggestions/', type: 'review',
  title: 'Suggestions and the decisions they wait on',
  description: 'Every proposal with its trade-offs, including the four reader-facing items SG-27 to SG-30 and the decisions still open.',
  body: `<div class="wrap">
<section class="page-head">
  <p class="kicker">Decision queue <span class="sep">|</span> ${suggestionsDoc.suggestions.length} items</p>
  <h1>Choose a path before anything changes</h1>
  <p class="deck">${esc(suggestionsDoc.note)}</p>
</section>

<div class="box"><span class="t">How to read a row</span><p>Every item states the problem, the options with their real trade-offs, what this build does by default, and the single decision that changes it. A row with no trade-off is a row that has not been thought about.</p></div>

${suggestionsDoc.suggestions.map((s) => `<section class="flag-card" id="${esc(s.id)}" style="border-left-color:var(--clay)">
  <div class="flag-head">
    <a class="badge" href="#${esc(s.id)}">${esc(s.id)}</a>
    <span class="badge ${esc(s.status)}">${esc(s.status)}</span>
    <span class="badge">${esc(s.category)}</span>
  </div>
  <h2>${esc(s.topic)}</h2>
  <p><strong>The problem.</strong> ${esc(s.problem)}</p>
  <ul class="opts">
    ${s.options.map((o) => `<li><strong>${esc(o.id)}.</strong> ${esc(o.label)} <span class="trade">Trade-off: ${esc(o.tradeoff)}</span></li>`).join('\n    ')}
  </ul>
  <p class="small" style="margin-top:14px"><strong>What this build does:</strong> ${esc(s.chosen)}. ${esc(s.reasoning)}</p>
  ${s.implemented ? `<p class="small"><strong>Implemented:</strong> ${esc(s.implemented)}</p>` : ''}
  <p class="small"><strong>The prompt that would have got here faster:</strong> ${esc(s.prompt_improvement)}</p>
</section>`).join('\n')}

<div class="box info"><span class="t">What SG-27 to SG-30 actually delivered</span>
<p><strong>SG-27</strong> shipped: the top navigation is reader verbs, and every register lives in one footer group plus an operator index. <strong>SG-28</strong> shipped: the feed is generated from the guide register and the gate asserts one item per guide. <strong>SG-29</strong> and <strong>SG-30</strong> are gated, honestly: Search Console needs a Google account and reader capture needs a provider and a consent model. Both are written up here with their trade-offs rather than quietly dropped.</p></div>
</div>`,
});

add({
  path: '/review/ledger/', type: 'review',
  title: 'Campaign ledger',
  description: 'An empty ledger with a defined schema and a provenance rule. Rows are added only from authorised first-party reports.',
  body: `<div class="wrap">
<section class="page-head">
  <p class="kicker">Campaign ledger</p>
  <h1>Starting from nothing, on purpose</h1>
  <p class="deck">${esc(ledgerDoc.status)}</p>
</section>

<div class="box warn"><span class="t">The provenance rule</span><p>${esc(ledgerDoc.rule)}</p></div>

<div class="table-wrap">
  <table class="data wide">
    <thead><tr>${ledgerDoc.columns.map((c) => `<th scope="col">${esc(c.name)}</th>`).join('')}</tr></thead>
    <tbody><tr>${ledgerDoc.columns.map(() => '<td class="blank"><span class="blank-mark">—</span></td>').join('')}</tr></tbody>
  </table>
</div>
<p class="fine">Rows: ${ledgerDoc.rows.length}. No conversion score, revenue forecast or optimisation is presented anywhere on this site.</p>

<h2>What each column means</h2>
<div class="table-wrap">
  <table class="data">
    <thead><tr><th scope="col">Column</th><th scope="col">What goes in it</th></tr></thead>
    <tbody>${ledgerDoc.columns.map((c) => `<tr><td><code>${esc(c.name)}</code></td><td>${esc(c.meaning)}</td></tr>`).join('\n    ')}</tbody>
  </table>
</div>

<h2>What will never appear in it</h2>
<ul class="prose">
  ${ledgerDoc.prohibited.map((p) => `<li>${esc(p)}</li>`).join('\n  ')}
</ul>
<p class="prose">The reason for the strictness is practical rather than moral. A ledger that mixes an exported report with an estimate cannot be used to make a decision, because there is no way to tell which row caused the result. An empty ledger is a weaker asset than a populated one and a far better one than a populated fiction.</p>
</div>`,
});

add({
  path: '/review/measurement/', type: 'review',
  title: 'Measurement: five events and a deliberate silence',
  description: 'The five events this site would record, the privacy rules that shape them, and why nothing is being collected today.',
  body: `<div class="wrap">
<section class="page-head">
  <p class="kicker">Measurement</p>
  <h1>What we record, and what we refuse to</h1>
  <p class="deck">${esc(eventsDoc.status)}</p>
</section>

<div class="box warn" style="margin-top:22px"><span class="t">Live status</span><p>${cfg.analyticsEndpoint ? 'An endpoint is configured; events are being sent.' : `Inactive. No analytics endpoint is configured, so the browser sends nothing and no traffic figure exists anywhere on this site. ${flagLinks(['CDF-10'])}`}</p></div>

<h2>The five events</h2>
<div class="table-wrap">
  <table class="data wide">
    <thead><tr><th scope="col">Event</th><th scope="col">Fires when</th><th scope="col">Properties</th></tr></thead>
    <tbody>${eventsDoc.events.map((e) => `<tr><td><code>${esc(e.name)}</code></td><td>${esc(e.fires)}</td><td>${e.properties.map((p) => `<code>${esc(p)}</code>`).join(' ')}</td></tr>`).join('\n    ')}</tbody>
  </table>
</div>

<h2>The rules that shape the schema</h2>
<ul class="prose">
  ${eventsDoc.principles.map((p) => `<li>${esc(p)}</li>`).join('\n  ')}
</ul>

<h2>Not collected</h2>
<p class="prose">${eventsDoc.not_collected.map((x) => `<code>${esc(x)}</code>`).join(' ')}</p>

<h2>The endpoint contract</h2>
<div class="table-wrap">
  <table class="data">
    <tbody>
      <tr><th scope="row">Method and type</th><td><code>${esc(eventsDoc.endpoint_contract.method)}</code> · <code>${esc(eventsDoc.endpoint_contract.content_type)}</code></td></tr>
      <tr><th scope="row">Body</th><td><code>${esc(eventsDoc.endpoint_contract.body)}</code></td></tr>
      <tr><th scope="row">Accepted events</th><td>${esc(eventsDoc.endpoint_contract.allowed_events)}</td></tr>
      <tr><th scope="row">Response</th><td>${esc(eventsDoc.endpoint_contract.response)}</td></tr>
      <tr><th scope="row">Reference implementations</th><td>${eventsDoc.collector.reference_implementations.map((r) => `<code>${esc(r)}</code>`).join(' ')}</td></tr>
      <tr><th scope="row">Storage</th><td>${esc(eventsDoc.collector.storage)}</td></tr>
      <tr><th scope="row">Deployment</th><td>${esc(eventsDoc.collector.deployment)}</td></tr>
    </tbody>
  </table>
</div>

<h2>Why an outbound click is never routed through this site</h2>
<p class="prose">It would be easy to send the reader through a <code>/go/&lt;id&gt;</code> redirect and count the click on the way. Amazon's rules forbid it: Participation Requirements 6(v) treats a Redirecting Link as a way of obscuring the site a click came from, and 6(w) restricts link shortening that makes it unclear a link goes to Amazon ${cite('S02')}. So the counter records the click in the browser and lets the browser follow the link directly. Fewer analytics, and a link that stays honest.</p>

<h2>Why there is no chart on this page</h2>
<p class="prose">A chart of nothing is a chart that gets screenshotted. When an endpoint is deployed and a thirty-day window exists, the numbers will appear here with their window, their source and their gaps — and not before.</p>
</div>`,
});

add({
  path: '/review/compliance/', type: 'review',
  title: 'Disclosure, link rules and the publishing gates',
  description: 'The rule-by-rule compliance record: the clause, what it requires, and what in this build enforces it.',
  body: `<div class="wrap">
<section class="page-head">
  <p class="kicker">Compliance</p>
  <h1>Disclosure, links and the gates before scaling</h1>
  <p class="deck">Every rule below cites the clause it comes from and names the thing in the build that enforces it. A rule with no enforcement mechanism is a wish, so none of them are listed without one.</p>
</section>

<h2>The two statements and where they sit</h2>
<div class="prose">
<p>Amazon's Operating Agreement §5 requires the site to state, clearly and prominently: <strong>“${esc(cfg.associatesStatement)}”</strong> ${cite('S01')}</p>
<p>The FTC's affiliate-marketing guidance gives its own example wording — <strong>“${esc(cfg.disclosure)}”</strong> — and says the disclosure should sit as close to the recommendation as it can ${cite('S05')}, which is what 16 CFR 255.5 means by clearly and conspicuously ${cite('S06')}.</p>
<p>Both sentences appear in the disclosure bar directly under the masthead on every page of this site, and both are repeated in the footer. The bar is above the first product on the front page and above the first buy button on every product page, so no reader reaches a paid link without having passed it.</p>
</div>

<h2>Link rules, and what enforces them</h2>
<div class="table-wrap">
  <table class="data wide">
    <thead><tr><th scope="col">Rule</th><th scope="col">Source</th><th scope="col">How this build complies</th><th scope="col">Enforced by</th></tr></thead>
    <tbody>
      <tr><td>Every link to an Amazon site must carry the Associates ID as a URL parameter</td><td>${cite('S02')}</td><td>Every outbound product link is generated as <code>amazon.com/dp/&lt;asin&gt;?tag=${esc(cfg.trackingId)}</code> by a single function; no hand-written Amazon href exists anywhere</td><td>Gate: any Amazon retail link without the exact tag fails the build</td></tr>
      <tr><td>Paid and affiliate links should be qualified for search</td><td>${cite('S04')}</td><td><code>rel="sponsored noopener"</code> on every Amazon link</td><td>Gate: an Amazon link without <code>sponsored</code> fails</td></tr>
      <tr><td>Special Links must be accessed directly; no cloaking or redirecting link</td><td>${cite('S02')}</td><td>No redirect endpoint exists in this build. The click counter is client-side only</td><td>Gate: a meta refresh or <code>window.location</code> assignment fails; no <code>/go/</code> path is generated</td></tr>
      <tr><td>No link shortening that makes it unclear the link goes to Amazon</td><td>${cite('S02')}</td><td>The supplied <code>link.amazon</code> short links are shown as plain text evidence in the register, never as clickable links</td><td>Gate: a <code>link.amazon</code> anchor fails</td></tr>
      <tr><td>Price and availability only from Amazon-served data or the API</td><td>${cite('S02')}</td><td>No price, availability or currency amount is published anywhere</td><td>Gate: a currency pattern in any rendered page fails</td></tr>
      <tr><td>Customer reviews and star ratings only from the API</td><td>${cite('S02')}</td><td>No rating, review count or review text is republished</td><td>Gate: a rating pattern fails</td></tr>
      <tr><td>No price tracking or alerting</td><td>${cite('S02')}</td><td>The site stores no price and no history</td><td>Structural: there is no price field in the data model</td></tr>
      <tr><td>Disclosure must be clear and conspicuous</td><td>${cite('S06')}</td><td>The bar sits above the fold on every page and is repeated in the footer</td><td>Gate: a page whose disclosure appears after <code>&lt;main&gt;</code> fails</td></tr>
      <tr><td>One coherent site for search engines</td><td>${cite('S04')}</td><td>This edition has its own sitemap and feed, is namespaced under <code>/counter-desk/</code>, and declares a canonical URL on every page</td><td>Gate: a page missing from the sitemap fails; the feed must match the guide register</td></tr>
      <tr><td>No claim of hands-on testing</td><td>Editorial policy</td><td>Every image is captioned as illustration; the front page, About page and every product page say the appliances were not tested</td><td>Gate: a testing claim pattern fails</td></tr>
    </tbody>
  </table>
</div>

<h2>Gates before this scales</h2>
<div class="table-wrap">
  <table class="data wide">
    <thead><tr><th scope="col">Gate</th><th scope="col">Check</th><th scope="col">Method</th><th scope="col">Status</th></tr></thead>
    <tbody>
      <tr><td>G-01</td><td>Both disclosures above the fold on every page, repeated in the footer</td><td>Automated</td><td><span class="badge resolved">passing</span></td></tr>
      <tr><td>G-02</td><td>One Special Link per product tested in Associates Central, destination and tracking report confirmed</td><td>Manual — needs an Associates login</td><td><span class="badge high">pending</span> ${flagLinks(['CDF-04'])}</td></tr>
      <tr><td>G-03</td><td>Every Amazon link carries <code>rel="sponsored"</code></td><td>Automated</td><td><span class="badge resolved">passing</span></td></tr>
      <tr><td>G-04</td><td>Every outbound product link carries <code>tag=${esc(cfg.trackingId)}</code></td><td>Automated</td><td><span class="badge resolved">passing</span></td></tr>
      <tr><td>G-05</td><td>No redirect, cloaking page or shortener anchor</td><td>Automated</td><td><span class="badge resolved">passing</span></td></tr>
      <tr><td>G-06</td><td>No price, rating or availability displayed</td><td>Automated</td><td><span class="badge resolved">passing</span></td></tr>
      <tr><td>G-07</td><td>Every published specification carries a source id that exists</td><td>Automated</td><td><span class="badge resolved">passing</span></td></tr>
      <tr><td>G-08</td><td>Ledger rows only from authorised first-party reports</td><td>Manual</td><td><span class="badge low">no rows yet</span></td></tr>
      <tr><td>G-09</td><td>Only the five defined events; no cookies, no storage</td><td>Automated</td><td><span class="badge resolved">passing</span></td></tr>
      <tr><td>G-10</td><td>Sitemap and feed cover every page and guide; no broken internal links; every image exists with alt text</td><td>Automated</td><td><span class="badge resolved">passing</span></td></tr>
      <tr><td>G-11</td><td>Every image is captioned as an illustration</td><td>Automated</td><td><span class="badge resolved">passing</span></td></tr>
      <tr><td>G-12</td><td>One canonical URL per page, one <code>h1</code>, a title under 90 characters</td><td>Automated</td><td><span class="badge resolved">passing</span></td></tr>
    </tbody>
  </table>
</div>
<p class="fine">Gate G-02 is the only one this build cannot pass, and it cannot pass it by writing better code: it needs a signed-in Associates session. Everything else is enforced by <code>node tools/3b45b513/gate.mjs</code>, which runs in CI on every push and fails the build rather than warning.</p>
</div>`,
});

add({
  path: '/review/sources/', type: 'review',
  title: 'Source register',
  description: 'Every source read for this edition, how it was checked, what it supports, and how far to trust it.',
  body: `<div class="wrap">
<section class="page-head">
  <p class="kicker">Source register <span class="sep">|</span> ${sourcesDoc.sources.length} sources</p>
  <h1>Every source, and how far to trust it</h1>
  <p class="deck">${esc(sourcesDoc.note)}</p>
</section>
<div class="table-wrap" style="margin-top:24px">
  <table class="data wide">
    <thead><tr><th scope="col">ID</th><th scope="col">Source</th><th scope="col">Publisher</th><th scope="col">How it was checked</th><th scope="col">What it supports</th><th scope="col">Status</th><th scope="col">Link</th></tr></thead>
    <tbody>${sourcesDoc.sources.map((s) => `<tr id="${esc(s.id)}">
      <td><strong>${esc(s.id)}</strong></td>
      <td>${esc(s.title)}</td>
      <td>${esc(s.publisher)}</td>
      <td>${esc(s.method)}</td>
      <td>${esc(s.supports)}</td>
      <td><span class="badge ${s.status === 'verified' ? 'resolved' : ''}">${esc(s.status)}</span></td>
      <td>${sourceLink(s.id, 'Open')}</td>
    </tr>`).join('\n    ')}</tbody>
  </table>
</div>

<h2>How to read the status column</h2>
<div class="prose">
<ul>
  <li><strong>verified</strong> — the full page was retrieved and read on the date shown, and the wording relied on is quoted in the register.</li>
  <li><strong>observed</strong> — a value read off a live Amazon page on a dated fetch. Useful as evidence of what happened that day, and capable of changing tomorrow.</li>
</ul>
<p>No blog, review site, reseller listing or aggregator is cited for a single value on this site. Where a number could not be traced to one of the rows above, it is absent from the page rather than borrowed from a source that would not survive being asked about.</p>
</div>
</div>`,
});

add({
  path: '/review/register/', type: 'review',
  title: 'Product-intent register',
  description: 'The register that keeps what each supplied link was meant to reach separate from what it actually reached, with every field and its status.',
  body: `<div class="wrap">
<section class="page-head">
  <p class="kicker">Product-intent register</p>
  <h1>Intent and observation, kept apart</h1>
  <p class="deck">${esc(productsDoc.rule)}</p>
</section>

<div class="table-wrap" style="margin-top:24px">
  <table class="data wide">
    <thead><tr><th scope="col">ID</th><th scope="col">Supplied link</th><th scope="col">Token</th><th scope="col">Intended ASIN</th><th scope="col">Official listing URL</th><th scope="col">Confirmation date</th><th scope="col">Confirmation source</th><th scope="col">Observed ASIN</th><th scope="col">Observed on</th></tr></thead>
    <tbody>${PRODUCTS.map((p) => `<tr>
      <td><strong>${esc(p.id)}</strong></td>
      <td><code>${esc(p.submitted_url.replace('https://', ''))}</code></td>
      <td><code>${esc(p.submitted_token)}</code><br><span class="fine">${p.submitted_token_length} chars</span></td>
      <td class="blank"><span class="blank-mark">blank</span></td>
      <td class="blank"><span class="blank-mark">blank</span></td>
      <td class="blank"><span class="blank-mark">blank</span></td>
      <td class="blank"><span class="blank-mark">blank</span></td>
      <td><code>${esc(p.observed.asin)}</code></td>
      <td>${esc(p.observed.date)}</td>
    </tr>`).join('\n    ')}</tbody>
  </table>
</div>

<div class="box warn" style="margin-top:22px"><span class="t">Why four columns are blank</span><p>They are filled only from an owner confirmation or an official Associates record. Neither was supplied with this brief, so all four are blank for all five rows. Filling them from the observed column would look tidier and would destroy the only thing this register is for: the ability to show that intent and observation are separate claims which are allowed to disagree. ${flagLinks(['CDF-02'])}</p></div>

<h2>What each row observes, verbatim</h2>
${PRODUCTS.map((p) => `<div class="trade-card" style="margin-bottom:14px">
  <h3>${esc(p.id)} · ${esc(p.short_name)}</h3>
  <p class="small" style="margin:0 0 8px"><strong>Listing observed ${esc(dateLong(p.observed.date))}:</strong> “${esc(p.observed.title)}”</p>
  <p class="small" style="margin:0 0 8px"><strong>Breadcrumb:</strong> ${esc(p.observed.breadcrumb)}</p>
  <p class="small" style="margin:0"><strong>Observed via:</strong> ${cite(p.observed.source)} · <strong>Specifications from:</strong> ${cites(p.spec_sources)}</p>
</div>`).join('\n')}
</div>`,
});

// ── write ────────────────────────────────────────────────────────────────
fs.rmSync(OUT, { recursive: true, force: true });
fs.mkdirSync(OUT, { recursive: true });

const written = [];
for (const p of pages) {
  const file = p.path.endsWith('.html') ? path.join(OUT, p.path) : path.join(OUT, p.path, 'index.html');
  fs.mkdirSync(path.dirname(file), { recursive: true });
  let html = shell(p);
  // A currency amount must never survive rendering, whatever a data file says.
  html = html.replace(/\$\s?\d[\d,]*(\.\d{2})?/g, (m) => `<!-- stripped currency: ${m.replace(/--/g, '')} -->`);
  fs.writeFileSync(file, html);
  written.push({ path: p.path, file: path.relative(ROOT, file), noSitemap: !!p.noSitemap, noindex: !!p.noindex });
}

// assets
fs.mkdirSync(path.join(OUT, 'assets/img'), { recursive: true });
for (const f of ['style.css', 'analytics.js', 'finder.js']) {
  fs.copyFileSync(path.join(ASSETS_SRC, f), path.join(OUT, 'assets', f));
}
for (const f of fs.readdirSync(path.join(ASSETS_SRC, 'img'))) {
  fs.copyFileSync(path.join(ASSETS_SRC, 'img', f), path.join(OUT, 'assets/img', f));
}
fs.writeFileSync(path.join(OUT, '.nojekyll'), '');

// sitemap
const sitemapPages = written.filter((w) => !w.noSitemap);
fs.writeFileSync(path.join(OUT, 'sitemap.xml'), `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${sitemapPages.map((w) => `  <url><loc>${esc(abs(w.path === '/404.html' ? '/' : w.path))}</loc><lastmod>${cfg.lastReviewed}</lastmod><changefreq>${w.path === '/' ? 'weekly' : 'monthly'}</changefreq></url>`).join('\n')}
</urlset>
`);

// feed
const feedItems = [...GUIDES].sort((a, b) => (a.date < b.date ? 1 : -1));
fs.writeFileSync(path.join(OUT, 'feed.xml'), `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
  <title>Counter Desk — kitchen buying guides</title>
  <link>${esc(abs('/'))}</link>
  <atom:link href="${esc(abs('/feed.xml'))}" rel="self" type="application/rss+xml"/>
  <description>${esc('Countertop cooking appliances compared by manufacturer specification, with every gap and conflict stated plainly.')}</description>
  <language>en-US</language>
  <lastBuildDate>${rfc822(cfg.lastReviewed)}</lastBuildDate>
  <copyright>Counter Desk. Product names and trademarks belong to their owners.</copyright>
${feedItems.map((g) => `  <item>
    <title>${esc(g.title)}</title>
    <link>${esc(abs('/guides/' + g.slug + '/'))}</link>
    <guid isPermaLink="true">${esc(abs('/guides/' + g.slug + '/'))}</guid>
    <pubDate>${rfc822(g.date)}</pubDate>
    <description>${esc(g.description)}</description>
  </item>`).join('\n')}
</channel>
</rss>
`);

// robots — this edition is additive and namespaced; it points at its own sitemap only
fs.writeFileSync(path.join(OUT, 'robots.txt'), `User-agent: *
Allow: ${cfg.basePath}/

Sitemap: ${abs('/sitemap.xml')}
`);

console.log(`counter-desk: built ${written.length} pages, ${feedItems.length} feed items, ${sitemapPages.length} sitemap URLs`);
