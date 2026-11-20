# Coordination — Affil3

Shared task board for the Affil3 affiliate publication. Last updated 2026-11-20 (UTC) by session `arena-f761b123-affil3`.

## Status legend
`unclaimed` · `in progress` · `done` · `needs review` (published on `flagged.html`/Flagged for Review, does not block anything)

## Sessions

| Session | Branch | Scope | Outcome |
|---|---|---|---|
| `arena-83a43a96-affil3` | `arena/83a43a96-affil3` | First publication pass (landing, products, guides, disclosure, sitemap, feed, click counter) | Merged to `main` via PR #1 (`db77ec4`). Product fields were left blank because it recorded the short links as unresolvable. **Superseded by this session** — see Irregularity log IRR-01. |
| `arena-f761b123-affil3` (this session) | `arena/f761b123-affil3` | Full rebuild: verified product register, category + guide pages, dashboards, measurement, compliance gates, Pages source switch to `/docs` | Built: 5 product rows (4 confirmed, 1 unverified), 5 guides, category pages, dashboards, ledger, RSS, sitemap, checker, receiver. Prior URLs redirect. Pending: PR, merge, Pages switch. |

Session note: the brief asks for `session-<id>/<task>` branches. The Arena session rule for this sandbox requires all work on the single current branch `arena/f761b123-affil3`, so task scopes below are separated by **directory and file**, not by branch.

## Task board (session `arena-f761b123-affil3`)

| # | Task | Status | Owner | File scope | Sources (see `data/sources.json`) | Notes |
|---|---|---|---|---|---|---|
| T1 | Repo review: every file, irregularities flagged | done | arena-f761b123-affil3 | `COORDINATION.md`, `data/flags.json` | SRC-01..SRC-16 | Repo review log in Irregularity log below |
| T2 | Product-intent confirmation record (5 submitted links) | done | arena-f761b123-affil3 | `data/products.json` | SRC-14, SRC-15, SRC-04 | ASIN, listing URL, date, source, observed redirect target (separate field) |
| T3 | Associates compliance gate (disclosure text, `rel="sponsored"`, prices/ratings exclusions, tag check) | done | arena-f761b123-affil3 | `tools/check_site.py`, `data/site.json` | SRC-01, SRC-02 | Checker fails build on violations |
| T4 | Design system + publication layout (masthead, nav group, disclosure strip, footer) | done | arena-f761b123-affil3 | `assets/css/`, `tools/build_site.py` | — | No external fonts or frameworks |
| T5 | Landing page as publication front page (products first) | done | arena-f761b123-affil3 | `tools/build_site.py` (home) | SRC-06, SRC-05 | — |
| T6 | Category subpages + product register + dashboards (sources, findings, questions, suggestions, flagged, ledger) | done | arena-f761b123-affil3 | `tools/build_site.py`, `data/*.json` | all | Every table row has a source link or is marked unverified |
| T7 | Question-shaped buyer guides (4 working titles + 1 proposed) with clusters | done | arena-f761b123-affil3 | `content/guides/*.md` | SRC-11 (thermometer guide), SRC-05, SRC-07 | Editorial only; no testing claims |
| T8 | Measurement: outbound-click counter + five events + self-hosted receiver | done (receiver tested locally; not hosted, FLG-004) | arena-f761b123-affil3 | `assets/js/measure.js`, `analytics/` | SRC-02 (privacy disclosure; section not recorded), SRC-05 | Receiver is NOT hosted by GitHub Pages; flagged FLG-004 |
| T9 | Campaign ledger (empty, well-defined) | done (empty) | arena-f761b123-affil3 | `data/campaign_ledger.csv` | — | No first-party reports supplied; no revenue forecast |
| T10 | Sitemap, RSS 2.0 feed, robots.txt, 404 | done | arena-f761b123-affil3 | `tools/build_site.py` | SRC-08, SRC-09 | Feed = guides; sitemap = every HTML page |
| T11 | Executive summary | done | arena-f761b123-affil3 | `EXECUTIVE_SUMMARY.md`, `docs/executive-summary/` | — | — |
| T12 | Build + link check + tests (no broken links) | done | arena-f761b123-affil3 | `tools/`, `tests/` | — | — |
| T13 | GitHub Pages: switch publishing source to `main` `/docs` and verify deploy | pending: switch Pages source to main /docs after merge | arena-f761b123-affil3 | repo settings via GitHub API | SRC-10 | Switch done after merge (source folder must exist on `main`) |
| T14 | Pull request `arena/f761b123-affil3` → `main`, merge, record result | in progress | arena-f761b123-affil3 | `COORDINATION.md` | — | Flagged items do not block merge |

## Irregularity log

| ID | Date | Where | Irregularity | Action |
|---|---|---|---|---|
| IRR-01 | 2026-11-20 | `products.html` (main @ db77ec4) | Prior session stated the short links "could not be resolved here". This session fetched all five links; four resolve to Amazon product pages (see `data/products.json`). | Product fields re-verified and filled from the observed official listing pages. Prior blank values superseded. |
| IRR-02 | 2026-11-20 | repo-wide | The brief cites a source register (`S01`, `S02`, `S07`, `S24`, `FLG-003`, `SG-27`..`SG-30`). No such file exists in the repository or on `main`. | Cannot be matched to content. Logged as FLG-011. Site uses its own register `SRC-01…` with live URLs. |
| IRR-03 | 2026-11-20 | `assets/js/app.js` (main) | Prior click script stored a persistent random session ID in `localStorage` and queued events for an endpoint that does not exist. This conflicts with the privacy-preserving requirement and grows storage without bound. | Replaced by `assets/js/measure.js`: no identifiers, no storage, honours Do Not Track and Global Privacy Control, no-op until an endpoint is configured. |
| IRR-04 | 2026-11-20 | Observed short-link targets | None of the four resolved Amazon URLs contains a `tag=` parameter. Participation Requirements 2(a) requires the Associates ID as a URL parameter in each link. | Flagged FLG-009. Not claimed invalid; owner must confirm in Associates Central (SUG-01). |
| IRR-05 | 2026-11-20 | `B00hJ57DV` short link | Resolves to an Amazon checkpoint interstitial ("To continue, please click the Continue shopping button"), not a product page. | Product left unverified (FLG-008). |
| IRR-06 | 2026-11-20 | Amazon schedule page | `affiliate-program.amazon.com/help/operating/schedule` (commission rates) redirects to an Amazon sign-in page when fetched. | Commission rates left blank (FLG-010). |
| IRR-07 | 2026-11-20 | Brief | The brief asks for "five defined events" but their definitions are not in the repo. Prior session's five event names are used and documented in `data/analytics_events.json`. | Flagged FLG-012 for confirmation. |
| IRR-08 | 2026-11-20 | Branch rule | The brief asks for `session-<id>/<task>` branches; the sandbox branch rule requires work on the single current branch. | Followed the sandbox rule; scopes separated by file (see Session note). |

## Ground rules followed
- Work on `arena/f761b123-affil3` only; push only to that branch; PR from it to `main`.
- Commit and push the claim before writing site files; `git pull --rebase` before each push.
- No value inferred. A value is recorded only when observed on an official page (URL and date stored with it). Otherwise blank + flagged.
- Prices and star ratings are not displayed or stored (Participation Requirements §2(b) and §6(t)).
- Outbound Amazon links are the submitted short links, `rel="sponsored noopener"`. No claim that they are invalid.
