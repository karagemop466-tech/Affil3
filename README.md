# Affil3

An Amazon Associates publication for countertop kitchen appliances, generated from a verified source
register. Tracking ID `shopnow047c-20`.

**Live:** https://karagemop466-tech.github.io/Affil3/

Two rules run through the whole repository:

1. **A value that cannot be confirmed from an official source stays blank.** Blank is a documented
   result, and every blank is flagged with the step that would close it.
2. **A claim that cannot be sourced is not published.** No prices, no star ratings, no test results,
   no revenue forecasts.

## What is published

| Path | Status | Owner | What it is |
|---|---|---|---|
| `/` | indexable | `tools/build.mjs` | The publication: front page, 5 product pages, comparison, 3 categories, 8 guides, 13 record pages |
| `/editorial/` | `noindex`, robots-disallowed | `tools/build.py` | An independently generated earlier publication, kept for its verification provenance |
| `/legacy/` | robots-disallowed | — | The first session's site, preserved unchanged |

Search engines are offered one site. The archive trees remain readable but out of the index, because
deleting another session's work to tidy a sitemap would destroy verification history (decision S-16).

## Start here

| File | What it is |
|---|---|
| [`EXECUTIVE-SUMMARY.md`](EXECUTIVE-SUMMARY.md) | Current summary: the five links, what is verified, what blocks progress, what changed |
| [`COORDINATION.md`](COORDINATION.md) | Session boards, claims, verification logs, merge logs |
| [`QA-BRIEF.md`](QA-BRIEF.md) | 30 questions with answers and sources; read its correction banner first |
| [`data/`](data/) | Register for the root publication |
| [`data/register/`](data/register/) | Register for the archive publication |

On the site itself: [decision board](https://karagemop466-tech.github.io/Affil3/suggestions/) ·
[open questions](https://karagemop466-tech.github.io/Affil3/questions/) ·
[flagged for review](https://karagemop466-tech.github.io/Affil3/flagged/) ·
[source register](https://karagemop466-tech.github.io/Affil3/sources/).

## Build

Node 18+ for the root publication, Python 3.9+ for the archive. Neither has dependencies.

```bash
node tools/build.mjs     # data/*.json        -> repository root
node tools/verify.mjs    # 4,414 checks
python3 tools/build.py   # data/register/*   -> editorial/
python3 tools/check_site.py
npm run check            # node build + node verify
```

CI rebuilds both publications on every push and fails if the committed output drifts from the data.

## What the gate refuses to let through

Root publication (`tools/verify.mjs`, 4,414 checks):

- A page without the Associates statement, or without the disclosure strip above `<main>`.
- A page without a footer repeat of the disclosure.
- An Amazon link without `rel="sponsored"`, or a `/dp/` link without a 10-character ASIN.
- A `/dp/` link carrying a tag other than `shopnow047c-20`, or **any** Amazon link without the tag —
  including a link used only as evidence for an observation.
- An untagged `link.amazon` short link published as a link (they are shown as text, because a short link
  cannot carry the tag).
- A currency amount anywhere in the HTML. A price cannot be rendered, by construction.
- A missing image, an image without `alt`, or an image served from another host.
- An external stylesheet or font.
- A broken internal link, a missing anchor, or a page missing from the sitemap.
- A guide missing from the feed, or a feed item missing from the sitemap.
- A source ID that does not exist, a flag ID that does not exist, a question citing a source that does
  not exist, or a discovery step that closes nothing.
- A product row whose intended fields are filled without a confirmation date and source.
- A page whose title exceeds 75 characters or whose description falls outside 40–175 characters.
- An archive URL in the root sitemap, or an archive page missing its `noindex`.

Archive publication (`tools/check_site.py`): the same link, disclosure, tag, source and sitemap rules.

## The finding both registers agree on

Every supplied `link.amazon` short link resolves to an `amazon.com/dp/<ASIN>` URL **with no `tag=`
parameter**. Amazon's Program Policies §2(b) require the Associates ID as a URL parameter on every link
placed on a site. The supplied links are untagged — a different claim from *invalid*, and only the first
is made here (FLG-003).

The site therefore publishes constructed `https://www.amazon.com/dp/<observed ASIN>?tag=shopnow047c-20`
links and labels them as pending validation until one is tested in Associates Central (gate G-02).

## Licence and attributions

Product names and trademarks belong to their owners. Quoted listing titles are the seller's wording,
retrieved from the Amazon page on the stated date. The illustrations in `src/assets/img/` are original,
decorative, and explicitly not product photography. Neither publication is endorsed by or affiliated with
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
