// Trust pages: disclosure, editorial standards, how we pick, privacy, contact.
import { page, breadcrumb, SITE } from "../lib/layout.mjs";

const shell = (title, kicker, lede, inner, meta = "") => `
<section class="article-head wrap">
  <p class="kicker">${kicker}</p>
  <h1>${title}</h1>
  <p class="lede">${lede}</p>
  ${meta ? `<div class="article-head__meta">${meta}</div>` : ""}
</section>
<section class="section wrap">
  <div class="prose">${inner}</div>
</section>`;

function disclosure() {
  return `${breadcrumb([["Home", "/"], ["Disclosure", null]])}
${shell(
    "How this site makes money, stated plainly",
    "Disclosure",
    "This page exists so that nobody has to guess. It is short on purpose.",
    `
<div class="callout callout--verify">
  <span class="callout__label">The short version</span>
  <p><strong>${SITE.ftc}</strong> ${SITE.assoc}</p>
  <p class="small" style="margin-top:.6rem">If you click a product link on this site and buy something, we may earn a commission. The price you pay is the same. Nothing on this site is a paid placement by a brand, and no brand has paid for a position in any guide.</p>
</div>

<h2>Where the disclosure appears</h2>
<p>On every page of this site, in two places:</p>
<ul>
  <li><strong>Directly under the site header</strong>, before any content, so it is visible without scrolling.</li>
  <li><strong>Beside every product link</strong>, as the literal words <em>Paid link</em>, and again in the footer.</li>
</ul>
<p>That is deliberate. The FTC's guidance says the closer a disclosure sits to the recommendation the better, and that a disclosure at the very top of a page, outside the article, can be overlooked. Doing both is the only way to satisfy either reading. The wording <em>I get commissions for purchases made through links in this post</em> is the FTC's own example; <em>Paid link</em> is the wording the FTC says should be adequate next to an affiliate link. Terms the FTC says are unclear on their own — such as <em>affiliate link</em>, <em>commissionable link</em>, or a <em>buy now</em> button — are not used as the sole disclosure anywhere.</p>

<h2>Why every link carries a tag</h2>
<p>Amazon's Associates policies require the Associates ID to appear as a parameter in the URL of each link to an Amazon site. Every outbound product link on this site is a canonical Amazon product address with the tracking ID <code>${SITE.trackingId}</code> appended. We do not shorten our own links, because a reader should be able to see where a link goes before clicking it.</p>

<h2>What we do not do</h2>
<ul>
  <li><strong>We do not publish prices.</strong> Amazon permits price display only where Amazon serves the link containing the price, or where the figure comes from its API. We have neither, so every price lives on Amazon and may have changed since you last looked. Amazon itself states it cannot confirm an item's price until you order.</li>
  <li><strong>We do not use Amazon product photography.</strong> Listing images are licensed content with rules about caching and alteration. Our product cards are typographic instead.</li>
  <li><strong>We do not rank by commission.</strong> Commission rates played no part in which products appear. The products on this desk were supplied by the site owner.</li>
  <li><strong>We do not claim to have tested products.</strong> We have not. Every specification on this site was read from the manufacturer's listing on the date recorded on the page.</li>
  <li><strong>We do not offer incentives</strong> for clicking a link or buying. Amazon's policies prohibit rewards or discounts in exchange for using Special Links.</li>
</ul>

<h2>Amazon relationship</h2>
<p>${SITE.assoc} This site is a participant in the Amazon Services LLC Associates Program, an affiliate advertising program. This site is not endorsed by, sponsored by, or otherwise affiliated with Amazon or any brand named on it, and nothing here should be read as an endorsement by Amazon of this site or its content.</p>

<div class="callout callout--warn">
  <span class="callout__label">One thing still unconfirmed</span>
  <p class="small" style="margin:0">The tracking ID above is the one supplied by the site owner. Whether the associated Associates account is approved, and whether that tag is registered to this site, could not be confirmed from this environment. It is listed as an open item on the <a href="${SITE.base}/review/flagged-for-review/">known gaps page</a> rather than being asserted as settled.</p>
</div>

<h2>Sources</h2>
<ul class="small">
  <li><a href="https://affiliate-program.amazon.com/help/operating/agreement" target="_blank" rel="noopener">Amazon Associates Program Operating Agreement</a> — §5 requires the identification statement; §1 defines Special Links.</li>
  <li><a href="https://affiliate-program.amazon.com/help/operating/policies" target="_blank" rel="noopener">Amazon Associates Program Policies</a> — tag requirement, price display condition, incentive prohibition, content rules.</li>
  <li><a href="https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking" target="_blank" rel="noopener">FTC, Endorsement Guides: What People Are Asking</a> — affiliate wording and placement.</li>
  <li><a href="https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255/section-255.5" target="_blank" rel="noopener">16 CFR 255.5</a> — disclosure of material connections.</li>
</ul>
<p class="tiny muted">Full claim-by-claim register with retrieval dates: <a href="${SITE.base}/review/sources/">source register</a>.</p>
`,
    `<span>Updated ${SITE.published}</span><span>Applies to every page</span>`
  )}`;
}

function editorial() {
  return `${breadcrumb([["Home", "/"], ["Editorial standards", null]])}
${shell(
    "What we will and will not claim",
    "Editorial standards",
    "A publication is defined by what it refuses to print. These are ours.",
    `
<h2>Authorship</h2>
<p>Everything on this site is written and signed by the <strong>${SITE.author}</strong>. There is no bylined individual, because no individual has tested these products; inventing an author with a biography would imply an authority we do not have. Corrections and complaints are handled by the same desk.</p>

<h2>What we have not done</h2>
<p><strong>We have not tested any product on this site.</strong> No unit was purchased, measured, or used. This is stated on the home page, in every guide's verification note, and here, because it is the single most important fact about the reliability of the recommendations.</p>
<p>What we did instead was read each product's Amazon listing on ${SITE.published} and record exactly what it says: capacity, stated temperature, modes named in the title, included accessories, stated warranty. Where a listing did not state something a buyer would want — interior dimensions, wattage, probe diameter — we say it is not stated rather than estimating it.</p>

<h2>How specifications are handled</h2>
<ul>
  <li>A specification is published only if it appears in the listing text we retrieved.</li>
  <li>If two listings state different things about similar products, both are reported as stated, without reconciliation.</li>
  <li>Marketing claims in a title — "sync finish", "4-in-1", "24 presets" — are reported as claims, in the listing's own terms, not as verified capabilities.</li>
  <li>Review sentiment is reported only where Amazon's own review-summary widget displayed it, and is labelled as such. We do not convert anecdotes into failure rates.</li>
</ul>

<h2>Why there are no prices or star ratings</h2>
<p>Amazon permits price and availability display only through its own served links or through its API, and requires that comparison prices show both the lowest new and lowest used price. We have no API access. Prices also change within hours, and star averages hide the distribution that matters. Both are omitted on purpose; the reasoning is on the <a href="${SITE.base}/review/flagged-for-review/">known gaps page</a>.</p>

<h2>Imagery</h2>
<p>No Amazon listing photography is used. Program Content may not be altered, and image caching is restricted. Our product cards use typography and a monogram instead. The page makes no third-party requests at all, which also means no tracking pixels load before you decide to allow them.</p>

<h2>Corrections</h2>
<p>If something here is wrong, it will be corrected and the correction will be noted on the page, not silently overwritten. The route is on the <a href="${SITE.base}/contact/">contact page</a>. A correction that changes a recommendation will also be recorded on the <a href="${SITE.base}/review/sources/">source register</a> with the date.</p>

<h2>Independence</h2>
<p>No brand paid for placement, and no brand reviewed a page before publication. The products covered on this desk were supplied by the site owner, which is itself a limitation on independence and is disclosed here rather than concealed.</p>

<h2>AI assistance</h2>
<p>Parts of this site's build — page templates, the sitemap, the feed, link validation — are automated. The prose was written and checked by the desk, and compliance statements are quoted from the sources listed on the <a href="${SITE.base}/review/sources/">source register</a>. Amazon's policies prohibit using its Program Content to develop machine learning models without prior written approval, so listing text was not fed to a model to generate articles; that boundary is documented on the <a href="${SITE.base}/operations/automation/">automation page</a> and logged as FLG-009.</p>
`,
    `<span>Updated ${SITE.published}</span><span>Corrections policy applies from launch</span>`
  )}`;
}

function howWePick() {
  return `${breadcrumb([["Home", "/"], ["How we pick", null]])}
${shell(
    "The method, before the recommendations",
    "How we pick",
    "We match an appliance's design to the job you actually have. Where the listing does not give us what we need to make the match, we say so.",
    `
<h2>The order of operations</h2>
<ol>
  <li><strong>Start from the job.</strong> What do you cook most often, for how many people, in what size of pan or tray?</li>
  <li><strong>Choose the shape.</strong> Dual basket, single basket, oven, or an instrument instead of an appliance. This decision eliminates more products than any specification comparison.</li>
  <li><strong>Check the space.</strong> Footprint, clearance above, clearance in front. A product that does not fit its home is not a candidate.</li>
  <li><strong>Count the cleanup.</strong> Parts that touch grease, and whether they fit your sink.</li>
  <li><strong>Read the specifications as stated.</strong> Not as summarised, not as inferred.</li>
  <li><strong>Read the objections.</strong> Recent one-star reviews, stated warranty, and any repeated mechanical complaint.</li>
  <li><strong>Ask whether a cheaper specialist tool solves it.</strong> Sometimes the answer is a probe, not an appliance.</li>
</ol>

<h2>Why we do not produce a ranked "best" list</h2>
<p>A ranking implies that one product is best across all buyers, which is only true when everybody cooks the same thing in the same kitchen. Two 3-quart drawers beat an 8-quart basket for some households and lose badly for others. Instead of a ranking, each guide maps designs to jobs and states which job each product fits.</p>

<h2>What counts as evidence here</h2>
<ul>
  <li><strong>Listing specifications</strong> — the strongest thing we have, because they are the manufacturer's own statements.</li>
  <li><strong>Amazon's review summaries</strong> — reported as what the widget displayed, never as our finding.</li>
  <li><strong>Compliance statements</strong> — quoted from Amazon, the FTC, or 16 CFR, with the section and the retrieval date.</li>
  <li><strong>Industry commentary</strong> — not used as evidence for any claim. Where a claim exists only in secondary reporting, it appears as an open question instead of a published fact.</li>
</ul>

<h2>What would change our recommendations</h2>
<p>Measured performance data would change them immediately, which is why <a href="${SITE.base}/review/questions/">question 8</a> asks whether there is any budget for testing. Real search query data would change which guides come next, which is why <a href="${SITE.base}/review/questions/">question 5</a> is about Search Console.</p>

<h2>What we won't do</h2>
<p>Publish a price we cannot source. Rank by commission. Describe a product we have not read the listing for. Fill a blank with an estimate to make a table look complete. Every blank on this site is blank on purpose, and is listed on the <a href="${SITE.base}/review/flagged-for-review/">known gaps page</a>.</p>
`,
    `<span>Updated ${SITE.published}</span><span>Method applies to all six guides</span>`
  )}`;
}

function privacy() {
  return `${breadcrumb([["Home", "/"], ["Privacy", null]])}
${shell(
    "Privacy, in one page",
    "Privacy",
    "There is very little to disclose, because the page loads nothing from anyone else. This page describes exactly what happens when you visit.",
    `
<div class="callout">
  <span class="callout__label">Current state, verified</span>
  <p style="margin:0">This site makes <strong>no third-party requests</strong>. The stylesheet, the script and the icon are served from this domain. There are no fonts, no pixels, no social embeds and no advertising scripts on any page. No analytics collector is live yet.</p>
</div>

<h2>What is loaded</h2>
<p>One HTML file, one CSS file, one small JavaScript file and one SVG icon, all served from this site. Nothing is fetched from Amazon until you click a product link, and that click leaves this site.</p>

<h2>What is recorded now</h2>
<p><strong>Nothing.</strong> The site includes code that emits five defined events to an endpoint, but no endpoint is configured, so no data leaves your browser. The measurement page describes what the events contain and what they deliberately exclude. When a collector is configured, it will be described here with its retention period before it is switched on.</p>

<h2>What the events will contain, once enabled</h2>
<ul>
  <li>The name of an event, such as a page view or a click on a product link.</li>
  <li>The page path and the product identifier involved.</li>
  <li>A coarse session identifier held in memory for the visit only, not stored on your device and not linked across visits.</li>
</ul>
<p>They will not contain your name, email, IP address, device fingerprint, or any identifier that persists between visits.</p>

<h2>Cookies</h2>
<p>This site sets no cookies of its own. GitHub Pages, which hosts the files, may process technical request data as described in GitHub's own privacy statement; that is outside this site's control and worth knowing.</p>

<h2>The email form</h2>
<p>No email list is connected. Submitting the form currently records nothing and sends nothing. When a service is connected, the legal basis, the retention period and the unsubscribe route will be stated here before the form is switched on.</p>

<h2>Your choices</h2>
<p>Because nothing is collected, there is nothing to opt out of. If that changes, an opt-out will exist before collection begins, not after.</p>
`,
    `<span>Updated ${SITE.published}</span><span>No third-party requests</span>`
  )}`;
}

function contact() {
  return `${breadcrumb([["Home", "/"], ["Contact", null]])}
${shell(
    "Contact and corrections",
    "Contact",
    "There is no support inbox yet. Here is what exists, and what to use in the meantime.",
    `
<h2>Corrections and complaints</h2>
<p>Open an issue on the public repository that publishes this site: <a href="https://github.com/karagemop466-tech/Affil3/issues" target="_blank" rel="noopener">github.com/karagemop466-tech/Affil3/issues</a>. That is a real, working route today, and it keeps the correction visible to anyone reading the site later.</p>
<p>When a correction changes a recommendation, the page is updated and the change is recorded on the <a href="${SITE.base}/review/sources/">source register</a> with a date.</p>

<h2>What is not available</h2>
<p>There is no press address, no advertising sales contact, and no brand partnership contact. No brand has paid for placement here, and there is no mechanism to buy one.</p>

<h2>Legal</h2>
<p>${SITE.assoc} See the <a href="${SITE.base}/disclosure/">disclosure</a> for the full affiliation statement and the <a href="${SITE.base}/privacy/">privacy page</a> for data handling.</p>

<div class="callout callout--warn">
  <span class="callout__label">Open item</span>
  <p class="small" style="margin:0">A dedicated contact address is an open question (Q-09). Until the owner supplies an entity and an address, the repository issue tracker is the only route, and this page says so rather than displaying a placeholder email that bounces.</p>
</div>
`,
    `<span>Updated ${SITE.published}</span><span>Route: repository issues</span>`
  )}`;
}

export function buildTrust({ out, addRoute }) {
  const pages = [
    ["/disclosure/", disclosure, "Disclosure — how this site makes money", "The full affiliate disclosure: FTC-compliant wording above the fold on every page, the Amazon Associates statement, what we do not do, and the sources behind each rule."],
    ["/editorial-standards/", editorial, "Editorial standards — what we will and will not claim", "Authorship, what was not tested, how specifications are handled, why there are no prices or star ratings, and the corrections policy."],
    ["/how-we-pick/", howWePick, "How we pick — the method behind the recommendations", "The seven-step method: start from the job, choose the shape, check the space, count the cleanup, read the specs as stated, read the objections, consider a specialist tool."],
    ["/privacy/", privacy, "Privacy — what this site does with your data", "No third-party requests, no cookies, no live analytics. Exactly what is loaded, what is recorded, and what the future event payloads will and will not contain."],
    ["/contact/", contact, "Contact and corrections", "How to report a correction, what contact routes exist today, and what is deliberately unavailable."],
  ];

  for (const [path, fn, title, desc] of pages) {
    addRoute(path, { priority: 0.4, changefreq: "yearly" });
    out(`${path.slice(1)}index.html`, page({ path, title: `${title} — ${SITE.name}`, description: desc, body: fn() }));
  }
}
