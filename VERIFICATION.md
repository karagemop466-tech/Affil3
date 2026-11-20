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

# Session `c252594d` — primary-source re-verification (2026-11-20)

**Rule, unchanged:** every published value points at a dated fetch of the page named in the source
register. Where two official pages disagree, the cell is left blank and the disagreement is
published as a flag. Nothing is inferred.

## A · Sources read in full by this session

| ID | Page | Read | Used for |
|---|---|---|---|
| [S21](https://www.thermomaven.com/products/f1-ace) | ThermoMaven F1 Ace Instant Read Thermometer | 2026-11-20 | P04 specifications; the page FLG-025 said did not exist |
| [S22](https://chefman.com/collections/air-fryers-1/products/turbofry-touch-air-fryer-1) | Chefman TurboFry Touch Stainless-Steel Air Fryer, 8 qt (RJ38-SQSS-8T) | 2026-11-20 | P03 temperature range, weight, presets, certification |
| [S23](https://advertising.amazon.com/library/guides/asins-introduction) | Amazon Ads — "Understanding ASINs" | 2026-11-20 | The Amazon-owned ASIN definition; closes FLG-012 |
| [S11](https://chefman.com/products/turbofry-touch-dual-window-air-fryer) | Chefman TurboFry Touch 6 Qt Dual-Window | 2026-11-20, re-read in full | P01 re-check: capacity, range, watts, size, weight, model — all unchanged |
| [S12](https://chefman.com/products/turbofry-8-qt-air-fryer-w-high-fry) | Chefman TurboFry 8 Qt w/ High Fry (RJ38-8T-BLACK) | 2026-11-20, re-read in full | The second 8 qt machine; sharpens FLG-026 |
| [S13](https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360) | Emeril Lagasse French Door AirFryer 360, 26 QT | 2026-11-20, re-read in full | P02 re-check: 26 qt / 24.6 L, 16.9 × 15.8 × 14.8 in, 120 V, 25 pre-sets, model 4-00675-02A-VN |
| [S14](https://chefiq.com/products/iq-sense) | CHEF iQ Sense | 2026-11-20, re-read in full | P05 internal 32–212 °F, ambient 32–1,000 °F, heat resistance to 1,000 °F, probe 0.19 in × 4.75 in, materials stainless steel and zirconia |
| [S04](https://www.amazon.com/dp/B0DHZTCNR5) | Amazon listing for the ThermoMaven row | 2026-11-20 | Confirms the observed destination is live and is a ThermoMaven 1 Sec Professional Digital Meat Thermometer |
| [S05](https://link.amazon/B0c8moW59) | The submitted short link for the ThermoMaven row | 2026-11-20, three attempts | Two attempts in earlier sessions resolved to the listing; a third attempt on this date landed on the Amazon home page. The destination varies by attempt — FLG-003 |

Also read on 2026-11-20 and unchanged: the Associates Program Operating Agreement and Program
Policies (S01, S02), Google `rel="sponsored"` guidance (S06), 16 CFR Part 255 (S07, S08), and the
USDA temperature and thermometer-placement pages (S09, S10, S20).

## B · Line-by-line result for every published specification

Blank means the maker's page does not state it. "Not stated" cells are counted by the gate and
must match the data exactly.

| Row | Field | Was published | Now published | Evidence |
|---|---|---|---|---|
| P01 | model / capacity / range / power / size / weight / certification / warranty | RJ38-SQPF-3TDB-2W, 6 qt, 200–450 °F, 1700 W, 13.38 × 11.81 × 10.63 in, 13.3 lb, cETL, 1-year | **unchanged** | S11 re-read in full |
| P02 | capacity / size / voltage / model | 26 qt / 24.6 L, 16.9 × 15.8 × 14.8 in, 120 V, 4-00675-02A-VN | **unchanged** | S13 re-read in full |
| P02 | wattage / weight / temperature range | blank | **still blank** — the maker states none of them | S13 |
| P02 | preset count | blank | **still blank** — maker says 25 pre-sets, listing says 24 one-touch options (FLG-024) | S13, S04 |
| P03 | model | RJ38-8T-BLACK | **RJ38-SQSS-8T** — the model the Amazon listing itself names, and which the maker publishes | S22, S16 |
| P03 | temperature range | blank | **200–400 °F** | S22 |
| P03 | weight | blank | **12.8 lb** | S22 |
| P03 | wattage | blank | **still blank** — maker says 1700 W, listing says 1000 W (FLG-026) | S22, S04 |
| P03 | size | blank | **still blank** — maker says 15.4 × 12.6 × 13.5 in, listing says 12.75 × 13.5 × 10 in (FLG-026) | S22, S04 |
| P04 | every field | blank, no buy button, flagged FLG-025 | **model, functions, cleaning, certification wording, warranty populated; tagged outbound link enabled** | S21, S04 |
| P04 | temperature range / power / size / weight | blank | **still blank** — the maker states none of them | S21 |
| P05 | temperature range | 32–1,000 °F | **32–212 °F** internal, with 32–1,000 °F published as the ambient range on its own row | S14 |
| P05 | probe size / cleaning / functions | 0.19 in × 4.75 in, waterproof, sensors | **unchanged**, plus the sensor-count conflict recorded (FLG-033) | S14 |
| P05 | model / battery | blank | **still blank** — the maker shows one variant of a family and the two pages disagree on battery life (FLG-023) | S14, S15 |

## C · Flags opened, closed and sharpened by this pass

| Flag | Action |
|---|---|
| FLG-012 | **Closed.** Amazon's own page defines the ASIN as 10 letters and numbers (S23). |
| FLG-025 | **Closed.** A ThermoMaven manufacturer page exists (S21); the specifications are published and the buy link is enabled. |
| FLG-026 | **Sharpened.** Chefman publishes two 8 qt machines; the maker's page for the model the listing names agrees on the range, and still disagrees on wattage and size. |
| FLG-031 | **Opened.** The maker's page and the listing carry different model names for the instant-read thermometer. |
| FLG-032 | **Opened.** The listing states NSF certification and an IP67 rating that the maker's page does not. |
| FLG-033 | **Opened.** The maker's own page contradicts itself on the wireless thermometer's sensor count. |

## D · What was deliberately not done

- No intended ASIN, official listing URL, confirmation date or confirmation source was filled in.
  The submitted tokens are nine characters and the observed destinations differ from them; the
  intended product stays blank until it is confirmed in a signed-in session.
- No price, rating, review count, commission rate, conversion score or revenue forecast was
  published. None can be sourced from an official page without authorised access.
- No claim was made that any supplied short link is invalid. Their compliance status is unresolved
  (FLG-003), and the destination varies by attempt.
- Nothing was published about hands-on use. The site is specification-led and says so.
