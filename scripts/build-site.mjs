import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const projectRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const sourceRoot = path.join(projectRoot, 'site-src');
const outputRoot = path.join(projectRoot, 'countertop-notes');
const manifest = JSON.parse(await fs.readFile(path.join(sourceRoot, 'pages.json'), 'utf8'));
const sourcesDoc = JSON.parse(await fs.readFile(path.join(sourceRoot, 'data/sources.json'), 'utf8'));
const productsDoc = JSON.parse(await fs.readFile(path.join(sourceRoot, 'data/products.json'), 'utf8'));
const questionsDoc = JSON.parse(await fs.readFile(path.join(sourceRoot, 'data/questions.json'), 'utf8'));
const suggestionsDoc = JSON.parse(await fs.readFile(path.join(sourceRoot, 'data/suggestions.json'), 'utf8'));
const requirementsDoc = JSON.parse(await fs.readFile(path.join(sourceRoot, 'data/requirements.json'), 'utf8'));
const eventsDoc = JSON.parse(await fs.readFile(path.join(sourceRoot, 'data/analytics-events.json'), 'utf8'));
const campaignDoc = JSON.parse(await fs.readFile(path.join(sourceRoot, 'data/campaign-ledger.json'), 'utf8'));
const flagsDoc = JSON.parse(await fs.readFile(path.join(sourceRoot, 'data/flags.json'), 'utf8'));
const sourceById = new Map(sourcesDoc.sources.map((source) => [source.id, source]));
const guideCount = manifest.pages.filter((page) => page.type === 'article' && page.publishedOn).length;
const observedCount = productsDoc.products.filter((product) => product.observedTargetTitle).length;
const runtimeConfig = JSON.parse(await fs.readFile(path.join(sourceRoot, 'data/analytics-runtime.json'), 'utf8'));
const intentCount = productsDoc.products.filter((product) => product.intendedAsin && product.officialListingUrl && product.confirmationDate && product.confirmationSource).length;
const priceCount = productsDoc.products.filter((product) => product.price).length;
const baseUrl = manifest.baseUrl.endsWith('/') ? manifest.baseUrl : `${manifest.baseUrl}/`;

const escapeHtml = (value = '') => String(value).replace(/[&<>"']/g, (character) => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
}[character]));
const escapeXml = (value = '') => String(value).replace(/[&<>"']/g, (character) => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&apos;'
}[character]));
const slugTitle = (page) => page.path.replace(/\/index\.html$/, '/').replace(/^index\.html$/, '');
const canonicalFor = (page) => `${baseUrl}${slugTitle(page)}`;
const rootRelativeFor = (page) => {
  const directory = path.posix.dirname(page.path);
  const depth = directory === '.' ? 0 : directory.split('/').filter(Boolean).length;
  return depth === 0 ? './' : '../'.repeat(depth);
};
const sourceHref = (id) => sourceById.get(id)?.url ?? '';
const isProductSource = (id) => id.startsWith('SRC-P');

function linkToSource(id, label = '') {
  const source = sourceById.get(id);
  if (!source) return `<span class="missing-source">Missing source: ${escapeHtml(id)}</span>`;
  const rel = isProductSource(id) ? 'sponsored nofollow noopener noreferrer' : 'nofollow noopener noreferrer';
  const safeLabel = label || `${id} · ${source.publisher}`;
  return `<a href="${escapeHtml(source.url)}" target="_blank" rel="${rel}">${escapeHtml(safeLabel)}</a>`;
}

function renderSourceLinks(ids = []) {
  const unique = [...new Set(ids)];
  return `<div class="source-links">${unique.map((id) => linkToSource(id)).join('')}</div>`;
}

function blankCell(label = 'Not verified; field left blank') {
  return `<td><span aria-label="${escapeHtml(label)}">&nbsp;</span><small class="table-note">Not verified · blank</small></td>`;
}

function inspectionLink(url, label, productId) {
  if (!url) return '';
  return `<a class="product-link" href="${escapeHtml(url)}" target="_blank" rel="sponsored nofollow noopener noreferrer" data-product-link="${escapeHtml(productId)}">${escapeHtml(label)}</a>`;
}

function renderProductCard(product) {
  const observedSource = sourceById.get(product.observationSourceId);
  const recordNumber = product.id.match(/(\d+)$/)?.[1] || '—';
  const observedName = product.observedTargetTitle || 'No product detail page resolved in this check';
  const observedTarget = product.observedRedirectTarget;
  const observedLink = product.observedTargetTitle && observedTarget
    ? inspectionLink(observedTarget, 'Inspect observed Amazon page', product.id)
    : '';
  const suppliedLink = inspectionLink(product.submittedUrl, 'Inspect submitted link', product.id);
  const targetPath = observedTarget.replace(/^https:\/\//, '');
  const statusClass = product.observedTargetTitle ? 'neutral' : 'alert';
  return `<article class="product-card">
    <p class="record-id">Record ${escapeHtml(recordNumber)} · ${escapeHtml(product.id)}</p>
    <div class="status-line"><span class="status-pill ${statusClass}">Intent unconfirmed</span></div>
    <h3 class="product-title">${escapeHtml(observedName)}</h3>
    <p class="table-note">Observed title and breadcrumb only. Neither confirms the product or category the owner intended.</p>
    <dl>
      <dt>Observed breadcrumb category</dt><dd>${escapeHtml(product.observedCategory || 'Not captured')}</dd>
      <dt>Submitted path</dt><dd><code>${escapeHtml(product.submittedPathToken)}</code></dd>
      <dt>Observed target path</dt><dd>${escapeHtml(targetPath)}</dd>
      <dt>Intended ASIN</dt><dd>Not confirmed · left blank</dd>
      <dt>Official intended listing</dt><dd>Not confirmed · left blank</dd>
      <dt>Price / availability</dt><dd>Not verified · left blank</dd>
    </dl>
    <div class="product-links">${suppliedLink}${observedLink}</div>
    <p class="table-note">Inspection only—not a validated Special Link or a buy button. Source: ${observedSource ? linkToSource(product.observationSourceId, `${product.observationSourceId} · Amazon observation`) : 'submitted link only'}.</p>
  </article>`;
}

function renderProductRow(product) {
  const observedLink = product.observedTargetTitle
    ? `<a href="${escapeHtml(product.observedRedirectTarget)}" target="_blank" rel="sponsored nofollow noopener noreferrer" data-product-link="${escapeHtml(product.id)}">Inspect observed Amazon page</a><br><small>${escapeHtml(product.observedTargetTitle)}</small>`
    : `<span>No product detail page surfaced in this check.</span>`;
  const suppliedLink = `<a href="${escapeHtml(product.submittedUrl)}" target="_blank" rel="sponsored nofollow noopener noreferrer" data-product-link="${escapeHtml(product.id)}">Inspect supplied URL (review only)</a><br><code>${escapeHtml(product.submittedPathToken)}</code>`;
  const sourceIds = [product.observationSourceId, 'SRC-02', 'SRC-03', 'SRC-12'];
  const metrics = ['price', 'availability', 'rating', 'reviewCount', 'competition', 'commissionPotential', 'trendEvidence']
    .map((field) => `<span><strong>${escapeHtml(fieldLabel(field))}:</strong> — <small>unverified</small></span>`)
    .join('<br>');
  return `<tr>
    <td><strong>${escapeHtml(product.id)}</strong><br>${suppliedLink}</td>
    <td>${observedLink}<br><small>Observed ${escapeHtml(product.observedOn)}; not an intent confirmation.</small></td>
    <td>${escapeHtml(product.observedCategory || 'Not captured')}<br><small>Observed Amazon breadcrumb only.</small></td>
    ${blankCell('Intended ASIN unverified; field left blank')}
    ${blankCell('Official intended listing URL unverified; field left blank')}
    ${blankCell('Confirmation date and source unverified; fields left blank')}
    <td>${metrics}</td>
    <td><span class="status-pill alert">${escapeHtml(product.status)}</span></td>
    <td>${renderSourceLinks(sourceIds)}</td>
  </tr>`;
}

function groupProductsByObservedCategory() {
  const groups = new Map();
  for (const product of productsDoc.products) {
    const category = product.observedCategory || 'Category not captured';
    if (!groups.has(category)) groups.set(category, []);
    groups.get(category).push(product);
  }
  return [...groups.entries()];
}

function categoryId(category) {
  return `observed-${category.toLowerCase().replace(/[^a-z0-9]+/g, '-')}`;
}

function renderProductGroups() {
  return groupProductsByObservedCategory().map(([category, products]) => `<section class="category-group" aria-labelledby="shop-${categoryId(category)}">
    <div class="section-heading"><div><p class="kicker">Observed Amazon breadcrumb · not intended category</p><h2 id="shop-${categoryId(category)}">${escapeHtml(category)}</h2><p class="table-note">Category label surfaced on the observed pages only; the owner has not confirmed this product grouping.</p></div></div>
    <div class="product-grid">${products.map(renderProductCard).join('')}</div>
  </section>`).join('\n');
}

function renderProductTableGroups() {
  const headers = ['Record & submitted link', 'Observed page (normalized target)', 'Observed Amazon category', 'Intended ASIN', 'Official intended listing URL', 'Confirmation date / source', 'Unverified metrics', 'Status', 'Official source links'];
  return groupProductsByObservedCategory().map(([category, products]) => `<section class="category-group" aria-labelledby="register-${categoryId(category)}">
    <div class="section-heading"><div><p class="kicker">Observed Amazon breadcrumb · not intended category</p><h2 id="register-${categoryId(category)}">${escapeHtml(category)}</h2></div></div>
    <div class="table-wrap"><table>
      <caption>Product-intent and evidence records grouped by observed Amazon page category · checked 20 November 2026</caption>
      <thead><tr>${headers.map((header) => `<th scope="col">${escapeHtml(header)}</th>`).join('')}</tr></thead>
      <tbody>${products.map(renderProductRow).join('\n')}</tbody>
    </table></div>
  </section>`).join('\n');
}

function fieldLabel(field) {
  return ({
    price: 'Price', availability: 'Availability', rating: 'Rating', reviewCount: 'Review count',
    competition: 'Competition', commissionPotential: 'Commission potential', trendEvidence: 'Trend evidence'
  })[field] || field;
}

function statusPill(status) {
  const lower = status.toLowerCase();
  const statusClass = lower.includes('blocked') || lower.includes('not-deployed') || lower.includes('unverified') || lower.includes('pending')
    ? 'alert'
    : lower.includes('done')
      ? 'good'
      : 'neutral';
  return `<span class="status-pill ${statusClass}">${escapeHtml(status.replaceAll('-', ' '))}</span>`;
}

function renderQuestionRows() {
  return questionsDoc.questions.map((item) => `<tr>
    <td><strong>${escapeHtml(item.id)}</strong><br>${escapeHtml(item.question)}</td>
    <td>${escapeHtml(item.known)}</td>
    <td>${escapeHtml(item.unknown)}</td>
    <td>${escapeHtml(item.howToFind)}</td>
    <td>${escapeHtml(item.blocks)}</td>
    <td>${renderSourceLinks(item.sourceIds)}</td>
  </tr>`).join('\n');
}

function renderSuggestionRows() {
  return suggestionsDoc.paths.map((item) => `<tr>
    <td><strong>${escapeHtml(item.label)}</strong></td>
    <td><strong>${escapeHtml(item.title)}</strong><br>${escapeHtml(item.description)}</td>
    <td>${escapeHtml(item.tradeoff)}</td>
    <td>${statusPill(item.status)}</td>
    <td>${renderSourceLinks(item.sourceIds)}</td>
  </tr>`).join('\n');
}

function renderSuggestionOptions() {
  return suggestionsDoc.paths.map((item) => {
    const checked = item.id === suggestionsDoc.recommendedPath ? ' checked' : '';
    const recommended = item.id === suggestionsDoc.recommendedPath ? ' <span class="status-pill good">Starting recommendation</span>' : '';
    return `<label class="choice-option"><input type="radio" name="path" value="${escapeHtml(item.id)}"${checked}><span><strong>${escapeHtml(item.title)}${recommended}</strong><span>${escapeHtml(item.tradeoff)}</span></span></label>`;
  }).join('\n');
}

function renderRequirementRows() {
  return requirementsDoc.requirements.map((item) => `<tr>
    <td><code>${escapeHtml(item.id)}</code></td>
    <td><strong>${escapeHtml(item.title)}</strong></td>
    <td>${statusPill(item.status)}</td>
    <td>${escapeHtml(item.implementation)}</td>
    <td>${renderSourceLinks(item.evidenceSourceIds)}</td>
  </tr>`).join('\n');
}

function renderSourceItems() {
  return sourcesDoc.sources.map((source) => `<article class="source-item">
    <div class="source-id">${escapeHtml(source.id)}</div>
    <div><h3><a href="${escapeHtml(source.url)}" target="_blank" rel="${isProductSource(source.id) ? 'sponsored nofollow noopener noreferrer' : 'nofollow noopener noreferrer'}">${escapeHtml(source.title)}</a></h3><p>${escapeHtml(source.publisher)}${source.pageUpdated ? ` · Page updated ${escapeHtml(source.pageUpdated)}` : ''}. ${escapeHtml(source.verifiedNotes)}</p></div>
    <time class="source-checked" datetime="${escapeHtml(source.checkedOn)}">Checked ${escapeHtml(source.checkedOn)}</time>
  </article>`).join('\n');
}

function renderFlagItems() {
  return flagsDoc.flags.map((flag) => `<article class="card">
    <div class="status-line"><span class="source-id">${escapeHtml(flag.id)}</span>${statusPill(flag.status)}</div>
    <h2>${escapeHtml(flag.title)}</h2>
    <p><strong>Finding:</strong> ${escapeHtml(flag.finding)}</p>
    <p><strong>Irregularity / limit:</strong> ${escapeHtml(flag.irregularity)}</p>
    <p><strong>Next discovery step:</strong> ${escapeHtml(flag.nextStep)}</p>
    <p><strong>Official source links:</strong></p>${renderSourceLinks(flag.sourceIds)}
  </article>`).join('\n');
}

function renderEventRows() {
  return eventsDoc.events.map((event) => {
    const sourceIds = event.name === 'reader_signup'
      ? ['SRC-10', 'SRC-11']
      : event.name === 'outbound_click'
        ? ['SRC-10', 'SRC-12']
        : event.name === 'page_view' || event.name === 'guide_open'
          ? ['SRC-10']
          : ['SRC-09', 'SRC-10'];
    return `<tr>
      <td><code>${escapeHtml(event.name)}</code></td>
      <td>${escapeHtml(event.purpose)}</td>
      <td>${event.allowedFields.map((field) => `<code>${escapeHtml(field)}</code>`).join('<br>')}</td>
      <td>${escapeHtml(eventsDoc.privacyModel)}</td>
      <td>${renderSourceLinks(sourceIds)}</td>
    </tr>`;
  }).join('\n');
}

function renderCampaignRows() {
  if (campaignDoc.rows.length === 0) {
    return `<tr><td colspan="7">No authorized first-party report rows. The ledger is intentionally empty. No metric is inferred. <a href="${escapeHtml(sourceHref('SRC-05'))}" target="_blank" rel="nofollow noopener noreferrer">Amazon report documentation</a></td></tr>`;
  }
  return campaignDoc.rows.map((row) => `<tr>${campaignDoc.columns.map((column) => `<td>${escapeHtml(row[column] ?? '')}</td>`).join('')}<td>${linkToSource('SRC-05')}</td></tr>`).join('\n');
}

function renderNavigation(root, activeSection) {
  const active = (section) => activeSection === section ? ' aria-current="page"' : '';
  return `<header class="site-header">
    <div class="masthead">
      <a class="brand" href="${root}" aria-label="Countertop Notes home"><span class="brand-mark" aria-hidden="true">CN</span><span class="brand-copy"><span class="brand-name">Countertop Notes</span><span class="brand-line">Kitchen choices, made clearer</span></span></a>
      <nav class="primary-nav" aria-label="Main navigation">
        <a href="${root}shop/"${active('shop')}>Shop</a>
        <a href="${root}guides/"${active('guides')}>Buying guides</a>
        <a href="${root}about/"${active('about')}>Our approach</a>
        <details class="nav-details"><summary>Research desk</summary><div class="nav-panel">
          <span class="nav-panel-label">Research & decisions</span>
          <a href="${root}desk/">Executive summary</a>
          <a href="${root}desk/products.html">Product-intent register</a>
          <a href="${root}desk/suggestions.html">Suggestions & paths</a>
          <a href="${root}desk/questions.html">Open questions</a>
          <a href="${root}desk/requirements.html">Requirements & status</a>
          <span class="nav-panel-label">Measurement & review</span>
          <a href="${root}desk/measurement.html">Analytics & campaign ledger</a>
          <a href="${root}desk/workflow.html">Automation & compliance gate</a>
          <a href="${root}desk/sources.html">Source register</a>
          <a href="${root}flagged/">Flagged for Review</a>
        </div></details>
      </nav>
    </div>
    <div class="disclosure-strip"><div class="disclosure-inner"><p><strong>Affiliate disclosure</strong> “I get commissions for purchases made through links in this post.” As an Amazon Associate I earn from qualifying purchases.</p><a href="${root}about/#affiliate">How this works</a></div></div>
  </header>`;
}

function renderFooter(root) {
  return `<footer class="site-footer">
    <div class="footer-inner">
      <div class="footer-top">
        <div class="footer-brand"><a class="brand" href="${root}"><span class="brand-mark" aria-hidden="true">CN</span><span class="brand-copy"><span class="brand-name">Countertop Notes</span><span class="brand-line">Kitchen choices, made clearer</span></span></a><p>A publication-style guide to thoughtful kitchen purchases. Clear questions, careful sources, and no invented product claims.</p></div>
        <div class="footer-groups">
          <section class="footer-group" aria-labelledby="footer-read"><h2 id="footer-read">Read</h2><ul><li><a href="${root}shop/">Shop queue</a></li><li><a href="${root}guides/">Buying guides</a></li><li><a href="${root}about/">About the publication</a></li><li><a href="${root}privacy/">Privacy</a></li><li><a href="${root}feed.xml">RSS feed</a></li></ul></section>
          <section class="footer-group" aria-labelledby="footer-desk-one"><h2 id="footer-desk-one">Research desk</h2><ul><li><a href="${root}desk/">Executive summary</a></li><li><a href="${root}desk/products.html">Product register</a></li><li><a href="${root}desk/suggestions.html">Suggestions</a></li><li><a href="${root}desk/questions.html">Open questions</a></li><li><a href="${root}desk/requirements.html">Requirements</a></li></ul></section>
          <section class="footer-group" aria-labelledby="footer-desk-two"><h2 id="footer-desk-two">Measurement & checks</h2><ul><li><a href="${root}desk/measurement.html">Measurement ledger</a></li><li><a href="${root}desk/workflow.html">Automation gate</a></li><li><a href="${root}desk/sources.html">Source register</a></li><li><a href="${root}flagged/">Flagged for Review</a></li><li><a href="${root}sitemap.xml">Sitemap</a></li></ul></section>
        </div>
      </div>
      <div class="footer-disclosure"><strong>Affiliate disclosure:</strong> “I get commissions for purchases made through links in this post.” As an Amazon Associate I earn from qualifying purchases.</div>
      <div class="footer-bottom"><span>© 2026 Countertop Notes · Editorial frameworks, not product tests.</span><span><a href="${root}privacy/">Privacy</a> · <a href="${root}feed.xml">RSS</a> · <a href="${root}flagged/">Open review flags</a></span></div>
    </div>
  </footer>`;
}

function layout(page, body) {
  const root = rootRelativeFor(page);
  const canonical = canonicalFor(page);
  const robots = page.indexable ? 'index,follow' : 'noindex,follow';
  const type = page.type === 'article' ? 'article' : 'website';
  const author = page.type === 'article' ? '<meta name="author" content="Countertop Notes Editorial Desk">' : '';
  const published = page.publishedOn ? `<meta property="article:published_time" content="${escapeHtml(page.publishedOn)}">` : '';
  const bodyWithRoot = body.replaceAll('{{root}}', root);
  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#19332d">
  <meta name="site-root" content="${root}">
  <meta name="robots" content="${robots}">
  <meta name="description" content="${escapeHtml(page.description)}">
  ${author}
  ${published}
  <title>${escapeHtml(page.title)}</title>
  <link rel="canonical" href="${escapeHtml(canonical)}">
  <link rel="alternate" type="application/rss+xml" title="Countertop Notes RSS" href="${root}feed.xml">
  <link rel="icon" href="${root}assets/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="${root}assets/site.css">
  <meta property="og:type" content="${type}">
  <meta property="og:site_name" content="Countertop Notes">
  <meta property="og:title" content="${escapeHtml(page.title)}">
  <meta property="og:description" content="${escapeHtml(page.description)}">
  <meta property="og:url" content="${escapeHtml(canonical)}">
  <meta property="og:image" content="${baseUrl}assets/hero.svg">
</head>
<body data-page="${escapeHtml(page.path)}" data-page-type="${escapeHtml(page.type)}">
  <a class="skip-link" href="#main-content">Skip to content</a>
  ${renderNavigation(root, page.section)}
  ${bodyWithRoot}
  ${renderFooter(root)}
  <script src="${root}assets/analytics.js" defer></script>
  <script src="${root}assets/site.js" defer></script>
  ${page.path === 'guides/index.html' ? `<script src="${root}assets/search.js" defer></script>` : ''}
  ${page.path === 'desk/measurement.html' ? `<script src="${root}assets/measurement.js" defer></script>` : ''}
</body>
</html>
`;
}

function replaceDataTokens(body, page) {
  const replacements = {
    PRODUCT_COUNT: productsDoc.products.length,
    INTENT_COUNT: intentCount,
    OBSERVED_COUNT: observedCount,
    PRICE_COUNT: priceCount,
    GUIDE_COUNT: guideCount,
    CAMPAIGN_ROW_COUNT: campaignDoc.rows.length,
    PUBLIC_EVENTS_STATUS: runtimeConfig.enabled === true ? 'Enabled' : 'Disabled',
    PRODUCT_GROUPS: renderProductGroups(),
    PRODUCT_TABLE_GROUPS: renderProductTableGroups(),
    QUESTION_TABLE_ROWS: renderQuestionRows(),
    SUGGESTION_TABLE_ROWS: renderSuggestionRows(),
    SUGGESTION_OPTIONS: renderSuggestionOptions(),
    REQUIREMENT_TABLE_ROWS: renderRequirementRows(),
    SOURCE_ITEMS: renderSourceItems(),
    FLAG_ITEMS: renderFlagItems(),
    EVENT_TABLE_ROWS: renderEventRows(),
    CAMPAIGN_TABLE_ROWS: renderCampaignRows()
  };
  let output = body;
  for (const [key, value] of Object.entries(replacements)) {
    output = output.replaceAll(`{{${key}}}`, String(value));
  }
  output = output.replaceAll('{{root}}', rootRelativeFor(page));
  const unresolved = output.match(/\{\{[A-Z_]+\}\}/g);
  if (unresolved) throw new Error(`Unresolved page tokens in ${page.path}: ${[...new Set(unresolved)].join(', ')}`);
  return output;
}

await fs.rm(outputRoot, { recursive: true, force: true });
await fs.mkdir(outputRoot, { recursive: true });
await fs.cp(path.join(sourceRoot, 'assets'), path.join(outputRoot, 'assets'), { recursive: true });
await fs.cp(path.join(sourceRoot, 'data'), path.join(outputRoot, 'data'), { recursive: true });

for (const page of manifest.pages) {
  const body = await fs.readFile(path.join(sourceRoot, 'pages', page.body), 'utf8');
  const hydrated = replaceDataTokens(body, page);
  const outputPath = path.join(outputRoot, page.path);
  await fs.mkdir(path.dirname(outputPath), { recursive: true });
  await fs.writeFile(outputPath, layout(page, hydrated));
}

const sitemapPages = manifest.pages.filter((page) => page.indexable && page.path !== '404.html');
const sitemapXml = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${sitemapPages.map((page) => `  <url><loc>${escapeXml(canonicalFor(page))}</loc><lastmod>${escapeXml(page.publishedOn || '2026-11-20')}</lastmod></url>`).join('\n')}\n</urlset>\n`;
await fs.writeFile(path.join(outputRoot, 'sitemap.xml'), sitemapXml);

const feedPages = manifest.pages.filter((page) => page.type === 'article' && page.publishedOn);
const feedXml = `<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:dc="http://purl.org/dc/elements/1.1/">\n  <channel>\n    <title>${escapeXml(manifest.siteName)}</title>\n    <link>${escapeXml(baseUrl)}</link>\n    <description>Question-led kitchen buying guides, with sources and no unsupported product claims.</description>\n    <language>en-us</language>\n    <lastBuildDate>${escapeXml(new Date().toUTCString())}</lastBuildDate>\n${feedPages.map((page) => `    <item>\n      <title>${escapeXml(page.title)}</title>\n      <link>${escapeXml(canonicalFor(page))}</link>\n      <guid isPermaLink="true">${escapeXml(canonicalFor(page))}</guid>\n      <description>${escapeXml(page.description)}</description>\n      <dc:creator>Countertop Notes Editorial Desk</dc:creator>\n      <pubDate>${escapeXml(new Date(`${page.publishedOn}T00:00:00Z`).toUTCString())}</pubDate>\n    </item>`).join('\n')}\n  </channel>\n</rss>\n`;
await fs.writeFile(path.join(outputRoot, 'feed.xml'), feedXml);
await fs.writeFile(path.join(outputRoot, 'robots.txt'), `User-agent: *\nAllow: /\nSitemap: ${baseUrl}sitemap.xml\n`);
await fs.writeFile(path.join(outputRoot, '.nojekyll'), '');

console.log(`Built ${manifest.pages.length} static pages, ${guideCount} guide-feed items, ${sitemapPages.length} sitemap URLs into ${path.relative(projectRoot, outputRoot)}.`);
