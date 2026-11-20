# COORDINATION.md — shared task board

Repo: `karagemop466-tech/Affil3` · Base: `main @ 847ae37` · Working branch: `arena/6ca11b63-affil3`

## Session and branch rules

- **Session ID:** `arena-6ca11b63` (the only session that has written to this repo as of this claim; no other session claims, branches, or log entries existed when this board was created).
- **Branch deviation:** the task brief asks for `session-<id>/<task>` branches. The Arena session is bound to a single branch, `arena/6ca11b63-affil3`, and must not switch or create branches. All tasks below are therefore committed to that one branch. Scopes are still kept separate by directory (see "Files touched").
- **Integration:** this session is also the final integration session. Shared outputs (`docs/`, `data/`, `README.md`, `COORDINATION.md`) are changed only by this session.

## Task board

| ID | Task | Status | Owner | Files touched |
|---|---|---|---|---|
| T01 | Repo review; irregularity log | done | arena-6ca11b63 | `COORDINATION.md`, `data/flags.json` |
| T02 | Product-intent confirmation records (intended ASIN vs observed redirect) | done | arena-6ca11b63 | `data/products.json` |
| T03 | Source register (official URLs, retrieval date, what each supports) | done | arena-6ca11b63 | `data/sources.json` |
| T04 | Static site generator + pages (landing, category, dashboard) | done | arena-6ca11b63 | `scripts/build_site.py`, `docs/**` |
| T05 | Compliance: Associates statement, disclosure strip (every page + footer), `rel="sponsored"` on every outbound product link | done | arena-6ca11b63 | `scripts/build_site.py`, `docs/**` |
| T06 | Measurement: outbound-click hook, self-hosted endpoint **gated**, campaign ledger (empty) | done (endpoint gated) | arena-6ca11b63 | `docs/assets/analytics.js`, `data/campaign_ledger.csv` |
| T07 | Editorial: question-led guides, sitemap, RSS feed | done | arena-6ca11b63 | `data/guides.json`, `docs/guides/**`, `docs/sitemap.xml`, `docs/feed.xml`, `docs/robots.txt` |
| T08 | Questions, suggestions (decision board), executive summary, Flagged for Review page | done | arena-6ca11b63 | `data/questions.json`, `data/suggestions.json`, `docs/questions.html`, `docs/suggestions.html`, `docs/executive-summary.html`, `docs/flagged.html` |
| T09 | Validation gate (`check_site.py`): row-level source links, disclosure presence, sponsored rel, internal links | done | arena-6ca11b63 | `scripts/check_site.py` |
| T10 | Integration: rebuild, re-verify combined data, gate, PR to `main`, merge, enable/confirm GitHub Pages | in progress (build and gate pass locally) | arena-6ca11b63 | all shared outputs |

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
