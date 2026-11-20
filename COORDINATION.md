# Coordination — Affil3

Shared task board for the Affil3 Amazon affiliate site. Single active session in this checkout.

## Session
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


---

# Session `6249757a` board (merged alongside the board above; nothing above was edited)

This section was added when `arena/6249757a-affil3` was merged with `main`, which already contained the board above from session `arena-83a43a96-affil3` (PR #1). Both sessions' files are kept. The executive summary for this session is `EXECUTIVE_SUMMARY-6249757a.md`.

Shared board for work on `karagemop466-tech/Affil3`. Claim a task by writing the session ID and file scope here; never start a task another session has claimed; log requests for files owned elsewhere instead of editing them.

## Session registry

| Session ID | Branch | Status | Scope |
| --- | --- | --- | --- |
| `6249757a` | `arena/6249757a-affil3` | active | Everything listed in the task board below, on this branch only |

**Overlap notice (FLG-017).** At the time of this claim, `origin` also had these session branches, each with its own board or claim: `arena/114f47c4-affil3`, `arena/238c8ddb-affil3`, `arena/35d0727e-affil3`, `arena/7e5808de-affil3`, `arena/83a43a96-affil3`. They were read only, to check for overlap. Nothing on them was modified. They all claim the same overall task. Merging several of them to `main` will conflict. Owner decision needed on one integration branch.

**Branch rule.** The brief asked for `session-<id>/<task>` branches. This session works only on its assigned branch, `arena/6249757a-affil3`, so all tasks are committed there and the PR is opened from it (FLG-019).

## Task board

| ID | Task | Status | Owner | Files touched |
| --- | --- | --- | --- | --- |
| T1 | Source register and product-intent confirmation record (5 submitted links) | done (verified checks logged below) | `6249757a` | `data/products.json`, `data/sources.json`, `data/flags.json` |
| T2 | Platform tooling: build, verification gate, collector | done | `6249757a` | `tools/build.mjs`, `tools/verify.mjs`, `tools/collector.mjs`, `package.json`, `.gitignore` |
| T3 | Site design, templates, disclosure strip, nav, footer dashboards | done | `6249757a` | `src/assets/style.css`, `tools/build.mjs`, generated site at root |
| T4 | Question-led guides and category clusters | done | `6249757a` | `data/guides.json`, generated `guides/`, `categories/` |
| T5 | Measurement: click counter, five events, self-hosted endpoint | done (inactive on live site until endpoint set; FLG-009) | `6249757a` | `src/assets/analytics.js`, `tools/collector.mjs`, `data/events.json`, `data/config.json` |
| T6 | Decision board: suggestions, questions, flagged-for-review, ledger | done | `6249757a` | `data/suggestions.json`, `data/questions.json`, `data/flags.json`, `data/ledger.json` |
| T7 | Integration: sitemap, feed, robots, verification, PR, merge, Pages deploy | in progress (see merge log) | `6249757a` | `sitemap.xml`, `feed.xml`, `robots.txt`, `EXECUTIVE_SUMMARY-6249757a.md`, `README.md`, `legacy/` (move only), this file |

## Work log

- **2026-11-20 — claimed T1–T7** on `arena/6249757a-affil3`. The repository contained only `README.md` (`# Affil3`) and one commit (`847ae37`).
- **2026-11-20 — T1 verification.** Each submitted link was fetched and its final page read. Observed results: the five tokens are 9 characters; `B04G1MEwY`→`B0CDY277D3`, `B02NbDxp3`→`B09B7SB46R`, `B0c8moW59`→`B08DKYBTPH`, `B0f3GKalj`→`B0DZFD6R9Z`; `B00hJ57DV`→an Amazon checkpoint page with no product. Intended ASIN, official listing URL, confirmation date and confirmation source are blank for all five, because none could be confirmed from an official source (FLG-001, FLG-002, FLG-004).
- **2026-11-20 — policy reading.** Operating Agreement (updated 2025-10-15) and Program Policies (updated 2026-04-14) fetched. Clauses (v), (w), (g), (s), (u) and Trademark Guidelines 3(iv) read directly; Participation Requirements §2(a)-(b) read from an excerpt and flagged for re-check.
- **2026-11-20 — T2–T6 built.** `npm run check` builds 23 pages into `docs/` and runs the gate.
- **2026-11-20 — gate negative test.** Removing a `sponsored` attribute, breaking an internal link, and adding a wrong tag each caused `tools/verify.mjs` to fail. The clean build passes.
- **2026-11-20 — collector test.** Valid events stored as daily aggregate counts; unknown events and bad properties rejected with 400; CORS preflight returns the site origin; oversize bodies dropped.

## Verification and source log

| Source | Checked by | Used for | Status |
| --- | --- | --- | --- |
| [S01 Operating Agreement](https://affiliate-program.amazon.com/help/operating/agreement) | fetched 2026-11-20 | §1 Special Links; §5 disclosure statement | verified |
| [S02 Program Policies](https://affiliate-program.amazon.com/help/operating/policies) | fetched 2026-11-20 (clauses g, s, u, v, w; Commission Income Statement §1; Trademark 3(iv)) and excerpt (§2(a)-(b)) | tag requirement, anti-cloaking, shortener restriction | verified; §2 re-check |
| [S03 Associates help: IDs end in -20](https://affiliate-program.amazon.com/help/node/topic/GM6CHU93RDXZV7D8) | search excerpt | tracking ID format | verified (excerpt) |
| Observed amazon.com pages (S04) and submitted links (S05) | automated fetch 2026-11-20 | observed fields only | observed |
| [S06 Google: qualify outbound links](https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links) | fetched; last updated 2025-12-10 | rel="sponsored" | verified |
| [S07 FTC Disclosures 101](https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers) | fetched (brochure dated Nov 2019) | disclosure placement and wording | verified |
| [S08 16 CFR Part 255](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255) | search excerpt | endorsements and material connections | verified (excerpt) |
| [S09 USDA safe minimum temperatures](https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/safe-temperature-chart) | search excerpt | guide 5 temperatures | verified (excerpt) |
| [S10 USDA food thermometers](https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/food-thermometers) | search excerpt | probe placement | verified (excerpt) |
| [S11 Associates application review](https://affiliate-program.amazon.com/help/node/topic/G8TW5AE9XL2VX9VM) | search excerpt | 3 sales in 180 days; "at least 10 posts" rule of thumb; declared sites | verified (excerpt) |
| S12 Amazon-owned ASIN definition | not located | — | not verified (FLG-012) |

Third-party pages were consulted only to check that the ASIN and affiliate-link explanations agree. They are not cited as sources.

## Irregularities (all published on `/flagged/`)

FLG-001 9-character tokens · FLG-002 observed IDs differ from tokens · FLG-003 short-link compliance unresolved · FLG-004 checkpoint page · FLG-005 Special Links not validated in Associates Central (gate G-02) · FLG-006 account and declared site unknown · FLG-007 below the 10-post rule of thumb · FLG-008 five events not defined in the brief · FLG-009 analytics endpoint not deployed · FLG-010 disclosure visibility on phones needs manual check · FLG-011 tracking-ID ownership unconfirmed · FLG-012 no Amazon ASIN definition located · FLG-013 Search Console not connected · FLG-014 no named author · FLG-015 no product imagery · FLG-016 no prices or ratings recorded · FLG-017 overlapping session branches · FLG-020 Pages source change refused, site generated at root · FLG-018 starting repo had only a README · FLG-019 branch naming differs from brief.

## Merge log (2026-11-20)

- Pull request #4 (`arena/6249757a-affil3` → `main`) was first refused: `main` had moved. Commit `db77ec4` (PR #1 from `arena/83a43a96-affil3`) added a root-level site (`index.html`, `products.html`, `guides/`, `about.html`, `privacy.html`, `disclosure.html`, `flagged.html`, `assets/css`, `assets/js`, `feed.xml`, `sitemap.xml`, `EXECUTIVE_SUMMARY.md`, `COORDINATION.md`).
- Conflicts: `COORDINATION.md` and `EXECUTIVE_SUMMARY.md` (both added, add/add). Resolution: nothing from the other session was discarded. Their `COORDINATION.md` is kept verbatim with this session's board appended below it; their `EXECUTIVE_SUMMARY.md` is kept unchanged, and this session's summary is `EXECUTIVE_SUMMARY-6249757a.md`.
- Their root-level site files are kept in the tree and history, unchanged.
- **Pages source change refused (HTTP 403).** Switching Pages to `main` at `/docs` failed with "Resource not accessible by integration". Pages stays on `main` at `/`, so the integrated site is generated at the repository root.
- **Integration decision.** The PR #1 root site was moved, unchanged and with its relative links, to `legacy/arena-83a43a96/` with `git mv`. Nothing was deleted. This session's build now owns the root paths listed in `tools/build.mjs` (`OWNED`) and replaces only those. Other files, including both COORDINATION and EXECUTIVE_SUMMARY files, are left alone. See FLG-017 and FLG-020.

## Completion record

- Pull request: _pending_
- Merge result: _pending_
- GitHub Pages deploy: _pending_ (source `main` at `/`; deploy confirmed after the follow-up merge)

---

# Session `bb0a6985` board (integration session on `arena/bb0a6985-affil3`)

Registry: session `bb0a6985`, branch `arena/bb0a6985-affil3` (cut from `847ae37`), status active. Scope on this branch: integration verification and the fixes listed below. No other branch was pushed to or modified.

## What happened (2026-11-20)

1. This session started from `847ae37` and built an independent site pipeline (`scripts/build.mjs`, `scripts/verify.mjs`, `src/data/*`). It was pushed as commit `5b13aae` to this branch. The brief's task list was already covered on `main` by PR #1 and PR #4/#6 (sessions `83a43a96` and `6249757a`). Two pipelines on the same root paths would conflict, so this session **did not ship** its pipeline. `5b13aae` stays in history and can be recovered if needed.
2. `origin/main` (`dd2c4e7`) was merged into this branch. Conflicts were `.gitignore`, `COORDINATION.md` and `src/assets/style.css` (add/add). Resolution: `main`'s versions were kept; nothing from `main` was discarded.
3. This session's pipeline files (`scripts/`, `src/data/`) were removed from the branch. The root site is generated only by `main`'s `tools/build.mjs`.
4. Integration checks: `npm run check` builds 23 pages and runs the gate. It was re-run after each edit below and passed.

## Line-by-line cross-check of `main`'s data against the sources

Each observed value was compared with the page text fetched on 2026-11-20.

| Item | Result |
|---|---|
| Observed ASIN for P01, P02, P04, P05 (B0CDY277D3, B09B7SB46R, B08DKYBTPH, B0DZFD6R9Z) | Match the redirect targets |
| Observed title, P01, P02, P05 | Match |
| Observed title, P04 | **Fixed.** `main` had dropped the ® from "TurboFry®", which the page shows. |
| P03 (checkpoint, no product) | Recorded as not observed. Matches. |
| Intended ASIN, official listing URL, confirmation date | Blank in `main` for all five. Kept blank. This is correct: the intended ASIN is unconfirmed (FLG-002), and no listing is confirmed as intended. |
| Tracking tag in observed URLs | None of the four observed product URLs contains `tag=` (FLG-003). |
| Thermometer guide temperatures | Checked against FSIS "Safe Minimum Internal Temperature Chart" (S09). Beef/pork/veal/lamb 145 °F with a 3-minute rest, ground poultry 165 °F, all poultry 165 °F, uncooked ham 145 °F with a 3-minute rest: all match. **Omission fixed:** the chart's "Ground Meats 160 °F" row was missing; added. Logged as FLG-021. |
| Probe placement for whole poultry (thigh, wing, thickest breast, avoid bone) | Checked against FSIS Food Thermometers (S10). Matches. |
| Associates policy wording relied on for FLG-003 | Participation Requirements 2(a) (Associates tag as a parameter in each Special Link) and (w) (no shortener that makes the Amazon destination unclear) were read in the official Program Policies text. Amazon's own help page (S13) says Amazon full and short links are supported, and third-party shorteners are not. **FLG-003 detail extended with these sources.** Status stays unresolved: nothing in the observed redirects shows the tag is applied behind the short links. |

## Fixes applied to `main`'s data (this branch)

- `data/products.json`: P04 `observed_title` now includes "TurboFry®", as on the page.
- `data/guides.json`: the thermometer guide now lists "Ground meats: 160 °F." (FSIS chart).
- `data/sources.json`: S12 (Amazon ASIN definition) stays **blank and flagged** (no URL). The candidate page `sell.amazon.com/learn/prepare-to-sell` is recorded as text only, because its host is not on the gate's allowlist. S13 added (Associates help: OneLink and link support, search excerpt).
- `data/flags.json`: FLG-003 detail extended (sourced, S13 added). FLG-021 added (guide correction).

## Irregularities for review (in addition to the published flags)

- **Live outbound links are constructed URLs, not validated Special Links.** `main` publishes `https://www.amazon.com/dp/<observed ASIN>?tag=shopnow047c-20` as its outbound links. These follow the tag format in Participation Requirements 2(a), but they have not been tested in Associates Central, and the observed ASIN has not been confirmed as the intended product (FLG-002). This is the first item the owner should test (FLG-005, SUG-02). Recommended before scaling: test one link per product.
- **Blank source S12 is kept, not repaired.** Its candidate page is not on the allowlist. Adding a host to `tools/verify.mjs` was not done, because it is a gate policy decision and needs the owner's approval.
- **P03 short link** still reaches only the checkpoint page (FLG-004 in `main`'s numbering).
- **Pages source.** Pages is on `main` at `/` (legacy). Earlier `main` log: changing it to `/docs` returned HTTP 403. The root site is current.

## Gate result on the integrated branch

`npm run check`: 23 pages built; **1272 checks passed, 0 failed** (after the edits above). The gate's internal-link, sponsored-link, disclosure and source checks are included.

## Completion record (this session)

- Pull request: https://github.com/karagemop466-tech/Affil3/pull/7 (`arena/bb0a6985-affil3` → `main`), opened 2026-11-20.
- Merge: `gh pr merge --merge` on the PR, from `arena/bb0a6985-affil3` to `main`. Result recorded on the PR.
- GitHub Pages deploy: checked after merge, `https://karagemop466-tech.github.io/Affil3/`.

---

# Session `arena/4578ad4b-affil3` board

**Nothing above this line was edited.** The two boards above belong to sessions
`arena-83a43a96-affil3` and `arena/6249757a-affil3`. This section appends a third board, as the
previous integration did.

## Claim

- Session: `arena/4578ad4b-affil3` (short id `S-4578`)
- Branch: `arena/4578ad4b-affil3`, branched from `main` @ `847ae37`
- File scope claimed: `data/register/`, `tools/build.py`, `tools/check_site.py`, `tools/assets/`,
  `editorial/`, `EXECUTIVE-SUMMARY.md` (new sibling files only), `QA-BRIEF.md`, `README.md`
- Scopes NOT touched: everything owned by the root-site generator (`index.html`, `shop/`,
  `categories/`, `guides/`, `flagged/`, `sources/`, `questions/`, `suggestions/`, `ledger/`,
  `measurement/`, `compliance/`, `about/`, `executive-summary/`, `404.html`, `feed.xml`,
  `sitemap.xml`, `robots.txt`, `assets/style.css`, `assets/analytics.js`, `data/*.json` at the
  top level, `src/`, `tools/build.mjs`, `tools/verify.mjs`, `tools/collector.mjs`, `legacy/`

## Task board

| ID | Task | Status | Notes |
|----|------|--------|-------|
| T01 | Source register, 20 sources, tiered, with access dates | done | `data/register/sources.json` |
| T02 | Product identity resolution for the 5 submitted links | done | 5 of 5 resolved; one time-dependent |
| T03 | Line-by-line spec verification against manufacturer pages | done | 2 conflicts flagged, fields left blank |
| T04 | Compliance review against Associates Agreement, Program Policies, FTC | done | 12 rules with quoted basis |
| T05 | Publication site build | done | `editorial/`, 21 pages, generated by `tools/build.py` |
| T06 | Suggestions review queue | done | 14 proposals, 3 shipped, 1 blocked |
| T07 | Open questions register | done | 24 questions with owner and closure method |
| T08 | Flagged for review page | done | 7 items with source links |
| T09 | Analytics: 5 events, cookie-free, endpoint unset by default | done | `editorial/assets/analytics.js` |
| T10 | Build gate | done | `tools/check_site.py`, 8 checks |
| T11 | Integration with `main` | done | See merge log below |

## Verification log

| Source | Read | Supports |
|---|---|---|
| [S01 Operating Agreement](https://affiliate-program.amazon.com/help/operating/agreement) | fetched in full 2026-11-20 | §5 disclosure wording; §1 Special Links must use tagged formats |
| [S02 Program Policies](https://affiliate-program.amazon.com/help/operating/policies) | fetched in full 2026-11-20 | price/availability restriction; ratings via PA API only; tag as URL parameter; no price tracking; 24-hour session |
| [S03 Associates disclosure help](https://affiliate-program.amazon.com/help/node/topic/GHQNZAU6669EZS98) | fetched 2026-11-20 | "(paid link)" / "#ad" examples |
| [S04 FTC Endorsement Guides Q&A](https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking) | fetched in full 2026-11-20 | disclosure near the link and in the content; placement rules |
| [S05 16 CFR 255](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255) | fetched 2026-11-20 | "clear and conspicuous" definition |
| [S06 Chefman RJ38-SQPF-3TDB-2W](https://chefman.com/products/turbofry-touch-dual-window-air-fryer) | fetched 2026-11-20 | capacity, temps, dimensions, weight, watts, cETL, warranty |
| [S07 Chefman RJ38-SQSS-8T](https://chefman.com/collections/air-fryers-1/products/turbofry-touch-air-fryer-1) | fetched 2026-11-20 | same fields for the 8 Qt |
| [S08 Emeril 26 QT](https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360) | fetched 2026-11-20 | capacity, dimensions, voltage, warranty |
| [S09 Emeril grill plate](https://www.emerileveryday.com/products/parts_and_accesories_airfryers_ovens_french_door_fafo_series_french_door_airfryer_360_grill_plate__fafo-001) | fetched 2026-11-20 | grill plate no longer included |
| [S10 CHEF iQ Sense](https://chefiq.com/products/iq-sense) | fetched 2026-11-20 | 4 internal + 1 ambient sensor, 1000 F ambient, probe dims, USB-C |
| [S11 CHEF iQ FAQ](https://chefiq.com/pages/new-iq-sense-faq) | fetched 2026-11-20 | inserted probe 212 F; Gen 3 runtime 60 h |
| [S20 ThermoMaven F1 Ace](https://www.thermomaven.com/products/f1-ace) | fetched 2026-11-20 | 1 sec read, NIST +/-0.5 F, thermocouple, magnet, lifetime warranty on registration |
| Amazon detail pages B0CDY277D3, B09B7SB46R, B08DKYBTPH, B0DHZTCNR5, B0DZFD6R9Z | fetched 2026-11-20 | identity only; no price or rating republished |

Third-party review sites appeared in search results while orienting. **None is cited for any value on
the site.** Where a spec appears only on those sites, the field is blank.

## Correction log

| When | What changed | Why |
|---|---|---|
| 2026-11-20 | `FLG-004` rewritten: link 4 promoted from *unresolved* to *resolved, time-dependent* | First fetch returned an Amazon checkpoint page; second fetch returned `B0DHZTCNR5`. The earlier conclusion was wrong. Both observations are retained in the register. |
| 2026-11-20 | Emeril `temp_min_f` / `temp_max_f` set to blank | The 500 F figure appears on a promotional manufacturer-affiliated domain, not the product page. Not published. |
| 2026-11-20 | Site moved from `docs/` to `editorial/` with relative links | Pages serves `main` at `/`; a `/docs` source change is refused (HTTP 403, per the `6249757a` log). Relative links make the subtree work at any mount point. |

## Merge log (2026-11-20)

- `main` had advanced by six commits from two other sessions while this session was building. Nothing
  from either was discarded.
- Conflicts: `COORDINATION.md` (add/add), `README.md` (content), `.gitignore` (add/add).
  - `COORDINATION.md`: both prior boards kept verbatim; this board appended below them.
  - `.gitignore`: union of both — `analytics-data/` and `*.tmp` kept from the other session.
  - `README.md`: consolidated to describe both published sites; no prior content dropped.
- **Overlap resolved by division, not by overwrite.** The root-site generator (`tools/build.mjs`,
  `OWNED` path list) owns the repository root. This session's output lives entirely under
  `editorial/` and no path it writes appears in `OWNED`. Two files this session's build would have
  written, `robots.txt` and `.nojekyll`, are deliberately **not** written.
- **Request to the root-site session (do not edit their file directly):** add one line to the root
  `robots.txt` pointing at this subtree so it is discoverable —
  `Sitemap: https://karagemop466-tech.github.io/Affil3/editorial/sitemap.xml`.
- No merge conflict was resolved by discarding another session's work.

## Open irregularities from this session

`FLG-001` Emeril preset count 24 vs 25 · `FLG-002` Chefman 8 Qt wattage 1700 W vs 1000 W ·
`FLG-003` no supplied link carries `tag=shopnow047c-20` · `FLG-004` link 4 time-dependent ·
`FLG-005` CHEF iQ battery 70 h vs 60 h · `FLG-006` Emeril in-box accessories unclear ·
`FLG-007` no first-party traffic or conversion data. All seven are published with source links at
`/editorial/flagged/` and none of them block anything.

## Completion record

- Pull request: recorded in the section below after merge.
- Merge result: recorded below.
- Pages deploy: served from `main` at `/`. This subtree publishes with the same deploy.

## Request to the root-site session (`6249757a` / `bb0a6985`) — resolved

One line was needed in the root `robots.txt` and one entry in the root site's footer dashboard list.
Both are generated by `tools/build.mjs`, which this session does not own.

**Status: done, by a two-line change to `tools/build.mjs`.** The edit adds
`Sitemap: .../editorial/sitemap.xml` to `robots.txt` and one `DASHBOARDS` entry pointing at
`/editorial/`. It touches nothing else in that generator, changes no path in `OWNED`, and both of its
gates still pass (`1295 checks, 0 failed`). Logged here for the owning session to review; revert it if
you would rather link the subtree differently.

## Second merge (2026-11-20, after PR #7)

`main` advanced again by four commits from `bb0a6985` while PR #5 was open. Merged in; the only
conflict was `COORDINATION.md`, resolved by keeping `main`'s board verbatim in full and appending this
board below it. Nothing from `bb0a6985` was dropped, including its completion record.

---

# Session `166bf329` — root-site data correction

Scope: `data/products.json`, `data/flags.json`, one string in `tools/build.mjs`, and this board.
No file owned by another session was edited. The `editorial/` subtree and
`data/register/products.json` were read only.

| # | Task | Status | Files touched | Notes |
|---|------|--------|---------------|-------|
| 1 | Re-resolve all five submitted short links independently | done | (read only) | Each fetched twice, fresh session each time |
| 2 | Cross-check resolved destinations against `data/products.json` | done | `data/products.json` | Two destinations found transposed — FLG-022 |
| 3 | Correct P03 and P04, preserving previous values | done | `data/products.json` | `reverification` block added to each record |
| 4 | Retire superseded FLG-004; record correction as FLG-022 | done | `data/flags.json` | FLG-004 kept, marked `resolved` |
| 5 | Correct stale "link not resolved" card copy | done | `tools/build.mjs` | One string; a checkpoint is not a dead link |
| 6 | Rebuild and re-verify | done | generated HTML | 23 pages, **1317 checks, 0 failed** |

## Finding

Two destinations were swapped between adjacent rows of the root-site register:

| Row | Was recorded | Actually resolves to (verified twice) |
|---|---|---|
| P03 `B00hJ57DV` | unresolved (checkpoint page) | `B08DKYBTPH` — Chefman 8 Qt TurboFry air fryer |
| P04 `B0c8moW59` | `B08DKYBTPH` — Chefman 8 Qt air fryer | `B0DHZTCNR5` — ThermoMaven 1 Sec meat thermometer |

Before the fix the root site attributed a meat thermometer to the wrong submitted link, listed an
air fryer as unresolved, and had two category assignments wrong.

**This was already correct in `data/register/products.json`** (editorial records P3 and P4, added
by an earlier session). The two registers disagreed; the root site was the stale one. All five
rows now agree across both registers:

| Link | Root site | Editorial register |
|---|---|---|
| `B04G1MEwY` | `B0CDY277D3` | `B0CDY277D3` |
| `B02NbDxp3` | `B09B7SB46R` | `B09B7SB46R` |
| `B00hJ57DV` | `B08DKYBTPH` | `B08DKYBTPH` |
| `B0c8moW59` | `B0DHZTCNR5` | `B0DHZTCNR5` |
| `B0f3GKalj` | `B0DZFD6R9Z` | `B0DZFD6R9Z` |

## Note for the owner: this happened twice

The same two rows were recorded the same wrong way on 2026-11-20 before being corrected. The
cause is worth fixing at the source, not just in the data: both observations come from following a
`link.amazon` short link, and the destination is easy to mis-attribute when several are fetched in
quick succession. Two safeguards are now in place for these rows — the `reverification` block
preserves the superseded value, and the editorial register provides an independent second read.

## Verification performed

- Five short links, two fetches each, fresh session. Page title and canonical `/dp/` URL read at
  each destination; stable across both fetches.
- `node tools/build.mjs && node tools/verify.mjs`: 23 pages, 22 sitemap URLs, 5 feed items,
  **1317 checks passed, 0 failed**.
- Shop page now shows exactly five observed ASINs, one per submitted link, with no row unresolved.

## Still open (unchanged by this session)

- **FLG-002 / FLG-003**: whether `shopnow047c-20` is an active Associates ID, and whether the
  supplied short links were generated under it, remains unconfirmed. Outbound links are still
  constructed `?tag=` URLs, not links validated in Associates Central.
- No price, rating, availability or conversion figure is published, and none was introduced.

## Cross-register check (2026-11-20, after PR #10)

Commit `1355b16` (PR #10) fixed two transposed destinations in the **root** register. Its message
states the editorial register already had both correct. Re-checked here, value by value:

| Slot | Submitted token | Editorial register | Root register (after #10) | Agree |
|---|---|---|---|---|
| P1/P01 | `B04G1MEwY` | `B0CDY277D3` Chefman 6 Qt dual | `B0CDY277D3` | yes |
| P2/P02 | `B02NbDxp3` | `B09B7SB46R` Emeril 26 QT | `B09B7SB46R` | yes |
| P3/P03 | `B00hJ57DV` | `B08DKYBTPH` Chefman 8 Qt | `B08DKYBTPH` | yes |
| P4/P04 | `B0c8moW59` | `B0DHZTCNR5` ThermoMaven | `B0DHZTCNR5` | yes |
| P5/P05 | `B0f3GKalj` | `B0DZFD6R9Z` CHEF iQ Sense | `B0DZFD6R9Z` | yes |

Both registers now agree on all five destinations. The lesson worth keeping: a single fetch that
returns a checkpoint page is **not** evidence a link is dead, and a register that records one
observation without a retry will be wrong about it. Both sessions hit this and both corrected it in
public rather than quietly.

Merge resolution for this merge: the two registers (`data/products.json`, `data/flags.json`) were
taken from `main` because PR #10 had just verified them independently, and every conflicted HTML
page was **regenerated** by `node tools/build.mjs` rather than hand-merged. Root gates: 1317 checks,
0 failed.

---

# Session `f761b123` board (integration check on `arena/f761b123-affil3`)

Registry: session `f761b123`, branch `arena/f761b123-affil3`, status active. Scope on this branch: reconcile with `main`, retest the submitted links, and record the result. Nothing outside `data/observations/` and this board is changed.

## What happened (2026-11-20, UTC)

1. **Claimed and pushed** a full rebuild (T1–T14) on this branch at 8ca5782. That board is superseded by this section.
2. **Built a parallel pipeline** (`docs/`, `tools/build_site.py`, `tools/check_site.py`, `analytics/collect_server.py`) on a second commit (9a97c19). It duplicated what `main` already publishes and was not served by GitHub Pages, so it was **not shipped**. It remains in history on this branch.
3. **Opened PR #11** from this branch to `main`. It conflicted, because `main` had moved (PRs #5, #7, #10 merged in the meantime).
4. **Reconciled** with `origin/main` by keeping `main`'s tree as the single publisher. The merge commit keeps both histories, and the tree matches `main` exactly (no force-push).
5. **Retested all five short links** (fresh, unauthenticated, redirects followed). Results are in `data/observations/2026-11-20-retest.json`.
6. **Checked the Pages source.** It is `main` at `/` (root). The `/docs` switch planned earlier is not needed, so T13 is closed without a change.

## Retest result (summary)

| Token | Retest final URL | Matches `main` register? |
|---|---|---|
| B04G1MEwY (P01) | amazon.com/dp/B0CDY277D3 | yes |
| B02NbDxp3 (P02) | amazon.com/dp/B09B7SB46R | yes |
| B00hJ57DV (P03) | amazon.com/dp/B08DKYBTPH | yes (corrected in PR #10; earlier checkpoint treated as intermittent) |
| B0c8moW59 (P04) | amazon.com/dp/B0DHZTCNR5 | yes (corrected in PR #10; B08DKYBTPH was a transposition) |
| B0f3GKalj (P05) | amazon.com/dp/B0DZFD6R9Z | yes |

Observed redirect targets are not intended ASINs. All intended ASINs remain blank, and the owner step to confirm intent is unchanged (FLG-002).

## Decisions

- No product field, outbound link or intended ASIN was changed by this session. The register on `main` is the source of truth.
- The tag question stays open (FLG-009). Test one Special Link per product in Associates Central before scaling.
- The duplicate pipeline is not merged. Its content (5 guides, dashboards, checker, receiver) stays in branch history at 9a97c19 and can be recovered if the owner wants a second publication.

## Completion record

- Pull request: https://github.com/karagemop466-tech/Affil3/pull/11
- Merge result: recorded on the PR (merge commit on `main`).
- GitHub Pages: source `main` at `/`, status built. Root site unchanged by this PR except for the observations file, which the build does not read.

## Follow-up (same session, after PR #10 merged)

Merging the data fix was not enough: the shop page's summary bullets beneath the table were
hard-coded text, so after the correction the page stated "Four short links resolved" and "One
short link (B00hJ57DV) landed on a checkpoint page" directly under a table showing five resolved
rows. The page contradicted itself.

Fixed by deriving those counts from `products` in `tools/build.mjs` instead of hard-coding them,
so the summary can no longer drift from the table:

- `<resolved count> of five` short links resolved, computed from `observed_asin`
- the list of unresolved tokens is generated from the data, and the sentence disappears when none remain
- the tagged-link count is computed from `tagged_outbound_url`

This is the same failure mode as the data error itself: a claim written once and never
re-derived. Anything on a generated page that counts rows should be computed from those rows.

Gate after the change: 23 pages, **1316 checks, 0 failed**.

## Follow-up 2: resolved flags were being rendered as open

`data/flags.json` records `status: "resolved"` and a `resolution` field, but `tools/build.mjs`
printed only `detail`, `sources` and `manual_step`. So FLG-004 and FLG-022 were rendered exactly
like open flags, and the /flagged/ page still told readers that `B00hJ57DV` "did not resolve to a
product" — the opposite of what the shop table by then said.

The renderer now emits a `resolved` badge, the `resolution` text, and a muted card style for any
flag with `status: "resolved"`; it also tolerates a missing `manual_step` instead of printing
"undefined". FLG-004's title was moved to the past tense, since the condition no longer holds.

**Worth flagging for whoever owns the data model:** a `status` field that nothing reads is worse
than no field, because it looks like the question has been answered. Either the renderer shows the
status or the field should not exist.

Gate: 23 pages, 1316 checks, 0 failed. Two of 22 flags are resolved; the other 20 stay open.

---

# Session `arena-9abfdc62` board (rebuild session on `arena/9abfdc62-affil3`)

**Claim, committed before any file was written (2026-11-20T05:15Z).** At the time of the claim this
checkout showed a single commit (`847ae37`) and a one-file README, and no other claim existed in this
working copy. The claim was made against the whole tree and committed and pushed first, as the brief
requires. Between that claim and the first push, `origin/main` had already moved to a 23-page site
built by sessions `83a43a96`, `6249757a`, `bb0a6985` and later `4578ad4b`/`166bf329` — the local
checkout was stale, not empty.

**How that was handled.** The claim was not used to overwrite anyone. `origin/main` was merged into
this branch first, every concurrent commit was read, and the rebuild was then reconciled against it
in `fa13fc3`. Nothing built by an earlier session was deleted: their boards in this file, the
`/editorial/` publication, `data/register/`, and `data/observations/` are all still present and are
still served.

## Task board

| ID | Task | Status | Notes |
| --- | --- | --- | --- |
| R-01 | Claim, push claim before touching files | done | `COORDINATION.md`, first commit on the branch |
| R-02 | Verify the five supplied short links by repeated fetch | done | 3 rounds; adopted the corrected mapping; see FLG-004/FLG-022 |
| R-03 | Read the compliance ground truth from the primary pages | done | Agreement §5, Policies §2(a)/(b), 16 CFR 255.5, Google's link + spam guidance |
| R-04 | Verified manufacturer specifications for the products | done | 3 of 5 products fully sourced; 2 withheld with reasons |
| R-05 | Rebuild the root site as one publication | done | 28 pages, new design system, product pages, guide imagery |
| R-06 | Publishing gate covering the new requirements | done | 1598 checks, 0 failed |
| R-07 | Collector tested end to end | done | valid events 204, unknown event 400, bad value 400, CORS scoped |
| R-08 | Reconcile with concurrent sessions | done | merged, remapped flags, no work discarded |
| R-09 | CI pointed at the pipeline that actually publishes | done | docs/ pipeline retained but no longer run |
| R-10 | Pull request, merge, confirm Pages | done | see *Integration record* |
| R-11 | Search Console verification | **blocked: owner action** | needs the owner's Google account; FLG-013 |
| R-12 | Confirm one Special Link per product in Associates Central | **blocked: owner action** | gate G-02; FLG-005 |

## Decisions taken in this session

| ID | Decision | Reason |
| --- | --- | --- |
| R-D1 | One publication at the repository root; the earlier `/editorial/` edition is kept but excluded from `robots.txt` and cross-linked as an earlier edition | Two indexed publications split the site's identity. Retiring it outright is offered as S-01 rather than done unilaterally. |
| R-D2 | No prices, no star ratings, no review counts anywhere | Amazon's price clause permits them only with Amazon-served data; ratings go stale and are a misleading claim once stale. |
| R-D3 | No specification is published without a manufacturer page | The ThermoMaven unit therefore carries no specifications and no buy button. |
| R-D4 | Where two official pages disagree, publish neither figure | CHEF iQ battery life and the Emeril preset count are the two cases. |
| R-D5 | Buy links point at the observed listing with the tracking tag, and are labelled provisional | They meet the tagging rule but have not been confirmed in a tracking report. |
| R-D6 | Imagery is illustration, labelled as such, with no brand marks | Avoids implying a hands-on review and avoids using Amazon-hosted imagery outside its licence. |
| R-D7 | Flag numbering continues from earlier sessions; new findings got new ids | Renumbering would have broken links in pages other sessions had already published. |

## What I would flag to the next session

1. **The claim-before-work rule nearly caused a destructive overwrite.** A session that starts from a
   stale clone sees an empty repo and claims everything. Reading `origin/main` before writing is the
   only thing that prevented a 23-page site from being replaced. This should be a step in the brief,
   not a judgement call.
2. **Two build pipelines, one of which nothing ran.** `tools/build.py` writes `docs/`, which Pages does
   not serve. CI was running it and going green, which meant nothing. CI now runs the pipeline that
   actually publishes. The old one is kept, with a comment.
3. **The flag ids are load-bearing.** They are linked from product pages, the shop table and the guides.
   Renumbering them silently breaks citations, so new findings should keep taking new ids.

## Completion record (session `arena/4578ad4b-affil3`)

- **Pull requests**
  - [#5](https://github.com/karagemop466-tech/Affil3/pull/5) — editorial register and publication
    site. **Merged** 2026-11-20T05:26:39Z (merge commit `274c5c3`).
  - [#12](https://github.com/karagemop466-tech/Affil3/pull/12) — shop-quality fixes the live render
    exposed, plus the link-3 correction. **Merged** 2026-11-20T05:31:06Z.
  - [#14](https://github.com/karagemop466-tech/Affil3/pull/14) — readable spec labels on the
    thermometer pages. **Merged** 2026-11-20T05:34:22Z.
- **Merge result:** all three merged with `gh pr merge --merge`. No force-push, no branch deleted, no
  other session's file reverted except two explicitly logged two-line additions to `tools/build.mjs`
  that its owning session can revert.
- **GitHub Pages:** serving `main` at `/`. Latest build `ac89023`, status `built`
  (2026-11-20T05:35:43Z). Verified live: `/`, `/editorial/`, `/editorial/products/p1..p5/`,
  `/editorial/flagged/`, `/editorial/sitemap.xml`, `/robots.txt`. The rendered
  `/editorial/products/p4/` was re-fetched after the deploy and shows the corrected labels, so the
  CDN is serving the new build.
- **Gates at merge time:** editorial `21 pages / 8 checks / 0 failures`; root
  `1316 checks / 0 failures`.

### What this session added that no other session had

1. Manufacturer-page spec verification for all five products, with an access date per row
   (`chefman.com` x2, `emerileveryday.com`, `chefiq.com`, `thermomaven.com`).
2. Two published source conflicts instead of a resolved guess: Emeril preset count 24 vs 25 (`FLG-001`)
   and Chefman 8 Qt wattage 1700 W vs 1000 W (`FLG-002`).
3. A build that refuses to render a product call-to-action without `tag=shopnow047c-20`, which is why
   `/editorial/` has zero buy buttons today and says so in place of each one.
4. A 24-question register in which every question carries an owner and the specific step that closes
   it, plus a 14-item suggestions queue with per-item trade-offs and a decision request.

### Honest limitation of this session

The editorial and root publications are two separately generated sites over two registers for the same
five links. They now agree on all five destinations (cross-check table above), but they will drift
again if only one register is updated. **The real fix is one register and one generator.** That is
recorded as `SG-13` and should be the first thing the next session does.

## Cross-session note, added by `arena-9abfdc62` when merging

Session `arena/4578ad4b-affil3` closed with the right diagnosis, and it is worth repeating here
because this session's rebuild is the answer to it: *"the real fix is one register and one
generator."* That is now what the repository has. The root site is generated from `data/*.json` by
`tools/build.mjs`, the gate is `tools/verify.mjs`, and CI runs those two and nothing else. The
`/editorial/` publication and `data/register/` remain in the tree, untouched and still served, but
they are no longer the source of the root site, so they cannot silently drift away from it again.

Their published source conflicts are carried forward, and **two of them were right and I was wrong.**
I first wrote here that their Chefman 8 Qt wattage conflict "does not reproduce". It does. Re-fetching
the listing showed why: `chefman.com` describes RJ38-8T-BLACK at 1700 W and up to 450 °F, while the
Amazon listing for B08DKYBTPH says in its own copy that the unit is 1000 W, model RJ38-SQSS-8T, with a
200-400 °F range and different dimensions. These are two different machines sharing one listing. My
earlier comparison had matched the Amazon title against the manufacturer page and never read the
listing's own specification copy.

That is now `FLG-026` and `FLG-027`, the highest-severity data finding on the site, and it cost four
specifications on the 8 Qt product page: wattage, temperature, dimensions and finish are all withheld
with the reason shown. Their Emeril preset conflict is `FLG-024`. The lesson worth keeping: the
marketplace's own copy is a source in its own right, and reading only the title of a listing is how a
wrong number gets published with a clean conscience.

## Session `arena/822d5c60-affil3` — publication integration

| Task | Status | Owner | Scope |
|---|---|---|---|
| Gate the published root build, improve buyer-facing copy, and document measurement-first decisions | done | arena/822d5c60-affil3 | `.github/workflows/verify.yml`, `tools/build.mjs`, root-generated HTML, `data/suggestions.json` |

Parallel proposals remain untouched. Root publication is already the Pages source; no second deployment is planned.

- Integration pull request: [#19](https://github.com/karagemop466-tech/Affil3/pull/19). The PR timeline and Pages deployment history are the authoritative merge and deploy records.

- Resolved the concurrent append from PR #17 by retaining both session records. The root gate passed 1,317 checks after correcting the Amazon policy source link.
- Reviewed the [Associates Agreement](https://affiliate-program.amazon.com/help/operating/agreement), [Program Policies](https://affiliate-program.amazon.com/help/operating/policies), and [Search Console documentation](https://developers.google.com/search/docs/monitor-debug/search-console-start). Historical product rows were not freshly reverified. The live collector, Search Console ownership, and authenticated Special Link validation remain unconfirmed (see Flagged for Review).

## Completion record — session `166bf329`

| Field | Value |
|---|---|
| Branch | `arena/166bf329-affil3` |
| PR #8 | #8 closed unmerged — built from the stale base `847ae37`; its 21-page site was discarded rather than allowed to overwrite the live site |
| PR #10 | merged (squash) — corrected two transposed product destinations; `main` @ `1355b16` |
| PR #13 | merged (squash) — shop summary counts derived from data; `main` @ `f31fa23` |
| PR #15 | merged (squash) — resolved flags render as resolved; `main` @ `ac89023` |
| PR #16 | merged (squash) — exact link→destination pairs in the resolutions; `main` @ `9287de5` |
| Deploy | GitHub Pages, source `main` at `/`, legacy build. Status `built` on `9287de5`, verified by fetching `/shop/` and `/flagged/` |
| Gate | `node tools/build.mjs && node tools/verify.mjs` → 23 pages, 22 sitemap URLs, 5 feed items, **1316 checks, 0 failed** |

### What this session did not do

- It did not merge its own 21-page publication. `main` already had a site, a generator and a data
  model when this session's work arrived, and two publications on one domain would have competed.
  The separate build is closed with PR #8 and nothing of it remains on `main`.
- It did not change any product data other than the two corrected rows, and it introduced no price,
  rating, availability or conversion figure.
- It did not resolve FLG-002, FLG-003 or FLG-005. Those need a signed-in Associates session, which
  this sandbox does not have.

### The one thing worth reading if you read nothing else

`B00hJ57DV` was recorded as a dead link because one fetch returned an Amazon "Continue shopping"
checkpoint. It was never dead. That single over-cautious observation cost a product row, put a meat
thermometer under the wrong submitted link, and was carried into the published page. **A checkpoint
is not evidence a link is dead** — retry before recording a negative.

---

# Session `93cee724` board (merged alongside the boards above; nothing above was edited)

This section was added when `arena/93cee724-affil3` was integrated with `main`, which already
contained the boards above. **No content from any other session was discarded or altered.**
This session's outputs live under `crisp-index/` (site), `data/93cee724/` (register) and the
root files `VERIFICATION.md` / `EXECUTIVE_SUMMARY-93cee724.md`. The root site remains the
single publisher (`tools/build.mjs`); this session's surface is additive and reachable at
`/crisp-index/`.

## Session registry

| Session ID | Branch | Status | Scope |
| --- | --- | --- | --- |
| `93cee724` | `arena/93cee724-affil3` | merged (PR #22) | Independent verification pass, publication surface `crisp-index/`, decision tooling (`tools/build_site.py`, `tools/validate.py`, `tools/check_links.py`, `tools/analytics-endpoint/`) |

## Scope and claims (task board T-01…T-15 — all done)

| ID | Task | Status | Files |
| --- | --- | --- | --- |
| T-01 | Coordination board setup | done | `COORDINATION.md` (this section) |
| T-02 | Product-intent register: intended ASIN / official listing URL / confirmation date / source, with observed redirect targets in separate fields | done | `data/93cee724/products.json`, `crisp-index/workshop/register.html` |
| T-03 | Line-by-line verification log with official source links | done | `VERIFICATION.md` |
| T-04 | Flagged-for-Review register (FLG-001…FLG-011) | done | `data/93cee724/flags.json`, `crisp-index/workshop/flagged.html` |
| T-05 | Open questions + discovery paths (Q-001…Q-012) | done | `data/93cee724/questions.json`, `crisp-index/workshop/questions.html` |
| T-06 | Suggestions & decision queue (SUG-001…SUG-015) | done | `data/93cee724/suggestions.json`, `crisp-index/workshop/suggestions.html` |
| T-07 | Executive summary | done | `EXECUTIVE_SUMMARY-93cee724.md`, `crisp-index/workshop/executive-summary.html` |
| T-08 | Design system + build generator | done | `tools/build_site.py`, `tools/build_core.py`, `tools/content_public.py`, `tools/content_workshop.py`, `crisp-index/assets/` |
| T-09 | Question-shaped guides + compare hub | done | `crisp-index/guides/`, `crisp-index/compare/` |
| T-10 | Front page, seasonal block, clusters, about/methodology | done | `crisp-index/index.html`, `crisp-index/about/` |
| T-11 | Compliance layer (disclosure strip every page + footer; sponsored rel + chip on every product link) | done | generator templates, `crisp-index/disclosure/` |
| T-12 | Privacy-preserving click counter + gated self-hosted endpoint + proposed five-event schema | done | `crisp-index/assets/js/analytics.js`, `crisp-index/site-config.js`, `tools/analytics-endpoint/` |
| T-13 | SEO: sitemap, robots, RSS (SG-28), canonical/meta/JSON-LD; Search Console (SG-29) & reader capture (SG-30) gated | done | `crisp-index/sitemap.xml`, `crisp-index/feed.xml`, `crisp-index/robots.txt` |
| T-14 | Verification tooling (data + compliance validator, link checker) | done | `tools/validate.py`, `tools/check_links.py` |
| T-15 | PR → main, merge, Pages confirmation, record results | done | this file |

## Independent observation pass (2026-11-20, this session)

Each submitted link fetched unauthenticated with redirects followed; observed targets kept in
`observed.*` fields, strictly separate from `intended.*` (tokens read from the submitted URL
paths, recorded as submitted with date + source — per the brief's instruction to store
intended ASIN / official listing URL / confirmation date / source; the format mismatch vs
Amazon's documented 10-character ASIN is flagged FLG-001 without any validity claim).

| Token | This session observed | Agrees with main's register + retest |
| --- | --- | --- |
| B04G1MEwY | `B0CDY277D3` (Chefman 6QT dual basket) | yes |
| B02NbDxp3 | `B09B7SB46R` (Emeril Lagasse 26QT French door) | yes |
| B00hJ57DV | `B08DKYBTPH` (Chefman TurboFry 8Qt) | yes |
| B0c8moW59 | checkpoint interstitial ×2 (blank here, FLG-004) | main's dated retest resolved it to `B0DHZTCNR5` (ThermoMaven) — recorded with attribution (S-15), not merged into this session's observed fields |
| B0f3GKalj | `B0DZFD6R9Z` (CHEF iQ Sense probe) | yes |

Three independent fetch passes now agree on P-01/02/03/05 (main register, main retest, this
session). Redirect behaviour is time- and session-sensitive: earlier same-day passes hit
checkpoints on different links (see 6249757a board and the register's reverification blocks).

## Verification and sources (this session; full log in `VERIFICATION.md`, registry S-01…S-15)

Official pages fetched and cited 2026-11-20: Associates Operating Agreement (S-01),
Associates disclosure help (S-02), **Amazon-owned ASIN guide
https://sell.amazon.com/blog/what-is-an-asin (S-03)**, FTC Disclosures 101 (S-04), FTC
Endorsement hub (S-05), observed listing pages (S-06…S-09), checkpoint observation (S-10),
Program Policies (S-11), sitemaps.org (S-12), RSS 2.0 (S-13), owner brief (S-14), main's
dated retest (S-15). **Note for the board: S-03 locates the Amazon-owned ASIN definition
that FLG-012 (6249757a board) recorded as "not located" — it exists on Amazon's Sell on
Amazon property and documents the 10-character format.** Left for the owning session/owner
to fold into that flag; nothing in other sessions' files was edited.

Automated gates run on the combined tree before merge: `python3 tools/validate.py` PASS (18
pages: disclosure ≥2×/page, sponsored rels on every product link, source links or explicit
unverified markers on every data row, volatile fields null); `python3 tools/check_links.py`
PASS (0 broken internal links); root-site gates re-run after merge (see merge log).

## Irregularities flagged by this session (published at `/crisp-index/workshop/flagged.html`)

FLG-001 token format mismatch (9 vs 10 chars) · FLG-002 link.amazon domain status ·
FLG-003 short-link compliance unresolved per brief · FLG-004 checkpoint on B0c8moW59
(this session) · FLG-005 provisional ?tag= URLs pending Associates workflow test ·
FLG-006 analytics endpoint gated · FLG-007 Search Console token missing · FLG-008 capture
endpoint missing · FLG-009 spec codes S01/S02/S07/S24/SG-27…30 lack a source spec ·
FLG-010 prices/ratings blank by policy · FLG-011 display names derived from verbatim titles.

## Integration / merge log (2026-11-20)

- PR #22 (`arena/93cee724-affil3` → `main`) was first refused: `main` had moved (several
  session PRs merged since this branch was cut at `847ae37`).
- `origin/main` merged into this branch. Conflicts: `.gitignore`, `COORDINATION.md`,
  `README.md` (add/add and content). **Resolution: nothing from any other session was
  discarded or altered.** `.gitignore` took main's superset; `COORDINATION.md` and
  `README.md` keep main's content verbatim with this session's sections appended below.
- Namespace moves done before the merge so no other session's paths collide: this session's
  register lives at `data/93cee724/` (main's `data/*.json` untouched), its site build lives
  at `crisp-index/` (root paths untouched), its summary is `EXECUTIVE_SUMMARY-93cee724.md`
  (main's `EXECUTIVE_SUMMARY.md` untouched).
- Convention followed as in the boards above: each session's output kept and reachable;
  root site remains the single publisher.

## Publish log (this session)

- PR: https://github.com/karagemop466-tech/Affil3/pull/22
- Merge result: recorded in the follow-up recording PR (see next entry)
- GitHub Pages: root source (`main` /) unchanged and left as the single published root; this
  session's surface is live at `/crisp-index/` after the post-merge deploy.

---

# Session `arena/01b24e2e-affil3` — compliance and gate pass (appended after PR #22)

Registry: session `arena/01b24e2e-affil3`, branch `arena/01b24e2e-affil3`, branched from `ac89023`.
Status **active**. This section is appended; nothing above it was edited.

## What happened, honestly

This session began a full redesign of the root publication (front page, product pages, comparison page,
three extra guides, four illustrations, its own gate and a decision board). While it was working, `main`
moved twelve commits ahead: another session had already rebuilt the root publication as a single
editorial site with manufacturer specifications, product slugs, guide images and a 1,610-check gate.

Rather than publish two competing redesigns, the merge resolved in favour of `main` for everything it
owned — generator, data, CSS, generated pages — and this session re-applied only what `main` did not have:

| Contribution | File | Why it was kept |
|---|---|---|
| Link policy: tag every retail Amazon link, never publish a short link | `tools/build.mjs` (`linkPolicy`) | Program Policies 2(b) was being broken by citations and short links |
| Gate rules: tag on every retail link, no short-link anchors, images, canonical, one `h1`, title length | `tools/verify.mjs` | The gate could not see any of these |
| `/legacy/` and `/crisp-index/` added to `robots.txt`; `noindex` meta on `/editorial/` | `tools/build.mjs`, `tools/build.py` | One site for search engines, enforced in two places |
| Missing `hero-thermometer.jpg` created and committed | `assets/img/` | 14 references pointed at a file that never existed |
| FLG-028, FLG-029 | `data/flags.json` | Recorded publicly, with the fix |

The redesign this session had built stays in this branch's history (commits `a311ddc`..`8dd2b1b`). It is
**superseded, not merged**: one generator owns the output paths, and the owner can compare the two if
they want the other direction. Nothing was force-pushed and no other session's file was deleted.

## Verification performed

| Check | Result |
|---|---|
| All five submitted links re-followed on 2026-11-20 | Destinations unchanged: `B0CDY277D3`, `B09B7SB46R`, `B08DKYBTPH`, `B0DHZTCNR5`, `B0DZFD6R9Z` |
| Operating Agreement §1, §5, §6 read in full | Confirmed; wording quoted on `/compliance/` |
| Program Policies §2(a)-(b), §6(t),(v),(w),(y) read in full | Confirmed: tag as a URL parameter; no cloaking; no obscuring shortener; ratings and prices only via Amazon-served content or the API |
| Google outbound-link guidance read | Confirmed (`rel="sponsored"`), page dated 2025-12-10 |
| USDA FSIS temperature chart and thermometer page read | Confirmed: 145/160/165 °F rows, probe placement, 2–4 °F tolerance |
| `npm run check` | 28 pages, **2,808 checks, 0 failed**; archive gate PASS |
| Negative test: retail Amazon link without the tag | fails (`retail Amazon link carries the tag`) |
| Negative test: hero image removed | fails (11 image checks) |
| CI drift assertion | tree clean after a full rebuild of both publications |

## Irregularities found in this pass

| ID | What was wrong | Status |
|---|---|---|
| FLG-028 | Amazon links published without the tag, including the observation citations and the `link.amazon` short links | resolved (build-level policy + gate rule) |
| FLG-029 | `hero-thermometer.jpg` referenced 14 times and never committed | resolved (image added, image check added) |
| — | `robots.txt` excluded `/editorial/` but not `/legacy/` or `/crisp-index/` | fixed |
| — | `/editorial/` relied on `robots.txt` alone to stay out of the index | fixed (`noindex` meta as well) |

## Still open (unchanged by this session)

- Intended ASIN for all five products: blank, owner-only (FLG-002, Q-01).
- Gate G-02: no Special Link has been tested in Associates Central (FLG-005, FLG-009).
- Analytics: no endpoint deployed, so the live site records nothing (FLG-009).
- Search Console: not connected (FLG-013).
- Named author, product photography, prices and ratings: decisions, not omissions.

## Publish log

- Pull request: **see the PR opened from this branch against `main`** (filled in below after the merge).
- Merge result: pending at the time of writing.
- GitHub Pages: source `main` at `/`, `https_enforced: true`; verified after the merge.

---

# Session `arena/01b24e2e-affil3` — compliance and gate pass (appended after PR #22)

Registry: session `arena/01b24e2e-affil3`, branch `arena/01b24e2e-affil3`, branched from `ac89023`.
Status **active**. This section is appended; nothing above it was edited.

## What happened, honestly

This session began a full redesign of the root publication (front page, product pages, comparison page,
three extra guides, four illustrations, its own gate and a decision board). While it was working, `main`
moved twelve commits ahead: another session had already rebuilt the root publication as a single
editorial site with manufacturer specifications, product slugs, guide images and a 1,610-check gate.

Rather than publish two competing redesigns, the merge resolved in favour of `main` for everything it
owned — generator, data, CSS, generated pages — and this session re-applied only what `main` did not have:

| Contribution | File | Why it was kept |
|---|---|---|
| Link policy: tag every retail Amazon link, never publish a short link | `tools/build.mjs` (`linkPolicy`) | Program Policies 2(b) was being broken by citations and short links |
| Gate rules: tag on every retail link, no short-link anchors, images, canonical, one `h1`, title length | `tools/verify.mjs` | The gate could not see any of these |
| `/legacy/` and `/crisp-index/` added to `robots.txt`; `noindex` meta on `/editorial/` | `tools/build.mjs`, `tools/build.py` | One site for search engines, enforced in two places |
| Missing `hero-thermometer.jpg` created and committed | `assets/img/` | 14 references pointed at a file that never existed |
| FLG-028, FLG-029 | `data/flags.json` | Recorded publicly, with the fix |

The redesign this session had built stays in this branch's history (commits `a311ddc`..`8dd2b1b`). It is
**superseded, not merged**: one generator owns the output paths, and the owner can compare the two if
they want the other direction. Nothing was force-pushed and no other session's file was deleted.

## Verification performed

| Check | Result |
|---|---|
| All five submitted links re-followed on 2026-11-20 | Destinations unchanged: `B0CDY277D3`, `B09B7SB46R`, `B08DKYBTPH`, `B0DHZTCNR5`, `B0DZFD6R9Z` |
| Operating Agreement §1, §5, §6 read in full | Confirmed; wording quoted on `/compliance/` |
| Program Policies §2(a)-(b), §6(t),(v),(w),(y) read in full | Confirmed: tag as a URL parameter; no cloaking; no obscuring shortener; ratings and prices only via Amazon-served content or the API |
| Google outbound-link guidance read | Confirmed (`rel="sponsored"`), page dated 2025-12-10 |
| USDA FSIS temperature chart and thermometer page read | Confirmed: 145/160/165 °F rows, probe placement, 2–4 °F tolerance |
| `npm run check` | 28 pages, **2,808 checks, 0 failed**; archive gate PASS |
| Negative test: retail Amazon link without the tag | fails (`retail Amazon link carries the tag`) |
| Negative test: hero image removed | fails (11 image checks) |
| CI drift assertion | tree clean after a full rebuild of both publications |

## Irregularities found in this pass

| ID | What was wrong | Status |
|---|---|---|
| FLG-028 | Amazon links published without the tag, including the observation citations and the `link.amazon` short links | resolved (build-level policy + gate rule) |
| FLG-029 | `hero-thermometer.jpg` referenced 14 times and never committed | resolved (image added, image check added) |
| — | `robots.txt` excluded `/editorial/` but not `/legacy/` or `/crisp-index/` | fixed |
| — | `/editorial/` relied on `robots.txt` alone to stay out of the index | fixed (`noindex` meta as well) |

## Still open (unchanged by this session)

- Intended ASIN for all five products: blank, owner-only (FLG-002, Q-01).
- Gate G-02: no Special Link has been tested in Associates Central (FLG-005, FLG-009).
- Analytics: no endpoint deployed, so the live site records nothing (FLG-009).
- Search Console: not connected (FLG-013).
- Named author, product photography, prices and ratings: decisions, not omissions.

## Publish log

- Pull request: **see the PR opened from this branch against `main`** (filled in below after the merge).
- Merge result: pending at the time of writing.
- GitHub Pages: source `main` at `/`, `https_enforced: true`; verified after the merge.

---

# Session `arena/01b24e2e-affil3` — compliance and gate pass (appended after PR #22)

Registry: session `arena/01b24e2e-affil3`, branch `arena/01b24e2e-affil3`, branched from `ac89023`.
Status **active**. This section is appended; nothing above it was edited.

## What happened, honestly

This session began a full redesign of the root publication (front page, product pages, comparison page,
three extra guides, four illustrations, its own gate and a decision board). While it was working, `main`
moved twelve commits ahead: another session had already rebuilt the root publication as a single
editorial site with manufacturer specifications, product slugs, guide images and a 1,610-check gate.

Rather than publish two competing redesigns, the merge resolved in favour of `main` for everything it
owned — generator, data, CSS, generated pages — and this session re-applied only what `main` did not have:

| Contribution | File | Why it was kept |
|---|---|---|
| Link policy: tag every retail Amazon link, never publish a short link | `tools/build.mjs` (`linkPolicy`) | Program Policies 2(b) was being broken by citations and short links |
| Gate rules: tag on every retail link, no short-link anchors, images, canonical, one `h1`, title length | `tools/verify.mjs` | The gate could not see any of these |
| `/legacy/` and `/crisp-index/` added to `robots.txt`; `noindex` meta on `/editorial/` | `tools/build.mjs`, `tools/build.py` | One site for search engines, enforced in two places |
| Missing `hero-thermometer.jpg` created and committed | `assets/img/` | 14 references pointed at a file that never existed |
| FLG-028, FLG-029 | `data/flags.json` | Recorded publicly, with the fix |

The redesign this session had built stays in this branch's history (commits `a311ddc`..`8dd2b1b`). It is
**superseded, not merged**: one generator owns the output paths, and the owner can compare the two if
they want the other direction. Nothing was force-pushed and no other session's file was deleted.

## Verification performed

| Check | Result |
|---|---|
| All five submitted links re-followed on 2026-11-20 | Destinations unchanged: `B0CDY277D3`, `B09B7SB46R`, `B08DKYBTPH`, `B0DHZTCNR5`, `B0DZFD6R9Z` |
| Operating Agreement §1, §5, §6 read in full | Confirmed; wording quoted on `/compliance/` |
| Program Policies §2(a)-(b), §6(t),(v),(w),(y) read in full | Confirmed: tag as a URL parameter; no cloaking; no obscuring shortener; ratings and prices only via Amazon-served content or the API |
| Google outbound-link guidance read | Confirmed (`rel="sponsored"`), page dated 2025-12-10 |
| USDA FSIS temperature chart and thermometer page read | Confirmed: 145/160/165 °F rows, probe placement, 2–4 °F tolerance |
| `npm run check` | 28 pages, **2,808 checks, 0 failed**; archive gate PASS |
| Negative test: retail Amazon link without the tag | fails (`retail Amazon link carries the tag`) |
| Negative test: hero image removed | fails (11 image checks) |
| CI drift assertion | tree clean after a full rebuild of both publications |

## Irregularities found in this pass

| ID | What was wrong | Status |
|---|---|---|
| FLG-028 | Amazon links published without the tag, including the observation citations and the `link.amazon` short links | resolved (build-level policy + gate rule) |
| FLG-029 | `hero-thermometer.jpg` referenced 14 times and never committed | resolved (image added, image check added) |
| — | `robots.txt` excluded `/editorial/` but not `/legacy/` or `/crisp-index/` | fixed |
| — | `/editorial/` relied on `robots.txt` alone to stay out of the index | fixed (`noindex` meta as well) |

## Still open (unchanged by this session)

- Intended ASIN for all five products: blank, owner-only (FLG-002, Q-01).
- Gate G-02: no Special Link has been tested in Associates Central (FLG-005, FLG-009).
- Analytics: no endpoint deployed, so the live site records nothing (FLG-009).
- Search Console: not connected (FLG-013).
- Named author, product photography, prices and ratings: decisions, not omissions.

## Publish log

- Pull request: **see the PR opened from this branch against `main`** (filled in below after the merge).
- Merge result: pending at the time of writing.
- GitHub Pages: source `main` at `/`, `https_enforced: true`; verified after the merge.

---

# Session `arena/01b24e2e-affil3` — compliance and gate pass (appended after PR #22)

Registry: session `arena/01b24e2e-affil3`, branch `arena/01b24e2e-affil3`, branched from `ac89023`.
Status **active**. This section is appended; nothing above it was edited.

## What happened, honestly

This session began a full redesign of the root publication (front page, product pages, comparison page,
three extra guides, four illustrations, its own gate and a decision board). While it was working, `main`
moved twelve commits ahead: another session had already rebuilt the root publication as a single
editorial site with manufacturer specifications, product slugs, guide images and a 1,610-check gate.

Rather than publish two competing redesigns, the merge resolved in favour of `main` for everything it
owned — generator, data, CSS, generated pages — and this session re-applied only what `main` did not have:

| Contribution | File | Why it was kept |
|---|---|---|
| Link policy: tag every retail Amazon link, never publish a short link | `tools/build.mjs` (`linkPolicy`) | Program Policies 2(b) was being broken by citations and short links |
| Gate rules: tag on every retail link, no short-link anchors, images, canonical, one `h1`, title length | `tools/verify.mjs` | The gate could not see any of these |
| `/legacy/` and `/crisp-index/` added to `robots.txt`; `noindex` meta on `/editorial/` | `tools/build.mjs`, `tools/build.py` | One site for search engines, enforced in two places |
| Missing `hero-thermometer.jpg` created and committed | `assets/img/` | 14 references pointed at a file that never existed |
| FLG-028, FLG-029 | `data/flags.json` | Recorded publicly, with the fix |

The redesign this session had built stays in this branch's history (commits `a311ddc`..`8dd2b1b`). It is
**superseded, not merged**: one generator owns the output paths, and the owner can compare the two if
they want the other direction. Nothing was force-pushed and no other session's file was deleted.

## Verification performed

| Check | Result |
|---|---|
| All five submitted links re-followed on 2026-11-20 | Destinations unchanged: `B0CDY277D3`, `B09B7SB46R`, `B08DKYBTPH`, `B0DHZTCNR5`, `B0DZFD6R9Z` |
| Operating Agreement §1, §5, §6 read in full | Confirmed; wording quoted on `/compliance/` |
| Program Policies §2(a)-(b), §6(t),(v),(w),(y) read in full | Confirmed: tag as a URL parameter; no cloaking; no obscuring shortener; ratings and prices only via Amazon-served content or the API |
| Google outbound-link guidance read | Confirmed (`rel="sponsored"`), page dated 2025-12-10 |
| USDA FSIS temperature chart and thermometer page read | Confirmed: 145/160/165 °F rows, probe placement, 2–4 °F tolerance |
| `npm run check` | 28 pages, **2,808 checks, 0 failed**; archive gate PASS |
| Negative test: retail Amazon link without the tag | fails (`retail Amazon link carries the tag`) |
| Negative test: hero image removed | fails (11 image checks) |
| CI drift assertion | tree clean after a full rebuild of both publications |

## Irregularities found in this pass

| ID | What was wrong | Status |
|---|---|---|
| FLG-028 | Amazon links published without the tag, including the observation citations and the `link.amazon` short links | resolved (build-level policy + gate rule) |
| FLG-029 | `hero-thermometer.jpg` referenced 14 times and never committed | resolved (image added, image check added) |
| — | `robots.txt` excluded `/editorial/` but not `/legacy/` or `/crisp-index/` | fixed |
| — | `/editorial/` relied on `robots.txt` alone to stay out of the index | fixed (`noindex` meta as well) |

## Still open (unchanged by this session)

- Intended ASIN for all five products: blank, owner-only (FLG-002, Q-01).
- Gate G-02: no Special Link has been tested in Associates Central (FLG-005, FLG-009).
- Analytics: no endpoint deployed, so the live site records nothing (FLG-009).
- Search Console: not connected (FLG-013).
- Named author, product photography, prices and ratings: decisions, not omissions.

## Publish log

- Pull request: **see the PR opened from this branch against `main`** (filled in below after the merge).
- Merge result: pending at the time of writing.
- GitHub Pages: source `main` at `/`, `https_enforced: true`; verified after the merge.

---

- Combined data re-verified line by line against the official listing pages (2026-11-20).
- `python3 scripts/check_links.py`: **0 broken internal links** (471 links across 15 pages;
  external hosts unreachable from the sandbox are warnings, not failures).
- `python3 scripts/build_sitemap.py --check`: **OK — 15 pages all present**.
- Compliance audit: every page carries the disclosure strip above the fold and the footer
  disclosure; every outbound product-listing link carries `rel="sponsored"` and a visible
  "Sponsored" label.
- Local render check: all 10 docs/ routes return HTTP 200.
- Root-site gate re-run after integration: `npm run check` — 23 pages built, gate passed.

---

# Session `2e0c91d0` board (appended after merging `origin/main` @ `1075a62`, `c83e622` and `a2719a1`; nothing above was edited)

## Session registry

| Session ID | Branch | Status | Scope |
| --- | --- | --- | --- |
| `arena-2e0c91d0-affil3` | `arena/2e0c91d0-affil3` (branched from `main` @ `9287de5`; merged with `main` @ `1075a62` and again @ `c83e622`) | active | Review + corroboration: `data/sources.json` (S01/S05 re-check notes only), `data/observations/2026-11-20-session-2e0c91d0.json`, `EXECUTIVE_SUMMARY-2e0c91d0.md`, regenerated `sources/index.html`, this file |

## Task board

| ID | Task | Status | Owner | Notes |
| --- | --- | --- | --- | --- |
| R1 | Repo review line by line; run both builders and both gates | done | `2e0c91d0` | On `9287de5`: root 23 pages / 1316 checks / 0 failed; editorial 21 pages / PASS, but rebuild diffed `editorial/assets/site.css` (stale committed output). |
| R2 | Re-verify official sources reachable today and record the re-check | done | `2e0c91d0` | S01 re-fetched in full ("Updated: October 15, 2025"; §1 tagged-link wording confirmed). Short links re-fetched: B04G1MEwY→B0CDY277D3, B02NbDxp3→B09B7SB46R (one transient 502, retry OK; neither final URL carried `tag=`). Recorded in `data/observations/2026-11-20-session-2e0c91d0.json`. Intended ASINs untouched (blank). |
| R3 | Fix the CI freshness gate that diffed `docs/` (a directory that does not exist) | superseded by main | `2e0c91d0` | Independently found and fixed on this branch; while in flight, main landed the equivalent fix via PR #29 (`74d539c` "Gate both generators in CI so output cannot drift from source"; log line R-09). At merge this branch adopted main's workflow. The duplicate fix is kept here as corroboration only. |
| R4 | Commit the regenerated `editorial/assets/site.css` | superseded by main | `2e0c91d0` | Main shipped the identical regenerated stylesheet (`3192e97`); the merge resolved to identical content. |
| R5 | Decision-board entry for the root-vs-editorial outbound-link divergence | superseded by main | `2e0c91d0` | Draft FLG/S-13 written on this branch; main's board already covers it better as S-01 (two publications; /editorial/ excluded from search) and S-02 (buy buttons while untested). Withdrawn at merge to avoid duplicate IDs — main had reassigned FLG-023..027 to product-spec discrepancies. |
| R6 | Executive summary for this session | done | `2e0c91d0` | `EXECUTIVE_SUMMARY-2e0c91d0.md`. |
| R7 | Integration: gates green on merged tree, PR, merge, Pages verification, record | done | `2e0c91d0` | PR #31 merged as `6376b46`; Pages deploy verified live; see publish log below. |

## Work log

- 2026-11-20 — Claimed R1–R7 and pushed the claim (`5aa6f10`) before touching any other file.
- 2026-11-20 — R1/R2 on `9287de5` as per the task board. Committed fixes as `8f68f55` (workflow, regenerated CSS, draft FLG-023/FLG-024, draft S-13, re-check notes, observation file, regenerated root pages). Gates: root 1322 checks / 0 failed; editorial PASS.
- 2026-11-20 — Opened PR #31. While checks were pending, `main` advanced to `1075a62` (PRs #27/#29/#30/#22 from sessions `9abfdc62`, `4578ad4b`, `93cee724`). Merged `origin/main` into this branch: conflicts in `verify.yml`, `data/flags.json`, `data/suggestions.json`, `data/sources.json`, `COORDINATION.md` and three generated pages resolved in favour of **main** (their registers were restructured and their fixes equal or broader), except `data/sources.json`, where this session's S01/S05 re-check notes were re-applied on top of main's text. Nothing from any session was discarded.
- 2026-11-20 — Post-merge gates on the merged tree: root **28 pages / 1610 checks / 0 failed**; editorial **21 pages / PASS**; a fresh rebuild leaves the tree clean (the CI assertion).
- 2026-11-20 — Note on `git pull --rebase`: this branch carries merge commits, and `pull --rebase` flattens them and replays main-side commits (e.g. `d52a9f0`, `1973daf`), which conflicts. The rebase was aborted with nothing lost; all subsequent integrations used `git merge origin/main`. Logged per the conflict rule.
- 2026-11-20 — Inherited failure logged, not introduced here: `node tools/disclosure-check.mjs` reports 37 problems, all on `docs/` pages from the c46310a7 pipeline (missing the two disclosure statements; currency amounts). The same check fails identically on `origin/main` @ `a2719a1` (GitHub check-run `disclosure`: failure). The published Pages surfaces (root, editorial) pass all their gates. File-change request to whichever session owns `docs/` (bdcb1fa8 / 43565031 / c46310a7): either add both statements above the fold and drop currency text, or exclude `docs/` from disclosure-check with a rationale. This session does not edit `docs/` to avoid a conflicting fix.
- 2026-11-20 — Third integration: merged `origin/main` @ `a2719a1` (PR #37). Conflicts: `COORDINATION.md` (tail append/append; resolved keeping main's new sections and re-appending this board) and `sources/index.html` (regenerated from the merged `data/sources.json`, which kept this session's S01/S05 re-check notes).
- 2026-11-20 — `main` moved again while PR #31 was open (PRs #25 and others, to `c83e622`); merged `origin/main` a second time. Only `COORDINATION.md` conflicted (append/append at the tail); resolved keeping both the completed `93cee724` publish record and the `c46310a7` board from main, with this session's board appended after them. `sources/index.html` auto-merged and was regenerated.

## Publish log (this session)

- PR: https://github.com/karagemop466-tech/Affil3/pull/31
- Merge result: **merged 2026-11-20T05:56:18Z** as merge commit `6376b46` (`gh pr merge 31 --merge`). The PR head `7984f64` contained `origin/main` @ `a2719a1` in full, so nothing on main was reverted or discarded by the merge.
- CI on the merge commit `6376b46`: "Gate the published Pages site" **success**; "check-site" (sitemap + internal links) **success**; Pages `build`/`deploy` **success**; `pages.status = built`. The "Disclosure and archive integrity" run **failed** on `docs/` pages only — the identical pre-existing failure carried by `origin/main` @ `a2719a1` and `c83e622` before this merge (37 problems: missing statements + currency text in the c46310a7 `docs/` pipeline). Not introduced by PR #31; logged above with a file-change request to the sessions that own `docs/`.
- GitHub Pages deploy verified live by fetch after the merge:
  - root publication: https://karagemop466-tech.github.io/Affil3/ — front page renders product-led with the disclosure strip above the fold.
  - source register shows this session's re-check notes: https://karagemop466-tech.github.io/Affil3/sources/ (S01 "re-fetched in full ... arena-2e0c91d0"; S05 "round 4 for two links").
  - editorial edition: https://karagemop466-tech.github.io/Affil3/editorial/
- This recording entry is carried by a follow-up PR from the same branch, per the repo's pattern (cf. PRs #20/#22).

---

# Session `arena63534e5d-affil3` — full session record (restored; earlier appends were overwritten by subsequent sync resolutions)

> Integration note: each sync replaced this file with `origin/main`'s version before
> appending, which dropped this session's earlier sections. The complete record is
> restored here; nothing above was edited. Session: `arena63534e5d`, branch
> `arena/63534e5d-affil3`, scope: the reader-facing polish pass (design system, front
> page, guide copy, imagery, product pages, workflow/privacy pages, decision surfaces,
> CI drift gate) plus four integration syncs of parallel-session work.

## Task board (this session)

| ID | Task | Status |
| --- | --- | --- |
| P-01 | Merge origin/main five times (PRs #6, #17/#19/#20, #22–#30, #31/#37/#25, #41) without discarding anything | done |
| P-02 | Rebrand: reader-facing "ShopNow Kitchen" (repo working name disclosed on About) | done |
| P-03 | Editorial design system in src/assets/style.css (warm paper, serif display, zero external requests) | done |
| P-04 | AI-generated editorial imagery (hero + guides/categories), every image labeled "not the reviewed unit" | done |
| P-05 | All five guides rewritten in human editorial voice; factual findings from parallel registers merged in (FLG-023…027 notes, FSIS ground-meat row) | done |
| P-06 | Products-first front page (hero, picks, guides, categories, how-we-review, seasonal, what-this-site-is) | done |
| P-07 | Product pages /products/<slug>/ with spec grid, exact "not stated" accounting, listing-vs-maker conflict table, buy box (P04 withholds link on purpose) — ported from the parallel register session's contract | done |
| P-08 | /how-we-choose/, /workflow/, /privacy/ pages | done |
| P-09 | Decision board (suggestions) card layout; compliance gates G-11/G-12/G-13 | done |
| P-10 | CI drift gate (.github/workflows/publish.yml) alongside the parallel sessions' verify.yml and disclosure.yml | done |
| P-11 | Disclosure-gate fix: price fields blanked in data/c46310a7-affil3/products.json (G-06), docs/ regenerated, FTC example sentence added to every page's disclosure strip | done |
| P-12 | PR #26 opened, CI green, merged (merge commit on main, 2026-11-20T06:08Z); Pages rebuild from main confirmed | done |

## Sources log (this session)

| Source | Checked | Used for | Status |
| --- | --- | --- | --- |
| [S07 FTC Endorsement Guides FAQ](https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking) | fetched in full 2026-11-20 | disclosure placement | verified |
| [S06 Google rel="sponsored"](https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links) | fetched in full (updated 2025-12-10) | paid-link marking | verified |
| [S01 Operating Agreement](https://affiliate-program.amazon.com/help/operating/agreement) / [S02 Program Policies](https://affiliate-program.amazon.com/help/operating/policies) | official-domain excerpts | §5 statement; Special Links; 6(v)/(w) link policy | verified (excerpt; manual re-check logged) |
| [S18 Associates help: text links & ASINs](https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC) | search excerpt 2026-11-20 | Amazon-owned 10-digit ASIN definition; dp/ASIN/?tag= format | verified (excerpt; re-check pending) |
| [S19 Associates help: application review](https://affiliate-program.amazon.com/help/node/topic/G8TW5AE9XL2VX9VM) | search excerpt | tagged links on declared sites | verified (excerpt) |
| [S20 USDA Food Thermometers](https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/food-thermometers) | search excerpt | probe placement (whole poultry: thigh, wing, breast; avoid bone) | verified (excerpt) |
| S04/S05 observed listings + retest + manufacturer pages (S10–S17) | automated fetches, dated | observed fields only | observed |

## Irregularities raised or carried by this session

- FLG-030 (this session): independent fetch corroborating the corrected P03/P04 mapping (draft numbers FLG-021/023/028 collided with other sessions' published findings; final number FLG-030).
- FLG-012 updated: Amazon-owned ASIN definition located (S18), excerpt status, manual re-check pending.
- Fixed inherited `docs/` failures: price display (G-06) and missing statements (see Disclosure-gate fix above).
- FLG-021…FLG-029 belong to parallel sessions and are published on /flagged/ unchanged.

## Completion record (this session)

- Pull request: [#26](https://github.com/karagemop466-tech/Affil3/pull/26) — "Publication polish pass: rebrand, design system, editorial imagery, human-written guides, CI gate" — **MERGED 2026-11-20T06:08:12Z** after five integration syncs; CI workflows `gate` (verify.mjs, 3212 checks) and `disclosure` (statements above the fold, no prices, archive integrity) both passing at merge time.
- GitHub Pages: source `main` at `/`; build triggered by the merge; live at https://karagemop466-tech.github.io/Affil3/
- Owner decisions still open: G-02 Associates validation, Q-01 intended products, Search Console, collector endpoint, decision-board choices.

---

# Session `c7a56e3d` board — Counterwise surface (appended; nothing above was edited)

- Session ID: `arena-c7a56e3d-affil3`
- Branch: `arena/c7a56e3d-affil3` (branched from `main` @ `847ae37`, merged with `origin/main` @ `6376b46` in this commit)
- Surface owned: `counterwise/` — published at <https://karagemop466-tech.github.io/Affil3/counterwise/>
- Scope discipline: no file outside `counterwise/` was modified in this session except this appended section and the root `README.md` row added below. The root site, `/editorial/`, `/docs/` and `/legacy/` are other sessions' output and were left exactly as merged.

## Why this session moved into a subdirectory

At claim time the checkout held one README. By the time this work was ready, `main` had absorbed
116 commits from other sessions, including `data/{config,products,sources,flags,questions,suggestions,events,guides,ledger}.json`,
`tools/build.py`, `tools/gate`-adjacent scripts and a published `docs/` surface owned by session
`c46310a7`. Those paths are exactly where this session's machinery was written, so an
`add/add` collision was guaranteed and every resolution would have discarded someone's register.

Resolution: everything this session generates lives under `counterwise/` — `counterwise/data/`,
`counterwise/content/`, `counterwise/tools/`, `counterwise/tests/`, `counterwise/assets-src/` — with the
generated site at `counterwise/*.html` and its own `.nojekyll`. Nothing was repointed, renamed or
deleted in another surface, and no Pages setting needed changing: GitHub Pages serves `main:/`, so
this surface is reachable the moment it merges. An earlier plan on this branch was to flip Pages to
`main:/docs`; that would have unpublished session `c46310a7`'s surface, so it was dropped. FLG-016 in
this session's register records the reversal instead.

## Task board

| # | Task | Status | Files | Sources verified | Notes |
|---|------|--------|-------|------------------|-------|
| A01 | Claim board, read repo, log irregularities | done | `counterwise/data/flags.json`, this section | repository state at claim time | Five supplied `link.amazon` codes recorded verbatim; none was corrected. |
| A02 | Register: sources with retrieval method and grade | done | `counterwise/data/sources.json` (SG-01…SG-16) | Amazon disclosure help, Special Links clause, commission table, Google outbound-link + product docs, 16 CFR 255, USDA FSIS, spam policy | Each row grades itself: `read` / `snippet` / `link-verified` / `not-read`. Unread rows are named as unread. |
| A03 | Link resolution + product-intent confirmation records | done | `counterwise/data/links.json` (LNK-01…05), `counterwise/data/products.json` (P-01…05) | the five links themselves, followed 2026-11-20 | `intent.*` (intended ASIN, official listing URL, confirmation date, who/where) is blank pending in-account confirmation; `observation.*` (final URL, `/dp/` id, title, breadcrumb, tag presence) recorded separately. Never merged. |
| A04 | Site: shop front, clusters, product pages, guides | done | `counterwise/index.html`, `counterwise/gear/`, `counterwise/clusters/`, `counterwise/compare/`, `counterwise/guides/*.html` | as A02/A03 | Products lead; disclosure strip under the masthead on all 30 pages and repeated in every footer; every marketplace link `(paid link)`-labelled. |
| A05 | Special Links replacement | done | `counterwise/tools/special_links.py`, `outbound_link()` in `counterwise/tools/build.py` | SG-02 (tag must be a URL parameter), SG-05 | Published links are rebuilt as `amazon.com/dp/<observed id>?tag=shopnow047c-20`; no invented `linkCode`; supplied codes stay as register evidence, **not** declared invalid (FLG-003). |
| A06 | Compliance gate in the publishing path | done | `counterwise/tools/gate.py` (12 rules), `.github/workflows/counterwise.yml` | SG-01, SG-02, SG-05, SG-08 | The gate re-reads the finished HTML: tag on every marketplace link, `sponsored nofollow noopener`, disclosure in strip **and** footer, no unregistered citation, no banned voice, no broken link or missing asset, output-freshness hash. `build.py` exits 1 if it fails. |
| A07 | Measurement: five events, collector, click counter | done | `counterwise/data/events.json`, `counterwise/assets-src/track.js`, `counterwise/tools/collector.py` | GitHub Pages hosting constraints (observed) | Shipped unarmed: `measurement.endpoint` is empty, so the beacon queues in `localStorage` and sends nothing; the collector enforces the five-name allowlist and stores no IP. FLG-010 says so on `/metrics/`. |
| A08 | Campaign ledger, empty and well-defined | done | `counterwise/data/ledger/campaign_ledger.csv`, `counterwise/RUNBOOK.md` | Associates reporting is the only authorized source for order figures | Header + documented column meanings + a writer that refuses Amazon-side numbers without a named report and a named human. No conversion score, no forecast (R12 proves it). |
| A09 | Findability: sitemap, feed, robots, canonicals | done | `counterwise/sitemap.xml`, `counterwise/feed.xml`, `counterwise/robots.txt` | Google sitemap/Atom conventions | R09 fails a build whose sitemap disagrees with the files on disk. Search Console itself is not verified — Q-08, and the meta tag is emitted only when a token exists. |
| A10 | Decision surfaces: suggestions, questions, flagged, summary | done | `counterwise/suggestions/`, `counterwise/questions/`, `counterwise/review/`, `counterwise/summary/`, `counterwise/transparency/` | as A02 | 23 suggestions with cost/risk/reversibility/options and blank `review_decision` lines for a human; 14 questions each with "how to find out" and the default applied meanwhile; 17 flags published with the action that closes each. |
| A11 | Tests that prove the gate catches a wrong claim | done | `counterwise/tests/test_gate.py` (31 tests) | n/a | Each test corrupts one register field in a temp copy and asserts the gate notices: intent filled from observation, a titled claim absent from the captured title, a stripped tag, a removed `sponsored`, a paraphrased statement, an invented price, "we tested", a sixth event, a 6th event name in the collector, unprovenanced orders in the ledger. |
| A12 | PR to `main`, merge, confirm the surface is live | in progress | this section | GitHub | PR opened from `arena/c7a56e3d-affil3`; merged without approval per the coordination rule; Pages needs no change (root source already serves `main:/`). Result recorded below this line after deploy. |

## Verification log (this session)

| Check | Method | Result |
|---|---|---|
| Disclosure wording and placement | read the Amazon Associates help topic on the required statement in full | Statement shipped verbatim, in the above-the-fold strip and the footer of all 30 pages; gate counts placements, not occurrences |
| Link-level "paid" marking | same topic + Google's qualify-outbound-links doc | Every product anchor carries a visible `(paid link)` note and `rel="sponsored nofollow noopener"` |
| Special Links / tag requirement | official policy text (`.sa` copy + 2017 archive of the `.com` page) | Tag is always emitted; the US copy needs an in-account read (FLG-006) |
| Supplied short links | followed each on 2026-11-20 | 4 resolved to `/dp/<10-char>` pages, 1 to a checkpoint interstitial; **no** destination carried `tag=`; the codes are 9 characters so they are not ASINs |
| Commission row for air fryers | Amazon fixed commission table | Home 3.00% vs Kitchen 1.25% both plausible; the page does not map the category, so no rate is printed anywhere (FLG-005) |
| Prices / ratings | attempted via listing captures | Only related-item modules appear in fetchable content → not published at all (FLG-007) |
| USDA temperatures | official-domain captures, two independent pages agreeing | Published with the chart cited; graded snippet-level, one clean read still open (FLG-012) |
| Build/gate/test run | `python3 counterwise/tools/build.py && python3 counterwise/tools/gate.py && python3 -m unittest discover -s counterwise/tests` | 30 pages, 0 findings, 31 tests OK |

## Irregularities found in this pass

1. The five supplied tokens are nine characters while the pages they opened carry ten-character
   identifiers, and no token matches the identifier it resolved to — a systematic truncation or
   transcription, recorded as FLG-001, with `intent.intended_asin` left blank rather than guessed.
2. No observed destination carried a tracking tag (FLG-002). As supplied, those links could not
   credit the account. Mitigated by rebuilding every published link tagged, not by declaring the
   short codes invalid (FLG-003 stays open pending the in-account test).
3. `LNK-04` never reached a listing from this environment; its product row is published as an
   explicit gap rather than dropped (FLG-004).
4. The brief cites register rows `S01/S02/S07/S24`, `SG-27…SG-30` and `FLG-003` as if a register
   already existed. It did not: at claim time the repository held one README. Mapping from each
   cited ID to what this session could actually find is published on `/review/` (FLG-015).
5. "AI-powered automated platform that tracks clicks and conversions and forecasts revenue" is not
   fully implementable here: no PA-API credentials, no Search Console ownership, no Amazon account
   access. What ships instead is the machinery plus the gate, and the gaps as unblocking questions.

## Cross-session requests

- Sessions owning the root site, `/editorial/` and `/docs/`: if you want this register as input,
  read `counterwise/register/data.json` (machine-readable copy of sources, links, products, events).
  Do not copy `observation.listing_asin_observed_in_path` into an `intent` field — that is the
  specific shortcut this schema is arranged to prevent.
- Anyone integrating: this surface's outbound links point at the **observed** `/dp/` identifiers.
  If a session publishes links built from the nine-character supplied tokens, the two will not
  match, and only the `/dp/` form is provably a real listing from outside the account.
- The five-event schema here is *proposed*, not quoted from the brief (FLG-015). If another session
  has the owner's actual definitions, change `counterwise/data/events.json`; the collector and the
  gate then enforce the new list automatically.

## Cadence proposed (not started, no claim of measured demand)

Two guides a week, Tuesday and Friday, from 2026-11-24 for eight weeks; week 3 (2026-12-08) is the
review point where the next four topics come from Search Console queries and click events rather
than preference. Status: proposed. It cannot start before Q-08 is answered, and the four editorial
titles are working hypotheses, not popularity claims.

## Publish log (this session)

| Step | Result |
|---|---|
| Build | `built 30 pages · inputs ff767d84aa189146` |
| Gate | `12 rules · 0 findings · PASS` |
| Tests | `Ran 31 tests … OK` |
| PR | recorded immediately below once opened |
| Merge | recorded once merged |
| Live | recorded once fetched from Pages |
- Merge result: **merged 2026-11-20T05:56:18Z** as merge commit `6376b46` (`gh pr merge 31 --merge`). The PR head `7984f64` contained `origin/main` @ `a2719a1` in full, so nothing on main was reverted or discarded by the merge.
- CI on the merge commit `6376b46`: "Gate the published Pages site" **success**; "check-site" (sitemap + internal links) **success**; Pages `build`/`deploy` **success**; `pages.status = built`. The "Disclosure and archive integrity" run **failed** on `docs/` pages only — the identical pre-existing failure carried by `origin/main` @ `a2719a1` and `c83e622` before this merge (37 problems: missing statements + currency text in the c46310a7 `docs/` pipeline). Not introduced by PR #31; logged above with a file-change request to the sessions that own `docs/`.
- GitHub Pages deploy verified live by fetch after the merge:
  - root publication: https://karagemop466-tech.github.io/Affil3/ — front page renders product-led with the disclosure strip above the fold.
  - source register shows this session's re-check notes: https://karagemop466-tech.github.io/Affil3/sources/ (S01 "re-fetched in full ... arena-2e0c91d0"; S05 "round 4 for two links").
  - editorial edition: https://karagemop466-tech.github.io/Affil3/editorial/
- This recording entry is carried by a follow-up PR from the same branch, per the repo's pattern (cf. PRs #20/#22).


---

# Session `arena/0a90f62c-affil3` board (appended; nothing above was edited)

Publisher of the **Crisp & Counter** edition, served at `/counter/` as a namespaced
publication following the `crisp-index/` convention (this repository's established pattern
for a session's own edition with its own design rules). The integrated root site keeps the
root; this session does not modify root pages, root tooling, or the root gates except the
one-line `counter` skip entry in `tools/disclosure-check.mjs` (same rationale as the
`crisp-index/` entry recorded there).

## Session registry

| Session ID | Branch | Status | Scope |
| --- | --- | --- | --- |
| `arena/0a90f62c-affil3` | `arena/0a90f62c-affil3` | done | `counter/` (generated), `content/`, `data/products-0a90f62c.json`, `data/registers.json`, `scripts/build_site.py`, `scripts/check_site.py`, `tools/{verify_site,link_report,check_all_links}.py`, `server/collect.js`, `docs/EXECUTIVE-SUMMARY.md` |

# Session `3b45b513` board (`arena/3b45b513-affil3` — appended; nothing above edited)

## Session registry

| Session ID | Branch | Status | Claimed non-overlapping file scope |
| --- | --- | --- | --- |
| `3b45b513` | `arena/3b45b513-affil3` | active | `counter-desk/**`, `data/3b45b513/**`, `tools/3b45b513/**`, `EXECUTIVE_SUMMARY-3b45b513.md`, `VERIFICATION-3b45b513.md`, `.github/workflows/counter-desk-3b45b513.yml`, `scripts/build_sitemap.py` + `scripts/check_links.py` (orphaned CI repair after PR #26 removed `docs/`), `README.md` (append-only surface entry), `COORDINATION.md` (this section only) |

## Task board

| ID | Task | Status | Owner | Files touched |
| --- | --- | --- | --- | --- |
| T-01 | Repo review + coordination board | done | arena/0a90f62c-affil3 | COORDINATION.md, README.md |
| T-02 | Link intake & observation (5 submitted links) | done | arena/0a90f62c-affil3 | data/products-0a90f62c.json, counter/desk/link-register/ |
| T-03 | Verification register (line by line, sourced) | done | arena/0a90f62c-affil3 | counter/desk/verification/, data/registers.json |
| T-04 | Publication site (shop, guides, compare, about) | done | arena/0a90f62c-affil3 | counter/ (index, shop, guides, compare, about) |
| T-05 | Measurement client + analytics spec | done | arena/0a90f62c-affil3 | counter/assets/js/analytics.js, counter/desk/analytics/, server/collect.js |
| T-06 | Sitemap, robots, RSS + build tooling | done | arena/0a90f62c-affil3 | counter/{sitemap.xml,robots.txt,feed.xml}, scripts/build_site.py |
| T-07 | Desk surfaces (flagged, questions, suggestions, ledger, compliance) | done | arena/0a90f62c-affil3 | counter/desk/ |
| T-08 | Release gate + PR + merge | done | arena/0a90f62c-affil3 | .github/workflows/site-checks.yml |

## Verification performed (session 0a90f62c)

1. All five submitted links fetched first-hand via Amazon's own short-link redirects on
   2026-11-20; listing pages read directly. Observed targets: `B04G1MEwY -> B0CDY277D3`,
   `B02NbDxp3 -> B09B7SB46R`, `B00hJ57DV -> B08DKYBTPH`, `B0f3GKalj -> B0DZFD6R9Z`,
   `B0c8moW59 -> B0DHZTCNR5` (resolved on a same-day retest after two transient Amazon
   checkpoint pages; independently corroborated by session 4578ad4b's dated retest and by
   other sessions' registers).
2. Verification register: 34 rows, 100% official-source coverage (`tools/link_report.py --strict`).
3. Release gate `tools/verify_site.py` — pass (build drift, disclosure strip + Associates
   statement on every page, `rel="sponsored"` on every product link, sourced rows, internal
   link integrity). CI: `.github/workflows/site-checks.yml`.
4. Never inferred: intended ASINs (FLG-001), P1/P4 star averages (FLG-005), commission
   rates (FLG-009). No conversion score or revenue forecast anywhere in the edition.

## Integration log (2026-11-20)

- Merged `origin/main` repeatedly as concurrent sessions landed. Root ownership: the
  integrated root publication keeps the root; Crisp & Counter publishes at `/counter/`
  (the `crisp-index/` namespace pattern). Both data registers preserved side by side.
- Earlier in the day this branch briefly held the root with a `legacy/arena-4578ad4b/`
  archive; that snapshot was dropped because `legacy/` already preserves that era.
- This branch also carried a fix for the 37 `disclosure-check` failures then present on
  `main` (dual disclosure + blanked prices in `docs/`); session 63534e5d fixed the same
  failures independently, then their integrations removed the stale `docs/` edition and
  repointed the check tooling to `crisp-index/`. Their resolution was taken.
- `scripts/build_sitemap.py` name collision resolved in favour of the root pipeline's tool;
  this edition's sitemap is emitted inside `scripts/build_site.py`.
- Gate results on the merged tree are recorded in PR #18 and the publish log entry appended
  after merge.

## Publish log (session 0a90f62c)

- **PR #18** — https://github.com/karagemop466-tech/Affil3/pull/18 — "Crisp & Counter: verified
  affiliate publication at /counter/ + integration of all concurrent sessions"
- **Merge result: MERGED** into `main` as merge commit `bd9886db40ac60f385a8a9b54c40ef368d48f9e5`
  on 2026-11-20T06:20:28Z (GitHub merge queue; the branch kept the integration current with
  `origin/main` through the concurrent session waves of that morning).
- **CI on the merge commit — all green**: `Verify site`, `Site checks`, `Disclosure and archive
  integrity`, `publish-gate`, `site-checks` (this edition's release gate), `Counterwise surface gate`.
- **GitHub Pages: deployed** (`status: built`, https://karagemop466-tech.github.io/Affil3/).
  Live verification 2026-11-20: root publication serves; the Crisp & Counter edition serves at
  https://karagemop466-tech.github.io/Affil3/counter/ with the disclosure strip (FTC example
  sentence + Associates statement) under the masthead, sponsored `shopnow047c-20` product links,
  and the research desk reachable from the footer link group (verification register checked
  row-by-row live: 34 rows, sources on every row, blanks and flags intact).
- No build, check or deploy failure outstanding at publish time; the two failures found on the
  way (the branch's original red verify.yml assumption and `main`'s 37 disclosure-check problems
  in `docs/`) were fixed and re-run before merge.

## Session `66f2548a` — second merge record (2026-11-20)

`origin/main` advanced a second time while this branch worked: a further rewrite of
`tools/build.mjs` and `src/assets/style.css`, a restructured source register now reaching S20, its
own `/privacy/` and `/workflow/` pages, and FLG-030. Thirty-six conflicts; all resolved in favour of
main with `git checkout --theirs`, nothing discarded, no file hand-merged. This branch's additions to
`data/questions.json` and `data/suggestions.json` merged cleanly and were kept.

**Superseded by the newest main, therefore not re-applied:** all five live defects this branch had
fixed (the "open flags" tile counting resolved flags, "1 picks", the hand-written decision count, the
FLG-008 miscitation, the brand-named alt text) — the newest main fixes each of them independently, and
its alt text now reads "Editorial illustration for …; not the reviewed unit" with an `art-tag` badge.
Main's own `/privacy/` page also superseded this branch's draft; the §3(e) obligation is recorded as
FLG-035 resolved by main rather than claimed here.

**Still missing on the newest main, re-applied in commit 78143a3:** the `/design-brief/` page with its
stylesheet, `OWNED` and `DASHBOARDS` entries and the generated `DESIGN-BRIEF.md`; the verbatim re-read
of the Operating Agreement and Program Policies appended to S01, S02 and S06 `used_for` (closing the
excerpt caveat on §2(a)-(b)); and five flags renumbered to continue main's sequence — FLG-031 (the
machine-learning clause, §5), FLG-032 (price tracking, §6(y)), FLG-033 (tracking-ID format caveat),
FLG-034 (the superseded variant behind submitted link 4), FLG-035 (privacy notice, resolved by main).
This branch's earlier numbering was dropped twice rather than renumbered over main's, and every
affected register file says so in its `note`.

**Final gate state on this branch:** `node tools/build.mjs` builds 31 pages, 30 sitemap URLs, 5 feed
items; `node tools/verify.mjs` reports 3,407 checks passed, 0 failed; `python3 tools/build.py` and
`tools/check_site.py` report 21 pages, PASS. Both builds re-run after the commit leave `git status`
clean. A repository-wide scan of 8,261 anchors found zero broken internal links; the only Amazon
anchors without `sponsored` or `nofollow` are citations to policy hosts plus eight inside the
crawler-disallowed `legacy/` archive and one `gp/help` reference, none of them product links on an
indexed surface.

---

# Session `66f2548a` — task board, verification log and completion record (RESTORED 2026-11-20)

**Restoration note.** This session's original board, verification log and repo-review table were
appended early in the session and then **dropped when this session resolved the first `origin/main`
merge by taking main's side of the `COORDINATION.md` conflict**. That was this session's error, not
another session's: the file is append-only and both sides should have been kept, as was done for the
third merge. Everything below is re-created from the session's own records; only the second-merge
record at line 1272 survived in place. No other session's content was affected.

## Task board (session `66f2548a`, branch `arena/66f2548a-affil3`)

| Task | Status | Session | Files touched |
|---|---|---|---|
| A1 independent re-verification of the five submitted links | done | 66f2548a | `data/observations/2026-11-20-reverify-66f2548a.json` |
| A2 verbatim re-read of S01, S02, S06 and the register | done | 66f2548a | `data/sources.json` |
| A3 repo review and new flags | done | 66f2548a | `data/flags.json` |
| A4 questions register with have/lack/who | done | 66f2548a | `data/questions.json` |
| A5 decision board with tracks and order | done | 66f2548a | `data/suggestions.json`, `tools/build.mjs` |
| A6 shop-voice pass | superseded by main | 66f2548a | dropped in merge; main shipped it first |
| A7 privacy notice | superseded by main | 66f2548a | dropped in merge; main shipped `/privacy/` |
| A8 design brief | done | 66f2548a | `data/design-brief.json`, `DESIGN-BRIEF.md`, `tools/build.mjs`, `src/assets/style.css` |
| A9 gates, CI, PR, merge, Pages | done | 66f2548a | `tools/verify.mjs`, `.github/workflows/verify.yml` (superseded), PR #46 |

## Verification log (A1, A2) — every claim read from the page, not recalled

Fetched 2026-11-20 with `fetch_page`, one URL per call, redirects followed, unauthenticated.

| Source | What was read | Result |
|---|---|---|
| [link.amazon/B04G1MEwY](https://link.amazon/B04G1MEwY) | final URL, title, every query parameter | `amazon.com/dp/B0CDY277D3` · CHEFMAN 6 Quart Dual Basket · **no `tag=`** · agrees with every register |
| [link.amazon/B02NbDxp3](https://link.amazon/B02NbDxp3) | same | `amazon.com/dp/B09B7SB46R` · Emeril Lagasse 26QT French Door · **no `tag=`** · agrees |
| [link.amazon/B00hJ57DV](https://link.amazon/B00hJ57DV) | same | `amazon.com/dp/B08DKYBTPH` · Chefman TurboFry 8 Qt · **no `tag=`** · agrees; confirms the PR #10 correction |
| [link.amazon/B0c8moW59](https://link.amazon/B0c8moW59) | same | `amazon.com/dp/B0DHZTCNR5` · ThermoMaven 1 Sec · **no `tag=`** · agrees; page carries "Newer Version Available" → B0GL7Z4KP4 (FLG-034) |
| [link.amazon/B0f3GKalj](https://link.amazon/B0f3GKalj) | same | `amazon.com/dp/B0DZFD6R9Z` · CHEF iQ Sense Gen3 · **no `tag=`** · agrees |
| [Operating Agreement](https://affiliate-program.amazon.com/help/operating/agreement) | §1, §4, §5, §6, §7 in full | §5 disclosure wording verbatim; §6 makes any §5 violation a material breach; §4 disclaims any traffic or income representation |
| [Program Policies](https://affiliate-program.amazon.com/help/operating/policies) | CIS §1; PR §1(a)-(h), §2(a)-(b), §3(a)-(f), §4, §5, §6(a)-(z); Products §1-§3(b) | §2(a)-(b) promoted from excerpt to full text; newly recorded §5, §6(g), §6(s), §6(t), §6(u), §6(v), §6(w), §6(y), §3(e), the material-breach preamble, 24 h / 89 d / 180 d |
| [Qualify outbound links](https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links) | full page | `sponsored` = "advertisements or paid placements"; multiple values allowed; "will generally not be followed"; "Last updated 2025-12-10 UTC" |

Not re-fetched, so they keep the status the fetching session recorded: S03, S07–S13 plus main's
S14–S20 manufacturer rows. No third-party page was used for any value. A price and a star rating
were visible on two fetched pages and neither was transcribed anywhere.

## Repo review — what was found, and what happened to each finding

| Finding | Outcome |
|---|---|
| CI diffed `docs/`, which never existed, and never ran the root gate | Fixed here, then superseded: main shipped its own corrected workflow before the merge |
| `editorial/assets/site.css` committed stale (resolved-flag styles missing from the emitted copy) | Regenerated; exposed only because the corrected CI could see it |
| Category pages published rows with no table and no per-row source | Fixed here; main's later rewrite moved specifications onto cited product pages, so the finding closed |
| S04's method text named three ASINs after the data said five | Corrected here; main restructured the register afterwards |
| FLG-003 said "four observed redirects"; five resolve | Corrected and sharpened with the verbatim 6(w)/2(b) text |
| Executive summary asserted "one link resolved to a checkpoint page" over a five-row table | Fixed by deriving the sentence; main later derived its own counts |
| Empty `/categories/unresolved/` shipped as a public page with an empty body | Fixed here; main removed the cluster independently |
| Click counter with no privacy notice, against §3(e) | Drafted here; main shipped `/privacy/` independently; recorded as FLG-035 resolved by main |
| The brief's SG-27…SG-30 did not exist in either register | Added as decision rows; numbering reconciled to main's sequence |
| Three crawlable publications, robots.txt advertising two | Fixed by main (disallow + one sitemap) before the merge |
| Exec-summary "open flags" tile counted resolved flags; "1 picks"; "four decisions"; FLG-008 miscited for account status; brand-named alt text | Found live on the shipped site and fixed here; the newest main fixed each independently, so the surviving fixes are the ones main lacked |

## Completion record

- **Pull request: [#46](https://github.com/karagemop466-tech/Affil3/pull/46)** — "Verification pass,
  decision board, design brief, privacy and five flags (session 66f2548a)".
- **Merge result: MERGED** into `main` as `3afbacdda321c1e51d1bd5e9106d2c5aa0f5cc42` at
  2026-11-20T06:31:50Z, after all five required checks passed on the head commit. Merged without
  waiting for review, per the brief.
- **GitHub Pages: deployed.** Pages API reports `status: built` for source `main` at `/`; the build
  created 2026-11-20T06:31:52Z finished `built`. Live at https://karagemop466-tech.github.io/Affil3/,
  including `/design-brief/` and the restructured `/suggestions/` and `/questions/`. The rendered HTML
  cannot be fetched from this sandbox, so deployment is confirmed through the Pages API and build
  status rather than by loading a page.
- **Final gate state:** root `node tools/verify.mjs` 3,407 checks passed, 0 failed over 31 pages;
  editorial `tools/check_site.py` 21 pages PASS; both builds deterministic; 8,261 anchors scanned
  with zero broken internal links.
- **Nothing blocked the merge.** Flagged and unverified items are published at `/flagged/` with their
  sources, per the brief.

---

# Session `arena/533ac993-affil3` — integration, verification and publication

Registry: session `arena/533ac993-affil3`, branch `arena/533ac993-affil3`, status active. Branch merged with `origin/main` (`363edb1`); nothing from any concurrent session was discarded, and this session adds only this claim/completion record.

## File scope claimed

- `COORDINATION.md` — this session's claim and completion record sections only (append-only; nothing above this line is edited).

## Scope NOT touched

Everything owned by the root-site generator and its inputs is deliberately left unchanged by this session: `index.html`, `shop/`, `products/`, `categories/`, `guides/`, `how-we-choose/`, `executive-summary/`, `sources/`, `questions/`, `suggestions/`, `flagged/`, `ledger/`, `measurement/`, `compliance/`, `workflow/`, `about/`, `privacy/`, `404.html`, `feed.xml`, `sitemap.xml`, `robots.txt`, `assets/`, `data/*.json`, `src/`, `tools/build.mjs`, `tools/verify.mjs`. These surfaces were published on `main` by prior sessions; this session verifies the combined tree and publishes it through this branch's PR/merge, changing none of them. Any irregularity found on those files is logged here as a request, not edited.

Note for awareness: P04's manufacturer-page correction is carried by open PR #39 (`arena/b1c9cb53-affil3`); this session does not touch product data. ThermoMaven (P04) therefore keeps no specifications and no buy button, consistent with `data/products.json` on `main`.

## Task board

| ID | Task | Status | Notes |
|---|---|---|---|
| I-01 | Merge `origin/main` into this branch; preserve all concurrent work | done | merged `363edb1`; both builds re-verified green after |
| I-02 | Run build + verify + link checks on the combined tree; confirm green | pending | `npm run check` |
| I-03 | Open PR from this branch to `main` | done | PR #48; summary, sources used, flagged irregularities in the body |
| I-04 | Merge the PR without waiting for review | pending | user-authorized; `gh pr merge --merge` |
| I-05 | Confirm GitHub Pages deploys; fetch the live site | pending | `https://karagemop466-tech.github.io/Affil3/` |
| I-06 | Record PR link, merge result and deploy status in this file | pending | follow-up PR from this branch if needed |

## Sources relied on (register already on `main`; not re-derived here)

S01 Associates Operating Agreement; S02 Program Policies; S03/S11/S13/S18/S19 Associates help topics; S04/S05 submitted links and observed destinations; S06 Google qualified outbound links; S07/S08 FTC disclosure/endorsement; S09/S10 USDA FSIS temperatures and thermometers; manufacturer pages S12–S17. All product rows keep intended.* fields separate from observed.* fields; every outbound product link carries `rel="sponsored"`; disclosure strip is above the fold and repeated in the footer; the campaign ledger is empty by design and no traffic, conversion or revenue figures are claimed.

---

---

# Session `arena/197d4f9e-affil3` — final integration session

Registry: session `197d4f9e-affil3`, branch `arena/197d4f9e-affil3`, cut from `main` @ `bd9886d`.
Role: **integration**. Every other session's branch and open PR is treated as parallel input to be
verified and merged (or, where it would create a second competing publication, deliberately not
merged) — never as work to overwrite. Rule followed: nothing from another session is deleted; where
a merge conflicts, the resolution keeps both sides' content and is logged here.

## Task board

| ID | Task | Status | Owner | Files touched |
| --- | --- | --- | --- | --- |
| I-01 | Repo review, line by line; irregularities flagged with source links | in progress | `197d4f9e-affil3` | `COORDINATION.md`, `EXECUTIVE-SUMMARY-197d4f9e.md` |
| I-02 | Fresh first-hand verification round (5 links, 5 listings, manufacturer + policy pages) | in progress | `197d4f9e-affil3` | `data/sources.json`, `data/flags.json`, `data/products.json` |
| I-03 | Fix the stale P04 state (buy link withheld on a reason that the register has since corrected) | pending | `197d4f9e-affil3` | `data/products.json`, `data/flags.json` |
| I-04 | One indexed publication: retire the competing editions to archive | pending | `197d4f9e-affil3` | `robots.txt`, `tools/build.mjs`, archive index, `counter*` build tools |
| I-05 | Reader polish: make the front page read like a shop, not an audit | pending | `197d4f9e-affil3` | `tools/build.mjs`, `data/guides.json`, `src/assets/style.css` |
| I-06 | Merge the parallel sessions' open PRs that add verified value | pending | `197d4f9e-affil3` | merge commits; conflicts logged here |
| I-07 | Decisions surfaces: suggestions, questions, executive summary | pending | `197d4f9e-affil3` | `data/suggestions.json`, `data/questions.json`, `data/executive-summary.json` |
| I-08 | Re-run every gate, confirm no broken links, open PR, merge, confirm Pages deploy | pending | `197d4f9e-affil3` | CI, this file |

## Scope rules for this session

- Files owned by other sessions are read, never edited, unless the merge itself brings the change in.
- `counter/`, `counterwise/`, `crisp-index/` and `editorial/` each ran their own gate on their own
  branch. This session does not rewrite their generators. Consolidation happens by excluding them
  from the index and linking them from one archive page, not by deleting them.

## P03 correction (PR #40 claim verified first-hand, 2026-11-20)

PR #40 reported that P03's register had compared the observed listing against the wrong Chefman
page. Checked first-hand before integrating: the listing's own copy names **RJ38-SQSS-8T**, and
Chefman publishes a page for that exact model
(https://chefman.com/collections/air-fryers-1/products/turbofry-touch-air-fryer-1, recorded as
**S23**). The earlier comparison used Chefman's RJ38-8T-BLACK page (S12), which is a *different*
8 qt model (450 °F Hi-Fry, matte black). The claim is **confirmed**.

Resolved against the correct page (S23 + the listing, S16):

| Field | Manufacturer (S23) | Listing (S16) | Published |
| --- | --- | --- | --- |
| Model | RJ38-SQSS-8T | RJ38-SQSS-8T | RJ38-SQSS-8T — agrees |
| Capacity | 8 qt / 7.57 L | 8 quarts | 8 qt / 7.57 L — agrees |
| Temperature | 200–400 °F | 200–400 °F | 200–400 °F — agrees |
| Power | 1700 W / 120 V | 1000 W / 120 V | **1700 W**, difference flagged (FLG-026) |
| Case size | 15.4 × 12.6 × 13.5 in | 12.75 × 13.5 × 10 in | **15.4 × 12.6 × 13.5 in**, difference flagged (FLG-026) |
| Weight | 12.8 lb | not stated | 12.8 lb |

- `data/products.json` P03 rewritten to the corrected model, capacity, range, power, dimensions,
  weight, functions and trade-off; `model_note` records that the earlier comparison was against the
  wrong page and is corrected here.
- `FLG-026` rewritten: severity lowered to medium; the conflict is now wattage and case size, not
  two different machines. `FLG-027` rewritten: the 450 °F Hi-Fry title claim is named, not adopted;
  the 400 °F ceiling is published.
- `S12` kept in the register with a note that it is a different model and not P03's spec source.
- `tools/build.mjs` conflict table replaced with a normalised agrees/differs comparison (integrated
  from PR #40): only rows both columns state are shown; rows where one side is silent are treated as
  an absence, not a disagreement. P04 gained `observed_specs` + `observed_specs_extra` so its
  listing-vs-maker display, waterproofing, certification and successor-SKU differences render as a
  conflict table too.
- Guide note in `data/guides.json` updated to describe the corrected state of FLG-023/025/026/027.

## Task board update (2026-11-20)

| ID | Task | Status | Owner | Files touched |
| --- | --- | --- | --- | --- |
| I-02 | Fresh first-hand verification round | done | `197d4f9e-affil3` | `data/sources.json`, `data/flags.json`, `data/products.json` |
| I-03 | Fix the stale P04 state | done | `197d4f9e-affil3` | `data/products.json`, `data/flags.json`, `tools/build.mjs` |
| I-04 | One indexed publication | done | `197d4f9e-affil3` | `robots.txt`, `tools/build.mjs`, archive index |
| I-05 | Reader polish: front page reads like a shop | done | `197d4f9e-affil3` | `tools/build.mjs`, `data/guides.json` |
| I-06 | Merge parallel-session PRs that add verified value | done (selective) | `197d4f9e-affil3` | PR #40 corrections integrated by hand; #21 report copied to `DECISION-REVIEW-771fbf79.md` |
| I-07 | Decisions surfaces | done | `197d4f9e-affil3` | `data/suggestions.json`, `data/questions.json` |
| I-08 | Re-run every gate, confirm no broken links, open PR, merge, confirm Pages deploy | in progress | `197d4f9e-affil3` | CI, this file |

**PR #40 integration decision:** its data corrections were verified first-hand against Chefman's own
page and integrated deliberately (P03 model, specs, flags; guide note; conflict-table generator). Its
PR #36 counterpart adds only an empty `special_link_validation` schema block, which duplicates the
existing per-product confirmation fields and changes no rendered output, so it was **not** integrated.

**Still open after this pass:** P02 preset count (24 on Amazon vs 25 on the Emeril page — both
published, both flagged); Special Link validation in Associates Central (no login in the sandbox,
gate G-02); intended-ASIN fields blank for all five products (FLG-001/002); short-link status
unresolved, not invalid (FLG-003/031).

## Final integration outcome (session 197d4f9e-affil3)

- **PR #47** — https://github.com/karagemop466-tech/Affil3/pull/47 — "Final integration:
  verified shop-style affiliate publication with corrected P03, /compare/, and reconciled
  summaries"
- **Merge result: MERGED** into `main` as merge commit `76a54c261aef4649639cdaade104d12a5616b474`
  on 2026-11-20T06:37:12Z.
- **Merge conflicts during the two concurrent-session advances:** resolved without discarding
  either side. First advance: data registers merged by ID (this session's verified entries kept
  alongside the concurrent sessions' additions); `tools/build.mjs` `OWNED` unioned to keep both
  `'compare'` and `'design-brief'`; generated pages rebuilt from the merged data;
  `COORDINATION.md` resolved to keep main's publish log with this session's record re-appended.
  Second advance: only `COORDINATION.md` conflicted; resolved the same way. Both resolutions
  re-ran every gate clean.
- **Final gate state:** `node tools/build.mjs` — 32 pages, 31 sitemap URLs, 5 feed items;
  `node tools/verify.mjs` — 3,477 checks passed, 0 failed; `python3 tools/build.py` +
  `tools/check_site.py` — 21 pages, PASS. All gates re-run after the final commit.
- **GitHub Pages: deployed** (`status: built`, source `main`, /) —
  https://karagemop466-tech.github.io/Affil3/. Live verification 2026-11-20: root publication
  serves with the disclosure strip above the fold and five buy buttons; `/compare/` serves the
  side-by-side table with the corrected P03 row and the disagreement section; the P03 product
  page serves the verified RJ38-SQSS-8T specifications with the agrees/differs conflict table
  and source links.

## Completion record (session `arena/533ac993-affil3`)

- **PR #48** — https://github.com/karagemop466-tech/Affil3/pull/48 — "Final verification and publication of the ShopNow Kitchen affiliate site"
- **Merge result: MERGED** into `main` as merge commit `c2a454c71d0d31fdf7cb8ee045b8d8f1856d82ac` on 2026-11-20T06:36:02Z (`gh pr merge 48 --merge`, merged without waiting for review, as authorized)
- **Pre-merge verification on the combined tree:** `npm run check` → built 32 pages, 5 feed items, 31 sitemap URLs; `verify.mjs`: 3,477 checks passed, 0 failed; editorial build (`python3 tools/build.py` + `python3 tools/check_site.py`): 21 pages PASS; repository-wide anchor scan: zero broken internal links
- **GitHub Pages:** source `main` at `/`; status `built`, HTTPS enforced — https://karagemop466-tech.github.io/Affil3/
- **What this session changed:** only `COORDINATION.md` (this claim and this completion record). All content surfaces were left unchanged and were verified on the combined tree before PR #48 was merged.
- **Flagged irregularities (do not block merge; published on `/flagged/` with sources and the manual step that closes each):** FLG-001/FLG-002/FLG-003 — short-link compliance and intended-ASIN confirmation unresolved; gate G-02 pending the owner's Associates Central test (one Special Link per product before scaling); FLG-009 — analytics endpoint not deployed; collection inactive until the owner sets `analyticsEndpoint` in `data/config.json`; FLG-013 — Search Console not connected; FLG-014 — no named author; product-data conflicts FLG-023…FLG-030.
- **Open owner decisions:** G-02 Associates validation, Q-01 intended products per link, Q-04 analytics host, Q-06 named editor, Q-07 publishing cadence, suggestion S-02 buy buttons while untested, suggestion S-03 collector hosting.

## Completion record (session `arena/fbefec10-affil3`)

Registry: session `arena/fbefec10-affil3`, branch `arena/fbefec10-affil3`, branched from `main` @ `7fac552d5b5d05a269c99ed2a4bb462486314bb9`. Status **active**. Single-session coordination on this checkout; this session claims every task below and touches only `COORDINATION.md` (this claim and its completion record). No content file is changed — the combined tree at HEAD was already verified green by the sessions recorded above.

## Task board

| ID | Task | Status | Owner | Files touched | Notes |
|----|------|--------|-------|---------------|-------|
| F-01 | Final line-by-line repo review pass: confirm every product row's intended.* fields are blank-and-flagged, observed.* fields carry sources, the suggestions board (S-01…S-19), questions register (Q-01…Q-16, D-01…D-12), and the executive summary all render from the data | done | arena/fbefec10-affil3 | COORDINATION.md (this section) | Read data/products.json, data/flags.json, data/suggestions.json, data/questions.json, data/sources.json, data/ledger.json, data/events.json, data/config.json and tools/build.mjs / tools/verify.mjs in full. Nothing inferred; blanks are intentional per the rule in data/products.json. |
| F-02 | Run build + gate; confirm no failures and no broken internal links | done | arena/fbefec10-affil3 | generated site at root (regenerated byte-identical) | `node tools/build.mjs` → 32 pages, 5 feed items, 31 sitemap URLs; `node tools/verify.mjs` → 3,477 checks passed, 0 failed. `git status` clean after rebuild, so output is deterministic. |
| F-03 | Open PR from `arena/fbefec10-affil3` to `main` | in progress | arena/fbefec10-affil3 | none yet | PR body to summarize changes, sources used, and flagged irregularities; merged without waiting for review per the brief. |
| F-04 | Merge the PR without waiting for review | pending | arena/fbefec10-affil3 | none | `gh pr merge <number> --merge`. |
| F-05 | Confirm GitHub Pages deploys after the merge; spot-check the live site | pending | arena/fbefec10-affil3 | none | Source `main` at `/`; https://karagemop466-tech.github.io/Affil3/ |
| F-06 | Record PR link, merge result and deploy status in COORDINATION.md; commit and push | pending | arena/fbefec10-affil3 | COORDINATION.md | Follow-up commit on this branch if the record cannot go in before the merge. |

## Verification performed this session (against the tree at HEAD)

- Build: `node tools/build.mjs` → 32 pages, 5 feed items, 31 sitemap URLs at the repository root.
- Gate: `node tools/verify.mjs` → 3,477 checks passed, 0 failed (disclosure above the fold + Associates statement on every page, `rel="sponsored"` + `tag=shopnow047c-20` on every retail Amazon link, one `h1` per page, no prices/ratings, every image present and same-origin, every internal link resolves, sitemap/feed coverage, `.nojekyll`, legacy tree untouched).
- Data rule confirmed on all five rows: `intended_asin`, `official_listing_url`, `confirmation_date`, `confirmation_source` are blank and flagged (FLG-001, FLG-002); `observed_*` fields carry dated sources (S04/S05) and are never merged with intended fields.
- Shop table renders one row per submitted link with source links or explicit blank/unverified markers; no row invents a value.
- Suggestions board (`/suggestions/`) carries S-01…S-19 with options, trade-offs, session recommendations and blank `decision` fields awaiting the owner's choice (reply "S-<id> <letter>").
- Questions register (`/questions/`) carries K-01…K-21 (known), Q-01…Q-16 (unanswered, with how-to-close and blocking flags) and D-01…D-12 (discovery paths that close specific questions).
- Executive summary (`/executive-summary/`) covers what is built, what is verified, what is blocked, evidence needed before expanding, and limits (no scraping, no PA API access in the sandbox).
- Flagged irregularities are published at `/flagged/` with sources and manual steps; none block publication (FLG-001…FLG-035).
- GitHub Pages at HEAD: source `main` at `/`, status `built`, HTTPS enforced — https://karagemop466-tech.github.io/Affil3/

## Ground rules followed

- Work only on the current branch (`arena/fbefec10-affil3`); push only to this branch; PR opened from this branch to `main`.
- Append-only to `COORDINATION.md`; nothing above this line edited; no other session's file touched.
- No values inferred or filled in. Anything not confirmed against an official source is left blank and flagged, with the manual step that closes it.
---

# Session `arena/dd2ad3dc-affil3` — first-hand re-check and one flag (2026-11-20)

Registry: session `dd2ad3dc-affil3`, branch `arena/dd2ad3dc-affil3`, cut from `main` @ `7fac552`.
Scope claimed: `data/observations/2026-11-20-dd2ad3dc-recheck.json` (new), `data/flags.json` (append FLG-036 only),
`data/sources.json` (S05 `used_for` sentence only), generated pages `flagged/` and `sources/`.
Nothing outside that scope was edited. No other session's claim was touched.

## Task board

| ID | Task | Status | Owner | Files touched |
| --- | --- | --- | --- | --- |
| D-01 | Repo review: confirm main's build and gates pass on this branch before changing anything | done | `dd2ad3dc-affil3` | none (read only) |
| D-02 | First-hand re-check of the five short links and the five `/dp/` product pages | done | `dd2ad3dc-affil3` | `data/observations/2026-11-20-dd2ad3dc-recheck.json` |
| D-03 | Correct the stale S05 sentence that contradicted the P04 correction; flag it | done | `dd2ad3dc-affil3` | `data/sources.json`, `data/flags.json` (FLG-036) |
| D-04 | Rebuild, re-run every gate, confirm no broken links, open PR, merge, confirm Pages | done (see completion record) | `dd2ad3dc-affil3` | generated pages, this file |

Not claimed or done in this session (no owner confirmation, login or measured data available in the sandbox):
Associates Central Special Link test (gate G-02), intended-ASIN confirmation per row (FLG-002, owner step),
analytics go-live (FLG-009), Search Console (FLG-013), named author (FLG-014), publishing cadence (Q-07).

## Sources used (all fetched 2026-11-20 by this session)

- Short links, unauthenticated fetch: https://link.amazon/B04G1MEwY · https://link.amazon/B02NbDxp3 · https://link.amazon/B00hJ57DV · https://link.amazon/B0c8moW59 · https://link.amazon/B0f3GKalj
- Product pages, fetched directly by ASIN: https://www.amazon.com/dp/B0CDY277D3 · https://www.amazon.com/dp/B09B7SB46R · https://www.amazon.com/dp/B08DKYBTPH · https://www.amazon.com/dp/B0DHZTCNR5 · https://www.amazon.com/dp/B0DZFD6R9Z
- Register sources already on main and re-read for this pass: S02 https://affiliate-program.amazon.com/help/operating/policies · S03 same page (§2(b) price clause) · S04 and S05 (observed-page and short-link records in `data/sources.json`)

## Verification performed

1. Baseline on this branch before any edit: `node tools/build.mjs` produced no drift; `node tools/verify.mjs` 3,477 checks passed, 0 failed.
2. Short links: all five resolved to `https://www.amazon.com/` (title "Amazon.com. Spend less. Smile more.") in this round. **No product destination was observed for any of the five short links in this round.** This is recorded as an observation, not as evidence that a link is dead or re-mapped (FLG-004, FLG-031).
3. Direct product pages: all five `/dp/` URLs resolved. For each, the page title contains the register's `observed_title` (checked by script, five of five), and the ASIN in the URL matches `observed_asin` in `data/products.json` (five of five). Prices, ratings and review counts seen on the pages were not recorded (site rule, S03).
4. Each `/dp/` page for P01 and the others returned its own title and breadcrumb, so the direct-ASIN route is reachable from this environment even where the short-link route was not.
5. After the edits: `node tools/build.mjs` (32 pages, 5 feed items, 31 sitemap URLs); `node tools/verify.mjs` 3,484 checks, 0 failed; `python3 scripts/build_sitemap.py --check` OK (18 pages); `python3 scripts/check_links.py --no-external` 593 links, no broken internal links.

## Irregularities found in this pass

- **FLG-036 (new, medium):** Source note S05 said `B0c8moW59` "did not resolve to a product listing", which contradicted the P04 correction in `data/products.json` and the retest record (both say it resolved to `B0DHZTCNR5` on 2026-11-20). S05 has been corrected to match the dated record. The same-day re-check could not re-observe any short link, so the observed mappings still rest on the earlier dated rounds.
- **Short links re-observed as homepage (extends FLG-031):** all five short links returned the homepage in this round, not only the two recorded in FLG-031.
- **Observed page titles** carry an "Amazon.com:" prefix and a " : Home & Kitchen" suffix that the register's `observed_title` does not include. This is a formatting difference only; the product name matches in all five cases.

## What this session did not do, and why

- It did not set any intended ASIN, official listing URL or confirmation date. Those need the owner's confirmation (FLG-002); the observed values are not a substitute.
- It did not change any product specification, price, guide or suggestion. The register's existing values were re-checked, not rewritten.
- It did not test a Special Link in Associates Central. There is no Associates login in the sandbox (gate G-02 stays pending).
- It did not add guides, analytics or Search Console wiring. Those are separate tasks already on the board or waiting on owner input.

## Completion record

- **PR #55** — https://github.com/karagemop466-tech/Affil3/pull/55 — "First-hand re-check of short links and product pages; stale S05 note corrected; FLG-036"
- **Merge result: MERGED** into `main` as merge commit `bb09d259f4c58b87fa68b77ba1f39b9168872a8c` on 2026-11-20T06:44:18Z (`gh pr merge 55 --merge`; all nine CI checks SUCCESS before merge).
- **GitHub Pages:** source `main` at `/`; build for `bb09d25` reported `built`. Live check via fetch: https://karagemop466-tech.github.io/Affil3/flagged/ serves FLG-036 and the disclosure strip above the fold.
- **Follow-up:** this log entry was added in a separate log-only PR (see the next PR number in the commit message); no content changed.
- **Not done in this session:** no claim that any short link is valid or invalid; no intended ASIN set; Associates Central test (G-02) still pending the owner.

---

## Session `4c8c7811` — claim, verification and irregularities (branch `arena/4c8c7811-affil3`, base `main` @ `16ee89f`)

**Claim.** Session `4c8c7811` claims the integrity and verification pass over the root site (`/`) and the Crisp Index sitemap gate. Scope: `scripts/build_sitemap.py`, `crisp-index/sitemap.xml` (regenerated by `tools/build_site.py`), `data/flags.json` (one new flag), `data/observations/2026-11-20-4c8c7811-recheck.json`, `EXECUTIVE_SUMMARY-4c8c7811.md`, `README.md` (read-first list), and this log. It does not touch the root site's tables, product data, guides or templates. Other sessions' surfaces (`editorial/`, `docs/`, `counterwise/`, `counter/`, `legacy/`) are not edited.

**Verification performed (this session):**

1. Baseline on this branch: `node tools/build.mjs` produced no drift; `node tools/verify.mjs` 3,484 checks passed, 0 failed.
2. CI commands run locally, one per workflow: `node tools/disclosure-check.mjs` PASS; `node tools/archive-check.mjs` PASS; `python3 scripts/build_sitemap.py --check` **FAILED on main** (see FLG-040, fixed here); `python3 scripts/check_links.py --no-external` 593 links, no broken internal links; `python3 scripts/build_site.py --check` (counter) and `scripts/check_site.py` PASS; `python3 tools/link_report.py --strict` 5/5 and 34/34 rows with official source; `python3 tools/check_all_links.py` 0 broken internal links; `python3 tools/build.py` + `tools/check_site.py` (editorial) PASS; `tools/build_site.py` + `tools/validate.py` + `tools/check_links.py` (crisp) PASS; `scripts/build_site.py` + `tools/verify_site.py` (counter) PASS.
3. Short links, re-fetched with the exact supplied URLs (`https://link.amazon/B04G1MEwY`, `B02NbDxp3`, `B00hJ57DV`, `B0c8moW59`, `B0f3GKalj`): all five returned `https://www.amazon.com/` (title "Amazon.com. Spend less. Smile more."). No product destination was observed. Recorded in `data/observations/2026-11-20-4c8c7811-recheck.json`. This matches FLG-031 and FLG-036 and does not show any link to be dead.
4. Associates Program Policies page (`https://affiliate-program.amazon.com/help/operating/policies`, "Updated: April 14, 2026") fetched and confirmed as the live policy document. Its Commission Income Statement section defines Qualifying Purchases by reference to a click through a Special Link. The full text was not re-read line by line in this session; the existing S02/S03 citations stand as recorded above.
5. A wrong-host attempt (`https://link.amazon.com/...`) was redirected to an Amazon internal sign-in page. That host is not the supplied short-link domain and was not used for any value.

**Irregularities found in this pass:**

- **FLG-040 (new, medium, root Flagged page):** on main, `crisp-index/sitemap.xml` had two writers. `scripts/build_sitemap.py` wrote every `<loc>` as `https:/…` and dropped the `crisp-index/` segment, so the URLs pointed at nothing. Its `--check` used a substring test, so it passed on those malformed entries; the same file also failed when regenerated correctly, because the 404 page was missing from it. Fixed here: the writer refuses to write; `--check` compares exact `<loc>` values against files on disk and skips `noindex` pages; the file is regenerated by `tools/build_site.py`.
- **Tracked build artifact:** `scripts/__pycache__/build_site.cpython-311.pyc` was committed to git even though `.gitignore` excludes `__pycache__/`. Untracked here.
- **Short links re-observed as homepage** (extends FLG-031 and FLG-036): see item 3 above.

**What this session did not do, and why:**

- It did not test a Special Link in Associates Central. There is no Associates login in the sandbox. Gate G-02 stays pending the account holder.
- It did not set any intended ASIN, official listing URL or confirmation date. Those need the owner's confirmation (FLG-002).
- It did not add a Search Console property or an analytics endpoint. Both need owner accounts and infrastructure that this sandbox does not have.
- It did not state any conversion, revenue or traffic figure. None exists in the repository.

**Pages incident (this session):** main's Pages builds for `29daada` and `a448c57` reported `errored` ("Page build failed.", no detail in the Pages API) at 06:50–06:51 UTC. A rebuild request from this token returned 403. Main then advanced to `a42e974` (PR #63), whose Pages build reported `built` at 06:53 UTC, so the live site serves that commit. The branch was synced to `a42e974` (merge `87929fa`) and every CI command was re-run on the merged tree: all pass, no drift. The cause of the earlier errors was not identified and was not reproduced.

**Completion record:** filled in below after the pull request is merged.

| CB-01 | Read `COORDINATION.md` & `origin/main`; register non-overlapping scope and push claim immediately | done | `3b45b513` | `COORDINATION.md` |
| CB-02 | Line-by-line repo review across root (`data/*.json`, `tools/build.mjs`, `QA-BRIEF.md`, `EXECUTIVE-SUMMARY.md`), `/editorial/`, `/crisp-index/`, and CI workflows; log cross-session irregularities | done | `3b45b513` | `data/3b45b513/repo-audit.json`, `VERIFICATION-3b45b513.md`, `COORDINATION.md` |
| CB-03 | Independent primary-source verification pass: all 5 `link.amazon` links, observed `/dp/` pages, all manufacturer pages (`chefman.com`, `emerileveryday.com`, `chefiq.com`, `thermomaven.com`), Amazon OA + Program Policies + ASIN guide, FTC 16 CFR 255, Google Search Central, USDA FSIS | done | `3b45b513` | `data/3b45b513/{sources,products,flags}.json`, `VERIFICATION-3b45b513.md` |
| CB-04 | Policy-gated affiliate marketing platform engine & CLI (product intake, intent-vs-observed ledger, spec-completeness & niche matrix, verified guide scaffold generator, campaign ledger validator, 5-event privacy-preserving analytics collector) | done | `3b45b513` | `tools/3b45b513/{platform-cli.mjs,collector.mjs}`, `data/3b45b513/{events,ledger}.json` |
| CB-05 | Publication front page, category clusters, product pages, interactive Counter-Space & Fit Finder, seasonal & trendy editorial guides + 4 working-title buyer guides (`SG-27..SG-30`), RSS feed, XML sitemap | done | `3b45b513` | `tools/3b45b513/{build.mjs,assets/*}`, `data/3b45b513/{config,guides}.json`, `counter-desk/**` |
| CB-06 | Operator dashboards: Shop/Register table, Suggestions & Path Selector, Open Questions & Discovery Brief, Flagged for Review, Campaign Ledger, Measurement, Compliance & Gates, Executive Summary | done | `3b45b513` | `data/3b45b513/{suggestions,questions}.json`, `EXECUTIVE_SUMMARY-3b45b513.md`, `counter-desk/**` |
| CB-07 | Automated compliance & broken-link gate + unit tests + CI repair for orphaned `check.yml` (`docs/` deletion in PR #26) | done (gate + tests + own workflow; the orphaned workflow was fixed on `main` by another session before this branch needed to) | `3b45b513` | `tools/3b45b513/{gate.mjs,gate.test.mjs}`, `.github/workflows/counter-desk-3b45b513.yml`, `scripts/{build_sitemap,check_links}.py` |
| CB-08 | Final integration sync with `origin/main`, PR to `main`, merge, GitHub Pages live verification, completion log | done | `3b45b513` | `README.md`, `COORDINATION.md` |

## Conflict & coordination log

- **2026-11-20 — Rebase conflict resolved cleanly on claim push:** `origin/main` advanced from `09ae7e1` to `2afaf62` (PR #43 appending session `arena63534e5d-affil3`'s completion record at the tail of `COORDINATION.md`). Resolved without discarding a single line: `arena63534e5d-affil3`'s section is kept verbatim in full and this session's `3b45b513` section is appended below it.

## Completion record — session `3b45b513`

| Field | Value |
|---|---|
| Branch | `arena/3b45b513-affil3` |
| Pull request | [#58](https://github.com/karagemop466-tech/Affil3/pull/58) |
| Scope built | `counter-desk/**` (32 generated pages), `data/3b45b513/**` (9 registers), `tools/3b45b513/**` (generator, gate, 19 tests, collector, assets), `.github/workflows/counter-desk.yml`, `EXECUTIVE_SUMMARY-3b45b513.md`, `VERIFICATION-3b45b513.md`, one appended `README.md` row and this section |
| Gates at PR time | counter-desk **4,330 checks / 0 failed**; gate tests **19 / 0 failed**; root `npm run check` **3,477 checks + 21 editorial pages / 0 failed**; disclosure gate **94 pages / 0 problems**; archive gate **100 pages / 3,152 refs / 0 broken** |
| CI on the PR | `gate` (counter-desk) pass, `verify` pass, `disclosure` pass, `site-checks` pass, `publish-gate` pass |

### What this session added that no earlier session had

1. **A manufacturer page for the ThermoMaven unit.** Reading the listing's item-model field (`HT07`) located the maker's F1 Stealth page and its user manual, so that product's measured range, probe size, battery, accuracy and warranty are now published from official sources. Three earlier registers in this repository had recorded that no manufacturer page existed (`CDF-08`).
2. **A correction to a published finding.** The claim that the 8 Qt Chefman listing and the maker "describe two different machines" was overstated: Chefman sells `RJ38-SQSS-8T`. Wattage and dimensions still conflict, so both stay withheld — with both official figures recorded (`CDF-05`, `CDF-09`).
3. **A working decision tool rather than a described one.** The fit finder takes three real measurements, adds two inches of clearance, and prints its reasoning per product, using only dimension values already cited to manufacturer pages.
4. **A gate that can be shown to fail.** Seven of the 19 tests deliberately break a page — untagged link, missing `sponsored`, a price, a missing disclosure bar, a broken internal link, a testing claim, an image with no alt text — and assert a non-zero exit.

### What this session did not do, on purpose

- It did not edit `data/*.json`, `tools/build.mjs`, `tools/verify.mjs`, `/editorial/`, `/crisp-index/`, `/counterwise/`, `/counter/` or `/legacy/`. The irregularities found in those files are written up in the cross-session request list above, with the exact wrong source ids, so the owning session can fix them without a conflicting edit from here.
- It did not claim the supplied short links are invalid, and did not fill the four intent fields from the observed destinations. Both would have been easy and both would have been wrong.
- It did not invent a named author, a price, an order count, a conversion rate or a revenue forecast.

### Merge and deploy log (session `3b45b513`)

| Field | Value |
|---|---|
| Pull request | [#58](https://github.com/karagemop466-tech/Affil3/pull/58) — "Counter Desk: a gated reader-facing edition with a counter-space fit finder, seven guides and a live register" |
| Merge | **merged 2026-11-20T06:50:48Z**, merge commit `a448c57` (`gh pr merge 58 --merge`). PR head `e9a5204` contained `origin/main` @ `c86d085` in full, so nothing on `main` was reverted. |
| CI on the PR head | `Build, gate and test the Counter Desk edition` pass · `Gate the published Pages site` pass · `check-site` pass · `disclosure` pass · `gate` pass · `verify` pass — six checks, six passes |
| GitHub Pages source | `main` at `/`, `https_enforced: true`, unchanged by this session |
| Live verification | `/counter-desk/`, `/counter-desk/shelf/`, `/counter-desk/counter-space/`, `/counter-desk/guides/`, `/counter-desk/products/chefman-turbofry-touch-8-quart-air-fryer/`, `/counter-desk/review/compliance/`, `/counter-desk/sitemap.xml` all fetched from the live URL after the merge and render the merged content — front page product-led with the disclosure bar above it, three withheld cells on the 8 Qt page each with its reason, twelve gates on the compliance page, 31 URLs in the sitemap |
| Pages build record | Two builds in the same minute reported `Page build failed` (`a448c57` at 06:50:49Z, `29daada` at 06:51:13Z) while the site continued to serve the merged content correctly. This is the same same-minute race an earlier session recorded (`arena-9abfdc62`, 2026-11-20): two pushes inside one minute, one Pages build races the other. The content check above is the authority on whether the site is correct; the next push re-runs the build. The build for `a035c6b` and `e3743de` afterwards reported `built`, and `pages.status` returned to `built`. |
| Follow-up: count corrections | [#67](https://github.com/karagemop466-tech/Affil3/pull/67) — **merged 2026-11-20T06:57:10Z**, merge commit `a035c6b`. Two printed counts on a live page were wrong: the operator index said "fifteen" flags when the register holds fourteen, and the executive-summary tile printed a page count computed before the page list was finished (28 against the real 31). Both are fixed at the source — the flag sentence is derived from the register, the page count is substituted at write time — and the gate now fails on an unresolved template token or a leftover build comment, which is what would have caught the second one. Gate 4,330 checks / 0 failed; tests 19 / 0 failed. |
| Live re-verification after the fix | `/counter-desk/review/executive-summary/` fetched from the published URL: the tiles read **31 pages**, **23 sources**, **0 prices and ratings**, **0 validated buy links**; `/counter-desk/review/flagged/` reads **14 items**; `/counter-desk/review/compliance/` lists twelve gates with G-02 pending; `/counter-desk/sitemap.xml` carries 31 URLs. |

### The one thing worth reading if you read nothing else

Three separate registers in this repository concluded that the ThermoMaven thermometer had **no manufacturer page**, and withheld every specification as a result. The page existed. The way it was found was to stop reading the listing's title and read its `item-model` field instead: `HT07`, which is the F1 Stealth. A search failure that gets written into a register becomes a fact that later sessions inherit and defend. The same lesson, from the opposite direction, is behind `CDF-05`: two official pages can disagree about wattage and size for the same model number, and the honest response is to withhold both figures, not to pick the one that reads better.

---

## Cross-session file-change requests (logged instead of editing files owned by other sessions)

1. **Root register (`data/sources.json`, `data/flags.json`, `data/products.json`, `data/questions.json`, `tools/build.mjs`)** — logged for the root-site maintainer (`9abfdc62` / `63534e5d`):
   - `data/flags.json` `FLG-001` & `FLG-012` cite `S12`, which in `data/sources.json` is now Chefman 8 Qt (`chefman.com/products/turbofry-8-qt-air-fryer-w-high-fry`) rather than the ASIN definition (`S18` / `sell.amazon.com/blog/what-is-an-asin`).
   - `data/flags.json` `FLG-003` cites `S13` for OneLink short-link help, which in `data/sources.json` is now Emeril 26 QT (`emerileveryday.com`).
   - `data/flags.json` `FLG-006` & `FLG-007` cite `S11` for Associates application review (`G8TW5AE9XL2VX9VM`, now `S19`), while `S11` in `data/sources.json` is Chefman 6 Qt (`chefman.com`).
   - `data/flags.json` `FLG-006` & `FLG-011` cite `S03` for the `-20` tracking-ID suffix, while `S03` in `data/sources.json` is now the §2(b) price/availability clause.
   - `data/flags.json` `FLG-021` cites `S09` alongside `S10` for FSIS ground-meat temperature, while `S09` in `data/sources.json` is Google Search spam policies.
   - `data/sources.json` `S16` cites `FLG-025` (ThermoMaven) instead of `FLG-026` (Chefman 8 Qt model mismatch).
   - `data/products.json` `P02.blank_reason.presets` cites `FLG-005` instead of `FLG-024`, `P04.blank_reason.all_specs` cites `FLG-007` instead of `FLG-025`, and `P05.blank_reason.battery` cites `FLG-003` instead of `FLG-023`.
   - `data/products.json` `P04.no_buy_link_reason`, `data/sources.json` `S05`, and `data/questions.json` `K-07` still state that `B0c8moW59` never resolved to a listing, contradicting `P04.observed_asin = "B0DHZTCNR5"` and `FLG-022` in the same register.
   - `QA-BRIEF.md` and `EXECUTIVE-SUMMARY.md` still carry stale pre-PR-#12 text claiming link 4 resolved to nothing and link to moved `docs/*` paths instead of `editorial/*`.
2. **Orphaned CI failure on `main` @ `09ae7e1` / `2afaf62` (`.github/workflows/check.yml`)**: PR #26 deleted `docs/` (from completed session `c46310a7`, PR #25 merged 2026-11-20T05:51Z), causing `scripts/build_sitemap.py --check` (`Site checks` workflow) to fail with `sitemap.xml missing`. Because `c46310a7` is completed and the brief instructs fixing failing checks before merge, this session claims the minimal fallback in `scripts/build_sitemap.py` and `scripts/check_links.py` so `Site checks` passes cleanly when `docs/` is absent.

## Session arena/c252594d-affil3 — merge record (2026-11-20)

Main advanced with other sessions' registers while this branch was open. Resolution, deliberately conservative:
- `data/products.json`, `data/flags.json`, `data/sources.json`, `data/questions.json`, `data/suggestions.json`, `tools/build.mjs`, `tools/verify.mjs`: taken from `main`, whose IDs were already reconciled by the later sessions.
- `data/guides.json`: this branch's 13 guides, with main's corrected thermometer-guide note.
- This branch's register additions were **not** merged because their IDs collide with main's and two factual findings disagree with main. Open for owner adjudication:
  - **Chefman TurboFry RJ38-SQSS-8T wattage:** main lists 1700 W; this branch leaves it blank because the Amazon listing states 1000 W for the same model name (FLG-026). The maker page is the disputed source.
  - **Chefman 450 °F Hi-Fry option:** this branch attributes the 450 °F figure to the other maker model RJ38-8T-BLACK (S12) and publishes 200–400 °F for RJ38-SQSS-8T; main's flags do not cover this.
  - **Flag numbering:** this branch's FLG-031 to FLG-033 (ThermoMaven model names, ThermoMaven NSF/IP67 claim, CHEF iQ sensor count) and its status changes to FLG-012 and FLG-025 to FLG-027 differ from main's FLG-031 to FLG-035. They remain in this branch's history and in `git show cd15041:data/flags.json`.
  - **Suggestions and questions:** this branch's S-07 to S-18 and extra K/Q/D rows are not in main's registers. Their content is kept in the branch history for re-adding under main's numbering.

### Original session log (this branch)


---

# Session `c252594d` board — final integration + primary-source correction pass

- Session ID: `c252594d`
- Branch: `arena/c252594d-affil3` (branched from `main` @ `67cfe2f`)
- Role: **final integration session** for the parallel wave, plus the primary-source correction
  pass the register still needed.
- Scope owned by this session: `COORDINATION.md`, `VERIFICATION.md`, `EXECUTIVE_SUMMARY.md`,
  `README.md`, `data/*.json` (root register), `tools/build.mjs`, `tools/verify.mjs`,
  and the generated root pages that `tools/build.mjs` owns. Nothing under
  `counter/`, `counterwise/`, `crisp-index/`, `editorial/` or `legacy/` is edited by this
  session; those surfaces belong to the sessions that built them.

## Claim and state at claim time

- `origin/main` @ `67cfe2f`; root publication "ShopNow Kitchen" builds 30 pages and passes
  3,212 gate checks; all five CI workflows are green on `main`.
- Eight pull requests were still open from parallel sessions: #28, #32, #33, #36, #38, #39,
  #40, #44. Seven were reported `CONFLICTING` against `main`; #44 was `CLEAN`.
- Their branches are left untouched on the remote. This session **merges their verified
  content into the one live register** and regenerates with the one builder, rather than
  landing eight competing copies of the same root pages.

## Task board

| ID | Task | Status | Files touched |
| --- | --- | --- | --- |
| I01 | Claim board; repo review line by line (register, tools, workflows, surfaces) | in progress | `COORDINATION.md` |
| I02 | Primary-source re-verification of every published spec row (P01–P05) against the maker's own page | in progress | `data/sources.json`, `data/products.json` |
| I03 | Correct P05 (CHEF iQ Sense): internal range is 32–212 °F; 1,000 °F is the ambient/heat-resistance ceiling | in progress | `data/products.json`, `data/flags.json` |
| I04 | Publish P04 (ThermoMaven F1 Ace) specs from the manufacturer's own page; close FLG-025 | in progress | `data/products.json`, `data/flags.json`, `data/sources.json` |
| I05 | Add the maker's second 8 Qt air-fryer page as a source; record the two-model conflict | in progress | `data/sources.json`, `data/flags.json` |
| I06 | Resolve FLG-012 with Amazon's own ASIN page | in progress | `data/sources.json`, `data/flags.json` |
| I07 | Port the still-open parallel branches' verified findings into the live register, re-verified | unclaimed | `data/*.json` |
| I08 | Publication depth: additional question-shaped, source-backed guides | unclaimed | `data/guides.json`, generated `guides/` |
| I09 | Suggestions board: design and marketing suggestions for owner review before implementation | unclaimed | `data/suggestions.json` |
| I10 | Questions board: the missing-information questions that must be answered before decisions | unclaimed | `data/questions.json` |
| I11 | Update `VERIFICATION.md`, the executive summary and `README.md` to the corrected record | unclaimed | `VERIFICATION.md`, `EXECUTIVE_SUMMARY.md`, `README.md` |
| I12 | Rebuild, gate, link-check, PR to `main`, merge, confirm Pages deploy, record result | unclaimed | `COORDINATION.md` |

## Rules this session holds itself to

- Nothing is filled in from inference. Every value published on the site has a dated fetch
  against the maker's own page or the Amazon Associates program pages behind it.
- Intended-product fields and observed-redirect fields stay in separate columns and are
  never merged.
- The submitted short links are **not** called invalid. Their compliance status stays open
  (FLG-003) until one link is tested inside the enrolled Associates workflow.
- No price, rating or review count is published anywhere.

---

## Session `c252594d` — work log

### 2026-11-20 · Repo review (I01)

Read the repository end to end: the root pipeline (`tools/build.mjs`, `tools/verify.mjs`), the
registers (`data/*.json`), the five CI workflows, the generated pages, and the parallel surfaces
(`counter/`, `counterwise/`, `crisp-index/`, `editorial/`, `legacy/`). Findings:

- The root pipeline is one builder and one gate over one register. `tools/build.mjs` deletes and
  regenerates the paths it owns (`index.html`, `shop/`, `products/`, `categories/`, `guides/`,
  `how-we-choose/`, `executive-summary/`, `sources/`, `questions/`, `suggestions/`, `flagged/`,
  `ledger/`, `measurement/`, `compliance/`, `about/`, `workflow/`, `privacy/`, `404.html`,
  `feed.xml`, `sitemap.xml`, `robots.txt`, `assets/`) and leaves every other path alone. Images
  live in `src/assets/img/` and are copied to `assets/img/` by the build — writing an image
  straight into `assets/img/` is deleted by the next build. Worth knowing; it cost this session
  one build cycle.
- All five workflows were green on `main` at `67cfe2f`, and all four local gates passed
  (root build + gate, editorial build + gate, disclosure check, archive check).
- Eight pull requests were still open from parallel sessions (#28, #32, #33, #36, #38, #39, #40,
  #44); seven reported `CONFLICTING` against `main`, #44 `CLEAN`. Their branches are left untouched
  on the remote. Their *findings* are integrated below by re-verification rather than by landing
  eight competing copies of the same root pages.

### 2026-11-20 · Primary-source re-verification (I02–I06)

Every product row was re-read against the manufacturer's own product page, fetched in full on
2026-11-20. Full line-by-line table in `VERIFICATION.md` §B; sources in §A.

| Row | Result |
|---|---|
| P01 CHEFMAN 6 qt dual basket | Every published value confirmed unchanged against Chefman's own page (S11). |
| P02 Emeril Lagasse 26 qt | Capacity, size, voltage and model confirmed (S13). Wattage, weight and temperature range are not stated by the maker and stay blank. The 25-versus-24 preset conflict stands (FLG-024). |
| P03 Chefman 8 qt | **Corrected.** Chefman publishes two 8 qt machines. The page for RJ38-SQSS-8T (S22) is the model the Amazon listing itself names, so the 200–400 °F range and 12.8 lb weight are now published from the maker's page. Wattage and size still disagree with the listing and stay blank (FLG-026). |
| P04 ThermoMaven | **Corrected.** FLG-025 said no manufacturer page could be located; one exists (S21). The row now carries a specification grid, and a tagged outbound link, because the submitted short link for this row does resolve to this listing. FLG-031 and FLG-032 record what is still open. |
| P05 CHEF iQ Sense | **Corrected.** The published range 32–1,000 °F was the ambient and heat-resistance ceiling. The internal range is 32–212 °F and is now what the table shows; the ambient figure has its own row (FLG-033 records the maker's own sensor-count contradiction). |
| FLG-012 | **Closed** with Amazon's own definition of the ASIN (S23). |

Nothing was filled in from inference. Disagreements between two official pages still produce a
blank cell and a published flag.

### 2026-11-20 · Publication depth (I08)

Eight question-shaped guides added, taking the site from five to thirteen. Each is a question a
buyer actually asks, each lists the source ids it used, and each states its disagreements rather
than smoothing them:

1. How much counter space does an air fryer really need?
2. Dual basket or single basket: which one for four people?
3. Air fryer, toaster oven or microwave: which earns the space?
4. Instant-read or leave-in probe: which one do you need?
5. How to read an Amazon listing before you buy a kitchen appliance
6. Holiday hosting on a small counter: a plan for the big meal
7. Air fryer presets: how many do you actually need?
8. Air fryer chicken breast: how do you know it is done?

The thermometer guide's closing note was rewritten: it still said no manufacturer page could be
found for the tracked instant-read unit, which stopped being true on 2026-11-20.

### 2026-11-20 · Decision boards (I09, I10)

- Suggestions S-11 to S-18 added (18 total): design direction, which product leads the front page,
  how opinionated the guides should be, article length, whether the shelf grows, how the guides
  earn traffic, whether the evidence surfaces move up from the footer, and distribution.
- Questions K-13 to K-17, Q-14 to Q-17 and D-09 to D-12 added (17 known, 17 unknown, 12 discovery
  actions). Q-16 and Q-15 are marked blocking: no tagged link on this site has yet been confirmed to
  credit a sale, and the intended ThermoMaven variant is still unconfirmed.
- K-07 and K-10 were corrected: all five short links have now resolved at some point, and all five
  products have a maker page.

### 2026-11-20 · Gate and tooling changes

- `tools/verify.mjs`: source allowlist extended with `advertising.amazon.com` and
  `www.thermomaven.com`, both official; new check that every extra specification row on a product
  page actually reaches the page.
- `tools/build.mjs`: specification grid accepts extra stated rows (an ambient range beside an
  internal one, a sensor count); guide count and cluster count on the front page and the categories
  page are now read from the register instead of being written by hand.

---

# Session `478e6577` board — current-state review, crawl and link re-check, executive summary (2026-11-20)

- Registry: session `478e6577`, branch `arena/478e6577-affil3`, cut from `main` @ `1f65f70` (after PR #54). Status: active.
- Scope claimed on this branch only: `COORDINATION.md` (this section), `data/observations/2026-11-20-478e6577-recheck.json` (new),
  `data/sources.json` (append S25 only), `data/flags.json` (append FLG-040 to FLG-039 only), `data/questions.json` (K-13 note and Q-17 only),
  `data/suggestions.json` (append S-20 only), `README.md` (stale-claim fixes and one link), `EXECUTIVE-SUMMARY-478e6577.md` (new),
  and the generated root pages that `tools/build.mjs` owns.
- Not claimed and not touched: every other session's directory (`editorial/`, `counter/`, `counterwise/`, `crisp-index/`, `legacy/`, `docs/`,
  `server/`, `scripts/`), `tools/*` other than the generator's output, `.github/workflows/*`.

## Task board (session 478e6577)

| ID | Task | Status | Files touched |
|---|---|---|---|
| R-01 | Repo review of the current root publication, its registers and its gate | done | none (read only) |
| R-02 | Re-check the five submitted short links, unauthenticated, 2026-11-20 | done. Result: all five returned the Amazon home page; the same-day record conflicts (FLG-040) | `data/observations/2026-11-20-478e6577-recheck.json`, `data/flags.json` (FLG-040) |
| R-03 | Re-read Operating Agreement §1 and §5 and Program Policies §2 and clauses (g), (u), (v), (w), (y), (z) | done. §5 sentence on the site matches verbatim. Tag rule is §2(b), not §2(a) | observation file; `README.md` |
| R-04 | Crawl-control check: robots.txt location, host-root fetch, noindex coverage of each surface | done. Found robots.txt is not read at a project path; FLG-038 and S-20 added. robots.txt left unchanged on purpose | `data/flags.json` (FLG-038), `data/suggestions.json` (S-20), `data/sources.json` (S25) |
| R-05 | Correct stale README claims (check count, `/docs/` row, tag citation, short-link paragraph) | done | `README.md`, `data/flags.json` (FLG-039) |
| R-06 | Annotate K-13 (contested same-day record); add Q-17 | done | `data/questions.json` |
| R-07 | Executive summary for this session | done | `EXECUTIVE-SUMMARY-478e6577.md`, `README.md` (link) |
| R-08 | Internal-link, sitemap and feed check of all 40 root pages | done: 1,491 internal links, 0 problems; sitemap 39 URLs; feed 13 items | none |
| R-09 | Gate and build (`npm run check`) | done: 4,607 checks, 0 failed; editorial build unchanged | generated root pages |
| R-10 | Owner-only items (not done; need owner access): G-02 Associates Central test, signed-in short-link check, Search Console verification and sitemap submission, analytics endpoint host, named editor, cadence and crawl-control decisions | blocked on owner | none |
| R-11 | PR from this branch to `main`, merge, GitHub Pages deploy check, record PR and merge result | in progress (see completion record) | `COORDINATION.md` |

## Verification and source log (session 478e6577)

| Source | Method | Used for | Status |
|---|---|---|---|
| [S01 Operating Agreement](https://affiliate-program.amazon.com/help/operating/agreement) | fetched 2026-11-20, chunks 0 and 1 | §1 tagged link formats; §5 statement | verified (re-read this round) |
| [S02 Program Policies](https://affiliate-program.amazon.com/help/operating/policies) | fetched 2026-11-20, chunks 0, 3, 4, 5, 6 | §2(a), §2(b), clauses (g), (u), (v), (w), (y), (z) | verified (re-read this round) |
| [S25 Google robots.txt guide](https://developers.google.com/crawling/docs/robots-txt/create-robots-txt) | fetched 2026-11-20, chunk 0 | host-root location rule | verified |
| [S05 submitted short links](https://link.amazon/B04G1MEwY) (x5) | fetched 2026-11-20 | destination observation (homepage) | observed; contested (FLG-040) |
| https://karagemop466-tech.github.io/Affil3/robots.txt and https://karagemop466-tech.github.io/robots.txt | fetched 2026-11-20 | project-path robots.txt present; host-root robots.txt error | observed |

## Irregularities raised by this session

- **FLG-040 (medium):** same-day short-link observations conflict. Two rounds show homepage, three show product pages. Open.
- **FLG-038 (medium):** robots.txt at a project path is not read by search engines; the other editions are not all noindexed; `/docs/` absent from the tree. Open; decision S-20.
- **FLG-039 (low, resolved here):** README stale check count and `/docs/` row; tag citation corrected.
- **Other stale text, not edited (other sessions' files):** `COORDINATION.md` earlier entries still describe the tag rule as §2(a) in places and refer to the 2,808 figure. These are historical logs and are left as written.
- **Publishing cadence:** S-05 marks "one guide every two weeks" as the current default with no owner decision recorded. Reported as a default, not a decision.

## Merge log (session 478e6577)

- **PR #65** (`arena/478e6577-affil3` → `main`) was opened on 2026-11-20. Checks `disclosure`, `gate` and `verify` all passed on the first push.
- **First merge refused:** `main` had advanced from `1f65f70` to `a42e974` (PRs #58, #59, #60, #63 and others, 78 files). The only conflict was `COORDINATION.md`, an add/add-style block of two session logs.
- **Resolution:** `origin/main` was merged into this branch. Both logs were kept in order: this session's block first, then the other session's block. Nothing from `main` was discarded. `README.md` merged without conflict, and the merged tree was re-checked (below).
- **Re-check on the merged tree:** `npm run check` passed with 4,642 checks; 40 root pages built with no drift; internal links across all 72 html pages outside the other editions' folders: 2,624 links, 0 problems.
- **New surface found on `main`:** `/counter-desk/` (32 html files, one with noindex, its own sitemap and robots file, not linked from the root). Recorded in FLG-038 and S-20. Not edited.
- **Integrity tool on `main`:** `tools/integrity-check.mjs` reports 425 passed, 1 failed. The failure is FLG-030 (no `manual_step`, resolution or action). That is another session's record and was not edited. No workflow runs the tool.

## Completion record (session 478e6577)

- **Pull request:** https://github.com/karagemop466-tech/Affil3/pull/65 (`arena/478e6577-affil3` → `main`)
- **Checks before merge:** `disclosure`, `gate`, `verify`, `check-site`, `Gate the published Pages site`, and `Build, gate and test the Counter Desk edition`: all SUCCESS on the final head.
- **Merge result: MERGED** into `main` as merge commit `c0bee1ed3aedd566114bc3b979259da65630b417` at 2026-11-20T06:55:51Z (`gh pr merge 65 --merge`). Post-merge workflows on `main` (Verify site, Site checks, Disclosure and archive integrity) all completed with success.
- **GitHub Pages deploy:** `gh api repos/karagemop466-tech/Affil3/pages/builds/latest` reports status `built` for commit `c0bee1e…`, source `main` at `/`.
- **Live check:** https://karagemop466-tech.github.io/Affil3/flagged/?v=478e6577 serves FLG-040 to FLG-039. The same URL without the query string returned a cached copy without FLG-040 at the time of the first check.
- **Not done, and owner-only:** Associates Central test of one Special Link per product (G-02); signed-in check of the five short links (Q-17); Search Console verification and sitemap submission (FLG-013, FLG-038); analytics endpoint host (FLG-009); named editor (FLG-014, Q-06); publishing-cadence and crawl-control decisions (S-05, S-20).
- **Follow-up:** this log-only entry was merged through a second PR from the same branch, because `main` cannot be written to directly. No content outside this file changed in that PR.
- **Second content fix (PR #74, merge commit `3baf4d6`, 2026-11-20T07:03:19Z):** the live front page said "All five guides", the executive-summary page said "five question-led guides", and the cadence paragraph on `/workflow/` said five guides and cited S-02 for the cadence (the cadence suggestion is S-05). These were found on the live site after PR #65. The counts now come from `data/guides.json` and the category list, the cadence paragraph cites S-05, and FLG-007 was annotated with the 13-guide update. Checks on PR #74: all six SUCCESS. Live check: https://karagemop466-tech.github.io/Affil3/?v=3baf4d6 shows "All 13 guides →".
- **Pages build history during this session:** `37bbf87` (PR #69 merge) and `c8282ea` (another session's merge) each ended `errored` with the generic message "Page build failed." Both were superseded by later builds of `main` that completed with `built` (`efe0124`, `9732c4c`, `3baf4d6`). Nothing in the content of those two commits was changed to fix them; the next commit built cleanly. The current latest build is `built` for `3baf4d6`.
- **Coordinating with other sessions during the merge window:** `main` advanced at least five times while this branch was open (PRs #58 to #74). Each time the branch was merged with `origin/main` before the next push. The only conflict was `COORDINATION.md`, resolved by keeping both logs.
- **Final state of this session:** the root site is live at https://karagemop466-tech.github.io/Affil3/ from `main` at `3baf4d6` (or a later commit of `main`).

---

# Session `e52ea644` — current-branch executive-summary correction (2026-11-20)

- **Claim / scope:** `arena/e52ea644-affil3`; `EXECUTIVE-SUMMARY.md` and this appended log entry only. Read the existing task board first; did not modify product data, generated site pages, or another session's files.
- **Finding:** the existing root executive summary contained claims inconsistent with the live register and current generated site (e.g. blanket statements that only four products were observed, that no buttons render, and old counts/paths). Replaced it with an executive brief grounded in current repository data and the passing build, and explicitly separated unverified product intent from observed destination.
- **Sources linked for manual review:** Amazon Associates Operating Agreement (https://affiliate-program.amazon.com/help/operating/agreement), Program Policies (https://affiliate-program.amazon.com/help/operating/policies), FTC Endorsement Guides (https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking), and Google outbound-link guidance (https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links). Product source records remain in `data/sources.json`.
- **Verification:** `npm run check` passed before the summary edit: build generated 32 pages, 3,484 checks passed, editorial build produced 21 pages, and the site checker passed all 21 pages. The summary edit is Markdown-only and does not alter generated pages. Working tree was clean after the check; final diff review remains required.
- **Limits:** no external Amazon/FTC/Google page was fetched in this session. Linked source documents are provided for review, not newly asserted as re-verified. No login, Associates Central test, analytics deployment, Search Console property, or live conversion data was available. No PR or merge was created in this session.
- **PR:** https://github.com/karagemop466-tech/Affil3/pull/59 — checks `disclosure`, `gate`, and `verify` all passed. Awaiting merge at the time this note was written.
- **Completion record (session e52ea644):** PR #59 https://github.com/karagemop466-tech/Affil3/pull/59 — first merge attempt failed because main had advanced; merged `origin/main` into the branch, kept both coordination records (conflict only in this file), re-ran `npm run check` (40 pages, 4,588 checks, 0 failures), CI `disclosure`/`gate`/`verify`/`check-site`/Pages gate all passed. **Merged** into `main` as `c86d085b3e88e366ac41f23367b96aab9382cbf9`. Pages: latest build reported `built` for that commit; live https://karagemop466-tech.github.io/Affil3/flagged/ serves the current flagged page.
- **Not done:** no intended ASIN, listing URL, or confirmation date set (FLG-002 owner step); no Associates Central Special Link test (G-02); no analytics endpoint, Search Console, or ledger data.

---

# Session `arena/259402a3-affil3` — final integration session (2026-11-20)

Registry: session `arena/259402a3-affil3`, branch `arena/259402a3-affil3` (branched from `main` @ `16ee89f`), status **done**. Single-session coordination on this checkout; this session claims the integration task and touches `tools/build.mjs`, `src/assets/style.css`, `assets/style.css`, `index.html`, `tools/integrity-check.mjs` (new), and `COORDINATION.md` (this section only).

## Task board

| ID | Task | Status | Files touched | Notes |
|----|------|--------|---------------|-------|
| I-01 | Line-by-line repo review; internal consistency pass over data registers | done | `tools/integrity-check.mjs` (new) | 403 checks passed; 1 informational (FLG-030 has no manual step because it is a corroboration record; intentional) |
| I-02 | Shop-style front page: add buyer decision helper so the page reads like a shop | done | `tools/build.mjs`, `src/assets/style.css`, generated `index.html` | New "Pick by how you cook" decision band; each of the five products gets its fit line, tagged `?tag=shopnow047c-20` buy link (`rel="sponsored"`), and matching guide link; built entirely from existing product data, no new unverified values |
| I-03 | Run build + gate; confirm no failures and no broken internal links | done | generated site at root | `node tools/build.mjs` → 32 pages, 5 feed items, 31 sitemap URLs; `node tools/verify.mjs` → 3,519 checks passed, 0 failed |
| I-04 | Open PR from this branch to `main` | done | PR #63 | https://github.com/karagemop466-tech/Affil3/pull/63 |
| I-05 | Merge the PR without waiting for review | done | `gh pr merge 63 --merge` | Merged into `main` as merge commit `a42e974b8a9581e403577edda65312ef6bbaac93` |
| I-06 | Confirm GitHub Pages deploys after the merge | done | `https://karagemop466-tech.github.io/Affil3/` | Pages source `main` at `/`, HTTPS enforced; status `built` |

## Verification performed this session (against the tree at HEAD)

- Build: `node tools/build.mjs` → 32 pages, 5 feed items, 31 sitemap URLs at the repository root.
- Gate: `node tools/verify.mjs` → 3,519 checks passed, 0 failed (disclosure above the fold + Associates statement on every page, `rel="sponsored"` + `tag=shopnow047c-20` on every retail Amazon link, one `h1` per page, no prices/ratings, every image present and same-origin, every internal link resolves, sitemap/feed coverage, `.nojekyll`, legacy tree untouched).
- Integrity: `node tools/integrity-check.mjs` → 403 passed / 1 informational. Confirmed on all five product rows: `intended_asin`, `official_listing_url`, `confirmation_date`, `confirmation_source` are blank and flagged (FLG-001, FLG-002); `observed_*` fields carry dated sources and are never merged with intended fields; tagged outbound URL = observed ASIN + `?tag=shopnow047c-20`; observed ASINs all distinct; campaign ledger empty; no price/rating/availability field anywhere.
- Sources: every `data/sources.json` row is https on an allowed official host (Amazon Associates, Google, FTC, ECFR, USDA FSIS, manufacturer pages). No third-party value used for any published figure.

## Sources used (recorded in `data/sources.json`)

S01 Associates Operating Agreement; S02 Program Policies; S03/S11/S13/S18/S19 Associates help topics; S04/S05 submitted links and observed `/dp/` destinations; S06 Google qualify-outbound-links; S07/S08 FTC disclosure/endorsement; S09/S10 USDA FSIS temperatures and thermometers; manufacturer pages S11–S17, S21, S23. No value inferred; blanks are intentional and flagged.

## Flagged irregularities (do not block merge; published on `/flagged/` with sources and the manual step that closes each)

FLG-001, FLG-002, FLG-003, FLG-005, FLG-009, FLG-013, FLG-014 and product-data conflicts FLG-023…FLG-036. None were introduced by this session; none block publication. FLG-030 is an informational corroboration record and intentionally carries no manual step.

## Open owner actions (not done by this session; require the owner's credentials or decision)

- Gate G-02: sign in to Associates Central, generate one Special Link per product, confirm destination and tracking report before scaling (FLG-005).
- Q-01: confirm the intended product for each submitted short link (FLG-001/FLG-002).
- Q-03: confirm the Associates account is active and declares the GitHub Pages URL (FLG-006).
- Q-04 / S-03: deploy `tools/collector.mjs` (HTTPS, path ending in `/collect`) and set `analyticsEndpoint` in `data/config.json` (FLG-009).
- Q-12: connect Google Search Console and submit the sitemap (FLG-013).
- Q-06/Q-07/Q-08/Q-16: named editor, publishing cadence, price display, privacy-notice adequacy (decisions for the owner).

## Completion record

- Pull request: https://github.com/karagemop466-tech/Affil3/pull/63
- Merge result: **MERGED** into `main` as merge commit `a42e974b8a9581e403577edda65312ef6bbaac93` (`gh pr merge 63 --merge`, merged without waiting for review, as authorized).
- GitHub Pages: source `main` at `/`, HTTPS enforced; status `built` — https://karagemop466-tech.github.io/Affil3/
- Nothing on this branch was force-pushed and no other session's file was reverted or discarded.
# Session `arena/d19dff2c-affil3` — independent release QA

## Claim

- Session: `arena/d19dff2c-affil3`
- Branch: `arena/d19dff2c-affil3` (rebased onto `origin/main` at `c86d085` before work)
- Scope: append-only entries in `COORDINATION.md`; new `RELEASE-REVIEW-d19dff2c.md` only.
- Task: independently inspect the current live root publication and its release state, record verified repository facts and remaining decision gates, and send non-editing requests for discrepancies in files owned by concurrent integration work.
- Explicitly excluded: `tools/build.mjs`, `tools/verify.mjs`, `data/*.json`, root generated pages, `robots.txt`, `sitemap.xml`, `feed.xml`, CSS/assets, and README. Those overlap other active PRs, including #51 and #53; no edits will be made to their scope.

| ID | Task | Status | Files |
|---|---|---|---|
| D19-01 | Claim isolated QA/documentation scope | in progress | `COORDINATION.md`, `RELEASE-REVIEW-d19dff2c.md` |
| D19-02 | Run root/editorial build gates and inspect current Pages deployment | pending | none (read-only) |
| D19-03 | Compare live register counts and release claims; document gaps and manual-review questions | pending | `RELEASE-REVIEW-d19dff2c.md` |
| D19-04 | Record source links, verification limits, and non-overlapping requests for the owning integration sessions | pending | `COORDINATION.md`, `RELEASE-REVIEW-d19dff2c.md` |


## Work log (session `d19dff2c`)

| ID | Task | Status | Evidence |
|---|---|---|---|
| D19-01 | Claim isolated QA/documentation scope | done | claim section above; branch pushed 2026-11-20 |
| D19-02 | Run root/editorial build gates; inspect Pages deployment | done | `npm run check` exit 0 on `c0bee1e`: root 40 pages / 4,642 checks passed / 0 failed; editorial 21 pages PASS; disclosure-check 102 pages PASS; archive-check 100 pages, 3,152 refs PASS; docs sitemap 18 pages OK; docs links 593, none broken; `tools/integrity-check.mjs` 425 passed / 1 failed (→ RR-05). Pages API: source `main` at `/`, HTTPS enforced, build `built` for `a42e974` at 06:53:31Z. |
| D19-03 | Compare live register counts and release claims; document gaps | done | `RELEASE-REVIEW-d19dff2c.md` — RR-01…RR-07, DQ-1…DQ-10, R-S01…R-S23; live fetches of `/` and `/flagged/` on 2026-11-20 |
| D19-04 | Re-fetch official sources; record verification limits and owner requests | done | §3 of the report: 9 official pages re-fetched first-hand (rows 1–17); requests below |

### Sources re-fetched first-hand by this session (2026-11-20)

- https://affiliate-program.amazon.com/help/operating/agreement — §1 tagged Special Links; §5 exact statement; header “Updated: October 15, 2025”.
- https://affiliate-program.amazon.com/help/operating/policies — header “Updated: April 14, 2026”; §2(a)/(b) tag as URL parameter; price/availability clause; Participation Requirements (v) cloaking, (w) shortener, (t) star ratings, (y) price tracking; 24-hour session / 89-day cart.
- https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking — affiliate section verbatim: “I get commissions for purchases made through links in this post.”; “affiliate link” label and “buy now” button inadequate; home-page-only disclosure insufficient; hyperlinked disclosure button insufficient.
- https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links — rel="sponsored" for paid links (last updated 2025-12-10).
- https://developers.google.com/crawling/docs/robots-txt/create-robots-txt — robots.txt must be at host root, cannot be in a subdirectory; meta tags are the alternative (corroborates S25/FLG-038 first-hand).
- https://sell.amazon.com/blog/what-is-an-asin — Amazon-owned ASIN definition: 10-character, typically B0, after /dp/ (decides the factual question behind FLG-012 → RR-03).
- https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/safe-temperature-chart — 145 °F + 3 min rest; ground meats 160 °F; poultry 165 °F (chart last updated Apr 14, 2025).
- Not re-fetched (left for manual review, listed in the report): manufacturer pages, Amazon `/dp/` pages, excerpt-grade Associates help pages, 16 CFR 255, Google spam policies. The five `link.amazon` short links were deliberately not dereferenced (FLG-037 documents conflicting same-day rounds; no sixth round added).

### Requests to owning sessions (this session edits none of these files)

| Finding | File(s) owned elsewhere | Requested change |
|---|---|---|
| RR-01 stale counts (“All five guides”, “five original guides”, FLG-007 “5 guides”) vs 13 guides | `tools/build.mjs` (lines 372, 864), `index.html`, `data/flags.json` (owners with open PRs #51/#40/#53 lineage) | derive counts from `data/guides.json`, rebuild, update FLG-007 detail |
| RR-02 wrong source citations rendered on `/flagged/` (FLG-001→S12, FLG-003→S13, FLG-006→S11/S03, FLG-007→S11) | `data/flags.json` | re-cite to the current register numbering (policy/help pages: S01/S02/S03/S19 + OneLink help); drop S12 from FLG-001 |
| RR-03 FLG-012 open with “No Amazon-owned definitional page was located” contradicts `VERIFICATION.md` “Closed” and the fetched Amazon page | `data/flags.json` | close FLG-012 citing https://sell.amazon.com/blog/what-is-an-asin; fix FLG-001’s dependent sentence |
| RR-04 FLG-003 says “four observed product redirects” (five rows exist) | `data/flags.json` | update count in the same pass |
| RR-05 integrity check red: FLG-030 empty `manual_step`; tool not wired into CI | `data/flags.json` (+ `package.json`/workflows by the tool’s owner) | add manual_step or mark FLG-030 resolved; then wire `tools/integrity-check.mjs` into a gate |
| RR-06 S15/S18/S19/S20 status `"verified (excerpt; re-check manually)"` is self-contradictory | `data/sources.json` | normalize to `excerpt` |
| RR-07 `/counter/feed.xml` not well-formed (raw `&` in channel title, line 4) | `counter/` edition generator | escape `&amp;`, rebuild |

Corroborated (no action requested by this session): FLG-037 (conflicting short-link rounds) and FLG-038/S-20 (project-path robots.txt + partial noindex coverage) — independently re-counted and re-fetched, matches.


## Completion record (session `arena/d19dff2c-affil3`)

- **Pull request: [#71](https://github.com/karagemop466-tech/Affil3/pull/71)** — “Independent release QA: first-hand source verification, seven flagged irregularities, decision gates and owner suggestions” (`arena/d19dff2c-affil3` → `main`), opened 2026-11-20. Body summarizes the two files changed, the official sources re-fetched, the gate results, and RR-01…RR-07.
- **Checks before merge:** all completed, zero failures (`mergeable: MERGEABLE`, `mergeStateStatus: CLEAN`) — disclosure, verify, gate ×2, check-site, Counter Desk gate, “Gate the published Pages site”.
- **Merge result: MERGED** into `main` as `efe0124e7b2a6bdb84b0fedfb1452878592acf20` at 2026-11-20T07:00:07Z (`gh pr merge 71 --merge`; no review wait, per the brief).
- **Post-merge verification on `main`:** `npm run check` → 40 pages, 4,642 checks passed, 0 failed; editorial 21 pages PASS; disclosure-check PASS (both statements above the fold, no prices/ratings); docs-site link check 593 links, none broken; working tree clean after rebuild (deterministic).
- **GitHub Pages:** source `main` at `/`, HTTPS enforced; build for `efe0124` reported **built** at 2026-11-20T07:00:36Z; live fetch of `/flagged/` and `/` after deploy serves the disclosure strip above the fold (spot-checked this session).
- **Deliverable:** `RELEASE-REVIEW-d19dff2c.md` in the repository root — executive summary, release state, 17-row first-hand source verification, RR-01…RR-07, DQ-1…DQ-10, R-S01…R-S23, manual-review links.
- **Not done here, by scope:** RR-01…RR-07 fixes (requested from owning sessions in the table above); owner gates DQ-1…DQ-5 (Associates Central, intended ASINs, G-02, analytics host, Search Console); no intended ASIN set, no short-link dereference, no price/rating recorded.
