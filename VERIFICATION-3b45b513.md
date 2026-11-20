# Verification log — session `3b45b513`

**Verified:** 2026-11-20 · **Rule:** every row below was read in this session, and every value
on the site traces to one of these rows. A value that no official page states is blank on the
site with the reason beside it. Nothing is inferred, rounded toward a nicer number, or filled
from a reseller.

Source ids match `data/3b45b513/sources.json`, which is published on the site at
`/counter-desk/review/sources/`.

---

## 1 · Official rules (read in full)

| # | What it says | Source | Verified |
|---|---|---|---|
| 1 | An ASIN is "a unique 10-character alphanumeric code assigned to every product listed in the Amazon store", and appears after `/dp/` in a product URL | [Understanding ASINs](https://sell.amazon.com/blog/what-is-an-asin) — Sell on Amazon, published 2025-06-04 (`S23`) | 2026-11-20 |
| 2 | "The links must properly use the special 'tagged' link formats we provide … ('Special Links')" | [Operating Agreement §1](https://affiliate-program.amazon.com/help/operating/agreement), updated 2025-10-15 (`S01`) | 2026-11-20 |
| 3 | The exact statement required on the site: "As an Amazon Associate I earn from qualifying purchases." | [Operating Agreement §5](https://affiliate-program.amazon.com/help/operating/agreement) (`S01`) | 2026-11-20 |
| 4 | "All Special Links must be accessed directly from your Site … you must include your Associates ID or 'tag' … as a parameter in the URL of each link you place on your Site to an Amazon Site" | [Program Policies 2(b)](https://affiliate-program.amazon.com/help/operating/policies), updated 2026-04-14 (`S02`) | 2026-11-20 |
| 5 | Price and availability: "your Site may only show prices and availability if: (a) we serve the link in which that price and availability data are displayed, or (b) you obtain Product pricing and availability data via Creators API or PA API" | Program Policies 2(b) (`S02`) | 2026-11-20 |
| 6 | Star ratings and customer reviews may not be displayed without an API-sourced link | Program Policies 6(t) (`S02`) | 2026-11-20 |
| 7 | "You will not cloak, hide, spoof, or otherwise obscure the URL of your Site containing Special Links (including by use of Redirecting Links)" | Program Policies 6(v) (`S02`) | 2026-11-20 |
| 8 | "You will not use a link shortening service, button, hyperlink or other ad placement in a manner that makes it unclear that you are linking to an Amazon Site" | Program Policies 6(w) (`S02`) | 2026-11-20 |
| 9 | No price tracking or alerting on the site | Program Policies 6(y) (`S02`) | 2026-11-20 |
| 10 | A session lasts 24 hours from the click, or 89 days if the item is added to the cart first; purchases are disqualified when links are "not correctly formatted" | Commission Income Statement 1 and 2(g) (`S03`) | 2026-11-20 |
| 11 | "You could say something like, 'I get commissions for purchases made through links in this post.'" — and the disclosure belongs close to the recommendation | [FTC Endorsement Guides Q&A, affiliate section](https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking) (`S05`) | 2026-11-20 |
| 12 | "such connection must be disclosed clearly and conspicuously" | [16 CFR 255.5](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255/section-255.5) (`S06`) | 2026-11-20 |
| 13 | "Mark links that are advertisements or paid placements (commonly called paid links) with the sponsored value." | [Qualify your outbound links](https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links), updated 2025-12-10 (`S04`) | 2026-11-20 |
| 14 | "Most food thermometers will give an accurate reading within 2 to 4 degrees F" | [FSIS Food Thermometers](https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/food-thermometers) (`S08`) | 2026-11-20 |

## 2 · USDA temperatures, row by row

Every number in the thermometer guide, checked against
[the Safe Minimum Internal Temperature Chart](https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/safe-temperature-chart)
(`S07`, page last updated 2025-04-14):

| Row on the chart | Site wording | Match |
|---|---|---|
| Beef, Pork, Veal and Lamb Steaks, Chops and Roasts — 145 °F, rest 3 minutes | same | ✅ |
| Ground Meats — 160 °F | same | ✅ |
| Ground Poultry — 165 °F | same | ✅ |
| All Poultry (breasts, whole bird, legs, thighs, wings, ground poultry, giblets, stuffing) — 165 °F | same | ✅ |
| Ham, fresh or smoked, uncooked — 145 °F, rest 3 minutes | same | ✅ |
| Fish & Shellfish — 145 °F | same | ✅ |
| Eggs — 160 °F; Leftovers — 165 °F; Casseroles — 165 °F | same | ✅ |
| Fully Cooked Ham (to reheat) — 140 °F / 165 °F | **not published** — the guide lists only the uncooked ham row, because the reheat row is a different question | ⚠️ omitted deliberately |

Probe placement, checked against the FSIS factsheet (`S08`): whole poultry — innermost thigh,
innermost wing, thickest breast, avoiding bone ✅; poultry parts — thickest area, avoiding bone ✅;
thin foods — insert through the side to the centre ✅.

## 3 · Product identity, observed on 2026-11-20

| # | Supplied | Chars | Resolved this pass | Earlier same day | Listing title (verbatim, first clause) | Source |
|---|---|---|---|---|---|---|
| 1 | `link.amazon/B04G1MEwY` | 9 | homepage | `/dp/B0CDY277D3` | "CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows…" | `S22`, `S09` |
| 2 | `link.amazon/B02NbDxp3` | 9 | `/dp/B09B7SB46R` | same | "Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven…" | `S22`, `S11` |
| 3 | `link.amazon/B00hJ57DV` | 9 | `/dp/B08DKYBTPH` | same | "Chefman Air Fryer 8 Qt \| TurboFry® 4-in-1 with 450°F Hi-Fry…" | `S22`, `S13` |
| 4 | `link.amazon/B0c8moW59` | 9 | homepage | `/dp/B0DHZTCNR5` | "ThermoMaven 1 Sec Professional Digital Meat Thermometer…" | `S22`, `S19` |
| 5 | `link.amazon/B0f3GKalj` | 9 | `/dp/B0DZFD6R9Z` | same | "CHEF iQ Sense \| Smart Wireless Meat Thermometer \| 3 Ultra-Thin Probes…" | `S22`, `S16` |

All five tokens are nine characters; every observed identifier is ten. Recorded as a format
observation (`CDF-01`), never as a verdict on the link.

## 4 · Manufacturer specifications, value by value

### Product 1 — Chefman TurboFry Touch 6 Qt dual-window (`RJ38-SQPF-3TDB-2W`)

| Value on the site | Manufacturer page (`S10`) |
|---|---|
| 6 qt / 5.67 L, two 3 qt baskets | "Capacity: 6 Qt / 5.67 L"; "Two independent 3-qt baskets" ✅ |
| 200–450 °F | "200–450°F / 95º-235ºC temperature range" ✅ |
| 1700 W / 120 V | "Power: 1700W/120V" ✅ |
| 13.38 × 11.81 × 10.63 in | "Dimensions: 13.38 in x 11.81 in x 10.63 in" ✅ |
| 13.3 lb / 6.03 kg | "Weight: 13.3 lbs / 6.03 kg" ✅ |
| cETL, 1-year assurance | "cETL approved with a 1-year Chefman® assurance" ✅ |
| Preset count — **blank** | The page lists named functions and no preset count; the listing states none. Withheld rather than counted ✅ |

### Product 2 — Emeril Lagasse 26 QT French Door (`4-00675-02A-VN`)

| Value on the site | Manufacturer page (`S12`) |
|---|---|
| 26 qt / 24.6 L, food for 4–6 | "26-Quart Capacity … preparing food for 4–6 people"; "24.6 Liters" ✅ |
| 16.9 × 15.8 × 14.8 in | "16.9\"D x 15.8\"W x 14.8\"H" ✅ |
| 120 V | "120 volts" ✅ |
| 1-year warranty | "1-Years Warranty" ✅ |
| Temperature range — **blank** | No numeric range on the product page ✅ |
| Wattage, weight — **blank** | Not stated on the product page ✅ |
| Preset count — **blank** | Page states "25 Cooking Pre-sets" *and* "24 one-touch cooking presets"; listing says 24 (`CDF-06`) ✅ |
| In-box accessories — **blank** | Description says 7; listing title says 6; grill plate sold separately (`CDF-06`) ✅ |

### Product 3 — Chefman TurboFry Touch 8 Qt (`RJ38-SQSS-8T`)

| Value on the site | Manufacturer page (`S14`) | Listing (`S13`) |
|---|---|---|
| 8 qt / 7.57 L | "Capacity: 8 Qt / 7.57 L" ✅ | "8 quarts" ✅ |
| 200–400 °F | "200–400°F" ✅ | "temperature range from 200-400°F" ✅ |
| 12.8 lb / 5.8 kg | "Weight: (8 Qt Model) 12.8 lbs / 5.8 kg" ✅ | not stated |
| 4 presets | "4 cooking presets" ✅ | "Four presets" ✅ |
| Top-rack dishwasher-safe basket and rack | "Top-rack dishwasher-safe basket" ✅ | "top rack dishwasher safe" ✅ |
| cETL, 1-year assurance | "cETL approved … 1-year Chefman® assurance" ✅ | "cETL approved" ✅ |
| Wattage — **blank** | **1700 W / 120 V** | **1000 W / 120 V** → conflict, `CDF-05` ✅ |
| Dimensions — **blank** | **15.4 × 12.6 × 13.5 in** | **12.75 × 13.5 × 10 in** → conflict, `CDF-05` ✅ |

Note on the earlier finding: the listing's model number `RJ38-SQSS-8T` is a real Chefman model,
not evidence of a different machine. The conflict is wattage and size, not identity (`CDF-09`).

### Product 4 — ThermoMaven F1 Stealth (`HT07`)

| Value on the site | Manufacturer page (`S20`) / manual (`S21`) |
|---|---|
| −58 to 572 °F | Manual: "Temperature Range \| -58 to 572 °F (-49.9 to 299.9°C)" ✅ |
| 1 second, thermocouple | Page: "Truly instant read in 1 second, thanks to Thermocouple sensor!" ✅ |
| ±0.5 °F / ±0.3 °C, NIST-certified per the manufacturer | Page: "NIST certified accurate to ±0.5℉/±0.3℃" ✅ |
| Probe 4.3 in × 0.14 in, tapering to 0.06 in | Manual: "4.3\" (L) × 0.14\" dia. (reduces to 0.06\" dia.)" ✅ |
| 0.83 × 1.61 in LED, rotates 180° | Manual: "0.83\" (H) × 1.61\" (W) LED, rotates 180°" ✅ |
| One AAA; 30-second sleep; wake by movement | Manual: "(1) × 1.5 volt AAA"; "Sleep Mode 30 seconds"; "Motion-sensing wake/sleep" ✅ |
| "100% waterproof design", **no IP number** | Page: "100% waterproof design"; no IP rating stated. The listing's IP67 is a marketplace claim and is **not** published ✅ |
| Leave-in — **blank** | Manual: "DO NOT leave the thermometer in the food whilst cooking"; "DO NOT leave the device in the oven, microwave, or dishwasher" ✅ |
| Lifetime warranty on registration within 30 days | Page: "Activate your Lifetime Warranty within 30 days after purchase" ✅ |
| Model `HT07` | Listing item-model field (`S19`) matches the manual's "Model: HT07" ✅ |

### Product 5 — CHEF iQ Sense, 3 probes (`B0DZFD6R9Z`)

| Value on the site | Manufacturer page (`S17`) / FAQ (`S18`) |
|---|---|
| 3 probes in this bundle | Page offers 1–4 probe configurations; the listing is the 3-probe bundle ✅ |
| 4 internal + 1 ambient sensor | Page feature list: "4 internal temperature sensors … 1 ambient temperature sensor" ✅ |
| Inserted probe 32–212 °F | Page: "Internal temp range of 32ºF to 212ºF"; FAQ: "max temperature for the portion of the probe inserted into the food is 212˚F" ✅ |
| Ambient 32–1,000 °F | Page: "Ambient temp range of 32ºF to 1,000ºF"; FAQ: Gen 3 ambient limit 1,000 °F ✅ |
| Probe 0.19 in × 4.75 in | Page: "Probe: 0.19\" thin, 4.75\" long" ✅ |
| Wi-Fi + Bluetooth, USB-C, hub speaker | Page: "Wi-Fi and Bluetooth® connectivity"; "charges via USB-C"; "Built-in speaker" ✅ |
| Probe dishwasher-safe, hub is not | FAQ: probe "is technically top-rack dishwasher safe"; "The CHEF iQ® Smart Hub is not waterproof" ✅ |
| Battery life — **blank** | Page: "70+ Hours of Battery"; FAQ: "Gen 3 probes will hold their charge for up to 60 hours" → conflict, `CDF-07` ✅ |
| Warranty — **blank** | Not stated on the product page or the FAQ ✅ |

## 5 · What was deliberately left blank, and why

| Field | State | Reason |
|---|---|---|
| Intended ASIN, official listing URL, confirmation date, confirmation source — all 5 products | blank | Filled only from an owner confirmation or an Associates record; neither was supplied (`CDF-02`) |
| Price, availability — every product | absent | Program Policies 2(b) permits neither without Amazon-served or API data (`S02`) |
| Star rating, review count — every product | absent | Program Policies 6(t) (`S02`) |
| 8 Qt wattage and dimensions | blank | Two official pages disagree, both figures recorded (`CDF-05`) |
| Emeril preset count and in-box list | blank | The maker contradicts itself and its listing (`CDF-06`) |
| CHEF iQ battery life | blank | Two figures on two official pages (`CDF-07`) |
| Traffic, clicks, orders, commission | absent | No endpoint, no authorised report; the ledger is empty (`CDF-10`, `CDF-11`) |

## 6 · Build and gate results on this branch

| Check | Command | Result |
|---|---|---|
| Generate the edition | `node tools/3b45b513/build.mjs` | 32 pages, 7 feed items, 31 sitemap URLs |
| Publishing gate | `node tools/3b45b513/gate.mjs` | **4,330 checks, 0 failed** |
| Gate unit tests | `node --test tools/3b45b513/gate.test.mjs` | **19 tests, 0 failed** (7 of them deliberately break a page) |
| Collector behaviour | `POST /collect` with valid, unknown, malformed and wrong-type bodies | 204 / 400 / 400 / 415; `GET` → 405; a disallowed property is stripped before storage |
| Root publication (another session's) | `npm run check` | 3,477 checks + 21 editorial pages, 0 failed |
| Disclosure gate across the domain | `node tools/disclosure-check.mjs` | 94 published pages, both statements above the fold, no price or rating text |
| Archive integrity | `node tools/archive-check.mjs` | 100 archived pages, 3,152 refs, 0 broken |
| Local route check | `python3 -m http.server` under a simulated `/Affil3/` mount | 11 representative routes, all 200 |

## 7 · Every external URL this edition links to

Official pages (linked from the product pages, guides and registers):

- https://affiliate-program.amazon.com/help/operating/agreement
- https://affiliate-program.amazon.com/help/operating/policies
- https://sell.amazon.com/blog/what-is-an-asin
- https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links
- https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking
- https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255/section-255.5
- https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/safe-temperature-chart
- https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/food-thermometers
- https://chefman.com/products/turbofry-touch-dual-window-air-fryer
- https://chefman.com/collections/air-fryers-1/products/turbofry-touch-air-fryer-1
- https://chefman.com/products/turbofry-8-qt-air-fryer-w-high-fry
- https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360
- https://chefiq.com/products/iq-sense
- https://chefiq.com/pages/new-iq-sense-faq
- https://www.thermomaven.com/products/f1-stealth
- https://cdn.shopify.com/s/files/1/0828/4726/9152/files/HT07_user_manual.pdf
- https://github.com/karagemop466-tech/Affil3/issues

Marketplace pages (recorded as observed evidence; only the tagged `/dp/` buy links are published
as links, and the `link.amazon` short links are never published as links):

- https://www.amazon.com/dp/B0CDY277D3 · /B09B7SB46R · /B08DKYBTPH · /B0DHZTCNR5 · /B0DZFD6R9Z
- https://link.amazon/B04G1MEwY · /B02NbDxp3 · /B00hJ57DV · /B0c8moW59 · /B0f3GKalj

## 8 · Errors made and corrected in this pass

| What | How it was caught | Fix |
|---|---|---|
| The capacity guide said no manufacturer publishes exterior dimensions for the 8 Qt unit | Re-reading S14 while writing the product page | Rewritten: all three maker pages publish exterior dimensions; none publishes interior ones |
| The cleanup guide attributed "flat frying tray" wording to S14 | Re-reading S14's specification block | Rewritten to what S14 actually says: "basket and rack, top-rack dishwasher safe" |
| A currency amount survived into a rendered page as an HTML comment | The gate caught it | Removed from the data file; the generator now throws instead of commenting |
| A `link.amazon` short link and an untagged Amazon citation appeared as real anchors | The gate caught both | Citation rendering refuses both: short links render as code, marketplace pages render as text |
| Canonical URLs were double-prefixed (`/Affil3/Affil3/…`) | Spot-checking the first render | Absolute-URL helper corrected; the gate now asserts it |
| Product 1's card used the front-page hero instead of a product illustration | Visual check of the render | Per-product illustration fields added to the register |

As an Amazon Associate I earn from qualifying purchases.
