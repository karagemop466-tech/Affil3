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
| `/docs/` | session `arena/c46310a7-affil3` | A third, independently generated publication: shop front, product register with the product-intent confirmation record, 4 buyer guides, comparisons, analytics, suggestions, decision questions, flagged items, compliance, executive summary. Verified with `scripts/` (sitemap, feed, link checker, intake validator, source verifier) and a self-hosted analytics endpoint in `server/` |
| `/kitchen-edit/` | `tools/build_kitchen_edit.py` (session `arena/0a417943-affil3`) | A fourth, reader-facing publication: shop-first front page, 4 question-shaped guides with FAQ JSON-LD, 5 product profiles carrying full intent/observation records, source register, flagged-for-review, decision-readiness questions, suggestion review board, compliance gate, analytics/ledger, working dashboard. Outbound CTAs follow the canonical register's tagged `/dp/<observed-ASIN>?tag=shopnow047c-20` destinations; submitted short links appear as evidence only. Its own gates (`tools/validate_kitchen_edit.py`, G-A1..G-A7) run via `.github/workflows/kitchen-edit-gates.yml`, scoped to its subtree |
| `/legacy/arena-83a43a96/` | preserved | The first session's site, kept unchanged |

`/editorial/` and `/docs/` exist because their builds were written against different data models and
each verification pass found things the other register did not. Keeping all builds preserves every
verification pass rather than merging them into one file whose provenance nobody can reconstruct.

## Read these first

| File | What it is |
|---|---|
| [`EXECUTIVE-SUMMARY.md`](EXECUTIVE-SUMMARY.md) | What the five links are, what was built, what is blocked |
| [`EXECUTIVE_SUMMARY-6249757a.md`](EXECUTIVE_SUMMARY-6249757a.md) | The root site's summary |
| [`QA-BRIEF.md`](QA-BRIEF.md) | 30 questions: answered, unanswered, and what closes each one |
| [`COORDINATION.md`](COORDINATION.md) | All session boards, claims, verification logs, merge logs |
| [`data/`](data/) | Register for the root site |
| [`data/c46310a7-affil3/`](data/c46310a7-affil3/) | Register for the `/docs/` site (session-scoped copy; identical content to the session's committed records) |
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

**Docs site** (Python, standard library only):

```bash
python3 scripts/build_sitemap.py --check   # docs/sitemap.xml covers every live page
python3 scripts/check_links.py            # no broken internal links in docs/
python3 scripts/build_feed.py             # keep docs/rss.xml in sync
python3 scripts/amazon_intake.py --link 'https://link.amazon/B04G1MEwY' --validate-only
python3 scripts/verify_sources.py         # re-check recorded official listing URLs
python3 server/analytics_server.py --port 8080   # self-hosted analytics endpoint (no IPs stored)
```

**Kitchen-edit site** (Python, no dependencies):

```bash
python3 tools/build_kitchen_edit.py      # kitchen-edit/src/*.html -> kitchen-edit/
python3 tools/validate_kitchen_edit.py   # gates G-A1..G-A7 (scoped to kitchen-edit/)
```

All builds are deterministic. CI rebuilds the root and editorial sites and fails if the committed
output differs; the docs-site workflow (`.github/workflows/check.yml`) runs the docs-site gates;
the kitchen-edit workflow (`.github/workflows/kitchen-edit-gates.yml`) runs its gates, scoped to
its subtree.

## What the root gate refuses to let through

`node tools/verify.mjs` runs **2,808 checks** over the 28 published pages. It stops the build on:

- a page without the Associates statement, the disclosure strip above `<main>`, or the footer repeat;
- an Amazon retail link without `tag=shopnow047c-20`, or without `rel="sponsored"`;
- a `link.amazon` short link published as a clickable link (it cannot carry the tag, so it renders as text);
- a currency amount anywhere in the HTML, a star rating or a review count;
- an image that is missing, remote, or without `alt` text;
- a page without a canonical URL, with more than one `h1`, or with a title longer than 90 characters;
- a broken internal link, a missing anchor, or a page missing from the sitemap;
- a source ID that does not exist, or a spec row citing one.

The link rules are enforced by the build itself (`linkPolicy` in `tools/build.mjs`), so a new template
cannot bypass them, and by the gate, so a hand-edited page cannot either.

## One indexable site

`robots.txt` disallows `/editorial/`, `/legacy/` and `/crisp-index/`, and every `/editorial/` page also
carries `<meta name="robots" content="noindex,nofollow">`. The root publication is the one site offered
to search engines; the other surfaces stay online and reachable for the people who need their evidence.

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

## Disclosure

This site participates in the Amazon Associates Program and earns from qualifying purchases.
Every outbound product link is marked as sponsored. Sources:

- [Associates Program Operating Agreement](https://affiliate-program.amazon.com/help/operating/agreement)
- [Associates Program Policies](https://affiliate-program.amazon.com/help/operating/policies)
- [FTC endorsements guidance](https://www.ftc.gov/business-guidance/advertising-marketing/endorsements-influencers-reviews)
- [Google rel="sponsored" guidance](https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links)

## Licence and attribution

Product names and trademarks belong to their owners. Specification values are quoted from the
publisher's own pages and cited by source ID. Neither publication is endorsed by or affiliated with
Amazon.com, Inc. beyond participation in the Amazon Associates program.

As an Amazon Associate I earn from qualifying purchases.

---

## Session `93cee724` addition (integrated 2026-11-20; nothing above changed)

| Path | Owner | What it is |
|---|---|---|
| `/crisp-index/` | `tools/build_site.py` (Python, stdlib) | A third publication surface: shop front page, 5 question-shaped guides (incl. seasonal), compare hub, test queue with verbatim listing quotes, about/methodology, disclosure, and a Workshop group (product register with intended-vs-observed separation, flagged-for-review, suggestions & decisions queue, open questions, campaign ledger & analytics gates) |

Also added at root: [`VERIFICATION.md`](VERIFICATION.md) (line-by-line verification log,
sources S-01…S-15 with links for manual review) and
[`EXECUTIVE_SUMMARY-93cee724.md`](EXECUTIVE_SUMMARY-93cee724.md). This session's register is
[`data/93cee724/`](data/93cee724/) (its own namespace — `data/*.json` above are untouched).

**Build & gates (this surface):**

```bash
python3 tools/build_site.py   # data/93cee724/*.json -> crisp-index/
python3 tools/validate.py     # data + compliance gates
python3 tools/check_links.py  # internal links + anchors
```

**Find worth knowing:** the Amazon-owned ASIN definition that FLG-012 (board) recorded as
"not located" exists at https://sell.amazon.com/blog/what-is-an-asin (10-character format;
ASIN appears after `/dp/`). Cited as S-03 in `VERIFICATION.md`.
