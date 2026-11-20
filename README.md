# Counter Notes — executive summary

## What this repository now contains

A static, responsive publication front page focused on useful kitchen-buying questions; four original general-purpose decision guides; a product-intent review page; an editorial suggestion desk; methodology and official-source notes; an RSS 2.0 feed; an XML sitemap; and a GitHub Pages Actions workflow with structural link checks. This is a publication site and verification scaffold—not an operating AI affiliate automation platform: no Amazon catalog API, product research automation, trend/commission scoring, link generation, Search Console integration, live analytics backend or conversion ingestion is active.

The landing page leads with reading and decisions—not an audit dashboard. A compact review queue keeps operational surfaces reachable from the footer and navigation. Each HTML page has the Amazon Associate statement under the masthead and again in its footer.

## Product and compliance status

The only inputs about the five products were the five short URLs in the request. No product identity or product category, exact official listing, feature, price, review, rating, availability, commission, conversion, or performance information could be verified from those inputs. Air-fryer article ideas came from the request’s editorial examples and are not evidence that the submitted links are air fryers. The path tokens are each nine characters as submitted. Amazon describes ASINs as 10-character alphanumeric identifiers; this is a reason to confirm the intended identifiers, **not** evidence that the supplied short links are invalid. Their compliance status remains unresolved.

The intended ASIN, official listing URL, confirmation date/source and observed redirect target have separate columns in `data/product-intent.csv`; unknown values are blank. The selected Tracking ID `shopnow047c-20` was supplied by the user but could not be checked against Associates Central. No product purchase links are active until a reviewer confirms product intent, destination, Special Link status, tracking attribution and relevant first-party reports. Do not infer a destination from a redirect and overwrite product intent.

The general buyer guides do not state that any listed model has been tested, preferred, best-selling, trending or superior. Their article topics are editorial hypotheses, not measured demand. See [Flagged for Review](flagged-review.html) for the complete questions and discovery plan.

## Measurement and publishing

The browser script defines five event types and holds a capped event log in localStorage on that visitor's device only. It sends nothing because no analytics API is deployed. `analytics/server.mjs` is an optional self-hosted, aggregate-only endpoint implementation, but it is not running on GitHub Pages and is not connected to this site. No Search Console property, query report, Amazon orders, sales or revenue is available. `data/campaign-ledger.csv` is intentionally empty beyond its schema. No score, forecast or conversion claim is presented.

Recommended operating cadence: review Search Console and the authorized Associates report monthly; schedule one evidence-reviewed guide per week only when a question is supported by actual query evidence or demonstrable reader need, and update the feed and sitemap in the same change. This is a proposed operating rhythm, not a promise of future publication. The four current guides are general editorial checklists and were added to both feed and sitemap.

## Executive decisions still needed

1. Confirm the Associates account/site enrollment, marketplace, and status of Tracking ID `shopnow047c-20` within Associates Central.
2. Test one submitted link per product in the enrolled workflow. Confirm intended product, official listing, actual observed destination and tracking report separately.
3. Confirm exactly which product facts may be published and which authorized Amazon data source/tool will supply them. Recheck current program policies before using API content, prices or images.
4. Decide on an HTTPS first-party analytics host and privacy/retention configuration. GitHub Pages cannot host the endpoint.
5. Connect Search Console after publication and use measured queries—not assumed trendiness—to select the next guide.
6. Assign a human editorial/compliance reviewer for product-link activation, endorsements, and ongoing policy checks.

## Run checks locally

```sh
python3 scripts/check_site.py
node --check analytics/server.mjs
```

To publish, enable GitHub Pages with GitHub Actions as its source, then merge the validated workflow to `main`. The configured workflow deploys from `main`. The branch working this session is `arena/114f47c4-affil3`; this static build is not described as live until GitHub reports a successful Pages deployment.

## Official sources reviewed

- [Amazon Associates Program Operating Agreement](https://affiliate-program.amazon.com/help/operating/agreement) — Associates disclosure and program terms.
- [Amazon Associates link disclosure guidance](https://affiliate-program.amazon.com/help/node/topic/GPXFHVYZMTGPUMPE) — link-level disclosure placement examples.
- [Amazon Associates Program Policies](https://affiliate-program.amazon.com/help/operating/policies) — program and Product Advertising Content/API policies.
- [Amazon ASIN overview](https://sell.amazon.com/blog/fba-new-selection-program) — ASIN described as a unique 10-character alphanumeric identifier.
- [FTC Endorsement Guides: What People Are Asking](https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking) — FTC guidance on clear and conspicuous affiliate disclosures.
- [FTC Disclosures 101 for Social Media Influencers](https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers) — general disclosure guidance.
- [Google Search Central: qualify outbound links](https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links) — paid links can be marked `rel="sponsored"`.
- [GitHub Pages documentation](https://docs.github.com/en/pages) — GitHub Pages static hosting.

Sources reviewed 20 November 2026. Program policies and official guidance may change; verify the current text before launch. This is operational documentation, not legal advice.
