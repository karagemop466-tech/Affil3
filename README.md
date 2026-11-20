# Affil3 — ShopNow 047

An Amazon-Associates publishing site for kitchen gear, built so that **every claim on a page can be
traced to a dated row in a register, and every rule that can be checked by a machine is checked on
every build.**

Live site: **https://karagemop466-tech.github.io/Affil3/** (served from `docs/` on `main`)

> **Read this first.** The five product links supplied to this project were
> `https://link.amazon/<9-character token>`. Amazon ASINs are 10 characters, so those strings are
> redirect handles, not identifiers. Four of them resolved on 2026-11-20 to real listings
> (`B0CDY277D3`, `B09B7SB46R`, `B08DKYBTPH`, `B0DZFD6R9Z`); one did not resolve at all. The register
> stores the *intended* identifier and the *observed* one in separate fields and never merges them.
> No price, rating, review count or availability appears anywhere on this site, because the sources
> that would make those figures current are not available to it. Nothing is guessed. See
> [`docs/EXECUTIVE-SUMMARY.md`](docs/EXECUTIVE-SUMMARY.md).

## Quickstart

```bash
node scripts/build.mjs     # register + content  ->  docs/
node scripts/checks.mjs    # the compliance gate; exit 1 = do not merge
node scripts/serve.mjs     # preview at http://localhost:8080/Affil3/
node scripts/collect.mjs   # local event collector on :8788 (see /dashboard/)
npm run verify             # build + gate
```

No dependencies. No install step. Node 20+.

## Layout

| Path | Role |
|---|---|
| `register/` | **Source of truth.** Products, sources, flags, suggestions, questions, ledger, links, measurement, compliance, site config |
| `register/schema/` | Ingest contract for automated product research — refuses a 9-char ASIN and any unlicensed source system |
| `content/` | Authored editorial: home, about, methodology, disclosure, privacy, `guides/*.md` |
| `scripts/` | `build.mjs`, `checks.mjs`, `links.mjs`, `new-guide.mjs`, `collect.mjs`, `serve.mjs` |
| `docs/` | Generated site. Committed so Pages serves exactly what was reviewed. **Do not hand-edit** — change the register and rebuild |
| `docs/EXECUTIVE-SUMMARY.md`, `docs/DECISION-BRIEF.md` | The two reading-first documents |
| `COORDINATION.md` | Shared task board for parallel sessions: claims, scope, log |
| `.github/workflows/ci.yml` | CI: parse registers → rebuild → run gate → prove `docs/` is not stale → audit output |

## The rules the build enforces

`scripts/checks.mjs` fails the build on any of:

- **C-01** the required Associates sentence missing above the fold or in the footer of any page
- **C-02** an Amazon link without `tag=` matching the site tracking ID, or without `rel="sponsored nofollow"`, or a purchase link routed through anything but `amazon.com`
- **C-03** any currency figure or star rating reaching the published site
- **C-04** testing language, superlatives, implied endorsement, or an unsourced demand claim, on any page a buyer reads
- **C-05** any Amazon CDN asset loaded as a resource (Program Content licensing path)
- **C-06** trackers, cookies, persistent storage identity, foreign scripts, missing canonical or description
- **C-07** a field published as fact with no source row, or a volatile product field populated while its policy source is unresolved
- **C-08** a compliance control claiming "passing" with no gate defined behind it
- **C-09** a broken internal link
- **C-10** any page missing from the sitemap, or any sitemap/feed entry pointing nowhere
- **C-11** an orphan page nothing links to

## Publishing a guide

```bash
node scripts/new-guide.mjs "What should you compare before buying a dual-basket fryer" --cluster air-fryers
$EDITOR content/guides/what-should-you-compare-before-buying-a-dual-basket-fryer.md
node scripts/build.mjs && node scripts/checks.mjs
```

The guides index, home rack, sitemap, RSS feed, search index and JSON-LD all pick it up. A new
guide cannot skip the byline, the no-testing note, or the sources section — the template pre-fills
them, and the gate rejects the page if the wording fails.

## What is deliberately *not* here

- **No prices.** Amazon's terms permit price and availability only from an Amazon-served link or the
  catalog API, with a short refresh ceiling. There are no API credentials here, so there are no
  numbers. The alternative — a figure copied once and left to rot — is the failure this project was
  built to avoid.
- **No testing claims.** No product was handled. Guides are written as *what to check*, and each one
  says so inside the article.
- **No revenue or traffic forecast.** Section 4 of the Operating Agreement disclaims any
  representation about expected traffic or income; the campaign ledger ships with zero rows and a
  provenance rule, and read-time ratios are hidden until their denominators clear a stated floor.
- **No email capture.** See SG-30: the provider, the consent text, and the traffic to justify it do
  not exist yet. The RSS feed is the subscription channel that requires none of that.
- **No invented author.** The byline is a desk, and the about page explains why that is more honest
  than a biography.

## Status

11 source rows (3 verbatim, 4 excerpt, 4 unresolved), 5 product-intent records, 22 suggestions
(12 implemented, 8 awaiting a choice), 22 open questions (6 blocking), 10 flagged items, 12
compliance controls, 5 defined events, 29 published pages. Every unresolved item is published on
[/flagged-for-review/](https://karagemop466-tech.github.io/Affil3/flagged-for-review/) with the one
action that closes it.
