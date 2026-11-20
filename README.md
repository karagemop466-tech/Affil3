# Affil3 — ShopNow Kitchen

An Amazon Associates publication site for air-fryer and small-kitchen-appliance
buying guidance, built to be shop-first for readers and audit-grade behind the
scenes.

- **Tracking ID:** `shopnow047c-20`
- **Live site:** https://karagemop466-tech.github.io/Affil3/ (GitHub Pages, deployed from `main`)
- **Board:** see [`COORDINATION.md`](COORDINATION.md) before doing any work in this repo.

## Repository layout

```
index.html              Publication front page (products lead)
guides/                 Question-shaped buying guides
products/index.html     Product register + product-intent confirmation records
sources.html            Source register (every table row cites an official URL)
requirements.html       Requirements register (brief → implementation)
suggestions.html        Suggestions awaiting a human decision
decision-brief.html     Questions, known/unknown info, discovery plans
flagged-for-review.html Published irregularities (never blocks the merge)
executive-summary.html  Executive summary
analytics.html          Five defined events + campaign ledger view
workflow.html           Publishing cadence + compliance gates
editorial-policy.html, privacy.html, 404.html
assets/                 CSS, JS (privacy-preserving counter), images
content/                Guide bodies (HTML fragments consumed by the generator)
data/                   JSON/CSV registers consumed by the generator
feed.xml, sitemap.xml, robots.txt
tools/                  build_site.py, compliance_gate.py, check_links.py, analytics_server.py
.github/workflows/      CI: drift check + gates + Pages deploy
```

## Rules of the road

1. Never publish a value that is not verifiable from an official source — leave it
   blank, mark it `unverified`, and flag it.
2. Intended ASIN (as submitted) and observed redirect target are **separate fields**;
   never merge them. No validity claim is made about submitted short links (FLG-003).
3. Every outbound product link carries `rel="sponsored nofollow"` and a visible
   "paid link" label. The Associates statement appears above the fold on every page.
4. No conversion scores, revenue forecasts, or unverified traffic claims — the
   campaign ledger starts empty and only accepts data from authorized first-party reports.
5. Edit `data/*.json` + `content/` and re-run `python3 tools/build_site.py`; the CI
   drift check fails if committed HTML does not match the registers.
