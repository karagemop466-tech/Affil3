---
title: How we decide what to publish
slug: methodology
description: The four rules this site runs on, the automated gate that enforces them, and the exact list of things we could not verify.
---

## Four rules

**1. A number needs a source, or it does not appear.**
Every figure on this site resolves to a row in the [source register](/sources/): an official page, fetched or excerpted, with an access date and the exact quote. Four of the eleven source rows are marked unresolved. That is not a gap in the work; it is the work telling you where it stopped.

**2. We do not claim to have tested anything.**
There is no test kitchen behind this site. No product has been measured, weighed, cooked in, or disassembled by us. First-person testing claims, lab claims, and hands-on framing do not appear here, and a build check rejects them by name. When a guide says "check X", it means you should check X, not that we did.

**3. Prices and ratings belong to Amazon, at the moment of purchase.**
Amazon's Program Policies permit a site to show price and availability only when the data comes from an Amazon-served link or its catalog API, with a 24-hour refresh ceiling. We have no API access - and the eligibility gate for it sits behind the sales that access would help produce. So we publish no monetary figure at all, and a build check fails if one slips in.

**4. The sponsor relationship is stated where you are reading, not on a page you have to go find.**
The disclosure sentence sits under the masthead on every page and again in the footer, in text, not behind a button. That placement is deliberate: the FTC has said a hyperlinked "DISCLOSURE" control is not clear and conspicuous, because most people will not click it.

## What a machine enforces

Compliance that depends on someone remembering is compliance that fails on a busy day. So the checks are code, they run on every build, and CI blocks the merge:

| Gate | What it catches |
|---|---|
| Disclosure present | any page missing the required sentence above the fold or in the footer |
| Sponsored marking | any commerce link without `rel="sponsored nofollow"` and a visible Sponsored label |
| Tracking tag | any Amazon link whose `tag=` does not match the site's tracking ID |
| Price guard | any currency pattern reaching the published site |
| Program Content guard | any reference to Amazon's image CDN |
| Claim guard | banned-phrase list, including implied testing and implied endorsement |
| Verification guard | a field published as fact with no source row behind it |
| Link integrity | any broken internal link, and any page missing from the sitemap or feed |

The list is the file [scripts/checks.mjs](https://github.com/karagemop466-tech/Affil3/blob/main/scripts/checks.mjs). If you want to argue with a rule, the argument is with a script, not with a person's judgement on a bad day.

## How a product gets listed

A product is only published when its listing has been *resolved*: we follow the supplied link, record the destination, and store the intended identifier and the observed destination in **separate fields** so a reader can see which is which. Where a link would not resolve - as with one of our five - the product has no page and no card, and the register says UNRESOLVED.

We did not guess a brand, a category, or a price to fill that row. Five products came in; four are on the shop floor; one is in the dashboard with a blank where the name should be. [Full ledger.](/dashboard/)

## What "verified" means here, precisely

- **verbatim** - we fetched the official page in this session and copied the text.
- **excerpt** - official-domain text returned by a search index; the page itself would not load in this environment. Enough to publish a citation, not enough to quote at length.
- **unresolved** - sources conflict, or the page could not be reached. Nothing was adopted. The row stays, with the conflict described.

No row on this site uses a fourth category. There is no "probably", and nothing is filled in because the blank looked bad.

## Reader-facing honesty page

If we get a fact wrong, the register should show it before you have to email us. That is what [Flagged for review](/flagged-for-review/) is for: ten open items, each with the source link, the exact owner action that would close it, and what we withheld from the site as a result.
