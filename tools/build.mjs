#!/usr/bin/env node
/**
 * Static site builder.
 *
 * Reads data/*.json and content/guides/*.md, writes every HTML page, the
 * sitemap, the feed and robots.txt. No dependencies, no network access.
 *
 * Run: node tools/build.mjs
 */
import { readFileSync, writeFileSync, mkdirSync, existsSync, rmSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { SITE } from "./lib/layout.mjs";
import { buildShop } from "./pages/shop.mjs";
import { buildTrust } from "./pages/trust.mjs";
import { buildReview } from "./pages/review.mjs";
import { buildOps } from "./pages/ops.mjs";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");

export const readJson = (p) => JSON.parse(readFileSync(join(ROOT, p), "utf8"));
export const readText = (p) => readFileSync(join(ROOT, p), "utf8");

export const DATA = {
  products: readJson("data/products.json"),
  claims: readJson("data/claims.json"),
  suggestions: readJson("data/suggestions.json"),
  questions: readJson("data/questions.json"),
  flags: readJson("data/flags.json"),
  ledger: readJson("data/ledger.json"),
};

/** front-matter + body */
export function parseGuide(file) {
  const raw = readText(`content/guides/${file}`);
  const m = raw.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
  if (!m) throw new Error(`No front matter in ${file}`);
  const meta = {};
  for (const line of m[1].split("\n")) {
    const kv = line.match(/^([a-z_]+):\s*"?([\s\S]*?)"?\s*$/);
    if (kv) meta[kv[1]] = kv[2];
  }
  meta.products = (meta.products || "").split(",").map((s) => s.trim()).filter(Boolean);
  return { meta, body: m[2], file };
}

export const GUIDES = [
  "basket-or-oven-air-fryer.md",
  "air-fryer-capacity-checklist.md",
  "cleanup-and-counter-space.md",
  "questions-before-buying-multifunction.md",
  "knowing-when-food-is-done.md",
  "air-fryer-recipes-that-work.md",
].map(parseGuide);

export const published = DATA.products.products.filter((p) => p.published);

/** route registry, written by the page builders */
export const routes = [];
export function addRoute(path, { priority = 0.6, changefreq = "monthly", lastmod = SITE.published, inSitemap = true } = {}) {
  routes.push({ path, priority, changefreq, lastmod, inSitemap });
}

export const out = (path, content) => {
  const full = join(ROOT, path);
  mkdirSync(dirname(full), { recursive: true });
  writeFileSync(full, content, "utf8");
};

/** shared small helpers used across page modules */
export const esc = (s) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

/**
 * Rank a suggestion's impact/confidence/effort into a single 0-100 ordering
 * score, purely so a reviewer can triage the list. This is an editorial
 * heuristic, and the page says so; it is not a measured outcome.
 */
export function priorityScore(s) {
  const w = { critical: 4, high: 3, medium: 2, low: 1 };
  const base = (w[s.impact] ?? 1) * 20 + (w[s.confidence] ?? 1) * 5;
  const effortPenalty = { none: 0, low: 0, medium: 4, high: 8 }[s.effort] ?? 4;
  const stateBoost = { open: 8, deferred: 4, applied: 0, blocked: -6 }[s.decision] ?? 0;
  return Math.max(1, Math.min(100, base - effortPenalty + stateBoost));
}

const bump = (v) => String(v ?? "").replace(/[<>&"]/g, (c) => ({ "<": "&lt;", ">": "&gt;", "&": "&amp;", '"': "&quot;" }[c]));

function sitemap() {
  const urls = routes
    .filter((r) => r.inSitemap)
    .map(
      (r) => `  <url>
    <loc>${SITE.url}${r.path === "/" ? "/" : r.path}</loc>
    <lastmod>${r.lastmod}</lastmod>
    <changefreq>${r.changefreq}</changefreq>
    <priority>${r.priority.toFixed(1)}</priority>
  </url>`
    )
    .join("\n");
  return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls}
</urlset>
`;
}

function feed() {
  const items = GUIDES.map((g) => {
    const url = `${SITE.url}/buying-guides/${g.meta.slug}/`;
    return `    <item>
      <title>${bump(g.meta.title)}</title>
      <link>${url}</link>
      <guid isPermaLink="true">${url}</guid>
      <pubDate>${new Date(`${g.meta.published}T09:00:00Z`).toUTCString()}</pubDate>
      <category>${bump(g.meta.kicker)}</category>
      <description>${bump(g.meta.description)}</description>
    </item>`;
  }).join("\n");

  return `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>${SITE.name} — new buying guides</title>
    <link>${SITE.url}/buying-guides/</link>
    <atom:link href="${SITE.url}/feed.xml" rel="self" type="application/rss+xml" />
    <description>New question-shaped buying guides from the ShopNow Labs countertop desk.</description>
    <language>en-us</language>
    <lastBuildDate>${new Date(`${SITE.published}T09:00:00Z`).toUTCString()}</lastBuildDate>
${items}
  </channel>
</rss>
`;
}

const robots = `# ${SITE.name}
User-agent: *
Allow: /

# Dashboard and review surfaces are public and indexable on purpose:
# the brief asks for every finding to be reachable and reviewable.
Sitemap: ${SITE.url}/sitemap.xml
`;

function favicon() {
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="ShopNow Labs">
  <rect width="64" height="64" rx="14" fill="#171310"/>
  <text x="32" y="43" font-family="Georgia,serif" font-size="30" font-weight="600" fill="#fbf8f3" text-anchor="middle">S</text>
  <circle cx="49" cy="41" r="3.4" fill="#b8410f"/>
</svg>
`;
}

// ---- build ---------------------------------------------------------------
if (existsSync(join(ROOT, "review"))) rmSync(join(ROOT, "review"), { recursive: true, force: true });

buildShop({ out, addRoute, DATA, GUIDES, published, esc });
buildTrust({ out, addRoute, DATA, esc });
buildReview({ out, addRoute, DATA, GUIDES, published, esc, priorityScore });
buildOps({ out, addRoute, DATA, esc });

out("sitemap.xml", sitemap());
out("feed.xml", feed());
out("robots.txt", robots);
out("assets/img/favicon.svg", favicon());
out(".nojekyll", "");

const sm = sitemap().length;
console.log(`built ${routes.length} routes (${routes.filter((r) => r.inSitemap).length} in sitemap, ${sm} bytes)`);
for (const r of routes) console.log("  " + r.path);
