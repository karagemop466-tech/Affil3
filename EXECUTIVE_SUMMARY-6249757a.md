# Executive summary: Affil3 Amazon affiliate buying-guide site

**Date:** 2026-11-20 · **Branch:** `arena/6249757a-affil3` · **Tracking ID:** `shopnow047c-20`

## What was delivered

- A static, publication-style site (23 pages): front page led by the five submitted products, a shop table with every row and its sources, four category clusters, five question-led guides, RSS feed, sitemap and robots.txt. Source: `docs/`, built from `data/`.
- Dashboards linked from the footer: executive summary, shop table, categories, source register, questions and gaps, suggestions (choose a path), flagged for review, campaign ledger (empty), measurement, compliance and gates, about.
- Disclosure strip under the masthead on every page, repeated in the footer, using the statement required by Associates Operating Agreement §5 ([S01](https://affiliate-program.amazon.com/help/operating/agreement)).
- Automated publishing gate (`tools/verify.mjs`, 1,265 checks) and a privacy-preserving click counter with a self-hostable collector.

## What is verified (official sources)

- Operating Agreement §1 (Special Links), §5 (disclosure): [S01](https://affiliate-program.amazon.com/help/operating/agreement).
- Program Policies: tag requirement (§2, excerpt), anti-cloaking (v), link-shortener restriction (w): [S02](https://affiliate-program.amazon.com/help/operating/policies).
- Associates ID format ending in -20: [S03](https://affiliate-program.amazon.com/help/node/topic/GM6CHU93RDXZV7D8).
- rel="sponsored" for paid and affiliate links: [S06](https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links).
- FTC disclosure placement: [S07](https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers); 16 CFR Part 255: [S08](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255).
- USDA minimum internal temperatures: [S09](https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/safe-temperature-chart), [S10](https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/food-thermometers).
- Observed Amazon product pages for four of the five links (title, breadcrumb, 10-character ASIN), read on 2026-11-20: [S04](https://www.amazon.com/dp/B0CDY277D3), [S05](https://link.amazon/B04G1MEwY).

## What is not verified, and why

| Item | Status | Flag |
| --- | --- | --- |
| Intended ASIN, official listing URL, confirmation date and source | Blank for all five rows. The submitted tokens are 9 characters; observed Amazon IDs are 10. | FLG-001 |
| Observed destinations differ from the tokens | Recorded separately; not treated as the intended product. | FLG-002 |
| Short-link compliance | Unresolved, not invalid. Policy (w) restricts shorteners that obscure the Amazon destination. | FLG-003 |
| One link (B00hJ57DV) | Landed on a checkpoint page; no product; no buy link published. | FLG-004 |
| Associates validation of tagged links | Not tested; no Associates login in the sandbox. Gate G-02 before any scaling. | FLG-005 |
| Associates account status and declared site | Unknown. | FLG-006 |
| Amazon-owned ASIN definition | Not located. | FLG-012 |

## Decisions needed from you

1. The intended product for each short link, or confirmation of the observed product (Q-01, blocking).
2. Whether the Associates account is active and declares this site (Q-03, blocking).
3. Result of gate G-02 in Associates Central (Q-04, blocking).
4. Choices on the Suggestions page (S-01 to S-12). Nothing there is implemented until you choose.
5. Analytics hosting for the collector (S-03) and the five events (Q-05).

## Limits

- No prices, ratings, sales or commissions are shown. The campaign ledger is empty. No conversion score or revenue forecast is presented.
- The product research platform described in the brief (automated trend and competition analysis) needs authorized Amazon data access (for example the Product Advertising API) and Associates reports. The sandbox has neither, and the site does not scrape Amazon.
- Six other session branches on the remote claim the same overall task (FLG-017). Merging them will need a single integration decision.
