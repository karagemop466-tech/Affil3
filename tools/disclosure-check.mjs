#!/usr/bin/env node
/**
 * Disclosure check — the second gate.
 *
 * The editorial edition's tools/verify.mjs checks 1638 assertions about links,
 * sources, prices and coverage. This script checks the two things a reader
 * actually depends on and a build can silently lose:
 *
 *   1. The FTC's own example sentence for affiliate disclosure appears on every
 *      published page, and appears BEFORE the main content.
 *   2. The Amazon Associates statement required by Operating Agreement section 5
 *      appears on every published page.
 *
 * Why both: section 5 is a contractual obligation with Amazon, and the FTC
 * guidance is the legal one. A page with only the Amazon sentence can still fail
 * the FTC's plain-language test, and vice versa. Neither substitutes for the other.
 *
 * Also fails on a currency amount or a star rating in published text, because
 * this site publishes neither and a regression there is worse than a build break.
 */
import { readFileSync, readdirSync, statSync } from "node:fs";
import { join, dirname, relative } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");

// Only the published site at the repository root is checked.
//   legacy/      frozen editions, preserved as they shipped
//   editorial/   the editorial session's internal register build
//   crisp-index/ a separate publication by another session, namespaced away
//                from the root site; it is not linked from the sitemap and is
//                not this pipeline's output, so its design is not ours to change
//   counter/     Crisp & Counter, a namespaced publication by session 0a90f62c;
//                like crisp-index/ it runs its own gate (site-checks.yml) and its
//                design rules differ (it publishes date-stamped observed prices
//                and ratings, with the listing linked as source of truth)
//
// docs/ is deliberately NOT skipped. Only its retirement page remains there: an
// earlier edition published Amazon prices and star ratings, the whole edition
// was removed, and a single noindex redirect page now stands in its place so
// old links keep resolving. The exemption below applies only to that page (no
// Amazon links, no tag, noindex); see FLG-031.
const SKIP = new Set([".git", "node_modules", "legacy", "editorial", "crisp-index", "counter", "src", "tools", "data", "analytics-data", "site-src", "shopnow/content", "content"]);

// site-src/ (and shopnow/content, content/) hold build inputs — partial templates and markdown —
// the same category as src/; their rendered output at countertop-notes/ IS walked below.
const FTC = "I get commissions for purchases made through links in this post";
const ASSOC = "As an Amazon Associate I earn from qualifying purchases";

function walk(dir, acc = []) {
  for (const name of readdirSync(dir)) {
    if (SKIP.has(name)) continue;
    const full = join(dir, name);
    if (statSync(full).isDirectory()) walk(full, acc);
    else if (full.endsWith(".html")) acc.push(full);
  }
  return acc;
}

const problems = [];
const pages = walk(ROOT);

for (const f of pages) {
  const page = relative(ROOT, f);
  const html = readFileSync(f, "utf8");

  // A page that carries no affiliate link and no product claim needs no affiliate
  // disclosure. Rather than trusting a marker, verify it: count outbound Amazon
  // links and affiliate tags. /docs/ is retired and must stay link-free.
  const amazonLinks = (html.match(/https?:\/\/(?:[a-z0-9-]+\.)*amazon\.com\//gi) || []).length;
  const tagged = /[?&]tag=shopnow047c-20\b/.test(html);
  const disclosureFree = page.startsWith("docs/") && amazonLinks === 0 && !tagged
    && /<meta name="robots" content="noindex/.test(html);
  if (disclosureFree) continue;

  if (!html.includes(FTC)) problems.push(`${page}: missing the FTC example disclosure sentence`);
  if (!html.includes(ASSOC)) problems.push(`${page}: missing the Amazon Associates statement (section 5)`);

  // Placement: the disclosure must precede the main content, not sit below it.
  const disc = html.indexOf(FTC);
  const main = html.indexOf("<main");
  if (disc !== -1 && main !== -1 && disc > main) {
    problems.push(`${page}: FTC disclosure appears after <main> rather than above the fold`);
  }

  // No price may reappear. The site links out for prices instead.
  const text = html.replace(/<script[\s\S]*?<\/script>/gi, " ").replace(/<[^>]+>/g, " ");
  const money = text.match(/\$\s?\d[\d,]*(?:\.\d{2})?/g);
  if (money) {
    const unique = [...new Set(money.map((m) => m.trim()))];
    problems.push(`${page}: currency amount in page text (${unique.slice(0, 3).join(", ")})`);
  }

  // Nor may a star rating.
  const stars = text.match(/\b\d\.\d\s*(?:out of 5|\/5)\b/g);
  if (stars) problems.push(`${page}: star rating in page text (${stars[0]})`);
}

console.log(`\nDisclosure check — ${pages.length} published pages\n`);
if (problems.length) {
  for (const p of problems.slice(0, 40)) console.log(`  FAIL  ${p}`);
  if (problems.length > 40) console.log(`  ...and ${problems.length - 40} more`);
  console.log(`\n  ${problems.length} problem(s). Not publishable.\n`);
  process.exit(1);
}
console.log("  PASS  both statements present and above the fold on every page");
console.log("  PASS  no price or rating text anywhere\n");
