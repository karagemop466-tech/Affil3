# ShopNow Labs — countertop buying desk

A static affiliate publication for countertop cooking appliances, built for the Amazon
Associates tracking ID `shopnow047c-20`.

**Live site:** https://karagemop466-tech.github.io/Affil3/

---

## What this is

A publication, not a dashboard. The front page leads with a guide and a product shelf; every
audit surface lives one click away in a single footer group. There are 30 pages: six buyer
guides, two category desks, four product pages, three collections, five trust pages, seven
review-room pages and three operations pages.

It is deliberately small and dependency-free. No framework, no build server, no tracking
scripts, and no requests to any third party when a page loads.

## What this is not

- **Not tested.** No product on the site has been purchased or used. Every specification was
  read from the manufacturer's Amazon listing on the date recorded on the page.
- **Not priced.** No price and no star rating appears anywhere. Amazon permits price display
  only through its own served link or its API, and prices change hourly.
- **Not finished.** Ten irregularities are published on
  [`/review/flagged-for-review/`](https://karagemop466-tech.github.io/Affil3/review/flagged-for-review/)
  rather than hidden. The worst one: the supplied short links do not show an Associates tag in
  their redirect, so attribution cannot be confirmed from outside the account.

## Layout

```
data/            the single source of truth; every page is generated from these
  products.json    5 submitted links, intended vs observed fields kept separate
  claims.json      28 claims, each with an official source and a verbatim quote
  suggestions.json 15 suggestions, each with alternative paths and trade-offs
  questions.json   12 open questions, each with a condition that closes it
  flags.json       10 irregularities, each with a source and a fix
  ledger.json      campaign ledger: empty, with a strict schema and provenance rules
content/guides/   six guides as markdown with front matter
tools/
  build.mjs        generator -> HTML, sitemap.xml, feed.xml, robots.txt
  validate.mjs     the publication gate (7 rule groups)
  structure.mjs    markup check (headings, landmarks, tag balance)
  pages/           page modules
assets/          css, js, icon — no external dependencies
```

## Build and check

```bash
node tools/build.mjs        # regenerate every page, the sitemap and the feed
node tools/validate.mjs     # the gate; exit 1 means not publishable
node tools/structure.mjs    # markup check
```

CI runs all three on every push (`.github/workflows/checks.yml`) and fails if the committed
output drifts from the generator.

## The gate

`tools/validate.mjs` blocks publication on:

1. A page missing either the FTC disclosure wording or the Amazon Associates statement.
2. An affiliate link without the `tag=` parameter or without `rel="sponsored"`.
3. An affiliate link block without the literal label **Paid link**.
4. A published product whose `intended_asin` disagrees with its intended URL, or whose link
   never resolved.
5. A currency amount or a star rating anywhere in the generated HTML.
6. A broken internal link.
7. A page missing from the sitemap, or a guide missing from the feed.

It was tested by deliberately breaking each class of rule; see the commit history.

## Measurement

Five defined events — `page_view`, `guide_read`, `product_view`, `outbound_click`,
`capture_submit` — are emitted to a documented interface with no cookies and no persistent
identifier. The endpoint is an empty string, so **every event is dropped in the browser and
nothing is transmitted or stored.** That is the shipped state, not an oversight. See
`assets/js/analytics-config.js` and `/operations/measurement/`.

## Compliance summary

| Rule | Where it is stated | Where it is applied |
| --- | --- | --- |
| "As an Amazon Associate I earn from qualifying purchases." (Operating Agreement §5) | `/disclosure/` | Disclosure strip on every page, every product footer, page footer |
| "I get commissions for purchases made through links in this post." (FTC example wording) | `/disclosure/` | Disclosure strip above the fold on every page |
| Associates tag required in each link (Program Policies) | `/review/sources/#C-02` | Every product link is `?tag=shopnow047c-20` |
| Price display restricted (Program Policies) | `/review/sources/#C-09` | No price anywhere; validator fails on a currency amount |
| No incentives for clicks (Program Policies §6(g)) | `/review/sources/#C-23` | Newsletter carries no offer |
| No Program Content in ML training (IP License) | `/review/sources/#C-24` | Articles written, not generated from listing text |

## Sources

Every compliance claim is quoted with its section number in `data/claims.json` and rendered at
`/review/sources/`. Primary documents:

- Amazon Associates Program Operating Agreement — https://affiliate-program.amazon.com/help/operating/agreement
- Amazon Associates Program Policies — https://affiliate-program.amazon.com/help/operating/policies
- Amazon PA-API 5 deprecation notice — https://affiliate-program.amazon.com/creatorsapi/docs/en-us/paapiv5-deprecation
- FTC, Endorsement Guides: What People Are Asking — https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking
- 16 CFR 255.5 — https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255/section-255.5
- Google Search Central, canonical URLs and sitemaps — https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap

## Repo conventions

`COORDINATION.md` is the shared task board. If more than one session works in this repository,
claim rows there before editing, keep file scopes non-overlapping, and log the sources and the
verification performed when you close a row. See that file for the current state.
