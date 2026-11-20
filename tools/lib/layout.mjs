// Shared page chrome. Every page gets: skip link, masthead, disclosure strip,
// single navigation group, footer with repeated disclosure, and the five
// document landmarks. Nothing here is optional per page.
import { esc } from "./md.mjs";

export const SITE = {
  name: "ShopNow Labs",
  tagline: "Countertop buying desk",
  base: "/Affil3",
  url: "https://karagemop466-tech.github.io/Affil3",
  author: "ShopNow Labs editorial desk",
  trackingId: "shopnow047c-20",
  published: "2026-11-20",
  assoc: "As an Amazon Associate I earn from qualifying purchases.",
  ftc: "I get commissions for purchases made through links in this post.",
};

// The single navigation group. Dashboard surfaces live in the footer only,
// so the reader-facing nav stays small and shop-like.
export const NAV = [
  ["Guides", "/buying-guides/"],
  ["Air fryers", "/air-fryers/"],
  ["Thermometers", "/thermometers/"],
  ["How we pick", "/how-we-pick/"],
];

// Every dashboard surface, reachable from the footer on every page.
export const FOOTER_GROUPS = [
  {
    title: "The desk",
    links: [
      ["All buying guides", "/buying-guides/"],
      ["Air fryers", "/air-fryers/"],
      ["Thermometers", "/thermometers/"],
      ["How we pick", "/how-we-pick/"],
      ["Seasonal collections", "/collections/"],
    ],
  },
  {
    title: "Review room",
    links: [
      ["Executive summary", "/review/executive-summary/"],
      ["Flagged for review", "/review/flagged-for-review/"],
      ["Suggestion register", "/review/suggestions/"],
      ["Open questions", "/review/questions/"],
      ["Product register", "/review/product-register/"],
    ],
  },
  {
    title: "Operations",
    links: [
      ["Automation & gates", "/operations/automation/"],
      ["Measurement plan", "/operations/measurement/"],
      ["Campaign ledger", "/review/campaign-ledger/"],
      ["Source register", "/review/sources/"],
    ],
  },
  {
    title: "The fine print",
    links: [
      ["Disclosure", "/disclosure/"],
      ["Privacy", "/privacy/"],
      ["Editorial standards", "/editorial-standards/"],
      ["Contact", "/contact/"],
    ],
  },
];

const abs = (p) => `${SITE.url}${p === "/" ? "/" : p}`;

function head({ title, description, path, type = "website", extraHead = "" }) {
  const canonical = abs(path);
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(title)}</title>
<meta name="description" content="${esc(description)}">
<link rel="canonical" href="${canonical}">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta property="og:type" content="${type}">
<meta property="og:site_name" content="${SITE.name}">
<meta property="og:title" content="${esc(title)}">
<meta property="og:description" content="${esc(description)}">
<meta property="og:url" content="${canonical}">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary">
<meta name="theme-color" content="#fbf8f3">
<meta name="generator" content="ShopNow Labs static desk v1">
<link rel="alternate" type="application/rss+xml" title="${SITE.name} — new guides" href="${SITE.base}/feed.xml">
<link rel="stylesheet" href="${SITE.base}/assets/css/site.css">
<link rel="icon" href="${SITE.base}/assets/img/favicon.svg" type="image/svg+xml">
<script defer src="${SITE.base}/assets/js/analytics-config.js"></script>
<script defer src="${SITE.base}/assets/js/shop.js"></script>
${extraHead}</head>
<body>
<a class="skip" href="#main">Skip to content</a>
`;
}

function masthead(current) {
  const nav = NAV.map(([label, href]) => {
    const cur = current === href ? ' aria-current="page"' : "";
    return `<a href="${SITE.base}${href}"${cur}>${label}</a>`;
  }).join("");
  return `<header class="masthead">
  <div class="wrap masthead__bar">
    <a class="brand" href="${SITE.base}/">
      <span class="brand__mark">ShopNow<em>.</em>Labs</span>
      <span class="brand__tag">Countertop buying desk</span>
    </a>
    <nav class="nav" aria-label="Sections">
      ${nav}
      <a class="nav__cta" href="${SITE.base}/buying-guides/">Start with a guide</a>
    </nav>
  </div>
</header>
<div class="disclosure" role="note" aria-label="Affiliate disclosure">
  <div class="wrap">
    <span class="disclosure__tag">Disclosure</span>
    <span>${SITE.ftc} ${SITE.assoc} Links are marked <strong>paid</strong> and open Amazon in a new tab. <a href="${SITE.base}/disclosure/">How this works</a></span>
  </div>
</div>`;
}

function footer() {
  const groups = FOOTER_GROUPS.map(
    (g) => `<div>
      <h3>${g.title}</h3>
      <ul>${g.links.map(([l, h]) => `<li><a href="${SITE.base}${h}">${l}</a></li>`).join("")}</ul>
    </div>`
  ).join("");

  return `<footer class="footer">
  <div class="wrap">
    <div class="footer__grid">
      <div class="footer__brand">
        <a class="brand" href="${SITE.base}/"><span class="brand__mark">ShopNow<em>.</em>Labs</span></a>
        <p style="margin-top:.7rem">A small buying desk for countertop cooking appliances. We publish the reasoning, not just the ranking.</p>
        <p class="tiny" style="margin-top:.7rem">Tracking ID <code>${SITE.trackingId}</code> · Amazon.com</p>
      </div>
      ${groups}
    </div>
    <div class="footer__legal">
      <p class="assoc"><strong>${SITE.assoc}</strong> ${SITE.ftc}</p>
      <p>Prices and availability are shown on Amazon and can change at any time. We do not publish prices on this site. Product names, logos and brands are the property of their respective owners and are used for identification only. This site is not endorsed by or affiliated with any brand mentioned.</p>
      <p>© ${new Date().getFullYear()} ${SITE.name}. Editorial content published ${SITE.published}. <a href="${SITE.base}/privacy/">Privacy</a> · <a href="${SITE.base}/disclosure/">Disclosure</a> · <a href="${SITE.base}/review/flagged-for-review/">Known gaps</a></p>
    </div>
  </div>
</footer>
`;
}

/**
 * @param {object} o
 * @param {string} o.path      URL path relative to base, e.g. "/buying-guides/"
 * @param {string} o.title     <title>
 * @param {string} o.description
 * @param {string} o.body      main content html (inside <main>)
 * @param {string} [o.jsonLd]  JSON-LD object or array
 * @param {string} [o.afterMain] html placed after </main> e.g. capture block
 */
export function page({ path, title, description, body, jsonLd, afterMain = "", current }) {
  const ld = jsonLd
    ? `<script type="application/ld+json">${JSON.stringify(jsonLd).replace(/</g, "\\u003c")}</script>\n`
    : "";
  return `${head({ title, description, path })}
${masthead(current ?? path)}
<main id="main">
${body}
</main>
${afterMain}
${footer()}
${ld}</body>
</html>
`;
}

export function breadcrumb(trail) {
  return `<nav class="breadcrumb wrap" aria-label="Breadcrumb">${trail
    .map(([label, href], idx) =>
      idx === 0 ? `<a href="${SITE.base}${href}">${label}</a>` : `<span>/</span>${href ? `<a href="${SITE.base}${href}">${label}</a>` : label}`
    )
    .join("")}</nav>`;
}

/** Paid-link button used everywhere a product link appears. */
export function paidLink(url, label = "Check price on Amazon", { small = false } = {}) {
  return `<a class="link-out${small ? " small" : ""}" href="${url}" target="_blank" rel="sponsored nofollow noopener" data-outbound data-product-link>${label}</a> <span class="paid">Paid link</span>`;
}

export function jsonLdOrg() {
  return {
    "@type": "Organization",
    "@id": `${SITE.url}/#org`,
    name: SITE.name,
    url: `${SITE.url}/`,
    description: "An independent buying desk for countertop cooking appliances.",
  };
}

export function jsonLdWebSite() {
  return {
    "@type": "WebSite",
    "@id": `${SITE.url}/#site`,
    url: `${SITE.url}/`,
    name: SITE.name,
    publisher: { "@id": `${SITE.url}/#org` },
    inLanguage: "en-US",
  };
}
