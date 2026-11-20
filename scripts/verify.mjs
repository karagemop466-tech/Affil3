#!/usr/bin/env node
// Compliance and integrity gate for the built site (_site/) and src/data.
// Exits non-zero on any failure. Run after scripts/build.mjs.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const SITE = path.join(ROOT, '_site');
const DATA = path.join(ROOT, 'src/data');
const DISCLOSURE = 'As an Amazon Associate I earn from qualifying purchases.';
const ASIN_RE = /^[A-Z0-9]{10}$/;
const errors = [];
const warn = [];
const fail = (m) => errors.push(m);
const ok = [];

const load = (f) => JSON.parse(fs.readFileSync(path.join(DATA, f), 'utf8'));
const products = load('products.json');
const sources = load('sources.json');
const flags = load('flags.json');
const ledger = load('ledger.json');

const walk = (d) =>
  fs.readdirSync(d, { withFileTypes: true }).flatMap((e) =>
    e.isDirectory() ? walk(path.join(d, e.name)) : [path.join(d, e.name)],
  );
const allFiles = walk(SITE);
const htmlFiles = allFiles.filter((f) => f.endsWith('.html'));
const rel = (f) => path.relative(SITE, f).split(path.sep).join('/');

// 1. Disclosure present under masthead and in footer on every page.
for (const f of htmlFiles) {
  const html = fs.readFileSync(f, 'utf8');
  if (!html.includes(DISCLOSURE)) fail(`${rel(f)}: disclosure statement missing`);
  const strip = html.indexOf('class="disclosure" role="note"');
  const mast = html.indexOf('class="masthead"');
  const foot = html.indexOf('class="footer"');
  if (strip < 0 || mast < 0 || strip < mast) fail(`${rel(f)}: disclosure strip not under masthead`);
  if (foot < 0 || !html.slice(foot).includes(DISCLOSURE)) fail(`${rel(f)}: disclosure not repeated in footer`);
  if (/undefined|NaN|\[object Object\]/.test(html)) fail(`${rel(f)}: contains undefined/NaN/[object Object]`);
}
ok.push(`Disclosure check: ${htmlFiles.length} pages`);

// 2. Every link to an Amazon product or short link carries rel="sponsored".
let outbound = 0;
const aRe = /<a\s([^>]*)>/g;
for (const f of htmlFiles) {
  const html = fs.readFileSync(f, 'utf8');
  for (const m of html.matchAll(aRe)) {
    const attrs = m[1];
    const href = (attrs.match(/href="([^"]*)"/) || [])[1] || '';
    if (/amazon\.com\/dp\/|link\.amazon\//.test(href)) {
      outbound++;
      const relAttr = (attrs.match(/rel="([^"]*)"/) || [])[1] || '';
      if (!relAttr.split(/\s+/).includes('sponsored')) fail(`${rel(f)}: Amazon link without rel=sponsored: ${href}`);
    }
  }
}
ok.push(`Sponsored check: ${outbound} Amazon product links, all marked sponsored`);

// 3. Internal links and fragments resolve.
const idsByFile = new Map();
for (const f of htmlFiles) {
  const html = fs.readFileSync(f, 'utf8');
  idsByFile.set(f, new Set([...html.matchAll(/\sid="([^"]+)"/g)].map((m) => m[1])));
}
let internal = 0;
for (const f of htmlFiles) {
  const html = fs.readFileSync(f, 'utf8');
  for (const m of html.matchAll(/href="([^"]*)"/g)) {
    const href = m[1];
    if (!href || /^(https?:|mailto:|tel:|javascript:)/.test(href)) continue;
    internal++;
    const [pathPart, frag] = href.split('#');
    let target = pathPart ? path.resolve(path.dirname(f), pathPart) : f;
    if (pathPart && pathPart.endsWith('/')) target = path.join(target, 'index.html');
    if (pathPart && !path.extname(target)) target = path.join(target, 'index.html');
    if (!fs.existsSync(target)) {
      fail(`${rel(f)}: broken internal link ${href}`);
      continue;
    }
    if (frag && target.endsWith('.html')) {
      const ids = idsByFile.get(target) || new Set();
      if (!ids.has(frag)) fail(`${rel(f)}: missing anchor #${frag} on ${rel(target)}`);
    }
  }
}
ok.push(`Internal link check: ${internal} internal links resolve`);

// 4. Every table with a Source column has a source link in every body row.
for (const f of htmlFiles) {
  const html = fs.readFileSync(f, 'utf8');
  for (const t of html.matchAll(/<table[^>]*>([\s\S]*?)<\/table>/g)) {
    const thead = (t[1].match(/<thead>([\s\S]*?)<\/thead>/) || [])[1] || '';
    const headers = [...thead.matchAll(/<th[^>]*>([\s\S]*?)<\/th>/g)].map((m) => m[1].replace(/<[^>]+>/g, '').trim());
    const srcCol = headers.indexOf('Source');
    if (srcCol < 0) continue;
    const tbody = (t[1].match(/<tbody>([\s\S]*?)<\/tbody>/) || [])[1] || '';
    for (const row of tbody.matchAll(/<tr>([\s\S]*?)<\/tr>/g)) {
      if (/class="empty"/.test(row[1])) continue;
      const cells = [...row[1].matchAll(/<td[^>]*>([\s\S]*?)<\/td>/g)].map((m) => m[1]);
      if (!/href="https?:\/\//.test(cells[srcCol] || '')) fail(`${rel(f)}: table row without source link`);
    }
  }
}
ok.push('Table source check: every Source cell links to an https source');

// 5. Data integrity.
for (const p of products) {
  if (p.intended_asin && !ASIN_RE.test(p.intended_asin)) fail(`${p.id}: intended_asin is not a 10-character ASIN`);
  if (p.observed_redirect_asin && !ASIN_RE.test(p.observed_redirect_asin)) fail(`${p.id}: observed_redirect_asin is not a 10-character ASIN`);
  if (p.intended_asin && p.intended_asin === p.observed_redirect_asin) warn.push(`${p.id}: intended and observed ASIN are equal; confirm they were not merged`);
  if (!/^https:\/\/(www\.amazon\.com|link\.amazon)\//.test(p.source_url)) fail(`${p.id}: source_url is not an Amazon domain`);
  if (!sources.some((s) => s.id === p.source_id)) fail(`${p.id}: source_id not in register`);
  for (const fl of p.flags) if (!flags.some((x) => x.id === fl)) fail(`${p.id}: unknown flag ${fl}`);
  for (const key of ['price', 'rating', 'availability']) {
    if (p[key]) fail(`${p.id}: ${key} is set but no source value has been recorded for it`);
  }
  if (p.supplied_code_length !== p.supplied_code.length) fail(`${p.id}: supplied_code_length mismatch`);
}
for (const s of sources) if (!/^https:\/\//.test(s.url)) fail(`${s.id}: source url is not https`);
for (const f of flags) for (const sid of f.sources) if (!sources.some((s) => s.id === sid)) fail(`${f.id}: unknown source ${sid}`);
if (ledger.rows.length !== 0) warn.push(`ledger has ${ledger.rows.length} rows; each must cite an authorised first-party report`);
ok.push(`Data check: ${products.length} products, ${sources.length} sources, ${flags.length} flags`);

// 6. Sitemap lists every indexable page.
const sitemap = fs.readFileSync(path.join(SITE, 'sitemap.xml'), 'utf8');
for (const f of htmlFiles) {
  if (rel(f) === '404.html') continue;
  const loc = rel(f).replace(/index\.html$/, '');
  const expected = `<loc>https://karagemop466-tech.github.io/Affil3/${loc}</loc>`;
  if (!sitemap.includes(expected)) fail(`sitemap missing ${rel(f)}`);
}
ok.push('Sitemap check: all pages listed');

for (const w of warn) console.warn('WARN  ', w);
for (const o of ok) console.log('OK    ', o);
if (errors.length) {
  for (const e of errors) console.error('FAIL  ', e);
  console.error(`\n${errors.length} failure(s).`);
  process.exit(1);
}
console.log(`\nAll checks passed (${warn.length} warning(s)).`);
