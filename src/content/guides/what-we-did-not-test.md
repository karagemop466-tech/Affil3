---
title: What we did not test, and why that sentence is on every page
desc: The house rules of this site, written down where readers can hold us to them — including the part where our own five product links are not clickable yet.
date: 2026-12-07
kicker: Method
cluster: null
author: Counter Tested
status: published
sources: S01, S06, S07, S08, S10, S12, S16, S20
---

Every guide on this site ends with a version of the same line: *we have not tested this*. It is not modesty and it is not a legal disclaimer. It is the only claim we can make about these five appliances without inventing something, and a site that will not tell you what it did not check has not earned the right to tell you what to buy.

Here are the rules we run the site on. They are on the repo too, as a build gate, so they are not a promise we can quietly break.

## 1. If we cannot source it, the cell is blank

Prices, star ratings, review counts, "serves 6" claims. Two reasons, and the second is the binding one. Amazon's rules allow prices and availability on our site only when the data is served through their link or pulled from their API under licence, and customer ratings may only appear through that same licensed path. Independently, publishing a number we cannot date-stamp and defend would be exactly the misleading product claim the programme prohibits. So there is no price column here and there never will be a stale one.

## 2. We do not scrape, cache or warehouse product data

No spiders on listing pages, no spreadsheets of spec pulls, no "sentiment analysis" run over other people's reviews. The licence excludes robots and data-mining tools from what we may do with their content, and separately forbids using that content to aggregate, analyse or train a model without written approval. So the automation on this site points at our own files: it validates data, builds pages, checks the paperwork and refuses to publish when the paperwork is missing. That is a smaller ambition than "AI-powered everything" and a much more durable one.

## 3. No fake live-ness

Five product links were supplied to us in a short-link form that our build environment could not resolve. We are not declaring those links invalid — that is an open question we are asking a human to settle inside the enrolled account. What we refuse to do is dress an unresolved identifier in a "Buy now" button. Until someone confirms the destination and that the tracking tag survives, the card shows the identifier, shows what is missing, and links to the status page instead of to a checkout.

## 4. We cannot buy them ourselves to test the tracking

There is a rule that surprises people: an associate may not purchase through their own links, or ask friends to. So the "just buy one and check" trick that a normal affiliate might use to verify a link is not available to us. The link test checks what the address bar shows and what the report says the next day. Nothing more, and no staged orders.

## 5. Disclosure goes at the top, not in a footer

The programme requires one clear sentence — *As an Amazon Associate I earn from qualifying purchases* — and the FTC's position is effectively stricter: a connection readers would not expect has to be hard to miss and close to the recommendation. So the strip is above the fold on every page, repeated in the footer, and the links themselves are marked as sponsored in the markup.

## 6. An empty results table is a correct state

We publish a campaign ledger. Today it has no rows in it, because the only honest contents are clicks counted on our own pages and orders transcribed from the reports inside our account, and neither has happened yet. A site that shows you a revenue forecast before it has any data has sold you a number. The gate refuses to render a conversion score with nothing behind it.

:::note What would change these rules
Real test time on a unit. That is the one input that unlocks the strongest version of this site: same meals, same batches, dimensions taken with a tape, cleanup timed, published with the failures in the same table. If you want us to run that on one of these five listings, tell us which — we would rather do one appliance properly than five with adjectives.
:::

## Where to check our work

- [Source register](source-register.html) — every assertion, with the official page it came from and the date we read it.
- [Flagged for review](flagged-for-review.html) — the ten things we could not resolve, including the short-link question.
- [Open questions](questions.html) — what has to be known before a decision here is a reasonable one.
- [Compliance gate](compliance-gate.html) — the thirteen checks the build runs, and what happens when one fails.
