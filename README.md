# Affil3

Amazon Associates publications built from a verified source register. Tracking ID `shopnow047c-20`.

**Live:** https://karagemop466-tech.github.io/Affil3/

GitHub Pages serves `main` at `/`, so the repository contains more than one published surface.
Nothing was deleted to make room; each session's output is kept and reachable.

## What is published

| Path | Owner | What it is |
|---|---|---|
| `/` | root site (`tools/build.mjs`) | Integrated publication: shop, categories, guides, sources, questions, suggestions, flagged, ledger, measurement, compliance |
| `/editorial/` | `tools/build.py` | A second, independently generated publication: front page, 3 category pages, 5 product pages, 4 guides, source register, flagged-for-review, open questions, suggestions queue, dashboard, disclosure and method |
| `/legacy/arena-83a43a96/` | preserved | The first session's site, kept unchanged |
| `/shop/` | session `59aebafb` (`scripts/build.mjs`) | Third independent publication: 6 buyer guides, 4 product records, 4 shape clusters, a comparison table, and the full review board (22 suggestions, 22 open questions, 10 flags) — with an 11-gate compliance checker |

`/editorial/` exists because its build was written against a different data model and its verification
found things the other register did not. Keeping both builds preserves both verification passes rather
than merging them into one file whose provenance nobody can reconstruct.

## Read these first

| File | What it is |
|---|---|
| [`EXECUTIVE-SUMMARY.md`](EXECUTIVE-SUMMARY.md) | What the five links are, what was built, what is blocked |
| [`EXECUTIVE_SUMMARY-6249757a.md`](EXECUTIVE_SUMMARY-6249757a.md) | The root site's summary |
| [`QA-BRIEF.md`](QA-BRIEF.md) | 30 questions: answered, unanswered, and what closes each one |
| [`report/EXECUTIVE-SUMMARY.md`](report/EXECUTIVE-SUMMARY.md) | The `/shop/` session's summary: what the links resolve to, what was verified, what is blocked |
| [`report/DECISION-BRIEF.md`](report/DECISION-BRIEF.md) | The six answers that gate everything else, plus the discovery steps that obtain them |
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

## Build

**Shop site** (Node, no dependencies) — output is committed to `shop/`:

```bash
node scripts/build.mjs     # register/*.json + content/*.md  ->  shop/
node scripts/checks.mjs     # 11 gates; exit 1 blocks the merge
node scripts/serve.mjs      # http://localhost:8080/Affil3/shop/
node scripts/collect.mjs    # optional self-hosted event collector on :8788
```

Run via npm as `npm run shop:build`, `shop:check`, `shop:verify`, `shop:links`,
`shop:new-guide`, `shop:collect`, `shop:serve`. The `build` / `verify` / `check` names stay
pointed at the root site so nothing that already calls them breaks.

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

`/shop/` reaches the same conclusion from the other direction: it publishes no price and no rating
either, but it *does* render a buy button, built as a tagged `/dp/<ASIN>?tag=shopnow047c-20`
Special Link derived from the resolved ASIN rather than from the supplied short link. The two
surfaces differ on whether an untagged supplied link should be used at all — that disagreement is
recorded rather than averaged away, in `FLG-003` and in `register/links.json`.

## The finding all sessions independently agree on

Every submitted link resolves to an `amazon.com/dp/<ASIN>` URL **with no `tag=` parameter**. Amazon's
Program Policies §2(b) require the Associates ID as a URL parameter on every link placed on a site.
The links are untagged — that is a different claim from *invalid*, and only the first is made here.
The `/shop/` register records the same four resolved ASINs (`B0CDY277D3`, `B09B7SB46R`,
`B08DKYBTPH`, `B0DZFD6R9Z`), the same `redirect_had_tag: false`, and the same blank *intended* ASIN
on every row — two independent resolution passes agreeing is stronger evidence than either alone.

## Licence and attribution

Product names and trademarks belong to their owners. Specification values are quoted from the
publisher's own pages and cited by source ID. Neither publication is endorsed by or affiliated with
Amazon.com, Inc. beyond participation in the Amazon Associates program.

As an Amazon Associate I earn from qualifying purchases.
