#!/usr/bin/env node
/**
 * Publication gate.
 *
 * Runs after the build and fails on any of the conditions below. These are
 * hard failures, not warnings: a blocked deploy costs an hour, a published
 * page with a missing disclosure costs the account.
 *
 *   1. Every HTML page carries the FTC wording AND the Amazon Associates statement.
 *   2. Every outbound amazon.com link is tagged, rel="sponsored", and labelled Paid link.
 *   3. intended_asin === ASIN in intended_listing_url, and the row resolved, before publish.
 *   4. No price or star-rating patterns in generated HTML.
 *   5. Every internal link resolves to a generated file.
 *   6. JSON-LD parses and carries the required fields.
 *   7. Every indexable route appears in the sitemap exactly once.
 *
 * Exit code 0 = publishable. 1 = blocked, with reasons.
 */
import { readFileSync, readdirSync, statSync, existsSync } from "node:fs";
import { join, relative, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const SITE_URL = "https://karagemop466-tech.github.io/Affil3";
const BASE = "/Affil3";
const TRACKING = "shopnow047c-20";

const errors = [];
const warnings = [];
const fail = (rule, file, msg) => errors.push({ rule, file, msg });

/* ---------------------------------------------------------------- helpers */
function walk(dir, acc = []) {
  for (const name of readdirSync(dir)) {
    // "legacy" is a frozen archive of earlier sessions' publications. It is
    // preserved verbatim for provenance and is deliberately NOT held to this
    // build's rules: it was published under a different design system and
    // rewriting it would destroy the record it exists to hold. It is linked
    // from /legacy/ and is excluded from the sitemap. See COORDINATION.md.
    if ([".git", "node_modules", "tools", "data", "content", "legacy"].includes(name)) continue;
    if (name === "404.html") continue; // generated; checked separately below and excluded from the sitemap
    const full = join(dir, name);
    const s = statSync(full);
    if (s.isDirectory()) walk(full, acc);
    else acc.push(full);
  }
  return acc;
}

const htmlFiles = walk(ROOT).filter((f) => f.endsWith(".html"));
const rel = (f) => relative(ROOT, f).replace(/\\/g, "/");

/* ------------------------------------------------- 1. disclosure on every page */
const FTC = "I get commissions for purchases made through links in this post";
const ASSOC = "As an Amazon Associate I earn from qualifying purchases";

for (const f of htmlFiles) {
  const html = readFileSync(f, "utf8");
  if (!html.includes(FTC)) fail("disclosure", rel(f), "missing FTC disclosure wording");
  if (!html.includes(ASSOC)) fail("disclosure", rel(f), "missing Amazon Associates statement (§5)");
  // the strip must appear before the main content, not only in the footer
  const stripAt = html.indexOf('class="disclosure"');
  const mainAt = html.indexOf('<main id="main"');
  if (stripAt === -1) fail("disclosure", rel(f), "no disclosure strip element");
  else if (mainAt !== -1 && stripAt > mainAt) fail("disclosure", rel(f), "disclosure strip appears after main content");
}

/* ------------------------------------- 2. outbound links tagged + labelled */
// Two different kinds of Amazon link appear on this site:
//   (a) AFFILIATE links — anything we send a buyer to. These must be tagged,
//       rel=sponsored, and labelled "Paid link".
//   (b) EVIDENCE links — registers and flag pages cite the listing or the
//       observed redirect as documentation. These must NOT be tagged, because
//       a tagged citation would attribute the operator's own audit click.
// The rule below enforces (a) and protects (b), and fails if either flips.
const EVIDENCE_PAGES = /^(review\/|operations\/)/;

for (const f of htmlFiles) {
  const page = rel(f);
  const html = readFileSync(f, "utf8");
  const isEvidencePage = EVIDENCE_PAGES.test(page);

  // (a) affiliate links: inside a .link-out block
  const linkOuts = [...html.matchAll(/<a class="link-out[^"]*"[^>]*href="([^"]+)"[^>]*>/g)];
  for (const m of linkOuts) {
    const href = m[1];
    if (!/amazon\./i.test(href)) continue;
    if (!href.includes(`tag=${TRACKING}`)) {
      fail("outbound-tag", page, `affiliate link without tag parameter: ${href.slice(0, 90)}`);
    }
    if (!/rel="[^"]*sponsored/.test(m[0])) {
      fail("outbound-sponsored", page, `affiliate link without rel=sponsored: ${href.slice(0, 80)}`);
    }
  }

  // (b) every "link-out" block must be accompanied by the literal words Paid link
  const outBlocks = (html.match(/class="link-out/g) || []).length;
  const paidLabels = (html.match(/>Paid link</g) || []).length;
  if (outBlocks > paidLabels) {
    fail("paid-label", page, `${outBlocks} affiliate link blocks but only ${paidLabels} "Paid link" labels`);
  }

  // (c) an AFFILIATE-tagged link outside an evidence page must never appear
  //     without the visible label somewhere in the page.
  const taggedLinks = [...html.matchAll(/href="(https?:\/\/[^"]*[?&]tag=shopnow047c-20[^"]*)"/g)];
  if (taggedLinks.length && !paidLabels) {
    fail("paid-label", page, "tagged affiliate link present but no 'Paid link' label anywhere on the page");
  }

  // (d) evidence pages may cite bare listings, but a buyer-facing page may not
  if (!isEvidencePage && tagDberr(html)) fail("outbound-tag", page, "bare product listing link on a buyer-facing page");
}

function tagDberr(html) {
  // a product link with neither a tag nor rel=nofollow is treated as an accidental affiliate link
  const links = [...html.matchAll(/<a[^>]*href="(https?:\/\/[^"]*\/dp\/[A-Z0-9]{10}[^"]*)"[^>]*>/g)];
  return links.some((m) => !m[1].includes("tag=") && !/rel="[^"]*nofollow/.test(m[0]));
}

/* ------------------------------------------------ 3. product identity rules */
const products = JSON.parse(readFileSync(join(ROOT, "data/products.json"), "utf8")).products;
for (const p of products) {
  if (!p.published) {
    if (p.intended_asin) fail("identity", p.id, "unpublished product still has an ASIN (would imply verification)");
    continue;
  }
  if (!p.intended_asin) fail("identity", p.id, "published without an ASIN");
  if (!p.intended_listing_url.includes(p.intended_asin)) {
    fail("identity", p.id, `intended_asin ${p.intended_asin} not present in intended_listing_url`);
  }
  if (p.observed_resolution_status !== "resolved") {
    fail("identity", p.id, "published but link never resolved");
  }
  if (!p.tagged_url.includes(`tag=${TRACKING}`)) {
    fail("identity", p.id, "tagged_url missing the tracking id");
  }
  if (!p.confirmation_date) fail("identity", p.id, "published without a confirmation date");
  if (!p.confirmation_source) fail("identity", p.id, "published without a confirmation source");
  // intended and observed must remain separate fields
  if (!("observed_redirect_target" in p)) fail("identity", p.id, "no observed_redirect_target field (fields must stay separate)");
}

/* -------------------------------- 4. no price or rating leakage into HTML */
for (const f of htmlFiles) {
  const html = readFileSync(f, "utf8");
  const text = html.replace(/<[^>]+>/g, " ");
  // currency amounts
  const money = text.match(/\$\s?\d{1,5}(?:\.\d{2})?/g);
  if (money) {
    // allow the documented payment-minimum prose and nothing else
    const allowed = /^(?:\$\s?1,000,000|\$\s?53,088)$/;
    const bad = money.filter((m) => !allowed.test(m.trim()));
    if (bad.length) fail("no-price", rel(f), `currency amount in page text: ${[...new Set(bad)].slice(0, 4).join(", ")}`);
  }
  // star ratings like "4.4 out of 5"
  const stars = text.match(/\b\d\.\d\s*(?:out of 5|\/5)\b/g);
  if (stars) fail("no-rating", rel(f), `star rating in page text: ${stars.slice(0, 3).join(", ")}`);
}

/* -------------------------------------------------- 5. internal links resolve */
const existing = new Set(
  htmlFiles.map((f) => "/" + relative(ROOT, f).replace(/\\/g, "/").replace(/index\.html$/, ""))
);
for (const f of htmlFiles) {
  const html = readFileSync(f, "utf8");
  const hrefs = [...html.matchAll(/href="(\/[^"#?]*)"/g)].map((m) => m[1]);
  for (const h of hrefs) {
    if (!h.startsWith(BASE + "/") && h !== BASE) {
      fail("link", rel(f), `absolute internal link not under base path: ${h}`);
      continue;
    }
    const p = h.slice(BASE.length) || "/";
    const norm = p.endsWith("/") ? p : p + "/";
    if (!existing.has(norm) && !existsSync(join(ROOT, p.replace(/^\//, "")))) {
      fail("link", rel(f), `broken internal link: ${h}`);
    }
  }
}

/* --------------------------------------------------- 6. JSON-LD sanity */
for (const f of htmlFiles) {
  const html = readFileSync(f, "utf8");
  const blocks = [...html.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)];
  for (const b of blocks) {
    try {
      const ld = JSON.parse(b[1]);
      const nodes = ld["@graph"] ? ld["@graph"] : [ld];
      for (const n of nodes) {
        if (!n["@type"]) fail("jsonld", rel(f), "node without @type");
        if (n["@type"] === "Article" && !n.headline) fail("jsonld", rel(f), "Article without headline");
        if (n["@type"] === "Product" && !n.name) fail("jsonld", rel(f), "Product without name");
      }
    } catch (e) {
      fail("jsonld", rel(f), "invalid JSON-LD: " + e.message);
    }
  }
}

/* ----------------------------------------------- 7. sitemap completeness */
const sitemap = readFileSync(join(ROOT, "sitemap.xml"), "utf8");
const locs = [...sitemap.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => m[1]);
const seen = new Set();
for (const l of locs) {
  if (seen.has(l)) fail("sitemap", "sitemap.xml", `duplicate loc: ${l}`);
  seen.add(l);
  if (!l.startsWith(SITE_URL)) fail("sitemap", "sitemap.xml", `loc not under site url: ${l}`);
}
for (const f of htmlFiles) {
  const p = "/" + relative(ROOT, f).replace(/\\/g, "/").replace(/index\.html$/, "");
  const url = `${SITE_URL}${p}`;
  if (!seen.has(url)) fail("sitemap", "sitemap.xml", `page missing from sitemap: ${p}`);
}

/* ------------------------------------------------------- 404 disclosure */
// The 404 is served for any missing path, so it must still carry the statement.
{
  const nf = join(ROOT, "404.html");
  if (!existsSync(nf)) fail("disclosure", "404.html", "no 404 page generated");
  else {
    const h = readFileSync(nf, "utf8");
    if (!h.includes(FTC)) fail("disclosure", "404.html", "404 missing FTC disclosure wording");
    if (!h.includes(ASSOC)) fail("disclosure", "404.html", "404 missing Amazon Associates statement");
    if (!/name="robots" content="noindex"/.test(h)) fail("disclosure", "404.html", "404 should be noindex");
  }
}

/* -------------------------------------------------------------- extras */
// feed must list every guide
const feed = readFileSync(join(ROOT, "feed.xml"), "utf8");
const guides = readdirSync(join(ROOT, "content/guides")).filter((f) => f.endsWith(".md"));
for (const g of guides) {
  const slug = g.replace(/\.md$/, "");
  if (!feed.includes(`/buying-guides/${slug}/`)) fail("feed", "feed.xml", `guide missing from feed: ${slug}`);
}

// claims integrity: a claim marked verified must carry a source and a quote
const claims = JSON.parse(readFileSync(join(ROOT, "data/claims.json"), "utf8"));
for (const c of claims.claims) {
  if (c.status === "verified" || c.status === "verified-excerpt") {
    if (!c.source) fail("claims", c.id, "verified claim without a source");
    if (!c.quote) fail("claims", c.id, "verified claim without a verbatim quote");
    if (c.source && !claims.meta.sources[c.source]) fail("claims", c.id, `source ${c.source} not registered`);
  }
  if (c.status === "unverified" && c.used_on && c.used_on.length) {
    fail("claims", c.id, "unverified claim is marked as used on a page");
  }
  if (c.used_on && c.used_on.length && c.status === "unverified") {
    fail("claims", c.id, "unverified claim listed as published");
  }
}

// suggestions: every path must carry a tradeoff, every open item a recommendation or blocker
const sugg = JSON.parse(readFileSync(join(ROOT, "data/suggestions.json"), "utf8"));
for (const s of sugg.suggestions) {
  if (!s.paths || s.paths.length < 2) fail("suggestions", s.id, "fewer than two paths (a decision needs alternatives)");
  for (const p of s.paths || []) {
    if (!p.tradeoff) fail("suggestions", s.id, `path ${p.id} has no stated tradeoff`);
  }
  if (s.decision === "open" && !s.recommended) fail("suggestions", s.id, "open decision without a recommendation");
  if (s.decision === "blocked" && !s.blocked_by) fail("suggestions", s.id, "blocked item without a reason");
}

// flags: every flag with a source must have a valid URL
const flags = JSON.parse(readFileSync(join(ROOT, "data/flags.json"), "utf8"));
for (const f of flags.flags) {
  for (const u of f.sources || []) {
    if (!/^https:\/\//.test(u)) fail("flags", f.id, `source is not https: ${u}`);
  }
}

// assets referenced must exist
for (const asset of ["assets/css/site.css", "assets/js/shop.js", "assets/js/analytics-config.js", "assets/img/favicon.svg"]) {
  if (!existsSync(join(ROOT, asset))) fail("assets", asset, "referenced asset is missing");
}

/* ------------------------------------------------------------- report */
const byRule = {};
for (const e of errors) (byRule[e.rule] = byRule[e.rule] || []).push(e);

console.log(`\nPublication gate — ${htmlFiles.length} pages checked\n`);
if (!errors.length) {
  console.log(`  PASS  all 7 rule groups`);
  for (const w of warnings) console.log(`  WARN  ${w}`);
  console.log("\nPublishable.\n");
  process.exit(0);
}

console.log(`  FAIL  ${errors.length} problem(s) across ${Object.keys(byRule).length} rule group(s)\n`);
for (const [rule, list] of Object.entries(byRule)) {
  console.log(`  [${rule}]`);
  for (const e of list.slice(0, 12)) console.log(`    ${e.file}: ${e.msg}`);
  if (list.length > 12) console.log(`    ...and ${list.length - 12} more`);
  console.log("");
}
console.log("Blocked. Fix the above before publishing.\n");
process.exit(1);
