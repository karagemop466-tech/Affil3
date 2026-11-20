# Affil3

An Amazon Associates publication built from a sourced product register. Tracking ID `shopnow047c-20`. This repository does not yet connect an AI provider, product-data API, query data source, analytics endpoint, or Associates reporting feed; see the executive summary and S-13/Q-14 on the site. No autonomous research or publishing claims are made.

**Live:** https://karagemop466-tech.github.io/Affil3/

GitHub Pages serves `main` at `/`. The root publication is the only search-index surface. The earlier editorial build remains reachable at `/editorial/` as a `noindex` archive so its separate register stays reviewable without presenting a second publication to search engines.

## What is published

| Path | Owner | What it is |
|---|---|---|
| `/` | root site (`tools/build.mjs`) | Integrated publication: shop, categories, guides, sources, questions, suggestions, flagged, ledger, measurement, compliance |
| `/editorial/` | `tools/build.py` | Noindex archive of the independent editorial register and its review pages; not in the root sitemap or robots sitemap declarations |
| `/legacy/arena-83a43a96/` | preserved | The first session's site, kept unchanged |

`/editorial/` remains reachable because its build uses a separate data model and captures an independent verification pass. It is explicitly noindex; the root publication is canonical for discovery and sitemap submission.

## Read these first

| File | What it is |
|---|---|
| [`EXECUTIVE-SUMMARY.md`](EXECUTIVE-SUMMARY.md) | What the five links are, what was built, what is blocked |
| [`EXECUTIVE_SUMMARY-6249757a.md`](EXECUTIVE_SUMMARY-6249757a.md) | Historical snapshot from an earlier integration; superseded by `EXECUTIVE-SUMMARY.md` and the live `/executive-summary/` page |
| [`QA-BRIEF.md`](QA-BRIEF.md) | Historical 30-question snapshot; the live `/questions/` page is the current decision register |
| [`COORDINATION.md`](COORDINATION.md) | Session claims, scopes, verification logs, merge history, and current integration notes |
| [`data/`](data/) | Register for the root site |
| [`data/register/`](data/register/) | Register for `/editorial/` |

## Build

**Root site** (Node, no dependencies):

```bash
node tools/build.mjs     # data/*.json  -> repository root
node tools/verify.mjs    # gates
```

**Editorial site** (Python, no dependencies):

```bash
python3 tools/build.py       # data/register/*.json -> editorial/
python3 tools/check_site.py  # gates
```

Both builds are deterministic. CI rebuilds both and fails if the committed output differs.

## What the editorial gate refuses to let through

- A price. No currency amount may appear in the HTML at all.
- A star rating or review count.
- A product call-to-action without `tag=shopnow047c-20`.
- An Amazon citation not marked `rel="nofollow"`.
- A page without the required Associates statement.
- A spec row citing a source ID that does not exist.
- A link that escapes the published subtree.
- A page missing from that subtree's sitemap.

This is why **no buy button renders on `/editorial/`**: the submitted links carry no tracking tag.
See `FLG-003` on the [flagged page](https://karagemop466-tech.github.io/Affil3/editorial/flagged/).

## The finding both sessions independently agree on

Every submitted link resolves to an `amazon.com/dp/<ASIN>` URL **with no `tag=` parameter**. Amazon's
Program Policies §2(b) require the Associates ID as a URL parameter on every link placed on a site.
The links are untagged — that is a different claim from *invalid*, and only the first is made here.

## Licence and attribution

Product names and trademarks belong to their owners. Specification values are quoted from the
publisher's own pages and cited by source ID. Neither publication is endorsed by or affiliated with
Amazon.com, Inc. beyond participation in the Amazon Associates program.

As an Amazon Associate I earn from qualifying purchases.
