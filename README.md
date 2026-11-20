# Countertop Journal (Affil3)

A static buyer-guide site for five submitted Amazon links, published with GitHub Pages from `docs/`.

## Layout

| Path | What it is |
|---|---|
| `data/` | Source of truth: product register, source register, findings, questions, suggestions, flags, measurement events, site settings, and the campaign ledger. |
| `content/guides/` | Question-shaped guides (Markdown with front matter). |
| `content/pages/` | Disclosure, privacy, about, executive summary. |
| `tools/build_site.py` | Generates `docs/` (HTML, sitemap, RSS, robots.txt). Stdlib only. |
| `tools/check_site.py` | Compliance and integrity checks on `docs/`. Fails the build on any violation. |
| `assets/` | Stylesheet and the measurement script (no-op until an endpoint is configured). |
| `analytics/collect_server.py` | Self-hosted receiver. Counts only. Not hosted by GitHub Pages (FLG-004). |
| `tests/` | Tests for the receiver. |
| `COORDINATION.md` | Shared task board, sessions, irregularity log. |

## Build and check

```bash
python3 tools/build_site.py      # regenerate docs/
python3 tools/check_site.py      # must print "check ok"
python3 -m unittest tests/test_collect.py
```

## Rules the checker enforces

- The Associates statement "As an Amazon Associate I earn from qualifying purchases." is present above `<main>` and in the footer on every page.
- Every Amazon link carries `rel="sponsored"`.
- No currency amounts, star ratings or rating counts appear on the site.
- Every product register row links its recorded source.
- The campaign ledger has no rows until first-party reports exist.
- The measurement script contains no storage or identifier code.

## Not in this repository

- Prices, availability and star ratings (not permitted without an approved data path).
- Amazon product photos.
- Any first-party campaign data.

See `data/flags.json` for open items and `data/suggestions.json` for decisions awaiting the owner.
