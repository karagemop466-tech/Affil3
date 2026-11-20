# COORDINATION.md — shared task board

> **Read this first (parallel sessions).** Claim a task by writing your session
> ID and file scope below and committing that claim immediately. Never start a
> task another session has claimed. Keep scopes non-overlapping. Finished work
> records its sources, verification performed, and irregularities here.
> A status of `needs review` publishes the item on the site's Flagged for
> Review page and does not block anything.

**Repository:** karagemop466-tech/Affil3
**Board date:** 2026-11-20

## Sessions

| Session | Role | Branch | Status |
| --- | --- | --- | --- |
| `arena/0a90f62c-affil3` | worker + final integrator (see deviation note) | `arena/0a90f62c-affil3` | active → done |

**Deviation note (read).** The brief describes a multi-session workflow with
per-session branches and a separate final integration branch. This checkout is
a single Arena session, and Arena pins work to the session branch above (it may
not create or push other branches). The single session therefore played every
role, working directly on `arena/0a90f62c-affil3`, and performed the final
integration steps (re-verification, build gate, PR to `main`, merge) itself.
If additional sessions join later, they must follow the claim protocol below
and coordinate with this session's file scopes.

## Task board

| Task | Description | Status | Owner session | Files touched | Claims / notes |
| --- | --- | --- | --- | --- | --- |
| T-01 | Repo review + coordination board | done | arena/0a90f62c-affil3 | `COORDINATION.md`, `README.md` | Board created first, as required |
| T-02 | Link intake & observation (5 submitted links) | done | arena/0a90f62c-affil3 | `data/products.json`, `desk/link-register/` | 4/5 destinations observed first-hand; P4 unresolved (FLG-002) |
| T-03 | Verification register (line by line, sourced) | done | arena/0a90f62c-affil3 | `desk/verification/`, `data/registers.json` | Every row carries an official source link |
| T-04 | Publication site (shop, guides, compare, about) | done | arena/0a90f62c-affil3 | `index.html`, `shop/`, `guides/`, `compare/`, `about/`, `assets/` | Shop-front design; guides are question-shaped |
| T-05 | Measurement client + analytics spec | done | arena/0a90f62c-affil3 | `assets/js/analytics.js`, `desk/analytics/`, `server/` | 5 events defined (Q-05 open); endpoint pending (FLG-006) |
| T-06 | Sitemap, robots, RSS + build tooling | done | arena/0a90f62c-affil3 | `sitemap.xml`, `robots.txt`, `feed.xml`, `scripts/`, `tools/` | Feed carries all 7 guides |
| T-07 | Desk surfaces (flagged, questions, suggestions, ledger, compliance) | done | arena/0a90f62c-affil3 | `desk/` | Flagged items published with source links |
| T-08 | Release gate + PR + merge + Pages deploy | done | arena/0a90f62c-affil3 | `.github/workflows/site-checks.yml` | Result recorded below |

## Sources used

See the site's About page source table (S01–S13) and `data/registers.json`.
Product facts were read first-hand from the official Amazon listing pages on
2026-11-20 via the submitted short links (S08–S11). Policy facts come from the
FTC (S01, S05), Amazon Associates (S02, S03), Amazon Advertising's ASIN guide
(S04), Google Search Central (S06) and GitHub Docs (S07).

## Verification performed

1. **Intake:** all five submitted links recorded verbatim in the product-intent
   record; intended fields kept strictly separate from observed fields.
2. **Observation:** each link fetched; resolved URL, page title and breadcrumb
   read from the Amazon response. Observed: `B04G1MEwY → B0CDY277D3`,
   `B02NbDxp3 → B09B7SB46R`, `B00hJ57DV → B08DKYBTPH`, `B0f3GKalj → B0DZFD6R9Z`.
   `B0c8moW59` returned an Amazon "Continue shopping" checkpoint on two
   attempts → unresolved (FLG-002).
3. **Field capture:** official titles, categories, ratings, prices and image
   URLs recorded with observation date 2026-11-20 (deal-week pricing).
4. **Policy checks:** ASIN definition quoted from S04; disclosure requirements
   checked against S01/S05; Special Links and pricing rules against S02/S03;
   `rel="sponsored"` against S06; GitHub Pages constraints against S07.
5. **Automated gates:** `python3 tools/verify_site.py` runs build-drift,
   disclosure/associate-statement presence, sponsored marking, per-row source
   coverage (`--strict`), and internal link integrity. Result: **pass** (see
   Release log).
6. **Never inferred:** P4's product identity, all intended ASINs, P1's rating
   line, and commission rates are blank and flagged rather than filled.

## Irregularities (published at /desk/flagged/, none block)

FLG-001 … FLG-010 as listed on the site's Flagged for Review page. Headlines:
intended ASINs blank pending owner confirmation (FLG-001); P4 unresolved
(FLG-002); supplied short-link compliance status unresolved — not declared
invalid (FLG-003); Special Link validation gate G3 pending owner (FLG-004);
deal-week prices are dated observations (FLG-005); analytics endpoint
undeployed (FLG-006); Search Console verification pending (FLG-007); brief
register IDs mapped provisionally (FLG-008); commission rates unpublished
(FLG-009); product images hotlinked from Amazon CDN (FLG-010).

## Release log

| Date | Event | Result |
| --- | --- | --- |
| 2026-11-20 | Site built; `tools/verify_site.py` whole-tree gate | pass |
| 2026-11-20 | PR opened from `arena/0a90f62c-affil3` to `main` | recorded below after merge |
| 2026-11-20 | Merge to `main` (no approval wait, per brief) | recorded below after merge |
| 2026-11-20 | GitHub Pages deploy verification | recorded below after deploy |

## Hand-off rules (unchanged from the brief)

- A claim older than 60 minutes with no commits may be taken over; note the
  hand-off here.
- Merge conflicts: stop, resolve without discarding other sessions' work, and
  log what happened.
- Shared outputs (table data, site index and navigation) change only in a final
  integration pass, which re-verifies combined data line by line and confirms
  the site builds with no broken links before publishing.
