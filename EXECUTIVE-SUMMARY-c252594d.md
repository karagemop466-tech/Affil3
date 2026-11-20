# Executive summary — session `c252594d`

**Repository:** `karagemop466-tech/Affil3` · **Branch:** `arena/c252594d-affil3` (from `main` @ `67cfe2f`)
**Live site:** https://karagemop466-tech.github.io/Affil3/
**Selected Associates tracking ID:** `shopnow047c-20` — still **unverified** against the account
(FLG-011); the format matches the US convention, the ownership does not.
**Verification date:** 2026-11-20. Every source below was fetched and read on that date.

This is the current summary of the whole project. Earlier per-session summaries are kept
alongside it (`EXECUTIVE_SUMMARY-6249757a.md`, `EXECUTIVE_SUMMARY-93cee724.md`,
`EXECUTIVE-SUMMARY-arena63534e5d.md`, `EXECUTIVE-SUMMARY-2e0c91d0.md`) and are not replaced by it.

---

## 1 · The five products, and what we can actually stand behind

The owner supplied five `link.amazon` short links. Each one was followed, dated, and recorded.
The destination each link reached on the day it was fetched is a fact; the product the owner
*meant* is not, and the two are stored in separate fields and never merged.

| Row | Submitted link | Observed destination (2026-11-20) | Maker's own page | Published specification grid |
|---|---|---|---|---|
| P01 | [link.amazon/B04G1MEwY](https://link.amazon/B04G1MEwY) | [dp/B0CDY277D3](https://www.amazon.com/dp/B0CDY277D3) — CHEFMAN 6 Quart Dual Basket Air Fryer | [chefman.com RJ38-SQPF-3TDB-2W](https://chefman.com/products/turbofry-touch-dual-window-air-fryer) | Complete: 6 qt / 5.67 L, 200–450 °F, 1700 W / 120 V, 13.38 × 11.81 × 10.63 in, 13.3 lb, cETL, 1-year assurance |
| P02 | [link.amazon/B02NbDxp3](https://link.amazon/B02NbDxp3) | [dp/B09B7SB46R](https://www.amazon.com/dp/B09B7SB46R) — Emeril Lagasse 26 QT French Door | [emerileveryday.com 26 QT](https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360) | Partial: 26 qt / 24.6 L, 16.9 × 15.8 × 14.8 in, 120 V, 25 pre-sets. Wattage and weight are not stated by the maker and stay blank |
| P03 | [link.amazon/B00hJ57DV](https://link.amazon/B00hJ57DV) | [dp/B08DKYBTPH](https://www.amazon.com/dp/B08DKYBTPH) — Chefman 8 Qt TurboFry | [chefman.com RJ38-SQSS-8T](https://chefman.com/collections/air-fryers-1/products/turbofry-touch-air-fryer-1) | Partial: 8 qt / 7.57 L, 200–400 °F, 12.8 lb, 4 presets, cETL. Wattage and size still conflict with the listing and stay blank (FLG-026) |
| P04 | [link.amazon/B0c8moW59](https://link.amazon/B0c8moW59) | [dp/B0DHZTCNR5](https://www.amazon.com/dp/B0DHZTCNR5) — ThermoMaven 1 Sec Professional | [thermomaven.com F1 Ace](https://www.thermomaven.com/products/f1-ace) | Partial: one-second read, ±0.5 °F claimed, thermocouple, auto-rotating LCD, waterproof, magnet, lifetime warranty. Temperature range, power, size and weight are not stated and stay blank |
| P05 | [link.amazon/B0f3GKalj](https://link.amazon/B0f3GKalj) | [dp/B0DZFD6R9Z](https://www.amazon.com/dp/B0DZFD6R9Z) — CHEF iQ Sense | [chefiq.com iQ Sense](https://chefiq.com/products/iq-sense) | Partial: internal 32–212 °F, ambient 32–1,000 °F, heat resistant to 1,000 °F, probe 0.19 in × 4.75 in, Wi-Fi hub, USB-C |

**What changed in this pass.** Three published facts were wrong and are now corrected against the
manufacturer's own page:

1. **P05's temperature range was wrong.** The site published 32–1,000 °F as the probe's reading
   range. The maker's page states an internal range of **32–212 °F** and an ambient sensor range of
   32–1,000 °F; 1,000 °F is the ambient and heat-resistance ceiling. New flag FLG-033 records that
   the same page contradicts itself on its sensor count.
2. **P04 had no specifications at all, and that was itself out of date.** FLG-025 said no
   manufacturer page could be located. One exists. The row now carries a specification grid and a
   tagged outbound link, because the submitted link for that row does resolve to that listing.
   FLG-031 and FLG-032 record what is still open about it.
3. **P03's maker's page was the wrong one.** Chefman publishes the model the Amazon listing itself
   names (RJ38-SQSS-8T), so the 200–400 °F range and the 12.8 lb weight are now published from the
   maker's page rather than withheld. Wattage and size still disagree between two official pages,
   so they stay blank.

**What did not change.** The intended ASIN, official listing URL, confirmation date and confirmation
source remain **blank for all five rows**. The submitted tokens are nine characters, and the observed
destinations do not match them. Nothing on this site claims to know which product the owner meant;
only where the link landed, on a dated fetch. That is FLG-001 and FLG-002, and they remain open.

## 2 · What was built

| Surface | What it is |
|---|---|
| `/` | The publication front page. Products first, then questions, then categories, then method. Disclosure strip above the fold, repeated in the footer. |
| `/shop/` | The full comparison table: every tracked row, the observed listing title, and a source link on every row. |
| `/products/…` (5) | One page per product. Specification grid where the maker's figure is a *not stated* cell, the conflict explained in full, one tagged outbound link. |
| `/categories/…` (3) | Air fryers, countertop ovens, thermometers — each with its products and the guides that cover it. |
| `/guides/…` (13) | Question-shaped buying guides. Every factual sentence points at a source id; each guide lists its sources. |
| `/sources/` | The source register: 23 sources, each with its publisher, the URL, how it was checked and what it was used for. |
| `/questions/` | 17 known facts, 17 open questions with a blocking flag and a way to close each one, 12 discovery actions. |
| `/suggestions/` | 18 decisions, each with options, a trade-off per option and a session recommendation. Nothing is implemented until one is chosen. |
| `/flagged/` | 33 irregularities and unverified items, each with its sources and the manual step that closes it. Two are now marked resolved. |
| `/ledger/`, `/measurement/`, `/compliance/`, `/workflow/`, `/about/`, `/privacy/` | The empty-but-defined campaign ledger, the measurement plan, the gate description, the publishing workflow and the two policies. |

Publishing is a gate, not a convention. `node tools/verify.mjs` runs over every generated page and
stops the build on: a missing Associates statement or disclosure strip; an Amazon link without
`rel="sponsored"`; an Amazon link without `tag=shopnow047c-20`; a published price, star rating or
review count; a missing or remote image; a broken internal link; a source id that does not exist; a
specification cell that says "not stated" a different number of times than the data says it should;
and any guide that claims hands-on testing.

## 3 · What is verified, and from where

- The Amazon Associates Operating Agreement and Program Policies, read in full on 2026-11-20
  (S01, S02). The exact statement required by §5 — *"As an Amazon Associate I earn from qualifying
  purchases."* — appears above the fold on every page and again in every footer.
- `rel="sponsored"` on every outbound Amazon link, per Google's own guidance (S06).
- The FTC's disclosure wording and 16 CFR Part 255 (S07, S08).
- USDA safe minimum internal temperatures and thermometer placement guidance (S09, S10, S20).
- **Amazon's own definition of the ASIN** (S23): *"a unique combination of 10 letters and numbers
  that Amazon assigns to a product"*. This closes FLG-012, which had recorded that no Amazon-owned
  definition had been found.
- Every product specification, re-read in full against the manufacturer's own product page
  (S11, S12, S13, S14, S21, S22) on 2026-11-20.

## 4 · What is not verified, and why it is on the page

| Flag | What is open | What closes it |
|---|---|---|
| FLG-001 / FLG-002 | Which product each submitted link was *meant* to reach. The intended fields are blank on all five rows. | Open each link in a signed-in Amazon session and name the product. One message closes it. |
| FLG-003 | Whether the supplied short links comply with the Program Policies. They are **not** claimed invalid. | Test one link per product inside the enrolled Associates workflow. |
| FLG-005 / Q-16 | No Special Link has been clicked from this site and confirmed to credit a sale. | One click, one report row. This is the single highest-value owner action. |
| FLG-026 | The 8 qt fryer's maker's page and its Amazon listing disagree on wattage and size. | Open the listing signed in and read the model number and size chart. |
| FLG-031 / FLG-032 | The instant-read thermometer's maker's page and its listing carry different model names, and the listing adds certification and IP67 claims the maker does not make. | One email to ThermoMaven closes both. |
| FLG-033 | The wireless thermometer's maker's page contradicts itself on its sensor count. | Ask CHEF iQ, or read the manufacturer's own user guide PDF. |
| FLG-009 | The analytics collector is not deployed; the click counter is inactive on the live site. | Deploy `tools/collector.mjs` somewhere that can run it and set `analyticsEndpoint`. |
| FLG-013 | Search Console is not connected. | Verify the property, submit the sitemap, read queries after two weeks. |
| FLG-014 | There is no named individual author. | Name the editor, or keep the byline as a team and accept the trade-off. |

## 5 · The decisions that are waiting

Eighteen suggestions are on `/suggestions/`, each with options and a trade-off per option. The four
that change what the site becomes:

- **S-11 Design direction** — keep the warm editorial system, push it toward a shop, toward a
  reference work, or layer a seasonal campaign on top of it.
- **S-13 How opinionated the guides should be** — descriptive, position-taking per guide, or a named
  recommendation. The third is not available yet: the site states it is not a test kitchen.
- **S-15 Whether the shelf grows past five products** — only worth doing after the link test passes.
- **S-18 Distribution** — hold social distribution until the click counter is live, so distribution
  and measurement switch on together.

## 6 · What this session did not do, and will not pretend to have done

- It did not confirm that the tracking ID belongs to the account, that the site is declared, or
  that a click produces a commission. Those need the owner's signed-in session.
- It did not scrape Amazon. Every value on this site was read from a page fetched one at a time and
  cited, and every observation is dated.
- It did not publish a price, a rating, a review count, a commission rate or a revenue forecast,
  because none of those can be sourced from an official page without authorised access.
- It did not fill in an intended ASIN, a confirmation date or a confirmation source. Blank means
  "not confirmed", and the register says so at the top of the file.
