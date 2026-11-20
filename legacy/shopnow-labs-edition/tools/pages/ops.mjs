// Operations pages: automation and gates, measurement plan, discoverability.
import { page, breadcrumb, SITE } from "../lib/layout.mjs";

const head = (kicker, h1, lede, meta = "") => `
<section class="article-head wrap">
  <p class="kicker">${kicker}</p>
  <h1>${h1}</h1>
  <p class="lede">${lede}</p>
  ${meta ? `<div class="article-head__meta">${meta}</div>` : ""}
</section>`;

const note = (text) => `<div class="callout callout--warn" style="margin-bottom:1.75rem"><span class="callout__label">Read this first</span><p class="small" style="margin:0">${text}</p></div>`;

/* ------------------------------------------------------------- automation */
function automation() {
  const body = `${breadcrumb([["Home", "/"], ["Operations", null], ["Automation", null]])}
${head(
    "Automation and gates",
    "What the machine does, and what it refuses to do",
    "The rule for this site: automate anything that can be checked deterministically, and put a hard gate in front of anything that requires a judgement. A build that fails is cheaper than a page that is wrong.",
    `<span>Updated ${SITE.published}</span><span>Runs on every push</span>`
  )}
<section class="section wrap">
  ${note(
    "The original brief asked for an engine that researches products, writes articles and optimises campaigns automatically. Two of those are constrained by Amazon's own policies and one cannot be done without data the site does not have yet. The table below says which is which rather than pretending all three shipped."
  )}

  <h2>The boundary</h2>
  <div class="tablewrap">
    <table class="data">
      <thead><tr><th>Task</th><th>Automated?</th><th>Why</th></tr></thead>
      <tbody>
        <tr><td>Page generation from data</td><td><span class="chip chip--ok">yes</span></td><td>Deterministic. Every page is built from <code>data/*.json</code>, so a fact changes in one place and can never disagree with itself across pages.</td></tr>
        <tr><td>Sitemap, feed, robots</td><td><span class="chip chip--ok">yes</span></td><td>Generated at build time from the same guide registry that generates the pages. A new guide cannot be missing from the sitemap or the feed.</td></tr>
        <tr><td>Link resolution check</td><td><span class="chip chip--ok">yes</span></td><td>The validator fails the build if a published product's intended ASIN disagrees with the recorded observation, or if any product link lacks the tag parameter.</td></tr>
        <tr><td>Disclosure presence</td><td><span class="chip chip--ok">yes</span></td><td>The validator fails the build if any page is missing either the FTC wording or the Amazon Associates statement, or if a paid link is not labelled.</td></tr>
        <tr><td>Broken internal links</td><td><span class="chip chip--ok">yes</span></td><td>Every internal href is resolved against the generated file tree; the build fails on a 404.</td></tr>
        <tr><td>Price and availability</td><td><span class="chip chip--stop">refused</span></td><td>Not permitted unless Amazon serves the data or it comes from the Creators API. No credentials exist, so the site publishes none.</td></tr>
        <tr><td>Article generation from listing text</td><td><span class="chip chip--stop">refused</span></td><td>Amazon prohibits using Program Content to develop machine learning models without prior written approval.</td></tr>
        <tr><td>Automatic product selection</td><td><span class="chip chip--flag">gated</span></td><td>Topics and products are an editorial judgement with a legal consequence. The machine can check a choice; it cannot defend one.</td></tr>
        <tr><td>Campaign optimisation</td><td><span class="chip chip--muted">not possible yet</span></td><td>Requires measured click and order data. The instrument is shipped and dormant; the collector is not configured.</td></tr>
      </tbody>
    </table>
  </div>

  <h2>What the gate actually checks</h2>
  <p><code>tools/validate.mjs</code> runs on every push and blocks publication on any of the following. These are hard failures, not warnings.</p>
  <ol>
    <li><strong>Disclosure present on every page.</strong> Both the FTC wording and the exact Amazon Associates statement must appear in the HTML.</li>
    <li><strong>Every outbound Amazon link is tagged and labelled.</strong> The <code>tag=${SITE.trackingId}</code> parameter must be present, the link must carry <code>rel="sponsored"</code>, and the literal words <em>Paid link</em> must sit beside it.</li>
    <li><strong>Identity agreement.</strong> For every published product, <code>intended_asin</code> must equal the ASIN embedded in <code>intended_listing_url</code>, and the resolution status must be <code>resolved</code>.</li>
    <li><strong>No price or rating leakage.</strong> A currency pattern or a star-rating pattern in the generated HTML fails the build, because both are things this site has decided never to publish.</li>
    <li><strong>No unresolved product in the catalogue.</strong> A product without a verified ASIN cannot be marked published.</li>
    <li><strong>Internal links resolve.</strong> Every relative href must correspond to a generated file.</li>
    <li><strong>Structured data parses.</strong> Every JSON-LD block is parsed and required fields are asserted.</li>
    <li><strong>Sitemap and feed agree with the pages.</strong> Every indexable route appears in the sitemap exactly once.</li>
  </ol>
  <p class="small muted">The gate is deliberately blunt. It cannot tell whether a sentence is true — that remains a human job — but it can make the mechanical failures impossible to ship.</p>

  <h2>Product data path, if API access is ever granted</h2>
  <p>Any future automation must target the <strong>Creators API</strong>. PA-API 5 is deprecated and returns an access-denied error to integrations that still call it. <a href="${SITE.base}/review/sources/#C-13">C-13</a></p>
  <ol>
    <li>Obtain credentials: a key pair plus the Associates tag, both assigned to this account. <a href="${SITE.base}/review/sources/#C-14">C-14</a></li>
    <li>Fetch only the fields the design uses. Do not cache image content; the licence limits even a stored image link to 24 hours. <a href="${SITE.base}/review/sources/#C-12">C-12</a></li>
    <li>Render price only inside an Amazon-served element, and never in a cross-retailer comparison without both the lowest new and lowest used price. <a href="${SITE.base}/review/sources/#C-09">C-09</a> <a href="${SITE.base}/review/sources/#C-10">C-10</a></li>
    <li>Re-verify at build time that no cached figure is older than the permitted window.</li>
  </ol>

  <h2>What is not automated, on purpose</h2>
  <ul>
    <li>Choosing which product to recommend. That carries a legal disclosure obligation, so a named editor owns it.</li>
    <li>Writing the prose. A model may not be fed listing content, so there is no compliant way to generate these articles from the data the site holds.</li>
    <li>Deciding whether a claim is true. The validator checks that a source exists for a claim; it cannot check that the source says what we think it says.</li>
    <li>Publishing a new guide. A new file appears in the sitemap and feed automatically, but the gate runs first and a human signs the page.</li>
  </ul>

  <div class="callout">
    <span class="callout__label">Failure direction</span>
    <p class="small" style="margin:0">When the gate is unsure, it fails the build. A blocked deploy costs an hour; a published page with a missing disclosure or an untagged link costs the account.</p>
  </div>
</section>`;

  return page({
    path: "/operations/automation/",
    title: `Automation and gates — ${SITE.name}`,
    description: "What is automated in this build, what is refused on policy grounds, and the exact checks that block publication.",
    body,
    current: "/operations/automation/",
  });
}

/* ------------------------------------------------------------ measurement */
function measurement() {
  const events = [
    ["page_view", "Every page load", "path, referrer category (search / direct / referral / internal), viewport bucket", "No IP, no user agent string, no fingerprint"],
    ["guide_read", "A guide page reaching 75% scroll depth", "path, minutes on page rounded to the minute", "No scroll positions, no keystrokes"],
    ["product_view", "A product page load", "product id, entry path", "No cross-visit identity"],
    ["outbound_click", "A click on a paid Amazon link", "product id, page path, link position on page", "No Amazon customer data, no order attribution"],
    ["capture_submit", "The newsletter form being submitted", "page path, whether the field validated", "No email address is sent to analytics, ever"],
  ];

  const body = `${breadcrumb([["Home", "/"], ["Operations", null], ["Measurement", null]])}
${head(
    "Measurement plan",
    "Five events, no cookies, and a collector that is not switched on",
    "Click and conversion measurement was supposed to come first. Here is the instrument, the payloads, and an honest statement that no endpoint exists yet.",
    `<span>Updated ${SITE.published}</span><span>Collector: not configured</span>`
  )}
<section class="section wrap">
  ${note(
    "The site emits the events below to a documented interface. Because no endpoint is configured, every event is dropped before it leaves the browser. Nothing is being recorded, and no figure anywhere on this site is derived from measurement."
  )}

  <h2>The five events</h2>
  <div class="tablewrap">
    <table class="data">
      <thead><tr><th>Event</th><th>Fires when</th><th>Payload</th><th>Deliberately excluded</th></tr></thead>
      <tbody>
        ${events.map((e) => `<tr><td><code>${e[0]}</code></td><td>${e[1]}</td><td class="tiny">${e[2]}</td><td class="tiny">${e[3]}</td></tr>`).join("")}
      </tbody>
    </table>
  </div>

  <h2>Why not just install Google Analytics</h2>
  <p>You can, and it may be the right answer. It is free, it is capable, and it comes with a consent obligation in several jurisdictions and a third-party script on every page. The design here is the opposite: a small first-party collector that stores aggregate counts and nothing that identifies a person. That choice is not free either — you have to run it.</p>
  <p>The decision is recorded as <a href="${SITE.base}/review/suggestions/#SUG-11">SUG-11</a> with three paths and a recommendation, so it can be made deliberately rather than by default.</p>

  <h2>What "conversion" means here</h2>
  <p>Two different things get called a conversion, and conflating them is how affiliate reporting goes wrong:</p>
  <ul>
    <li><strong>An outbound click</strong> — measured by this site, at the moment someone leaves for Amazon. This site can count it.</li>
    <li><strong>A qualifying purchase</strong> — measured only by Amazon, inside a session that begins with a click on a tagged Special Link and ends at the first of 24 hours, an order, or a click on a different Associates link. Cart purchases can still qualify up to 89 days later. This site cannot count it. <a href="${SITE.base}/review/sources/#C-18">C-18</a></li>
  </ul>
  <p>So the site reports clicks. It does not report a conversion rate, because the denominator would be invented. When Amazon reports orders, they go into the <a href="${SITE.base}/review/campaign-ledger/">campaign ledger</a> with the report date, and never into a score.</p>

  <h2>What is not measured, and why that is a problem</h2>
  <ul>
    <li><strong>Which question actually brings people in.</strong> Needs Search Console (see below) or a search-referrer breakdown from the collector.</li>
    <li><strong>Whether anyone reaches the paid link.</strong> Will be measurable once the collector exists; today the <code>outbound_click</code> event fires into nothing.</li>
    <li><strong>Whether a click becomes an order.</strong> Requires Amazon's report, which requires a working tagged link, which is the open item in <a href="${SITE.base}/review/flagged-for-review/#FLG-002">FLG-002</a>.</li>
  </ul>

  <h2>Turning it on</h2>
  <ol>
    <li>Choose a host for the endpoint and decide the retention period. Recommended: 30 days for raw aggregates, indefinite for daily totals.</li>
    <li>Set <code>ANALYTICS_ENDPOINT</code> in <code>assets/js/analytics-config.js</code>. The file ships with an empty string, which is why nothing transmits.</li>
    <li>Update the <a href="${SITE.base}/privacy/">privacy page</a> before switching it on, not after.</li>
    <li>Record the switch-on date in the campaign ledger so every later figure has a start date.</li>
    <li>Verify the property in Search Console and submit <code>/Affil3/sitemap.xml</code>.</li>
  </ol>

  <div class="callout callout--verify">
    <span class="callout__label">The honest status</span>
    <p class="small" style="margin:0">Instrument: shipped. Collector: not configured. Search Console: not verified. Therefore: zero measured data, and no optimisation claim anywhere on this site. <a href="${SITE.base}/review/flagged-for-review/#FLG-006">FLG-006</a> · <a href="${SITE.base}/review/flagged-for-review/#FLG-007">FLG-007</a></p>
  </div>
</section>`;

  return page({
    path: "/operations/measurement/",
    title: `Measurement plan — ${SITE.name}`,
    description: "The five defined events, their payloads, what is deliberately excluded for privacy, and the honest statement that no analytics collector is live yet.",
    body,
    current: "/operations/measurement/",
  });
}

/* ---------------------------------------------------------- discoverability */
function discoverability() {
  const body = `${breadcrumb([["Home", "/"], ["Operations", null], ["Discoverability", null]])}
${head(
    "Discoverability",
    "One site to index, and a reason to rank it",
    "A search engine needs a canonical version of every page, a map of them, and a reason to prefer them to the alternatives. Here is what this build provides for each.",
    `<span>Updated ${SITE.published}</span><span>sitemap · feed · structured data</span>`
  )}
<section class="section wrap">
  <div class="tablewrap">
    <table class="data">
      <thead><tr><th>Signal</th><th>What exists</th><th>Why it matters</th></tr></thead>
      <tbody>
        <tr><td>Canonical URL</td><td>Every page declares one <code>rel="canonical"</code> absolute URL</td><td>A canonical annotation is a strong consolidation signal. <a href="${SITE.base}/review/sources/#C-20">C-20</a></td></tr>
        <tr><td>XML sitemap</td><td><code>/sitemap.xml</code>, generated at build time, every indexable route exactly once</td><td>Sitemap inclusion is a weaker signal than a canonical, but it helps discovery. <a href="${SITE.base}/review/sources/#C-20">C-20</a></td></tr>
        <tr><td>robots.txt</td><td><code>/robots.txt</code> with an explicit sitemap declaration</td><td>Points a crawler at the map without needing a submission.</td></tr>
        <tr><td>RSS feed</td><td><code>/feed.xml</code>, one item per guide, with publication dates</td><td>Google supports RSS as a sitemap format, so the feed is a second discovery path. <a href="${SITE.base}/review/sources/#C-22">C-22</a></td></tr>
        <tr><td>Structured data</td><td>Organization, WebSite, Article, CollectionPage, Product and Review</td><td>Gives a crawler unambiguous entity information instead of inferring it from prose.</td></tr>
        <tr><td>Duplicate risk</td><td>Project path only, no alternate hostname, no query-string variants, no print views</td><td>Fewer URLs describing the same page, so less for a canonical to resolve.</td></tr>
        <tr><td>Question-shaped pages</td><td>Six pages, each targeting a decision rather than a product keyword</td><td>A category page competes with Amazon. A question does not.</td></tr>
      </tbody>
    </table>
  </div>

  <h2>What is missing</h2>
  <p><strong>Verification and submission.</strong> The property could not be verified from this environment, so the sitemap has not been submitted and no query data exists. This is the single most important open item for organic traffic. <a href="${SITE.base}/review/flagged-for-review/#FLG-007">FLG-007</a></p>
  <p><strong>Search demand evidence.</strong> The six guides were chosen on editorial judgement. Nothing on this site claims a search volume, a difficulty score or a trend, because no keyword tool was consulted. <a href="${SITE.base}/review/questions/#Q-05">Q-05</a></p>
  <p><strong>Links from anywhere else.</strong> Nothing points at this site yet, and no link-building tactic is proposed here, because the honest ones take time and the dishonest ones are a penalty risk.</p>

  <h2>A publishing cadence that compounds</h2>
  <ol>
    <li><strong>Ship two verified guides a month.</strong> Each one adds a sitemap entry and a feed item automatically, with no manual bookkeeping.</li>
    <li><strong>Read queries after four to six weeks.</strong> Write the next guide in the language people actually used, not the language we guessed.</li>
    <li><strong>Update rather than pile up.</strong> A revised guide with a new <code>dateModified</code> is worth more than two thin ones.</li>
    <li><strong>Retire what stops being true.</strong> When a product listing changes materially, the page that described it is corrected or removed, not left to rot.</li>
  </ol>

  <div class="callout">
    <span class="callout__label">Rule of thumb</span>
    <p class="small" style="margin:0">One verified page that answers one question beats ten pages that summarise a category. The sitemap does not care how many URLs it holds; a crawler only keeps the ones worth keeping.</p>
  </div>
</section>`;

  return page({
    path: "/operations/discoverability/",
    title: `Discoverability — ${SITE.name}`,
    description: "Canonical URLs, a generated sitemap, an RSS feed, structured data and question-shaped pages, plus the verification step that is still missing.",
    body,
    current: "/operations/discoverability/",
  });
}

export function buildOps(ctx) {
  const { out, addRoute } = ctx;
  const pages = [
    ["/operations/automation/", automation, 0.6],
    ["/operations/measurement/", measurement, 0.6],
    ["/operations/discoverability/", discoverability, 0.5],
  ];
  for (const [path, fn, pr] of pages) {
    addRoute(path, { priority: pr, changefreq: "monthly" });
    out(`${path.slice(1)}index.html`, fn(ctx));
  }
}
