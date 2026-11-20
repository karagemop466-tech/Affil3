# Executive summary — Affil3

**Prepared:** 2026-11-20 · **Tracking ID supplied:** `shopnow047c-20` · **Canonical publication:** https://karagemop466-tech.github.io/Affil3/

## Bottom line

The repository contains a static, question-led kitchen-products publication with a sourced product register, category pages, five buyer guides, RSS, a sitemap, compliance and decision dashboards. It is **not yet an AI-powered research or publishing platform**: no AI provider, Amazon product-data API, trend/keyword source, Search Console property, analytics collector endpoint, or Associates report is connected. No popularity, conversion, commission, revenue, or trend claims are made.

Product identity observations are kept separate from product intent. The supplied short-link tokens and the observed Amazon destinations are not treated as proof of the products the owner intended. Intended ASIN, official listing URL, confirmation date, and confirmation source remain blank for all five rows. Product purchase CTAs are withheld until every product has a Special Link test, confirmed destination, tracking-report reference, date, and source recorded in Associates Central (G-02). The supplied short links are **not described as invalid**; their precise compliance status remains unresolved (FLG-003).

## Product register — observed redirect destinations only

Observations below reflect the register dated 2026-11-20. They describe what the submitted link was observed to resolve to, not the owner's intended item. Follow the official Amazon listing for manual review; status is not a product recommendation or test result.

| ID | Submitted link | Observed Amazon destination | Observed listing title | Intended identity |
|---|---|---|---|---|
| 1 | `link.amazon/B04G1MEwY` | `amazon.com/dp/B0CDY277D3` | CHEFMAN TurboFry Touch 6 Qt. Dual-Window Air Fryer (RJ38-SQPF-3TDB-2W) | resolved |
| 2 | `link.amazon/B02NbDxp3` | `amazon.com/dp/B09B7SB46R` | Emeril Lagasse French Door AirFryer 360 Toaster Oven Combo, 26 QT (4-00675-02A-VN) | resolved |
| 3 | `link.amazon/B00hJ57DV` | `amazon.com/dp/B08DKYBTPH` | CHEFMAN TurboFry Touch Stainless-Steel Air Fryer, 8 Qt (RJ38-SQSS-8T) | resolved |
| 4 | `link.amazon/B0c8moW59` | `amazon.com/dp/B0DHZTCNR5` | ThermoMaven F1 Ace instant-read thermometer | resolved (a first automated fetch hit an Amazon checkpoint; retries and retests agree) |
| 5 | `link.amazon/B0f3GKalj` | `amazon.com/dp/B0DZFD6R9Z` | CHEF iQ Sense Smart Wireless Meat Thermometer, 3 Probes (Gen3) | resolved |

Three of the five are air fryers or air fryer ovens and two are meat thermometers for checking food
cooked in them. The niche chose itself: **countertop cooking appliances for kitchens with limited
counter space**, plus the two thermometers you use with them. All five now carry a manufacturer
specification page, and on two of them the maker and the Amazon listing disagree about the same
model number.

## What is implemented

- Product-led landing page, categories, the full five-row shop table, source register, and five question-shaped guides. Guide topics are editorial hypotheses, not claims about search demand.
- RSS feed and root sitemap. The root publication is the sole search-index target; the retained `/editorial/` review archive is marked `noindex` and omitted from both sitemap discovery paths.
- Associates disclosure strip beneath the masthead on every page, with the required statement repeated in the footer.
- A privacy-conscious browser event counter and self-hostable Node collector. **Live collection is inactive** until an endpoint is deployed and configured; no live click or conversion results exist.
- An empty campaign ledger with provenance fields; no score, forecast, or revenue estimate.
- Suggestions, open questions, and a Flagged for Review page so recommendations and unresolved facts are visible instead of silently filled in.

## Key release gates and unknowns

Note precisely what is and is not being claimed: the short links are **untagged, and their compliance
status is unresolved** — which is a different claim from 'broken', and none of them is broken. No
official document reviewed says `link.amazon` short URLs are invalid. Their exact compliance status is
not addressed in the documents read.

| Question or gate | Current state | How to resolve |
|---|---|---|
| Intended product and intended ASIN for each short link | Unconfirmed; fields blank | Confirm each item in Associates Central or with the intended official listing URL (Q-01). |
| Is `shopnow047c-20` active and is the site declared in the account? | Unknown to this repository | Check the Associates Central account and declared-site list (Q-03, FLG-006, FLG-011). |
| Are the product links valid Special Links with correct destinations and report rows? | G-02 pending; purchase buttons withheld | Generate one link per product in Associates Central, click and verify destination and report, then record the proof in the product validation record (Q-04, FLG-005). |
| Are analytics and search-query measurements active? | No. Search Console is unconnected and analytics endpoint is unset | Verify the site in Search Console; select, deploy, and test a collector endpoint (Q-06, Q-12; FLG-009, FLG-013). |
| What AI/data workflow is authorized? | Not configured | Choose an AI provider, product/query sources, budget/data terms, and human reviewer. Start with source-cited drafts only (Q-18, S-15). |
| Who is the named editor/author? | Team byline; no person or credentials supplied | Supply a real author/reviewer and accurate bio, or keep the team byline (Q-08, FLG-014). |

## Verification and publication

Build checks run from the checked-in sources:

```sh
node tools/build.mjs && node tools/verify.mjs
python3 tools/build.py && python3 tools/check_site.py
```

The root check validates product fields, citations, disclosure presence, sponsored link attributes, the G-02 CTA gate, analytics event consistency, internal links, sitemap/feed coverage, and that the archival `/editorial/` pages are noindex. The editorial check validates that the archive pages are noindex and omitted from its sitemap. These automated checks do not replace Associates Central, Search Console, mobile disclosure review, or a live-host link check.

## Official sources and review paths

- [Amazon Associates Operating Agreement](https://affiliate-program.amazon.com/help/operating/agreement)
- [Amazon Associates Program Policies](https://affiliate-program.amazon.com/help/operating/policies)
- [FTC disclosures guidance](https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers)
- [Google Search Central: robots meta tag and noindex](https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag)
- [Google Search Central: qualify outbound links](https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links)

This is why **no buy button renders today**. Rendering one would mean shipping a link that cannot pay
you. The product pages say so in plain language where the button would be.

## Verification standard applied

- Specs come from the **manufacturer's own product page** wherever one exists. Amazon listings were
  used for identity.
- **Official pages contradict each other in four places**, and each one is published rather than
  resolved by picking the friendlier number:
  - Emeril oven preset count, 25 in the spec tile and 24 in the body copy (`FLG-001`), plus an accessory
    list that no longer includes the grill plate (`FLG-006`);
  - Chefman 8 Qt `RJ38-SQSS-8T`, where the maker says 1700 W and 15.4 × 12.6 × 13.5 in and the listing
    says 1000 W and 12.75 × 13.5 × 10 in for the same model number (`FLG-026`), and a title promising
    450 °F against a 400 °F bullet (`FLG-027`);
  - CHEF iQ battery life, 70+ hours on the product page, 60 on the FAQ and 50 on the listing (`FLG-023`);
  - ThermoMaven, where the maker says "waterproof design" and LCD and the listing claims IP67, LED and
    NSF (`FLG-008`).
- **A manufacturer page an earlier pass reported as missing was found** (thermomaven.com). One of the
  five products had been published with no specifications and no buy link because a search missed it.
  It now carries the maker's specifications and its buy link, and the residual maker-versus-listing
  gaps are flagged instead (`FLG-025`, resolved).
- **Every source citation on `/editorial/` pointed at an anchor that did not exist.** `/flagged/`,
  `/questions/`, `/dashboard/` and `/disclosure/` all linked to `#Sxx` on their own pages, where no
  such id was emitted, so a reader clicking a source landed at the top of the page. Anchors now resolve
  to the source register, and both gates check cross-page fragments, so this cannot recur silently.
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

For the decision queue and evidence gaps, see the live [Suggestions](https://karagemop466-tech.github.io/Affil3/suggestions/), [Questions](https://karagemop466-tech.github.io/Affil3/questions/), and [Flagged for Review](https://karagemop466-tech.github.io/Affil3/flagged/) pages.
