# Affil3

A static buyer's guide for small kitchen appliances, built from the Amazon listings the owner submitted. Published with GitHub Pages from `docs/`.

- **Live site:** https://karagemop466-tech.github.io/Affil3/
- **Start here:** [Flagged for Review](https://karagemop466-tech.github.io/Affil3/flagged.html) · [Executive summary](https://karagemop466-tech.github.io/Affil3/executive-summary.html) · [Suggestions — choose a path](https://karagemop466-tech.github.io/Affil3/suggestions.html)
- **Task board:** [COORDINATION.md](COORDINATION.md)

## How it is built

```
data/            single source of truth (JSON / CSV)
  products.json        product-intent records (intended ASIN and observed target kept separate)
  sources.json         source register (official URLs, what each supports)
  analysis.json        counts computed from the records (no scores or forecasts)
  flags.json           irregularities and unverified items
  questions.json       questions that must be answered before decisions
  suggestions.json     options for owner choice (nothing implemented until chosen)
  guides.json          working-title guides (questions and checks, no product claims)
  measurement.json     proposed events and privacy design (endpoint gated)
  campaign_ledger.csv  empty by design; rows only from authorized first-party reports
scripts/
  build_site.py        generates every page in docs/ from data/ (stdlib only)
  check_site.py        validation gate; exits 1 on any failure
docs/            GitHub Pages source (generated HTML + assets/style.css + assets/analytics.js)
archive/         previous site from session arena-83a43a96 (PR #1), preserved and not published
```

Rebuild and verify:

```bash
python3 scripts/build_site.py && python3 scripts/check_site.py
```

The gate checks that:

- every page carries the Associates statement in the disclosure strip and in the footer;
- every link to an Amazon host has `rel="sponsored"`;
- every internal link resolves;
- every row of a sourced table has an official-source link, or is explicitly marked unverified;
- sitemap, RSS feed and robots.txt are valid and consistent.

## Ground rules

- A value is shown only if it is linked to an official source. If it cannot be confirmed, it is left blank and flagged. Nothing is inferred.
- The required statement is quoted exactly from the Associates Operating Agreement §5: "As an Amazon Associate I earn from qualifying purchases."
- Links to Amazon are marked sponsored. Prices are not shown unless the Associates Program Policies permit it.
- Analytics is built but **gated**: GitHub Pages cannot store events. Nothing is sent until an owner-controlled endpoint is set in `docs/assets/analytics.js`.

## Open items

See the Questions and Flagged pages on the live site, and the notes in `COORDINATION.md`. The short links need a one-product test in the Associates workflow before any scaling.
