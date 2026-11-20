# Affil3 — “ShopNow Kitchen Edit”

An Amazon Associates publication and shop: question-shaped buying guides, product-intent
records, and a compliance-gated publishing workflow for Tracking ID **shopnow047c-20**.

- **Live site:** https://karagemop466-tech.github.io/Affil3/
- **Task board:** [COORDINATION.md](COORDINATION.md) — read it before starting any work in this repo.
- **Flagged for review:** every unverified value and open compliance question is published on
  [`flagged/index.html`](flagged/index.html) with source links. Unverified items do not block merges.

## What lives here

| Path | Purpose |
|---|---|
| `index.html` | Publication front page — products and guides first; dashboard reachable from the footer |
| `guides/` | Question-shaped buying guides (4 published; clusters + seasonal calendar) |
| `products/` | Shop grid + product-intent confirmation records for the 5 submitted links |
| `summary/` | Executive summary |
| `suggestions/` | Suggestion review board — review and choose a path **before** implementation |
| `questions/` | Decision-readiness register — what we know, what we lack, how to find it |
| `flagged/` | Flagged for Review |
| `sourcing/` | Source register — every cited official source, verified by fetch |
| `analytics/` | The 5 defined events, campaign ledger schema, endpoint decision |
| `dashboard/` | Working hub: ledger viewer, Associates link-builder, event queue download |
| `compliance/` | Publishing compliance gate (disclosure placement, sponsored rel, API policy) |
| `search-console/` | Search Console readiness + verification steps |
| `data/` | Machine-readable registers: `products.json`, `flags.json`, `sources.json`, `questions.json`, `suggestions.json`, `events-schema.json`, `ledger/campaign-ledger.csv` |
| `tools/validate.py` + `.github/workflows/gates.yml` | Automated gates: JSON validity, disclosure on every page, `rel="sponsored"` on outbound product links, sitemap ↔ files consistency, ledger schema |

## Ground rules

1. **Verify, then write.** Every table row carries a source link to an official page. If a value
   cannot be confirmed from an official source, it is left blank and flagged UNVERIFIED — never inferred.
2. **Intent ≠ observation.** For each submitted link we store the intended ASIN, the official listing
   URL, the confirmation date, and the source — and keep observed redirect targets in a separate field.
   The two are never merged.
3. **Compliance status, not verdicts.** The supplied short links’ exact compliance status is
   **unresolved** (FLG-003). No session may claim they are invalid or valid without a check performed
   in the enrolled Associates workflow.
4. **Disclosure everywhere.** The Associates statement and reader-support disclosure sit above the
   fold on every page and repeat in the footer. Outbound product links carry `rel="sponsored nofollow noopener"`.
5. **Measure before optimizing.** The campaign ledger starts empty with a defined schema. No conversion
   score or revenue forecast is presented anywhere on the site.
