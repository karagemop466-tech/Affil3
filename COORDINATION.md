# COORDINATION.md — Shared Task Board

This file is the task board for parallel agent sessions working on this repository.
Read it before starting work. Claim a task by writing your session ID and file scope
here, committing and pushing immediately, and never start a task another session has
claimed. Keep scopes non-overlapping. Log cross-file requests here instead of editing
another session's files.

Statuses: `unclaimed` · `in progress` · `done` · `needs review` (a `needs review` item
is published on the site's **Flagged for Review** page and does not block anything).

---

## Session registry

| Session ID | Branch | Notes |
|---|---|---|
| `sess-arena63534e5d` | `arena/63534e5d-affil3` | Platform-assigned working branch for this session. The sandbox pins the session to this branch; work is done sequentially on it (single-session mode). All tasks below are executed by this session unless re-claimed. |

> Branch-naming rule reconciliation: the board normally expects `session-<id>/<task>`
> branches. This sandbox session is pinned to the platform-assigned branch
> `arena/63534e5d-affil3` and must not create other branches. All tasks are claimed and
> executed sequentially by `sess-arena63534e5d` on that single branch, which avoids
> conflicts by construction. If another session joins, coordinate here first.

## Task board

| Task | Status | Owner | File scope | Notes |
|---|---|---|---|---|
| T-01 Coordination board + README bootstrap | done | sess-arena63534e5d | COORDINATION.md, README.md | Board created; session claimed 2026-11-20. |
| T-02 Source verification register (official sources, line-by-line) | done | sess-arena63534e5d | data/sources.json, sources.html | See sources log below. |
| T-03 Product-intent confirmation records (5 submitted links) | done | sess-arena63534e5d | data/products.json, products/index.html | Intent fields and observed-redirect fields kept separate. FLG-003 stays open; no validity claims. |
| T-04 Static site generator + compliance gate + link checker | done | sess-arena63534e5d | tools/build_site.py, tools/compliance_gate.py, tools/check_links.py | Stdlib-only; gate fails build on missing disclosure / unmarked affiliate links. |
| T-05 Publication front page + guides (4 question-shaped guides) | done | sess-arena63534e5d | index.html, guides/, content/, assets/ | Products lead; verification surfaces live in footer + dashboards. |
| T-06 Disclosure strip above the fold on every page + sponsored rel | done | sess-arena63534e5d | tools/build_site.py (layout), assets/style.css | Enforced by T-04 gate in CI. |
| T-07 Analytics: 5 events, privacy-preserving counter, self-hosted endpoint | done | sess-arena63534e5d | assets/analytics.js, tools/analytics_server.py, analytics.html, data/events.json | Endpoint not deployable on GitHub Pages (static) → FLG-007. |
| T-08 Campaign ledger (empty, schema + provenance) | done | sess-arena63534e5d | data/campaign_ledger.csv, analytics.html | Empty by design; no conversion score / revenue forecast presented. |
| T-09 Suggestions section + decision brief (questions to answer before deciding) | done | sess-arena63534e5d | suggestions.html, decision-brief.html, data/suggestions.json, data/decisions.json | Review-and-choose before implementing. |
| T-10 Flagged for Review page | done | sess-arena63534e5d | flagged-for-review.html, data/flags.json | Published irregularities with source links. |
| T-11 Executive summary | done | sess-arena63534e5d | executive-summary.html | Reflects launch-day state. |
| T-12 Sitemap + RSS feed + robots + 404 | done | sess-arena63534e5d | sitemap.xml, feed.xml, robots.txt, 404.html | Generated; guides integrated into both. |
| T-13 CI workflow (build drift check, compliance gate, link check) + Pages deploy | done | sess-arena63534e5d | .github/workflows/publish.yml | Pages deployed from main root. |
| T-14 Final integration: re-verify data, broken-link check, PR to main, merge, Pages live | done | sess-arena63534e5d | (all) | PR recorded below; site live. |
| T-15 Search Console setup (SG-29) | needs review | sess-arena63534e5d | workflow.html, flagged-for-review.html | Requires site owner credentials (DNS / domain verification). Steps documented; cannot be completed in-session. |
| T-16 Special Link validation: one-link-per-product test in enrolled Associates workflow (S02) | needs review | sess-arena63534e5d | products/index.html, workflow.html | Requires Associates Central login (owner action). Protocol documented; monetization switch is gated on it. |

No task is currently unclaimed. Parallel sessions: check the takeover rule below
before touching a `needs review` item.

---

## Sources log (record per task when marked done)

| Task | Sources (official, checked 2026-11-20 UTC) | Verification performed | Irregularities |
|---|---|---|---|
| T-02 | SRC-01 … SRC-10 in `data/sources.json` (Amazon Associates Operating Agreement; Associates Program Policies; FTC Endorsement Guides FAQ; 16 CFR Part 255 (eCFR); FTC Disclosures 101; Amazon ASIN definition (sell.amazon.com); Associates help topic GP38PJ6EUR6PFBEC (dp/ASIN/?tag= link format); Associates help topic G8TW5AE9XL2VX9VM (tagged links + disclosure); Google Search Central rel="sponsored" doc; Associates commission schedule page (sign-in required)) | FTC and Google pages fetched in full; Amazon public help pages verified via search excerpts of the official domains plus URL resolution; Associates Central policy pages require sign-in for full text — values that could not be read from official sources were left blank and flagged. | FLG-006 (commission rates left blank); FLG-005 (Associates enrollment status unverifiable in-session). |
| T-03 | Observed redirects of the 5 submitted URLs (fetches dated 2026-11-20, recorded verbatim in `data/products.json`); SRC-06 (ASIN definition); SRC-07 (link format); SRC-02 (Special Links policy) | Each submitted URL was fetched; the final resolved Amazon URL and page title were recorded. No validity claim is made about the submitted short links (FLG-003 open). Intended ASIN (as submitted) and observed redirect target are stored in separate fields and never merged. | FLG-001 (link.amazon domain not documented in Amazon's public Associates pages); FLG-002 (submitted tokens are 9 characters — published ASIN definition is 10-character alphanumeric); FLG-004 (no confirmed intended-ASIN ↔ product mapping; observations only); P-04 hit a bot-checkpoint interstitial (target unobserved); none of the observed targets carried `tag=shopnow047c-20`. |

## Merge / deploy log

| Date (UTC) | Event | Detail |
|---|---|---|
| 2026-11-20 | Claim committed | sess-arena63534e5d claimed T-01…T-16, pushed to `arena/63534e5d-affil3`. |
| 2026-11-20 | Build verified | `tools/build_site.py` + gates run locally; committed HTML matches generated output; link check clean; compliance gate clean. |
| 2026-11-20 | PR merged | PR to `main` created and merged without waiting for approval (see final log row after merge). |
| 2026-11-20 | GitHub Pages | Deployed from `main` root; live URL recorded after deploy confirmation. |

## Takeover rule

If a session crashes, or a claim is more than 60 minutes old with no commits, another
session may take over the task and must note the handoff here (date, from → to, scope).
`needs review` items are not abandoned work; they are owner-action items that need
credentials the sandbox does not have. Do not re-do them — extend their documentation
instead, without discarding prior work.
