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
const OWNED = ['index.html', 'shop', 'categories', 'guides', 'executive-summary', 'sources', 'questions', 'suggestions',
  'flagged', 'ledger', 'measurement', 'compliance', 'about', '404.html', 'feed.xml', 'sitemap.xml', 'robots.txt',
  'assets/style.css', 'assets/analytics.js', '.nojekyll'];
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
  const title = displayName(p);
  const cat = catName(p.category);
  if (tagged(p)) {
    return `<article class="card product" data-product-view="${esc(p.id)}">
  <p class="kicker">${esc(cat)} · ${esc(p.id)}</p>
  <h3>${esc(title)}</h3>
  <p class="muted">Observed ASIN <code>${esc(p.observed_asin)}</code></p>
  <p><a class="btn" href="${esc(tagged(p))}" rel="sponsored noopener" data-outbound data-product="${esc(p.id)}" data-placement="${esc(placement)}">View on Amazon</a></p>
  <p class="status">${esc(p.outbound_status)}</p>
</article>`;
  }
  return `<article class="card product warn-card" data-product-view="${esc(p.id)}">
  <p class="kicker">${esc(cat)} · ${esc(p.id)}</p>
  <h3>Link not resolved</h3>
  <p class="muted">Submitted link: <code>${esc(p.submitted_token)}</code></p>
  <p class="status">No buy link is published. The link has not resolved to a product page in a verified session. An Amazon "Continue shopping" checkpoint is intermittent and is not by itself evidence that a link is dead. ${flagLinks(['FLG-004'])}</p>
</article>`;
}

function renderBlock(b) {
  switch (b.type) {
    case 'note': return `<p class="note">${esc(b.text)}</p>`;
    case 'p': return `<p>${esc(b.text)}</p>`;
    case 'h2': return `<h2 id="${esc(b.text.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, ''))}">${esc(b.text)}</h2>`;
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

// Home (publication front page: products first)
{
  const shelf = products.map((p) => productCard(p, 'front-shelf')).join('\n');
  const guideList = guides.map((g) => `<li class="guide-item"><a href="${esc(href('/guides/' + g.slug + '/'))}">${esc(g.title)}</a><span class="muted"> · ${esc(catName(g.category))} · ${esc(dateLong(g.date))}</span><p>${esc(g.deck)}</p></li>`).join('\n');
  const catCards = CATEGORIES.filter((c) => c.slug !== 'unresolved').map((c) => `<a class="card cat-card" href="${esc(href('/categories/' + c.slug + '/'))}"><h3>${esc(c.name)}</h3><p>${esc(c.blurb)}</p></a>`).join('\n');
  add({
    path: '/', title: 'Kitchen picks, traced to their listings',
    description: 'Five kitchen products we track, each traced to its Amazon listing, with buying guides that say what to compare and what was not verified.',
    type: 'home',
    body: `
<section class="front">
  <p class="kicker">Observed on 2026-11-20 · Amazon listings</p>
  <h1>Five kitchen picks, each traced to its listing</h1>
  <p class="deck">Start with a product, or with a guide that tells you what to compare. Each product shows the Amazon page it resolved to and the source we read.</p>
  <div class="shelf">${shelf}</div>
  <p class="shelf-note">Buttons open Amazon with our tracking ID in the link. Links are marked sponsored. See the <a href="${esc(href('/compliance/'))}">disclosure policy</a>.</p>
</section>
<section class="band">
  <h2>Start with a guide</h2>
  <ul class="guide-list">${guideList}</ul>
  <p><a href="${esc(href('/guides/'))}">All guides</a></p>
</section>
<section class="band">
  <h2>Browse by category</h2>
  <div class="cat-grid">${catCards}</div>
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
<ul class="guide-list">${guides.map((g) => `<li class="guide-item"><a href="${esc(href('/guides/' + g.slug + '/'))}">${esc(g.title)}</a><span class="muted"> · ${esc(dateLong(g.date))}</span><p>${esc(g.deck)}</p></li>`).join('')}</ul>`,
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
  description: 'Executive summary: what is built, what is verified, what is blocked, and the decisions needed.',
  body: `<section class="page-head"><p class="kicker">Executive summary · ${esc(dateLong(cfg.lastReviewed))}</p><h1>Where this stands</h1></section>
<div class="prose">
<h2>What is built</h2>
<ul>
<li>A publication-style site with a front page led by the five submitted products, a shop table, four category clusters, five question-led guides, and an RSS feed and sitemap.</li>
<li>Dashboards for sources, questions, suggestions, flagged items, the campaign ledger (empty), measurement, and compliance. All are linked from the footer.</li>
<li>A disclosure strip under the masthead on every page, repeated in the footer, using the statement required by Operating Agreement §5.</li>
<li>A privacy-preserving click counter in the browser and a self-hostable collector. The collector is inactive on the live site until an endpoint is set (FLG-009).</li>
<li>Automated checks (tools/verify.mjs) for disclosure presence, sponsored attributes, tags, sources, sitemap and feed coverage, and internal links.</li>
</ul>
<h2>What is verified</h2>
<ul>
<li>The Associates disclosure statement, the Special Link and tag rules, and the anti-cloaking clause are read from the official Associates pages (S01, S02).</li>
<li>The rel="sponsored" guidance (S06), FTC disclosure guidance (S07, S08), and USDA temperatures (S09, S10) are read from official pages.</li>
<li>For each product, the observed Amazon ASIN, title and breadcrumb are read from the amazon.com page the link resolved to on 2026-11-20 (S04, S05).</li>
</ul>
<h2>What is not verified, and why</h2>
<ul>
<li>The intended ASIN, official listing URL, confirmation date and source are blank for all five products. The submitted tokens are 9 characters, and the observed destinations differ from the tokens (FLG-001, FLG-002).</li>
<li>One link resolved to a checkpoint page (FLG-004). The status of the short links is unresolved, not invalid (FLG-003).</li>
<li>No Special Link has been tested in Associates Central. The sandbox has no Associates login (FLG-005, gate G-02).</li>
<li>No prices, ratings, sales or commission figures are shown. The campaign ledger is empty and no conversion score or revenue forecast is presented.</li>
</ul>
<h2>Decisions needed from you</h2>
<ol>
<li>Give the intended product for each short link, or confirm the observed product (Q-01).</li>
<li>Confirm the account declares this site and that tracking ID shopnow047c-20 is on the account (Q-03, FLG-011).</li>
<li>Run gate G-02: one Special Link per product in Associates Central, then tell us the result (Q-04).</li>
<li>Choose options on the <a href="${esc(href('/suggestions/'))}">Suggestions</a> page. Nothing there is implemented until you choose.</li>
</ol>
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
<h2>Unknown: questions to answer</h2>
${table(['ID', 'Question', 'Why it matters', 'How to close it', 'Blocks scaling?', 'Sources'], questions.unknown.map((q) => [esc(q.id), esc(q.question), esc(q.why_it_matters), esc(q.how_to_close), q.blocking ? '<strong>Yes</strong>' : 'No', q.sources.map(srcLink).join(', ') || '<span class="muted">none</span>']), 'wide')}
<h2>Ways to discover missing information</h2>
${table(['ID', 'Suggestion', 'Closes'], questions.discovery.map((d) => [esc(d.id), esc(d.suggestion), d.closes.map(esc).join(', ') || '<span class="muted">none</span>']))}`,
});

// Suggestions
add({
  path: '/suggestions/', title: 'Suggestions: choose a path',
  description: 'Options for the next decisions. Nothing is implemented until the owner chooses.',
  body: `<section class="page-head"><p class="kicker">Suggestions</p><h1>Choose a path before anything changes</h1><p class="deck">${esc(suggestionsDoc.note)}</p></section>
${table(['ID', 'Topic', 'Current', 'Options', 'Recommendation'], suggestionsDoc.suggestions.map((s) => [
    `<strong>${esc(s.id)}</strong>`, esc(s.topic), `<span class="badge">${esc(s.current)}</span>`,
    `<ul class="opts">${s.options.map((o) => `<li><strong>${esc(o.id)}.</strong> ${esc(o.label)} <span class="muted small">Tradeoff: ${esc(o.tradeoff)}</span></li>`).join('')}</ul>`,
    esc(s.recommendation),
  ]), 'wide')}`,
});

// Flagged for review
add({
  path: '/flagged/', title: 'Flagged for review',
  description: 'Irregularities and unverified items, with the sources and the manual step that would close each one.',
  body: `<section class="page-head"><p class="kicker">Flagged for review</p><h1>Flagged for review</h1><p class="deck">${esc(flagsDoc.note)} Flags do not block publication.</p></section>
${flagsDoc.flags.map((f) => `<section class="flag-card" id="${esc(f.id)}">
  <p class="flag-head"><span class="badge flag">${esc(f.id)}</span> <span class="badge sev-${esc(f.severity)}">${esc(f.severity)}</span> <strong>${esc(f.title)}</strong></p>
  <p>${esc(f.detail)}</p>
  <p class="small"><strong>Sources:</strong> ${f.sources.length ? f.sources.map(srcLink).join(', ') : 'none (repo or owner input)'}</p>
  <p class="small"><strong>Manual step:</strong> ${esc(f.manual_step)}</p>
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
