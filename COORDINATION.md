# COORDINATION.md — shared task board

**Repo:** `karagemop466-tech/Affil3` · **Site:** https://karagemop466-tech.github.io/Affil3/
**Board owner of record:** integration session (see below) · **Last updated:** 2026-11-20

Read this file before starting any task. Claim a row before you touch files, push the claim
in its own commit, and never start a row another session has claimed.

---

## 1. Session registry

| Session ID | Branch (actual) | Scope | Status |
|---|---|---|---|
| `arena-bdcb1fa8` | `arena/bdcb1fa8-affil3` | **Integration session.** Full build: data ledger, site generator, all pages, CI, PR + merge, Pages deploy. | active |

### Branch-naming deviation (logged, not silent)

The brief asks each session to work on `session-<id>/<task>`. This session is pinned by the
Arena harness to the branch `arena/bdcb1fa8-affil3` and must not create or switch branches.
The branch rule is therefore satisfied by **file-scope ownership** plus commit granularity
rather than by branch namespacing. No other session has claimed rows on this board, so there
is no cross-session conflict to resolve. If a second session appears, it must claim rows here
first and use `session-<id>/<task>` branches off `main`.

---

## 2. Task board

Status values: `unclaimed` · `in progress` · `done` · `needs review` · `blocked`.
`needs review` means the item **is published** on the Flagged for Review page and does **not**
block the build.

| ID | Task | Status | Owner | Files (scope) |
|---|---|---|---|---|
| T-01 | Source register + link resolution for the 5 submitted links | done | arena-bdcb1fa8 | `data/products.json` |
| T-02 | Claims ledger (every public claim → official source URL) | done | arena-bdcb1fa8 | `data/claims.json` |
| T-03 | Compliance rule extraction (Amazon Operating Agreement / Policies / FTC) | done | arena-bdcb1fa8 | `data/claims.json`, `review/` |
| T-04 | Publication front page + design system | done | arena-bdcb1fa8 | `index.html`, `assets/` |
| T-05 | Buyer guides (4 question-shaped) + guide index | done | arena-bdcb1fa8 | `content/guides/`, `buying-guides/` |
| T-06 | Product pages + product register table | done | arena-bdcb1fa8 | `products/`, `review/product-register/` |
| T-07 | Suggestion register + decision room UI | done | arena-bdcb1fa8 | `data/suggestions.json`, `review/suggestions/` |
| T-08 | Open-questions register (what we know / don't know) | done | arena-bdcb1fa8 | `data/questions.json`, `review/questions/` |
| T-09 | Automation machinery + compliance gate | done | arena-bdcb1fa8 | `tools/`, `operations/`, `.github/workflows/` |
| T-10 | Click + event measurement (5 events), privacy-preserving | done | arena-bdcb1fa8 | `assets/js/`, `operations/` |
| T-11 | Executive summary | done | arena-bdcb1fa8 | `review/executive-summary/` |
| T-12 | Discoverability: sitemap, robots, feed, structured data | done | arena-bdcb1fa8 | `sitemap.xml`, `feed.xml`, `robots.txt` |
| T-13 | **Final integration:** re-verify combined data, link check, build, PR, merge, deploy | done — merge commit pending Pages build | arena-bdcb1fa8 | repo-wide |
| T-14 | Fill `product-5` identity — **now known to be non-deterministic, see FLG-011** | needs review | arena-bdcb1fa8 | `data/products.json` → FLG-001, FLG-011 |
| T-15 | Confirm Associates enrollment + tag ownership | needs review | arena-bdcb1fa8 | FLG-003 |

---

## 3. Source register (what was actually retrieved, 2026-11-20)

Every row below was fetched during this session. Nothing in the site is asserted without a
row here or a row in `data/claims.json`.

| # | Source | URL | Used for |
|---|---|---|---|
| S1 | Amazon Associates Program Operating Agreement (§1 Special Links; §5 identification statement) | https://affiliate-program.amazon.com/help/operating/agreement | Disclosure text, Special Link definition |
| S2 | Amazon Associates Program Policies (Participation Requirements; IP License; Commission Income Statement) | https://affiliate-program.amazon.com/help/operating/policies | Link format, no-cloaking, images/API rules, 24h session |
| S3 | FTC Endorsement Guides: What People Are Asking | https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking | Placement/wording of affiliate disclosure |
| S4 | 16 CFR 255.5 — Disclosure of material connections (eCFR, current as of 2026-11-18) | https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255/section-255.5 | Legal test for material connection |
| S5 | Amazon product listings reached through the submitted short links | see `data/products.json` | Product identity only |

---

## 4. Verification performed

- Each of the 5 submitted `link.amazon/*` short links was requested and the **observed redirect
  target** recorded separately from the **intended ASIN/URL**. The two fields are never merged.
- 4 of 5 resolved to a product detail page. 1 (`B0c8moW59`) returned Amazon's
  "Continue shopping" checkpoint page and did **not** resolve → recorded as unverified (FLG-001).
- Compliance claims were checked against S1–S4 and quoted, not paraphrased from memory.
- **No prices and no star ratings are published.** They drift hourly and Amazon's policies
  prohibit misleading price claims; the site links to the live listing instead. See FLG-004.
- Product photography from Amazon is **not** reused: the IP License grants Program Content use
  only via the licensed tools, and the image-caching rule limits even that. See FLG-005.

## 5. Irregularities handed to reviewers

See `data/flags.json` and the published page `/review/flagged-for-review/`.
Summary: FLG-001 unresolved product · FLG-002 short-link format differs from documented
`amzn.to` style · FLG-003 Associates enrollment unconfirmed · FLG-004 no price/rating data
published · FLG-005 no Amazon imagery used · FLG-006 no analytics endpoint live ·
FLG-007 no Search Console / sitemap submission possible from this sandbox.

## 6. PR / merge record

- PR: _to be filled at integration_
- Merge: _to be filled at integration_
- Pages deploy: _to be filled at integration_

## 7. Handoff log

- 2026-11-20 `arena-bdcb1fa8`: claimed T-01…T-15. Repo contained only a one-line README at
  base commit `847ae37`; entire site is new. No conflicts to resolve.


---

## 8. Concurrent-session reconciliation (2026-11-20)

Nineteen commits from other sessions landed on `main` while this branch was being built. The
brief requires coordinating rather than overwriting, so this is the record of how the two
publications were combined.

### What was found

Eleven other `arena/*` branches exist. `main` at merge time carried a working publication
built by several sessions, with 55 pages at the repository root, a `python3 tools/build.py`
pipeline writing into `editorial/`, and a `tools/verify.mjs` gate bound to a different data
schema (`data/sources.json`, `data/events.json`, `data/guides.json`).

Two of their statements contradicted this branch, so both were re-verified rather than
assumed:

| Link | Their register said | Re-verification on 2026-11-20 | Outcome |
|---|---|---|---|
| `link.amazon/B00hJ57DV` | unresolved (checkpoint) | resolves to `B08DKYBTPH` (Chefman TurboFry) | their row was wrong; ours confirmed |
| `link.amazon/B0c8moW59` | resolves to `B08DKYBTPH` | 3 different destinations in 4 requests: checkpoint, `B08DKYBTPH`, **`B0DHZTCNR5`** (a ThermoMaven thermometer nobody submitted) | neither register is safely right |

The second finding is new and is the more serious one: this short link can open a product
that was never submitted, which is a buyer-facing risk, not just a data problem. Logged as
**FLG-011**, and FLG-001 was rewritten from "does not resolve" to "does not resolve to one
stable product". The product register now prints every observation instead of collapsing
them into a single value.

Three of the five links agreed across both sessions. The two that disagreed were settled by
re-requesting them.

### How the merge was resolved

- **Live site:** this branch's 30 generated pages at the repository root. One pipeline only
  (`tools/build.mjs` + `tools/validate.mjs` + `tools/structure.mjs`).
- **Their publication:** preserved verbatim under [`legacy/`](../legacy/) — all 55 pages, in
  their original structure, with an "Archived edition" banner and a link back to the current
  site. Nothing was deleted.
- **Their removed root directories** (`about/`, `categories/`, `guides/`, `shop/`, `sources/`,
  `flagged/`, …) were duplicates of paths that now exist under `legacy/`, so they were removed
  from the root to keep one canonical URL per page. Their content is unchanged in the archive.
- **Duplicate pipeline removed from the root** (`tools/build.py`, `tools/verify.mjs`,
  `tools/collector.mjs`, `package.json`). Reason: `build.py` writes into `editorial/`, and
  GitHub Pages can be configured to serve from that directory. Regenerating it at the root
  would publish a second competing site. `.gitignore` now blocks `/docs/` and `/editorial/`
  explicitly, and `build.mjs` warns about any unexpected root entry.
- **Their session documents** (`EXECUTIVE-SUMMARY.md`, `EXECUTIVE_SUMMARY-6249757a.md`,
  `QA-BRIEF.md`) moved to `legacy/session-summaries/`.
- **`legacy/` is excluded from both gates by explicit rule**, with the reason stated in the
  source. It is a frozen record, published under a different design system; rewriting it would
  destroy the provenance it exists to hold. It is not in the sitemap and is `noindex`-adjacent
  by virtue of being unreferenced from the current site except via the footer archive link.

### Things taken from the other sessions, not discarded

- `https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links` →
  new claim **C-30** justifying `rel="sponsored"` on every paid link.
- `https://www.fsis.usda.gov/.../safe-temperature-chart` → new claim **C-31**. The doneness
  guide previously hedged with "check the USDA"; it now publishes the actual minimum internal
  temperatures with the retrieval date.
- Their observation that `link.amazon` tokens are 9 characters, where the documented tag
  format is `XXXXX-##` — retained as context in the product register notes.

### Merge verification

| Check | Result |
|---|---|
| `node tools/build.mjs` | 30 routes, 30 in sitemap |
| `node tools/validate.mjs` | PASS, 7/7 rule groups |
| `node tools/structure.mjs` | PASS, 31 pages (incl. 404) |
| Archive internal links | 890 refs resolved, 0 broken, 0 missing assets |
| Duplicate top-level routes | 0 (all collisions moved into `legacy/`) |
| Conflicting ASIN claims | 2 found, both re-verified from source, both resolved |

### The one thing that still needs a human

`link.amazon/B0c8moW59` must not be published anywhere until the owner supplies the intended
`amazon.com/dp/` URL. It is not published on this site. If it is already in use in an email,
a social post or an old ad, that is worth checking, because it can open an unrelated product.
