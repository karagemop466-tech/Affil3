#!/usr/bin/env node
/*
 * ShopNow 047 - static site builder.
 *
 * One rule matters more than the rest: no page is written by hand. Every URL in shop/ is
 * generated from register/*.json + content/*.md, so a claim cannot exist on the site without
 * first existing in the register. The companion gate (scripts/checks.mjs) fails the build when
 * that invariant is violated - a missing disclosure, a currency figure, an untagged Amazon
 * link, a broken internal path, a page missing from the sitemap.
 *
 * Zero dependencies on purpose: CI runs this on a bare Node install, with nothing to install
 * and nothing to compromise.
 */
import fs from "node:fs";
import path from "node:path";
import url from "node:url";

const ROOT = path.resolve(path.dirname(url.fileURLToPath(import.meta.url)), "..");
const OUT = path.join(ROOT, "shopnow");
const READ = (p) => JSON.parse(fs.readFileSync(path.join(ROOT, p), "utf8"));

const site = READ("register/site.json");
const productsDoc = READ("register/products.json");
const products = productsDoc.products;
const sourcesDoc = READ("register/sources.json");
const flagsDoc = READ("register/flags.json");
const suggDoc = READ("register/suggestions.json");
const quesDoc = READ("register/questions.json");
const linksDoc = READ("register/links.json");
const ledger = READ("register/ledger.json");
const measure = READ("register/measurement.json");
const compliance = READ("register/compliance.json");
const review = READ("register/repo_review.json");

const BASE = site.base_url.replace(/\/$/, "");
const ROOTPATH = new URL(BASE).pathname.replace(/\/$/, "");
const TRACK = site.tracking_id;
/* Every amazon.com/dp/ href is emitted pre-tagged, so no click on this site can be unattributed.
   The link *text* stays the raw URL we observed, so a reviewer still sees exactly what was checked. */
function amazonTagged(href) {
  if (!/amazon\.com\/dp\//.test(href) || /[?&]tag=/.test(href)) return href;
  const join = href.includes("?") ? "&" : "?";
  return href + join + "tag=" + TRACK + "&linkCode=ll1";
}
const TODAY = "2026-11-20";

/* ------------------------------------------------------- deterministic clean
   The build owns everything in shop/. Authored assets live in content/assets/ and authored
   reports in report/, so a clean step can never destroy a hand-written file. A stale
   pages must not survive a rename (a moved slug otherwise leaves an orphaned, unregistered
   URL that still 200s and still gets crawled), so generated output is cleared before writing. */
const GENERATED_DIRS = ["guides", "products", "clusters", "search", "dashboard", "sources", "suggestions", "decisions", "flagged-for-review", "executive-summary", "about", "methodology", "disclosure", "privacy", "compare"];
const GENERATED_FILES = ["index.html", "404.html", "sitemap.xml", "feed.xml", "robots.txt", "humans.txt", "build-info.json"];
fs.mkdirSync(OUT, { recursive: true });
for (const d of GENERATED_DIRS) fs.rmSync(path.join(OUT, d), { recursive: true, force: true });
for (const f of GENERATED_FILES) fs.rmSync(path.join(OUT, f), { force: true });
/* Assets are authored in content/assets/ and *copied* into the output tree, never stored inside it:
   the clean step below deletes generated files, and a hand-written file that lives in the output
   directory is a file one rebuild away from being destroyed. That is not a hypothetical - it happened
   during the /docs -> /shop move, which is why the copy is explicit and ordered before any page writes. */
fs.cpSync(path.join(ROOT, "content", "assets"), path.join(OUT, "assets"), { recursive: true, force: true });


/* ------------------------------------------------------------------ utils */
const esc = (s) => String(s == null ? "" : s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
const U = (href) => (href.startsWith("/") ? ROOTPATH + href : href);
const slugify = (s) => String(s).toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
const dateLong = (d) => new Date(d + "T12:00:00Z").toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric", timeZone: "UTC" });
const BLANK = '<span class="blank">not verified</span>';
const field = (v) => (v == null || v === "" ? BLANK : esc(v));

function inline(s) {
  let o = esc(s);
  o = o.replace(/`([^`]+)`/g, (m, c) => "<code>" + c + "</code>");
  o = o.replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, (m, t, href) => {
    if (href.startsWith("/")) return '<a href="' + U(href) + '">' + t + "</a>";
    const isCommerce = /amazon\.com/.test(href);
    if (/^https?:/.test(href) && isCommerce) return '<a href="' + amazonTagged(href) + '" rel="sponsored nofollow noopener noreferrer" target="_blank">' + t + "</a>";
    if (/^https?:/.test(href)) return '<a href="' + href + '" rel="noopener noreferrer" target="_blank">' + t + "</a>";
    return '<a href="' + href + '">' + t + "</a>";
  });
  o = o.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  o = o.replace(/(^|[\s(])\*([^*\n]+)\*(?=[\s).,!?:;]|$)/g, "$1<em>$2</em>");
  return o;
}

/* markdown subset: headings, paragraphs, lists, quotes, tables, rules */
function md(src) {
  const lines = src.replace(/\r/g, "").split("\n");
  const out = [];
  const heads = [];
  let i = 0;
  const para = [];
  const flush = () => { if (para.length) { out.push("<p>" + inline(para.join(" ")) + "</p>"); para.length = 0; } };
  const isRow = (l) => /^\s*\|/.test(l);
  const cells = (l) => l.trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map((c) => c.trim());
  while (i < lines.length) {
    const L = lines[i];
    if (/^\s*$/.test(L)) { flush(); i++; continue; }
    if (/^###\s+/.test(L)) { flush(); const t = L.replace(/^###\s+/, ""); heads.push({ level: 3, text: t, id: slugify(t.replace(/[*`]/g, "")) }); out.push(`<h3 id="${heads[heads.length - 1].id}">${inline(t)}</h3>`); i++; continue; }
    if (/^##\s+/.test(L)) { flush(); const t = L.replace(/^##\s+/, ""); heads.push({ level: 2, text: t, id: slugify(t.replace(/[*`]/g, "")) }); out.push(`<h2 id="${heads[heads.length - 1].id}">${inline(t)}</h2>`); i++; continue; }
    if (/^#\s+/.test(L)) { flush(); out.push("<h1>" + inline(L.replace(/^#\s+/, "")) + "</h1>"); i++; continue; }
    if (/^---\s*$/.test(L)) { flush(); out.push("<hr>"); i++; continue; }
    if (/^>\s?/.test(L)) { flush(); const q = []; while (i < lines.length && /^>\s?/.test(lines[i])) { q.push(lines[i].replace(/^>\s?/, "")); i++; } out.push("<blockquote><p>" + inline(q.join(" ")) + "</p></blockquote>"); continue; }
    if (isRow(L)) {
      flush();
      const rows = [];
      while (i < lines.length && isRow(lines[i])) { rows.push(lines[i]); i++; }
      const parsed = rows.map(cells).filter((r) => !r.every((c) => /^:?-{2,}:?$/.test(c)));
      if (!parsed.length) continue;
      let h = "<table><thead><tr>" + parsed[0].map((c) => "<th>" + inline(c) + "</th>").join("") + "</tr></thead><tbody>";
      for (let k = 1; k < parsed.length; k++) h += "<tr>" + parsed[k].map((c) => "<td>" + (c === "" ? "&nbsp;" : inline(c)) + "</td>").join("") + "</tr>";
      out.push(h + "</tbody></table>");
      continue;
    }
    if (/^[-*]\s+/.test(L)) { flush(); const it = []; while (i < lines.length && /^[-*]\s+/.test(lines[i])) { it.push(lines[i].replace(/^[-*]\s+/, "")); i++; } out.push("<ul>" + it.map((t) => "<li>" + inline(t) + "</li>").join("") + "</ul>"); continue; }
    if (/^\d+\.\s+/.test(L)) { flush(); const it = []; while (i < lines.length && /^\d+\.\s+/.test(lines[i])) { it.push(lines[i].replace(/^\d+\.\s+/, "")); i++; } out.push("<ol>" + it.map((t) => "<li>" + inline(t) + "</li>").join("") + "</ol>"); continue; }
    para.push(L.trim()); i++;
  }
  flush();
  return { html: out.join("\n"), heads };
}

function fm(src) {
  const m = src.match(/^---\n([\s\S]*?)\n---\n?/);
  if (!m) return { meta: {}, body: src };
  const meta = {};
  m[1].split("\n").forEach((l) => {
    const kv = l.match(/^([A-Za-z_]+):\s*(.*)$/);
    if (!kv) return;
    let v = kv[2].trim().replace(/^"(.*)"$/, "$1");
    if (/^\[.*\]$/.test(v)) v = v.slice(1, -1).split(",").map((x) => x.trim().replace(/^"|"$/g, ""));
    else if (/^\d+$/.test(v)) v = Number(v);
    meta[kv[1]] = v;
  });
  return { meta, body: src.slice(m[0].length) };
}
const loadMd = (p) => fm(fs.readFileSync(path.join(ROOT, p), "utf8"));

/* ------------------------------------------------------------- file state */
const pages = [];
const written = new Set();
function write(relPath, content) {
  const abs = path.join(OUT, relPath);
  fs.mkdirSync(path.dirname(abs), { recursive: true });
  fs.writeFileSync(abs, typeof content === "string" ? content.replace(/\n{3,}/g, "\n\n") : content);
  written.add(relPath);
}
function record(relPath, o) {
  const href = "/" + relPath.replace(/index\.html$/, "");
  pages.push({ relPath, href: href === "/" ? "/" : href, ...o });
}

/* ------------------------------------------------------------------ chrome */
function layout(o) {
  const canonical = BASE + (o.href === "/" ? "/" : o.href);
  const crumbs = o.crumbs || [];
  const strip = `<div class="strip" role="note" aria-label="Affiliate disclosure">
  <div class="strip-in"><span class="dot" aria-hidden="true"></span><span><strong>${esc(site.disclosure.required_text)}</strong> Links marked Sponsored pay us a commission. ${esc(site.brand)} has not been paid or supplied by any brand named here, and nothing here has been tested by us. <a href="${U("/disclosure/")}" style="white-space:nowrap">Full disclosure</a></span></div>
</div>`;
  const nav = `<nav class="main" aria-label="Primary"><div class="nav-in">
  <a href="${U("/")}"${o.active === "home" ? ' aria-current="page"' : ""}>${esc(site.brand.split(" ")[0])}</a>
${site.nav.reader.map((n) => `  <a href="${U(n.href)}"${o.active === n.href ? ' aria-current="page"' : ""}>${esc(n.label)}</a>`).join("\n")}
  <details class="mech"><summary>${esc(site.nav.machinery_label)}</summary><div class="pop">
    <a href="${U("/dashboard/")}">Source dashboard</a>
    <a href="${U("/suggestions/")}">Suggestions to review</a>
    <a href="${U("/decisions/")}">Open questions</a>
    <a href="${U("/flagged-for-review/")}">Flagged for review</a>
    <a href="${U("/sources/")}">Source register</a>
    <a href="${U("/executive-summary/")}">Executive summary</a>
    <a href="${U("/search/")}">Search</a>
  </div></details>
</div></nav>`;
  const footer = `<footer class="site"><div class="foot-in">
  <div class="foot-disclose"><strong>${esc(site.disclosure.required_text)}</strong>
  <p class="tiny" style="margin:.4rem 0 0">Repeated here because it belongs on every page, not only on a page you have to go looking for. A purchase is assigned to us by Amazon through your click and a session we cannot see. We publish no price, availability, rating or review figure, because we cannot refresh one. <a href="${U("/disclosure/")}">Disclosure</a> · <a href="${U("/privacy/")}">Privacy</a> · <a href="${U("/methodology/")}">Methodology</a></p></div>
  <div class="foot-cols">
${site.nav.footer_groups.map((g) => `  <div><h5>${esc(g.label)}</h5><ul>${g.items.map((it) => `<li><a href="${U(it.href)}">${esc(it.label)}</a></li>`).join("")}</ul></div>`).join("\n")}
  </div>
  <div class="foot-legal">
    <div>© ${new Date().getFullYear()} ${esc(site.brand)} · kitchen gear desk</div>
    <div><a href="${U("/sources/")}">${sourcesDoc.sources.length} source rows</a> · <a href="${U("/flagged-for-review/")}">${flagsDoc.flags.length} flagged</a> · <a href="${U("/feed.xml")}">RSS</a> · generated from a register, gated in CI</div>
  </div>
</div></footer>`;
  const bc = crumbs.length ? `<div class="breadcrumb" aria-label="Breadcrumb"><a href="${U("/")}">Home</a>${crumbs.map((c) => ` <span>/</span> ${c.href ? `<a href="${U(c.href)}">${esc(c.label)}</a>` : `<em>${esc(c.label)}</em>`}`).join("")}</div>` : "";
  return `<!doctype html>
<html lang="${site.language}"${o.clusterAttr ? ` data-cluster="${esc(o.clusterAttr)}"` : ""}>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>${esc(o.title)}</title>
<meta name="description" content="${esc(o.desc || site.promise)}">
<link rel="canonical" href="${canonical}">
<meta property="og:type" content="${o.ogType || "website"}">
<meta property="og:site_name" content="${esc(site.brand)}">
<meta property="og:title" content="${esc(o.title)}">
<meta property="og:description" content="${esc(o.desc || site.promise)}">
<meta property="og:url" content="${canonical}">
<meta property="og:image" content="${BASE}/assets/img/hero.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="alternate" type="application/rss+xml" title="${esc(site.brand)} — ${esc(site.tagline)}" href="${BASE}/feed.xml">
<link rel="icon" href="${U("/assets/favicon.svg")}" type="image/svg+xml">
<link rel="stylesheet" href="${U("/assets/style.css")}">
${o.jsonld ? `<script type="application/ld+json">${JSON.stringify(o.jsonld)}</script>` : ""}
</head>
<body>
<a class="skip" href="#top">Skip to content</a>
<header class="masthead"><div class="masthead-in">
  <a class="wordmark" href="${U("/")}">${esc(site.brand.split(" ")[0])}<span class="num">${esc(site.brand.split(" ").slice(1).join(""))}</span></a>
  <div class="kicker">Counter-top desk · ${esc(site.marketplace)}</div>
  <div class="tagline">${esc(site.tagline)}</div>
</div></header>
${strip}
${nav}
<main id="top">
${bc}
${o.body}
</main>
${footer}
<script src="${U("/assets/track.js")}" defer></script>
<script src="${U("/assets/app.js")}" defer></script>
${o.script ? `<script src="${U(o.script)}" defer></script>` : ""}
</body>
</html>`;
}

/* --------------------------------------------------------------- fragments */
const linkFor = (id) => linksDoc.links.find((l) => l.product_id === id) || {};
const isLive = (p) => !!(p.observed_redirect_target && p.observed_redirect_target.asin);
const liveProducts = products.filter(isLive);
const slugFor = (p) => p.slug || slugify(p.id);
const productHref = (p) => "/products/" + slugFor(p) + "/";
const productBySlug = {};
products.forEach((p) => { productBySlug[slugFor(p)] = p; });

function gapPanel(p) {
  const un = Object.entries(p.published_fields).filter(([, v]) => v === null).map(([k]) => k);
  if (!un.length) return "";
  return `<div class="panel panel-gap" data-gap-flag="${esc((p.flag_ids || []).join(" "))}" data-gap-fields="${esc(un.join(","))}">
  <h4>What we did not verify about this product</h4>
  <ul>${un.map((f) => `<li><strong>${esc(f.replace(/_/g, " "))}</strong> — ${esc(p.unverified_fields_reason || "no official source was obtainable in this session; nothing was inferred.")}</li>`).join("")}</ul>
  <p class="tiny" style="margin:.7rem 0 0">This box is not decoration. The same blanks are what <a href="${U("/flagged-for-review/")}">the review list</a> and <a href="${U("/decisions/")}">the open questions</a> exist to close, and a build check fails the moment any of these fields is filled without a source row behind it.</p>
</div>`;
}

function cardBlurb(p) {
  if (!isLive(p)) return "This link never resolved to a listing, so no card here would be honest. It stays in the register and off the shop floor.";
  const t = p.observed_redirect_target.listing_title_observed || "";
  let open;
  if (/dual/i.test(t)) open = "Two zones that finish together - the case for it is synchronising, not doubling capacity.";
  else if (/oven|toaster|multi-function|french door/i.test(t)) open = "Cabinet format: a door, racks, and room for one genuinely large item.";
  else if (/thermometer|probe/i.test(t)) open = "The instrument that decides whether any of the appliances above actually worked.";
  else open = "Single basket, shake-and-go, the least friction of the three shapes.";
  return open + " We quote the listing title as an observation and publish no price, rating or specification we could not confirm.";
}

function productCard(p, placement) {
  const l = linkFor(p.id);
  const name = p.published_fields.product_name_from_listing || "Unidentified product";
  const buy = l.candidate_url
    ? `<a class="btn btn-primary" href="${esc(l.candidate_url)}" rel="sponsored nofollow noopener noreferrer" target="_blank" data-aff="${p.id}" data-asin="${esc(l.asin_used || "")}" data-placement="${esc(placement)}">See it at Amazon</a>
      <button class="btn btn-ghost" type="button" data-copy-link="${esc(l.candidate_url)}" data-product="${p.id}"><span class="cl-text">Copy link</span></button>`
    : `<span class="btn btn-ghost" style="opacity:.55" aria-disabled="true">No link published</span>`;
  return `<article class="card product-card">
  <div class="thumb" role="img" aria-label="No product image. Amazon catalog imagery may only be displayed through a licensed Program Content path, which this site does not hold.">no image — licensing reason below</div>
  <div class="body">
    <div><span class="brand">${field(p.published_fields.brand)}</span>${p.published_fields.form_factor ? ` <span class="chip">${esc(p.published_fields.form_factor)}</span>` : ""}</div>
    <h3><a href="${U(productHref(p))}">${esc(name)}</a></h3>
    <p>${esc(cardBlurb(p))}</p>
    <div class="disclose-inline"><span class="chip chip-sponsored">Sponsored</span> ${esc(site.disclosure.link_level_text)}</div>
    <div class="foot">${buy}<span class="tiny muted">${isLive(p) ? `ASIN <code>${esc(p.observed_redirect_target.asin)}</code>` : '<span class="blank">unresolved</span>'}</span></div>
  </div>
</article>`;
}

function guideCard(g) {
  return `<article class="card">
  <div class="body">
    <div class="eyebrow">${esc(g.meta.cluster || "guide")} · ${g.meta.reading_time ? esc(String(g.meta.reading_time)) + " min read" : "guide"}</div>
    <h4><a href="${U("/guides/" + g.meta.slug + "/")}">${esc(g.meta.title)}</a></h4>
    <p>${esc(g.meta.description)}</p>
    <div class="foot"><a href="${U("/guides/" + g.meta.slug + "/")}">Read the guide →</a></div>
  </div>
</article>`;
}

/* ----------------------------------------------------------------- guides */
const guides = fs.readdirSync(path.join(ROOT, "content/guides")).filter((f) => f.endsWith(".md")).map((f) => {
  const doc = loadMd("content/guides/" + f);
  doc.file = f;
  return doc;
}).sort((a, b) => String(b.meta.date).localeCompare(String(a.meta.date)));

/* ------------------------------------------------------------------- home */
{
  const home = loadMd("content/home.md");
  const r = md(home.body);
  const body = `
<section class="hero">
  <div>
    <p class="tiny" style="letter-spacing:.14em;text-transform:uppercase;font-weight:700;color:var(--ink-faint)">${esc(home.meta.hero_kicker)}</p>
    <h1>${esc(home.meta.hero_title)}</h1>
    <p class="hero-body">${esc(home.meta.hero_body)}</p>
    <div class="cta">
      <a class="btn btn-primary" href="${U("/guides/")}">Start with the guides</a>
      <a class="btn btn-ghost" href="${U("/products/")}">The products</a>
      <a class="btn btn-ghost" href="${U("/methodology/")}">Why there are no prices</a>
    </div>
  </div>
  <figure><img src="${U("/assets/img/hero.jpg")}" alt="Two air fryers on a kitchen counter: one with a pull-out basket, one with an open cabinet door" width="860" height="660">
  <figcaption class="tiny muted" style="margin-top:.5rem">${esc(site.imagery.credit_line)}</figcaption></figure>
</section>
<div class="prose">${r.html}</div>
<section class="section">
  <div class="section-head"><span class="eyebrow">On the counter</span><h2>The four products we could resolve</h2><a class="more" href="${U("/products/")}">All ${products.length} register rows →</a></div>
  <p class="lede" style="margin-bottom:1.2rem">Five links were supplied. Four resolved to a live listing and are below; one did not, and will not be invented into a card. <a href="${U("/flagged-for-review/")}">See what was withheld</a>.</p>
  <div class="grid g2">${liveProducts.map((p) => productCard(p, "home-card")).join("\n")}</div>
</section>
<section class="section">
  <div class="section-head"><span class="eyebrow">Choose the shape first</span><h2>Two ways to buy one badly</h2><a class="more" href="${U("/compare/")}">Side by side →</a></div>
  <div class="grid g3">${site.clusters.map((c) => {
    const n = products.filter((p) => isLive(p) && p.published_fields.form_factor === (c.tags[0])).length;
    return `<article class="card card-hero"><div class="body"><div class="eyebrow">${esc(c.name)} · ${n} listed</div><h4>${esc(c.question)}</h4><p>${esc((site.categories.find((k) => k.slug === c.category) || {}).blurb || "")}</p><div class="foot"><a href="${U("/clusters/" + c.slug + "/")}">Open cluster →</a></div></div></article>`;
  }).join("\n")}</div>
</section>
<section class="section">
  <div class="section-head"><span class="eyebrow">The desk</span><h2>Guides worth ninety seconds each</h2><a class="more" href="${U("/guides/")}">All ${guides.length} →</a></div>
  <div class="grid g3">${guides.slice(0, 6).map(guideCard).join("\n")}</div>
</section>
<section class="section">
  <div class="grid g2">
    <div class="panel panel-note"><h4>What “${esc(site.tagline)}” commits us to</h4>
      <ul>
        <li>Every figure on the site resolves to a dated row in the <a href="${U("/sources/")}">source register</a>.</li>
        <li>${sourcesDoc.source_register_integrity.unresolved} of ${sourcesDoc.sources.length} of those rows are marked <em>unresolved</em> — printed, not hidden.</li>
        <li>No price appears anywhere. A build check rejects one if anyone types it in.</li>
        <li>No testing language, because there is no test kitchen. Each guide says so inside the guide.</li>
      </ul>
    </div>
    <div class="panel"><h4>Where the project actually stands</h4>
      <ul>
        <li><a href="${U("/suggestions/")}">${suggDoc.suggestions.length} suggestions</a> on the review board — ${suggDoc.summary.implemented} implemented, ${suggDoc.summary.awaiting_choice} waiting on a choice.</li>
        <li><a href="${U("/decisions/")}">${quesDoc.sections.reduce((a, s) => a + s.questions.length, 0)} open questions</a>; ${quesDoc.answers_required_before_first_decision.length} of them block the first real move.</li>
        <li>Campaign ledger: <strong>${ledger.row_count} rows</strong>, deliberately. Nothing to report yet, and no invented baseline.</li>
        <li>${flagsDoc.flags.length} items <a href="${U("/flagged-for-review/")}">flagged for review</a>, each with the one action that closes it.</li>
      </ul>
    </div>
  </div>
</section>`;
  write("index.html", layout({
    href: "/", active: "home", title: `${site.brand} — ${site.tagline}`, desc: home.meta.description, body, ogType: "website",
    jsonld: { "@context": "https://schema.org", "@type": "WebSite", name: site.brand, alternateName: site.brand + " kitchen desk", description: site.promise, url: BASE + "/", inLanguage: site.language,
      publisher: { "@type": "Organization", name: site.brand, description: site.imagery.credit_line },
      potentialAction: { "@type": "SearchAction", target: BASE + "/search/?q={query}", "query-input": "required name=query" } }
  }));
  record("index.html", { title: site.brand + " — " + site.tagline, desc: home.meta.description, date: TODAY, section: "front page" });
}

/* ---------------------------------------------------------------- guides */
{
  const idx = `<div class="section-head"><span class="eyebrow">The desk</span><h2>All guides</h2></div>
<p class="lede">Six pieces, each answering a question a buyer actually has. No product is called the best of anything, because nobody here cooked in one. What we can do is tell you which line of a listing to read, and which number to look for.</p>
<div class="grid g2">${guides.map(guideCard).join("\n")}</div>
<div class="panel panel-note" style="margin-top:2rem"><h4>On the wording of these titles</h4><p class="tiny" style="margin:0">Each topic came from the project brief as a working title. They are not chosen from search-volume data — this project has none — and no claim about popularity or ranking is made anywhere on this site. If that changes, <a href="${U("/methodology/")}">the methodology page</a> is where the evidence gets recorded.</p></div>`;
  write("guides/index.html", layout({ href: "/guides/", active: "/guides/", title: "Guides — " + site.brand, desc: "Question-shaped buying guides for air fryers, multi-cookers and cooking thermometers. What to check, what to measure, and what we could not verify.", body: idx, crumbs: [{ label: "Guides" }], jsonld: { "@context": "https://schema.org", "@type": "CollectionPage", name: "Guides", url: BASE + "/guides/", isPartOf: { "@type": "WebSite", url: BASE + "/" }, hasPart: guides.map((g) => ({ "@type": "CreativeWork", name: g.meta.title, url: BASE + "/guides/" + g.meta.slug + "/" })) } }));
  record("guides/index.html", { title: "Guides", desc: "All buying guides", date: TODAY, section: "guides" });

  guides.forEach((g) => {
    const r = md(g.body);
    const cl = site.clusters.find((c) => c.slug === g.meta.cluster) || null;
    const related = guides.filter((x) => x.meta.slug !== g.meta.slug).slice(0, 3);
    const toc = r.heads.filter((h) => h.level === 2);
    const body = `<article class="article">
  <header>
    <div class="article-meta">${esc(dateLong(g.meta.date))} · ${g.meta.reading_time} min read · ${esc((g.meta.tags || []).join(", "))}</div>
    <h1 class="article-title">${esc(g.meta.title)}</h1>
    <p class="lede">${esc(g.meta.description)}</p>
  </header>
  <div class="byline"><span class="who">${esc(site.desk_name)}</span><span>AI-assisted draft · human sign-off pending (see below)</span><span class="chip chip-ghost">no product was tested for this</span></div>
  <div class="prose">${r.html}</div>
  ${toc.length > 1 ? `<nav class="panel" aria-label="Sections"><h4>In this guide</h4><ul>${toc.map((h) => `<li><a href="#${h.id}">${esc(h.text)}</a></li>`).join("")}</ul></nav>` : ""}
  <div class="verdict"><h4>The one thing to do after reading this</h4><p>Pick the single number this guide says to check, and go find it on a listing. Not here — on the seller's page, where it is current. That is the whole method.</p></div>
  <div class="panel panel-note"><h4>Why this page has no rating, price or verdict</h4><p class="tiny" style="margin:0">Nobody at ${esc(site.brand)} has handled these products, and we will not write a sentence that implies we did. Prices and ratings are omitted because Amazon permits a site to display them only through its own served link or its catalog API, and this project holds no API credentials — a number we could not refresh would be a claim outliving its own accuracy. <a href="${U("/methodology/")}">Full reasoning</a>, and the <a href="${U("/flagged-for-review/")}">list of what is withheld</a>.</p></div>
  <section class="section"><div class="section-head"><span class="eyebrow">Keep going</span><h2 style="font-size:1.1rem">Related</h2></div><div class="grid g3">${related.map(guideCard).join("\n")}</div></section>
</article>`;
    const href = "/guides/" + g.meta.slug + "/";
    write(path.join("guides", g.meta.slug, "index.html"), layout({
      href, active: "/guides/", title: g.meta.title + " — " + site.brand, desc: g.meta.description, body,
      crumbs: [{ label: "Guides", href: "/guides/" }, { label: g.meta.title }], clusterAttr: g.meta.cluster, ogType: "article",
      jsonld: [
        { "@context": "https://schema.org", "@type": "Article", headline: g.meta.title, description: g.meta.description, datePublished: g.meta.date, dateModified: g.meta.date, inLanguage: site.language,
          author: { "@type": "Organization", name: site.desk_name, url: BASE + "/about/" },
          publisher: { "@type": "Organization", name: site.brand },
          mainEntityOfPage: { "@type": "WebPage", "@id": BASE + href }, isAccessibleForFree: true, keywords: (g.meta.tags || []).join(", "),
          about: cl ? { "@type": "Thing", name: cl.name } : undefined },
        { "@context": "https://schema.org", "@type": "BreadcrumbList", itemListElement: [{ "@type": "ListItem", position: 1, name: "Home", item: BASE + "/" }, { "@type": "ListItem", position: 2, name: "Guides", item: BASE + "/guides/" }, { "@type": "ListItem", position: 3, name: g.meta.title, item: BASE + href }] }
      ]
    }));
    record(path.join("guides", g.meta.slug, "index.html"), { title: g.meta.title, desc: g.meta.description, date: g.meta.date, section: "guides" });
  });
}

/* --------------------------------------------------------------- products */
{
  const rows = products.map((p) => `<tr><td class="num">${p.id}</td><td>${field(p.submitted_token)}<div class="tiny muted">${esc(p.submitted_url)}</div></td><td>${p.observed_redirect_target && p.observed_redirect_target.asin ? `<code>${esc(p.observed_redirect_target.asin)}</code>` : BLANK}</td><td>${field(p.published_fields.product_name_from_listing)}</td><td>${esc(p.status)}</td><td class="num">${field(p.observed_redirect_target ? p.published_fields.price : null)}</td></tr>`).join("");
  const idx = `<div class="section-head"><span class="eyebrow">Inventory</span><h2>Products</h2></div>
<p class="lede">Five links came in. Four are here because they resolved to a live listing we could read a title off. The fifth is in the table below with a blank where its name should be, because a blank is the only honest cell available.</p>
<div class="grid g2" style="margin:1.6rem 0 2rem">${liveProducts.map((p) => productCard(p, "products-index")).join("\n")}</div>
<div class="section-head"><span class="eyebrow">Register view</span><h2 style="font-size:1.1rem">Every row, including the withheld one</h2></div>
<div class="table-wrap"><table class="data"><thead><tr><th>ID</th><th>Submitted token</th><th>Observed ASIN</th><th>Listing title</th><th>Status</th><th>Price</th></tr></thead><tbody>${rows}</tbody></table></div>
<p class="tiny muted" style="margin-top:.6rem">The price column is blank on every row by policy, not by omission — see <a href="${U("/flagged-for-review/")}">FLG-002</a>. Intended ASIN and observed ASIN are stored separately in <code>register/products.json</code> and are never merged.</p>`;
  write("products/index.html", layout({ href: "/products/", title: "Products — " + site.brand, desc: "Every product this site lists, with the official source for each row and the fields we could not confirm.", body: idx, crumbs: [{ label: "Products" }], jsonld: { "@context": "https://schema.org", "@type": "ItemList", name: "Products", itemListElement: liveProducts.map((p, i) => ({ "@type": "ListItem", position: i + 1, name: p.published_fields.product_name_from_listing, url: BASE + productHref(p) })) } }));
  record("products/index.html", { title: "Products", desc: "Product index", date: TODAY, section: "products" });

  liveProducts.forEach((p) => {
    const l = linkFor(p.id);
    const o = p.observed_redirect_target;
    const cl = site.clusters.find((c) => c.tags[0] === p.published_fields.form_factor);
    const specRows = [
      ["Brand", p.published_fields.brand],
      ["Form factor", p.published_fields.form_factor],
      ["Price", null], ["Availability", null], ["Star rating", null], ["Review count", null], ["Commission rate", null],
      ["Interior dimensions", null], ["Warranty term", null], ["Dishwasher-safe claim", null]
    ];
    const body = `<article class="article">
  <div class="article-meta">${esc(dateLong(productsDoc.retrieval.accessed_date))} · listing resolved and recorded · ${esc(site.desk_name)}</div>
  <h1 class="article-title">${esc(p.published_fields.product_name_from_listing)}</h1>
  <p class="lede">${esc(cardBlurb(p))}</p>
  <div class="panel" style="display:flex;gap:.8rem;align-items:center;flex-wrap:wrap">
    <a class="btn btn-primary" href="${esc(l.candidate_url)}" rel="sponsored nofollow noopener noreferrer" target="_blank" data-aff="${p.id}" data-asin="${esc(l.asin_used)}" data-placement="product-page">See it at Amazon</a>
    <button class="btn btn-ghost" type="button" data-copy-link="${esc(l.candidate_url)}" data-product="${p.id}"><span class="cl-text">Copy the tagged link</span></button>
    <span class="chip chip-sponsored">Sponsored</span>
    <span class="tiny muted" style="flex:1;min-width:220px">${esc(site.disclosure.link_level_text)} Current price and stock are shown on Amazon's page, where they are Amazon's to state and are up to date.</span>
  </div>
  <div class="grid g2">
    <section class="section"><div class="section-head"><h2 style="font-size:1.1rem">What we confirmed</h2></div>
      <div class="table-wrap"><table class="data"><tbody>
        <tr><th>Submitted link</th><td><code>${esc(p.submitted_url)}</code></td></tr>
        <tr><th>Official listing</th><td><a class="cite" href="${esc(amazonTagged(p.official_listing_url))}" rel="sponsored nofollow noopener noreferrer" target="_blank"><code>${esc(p.official_listing_url)}</code></a></td></tr>
        <tr><th>Observed ASIN</th><td><code>${esc(o.asin)}</code></td></tr>
        <tr><th>Listing title</th><td>${esc(o.listing_title_observed)}</td></tr>
        <tr><th>Confirmed on</th><td>${esc(p.confirmation.confirmed_date)}</td></tr>
        <tr><th>How</th><td>${esc(p.confirmation.confirmed_by)}</td></tr>
        <tr><th>Intended ASIN</th><td>${p.intended_asin ? "<code>" + esc(p.intended_asin) + "</code>" : '<span class="blank">' + esc(p.intended_asin_status.split(" - ")[0]) + "</span>"}</td></tr>
      </tbody></table></div>
      <p class="tiny muted">The two ASIN fields are separate on purpose. “Intended” means what the owner asked us to promote; “observed” means what the short link actually served when we followed it on ${esc(productsDoc.retrieval.accessed_date)}. Nothing merges them. The citation above is shown as the raw URL we observed; its href carries this site's tag, so no click on this page is unattributed.</p>
    </section>
    <section class="section"><div class="section-head"><h2 style="font-size:1.1rem">What we could not confirm</h2></div>
      <div class="table-wrap"><table class="data"><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>
        ${specRows.map(([k, v]) => `<tr><td>${esc(k)}</td><td>${v ? esc(v) : BLANK}</td></tr>`).join("")}
      </tbody></table></div>
    </section>
  </div>
  ${gapPanel(p)}
  <section class="section"><div class="section-head"><span class="eyebrow">Before you buy</span><h2 style="font-size:1.1rem">The checks that matter for this shape</h2></div>
    <div class="grid g2">
      <article class="card"><div class="body"><h4><a href="${U("/guides/capacity-checklist/")}">Capacity, the honest version</a></h4><p>Single-layer floor area beats every quart figure in the title.</p></div></article>
      <article class="card"><div class="body"><h4><a href="${U("/guides/cleanup-and-counter-space/")}">Cleanup and counter cost</a></h4><p>Clearance, door arc, and what actually fits in a dishwasher.</p></div></article>
      <article class="card"><div class="body"><h4><a href="${U("/guides/read-a-listing/")}">Reading this listing in 90 seconds</a></h4><p>The order to read it in, and the four table rows worth your time.</p></div></article>
      <article class="card"><div class="body"><h4><a href="${U("/compare/")}">Shape comparison</a></h4><p>Basket, dual-basket, oven-style: what each one costs you.</p></div></article>
    </div>
    ${cl ? `<p class="tiny muted" style="margin-top:1rem">Part of the <a href="${U("/clusters/" + cl.slug + "/")}">${esc(cl.name)}</a> cluster.</p>` : ""}
  </section>
</article>`;
    const href = productHref(p);
    write(path.join("products", slugFor(p), "index.html"), layout({
      href, title: p.published_fields.product_name_from_listing + " — " + site.brand,
      desc: `${p.published_fields.product_name_from_listing}: what this site could confirm about the listing, and every field it could not. No price, rating or test claim.`,
      body, crumbs: [{ label: "Products", href: "/products/" }, { label: p.published_fields.product_name_from_listing }], ogType: "article",
      jsonld: [
        { "@context": "https://schema.org", "@type": "Product", name: p.published_fields.product_name_from_listing,
          brand: p.published_fields.brand ? { "@type": "Brand", name: p.published_fields.brand } : undefined,
          category: p.published_fields.form_factor, description: cardBlurb(p) },
        { "@context": "https://schema.org", "@type": "BreadcrumbList", itemListElement: [{ "@type": "ListItem", position: 1, name: "Home", item: BASE + "/" }, { "@type": "ListItem", position: 2, name: "Products", item: BASE + "/products/" }, { "@type": "ListItem", position: 3, name: p.published_fields.product_name_from_listing, item: BASE + href }] }
      ]
    }));
    record(path.join("products", slugFor(p), "index.html"), { title: p.published_fields.product_name_from_listing, desc: "Product record", date: TODAY, section: "products" });
  });
}

/* --------------------------------------------------------------- clusters */
{
  site.clusters.forEach((c) => {
    const list = liveProducts.filter((p) => p.published_fields.form_factor === c.tags[0]);
    const cat = site.categories.find((k) => k.slug === c.category);
    const guideFor = { "basket-air-fryers": "capacity-checklist", "dual-basket": "basket-vs-oven-style", "oven-style-multi-cookers": "multi-function-appliance-questions", "getting-the-temperature-right": "probe-not-timer" }[c.slug];
    const g = guides.find((x) => x.meta.slug === guideFor);
    const body = `<div class="section-head"><span class="eyebrow">${esc(cat ? cat.name : "cluster")}</span><h2>${esc(c.name)}</h2></div>
<p class="lede">${esc(c.question)} ${list.length ? "This is what we could resolve in this shape, and the reading that goes with it." : "Nothing in this shape resolved yet — an empty cluster is reported as empty rather than padded with the nearest neighbour."}</p>
${list.length ? `<div class="grid g2" style="margin:1.6rem 0">${list.map((p) => productCard(p, "cluster")).join("\n")}</div>` : `<div class="empty" style="margin:1.4rem 0">No product row in this shape passed resolution. The register keeps it at <a href="${U("/dashboard/")}">/dashboard/</a>.</div>`}
${g ? `<div class="panel panel-note"><h4>Read this first</h4><p class="tiny" style="margin:0"><a href="${U("/guides/" + g.meta.slug + "/")}"><strong>${esc(g.meta.title)}</strong></a> — ${esc(g.meta.description)}</p></div>` : ""}
<div class="section-head" style="margin-top:2.4rem"><h2 style="font-size:1.1rem">The checks this shape makes harder</h2></div>
<div class="prose"><ul>
${({
      "basket-air-fryers": ["<strong>Floor area, not volume.</strong> A round basket's usable capacity is its single-layer footprint; the quart figure includes headspace nobody can fill.", "<strong>Shake access.</strong> If the basket has to come fully out to turn the food, that is a workflow you are agreeing to twice a night.", "<strong>Dishwasher geometry.</strong> Basket height versus rack height is a real, checkable incompatibility."],
      "dual-basket": ["<strong>Two small cavities, not one big one.</strong> Anything taller than one basket's interior simply does not fit, however the total is advertised.", "<strong>Sync finish is the feature.</strong> If you rarely cook two foods at once, you are paying for a mode you will not use.", "<strong>One outlet, one draw.</strong> Both zones running together is the peak load; the manual, not the title, states it."],
      "oven-style-multi-cookers": ["<strong>Door arc and counter depth.</strong> A downward door needs front clearance no spec table will complain about.", "<strong>Which functions are load-bearing.</strong> A low temperature floor is what separates real dehydration from a warm fan.", "<strong>More parts, more tax.</strong> Door glass and crumb trays are where owners stop, and where resentment starts."],
      "getting-the-temperature-right": ["<strong>Probe heat rating.</strong> Air-fryer and grill environments exceed what an oven-only probe survives; the ceiling is stated in the manual.", "<strong>How the alarm reaches you.</strong> A notification you cannot hear in the next room is a light on a box in the kitchen.", "<strong>Where the tip sits.</strong> Ten millimetres of error in a thin cutlet reads as an empty basket."]
    }[c.slug] || []).map((x) => "<li>" + x + "</li>").join("\n")}
</ul></div>
<p class="tiny muted" style="margin-top:1rem">Cluster membership is assigned by the form factor recorded in <code>register/products.json</code>, which comes from the observed listing title — not from a category Amazon confirmed to us. ${esc(site.tagline)}: <a href="${U("/methodology/")}">how that is decided</a>.</p>`;
    const href = "/clusters/" + c.slug + "/";
    write(path.join("clusters", c.slug, "index.html"), layout({
      href, active: c.slug === "basket-air-fryers" || c.slug === "dual-basket" ? "/clusters/basket-air-fryers/" : c.slug === "oven-style-multi-cookers" ? "/clusters/oven-style-multi-cookers/" : null,
      title: c.name + " — " + site.brand, desc: c.question + " Every product in this shape we could resolve, plus the fields we could not verify.",
      body, crumbs: [{ label: "Clusters", href: "/products/" }, { label: c.name }],
      jsonld: { "@context": "https://schema.org", "@type": "CollectionPage", name: c.name, description: c.question, url: BASE + href, mainEntity: { "@type": "ItemList", itemListElement: list.map((p, i) => ({ "@type": "ListItem", position: i + 1, name: p.published_fields.product_name_from_listing, url: BASE + productHref(p) })) } }
    }));
    record(path.join("clusters", c.slug, "index.html"), { title: c.name, desc: c.question, date: TODAY, section: "clusters" });
  });
}

/* ---------------------------------------------------------------- compare */
{
  const dims = [
    ["Best single item", "Limited by a round, shallow footprint", "Same limit, twice over", "A rack, a tray, a whole dish"],
    ["Even browning unattended", "Needs a shake or a turn", "Needs a shake or a turn, per zone", "The fan and the rack do more of it"],
    ["Cleaning load", "One coated basket", "Two coated baskets", "Door glass, racks, crumb tray"],
    ["Counter footprint", "Smallest", "Widest of the basket types", "Deepest; needs a door arc"],
    ["Two foods at once", "No — sequential batches", "Its entire purpose", "Yes, with racks"],
    ["Preheat", "Short", "Short", "Longer cavity to fill"],
    ["Fits in a cupboard", "Usually", "Rarely", "Rarely"]
  ];
  const body = `<div class="section-head"><span class="eyebrow">Decision table</span><h2>Basket, dual-basket, or oven-style</h2></div>
<figure style="margin:0 0 1.8rem"><img src="${U("/assets/img/compare.jpg")}" alt="Top-down counter diagram: a single round basket footprint, two smaller side-by-side baskets, and a wide rectangular cabinet, each with dashed clearance margins" width="1600" height="640"><figcaption class="tiny muted" style="margin-top:.4rem">${esc(site.imagery.credit_line)}</figcaption></figure>
<p class="lede">Seven rows that predict daily use better than any brand comparison. Nothing here is a rating, a score, or a verdict about the products linked from this site — it is the shape of the trade-off, written so you can fill in the numbers from a listing yourself.</p>
<div class="table-wrap" style="margin:1.6rem 0"><table class="data"><thead><tr><th>What it costs you</th><th>Single basket</th><th>Dual basket</th><th>Oven-style cabinet</th></tr></thead><tbody>
${dims.map((r) => `<tr><td><strong>${esc(r[0])}</strong></td><td>${esc(r[1])}</td><td>${esc(r[2])}</td><td>${esc(r[3])}</td></tr>`).join("\n")}
</tbody></table></div>
<div class="panel panel-gap" data-gap-flag="FLG-002"><h4>Why there is no price row, and no star rating row</h4><p class="tiny" style="margin:0">Both would need to be current, and only Amazon may supply them current to a page like this one. A comparison table whose numbers were copied once and left there is worse than no table, because it borrows the authority of a table without the upkeep. <a href="${U("/flagged-for-review/")}">FLG-002</a> tracks getting the API access that would make the row possible.</p></div>
<h2>Then read the two guides that fill these cells in</h2>
<div class="grid g2">${["basket-vs-oven-style", "capacity-checklist", "cleanup-and-counter-space", "multi-function-appliance-questions"].map((s) => {
    const g = guides.find((x) => x.meta.slug === s);
    return g ? guideCard(g) : "";
  }).join("\n")}</div>
<div class="section-head" style="margin-top:2.4rem"><h2 style="font-size:1.1rem">The products, by shape</h2></div>
<div class="grid g2">${liveProducts.map((p) => productCard(p, "compare")).join("\n")}</div>`;
  write("compare/index.html", layout({ href: "/compare/", title: "Basket vs dual-basket vs oven-style — " + site.brand, desc: "A seven-row comparison of what each air fryer shape costs you in cleaning, clearance, and single-item capacity. No prices, because we cannot refresh them.", body, crumbs: [{ label: "Compare" }], jsonld: { "@context": "https://schema.org", "@type": "Table", about: "air fryer form factors" } }));
  record("compare/index.html", { title: "Compare shapes", desc: "Comparison table", date: TODAY, section: "compare" });
}

/* ---------------------------------------------------------- prose pages */
[["about", "Who writes here", "/about/"], ["methodology", "How we decide", "/methodology/"], ["disclosure", "Disclosure", "/disclosure/"], ["privacy", "Privacy", "/privacy/"]].forEach(([key, label, href]) => {
  const doc = loadMd("content/" + key + ".md");
  const r = md(doc.body);
  const title = doc.meta.title || label;
  const body = `<article class="article"><h1 class="article-title">${esc(title)}</h1><div class="prose">${r.html}</div></article>`;
  write(key + "/index.html", layout({ href, title: title + " — " + site.brand, desc: doc.meta.description || site.promise, body, crumbs: [{ label: title }], ogType: "article", jsonld: { "@context": "https://schema.org", "@type": "About" === title ? "AboutPage" : "WebPage", name: title, url: BASE + href, description: doc.meta.description } }));
  record(key + "/index.html", { title, desc: doc.meta.description || "", date: TODAY, section: key });
});

/* ------------------------------------------------------------- dashboard */
{
  const prodRows = products.map((p) => `<tr>
    <td class="num">${p.id}</td>
    <td><code>${esc(p.submitted_token)}</code><div class="tiny muted">${esc(p.submitted_url)}</div></td>
    <td class="num">${p.submitted_token_length}<div class="tiny muted">needs 10</div></td>
    <td>${p.intended_asin ? `<code>${esc(p.intended_asin)}</code>` : BLANK}</td>
    <td>${p.observed_redirect_target && p.observed_redirect_target.asin ? `<code>${esc(p.observed_redirect_target.asin)}</code>` : BLANK}</td>
    <td>${field(p.published_fields.product_name_from_listing)}</td>
    <td class="num">${field(p.published_fields.price)}</td>
    <td class="num">${field(p.published_fields.star_rating)}</td>
    <td>${esc(p.status)}</td>
    <td class="num tiny">${esc((p.flag_ids || []).join(" "))}</td>
  </tr>`).join("");
  const linkRows = linksDoc.links.map((l) => `<tr><td class="num">${l.product_id}</td><td>${l.asin_used ? `<code>${esc(l.asin_used)}</code>` : BLANK}</td><td class="tiny"><code>${esc(l.candidate_url || "—")}</code></td><td><span class="chip ${l.validated ? "chip-open" : "chip-warn"}">${esc(l.status)}</span></td><td class="tiny">${esc(l.note || l.asin_provenance || "")}</td></tr>`).join("");
  const ledCols = ledger.schema.columns.map((c) => "<th>" + esc(c.name) + "</th>").join("");
  const body = `<div class="section-head"><span class="eyebrow">Machinery</span><h2>Dashboard</h2></div>
<p class="lede">Everything the site is built from, on one page, in the state the build sees it. This is the audit half of the project — kept reachable, kept out of the shopping path on purpose.</p>
<div class="kpi" style="margin:1.6rem 0 2rem">
  <div><div class="v">${products.length}</div><div class="k">links supplied</div></div>
  <div><div class="v">${liveProducts.length}</div><div class="k">resolved to a listing</div></div>
  <div><div class="v zero">0</div><div class="k">owner-confirmed identities</div></div>
  <div><div class="v">${sourcesDoc.sources.length}</div><div class="k">source rows</div></div>
  <div><div class="v zero">${sourcesDoc.source_register_integrity.unresolved}</div><div class="k">unresolved</div></div>
  <div><div class="v zero">${ledger.row_count}</div><div class="k">ledger rows</div></div>
  <div><div class="v">${flagsDoc.flags.length}</div><div class="k">items flagged</div></div>
</div>
<section class="section">
  <div class="section-head"><h2 style="font-size:1.15rem">Product-intent confirmation record</h2><span class="chip chip-ghost">intended and observed kept in separate fields</span></div>
  <div class="table-wrap"><table class="data"><thead><tr><th>ID</th><th>Submitted token</th><th>Len</th><th>Intended ASIN</th><th>Observed ASIN</th><th>Listing title</th><th>Price</th><th>Rating</th><th>Status</th><th>Flags</th></tr></thead><tbody>${prodRows}</tbody></table></div>
  <p class="tiny muted" style="margin-top:.5rem">${esc(productsDoc.aggregate_findings.note)}</p>
</section>
<section class="section">
  <div class="section-head"><h2 style="font-size:1.15rem">Special Links</h2><span class="chip chip-warn">test one before scaling</span></div>
  <p class="tiny muted">Format is generated, never hand-written, so it cannot drift. Attribution is unverified because the test has to run inside an enrolled Associates workflow with the site registered — see <a href="${U("/decisions/")}">Q-06 and Q-07</a>.</p>
  <div class="table-wrap"><table class="data"><thead><tr><th>Product</th><th>ASIN used</th><th>Candidate URL</th><th>Status</th><th>Provenance</th></tr></thead><tbody>${linkRows}</tbody></table></div>
  <div class="panel"><h4>One-link test protocol</h4><ol class="tiny" style="margin:0;padding-left:1.2rem">${linksDoc.one_link_test_protocol.steps.map((s) => "<li>" + esc(s.replace(/^\d+\.\s*/, "")) + "</li>").join("")}</ol><p class="tiny" style="margin:.6rem 0 0"><strong>Do not conclude:</strong> ${esc(linksDoc.one_link_test_protocol.do_not_conclude)}</p></div>
</section>
<section class="section">
  <div class="section-head"><h2 style="font-size:1.15rem">Campaign ledger</h2><span class="chip chip-ghost">${ledger.row_count} rows by design</span></div>
  <div class="table-wrap"><table class="data"><thead><tr>${ledCols}</tr></thead><tbody><tr><td colspan="${ledger.schema.columns.length}" style="color:var(--ink-faint);font-style:italic">Empty. Rows may be added only from an authorised first-party report, each with its own date and provenance. No derived, backfilled or modelled figure is ever entered here.</td></tr></tbody></table></div>
  <div class="grid g2">
    <div class="panel"><h4>Integrity rules</h4><ul class="tiny" style="margin:0">${ledger.schema.integrity_rules.map((r) => "<li>" + esc(r) + "</li>").join("")}</ul></div>
    <div class="panel"><h4>Read-time floors before any ratio is shown</h4><ul class="tiny" style="margin:0">${Object.entries(ledger.read_time_metric_definitions).map(([k, v]) => "<li><strong>" + esc(k) + "</strong> — " + esc(typeof v === "string" ? v : "") + "</li>").join("")}</ul></div>
  </div>
</section>
<section class="section">
  <div class="section-head"><h2 style="font-size:1.15rem">Measurement</h2><span class="chip chip-warn">${esc(measure.events[0].status)}</span></div>
  <div class="table-wrap"><table class="data"><thead><tr><th>Event</th><th>Definition</th><th>Fields</th><th>Conversion role</th><th>Privacy note</th></tr></thead><tbody>
  ${measure.events.map((e) => `<tr><td><code>${esc(e.id)}</code></td><td>${esc(e.definition)}</td><td class="tiny">${e.fields.map((f) => "<code>" + esc(f) + "</code>").join(" ")}</td><td>${esc(e.conversion_role)}</td><td class="tiny">${esc(e.privacy_note)}</td></tr>`).join("\n")}
  </tbody></table></div>
  <div class="grid g2" style="margin-top:1rem">
    <div class="panel"><h4>Explicitly not instrumented</h4><ul class="tiny" style="margin:0">${measure.explicitly_not_instrumented.map((x) => "<li>" + esc(x) + "</li>").join("")}</ul></div>
    <div class="panel panel-note"><h4>Collector contract</h4><ul class="tiny" style="margin:0">${Object.entries(measure.collector_contract).map(([k, v]) => "<li><strong>" + esc(k) + "</strong> — " + esc(String(v)) + "</li>").join("")}</ul></div>
  </div>
</section>
<section class="section">
  <div class="section-head"><h2 style="font-size:1.15rem">Compliance controls</h2><span class="chip ${compliance.gate_summary.failing_now === 0 ? "chip-open" : "chip-warn"}">${compliance.gate_summary.automated_checks} automated gates</span></div>
  <div class="table-wrap"><table class="data"><thead><tr><th>ID</th><th>Rule</th><th>Origin</th><th>Implementation</th><th>Gate</th><th>Status</th></tr></thead><tbody>
  ${compliance.controls.map((c) => `<tr><td class="num">${esc(c.id)}</td><td>${esc(c.rule)}</td><td class="tiny">${esc(c.origin)}${c.source_id ? " · " + esc(c.source_id) : ""}</td><td class="tiny">${esc(c.implementation)}</td><td class="tiny">${esc(c.gate)}</td><td><span class="chip ${/passing/.test(c.status) ? "chip-open" : "chip-warn"}">${esc(c.status)}</span></td></tr>`).join("\n")}
  </tbody></table></div>
</section>
<section class="section">
  <div class="section-head"><h2 style="font-size:1.15rem">Repo review</h2><span class="chip chip-ghost">commit ${esc(review.reviewed_commit.slice(0, 7))}</span></div>
  <div class="table-wrap"><table class="data"><thead><tr><th>ID</th><th>Severity</th><th>Finding</th><th>Verified by</th><th>Action taken</th></tr></thead><tbody>
  ${review.findings.map((f) => `<tr><td class="num">${esc(f.id)}</td><td><span class="chip ${f.severity === "high" ? "chip-warn" : "chip"}">${esc(f.severity)}</span></td><td class="tiny">${esc(f.finding)}</td><td class="tiny">${esc(f.verified_by)}</td><td class="tiny">${esc(f.action_taken)}</td></tr>`).join("\n")}
  </tbody></table></div>
</section>`;
  write("dashboard/index.html", layout({ href: "/dashboard/", title: "Dashboard — " + site.brand, desc: "The register behind this site: product-intent records, Special Links, campaign ledger, measurement events, compliance controls and the repo review.", body, crumbs: [{ label: "Inside the project" }, { label: "Dashboard" }], jsonld: { "@context": "https://schema.org", "@type": "Dataset", name: "ShopNow 047 register", description: "Source-of-truth data behind every page on this site.", dateModified: TODAY } }));
  record("dashboard/index.html", { title: "Dashboard", desc: "Register dashboard", date: TODAY, section: "dashboard" });
}

/* ---------------------------------------------------------------- sources */
{
  const body = `<div class="section-head"><span class="eyebrow">Evidence</span><h2>Source register</h2></div>
<p class="lede">Every source this site rests on, with what it proves, how far the verification actually got, and what we refused to publish because of it. Three tiers, never conflated: <strong>verbatim</strong> (official page fetched this session), <strong>excerpt</strong> (official-domain text, page would not load), <strong>unresolved</strong> (conflict or absent — nothing adopted).</p>
<div class="kpi" style="margin:1.4rem 0 2rem">
  <div><div class="v">${sourcesDoc.sources.length}</div><div class="k">rows</div></div>
  <div><div class="v">${sourcesDoc.source_register_integrity.verbatim}</div><div class="k">verbatim</div></div>
  <div><div class="v">${sourcesDoc.source_register_integrity.excerpt}</div><div class="k">excerpt</div></div>
  <div><div class="v zero">${sourcesDoc.source_register_integrity.unresolved}</div><div class="k">unresolved</div></div>
  <div><div class="v zero">${sourcesDoc.source_register_integrity.values_backfilled_by_inference}</div><div class="k">inferred values</div></div>
</div>
${sourcesDoc.sources.map((s) => `<section class="section" style="margin-top:1.8rem">
  <h2 style="font-size:1.15rem">${esc(s.id)} · ${esc(s.title)}</h2>
  <p class="tiny muted" style="margin:0 0 .5rem">${esc(s.publisher)} · ${esc(s.publisher_type)} · accessed ${esc(s.accessed_date || sourcesDoc.accessed_date)}${s.page_stated_update_date ? " · page dated " + esc(s.page_stated_update_date) : ""} · ${s.url ? '<a href="' + esc(amazonTagged(s.url)) + '" rel="' + (/amazon\.com/.test(s.url) ? "sponsored nofollow noopener noreferrer" : "noopener noreferrer") + '" target="_blank">open source</a>' : "no URL available"}</p>
  <div class="table-wrap"><table class="data"><thead><tr><th>Claim</th><th>Status</th><th>Evidence / quote</th></tr></thead><tbody>
  ${s.verified_claims.map((c) => `<tr><td>${esc(c.claim || c.description)}</td><td><span class="chip ${c.status === "verbatim" ? "chip-open" : c.status === "unresolved" ? "chip-warn" : "chip"}">${esc(c.status)}</span></td><td class="tiny">${c.quote ? "<blockquote style='margin:.2rem 0;font-size:.95rem'>" + esc(c.quote) + "</blockquote>" : ""}${c.why_unresolved ? "<em>" + esc(c.why_unresolved) + "</em>" : ""}${c.evidence ? "<br>" + esc(c.evidence) : ""}${c.conflict ? "<br><strong>conflict:</strong> " + Object.values(c.conflict).map(esc).join(" / ") : ""}${c.effect_on_this_project ? "<br><strong>effect:</strong> " + esc(c.effect_on_this_project) : ""}${c.status === "excerpt" ? "<br><span class='muted'>Official-domain text returned by a search index; the page itself would not load in this environment.</span>" : ""}</td></tr>`).join("\n")}
  </tbody></table></div>
  ${s.notes ? '<p class="tiny muted" style="margin:.5rem 0 0">' + esc(s.notes) + "</p>" : ""}
  ${s.owner_action ? '<p class="tiny" style="margin:.4rem 0 0"><strong>Closes when:</strong> ' + esc(s.owner_action) + "</p>" : ""}
</section>`).join("\n")}
<p class="tiny muted" style="margin-top:2rem">Verification method for each row, in full, is in <code>register/sources.json</code> in the repository — including the two pages that failed to load after three attempts, recorded as failures rather than retried into confidence.</p>`;
  write("sources/index.html", layout({ href: "/sources/", title: "Source register — " + site.brand, desc: "Every source behind this site, its access date, the exact quote where one exists, and the tier of verification reached. Four rows are unresolved and say so.", body, crumbs: [{ label: "Inside the project" }, { label: "Sources" }], jsonld: { "@context": "https://schema.org", "@type": "Dataset", name: "Source register", description: "Official sources underpinning every claim on this site", dateModified: TODAY } }));
  record("sources/index.html", { title: "Source register", desc: "All sources", date: TODAY, section: "sources" });
}

/* ----------------------------------------------------------- suggestions */
{
  const byPriority = {};
  suggDoc.suggestions.forEach((s) => { (byPriority[s.priority] = byPriority[s.priority] || []).push(s); });
  const prioName = { 1: "Priority 1 · make it read like a shop", 2: "Priority 2 · make it findable", 3: "Priority 3 · make it read like a publication", 4: "Priority 4 · evidence-based iteration", 5: "Priority 5 · compliance gate" };
  const render = (s) => {
    const done = s.implemented;
    return `<section class="sug" id="${slugify(s.id)}">
  <div style="display:flex;gap:.5rem;align-items:center;flex-wrap:wrap;margin-bottom:.35rem">
    <span class="chip chip-ink">${esc(s.id)}</span>
    <span class="chip ${done ? "chip-open" : /blocked/.test(s.status) ? "chip-warn" : "chip-sponsored"}">${esc(s.status)}</span>
    <span class="tag">effort ${esc(s.paths[0].effort)}</span>
    ${s.depends_on.length ? '<span class="tag">needs ' + s.depends_on.map(esc).join(", ") + "</span>" : ""}
  </div>
  <h3>${esc(s.title)}</h3>
  <p class="hook">${esc(s.hook)}</p>
  ${s.problem ? "<p class='tiny' style='margin:0 0 .7rem'>" + esc(s.problem) + "</p>" : ""}
  ${s.proposal ? "<div class='box' style='margin:.6rem 0'><h5>Proposal</h5><p>" + esc(s.proposal) + "</p></div>" : ""}
  <div class="path">
  ${s.paths.map((p) => `<div class="path-item${s.recommended && s.recommended.indexOf(p.id) === 0 ? " pick" : ""}">
      <span class="pid">${esc(p.id)}</span>
      <div><div class="plabel">${esc(p.label)}</div><p class="pdesc">${esc(p.description)}</p>
      <div class="pmeta"><span class="tag">effort ${esc(p.effort)}</span><span class="tag impact-${esc(p.impact)}">impact ${esc(p.impact)}</span><span class="tag risk-${esc(String(p.risk).split(" ")[0])}">risk ${esc(p.risk)}</span><span class="tag">gives up ${esc(p.gives_up)}</span></div></div>
    </div>`).join("\n")}
  </div>
  <div class="row">
    <div class="box"><h5>Recommended</h5><p><strong>${esc(s.recommended)}</strong></p></div>
    <div class="box"><h5>How you would know it worked</h5><p>${esc(s.measure)}</p></div>
  </div>
  <p class="tiny muted" style="margin:.5rem 0 0">Files: <code>${esc((s.files || []).join(", ") || "—")}</code>${done ? " · already live in this build" : " · nothing is implemented until you choose a path"}</p>
</section>`;
  };
  const body = `<div class="section-head"><span class="eyebrow">Review board</span><h2>Suggestions, before anything changes</h2></div>
<p class="lede">This is the decision surface the brief asked for: a place to read an option, pick a path, and only then have it built. ${suggDoc.summary.implemented} rows are already live because the brief mandated them; the rest wait for you. Nothing here has been decided on your behalf — the “recommended” line is an opinion with its reason attached, and several rows recommend against the easy option.</p>
<div class="kpi" style="margin:1.6rem 0 1.4rem">
  <div><div class="v">${suggDoc.suggestions.length}</div><div class="k">rows</div></div>
  <div><div class="v">${suggDoc.summary.implemented}</div><div class="k">implemented</div></div>
  <div><div class="v zero">${suggDoc.summary.awaiting_choice}</div><div class="k">awaiting your choice</div></div>
  <div><div class="v zero">${suggDoc.summary.blocked_on_owner}</div><div class="k">blocked on you</div></div>
</div>
<div class="panel panel-note"><h4>If you only make two choices today</h4><ul><li><strong>${esc(suggDoc.summary.highest_value_unblocked_choice)}</strong></li><li><strong>${esc(suggDoc.summary.cheapest_high_value_choice)}</strong></li></ul><p class="tiny muted" style="margin:.4rem 0 0">Both are cheap. Both sit upstream of everything else on this board, which is why they are called out rather than left in priority order.</p></div>
${Object.keys(byPriority).sort().map((k) => `<section class="section"><div class="section-head"><span class="eyebrow">P${esc(k)}</span><h2 style="font-size:1.2rem">${esc((prioName[k] || "Priority " + k).split("· ")[1] || prioName[k])}</h2></div>${byPriority[k].map(render).join("\n")}</section>`).join("\n")}
<div class="panel" style="margin-top:2.4rem"><h4>How to record a choice</h4><p class="tiny" style="margin:0">Pick a path id per row (a, b, c) and write it into <code>register/suggestions.json</code> under a new <code>chosen</code> field, or say it in plain words and hand it back to a session. The builder treats <code>implemented: false</code> as “do not build this yet”, which is what keeps this page from becoming a wish list that quietly half-shipped. The full board is on <a href="${U("/decisions/")}">the decisions page</a> as questions, and on <a href="${U("/flagged-for-review/")}">Flagged for review</a> as defects.</p></div>`;
  write("suggestions/index.html", layout({ href: "/suggestions/", title: "Suggestions to review — " + site.brand, desc: "Every improvement proposed for this site, with the trade-offs, the effort, the risk, and the measurement that would justify it. Nothing awaiting a choice has been implemented.", body, crumbs: [{ label: "Inside the project" }, { label: "Suggestions" }] }));
  record("suggestions/index.html", { title: "Suggestions", desc: "Review board", date: TODAY, section: "suggestions" });
}

/* ------------------------------------------------------------ decisions */
{
  const totalQ = quesDoc.sections.reduce((a, s) => a + s.questions.length, 0);
  const answered = quesDoc.sections.reduce((a, s) => a + s.questions.filter((q) => q.answer).length, 0);
  const blockedIds = new Set(quesDoc.answers_required_before_first_decision);
  const body = `<div class="section-head"><span class="eyebrow">Decision gate</span><h2>Open questions, and how to close each one</h2></div>
<p class="lede">${totalQ} questions. For each: what is already known, what is missing, the cheapest action that would settle it, and which decisions stay blocked until then. ${answered} are answered. The point of this page is that a decision made without the answer is a guess with a schedule attached.</p>
<div class="kpi" style="margin:1.6rem 0 1.8rem">
  <div><div class="v">${totalQ}</div><div class="k">questions</div></div>
  <div><div class="v zero">${answered}</div><div class="k">answered</div></div>
  <div><div class="v zero">${blockedIds.size}</div><div class="k">block the first move</div></div>
  <div><div class="v">${quesDoc.sections.length}</div><div class="k">areas</div></div>
</div>
<div class="panel panel-gap"><h4>What we are not going to do</h4><p class="tiny" style="margin:0">Fill any of these in with something plausible. Two rows an earlier outline contemplated — search volume and a paid-traffic target — were never created as questions at all, because no source for either exists in this repository and an invented figure would read like a measurement. That is the whole difference between this register and a confident one.</p></div>
${quesDoc.sections.map((sec) => `<section class="section">
  <div class="section-head"><span class="eyebrow">Section ${esc(sec.id)}</span><h2 style="font-size:1.2rem">${esc(sec.title)}</h2></div>
  ${sec.why_first ? '<p class="tiny muted">' + esc(sec.why_first) + "</p>" : ""}
  ${sec.questions.map((q) => `<div class="qa"${blockedIds.has(q.id) ? ' style="border-left:3px solid var(--accent)"' : ""}>
    <h4>${blockedIds.has(q.id) ? '<span class="chip chip-sponsored" style="margin-right:.4rem">blocks the first move</span>' : ""}${esc(q.id)}. ${esc(q.question)}</h4>
    <div class="kv">
      <b>Known</b><span>${esc(q.known)}</span>
      <b>Missing</b><span>${esc(q.unknown)}</span>
      <b>How to close</b><span>${esc(q.how_to_close)}</span>
      <b>Who</b><span>${esc(q.who)}</span>
      <b>Blocks</b><span>${q.blocks.map((b) => '<span class="tag">' + esc(b) + "</span>").join(" ")}</span>
    </div>
    <div class="answer"><strong>Answer:</strong> ${q.answer ? esc(q.answer) : '<span class="blank">awaiting input</span>'}</div>
  </div>`).join("\n")}
</section>`).join("\n")}
<div class="panel" style="margin-top:2rem"><h4>Discovery suggestions for the things nobody can answer yet</h4><ul class="tiny" style="margin:0">
<li><strong>Read the redirect yourself.</strong> Open each supplied link in a normal browser and copy the final URL. Five minutes, closes Q-01 and usually Q-02.</li>
<li><strong>One screenshot per account screen.</strong> Tracking IDs, Site Settings, the API access control, and Reports &gt; Transactions answer six questions at once and give the register dated provenance.</li>
<li><strong>Verify Search Console the day the domain exists.</strong> It costs nothing and its value is strictly a function of how early the clock starts.</li>
<li><strong>Ask the cheapest reader question first.</strong> Zero-result queries on the <a href="${U("/search/")}">search page</a> are a free demand signal the moment traffic exists — no tool, no cost, no consent problem.</li>
<li><strong>Write down the number you would quit at.</strong> Q-20 has no source and needs one: a stopping rule is data about you, and it is as recordable as any metric.</li>
</ul></div>`;
  write("decisions/index.html", layout({ href: "/decisions/", active: null, title: "Open questions — " + site.brand, desc: "The information this project still needs before any decision is defensible: what is known, what is missing, and the cheapest action that closes each gap.", body, crumbs: [{ label: "Inside the project" }, { label: "Decisions" }] }));
  record("decisions/index.html", { title: "Open questions", desc: "Decision gate", date: TODAY, section: "decisions" });
}

/* ------------------------------------------------------- flagged review */
{
  const body = `<div class="section-head"><span class="eyebrow">Transparency</span><h2>Flagged for review</h2></div>
<p class="lede">Everything this project could not confirm, every place the evidence ran out, and every rule we chose the strict reading of. Nothing here blocks the site going live — that is the point of publishing it rather than fixing it silently. Each row names what was withheld from the site as a result.</p>
<div class="search-box"><input type="search" placeholder="Filter ${flagsDoc.flags.length} rows — try 'ASIN', 'price', 'tag'" data-filter-table="#flagtable" aria-label="Filter flagged items"><span class="tiny muted" data-filter-count></span></div>
<div class="table-wrap" style="margin-bottom:1.6rem"><table class="data" id="flagtable"><thead><tr><th>ID</th><th>Item</th><th>Severity</th><th>Effect on this site</th><th>Closes when</th></tr></thead><tbody>
${flagsDoc.flags.map((f) => `<tr><td class="num">${esc(f.id)}</td><td>${esc(f.title)}</td><td><span class="chip ${f.severity === "high" ? "chip-warn" : f.severity === "medium" ? "chip" : "chip-ghost"}">${esc(f.severity)}</span></td><td class="tiny">${esc(f.consequence)}</td><td class="tiny">${esc(f.owner_action)}</td></tr>`).join("\n")}
</tbody></table></div>
${flagsDoc.flags.map((f) => `<section class="flag">
  <h3>${esc(f.id)} · ${esc(f.title)}</h3>
  <div style="display:flex;gap:.4rem;flex-wrap:wrap;margin-bottom:.5rem"><span class="chip ${f.severity === "high" ? "chip-warn" : "chip"}">${esc(f.severity)}</span><span class="tag">${esc(f.status)}</span><span class="tag">blocks launch: ${f.blocks_launch ? "yes" : "no"}</span></div>
  <dl>
    <dt>Finding</dt><dd>${esc(f.finding)}</dd>
    <dt>Consequence</dt><dd>${esc(f.consequence)}</dd>
    <dt>You would do</dt><dd>${esc(f.owner_action)}</dd>
    <dt>Discovery step</dt><dd>${esc(f.discovery_step)}</dd>
    <dt>Withheld</dt><dd>${esc(f.withheld_from_site)}</dd>
    <dt>Source</dt><dd>${f.source ? '<a href="' + esc(amazonTagged(f.source)) + '" rel="' + (/amazon\.com/.test(f.source) ? "sponsored nofollow noopener noreferrer" : "noopener noreferrer") + '" target="_blank">' + esc(f.source) + "</a>" : '<span class="blank">no source exists yet — that is the finding</span>'}${f.source_id ? ' · register row <code>' + esc(f.source_id) + "</code>" : ""}</dd>
  </dl>
</section>`).join("\n")}
<div class="panel panel-note" style="margin-top:2rem"><h4>Reading this list as a backlog</h4><p class="tiny" style="margin:0">Three rows — FLG-001, FLG-005 and FLG-006 — are worth more than every optimisation on the <a href="${U("/suggestions/")}">suggestions board</a> combined, because they gate identity, monetisation and trust respectively. The other seven are quality-of-evidence items that improve the register without changing what a reader sees.</p></div>`;
  write("flagged-for-review/index.html", layout({ href: "/flagged-for-review/", title: "Flagged for review — " + site.brand, desc: "Unverified values, unresolved links, withheld fields and open owner actions — with the source link for each and the exact step that closes it.", body, crumbs: [{ label: "Inside the project" }, { label: "Flagged for review" }] }));
  record("flagged-for-review/index.html", { title: "Flagged for review", desc: "All open flags", date: TODAY, section: "flags" });
}

/* --------------------------------------------------- executive summary page */
{
  const exec = loadMd("report/EXECUTIVE-SUMMARY.md");
  const r = md(exec.body);
  write("executive-summary/index.html", layout({ href: "/executive-summary/", title: "Executive summary — " + site.brand, desc: "What was asked for, what exists, what was verified, what could not be, and the four decisions that gate everything else.", body: `<article class="article"><div class="prose">${r.html}</div></article>`, crumbs: [{ label: "Inside the project" }, { label: "Executive summary" }], ogType: "article" }));
  record("executive-summary/index.html", { title: "Executive summary", desc: "Executive summary", date: TODAY, section: "summary" });
}

/* --------------------------------------------------------------- search */
{
  const docs = [];
  guides.forEach((g) => docs.push({ title: g.meta.title, href: "/guides/" + g.meta.slug + "/", blurb: g.meta.description, tags: g.meta.tags || [], section: "guide" }));
  liveProducts.forEach((p) => docs.push({ title: p.published_fields.product_name_from_listing, href: productHref(p), blurb: cardBlurb(p), tags: [p.published_fields.brand, p.published_fields.form_factor].filter(Boolean), section: "product" }));
  site.clusters.forEach((c) => docs.push({ title: c.name, href: "/clusters/" + c.slug + "/", blurb: c.question, tags: [c.category], section: "cluster" }));
  docs.push({ title: "Compare: basket, dual-basket, oven-style", href: "/compare/", blurb: "What each shape costs you in cleaning, clearance and capacity.", tags: ["air fryers", "comparison"], section: "compare" });
  [["Methodology", "/methodology/", "How claims get verified, and the gates that enforce it."], ["Who writes here", "/about/", "A desk, not a person — what that means for the advice."], ["Disclosure", "/disclosure/", "The full sponsorship disclosure in plain words."], ["Privacy", "/privacy/", "No cookies, no trackers. What could possibly be recorded."], ["Flagged for review", "/flagged-for-review/", "Unverified values and unresolved links, with sources."], ["Suggestions", "/suggestions/", "Every proposed change, with trade-offs, awaiting a choice."], ["Open questions", "/decisions/", "What must be answered before a decision is defensible."], ["Source register", "/sources/", "Every source, its date, and the verification tier reached."], ["Dashboard", "/dashboard/", "The register behind the site, as the build sees it."], ["Executive summary", "/executive-summary/", "What exists, what was verified, what gates the rest."]].forEach(([t, h, b]) => docs.push({ title: t, href: h, blurb: b, tags: ["project"], section: "project" }));
  write("search/index.json", JSON.stringify({ generated: TODAY, docs }, null, 1));
  const body = `<div class="section-head"><span class="eyebrow">Find</span><h2>Search the site</h2></div>
<p class="lede">${docs.length} pages indexed — guides, products, clusters and the register itself. The index is a static file: no query leaves your browser, nothing is logged, and no third party is involved.</p>
<div class="search-box"><input id="q" type="search" placeholder="try: capacity, cleanup, dishwasher, price, asin, sponsored" aria-label="Search query" autocomplete="off"><span class="tiny muted" id="sstatus" role="status"></span></div>
<div id="results"></div>
<noscript><div class="empty">This search needs JavaScript because it runs entirely in your browser, by design. Every page is one click away from the <a href="${U("/guides/")}">guides index</a>, the <a href="${U("/products/")}">product index</a>, or the <a href="${U("/dashboard/")}">dashboard</a>.</div></noscript>
<div class="panel panel-note" style="margin-top:2rem"><h4>What a zero-result page means here</h4><p class="tiny" style="margin:0">On most affiliate sites a failed internal search is invisible. Here it is the cheapest demand signal available — the questions readers ask that we have not written about become the next topic, which is what the brief means by choosing the next topic from measured queries instead of instinct. Until a collector is configured it is not recorded anywhere; see <a href="${U("/suggestions/#sg-28")}">SG-28</a>.</p></div>`;
  write("search/index.html", layout({ href: "/search/", title: "Search — " + site.brand, desc: "Search every guide, product and register page on this site. Client-side, no logging.", body, crumbs: [{ label: "Search" }], script: "/assets/search.js" }));
  record("search/index.html", { title: "Search", desc: "Site search", date: TODAY, section: "search" });
}

/* ------------------------------------------------------------- 404 / misc */
{
  write("404.html", layout({ href: "/404.html", title: "Not found — " + site.brand, desc: "This page does not exist.", body: `<div class="empty" style="max-width:640px;margin:3rem auto"><h1 style="font-size:2rem">Nothing here</h1><p>That URL is not a page on this site. If you followed an internal link, that is a defect worth reporting — the build is supposed to reject broken links before they can exist.</p><p style="margin-top:1.2rem"><a class="btn btn-primary" href="${U("/")}">Front page</a> <a class="btn btn-ghost" href="${U("/guides/")}">Guides</a> <a class="btn btn-ghost" href="${U("/search/")}">Search</a> <a class="btn btn-ghost" href="${U("/flagged-for-review/")}">Flagged for review</a></p></div>` }));
  write("robots.txt", `# ${site.brand}
# Static, generated, single origin. No crawl-delay needed; the site is ${pages.length + 1} pages.
User-agent: *
Allow: /

Sitemap: ${BASE}/sitemap.xml
`);
  write("humans.txt", `${site.brand} — ${site.tagline}
# TEAM
  Desk: ${site.desk_name} (AI-assisted; human editorial sign-off pending — see /about/)
  No named individual is credited on this site. That is deliberate, not an oversight.
# SITE
  Language: en-US
  Built: static, zero dependencies, generated from register/*.json
  Standards: semantic HTML, works without JavaScript, no cookies, no third-party scripts
  Sources: see /sources/ — every claim has a dated row, or the page says it cannot
# NOTE
  If a figure on this site is wrong, it is wrong in one file and one rebuild fixes it.
`);
  const sm = pages.filter((p) => p.relPath !== "404.html").map((p) => `  <url>\n    <loc>${BASE}${p.href}</loc>\n    <lastmod>${p.date || TODAY}</lastmod>\n  </url>`).join("\n");
  write("sitemap.xml", `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${sm}\n</urlset>\n`);

  const items = guides.slice(0, 20).map((g) => `  <item>
    <title>${esc(g.meta.title)}</title>
    <link>${BASE}/guides/${g.meta.slug}/</link>
    <guid isPermaLink="true">${BASE}/guides/${g.meta.slug}/</guid>
    <pubDate>${new Date(g.meta.date + "T09:00:00Z").toUTCString()}</pubDate>
    <description>${esc(g.meta.description)}</description>
    <category>${esc(g.meta.cluster || "guides")}</category>
    <author>${esc(site.desk_name)}</author>
  </item>`).join("\n");
  write("feed.xml", `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
  <title>${esc(site.brand)} — ${esc(site.tagline)}</title>
  <link>${BASE}/</link>
  <description>${esc(site.promise)}</description>
  <language>${site.language}</language>
  <lastBuildDate>${new Date().toUTCString()}</lastBuildDate>
  <managingEditor>${esc(site.desk_name)} (${esc(site.brand)})</managingEditor>
  <webMaster>${esc(site.brand)} build</webMaster>
  <ttl>1440</ttl>
  <image><url>${BASE}/assets/img/hero.jpg</url><title>${esc(site.brand)}</title><link>${BASE}/</link></url></image>
  <atom:link href="${BASE}/feed.xml" rel="self" type="application/rss+xml"/>
${items}
</channel>
</rss>
`.replace("</url></image>", "</image>"));
  for (const f of ["EXECUTIVE-SUMMARY.md", "DECISION-BRIEF.md"]) fs.copyFileSync(path.join(ROOT, "report", f), path.join(OUT, f));
  fs.writeFileSync(path.join(OUT, "build-info.json"), JSON.stringify({ generated: new Date().toISOString(), pages: pages.length + 1, written: [...written].sort(), base_url: BASE, tracking_id: TRACK }, null, 1));
}

console.log(`build: ${written.size} files · ${pages.length} registered pages · ${guides.length} guides · ${liveProducts.length} live products of ${products.length} rows`);
