# Coordination — Affil3

Shared task board. The first checkout observed only `README.md`; another session subsequently completed and merged the initial publication build while this branch was active. This file preserves that work and records the follow-up integration below.

## Sessions

| Session | Branch | Status | Scope / handoff |
|---|---|---|---|
| `arena-83a43a96-affil3` | `arena/83a43a96-affil3` | merged | Initial publication build, product register, guides, disclosure, sitemap/feed, first-pass measurement notes. Merged to `main` in PR [#1](https://github.com/karagemop466-tech/Affil3/pull/1) on 2026-11-20. |
| `arena/35d0727e-affil3` | `arena/35d0727e-affil3` | active | Final integration: independently verify sources and supplied-link observations, add source-backed questions/suggestions/review surfaces, repair measurement/privacy claims, preserve the separate intended-vs-observed product fields, test, and deploy through a PR from this branch. |

## Task board

| # | Task | Status | Owner | Files touched / scope | Notes |
|---|---|---|---|---|---|
| 1 | Initial repository review | done | `arena-83a43a96-affil3` | `README.md`, `COORDINATION.md` | Initial checkout contained only `README.md` (`# Affil3`). |
| 2 | Product-intent confirmation record for five submitted links | needs review | `arena/35d0727e-affil3` | `products.html`, `flagged.html`, new product/source data | Keep intended ASIN, intended official listing URL, confirmation date, confirmation source, and observed redirect target separate. Intended fields remain blank until confirmed. Link status is unresolved; no claim that a submitted short link is invalid. |
| 3 | Publication design, categories, and home-page polish | in progress | `arena/35d0727e-affil3` | `index.html`, shared CSS, navigation/footer | Integration pass after PR #1: lead with useful buyer questions, keep dashboard links inside one Studio group and in the footer. |
| 4 | Question-led buyer guides and cadence | done / needs iteration | `arena-83a43a96-affil3` + `arena/35d0727e-affil3` | `guides/*.html`, `guides/index.html`, `feed.xml`, `sitemap.xml` | Four question-led guides exist. Current session will verify language, cross-links, publication dates, and discoverability; titles remain editorial hypotheses, not demand claims. |
| 5 | Disclosure placement and sponsored-link handling | in progress | `arena/35d0727e-affil3` | all HTML pages, CSS, site scripts | Ensure the exact Associates statement is visible under the masthead and repeated in the footer on every page; every outbound product link must include `rel="sponsored"`. |
| 6 | Source-backed executive brief, questions, suggestions, and flagged items | in progress | `arena/35d0727e-affil3` | `EXECUTIVE_SUMMARY.md`, `about.html`, `flagged.html`, new `studio/**` | Publish known facts, gaps, discovery steps, recommendation options, hosting/measurement constraints, and official source links. |
| 7 | RSS, sitemap, canonical origin, internal links, and Search Console notes | in progress | `arena/35d0727e-affil3` | `feed.xml`, `sitemap.xml`, `robots.txt`, all HTML pages, `scripts/**` | Canonical origin is the existing project Pages URL. Search Console ownership is not connected or verified. |
| 8 | Privacy-preserving analytics endpoint and event definitions | needs review | `arena/35d0727e-affil3` | `analytics/**`, `assets/js/app.js`, `site-config.js`, `privacy.html` | A dependency-free endpoint and tests are being added. GitHub Pages is static, so public collection stays disabled until a supported first-party server host is configured. Do not describe uncollected data as live analytics. |
| 9 | Campaign ledger and authorized report-import gate | in progress | `arena/35d0727e-affil3` | new `studio/campaign-ledger.html`, `data/**`, `analytics/**` | Start empty. Store only dated, authorized first-party report data with provenance; no inferred sessions, conversions, revenue, or forecasts. |
| 10 | Automated build, link/disclosure checks, PR and Pages deployment verification | in progress | `arena/35d0727e-affil3` | `scripts/**`, `.github/workflows/**`, `COORDINATION.md` | Do not merge a failing build. Preserve PR #1 work, verify the new integration on this branch, then create and merge a separate PR to `main`. |

## Verification and source log

- 2026-11-20 — Confirmed the repository is public, default branch `main`, and GitHub Pages is enabled at `https://karagemop466-tech.github.io/Affil3/`, publishing from `main` root. PR #1 is merged; no branch switch is being made.
- 2026-11-20 — Independently fetched the official Amazon ASIN explainer. It defines ASIN as a unique 10-character alphanumeric code and says a product page URL identifies the ASIN after `/dp/`. The five submitted path strings are each nine characters; they are stored as submitted identifiers, not marked as ASINs.
- 2026-11-20 — Fetched the five user-supplied `https://link.amazon/...` URLs. Four tool-observed responses landed on Amazon detail URLs with different 10-character `/dp/` identifiers; the fifth stopped at an Amazon “Continue shopping” checkpoint without exposing a product destination. These are observed outcomes only, not confirmations of intended products, Special Link compliance, or tracking attribution. See the separate product record and FLG-002/FLG-003.
- 2026-11-20 — Verified Amazon's Associates Operating Agreement and Program Policies, FTC affiliate/endorsement guidance, Google's people-first and sitemap guidance, Amazon's official Associates Order Report help, and GitHub Pages' static-hosting and usage-limits documentation. Source URLs and the verified implications are published in the site source register.
- 2026-11-20 — Rebase conflict: `origin/main` advanced with merged PR #1 and added this file while the current branch still carried its original claim. Resolved by retaining the existing session's board and adding the current branch's follow-up scope. No upstream site files were discarded.

## Irregularities / items requiring review

- The earlier PR #1 site stated that the short links could not be resolved. The current session did fetch them; the earlier claim is superseded by the dated observations above. This does **not** establish the intended product or link validity.
- GitHub Pages documentation says Pages is static and cannot run server-side code; it also says Pages is not intended or allowed as free hosting for online businesses/e-commerce sites or sites primarily directed at commercial transactions/SaaS. The affiliate-publication use case needs hosting-policy review. GitHub's Pages documentation also says it logs and stores visitor IP addresses for security; the site cannot disable that host-level processing.
- Amazon policy pages require a valid Associates ID in Special Links, impose conditions on product information/pricing/reviews, and restrict use of Program Content/API data for machine learning or analysis without required permissions. No product-data API, scraping, review aggregation, or autonomous Amazon interaction is enabled.
- The selected tracking ID `shopnow047c-20`, enrollment status, official product identities, live pricing, review data, commission rates, conversion totals, and Search Console property have not been verified in the relevant first-party accounts.
- Analytics code can be tested locally, but GitHub Pages cannot receive `/api/events`; production collection remains off until a compatible first-party host is selected and configured.

## Ground rules

- Work on the active Arena branch `arena/35d0727e-affil3`; do not switch, rename, or push another branch.
- Preserve completed work from PR #1. The new session owns only the final integration pass and the files scoped above; coordinate before any further overlap.
- Before every push, rebase against the current `origin/main`; push only `arena/35d0727e-affil3`.
- Leave unconfirmed values blank and label them unverified. Never treat an observed redirect target as the intended product.
