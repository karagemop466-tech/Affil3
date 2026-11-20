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
