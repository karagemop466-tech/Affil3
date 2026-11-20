#!/usr/bin/env node
// Publishing gate for Affil3. Run after tools/build.mjs. Exits non-zero on any failure.
// Checks data (source links, flags, ASIN format, tags) and the generated site (disclosure,
// sponsored attributes, internal links, sitemap/feed coverage, no redirects, no prices, analytics allowlist).
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const DOCS = ROOT; // generated site lives at the repository root
const OWNED = ['index.html', 'shop', 'categories', 'guides', 'executive-summary', 'sources', 'questions', 'suggestions',
  'flagged', 'ledger', 'measurement', 'compliance', 'about', '404.html'];
const read = (p) => JSON.parse(fs.readFileSync(path.join(ROOT, p), 'utf8'));
const cfg = read('data/config.json');
const products = read('data/products.json').products;
const sources = read('data/sources.json').sources;
const flags = read('data/flags.json').flags;
const events = read('data/events.json').events;
const guides = read('data/guides.json').guides;

const ALLOWED_SOURCE_HOSTS = new Set([
  'affiliate-program.amazon.com', 'www.amazon.com', 'link.amazon', 'developers.google.com', 'www.ftc.gov',
  'www.ecfr.gov', 'www.fsis.usda.gov', 'github.com',
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
  const pageUrls = htmlFiles.filter((f) => path.basename(f) !== '404.html').map((f) => cfg.siteUrl + rel(f).replace(/index\.html$/, ''));

  for (const f of htmlFiles) {
    const html = fs.readFileSync(f, 'utf8');
    const name = rel(f);
    const body = html.replace(/<script[\s\S]*?<\/script>/g, '');
    check(`${name}: disclosure strip above main`, /<div class="disclosure-strip"[\s\S]*?Disclosure\.[\s\S]*?<\/div>\s*<main/.test(html));
    check(`${name}: Associates statement present`, html.includes(cfg.associatesStatement));
    check(`${name}: footer repeats disclosure`, /<footer[\s\S]*<p class="disclosure-footer">[\s\S]*?Disclosure\./.test(html));
    check(`${name}: no meta refresh / redirect`, !/http-equiv="refresh"|window\.location\s*=/.test(html));
    // images: local, present on disk, with alt text
    for (const m of html.matchAll(/<img\b([^>]*)>/g)) {
      const attrs = m[1];
      const src = (attrs.match(/src="([^"]*)"/) || [])[1] || '';
      check(`${name}: image has alt attribute`, /\balt="/.test(attrs), src);
      check(`${name}: image is served from this site`, src.startsWith(base + '/assets/img/'), src);
      const imgFile = src.startsWith(base) ? path.join(DOCS, src.slice(base.length)) : '';
      check(`${name}: image file exists ${src}`, !!imgFile && fs.existsSync(imgFile), src);
      check(`${name}: image has width and height`, /\bwidth="/.test(attrs) && /\bheight="/.test(attrs), src);
    }
    check(`${name}: loads no external stylesheet or font`, !/<link[^>]+rel="stylesheet"[^>]+href="https?:/.test(html) && !/@import\s+url\(/.test(html));
    check(`${name}: has a canonical URL`, /<link rel="canonical" href="https:\/\/karagemop466-tech\.github\.io\/Affil3\//.test(html));
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
        const t = href.match(/[?&]tag=([^&]+)/);
        check(`${name}: every Amazon link carries the tracking tag`, !!t && decodeURIComponent(t[1]) === TAG, href);
      }
      check(`${name}: no untagged link.amazon short link is published`, host !== 'link.amazon', href);
      if (href.includes('/dp/') && host.endsWith('amazon.com')) {
        const m2 = href.match(/\/dp\/([A-Za-z0-9]+)/);
        check(`${name}: /dp/ link has a 10-character ASIN`, !!m2 && m2[1].length === 10, href);
        const tagMatch = href.match(/[?&]tag=([^&]+)/);
        check(`${name}: /dp/ link carries the tag ${TAG}`, !!tagMatch && decodeURIComponent(tagMatch[1]) === TAG, href);
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
  // sitemap coverage
  for (const u of pageUrls) check(`sitemap includes ${u}`, sitemapUrls.includes(u));
  // discovery hygiene: titles and descriptions within search-engine display limits
  for (const f of htmlFiles) {
    const html = fs.readFileSync(f, 'utf8');
    if (path.basename(f) === '404.html') continue;
    const title = (html.match(/<title>([\s\S]*?)<\/title>/) || ['', ''])[1].replace(' | ' + cfg.siteName, '');
    const desc = (html.match(/<meta name="description" content="([^"]*)"/) || ['', ''])[1];
    check(`${rel(f)}: title within 75 characters`, title.length > 0 && title.length <= 75, String(title.length));
    check(`${rel(f)}: description 40-175 characters`, desc.length >= 40 && desc.length <= 175, String(desc.length));
    check(`${rel(f)}: has a single h1`, (html.match(/<h1[\s>]/g) || []).length === 1, String((html.match(/<h1[\s>]/g) || []).length));
  }

  // one indexable site: archive publications excluded from robots; root sitemap has no archive URLs
  const robotsTxt = fs.readFileSync(path.join(DOCS, 'robots.txt'), 'utf8');
  check('robots.txt disallows the archive publications', /Disallow: \/editorial\//.test(robotsTxt) && /Disallow: \/legacy\//.test(robotsTxt));
  check('root sitemap lists no archive URLs', !sitemapUrls.some((u) => u.includes('/editorial/') || u.includes('/legacy/')));
  // feed coverage
  const feed = fs.readFileSync(path.join(DOCS, 'feed.xml'), 'utf8');
  const feedLinks = [...feed.matchAll(/<link>([^<]+)<\/link>/g)].map((m) => m[1]).filter((u) => u.includes('/guides/'));
  check('feed has one item per guide', feedLinks.length === guides.length, `${feedLinks.length} vs ${guides.length}`);
  for (const l of feedLinks) check(`feed item in sitemap: ${l}`, sitemapUrls.includes(l));
  check('robots.txt references sitemap', fs.readFileSync(path.join(DOCS, 'robots.txt'), 'utf8').includes(cfg.siteUrl + '/sitemap.xml'));
  check('.nojekyll present', fs.existsSync(path.join(DOCS, '.nojekyll')));
  check('legacy site untouched by build (not regenerated)', !htmlFiles.some((f) => f.includes(path.join('legacy', ''))));
}

// ---------- 3. decision register ----------
const suggestions = read('data/suggestions.json');
const questions = read('data/questions.json');
for (const s of suggestions.suggestions) {
  for (const k of ['id', 'topic', 'current', 'options', 'recommendation', 'status', 'owner', 'impact', 'effort']) {
    check(`suggestion ${s.id} has ${k}`, Object.prototype.hasOwnProperty.call(s, k), k);
  }
  check(`suggestion ${s.id} has at least two options`, s.options.length >= 2, String(s.options.length));
  check(`suggestion ${s.id} current points at a real option`, s.options.some((o) => o.id === s.current), s.current);
  check(`suggestion ${s.id} status is known`, ['implemented', 'needs decision', 'blocked'].includes(s.status), s.status);
  for (const o of s.options) check(`suggestion ${s.id} option ${o.id} has a tradeoff`, !!o.tradeoff, o.id);
}
for (const p of suggestions.paths) {
  for (const k of ['id', 'name', 'summary', 'needs', 'buys', 'risks']) check(`path ${p.id} has ${k}`, Object.prototype.hasOwnProperty.call(p, k), k);
}
check('exactly one path is recommended', suggestions.paths.filter((p) => p.recommended).length === 1);
for (const q of questions.unknown) {
  for (const k of ['id', 'question', 'why_it_matters', 'how_to_close', 'sources']) check(`question ${q.id} has ${k}`, Object.prototype.hasOwnProperty.call(q, k), k);
  for (const sid of q.sources) check(`question ${q.id} source ${sid} exists`, SRC.has(sid), sid);
}
for (const d of questions.discovery) for (const c of d.closes) check(`discovery ${d.id} closes a real question`, questions.unknown.some((q) => q.id === c) || questions.discovery.some((x) => x.id === c), c);
check('every blocking question is referenced by a discovery step', questions.unknown.filter((q) => q.blocking).every((q) => questions.discovery.some((d) => d.closes.includes(q.id))));

// ---------- report ----------
console.log(`verify: ${passes.length} checks passed, ${failures.length} failed`);
if (failures.length) {
  for (const f of failures) console.log('  FAIL ' + f);
  process.exit(1);
}
