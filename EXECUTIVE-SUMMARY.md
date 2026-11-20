# Executive summary

**Prepared:** 2026-11-20 · **Tracking ID:** `shopnow047c-20` · **Site:** https://karagemop466-tech.github.io/Affil3/
**Branch merged from:** `arena/4578ad4b-affil3`

---

## The one-paragraph version

Five Amazon links were supplied. Four resolve to real products in one coherent niche — countertop
cooking appliances. The fifth resolves to nothing and is published as nothing. None of the five carries
your tracking ID, which is the single thing standing between this site and earning a cent. The site is
built, verified, and live; the measurement it collects is honest and currently zero, because there is
nothing honest to report yet.

---

## What the five links actually are

| Slot | Supplied link | Resolves to | Product | Identity |
|---|---|---|---|---|
| 1 | `link.amazon/B04G1MEwY` | `amazon.com/dp/B0CDY277D3` | CHEFMAN TurboFry Touch 6 Qt. Dual-Window Air Fryer (RJ38-SQPF-3TDB-2W) | resolved |
| 2 | `link.amazon/B02NbDxp3` | `amazon.com/dp/B09B7SB46R` | Emeril Lagasse French Door AirFryer 360 Toaster Oven Combo, 26 QT (4-00675-02A-VN) | resolved |
| 3 | `link.amazon/B00hJ57DV` | `amazon.com/dp/B08DKYBTPH` | CHEFMAN TurboFry Touch Stainless-Steel Air Fryer, 8 Qt (RJ38-SQSS-8T) | resolved |
| 4 | `link.amazon/B0c8moW59` | Amazon "Continue shopping" interstitial; catalog search returns no results | — | **unresolved** |
| 5 | `link.amazon/B0f3GKalj` | `amazon.com/dp/B0DZFD6R9Z` | CHEF iQ Sense Smart Wireless Meat Thermometer, 3 Probes (Gen3) | resolved |

Four of five are air fryers or air fryer ovens. The niche chose itself: **countertop cooking appliances
for kitchens with limited counter space.** The thermometer is the natural adjacency, not a detour.

## The finding that matters most

Every supplied link resolves to an `amazon.com/dp/<ASIN>` URL with **no `tag=` parameter**. Amazon's
Program Policies require the Associates ID to appear as a URL parameter on every link placed on a site,
and the Operating Agreement requires links to use the tagged formats Amazon provides. As supplied,
these links would not attribute a sale.

The correct response is not to rewrite the links by hand. It is to re-issue them from Associates
Central, click one, and confirm the click shows up in the report before touching the other four —
one link tested, then scale. That is `SG-08` on the suggestions page, and it is the only thing on this
site that is blocked rather than done.

Note precisely what is and is not being claimed: the short links are **untagged and unresolved**. No
official document reviewed says `link.amazon` short URLs are invalid. Their exact compliance status is
not addressed in the documents read.

## What was built

| Surface | What it does |
|---|---|
| Front page | Leads with three shape-based picks. No verification talk above the fold. |
| Category pages | Air fryers, oven-style, thermometers. Comparison table plus cards. |
| Product pages | Source-cited spec table, gains/costs, fit statement, product-intent record. |
| Four guides | Question-shaped, answered from the register. RSS + sitemap included. |
| Source register | 19 sources, tiered, each with what it supports and when it was read. |
| Flagged for review | 7 irregularities, published with source links. Does not block publication. |
| Open questions | 24 questions, each with an owner and the step that closes it. |
| Suggestions queue | 14 proposals with problem, cost, and the decision needed. 3 shipped, 1 blocked. |
| Dashboard | Entry status, campaign ledger schema (empty), 12 compliance rules, 5 events. |
| Disclosure & method | Rule-by-rule record with the quoted policy basis for each. |

Every dashboard surface is reachable from **one** footer group. There is one navigation group.

## What is enforced by the build, not by good intentions

`tools/check_site.py` fails the build if:

- any internal link breaks,
- a currency amount appears anywhere in the HTML,
- a star rating or review count appears,
- a product call-to-action lacks `tag=shopnow047c-20`,
- an Amazon citation is not marked `rel="nofollow"`,
- the Associates statement is missing from any page,
- a cited source ID does not exist,
- the sitemap does not cover every page.

This is why **no buy button renders today**. Rendering one would mean shipping a link that cannot pay
you. The product pages say so in plain language where the button would be.

## Verification standard applied

- Specs come from the **manufacturer's own product page** wherever one exists. Amazon listings were
  used for identity.
- **Two official pages contradicted each other twice**: preset count on the Emeril oven (`FLG-001`) and
  wattage on the Chefman 8 Qt (`FLG-002`). Both fields are blank on the site and both conflicts are
  published.
- **Secondhand review sites were read while orienting and are never cited.** No value on the site
  traces to one.
- A value with no official source is **blank and marked unverified**. Nothing is inferred.
- No price, no star rating, no review count appears anywhere — that is a policy requirement, and it is
  also why the site cannot be tempted into stale numbers.

## What is still missing, and who closes it

| Missing | Blocks | Owner | Closes in |
|---|---|---|---|
| A tagged link, tested once | All revenue | Account holder | minutes |
| Whether `shopnow047c-20` is live on the account | Confidence in every URL | Account holder | minutes |
| What link 4 points to | Slot 4 existing at all | Account holder | minutes |
| API access yes/no | Any price ever appearing | Account holder | minutes |
| Search Console verification | Choosing the next topic from data | Site owner | an hour |
| An analytics endpoint and an owner for it | Any measurement at all | Site owner | an hour |
| Author name and credentials | Reader trust, ranking | Site owner | a day |
| Confirmation of two disputed specs | Two blank table rows | Editor | an email |

Nine of these are access problems, not research problems. That is the useful thing to know: the site is
not waiting on more work, it is waiting on credentials.

## The honest position on revenue

The site earns **nothing today** and will earn nothing until a tagged link exists. Once it does, the
first month of data will be small, and the right response is to read it rather than to scale content
against it. No conversion rate, revenue forecast, or traffic estimate appears anywhere in this
repository, because none exists and inventing one would be the exact failure mode this project was
built to avoid.

## Read next

- `COORDINATION.md` — task board, claims, verification log
- `docs/flagged/` — the seven irregularities
- `docs/questions/` — 24 questions with owners
- `docs/suggestions/` — 14 proposals awaiting a decision
- `docs/disclosure/` — the rule-by-rule compliance record
