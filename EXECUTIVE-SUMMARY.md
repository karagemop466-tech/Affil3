# Executive summary

**Prepared:** 2026-11-20 · **Tracking ID:** `shopnow047c-20` · **Site:** https://karagemop466-tech.github.io/Affil3/
**Branch:** `arena/01b24e2e-affil3` · **Publisher:** the root publication, built by `tools/build.mjs`

This file supersedes the earlier summary of the same name. What changed is listed under
[Corrections](#corrections) at the bottom, and nothing was removed without a reason.

---

## The one-paragraph version

Five Amazon links were supplied. All five now resolve to real products in one coherent niche: countertop
cooking appliances. That is an observation, not a confirmation — the links carry no tracking tag, the
intended ASIN is still unconfirmed, and not one Special Link has been tested inside Associates Central.
The site is built, gated and live: 32 pages, one indexable publication, a disclosure strip above the fold
everywhere, and every outbound Amazon link marked sponsored with the tracking ID in the URL. Measurement
is wired but inactive, because no analytics endpoint exists to receive it. Four decisions are waiting on
the account owner, and none of them is a design decision.

---

## What the five links are

Re-fetched and read on 2026-11-20 (fresh, unauthenticated, redirects followed). The page title and the
canonical `/dp/` URL were read at each destination.

| Slot | Supplied link | Observed destination | Product (from the listing title) | Intended ASIN |
|---|---|---|---|---|
| P01 | `link.amazon/B04G1MEwY` | [amazon.com/dp/B0CDY277D3](https://www.amazon.com/dp/B0CDY277D3) | CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows | blank |
| P02 | `link.amazon/B02NbDxp3` | [amazon.com/dp/B09B7SB46R](https://www.amazon.com/dp/B09B7SB46R) | Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven | blank |
| P03 | `link.amazon/B00hJ57DV` | [amazon.com/dp/B08DKYBTPH](https://www.amazon.com/dp/B08DKYBTPH) | Chefman Air Fryer 8 Qt, TurboFry 4-in-1 | blank |
| P04 | `link.amazon/B0c8moW59` | [amazon.com/dp/B0DHZTCNR5](https://www.amazon.com/dp/B0DHZTCNR5) | ThermoMaven 1 Sec Professional Digital Meat Thermometer | blank |
| P05 | `link.amazon/B0f3GKalj` | [amazon.com/dp/B0DZFD6R9Z](https://www.amazon.com/dp/B0DZFD6R9Z) | CHEF iQ Sense Smart Wireless Meat Thermometer, 3 probes | blank |

Three air fryers or air fryer ovens, two thermometers. That is the whole catalogue, and the site does not
pretend otherwise.

**Why "intended ASIN" is blank in all five rows.** The submitted token is nine characters; the observed
product ID is ten; the two never match. Only the owner can say which product a short link was meant to
reach, so the field stays empty and the row is flagged (FLG-001, FLG-002). Observed and intended values
live in separate fields and are never copied across.

---

## What is verified, and what it cost to verify

| Claim on the site | Source | How it was checked |
|---|---|---|
| Special Links must use the tagged formats Amazon provides | [Operating Agreement §1](https://affiliate-program.amazon.com/help/operating/agreement) | Full text read 2026-11-20 |
| The Associates statement must appear clearly and prominently | [Operating Agreement §5](https://affiliate-program.amazon.com/help/operating/agreement) | Full text read 2026-11-20 |
| The tag must be a URL parameter on every link on the site | [Program Policies §2(b)](https://affiliate-program.amazon.com/help/operating/policies) | Full text read 2026-11-20 |
| Cloaking or redirecting to obscure the site URL is prohibited | [Program Policies §6(v)](https://affiliate-program.amazon.com/help/operating/policies) | Full text read 2026-11-20 |
| A shortener may not be used so the Amazon destination is unclear | [Program Policies §6(w)](https://affiliate-program.amazon.com/help/operating/policies) | Full text read 2026-11-20 |
| Reviews, ratings and prices only via Amazon-served content or the API | [Program Policies §6(t), §2(b)](https://affiliate-program.amazon.com/help/operating/policies) | Full text read 2026-11-20 |
| `rel="sponsored"` is the mark for paid links | [Google Search Central](https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links) | Page read 2026-11-20 (page dated 2025-12-10) |
| Safe minimum internal temperatures | [USDA FSIS chart](https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/safe-temperature-chart) | Full chart read; values quoted, not paraphrased |
| Probe placement and 2–4 °F tolerance | [USDA FSIS, Food Thermometers](https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/food-thermometers) | Page read 2026-11-20 |

The FTC references (S07, S08) and the Associates help pages (S03, S11, S13) are carried forward from the
earlier register and marked as excerpt-level checks. They are **not** re-verified in this pass, and the
source register says so rather than implying otherwise.

---

## What is published

| Path | Status | What it is |
|---|---|---|
| `/` | indexable | The publication: front page, 5 product pages, comparison, 3 categories, 8 guides, and 13 record pages |
| `/editorial/` | `noindex` + robots-disallowed | An earlier, independently generated publication, kept for its verification provenance |
| `/legacy/` | robots-disallowed | The first session's site, unchanged |

One site is offered to search engines. The other two stay readable to anyone with the link: deleting
another session's work to tidy a sitemap is not a decision this pass should make.

---

## What blocks progress (nothing here is a design problem)

1. **Gate G-02 — link validation.** Generate one Special Link per product in Associates Central, click
   it, and confirm the destination and the tracking report before scaling. Needs the account.
2. **Product intent (Q-01).** Which product was each short link meant to reach? Only the owner knows.
3. **Analytics receiver (S-03).** The five events are defined and `tools/collector.mjs` exists, but no
   endpoint is deployed, so the live site records nothing. Nothing was invented to fill the gap.
4. **Search Console (S-12).** Not connected, so the next topic cannot be chosen from measured queries.

Also open, lower priority: no named author, no product photography, no prices or ratings, no email
capture. Each has a decision and a flag on the site.

---

## Decisions, paths, and where to make them

The [decision board](https://karagemop466-tech.github.io/Affil3/suggestions/) lists 19 decisions with a
status, an owner, impact, effort, options and a recommendation. Three paths summarise the choice:

- **Path A — Ship and measure (recommended).** Keep the tagged links live, close G-02 this week, add
  Search Console. Buys a live site and first search data; risks untested links staying live until G-02.
- **Path B — Measure first.** Deploy the collector, record the five events for two weeks, then choose.
  Buys click data before more writing; needs a receiver and a privacy notice.
- **Path C — Associates-ready.** Hide buy buttons until G-02 passes, reach ten guides, then submit.
  Lowest compliance risk, slowest path to any revenue.

Answer with a decision ID and an option letter (`S-01 B`) or a path name (`Path A`). Unanswered decisions
stay exactly as they are.

---

## Repository map

| Path | What it is |
|---|---|
| `data/products.json` | Product-intent register (root publication) |
| `data/sources.json` | Every source, how it was checked, and how strong the check was |
| `data/guides.json` | Eight guides: body, short version, limits, buyer questions, sources |
| `data/suggestions.json` | Decision board: 19 decisions, 3 paths |
| `data/questions.json` | Known facts, open questions, discovery steps |
| `data/flags.json` | 27 flags, 6 resolved |
| `tools/build.mjs` → site root | Root publication build, no dependencies |
| `tools/verify.mjs` | Publishing gate: 4,414 checks |
| `tools/build.py` → `editorial/` | Archive publication build (Python, no dependencies) |
| `tools/check_site.py` | Archive gate |
| `.github/workflows/verify.yml` | Rebuilds both publications on every push and fails on drift |

```bash
node tools/build.mjs && node tools/verify.mjs     # 32 pages, 4414 checks, 0 failed
python3 tools/build.py && python3 tools/check_site.py   # 21 pages, PASS
```

---

## Corrections

| Earlier statement | Corrected to | Why |
|---|---|---|
| "The fifth link resolves to nothing" (P04) | P04 resolves to `B0DHZTCNR5`, a ThermoMaven thermometer | Two fetches on 2026-11-20 landed on the same product; the earlier checkpoint page was intermittent (FLG-022) |
| "Four of five resolve" | All five resolve | Same correction |
| "None of the five carries your tracking ID" | The **supplied** short links carry no tag; the **site's** outbound links are constructed `?tag=shopnow047c-20` | The two are different links; the second is what the site publishes |
| USDA temperatures cited as an excerpt | Values quoted from the chart page itself, with the chart's date | Page read in full on 2026-11-20 |
| Participation Requirements §2 read from an excerpt | Read in full | Page read in full on 2026-11-20 |

No price, rating, availability, conversion or revenue figure appears anywhere in this repository or on
the site. There is no forecast, and there will not be one until there are authorized first-party reports.
