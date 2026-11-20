# Affil3 — Countertop & Co.

An Amazon Associates publication covering countertop cooking appliances, built from a verified source
register rather than from copy.

**Live site:** https://karagemop466-tech.github.io/Affil3/
**Tracking ID:** `shopnow047c-20`

## Read these first

| File | What it is |
|---|---|
| [`EXECUTIVE-SUMMARY.md`](EXECUTIVE-SUMMARY.md) | What the five links are, what was built, what is blocked |
| [`QA-BRIEF.md`](QA-BRIEF.md) | 30 questions: answered, unanswered, and what closes each one |
| [`COORDINATION.md`](COORDINATION.md) | Shared task board, claims, and the verification log |
| [`data/`](data/) | The registers. These are the source of truth; the site is generated from them |
| [`docs/`](docs/) | The generated site. Do not hand-edit — change `data/` and rebuild |

## Build

```bash
python3 tools/build.py        # data/*.json -> docs/
python3 tools/check_site.py   # gate: links, prices, ratings, tags, disclosure, sitemap
```

The build is deterministic. CI rebuilds from `data/` and fails if the committed `docs/` differs.

## What the gate refuses to let through

- A price. No currency amount may appear in the HTML at all.
- A star rating or review count.
- A product call-to-action without `tag=shopnow047c-20`.
- An Amazon citation that is not marked `rel="nofollow"`.
- A page without the required Associates statement.
- A spec row citing a source ID that does not exist.
- A page missing from the sitemap.

This is why **no buy button renders yet**: the supplied links carry no tracking tag. See FLG-003 on the
[Flagged for review](https://karagemop466-tech.github.io/Affil3/flagged/) page.

## Data model

| File | Holds |
|---|---|
| `data/sources.json` | 19 sources, tiered, each with what it supports and when it was read |
| `data/products.json` | 5 entries plus 7 flags. Every spec carries `value`, `source`, and `note` |
| `data/compliance.json` | 12 policy rules with quoted basis, plus the 5 measurement events |
| `data/campaign-ledger.json` | Empty ledger schema. No row exists without an authorized report |
| `data/suggestions.json` | 14 proposals held for a decision |
| `data/questions.json` | 24 questions with owner and resolution method |

A field is `null` when no official source stated it. A field is `listing_only: true` when the value came
from a retailer page rather than the manufacturer. Neither is ever filled in to look complete.

## Measurement

`docs/assets/analytics.js` records five events — `page_view`, `outbound_product_click`, `guide_read`,
`suggestion_vote`, `disclosure_view` — with no cookies, no identifiers, and no full URLs. The endpoint is
unset by default, so it records nothing. Set it at build time:

```bash
ANALYTICS_ENDPOINT="https://your-endpoint.example/collect" python3 tools/build.py
```

## Licence and attribution

Product names and trademarks belong to their owners. Specification values are quoted from the
publisher's own pages and cited by source ID. This publication is not endorsed by or affiliated with
Amazon.com, Inc. beyond participation in the Amazon Associates program.

As an Amazon Associate I earn from qualifying purchases.
