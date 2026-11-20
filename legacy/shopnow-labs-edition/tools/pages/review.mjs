// The review room: executive summary, product register, suggestions, questions,
// flagged items, source register, campaign ledger.
import { page, breadcrumb, SITE, paidLink } from "../lib/layout.mjs";

const reviewBar = (label) => `<div class="reviewbar"><div class="wrap">
  <strong>Review room</strong>
  <span>${label}</span>
  <span style="margin-left:auto"><a href="${SITE.base}/review/suggestions/">Suggestion register</a> · <a href="${SITE.base}/review/questions/">Open questions</a> · <a href="${SITE.base}/review/flagged-for-review/">Known gaps</a></span>
</div></div>`;

const head = (kicker, h1, lede, meta = "") => `
<section class="article-head wrap">
  <p class="kicker">${kicker}</p>
  <h1>${h1}</h1>
  <p class="lede">${lede}</p>
  ${meta ? `<div class="article-head__meta">${meta}</div>` : ""}
</section>`;

const reviewerNote = (text) =>
  `<div class="callout callout--warn" style="margin-bottom:1.5rem"><span class="callout__label">For the reviewer</span><p class="small" style="margin:0">${text}</p></div>`;

const chip = (kind, label) => `<span class="chip chip--${kind}">${label}</span>`;

/* ------------------------------------------------------- executive summary */
function executive({ DATA }) {
  const { products } = DATA.products;
  const resolved = products.filter((p) => p.observed_resolution_status === "resolved");
  const tags = products.filter((p) => p.observed_tag_parameter && p.observed_tag_parameter !== "none present in the observed redirect target");
  const openSugg = DATA.suggestions.suggestions.filter((s) => s.decision === "open");
  const criticalFlags = DATA.flags.flags.filter((f) => f.severity === "high");

  const body = `${reviewBar("Executive summary · the whole project on one page")}
${head(
    "Executive summary",
    "What was built, what was verified, and what still needs a decision",
    "Six minutes of reading before you look at anything else. Every number here is countable from the repository, and every claim links to the register that holds its source.",
    `<span>Prepared ${SITE.published}</span><span>Repository karagemop466-tech/Affil3</span>`
  )}
<section class="section wrap">

  <div class="stat-grid" style="margin-bottom:2rem">
    <div class="stat"><div class="stat__n">${resolved.length}<span style="font-size:1rem;color:var(--ink-3)">/${products.length}</span></div><div class="stat__l">Submitted links resolved</div></div>
    <div class="stat"><div class="stat__n">${DATA.claims.claims.filter((c) => c.status === "verified" || c.status === "verified-excerpt").length}</div><div class="stat__l">Claims sourced</div></div>
    <div class="stat"><div class="stat__n">${DATA.flags.flags.length}</div><div class="stat__l">Irregularities published</div></div>
    <div class="stat"><div class="stat__n">${openSugg.length}</div><div class="stat__l">Decisions awaiting you</div></div>
  </div>

  <h2>The situation in five sentences</h2>
  <p>You supplied five Amazon short links and a tracking ID. Four resolved to real product pages; the fifth was stopped by an Amazon checkpoint page and has no verified identity. None of the four observed redirects carried a visible Associates tag, which means attribution cannot be confirmed from outside the account. The site therefore ships with canonical, tagged product links, publishes no prices and no ratings because policy and accuracy both forbid it, and states on every page that no product here has been physically tested. Everything that could not be settled is published openly rather than smoothed over, so you can make the call after launch rather than before.</p>

  <h2>What was built</h2>
  <div class="tablewrap">
    <table class="data">
      <thead><tr><th>Surface</th><th>What it is</th><th>Why it exists</th></tr></thead>
      <tbody>
        <tr><td><a href="${SITE.base}/">Front page</a></td><td>A publication front page: lead guide, product shelf, collections, capture</td><td>Reads like a shop. Registers reachable from one footer group instead of a nav bar full of dashboards.</td></tr>
        <tr><td><a href="${SITE.base}/buying-guides/">Six buyer guides</a></td><td>Question-shaped articles, 6–8 minutes each</td><td>Each answers one decision a buyer actually faces, then hands off to the product that fits.</td></tr>
        <tr><td><a href="${SITE.base}/air-fryers/">Category desks</a></td><td>Air fryers and thermometers, card view and scan table</td><td>Organised by category as requested, with a table a buyer can read in ten seconds.</td></tr>
        <tr><td><a href="${SITE.base}/products/chefman-6qt-dual-basket-air-fryer/">Product pages</a></td><td>One page per verified product, specs as stated, objections included</td><td>Spec traceability plus the honest objection, which is the part buyers actually need.</td></tr>
        <tr><td><a href="${SITE.base}/review/suggestions/">Suggestion register</a></td><td>${DATA.suggestions.suggestions.length} suggestions, each with paths and a recommended one</td><td>The decision room you asked for. Choose a path before anything is implemented.</td></tr>
        <tr><td><a href="${SITE.base}/review/questions/">Open questions</a></td><td>${DATA.questions.questions.length} questions, each with what we know, what we don't, and how to close it</td><td>Separates missing information from settled fact.</td></tr>
        <tr><td><a href="${SITE.base}/review/flagged-for-review/">Known gaps</a></td><td>${DATA.flags.flags.length} irregularities with sources and a fix</td><td>Nothing is hidden to make the site look finished.</td></tr>
        <tr><td><a href="${SITE.base}/operations/automation/">Automation and gates</a></td><td>What is automated, what is gated, what is deliberately refused</td><td>Automation you can audit, and a build that fails rather than publishing something wrong.</td></tr>
        <tr><td><a href="${SITE.base}/operations/measurement/">Measurement plan</a></td><td>Five defined events, privacy-preserving, no collector yet</td><td>Instrument shipped before optimisation, as instructed.</td></tr>
      </tbody>
    </table>
  </div>

  <h2>Verification method, in full</h2>
  <ol>
    <li><strong>Every submitted link was requested</strong> and the final URL and page title recorded. Intended and observed values went into separate fields and were never merged.</li>
    <li><strong>Every compliance statement was read from the official page</strong>, quoted verbatim, and stored with its section number and retrieval date in the <a href="${SITE.base}/review/sources/">source register</a>.</li>
    <li><strong>Specifications were taken only from listing text that was actually retrieved.</strong> Anything absent — interior dimensions, wattage, probe diameter, two review summaries — was left blank and flagged.</li>
    <li><strong>Secondary sources were not used as evidence.</strong> Where a claim exists only in commentary (the API eligibility threshold, search volumes), it appears as an open question, not a fact.</li>
    <li><strong>A validator runs on every build</strong> and fails on a mismatched ASIN, a missing disclosure, an untagged product link, or a broken internal link.</li>
  </ol>

  <h2>What could not be verified, and why it matters</h2>
  <div class="tablewrap">
    <table class="data">
      <thead><tr><th>Item</th><th>Status</th><th>Consequence</th><th>Closes when</th></tr></thead>
      <tbody>
        ${DATA.flags.flags
          .map(
            (f) => `<tr>
          <td><a href="${SITE.base}/review/flagged-for-review/#${f.id}">${f.id}</a> ${f.title}</td>
          <td>${f.severity === "high" ? chip("stop", "high") : f.severity === "medium" ? chip("flag", "medium") : chip("muted", "low")}</td>
          <td>${f.impact}</td>
          <td>${f.fix}</td>
        </tr>`
          )
          .join("")}
      </tbody>
    </table>
  </div>

  <h2>Commercial reality, stated without a forecast</h2>
  <p>There is no traffic, no click data and no revenue figure in this report, because none has been measured. The <a href="${SITE.base}/review/campaign-ledger/">campaign ledger</a> starts deliberately empty and defines the fields that will be filled only from authorised first-party reports. Anyone who shows you a conversion projection for a site that launched today is guessing.</p>
  <p>What can be said is structural: the site now has six indexable pages answering distinct buying questions, a sitemap, a feed, structured data, and one product page per verified product. That is the minimum a search engine needs to begin ranking something. Whether it does is an empirical question, and <a href="${SITE.base}/review/questions/">Q-05</a> is the one that answers it.</p>

  <h2>The four decisions that actually need you</h2>
  <ol>
    <li><strong>Confirm the tag works.</strong> One SiteStripe link, one test click, one report check. Everything commercial depends on it. <a href="${SITE.base}/review/suggestions/#SUG-09">SUG-09</a></li>
    <li><strong>Send the fifth product's real URL.</strong> One line of text, and the catalogue is complete. <a href="${SITE.base}/review/suggestions/#SUG-12">SUG-12</a></li>
    <li><strong>Decide where analytics lands.</strong> The event code is shipped and dormant; the endpoint is your call. <a href="${SITE.base}/review/suggestions/#SUG-11">SUG-11</a></li>
    <li><strong>Say what success means.</strong> A revenue target and a date changes every prioritisation after this one. <a href="${SITE.base}/review/questions/#Q-04">Q-04</a></li>
  </ol>
  <p>Nothing in that list blocks the site from being live. That is why it is live now, with the list attached to it.</p>

  <h2>Reading order for a reviewer</h2>
  <ol>
    <li><a href="${SITE.base}/review/flagged-for-review/">Known gaps</a> — the eight things that are not settled, worst first.</li>
    <li><a href="${SITE.base}/review/suggestions/">Suggestion register</a> — ${DATA.suggestions.suggestions.length} ideas with the paths not taken, including two that are blocked by policy.</li>
    <li><a href="${SITE.base}/review/sources/">Source register</a> — ${DATA.claims.claims.length} claims and the exact document each came from.</li>
    <li><a href="${SITE.base}/review/questions/">Open questions</a> — what a decision is waiting on.</li>
    <li>The site itself, starting at the <a href="${SITE.base}/">front page</a>.</li>
  </ol>
</section>`;

  return page({
    path: "/review/executive-summary/",
    title: `Executive summary — ${SITE.name}`,
    description: "The whole project on one page: what was built, what was verified against official sources, what could not be verified, and the four decisions that need the owner.",
    body,
    current: "/review/executive-summary/",
  });
}

/* ------------------------------------------------------- product register */
function register({ DATA }) {
  const rows = DATA.products.products
    .map((p) => {
      const resolved = p.observed_resolution_status === "resolved";
      return `<tr id="${p.id}">
      <td>${p.published ? `<a href="${SITE.base}/products/${p.slug}/">${p.short_name}</a>` : `<strong>${p.working_name}</strong>`}<br><span class="id">${p.intended_asin || "no ASIN"}</span></td>
      <td><a href="${p.submitted_link}" target="_blank" rel="nofollow noopener"><code>${p.submitted_link}</code></a></td>
      <td>${p.intended_asin || "—"}<br><span class="tiny muted">${p.confirmation_date || "unconfirmed"}</span></td>
      <td>${
        p.observed_resolution_status === "resolved"
          ? `<a href="${p.observed_redirect_target}" target="_blank" rel="nofollow noopener" class="tiny"><code>${p.observed_redirect_target.split("?")[0]}</code></a>`
          : p.observed_targets_log && p.observed_targets_log.length
            ? `<span class="tiny"><strong>${p.observed_targets_log.length} observations, no agreement:</strong><br>` +
              p.observed_targets_log
                .map((o) => `(${o.run}) ${o.result === "product" ? `<a href="${o.final_url}" target="_blank" rel="nofollow noopener"><code>${o.final_url.split("/").pop()}</code></a>` : `<span class="muted">checkpoint, no product</span>`}`)
                .join("<br>") +
              `</span>`
            : `<span class="tiny muted">checkpoint page, no product</span>`
      }</td>
      <td>${p.observed_tag_parameter && p.observed_tag_parameter !== "none present in the observed redirect target" ? chip("ok", "tag present") : chip("stop", "no tag seen")}</td>
      <td>${resolved ? chip("ok", "resolved") : chip("stop", "blocked")}</td>
      <td>${p.published ? chip("info", "live") : chip("flag", p.flag)}</td>
    </tr>`;
    })
    .join("");

  const body = `${reviewBar("Product register · intended vs observed")}
${head(
    "Product register",
    "Five submissions, recorded as intended and as observed",
    "The rule this table enforces: what you said the link should point to and what the request actually returned are two different fields. They are never merged, because merging them is how a broken affiliate link hides for months.",
    `<span>Retrieved ${SITE.published}</span><span>Separate fields, by design</span>`
  )}
<section class="section wrap">
  ${reviewerNote(
    "Every row below was produced by requesting the submitted link in this session. The <em>intended</em> column is the product the link should reach; the <em>observed</em> column is where it actually went. The tag column reports whether an Associates tag parameter appeared in the observed redirect — not whether the link works in Amazon's internal attribution."
  )}

  <div class="tablewrap">
    <table class="data">
      <thead><tr>
        <th>Product / ASIN</th><th>Submitted link</th><th>Intended ASIN + date</th><th>Observed redirect target</th><th>Tag in redirect</th><th>Resolution</th><th>Site status</th>
      </tr></thead>
      <tbody>${rows}</tbody>
    </table>
  </div>

  ${
    DATA.products.products.some((p) => p.observed_targets_log && p.observed_targets_log.length)
      ? `<h2 style="margin-top:2.5rem">Every observation of the fifth link</h2>
  <p class="small">The fifth link was requested four times from this environment, plus once by an independent dated retest recorded by another session in this repository. The product page was reached twice and an Amazon checkpoint page three times. Every observation is listed rather than reduced to one "observed" value, because the interception rate is the finding.</p>
  <div class="tablewrap">
    <table class="data">
      <thead><tr><th>Observation</th><th>Result</th><th>Final URL</th><th>Page title observed</th><th>Date</th></tr></thead>
      <tbody>
        ${DATA.products.products
          .filter((p) => p.observed_targets_log)
          .flatMap((p) =>
            p.observed_targets_log.map(
              (o) => `<tr><td>${o.run}</td><td>${o.result === "product" ? chip("flag", "product page") : chip("stop", "checkpoint")}</td><td>${o.final_url ? `<a href="${o.final_url}" target="_blank" rel="nofollow noopener" class="tiny"><code>${o.final_url}</code></a>` : "—"}</td><td class="tiny">${o.title || "no product title returned"}</td><td>${o.date}</td></tr>`
            )
          )
          .join("")}
      </tbody>
    </table>
  </div>
  <p class="small" style="margin-top:.8rem">The product behind this link was never submitted by the owner and is not a countertop appliance of the same kind as the other four, so it is identified but not added to the catalogue. Logged as <a href="${SITE.base}/review/flagged-for-review/#FLG-001">FLG-001</a>.</p>
  <div class="callout callout--warn" style="margin-top:1rem"><span class="callout__label">Correction, published rather than hidden</span>
  <p class="small" style="margin:0">An earlier version of this register said this link resolved to the Chefman TurboFry. It does not. That was a transcription error in this session's own notes, found by comparing against another session's independent retest. The correction and its cause are logged as <a href="${SITE.base}/review/flagged-for-review/#FLG-012">FLG-012</a>.</p></div>`
      : ""
  }

  <h2 style="margin-top:2.5rem">Link construction used on the site</h2>
  <p class="small">Every published product link is built as a canonical Amazon address plus the Associates tag, rather than by reusing the supplied short link. The reason is in <a href="${SITE.base}/review/suggestions/#SUG-09">SUG-09</a>: the short links did not show a tag in the redirect, so their attribution cannot be confirmed from outside the account. This is a risk-averse choice, not a claim that the supplied links are invalid.</p>
  <div class="tablewrap">
    <table class="data">
      <thead><tr><th>Product</th><th>Link used on this site</th><th>Tag parameter</th></tr></thead>
      <tbody>
        ${DATA.products.products
          .filter((p) => p.published)
          .map(
            (p) => `<tr><td>${p.short_name}</td><td><code>${p.tagged_url.replace("?tag=" + SITE.trackingId, "")}</code></td><td><code>?tag=${SITE.trackingId}</code></td></tr>`
          )
          .join("")}
      </tbody>
    </table>
  </div>

  <h2 style="margin-top:2.5rem">Specification provenance</h2>
  <p class="small">Each specification below appears in the retrieved listing text. Anything not stated is marked, not estimated.</p>
  <div class="tablewrap">
    <table class="data">
      <thead><tr><th>Product</th><th>Specification as stated</th><th>Source</th></tr></thead>
      <tbody>
        ${DATA.products.products
          .filter((p) => p.published)
          .flatMap((p) =>
            (p.attributes_from_listing || []).map(
              (a) => `<tr><td>${p.short_name}</td><td>${a.name}: <strong>${a.value}</strong>${a.note ? ` <span class="muted tiny">(${a.note})</span>` : ""}</td><td><a href="${p.intended_listing_url}" target="_blank" rel="nofollow noopener" class="tiny">listing</a> <span class="tiny muted">${p.confirmation_date}</span></td></tr>`
            )
          )
          .join("")}
      </tbody>
    </table>
  </div>

  <h2 style="margin-top:2.5rem">Fields deliberately left blank</h2>
  <div class="tablewrap">
    <table class="data">
      <thead><tr><th>Field</th><th>Why blank</th><th>Flag</th></tr></thead>
      <tbody>
        <tr><td>Price, for every product</td><td>Amazon permits price display only through its own served link or its API; we hold neither. Also changes hourly.</td><td><a href="${SITE.base}/review/flagged-for-review/#FLG-004">FLG-004</a></td></tr>
        <tr><td>Star rating and review count</td><td>Moves daily, and the average hides the distribution. Review sentiment is reported only where Amazon's own summary was displayed.</td><td><a href="${SITE.base}/review/flagged-for-review/#FLG-004">FLG-004</a></td></tr>
        <tr><td>Interior dimensions, wattage</td><td>Not present in the retrieved listing text for any of the three appliances. Not estimated.</td><td><a href="${SITE.base}/review/flagged-for-review/#FLG-008">FLG-008</a></td></tr>
        <tr><td>Probe diameter, battery life</td><td>Not present in the retrieved listing text.</td><td><a href="${SITE.base}/review/flagged-for-review/#FLG-008">FLG-008</a></td></tr>
        <tr><td>Fifth product: name, ASIN, everything</td><td>The link never resolved to a product page.</td><td><a href="${SITE.base}/review/flagged-for-review/#FLG-001">FLG-001</a></td></tr>
        <tr><td>Review summaries for two listings</td><td>Not captured during retrieval; characterised only where displayed.</td><td><a href="${SITE.base}/review/flagged-for-review/#FLG-008">FLG-008</a></td></tr>
      </tbody>
    </table>
  </div>
</section>`;

  return page({
    path: "/review/product-register/",
    title: `Product register — ${SITE.name}`,
    description: "The five submitted products with intended ASIN and observed redirect target recorded as separate fields, plus specification provenance and every deliberately blank field.",
    body,
    current: "/review/product-register/",
  });
}

/* ---------------------------------------------------------- suggestions */
function suggestions({ DATA, priorityScore }) {
  const list = [...DATA.suggestions.suggestions].sort((a, b) => priorityScore(b) - priorityScore(a));
  const counts = DATA.suggestions.suggestions.reduce((acc, s) => ((acc[s.decision] = (acc[s.decision] || 0) + 1), acc), {});

  const card = (s) => {
    const score = priorityScore(s);
    const decisionChip =
      s.decision === "applied" ? chip("ok", "applied in this build")
      : s.decision === "blocked" ? chip("stop", "blocked by policy")
      : s.decision === "deferred" ? chip("muted", "deferred")
      : chip("flag", "needs your call");

    return `<article class="sugg__item" id="${s.id}">
      <div class="sugg__score"><b>${score}</b><span>priority</span></div>
      <div>
        <div style="display:flex;gap:.5rem;flex-wrap:wrap;align-items:center;margin-bottom:.5rem">
          <span class="id" style="font-family:var(--mono);font-size:.7rem;color:var(--ink-3)">${s.id}</span>
          ${decisionChip}
          ${chip("muted", s.pillar)}
          ${chip("muted", `${s.impact} impact`)}
        </div>
        <h3 class="sugg__title">${s.title}</h3>
        <p class="sugg__why">${s.why}</p>

        <div class="sugg__paths">
          ${s.paths
            .map(
              (p) => `<div class="path${p.picked ? " path--pick" : ""}">
            <span class="path__k">${p.id}${p.picked ? " ✓" : ""}</span>
            <span><strong>${p.label}</strong><br><span class="muted">${p.tradeoff}</span></span>
          </div>`
            )
            .join("")}
        </div>

        ${
          s.evidence && s.evidence.length
            ? `<div class="sugg__meta" style="margin-top:.8rem">Evidence: ${s.evidence
                .map((c) => {
                  const claim = DATA.claims.claims.find((x) => x.id === c);
                  return claim ? `<a href="${SITE.base}/review/sources/#${c}">${c}</a>` : c;
                })
                .join(", ")}</div>`
            : `<div class="sugg__meta" style="margin-top:.8rem"><span class="muted">No regulatory evidence required: this is an editorial judgement.</span></div>`
        }
        ${s.recommended ? `<div class="sugg__meta" style="margin-top:.4rem">Desk recommendation: <strong>path ${s.recommended}</strong></div>` : ""}
        ${s.blocked_by ? `<div class="sugg__meta" style="margin-top:.4rem;color:var(--flag)">Cannot proceed yet: ${s.blocked_by}</div>` : ""}
        ${s.implemented_as ? `<div class="sugg__meta" style="margin-top:.4rem">Applied as: <span class="muted">${s.implemented_as}</span></div>` : ""}
        ${s.what_would_change_our_mind ? `<div class="sugg__meta" style="margin-top:.4rem">What would change our mind: <span class="muted">${s.what_would_change_our_mind}</span></div>` : ""}
      </div>
    </article>`;
  };

  const body = `${reviewBar("Suggestion register · the decision room")}
${head(
    "Decision room",
    "Pick a path before anything changes",
    "Every suggestion below is a choice, not an instruction. Each has its alternatives written out with the trade-off attached, so a reviewer can see what the other path costs before committing.",
    `<span>${DATA.suggestions.suggestions.length} suggestions</span><span>${counts.open || 0} awaiting your call</span><span>${counts.blocked || 0} blocked by policy</span>`
  )}
<section class="section wrap">
  ${reviewerNote(
    "The priority score is an editorial triage heuristic — impact and confidence, minus effort, adjusted for whether the item is still open. It is <strong>not</strong> a measured outcome, not a forecast, and not revenue. It exists only so you can read the list top-down."
  )}

  <div class="stat-grid" style="margin-bottom:2rem">
    <div class="stat"><div class="stat__n">${counts.open || 0}</div><div class="stat__l">Need a decision</div></div>
    <div class="stat"><div class="stat__n">${counts.applied || 0}</div><div class="stat__l">Applied, reversible</div></div>
    <div class="stat"><div class="stat__n">${counts.blocked || 0}</div><div class="stat__l">Blocked by policy</div></div>
    <div class="stat"><div class="stat__n">${counts.deferred || 0}</div><div class="stat__l">Deferred</div></div>
  </div>

  <h2 style="margin-bottom:1rem">The register, highest priority first</h2>
  <div class="sugg">${list.map(card).join("")}</div>
</section>`;

  return page({
    path: "/review/suggestions/",
    title: `Suggestion register — ${SITE.name}`,
    description: "A decision room of suggestions for improving the site, each with alternative paths, trade-offs, a recommended option and the regulatory evidence where one applies.",
    body,
    current: "/review/suggestions/",
  });
}

/* ------------------------------------------------------------ questions */
function questions({ DATA }) {
  const order = { blocker: 0, high: 1, medium: 2, low: 3 };
  const list = [...DATA.questions.questions].sort((a, b) => (order[a.priority] ?? 9) - (order[b.priority] ?? 9));

  const card = (q) => `<article class="q" id="${q.id}">
    <div class="q__h">
      <h3 class="q__t">${q.question}</h3>
      <div style="display:flex;gap:.4rem;flex-wrap:wrap">
        ${chip(q.priority === "blocker" ? "stop" : q.priority === "high" ? "flag" : "muted", q.priority)}
        ${chip("muted", q.owner)}
        ${q.flag ? `<a class="chip chip--stop" href="${SITE.base}/review/flagged-for-review/#${q.flag.split(",")[0].trim()}" style="text-decoration:none">${q.flag}</a>` : ""}
      </div>
    </div>
    <div class="q__body">
      <div class="q__row"><span class="q__k">Blocks</span><span>${q.blocks}</span></div>
      <div class="q__row"><span class="q__k">We know</span><span>${q.known}</span></div>
      <div class="q__row"><span class="q__k">We don't</span><span>${q.unknown}</span></div>
      <div class="q__row"><span class="q__k">To close it</span><span><strong>${q.to_close}</strong></span></div>
    </div>
  </article>`;

  const body = `${reviewBar("Open questions · what a decision is waiting on")}
${head(
    "Open questions",
    "Twelve things nobody has answered yet",
    "A decision made without these answers is a guess wearing a suit. Each question names what we know, what we do not, and the specific step that would close it.",
    `<span>${DATA.questions.questions.length} questions</span><span>${DATA.questions.questions.filter((q) => q.priority === "blocker").length} blocking</span><span>Updated ${SITE.published}</span>`
  )}
<section class="section wrap">
  ${reviewerNote(
    "Three of these block the commercial case rather than the website: the unresolved product, the untagged links, and unconfirmed enrollment. The site is live anyway because publishing a known gap with its source is more useful than withholding the whole site until it is perfect."
  )}
  <h2 style="margin-bottom:1rem">Blocking and high-priority questions</h2>
  ${list.map(card).join("")}

  <h2 style="margin-top:2.5rem">Questions that were asked and are now closed</h2>
  <p class="small">Recorded so they are not re-litigated later.</p>
  <div class="tablewrap">
    <table class="data">
      <thead><tr><th>Question</th><th>Answer</th><th>Source</th></tr></thead>
      <tbody>
        <tr><td>Can we show a delivery estimate?</td><td>No, unless Amazon serves the link containing the data or it comes from the API.</td><td><a href="${SITE.base}/review/sources/#C-09">C-09</a></td></tr>
        <tr><td>Can we publish prices with a "last updated" note?</td><td>No. The condition is about who serves the data, not how fresh our note is.</td><td><a href="${SITE.base}/review/sources/#C-09">C-09</a></td></tr>
        <tr><td>Is "affiliate link" enough as a disclosure?</td><td>No. The FTC says readers may not understand it means you are paid. "Paid link" beside the link should be adequate.</td><td><a href="${SITE.base}/review/sources/#C-07">C-07</a></td></tr>
        <tr><td>Can we offer a discount for subscribing?</td><td>No. Incentives for using Special Links are prohibited.</td><td><a href="${SITE.base}/review/sources/#C-23">C-23</a></td></tr>
        <tr><td>Is PA-API 5 the way to get product data?</td><td>No. It is deprecated in favour of the Creators API.</td><td><a href="${SITE.base}/review/sources/#C-13">C-13</a></td></tr>
      </tbody>
    </table>
  </div>
</section>`;

  return page({
    path: "/review/questions/",
    title: `Open questions — ${SITE.name}`,
    description: "The twelve questions that must be answered before a decision can reasonably be made, each with what is known, what is missing, and how to close it.",
    body,
    current: "/review/questions/",
  });
}

/* ---------------------------------------------------------------- flags */
function flags({ DATA }) {
  const order = { high: 0, medium: 1, low: 2 };
  const list = [...DATA.flags.flags].sort((a, b) => (order[a.severity] ?? 9) - (order[b.severity] ?? 9));

  const card = (f) => `<article class="flag" id="${f.id}">
    <div style="display:flex;gap:.5rem;align-items:center;flex-wrap:wrap">
      <span class="flag__id">${f.id}</span>
      ${chip(f.severity === "high" ? "stop" : f.severity === "medium" ? "flag" : "muted", `${f.severity} severity`)}
    </div>
    <h3>${f.title}</h3>
    <p>${f.detail}</p>
    <p><strong style="font-size:.8rem">What it affects:</strong> ${f.impact}</p>
    <p><strong style="font-size:.8rem">How it is handled on the site:</strong> ${f.published_handling}</p>
    <div class="flag__fix"><b>How to close it</b>${f.fix}</div>
    ${
      f.sources && f.sources.length
        ? `<p class="tiny" style="margin-top:.7rem">Sources: ${f.sources
            .map((s) => `<a href="${s}" target="_blank" rel="noopener">${s.replace(/^https?:\/\//, "").split("?")[0]}</a>`)
            .join(" · ")}</p>`
        : `<p class="tiny muted" style="margin-top:.7rem">No external source applies; this is a state of the project, not a claim.</p>`
    }
  </article>`;

  const body = `${reviewBar("Known gaps · published, not hidden")}
${head(
    "Flagged for review",
    "Everything that did not check out",
    "This page is the reason to trust the rest of it. Each item below is a real problem found during verification, with what it affects and how to close it. None of them block the site being useful; all of them block the site being finished.",
    `<span>${DATA.flags.flags.length} items</span><span>${DATA.flags.flags.filter((f) => f.severity === "high").length} high severity</span><span>Updated ${SITE.published}</span>`
  )}
<section class="section wrap">
  ${reviewerNote(
    "Nothing on this page prevents the site from going live, and nothing here was quietly dropped. Where a value could not be confirmed from an official source it was left blank in the data and recorded here — no estimate was substituted."
  )}
  <h2 style="margin-bottom:1rem">The list, worst first</h2>
  ${list.map(card).join("")}

  <h2 style="margin-top:2.5rem">How to request a change</h2>
  <p>Pick any item above, read the fix, and either apply it or tell the desk which path to take. The <a href="${SITE.base}/review/suggestions/">suggestion register</a> already contains the decision that corresponds to most of these, with the alternatives and their trade-offs. The route for a correction is the <a href="https://github.com/karagemop466-tech/Affil3/issues" target="_blank" rel="noopener">repository issue tracker</a>.</p>
</section>`;

  return page({
    path: "/review/flagged-for-review/",
    title: `Flagged for review — ${SITE.name}`,
    description: "Every irregularity found during verification: the unresolved product link, untagged redirects, unconfirmed enrollment, and the fields intentionally left blank, each with a source and a fix.",
    body,
    current: "/review/flagged-for-review/",
  });
}

/* --------------------------------------------------------------- sources */
function sources({ DATA }) {
  const srcRows = Object.entries(DATA.claims.meta.sources)
    .map(
      ([id, s]) => `<tr id="${id}"><td>${id}</td><td>${s.title}</td><td><a href="${s.url}" target="_blank" rel="noopener" class="tiny"><code>${s.url.replace(/^https?:\/\//, "")}</code></a></td><td>${s.publisher}</td></tr>`
    )
    .join("");

  const claimRows = DATA.claims.claims
    .map(
      (c) => `<tr id="${c.id}">
      <td>${c.id}</td>
      <td>${c.topic}</td>
      <td>${c.statement}</td>
      <td>${
        c.source
          ? `<a href="${DATA.claims.meta.sources[c.source].url}" target="_blank" rel="noopener">${c.source}</a>${c.section ? `<br><span class="tiny muted">${c.section}</span>` : ""}`
          : `<span class="tiny muted">none</span>`
      }</td>
      <td>${c.status === "verified" ? chip("ok", "verified") : c.status === "verified-excerpt" ? chip("info", "verified, excerpt") : c.status === "unverified" ? chip("stop", "unverified") : chip("muted", c.status)}</td>
      <td>${c.used_on && c.used_on.length ? `<span class="tiny">${c.used_on.join("<br>")}</span>` : `<span class="tiny muted">not published</span>`}</td>
    </tr>`
    )
    .join("");

  const body = `${reviewBar("Source register · claim by claim")}
${head(
    "Source register",
    "Every claim, and the document it came from",
    "If a sentence on this site makes a statement about a rule, a price, a fee or a legal requirement, it is in this table with the section number and the official URL. Quotes are verbatim.",
    `<span>${DATA.claims.claims.length} claims</span><span>${Object.keys(DATA.claims.meta.sources).length} sources</span><span>Read ${DATA.claims.meta.retrieved}</span>`
  )}
<section class="section wrap">
  ${reviewerNote(
    "Two claims are marked <em>verified, excerpt</em>: the page was retrieved, but the specific sentence came from its indexed excerpt rather than the rendered text. Both were treated conservatively when the site was built, and both are flagged so a reviewer can confirm them on a second read. One claim is explicitly unverified and is <em>not</em> published as fact anywhere on the site."
  )}

  <h2>Sources</h2>
  <div class="tablewrap">
    <table class="data">
      <thead><tr><th>ID</th><th>Document</th><th>URL</th><th>Publisher</th></tr></thead>
      <tbody>${srcRows}</tbody>
    </table>
  </div>

  <h2 style="margin-top:2.5rem">Claims</h2>
  <div class="tablewrap">
    <table class="data">
      <thead><tr><th>ID</th><th>Topic</th><th>What we state</th><th>Source</th><th>Status</th><th>Used on</th></tr></thead>
      <tbody>${claimRows}</tbody>
    </table>
  </div>

  <h2 style="margin-top:2.5rem">Verbatim quotes</h2>
  <div class="prose">
    ${DATA.claims.claims
      .filter((c) => c.quote)
      .map(
        (c) => `<blockquote style="font-size:.95rem"><p style="margin-bottom:.4rem">${c.quote}</p><p class="tiny muted" style="margin:0">— ${DATA.claims.meta.sources[c.source].title}${c.section ? `, ${c.section}` : ""} · <a href="${DATA.claims.meta.sources[c.source].url}" target="_blank" rel="noopener">${c.id}</a></p></blockquote>`
      )
      .join("")}
  </div>
</section>`;

  return page({
    path: "/review/sources/",
    title: `Source register — ${SITE.name}`,
    description: "Every compliance and factual claim on the site, quoted verbatim with the official Amazon, FTC, eCFR, Google or sitemaps.org document it came from.",
    body,
    current: "/review/sources/",
  });
}

/* --------------------------------------------------------------- ledger */
function ledger({ DATA }) {
  const { meta, rows } = DATA.ledger;
  const body = `${reviewBar("Campaign ledger · deliberately empty")}
${head(
    "Campaign ledger",
    "An empty ledger with strict rules",
    "This starts with zero rows because no authorised first-party report has been received yet. The schema is fixed now so that no future number can be entered without a source and a date.",
    `<span>${rows.length} rows</span><span>Provenance required</span><span>Updated ${SITE.published}</span>`
  )}
<section class="section wrap">
  ${reviewerNote(
    "A ledger with invented rows is worse than no ledger. Nothing below is a forecast, a benchmark or an industry average. When a row is added it must carry the report it came from and the date it was pulled."
  )}

  <h2>Rules for adding a row</h2>
  <ol>
    <li><strong>Source must be an authorised first-party report.</strong> The Amazon Associates dashboard, the Creators API, or a self-hosted analytics collector. Not an estimate, not a third-party blog, not a scrape.</li>
    <li><strong>Timestamp every row.</strong> A number without a date is a rumour.</li>
    <li><strong>Never mix a click count with an order count.</strong> They come from different systems with different attribution windows, and the session rules matter.</li>
    <li><strong>Leave a field empty rather than estimating it.</strong> An empty cell is honest; a filled guess is not.</li>
    <li><strong>No revenue forecast.</strong> This ledger records what happened, never what might.</li>
  </ol>

  <h2>What the attribution window means for this ledger</h2>
  <p>Amazon's Commission Income Statement defines a session as beginning when a customer clicks a Special Link and ending at the first of: 24 hours elapsing, the customer placing an order, or the customer clicking a different Associates link. Cart purchases can still qualify up to 89 days after the initial click. So a click today and an order next week can belong to the same row, and a click today and an order after someone clicked a competitor's link cannot. ${""} <a href="${SITE.base}/review/sources/#C-18">C-18</a></p>

  <h2>Schema</h2>
  <div class="tablewrap">
    <table class="data">
      <thead><tr><th>Field</th><th>Type</th><th>Rule</th></tr></thead>
      <tbody>
        ${meta.schema.map((f) => `<tr><td>${f.field}</td><td>${f.type}</td><td>${f.rule}</td></tr>`).join("")}
      </tbody>
    </table>
  </div>

  <h2 style="margin-top:2.5rem">Rows</h2>
  <div class="tablewrap">
    <table class="data">
      <thead><tr>${meta.schema.map((f) => `<th>${f.field}</th>`).join("")}</tr></thead>
      <tbody>
        ${
          rows.length
            ? rows.map((r) => `<tr>${meta.schema.map((f) => `<td>${r[f.field] ?? "—"}</td>`).join("")}</tr>`).join("")
            : `<tr><td colspan="${meta.schema.length}" style="text-align:center;padding:2.5rem 1rem;color:var(--ink-3)">No rows yet. No authorised first-party report has been received.<br><span class="tiny">This is the correct state for a site that launched today. See <a href="${SITE.base}/review/flagged-for-review/#FLG-006">FLG-006</a>.</span></td></tr>`
        }
      </tbody>
    </table>
  </div>

  <h2 style="margin-top:2.5rem">Payment timing, for planning only</h2>
  <p>Commission income is paid approximately 60 days after the end of the calendar month in which it was earned, per the Commission Income Statement. That is a payment schedule, not a revenue projection. <a href="${SITE.base}/review/sources/#C-25">C-25</a></p>
</section>`;

  return page({
    path: "/review/campaign-ledger/",
    title: `Campaign ledger — ${SITE.name}`,
    description: "An empty campaign ledger with a fixed schema and strict provenance rules: timestamp, source, channel, eligible sessions, clicks and reported orders, added only from authorised first-party reports.",
    body,
    current: "/review/campaign-ledger/",
  });
}

export function buildReview(ctx) {
  const { out, addRoute } = ctx;
  const pages = [
    ["/review/executive-summary/", executive, 0.7],
    ["/review/product-register/", register, 0.6],
    ["/review/suggestions/", suggestions, 0.6],
    ["/review/questions/", questions, 0.6],
    ["/review/flagged-for-review/", flags, 0.7],
    ["/review/sources/", sources, 0.6],
    ["/review/campaign-ledger/", ledger, 0.4],
  ];
  for (const [path, fn, pr] of pages) {
    addRoute(path, { priority: pr, changefreq: "monthly" });
    out(`${path.slice(1)}index.html`, fn(ctx));
  }
}
