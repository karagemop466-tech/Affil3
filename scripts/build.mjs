#!/usr/bin/env node
// Builds the static site from src/data/*.json into _site/.
// No dependencies. Every value shown comes from src/data; nothing is inferred.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const DATA = path.join(ROOT, 'src/data');
const ASSETS = path.join(ROOT, 'src/assets');
const OUT = path.join(ROOT, '_site');
const SITE_URL = 'https://karagemop466-tech.github.io/Affil3/';
const DISCLOSURE = 'As an Amazon Associate I earn from qualifying purchases.';
const SPONSOR_LABEL = 'Sponsored link';

const load = (f) => JSON.parse(fs.readFileSync(path.join(DATA, f), 'utf8'));
const products = load('products.json');
const sources = load('sources.json');
const flags = load('flags.json');
const questions = load('questions.json');
const suggestions = load('suggestions.json');
const guides = load('guides.json');
const findings = load('findings.json');
const ledger = load('ledger.json');

const srcById = Object.fromEntries(sources.map((s) => [s.id, s]));

const esc = (s) =>
  String(s ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
const short = (s, n) => (s.length > n ? s.slice(0, n - 1).trimEnd() + '…' : s);
const H = (html) => ({ html });
const cell = (c) => (c && typeof c === 'object' && 'html' in c ? c.html : esc(c));
const isAmazonProduct = (u) => /amazon\.com\/dp\/|link\.amazon\//.test(u);
const relFor = (u) => (isAmazonProduct(u) ? 'sponsored noopener' : 'noopener');

// Outbound anchor. Any link to an Amazon product or short link is marked sponsored.
const a = (href, label, extra = '') =>
  `<a href="${esc(href)}" rel="${relFor(href)}"${/^https?:/.test(href) ? ' target="_blank"' : ''}${extra}>${esc(label)}</a>`;

const srcLink = (id) => {
  const s = srcById[id];
  if (!s) return H(`<span class="tag tag-warn">Missing source ${esc(id)}</span>`);
  return H(a(s.url, `${s.id} · ${short(s.title, 60)}`));
};
const srcList = (ids) => H(ids.map((id) => (srcById[id] ? srcLink(id).html : `<span class="tag tag-warn">${esc(id)}</span>`)).join('<br>'));
const flagRef = (id, R) => `<a class="flagref" href="${R}flagged/#${id}">${id}</a>`;
const flagList = (ids, R) => H(ids.map((id) => flagRef(id, R)).join(' '));
const unverifiedTag = H('<span class="tag tag-warn">Unverified · blank</span>');
const observedTag = H('<span class="tag tag-ok">Observed</span>');

function table(headers, rows, { cls = '', empty = 'No rows yet.' } = {}) {
  const th = headers.map((h) => `<th scope="col">${esc(h)}</th>`).join('');
  const body = rows.length
    ? rows.map((r) => `<tr>${r.map((c) => `<td>${cell(c)}</td>`).join('')}</tr>`).join('')
    : `<tr><td colspan="${headers.length}" class="empty">${esc(empty)}</td></tr>`;
  return `<div class="table-wrap"><table class="${cls}"><thead><tr>${th}</tr></thead><tbody>${body}</tbody></table></div>`;
}

// ---------- layout ----------
const NAV = [
  ['Shop', 'products/'],
  ['Categories', 'categories/'],
  ['Guides', 'guides/'],
  ['Research', 'research/'],
  ['Verification', 'verification/'],
  ['Questions', 'questions/'],
  ['Suggestions', 'suggestions/'],
  ['Ledger', 'ledger/'],
  ['Flagged for Review', 'flagged/'],
  ['Executive Summary', 'executive-summary/'],
];

function page({ file, title, description, active, body }) {
  const depth = file.split('/').length - 1;
  const R = depth === 0 ? './' : '../'.repeat(depth);
  const navHtml = NAV.map(
    ([label, href]) =>
      `<a href="${R}${href}"${active === href ? ' aria-current="page"' : ''}>${esc(label)}</a>`,
  ).join('');
  const canonical = SITE_URL + (file === 'index.html' ? '' : file.replace(/index\.html$/, ''));
  const footNav = NAV.map(([label, href]) => `<li><a href="${R}${href}">${esc(label)}</a></li>`).join('');
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(title)} · Affil3</title>
<meta name="description" content="${esc(description)}">
<link rel="canonical" href="${esc(canonical)}">
<link rel="stylesheet" href="${R}assets/style.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="masthead">
  <div class="wrap masthead-inner">
    <a class="brand" href="${R}">Affil3</a>
    <p class="tagline">Kitchen picks, checked line by line against Amazon's own listing pages</p>
  </div>
  <nav class="nav" aria-label="Main"><div class="wrap">${navHtml}</div></nav>
</header>
<div class="disclosure" role="note"><div class="wrap"><strong>Disclosure:</strong> ${esc(DISCLOSURE)} Links labelled “${SPONSOR_LABEL}” are affiliate links.</div></div>
<main id="main" class="wrap">
${body(R)}
</main>
<footer class="footer">
  <div class="wrap">
    <div class="disclosure footer-disclosure"><strong>Disclosure:</strong> ${esc(DISCLOSURE)}</div>
    <div class="footer-cols">
      <div>
        <h4>All sections</h4>
        <ul>${footNav}</ul>
      </div>
      <div>
        <h4>About this site</h4>
        <p>Every product row shows its source link. Values that could not be confirmed are left blank and flagged. The site is updated from data files in the repository.</p>
        <p><a href="${R}executive-summary/">Read the executive summary</a> · <a href="${R}flagged/">Flagged for Review</a></p>
      </div>
    </div>
  </div>
</footer>
</body>
</html>
`;
}

// ---------- shared pieces ----------
const productById = Object.fromEntries(products.map((p) => [p.id, p]));
const resolvedCount = products.filter((p) => p.observed_redirect_asin).length;
const unresolvedCount = products.length - resolvedCount;
const confirmedPriceCount = products.filter((p) => p.price).length;
const openQuestions = questions.length;
const awaitingSuggestions = suggestions.filter((s) => !s.decision).length;
const flagCount = flags.length;
const highFlags = flags.filter((f) => f.severity === 'High').length;

const categories = [...new Set(products.map((p) => p.category))];
const catSlug = (c) =>
  c.toLowerCase().replace(/&/g, 'and').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
const categoryPages = categories.filter((c) => c !== 'Not classified');

function card(p, R) {
  const resolved = Boolean(p.observed_redirect_asin);
  const title = p.observed_title ? short(p.observed_title, 120) : 'Listing not yet identified';
  return `<article class="card" id="card-${p.id}">
  <p class="card-cat">${esc(p.category)} · ${esc(p.id)}</p>
  <h3>${esc(title)}</h3>
  <dl class="facts">
    <div><dt>Observed ASIN</dt><dd>${resolved ? esc(p.observed_redirect_asin) : '<span class="tag tag-warn">None observed</span>'}</dd></div>
    <div><dt>Price</dt><dd><span class="tag tag-warn">Not confirmed</span></dd></div>
  </dl>
  ${resolved ? '' : `<p class="note">The supplied link led to an Amazon checkpoint page, not a product. See ${flagRef('FLG-005', R)}.</p>`}
  <div class="card-actions">
    ${a(p.supplied_url, resolved ? 'View on Amazon ↗' : 'Open supplied link ↗', ' class="btn"')}
    <span class="sponsor">${SPONSOR_LABEL}</span>
  </div>
  <a class="small-link" href="${R}products/#${p.id}">Sources and details</a>
</article>`;
}

// ---------- pages ----------
const pages = [];

pages.push({
  file: 'index.html',
  active: '',
  title: 'Affil3 · Kitchen picks',
  description: 'Air fryers and a smart thermometer, with ASINs and Amazon listing sources shown for every entry.',
  body: (R) => `
<section class="hero">
  <p class="kicker">This week on the shelf</p>
  <h1>Air fryers and a smart thermometer, with the listing facts shown first</h1>
  <p class="dek">Four of the five links we were given lead to Amazon product pages. Each entry shows the ASIN we observed, the title the seller wrote, and what we could not confirm.</p>
  <div class="cta-row">
    <a class="btn" href="${R}products/">Browse all five</a>
    <a class="btn btn-ghost" href="${R}categories/">Shop by category</a>
  </div>
</section>

<section>
  <h2 class="section-head">Featured listings</h2>
  <div class="grid">${products.map((p) => card(p, R)).join('')}</div>
</section>

<section class="split">
  <div>
    <h2 class="section-head">Shop by category</h2>
    <ul class="linklist">
      ${categoryPages.map((c) => `<li><a href="${R}categories/${catSlug(c)}.html">${esc(c)}</a> <span class="muted">${products.filter((p) => p.category === c).length} listing(s)</span></li>`).join('')}
      <li><a href="${R}products/#P03">Not yet classified</a> <span class="muted">1 listing, unresolved</span></li>
    </ul>
  </div>
  <div>
    <h2 class="section-head">Guides in preparation</h2>
    <p class="muted">Working titles, not published. Each is a hypothesis to test, not a claim.</p>
    <ul class="linklist">
      ${guides.map((g) => `<li><a href="${R}guides/#${g.id}">${esc(g.working_title)}</a></li>`).join('')}
    </ul>
  </div>
</section>

<section class="status">
  <h2 class="section-head">Where things stand</h2>
  <div class="stat-row">
    <div class="stat"><span>${products.length}</span>listings in the register</div>
    <div class="stat"><span>${resolvedCount}</span>resolved to Amazon product pages</div>
    <div class="stat"><span>${confirmedPriceCount}</span>prices confirmed</div>
    <div class="stat"><span>${openQuestions}</span>open questions</div>
    <div class="stat"><span>${flagCount}</span>items flagged for review (${highFlags} high)</div>
    <div class="stat"><span>${ledger.rows.length}</span>campaign ledger rows</div>
  </div>
  <p class="muted">Flagged items are published on <a href="${R}flagged/">Flagged for Review</a> and do not block the site. Full row-by-row checks are on <a href="${R}verification/">Verification</a>.</p>
</section>
`,
});

pages.push({
  file: 'products/index.html',
  active: 'products/',
  title: 'Shop · all listings',
  description: 'All five supplied listings with observed ASINs, source links and open flags.',
  body: (R) => `
<h1 class="page-title">Shop · all listings</h1>
<p class="dek">Each row is one supplied link. The observed ASIN comes from the Amazon page the link led to. The intended ASIN is kept in its own column and is blank until the owner confirms it.</p>
${table(
  ['ID', 'Listing title (as written by seller)', 'Category', 'Observed ASIN (redirect)', 'Intended ASIN', 'Confirmed on', 'Outbound link', 'Price', 'Source', 'Flags'],
  products.map((p) => [
    H(`<span id="${p.id}">${esc(p.id)}</span>`),
    p.observed_title ? esc(p.observed_title) : H('<span class="tag tag-warn">Not identified (FLG-005)</span>'),
    esc(p.category),
    p.observed_redirect_asin ? p.observed_redirect_asin : H('<span class="tag tag-warn">None observed</span>'),
    H('<span class="tag tag-warn">Unverified · blank</span>'),
    p.confirmation_date,
    H(a(p.supplied_url, 'Supplied link ↗') + ` <span class="sponsor">${SPONSOR_LABEL}</span>`),
    H('<span class="tag tag-warn">Not confirmed</span>'),
    H(a(p.source_url, 'Listing page ↗')),
    flagList(p.flags, R),
  ]),
  { cls: 'wide' },
)}

<h2 class="section-head">Intended vs observed: kept separate</h2>
${table(
  ['ID', 'Supplied code', 'Code length', 'Intended ASIN (confirmed by owner)', 'Observed redirect ASIN', 'Official listing URL', 'Tag in observed URL'],
  products.map((p) => [
    p.id,
    p.supplied_code,
    String(p.supplied_code_length),
    H('<span class="tag tag-warn">Unverified · blank</span>'),
    p.observed_redirect_asin || H('<span class="tag tag-warn">None observed</span>'),
    p.official_listing_url ? H(a(p.official_listing_url, p.official_listing_url.replace('https://www.amazon.com', 'amazon.com'))) : H('<span class="tag tag-warn">None</span>'),
    p.tracking_tag_in_redirect,
  ]),
  { cls: 'wide' },
)}
<p class="muted">Short codes are 9 characters; Amazon ASINs are 10 characters (${flagRef('FLG-002', R)}). Tracking ID check is pending (${flagRef('FLG-009', R)}).</p>
`,
});

pages.push({
  file: 'categories/index.html',
  active: 'categories/',
  title: 'Categories',
  description: 'Listings grouped by category, with counts and links.',
  body: (R) => `
<h1 class="page-title">Categories</h1>
<div class="grid grid-cats">
  ${categoryPages
    .map(
      (c) => `<article class="card"><h3><a href="${R}categories/${catSlug(c)}.html">${esc(c)}</a></h3>
      <p>${products.filter((p) => p.category === c).length} listing(s) in the register.</p></article>`,
    )
    .join('')}
  <article class="card"><h3><a href="${R}products/#P03">Not yet classified</a></h3>
  <p>1 listing. The supplied link did not reach a product page (${flagRef('FLG-005', R)}).</p></article>
</div>
`,
});

const categoryNotes = {
  'Air fryers': (R) => `
<p>Three listings are air fryers by their Amazon category path. The titles state the following, as written by the seller (${flagRef('FLG-012', R)}):</p>
<ul class="linklist">
  <li><strong>P01</strong> · capacity “6 Quart”, format “Dual Basket”, “Dishwasher Safe” baskets.</li>
  <li><strong>P02</strong> · capacity “26QT”, format “French Door Multi-Function Air Fryer Toaster Oven”, “24 One-Touch Preset Options”.</li>
  <li><strong>P04</strong> · capacity “8 Qt”, “TurboFry 4-in-1”, “XL Nonstick Dishwasher-Safe Basket”.</li>
</ul>
<p class="muted">No prices, ratings or dimensions are confirmed. A comparison of value or performance would need them first (${flagRef('FLG-006', R)}).</p>`,
  'Kitchen thermometers': (R) => `
<p>One listing: a wireless meat thermometer with probes, observed in the Amazon category path “Thermometers & Timers › Meat”. There is nothing to compare yet.</p>
<p class="muted">Price, rating and availability are not confirmed (${flagRef('FLG-006', R)}).</p>`,
};

for (const c of categoryPages) {
  pages.push({
    file: `categories/${catSlug(c)}.html`,
    active: 'categories/',
    title: `${c} · categories`,
    description: `Listings in the ${c} category, with observed ASINs and sources.`,
    body: (R) => `
<p class="breadcrumb"><a href="${R}categories/">Categories</a> › ${esc(c)}</p>
<h1 class="page-title">${esc(c)}</h1>
<div class="prose">${(categoryNotes[c] || (() => ''))(R)}</div>
<div class="grid">${products.filter((p) => p.category === c).map((p) => card(p, R)).join('')}</div>
${table(
  ['ID', 'Observed ASIN', 'Brand (in title)', 'Capacity (in title)', 'Source'],
  products.filter((p) => p.category === c).map((p) => [
    p.id,
    p.observed_redirect_asin,
    p.brand_in_title,
    p.capacity_in_title || H('<span class="tag tag-warn">Not stated</span>'),
    H(a(p.source_url, p.source_url)),
  ]),
)}
`,
  });
}

pages.push({
  file: 'guides/index.html',
  active: 'guides/',
  title: 'Guides in preparation',
  description: 'Four question-shaped guide working titles, what each needs before drafting, and what is already known.',
  body: (R) => `
<h1 class="page-title">Guides in preparation</h1>
<p class="dek">These are working titles, chosen as buyer questions. They are not claims about popularity, search volume or product quality. None is published yet, and each needs verified data first (${flagRef('FLG-011', R)}).</p>
${guides
  .map(
    (g) => `<article class="card guide" id="${g.id}">
  <p class="card-cat">${esc(g.id)} · ${esc(g.status)}</p>
  <h2>${esc(g.working_title)}</h2>
  <p><strong>Buyer question:</strong> ${esc(g.buyer_question)}</p>
  <p><strong>Needed before drafting:</strong></p>
  <ul>${g.needs_before_drafting.map((n) => `<li>${esc(n)}</li>`).join('')}</ul>
  <p><strong>Already known (as stated in listing titles):</strong> ${esc(g.data_available)}</p>
</article>`,
  )
  .join('')}
<p class="muted">Publishing cadence is an open suggestion (SUG-04). Once a guide is drafted, it will be added to the sitemap.</p>
`,
});

pages.push({
  file: 'research/index.html',
  active: 'research/',
  title: 'Research · findings',
  description: 'Findings from the repository review and the listing checks, each with sources and flags.',
  body: (R) => `
<h1 class="page-title">Research · findings</h1>
<p class="dek">What the review found, with the source behind each finding. No conversion, revenue or ranking score is shown, because none has been measured.</p>
${table(
  ['ID', 'Finding', 'Evidence', 'Sources', 'Flag'],
  findings.map((f) => [f.id, f.finding, f.evidence, srcList(f.sources), f.flag ? flagList([f.flag], R) : H('<span class="muted">None</span>')]),
)}
<h2 class="section-head">What this means for the next step</h2>
<ul class="linklist">
  <li>The short links cannot be shown to carry the Tracking ID (F-03). Test them in the Associates account before scaling (${flagRef('FLG-003', R)}).</li>
  <li>Intended ASINs must come from the owner. The supplied codes cannot be turned into ASINs (${flagRef('FLG-002', R)}).</li>
  <li>Price data is the biggest gap for any comparison (${flagRef('FLG-006', R)}).</li>
</ul>
`,
});

pages.push({
  file: 'verification/index.html',
  active: 'verification/',
  title: 'Verification',
  description: 'Row-by-row verification of every field, with a source link on every row.',
  body: (R) => {
    const fields = [
      ['supplied_url', 'Supplied link', (p) => p.supplied_url, 'Observed (as supplied)'],
      ['intended_asin', 'Intended ASIN', (p) => p.intended_asin, 'Owner confirmation needed'],
      ['official_listing_url', 'Official listing URL', (p) => p.official_listing_url, 'Observed on redirect'],
      ['observed_redirect_asin', 'Observed redirect ASIN', (p) => p.observed_redirect_asin, 'Observed on redirect'],
      ['observed_title', 'Listing title', (p) => p.observed_title, 'Observed on listing page'],
      ['brand_in_title', 'Brand (in title)', (p) => p.brand_in_title, 'Observed on listing page'],
      ['capacity_in_title', 'Capacity (in title)', (p) => p.capacity_in_title, 'Observed on listing page'],
      ['category', 'Category', (p) => p.category, 'Derived from observed breadcrumb'],
      ['tracking_tag_in_redirect', 'Tracking tag in observed URL', (p) => p.tracking_tag_in_redirect, 'Observed (absent)'],
      ['price', 'Price', (p) => p.price, 'Not present in extracted text'],
      ['rating', 'Rating', (p) => p.rating, 'Not present in extracted text'],
      ['availability', 'Availability', (p) => p.availability, 'Not present in extracted text'],
    ];
    const rows = [];
    for (const p of products) {
      for (const [key, label, get, how] of fields) {
        const v = get(p);
        const has = v !== undefined && v !== null && String(v).trim() !== '' && !String(v).startsWith('Not present') && !String(v).startsWith('Not determinable');
        const isTagAbsent = key === 'tracking_tag_in_redirect';
        const status = isTagAbsent
          ? H(`<span class="tag tag-warn">${esc(v)}</span>`)
          : has
            ? H(`<span class="tag tag-ok">${esc(how)}</span>`)
            : H(`<span class="tag tag-warn">Unverified · blank</span>`);
        rows.push([
          p.id,
          label,
          isTagAbsent || has ? (typeof v === 'string' && /^https?:/.test(v) ? H(a(v, v)) : esc(v)) : H('<span class="muted">(blank)</span>'),
          status,
          H(a(p.source_url, p.source_url)),
          flagList(p.flags, R),
        ]);
      }
    }
    return `
<h1 class="page-title">Verification</h1>
<p class="dek">Rules applied. A value is shown only when it was read from a source page on ${esc('2026-11-20')}. If it could not be read, the cell is blank and marked unverified. Nothing is inferred. Every row links to its source.</p>
${table(['ID', 'Field', 'Value', 'Status', 'Source', 'Flags'], rows, { cls: 'wide' })}

<h2 class="section-head">Source register</h2>
<p class="muted">Each source was accessed on ${esc('2026-11-20')}. “Method” states what was actually checked, including partial reads.</p>
${table(
  ['ID', 'Source', 'Publisher', 'Method', 'Used for'],
  sources.map((s) => [H(`<span id="${s.id}">${esc(s.id)}</span>`), H(a(s.url, s.title)), s.publisher, s.method, s.used_for]),
  { cls: 'wide' },
)}
`;
  },
});

pages.push({
  file: 'questions/index.html',
  active: 'questions/',
  title: 'Questions',
  description: 'The questions that must be answered before the next decision, with what is known and what is missing.',
  body: (R) => `
<h1 class="page-title">Questions</h1>
<p class="dek">Each question states what is already known from sources, what is missing, and how to obtain it. A decision that depends on a missing answer should wait.</p>
${table(
  ['ID', 'Question', 'Known (with source)', 'Missing', 'How to obtain', 'Blocks'],
  questions.map((q) => [q.id, q.question, q.known, q.missing, q.how_to_obtain, q.blocks]),
  { cls: 'wide' },
)}
<h2 class="section-head">Flags that these questions address</h2>
<p>${flags.filter((f) => f.severity !== 'Low').map((f) => flagRef(f.id, R)).join(' ')}</p>
`,
});

pages.push({
  file: 'suggestions/index.html',
  active: 'suggestions/',
  title: 'Suggestions',
  description: 'Suggested paths for the site, each with options. Nothing changes until a path is chosen.',
  body: (R) => `
<h1 class="page-title">Suggestions</h1>
<p class="dek">Review each suggestion and pick an option. No change is implemented until a choice is recorded. Each option lists its trade-offs. Current build = the option the site uses today.</p>
<div class="prose"><p class="callout"><strong>How to choose:</strong> reply in chat with the suggestion ID and option letter (for example “SUG-02 A”), or record the decision in COORDINATION.md. Until then, the status stays “Awaiting owner choice”.</p></div>
${suggestions
  .map(
    (s) => `<article class="card" id="${s.id}">
  <p class="card-cat">${esc(s.id)} · ${esc(s.status)}</p>
  <h2>${esc(s.title)}</h2>
  <p>${esc(s.recommendation)}</p>
  <p class="muted"><strong>Why:</strong> ${esc(s.rationale)}</p>
  ${table(['Option', 'Choice', 'Upside', 'Downside'], s.options.map((o) => [o.id, o.label, o.pros, o.cons]))}
</article>`,
  )
  .join('')}
`,
});

pages.push({
  file: 'ledger/index.html',
  active: 'ledger/',
  title: 'Campaign ledger',
  description: 'Empty campaign ledger. Rows only from authorised first-party reports.',
  body: () => `
<h1 class="page-title">Campaign ledger</h1>
<p class="dek">${esc(ledger.description)}</p>
<p><strong>${ledger.rows.length} rows.</strong> No clicks, sessions or orders have been recorded. No conversion score or revenue forecast is shown.</p>
${table(ledger.columns, ledger.rows, { empty: 'No rows. Waiting for authorised first-party reports.' })}
`,
});

pages.push({
  file: 'flagged/index.html',
  active: 'flagged/',
  title: 'Flagged for Review',
  description: 'Irregularities and unverified items, with source links, published for owner review.',
  body: (R) => `
<h1 class="page-title">Flagged for Review</h1>
<p class="dek">Irregularities and unverified items found in the review. They are published here for your review and do not block the site. Each has a severity, sources and the action needed.</p>
${flags
  .map(
    (f) => `<article class="card flag sev-${esc(f.severity.toLowerCase())}" id="${f.id}">
  <p class="card-cat">${esc(f.id)} · Severity: ${esc(f.severity)}</p>
  <h2>${esc(f.title)}</h2>
  <p>${esc(f.detail)}</p>
  <p><strong>Action:</strong> ${esc(f.action)}</p>
  ${f.sources.length ? `<p><strong>Sources:</strong><br>${srcList(f.sources).html}</p>` : '<p class="muted">No external source applies.</p>'}
</article>`,
  )
  .join('')}
`,
});

pages.push({
  file: 'executive-summary/index.html',
  active: 'executive-summary/',
  title: 'Executive summary',
  description: 'Executive summary of the Affil3 review: what was found, what is verified, what is blocked, and what needs a decision.',
  body: (R) => `
<h1 class="page-title">Executive summary</h1>
<p class="dek">A short view of what this site contains, what is verified, what is not, and what needs your decision.</p>

<div class="prose">
<h2>What this is</h2>
<p>A product-led kitchen site built on five supplied Amazon Associates links. It lists each product with its observed ASIN, its source, and what has not been confirmed. The site has no traffic, click or sales data yet.</p>

<h2>Key numbers</h2>
<ul class="linklist">
  <li>${products.length} supplied links; ${resolvedCount} resolved to Amazon product pages; ${unresolvedCount} resolved to a checkpoint (${flagRef('FLG-005', R)}).</li>
  <li>0 of ${products.length} supplied codes is a 10-character ASIN (${flagRef('FLG-002', R)}).</li>
  <li>${products.filter((p) => p.observed_redirect_asin && !p.tracking_tag_in_redirect.startsWith('Not present')).length} of ${resolvedCount} observed product URLs contain the Tracking ID (${flagRef('FLG-003', R)}).</li>
  <li>${confirmedPriceCount} prices confirmed (${flagRef('FLG-006', R)}).</li>
  <li>${ledger.rows.length} campaign ledger rows. No conversion or revenue figure is claimed.</li>
</ul>

<h2>Verified</h2>
<ul class="linklist">
  <li>The Associates Operating Agreement requires the statement “${esc(DISCLOSURE)}” to be clearly and prominently displayed. It appears under the masthead of every page and in the footer (${srcLink('SRC-OA').html}).</li>
  <li>Google recommends rel="sponsored" for affiliate links. All outbound Amazon links carry it (${srcLink('SRC-GOOG-QOL').html}).</li>
  <li>16 CFR 255.5 covers disclosure of material connections (${srcLink('SRC-ECFR-255-5').html}). “Sponsored link” labels sit beside each product link.</li>
</ul>

<h2>Not verified (blocked on owner input)</h2>
<ul class="linklist">
  <li>Intended ASIN for each supplied link (Q-01).</li>
  <li>Whether the supplied short links comply with Special Link rules. The brief says this is unresolved (Q-02). No link has been declared invalid.</li>
  <li>The Tracking ID shopnow047c-20 in the Associates account (Q-03).</li>
  <li>Price, rating and availability for each listing (Q-04).</li>
  <li>Click counter, analytics endpoint and the five events. These need a hosting decision (SUG-03).</li>
</ul>

<h2>Decisions needed</h2>
<p>${suggestions.length} suggestions are awaiting your choice (${suggestions.map((s) => `<a href="${R}suggestions/#${s.id}">${s.id}</a>`).join(', ')}). Nothing has been changed on the basis of them.</p>

<h2>Irregularities for your review</h2>
<p>${flagCount} items are flagged, ${highFlags} at high severity. They are listed with sources on <a href="${R}flagged/">Flagged for Review</a>.</p>
</div>
`,
});

pages.push({
  file: '404.html',
  active: '',
  title: 'Page not found',
  description: 'This page does not exist.',
  body: (R) => `
<h1 class="page-title">Page not found</h1>
<p>The page you were looking for does not exist. <a href="${R}">Go to the front page</a>.</p>
`,
});

// ---------- write ----------
fs.rmSync(OUT, { recursive: true, force: true });
fs.mkdirSync(OUT, { recursive: true });
for (const p of pages) {
  const dest = path.join(OUT, p.file);
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  fs.writeFileSync(dest, page(p));
}
fs.mkdirSync(path.join(OUT, 'assets'), { recursive: true });
fs.copyFileSync(path.join(ASSETS, 'style.css'), path.join(OUT, 'assets/style.css'));
fs.writeFileSync(path.join(OUT, '.nojekyll'), '');

const htmlFiles = pages.map((p) => p.file).filter((f) => f !== '404.html');
fs.writeFileSync(
  path.join(OUT, 'sitemap.xml'),
  `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${htmlFiles
  .map((f) => `  <url><loc>${SITE_URL}${f.replace(/index\.html$/, '')}</loc><lastmod>2026-11-20</lastmod></url>`)
  .join('\n')}
</urlset>
`,
);
fs.writeFileSync(path.join(OUT, 'robots.txt'), `User-agent: *\nAllow: /\n\nSitemap: ${SITE_URL}sitemap.xml\n`);

console.log(`Built ${pages.length} pages into _site/`);
