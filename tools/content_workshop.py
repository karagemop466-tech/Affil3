#!/usr/bin/env python3
"""The Crisp Index — workshop pages (verification, decisions, measurement).

Dashboard surfaces live here and in the footer's "The Workshop" group. They are
deliberately plain: registers and gates that make the shop trustworthy.
"""
from build_core import esc


def pages(ctx):
    return [
        executive_summary_page(ctx),
        register_page(ctx),
        flagged_page(ctx),
        suggestions_page(ctx),
        questions_page(ctx),
        ledger_page(ctx),
    ]


def crumb(label):
    return [("The Workshop", "workshop/executive-summary.html"), (label, None)]


def executive_summary_page(ctx):
    ps = ctx.d["products"]["products"]
    resolved = [p for p in ps if p["observed"]["status"] == "resolved"]
    body = f"""
<div class="wrap article-header article">
  <p class="eyebrow">The Workshop · Executive summary</p>
  <h1>Executive summary</h1>
  <p class="lede">What this project is, what shipped, what is verified, what is flagged, and what
  needs a decision. Written for the owner reviewing after launch — same facts as
  <code>EXECUTIVE_SUMMARY.md</code> in the repository.</p>
</div>
<div class="wrap article">
  <h2>1 · The project in one paragraph</h2>
  <p>An Amazon affiliate publication — <strong>{esc(ctx.site['brand'])}</strong> — for countertop
  kitchen products, monetized with tracking ID <strong>{esc(ctx.site['tracking_id'])}</strong>. The
  reader-facing side is a shop-like magazine: question-shaped buyer’s guides, a comparison hub, and
  a test queue of the five submitted links. The machinery side keeps it honest: a source register,
  a flagged-for-review register, a suggestions queue, open questions, and an empty-but-defined
  campaign ledger. Every product link is marked Sponsored and every page carries the required
  Associates statement above the fold.</p>

  <h2>2 · Monetization &amp; links</h2>
  <ul>
    <li>Five links submitted (tokens B04G1MEwY, B02NbDxp3, B00hJ57DV, B0c8moW59, B0f3GKalj).
    Intended identifiers recorded exactly as submitted; observed redirect targets recorded in
    separate fields and never merged.</li>
    <li><strong>{len(resolved)} of 5</strong> submitted links resolved to Amazon listing pages on
    2026-11-20 (three air fryers, one probe thermometer); 1 hit Amazon’s checkpoint interstitial and
    stays unverified {ctx.flag('FLG-004')}.</li>
    <li>Outbound URLs are provisional tagged links
    (<code>?tag={esc(ctx.site['tracking_id'])}</code> on observed listing URLs) pending the
    one-link-per-product Associates workflow test {ctx.flag('FLG-005')}. Per the brief, the short
    links’ compliance status is unresolved and is <em>not</em> claimed invalid {ctx.flag('FLG-003')}.</li>
    <li>All five tokens are 9 characters and mixed case; Amazon’s own ASIN guide documents ASINs as
    10-character codes {ctx.flag('FLG-001')} {ctx.src('S-03')} — a format mismatch, flagged for
    review, not a validity claim.</li>
  </ul>

  <h2>3 · What shipped</h2>
  <ul>
    <li><strong>Publication site</strong> (GitHub Pages): front page, 5 question-shaped guides,
    compare hub, test queue, about/methodology, disclosure page.</li>
    <li><strong>Compliance layer</strong>: disclosure strip on every page + footer repeat (exact
    Operating Agreement statement), Sponsored chips and <code>rel="sponsored"</code> on every
    product link, blank-and-flag rule for unconfirmed values.</li>
    <li><strong>Machinery</strong>: product register, verification log, flag register, suggestions
    queue, open-questions list, campaign ledger schema, privacy-preserving click counter (dry-run),
    sitemap, RSS feed (SG-28), robots.txt, 404 page, build + validation tooling.</li>
  </ul>

  <h2>4 · Verification posture</h2>
  <p>Every table row on data surfaces carries an official source link or an explicit
  “unverified — flagged” state. Sources fetched and cited 2026-11-20: the Associates Operating
  Agreement {ctx.src('S-01')}, Associates disclosure help {ctx.src('S-02')}, Amazon’s ASIN guide
  {ctx.src('S-03')}, FTC Disclosures 101 {ctx.src('S-04')}, FTC Endorsement hub {ctx.src('S-05')},
  and the four observed listing pages {ctx.src('S-06')} {ctx.src('S-07')} {ctx.src('S-08')}
  {ctx.src('S-09')}. Prices, ratings, and review counts are blank everywhere {ctx.flag('FLG-010')}.</p>

  <h2>5 · Measurement (Priority 4 / 5)</h2>
  <p>The campaign ledger is empty and well-defined: rows appear only from authorized first-party
  reports, with a dated provenance trail. No conversion score or revenue forecast exists in this
  project. The click counter ships disabled because GitHub Pages cannot host an endpoint; reference
  servers ship in <code>tools/analytics-endpoint/</code> {ctx.flag('FLG-006')}. The brief’s “five
  defined events” are not enumerated in the brief; a proposed five-event schema awaits confirmation
  {ctx.flag('FLG-009')}.</p>

  <h2>6 · Decisions needed from the owner</h2>
  <p>Fifteen suggestions sit in the
  <a href="{esc(ctx.rel('workshop/suggestions.html'))}">decision queue</a> (brand approval, cadence,
  analytics host, newsletter stack, price display policy, link-swap plan), and twelve
  <a href="{esc(ctx.rel('workshop/questions.html'))}">open questions</a> block specific next steps —
  chief among them: confirming what the five tokens intend to identify (Q-001), and the Associates
  account status for tag {esc(ctx.site['tracking_id'])} (Q-007).</p>

  <h2>7 · Risks &amp; flags</h2>
  <p>Eleven items are <a href="{esc(ctx.rel('workshop/flagged.html'))}">flagged for review</a>;
  none block the site, and none are hidden from readers. The two that gate growth: link compliance
  testing (FLG-003/FLG-005) before adding any product, and the analytics endpoint (FLG-006) before
  any optimization work.</p>

  <h2>8 · Next actions (in order)</h2>
  <ol>
    <li>Owner confirms intended products for the five tokens (Q-001) and Associates status (Q-007).</li>
    <li>Run the one-link-per-product workflow test; swap to validated Special Links (SUG-015).</li>
    <li>Deploy the analytics endpoint and confirm the five-event schema (SUG-003/SUG-004).</li>
    <li>Add the Search Console token, submit the sitemap (SUG-008).</li>
    <li>Approve a cadence; publish the next two guides from measured queries (SUG-002).</li>
  </ol>
</div>
"""
    return {
        "path": "workshop/executive-summary.html",
        "title": "Executive summary",
        "description": "The Affil3 project executive summary: what shipped, what is verified, what is flagged, decisions needed, and next actions.",
        "section": "workshop",
        "breadcrumb": crumb("Executive summary"),
        "jsonld": [],
        "body": body,
        "sitemap": {"priority": "0.5", "changefreq": "monthly"},
    }


def register_page(ctx):
    ps = ctx.d["products"]["products"]
    sources = ctx.d["sources"]["sources"]
    rows = []
    for p in ps:
        obs = p["observed"]
        obs_cell = (
            f'<strong>{esc(obs["asin"])}</strong><br><span class="fine">{esc(obs["final_url"])}</span>'
            if obs["status"] == "resolved"
            else f'<span class="unverified">— unverified</span><br><span class="fine">{esc(obs["note"])}</span>'
        )
        rows.append(
            f'<tr id="{esc(p["id"])}"><td><strong>{esc(p["id"])}</strong><br>'
            f'<span class="fine">{esc(p["display_name"] or "—")}</span></td>'
            f'<td><span class="fine">{esc(p["submitted_link"])}</span><br>token <code>{esc(p["submitted_token"])}</code></td>'
            f'<td><strong>{esc(p["intended"]["asin"])}</strong><br>'
            f'<span class="fine">{esc(p["intended"]["listing_url"])}</span><br>'
            f'<span class="fine">confirmed {esc(p["intended"]["confirmation_date"])} · '
            f'{esc(p["intended"]["source"])}</span> {ctx.src(p["intended"]["source_ref"])}</td>'
            f"<td>{obs_cell}<br><span class=\"fine\">{esc(obs['method'])} · {esc(obs['date'])}</span></td>"
            f'<td><span class="fine">{esc(p["token_format_check"]["result"])}</span></td>'
            f'<td class="src-cell">{ctx.srcs(p["sources"])}</td></tr>'
        )
    src_rows = "".join(
        f'<tr><td><strong>{esc(s["id"])}</strong></td><td>{esc(s["org"])}</td>'
        f'<td>{esc(s["title"])}</td><td>{ctx.external(s["url"], s["url"])}</td>'
        f'<td><span class="fine">{esc(s["supports"])}</span></td>'
        f'<td>{esc(s["accessed"])}</td></tr>'
        for s in sources
    )
    body = f"""
<div class="wrap article-header">
  <p class="eyebrow">The Workshop · Product register</p>
  <h1>Product-intent confirmation register</h1>
  <p class="lede">{esc(ctx.d['products']['record_separation_note'])}</p>
</div>
<section class="section"><div class="wrap">
  <h2>Register</h2>
  <div class="table-scroll"><table class="data">
    <thead><tr>
      <th>Item</th><th>Submitted link &amp; token</th><th>Intended identifier, URL, date, source</th>
      <th>Observed redirect target (separate field)</th><th>Token format check</th><th>Sources</th>
    </tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table></div>

  <h2 style="margin-top:2.2em">Observation method</h2>
  <ol>
    <li>Each submitted link was fetched individually on 2026-11-20, following redirects.</li>
    <li>The final destination, its ASIN (read from the <code>/dp/</code> URL), the page title, and the
    category breadcrumb were recorded verbatim as observations.</li>
    <li>Two fetch attempts were made for <code>B0c8moW59</code>; both returned Amazon’s
    “Continue shopping” checkpoint interstitial, so no destination was recorded for P-04
    {ctx.flag('FLG-004')}.</li>
    <li>Prices and ratings seen in page carousels referred to <em>other</em> items and were not
    attributable to the resolved products; nothing was recorded {ctx.flag('FLG-010')}.</li>
    <li>The token-format check compares each submitted token against Amazon’s published ASIN
    definition (10-character codes, typically “B0” + 8) {ctx.src('S-03')}. A mismatch is recorded as a
    checkable fact; validity is <em>not</em> claimed either way {ctx.flag('FLG-003')}.</li>
  </ol>

  <h2 style="margin-top:2.2em">Source register</h2>
  <div class="table-scroll"><table class="data">
    <thead><tr><th>ID</th><th>Type</th><th>Organization</th><th>Link for manual review</th><th>What it supports</th><th>Accessed</th></tr></thead>
    <tbody>{src_rows}</tbody>
  </table></div>
  <p class="fine">Every externally checkable claim on this site cites one of these IDs. Internal
  records (S-14) are marked as such.</p>
</div></section>
"""
    return {
        "path": "workshop/register.html",
        "title": "Product register & verification",
        "description": "The product-intent confirmation register: intended identifiers and official listing URLs, observed redirect targets in separate fields, token format checks, and the full source register.",
        "section": "workshop",
        "breadcrumb": crumb("Product register"),
        "jsonld": [],
        "body": body,
        "sitemap": {"priority": "0.5", "changefreq": "monthly"},
    }


def flagged_page(ctx):
    rows = []
    for f in ctx.d["flags"]["flags"]:
        status_cls = "status-review" if f["status"] == "needs review" else "status-info"
        affects = ", ".join(f["affects"])
        rows.append(
            f'<tr id="{esc(f["id"])}"><td><strong>{esc(f["id"])}</strong></td>'
            f'<td><strong>{esc(f["title"])}</strong><br><span class="fine">{esc(f["detail"])}</span></td>'
            f"<td>{esc(affects)}</td>"
            f'<td><span class="status-pill {status_cls}">{esc(f["status"])}</span></td>'
            f'<td><span class="fine">{esc(f["action"])}</span></td>'
            f'<td class="src-cell">{ctx.srcs(f["sources"])}</td></tr>'
        )
    body = f"""
<div class="wrap article-header">
  <p class="eyebrow">The Workshop · Flagged for Review</p>
  <h1>Flagged for Review</h1>
  <p class="lede">Irregularities, unverified values, and gated work — published openly so nothing
  blocks the site and nothing hides from you. A status of “needs review” means this item is listed
  here and does not block anything.</p>
</div>
<section class="section"><div class="wrap">
  <div class="table-scroll"><table class="data">
    <thead><tr><th>ID</th><th>Flag &amp; detail</th><th>Affects</th><th>Status</th><th>Action to close</th><th>Sources</th></tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table></div>
  <div class="callout flag" style="margin-top:2em">
    <h3>Rules of this register</h3>
    <ul>
      <li>Nothing is marked verified without an official source link.</li>
      <li>Unconfirmed values appear as blanks with the flag — never inferred, never filled in.</li>
      <li>The supplied short links are never called invalid; their compliance status is unresolved
      (FLG-003) until tested in the enrolled Associates workflow.</li>
    </ul>
  </div>
</div></section>
"""
    return {
        "path": "workshop/flagged.html",
        "title": "Flagged for Review",
        "description": "Every irregularity and unverified value in the project, with sources, affected items, and the action needed to close it.",
        "section": "workshop",
        "breadcrumb": crumb("Flagged for Review"),
        "jsonld": [],
        "body": body,
        "sitemap": {"priority": "0.5", "changefreq": "monthly"},
    }


def suggestions_page(ctx):
    cards = []
    for s in ctx.d["suggestions"]["suggestions"]:
        opt_rows = "".join(
            f'<tr><td><strong>{esc(o["id"].upper())}</strong></td><td><strong>{esc(o["label"])}</strong></td>'
            f'<td>{esc(o["pros"])}</td><td>{esc(o["cons"])}</td></tr>'
            for o in s["options"]
        )
        provisional = (
            ctx.chip("shipped provisionally", "chip-flag") if s.get("shipped_provisionally") else ""
        )
        deps = ", ".join(s["depends_on"]) or "none"
        cards.append(f"""<div class="sug-card" id="{esc(s['id'])}">
  <div class="sug-head">
    <span class="sug-id">{esc(s['id'])}</span>
    <h3 style="margin:0">{esc(s['title'])}</h3>
    <span class="status-pill status-awaiting">{esc(s['status'])}</span>
    {provisional}
  </div>
  <p>{esc(s['context'])}</p>
  <table class="option-table">
    <thead><tr><th></th><th>Option</th><th>Pros</th><th>Cons</th></tr></thead>
    <tbody>{opt_rows}</tbody>
  </table>
  <p><strong>Our recommendation:</strong> {esc(s['recommendation'])}</p>
  <p class="fine">Effort: {esc(s['effort'])} · Risk: {esc(s['risk'])} · Depends on: {esc(deps)} ·
  Feeds into: {esc(s['feeds_into'])}</p>
</div>""")
    body = f"""
<div class="wrap article-header">
  <p class="eyebrow">The Workshop · Suggestions &amp; decisions</p>
  <h1>Suggestions &amp; decisions</h1>
  <p class="lede">Every proposed change, with its options, trade-offs, and our recommendation —
  waiting for you to choose a path before anything irreversible happens. Where the brief forced a
  provisional call to get the site live, the card says so.</p>
</div>
<section class="section"><div class="wrap">
  {''.join(cards)}
  <div class="callout">
    <h3>How to use this queue</h3>
    <ol>
      <li>Pick an option (or propose a new one) per card — reply with the ID and option letter.</li>
      <li>We implement it and record the outcome in
      <a href="https://github.com/karagemop466-tech/Affil3/blob/main/COORDINATION.md" rel="noopener" target="_blank">COORDINATION.md</a>
      in the repository and in the PR description.</li>
      <li>Cards marked <em>shipped provisionally</em> can be revised with no rework cost — they are
      template constants.</li>
    </ol>
  </div>
</div></section>
"""
    return {
        "path": "workshop/suggestions.html",
        "title": "Suggestions & decisions",
        "description": "The decision queue: proposed changes with options, pros and cons, recommendations, and status — reviewable before anything is implemented.",
        "section": "workshop",
        "breadcrumb": crumb("Suggestions & decisions"),
        "jsonld": [],
        "body": body,
        "sitemap": {"priority": "0.5", "changefreq": "monthly"},
    }


def questions_page(ctx):
    items = []
    for q in ctx.d["questions"]["questions"]:
        status_cls = "status-awaiting" if q["status"] == "open" else "status-info"
        flags = " ".join(ctx.flag(f) for f in q["flags"])
        items.append(f"""<div class="sug-card" id="{esc(q['id'])}">
  <div class="sug-head">
    <span class="sug-id">{esc(q['id'])}</span>
    <h3 style="margin:0">{esc(q['question'])}</h3>
    <span class="status-pill {status_cls}">{esc(q['status'])}</span>
    {flags}
  </div>
  <dl class="qa">
    <dt>What we already know</dt><dd>{esc(q['known'])}</dd>
    <dt>What is missing</dt><dd>{esc(q['missing'])}</dd>
    <dt>How to discover it</dt><dd>{esc(q['discover'])}</dd>
    <dt>What it blocks</dt><dd>{esc(q['blocks'])}</dd>
  </dl>
</div>""")
    body = f"""
<div class="wrap article-header">
  <p class="eyebrow">The Workshop · Open questions</p>
  <h1>What we don’t know yet — and how to find out</h1>
  <p class="lede">The honest list. Each entry separates what we already know from what is missing,
  names the way to discover it, and says which decision waits on it. Nothing on this list is guessed.</p>
</div>
<section class="section"><div class="wrap">
  {''.join(items)}
</div></section>
"""
    return {
        "path": "workshop/questions.html",
        "title": "Open questions",
        "description": "Questions that must be answered before key decisions can be made: what we know, what is missing, how to discover it, and what it blocks.",
        "section": "workshop",
        "breadcrumb": crumb("Open questions"),
        "jsonld": [],
        "body": body,
        "sitemap": {"priority": "0.5", "changefreq": "monthly"},
    }


def ledger_page(ctx):
    ledger = ctx.d["ledger"]
    schema_rows = "".join(
        f'<tr><td><code>{esc(f["field"])}</code></td><td>{esc(f["type"])}</td>'
        f'<td>{esc(f["definition"])}</td><td>{"yes" if f["required"] else "no"}</td></tr>'
        for f in ledger["schema"]
    )
    events = ", ".join(ctx.site["proposed_events"])
    body = f"""
<div class="wrap article-header">
  <p class="eyebrow">The Workshop · Campaign ledger &amp; analytics</p>
  <h1>Measurement, gated honestly</h1>
  <p class="lede">{esc(ledger['policy'])}</p>
</div>
<section class="section"><div class="wrap">
  <h2>Campaign ledger schema</h2>
  <div class="table-scroll"><table class="data">
    <thead><tr><th>Field</th><th>Type</th><th>Definition</th><th>Required</th></tr></thead>
    <tbody>{schema_rows}</tbody>
  </table></div>
  <div class="callout">
    <h3>Current entries: none</h3>
    <p>{esc(ledger['note'])}</p>
    <p class="fine">Status: <span class="status-pill status-info">empty by policy</span></p>
  </div>

  <h2 style="margin-top:2em">Event schema (proposed)</h2>
  <p>The brief requires recording “the five defined events” but does not enumerate them
  {ctx.flag('FLG-009')}. Proposed five, implemented in <code>assets/js/analytics.js</code> and
  awaiting your confirmation {ctx.flag('FLG-006')}:</p>
  <p><code>{esc(events)}</code></p>
  <p class="fine">{esc(ctx.site['events_note'])}</p>

  <h2 style="margin-top:2em">The gate: self-hosted endpoint</h2>
  <ol>
    <li>Deploy <code>tools/analytics-endpoint/</code> (Cloudflare Worker reference, or the Python
    stdlib server) on the host chosen in <a href="{esc(ctx.rel('workshop/suggestions.html'))}#SUG-004">SUG-004</a>.</li>
    <li>Set <code>analyticsEndpoint</code> in <code>docs/site-config.js</code> — that single line
    releases the counter.</li>
    <li>The endpoint stores only <code>{{event, path, ts, ref}}</code> — no cookies, no IP, no
    user agent, no cross-site identifiers.</li>
    <li>Rows appear in the ledger only from authorized first-party reports, each with a dated
    provenance entry. Until then: no sessions, no clicks, no orders, no forecasts.</li>
  </ol>

  <h2 style="margin-top:2em">Compliance gate in the publishing workflow (Priority 5)</h2>
  <ul>
    <li>Disclosure placement and endorsement context reviewed against the Operating Agreement
    {ctx.src('S-01')} and FTC guidance {ctx.src('S-04')} {ctx.src('S-05')} on every publish.</li>
    <li>No product goes live without register entry + source links; no optimization runs before
    measurement exists (Priority 4).</li>
  </ul>
</div></section>
"""
    return {
        "path": "workshop/ledger.html",
        "title": "Campaign ledger & analytics",
        "description": "The empty-but-defined campaign ledger, the proposed five-event analytics schema, the self-hosted endpoint gate, and the compliance checks in the publishing workflow.",
        "section": "workshop",
        "breadcrumb": crumb("Campaign ledger & analytics"),
        "jsonld": [],
        "body": body,
        "sitemap": {"priority": "0.5", "changefreq": "monthly"},
    }
