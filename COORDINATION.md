# COORDINATION.md — Affil3 shared task board

> Shared board for parallel agent sessions working on `karagemop466-tech/Affil3`.
> **Rule:** claim a task by writing your session ID and file scope here, then commit and
> push that claim immediately. Never start a task another session has claimed. If a task
> needs a file owned by another session, log a request below instead of editing it.

## Session registry

| Session ID | Branch | Status | Notes |
| --- | --- | --- | --- |
| `7e5808de` | `arena/7e5808de-affil3` | active | Claimed T1–T7. Built the data register, the platform tooling, the static site, the guides, the measurement layer, the compliance gate and the decision board. |

Unregistered branches seen on the remote at board-creation time (no claim recorded, no
commits beyond `main`): `arena/114f47c4-affil3`, `arena/238c8ddb-affil3`,
`arena/35d0727e-affil3`. If any of those sessions are live, they must add a row here
before touching files. If a claim is more than 60 minutes old with no commits, any
session may take the task over and note the handoff in the log.

## Task board

| ID | Task | Status | Owner | Files touched |
| --- | --- | --- | --- | --- |
| T1 | Source register + product-intent confirmation record (5 links) | done | `7e5808de` | `data/products.json`, `data/sources.json` |
| T2 | Platform tooling: Special-Link builder, Creators API research, ledger, checks | done | `7e5808de` | `tools/affiliate.py`, `tools/research.py`, `tools/sitekit.py` |
| T3 | Static site build: templates, CSS, layout, nav, disclosure strip | done | `7e5808de` | `tools/build_site.py`, `assets/css/site.css`, `assets/js/site.js` |
| T4 | Editorial: question-shaped guides + comparisons | done | `7e5808de` | `data/guides.json`, `guides/*`, `compare/*`, `categories/*` |
| T5 | Measurement: privacy-preserving click counter + self-hosted endpoint | done | `7e5808de` | `assets/js/analytics.js`, `tools/analytics_sink.py`, `data/config.json` |
| T6 | Decision board: suggestions, open questions, flagged-for-review | done | `7e5808de` | `data/suggestions.json`, `data/questions.json`, `data/flags.json` |
| T7 | Integration: sitemap, feed, robots, link check, PR + merge + Pages deploy | in progress | `7e5808de` | `sitemap.xml`, `feed.xml`, `robots.txt`, `tools/check_site.py` |

Status values: `unclaimed` · `in progress` · `done` · `needs review`.
`needs review` means the item is published on the site's **Flagged for Review** page and
does not block anything else.

## Cross-session requests

_(none yet)_

## Log

### 2026-11-20 — session `7e5808de`

**Created** `COORDINATION.md` (the board did not exist). Verified all five submitted
`link.amazon` links live against `amazon.com` product pages and recorded the observed
redirect targets. All five resolve; the observed targets are recorded separately from
the (still unconfirmed) intended ASIN fields. Claimed T1–T7 and pushed the claim.

#### Verification performed

| Check | How | Result |
| --- | --- | --- |
| Five submitted links resolve | Fetched each link, followed the redirect chain | 5/5 reached an `amazon.com/dp/<ASIN>` page |
| Destination titles | Read the page title on the destination | Captured verbatim for all five, each with its URL and date |
| Browse path | Read the breadcrumb on the destination | 3 under Air Fryers (`17659096011`), 2 under Meat thermometers (`289810`) |
| ASIN shape | Compared token length against Amazon's own ASIN definition | 3 tokens are 9 characters (cannot be ASINs); 2 are 10 characters but neither confirmed issued |
| Price publication | Read Program Policies 2(b) | No price may be published without Amazon serving the link or Creators API / PA API |
| Rating publication | Read Program Policies 5(t) | No rating or review count may be published without Creators API / PA API |
| Link format | Read Program Policies 2(b), 5(v), 5(w) | Submitted short links are redirects; published links are direct tagged Special Links |
| Disclosure | Read Operating Agreement 5 and FTC Disclosures 101 | Strip under the masthead on every page, repeated in the footer |
| Outbound link marking | Read Google's outbound-link guidance | `rel="sponsored nofollow"` plus a visible marker and an aria-label |
| API status | Read the PA-API 5 deprecation notice | PA-API 5 returns HTTP 403 `AccessDeniedException`; the tooling targets the Creators API |
| Release gate | `python3 tools/check_site.py` | 0 violations, 0 warnings across 30 generated pages |
| Collector | Live POST against `tools/analytics_sink.py` | Valid events stored with a server-salted id; unknown events and unexpected fields rejected with 400 |

#### Irregularities found and flagged (published on the Flagged for Review page)

FLG-001 tracking ID unconfirmed · FLG-002 intended ASIN unconfirmed · FLG-003 submitted
links are redirects, not Special Links · FLG-004 two tokens ASIN-shaped but unconfirmed ·
FLG-005 Associates account not publicly verifiable · FLG-006 commission rate unverified ·
FLG-007 Creators API needs 10 qualifying sales in 30 days · FLG-008 PA-API 5 deprecated ·
FLG-009 no measured search data yet · FLG-010 listings drift over time · FLG-011 a
near-identical ThermoMaven listing under a different ASIN · FLG-012 GitHub Pages logs
visitor IP addresses.

None of these block the site going live.
