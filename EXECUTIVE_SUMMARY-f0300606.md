# Executive summary — ShopNow Kitchen (Affil3), publication polish pass

Session `arena/f0300606-affil3` · 2026-11-20 · Branch `arena/f0300606-affil3` → `main`

## What this is

An Amazon Associates affiliate publication (**ShopNow Kitchen**) covering five kitchen
appliances submitted by the owner: two basket air fryers, one oven-style air fryer, one
instant-read thermometer, and one wireless leave-in thermometer. The site is a GitHub Pages
publication at <https://karagemop466-tech.github.io/Affil3/>, generated from a single data
register (`data/*.json`) by one generator (`tools/build.mjs`), gated by `tools/verify.mjs`
and re-checked by CI on every push.

This session's brief was *"make it read like a shop, not an audit"*: lead with the products,
keep the dashboards reachable from the footer and one navigation group, ship the suggestions
and questions decision surfaces, publish question-shaped guides, and keep disclosure,
sponsored links, measurement and the compliance gate exactly as verified.

## The five products (submitted link → observed listing)

| # | Submitted link | Observed Amazon listing | Product | Category | Buy button |
|---|----------------|-------------------------|---------|----------|------------|
| P01 | `link.amazon/B04G1MEwY` | `amazon.com/dp/B0CDY277D3` | CHEFMAN 6 Qt Dual Basket Air Fryer | Air fryers | yes (tagged, provisional) |
| P02 | `link.amazon/B02NbDxp3` | `amazon.com/dp/B09B7SB46R` | Emeril Lagasse 26 QT French Door Air Fryer Toaster Oven | Countertop ovens | yes (tagged, provisional) |
| P03 | `link.amazon/B00hJ57DV` | `amazon.com/dp/B08DKYBTPH` | Chefman TurboFry 8 Qt air fryer | Air fryers | yes (tagged, provisional) |
| P04 | `link.amazon/B0c8moW59` | `amazon.com/dp/B0DHZTCNR5` | ThermoMaven instant-read thermometer | Thermometers | yes (tagged; specs labelled family-page figures, FLG-025/Q-14) |
| P05 | `link.amazon/B0f3GKalj` | `amazon.com/dp/B0DZFD6R9Z` | CHEF iQ Sense wireless thermometer | Thermometers | yes (tagged, provisional) |

Per the brief's product-intent rule, **intended** fields (intended ASIN, official listing URL,
confirmation date, confirmation source) remain **blank for all five** — nothing was confirmed
from an official in-account source. Observed redirect targets are stored in separate `observed_*`
fields and are never merged into the intended fields. The nine-character submitted tokens are
recorded verbatim; their compliance status is **unresolved, not invalid** (FLG-003).

## What this session changed

1. **Front page rebuilt as a shop front.** Products lead; buyer language throughout; "shop by
   the job" need tiles; a seasonal deal-week module (Thanksgiving 2026-11-26, Black Friday
   2026-11-27); a compact trust strip; a reader-capture band; audit copy moved to the desk.
2. **`/shop/` is now a buyer-actionable page** — a side-by-side comparison table first (shape,
   capacity, temperatures, power, best-for, trade-off, where to check it, sources), with the
   full findings register (intended vs observed, flags, sources) kept below it, clearly labelled.
3. **Three new question-shaped guides** (16 total after the merge with the parallel sessions'
   own eight, all in the sitemap and RSS feed):
   *Black Friday kitchen deals: a checklist before you click add to cart*,
   *Dual-basket, single-basket, or oven-style? Match the shape to your week*, and
   *Smart meat thermometers: what actually matters before you buy*. Working titles only —
   no popularity, search-volume or superiority claims. Every factual claim carries its source.
4. **SG-27..SG-30 publication layer.** Nav labels are reader-facing with one quiet
   "The desk" group for dashboards (SG-27); the RSS feed is promoted in a follow band (SG-28);
   the Search Console verification meta is emitted only when the owner sets a token (SG-29,
   currently empty, FLG-013); reader email capture is gated behind S-06 and ships only after
   the privacy notice is updated (SG-30, currently RSS-only).
5. **One site for search engines.** `robots.txt` now excludes `/counter/` and `/counterwise/`
   alongside `/editorial/`, `/legacy/` and `/crisp-index/`. The sub-editions stay readable;
   S-11 lets the owner reverse this.
6. **Decision surfaces.** Suggestions S-11…S-14 added (sub-edition indexing, December content
   direction, target reader, measurement-vs-content order); Q-14 (email capture endpoint and
   consent wording) and discovery steps D-09/D-10 added. Nothing on the decision board is
   implemented until the owner names an option.
7. **Data correction (found pre-merge, superseded at merge).** P04's "no buy button" reason
   contradicted its own row ("no submitted link resolved to this listing" while the row records
   B0c8moW59 → B0DHZTCNR5). Before the fix could ship, the merge brought in `origin/main`'s
   deeper rebuild: a ThermoMaven manufacturer family page (S21) had been found and P04 rebuilt
   with sourced figures and a buy button, so the stale text no longer exists. The finding is
   recorded in `COORDINATION.md`; the merged register keeps `main`'s rebuild wholesale. Only the
   FLG-007 guide-count/cross-ref edit was re-applied on top.

## What is verified (official sources only)

* Associates Operating Agreement and Program Policies: the required disclosure statement
  (§5), Special Links must carry the tag as a URL parameter, no cloaking/shorteners,
  price/availability only from Amazon-served data (S01–S03).
* Google's `rel="sponsored"` guidance (S06); FTC disclosure guidance and 16 CFR Part 255
  (S07, S08); USDA FSIS safe temperatures and probe placement (S10, S20).
* Manufacturer specification pages for P01, P02, P03, P05 (Chefman ×2, Emeril Everyday,
  CHEF iQ) populate the spec grids; conflicts between official pages are published, not
  smoothed (FLG-023, FLG-024, FLG-026, FLG-027).
* Observed listing pages for all five rows (S04), dated 2026-11-20, corroborated by multiple
  independent fetch passes including the PR #10 transposition fix.

## What is not verified (and stays blank)

* Intended ASIN / official listing URL / confirmation date / confirmation source for all five.
* Gate G-02: no Special Link has been tested in the enrolled Associates workflow; buy links
  are tagged `?tag=shopnow047c-20` and labelled provisional (FLG-005).
* Whether the tracking ID belongs to the signed-in account (FLG-011); account status and
  declared site (FLG-006).
* Analytics endpoint: shipped but idle on GitHub Pages (FLG-009, S-03); Search Console not
  connected (FLG-013). No prices, ratings or availability are shown anywhere, by policy.
* P04 model identity: the listing names no model; its figures are the manufacturer's F1 Ace
   family-page figures, labelled as such and not adopted as confirmed specifications of the
   listed unit (FLG-025, Q-14).

## Compliance posture (gates before scaling)

* G-01 disclosure strip above the fold on every page + footer repeat — automated, passing.
* G-03/G-04/G-05 every Amazon link `rel="sponsored"` + tagged + no redirects — automated, passing.
* G-06 no prices/ratings/availability — automated, passing (negative-tested this session).
* G-02 one Special Link per product tested in Associates Central — **owner action required
  before scaling** (FLG-005). Do not scale traffic before this is done.
* The publishing gate (`tools/verify.mjs`) is enforced in CI on every push; a failing check
  blocks publication. This session pre-merge: 33 pages, 3,776 checks; **merged tree: 43 pages, 5,248 checks, 0 failed**.

## Evidence-based iteration (Priority 4)

The campaign ledger is empty and well-defined: rows are added only from authorized first-party
reports (Associates exports), with date range and provenance. No conversion score or revenue
forecast is presented anywhere. Measurement ships privacy-preserving: five allowlisted events
(`page_view`, `category_view`, `product_view`, `outbound_click`, `guide_read_75`), no cookies,
no IP, DNT respected, and clicks are never routed through a redirect (Program Policies
anti-cloaking). Collection activates when the owner deploys `tools/collector.mjs` and sets
`analyticsEndpoint` (S-03, S-14).

## Decisions waiting on the owner (nothing here is implemented)

Reply with the ID and option letter, e.g. `S-14 A`:

* **S-21** December content: holiday hosting (current A) / gift guides / deal follow-ups.
* **S-22** target reader: weeknight small households (current A) / hosts / gadget-first.
* **S-23** order of operations: **A — deploy measurement before the next guide batch** (rec.)
  or B — publish first (current).
* From the parallel sessions (kept unchanged): **S-11** four editions on one domain,
  **S-12** the ThermoMaven buy button, **S-13** a side-by-side comparison page (served twice
  over now: their `/compare/` spec sheet and this session's `/shop/` buyer table),
  **S-14** derive every count from its rows, and S-01..S-10 plus S-15..S-20. (My draft S-11
  duplicated their S-11 and was dropped at merge; my drafts S-12..S-14 were renumbered
  S-21..S-23.)

Blocking questions (with how-to-close steps on `/questions/`): **Q-01** confirm intended
products from the enrolled link-generation record; **Q-02** run gate G-02 in Associates
Central; **Q-03** confirm the account and declared site. Q-04..Q-14 cover the analytics
endpoint, marketplace, named editor, cadence, pricing, ledger imports, sub-editions, privacy
review, Search Console ownership, target reader, and reader-capture consent.

## Flagged for review (published at `/flagged/`, none block publication)

Open highlights: FLG-001/002 (token format and observed-vs-intended separation), FLG-003
(short-link compliance unresolved — **not claimed invalid**), FLG-005 (G-02 pending),
FLG-023/024/026/027 (official-source spec conflicts), FLG-025 (P04 withheld specs).
Resolved this session: **FLG-031** (P04 stale reason text). Previously resolved: FLG-004,
FLG-022, FLG-028, FLG-029.

## Links for manual review

* Live site: <https://karagemop466-tech.github.io/Affil3/>
* Buyer comparison: `/shop/` · Guides: `/guides/` · Decisions: `/suggestions/`, `/questions/`
* Registers: `/sources/`, `/flagged/`, `/shop/#full-findings-register` (intended vs observed)
* Compliance: `/compliance/`, `/workflow/`, `/privacy/`, `/measurement/`, `/ledger/`
* Comparison: `/compare/` (spec sheet) · Next-redesign brief: `/design-brief/` (+ `DESIGN-BRIEF.md`)
* Tooling: `tools/build.mjs` (generator), `tools/verify.mjs` (gate), `tools/collector.mjs`
  (self-hosted analytics endpoint, deployment pending)
