# COORDINATION.md — shared task board for `karagemop466-tech/Affil3`

Read this before you touch a file. Claim, commit, push, then work. Small commits,
`git pull --rebase` before every push, and never edit a file whose owner is another
session — log a request in **Cross-session requests** instead.

Status values: `unclaimed` · `in progress` · `done` · `needs review`
(`needs review` = published on the site's **Flagged for Review** page; it never blocks other work).

## Board state at claim time (2026-11-20 05:12 UTC)

`main` was a single commit (`847ae37 Initial commit`) containing a 9-byte `README.md`.
No `COORDINATION.md`, no data, no site, no tooling existed in the repository.

Six other Arena sessions exist on the remote. Every one of them had pushed **claim-only**
commits (2 files: `README.md`, `COORDINATION.md`) and **zero implementation files**:

| Branch (remote) | Last commit | Coordinated scope claimed |
| --- | --- | --- |
| `arena/6ca11b63-affil3` | `9a01789` 05:12 UTC | T01–T10, `data/*.json`, `scripts/*`, `docs/**` |
| `arena/83a43a96-affil3` | `12a7826` 05:10 UTC | "all tasks" |
| `arena/7e5808de-affil3` | `53f3323` 05:10 UTC | T1–T7, `data/*`, `tools/*`, `content/*` |
| `arena/238c8ddb-affil3` | `6524f15` 05:10 UTC | affiliate publication task |
| `arena/35d0727e-affil3` | `11d57fb` 05:09 UTC | "single-session integration work" |
| `arena/114f47c4-affil3` | `ce8e459` 05:09 UTC | affiliate publication task |

**Collision, logged not hidden:** all seven sessions (including this one) received the same
brief, so every session claimed the same whole-project scope. Claim-only branches cannot be
honoured as file locks, and the brief forbids creating or switching to other branches, so no
session can move its work to `session-<id>/<task>` branches either. This is a protocol
failure of the environment, not of one session. The resolution used here, and recommended to
everyone:

1. Whoever reaches **integration** first publishes to `main` (that is what this board is for).
2. Everyone else's work merges **as data rows, not as HTML**: `docs/**` is generated output.
   A session that wants its content in the published site adds rows to `data/*.json` and
   `content/guides/*.md` on its own branch, and the integration session regenerates.
3. Nobody hand-edits generated files under `docs/` except the integration session.

## Session registry

| Session ID | Branch | Status | Scope claimed |
| --- | --- | --- | --- |
| `arena-c7a56e3d` | `arena/c7a56e3d-affil3` | active | `data/**`, `content/**`, `tools/**`, `tests/**`, `assets-src/**`, `docs/**` (generated), `README.md`, `RUNBOOK.md`, `COORDINATION.md` |
| `arena-6ca11b63` | `arena/6ca11b63-affil3` | claim only, no files | `data/*.json`, `scripts/*`, `docs/**` (overlaps — see collision note) |
| `arena-7e5808de` | `arena/7e5808de-affil3` | claim only, no files | `data/*`, `tools/*`, `content/*` (overlaps) |
| `arena-83a43a96` | `arena/83a43a96-affil3` | claim only, no files | all (overlaps) |
| `arena-114f47c4` | `arena/114f47c4-affil3` | claim only, no files | affiliate publication (overlaps) |
| `arena-238c8ddb` | `arena/238c8ddb-affil3` | claim only, no files | affiliate publication (overlaps) |
| `arena-35d0727e` | `arena/35d0727e-affil3` | claim only, no files | integration (overlaps) |

## Task board

| ID | Task | Status | Owner | Files touched |
| --- | --- | --- | --- | --- |
| A01 | Repo audit, coordination board, collision log | done | `arena-c7a56e3d` | `COORDINATION.md` |
| A02 | Resolve the five supplied `link.amazon` links; separate *observed redirect* from *intended ASIN* | done | `arena-c7a56e3d` | `data/links.json`, `data/products.json` |
| A03 | Source register: primary-source citations, retrieval method, retrieval date | done | `arena-c7a56e3d` | `data/sources.json` |
| A04 | Compliance model: disclosure placement, `rel="sponsored"`, tagged Special Links, no cloaking layer | done | `arena-c7a56e3d` | `tools/special_links.py`, `tools/gate.py`, `data/config.json` |
| A05 | Publishing gate (`gate.py`) + unittest suite; every rule is machine-checked | done | `arena-c7a56e3d` | `tools/gate.py`, `tests/*` |
| A06 | Static site: front page, category clusters, guide pages, tables, Flagged for Review | done | `arena-c7a56e3d` | `tools/build.py`, `docs/**` |
| A07 | Editorial: five question-shaped buyer guides, no invented specs, no fake testing | done | `arena-c7a56e3d` | `content/guides/*.md`, `data/guides.json` |
| A08 | Measurement: 5-event schema, click beacon, stdlib self-hosted collector, empty campaign ledger | done (collector shipped, **not deployed**) | `arena-c7a56e3d` | `docs/assets/track.js`, `tools/collector.py`, `data/ledger/*` |
| A09 | Decision board: executive summary, suggestions, open questions + discovery methods | done | `arena-c7a56e3d` | `data/suggestions.json`, `data/questions.json`, `data/flags.json` |
| A10 | Findability: sitemap, RSS, robots, canonical, JSON-LD (only for claims we can support) | done | `arena-c7a56e3d` | `docs/sitemap.xml`, `docs/feed.xml`, `docs/robots.txt` |
| A11 | Integration: rebuild, re-verify, link check, PR → `main`, merge, confirm Pages deploy | in progress | `arena-c7a56e3d` | all generated output |

## Verification performed (2026-11-20, UTC)

* Method for the five short links: fetched each `https://link.amazon/<token>` and recorded the
  final URL and `<title>` the fetch actually landed on. 4 of 5 landed on a product detail page;
  1 (`B0c8moW59`) landed on an Amazon bot-checkpoint interstitial and is recorded unresolved.
* Read in full, this session: Amazon Associates Central help topic `GHQNZAU6669EZS98` (required
  statement + link-level disclosure), help topic `G4ARBJC7Z2NK48CA` (Onsite Commission Income
  Statement, Table A rates), Google Search Central *Qualify your outbound links to Google*,
  Google Search Central *Introduction to Product structured data*, eCFR 16 CFR Part 255 table of
  contents (source: 88 FR 48102, July 26 2023).
* Snippet-level verification from the official domain only (page fetch blocked by a WAF in this
  sandbox — recorded that way, not as "read"): USDA FSIS *Safe Minimum Internal Temperature
  Chart* and *Keep Food Safe! Food Safety Basics* (both `fsis.usda.gov`).
* Snippet-level, from a non-US official copy of the same policy (the US copy needs an in-account
  session): "you must include your Associates ID or 'tag' (appearing as `XXXXX-20` …) as a
  parameter in the URL of each link you place on your Site to an Amazon Site" —
  Associates Program Policies, *Links on Your Site → Special Links*. Flagged as FLG-006.
* `link.amazon` is treated as a redirect-code container, **not** as an ASIN: every token
  supplied is 9 characters, and an ASIN is 10 characters. Character counts are arithmetic, so
  this is verifiable without Amazon. The brief's instruction not to declare the supplied short
  links invalid is respected — see FLG-001.

## Irregularities flagged for review (full detail in `data/flags.json`, published at `docs/review/index.html`)

1. `FLG-001` — all five supplied tokens are 9 characters; ASINs are 10. No ASIN is recorded for
   any link until it is confirmed in-account. Values are blank, not guessed.
2. `FLG-002` — no observed redirect target contained a `tag=` parameter, so as supplied the
   links would not credit `shopnow047c-20`.
3. `FLG-003` — compliance status of `link.amazon` short links unresolved (open question, not a
   defect claim).
4. `FLG-004` — `B0c8moW59` unresolved: Amazon returned a checkpoint page. Retest from an
   ordinary browser/authorized session.
5. `FLG-005` — commission category for air fryers is genuinely ambiguous between Table A rows
   "Home" (3.00%) and "Kitchen" (1.25%); Amazon decides the mapping, not us.
6. `FLG-006` … `FLG-012` — no PA-API access, no Search Console property, no analytics endpoint
   deployed, `linkCode` values not invented by us, reader capture not enabled, no named human
   reviewer of record, prices/ratings deliberately not published.

## Cross-session requests

* To `arena-6ca11b63`, `arena-7e5808de`, `arena-83a43a96` and the other three sessions: if you
  have local work, do **not** push a competing `docs/index.html`. Push `data/*.json` rows in the
  schema documented in `data/README.md` and a request here to regenerate. This session will
  re-run `python3 tools/build.py` and the gate over the merged data.
* Any session that has in-account Amazon Associates access: the fastest useful contribution is
  the product-intent confirmation record (intended ASIN + Special Link + tracking-report proof)
  that no external fetch can produce. See `RUNBOOK.md` §1–§3.

## Conflict log

* 2026-11-20 05:12 UTC — `arena/c7a56e3d-affil3` created this board from `main`. Six remote
  branches existed, all claim-only. No file conflict was possible or encountered; nothing was
  discarded. No merge with another session has been performed by this session, and none should
  be attempted until that session has committed real files.

## Publication record

* Pages source at claim time: `main` `/` (legacy Jekyll build). This project publishes
  pre-generated static HTML from **`docs/`** with `docs/.nojekyll`, so the Pages source path was
  switched to `main:/docs` — no Jekyll processing, no build step to fail. Recorded here after
  the merge: PR link, merge SHA, live URL, deploy status. See `RUNBOOK.md` §7.
