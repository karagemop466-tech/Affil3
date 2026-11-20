# Decision record (ADR-lite)

Newest last. One entry = one decision that constrains future work. `basis` cites `data/sources.json` ids.

**D-001 · Static site, built from data, published through Actions** — *2026-11-20*
Decision: a hand-written builder (`tools/build_site.py`) instead of a generator framework; `site/` is
committed output; CI rebuilds and fails on drift. Basis: zero dependencies, reviewable diffs, and a Pages
deploy path needing only the standard actions [S24]. Consequence: one file per page type, no template
language; a human editing `site/` directly is caught by the build.

**D-002 · Reader pages and audit surfaces are separate, joined by one nav group** — Decision: front page,
shelf and guides read like a shop; the seven registers live under "How we work" and in the footer. Basis:
the brief's publication pass. Consequence: `layout.product_tables_inline` exists in case that split is
rejected (FLG-010).

**D-003 · No price, rating, review or product-image content until an authorised source exists** — Decision:
those fields are `null` in the data and absent from the pages; the gate enforces it structurally (schema.org
nodes, currency on reader-facing pages). Basis: Participation Requirements 2(b)/6(t); IP License 2(h)–(k)
[S06] [S07] [S08] [S09]. Consequence: the tables look sparse; they are honestly sparse.

**D-004 · No scraper, no product-research warehouse, no model trained on Program Content** — Decision:
automation is confined to this repo's own data. Basis: IP License §1, §2(e); Participation Requirements §5
[S10] [S11] [S14]. Consequence: the "identify trending, high-converting products" ambition is deferred
pending API access, written approval, or our own test data. **This is the biggest scope cut in the
project** and the one a future session is most likely to try to undo.

**D-005 · Affiliate links stay behind a two-level gate** — Decision: per-product `link_state` plus
site-wide `allow_live_links`; both green before a clickable href exists. Basis: §2(a)–(b) formatting and
tag rules; Commission Income Statement 2(e)/(g) disqualifiers; the brief's one-link-test instruction
[S02] [S03] [S04]. Consequence: the site ships with zero clickable links and a five-minute path to
turning them on.

**D-006 · Intended and observed link data are separate fields, forever** — Decision: the register keeps
`intended_asin`/`candidate_listing_url` apart from `observed_redirect_target`, and `scan` fails if they are
merged without evidence. Basis: the brief's explicit instruction, plus the checkability of an ASIN [S26].

**D-007 · Cookies are not used at all, so the collector needs no consent UI** — Decision: stdlib collector;
no IP, user-agent or referrer; per-load random id. Basis: Participation Requirements 3(e) obliges us to
disclose cookie/pixel use [S19]; the least-bad design is to have none. Consequence: no cross-visit
analytics, and we accept that out loud.

**D-008 · Deal and price-alert content is rejected, not deferred** — Basis: the price tracking/alerting ban
[S13], and the duty to remove expired promotional mentions [S15], which a static page cannot honour by
itself. Consequence: seasonal pages carry `review_by`; CHK-09/CHK-10 enforce both halves.

**D-009 · Event names were defined here and are marked as proposed** — Basis: the "five defined events"
were not in the repo; inventing them silently would make the ledger unauditable. Consequence: SG-12 asks
for approval; a rename is one file plus a rebuild.

**D-010 · One site, one host, one path** — Basis: the brief's "give search engines one site to index"; the
redistribution rule; the thin-affiliate-network pattern [S14] [S27]. Consequence: no sister microsites —
niche growth means new clusters here, not a new repository.

**D-011 · Where a value cannot be confirmed, the site says so instead of smoothing it over** — Basis: the
misleading-claims prohibition [S16] and the project's own brief ("leave it blank and flag it").
Consequence: this is the visible difference between this site and a template, and it is the property most
likely to be quietly removed under traffic pressure. Guarded by CHK-03 and by the intake tool's refusals.
