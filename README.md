# Affil3

Amazon Associates publications built from a verified source register. Tracking ID `shopnow047c-20`.

**Live:** https://karagemop466-tech.github.io/Affil3/

GitHub Pages serves `main` at `/`, so the repository contains more than one published surface.
Nothing was deleted to make room; each session's output is kept and reachable.

## The shop

The root site is a shop front, not an audit trail. A visitor lands on five kitchen appliances, each
with a reason to pick it, the one number that decides it, and a way to buy. The registers are all
still there, behind the footer.

| Path | What a visitor finds |
|---|---|
| `/` | Front page: a hero, four "start here if" lanes, the five-product grid, category tiles |
| `/products/<slug>/` | One page per product: best for, not for, how to decide in a minute, every spec cited to the maker, buyer FAQ, buy link |
| `/compare/` | Basket versus oven-style, decided on published facts only |
| `/guides/` | Five question-shaped guides, each with a sourced table |
| `/search/` | Client-side search over products, guides and categories |
| `/categories/` | Three category clusters |

Everything below the shop is unchanged and still reachable from the footer of every page: the shop
table, source register, open questions, suggestions board, flagged items, ledger, measurement and
compliance pages.

## What is published

| Path | Owner | What it is |
|---|---|---|
| `/` | root site (`tools/build.mjs`) | Integrated publication: shop, product pages, compare, search, categories, guides, sources, questions, suggestions, flagged, ledger, measurement, compliance |
| `/editorial/` | `tools/build.py` | A second, independently generated publication: front page, 3 category pages, 5 product pages, 4 guides, source register, flagged-for-review, open questions, suggestions queue, dashboard, disclosure and method |
| `/legacy/arena-83a43a96/` | preserved | The first session's site, kept unchanged |

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

## What the root-site gate refuses to let through

Every figure on a product page must cite a manufacturer or observed source; a published value with no
source fails the build, and so does a blank value with no explanation next to it. On top of that:
no price-like amount anywhere, no star rating, a tagged link on every product page, `rel="sponsored"`
on every Amazon link, the Associates statement on every page, a product page for every product, sitemap
coverage, working internal links, and WCAG AA (4.5:1) contrast on every colour pair in the stylesheet.
That is 2,225 checks on the current tree.

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
