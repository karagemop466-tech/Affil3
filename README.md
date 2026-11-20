# Affil3

Amazon Associates publications built from a verified source register. Tracking ID `shopnow047c-20`.

**Live:** https://karagemop466-tech.github.io/Affil3/

GitHub Pages serves `main` at `/`, so the repository contains more than one published surface.
Nothing was deleted to make room; each session's output is kept and reachable.

## What is published

| Path | Owner | What it is |
|---|---|---|
| `/` | root site (`tools/build.mjs`) | Integrated publication: shop, categories, guides, sources, questions, suggestions, flagged, ledger, measurement, compliance, privacy, design brief |
| `/editorial/` | `tools/build.py` | A second, independently generated publication: front page, 3 category pages, 5 product pages, 4 guides, source register, flagged-for-review, open questions, suggestions queue, dashboard, disclosure and method |
| `/legacy/arena-83a43a96/` | preserved | The first session's site, kept unchanged |

Three surfaces publishing the same five products is a deliberate preservation choice and an open
SEO problem, not a settled design. `robots.txt` currently advertises two of them. Deciding how many
a crawler should see is `S-18` on the [suggestions page](https://karagemop466-tech.github.io/Affil3/suggestions/).

`/editorial/` exists because its build was written against a different data model and its verification
found things the other register did not. Keeping both builds preserves both verification passes rather
than merging them into one file whose provenance nobody can reconstruct.

## Read these first

| File | What it is |
|---|---|
| [`EXECUTIVE-SUMMARY.md`](EXECUTIVE-SUMMARY.md) | What the five links are, what was built, what is blocked |
| [`EXECUTIVE_SUMMARY-6249757a.md`](EXECUTIVE_SUMMARY-6249757a.md) | The root site's summary |
| [`QA-BRIEF.md`](QA-BRIEF.md) | 30 questions: answered, unanswered, and what closes each one |
| [`DESIGN-BRIEF.md`](DESIGN-BRIEF.md) | Generated from [`data/design-brief.json`](data/design-brief.json). The brief to hand whoever redesigns this site next: diagnosed problems, invariants no art direction may relax, prescriptions with before-and-after copy, a forbidden-phrases list, and the prompt itself |
| [`COORDINATION.md`](COORDINATION.md) | Session boards, claims, verification logs, merge logs |
| [`data/`](data/) | Register for the root site |
| [`data/register/`](data/register/) | Register for `/editorial/` |
| [`data/observations/`](data/observations/) | Dated raw link-resolution records, one file per verification pass |

**Decide something?** [`/suggestions/`](https://karagemop466-tech.github.io/Affil3/suggestions/) is 25
rows in six tracks, each with options, cost, risk and what must be settled first. Reply with an ID and
an option letter, for example `S-18 B`. Nothing there is implemented until you choose.
[`/questions/`](https://karagemop466-tech.github.io/Affil3/questions/) is the other half: what is
already established from an official source, what is missing, who can supply it, and the step that
closes it.

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

Both builds are deterministic — a rebuild after a commit leaves the working tree clean, and CI
asserts it. `DESIGN-BRIEF.md` is generated too; edit the JSON, not the markdown.

## What each gate refuses to let through

**Root site** (`tools/verify.mjs`, 1699 checks):

- A price-like amount, a star rating or a review count.
- A product call-to-action without `tag=shopnow047c-20`, or a `/dp/` link whose ASIN is not 10 characters.
- An Amazon link that is not marked `rel="sponsored"`.
- A page without the disclosure strip above `<main>`, or without the Associates statement, or whose footer drops any dashboard.
- A cited source ID or flag ID that does not exist in the register.
- An internal link or in-page anchor that does not resolve.
- A page missing from the sitemap, or a guide missing from the feed.
- A stylesheet, script or webfont loaded from an external origin — the site makes no third-party request, and `/privacy/` says so.
- Intended-ASIN fields filled without an official listing URL, confirmation date and source. Observed redirect targets are kept in separate fields and the gate refuses to let them be merged.

**Editorial site** (`tools/check_site.py`, 8 checks):

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

## The finding three independent passes agree on

Every submitted link resolves to an `amazon.com/dp/<ASIN>` URL **with no `tag=` parameter**. Amazon's
Program Policies, Participation Requirements 2(b), require the Associates ID as a URL parameter on
every link placed on a site. The links are untagged — that is a different claim from *invalid*, and
only the first is made here.

Three passes reached that conclusion separately: the root register, the editorial register, and the
re-fetch recorded in
[`data/observations/2026-11-20-reverify-66f2548a.json`](data/observations/2026-11-20-reverify-66f2548a.json),
which enumerates every query parameter seen on each resolved URL. All five destinations agree across
all three.

## CI

`.github/workflows/verify.yml` rebuilds both surfaces from their registers, asserts the committed
output matches a fresh build, and runs both gates. It previously diffed `docs/`, a directory that has
never existed in this repository, so the freshness assertion could not fail and the root gate never
ran. Regenerating `editorial/` after the fix exposed a real consequence: `editorial/assets/site.css`
had been committed stale, missing the resolved-flag styles present in its own source, so resolved
flags rendered unstyled on the live site.

## Licence and attribution

Product names and trademarks belong to their owners. Specification values are quoted from the
publisher's own pages and cited by source ID. Neither publication is endorsed by or affiliated with
Amazon.com, Inc. beyond participation in the Amazon Associates program.

As an Amazon Associate I earn from qualifying purchases.
