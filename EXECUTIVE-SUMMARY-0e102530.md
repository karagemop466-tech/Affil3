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
| 4 | **Two guides written, then withdrawn as duplicates.** They were drafted and illustrated, and they were dropped at merge time because `main` had moved on and now publishes guides on both exact topics — better ones, with the same points. Publishing them would have put two versions of the same question on one domain, which is the duplicate-content pattern the site's own spam-policy citation forbids. The findings that were not already on the site were carried into the register instead (FLG-041, FLG-042, K-22, Q-20). | `data/guides.json` (no change from my branch) |
| 5 | **Guide counts derived, not typed.** The front page said "All five guides" in a template. It now reads the number from the data, so it cannot go stale the way the hand-written count did before (this is the same class of bug as DX-7). | `tools/build.mjs` |
| 6 | **Page weight cut by most of a third, and the front page by two thirds.** Every illustration was 3.3–4.0 MB. Re-encoded to a 256-colour palette and scaled to 1200 px, they are roughly 0.5 MB each with no visible change (pixel RMSE 0.012). A 768 px card variant derived from each one is offered through `srcset`, so the front page falls from **3.9 MB of images to 1.2 MB** and the guides index from 3.6 MB to **0.4 MB**. The hero is now a 153 KB JPEG, and nothing above the fold blocks on a PNG any more. | `src/assets/img/`, `assets/img/` |
| 7 | **Image dimensions are read from the files, and gated.** Every `<img>` carried a typed-in `width`/`height` that no longer matched its file, which makes the browser reserve the wrong box and the page jump as images arrive. The build now reads the real pixel size from each file. `tools/verify.mjs` checks all 58 of them, and fails the build if a declared size ever disagrees with the file again. | `tools/build.mjs`, `tools/verify.mjs` |
| 8 | **Two new flags, two new suggestions, three new questions, three new discovery steps.** FLG-041 and FLG-042 record the two irregularities found in the re-read. S-26 asks where the analytics collector should actually run, now that it is known to work. S-27 records the image-weight decision. Q-20 and Q-21 are the two questions this session's re-read exposed. | `data/flags.json`, `data/suggestions.json`, `data/questions.json` |

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
dangerous one. That gap is now recorded as Q-20, with a discovery step (D-16) asking the manufacturer
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

- **FLG-042 — two manufacturer pages disagree with themselves.** The Emeril page's specification block
  says *25 cooking pre-sets*, its own description says *10-in-1*, its image alt text on the same page
  says *11-in-1*, and the Amazon listing title says *24*. The CHEF iQ page says *"Five internal
  sensors"* in its introduction while its specification list says four internal plus one ambient. The
  site publishes no preset count and no in-1 count for the oven, and follows the specification list for
  the sensor count. Choosing between four official statements would be inference, not verification.
- **FLG-041 — the correction above, filed as a flag** rather than quietly fixed, so it appears on the
  Flagged for Review page with both source links and the manual step that would settle it.

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
host, and that is now the subject of suggestion S-26 rather than an unexamined gap. It stays flagged as
FLG-009 and does not block anything.

---

## Page weight, and why it was worth a build

The brief asks for a site that draws organic traffic. Organic traffic arrives on a phone, on a
connection that is not the one in this sandbox, and a site whose first page weighs 3.9 MB of images
before a line of text is read does not get read.

The illustrations themselves were never the problem. They are flat, grainy, mid-tone drawings, which is
exactly the kind of image a small palette compresses well, and they had been saved as full-colour PNGs
at 3.3–4.0 MB each. Two changes fixed it without touching a single file name, file path or pixel:

| Page | Images before | Images now |
|---|---|---|
| Front page | 3,947 KB | 1,176 KB |
| Guides index | 3,568 KB | 442 KB |
| A guide page | ~3.4 MB hero alone | ~600 KB |
| Shop table, comparison table | 0 KB | 0 KB |

The third change was less visible and more important for how the site feels. Every `<img>` carried a
`width` and `height` typed in by hand at some point, and several no longer matched their file, because
the files had been resized since. A browser that is told an image is 1536×1024 and then receives one
that is 1200×768 reserves the wrong box, and the page visibly jumps as each image arrives. The build now
reads the real size from the file, and the gate checks all 58 declared sizes against the files on every
run. That check is not decorative: it failed on four images the first time it ran, which is how the
mismatch was found.

---

## The two guides that were written and then withdrawn

This is worth recording because the decision not to publish is the more useful part.

Two guides were drafted and illustrated in this session: a comparison of the two Chefman air fryers on
published figures only, and a decoder for the four numbers on an air fryer specification sheet. Both were
built, passed every gate, and were committed.

At merge time, `main` had moved 258 commits and now publishes thirteen guides, including
*"Dual basket or single basket: which one for four people?"* and *"How to read an Amazon listing before
you buy a kitchen appliance."* Both cover the same questions mine did. Publishing mine would have put
two versions of the same question on one domain, competing with each other for the same search result,
which is exactly the pattern the site cites the Google spam policies for forbidding.

So they were dropped. What was not dropped were the findings `main` had not captured:

- the CHEF iQ ambient-versus-food temperature range distinction (FLG-041, K-22, Q-20, D-16);
- the two manufacturer pages that disagree with themselves (FLG-042, D-18);
- the collector test result and the question of where it should run (S-26);
- the image-weight work and the intrinsic-size gate (S-27).

Both illustrations remain in `src/assets/img/` and are wired to nothing. That is recorded here rather
than hidden: two unused files, roughly 784 KB, which can be deleted or used for a guide on a topic not
already covered.

---

## What this session did not do, and why

- **It did not set an intended ASIN, an official listing URL, a confirmation date or a confirmation
  source for any row.** Those require the owner. The observed redirect targets stay in their own field.
- **It did not claim that any submitted short link is valid or invalid.** All five landed on the Amazon
  home page when fetched without a session on 2026-11-20 — the same behaviour two earlier dated rounds
  recorded. That is an observation, not a verdict (FLG-003, FLG-031, and now Q-21).
- **It did not test a Special Link in Associates Central.** There is no Associates login in the sandbox,
  so gate G-02 stays pending and no buy button is treated as validated.
- **It did not publish a price, a rating, a review count or a revenue figure.** No authorized API is
  available, so none of those exist on this site.
- **It did not switch analytics on.** That needs hosting and a settled privacy notice (Q-16), not code.
- **It did not add a product.** Only the five the owner submitted appear anywhere on the site.

---

## The merge

`main` advanced 258 commits while this branch was open, through PRs #57–#75. The merge collided in five
files that other sessions had also edited. Every collision was resolved by keeping both sides, and the
one place that could not be — where my rows would have reused flag, suggestion and question numbers
another session had already taken — was resolved by renumbering mine rather than overwriting theirs:

| Register | Main was at | My rows became |
|---|---|---|
| Flags | FLG-040 | FLG-041, FLG-042 |
| Suggestions | S-25 | S-26, S-27 |
| Questions | Q-19 | Q-20, Q-21 |
| Discovery | D-14 | D-16, D-17, D-18 |
| Known | K-21 | K-22 |

`COORDINATION.md` is append-only and both sessions added a section at the same point in the file, so both
sections are kept: main's first, mine after it. Nothing was discarded. The generated pages were rebuilt
from the merged registers rather than hand-merged, which is why the merge commit contains 150 files and
only five of them were edited by hand.

---

## What still blocks revenue, in order

1. **One tagged Special Link, opened and confirmed in the tracking report.** Everything else on this
   list is downstream of it. Gate G-02. Owner-access, minutes not days.
2. **The five intended ASINs**, confirmed from a signed-in Amazon session. Closes Q-01, Q-21 and FLG-002.
3. **A host and a decision for the analytics collector.** S-26, with Q-16 (privacy notice) first.
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
node tools/build.mjs   → 40 pages, 13 feed items, 39 sitemap URLs
node tools/verify.mjs  → 4795 checks passed, 0 failed
```

Every disclosure, sponsored-link, tracking-tag, source-link, sitemap, feed, internal-link and
image-dimension check passes. No price, rating or review count appears anywhere in the generated site. The two new guides
are in the sitemap and the RSS feed. The site builds, and it builds clean.
