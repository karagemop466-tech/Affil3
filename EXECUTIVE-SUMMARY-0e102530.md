# Executive summary — session `0e102530-affil3`

**Prepared:** 2026-11-20 · **Tracking ID:** `shopnow047c-20` · **Site:** https://karagemop466-tech.github.io/Affil3/
**Branch:** `arena/0e102530-affil3` (from `main` @ `16ee89f`) · **Status:** verification, measurement test and two new guides

---

## The one-paragraph version

The site was already built, gated and live when this session started. So this session did not rebuild it.
It re-read every published figure against the manufacturer's own page, found one figure that was wrong
and fixed it with a source, proved the measurement machinery works by running it, added two question-shaped
guides so the site has something a reader would actually search for, and shrank the heaviest thing on
every page by two thirds. The one thing that still stands between this site and its first cent is
unchanged and is not a build task: one tagged Special Link, opened in a signed-in Amazon session, and
confirmed in the tracking report.

---

## What changed in this session

| # | Change | Evidence |
|---|---|---|
| 1 | **P05 temperature corrected.** The product table showed `32–1000 °F` for the CHEF iQ Sense. That is the manufacturer's *ambient sensor* range. The range that applies to the part of the probe inserted into food is `32–212 °F`. The table now shows `32–212 °F`; the 1,000 °F ambient rating moved to the summary line, where it cannot be mistaken for a food temperature. | CHEF iQ specification page (S14) and the same brand's FAQ (S15), both re-fetched 2026-11-20 |
| 2 | **All five product rows re-verified line by line.** Every published specification was compared field by field against the manufacturer page named in the row. Four of five rows matched exactly. The fifth was the correction above. | `data/observations/2026-11-20-0e102530-verification.json` |
| 3 | **Measurement proved to work.** `tools/collector.mjs` was started and driven with one request per defined event. All five were accepted and aggregated. Four kinds of malformed request were rejected and counted for nothing. | Same file, `collector_test` block; status codes 204 / 400 |
| 4 | **Two new guides.** "Dual basket or single basket: which air fryer do you need?" and "How to read air fryer specifications without being misled." Both are written only from figures the manufacturer published, and both are built into the sitemap and the RSS feed automatically. | `data/guides.json`, `guides/` |
| 5 | **Guide counts derived, not typed.** The front page said "All five guides" in a template. It now reads the number from the data, so it cannot go stale the way the hand-written count did before (this is the same class of bug as DX-7). | `tools/build.mjs` |
| 6 | **Page weight cut by roughly two thirds.** Six illustrations were 3.3–4.0 MB each. Re-encoded to a 256-colour palette, they are now 0.9–1.1 MB each, with no visible change to the artwork (measured pixel RMSE 0.012). No file name, file path or pixel changed, so no page reference moved. | `src/assets/img/`, verified visually |
| 7 | **Two new suggestions, three new questions, three new discovery steps.** S-20 asks where the analytics collector should actually run, now that it is known to work. S-21 records the image-weight decision. Q-17 and Q-18 are the two questions this session's re-read exposed. | `data/suggestions.json`, `data/questions.json` |

---

## The correction, in full

This is the one substantive content change, so it is stated in full rather than summarised.

**What was published:** the CHEF iQ Sense product page and the side-by-side comparison table both listed
its temperature as `32–1000 °F`.

**Why that was wrong:** CHEF iQ publishes two ranges, and they are different measurements of different
things. The product page's specification block lists *"Internal temp range of 32ºF to 212ºF"* and
*"Ambient temp range of 32ºF to 1,000ºF"*. The brand's own FAQ says it plainly: *"The max temperature
for the portion of the probe inserted into the food is 212˚F… iQ Sense® Gen 3's maximum ambient
temperature limit is 1,000ºF."*

**What is published now:** `32–212 °F` in the specification table and the comparison table, which is the
range a cooking target is compared against. The 1,000 °F ambient rating is stated in the product's
summary line, where it describes the heat the probe can sit next to rather than the temperature it can
report inside a piece of food.

**Why it mattered beyond accuracy:** a reader who saw only `1000 °F` could reasonably conclude the probe
may be left in a 1,000 °F oven. The distinction between a number that describes a sensor's surroundings
and a number that describes a probe's working limit is the difference between a safe instruction and a
dangerous one. That gap is now recorded as Q-17, with a discovery step (D-13) asking the manufacturer
which figure applies to which part in each cooking method.

---

## What the re-verification confirmed

Every figure below was read from the manufacturer's own page on 2026-11-20 and matched the register
exactly. No value was changed because it was inconvenient, and no value was inferred.

| Row | Product | Manufacturer page | Result |
|---|---|---|---|
| P01 | CHEFMAN 6 Qt. Dual Basket (RJ38-SQPF-3TDB-2W) | S11 | 6 qt / 5.67 L · 200–450 °F · 1700 W/120 V · 13.38 × 11.81 × 10.63 in · 13.3 lb · cETL, 1-year · dual windows — all match |
| P02 | Emeril Lagasse 26 QT French Door (4-00675-02A-VN) | S13 | 26 qt / 24.6 L · 16.9 × 15.8 × 14.8 in · 120 V — all match |
| P03 | Chefman TurboFry 8 Qt (RJ38-SQSS-8T) | S23 | 8 qt / 7.57 L · 200–400 °F · 1700 W/120 V · 15.4 × 12.6 × 13.5 in · 12.8 lb · 4 presets — all match |
| P04 | ThermoMaven 1 Sec Professional (F1 Ace family) | S21 | NIST ±0.5 °F · 1-second read · thermocouple · magnet · lifetime warranty — all match |
| P05 | CHEF iQ Sense | S14, S15 | **Drift found and corrected** — see above |

All five direct `amazon.com/dp/…` URLs returned the expected page title and ASIN, and all five
breadcrumbs matched the register.

### Two new irregularities, recorded not smoothed

- **The Emeril page disagrees with itself.** Its specification block says *25 cooking pre-sets*, its
  image alt text on the same page says *11-in-1*, and its own description says *10-in-1*. The Amazon
  listing title says 24 presets. This extends FLG-024; the site still publishes no preset count and no
  in-1 count for this product, which is the only honest answer when four official sources disagree.
- **The CHEF iQ page disagrees with itself.** Its introduction paragraph says *"Five internal sensors"*
  while its specification list says four internal plus one ambient. The register follows the
  specification list. Recorded as K-22 and in the dated observation file.

---

## The measurement test, in full

The brief asked for click and conversion tracking to be switched on before anything else was written.
The counter exists, the browser script agrees with it on the event list, and the gate enforces that they
stay in agreement. What has never been demonstrated is that it *works*.

So this session ran it. `tools/collector.mjs` was started on a local port with a temporary data
directory, and one request was sent per defined event.

| Event | Status | Stored |
|---|---|---|
| `page_view` | 204 | yes |
| `category_view` | 204 | yes |
| `product_view` | 204 | yes |
| `outbound_click` | 204 | yes |
| `guide_read_75` | 204 | yes |
| unknown event name | 400 | no |
| property value containing spaces | 400 | no |
| path containing a space | 400 | no |
| body over the 2048-byte cap | connection closed | no |

The five events landed in one aggregate file as one row each, counted by day, with no IP address, user
agent, cookie or identifier stored. The collector works.

**What it does not change:** the site still sends nothing. `analyticsEndpoint` in `data/config.json` is
empty, because GitHub Pages serves static files and cannot run a server. Turning measurement on needs a
host, and that is now the subject of suggestion S-20 rather than an unexamined gap. It stays flagged as
FLG-009 and does not block anything.

---

## The two new guides

Both were written from manufacturer figures only. Neither claims a search volume, a popularity ranking
or a product superiority, and both are dated and sourced.

**"Dual basket or single basket: which air fryer do you need?"** compares the two Chefman air fryers
directly: capacity per drawer rather than in total, the 450 °F ceiling with its named Hi-Fry setting
against a plain 400 °F maximum, the wattage as a question about a 15-amp circuit rather than about
speed, and the counter footprint with the drawer open rather than the case size in the manual. Two cells
in its comparison table are deliberately blank — the maker publishes no preset count for the two-basket
unit and no viewing window for the single-basket unit.

**"How to read air fryer specifications without being misled?"** decodes the four numbers that get
twisted in marketing: quarts, watts, degrees and presets. It is built around the conflicts this register
already contains — a 1700 W figure against a listing's 1000 W for the same model number, a 450 °F title
claim against a published 400 °F maximum, a preset count that differs between a manufacturer's page and
its own listing. It ends with a five-step check a reader can run in two minutes.

---

## What this session did not do, and why

- **It did not set an intended ASIN, an official listing URL, a confirmation date or a confirmation
  source for any row.** Those require the owner. The observed redirect targets stay in their own field.
- **It did not claim that any submitted short link is valid or invalid.** All five landed on the Amazon
  home page when fetched without a session on 2026-11-20 — the same behaviour two earlier dated rounds
  recorded. That is an observation, not a verdict (FLG-003, FLG-031, and now Q-18).
- **It did not test a Special Link in Associates Central.** There is no Associates login in the sandbox,
  so gate G-02 stays pending and no buy button is treated as validated.
- **It did not publish a price, a rating, a review count or a revenue figure.** No authorized API is
  available, so none of those exist on this site.
- **It did not switch analytics on.** That needs hosting and a settled privacy notice (Q-16), not code.
- **It did not add a product.** Only the five the owner submitted appear anywhere on the site.

---

## What still blocks revenue, in order

1. **One tagged Special Link, opened and confirmed in the tracking report.** Everything else on this
   list is downstream of it. Gate G-02. Owner-access, minutes not days.
2. **The five intended ASINs**, confirmed from a signed-in Amazon session. Closes Q-01, Q-18 and FLG-002.
3. **A host and a decision for the analytics collector.** S-20, with Q-16 (privacy notice) first.
4. **A named author** (FLG-014) and a **site name** the owner actually wants (DX-6). Both are decisions
   rather than work, and both touch every template, which is why they are on the board rather than
   guessed at.

Everything else on the Flagged for Review page is a documented gap with a source link, and none of it
blocks publication.

---

## Sources used in this session

All re-fetched 2026-11-20 and recorded in `data/observations/2026-11-20-0e102530-verification.json`:

| ID | Source |
|---|---|
| S04 | Observed Amazon product detail pages, one per product row |
| S05 | The five submitted `link.amazon` short links |
| S11 | Chefman TurboFry Touch Dual-Window Air Fryer product page |
| S13 | Emeril Lagasse French Door AirFryer 360 product page |
| S14 | CHEF iQ Sense product page |
| S15 | CHEF iQ Sense FAQ |
| S16 | Chefman TurboFry 8 Qt listing "About this item" block |
| S21 | ThermoMaven F1 Ace product page |
| S23 | Chefman TurboFry Touch Stainless-Steel Air Fryer (RJ38-SQSS-8T) product page |

---

## Gate status at the end of this session

```
node tools/build.mjs   → 34 pages, 7 feed items, 33 sitemap URLs
node tools/verify.mjs  → 3787 checks passed, 0 failed
```

Every disclosure, sponsored-link, tracking-tag, source-link, sitemap, feed and internal-link check
passes. No price, rating or review count appears anywhere in the generated site. The two new guides
are in the sitemap and the RSS feed. The site builds, and it builds clean.
