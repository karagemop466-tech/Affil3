# VERIFICATION — line-by-line verification log

Session `arena-93cee724` · verification date **2026-11-20** · rule: **every table row has a
source link to an official site; if a value can't be confirmed from an official source it is
left blank and flagged as unverified. Nothing is inferred or filled in.**

Source registry with full URLs: `data/93cee724/sources.json` (IDs S-01…S-15). All sources were
fetched and read on 2026-11-20 unless noted.

## 1 · Compliance references (verified)

| # | Claim used | Status | Official source (for manual review) | Verified |
|---|-----------|--------|-------------------------------------|----------|
| 1 | Amazon requires the statement “As an Amazon Associate I earn from qualifying purchases.” clearly and prominently on the site (Operating Agreement §5) | verified | [Associates Program Operating Agreement](https://affiliate-program.amazon.com/help/operating/agreement) (S-01) | 2026-11-20 |
| 2 | Affiliate links must use the special “tagged” link formats Amazon provides (“Special Links”) (Operating Agreement §1) | verified | [Operating Agreement](https://affiliate-program.amazon.com/help/operating/agreement) (S-01) | 2026-11-20 |
| 3 | Link-level disclosure must be legally compliant (FTC) and the OA statement must appear on the site | verified | [Associates help — identifying yourself as an Associate](https://affiliate-program.amazon.com/help/node/topic/GHQNZAU6669EZS98) (S-02) | 2026-11-20 |
| 4 | ASIN = 10-character alphanumeric code, typically “B0” + 8; appears after `/dp/` in the product URL | verified | [Sell on Amazon — Understanding ASINs](https://sell.amazon.com/blog/what-is-an-asin) (S-03, Amazon-owned property) | 2026-11-20 |
| 5 | Material connections must be disclosed, hard to miss, in plain language (“advertisement”, “ad”, “sponsored”), with the endorsement itself | verified | [FTC — Disclosures 101 for Social Media Influencers](https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers) (S-04) | 2026-11-20 |
| 6 | Endorsements must be truthful and not misleading; compensated promoters must disclose (Endorsement Guides, rev. June 2023) | verified | [FTC — Advertisement Endorsements hub](https://www.ftc.gov/news-events/topics/truth-advertising/advertisement-endorsements) (S-05) | 2026-11-20 |
| 7 | Program Policies are incorporated into the Operating Agreement | verified (by S-01 text) | [Associates Program Policies](https://affiliate-program.amazon.com/help/operating/policies) (S-11) | 2026-11-20 |

## 2 · Product register (observed 2026-11-20; intended vs observed kept separate)

Method: each submitted link fetched individually with redirects followed. ASIN read from the
`/dp/` segment of the final URL. Title and category breadcrumb recorded verbatim. **Two
fields, never merged:** `intended.*` = what the submitted link states; `observed.*` = what
the fetch saw. (Per the brief, no claim is made that any submitted link is invalid;
compliance status is unresolved — FLG-003.)

**Cross-session note:** this session’s independent fetches (4 resolved, 1 checkpoint) agree
exactly with the corrected register and dated retest already on `main`
(`data/products.json`, `data/observations/2026-11-20-retest.json`, PR #10 correction),
which additionally resolved the checkpointed link to `B0DHZTCNR5`. Three independent
observation passes now agree on P-01, P-02, P-03, P-05.

| Item | Submitted (S-14) | Intended token (9 chars) | Observed redirect target | Observed listing title (verbatim) | Source | Status |
|------|------------------|--------------------------|--------------------------|-----------------------------------|--------|--------|
| P-01 | [link.amazon/B04G1MEwY](https://link.amazon/B04G1MEwY) | B04G1MEwY | [amazon.com/dp/B0CDY277D3](https://www.amazon.com/dp/B0CDY277D3) | “CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows, Sync Finish, Hi-Fry, Auto Shutoff, 2 Independent 3Qt Nonstick Dishwasher Safe Frying Baskets, Digital Double Air Fryer - Black” | S-06 | observed |
| P-02 | [link.amazon/B02NbDxp3](https://link.amazon/B02NbDxp3) | B02NbDxp3 | [amazon.com/dp/B09B7SB46R](https://www.amazon.com/dp/B09B7SB46R) | “Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven \| Countertop Convection Cooker, 24 One-Touch Preset Options, Extra Large Interior, Six Cooking Accessories Included” | S-07 | observed |
| P-03 | [link.amazon/B00hJ57DV](https://link.amazon/B00hJ57DV) | B00hJ57DV | [amazon.com/dp/B08DKYBTPH](https://www.amazon.com/dp/B08DKYBTPH) | “Chefman Air Fryer 8 Qt \| TurboFry 4-in-1 with 450F Hi-Fry Option for Crispier Results \| Bake, Dehydrate, Frozen \| XL Nonstick Dishwasher-Safe Basket \| Stainless Steel” | S-08 | observed |
| P-04 | [link.amazon/B0c8moW59](https://link.amazon/B0c8moW59) | B0c8moW59 | — **blank (this session)** | — **blank (this session)** | S-10, S-15 | **unverified here (FLG-004)** — Amazon “Continue shopping” checkpoint interstitial on 2 fetch attempts by this session. A later independent retest (S-15, session f761b123) resolved the same link to [amazon.com/dp/B0DHZTCNR5](https://www.amazon.com/dp/B0DHZTCNR5) (“ThermoMaven 1 Sec Professional Digital Meat Thermometer…”). Cross-session observation recorded with attribution; not merged into this session’s observed fields; intent still unconfirmed (FLG-003) |
| P-05 | [link.amazon/B0f3GKalj](https://link.amazon/B0f3GKalj) | B0f3GKalj | [amazon.com/dp/B0DZFD6R9Z](https://www.amazon.com/dp/B0DZFD6R9Z) | “CHEF iQ Sense \| Smart Wireless Meat Thermometer \| 3 Ultra-Thin Probes \| WiFi Unlimited Range \| 1000F Heat Safe \| 5 Sensors \| BBQ, Grill, Oven, Smoker, Air Fryer \| Gen3” | S-09 | observed |

### Token format check (checkable fact, not a validity claim)

| Check | Result | Source |
|-------|--------|--------|
| Each submitted token vs documented ASIN format (10 characters, typically B0 + 8) | All five tokens are **9 characters, mixed case** → format mismatch recorded as **FLG-001**. Validity **not claimed** either way (FLG-003; brief: “Do not claim that the supplied short links are invalid”) | S-03 |

### Values deliberately left blank (never inferred)

| Value | State | Reason |
|-------|-------|--------|
| Price (all items) | blank · FLG-010 | Volatile; not verified at fetch time; carousel prices on fetched pages referred to other items and were not attributable |
| Rating / review count (all items) | blank · FLG-010 | Same |
| P-04 identity, title, category | blank · FLG-004 | Destination never observed |
| Commission rates | blank | Not verified from an authorized first-party report |

## 3 · Site build verification (automated)

Run before publish (all green on 2026-11-20):

| Check | Tool | Result |
|-------|------|--------|
| intended/observed fields separate; volatile fields null; flag/source refs resolve | `python3 tools/validate.py` | PASS — 5 products, 11 flags, 14 sources, 12 questions, 15 suggestions |
| Exact Associates statement ≥ 2× per page (strip + footer) | `tools/validate.py` | PASS — 18 pages |
| Every `amazon.com/dp/` and `link.amazon/` link `rel="sponsored nofollow noopener"` + `data-tci="outbound"` + visible Sponsored chip | `tools/validate.py` | PASS |
| Every data surface has source links or explicit unverified markers | `tools/validate.py` | PASS |
| Sitemap (17 URLs, S-12 format) and RSS feed (6 items, S-13 format) cover the site | `tools/validate.py` | PASS |
| Internal links + anchors | `python3 tools/check_links.py` | PASS — 18 pages, 0 broken internal links |

## 4 · Irregularities (all published on the site’s Flagged for Review page)

1. **FLG-001** — submitted tokens don’t match the documented ASIN format (9 vs 10 chars).
2. **FLG-002** — `link.amazon` domain resolves into amazon.com (observed), but its status as an Amazon-operated short-link service is unconfirmed from an official source.
3. **FLG-003** — short-link compliance unresolved (per the brief’s own wording); one-link-per-product Associates workflow test required before scaling.
4. **FLG-004** — P-04 destination unverified (checkpoint interstitial ×2).
5. **FLG-005** — site outbound URLs use `?tag=shopnow047c-20` on observed listing URLs; not yet validated in the enrolled Associates workflow (brief item S02).
6. **FLG-006** — self-hosted analytics endpoint not deployed (GitHub Pages is static); counter ships dry-run with a reference implementation ready in `tools/analytics-endpoint/`.
7. **FLG-007** — Search Console verification token missing (owner account required) — SG-29 gated.
8. **FLG-008** — reader-capture endpoint missing (owner decision required) — SG-30 gated.
9. **FLG-009** — spec codes S01/S02/S07/S24/SG-27…SG-30 referenced in the brief without a source spec; mapped provisionally from the brief’s own wording.
10. **FLG-010** — price/rating fields intentionally blank.
11. **FLG-011** — editorial display names shortened from verbatim listing titles (derivation shown on-page).

## 5 · External links for manual review

- https://affiliate-program.amazon.com/help/operating/agreement
- https://affiliate-program.amazon.com/help/node/topic/GHQNZAU6669EZS98
- https://affiliate-program.amazon.com/help/operating/policies
- https://sell.amazon.com/blog/what-is-an-asin
- https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers
- https://www.ftc.gov/news-events/topics/truth-advertising/advertisement-endorsements
- https://www.amazon.com/dp/B0CDY277D3 · /dp/B09B7SB46R · /dp/B08DKYBTPH · /dp/B0DZFD6R9Z
- https://link.amazon/B04G1MEwY · /B02NbDxp3 · /B00hJ57DV · /B0c8moW59 · /B0f3GKalj
- https://www.sitemaps.org/protocol.html · https://www.rssboard.org/rss-specification

---

# VERIFICATION — session `arena/77e4ac42-affil3` (Journal + decision board)

Verification date **2026-11-20** · rule unchanged: **every table row has a source link to an official
site; if a value can't be confirmed from an official source it is left blank and flagged as
unverified. Nothing is inferred or filled in.** This session added a reader-facing Journal and a
decision board. It did not change any product, spec, flag or source value.

## 6 · The Journal articles (sourced; no new facts invented)

Each article's factual claims are drawn only from source IDs already in the register and cited on the
article. Article titles are editorial working titles, not popularity, search-volume or superiority
claims. No price, rating, review count or hands-on test claim appears.

| # | Article | Factual claims | Source IDs | Status |
|---|---------|----------------|-----------|--------|
| 1 | Two baskets, one machine: what dual-basket air fryers change | 6 qt in two 3 qt baskets; Sync Finish; 200–450 °F; 1700 W; dishwasher-safe baskets; case size; 1-yr warranty | S11, S04 | sourced |
| 2 | When a basket isn't enough: the case for a 26-quart oven | 26 qt / 24.6 L; french doors; food for 4–6; case size 16.9×15.8×14.8 in; 1-yr warranty; preset-count discrepancy named | S13, S04 | sourced |
| 3 | Eight quarts, one basket: the big-batch air fryer | 8 qt / 7.57 L; 200–400 °F; maker 1700 W vs listing wattage conflict; RJ38-SQSS-8T vs RJ38-8T-BLACK | S12, S16, S04 | sourced |
| 4 | Counter space is the real spec: measure before you buy | Case dimensions for P01/P02/P03, reproduced in the makers' own order | S11, S12, S13, S04 | sourced |
| 5 | The number that decides when to pull it: thermometer basics | USDA safe minimum internal temperatures; probe placement | S10, S20, S21, S14 | sourced |
| 6 | Instant-read vs leave-in: two thermometers, two jobs | ThermoMaven 1-sec read, ±0.5 °F NIST; CHEF iQ leave-in, up to 1000 °F | S21, S14, S15, S10 | sourced |
| 7 | The big roast: what temperature actually means | USDA temperature targets and rest times; probe placement | S10, S20 | sourced |

**Values deliberately not claimed:** no price, rating, review count, availability, traffic, conversion
or revenue figure appears in any article. The wattage conflict in article 3 is named, not resolved.

## 7 · Decision board (no factual claims; questions carry their own sources)

| # | Board item | Type | Sources | Status |
|---|-----------|------|---------|--------|
| D-01…D-08 | Suggestions (house style, Journal, topic selection, reader capture, brand/imagery, navigation, revenue unblock, cadence) | each has options + recommendation | none (design proposals, not factual claims) | proposal |
| DQ-01…DQ-04 | Blocking questions (marketplace, tracking ID live, Special Link test, intended product) | owner-access | S01, S02, S04, S05 | open |
| DQ-05…DQ-10 | Non-blocking questions (reader, cadence, analytics endpoint, prices, byline, edition) | owner decision | S01, S02 where factual | open |

Questions that rest on a factual policy point cite the official source (S01 Associates Operating
Agreement, S02 Program Policies). Questions that are pure owner decisions carry no source, because they
are not factual claims — that is stated on the page.

## 8 · Build and gate results (2026-11-20)

| Check | Tool | Result |
|-------|------|--------|
| Root build | `node tools/build.mjs` | 41 pages, 12 feed items, 40 sitemap URLs |
| Publishing gate | `node tools/verify.mjs` | 4,876 checks passed, 0 failed |
| Full check (root + editorial) | `npm run check` | pass; editorial output did not drift |
| Table source coverage (strict) | `python3 tools/link_report.py --strict` | OK — every checked table 100% sourced |
| Internal link integrity | `python3 tools/check_all_links.py` | 0 broken internal links |
| Docs sitemap + links | `scripts/build_sitemap.py --check`, `scripts/check_links.py --no-external` | pass |
| Editorial gate | `python3 tools/check_site.py` | PASS — 21 pages |

## 9 · New external links for manual review

None added. Every Journal and decision-board link is either an internal page or an already-registered
source. The article product boxes resolve to the same tagged Amazon listing URLs already published on
the Shop and product pages.
