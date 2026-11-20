# Executive summary — session `arena-2e0c91d0-affil3` (2026-11-20)

Independent review-and-corroboration pass. This session branched from `main` @ `9287de5`, found
two pipeline problems, fixed them, and while it worked, `main` moved: sessions `9abfdc62` (PR #29)
and `93cee724`/`4578ad4b` (PRs #22/#30) landed overlapping and larger fixes. This branch was then
merged with the new `main` keeping **their** versions of everything they had already fixed, and
keeping only what this session contributed that main did not have. Nothing was discarded; the
duplicate fixes are recorded below as corroboration rather than shipped twice.

## What this session found on `main` @ `9287de5` (independently, before seeing PR #29)

1. **The CI freshness gate checked a directory that does not exist.** `verify.yml` asserted
   `git diff --quiet -- docs` while the Python builder writes `editorial/` and the Node builder
   writes the repo root. Proof it mattered: a fresh rebuild produced a diff in
   `editorial/assets/site.css` (resolved-flag styles missing from the committed file) while CI on
   `main` reported success. — *Concurrently fixed on main by PR #29 ("Gate both generators in CI
   so output cannot drift from source") and the stale CSS by "Ship the stylesheet the source
   actually contains". This branch adopts their workflow and their CSS; the independent find is
   kept as corroboration (their log line R-09 records the same failure).*
2. **The two published sites took opposite outbound-link positions** (root rendered tagged
   `?tag=shopnow047c-20` buy buttons "pending gate G-02"; editorial withheld every outbound
   button). — *Already on main's decision board in better form: S-01 "Two publications in one
   repository" (current option excludes /editorial/ from search) and S-02 "Buy buttons while
   links are untested". This session's draft flag/suggestion were withdrawn at merge to avoid
   duplicate board entries.*

## What this session contributes to `main` (unique, shipped in PR #31)

- **Round-4 re-observation of two submitted short links** (`data/observations/2026-11-20-session-2e0c91d0.json`):
  `https://link.amazon/B04G1MEwY` → `https://www.amazon.com/dp/B0CDY277D3` (CHEFMAN 6 Quart Dual
  Basket Air Fryer Oven with Easy View Windows) and `https://link.amazon/B02NbDxp3` →
  `https://www.amazon.com/dp/B09B7SB46R` (Emeril Lagasse 26QT French Door Multi-Function Air
  Fryer Toaster Oven). Both match the register; neither final URL carried `tag=` (consistent with
  the open tag-attribution question and gate G-02). One transient HTTP 502 on the first attempt at
  B02NbDxp3; the retry succeeded. Intended ASINs remain **blank** everywhere — observations are
  not confirmations of intent.
- **Independent full re-fetch of S01** (Associates Program Operating Agreement,
  https://affiliate-program.amazon.com/help/operating/agreement): header still reads "Updated:
  October 15, 2025"; §1 still defines Special Links as links that "must properly use the special
  'tagged' link formats we provide"; §5 disclosure requirement matches the register's quote.
  Re-check notes appended to S01/S05 `method` fields in `data/sources.json`, and the regenerated
  `/sources/` page shows them.

## Verified state after the merge (gates run locally on the merged tree)

- Root site: `node tools/build.mjs && node tools/verify.mjs` → **28 pages, 1610 checks, 0 failed**.
- Editorial site: `python3 tools/build.py && python3 tools/check_site.py` → **21 pages, PASS**
  (internal links resolve; no prices; no ratings/review counts; every rendered Amazon link carries
  the tracking tag; Associates statement on every page; sitemap complete; feed/sitemap parse).
- A fresh rebuild of both leaves the working tree clean — the exact assertion CI now makes.
- GitHub Pages: enabled for `main` at root, status `built` (GitHub API, 2026-11-20):
  https://karagemop466-tech.github.io/Affil3/

## What still blocks scaling (unchanged; all owner steps)

- **Gate G-02:** test one Special Link per product in Associates Central; confirm destination and
  a tracking-report row before scaling (Program Policies, S02 on the register).
- **Intent confirmation:** intended ASINs behind the five short links (Q-01), whether they came
  from the enrolled account (Q-02), and whether this site is declared on the account (Q-03).
- **Analytics:** the collector exists (`tools/collector.mjs`, plus new `tools/analytics-endpoint/`
  from main) but has no host; GitHub Pages cannot run it. No events are recorded yet.
- **Search Console:** needs a Google account owner.

## Source links for manual review

- Operating Agreement: https://affiliate-program.amazon.com/help/operating/agreement
- Program Policies: https://affiliate-program.amazon.com/help/operating/policies
- FTC Disclosures 101: https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers
- 16 CFR Part 255: https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255
- Google, qualify outbound links: https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links
- Re-fetched short links: https://link.amazon/B04G1MEwY · https://link.amazon/B02NbDxp3
- Live registers: /sources/ · /flagged/ · /suggestions/ · /questions/ on
  https://karagemop466-tech.github.io/Affil3/
