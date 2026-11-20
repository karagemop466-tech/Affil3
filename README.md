# Crisp & Counter — Amazon affiliate publication (Affil3)

A shop-shaped kitchen-gear publication with its research desk in the open.
Products lead; the verification machinery is one footer link away. Every
published claim carries an official source link, every affiliate link is
marked, and everything unconfirmed is published on a **Flagged for Review**
page instead of being guessed.

**Live site:** https://karagemop466-tech.github.io/Affil3/
**Tracking ID in use:** `shopnow047c-20` (owner-supplied; validation gate G3 pending — FLG-004)

## What's here

| Path | What it is |
| --- | --- |
| `index.html`, `shop/`, `compare/`, `guides/`, `about/` | The reader-facing publication |
| `desk/` | Research desk: verification register, link register, flagged items, open questions, suggestion board, campaign ledger, analytics spec, compliance gate, coordination log |
| `data/products.json` | Data of record for the five submitted links (intent fields ≠ observed fields) |
| `data/registers.json` | Sources (S01–S13), flags (FLG-001…010), questions (Q-01…10), suggestions (SG-01…12), event register, ledger schema |
| `content/guides/` | Seven question-shaped buyer guides (the publication's editorial voice) |
| `scripts/build_site.py` | Stdlib-only generator for the whole site (`--check` detects drift) |
| `scripts/check_site.py` | Content/compliance gates (disclosure, sponsored marking, sourced rows) |
| `scripts/build_sitemap.py` | Sitemap builder (`--check` for staleness) |
| `tools/verify_site.py` | Whole-tree release gate (exit 3 on violation) |
| `tools/link_report.py` | Per-table official-source coverage (`--strict`) |
| `tools/check_all_links.py` | Internal link integrity |
| `server/collect.js` | Self-hosted privacy-preserving event collector (Node, zero deps) |
| `docs/EXECUTIVE-SUMMARY.md` | The executive summary |
| `COORDINATION.md` | Shared task board (parallel sessions) |

## Build & verify

```sh
python3 scripts/build_site.py            # render the site
python3 tools/verify_site.py             # release gate (run before any publish)
python3 scripts/build_sitemap.py         # regenerate sitemap.xml from the tree
```

No third-party dependencies — Python standard library only. CI runs the same
gate on every push (`.github/workflows/site-checks.yml`).

## Verification stance (the rules this repo runs on)

1. Every table row links to an official source or is marked unverified.
2. Values that can't be confirmed stay **blank and flagged** — never inferred.
3. Intended ASIN / listing URL / confirmation date are stored separately from
   observed redirect targets and are never merged (Amazon defines an ASIN as a
   10-character identifier — source S04).
4. The supplied short links are recorded exactly as given; their compliance
   status is **unresolved**, and this project does not declare them invalid.
5. No conversion score or revenue forecast is presented anywhere.
6. Observed prices and ratings carry their observation date (2026-11-20).

## Disclosure

Crisp & Counter is a participant in the Amazon Services LLC Associates Program.
**As an Amazon Associate we earn from qualifying purchases.** The disclosure
strip sits under the masthead of every page and the full statement is repeated
in every footer — enforced automatically on each build.
