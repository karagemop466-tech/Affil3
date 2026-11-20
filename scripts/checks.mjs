#!/usr/bin/env node
/*
 * ShopNow 047 - the compliance gate.
 *
 * The brief's Priority 5 asks for disclosures and API-policy checks to live *in the publishing
 * workflow* rather than in a document someone reads once. So they are code, they run on every
 * build, and a failure is a red CI run that blocks the merge. Eleven automated checks below, plus
 * the one thing no machine can verify (Associates Central enrolment), which is reported as an open
 * owner action instead of being quietly treated as done.
 *
 * Exit 0 = publishable. Exit 1 = do not merge, regardless of how the page looks.
 */
import fs from "node:fs";
import path from "node:path";
import url from "node:url";

const ROOT = path.resolve(path.dirname(url.fileURLToPath(import.meta.url)), "..");
const OUT = path.join(ROOT, "shopnow");
const READ = (p) => JSON.parse(fs.readFileSync(path.join(ROOT, p), "utf8"));

const site = READ("register/site.json");
const productsDoc = READ("register/products.json");
const sourcesDoc = READ("register/sources.json");
const linksDoc = READ("register/links.json");
const compliance = READ("register/compliance.json");
const TRACK = site.tracking_id;

const failures = [];
const notes = [];
let checked = 0;
const fail = (check, where, msg) => failures.push({ check, where, msg });
const walk = (dir, acc = []) => {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) walk(p, acc);
    else acc.push(p);
  }
  return acc;
};
const files = walk(OUT).filter((f) => !path.basename(f).startsWith("."));
const htmls = files.filter((f) => f.endsWith(".html"));
const rel = (f) => path.relative(OUT, f).split(path.sep).join("/");
const lineOf = (txt, idx) => txt.slice(0, idx).split("\n").length;

/* ------------------------------------------------------------------ C-01
   Disclosure present, and present above the fold, on every page. */
const SENTENCE = site.disclosure.required_text;
for (const f of htmls) {
  checked++;
  const t = fs.readFileSync(f, "utf8");
  const bodyStart = t.indexOf("<body");
  const body = t.slice(bodyStart);
  const first = body.indexOf(SENTENCE);
  const inFooter = (t.match(new RegExp(SENTENCE.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "g")) || []).length;
  if (first === -1) fail("C-01 disclosure", rel(f), "the required Associates sentence does not appear at all");
  else if (first > 2400) fail("C-01 disclosure", rel(f), `sentence appears ${first} chars into <body>; it must be above the fold, not only in the footer`);
  if (inFooter < 2) fail("C-01 disclosure", rel(f), `sentence appears ${inFooter}x; brief requires the strip AND the footer on every page`);
}

/* ------------------------------------------------------------------ C-02
   Every commerce anchor: tagged, sponsored+nofollow, labelled, not cloaked. */
const ANCHOR = /<a\b[^>]*>/g;
for (const f of htmls) {
  const t = fs.readFileSync(f, "utf8");
  for (const m of t.matchAll(ANCHOR)) {
    const a = m[0];
    const href = (a.match(/href="([^"]+)"/) || [])[1] || "";
    if (!/amazon\.com/.test(href)) continue;
    checked++;
    const isDpListing = /\/dp\//.test(href);
    const relAttr = (a.match(/rel="([^"]*)"/) || [])[1] || "";
    if (!relAttr.includes("sponsored")) fail("C-02 links", rel(f) + ":" + lineOf(t, m.index), `amazon anchor rel="${relAttr}" is missing 'sponsored' -> ${href.slice(0, 90)}`);
    if (isDpListing && !relAttr.includes("nofollow")) fail("C-02 links", rel(f) + ":" + lineOf(t, m.index), "product link must also carry nofollow for search-engine qualification");
    if (isDpListing) {
      const u = new URL(href.replace(/&amp;/g, "&"));
      if (u.searchParams.get("tag") !== TRACK) fail("C-02 links", rel(f) + ":" + lineOf(t, m.index), `tag=${u.searchParams.get("tag")} but site tracking id is ${TRACK}`);
      if (!/^[A-Z0-9]{10}$/.test(u.pathname.split("/dp/")[1] || "")) fail("C-02 links", rel(f) + ":" + lineOf(t, m.index), "the /dp/ path is not a 10-character ASIN - a 9-character short-link token is not an identifier");
    }
    // a purchase-driving anchor must be marked where the click happens
    const near = t.slice(Math.max(0, m.index - 900), Math.min(t.length, m.index + 900));
    if ((/data-aff=/.test(a) || /btn-primary/.test(a)) && !/[Ss]ponsored/.test(near)) fail("C-02 links", rel(f) + ":" + lineOf(t, m.index), "commerce link with no 'Sponsored' marking nearby");
  }
  // data-aff marks a purchase-intent anchor; it must point straight at amazon.com, one hop, no wrapper
  for (const m of t.matchAll(/<a\b[^>]*data-aff=[^>]*>/g)) {
    const h = (m[0].match(/href="([^"]+)"/) || [])[1] || "";
    if (!/^https:\/\/(?:www\.)?amazon\.com\//.test(h.replace(/&amp;/g, "&"))) fail("C-02 links", rel(f) + ":" + lineOf(t, m.index), `data-aff anchor points at "${h.slice(0, 60)}" - a purchase-driving link may not be routed through a redirect or cloaker`);
  }
}

/* ------------------------------------------------------------------ C-03
   No price, ever. Absolute and dumb on purpose: a rule with exceptions rots. */
for (const f of htmls) {
  const t = fs.readFileSync(f, "utf8");
  const hits = [...t.matchAll(/[$]\s?\d/g)];
  if (hits.length) fail("C-03 price guard", rel(f) + ":" + lineOf(t, hits[0].index), `currency figure reaches the published site (${hits.length}x). Program Content pricing may only come from an Amazon-served link or the catalog API; suppress the value or ship the API path.`);
  const star = t.match(/(\d\.\d)\s*(out of 5|stars)/i);
  if (star) fail("C-03 price guard", rel(f) + ":" + lineOf(t, star.index), `star rating "${star[0]}" published without a refreshable source`);
}

/* ------------------------------------------------------------------ C-04
   No claim of testing, no implied endorsement, no invented authority. */
const BANNED = (site.voice.banned_words || []).concat(["editor's choice", "our testers", "we benchmarked", "Amazon approved", "officially endorsed", "certified by Amazon"]);
/* Scope matters here. The machinery pages exist to *describe* these rules, so they necessarily
   quote the phrases they forbid; quoting a rule is not the same as asserting a claim under it.
   The guard therefore binds on everything a buyer reads: guides, products, clusters, compare,
   home, and the standing prose pages. It is not weakened for those pages at all. */
const MACHINERY = new Set(["dashboard", "sources", "suggestions", "decisions", "flagged-for-review", "executive-summary", "404"]);
const editorial = htmls.filter((f) => !MACHINERY.has(rel(f).split("/")[0].replace(/\.html$/, "")));
for (const f of editorial) {
  const t = fs.readFileSync(f, "utf8").toLowerCase();
  const textOnly = t.replace(/<script[\s\S]*?<\/script>/g, "").replace(/<[^>]+>/g, " ");
  for (const b of BANNED) {
    const i = textOnly.indexOf(String(b).toLowerCase());
    if (i !== -1) fail("C-04 claim guard", rel(f), `banned phrase "${b}" - no test was run and no endorsement is implied. Reword or go run the test.`);
  }
  const vol = textOnly.match(/(search volume|monthly searches|trending (product|keyword)|most (searched|popular) on google)/);
  if (vol) fail("C-04 claim guard", rel(f), `demand claim "${vol[0]}" with no measurement source in register/sources.json`);
}

/* ------------------------------------------------------------------ C-05
   Program Content: no Amazon catalog imagery, no Amazon CDN of any kind. */
for (const f of files) {
  const t = fs.readFileSync(f, "utf8");
  const hit = t.match(/(?:src|href|url|content)="[^"]*(m\.media-amazon\.com|images-na\.ssl-images-amazon\.com|completion\.amazon\.com\/complete\/)[^"]*"/);
  if (hit) fail("C-05 program content", rel(f), `loads a resource from ${hit[1]} - Program Content images require the licensed API/widget path`);
}

/* ------------------------------------------------------------------ C-06
   Privacy: no third-party scripts, no cookies, no storage identity in shipped JS. */
for (const f of files.filter((x) => x.endsWith(".js") || x.endsWith(".html"))) {
  const t = fs.readFileSync(f, "utf8").replace(/\/\*[\s\S]*?\*\//g, "").replace(/(^|\n)\s*\/\/[^\n]*/g, "\n");
  if (/document\.cookie|gtag|google-analytics|googletagmanager|doubleclick|facebook\.net|hotjar|clarity\.ms/.test(t)) fail("C-06 privacy", rel(f), "tracker or cookie access present");
  const foreign = [...t.matchAll(/<script[^>]+src="([^"]+)"/g)].map((m) => m[1]).filter((h) => !/^(?:\.\.\/|\/|.*\/assets\/)/.test(h) && !h.startsWith("data:"));
  if (foreign.length) fail("C-06 privacy", rel(f), `script loaded from outside this site: ${foreign.join(", ")}`);
  if (/\blocalStorage\b/.test(t) && !/sessionStorage/.test(t)) fail("C-06 privacy", rel(f), "persistent localStorage use without sessionStorage - identity must not survive the tab");
}
for (const f of htmls) {
  const t = fs.readFileSync(f, "utf8");
  const priv = t.match(/<meta name="description" content="">/) || !/<meta name="description" content=".+">/.test(t);
  if (priv) fail("C-06 head", rel(f), "missing meta description - the search snippet is not optional");
  if (!/<link rel="canonical" href="https?:/.test(t)) fail("C-06 head", rel(f), "missing absolute canonical URL");
}

/* ------------------------------------------------------------------ C-07
   Verification guard: nothing may be published as fact without a source row. */
const srcIds = new Set(sourcesDoc.sources.map((s) => s.id));
for (const p of productsDoc.products) {
  checked++;
  if (!("intended_asin" in p) || !("observed_redirect_target" in p)) fail("C-07 verification", p.id, "intended and observed identifiers must be separate fields (brief requirement)");
  if (p.intended_asin && p.observed_redirect_target?.asin && p.intended_asin !== p.observed_redirect_target.asin && !p.intended_asin_status) fail("C-07 verification", p.id, "intended ASIN disagrees with observed ASIN with no explanation recorded");
  for (const [k, v] of Object.entries(p.published_fields)) {
    if (v === null) continue;
    if (["price", "availability", "star_rating", "review_count", "commission_rate", "specifications"].includes(k)) fail("C-07 verification", `${p.id}.${k}`, "volatile field is populated while S02/S07 are unresolved - blank it and flag it");
  }
  if (p.status && /verified/i.test(p.status) && !/not|un/i.test(p.status) && !p.confirmation?.source_id) fail("C-07 verification", p.id, "row claims verified without a source id");
}
for (const s of sourcesDoc.sources) {
  for (const c of s.verified_claims || []) {
    if (c.status === "verbatim" && !s.url) fail("C-07 verification", `${s.id}/${c.claim_id}`, "marked verbatim but carries no URL to check it against");
    if (c.status === "unresolved" && c.effect_on_this_project == null && c.why_unresolved == null) fail("C-07 verification", `${s.id}/${c.claim_id}`, "unresolved with no statement of what was therefore withheld");
  }
}
for (const l of linksDoc.links) {
  if (l.validated && !(l.destination_confirmed && l.tracking_report_confirmed)) fail("C-07 verification", l.product_id, "link marked validated without both destination and tracking-report confirmation");
  if (l.candidate_url && new URL(l.candidate_url).searchParams.get("tag") !== TRACK) fail("C-07 verification", l.product_id, "candidate link is not tagged with the site tracking id");
}
notes.push(`C-07: ${productsDoc.products.length} product rows, ${linksDoc.links.length} link rows, ${sourcesDoc.sources.length} source rows cross-checked`);

/* ------------------------------------------------------------------ C-08
   Control matrix must match reality: every 'passing' control has a gate. */
for (const c of compliance.controls) {
  if (c.status.startsWith("passing") && !c.gate) fail("C-08 controls", c.id, "claimed passing with no automated gate defined");
  if (c.source_id && !srcIds.has(c.source_id)) fail("C-08 controls", c.id, `cites ${c.source_id}, which is not in the source register`);
}

/* ------------------------------------------------------------------ C-09
   Internal link integrity: no page may point at a path that does not exist. */
const ROOTPATH = new URL(site.base_url).pathname.replace(/\/$/, "");
const present = new Set();
for (const f of files) {
  let r = "/" + rel(f);
  present.add(r);
  if (r.endsWith("/index.html")) present.add(r.replace(/index\.html$/, ""));
  if (r.endsWith("/404.html")) present.add("/404.html");
}
const linkGraph = {};
for (const f of htmls) {
  const t = fs.readFileSync(f, "utf8");
  linkGraph[rel(f)] = [];
  for (const m of t.matchAll(/(?:href|src)="([^"]+)"/g)) {
    let h = m[1].replace(/&amp;/g, "&");
    if (/^(https?:|mailto:|data:|#)/.test(h)) continue;
    if (ROOTPATH && h.startsWith(ROOTPATH + "/")) h = h.slice(ROOTPATH.length);
    if (!h.startsWith("/")) continue;
    const clean = h.split("#")[0].split("?")[0];
    if (!clean || clean === "/") { linkGraph[rel(f)].push("/index.html"); continue; }
    linkGraph[rel(f)].push(clean);
    checked++;
    if (!present.has(clean) && !present.has(clean + "index.html") && !present.has(clean.replace(/\/$/, "") + "/")) {
      fail("C-09 broken link", rel(f) + ":" + lineOf(t, m.index), `internal target does not exist: ${clean}`);
    }
  }
}

/* ------------------------------------------------------------------ C-10
   Sitemap, feed and robots cover exactly the published pages. */
const sitemap = fs.readFileSync(path.join(OUT, "sitemap.xml"), "utf8");
const feed = fs.readFileSync(path.join(OUT, "feed.xml"), "utf8");
const robots = fs.readFileSync(path.join(OUT, "robots.txt"), "utf8");
const BASE = site.base_url.replace(/\/$/, "");
const smUrls = new Set([...sitemap.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => m[1]));
for (const f of htmls) {
  if (rel(f) === "404.html") continue;
  const href = "/" + rel(f).replace(/index\.html$/, "");
  const want = BASE + (href === "/" ? "/" : href);
  if (!smUrls.has(want)) fail("C-10 discovery", rel(f), `not present in sitemap.xml as ${want}`);
}
for (const u of smUrls) {
  const p = u.replace(BASE, "").split("#")[0];
  if (!present.has(p) && !present.has(p + "index.html") && !p.endsWith(".xml") && !p.endsWith(".txt")) fail("C-10 discovery", "sitemap.xml", `sitemap lists ${u}, which does not exist`);
}
if (!robots.includes(BASE + "/sitemap.xml")) fail("C-10 discovery", "robots.txt", "no Sitemap: line pointing at the canonical sitemap");
if (!/feed\.xml/.test(robots) && !htmls.every((f) => fs.readFileSync(f, "utf8").includes("feed.xml"))) fail("C-10 discovery", "site", "feed is not advertised from every page");
const feedLinks = [...feed.matchAll(/<link>([^<]+)<\/link>/g)].map((m) => m[1]);
for (const l of feedLinks) {
  const p = l.replace(BASE, "");
  if (!present.has(p) && !present.has(p.replace(/\/$/, "") + "/index.html")) fail("C-10 discovery", "feed.xml", `feed item links to ${l}, which does not exist`);
}
if (smUrls.size < htmls.length - 1) fail("C-10 discovery", "sitemap.xml", `only ${smUrls.size} urls for ${htmls.length - 1} publishable pages`);

/* ------------------------------------------------------------------ C-11
   No orphans: every page is reachable from the chrome or from another page. */
const inbound = {};
for (const k of Object.keys(linkGraph)) for (const target of linkGraph[k]) inbound[target] = (inbound[target] || 0) + 1;
for (const f of htmls) {
  const r = rel(f);
  if (r === "index.html" || r === "404.html") continue;
  const asDir = "/" + r.replace(/index\.html$/, "");
  const asFile = "/" + r;
  if (!inbound[asDir] && !inbound[asFile] && !inbound[asDir.replace(/\/$/, ".html")]) fail("C-11 orphan", r, "no other page links here - it will never be crawled or found");
}

/* ---------------------------------------------------------------- report */
const openActions = compliance.controls.filter((c) => c.status.startsWith("open")).map((c) => `${c.id}: ${c.rule}`);
console.log(`\n  ShopNow 047 - compliance gate\n  ${"—".repeat(64)}`);
console.log(`  pages scanned        ${htmls.length}`);
console.log(`  files scanned        ${files.length}`);
console.log(`  assertions evaluated ${checked}`);
console.log(`  failures             ${failures.length}`);
notes.forEach((n) => console.log(`  note  · ${n}`));
if (openActions.length) console.log(`  manual actions still open:\n${openActions.map((a) => "    ! " + a).join("\n")}`);
if (failures.length) {
  console.log(`\n  ${failures.length} FAILURE(S) - build is not publishable:\n`);
  const byCheck = {};
  failures.forEach((f) => (byCheck[f.check] = byCheck[f.check] || []).push(f));
  for (const c of Object.keys(byCheck)) {
    console.log(`   ${c}`);
    byCheck[c].slice(0, 12).forEach((f) => console.log(`     - ${f.where}\n       ${f.msg}`));
    if (byCheck[c].length > 12) console.log(`     … and ${byCheck[c].length - 12} more`);
  }
  console.log("");
  process.exit(1);
}
console.log("\n  PASS - disclosure, sponsored tagging, price suppression, claim guard,");
console.log("         verification guard, link integrity, sitemap/feed parity, no orphans.\n");
