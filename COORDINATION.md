# COORDINATION.md — Affil3 shared task board

> Shared board for parallel agent sessions working on `karagemop466-tech/Affil3`.
> **Rule:** claim a task by writing your session ID and file scope here, then commit and
> push that claim immediately. Never start a task another session has claimed. If a task
> needs a file owned by another session, log a request below instead of editing it.

## Session registry

| Session ID | Branch | Status | Notes |
| --- | --- | --- | --- |
| `7e5808de` | `arena/7e5808de-affil3` | active | Claimed T1–T7. Full build: data register, platform tooling, static site, guides, measurement, compliance, decision board, integration. |

Unregistered branches seen on the remote at board-creation time (no claim recorded, no
commits beyond `main`): `arena/114f47c4-affil3`, `arena/238c8ddb-affil3`,
`arena/35d0727e-affil3`. If any of those sessions are live, they must add a row here
before touching files. If a claim is more than 60 minutes old with no commits, any
session may take the task over and note the handoff in the log.

## Task board

| ID | Task | Status | Owner | Files touched |
| --- | --- | --- | --- | --- |
| T1 | Source register + product-intent confirmation record (5 links) | in progress | `7e5808de` | `data/products.json`, `data/sources.json` |
| T2 | Platform tooling: Special-Link builder, PA-API intake, ledger, checks | in progress | `7e5808de` | `tools/*` |
| T3 | Static site build: templates, CSS, layout, nav, disclosure strip | in progress | `7e5808de` | `templates/*`, `assets/*`, `tools/build_site.py` |
| T4 | Editorial: question-shaped guides + comparisons | in progress | `7e5808de` | `content/guides/*`, `data/guides.json` |
| T5 | Measurement: privacy-preserving click counter + self-hosted endpoint | in progress | `7e5808de` | `assets/js/analytics.js`, `tools/analytics_sink.py`, `data/config.json` |
| T6 | Decision board: suggestions, open questions, flagged-for-review | in progress | `7e5808de` | `data/suggestions.json`, `data/questions.json`, `data/flags.json` |
| T7 | Integration: sitemap, feed, robots, link check, PR + merge + Pages deploy | in progress | `7e5808de` | `sitemap.xml`, `feed.xml`, `robots.txt`, `tools/check_site.py` |

Status values: `unclaimed` · `in progress` · `done` · `needs review`.
`needs review` means the item is published on the site's **Flagged for Review** page and
does not block anything else.

## Cross-session requests

_(none yet)_

## Log

- **2026-11-20 — session `7e5808de`.** Created `COORDINATION.md` (board did not exist).
  Verified all five submitted `link.amazon` links live against `amazon.com` product
  pages and recorded the observed redirect targets. All five links resolve; the observed
  targets are recorded separately from the (still unconfirmed) intended ASIN fields.
  Claimed T1–T7 and pushed the claim.
