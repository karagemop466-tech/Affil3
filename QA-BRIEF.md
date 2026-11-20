# Questions, answers, and the gaps between them

A decision brief. Read this before changing anything on the site.

**Rule for this document:** if a question has no official source behind it, the answer is
*no answer yet* — followed by what would produce one.

---

## Part 1 — What we know, with the source

| # | Question | Answer | Source |
|---|---|---|---|
| 1 | What product is link 1? | CHEFMAN TurboFry Touch 6 Qt. Dual-Window Air Fryer, model RJ38-SQPF-3TDB-2W | [chefman.com](https://chefman.com/products/turbofry-touch-dual-window-air-fryer) |
| 2 | What product is link 2? | Emeril Lagasse French Door AirFryer 360 Toaster Oven Combo, 26 QT, 4-00675-02A-VN | [emerileveryday.com](https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360) |
| 3 | What product is link 3? | CHEFMAN TurboFry Touch Stainless-Steel Air Fryer, 8 Qt, RJ38-SQSS-8T | [chefman.com](https://chefman.com/collections/air-fryers-1/products/turbofry-touch-air-fryer-1) |
| 4 | What product is link 5? | CHEF iQ Sense Smart Wireless Meat Thermometer, 3-probe Gen3 bundle | [chefiq.com](https://chefiq.com/products/iq-sense) |
| 5 | What product is link 4? | ThermoMaven F1 Ace instant-read thermometer, `B0DHZTCNR5`. A first fetch hit an Amazon checkout interstitial; retries resolved. The bare code returns no catalog results because it is a 9-character short-link token, not an ASIN | [thermomaven.com](https://www.thermomaven.com/products/f1-ace) |
| 6 | Do the supplied links carry our tag? | No. All resolve without a `tag=` parameter | [Program Policies](https://affiliate-program.amazon.com/help/operating/policies) |
| 7 | What exact disclosure wording is required? | "As an Amazon Associate I earn from qualifying purchases." | [Operating Agreement §5](https://affiliate-program.amazon.com/help/operating/agreement) |
| 8 | Can the site show prices? | Only if Amazon serves the link, or via Creators/PA API. Neither applies, so: no prices. | [Program Policies](https://affiliate-program.amazon.com/help/operating/policies) |
| 9 | Can the site show star ratings? | Only via PA API. So: no ratings. | [Program Policies](https://affiliate-program.amazon.com/help/operating/policies) |
| 10 | Can the site do price alerts? | No. Explicitly prohibited. | [Program Policies](https://affiliate-program.amazon.com/help/operating/policies) |
| 11 | When must the affiliate disclosure appear? | Where readers will see it, near the link, and not only at the end. | [FTC Endorsement Guides](https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking) |
| 12 | Is the grill plate included with the Emeril oven? | No. Manufacturer: "no longer included." | [Emeril Everyday accessory page](https://www.emerileveryday.com/products/parts_and_accesories_airfryers_ovens_french_door_fafo_series_french_door_airfryer_360_grill_plate__fafo-001) |
| 13 | What is the Chef iQ probe's max temperature? | 212 °F for the inserted portion; 1,000 °F is the ambient sensor | [CHEF iQ FAQ](https://chefiq.com/pages/new-iq-sense-faq) |
| 14 | Is there any first-party traffic or sales data? | No. Repository began as a one-line README. | — |
| 15 | Are both builds passing every gate? | Yes. 30 pages and 3,322 checks at the root with 0 failures; `/editorial/` 21 pages PASS; disclosure gate PASS on all 30 published pages; archive gate PASS | this repo |

## Part 2 — What we do not know, and what would settle it

| # | Unknown | Why it blocks a decision | What settles it |
|---|---|---|---|
| 16 | Is `shopnow047c-20` a live tracking ID on the account? | If not, every URL is wrong in a way no repo check can see | Associates Central → Account Settings → Tracking IDs |
| 17 | Does the account have API access? | Decides whether prices and ratings can ever appear | Associates Central credentials page |
| 18 | What is the commission rate for this category today? | Any revenue model needs it | Rate card, signed in |
| 19 | Which marketplace is the audience in? | All five products are 120 V, US-spec | State it; the site currently assumes amazon.com |
| 20 | Does the account meet the activity requirement to stay enrolled? | A dormant account makes a new site pointless | Export the payment report; read the current eligibility clause |
| 21 | Who is the author? | Readers and quality raters weigh who is claiming | A name, a bio, and a method statement |
| 22 | Where does the analytics endpoint live, and who reads it? | Measurement with no owner is a liability | Name the endpoint and the reader, or leave it off |
| 23 | What is the privacy policy for the five events? | Required by Program Policies once anything is recorded | Publish it naming endpoint, fields, retention |
| 24 | Is 24 or 25 the Emeril preset count, and how many accessories ship? | | Email manufacturer support (`FLG-001`) |
| 25 | Which is right for the Chefman 8 Qt: 1700 W or 1000 W, and which case size? | | Email CHEFMAN support (`FLG-002`) |
| 26 | What is in the Emeril box today? | | Ask for the current list by model number (`FLG-006`) |
| 27 | Is the site listed as an approved channel in the Associates account? | An unlisted site can be rejected after you send traffic to it | Add it in the account before promoting |
| 28 | Is the site's permanent home github.io/Affil3? | Moving later costs redirects and ranking | Decide before content volume grows |
| 29 | Which of the five products should lead? | Sets the whole front page | Currently P1, on editorial grounds — overrule it if you disagree |
| 30 | What separates this site from the ten air fryer sites already ranking? | Without an answer, guides compete on volume and lose | One sentence a competitor could not also write |

## Part 3 — Questions this project should not try to answer

These look like data problems and are actually credibility traps. Each one is a reason the site
deliberately shows nothing.

1. **"How much traffic will this get?"** Nobody can answer that before the site is indexed. A number
   here would be a guess wearing a percentage sign.
2. **"What is the conversion rate?"** There is no click history. Any rate quoted is borrowed from an
   unrelated site.
3. **"Which product converts best?"** Requires first-party data. The register ranks on specification
   fit, not on sales.
4. **"Is this the best air fryer?"** Nothing here was tested. "Best" would be an unsubstantiated claim
   under the Associates agreement and the FTC guides alike.

## Part 4 — The order to fix things in

1. **Re-issue one link with the tag and test it.** Until this happens, everything else is decoration.
2. **Confirm the tracking ID is live and the site is a listed channel.** Two screens in Associates Central.
3. **Chase the four maker-versus-listing conflicts.** Each needs a manufacturer reply, not more reading (`FLG-002`, `FLG-006`, `FLG-023`, `FLG-008`).
4. **Verify in Search Console and submit the sitemap.** This starts the measurement clock.
5. **Decide the reader (SG-10).** Every piece of copy downstream depends on it.
6. **Set the analytics endpoint and name its owner.** Then the five events mean something.
7. **Publish the next guide on the two-week cadence (SG-11).** Add it to sitemap and feed in the same commit.
8. **Re-verify all specs quarterly** and update the access dates. Specs decay; the dates are the tell.

## Part 5 — What to read before you decide anything

- [`docs/flagged/`](docs/flagged/index.html) — the seven irregularities
- [`docs/questions/`](docs/questions/index.html) — all 30 questions with owners
- [`docs/suggestions/`](docs/suggestions/index.html) — 14 proposals, each with its cost
- [`docs/disclosure/`](docs/disclosure/index.html) — the quoted policy basis for every rule
- [`docs/sources/`](docs/sources/index.html) — every source, its tier, and when it was read
