#!/usr/bin/env node
// Session arena/259402a3-affil3 integrity pass.
// Cross-checks the data registers for internal consistency: every row carries
// sources or is blank-and-flagged, no value is inferred, tagged URLs are
// derived from observed ASINs, and nothing resembles a hallucinated figure.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const read = (p) => JSON.parse(fs.readFileSync(path.join(ROOT, p), 'utf8'));

const failures = [];
const passes = [];
const check = (name, ok, detail = '') => (ok ? passes : failures).push(`${name}${detail ? ': ' + detail : ''}`);

const productsDoc = read('data/products.json');
const products = productsDoc.products;
const sourcesDoc = read('data/sources.json');
const SOURCES = new Map(sourcesDoc.sources.map((s) => [s.id, s]));
const flagsDoc = read('data/flags.json');
const FLAGS = new Map(flagsDoc.flags.map((f) => [f.id, f]));
const suggestionsDoc = read('data/suggestions.json');
const questionsDoc = read('data/questions.json');
const eventsDoc = read('data/events.json');
const ledgerDoc = read('data/ledger.json');
const cfg = read('data/config.json');

const TAG = cfg.trackingId;
const ALLOWED_HOSTS = new Set([
  'affiliate-program.amazon.com', 'www.amazon.com', 'link.amazon',
  'developers.google.com', 'www.ftc.gov', 'www.ecfr.gov', 'www.fsis.usda.gov',
  'chefman.com', 'www.emerileveryday.com', 'chefiq.com', 'www.thermomaven.com',
]);

check('config trackingId present', TAG === 'shopnow047c-20', TAG);

// ---------- sources ----------
let sourceHostIssues = 0;
for (const s of sourcesDoc.sources) {
  if (!s.id || !s.url) { failures.push(`source missing id/url: ${JSON.stringify(s)}`); continue; }
  let host = '';
  try { host = new URL(s.url).hostname; } catch {}
  if (!s.url.startsWith('https://') || !ALLOWED_HOSTS.has(host)) { sourceHostIssues++; failures.push(`source ${s.id} not https/allowed: ${s.url}`); }
}
check('all sources https on allowed official hosts', sourceHostIssues === 0, `${sourceHostIssues} issues`);

// ---------- products ----------
check('five submitted product rows present', products.length === 5, String(products.length));
for (const p of products) {
  const pref = `${p.id} (${p.slug})`;
  const REQUIRED = ['id','category','submitted_url','submitted_token','intended_asin','official_listing_url',
    'confirmation_date','confirmation_source','confirmation_status','flags','observed_final_url','observed_asin',
    'observed_title','observed_breadcrumb','observed_date','sources','tagged_outbound_url','outbound_status'];
  for (const k of REQUIRED) {
    if (!(k in p)) failures.push(`${pref} missing field ${k}`);
  }
  check(`${pref} all required fields present`, REQUIRED.every((k) => k in p));
  check(`${pref} token length matches`, p.submitted_token.length === p.submitted_token_length, `${p.submitted_token.length} vs ${p.submitted_token_length}`);
  check(`${pref} token is 9 chars`, p.submitted_token.length === 9, p.submitted_token);
  check(`${pref} submitted_url matches token`, p.submitted_url === `https://link.amazon/${p.submitted_token}`);
  // intended fields blank + flagged (nothing confirmed)
  check(`${pref} intended ASIN blank`, p.intended_asin === '', p.intended_asin);
  check(`${pref} official listing URL blank`, p.official_listing_url === '', p.official_listing_url);
  check(`${pref} confirmation date blank`, p.confirmation_date === '', p.confirmation_date);
  check(`${pref} confirmation source blank`, p.confirmation_source === '', p.confirmation_source);
  check(`${pref} flagged as unverified`, p.flags.length > 0, String(p.flags.length));
  check(`${pref} confirmation_status says unverified`, /unverified/i.test(p.confirmation_status));
  // observed ASIN 10 chars and URL consistent
  if (p.observed_asin) {
    check(`${pref} observed ASIN 10 chars`, /^[A-Z0-9]{10}$/i.test(p.observed_asin), p.observed_asin);
    check(`${pref} observed URL = dp/ASIN`, p.observed_final_url === `https://www.amazon.com/dp/${p.observed_asin}`, p.observed_final_url);
  }
  // tagged URL derived from observed ASIN + tag
  const expectedTagged = p.observed_asin ? `https://www.amazon.com/dp/${p.observed_asin}?tag=${TAG}` : '';
  check(`${pref} tagged outbound URL = observed + tag`, p.tagged_outbound_url === expectedTagged, p.tagged_outbound_url);
  // sources exist
  for (const sid of p.sources) {
    if (!SOURCES.has(sid)) failures.push(`${pref} references unknown source ${sid}`);
  }
  check(`${pref} all sources exist`, p.sources.every((sid) => SOURCES.has(sid)));
  // flags exist
  for (const fid of p.flags) {
    if (!FLAGS.has(fid)) failures.push(`${pref} references unknown flag ${fid}`);
  }
  check(`${pref} all flags exist`, p.flags.every((fid) => FLAGS.has(fid)));
  // no price/rating/availability fields
  const keys = Object.keys(p).join(' ');
  check(`${pref} no price/rating/availability fields`, !/price|rating|availability|stock|commission/i.test(keys));
}
// observed ASINs are all distinct (no transposition)
const observed = products.map((p) => p.observed_asin).filter(Boolean);
check('observed ASINs all distinct', new Set(observed).size === observed.length, observed.join(','));

// ---------- flags ----------
for (const f of flagsDoc.flags) {
  check(`flag ${f.id} has severity`, !!f.severity);
  check(`flag ${f.id} has title`, !!f.title);
  check(`flag ${f.id} has detail`, !!f.detail);
  check(`flag ${f.id} has manual_step, resolution or action`, !!f.manual_step || !!f.resolution || !!f.action);
  for (const sid of (f.sources || [])) {
    if (!SOURCES.has(sid)) failures.push(`flag ${f.id} references unknown source ${sid}`);
  }
}
check('all flag sources exist', flagsDoc.flags.every((f) => (f.sources || []).every((sid) => SOURCES.has(sid))));

// ---------- suggestions ----------
for (const s of suggestionsDoc.suggestions) {
  check(`suggestion ${s.id} has topic and options`, !!s.topic && Array.isArray(s.options) && s.options.length >= 2);
  check(`suggestion ${s.id} has recommendation`, !!s.recommendation);
  check(`suggestion ${s.id} decision undecided`, s.decision === 'undecided' || s.decision === '' || s.decision === undefined, String(s.decision));
  for (const o of s.options) check(`suggestion ${s.id} option ${o.id} has label`, !!o.label);
}

// ---------- questions ----------
for (const q of questionsDoc.unknown || []) {
  check(`question ${q.id} has how_to_close`, !!q.how_to_close);
  check(`question ${q.id} has sources`, Array.isArray(q.sources));
  check(`question ${q.id} has blocking flag`, typeof q.blocking === 'boolean');
}
for (const d of questionsDoc.discovery || []) {
  check(`discovery ${d.id} has suggestion`, !!d.suggestion);
}

// ---------- ledger + events ----------
check('campaign ledger empty (no imported rows)', Array.isArray(ledgerDoc.rows) && ledgerDoc.rows.length === 0, String(ledgerDoc.rows.length));
check('five proposed events', eventsDoc.events.length === 5, String(eventsDoc.events.length));
const names = new Set(eventsDoc.events.map((e) => e.name));
check('event names are the five defined', names.has('page_view') && names.has('category_view') && names.has('product_view') && names.has('outbound_click') && names.has('guide_read_75'));

// ---------- summary ----------
console.log(`INTEGRITY PASS: ${passes.length} passed, ${failures.length} failed`);
if (failures.length) { console.log('FAILURES:'); failures.forEach((f) => console.log(' - ' + f)); process.exit(1); }
