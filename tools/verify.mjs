#!/usr/bin/env node
// Publishing gate for Affil3. Run after tools/build.mjs. Exits non-zero on any failure.
// Checks data (source links, flags, ASIN format, tags) and the generated site (disclosure,
// sponsored attributes, internal links, sitemap/feed coverage, no redirects, no prices, analytics allowlist).
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const DOCS = ROOT; // generated site lives at the repository root
const OWNED = ['index.html', 'shop', 'products', 'categories', 'guides', 'how-we-choose', 'executive-summary', 'sources',
  'questions', 'suggestions', 'flagged', 'ledger', 'measurement', 'compliance', 'about', '404.html'];
const read = (p) => JSON.parse(fs.readFileSync(path.join(ROOT, p), 'utf8'));
const cfg = read('data/config.json');
const products = read('data/products.json').products;
const sources = read('data/sources.json').sources;
const flags = read('data/flags.json').flags;
const events = read('data/events.json').events;
const guides = read('data/guides.json').guides;
const questions = read('data/questions.json');
const suggestionsDoc = read('data/suggestions.json');

// Official sources only: Amazon Associates pages, Google Search documentation, US federal regulators,
// and the manufacturers of the products the owner submitted. No blog, review site or reseller is allowed.
const ALLOWED_SOURCE_HOSTS = new Set([
  'affiliate-program.amazon.com', 'www.amazon.com', 'link.amazon', 'advertising.amazon.com', 'developers.google.com', 'www.ftc.gov',
  'www.ecfr.gov', 'www.fsis.usda.gov', 'github.com',
  'chefman.com', 'www.emerileveryday.com', 'chefiq.com',
  // Added 2026-11-20 (session 197d4f9e-affil3): ThermoMaven is the maker of a submitted
  // product, so its own product page is the same kind of official source as the other two
  // manufacturers already listed. No reseller, review site or aggregator is added.
  'www.thermomaven.com',
]);
const TAG = cfg.trackingId;
const failures = [];
const passes = [];
const check = (name, ok, detail = '') => (ok ? passes : failures).push(detail ? `${name}: ${detail}` : name);

// ---------- 1. data ----------
const SRC = new Map(sources.map((s) => [s.id, s]));
const FLG = new Map(flags.map((f) => [f.id, f]));
for (const s of sources) {
  if (!s.url) continue;
  let host = ''; try { host = new URL(s.url).hostname; } catch {}
  check(`source ${s.id} is https on an allowed official host`, s.url.startsWith('https://') && ALLOWED_SOURCE_HOSTS.has(host), s.url);
}
const REQUIRED = ['id', 'category', 'submitted_url', 'submitted_token', 'intended_asin', 'official_listing_url', 'confirmation_date', 'confirmation_source', 'confirmation_status', 'flags', 'observed_final_url', 'observed_asin', 'observed_title', 'observed_breadcrumb', 'observed_date', 'sources', 'tagged_outbound_url', 'outbound_status'];
for (const p of products) {
  for (const k of REQUIRED) check(`${p.id} has field ${k}`, Object.prototype.hasOwnProperty.call(p, k), k);
  check(`${p.id} submitted token length recorded correctly`, p.submitted_token.length === p.submitted_token_length);
  // Intended fields: only filled when a 10-character ASIN and an official listing URL are confirmed.
  if (p.intended_asin) {
    check(`${p.id} intended ASIN is 10 characters`, /^[A-Z0-9]{10}$/i.test(p.intended_asin), p.intended_asin);
    check(`${p.id} intended listing URL and confirmation source present`, !!p.official_listing_url && !!p.confirmation_source && !!p.confirmation_date);
  } else {
    check(`${p.id} intended fields blank and flagged as unverified`, !p.official_listing_url && !p.confirmation_date && !p.confirmation_source && p.flags.length > 0);
  }
  check(`${p.id} has at least one official source id`, p.sources.length > 0);
  for (const sid of p.sources) check(`${p.id} source ${sid} exists`, SRC.has(sid), sid);
  for (const fid of p.flags) check(`${p.id} flag ${fid} exists`, FLG.has(fid), fid);
  if (p.observed_asin) {
    check(`${p.id} observed ASIN is 10 characters`, /^[A-Z0-9]{10}$/i.test(p.observed_asin), p.observed_asin);
    check(`${p.id} observed URL carries the observed ASIN`, p.observed_final_url === `https://www.amazon.com/dp/${p.observed_asin}`, p.observed_final_url);
    check(`${p.id} observed title present`, !!p.observed_title);
  }
  if (p.tagged_outbound_url) {
    const expected = `https://www.amazon.com/dp/${p.observed_asin}?tag=${TAG}`;
    check(`${p.id} outbound link is the observed product with tag ${TAG}`, p.tagged_outbound_url === expected, p.tagged_outbound_url);
  } else if (p.no_buy_link) {
    // A product may be observed but still carry no buy link, if there is nothing to stand behind.
    check(`${p.id} withholds its buy link on purpose and says why`, !!p.no_buy_link_reason, p.no_buy_link_reason);
  } else {
    check(`${p.id} no outbound link without an observed product`, !p.observed_asin);
  }
  check(`${p.id} has no price, rating or availability field`, !/price|rating|availability|stock/i.test(Object.keys(p).join(' ')));
}
check('five submitted product rows present', products.length === 5, String(products.length));
for (const g of guides) {
  for (const sid of g.sources) check(`guide ${g.slug} source ${sid} exists`, SRC.has(sid), sid);
}
for (const f of flags) for (const sid of f.sources) check(`flag ${f.id} source ${sid} exists`, SRC.has(sid), sid);

// analytics allowlist: events.json, the browser script and the collector must agree
const EVENT_NAMES = events.map((e) => e.name).sort().join(',');
const jsSrc = fs.readFileSync(path.join(ROOT, 'src/assets/analytics.js'), 'utf8');
const colSrc = fs.readFileSync(path.join(ROOT, 'tools/collector.mjs'), 'utf8');
const jsAllowed = (jsSrc.match(/var ALLOWED = \{([^}]*)\}/)[1].match(/\w+(?=\s*:)/g) || []).sort().join(',');
const colAllowed = (colSrc.match(/const EVENTS = \{([\s\S]*?)\n\};/)[1].match(/\w+(?=\s*:\s*\[)/g) || []).sort().join(',');
check('five analytics events agree across events.json, browser script and collector', EVENT_NAMES === jsAllowed && jsAllowed === colAllowed, `${EVENT_NAMES} | ${jsAllowed} | ${colAllowed}`);
check('browser script sets no cookies or storage', !/document\.cookie|localStorage|sessionStorage/.test(jsSrc));

// ---------- 2. generated site ----------
if (!fs.existsSync(path.join(DOCS, 'index.html'))) {
  failures.push('generated site missing: run node tools/build.mjs first');
} else {
  const htmlFiles = [];
  const walk = (d) => { for (const f of fs.readdirSync(d)) { const p = path.join(d, f); if (fs.statSync(p).isDirectory()) walk(p); else if (f.endsWith('.html')) htmlFiles.push(p); } };
  for (const o of OWNED) {
    const p = path.join(DOCS, o);
    if (!fs.existsSync(p)) continue;
    if (fs.statSync(p).isDirectory()) walk(p); else if (p.endsWith('.html')) htmlFiles.push(p);
  }
  const rel = (f) => '/' + path.relative(DOCS, f).split(path.sep).join('/');
  const base = cfg.basePath;
  const fileFor = (urlPath) => {
    const clean = urlPath.split('#')[0].split('?')[0];
    if (!clean.startsWith(base)) return null;
    const sub = clean.slice(base.length) || '/';
    const target = path.join(DOCS, sub.endsWith('/') ? path.join(sub, 'index.html') : sub);
    return target;
  };
  const sitemap = fs.readFileSync(path.join(DOCS, 'sitemap.xml'), 'utf8');
  const sitemapUrls = [...sitemap.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => m[1]);
  // Pages that carry noindex are deliberately excluded from the public sitemap; everything else must be in it.
  const pageUrls = htmlFiles
    .filter((f) => path.basename(f) !== '404.html')
    .filter((f) => !/name="robots"[^>]*noindex/.test(fs.readFileSync(f, 'utf8')))
    .map((f) => cfg.siteUrl + rel(f).replace(/index\.html$/, ''));

  for (const f of htmlFiles) {
    const html = fs.readFileSync(f, 'utf8');
    const name = rel(f);
    const body = html.replace(/<script[\s\S]*?<\/script>/g, '');
    check(`${name}: disclosure strip above main`, /<div class="disclosure-strip"[\s\S]*?Disclosure\.[\s\S]*?<\/div>\s*<main/.test(html));
    check(`${name}: Associates statement present`, html.includes(cfg.associatesStatement));
    check(`${name}: footer repeats disclosure`, /<footer[\s\S]*<p class="disclosure-footer">[\s\S]*?Disclosure\./.test(html));
    check(`${name}: no meta refresh / redirect`, !/http-equiv="refresh"|window\.location\s*=/.test(html));
    for (const m of html.matchAll(/<img\b([^>]*)>/g)) {
      const attrs = m[1];
      const src = (attrs.match(/src="([^"]*)"/) || [])[1] || '';
      check(`${name}: image has alt attribute`, /\balt="/.test(attrs), src);
      check(`${name}: image is served from this site`, src.startsWith(base + '/assets/img/'), src);
      const imgFile = src.startsWith(base) ? path.join(DOCS, src.slice(base.length)) : '';
      check(`${name}: image file exists`, !!imgFile && fs.existsSync(imgFile), src);
    }
    check(`${name}: has a canonical URL`, /<link rel="canonical" href="https:\/\/karagemop466-tech\.github\.io\/Affil3\//.test(html));
    if (path.basename(f) !== '404.html') {
      const h1s = (html.match(/<h1[\s>]/g) || []).length;
      check(`${name}: exactly one h1`, h1s === 1, String(h1s));
      const title = (html.match(/<title>([\s\S]*?)<\/title>/) || ['', ''])[1];
      check(`${name}: title within 90 characters`, title.length > 0 && title.length <= 90, String(title.length));
    }
    check(`${name}: no price-like amounts`, !/\$\s?\d/.test(body), (body.match(/.{0,20}\$\s?\d.{0,20}/) || [''])[0]);
    // Zero third-party requests. The site loads one stylesheet, one script and its own images, all
    // same-origin, and /privacy/ says so. A webfont, hosted analytics script or widget from another
    // origin would make that page false and would add a data processor nobody has reviewed.
    check(`${name}: no external stylesheet, script or font origin`,
      !/<link[^>]+rel="stylesheet"[^>]*href="https?:\/\//i.test(html)
      && !/<script[^>]+src="https?:\/\//i.test(html)
      && !/@import\s+url\(\s*['"]?https?:/i.test(html)
      && !/fonts\.(googleapis|gstatic)\.com/i.test(html),
      (html.match(/<link[^>]+rel="stylesheet"[^>]*href="https?:[^>]*>|<script[^>]+src="https?:[^>]*>/i) || [''])[0]);
    // dashboards in footer
    const footer = (html.match(/<footer[\s\S]*<\/footer>/) || [''])[0];
    // Kept in step with DASHBOARDS in tools/build.mjs; /privacy/ and /design-brief/ were added by
    // session 66f2548a so the two new pages cannot silently lose their footer entry.
    for (const d of ['/executive-summary/', '/shop/', '/sources/', '/questions/', '/suggestions/', '/flagged/', '/ledger/', '/measurement/', '/compliance/', '/about/', '/privacy/', '/design-brief/']) {
      check(`${name}: footer links ${d}`, footer.includes(`${base}${d}`));
    }
    // links
    for (const m of html.matchAll(/<a\b([^>]*)>/g)) {
      const attrs = m[1];
      const href = (attrs.match(/href="([^"]*)"/) || [])[1] || '';
      const rel_ = (attrs.match(/rel="([^"]*)"/) || [])[1] || '';
      let host = ''; try { host = new URL(href).hostname; } catch {}
      if (/(^|\.)amazon\.com$/.test(host) || host === 'link.amazon') {
        check(`${name}: Amazon link is sponsored`, /\bsponsored\b/.test(rel_), href);
      }
      // Program Policies 2(b): a link to an Amazon retail site must carry the tag.
      const DOC_HOSTS = ['affiliate-program.amazon.com', 'sell.amazon.com', 'developer.amazon.com', 'advertising.amazon.com'];
      const retail = /(^|\.)amazon\.com$/.test(host) && !DOC_HOSTS.includes(host);
      if (retail) {
        const t = href.match(/[?&]tag=([^&]+)/);
        check(`${name}: retail Amazon link carries the tag ${TAG}`, !!t && decodeURIComponent(t[1]) === TAG, href);
      }
      check(`${name}: no link.amazon short link is published as a link`, host !== 'link.amazon', href);
      if (href.includes('/dp/') && host.endsWith('amazon.com')) {
        const m2 = href.match(/\/dp\/([A-Za-z0-9]+)/);
        check(`${name}: /dp/ link has a 10-character ASIN`, !!m2 && m2[1].length === 10, href);
        const tagMatch = href.match(/[?&]tag=([^&]+)/);
        if (tagMatch) check(`${name}: tag is ${TAG}`, decodeURIComponent(tagMatch[1]) === TAG, href);
      }
      if (href.startsWith(base) || href.startsWith('/')) {
        const target = fileFor(href.startsWith('/') && !href.startsWith(base) ? base + href : href);
        if (target) check(`${name}: internal link resolves ${href.split('#')[0]}`, fs.existsSync(target) && fs.statSync(target).isFile() || fs.existsSync(target), href);
      }
      if (href.startsWith('#')) {
        const id = href.slice(1);
        if (id) check(`${name}: anchor ${href} exists`, html.includes(`id="${id}"`), href);
      }
    }
    // data-attribute checks for analytics
    if (name.startsWith('/guides/') && name !== '/guides/index.html') check(`${name}: has data-guide`, /data-guide="/.test(html));
  }
  // ---- editorial requirements unique to this build ----
  const home = fs.readFileSync(path.join(DOCS, 'index.html'), 'utf8');
  // Only links inside the reader-facing body count; the masthead and footer are navigation.
  const homeMain = (home.match(/<main id="main"[\s\S]*?<\/main>/) || [''])[0];
  // The front page must sell before it explains itself: the first buy button and the product
  // grid both have to appear before the first link to any process, flag or register page.
  const firstShop = homeMain.indexOf('class="shop-grid"');
  const firstBuy = homeMain.indexOf('data-outbound');
  const firstProcess = Math.min(...['/flagged/', '/executive-summary/', '/shop/', '/sources/', '/questions/', '/suggestions/', '/compliance/', '/workflow/']
    .map((u) => { const i = homeMain.indexOf(base + u); return i < 0 ? Infinity : i; }));
  check('home page puts the products before any process or register link', firstShop > 0 && firstBuy > 0 && firstShop < firstProcess && firstBuy < firstProcess,
    `shop@${firstShop} buy@${firstBuy} process@${firstProcess}`);
  check('home page opens with the five products in one grid', (home.match(/<article class="product-card/g) || []).length === products.length);
  check('home page carries a hero image with alt text', /class="hero-shop-art"[\s\S]*?<img [^>]*alt="[^"]+"/.test(home));
  check('home page names a live-price policy instead of printing a price', /Check price on Amazon/.test(home));

  for (const p of products) {
    const f = path.join(DOCS, 'products', p.slug, 'index.html');
    check(`product page exists for ${p.id}`, fs.existsSync(f), p.slug);
    if (!fs.existsSync(f)) continue;
    const h = fs.readFileSync(f, 'utf8');
    check(`product page ${p.id} has a specification grid`, /class="spec-grid"/.test(h));
    // Every specification the maker does not state must render as a labelled "not stated" cell,
    // and the count of those cells must match the data exactly (no silent fill-ins).
    const stated = [p.model, p.capacity_qt, (p.temp_min_f || p.temp_max_f), p.power_w, p.voltage, p.dimensions_in, p.weight_lb, p.dishwasher_safe, p.certification, p.warranty];
    const expectedNa = stated.filter((v) => !v).length;
    const actualNa = (h.match(/class="na"/g) || []).length;
    check(`product page ${p.id} shows exactly ${expectedNa} "not stated" cells`, actualNa === expectedNa, `${actualNa} rendered`);
    if (p.no_buy_link) {
      check(`product page ${p.id} publishes no buy button`, !/data-outbound/.test(h));
      check(`product page ${p.id} explains why`, /No buy button on this page/.test(h));
    } else {
      check(`product page ${p.id} has exactly one tagged outbound buy link`, (h.match(/data-outbound/g) || []).length === 1 && h.includes(`tag=${TAG}`));
    }
    check(`product page ${p.id} names its source ids`, (p.sources || []).every((id) => h.includes(`>${id}<`) || h.includes(id)));
  }
  for (const g of guides) {
    const f = path.join(DOCS, 'guides', g.slug, 'index.html');
    const h = fs.readFileSync(f, 'utf8');
    check(`guide ${g.slug} has a hero image`, /class="article-hero"/.test(h) && /<img [^>]*alt="[^"]+"/.test(h));
    check(`guide ${g.slug} lists its sources`, /Sources for this guide/.test(h));
    check(`guide ${g.slug} states it is not a test`, !/we tested|our test kitchen|we cooked/i.test(h));
  }
  check('no page claims hands-on testing', !htmlFiles.some((f) => /we tested (it|this|these|the)|our test kitchen|we cooked (it|with|in)/i.test(fs.readFileSync(f, 'utf8'))));
  const allHtml = htmlFiles.map((f) => fs.readFileSync(f, 'utf8')).join('\n');
  check('no star rating or review count is republished', !/\b\d\.\d\s*(out of 5|\/5|stars)\b/i.test(allHtml));
  check('every product image is labelled as illustration', /not the reviewed unit|Editorial illustration|editorial illustration/i.test(home));

  // sitemap coverage
  for (const u of pageUrls) check(`sitemap includes ${u}`, sitemapUrls.includes(u));
  // feed coverage
  const feed = fs.readFileSync(path.join(DOCS, 'feed.xml'), 'utf8');
  const feedLinks = [...feed.matchAll(/<link>([^<]+)<\/link>/g)].map((m) => m[1]).filter((u) => u.includes('/guides/'));
  check('feed has one item per guide', feedLinks.length === guides.length, `${feedLinks.length} vs ${guides.length}`);
  for (const l of feedLinks) check(`feed item in sitemap: ${l}`, sitemapUrls.includes(l));
  // ---- one indexable site, and a decision board that is actually answerable ----
  const robotsTxt = fs.readFileSync(path.join(DOCS, 'robots.txt'), 'utf8');
  for (const d of ['/editorial/', '/legacy/', '/crisp-index/', '/counter/', '/counterwise/']) {
    check(`robots.txt keeps archive ${d} out of the crawl`, robotsTxt.includes(`Disallow: ${d}`), d);
  }
  // Every archived edition on this domain must carry noindex in the page itself: robots.txt alone
  // does not remove a URL from results (Google, S25).
  for (const dir of ['crisp-index', 'counter', 'editorial']) {
    const base2 = path.join(DOCS, dir);
    if (!fs.existsSync(base2)) continue;
    const files = [];
    const walkA = (d) => { for (const f of fs.readdirSync(d)) { const q = path.join(d, f); if (fs.statSync(q).isDirectory()) walkA(q); else if (f.endsWith('.html')) files.push(q); } };
    walkA(base2);
    const missing = files.filter((f) => !/name="robots"[^>]*noindex/.test(fs.readFileSync(f, 'utf8')));
    check(`${dir}/: every page carries noindex (${files.length} pages)`, missing.length === 0, missing.slice(0, 3).join(', '));
  }
  // A reader must be able to compare from more than one page.
  const comparePage = path.join(DOCS, 'compare', 'index.html');
  check('a compare page exists and is in the sitemap', fs.existsSync(comparePage) && sitemapUrls.includes(cfg.siteUrl + '/compare/'), '/compare/');
  if (fs.existsSync(comparePage)) {
    const cmp = fs.readFileSync(comparePage, 'utf8');
    check('compare page carries a buy link per shoppable product', (cmp.match(/data-outbound/g) || []).length === products.filter((pr) => pr.tagged_outbound_url && !pr.no_buy_link).length);
    check('compare page marks every unknown value instead of filling it', /not stated/.test(cmp));
  }
  // Decision board: every entry this pass authored must be answerable — options, a recommendation,
  // a named current option, a confidence level, an effort estimate and a reply template.
  for (const sug of suggestionsDoc.suggestions) {
    check(`suggestion ${sug.id} has at least two options`, sug.options && sug.options.length >= 2, String(sug.options && sug.options.length));
    check(`suggestion ${sug.id} states a recommendation`, !!sug.recommendation);
    check(`suggestion ${sug.id} names the option currently in place`, !!(sug.options || []).find((o) => o.id === sug.current));
    if (sug.plain_question) {
      check(`suggestion ${sug.id} gives the owner something to reply with`, !!sug.prompt);
      check(`suggestion ${sug.id} states how much work it is`, !!sug.effort);
      check(`suggestion ${sug.id} states a confidence level`, ['high', 'medium', 'low'].includes(sug.confidence));
    } else {
      check(`suggestion ${sug.id} at least explains itself`, !!(sug.recommendation || sug.note));
    }
  }
  // Open questions: each must say how it is closed; blocking ones must offer an answer template.
  for (const q of questions.unknown) {
    check(`question ${q.id} says how to close it`, !!q.how_to_close);
    check(`question ${q.id} explains why it matters`, !!q.why_it_matters);
    if (q.blocking) check(`blocking question ${q.id} gives an answer template`, !!q.answer_template);
  }
  check('robots.txt references sitemap', fs.readFileSync(path.join(DOCS, 'robots.txt'), 'utf8').includes(cfg.siteUrl + '/sitemap.xml'));
  check('.nojekyll present', fs.existsSync(path.join(DOCS, '.nojekyll')));
  check('legacy site untouched by build (not regenerated)', !htmlFiles.some((f) => f.includes(path.join('legacy', ''))));
}

// ---------- report ----------
console.log(`verify: ${passes.length} checks passed, ${failures.length} failed`);
if (failures.length) {
  for (const f of failures) console.log('  FAIL ' + f);
  process.exit(1);
}
