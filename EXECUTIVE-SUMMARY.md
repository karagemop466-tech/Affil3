# Executive summary — ShopNow Kitchen

**Reviewed:** 2026-11-20 · **Tracking ID configured:** `shopnow047c-20` · **Site:** [ShopNow Kitchen](https://karagemop466-tech.github.io/Affil3/)

## Executive view

The repository contains a publication-style kitchen buying-guide site, a product/source register, a decision board, question register, flagged-items page, RSS feed and sitemap. The content is deliberately limited to facts recorded with sources. It does not claim product popularity, search volume, conversion performance or revenue. Product intent is not yet confirmed for any of the five supplied short links: intended ASIN and confirmation fields remain blank. The latest recorded observed ASINs are observations, not owner confirmation or validation of Associates tracking.

The site should be treated as an editorial prototype—not as a proven revenue system. The measurement endpoint is unset; therefore the browser instrumentation cannot report to a live collector. The campaign ledger is empty by design. No authorized first-party orders or revenue figures have been entered.

## What is in the repository

- **Shop front page and product/category pages:** product-led presentation, with disclosure immediately below the masthead and repeated in the footer.
- **Five submitted links:** preserved separately from observed targets in `data/products.json`. All intended ASIN/confirmation fields are blank; observed targets must not be substituted for intent.
- **Four question-led guide drafts:** buyer-oriented hypotheses about basket vs. oven formats, capacity, cleanup/counter space, and multi-function appliances. They are not assertions of search demand.
- **Decision board:** `/suggestions/` presents options and trade-offs before implementation.
- **Questions and discovery paths:** `/questions/` lists information gaps and ways to resolve them.
- **Flagged for Review:** `/flagged/` keeps unresolved identity, link, policy and operational issues visible.
- **Measurement and campaign ledger:** event definitions and a ledger schema exist, but no live analytics endpoint or reported campaign data is configured.
- **Build gate:** `npm run check` completed successfully on this checkout (32 generated pages; 3,484 verification checks; editorial check passed 21 pages). This is a local build result, not proof of a successful current GitHub Pages deployment.

## Important limitations and irregularities

1. **Product identity is not confirmed.** The register records observed destinations separately from intended ASINs. Confirm each product from the owner's Associates workflow before treating the link or product match as approved.
2. **Special Link tracking is untested.** The configured tracking ID is present in generated product links, but the account's enrollment status and the click/reporting outcome have not been validated in Associates Central. Do not describe conversions as tracked until a test is visible in an authorized report.
3. **No live analytics / no campaign data.** GitHub Pages is static and cannot itself host the collector. `analyticsEndpoint` is unset; the campaign ledger has no measured values. There are no conversion scores, revenue forecasts or optimization conclusions.
4. **Some evidence and site history conflict.** The repository retains multiple historical editions, generated surfaces and differing snapshots. The root is the intended reader-facing edition; legacy material should not be confused with the current product. Review the current `/flagged/` page and source register before relying on historical summary prose.
5. **The site is not an autonomous product-research agent.** It does not currently establish high-converting products, scrape Amazon, use the Creators API, or automatically publish optimized content. Those capabilities require authorized data access, policy review and human editorial approval.

## Recommended decision order

1. **Confirm the five product intents** from the Amazon listing and the account holder's records; record intended ASIN, official listing URL, date and source independently from observed redirects.
2. **Test one Special Link per product** inside Associates Central and check that the destination and report attribution match before wider rollout. Amazon source: [Operating Agreement](https://affiliate-program.amazon.com/help/operating/agreement) and [Program Policies](https://affiliate-program.amazon.com/help/operating/policies).
3. **Choose the publication's reader and cadence** on `/suggestions/`; prioritize useful, firsthand buyer questions over trend claims that have not been measured.
4. **Only then enable measurement:** select and secure a host for the collector, review the privacy notice, configure the endpoint, and verify the five event types using test traffic.
5. **Verify Search Console** and submit the sitemap; use actual query and landing-page data to choose later topics, without treating early or sparse data as proof of demand.
6. **Keep the compliance gate:** disclosures and `rel="sponsored"` on product-intent links; review current Amazon rules and FTC endorsement disclosure guidance before changing monetization or automation.

## Questions that prevent a sound business decision

| Question | Information currently missing | How to discover it |
|---|---|---|
| Which exact product does each supplied short link represent? | Owner-confirmed intended ASIN and listing | Open the listing in a signed-in browser; preserve the destination, date and official page as an intent-confirmation record. |
| Do the links earn attribution for this account? | Associates Central test result and report evidence | Generate a Special Link in the enrolled account, click a controlled test link and confirm its reporting outcome. |
| Who is the reader? | A defined buyer, cooking situation, budget and kitchen constraint | Choose a primary reader profile based on actual household/customer evidence, not assumed demographics. |
| Which product comparisons are defensible? | Directly verified model-specific specs and firsthand testing | Use manufacturer documentation and, where a field is absent or conflicting, leave it blank until confirmed. |
| Which topics attract qualified readers? | Search queries, impressions, visits and buyer questions | Verify Search Console; review query data over a meaningful period and document dates and provenance. |
| Do visits lead to clicks or orders? | Live collector and authorized Associates reports | Deploy and test the collector; use only authorized first-party reports for clicks/orders and keep dated provenance. |
| Is product-data automation permitted and available? | Account eligibility, API access and current policy interpretation | Confirm program eligibility and API terms in official Amazon documentation before building ingestion or price/review features. |

## Source review links

- [Amazon Associates Operating Agreement](https://affiliate-program.amazon.com/help/operating/agreement)
- [Amazon Associates Program Policies](https://affiliate-program.amazon.com/help/operating/policies)
- [FTC Endorsement Guides: What People Are Asking](https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking)
- [Google guidance on qualifying outbound links](https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links)
- Product and manufacturer sources are indexed by ID in [`data/sources.json`](data/sources.json); unverified issues are linked from the live [Flagged for Review](https://karagemop466-tech.github.io/Affil3/flagged/) page.
