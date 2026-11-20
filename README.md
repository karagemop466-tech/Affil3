# Affil3 · The Crisp Index

An Amazon affiliate publication site for countertop-kitchen products (air fryers,
countertop ovens, kitchen gadgets), built around tracking ID **shopnow047c-20**.

**Live site (GitHub Pages):** https://karagemop466-tech.github.io/Affil3/

## What this repository contains

| Path | What it is |
|------|-----------|
| `docs/` | The published static site (GitHub Pages source) — generated, committed |
| `data/` | The registers everything renders from: products (intended vs observed), flags, questions, suggestions, sources, ledger, site config |
| `tools/build_site.py` | Stdlib-only static site generator (`python3 tools/build_site.py`) |
| `tools/validate.py` | Data + compliance validator (disclosure, sponsored rels, source links, blank-and-flag rule) |
| `tools/check_links.py` | Internal link + anchor checker |
| `tools/analytics-endpoint/` | Reference self-hosted click-counter endpoint (Cloudflare Worker + Python server) — the gate behind `docs/site-config.js` |
| `VERIFICATION.md` | Line-by-line verification log with official source links |
| `EXECUTIVE_SUMMARY.md` | The executive summary (also rendered on the site) |
| `COORDINATION.md` | Shared task board for parallel sessions — read before working here |

## Rebuild & verify

```bash
python3 tools/build_site.py   # regenerates docs/ from data/
python3 tools/validate.py     # data + compliance gates
python3 tools/check_links.py  # internal links + anchors
```

## Core rules baked into the build

1. **Reads like a shop, sourced like a register.** Guides lead; dashboards live in one
   footer group (“The Workshop”).
2. **Disclosure above the fold on every page** — the exact statement “As an Amazon
   Associate I earn from qualifying purchases.” — repeated in every footer.
3. **Every outbound product link is marked Sponsored** (`rel="sponsored nofollow noopener"`
   + visible chip).
4. **Intended vs observed are never merged.** Submitted tokens live in `intended.*`;
   observed redirect targets live in `observed.*`.
5. **Blank beats invented.** Unconfirmable values are blank + flagged on the site’s
   Flagged for Review page.
6. **Nothing scales before validation** — one link per product must pass the Associates
   workflow test before more products are added.
7. **Measure before optimizing** — the campaign ledger stays empty until authorized
   first-party reports exist; no conversion scores, no revenue forecasts.

Start with `EXECUTIVE_SUMMARY.md`, then the site’s `/workshop/suggestions.html` and
`/workshop/questions.html` for the decisions that need an owner.
