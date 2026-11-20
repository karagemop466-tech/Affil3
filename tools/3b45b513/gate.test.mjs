#!/usr/bin/env node
/**
 * Unit tests for the Counter Desk gate.
 *
 * These do not re-test the live build; they test that the gate's own rules actually
 * fire. A publishing gate that cannot be made to fail is a decorative one, so each
 * test here mutates a rendering primitive or a data invariant and asserts the rule
 * notices. Run: node --test tools/3b45b513/gate.test.mjs
 */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '../..');
const DATA = path.join(ROOT, 'data/3b45b513');
const OUT = path.join(ROOT, 'counter-desk');
const read = (p) => JSON.parse(fs.readFileSync(path.join(DATA, p), 'utf8'));

const cfg = read('config.json');
const products = read('products.json').products;
const guides = read('guides.json').guides;
const flags = read('flags.json').flags;
const suggestions = read('suggestions.json').suggestions;
const questions = read('questions.json');
const events = read('events.json');
const ledger = read('ledger.json');
const sources = read('sources.json').sources;

/** Runs the gate against the committed output and returns its exit code + output. */
function runGate() {
  const r = spawnSync(process.execPath, [path.join(HERE, 'gate.mjs')], { encoding: 'utf8' });
  return { code: r.status, out: (r.stdout || '') + (r.stderr || '') };
}

/** Copies a generated file, applies a mutation, runs the gate, restores, returns output. */
function withMutation(relFile, mutate) {
  const file = path.join(OUT, relFile);
  const original = fs.readFileSync(file, 'utf8');
  try {
    fs.writeFileSync(file, mutate(original));
    const g = runGate();
    assert.equal(g.code, 1, 'gate must exit non-zero when the rule it claims to enforce is broken');
    return g.out;
  } finally {
    fs.writeFileSync(file, original);
  }
}

test('the data layer is internally consistent', () => {
  const ids = new Set(sources.map((s) => s.id));
  for (const p of products) {
    for (const id of [...p.sources, ...p.spec_sources, p.observed.source]) {
      assert.ok(ids.has(id), `${p.id} cites ${id}, which is not in the register`);
    }
  }
  for (const g of guides) for (const id of g.sources) assert.ok(ids.has(id), `${g.slug} cites ${id}`);
  for (const f of flags) for (const id of f.sources) assert.ok(ids.has(id), `${f.id} cites ${id}`);
});

test('intent and observation are never merged', () => {
  for (const p of products) {
    const intent = [p.intended_asin, p.official_listing_url, p.confirmation_date, p.confirmation_source];
    const filled = intent.filter(Boolean).length;
    assert.ok(filled === 0 || filled === 4, `${p.id} has ${filled} of 4 intent fields filled — that is a half-guess`);
    assert.notEqual(p.intended_asin, p.observed.asin, `${p.id} has copied its observation into its intent field`);
  }
});

test('every published buy link carries the tracking tag and points at the observed ASIN', () => {
  for (const p of products) {
    assert.equal(p.tagged_outbound_url, `https://www.amazon.com/dp/${p.observed.asin}?tag=${cfg.trackingId}`);
  }
});

test('every published specification has either a source or a written reason', () => {
  for (const p of products) {
    for (const [key, spec] of Object.entries(p.specs)) {
      const has = spec.value && String(spec.value).trim();
      if (has) assert.ok(spec.source, `${p.id}.${key} publishes a value with no source`);
      else assert.ok((spec.note || '').length > 15, `${p.id}.${key} is blank with no reason`);
    }
  }
});

test('the deliberately withheld figures stay withheld', () => {
  const p3 = products.find((p) => p.id === 'P3');
  const p5 = products.find((p) => p.id === 'P5');
  const p2 = products.find((p) => p.id === 'P2');
  assert.equal(p3.specs.power.value, '', 'wattage must stay blank while two official pages disagree');
  assert.equal(p3.specs.dimensions.value, '');
  assert.equal(p5.specs.battery.value, '');
  assert.equal(p2.specs.presets.value, '');
});

test('the four reader-facing pass items are all accounted for', () => {
  const ids = suggestions.map((s) => s.id);
  for (const id of ['SG-27', 'SG-28', 'SG-29', 'SG-30']) assert.ok(ids.includes(id), `${id} is missing`);
  const shipped = suggestions.filter((s) => ['SG-27', 'SG-28'].includes(s.id)).map((s) => s.status);
  assert.deepEqual(shipped, ['shipped', 'shipped']);
  for (const id of ['SG-29', 'SG-30']) {
    const s = suggestions.find((x) => x.id === id);
    assert.equal(s.status, 'gated', `${id} is a gated item and must not be described as shipped`);
  }
});

test('the working-hypothesis titles are labelled as hypotheses', () => {
  const hyps = guides.filter((g) => g.hypothesis);
  assert.ok(hyps.length >= 4, `expected at least four working-hypothesis guides, found ${hyps.length}`);
  for (const g of hyps) assert.ok(/working title/i.test(JSON.stringify(g)) || g.hypothesis === true);
});

test('no guide claims search volume, popularity or product superiority', () => {
  const text = JSON.stringify(guides).toLowerCase();
  for (const banned of ['search volume of', 'most popular', 'best seller', 'the best air fryer', 'we recommend buying']) {
    assert.ok(!text.includes(banned), `a guide contains an unsupported claim: "${banned}"`);
  }
});

test('every open question names an owner and a way to close it', () => {
  for (const q of questions.unknown) {
    assert.ok(q.owner && q.owner.length > 2, `${q.id} has no owner`);
    assert.ok(q.how && q.how.length > 15, `${q.id} has no closing step`);
  }
});

test('the ledger holds no rows and forbids the things it should', () => {
  assert.equal(ledger.rows.length, 0);
  assert.ok(ledger.prohibited.some((p) => /forecast/i.test(p)));
  assert.ok(ledger.columns.some((c) => c.name === 'provenance'), 'the ledger must ask for provenance');
});

test('the measurement schema is five events and no cookies', () => {
  assert.equal(events.events.length, 5);
  const js = fs.readFileSync(path.join(HERE, 'assets/analytics.js'), 'utf8');
  assert.ok(!/document\.cookie|localStorage|sessionStorage/.test(js));
});

test('the gate fails an untagged Amazon link', () => {
  const out = withMutation('shelf/index.html', (h) => h.replace(`?tag=${cfg.trackingId}`, ''));
  assert.match(out, /tracking tag/);
});

test('the gate fails an Amazon link without a sponsored rel', () => {
  const out = withMutation('shelf/index.html', (h) => h.replace('rel="sponsored noopener"', ''));
  assert.match(out, /marked sponsored/);
});

test('the gate fails a published price', () => {
  const out = withMutation('shelf/index.html', (h) => h.replace('</h1>', '</h1><p>On sale for $99.99.</p>'));
  assert.match(out, /currency amount/);
});

test('the gate fails a missing disclosure bar', () => {
  const out = withMutation('shelf/index.html', (h) => h.replace(/<div class="disclosure-strip"[\s\S]*?<\/div>\s*<\/div>/, ''));
  assert.match(out, /disclosure bar exists/);
});

test('the gate fails a broken internal link', () => {
  const out = withMutation('shelf/index.html', (h) => h.replace(`${cfg.basePath}/guides/`, `${cfg.basePath}/guidez/`));
  assert.match(out, /internal link resolves/);
});

test('the gate fails a testing claim', () => {
  const out = withMutation('shelf/index.html', (h) => h.replace('</h1>', '</h1><p>We tested this one for a month.</p>'));
  assert.match(out, /hands-on testing/);
});

test('the gate fails an image with no alt text', () => {
  // The shelf table is text-only by design, so mutate a page that actually carries art.
  const out = withMutation('products/chefman-6-quart-dual-basket-air-fryer/index.html', (h) => h.replace(/alt="[^"]+"/, 'alt=""'));
  assert.match(out, /alt text/);
});

test('the gate fails a link.amazon anchor', () => {
  const out = withMutation('shelf/index.html', (h) => h.replace('</h1>', '</h1><p><a href="https://link.amazon/B04G1MEwY">short</a></p>'));
  assert.match(out, /link\.amazon/);
});
