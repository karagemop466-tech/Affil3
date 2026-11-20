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

# Session arena-6ca11b63 board (this session)

Repo: `karagemop466-tech/Affil3` · Base: `main @ 847ae37` · Working branch: `arena/6ca11b63-affil3`

## Session and branch rules

- **Session ID:** `arena-6ca11b63` (the only session that has written to this repo as of this claim; no other session claims, branches, or log entries existed when this board was created).
- **Branch deviation:** the task brief asks for `session-<id>/<task>` branches. The Arena session is bound to a single branch, `arena/6ca11b63-affil3`, and must not switch or create branches. All tasks below are therefore committed to that one branch. Scopes are still kept separate by directory (see "Files touched").
- **Integration:** this session is also the final integration session. Shared outputs (`docs/`, `data/`, `README.md`, `COORDINATION.md`) are changed only by this session.

## Task board

| ID | Task | Status | Owner | Files touched |
|---|---|---|---|---|
| T01 | Repo review; irregularity log | done (on branch `arena/6ca11b63-affil3`; not on `main`) | arena-6ca11b63 | `COORDINATION.md`, `data/flags.json` |
| T02 | Product-intent confirmation records (intended ASIN vs observed redirect) | done (on branch; P3/P4 open, see re-fetch log) | arena-6ca11b63 | `data/products.json` |
| T03 | Source register (official URLs, retrieval date, what each supports) | done (on branch; not on `main`) | arena-6ca11b63 | `data/sources.json` |
| T04 | Static site generator + pages (landing, category, dashboard) | done (on branch; not on `main`) | arena-6ca11b63 | `scripts/build_site.py`, `docs/**` |
| T05 | Compliance: Associates statement, disclosure strip (every page + footer), `rel="sponsored"` on every outbound product link | done (on branch; not on `main`) | arena-6ca11b63 | `scripts/build_site.py`, `docs/**` |
| T06 | Measurement: outbound-click hook, self-hosted endpoint **gated**, campaign ledger (empty) | done on branch (endpoint gated; not on `main`) | arena-6ca11b63 | `docs/assets/analytics.js`, `data/campaign_ledger.csv` |
| T07 | Editorial: question-led guides, sitemap, RSS feed | done (on branch; not on `main`) | arena-6ca11b63 | `data/guides.json`, `docs/guides/**`, `docs/sitemap.xml`, `docs/feed.xml`, `docs/robots.txt` |
| T08 | Questions, suggestions (decision board), executive summary, Flagged for Review page | done (on branch; not on `main`) | arena-6ca11b63 | `data/questions.json`, `data/suggestions.json`, `docs/questions.html`, `docs/suggestions.html`, `docs/executive-summary.html`, `docs/flagged.html` |
| T09 | Validation gate (`check_site.py`): row-level source links, disclosure presence, sponsored rel, internal links | done (on branch; negative-tested) | arena-6ca11b63 | `scripts/check_site.py` |
| T10 | Integration: rebuild, re-verify combined data, gate, PR to `main`, merge, enable/confirm GitHub Pages | BLOCKED on owner decision: `main` now holds another session's integrated site (PR #4, Pages on `main /docs`); see Integration record | arena-6ca11b63 | all shared outputs |

## Claim log

- 2026-11-20 · arena-6ca11b63 · claimed T01–T10 (single session). Pushed before any other file changes.

## Verification log

All checks were performed on 2026-11-20 (UTC). Full source list: `data/sources.json`. Irregularities: `data/flags.json` (published at `docs/flagged.html`).

- Short links fetched via the verification fetch tool (`fetch_page`). Observed final URL, title, and category breadcrumb recorded per link. See T02 in `data/products.json`.
- Direct `/dp/` fetches for the **intended** ASINs returned errors (also `/gp/product/` for B04G1MEwY). Recorded as unverified, not as nonexistent. The identifiers also fail the 10-character format (9 characters), which is the more likely explanation; not confirmed.
- Validation gate (`scripts/check_site.py`) was negatively tested: a copy with a stripped `rel="sponsored"`, a removed disclosure, a broken internal link and an unsourced table row fails with all four reported.
- Official policy text read from `affiliate-program.amazon.com` (Operating Agreement §2, §3, §5; Participation Requirements §1–§6; Commission Income Statement §2). Commission rate schedule requires Associates sign-in: **not verified**.
- FTC "Disclosures 101 for Social Media Influencers" (ftc.gov) read in full.
- Google Search Central "Qualify your outbound links" read (rel="sponsored").
- GitHub Docs "Creating a GitHub Pages site" read (publishing source `/docs`, `.nojekyll`, propagation delay).

## Irregularities (summary; full detail in `data/flags.json`)

0. All five identifiers in the submitted links are **9 characters** with lowercase letters. The ASIN format in SRC-12 is 10 characters, typically starting "B0". Length checked with a script, not by eye. Flag FLG-01. Nothing was corrected.
1. Four of five submitted short links resolve to a product whose ASIN differs from the ASIN in the link path. One resolves to an Amazon interstitial page.
2. Observed redirect targets contain no `tag=` parameter; the tracking ID `shopnow047c-20` is not visible in them.
3. Product prices and rating counts for the main listing were not captured in a verifiable way and are left blank.
4. Source-register IDs `S01…S30` and `FLG-003` referenced in the brief are **not present in this repository**. They are not mapped or assumed here.
5. The "five defined events" for measurement are referenced in the brief but not defined anywhere in the materials. A proposed list is marked as proposed.
6. GitHub Pages is static hosting. A "self-hosted analytics endpoint" and an outbound-click counter that stores data cannot run on it. Built as a gated hook; see Questions Q07.


---

# Integration record (session arena-6ca11b63)

Written when this session merged `origin/main` (PR #1, session arena-83a43a96) into its branch. Both records are kept in full above and below; neither was edited.

## What was found on `main` at merge time

- `main` contained PR #1 (merged) from `arena/83a43a96-affil3`: a root-level site (`index.html`, `products.html`, `guides/`, `feed.xml`, `sitemap.xml`, `assets/`, `EXECUTIVE_SUMMARY.md`, and others). GitHub Pages was enabled from `main` `/` and was live from that site.
- PR #2 from `arena/114f47c4-affil3` was open and untouched by this session.
- The remote also holds branches for other sessions: `arena/0a417943`, `114f47c4`, `238c8ddb`, `35d0727e`, `59aebafb`, `6249757a`, `772f3220`, `7e5808de`, `83a43a96`, `93cee724`, `bdcb1fa8`, `be9ed869`. This session has not read, merged, or changed any of them.

## What this session did about it

1. **Did not overwrite or delete** the root-level site from PR #1. It is moved, with `git mv`, to `archive/session-83a43a96/` so its history follows the files. Its internal relative links are unchanged.
2. **Integrated** the generated site in `docs/` (this session's build). `docs/` is the single GitHub Pages source, so the public URL stays the same: https://karagemop466-tech.github.io/Affil3/
3. **Pages source** is changed from `main` `/` to `main` `/docs` after the PR merges.
4. **Merge conflict:** `COORDINATION.md` existed on both sides. Resolved by keeping the PR #1 board verbatim and appending this record. Nothing was dropped.
5. **Overlap on verified facts:** PR #1's `products.html` says the intended ASIN should be checked and the short links were not resolvable from its sandbox. This session resolved the four observed short links and recorded their destinations (see `data/products.json`). Its claims that the short links are not resolvable are superseded by the observed results. Its no-claim-of-invalid-links position is kept.
6. **Analytics:** PR #1's `assets/js/app.js` posts to `/analytics/collect`, which GitHub Pages cannot serve (it notes this itself). The new site's `docs/assets/analytics.js` is inactive until an endpoint is set. The archived script is not live.

## Status of the other sessions

No other session's branch has been merged or changed by this session. Sessions whose branches are not merged are not represented in `main`. Each would need its own integration to be included, and any of them that opens a PR into `main` should be reconciled against this record.

## Re-fetch log (2026-11-20, session arena-6ca11b63)

Purpose: settle the P3/P4 mapping before publishing it.

| Short link | Earlier reading (this session) | Re-fetch 2026-11-20 (this session) | Other session's board (same date) | Result |
|---|---|---|---|---|
| `link.amazon/B00hJ57DV` (P3) | redirect to `amazon.com/dp/B08DKYBTPH` | redirect to `amazon.com/dp/B08DKYBTPH` (Chefman 8 Qt TurboFry) | reported as a checkpoint page | **Open.** Readings conflict across sessions. |
| `link.amazon/B0c8moW59` (P4) | Amazon checkpoint/interstitial | Amazon checkpoint/interstitial ("Continue shopping") | reported as `B08DKYBTPH` | **Open.** Readings conflict across sessions. |

Conclusions:

- This session's two readings are self-consistent. Another session's readings for the same links are reversed. Results may vary by visit (checkpoint tokens are per-session).
- Neither mapping is published as settled. Pages now say P3 and P4 are open. Changed in `scripts/build_site.py`, `data/analysis.json`, `data/questions.json`, and FLG-02 in `data/flags.json`.
- Intended IDs remain 9 characters and unverified (FLG-01).
- To close P3/P4: a repeatable check from a clean session, logged here with the date, the link, and the final URL.

## Integration status (2026-11-20)

- Branch `arena/6ca11b63-affil3` is pushed (head `103f6a7` at last push). It contains this session's data, scripts, `docs/`, and the archived PR #1 site under `archive/session-83a43a96/`.
- PR #3 (this branch → `main`) is **CONFLICTING**. `main` moved to `5d2e7ab` (PR #4 from `arena/6249757a-affil3`). That PR also builds into `docs/`, adds `package.json` and `tools/`, and writes `data/products.json`, `data/flags.json`, and others with different schemas.
- Merging PR #3 would overwrite another session's live Pages output and its `data/` files. **Not done.** Choosing which integrated site goes live is an owner decision (FLG-017).
- Options for the owner: (a) keep `arena-6249757a`'s site and close PR #3 after moving any unique content from this branch; (b) keep this site and replace theirs; (c) merge both under separate paths, e.g. `docs/` for one and a different folder for the other.
- Pages is currently `main` at `/docs`, building from PR #4.

