# Executive summary — ShopNow 047

**Prepared:** 2026-11-20 · **Repository:** `karagemop466-tech/Affil3` · **Branch merged:** `arena/59aebafb-affil3` → `main`
**Tracking ID:** `shopnow047c-20` · **Marketplace:** Amazon.com (US)

---

## 1. What was asked, in one paragraph

Build an automated Amazon-associates publishing platform: product research, trending and
high-converting product identification, price/review/competition/commission analysis, SEO-optimised
articles, comparisons and buying guides, published and tracked affiliate links, campaign
optimisation — with automation and scale first-class and Associates compliance treated as a
gate rather than an afterthought. On top of that, turn the register into a shop a buyer can act
on, make it findable, add measurement before optimisation, and provide a reviewable suggestion
board plus a list of the questions that must be answered before a decision is defensible.

## 2. The finding that shapes everything else

**The catalog is not actually identified.** The five links supplied are
`https://link.amazon/<token>` where each token is **9 characters**. Amazon ASINs are 10. The tokens
are redirector handles, not identifiers:

| # | Submitted token | Length | Resolved to | Product |
|---|---|---|---|---|
| P01 | `B04G1MEwY` | 9 | `B0CDY277D3` | Chefman 6 Quart Dual Basket Air Fryer Oven |
| P02 | `B02NbDxp3` | 9 | `B09B7SB46R` | Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven |
| P03 | `B00hJ57DV` | 9 | `B08DKYBTPH` | Chefman Air Fryer 8 Qt TurboFry 4-in-1 |
| P04 | `B0c8moW59` | 9 | **unresolved** | — three attempts returned an Amazon anti-bot interstitial |
| P05 | `B0f3GKalj` | 9 | `B0DZFD6R9Z` | CHEF iQ Sense smart wireless meat thermometer |

Four of five resolved on 2026-11-20; the resolved ASINs share no characters with the submitted
tokens. Nobody has confirmed that "whatever the short link serves today" is the intended product.
That is the first blocking question (Q-01), and it is why the register stores *intended* and
*observed* identifiers in **separate fields** and never merges them.

## 3. What is real, verified against official sources

| Item | Status | Source |
|---|---|---|
| Disclosure sentence "As an Amazon Associate I earn from qualifying purchases." required, clear and prominent | **verbatim**, Agreement s.5 | [Operating Agreement](https://affiliate-program.amazon.com/help/operating/agreement) (page dated 2025-10-15) |
| Links must use Amazon's "tagged" Special Link formats | **verbatim**, s.1 | same |
| No implying Amazon endorsement; s.5/s.6 violation = material breach | **verbatim**, s.5–6 | same |
| No representation of expected traffic or income | **verbatim**, s.4 | same |
| Material connection must be clear and conspicuous; a "DISCLOSURE" button is not enough | **excerpt** | [FTC Endorsement Guides FAQ](https://consumer.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking) |
| Poultry 165°F; ground meat 160°F; whole cuts 145°F + 3-minute rest | **excerpt** | [USDA FSIS](https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/steps-keep-food-safe) |
| Price/availability only via Amazon-served link or API, 24h refresh ceiling | **unresolved** (policy body would not load) | [Program Policies](https://affiliate-program.amazon.com/help/operating/policies) |
| API eligibility threshold (3 vs 10 qualifying sales / 30 days) | **unresolved** (sources conflict) | [PA-API docs](https://webservices.amazon.com/paapi5/documentation/) |
| Tracking ID exists on the account; site registered to it | **unverifiable here** (login-walled) | Associates Central |

Eleven source rows: 3 verbatim, 4 excerpt, 4 unresolved. **Zero values inferred.** The four
unresolved rows are published as unresolved, on the site, not parked in a private note.

## 4. Decisions taken, and why

1. **No prices, ratings, review counts or availability anywhere on the site.** The permission to
   display them is gated behind API credentials this project does not have, and the policy wording
   could not be read in full. So the strict reading wins and a build check rejects any currency
   figure reaching the output. Cost: less "shop feel". Benefit: no stale claim can exist.
2. **Short links are not called invalid.** Observed final URLs carried no `tag=` parameter — an
   observation about what this environment saw, not proof about attribution. The site therefore
   publishes links generated in the documented `/dp/<ASIN>?tag=` form and leaves FLG-003 open.
3. **P04 gets no product page.** A card would require inventing a brand, a category or an image.
   It appears in the register as UNRESOLVED and nowhere else.
4. **No hands-on testing language, ever.** Nothing was tested. Guides are written as *what to
   check and how to read it*, and each one states the absence of testing inside the article.
5. **Original imagery only.** Amazon catalog images are Program Content; the licensed path is the
   API or an Amazon-served widget. Three generated editorial illustrations are captioned as
   illustration, so the site never implies product photography it did not license.
6. **Brand derived, and labelled as derived.** "ShopNow 047" comes from the tracking ID because
   the repo had no brand asset. It is one string in `register/site.json`.
7. **Campaign ledger ships empty.** The brief's own instruction: populate only from authorised
   first-party reports. An "industry average" seed was explicitly rejected (SG-26).

## 5. What was built

**Site** — 23 published pages generated from the register: publication front page; 6 question-shaped
guides; product pages for the 4 resolved listings; 4 decision-shape clusters; a 7-row shape
comparison; methodology, about, disclosure, privacy; and the machinery set (dashboard, source
register, suggestions, open questions, executive summary, flagged-for-review); client-side search
with a static index; RSS feed, sitemap, robots, humans.txt; JSON-LD (WebSite, Article, Product,
CollectionPage, ItemList, BreadcrumbList, Dataset) on every page.

**Machinery** — `scripts/build.mjs` (zero dependencies; every page, feed and sitemap entry
generated), `scripts/checks.mjs` (11 automated gates, exit-1 on failure), `scripts/collect.mjs`
(self-hosted NDJSON event collector), `docs/assets/track.js` (5 events, no cookies, no
fingerprinting, no third party), GitHub Actions CI that builds, checks, and proves `docs/` is not
stale.

**Data** — 11 source rows, 5 product-intent records, 22 suggestion rows, 22 open questions, 10
flags, 12 compliance controls, 5 link candidates with a one-link test protocol, and a typed
ingest schema (`register/schema/research_snapshot.schema.json`) that refuses a 9-character ASIN —
the exact failure mode of the supplied links.

**Measurement** — five events defined with fields, privacy notes and conversion roles; collector
contract specified; ledger schema with integrity rules and read-time floors (a ratio is not shown
until its denominator clears 50–100).

## 6. Where the model stops short of the ambition

The brief describes a self-optimising revenue engine. What can honestly exist today is the
publishing and compliance half, plus the *interfaces* for the research and optimisation half. The
gap is not effort, it is credentials:

- **No catalog API** → no automated product research, price analysis, review mining, or
  commission modelling. The eligibility gate sits behind the sales the data would enable. This is
  the central constraint and it is reported rather than routed around.
- **No registered site** → no attribution, therefore no clicks or conversions to count.
- **No traffic yet** → therefore no query data, therefore topic selection is a stated hypothesis,
  not a measured decision. Search Console verification is the cheapest way to change that
  (SG-29), and it is free.

Anyone who claims this site will earn a given amount is guessing; Amazon's own s.4 says no
representation about traffic or income is made. No forecast appears anywhere here.

## 7. The six answers that unblock the first real move

| | Question | Closes |
|---|---|---|
| Q-01 | Are the four resolved listings the products you intend? | identity of every page |
| Q-02 | What is behind `B0c8moW59`? | 1 of 5 products |
| Q-06 | Does tracking ID `shopnow047c-20` exist on the account? | every outbound link |
| Q-07 | Is a production URL registered as a Site? | monetisation, and FLG-005 |
| Q-11 | Adopt "checked, not hyped" as the positioning? | voice, titles, hero, about |
| Q-13 | Who signs off before a guide goes live? | authorship, E-E-A-T, FLG-006 |

## 8. Risk register

| Risk | Likelihood | Impact | Mitigation shipped |
|---|---|---|---|
| Stale or unsupported price claim | — | account | impossible by construction; CI rejects currency |
| Missing disclosure on some page | low | account | C-01 fails the build above the fold or in the footer |
| Untagged / unlabelled commerce link | low | revenue + account | C-02 checks `tag=` and `rel` on every Amazon anchor |
| Fabricated product data | — | trust | C-07 rejects a populated volatile field while S02/S07 are unresolved |
| Fabricated testing claim | — | legal + account | C-04 banned-phrase list, including implied endorsement |
| Thin/duplicate pages on a young site | medium | ranking | 1 category, 6 guides, no brand pages (SG-32); no orphans enforced (C-11) |
| github.io subpath treated as low trust | high | ranking + approval | SG-17: custom domain; flagged FLG-005 |
| Parallel sessions overwriting `docs/` | medium | build | `docs/` is generated; conflict resolves by rebuild, not by hand (FLG-009) |

## 9. Next 14 days, in order

1. Answer Q-01/Q-02 (ten minutes, a browser each) → register gains owner-confirmed identities.
2. Register a domain and add it in Associates Central (Q-06/Q-07) → set `base_url`, rebuild, done.
3. Run the one-link test protocol on P01 only → if attribution shows, scale to P02–P05.
4. Verify Search Console the day the domain exists (SG-29) → 28 days of query data starts accruing.
5. Publish two guides a week from the existing register-driven queue (SG-08).
6. Re-cut the next topics from measured queries, and only then decide on prices (SG-14), the
   collector (SG-28), and any niche expansion (SG-32).

## 10. How to review this in five minutes

`/flagged-for-review/` — the ten items and what each one withheld.
`/sources/` — eleven rows with tiers and quotes.
`/suggestions/` — the board, 12 implemented, 8 waiting on you.
`/decisions/` — 22 questions, 6 blocking.
`/dashboard/` — everything above, as tables, generated from the same JSON.

Every statement in this file is either an observation recorded during this session with a date, a
quotation from an official page with a link, or a decision written down with its reason. Nothing
here is inferred, and the places where information ran out are named rather than filled.
