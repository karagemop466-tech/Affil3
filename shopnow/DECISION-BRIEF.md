# Decision brief — what must be answered before anything else is worth doing

**Date:** 2026-11-20 · **Companion to:** `/decisions/` and `/suggestions/` on the live site, and
`register/questions.json` (22 rows) / `register/suggestions.json` (22 rows).

This document exists because most of what the brief asks for — automate research, model
commissions, optimise campaigns, pick trending topics — **cannot be decided on the information that
exists in this repository.** Not because it is hard, but because the inputs are absent. The honest
move is to say precisely which inputs, which question each one answers, and the cheapest way to get
it. That is what follows.

Everything here is separated into three kinds of statement, and they should not be confused:

- **Known** — observed in this session against an official source, with a date.
- **Missing** — required for a decision and not obtainable from here.
- **Chosen** — a judgement this project made under uncertainty, recorded so it can be overruled.

---

## 1. The six answers that gate everything else

| # | Question | Why it gates | Cheapest way to close it | Who |
|---|---|---|---|---|
| **Q-01** | Are the four listings your short links currently resolve to the products you intend us to promote? | Every product page, category, cluster and comparison inherits its identity from this. A redirect can be retargeted; a 9-character token cannot be an identifier. | Copy the ten-character ASIN from Associates Central → Links → Special Links into `register/products.json:intended_asin`. | Owner · ~10 min |
| **Q-02** | What is behind `link.amazon/B0c8moW59`? | One of five products has no identity. Three fetch attempts returned an Amazon anti-bot interstitial; it is withheld from the shop floor rather than guessed. | Open the link in a normal browser, paste the final URL. | Owner · ~2 min |
| **Q-06** | Does tracking ID `shopnow047c-20` exist on the account, and is it attached to a site? | Format is valid and every generated link carries it, but an ID that does not exist means zero attribution and zero earnings on perfectly good pages. | Account Settings → Tracking IDs. One screenshot into `register/links.json`. | Owner · ~3 min |
| **Q-07** | Is a production URL registered as a Site? | Approval and attribution are per registered URL. Today's host is a `github.io` subpath, which is a preview, not a publication. | Account Settings → Site Settings → add the exact URL. | Owner · ~5 min |
| **Q-11** | Do we adopt "checked, not hyped" as the position, or wait for API access and become a conventional review site? | This decides the masthead, every guide's structure, and whether the site's whole voice is a constraint or a strategy. Today it is a strategy forced by a missing credential. | A sentence from you. If "wait", the editorial queue pauses; if "adopt", nothing changes — it already ships. | Owner · now |
| **Q-13** | Who signs off on a guide before it goes live — a named human, the desk byline, or no one? | Authorship is simultaneously an E-E-A-T lever, a legal exposure question, and the gate the brief asks for on the non-automatable part. | Name a person and an email, or say "keep the desk byline". Do not lend a real person's name without their agreement. | Owner · now |

**Read those six as a set.** Q-01/Q-02 fix *what* is sold, Q-06/Q-07 fix *whether it can earn*, and
Q-11/Q-13 fix *how it is allowed to speak*. Any work scheduled before them is work likely to be
redone.

## 2. Known — verified in this session, with the tier stated honestly

| Statement | Tier | Source |
|---|---|---|
| "As an Amazon Associate I earn from qualifying purchases." required, clear and prominent | **verbatim**, s.5 | [Operating Agreement](https://affiliate-program.amazon.com/help/operating/agreement), page dated 2025-10-15 |
| Links must use Amazon's tagged "Special Links" formats | **verbatim**, s.1 | same |
| Implied endorsement is prohibited; s.5 breach is a material breach | **verbatim**, s.5–6 | same |
| No representation about expected traffic or income | **verbatim**, s.4 | same |
| Material connection must be clear and conspicuous; a linked "DISCLOSURE" button is insufficient | **excerpt** | [FTC Endorsement Guides FAQ](https://consumer.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking) |
| Poultry 165°F; ground meats 160°F; whole cuts 145°F + 3-min rest | **excerpt** | [USDA FSIS](https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/steps-keep-food-safe) |
| `rel="sponsored"` marks affiliate outbound links | **excerpt** | [Google Search Central](https://developers.google.com/search/docs/essentials/spam-policies) |
| All four resolved listings exist, with these titles, on 2026-11-20 | **primary observation** | the listing URLs in `register/products.json` |

Tier definitions are on the site's methodology page. `verbatim` = fetched and quoted here.
`excerpt` = official-domain text that would not load as a full page in this environment. There is no
tier for "assumed".

## 3. Missing — and what each gap actually blocks

### 3a. Data we are not permitted to obtain here
| Gap | Blocks | Consequence today |
|---|---|---|
| Catalog API credentials (Creators API / PA-API 5.0) | price display, rating display, review mining, availability checks, automated refresh, commission lookup | No numbers on product pages. Comparison tables carry criteria, not values. **This is the largest single constraint on the brief's ambition.** |
| The API eligibility threshold itself (3 vs 10 qualifying sales per 30 days; sources conflict) | planning the sequence "get data → make sales → keep data" | Recorded as **unresolved** (S07) rather than asserted. One screen in Associates Central resolves it. |
| Program Policies body text (price/caching wording) | any decision that hinges on the exact permitted refresh window | The site takes the strict reading: nothing to violate. |
| Category commission schedule | any EPC or "commission potential" model | `commission_rate` is null on every row. No rate is quoted from a third-party table. |

### 3b. Context only you have
| Gap | Blocks | Suggested way to discover it |
|---|---|---|
| Intended audience (first-time buyer / upgrader / household-scale) | guide titles, price bands, which products to add next | Pick one for the first six guides. Narrow beats accurate here. |
| Budget for data and hosting | whether the collector, a domain, an SEO dataset, or product purchase are live options | One number. Under ~20/month, the current build is already the right build. |
| Whether anyone can physically test the products | the entire "review" content track, original photography, and any claim of hands-on authority | Yes/no plus a rough cost per product. If yes, this outranks every on-page optimisation on the suggestions board. |
| Brand and domain ownership | name, feed title, JSON-LD publisher, trust signal | Send the domain, or say "keep ShopNow 047" (it was derived from your tracking ID because the repo had no brand asset). |
| Stopping rule / success number | whether to fund cadence or a single pillar page | Set it **after** 28 days of Search Console data, not before — anything earlier is a guess. |

### 3c. Signals that do not exist yet
| Gap | Blocks | How to get it |
|---|---|---|
| Search Console query data | replacing hypothesis with measured demand for topic selection | Verify the day the domain exists. Free, and its value is strictly a function of how early the clock starts. |
| Any click data | whether the collector gets self-hosted, deferred, or replaced by Plausible | Deploy `scripts/collect.mjs` on any box you own; point the site at it. One env value. |
| Zero-result internal searches | the cheapest missing-topic detector available to a static site | Already instrumented; needs a collector to be visible. |
| Baseline traffic | every "will this work" question | No substitute. 60 days of publishing or nothing. |

## 4. Chosen — judgements made under uncertainty, open to being overruled

1. **Suppress prices, ratings and availability rather than display stale ones.** Chosen because the
   permission is credential-gated and the wording could not be read in full. Reversible the day API
   access exists (SG-14 path c).
2. **Publish the unresolved link as a register row with no page.** Chosen over guessing a category
   from the brief's air-fryer framing. Closes with Q-02.
3. **Do not call the supplied short links invalid.** Observed final URLs carried no `tag=` — an
   observation about this environment's view, not proof about attribution (FLG-003). Chosen wording:
   "compliance status unresolved".
4. **Adopt the anti-hype position as the brand** rather than pretend to a lab. Forced by the missing
   data, and defensible as a strategy: it is the only positioning available that does not require
   anything this project lacks.
5. **Ship the campaign ledger empty.** Populating it with industry averages was rejected on
   principle (SG-26): a seeded baseline becomes the plan.
6. **Zero dependencies, committed output.** Chosen so the gate cannot be bypassed by a broken
   install, and so Pages serves exactly what CI reviewed.
7. **Search Console before analytics vendor.** Verification costs nothing and informs everything;
   the vendor decision (SG-28) can wait a month without losing data CI could not have collected
   anyway.

## 5. What I would do in the first two weeks, in order

1. **Answer Q-01 and Q-02** (≈12 minutes, a browser each). Everything downstream inherits product
   identity; this is the only step that cannot be delegated to a machine.
2. **Register a domain and add it to Site Settings** (Q-06/Q-07). Change `base_url` in
   `register/site.json`, rebuild, done. This single move unblocks approval, trust and attribution at
   once — it is the highest-value item on the entire board and it is nearly free.
3. **Run the one-link test on P01 only.** Protocol is in `register/links.json`. Confirm destination
   *and* that a session appears in Reports. Scale to P02–P05 only after it does. Do not scale links
   before one link is proven; that is how a broken format becomes twenty pages.
4. **Verify Search Console the same day.** Then wait, deliberately. The brief's "measure before
   automating optimisation" is mostly the discipline of not acting on 90 days of data you do not
   have.
5. **Publish two guides a week for six weeks** from the existing queue (`npm run new-guide`).
   Register-driven: sitemap, feed, index and search all update on build.
6. **Re-cut the next six topics from the query report**, and only then reopen SG-14 (prices),
   SG-28 (measurement) and SG-32 (niche expansion). If zero-result searches or query data show pull
   toward an adjacent category, that is the moment breadth stops being a content farm.

## 6. What will not be answered here, on purpose

No search volume. No trend claim. No revenue projection. No conversion benchmark. No "top 5". No
ranking of the four products against each other on data we did not collect. Each of those is one
sentence away from making this site look more finished and simultaneously making every number on it
uncheckable — which is the specific failure mode the brief asked this project to avoid.

If a decision needs one of those figures to proceed, the correct next action is the discovery step
in the table above, not a plausible estimate.
