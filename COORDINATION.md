# Coordination — Affil3

Shared task board for the Affil3 Amazon affiliate site.

> **Board status (2026-11-20):** multiple sessions have pushed independent copies of this file.
> Rows 1–13 below are owned by `arena-83a43a96-affil3` (merged as PR #1). A second site build is
> open as PR #2 from `arena/114f47c4-affil3` and touches `index.html`, `editorial.html`,
> `methodology.html`, `assets/*`, `analytics/*`, `scripts/*`, `data/campaign-ledger.csv`,
> `data/product-intent.csv`, `sitemap.xml`, `feed.xml`. `arena/bdcb1fa8-affil3` has claimed
> repo-wide "integration" scope on its own copy of this board. Treat the merged rows on `main` as
> authoritative; claim new rows below before editing.

## Session (active) — 43565031
- Session ID: `arena-43565031-affil3`
- Branch: `arena/43565031-affil3` (branched from `main` @ `db77ec4`, the PR #1 merge commit)
- Claimed scope — **new files only, plus surgical one-line additions to shared nav/sitemap**:
  - `verification.html`, `shop.html`, `suggestions.html`, `questions.html` (new pages)
  - `data/link-verification.json`, `data/suggestions.json`, `data/open-questions.json`,
    `data/claims.json` (new registers)
  - `scripts/build_registers.py`, `scripts/validate_site.py` (new)
  - `.github/workflows/ci.yml` (new; distinct from PR #2's `pages.yml`)
  - `docs/OFFICIAL-SOURCES.md` (new)
  - `EXECUTIVE_SUMMARY.md` — **updating**: PR #2's file list does not include it, and PR #1 is
    already merged, so no in-flight owner. Full rewrite with the verified findings.
  - `index.html` — **contested with PR #2.** I am editing only the `<main>` hero + product grid
    and appending two nav/footer links. If PR #2 merges, resolve by keeping PR #2's homepage
    structure and porting the verified product evidence + the four new page links into it.
  - `sitemap.xml` — **contested with PR #2.** Adding only 4 new `<url>` entries.
- **Not touching:** `assets/css/main.css` (appending a scoped block at the end only),
  `assets/js/app.js`, `guides/*` content, `products.html`, `disclosure.html`, `privacy.html`,
  `about.html`, `flagged.html`, `feed.xml`, anything under `analytics/`.
- Requests to other scopes (logged here, not edited): PR #2 owner — please merge `shop.html`,
  `suggestions.html`, `questions.html`, `verification.html` into your nav and `feed.xml`;
  `arena/bdcb1fa8` — `data/product-intent.csv` in your scope should be superseded by
  `data/link-verification.json` (it has dated, source-linked evidence; the CSV has blanks).

### Handoff log — 43565031
- 2026-11-20: `main` @ `db77ec4` deployed to Pages and building clean (`status: built`).
- 2026-11-20: **Rows 1, 2 and 11 of the board below are now superseded by evidence.** This
  session successfully dereferenced the `link.amazon` short links (fetch worked; the sandbox
  note "no outbound access to amazon.com" was not correct for the retrieval tools available here).
  Four of five resolve to live product pages carrying `plpRedirect=mhFallback`; one hits an Amazon
  checkpoint page. See `docs/OFFICIAL-SOURCES.md` and `data/link-verification.json`. Do not repeat
  the "cannot be resolved" claim in any copy — it is now falsified.

## Session (prior) — 83a43a96
- Session ID: `arena-83a43a96-affil3`
- Branch: `arena/83a43a96-affil3` (branched from `main` @ `847ae37`)
- Owner: this session claims every task below (single-session coordination; no overlapping scopes)

## Task board

| # | Task | Status | Owner | Files touched | Sources verified | Notes |
|---|------|--------|-------|---------------|------------------|-------|
| 1 | Repo review: read every file, flag irregularities | done | arena-83a43a96-affil3 | COORDINATION.md, README.md | none (repo had only README) | Repo contained only `README.md` ("# Affil3"). No source data, no existing links to verify. |
| 2 | Product-intent confirmation record (5 submitted Amazon links) | done | arena-83a43a96-affil3 | products.html, flagged.html, EXECUTIVE_SUMMARY.md | Amazon Associates Program policies (docs), link.amazon short links NOT resolvable in this sandbox (no outbound access to amazon.com) | All ASIN / listing-URL / date / source / redirect-target fields left blank and flagged UNVERIFIED. Never inferred. Short-link compliance status unresolved (see FLG-003 note); links are NOT claimed invalid. |
| 3 | Site design system (CSS) + assets | done | arena-83a43a96-affil3 | assets/css/main.css | none | Self-authored CSS; no external frameworks or fonts (zero external dependencies). |
| 4 | Landing page — publication front page, products lead, disclosure above fold | done | arena-83a43a96-affil3 | index.html | none | Editorial hypotheses used as working titles only; no popularity/search-volume claims. |
| 5 | Category subpages + entries table with sources + findings/analysis | done | arena-83a43a96-affil3 | products.html | Amazon Associates Program Operating Agreement; FTC disclosure guidance (ftc.gov) | Every table row carries a source link or is left blank + flagged unverified. |
| 6 | Question-shaped buyer guides (4 working titles) | done | arena-83a43a96-affil3 | guides/*.html | none | Working titles only; presented as hypotheses, not performance claims. Added to sitemap.xml and feed.xml. |
| 7 | Disclosure strip (above fold, every page) + footer repeat + `rel="sponsored"` on outbound links | done | arena-83a43a96-affil3 | all HTML pages | FTC "clear and conspicuous" guidance; Amazon Associates disclosure requirement | Disclosure strip under masthead on every page; repeated in footer. |
| 8 | Sitemap + RSS feed | done | arena-83a43a96-affil3 | sitemap.xml, feed.xml | none | Feed includes the 4 guides; sitemap lists all pages. |
| 9 | Click & conversion measurement instrumentation (5 events) | done | arena-83a43a96-affil3 | assets/js/app.js | none | Privacy-preserving client-side outbound click counter; beacon POST to `/analytics/collect`. Endpoint is NOT self-hosted on GitHub Pages (static hosting) — flagged, requires separate self-hosted receiver before it is operational. |
| 10 | Search Console / real analytics documentation | done | arena-83a43a96-affil3 | about.html, flagged.html | none | Cannot enable Search Console without a Google account; setup steps documented, flagged as not yet enabled. |
| 11 | Link check + build verification (no broken links) | done | arena-83a43a96-affil3 | all HTML | none | Internal links checked by script; outbound Amazon short links cannot be dereferenced in this sandbox. |
| 12 | GitHub Pages enable + deploy verification | in progress | arena-83a43a96-affil3 | repo settings via GitHub API | none | Pages source: `main` branch, `/ (root)`. To be enabled after merge to main. |
| 13 | Pull request + merge to main; record PR link and merge result | in progress | arena-83a43a96-affil3 | COORDINATION.md | none | PR from `arena/83a43a96-affil3` to `main`. Flagged/unverified items published on `flagged.html` and do not block merge. |

## Ground rules followed
- Work only on the current branch (`arena/83a43a96-affil3`); push only to this branch; PR opened from this branch to `main`.
- Small, frequent commits; `git pull --rebase` before every push.
- No values inferred or filled in. Anything not confirmed against an official source is left blank and flagged "unverified" with a source link where one exists.
- Outbound Amazon links kept as submitted; `rel="sponsored"` added; no claim made that short links are invalid (compliance status unresolved, see FLG-003).

## Task board — additions claimed by 43565031 (2026-11-20)

Status values: `unclaimed` · `in progress` · `done` · `needs review`.

| # | Task | Status | Owner | Files | Sources verified | Notes |
|---|------|--------|-------|-------|------------------|-------|
| 14 | Dereference all 5 submitted short links; record intended vs observed separately | done | arena-43565031-affil3 | `data/link-verification.json`, `verification.html` | Live fetch of each submitted URL, 2026-11-20 (see `docs/OFFICIAL-SOURCES.md` V1–V6) | 4/5 land on live product pages, all carrying `plpRedirect=mhFallback`; 1/5 lands on an Amazon checkpoint page. Observed ASIN ≠ submitted token in every resolved case. |
| 15 | Compliance rule extraction with verbatim quotes + retrieval dates | done | arena-43565031-affil3 | `data/claims.json`, `docs/OFFICIAL-SOURCES.md` | affiliate-program.amazon.com Operating Agreement (updated 2025-10-15) + Program Policies (updated 2026-04-14); ftc.gov Endorsement Guides | Six rules materially change site design (price display, tag parameter, list-page original content, sub-tag prohibition, promotion expiry, originality). |
| 16 | Decision Room: ranked suggestion register for owner review | done | arena-43565031-affil3 | `suggestions.html`, `data/suggestions.json` | rows cite `data/claims.json` / `data/link-verification.json` | Suggestions are proposals for the owner to select; none is implemented beyond the site shell. |
| 17 | Open-questions register: know / don't know / how to find out / who answers | done | arena-43565031-affil3 | `questions.html`, `data/open-questions.json` | as above | Includes the questions that block a pricing, commission, or niche decision. |
| 18 | Storefront page (`shop.html`) that reads like a shop, policy-compliant | done | arena-43565031-affil3 | `shop.html` | Program Policies §2(b) price/list rules | No hardcoded prices or ratings: §2(b) permits price display only via links we serve or Creators/PA API data, which this project does not have. |
| 19 | Data-driven page build + compliance gate in CI | done | arena-43565031-affil3 | `scripts/build_registers.py`, `scripts/validate_site.py`, `.github/workflows/ci.yml` | — | Pages are generated from the JSON registers; the validator fails the build on an unsourced row, an unflagged blank, a missing disclosure strip, or a product link lacking `rel="sponsored"`. |
| 20 | Executive summary refresh with verified findings | done | arena-43565031-affil3 | `EXECUTIVE_SUMMARY.md` | as above | |
| 21 | Re-verify `3 qualifying sales in 180 days` and commission-rate claims | needs review | unowned | — | NOT confirmed in the policy text retrieved 2026-11-20 | Widely repeated by third-party blogs; absent from the retrieved Program Policies. Do not publish as fact until confirmed in Associates Central. |
