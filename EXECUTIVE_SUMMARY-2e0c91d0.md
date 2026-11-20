# Executive summary — session `arena-2e0c91d0-affil3` (2026-11-20)

Review-and-integration pass over the Affil3 repo at `main` @ `9287de5`. Earlier sessions built the
two published sites and the data registers; this session re-verified what could be re-verified from
official sources today, fixed what was broken, and added the new findings to the decision board.
Nothing was inferred: every new field cites a source or is left blank.

## State of the project (verified today)

- **Live site:** GitHub Pages is enabled for `karagemop466-tech/Affil3` (`main`, root path), status
  `built`: https://karagemop466-tech.github.io/Affil3/ (root publication "Affil3") and
  https://karagemop466-tech.github.io/Affil3/editorial/ (reader publication "Countertop & Co.").
  Confirmed via the GitHub API (`repos/.../pages`) on 2026-11-20.
- **Tracking ID:** `shopnow047c-20`, matching the Associates `-20` US convention (source register
  S03). Ownership by the owner's Associates account is still unconfirmed (FLG-011, Q-03).
- **Products:** all five submitted `link.amazon` short links resolve to amazon.com detail pages.
  This session independently re-fetched two of them: `B04G1MEwY → B0CDY277D3` (CHEFMAN 6 Qt Dual
  Basket Air Fryer Oven) and `B02NbDxp3 → B09B7SB46R` (Emeril Lagasse 26QT French Door Air Fryer
  Toaster Oven). Both match the register exactly; neither final URL carried a `tag=` parameter.
  Recorded in `data/observations/2026-11-20-session-2e0c91d0.json`. Intended ASINs remain blank
  everywhere (FLG-001, FLG-002, Q-01) — only the owner can confirm intent.
- **Policy sources:** the Associates Operating Agreement (S01) was re-fetched in full today;
  the page still reads "Updated: October 15, 2025" and §1 still defines Special Links as links
  using the tagged formats Amazon provides. The register's `used_for` text matches the page.
- **Gates:** root site `node tools/verify.mjs` → 23 pages, 1322 checks, 0 failed. Editorial site
  `python3 tools/check_site.py` → 21 pages, PASS (internal links resolve, no prices, no ratings,
  tracking tag on every rendered Amazon link, Associates statement on every page, sitemap complete).

## Irregularities found this session

1. **FLG-023 (fixed): the CI freshness gate checked a directory that does not exist.**
   `.github/workflows/verify.yml` rebuilt with `tools/build.py` and asserted
   `git diff --quiet -- docs` — but the builder writes `editorial/`, and the root builder writes
   the repo root. Proof it mattered: a fresh rebuild today produced a diff in
   `editorial/assets/site.css` (resolved-flag styles missing from the committed file) while CI on
   `main` reported success. The workflow now runs **both** builders, asserts the whole tree is
   clean afterwards, and runs **both** gates. The stale CSS is committed regenerated.
2. **FLG-024 (open, owner decision): the two publications take opposite outbound-link positions.**
   The root site renders tagged `View on Amazon` buttons (`?tag=shopnow047c-20`,
   `rel="sponsored"`, annotated "pending validation, gate G-02"); the editorial site withholds
   every outbound button pending the same gate. Both are defensible; together they are
   inconsistent. Decision path added to the board as **S-13** (options A–D, recommendation:
   withhold on both until G-02 passes, then consolidate to one publication).

## What still blocks scaling (unchanged, all owner steps)

- **G-02 / Q-04:** test one Special Link per product in Associates Central and confirm the
  destination and a tracking-report row before any scaling (S02).
- **Q-01/Q-02/Q-03:** intended ASINs behind the five short links, whether they came from the
  enrolled account, and whether this site is declared on the account.
- **FLG-009 / S-03:** the analytics collector (`tools/collector.mjs`) exists but has no host;
  GitHub Pages cannot run it. No events are recorded until an endpoint is deployed.
- **FLG-013 / S-12:** Search Console needs a Google account owner.
- **FLG-007 / S-02:** five guides are published; the application-review rule of thumb is "at
  least 10 posts" (S11).

## Files changed this session

`.github/workflows/verify.yml` · `data/flags.json` (+FLG-023, +FLG-024) · `data/suggestions.json`
(+S-13) · `data/sources.json` (re-check notes on S01, S05) ·
`data/observations/2026-11-20-session-2e0c91d0.json` (new) · regenerated `flagged/`,
`suggestions/`, `sources/` pages and `editorial/assets/site.css` · `COORDINATION.md` · this file.

## Source links for manual review

- Operating Agreement: https://affiliate-program.amazon.com/help/operating/agreement (fetched 2026-11-20)
- Program Policies: https://affiliate-program.amazon.com/help/operating/policies
- FTC Disclosures 101: https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers
- Google, qualify outbound links: https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links
- Submitted links re-fetched: https://link.amazon/B04G1MEwY · https://link.amazon/B02NbDxp3
- Full register with per-row methods and statuses: https://karagemop466-tech.github.io/Affil3/sources/
- Flags: https://karagemop466-tech.github.io/Affil3/flagged/ · Decision board: https://karagemop466-tech.github.io/Affil3/suggestions/
