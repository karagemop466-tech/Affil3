# Executive summary — session `7e5808de`

**Repository:** `karagemop466-tech/Affil3`
**Live site:** <https://karagemop466-tech.github.io/Affil3/>
**Tracking ID:** `shopnow047c-20`
**Date:** 2026-11-20

---

## What this is

A reader-facing affiliate publication for two countertop cooking categories — air
fryers and kitchen thermometers — covering five supplied products. It is built as a
static site from a JSON data register, with no framework, no third-party dependency
and no third-party tracking script.

The organising idea is that the reader arrives with a question, not with a product.
So the site leads with six question-shaped buying guides, and the product register
sits behind them as the sourced evidence.

## The five products and where their links actually go

Every one of the five submitted `link.amazon` links was fetched and its redirect
followed on 2026-11-20. All five resolve to an `amazon.com/dp/<ASIN>` page.

| Submitted link | Token | Observed destination | Title read on the destination |
| --- | --- | --- | --- |
| `link.amazon/B04G1MEwY` | 9 chars | `B0CDY277D3` | Chefman 6 Quart Dual Basket Air Fryer Oven |
| `link.amazon/B02NbDxp3` | 9 chars | `B09B7SB46R` | Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven |
| `link.amazon/B00hJ57DV` | 9 chars | `B08DKYBTPH` | Chefman Air Fryer 8 Qt, TurboFry 4-in-1 |
| `link.amazon/B0c8moW59` | 9 chars | `B0DHZTCNR5` | ThermoMaven 1 Sec Professional Digital Meat Thermometer |
| `link.amazon/B0f3GKalj` | 9 chars | `B0DZFD6R9Z` | CHEF iQ Sense Gen3 Smart Wireless Meat Thermometer |

**All five tokens are 9 characters.** Amazon defines an ASIN as a 10-character
alphanumeric identifier, so none of the five tokens can be an ASIN. Every observed
destination is a 10-character ASIN. The intended ASIN, intended listing URL,
confirmation date and confirmation source are therefore recorded as **blank and
flagged**, and the observed destinations are recorded in entirely separate fields.
The two are never merged, anywhere, on any page.

## What was checked, and how

| Claim checked | Official source | Result |
| --- | --- | --- |
| Five links resolve | amazon.com product pages | 5/5, re-confirmed during integration |
| Destination identity | The `<title>` on each destination page | Captured verbatim with URL and date |
| Browse path | The breadcrumb on each destination page | 3 under Air Fryers (`17659096011`), 2 under Meat thermometers (`289810`) |
| ASIN shape | Amazon's Creators API reference: "10-character alphanumeric unique identifier" | All five tokens fail it; all five destinations pass it |
| Prices may not be published | Program Policies 2(b) | No price appears anywhere on the site |
| Ratings may not be published | Program Policies 5(t) | No rating or review count appears anywhere on the site |
| Links must be direct and tagged | Program Policies 2(b), 5(v), 5(w) | Every published link is a direct tagged Special Link; no short link is published |
| Disclosure wording and placement | Operating Agreement §5, FTC Disclosures 101 | Under the masthead on all 44 pages, repeated in the footer |
| Outbound link marking | Google Search Central, outbound links | `rel="sponsored nofollow"`, a visible marker and an aria-label on every one |
| API choice | Amazon's PA-API 5 deprecation notice | PA-API 5 is deprecated and returns 403 `AccessDeniedException`; the tooling targets the Creators API |

Fourteen official sources, each with a verbatim quote, are in the register at
`data/sources.json` and published at `/methods/sources/`.

## What the site does not claim

- **No price, star rating, review count, availability or commission rate** is published
  anywhere. Program Policies 2(b) and 5(t) allow those only from Creators API or
  PA API, and neither is configured. The code path for a live lookup exists in
  `assets/js/site.js` and stays empty until an endpoint is set.
- **No conversion score, revenue forecast, popularity claim, search-volume claim or
  product-superiority claim.** There is nothing to draw them from.
- **No forecast of any kind.** The campaign ledger ships empty, with its fifteen
  columns defined in `data/ledger_schema.md`.
- **No measured click or order data.** Only the five defined events are collected, and
  the ledger is only filled from authorized first-party reports with dated provenance.

## The measurement layer

`tools/analytics_sink.py` is a self-hosted collector and static server in the Python
standard library. It records the five events only — `page_view`, `outbound_click`,
`guide_progress`, `table_use`, `reader_signup` — with a server timestamp, the page
path, the event's own allow-listed fields, and a salted hash of a random per-session
id. It does **not** collect the client IP address, the user agent, cookies, referrer
URLs or any advertising identifier. Unknown events and unexpected fields are rejected
with a 400. It was exercised live during the build: a valid event was stored and
summarised, and both rejection paths returned 400.

The browser collector in `assets/js/analytics.js` honours Do Not Track and Global
Privacy Control, and does nothing at all when either is set.

## The editorial position

Six guides, each shaped as a question a reader would actually type:

1. Basket or oven-style air fryer — what should you compare?
2. A no-hype checklist for comparing air fryer capacity
3. How to assess cleanup and counter-space trade-offs
4. Questions to ask before buying a multi-function kitchen appliance
5. How accurate does a meat thermometer need to be?
6. Wireless meat thermometer or probe?

Plus two comparison pages, two category hubs, five product pages, and a decision
board: open questions (20, grouped by workstream), editorial paths (4, with 17
suggestions and a recommended sequence), and a flagged-for-review page (12 flags,
none of which block launch).

## The compliance position

Every Amazon shopping link on the site is a direct Special Link:

```
https://www.amazon.com/dp/<ASIN>?tag=shopnow047c-20&linkCode=ogi&th=1&psc=1&language=en_US
```

Each carries `rel="sponsored nofollow"`, a visible "Sponsored" marker and an
aria-label naming the product. There is no analytics redirector and no Amazon
sub-tag. The five submitted short links are recorded in the register as observations
and are never published as outbound links.

## The gate

`python3 tools/check_site.py` enforces eleven rules and currently reports
**0 violations, 0 warnings** across 44 generated pages: disclosure placement and
footer repetition, tagged sponsored product links, no published short redirects,
internal-link integrity, external-host allowlisting, page metadata, sitemap and feed
coverage, absence of published prices and ratings, intent/observation separation, the
empty-ledger policy, and product-page source evidence.

## What is left open

Twelve flags are published at `/desk/flags/`. The ones that matter most:

- The intended product behind each link cannot be read from any public source. It
  needs the owner's own confirmation, or a Creators API call with the tokens as
  ASINs.
- The tracking ID's issuance and activation were not publicly confirmed.
- The Associates account and its declared sites could not be verified.
- Creators API access requires enrolment and at least 10 qualifying sales in 30 days.
- GitHub Pages logs visitor IP addresses server-side, which is why the site keeps no
  client-side identifiers of its own.

None of these stop the site from serving. All of them are on the site, with the
source that was checked and the step that would close each one.

## Integration note

Two earlier sessions had already published to this repository. Their sites were
archived under `legacy/arena-83a43a96/` and `legacy/arena-6249757a/`, unchanged, and
their boards are kept verbatim in `COORDINATION.md`. Fourteen URL paths they
published now serve a redirect page pointing at the current home for that content.

One factual discrepancy between the sessions was found during integration and
resolved by re-checking the source: an earlier draft of this session's register
miscounted two submitted tokens as 10 characters. All five are 9. The register, the
flags, the questions, the source log and the page copy were corrected, and the
mapping was re-confirmed with fresh fetches.
