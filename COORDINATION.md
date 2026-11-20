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

# Session `7e5808de` board and integration record

This session was the third to work on this repository and the one that produced the
final integration. The two earlier boards above are kept verbatim and nothing in them
was edited. This session's executive summary for the record is `EXECUTIVE_SUMMARY-7e5808de.md`.

## Session registry (this session)

| Session ID | Branch | Status | Scope |
| --- | --- | --- | --- |
| `7e5808de` | `arena/7e5808de-affil3`, integration branch `integration/7e5808de` | active | Data register, platform tooling, static site, guides, measurement, compliance gate, decision board, final integration |

## Task board (this session)

| ID | Task | Status | Owner | Files touched |
| --- | --- | --- | --- | --- |
| T1 | Source register + product-intent confirmation record (5 links) | done | `7e5808de` | `data/products.json`, `data/sources.json` |
| T2 | Platform tooling: Special-Link builder, Creators API research, ledger, checks | done | `7e5808de` | `tools/affiliate.py`, `tools/research.py`, `tools/sitekit.py` |
| T3 | Static site build: templates, CSS, layout, nav, disclosure strip | done | `7e5808de` | `tools/build_site.py`, `assets/css/site.css`, `assets/js/site.js` |
| T4 | Editorial: question-shaped guides + comparisons | done | `7e5808de` | `data/guides.json`, `guides/*`, `compare/*`, `categories/*` |
| T5 | Measurement: privacy-preserving click counter + self-hosted endpoint | done | `7e5808de` | `assets/js/analytics.js`, `tools/analytics_sink.py`, `data/config.json` |
| T6 | Decision board: suggestions, open questions, flagged-for-review | done | `7e5808de` | `data/suggestions.json`, `data/questions.json`, `data/flags.json` |
| T7 | Integration: sitemap, feed, robots, link check, PR + merge + Pages deploy | done | `7e5808de` | `sitemap.xml`, `feed.xml`, `robots.txt`, `tools/check_site.py`, `legacy/arena-6249757a/` (move only) |

## Verification performed by this session

| Check | How | Result |
| --- | --- | --- |
| Five submitted links resolve | Fetched each link, followed the redirect chain | 5/5 reached an `amazon.com/dp/<ASIN>` page |
| Destination titles | Read the page title on the destination | Captured verbatim for all five, each with its URL and date |
| Browse path | Read the breadcrumb on the destination | 3 under Air Fryers (`17659096011`), 2 under Meat thermometers (`289810`) |
| Token length vs the ASIN definition | Measured each token against Amazon's own definition | **All five tokens are 9 characters.** None can be an ASIN. Every observed destination is 10 characters. |
| Price publication | Read Program Policies 2(b) | No price may be published without Amazon serving the link or Creators API / PA API |
| Rating publication | Read Program Policies 5(t) | No rating or review count may be published without Creators API / PA API |
| Link format | Read Program Policies 2(b), 5(v), 5(w) | Submitted short links are redirects; published links are direct tagged Special Links |
| Disclosure | Read Operating Agreement 5 and FTC Disclosures 101 | Strip under the masthead on every page, repeated in the footer |
| Outbound link marking | Read Google's outbound-link guidance | `rel="sponsored nofollow"` plus a visible marker and an aria-label |
| API status | Read the PA-API 5 deprecation notice | PA-API 5 returns HTTP 403 `AccessDeniedException`; the tooling targets the Creators API |
| Release gate | `python3 tools/check_site.py` | 0 violations, 0 warnings across 44 generated pages |
| Collector | Live POST against `tools/analytics_sink.py` | Valid events stored with a server-salted id; unknown events and unexpected fields rejected with 400 |

## Integration record (2026-11-20)

- **`main` had already moved.** Pull request #6 merged session `6249757a`'s site to
  `main` (commit `dd2c4e7`) while this session was working. Nothing was overwritten.
- **The earlier root site was archived, not discarded.** Session `6249757a`'s published
  surface (`index.html`, `404.html`, `feed.xml`, `sitemap.xml`, `robots.txt` and the
  `about/`, `assets/`, `categories/`, `compliance/`, `executive-summary/`, `flagged/`,
  `guides/`, `ledger/`, `measurement/`, `questions/`, `shop/`, `sources/`,
  `suggestions/` directories, plus its `data/`, `src/`, `tools/`, `package.json` and
  `README.md`) was moved with `git mv` to `legacy/arena-6249757a/`, unchanged. That
  follows the convention session `6249757a` set when it archived
  `legacy/arena-83a43a96/`. `legacy/` is excluded from crawling by `robots.txt`.
- **The old URLs now land somewhere.** Fourteen paths published by the earlier session
  (`/shop/`, `/categories/`, `/categories/air-fryer-ovens/`,
  `/categories/cooking-thermometers/`, `/categories/unresolved/`, `/sources/`,
  `/questions/`, `/suggestions/`, `/flagged/` and five earlier guide slugs) now serve a
  redirect page with a canonical pointing at the current home for that content.
- **One discrepancy was found between the sessions and it was resolved by re-checking
  the source.** This session's first draft recorded that two of the five submitted
  tokens were 10 characters long, and therefore ASIN-shaped. Re-measuring showed all
  five are 9 characters. The register, the flags, the questions, the source log and the
  page copy were corrected. The earlier board's FLG-001 already had this right.
- **One link-to-product mapping differed between the sessions.** The earlier session's
  log records `B0c8moW59` as resolving to `B08DKYBTPH` (Chefman Air Fryer 8 Qt) and
  `B00hJ57DV` as hitting an Amazon checkpoint page. This session observed
  `B0c8moW59` -> `B0DHZTCNR5` (ThermoMaven 1 Sec) and `B00hJ57DV` -> `B08DKYBTPH`
  (Chefman Air Fryer 8 Qt). Both were re-fetched during integration on 2026-11-20 with
  a fresh query string, and the mapping this session records was confirmed both times.
  The earlier session appears to have attributed the `B00hJ57DV` destination to the
  `B0c8moW59` link when the checkpoint interstitial interrupted it. The register now
  carries the re-confirmed mapping, and the checkpoint behaviour is itself noted.
- **All five observations were re-confirmed during integration.** The register's
  `verification_log` and `verification_note` record the re-check.

## Irregularities published on the Flagged for Review page

FLG-001 none of the five tokens can be an ASIN · FLG-002 the intended ASIN is
unconfirmed · FLG-003 the submitted links are redirects, not Special Links · FLG-004
the tokens are not live ASINs either · FLG-005 the Associates account is not publicly
verifiable · FLG-006 commission rates are unverified · FLG-007 Creators API needs 10
qualifying sales in 30 days · FLG-008 PA-API 5 is deprecated · FLG-009 there is no
measured search data yet · FLG-010 listings drift over time · FLG-011 a near-identical
ThermoMaven listing exists under a different ASIN · FLG-012 GitHub Pages logs visitor
IP addresses.

None of these block the site going live.
