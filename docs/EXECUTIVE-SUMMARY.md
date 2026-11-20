# Executive summary — Crisp & Counter (Affil3)

**Date:** 2026-11-20 · **Session:** arena/0a90f62c-affil3 · **Tracking ID:** shopnow047c-20 (owner-supplied)

## What was built

A complete Amazon affiliate publication — **Crisp & Counter** — that reads like
a shop, verifies like a lab notebook, and ships with its own governance:

1. **A publication front page** organized around products and question-shaped
   buyer guides (7 published), with a comparison desk, seasonal (Black Friday
   week) edition framing, and a single footer nav group ("Research desk")
   holding every dashboard surface.
2. **A verified product register** built from the five submitted links. All
   five were fetched against Amazon first-hand. Four resolved to official
   listings; one hit an Amazon checkpoint interstitial and is published as
   unresolved with nothing inferred.
3. **A line-by-line verification register** where every published claim —
   title, category, rating, price — carries its official source link and
   observation date. Unconfirmed values are blank and flagged.
4. **A product-intent confirmation record** with intended ASIN / listing URL /
   confirmation date / source kept strictly separate from observed redirect
   targets, per the brief's record design.
5. **Measurement, defined before more content:** a privacy-preserving
   outbound-click counter (no cookies, no IP, no third parties), five defined
   events (page_view, product_impression, outbound_click, guide_read,
   feedback_submit — the brief references "five defined events" without
   enumerating them; flagged as Q-05), and a ready-to-deploy self-hosted
   collector (`server/collect.js`).
6. **Compliance machinery:** disclosure strip under the masthead of every page,
   Amazon Associate statement in every footer, `rel="sponsored"` on every
   product link, and a publishing gate page (G1–G8) mapping to FTC and Amazon
   Associates sources. Automated checks enforce all of it on every build.
7. **Governance surfaces:** Flagged for Review (FLG-001…010), open questions
   (Q-01…10), a suggestion board with options/recommendations to review before
   implementing anything (SG-01…12), an empty-but-defined campaign ledger with
   intake rule and provenance trail, and COORDINATION.md for parallel sessions.

## What was verified (and how)

- **Products, first-hand:** each submitted short link was fetched; the resolved
  Amazon listing was read directly (not via third-party summaries):

  | Submitted | Observed target | Product (official title, abridged) | Observed |
  | --- | --- | --- | --- |
  | link.amazon/B04G1MEwY | amazon.com/dp/B0CDY277D3 | Chefman 6 Qt Dual Basket Air Fryer Oven | 2026-11-20 |
  | link.amazon/B02NbDxp3 | amazon.com/dp/B09B7SB46R | Emeril Lagasse 26QT French Door Air Fryer Toaster Oven | 2026-11-20 |
  | link.amazon/B00hJ57DV | amazon.com/dp/B08DKYBTPH | Chefman 8 Qt TurboFry Air Fryer | 2026-11-20 |
  | link.amazon/B0c8moW59 | — unresolved (checkpoint ×2) | — | 2026-11-20 |
  | link.amazon/B0f3GKalj | amazon.com/dp/B0DZFD6R9Z | CHEF iQ Sense Smart Wireless Meat Thermometer Gen3 | 2026-11-20 |

- **Policy sources:** FTC Endorsement Guides & Disclosures 101 (S01, S05),
  Amazon Associates Operating Agreement & Program Policies (S02, S03),
  Amazon's ASIN definition — "a unique combination of 10 letters and numbers"
  (S04), Google's rel="sponsored" guidance (S06), GitHub Pages docs (S07).
- **Automated gates:** disclosure presence, associate statement, sponsored
  marking, per-row official-source coverage, internal link integrity, and
  build-drift — all enforced by `tools/verify_site.py` and CI.

## Decisions the owner still needs to make (no fabrication possible)

1. **Confirm intended ASINs** for the five links (FLG-001, Q-01).
2. **Resolve P4** (`link.amazon/B0c8moW59`) in a normal browser session (FLG-002, Q-02).
3. **Run gate G3:** test one Special Link per product in the enrolled
   Associates workflow and confirm the tracking report before scaling
   (FLG-004, Q-03) — the brief's S02 requirement.
4. **Deploy the analytics endpoint** (`server/collect.js`) to close the
   measurement loop (FLG-006, SG-02).
5. **Search Console verification token** (FLG-007, SG-06), and decide the
   mailing/reader-capture question (Q-08, SG-10).

## Notable irregularities (all published at /desk/flagged/)

- The supplied short-link tokens (e.g. `B04G1MEwY`) are 9 characters; Amazon
  defines ASINs as 10. Per the brief (FLG-003) this project makes **no claim**
  the supplied links are invalid — intent fields stay blank pending owner
  confirmation while observed targets are recorded separately.
- Deal-week prices (observed 2026-11-20) will age quickly; every figure is
  date-stamped and the listing is the stated source of truth.
- The brief's register IDs (S01/S02/S07/S24, SG-27..SG-30, FLG-003) map to
  this repo's registers provisionally (FLG-008).
- Commission rates are intentionally unpublished (account-specific, FLG-009).
  **No revenue forecast or conversion score is presented anywhere.**

## Bottom line

The site is live-ready as a compliant, findable, source-linked publication:
products first, questions always, receipts attached. The remaining work is
owner-gated by design — the parts that can't be automated honestly are the
parts waiting on a human, and every one of them is listed, linked and dated.
