#!/usr/bin/env node
/**
 * Counter Desk — publishing gate.
 *
 * Fails the build rather than warning. Every rule below corresponds to one of three
 * things: an Amazon program requirement, an FTC disclosure requirement, or a promise
 * this publication makes to its own readers (no prices, no ratings, no testing claims,
 * every image captioned).
 *
 * Run: node tools/3b45b513/gate.mjs            (after the generator)
 *      node tools/3b45b513/gate.mjs --quiet    (prints failures only)
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '../..');
const OUT = path.join(ROOT, 'counter-desk');
const DATA = path.join(ROOT, 'data/3b45b513');
const quiet = process.argv.includes('--quiet');

const read = (p) => JSON.parse(fs.readFileSync(path.join(DATA, p), 'utf8'));
const cfg = read('config.json');
const sources = read('sources.json').sources;
const products = read('products.json').products;
const flags = read('flags.json').flags;
const guides = read('guides.json').guides;
const suggestions = read('suggestions.json').suggestions;
const questions = read('questions.json');
const ledger = read('ledger.json');
const events = read('events.json');

const TAG = cfg.trackingId;
const BASE = cfg.basePath; // /Affil3/counter-desk
const SRC = new Map(sources.map((s) => [s.id, s]));
const FLG = new Map(flags.map((f) => [f.id, f]));

const fail = [];
const pass = [];
const check = (name, ok, detail = '') => {
  if (ok) pass.push(name);
  else fail.push(detail ? `${name} — ${detail}` : name);
};

// ═══ 1. data layer ════════════════════════════════════════════════════════
// 1.1 Sources: official hosts only, https only, and every row says how it was checked.
const OFFICIAL_HOSTS = new Set([
  'affiliate-program.amazon.com', 'www.amazon.com', 'sell.amazon.com', 'link.amazon',
  'developers.google.com', 'www.ftc.gov', 'www.ecfr.gov', 'www.fsis.usda.gov',
  'chefman.com', 'www.emerileveryday.com', 'chefiq.com', 'www.thermomaven.com',
  'cdn.shopify.com', 'github.com', 'link.amazon',
]);
for (const s of sources) {
  let host = '';
  try { host = new URL(s.url).hostname; } catch { /* reported below */ }
  check(`source ${s.id} is https on an official host`, s.url.startsWith('https://') && OFFICIAL_HOSTS.has(host), s.url);
  check(`source ${s.id} records how it was checked`, typeof s.method === 'string' && s.method.length > 2, s.method);
  check(`source ${s.id} records a status`, ['verified', 'observed'].includes(s.status), s.status);
  check(`source ${s.id} has no unverified/excerpt status`, !/excerpt|unverified/i.test(s.status), s.status);
  check(`source ${s.id} states what it supports`, typeof s.supports === 'string' && s.supports.length > 20);
}

// 1.2 Products: the intent block is all-blank or all-filled, never half-guessed.
for (const p of products) {
  const intent = [p.intended_asin, p.official_listing_url, p.confirmation_date, p.confirmation_source];
  const filled = intent.filter(Boolean).length;
  check(`${p.id} intent fields are complete or all blank`, filled === 0 || filled === 4, `${filled}/4 filled`);
  if (filled === 4) {
    check(`${p.id} intended ASIN is 10 characters`, /^[A-Z0-9]{10}$/.test(p.intended_asin), p.intended_asin);
  }
  check(`${p.id} submitted token length is recorded correctly`, p.submitted_token.length === p.submitted_token_length);
  check(`${p.id} observed ASIN is 10 characters`, /^[A-Z0-9]{10}$/.test(p.observed.asin), p.observed.asin);
  check(`${p.id} observed URL matches the observed ASIN`, p.observed.final_url === `https://www.amazon.com/dp/${p.observed.asin}`, p.observed.final_url);
  check(`${p.id} outbound URL is the observed ASIN with the tracking tag`, p.tagged_outbound_url === `https://www.amazon.com/dp/${p.observed.asin}?tag=${TAG}`, p.tagged_outbound_url);
  check(`${p.id} has a dated observation`, /^\d{4}-\d{2}-\d{2}$/.test(p.observed.date));
  check(`${p.id} cites an observation source that exists`, SRC.has(p.observed.source), p.observed.source);
  for (const id of p.sources) check(`${p.id} source ${id} exists`, SRC.has(id), id);
  for (const id of p.spec_sources) check(`${p.id} spec source ${id} exists`, SRC.has(id), id);
  for (const id of p.flags) check(`${p.id} flag ${id} exists`, FLG.has(id), id);
  check(`${p.id} has no price/rating/availability field`, !/price|rating|availability|stock/i.test(Object.keys(p).join(' ')));

  // Every published specification value needs a source id; every blank needs a reason.
  for (const [key, spec] of Object.entries(p.specs)) {
    const has = spec.value && String(spec.value).trim();
    if (has) check(`${p.id}.${key} cites a real source`, !!spec.source && SRC.has(spec.source), spec.source || 'no source');
    else check(`${p.id}.${key} blank explains why`, typeof spec.note === 'string' && spec.note.length > 15, spec.note || 'no reason');
  }
  // The two figures this build deliberately withholds must stay withheld.
  if (p.id === 'P3') {
    check('P3 wattage stays withheld while two official pages disagree', p.specs.power.value === '');
    check('P3 dimensions stay withheld while two official pages disagree', p.specs.dimensions.value === '');
  }
  if (p.id === 'P5') check('P5 battery life stays withheld while two official pages disagree', p.specs.battery.value === '');
  if (p.id === 'P2') check('P2 preset count stays withheld while the maker contradicts itself', p.specs.presets.value === '');
}

// 1.3 Flags: ids unique, every source resolves, resolved flags keep their record.
const flagIds = flags.map((f) => f.id);
check('flag ids are unique', new Set(flagIds).size === flagIds.length);
for (const f of flags) {
  for (const id of f.sources) check(`flag ${f.id} source ${id} exists`, SRC.has(id), id);
  check(`flag ${f.id} states why it matters`, typeof f.why_it_matters === 'string' && f.why_it_matters.length > 20);
  check(`flag ${f.id} states what closes it`, typeof f.manual_step === 'string' && f.manual_step.length > 10);
  check(`flag ${f.id} has a valid status`, ['open', 'resolved'].includes(f.status), f.status);
  check(`flag ${f.id} has a valid severity`, ['high', 'medium', 'low'].includes(f.severity), f.severity);
}

// 1.4 Guides: unique slugs, real source ids, a stated hypothesis flag, sections that render.
for (const g of guides) {
  check(`guide ${g.slug} slug is url-safe`, /^[a-z0-9-]+$/.test(g.slug), g.slug);
  for (const id of g.sources) check(`guide ${g.slug} source ${id} exists`, SRC.has(id), id);
  check(`guide ${g.slug} dates itself`, /^\d{4}-\d{2}-\d{2}$/.test(g.date));
  check(`guide ${g.slug} has takeaways`, Array.isArray(g.key_takeaways) && g.key_takeaways.length >= 3);
  check(`guide ${g.slug} has a reading time`, Number.isInteger(g.read_minutes) && g.read_minutes > 2);
  // Every [Sxx] marker in the prose must name a source that exists.
  const prose = JSON.stringify(g.sections);
  for (const m of prose.matchAll(/\[(S\d{2})\]/g)) check(`guide ${g.slug} cites ${m[1]} which exists`, SRC.has(m[1]), m[1]);
  for (const s of g.sections) {
    check(`guide ${g.slug} section type is known`, ['p', 'h2', 'h3', 'ul', 'ol', 'note', 'product', 'table'].includes(s.type), s.type);
    if (s.type === 'product') check(`guide ${g.slug} inline product ${s.id} exists`, products.some((p) => p.id === s.id), s.id);
  }
}
check('guide slugs are unique', new Set(guides.map((g) => g.slug)).size === guides.length);
const hypothesisTitles = [
  'basket-or-oven-style-air-fryer-what-should-you-compare',
  'air-fryer-capacity-checklist',
  'cleanup-and-counter-space-tradeoffs',
  'questions-to-ask-before-buying-a-multi-function-kitchen-appliance',
];
for (const slug of hypothesisTitles) {
  const g = guides.find((x) => x.slug === slug);
  check(`working-hypothesis guide present: ${slug}`, !!g);
  if (g) check(`working-hypothesis guide ${slug} is labelled a hypothesis`, g.hypothesis === true);
}

// 1.5 Suggestions and questions: the SG-27..SG-30 pass items must be accounted for.
for (const id of ['SG-27', 'SG-28', 'SG-29', 'SG-30']) {
  const s = suggestions.find((x) => x.id === id);
  check(`suggestion ${id} is recorded`, !!s);
  if (s) {
    check(`suggestion ${id} states a status`, ['shipped', 'gated', 'open'].includes(s.status), s.status);
    check(`suggestion ${id} gives every option a trade-off`, s.options.every((o) => o.tradeoff && o.tradeoff.length > 10));
    check(`suggestion ${id} states a prompt-design improvement`, typeof s.prompt_improvement === 'string' && s.prompt_improvement.length > 20);
  }
}
for (const s of suggestions) {
  check(`suggestion ${s.id} has at least two options`, s.options.length >= 2, String(s.options.length));
  check(`suggestion ${s.id} gives every option a trade-off`, s.options.every((o) => o.tradeoff && o.tradeoff.length > 10));
}
for (const q of questions.unknown) {
  check(`question ${q.id} names an owner`, typeof q.owner === 'string' && q.owner.length > 2, q.owner);
  check(`question ${q.id} says how to close it`, typeof q.how === 'string' && q.how.length > 15);
  for (const id of q.sources) check(`question ${q.id} source ${id} exists`, SRC.has(id), id);
}
check('there is at least one blocking question recorded', questions.unknown.some((q) => q.blocks === true));

// 1.6 Measurement + ledger: five events, no cookies, no rows without provenance.
check('exactly five analytics events are defined', events.events.length === 5, String(events.events.length));
check('the ledger is empty and says so', ledger.rows.length === 0 && /empty/i.test(ledger.status));
check('the ledger defines the schema it will accept', ledger.columns.length >= 7);
const analyticsJs = fs.readFileSync(path.join(HERE, 'assets/analytics.js'), 'utf8');
const allowedNames = (analyticsJs.match(/^\s{4}(\w+): \[/gm) || []).map((m) => m.trim().split(':')[0]);
check('browser script allowlist matches the event schema', JSON.stringify(allowedNames.sort()) === JSON.stringify(events.events.map((e) => e.name).sort()), `${allowedNames.sort()} vs ${events.events.map((e) => e.name).sort()}`);
check('browser script sets no cookie or storage', !/document\.cookie|localStorage|sessionStorage|indexedDB/.test(analyticsJs));
check('browser script sends nothing without an https endpoint', /if \(!endpoint \|\| !\/\^https:/.test(analyticsJs));

// ═══ 2. generated site ════════════════════════════════════════════════════
if (!fs.existsSync(path.join(OUT, 'index.html'))) {
  fail.push('generated site missing — run node tools/3b45b513/build.mjs first');
} else {
  const htmlFiles = [];
  const walk = (d) => {
    for (const f of fs.readdirSync(d)) {
      const p = path.join(d, f);
      if (fs.statSync(p).isDirectory()) walk(p);
      else if (f.endsWith('.html')) htmlFiles.push(p);
    }
  };
  walk(OUT);

  const rel = (f) => '/' + path.relative(OUT, f).split(path.sep).join('/');
  const sitemap = fs.readFileSync(path.join(OUT, 'sitemap.xml'), 'utf8');
  const sitemapUrls = [...sitemap.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => m[1]);
  const feed = fs.readFileSync(path.join(OUT, 'feed.xml'), 'utf8');

  // 2.1 Well-formed-ish XML for the sitemap and feed.
  check('sitemap declares the urlset namespace', /<urlset xmlns="http:\/\/www\.sitemaps\.org\/schemas\/sitemap\/0\.9">/.test(sitemap));
  check('feed declares rss 2.0', /<rss version="2\.0"/.test(feed));
  check('feed has a self link', /<atom:link href="[^"]+\/feed\.xml" rel="self"/.test(feed));
  check('feed has one item per guide', [...feed.matchAll(/<item>/g)].length === guides.length, `${[...feed.matchAll(/<item>/g)].length} vs ${guides.length}`);
  for (const g of guides) check(`feed links guide ${g.slug}`, feed.includes(`${BASE}/guides/${g.slug}/`));

  for (const f of htmlFiles) {
    const html = fs.readFileSync(f, 'utf8');
    const name = rel(f);
    const text = html.replace(/<script[\s\S]*?<\/script>/g, ' ').replace(/<style[\s\S]*?<\/style>/g, ' ').replace(/<[^>]+>/g, ' ');

    // 2.2 Disclosure: both statements, above <main>, repeated in the footer.
    const strip = (html.match(/<div class="disclosure-strip"[\s\S]*?<\/div>\s*<\/div>/) || [''])[0];
    check(`${name}: disclosure bar exists`, strip.length > 0);
    check(`${name}: FTC example sentence in the bar`, strip.includes(cfg.disclosure));
    check(`${name}: Associates statement in the bar`, strip.includes(cfg.associatesStatement));
    check(`${name}: disclosure bar appears before main`, html.indexOf('class="disclosure-strip"') < html.indexOf('<main'));
    check(`${name}: footer repeats both statements`, /<p class="disclosure-footer">[\s\S]*?<\/p>/.test(html) && (() => {
      const footer = (html.match(/<footer[\s\S]*<\/footer>/) || [''])[0];
      return footer.includes(cfg.disclosure) && footer.includes(cfg.associatesStatement);
    })());
    check(`${name}: has an analytics-endpoint meta tag`, /<meta name="analytics-endpoint"/.test(html));

    // 2.3 Amazon links: tagged, sponsored, and never a short link.
    for (const m of html.matchAll(/<a\b([^>]*)>/g)) {
      const attrs = m[1];
      const href = (attrs.match(/href="([^"]*)"/) || [])[1] || '';
      const rel = (attrs.match(/rel="([^"]*)"/) || [])[1] || '';
      let host = '';
      try { host = new URL(href).hostname; } catch { /* relative link */ }

      check(`${name}: no link.amazon anchor is published`, host !== 'link.amazon', href);

      if (/(^|\.)amazon\.com$/.test(host) && !['affiliate-program.amazon.com', 'sell.amazon.com'].includes(host)) {
        check(`${name}: Amazon link is marked sponsored`, /\bsponsored\b/.test(rel), href);
        check(`${name}: Amazon link carries the tracking tag`, new RegExp(`[?&]tag=${TAG}(&|$)`).test(href), href);
        const asin = (href.match(/\/dp\/([A-Z0-9]{10})\b/) || [])[1];
        check(`${name}: Amazon product link names a 10-character ASIN`, !!asin, href);
      }

      // 2.4 Internal links resolve to a real published file.
      if (href.startsWith(BASE) || href.startsWith('/')) {
        const clean = href.split('#')[0].split('?')[0];
        const inSite = clean.startsWith(BASE) ? clean.slice(BASE.length) : clean;
        const target = path.join(OUT, inSite === '' || inSite === '/' ? 'index.html' : (inSite.endsWith('/') ? path.join(inSite, 'index.html') : inSite));
        check(`${name}: internal link resolves ${clean}`, fs.existsSync(target) && fs.statSync(target).isFile(), target);
        if (href.includes('#')) {
          const id = href.split('#')[1];
          if (/flagged/.test(href)) {
            check(`${name}: flag anchor ${id} exists on a page`, fs.readFileSync(path.join(OUT, 'review/flagged/index.html'), 'utf8').includes(`id="${id}"`), id);
          }
        }
      }
    }

    // 2.5 What this publication refuses to publish.
    check(`${name}: no currency amount`, !/\$\s?\d/.test(html), (html.match(/.{0,30}\$\s?\d.{0,30}/) || [''])[0]);
    check(`${name}: no star-rating text`, !/\b\d\.\d\s*(?:out of 5|\/5)\s*stars?\b/i.test(text));
    // An affirmative testing claim is a fabrication. A sentence that denies testing
    // ("none of them claims we tested anything") is the opposite, so context decides.
    const testingClaims = [...text.matchAll(/\bwe (?:tested|tried|cooked in|measured|handled)\b/gi)].filter((m) => {
      const around = (text.slice(Math.max(0, m.index - 70), m.index) + ' ' + text.slice(m.index, m.index + 45)).toLowerCase();
      return !/claim|not |never|nobody|no one|anything|something|whether|denies|did not/.test(around);
    });
    check(`${name}: no hands-on testing claim`, testingClaims.length === 0, testingClaims.map((m) => m[0]).join(', '));
    check(`${name}: no redirect or meta refresh`, !/http-equiv="refresh"|window\.location\s*=/.test(html));
    check(`${name}: no link shortener path`, !/href="\/[^"]*\/go\//.test(html));

    // 2.6 Images: local, alt-texted, and every caption says it is an illustration.
    for (const m of html.matchAll(/<img\b([^>]*)>/g)) {
      const attrs = m[1];
      const src = (attrs.match(/src="([^"]*)"/) || [])[1] || '';
      check(`${name}: image has alt text`, /alt="[^"]+"/.test(attrs), src);
      check(`${name}: image is served from this edition`, src.startsWith(BASE + '/assets/img/'), src);
      check(`${name}: image file exists`, fs.existsSync(path.join(OUT, src.slice(BASE.length))), src);
      check(`${name}: image loads lazily and decodes async`, /loading="lazy"/.test(attrs) && /decoding="async"/.test(attrs), src);
    }
    if (/<figure/.test(html)) {
      check(`${name}: figures are captioned`, /<figcaption[\s\S]*?<\/figcaption>/.test(html));
      check(`${name}: a caption says the image is not the product`, /illustration|not (the|a) (reviewed unit|photograph)/i.test(html));
    }

    // 2.7 SEO basics.
    check(`${name}: has a canonical URL`, /<link rel="canonical" href="https:\/\/karagemop466-tech\.github\.io\/Affil3\/counter-desk\//.test(html));
    check(`${name}: canonical is not double-prefixed`, !/Affil3\/Affil3\//.test(html));
    if (!html.includes('name="robots" content="noindex')) {
      const h1 = (html.match(/<h1[\s>]/g) || []).length;
      check(`${name}: exactly one h1`, h1 === 1, String(h1));
    }
    const title = (html.match(/<title>([\s\S]*?)<\/title>/) || ['', ''])[1];
    check(`${name}: title is 15-90 characters`, title.length >= 15 && title.length <= 90, `${title.length}: ${title}`);
    const desc = (html.match(/<meta name="description" content="([^"]*)"/) || ['', ''])[1];
    check(`${name}: meta description is 70-180 characters`, desc.length >= 70 && desc.length <= 185, `${desc.length}`);
    check(`${name}: page is in the sitemap`, name === '/404.html' ? true : sitemapUrls.includes(`https://karagemop466-tech.github.io/Affil3/counter-desk${name === '/index.html' ? '/' : name.replace(/index\.html$/, '')}`), name);
  }

  // 2.8 Publication-specific structural promises.
  const home = fs.readFileSync(path.join(OUT, 'index.html'), 'utf8');
  check('front page leads with products, not the register', home.indexOf('id="picks"') < home.indexOf('Three rules this site actually follows'));
  check('front page shows every product', products.every((p) => home.includes(p.observed.asin)));
  check('front page has a hero illustration with alt text', /hero-figure[\s\S]*?<img [^>]*alt="[^"]+"/.test(home));
  check('front page carries the seasonal block', home.includes(cfg.seasonal.title));
  check('shelf page publishes the intent register table', fs.readFileSync(path.join(OUT, 'shelf/index.html'), 'utf8').includes('The register behind the table'));
  for (const p of products) {
    const f = path.join(OUT, 'products', p.slug, 'index.html');
    check(`product page exists for ${p.id}`, fs.existsSync(f), p.slug);
    if (!fs.existsSync(f)) continue;
    const h = fs.readFileSync(f, 'utf8');
    check(`product page ${p.id} shows the specification table`, /<table class="spec-table">/.test(h));
    const blanks = Object.values(p.specs).filter((s) => !s.value || !String(s.value).trim()).length;
    const rendered = (h.match(/<td class="na">/g) || []).length;
    check(`product page ${p.id} renders exactly ${blanks} withheld cells`, rendered === blanks, `${rendered} rendered`);
    check(`product page ${p.id} has exactly one outbound buy link`, (h.match(/data-outbound/g) || []).length === 1);
    check(`product page ${p.id} links its sources`, p.sources.every((id) => h.includes(`>${id}<`) || h.includes(id)));
    check(`product page ${p.id} links back to its guide`, h.includes(`/guides/${p.guide_slug}/`));
    check(`product page ${p.id} states the link is unvalidated`, /Not yet confirmed against a tracking report/.test(h));
  }
  const cs = fs.readFileSync(path.join(OUT, 'counter-space/index.html'), 'utf8');
  check('fit finder ships its data island', /<script type="application\/json" id="fit-data">/.test(cs));
  check('fit finder names the clearance it adds', /two inches/.test(cs));
  check('fit finder works without JavaScript', /<noscript>/.test(cs));
  const flagged = fs.readFileSync(path.join(OUT, 'review/flagged/index.html'), 'utf8');
  for (const f of flags) check(`flag ${f.id} is published`, flagged.includes(`id="${f.id}"`));
  const rev = fs.readFileSync(path.join(OUT, 'review/index.html'), 'utf8');
  for (const [href, label] of [['/review/executive-summary/', 'Executive summary'], ['/review/flagged/', 'Flagged for review'], ['/review/questions/', 'Open questions'], ['/review/suggestions/', 'Suggestions and decisions'], ['/review/ledger/', 'Campaign ledger'], ['/review/measurement/', 'Measurement'], ['/review/compliance/', 'Disclosure and gates'], ['/review/sources/', 'Source register'], ['/review/register/', 'Product-intent register']]) {
    check(`operator index links ${label}`, rev.includes(href));
  }
  // Every page must reach the operator layer from its footer — one navigation group.
  for (const f of htmlFiles) {
    const html = fs.readFileSync(f, 'utf8');
    check(`${rel(f)}: footer links the operator index`, /<footer[\s\S]*\/review\/[\s\S]*<\/footer>/.test(html));
  }
  // 2.9 The edition's own robots file points at its own sitemap.
  const robots = fs.readFileSync(path.join(OUT, 'robots.txt'), 'utf8');
  check('robots points at this edition\'s sitemap', robots.includes(`Sitemap: https://karagemop466-tech.github.io/Affil3/counter-desk/sitemap.xml`));
}

// ═══ 3. report ════════════════════════════════════════════════════════════
const total = pass.length + fail.length;
if (!quiet) {
  console.log(`counter-desk gate: ${total} checks, ${pass.length} passed, ${fail.length} failed`);
}
if (fail.length) {
  for (const f of fail) console.log('  FAIL  ' + f);
  process.exit(1);
}
if (!quiet) console.log('  all clear');
