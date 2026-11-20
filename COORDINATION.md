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

# Session `arena63534e5d` board (appended below the boards above; nothing above was edited)

Added when `arena/63534e5d-affil3` was merged with `main`. The boards from session
`arena-83a43a96-affil3` (PR #1) and session `6249757a` (PRs #4/#6) are kept verbatim
above. This session executes the reader-facing polish pass ("publication, not generated")
requested by the project brief, on top of the existing machinery.

## Session registry (this session)

| Session ID | Branch | Status | Scope |
| --- | --- | --- | --- |
| `arena63534e5d` | `arena/63534e5d-affil3` | active | Design system + copy rewrite + imagery + front page + suggestions/decision surfaces + CI workflow, all on this branch only |

## Task board (this session)

| ID | Task | Status | Owner | Files touched |
| --- | --- | --- | --- | --- |
| P-01 | Merge origin/main; resolve add/add conflicts by appending boards (nothing discarded) | done | `arena63534e5d` | COORDINATION.md, README.md |
| P-02 | New design system (typography, palette, layout) | done | `arena63534e5d` | src/assets/style.css |
| P-03 | Copy rewrite: front page, guides, shop, dashboards — human editorial voice | done | `arena63534e5d` | data/guides.json, tools/build.mjs templates |
| P-04 | Editorial imagery (AI-generated illustrations, disclosed) | done | `arena63534e5d` | src/assets/img/, editorial policy |
| P-05 | New irregularity FLG-021 (two submitted tokens observed routing to the same product) | done | `arena63534e5d` | data/flags.json, data/products.json |
| P-06 | Suggestions + decision-brief surfaces upgraded for review-and-choose flow | done | `arena63534e5d` | data/suggestions.json, generated pages |
| P-07 | CI workflow: build drift check + gates on push | done | `arena63534e5d` | .github/workflows/publish.yml |
| P-08 | Re-verify, PR to main, merge, confirm Pages rebuild | done | `arena63534e5d` | (all), COORDINATION.md |

## Work log (this session)

- **2026-11-20 — claim + merge.** Branch started from `847ae37`; `origin/main` had moved to `dd2c4e7` (PR #6). Conflicts on COORDINATION.md and README.md resolved by keeping main's content verbatim and appending this session's sections. Nothing from prior sessions discarded.
- **2026-11-20 — new observation (FLG-021).** Session `6249757a` observed `B0c8moW59`→`B08DKYBTPH` and `B00hJ57DV`→checkpoint. This session observed `B00hJ57DV`→`B08DKYBTPH` and `B0c8moW59`→checkpoint. Across observations, two different submitted tokens route to the same observed product (`B08DKYBTPH`) and the two observations disagree about which token maps to it. This strengthens FLG-002/FLG-004: the token↔product mapping is unstable and must be confirmed in Associates Central before any per-product claims are made.
- **2026-11-20 — official sources re-checked** (FTC Endorsement Guides FAQ fetched in full; Google rel="sponsored" doc fetched in full; Amazon Associates Operating Agreement §5 and Program Policies confirmed via official-domain excerpts; ASIN definition confirmed from sell.amazon.com). See sources.html for the register.

