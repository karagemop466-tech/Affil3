import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const projectRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const siteRoot = path.join(projectRoot, 'countertop-notes');
const sourceRoot = path.join(projectRoot, 'site-src');
const manifest = JSON.parse(await fs.readFile(path.join(sourceRoot, 'pages.json'), 'utf8'));
const productsDoc = JSON.parse(await fs.readFile(path.join(sourceRoot, 'data/products.json'), 'utf8'));
const eventsDoc = JSON.parse(await fs.readFile(path.join(sourceRoot, 'data/analytics-events.json'), 'utf8'));
const runtimeDoc = JSON.parse(await fs.readFile(path.join(sourceRoot, 'data/analytics-runtime.json'), 'utf8'));
const campaignDoc = JSON.parse(await fs.readFile(path.join(sourceRoot, 'data/campaign-ledger.json'), 'utf8'));
const sourcesDoc = JSON.parse(await fs.readFile(path.join(sourceRoot, 'data/sources.json'), 'utf8'));
const expectedDisclosure = 'As an Amazon Associate I earn from qualifying purchases.';
const errors = [];
let checks = 0;
const check = (condition, message) => {
  checks += 1;
  if (!condition) errors.push(message);
};
const fail = (message) => { throw new Error(message); };

async function existsInSite(relativePath) {
  const candidate = path.join(siteRoot, relativePath);
  try {
    const stat = await fs.stat(candidate);
    return stat.isFile();
  } catch {
    return false;
  }
}

function internalTarget(pagePath, href) {
  const clean = href.split('#')[0].split('?')[0];
  if (!clean || clean.startsWith('http:') || clean.startsWith('https:') || clean.startsWith('mailto:') || clean.startsWith('tel:') || clean.startsWith('data:') || clean.startsWith('javascript:')) return null;
  const currentDir = path.posix.dirname(pagePath);
  const normalized = path.posix.normalize(path.posix.join(currentDir, clean));
  const safe = normalized.replace(/^\.\//, '').replace(/^\//, '');
  if (safe === '.' || safe === '') return 'index.html';
  return safe.endsWith('/') ? `${safe}index.html` : safe;
}

function canonicalFor(page, baseUrl) {
  const suffix = page.path.replace(/\/index\.html$/, '/').replace(/^index\.html$/, '');
  return `${baseUrl.endsWith('/') ? baseUrl : `${baseUrl}/`}${suffix}`;
}

if (!(await existsInSite('index.html'))) fail('Build output is missing; run npm run build first.');

for (const page of manifest.pages) {
  const htmlPath = path.join(siteRoot, page.path);
  let html;
  try {
    html = await fs.readFile(htmlPath, 'utf8');
  } catch {
    errors.push(`Missing generated page: ${page.path}`);
    continue;
  }

  check(html.includes(expectedDisclosure), `${page.path}: required Associates disclosure text missing`);
  check(html.includes('class="disclosure-strip"'), `${page.path}: top disclosure strip missing`);
  check(html.includes('class="footer-disclosure"'), `${page.path}: repeated footer disclosure missing`);
  check(html.includes('class="nav-details"'), `${page.path}: single Research desk navigation group missing`);
  check(html.includes('href="') && !html.includes('{{'), `${page.path}: page contains unresolved template placeholder`);
  check((html.match(/<h1\b/g) || []).length === 1, `${page.path}: expected exactly one h1`);
  if (!page.indexable) check(html.includes('<meta name="robots" content="noindex,follow">'), `${page.path}: expected noindex,follow`);
  if (page.indexable) check(html.includes(`<link rel="canonical" href="${canonicalFor(page, JSON.parse(await fs.readFile(path.join(sourceRoot, 'pages.json'), 'utf8')).baseUrl)}">`), `${page.path}: canonical URL missing or incorrect`);

  for (const match of html.matchAll(/\bhref="([^"]+)"/g)) {
    const target = internalTarget(page.path, match[1]);
    if (target === null) continue;
    check(await existsInSite(target), `${page.path}: broken internal href "${match[1]}" -> ${target}`);
  }
  for (const match of html.matchAll(/\b(?:src|href)="([^"]+)"/g)) {
    const target = internalTarget(page.path, match[1]);
    if (target === null) continue;
    check(await existsInSite(target), `${page.path}: broken local asset "${match[1]}" -> ${target}`);
  }

  for (const row of html.matchAll(/<tr\b[^>]*>([\s\S]*?)<\/tr>/g)) {
    if (!/<td\b/i.test(row[1])) continue;
    check(/href="https:\/\//i.test(row[1]), `${page.path}: a data table row has no official source link`);
  }

  for (const anchor of html.matchAll(/<a\b([^>]*?)>/g)) {
    const attributes = anchor[1];
    const href = attributes.match(/\bhref="([^"]+)"/)?.[1] || '';
    const isProductLink = attributes.includes('data-product-link=') || /(?:link\.amazon\/|amazon\.com\/dp\/|amazon\.com\/checkpoint\/)/i.test(href);
    if (!isProductLink) continue;
    const rel = attributes.match(/\brel="([^"]+)"/)?.[1] || '';
    check(rel.split(/\s+/).includes('sponsored'), `${page.path}: outbound product link is missing rel="sponsored": ${href}`);
    check(rel.split(/\s+/).includes('noopener'), `${page.path}: outbound product link is missing noopener: ${href}`);
  }
}

check(productsDoc.products.length === 5, 'Expected exactly five submitted product records');
check(productsDoc.selectedTrackingId === 'shopnow047c-20', 'Owner-supplied selected Tracking ID was not preserved exactly');
check(manifest.pages.find((page) => page.path === 'shop/index.html')?.indexable === false, 'Shop queue must be noindex until it contains confirmed, decision-useful product content');
for (const product of productsDoc.products) {
  for (const field of ['intendedAsin', 'officialListingUrl', 'confirmationDate', 'confirmationSource']) {
    check(product[field] === '', `${product.id}: ${field} must remain blank until confirmed`);
  }
  check(Boolean(product.submittedUrl), `${product.id}: supplied URL missing`);
  check(Boolean(product.observedRedirectTarget), `${product.id}: observed target field missing`);
  check(Boolean(product.observedCategory), `${product.id}: observed Amazon breadcrumb category is missing`);
  check(product.observedRedirectTarget !== product.officialListingUrl, `${product.id}: observed destination was merged into official intended listing URL`);
  for (const field of ['price', 'availability', 'rating', 'reviewCount', 'competition', 'commissionPotential', 'trendEvidence']) {
    check(product[field] === '', `${product.id}: unverified product metric ${field} must remain blank`);
  }
}

const eventNames = eventsDoc.events.map((event) => event.name);
const expectedEvents = ['page_view', 'guide_open', 'site_search', 'outbound_click', 'reader_signup'];
check(JSON.stringify(eventNames) === JSON.stringify(expectedEvents), `Expected the five proposed event names in order: ${expectedEvents.join(', ')}`);
check(eventsDoc.specificationStatus?.startsWith('Proposal only:') === true, 'The underspecified five-event contract must remain explicitly labelled as a proposal');
check(runtimeDoc.enabled === false && runtimeDoc.endpoint === '' && runtimeDoc.summaryEndpoint === '', 'Public analytics runtime must remain disabled until an event contract and backend are reviewed and verified');
const shopQueue = manifest.pages.find((page) => page.path === 'shop/index.html');
const shopHtml = await fs.readFile(path.join(siteRoot, shopQueue.path), 'utf8');
const productRegisterHtml = await fs.readFile(path.join(siteRoot, 'desk/products.html'), 'utf8');
for (const category of [...new Set(productsDoc.products.map((product) => product.observedCategory))]) {
  const slug = `observed-${category.toLowerCase().replace(/[^a-z0-9]+/g, '-')}`;
  check(shopHtml.includes(`shop-${slug}`), `Shop queue lacks the observed category group ${category}`);
  check(productRegisterHtml.includes(`register-${slug}`), `Product register lacks the observed category table ${category}`);
}
check(campaignDoc.rows.length === 0, 'Campaign ledger must stay empty until authorized first-party data is available');
check(eventsDoc.privacyModel.includes('Do not send or persist IP addresses'), 'Privacy restrictions are missing from the event schema');

const sitemap = await fs.readFile(path.join(siteRoot, 'sitemap.xml'), 'utf8');
const feed = await fs.readFile(path.join(siteRoot, 'feed.xml'), 'utf8');
const robots = await fs.readFile(path.join(siteRoot, 'robots.txt'), 'utf8');
const indexable = manifest.pages.filter((page) => page.indexable && page.path !== '404.html');
const articles = manifest.pages.filter((page) => page.type === 'article' && page.publishedOn);
for (const page of indexable) check(sitemap.includes(`<loc>${canonicalFor(page, manifest.baseUrl)}</loc>`), `Sitemap omits indexable page ${page.path}`);
for (const page of manifest.pages.filter((page) => !page.indexable)) check(!sitemap.includes(`<loc>${canonicalFor(page, manifest.baseUrl)}</loc>`), `Sitemap includes noindex page ${page.path}`);
for (const page of articles) check(feed.includes(`<link>${canonicalFor(page, manifest.baseUrl)}</link>`), `RSS feed omits article ${page.path}`);
check(robots.includes(`Sitemap: ${manifest.baseUrl}sitemap.xml`), 'robots.txt sitemap URL does not match the configured canonical base URL');
check(sourcesDoc.sources.every((source) => /^https:\/\//.test(source.url)), 'Source register contains a non-HTTPS or missing source URL');

if (errors.length) {
  console.error(`Verification failed (${errors.length} issues across ${checks} checks):`);
  for (const error of errors) console.error(`- ${error}`);
  process.exitCode = 1;
} else {
  console.log(`Verified ${manifest.pages.length} pages, ${productsDoc.products.length} product records, ${eventsDoc.events.length} proposed event names, ${indexable.length} sitemap URLs, ${articles.length} RSS items across ${checks} checks.`);
}
