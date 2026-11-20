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
