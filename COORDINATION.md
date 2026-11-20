# COORDINATION.md — Shared Task Board

This file is the single coordination point for every session working in this repo.
**Before starting any work, read this file, claim a task, and commit + push the claim immediately.**
Claimed tasks must never be started by another session.

## How to coordinate

1. Read the task table below. If `COORDINATION.md` did not exist, create it (with this protocol) before doing anything else.
2. Claim a task by writing your session ID in the **Owner** column, setting status to `in progress`, listing the exact files you will touch, and committing + pushing **immediately**.
3. Keep scopes non-overlapping. Each session edits only the files in its claimed scope, on its own branch (or git worktree) named `session-<id>/<task>`.
   - **Branch note (Arena sessions):** sessions launched by Arena work on a fixed branch assigned by the platform (this session: `arena/0a417943-affil3`). Platform policy forbids switching or creating other branches, so the assigned branch **is** that session's branch; log it here as the session's scope.
4. If a task requires changing a file owned by another session, **do not edit it** — log the request in the Log below and let the owner apply it.
5. Make small, frequent commits. Run `git pull --rebase` before every push.
6. On merge conflict: **stop**, resolve without discarding the other session's work, and log what happened below.
7. When a task is finished: record its sources, the verification performed, and any irregularities in the Log below, and mark the task `done`. A status of `needs review` means the item is published on the site's **Flagged for Review** page and does not block anything.
8. Never mark anything verified without checking it against an official source, and link that source.
9. Shared outputs — table data, the site's index and navigation, sitemap/feed — are changed only by a **final integration session** once all other tasks are done. That session merges branches, re-verifies combined data line by line, confirms the site builds with no broken links, opens the PR to `main`, merges it without waiting for approval, and confirms GitHub Pages deploys.
10. If a session crashes, or its claim is more than 60 minutes old with no commits, any other session may take over the task and note the handoff in the Log.
11. Flagged irregularities and unverified items **do not block** the merge; they are published on the clearly labeled **Flagged for Review** page with source links.
12. If the build, a check, or the deploy fails: fix the problem and retry until the site is live. Do not merge a broken site.

## Session registry

| Session ID | Branch | Scope | Started (UTC) | Last commit (UTC) |
|---|---|---|---|---|
| `arena-0a417943-affil3` | `arena/0a417943-affil3` | Bootstrap + full build + final integration (T-01..T-16 — repo was empty at session start) | 2026-11-20 | 2026-11-20 |

## Task board

Status values: `unclaimed` · `in progress` · `needs review` · `done`.

| # | Task | Owner | Status | Files touched |
|---|---|---|---|---|
| T-01 | Bootstrap coordination board + README | `arena-0a417943-affil3` | in progress | `COORDINATION.md`, `README.md` |
| T-02 | Source verification pass — locate + fetch every official source cited in registers (Amazon Associates agreement/policies, ASIN definition, FTC endorsement guides, PA-API terms, .amazon registry, GitHub Pages docs, Search Console docs) | `arena-0a417943-affil3` | in progress | `data/sources.json`, `sourcing/index.html` |
| T-03 | Product-intent confirmation records for the 5 submitted links (intended ASIN, official listing URL, confirmation date, source; observed redirect targets kept in a **separate** field — never merged) | `arena-0a417943-affil3` | unclaimed | `data/products.json`, `products/index.html`, `products/p1.html` … `products/p5.html` |
| T-04 | Flag register (incl. FLG-003 short-link compliance status: unresolved; no claim of invalidity) + Flagged for Review page | `arena-0a417943-affil3` | unclaimed | `data/flags.json`, `flagged/index.html` |
| T-05 | Decision-readiness register: questions, information needed, answers we have/lack, discovery suggestions | `arena-0a417943-affil3` | unclaimed | `data/questions.json`, `questions/index.html` |
| T-06 | Suggestion review board (proposals with status, options, impact/risk, decision needed — reviewed before implementation) | `arena-0a417943-affil3` | unclaimed | `data/suggestions.json`, `suggestions/index.html` |
| T-07 | Publication front page (lead with products + guides; dashboard reachable from footer, single nav group) + disclosure strip above the fold on **every** page | `arena-0a417943-affil3` | unclaimed | `index.html`, all pages, `assets/css/site.css`, `assets/js/site.js` |
| T-08 | Question-shaped guides ×4 (user-supplied working titles) + guides index with clusters + seasonal calendar | `arena-0a417943-affil3` | unclaimed | `guides/index.html`, `guides/basket-or-oven-air-fryer.html`, `guides/air-fryer-capacity-checklist.html`, `guides/cleanup-and-counter-space.html`, `guides/multifunction-appliance-questions.html` |
| T-09 | Product profiles + shop grid (every table row carries a source link; unconfirmed values blank + flagged UNVERIFIED) | `arena-0a417943-affil3` | unclaimed | `products/index.html`, `products/p1.html` … `products/p5.html` |
| T-10 | Executive summary page | `arena-0a417943-affil3` | unclaimed | `summary/index.html` |
| T-11 | Campaign ledger (empty but well-defined schema; no fabricated numbers, no conversion score, no revenue forecast) + events schema (5 defined events) + analytics collector | `arena-0a417943-affil3` | unclaimed | `data/ledger/campaign-ledger.csv`, `data/events-schema.json`, `assets/js/analytics.js`, `analytics/index.html` |
| T-12 | Compliance gate: publishing checklist, disclosure policy, sponsored-rel policy, API-policy checks (S01 · S07 · S24) | `arena-0a417943-affil3` | unclaimed | `compliance/index.html`, `tools/validate.py`, `.github/workflows/gates.yml` |
| T-13 | Findability: sitemap.xml, RSS feed.xml, robots.txt, canonical URLs, JSON-LD, Search Console readiness page | `arena-0a417943-affil3` | unclaimed | `sitemap.xml`, `feed.xml`, `robots.txt`, `search-console/index.html` |
| T-14 | Dashboard hub (ledger viewer, link-builder tool, events download) + suggestion/question pages wired to it | `arena-0a417943-affil3` | unclaimed | `dashboard/index.html`, `suggestions/index.html`, `questions/index.html` |
| T-15 | Imagery (AI-generated, labeled as illustrative; no scraped Amazon imagery) + favicon/logo | `arena-0a417943-affil3` | unclaimed | `assets/img/*`, `assets/img/favicon.svg` |
| T-16 | **Final integration** (re-verify combined data, CI gates green, open PR → `main`, merge without waiting, confirm Pages deploy, record PR link + merge result here) | `arena-0a417943-affil3` | unclaimed | PR, `COORDINATION.md` |

## Work log

| Date (UTC) | Session | Entry |
|---|---|---|
| 2026-11-20 | `arena-0a417943-affil3` | Repo found empty (README only, commit `847ae37`). Created board; claimed T-01..T-16 (no other sessions present at claim time; `main` had no site content to conflict with). GitHub Pages already enabled: builds from `main` root, `https://karagemop466-tech.github.io/Affil3/`. All tasks claimed by this session will be worked on branch `arena/0a417943-affil3`. |

## Merge & deploy record

| Date (UTC) | PR | Result |
|---|---|---|
| — | — | No merge yet. The final integration session records the PR link and merge result here only **after** it happens. |
