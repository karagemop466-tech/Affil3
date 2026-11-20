# Affil3

Amazon Associates publications built from a verified source register. Tracking ID `shopnow047c-20`.

**Live:** https://karagemop466-tech.github.io/Affil3/

GitHub Pages serves `main` at `/`, so the repository contains more than one published surface.
Nothing was deleted to make room; each session's output is kept and reachable.

## What is published

| Path | Owner | What it is |
|---|---|---|
| `/` | **Crisp & Counter** (`scripts/build_site.py`, session 0a90f62c) | Current root publication: shop, compare, 7 question-shaped guides, research desk (verification register, link register, flagged, questions, suggestion board, campaign ledger, analytics, compliance, coordination) |
| `/editorial/` | `tools/build.py` | A second, independently generated publication: front page, 3 category pages, 5 product pages, 4 guides, source register, flagged-for-review, open questions, suggestions queue, dashboard, disclosure and method |
| `/legacy/arena-83a43a96/` | preserved | The first session's site, kept unchanged |
| `/legacy/arena-4578ad4b/` | preserved | The previous integrated root edition (`tools/build.mjs`, sessions 6249757a/f761b123/4578ad4b), kept unchanged; internal `/Affil3/...` links rewritten into the archive so it is self-contained |

`/editorial/` exists because its build was written against a different data model and its verification
found things the other register did not. Keeping both builds preserves both verification passes rather
than merging them into one file whose provenance nobody can reconstruct.

## Read these first

| File | What it is |
|---|---|
| [`EXECUTIVE-SUMMARY.md`](EXECUTIVE-SUMMARY.md) | What the five links are, what was built, what is blocked |
| [`EXECUTIVE_SUMMARY-6249757a.md`](EXECUTIVE_SUMMARY-6249757a.md) | The root site's summary |
| [`QA-BRIEF.md`](QA-BRIEF.md) | 30 questions: answered, unanswered, and what closes each one |
| [`COORDINATION.md`](COORDINATION.md) | Three session boards, claims, verification logs, merge logs |
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


## Crisp & Counter — current root edition (session `arena/0a90f62c-affil3`)

The root site is a shop-shaped publication with its research desk in the open. Every published
claim carries an official source link; every affiliate link is marked `rel="sponsored"` and
tagged `shopnow047c-20`; everything unconfirmed is published on the Flagged for Review page
instead of being guessed.

```bash
python3 scripts/build_site.py        # render the root edition (stdlib only)
python3 tools/verify_site.py         # release gate (build drift, disclosures, sources, links)
python3 scripts/build_sitemap.py     # regenerate sitemap.xml from the tree
```

Data of record for this edition: `data/products-0a90f62c.json` (intent fields kept strictly
separate from observed redirect targets) and `data/registers.json` (sources S01–S13, flags
FLG-001…010, questions Q-01…10, suggestions SG-01…12, event register, campaign ledger schema).
`server/collect.js` is the self-hosted privacy-preserving analytics collector (not deployable
on GitHub Pages — see FLG-006).

Verification stance: every table row links to an official source or is marked unverified;
values that can't be confirmed stay blank and flagged; observed prices and ratings carry their
observation date (2026-11-20); no conversion score or revenue forecast is presented anywhere.
See [`docs/EXECUTIVE-SUMMARY.md`](docs/EXECUTIVE-SUMMARY.md) and the
[Coordination log](https://karagemop466-tech.github.io/Affil3/desk/coordination/).

**Note on `tools/build.mjs`:** its root output is superseded by `scripts/build_site.py`. The
previous root edition is preserved at `legacy/arena-4578ad4b/`; regenerating it to root would
overwrite the live site — coordinate in COORDINATION.md first. `tools/build.py` -> `editorial/`
is unaffected.
