#!/usr/bin/env node
// Publishing gate for Affil3. Run after tools/build.mjs. Exits non-zero on any failure.
// Checks data (source links, flags, ASIN format, tags) and the generated site (disclosure,
// sponsored attributes, internal links, sitemap/feed coverage, no redirects, no prices, analytics allowlist).
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const DOCS = ROOT; // generated site lives at the repository root
const OWNED = ['index.html', 'shop', 'products', 'compare', 'search', 'categories', 'guides', 'executive-summary', 'sources', 'questions', 'suggestions',
  'flagged', 'ledger', 'measurement', 'compliance', 'about', '404.html'];
const read = (p) => JSON.parse(fs.readFileSync(path.join(ROOT, p), 'utf8'));
const cfg = read('data/config.json');
const products = read('data/products.json').products;
const sources = read('data/sources.json').sources;
const flags = read('data/flags.json').flags;
const events = read('data/events.json').events;
const guides = read('data/guides.json').guides;
const catalog = read('data/catalog.json').products;

const ALLOWED_SOURCE_HOSTS = new Set([
  'affiliate-program.amazon.com', 'www.amazon.com', 'link.amazon', 'developers.google.com', 'www.ftc.gov',
  'www.ecfr.gov', 'www.fsis.usda.gov', 'github.com',
  // Manufacturer product pages: the primary source for every specification published on a product page.
  'chefman.com', 'www.emerileveryday.com', 'www.thermomaven.com', 'chefiq.com',
  // NIST, for the FAQ text used to qualify a "NIST-certified" marketing claim.
  'www.nist.gov',
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

// ---------- 1b. catalog: every specification traced to a manufacturer source ----------
const CATALOG_REQUIRED = ['id', 'asin', 'slug', 'brand', 'name', 'model', 'category', 'shape', 'one_liner', 'best_for', 'not_for', 'decide', 'specs', 'faq'];
check('catalog covers every product row', catalog.length === products.length, `${catalog.length} vs ${products.length}`);
for (const c of catalog) {
  for (const k of CATALOG_REQUIRED) check(`catalog ${c.id} has ${k}`, Object.prototype.hasOwnProperty.call(c, k), k);
  const p = products.find((x) => x.id === c.id);
  check(`catalog ${c.id} matches the submitted ASIN`, !!p && p.observed_asin === c.asin, c.asin);
  check(`catalog ${c.id} slug is url-safe`, /^[a-z0-9-]+$/.test(c.slug), c.slug);
  check(`catalog ${c.id} decides at least two things`, c.decide.length >= 2, String(c.decide.length));
  check(`catalog ${c.id} answers at least three buyer questions`, c.faq.length >= 3, String(c.faq.length));
  check(`catalog ${c.id} has no price-like value`, !c.specs.some((sp) => /\d+(\.\d+)?\s*(USD|\$)/.test(sp.value || '')), c.id);
  check(`catalog ${c.id} quotes no star rating`, !JSON.stringify(c).match(/\b\d(\.\d)?\s*(out of 5|stars?)\b/i), c.id);
  for (const sp of c.specs) {
    // A published value must carry a source. A blank value must NOT carry one (nothing to cite).
    if (sp.value) check(`catalog ${c.id} "${sp.label}" value has a source`, !!sp.source, sp.label);
    if (sp.value) check(`catalog ${c.id} "${sp.label}" source exists`, SRC.has(sp.source), String(sp.source));
    if (!sp.value) check(`catalog ${c.id} "${sp.label}" blank value is explained`, !!sp.note, sp.label);
    if (sp.source) check(`catalog ${c.id} "${sp.label}" cites a manufacturer or observed source`, /^S(1[4-9]|2[0-9])$/.test(sp.source), sp.source);
  }
  for (const f of c.faq) if (f.source) check(`catalog ${c.id} FAQ source exists`, SRC.has(f.source), f.source);
}

// analytics allowlist: events.json, the browser script and the collector must agree
const EVENT_NAMES = events.map((e) => e.name).sort().join(',');
const jsSrc = fs.readFileSync(path.join(ROOT, 'src/assets/analytics.js'), 'utf8');
const colSrc = fs.readFileSync(path.join(ROOT, 'tools/collector.mjs'), 'utf8');
const jsAllowed = (jsSrc.match(/var ALLOWED = \{([^}]*)\}/)[1].match(/\w+(?=\s*:)/g) || []).sort().join(',');
const colAllowed = (colSrc.match(/const EVENTS = \{([\s\S]*?)\n\};/)[1].match(/\w+(?=\s*:\s*\[)/g) || []).sort().join(',');
check('five analytics events agree across events.json, browser script and collector', EVENT_NAMES === jsAllowed && jsAllowed === colAllowed, `${EVENT_NAMES} | ${jsAllowed} | ${colAllowed}`);
check('browser script sets no cookies or storage', !/document\.cookie|localStorage|sessionStorage/.test(jsSrc));

// ---------- 1c. design: WCAG AA contrast on every colour pair the site uses ----------
// Computed here rather than asserted in prose, so a palette change cannot silently drop below AA.
const css = fs.readFileSync(path.join(ROOT, 'src/assets/style.css'), 'utf8');
const cssVar = (name) => {
  const m = css.match(new RegExp('--' + name + ':\\s*(#[0-9a-fA-F]{6})'));
  return m ? m[1] : null;
};
const hexLum = (h) => {
  const [r, g, b] = [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16) / 255)
    .map((c) => (c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4)));
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
};
const contrast = (a, b) => {
  const [l1, l2] = [hexLum(a), hexLum(b)].sort((x, y) => y - x);
  return (l1 + 0.05) / (l2 + 0.05);
};
const PAIRS = [
  ['ink', 'paper'], ['muted', 'paper'], ['muted', 'card'], ['accent', 'paper'], ['accent', 'card'],
  ['accent', 'accent-soft'], ['ink', 'strip'], ['warn', 'warn-bg'], ['bad', '#f7dedc'], ['good', '#e2efe6'],
];
for (const [fg, bg] of PAIRS) {
  const f = cssVar(fg), b = bg.startsWith('#') ? bg : cssVar(bg);
  check(`contrast ${fg} on ${bg} reaches WCAG AA (4.5:1)`, !!f && !!b && contrast(f, b) >= 4.5, f && b ? `${f} on ${b} = ${contrast(f, b).toFixed(2)}:1` : 'token missing');
}
// Fixed pairs that do not come from a token.
for (const [label, fg, bg] of [['button label', '#ffffff', '#7a3b1d'], ['footer body', '#e9e4d8', '#26241f'], ['footer fine print', '#bdb6a6', '#26241f']]) {
  check(`contrast ${label} reaches WCAG AA (4.5:1)`, contrast(fg, bg) >= 4.5, `${contrast(fg, bg).toFixed(2)}:1`);
}

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
  // 404 and the empty "unresolved" cluster are reachable but deliberately not advertised for indexing.
  const NO_SITEMAP = ['/404.html', '/categories/unresolved/index.html'];
  const pageUrls = htmlFiles.filter((f) => !NO_SITEMAP.includes(rel(f))).map((f) => cfg.siteUrl + rel(f).replace(/index\.html$/, ''));

  for (const f of htmlFiles) {
    const html = fs.readFileSync(f, 'utf8');
    const name = rel(f);
    const body = html.replace(/<script[\s\S]*?<\/script>/g, '');
    check(`${name}: disclosure strip above main`, /<div class="disclosure-strip"[\s\S]*?Disclosure\.[\s\S]*?<\/div>\s*<main/.test(html));
    check(`${name}: Associates statement present`, html.includes(cfg.associatesStatement));
    check(`${name}: footer repeats disclosure`, /<footer[\s\S]*<p class="disclosure-footer">[\s\S]*?Disclosure\./.test(html));
    check(`${name}: no meta refresh / redirect`, !/http-equiv="refresh"|window\.location\s*=/.test(html));
    check(`${name}: no price-like amounts`, !/\$\s?\d/.test(body), (body.match(/.{0,20}\$\s?\d.{0,20}/) || [''])[0]);
    // dashboards in footer
    const footer = (html.match(/<footer[\s\S]*<\/footer>/) || [''])[0];
    for (const d of ['/executive-summary/', '/shop/', '/sources/', '/questions/', '/suggestions/', '/flagged/', '/ledger/', '/measurement/', '/compliance/', '/about/']) {
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
    if (name.startsWith('/products/')) {
      check(`${name}: has a tagged buy link`, /href="https:\/\/www\.amazon\.com\/dp\/[A-Z0-9]{10}\?tag=/.test(html));
      check(`${name}: buy link is sponsored`, /rel="sponsored/.test(html));
      check(`${name}: carries Product structured data`, /"@type":"Product"/.test(html));
      check(`${name}: carries FAQ structured data`, /"@type":"FAQPage"/.test(html));
      check(`${name}: says the unit was not tested`, /have not tested/.test(html));
      check(`${name}: no unsourced buy button inside a headline`, !/class="btn"[^>]*>Buy now</.test(html));
    }
  }
  // sitemap coverage
  for (const u of pageUrls) check(`sitemap includes ${u}`, sitemapUrls.includes(u));
  // feed coverage
  const feed = fs.readFileSync(path.join(DOCS, 'feed.xml'), 'utf8');
  const feedLinks = [...feed.matchAll(/<link>([^<]+)<\/link>/g)].map((m) => m[1]).filter((u) => u.includes('/guides/'));
  check('feed has one item per guide', feedLinks.length === guides.length, `${feedLinks.length} vs ${guides.length}`);
  for (const l of feedLinks) check(`feed item in sitemap: ${l}`, sitemapUrls.includes(l));
  for (const c of catalog) check(`sitemap includes the product page for ${c.id}`, sitemapUrls.includes(cfg.siteUrl + `/products/${c.slug}/`), c.slug);
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
