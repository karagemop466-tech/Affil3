# COORDINATION.md — shared task board

Repository: `karagemop466-tech/Affil3` · Working branch: `arena/bb0a6985-affil3` (base `847ae37`, `main`)

Live site (after deploy): https://karagemop466-tech.github.io/Affil3/
Flagged for review (published with source links): https://karagemop466-tech.github.io/Affil3/flagged/

## Session rules used here

- One agent session (`bb0a6985`) is working on this repository. No other session has claimed a task.
- The session is bound to a single branch, `arena/bb0a6985-affil3`. Per the operator instruction, the `session-<id>/<task>` branch layout in the brief was **not** used; all tasks are committed to this branch, and it is the integration branch for the PR to `main`.
- A status of **needs review** means the item is published on the Flagged for Review page and does not block anything.
- Shared outputs (data, nav, index) were written by the same session that owns the tasks, so no separate integration session was needed. Integration checks are listed in the final section.

## Task board

| ID | Task | Status | Owner (session) | Files touched | Sources | Verification | Irregularities |
|---|---|---|---|---|---|---|---|
| T-01 | Review repo; create this board | done | bb0a6985 | `COORDINATION.md`, `README.md` | SRC-OA, SRC-PP, SRC-GOOG-QOL, SRC-ECFR-255-5, SRC-GHP-PUBLISH, SRC-ASIN-NAME | `git ls-files` at 847ae37 = README.md only; no board existed | FLG-001, FLG-010 |
| T-02 | Product-intent confirmation record (intended ASIN, official URL, date, source; observed redirect kept separate) | done, intended ASIN **blank** | bb0a6985 | `src/data/products.json` | SRC-LINK-01..05, SRC-AMZ-01/02/04/05 | Each short link followed; observed ASIN read from redirect URL; each row has a source link | FLG-002, FLG-004, FLG-005 |
| T-03 | Special Link validation (one link per product, destination + tracking report) | **blocked on owner** (needs Associates account login) | bb0a6985 | — | SRC-OA §1 | Not performed. Supplied links kept as outbound, marked sponsored | FLG-003, FLG-009 |
| T-04 | Compliance gate: disclosure under masthead and in footer; sponsored rel on Amazon links; source-link check | done | bb0a6985 | `scripts/verify.mjs`, `scripts/build.mjs` | SRC-OA §5, SRC-GOOG-QOL, SRC-ECFR-255-5 | `node scripts/verify.mjs` passes; negative test (removing `sponsored`) fails as expected | FLG-008 (policies partly reviewed) |
| T-05 | Static site: landing page, category pages, dashboard pages | done | bb0a6985 | `scripts/build.mjs`, `src/assets/style.css`, `src/data/*.json` | As each row | Build: 14 pages; internal links 663/663 resolve | — |
| T-06 | Editorial hypotheses / guides index (question-shaped working titles) | done as plan only; no guide drafted | bb0a6985 | `src/data/guides.json` | Listing titles | Each claim is quoted from a title, not verified | FLG-011, FLG-012 |
| T-07 | Suggestions section (options to choose from before any change) | done, all **awaiting owner choice** | bb0a6985 | `src/data/suggestions.json` | As cited per suggestion | n/a (no factual claims) | — |
| T-08 | Questions and information gaps | done | bb0a6985 | `src/data/questions.json` | As cited | n/a | FLG-014 |
| T-09 | Research findings and executive summary | done | bb0a6985 | `src/data/findings.json`, `build.mjs` | As cited per finding | Counts computed from data files | — |
| T-10 | Campaign ledger (empty, provenance columns) | done, **0 rows** | bb0a6985 | `src/data/ledger.json` | None (no rows) | n/a | — |
| T-11 | Click counter + self-hosted analytics endpoint + five events | **not done** (needs hosting decision and the five event definitions) | — | — | — | — | FLG-007 |
| T-12 | Publish to GitHub Pages (Actions workflow) | in progress at time of writing; see log | bb0a6985 | `.github/workflows/pages.yml` | SRC-GHP-PUBLISH | Deploy result recorded in the log below | — |
| T-13 | Flagged for Review page with source links | done | bb0a6985 | `src/data/flags.json` | As cited per flag | n/a | FLG-001 … FLG-014 |
| T-14 | Series extras from the brief: nav labels, shipped RSS feed, Search Console, reader capture (SG-27…SG-30) | **not done** (SG-27..SG-30 are not defined in the repo; Search Console needs owner verification) | — | — | — | — | FLG-001 |

## Claim log

- 2026-11-20 — `bb0a6985` claimed T-01 to T-14 for `arena/bb0a6985-affil3`. Claim committed with the first data files.

## Work log

- 2026-11-20 — Followed the five supplied short links. Four resolved to amazon.com product pages (ASINs B0CDY277D3, B09B7SB46R, B08DKYBTPH, B0DZFD6R9Z). One (`B00hJ57DV`) reached an Amazon checkpoint page on two attempts (FLG-005).
- 2026-11-20 — Found that all five supplied codes are 9 characters, not 10-character ASINs (FLG-002).
- 2026-11-20 — Found that none of the four observed product URLs carries `tag=shopnow047c-20` (FLG-003). Special Link validation not performed (no Associates access).
- 2026-11-20 — Read Operating Agreement §1, §2, §5 (required statement) on affiliate-program.amazon.com. Read Program Policies chunk 0 of 11 only (FLG-008).
- 2026-11-20 — Read Google's outbound-link documentation (rel="sponsored") and the eCFR section 255.5 title.
- 2026-11-20 — Built the site with `node scripts/build.mjs` and checked it with `node scripts/verify.mjs`. Both pass. Negative test confirmed the sponsored gate fails when `sponsored` is removed.

## Irregularities for review

See the Flagged for Review page for full detail, sources and actions. Summary:

- **FLG-001 (High)** — Source register cited in the brief (S01, S07, S24, SG-27…30, FLG-003) is not in the repo.
- **FLG-002 (High)** — Supplied codes are 9 characters, not ASINs. Intended ASIN fields are blank.
- **FLG-003 (High)** — Short-link compliance unresolved. None of the observed product URLs carries the Tracking ID.
- **FLG-005 (High)** — P03 short link reached a checkpoint page only.
- **FLG-007 (High)** — Analytics, click counter and five events not built / not defined.

## Integration checklist (final)

- [x] Data re-verified line by line against the source register (`src/data/sources.json`); every row links to a source.
- [x] `node scripts/build.mjs` builds with no errors.
- [x] `node scripts/verify.mjs` passes (disclosure, sponsored rel, internal links, source links, data integrity, sitemap).
- [ ] Pull request from `arena/bb0a6985-affil3` to `main`: see log.
- [ ] Merge: see log.
- [ ] GitHub Pages deploy: see log.

## PR and deploy record

_Filled in at the end of the session (see log lines below)._
