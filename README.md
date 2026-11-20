# Counter &amp; Crumb

A reader-facing affiliate publication for two countertop cooking categories — air
fryers and kitchen thermometers — with the machinery that produced it published
alongside it.

The site is a static build. No framework, no third-party dependency, no tracking
script from anyone else. Python 3.9+ and a browser is the whole toolchain.

---

## What is here

```
index.html            the publication front page
guides/               question-shaped buying guides
products/             the product register and one page per product
compare/              side-by-side comparisons
categories/           category hubs
desk/                 open questions, suggestions, flagged-for-review
methods/              source register and the verification method
compliance/           rule by rule, with the source for each
measurement/          the five events and what is never collected
ledger/               the campaign ledger (empty, with its columns defined)
executive-summary/    one page: what was built, verified, and left open
tools/                the build and the release gate
data/                 the source of truth for every page
```

`data/` is the source of truth. Every page, the sitemap and the feed are
generated from it, so a change to the register propagates everywhere in one run.

## Build it

```bash
python3 tools/build_site.py     # regenerate the site
python3 tools/check_site.py     # the release gate
```

The gate fails the build on a missing disclosure, an unmarked or untagged Amazon
link, a broken internal link, a missing canonical, a page missing from the
sitemap or the feed, a published price or rating, or an intent record that has
been merged with an observation.

## Run it locally

```bash
python3 tools/analytics_sink.py --port 8787
```

One process serves the site and collects events. Point a browser at
`http://localhost:8787/`.

## The three things that matter

**Intent and observation are never merged.** The register keeps the ASIN the
owner meant to promote in one field and the destination each submitted link
actually reaches in another. Three of the five submitted tokens are 9 characters
and so cannot be ASINs at all; the other two are 10 characters but neither was
confirmed as an issued ASIN. The intended fields stay blank until the owner
confirms them.

**Prices and ratings are not published.** Amazon's Program Policies allow a
price on your site only when Amazon serves the link that displays it or the
price comes from Creators API or PA API (2(b)), and bar the display of customer
reviews and star ratings without the same (5(t)). So the site shows neither and
links to the listing instead. The code path for a live lookup exists and stays
empty until the API is configured.

**Every outbound link is marked.** All of them are direct Special Links carrying
the Associates tag, with `rel="sponsored nofollow"`, a visible Sponsored marker
and an aria-label. The submitted `link.amazon` short links are recorded in the
register but are never published as outbound links.

## Tools

| Command | What it does |
| --- | --- |
| `python3 tools/build_site.py` | Regenerate every page, the sitemap, the feed and robots.txt |
| `python3 tools/check_site.py` | The release gate. `--strict` also fails on warnings |
| `python3 tools/affiliate.py --audit` | Check every published Amazon link |
| `python3 tools/affiliate.py --product <id>` | Print the Special Link for a product |
| `python3 tools/affiliate.py --link <url>` | Resolve a submitted link and report the observation |
| `python3 tools/research.py --items <ASINs>` | Creators API research. Needs credentials in the environment |
| `python3 tools/analytics_sink.py` | Self-hosted collector and static server |
| `python3 tools/analytics_sink.py --summary` | Summarise the event log |

Creators API credentials are read from the environment, never from the
repository: `AFFIL3_LWA_CLIENT_ID`, `AFFIL3_LWA_CLIENT_SECRET`,
`AFFIL3_PARTNER_TAG`, `AFFIL3_MARKETPLACE`, `AFFIL3_ANALYTICS_SALT`.

PA-API 5 is deprecated and now returns an HTTP 403 `AccessDeniedException`. The
research tooling targets the Creators API from the start.

## Where to look first

- **[The product register](https://karagemop466-tech.github.io/Affil3/products/)** — every product, the link submitted for it, and what could not be confirmed.
- **[Flagged for review](https://karagemop466-tech.github.io/Affil3/desk/flags/)** — everything this desk could not settle, with the source that was checked.
- **[Open questions](https://karagemop466-tech.github.io/Affil3/desk/)** — what has to be answered before the next decision.
- **[Source register](https://karagemop466-tech.github.io/Affil3/methods/sources/)** — every official page relied on, with quotes.
- **[Executive summary](https://karagemop466-tech.github.io/Affil3/executive-summary/)** — one page.

## Coordination

[`COORDINATION.md`](COORDINATION.md) is the shared task board for parallel agent
sessions working on this repository. Claim a task there before you start it.
Three sessions have worked on this repository. Their boards are all in that file,
kept verbatim, and their published sites are preserved under `legacy/`.

## Earlier versions of this site

`legacy/` holds the sites published by the two earlier sessions, moved there
unchanged with `git mv` when each new integration took over the root paths:

| Path | Published by |
| --- | --- |
| `legacy/arena-83a43a96/` | session `arena-83a43a96-affil3` (pull request #1) |
| `legacy/arena-6249757a/` | session `arena/6249757a-affil3` (pull requests #4 and #6) |

Nothing was deleted. `legacy/` is excluded from crawling by `robots.txt`, and the
URLs those versions published now serve a redirect page pointing at the current
home for that content. Their build scripts, data files and boards are all intact
inside the archive.

## Verification

`python3 tools/check_site.py` is the gate, and it is deliberately strict:

| Rule | What it enforces |
| --- | --- |
| G1 | The Amazon Associates disclosure sentence is present, and above the main content, on every page |
| G2 | Every Amazon shopping link is a direct, tagged Special Link with `rel="sponsored nofollow"` and a `data-product` attribute |
| G3 | No `link.amazon` short link is published as an outbound link |
| G4 | Every internal link resolves to a file that exists |
| G5 | Every external link points at an allowlisted host |
| G6 | Every page has a title, a meta description and a canonical link |
| G7 | Every page is in the sitemap and every guide is in the feed |
| G8 | No price, star rating or review count appears in the page text |
| G9 | The intended ASIN and the observed redirect target are never the same recorded value |
| G10 | The campaign ledger ships with no invented rows |
| G11 | Every product page carries its official listing URL and its observation date |
