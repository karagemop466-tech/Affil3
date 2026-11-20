# Executive summary — Affil3

**Prepared:** 2026-11-20 · **Tracking ID supplied:** `shopnow047c-20` · **Canonical publication:** https://karagemop466-tech.github.io/Affil3/

## Bottom line

The repository contains a static, question-led kitchen-products publication with a sourced product register, category pages, five buyer guides, RSS, a sitemap, compliance and decision dashboards. It is **not yet an AI-powered research or publishing platform**: no AI provider, Amazon product-data API, trend/keyword source, Search Console property, analytics collector endpoint, or Associates report is connected. No popularity, conversion, commission, revenue, or trend claims are made.

Product identity observations are kept separate from product intent. The supplied short-link tokens and the observed Amazon destinations are not treated as proof of the products the owner intended. Intended ASIN, official listing URL, confirmation date, and confirmation source remain blank for all five rows. Product purchase CTAs are withheld until every product has a Special Link test, confirmed destination, tracking-report reference, date, and source recorded in Associates Central (G-02). The supplied short links are **not described as invalid**; their precise compliance status remains unresolved (FLG-003).

## Product register — observed redirect destinations only

Observations below reflect the register dated 2026-11-20. They describe what the submitted link was observed to resolve to, not the owner's intended item. Follow the official Amazon listing for manual review; status is not a product recommendation or test result.

| ID | Submitted link | Observed Amazon destination | Observed listing title | Intended identity |
|---|---|---|---|---|
| P01 | [link.amazon/B04G1MEwY](https://link.amazon/B04G1MEwY) | [Amazon listing B0CDY277D3](https://www.amazon.com/dp/B0CDY277D3) | CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows | **Unverified — blank** |
| P02 | [link.amazon/B02NbDxp3](https://link.amazon/B02NbDxp3) | [Amazon listing B09B7SB46R](https://www.amazon.com/dp/B09B7SB46R) | Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven | **Unverified — blank** |
| P03 | [link.amazon/B00hJ57DV](https://link.amazon/B00hJ57DV) | [Amazon listing B08DKYBTPH](https://www.amazon.com/dp/B08DKYBTPH) | Chefman Air Fryer 8 Qt | **Unverified — blank** |
| P04 | [link.amazon/B0c8moW59](https://link.amazon/B0c8moW59) | [Amazon listing B0DHZTCNR5](https://www.amazon.com/dp/B0DHZTCNR5) | ThermoMaven 1 Sec Professional Digital Meat Thermometer | **Unverified — blank** |
| P05 | [link.amazon/B0f3GKalj](https://link.amazon/B0f3GKalj) | [Amazon listing B0DZFD6R9Z](https://www.amazon.com/dp/B0DZFD6R9Z) | CHEF iQ Sense | **Unverified — blank** |

Each observed page, source, correction history, and open flag is in the [Shop table](https://karagemop466-tech.github.io/Affil3/shop/) and [source register](https://karagemop466-tech.github.io/Affil3/sources/). No product price, availability, rating, review count, commission, or sales figure is published.

## What is implemented

- Product-led landing page, categories, the full five-row shop table, source register, and five question-shaped guides. Guide topics are editorial hypotheses, not claims about search demand.
- RSS feed and root sitemap. The root publication is the sole search-index target; the retained `/editorial/` review archive is marked `noindex` and omitted from both sitemap discovery paths.
- Associates disclosure strip beneath the masthead on every page, with the required statement repeated in the footer.
- A privacy-conscious browser event counter and self-hostable Node collector. **Live collection is inactive** until an endpoint is deployed and configured; no live click or conversion results exist.
- An empty campaign ledger with provenance fields; no score, forecast, or revenue estimate.
- Suggestions, open questions, and a Flagged for Review page so recommendations and unresolved facts are visible instead of silently filled in.

## Key release gates and unknowns

| Question or gate | Current state | How to resolve |
|---|---|---|
| Intended product and intended ASIN for each short link | Unconfirmed; fields blank | Confirm each item in Associates Central or with the intended official listing URL (Q-01). |
| Is `shopnow047c-20` active and is the site declared in the account? | Unknown to this repository | Check the Associates Central account and declared-site list (Q-03, FLG-006, FLG-011). |
| Are the product links valid Special Links with correct destinations and report rows? | G-02 pending; purchase buttons withheld | Generate one link per product in Associates Central, click and verify destination and report, then record the proof in the product validation record (Q-04, FLG-005). |
| Are analytics and search-query measurements active? | No. Search Console is unconnected and analytics endpoint is unset | Verify the site in Search Console; select, deploy, and test a collector endpoint (Q-06, Q-12; FLG-009, FLG-013). |
| What AI/data workflow is authorized? | Not configured | Choose an AI provider, product/query sources, budget/data terms, and human reviewer. Start with source-cited drafts only (Q-14, S-13). |
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

For the decision queue and evidence gaps, see the live [Suggestions](https://karagemop466-tech.github.io/Affil3/suggestions/), [Questions](https://karagemop466-tech.github.io/Affil3/questions/), and [Flagged for Review](https://karagemop466-tech.github.io/Affil3/flagged/) pages.
