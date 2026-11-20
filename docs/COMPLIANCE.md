# Compliance posture, and the line the machinery will not cross

This is the short version of what the primary sources permit. The clause numbers and wording were read
from Amazon's own pages, and from FTC / Google / GitHub documentation, on 2026-11-20; every row in
[`data/sources.json`](../data/sources.json) carries the URL that was actually fetched.

## What the licence forbids, as it affects software design

| Rule (primary source) | Consequence for this repo |
| --- | --- |
| Program Content may not be used with "data mining, robots, or similar data gathering and extraction tools" (IP License §1) | There is no crawler. `tools/` contains no HTTP client; `check_site.py` CHK-01 fails the build if one appears. |
| No using Creators API / PA API / Data Feeds "for the purpose of aggregating, analyzing, extracting, or repurposing" Product Advertising Content, nor for training or fine-tuning a model, without express prior written approval (IP License §2(e)) | No product-research database, no review-sentiment model, no price-history table. Any future analytical use needs written approval, which has not been requested (FLG-004). |
| No using Program Content or Special Links to "develop or improve large language or multimodal models, machine learning models or related technology" (IP License §1; Participation Requirements §5) | Content generation composes from this repo's own `data/` files only. Nothing trains on Amazon data. |
| Images may not be stored or cached; only a link to an image may be stored, for up to 24 h (IP License §2(h)) | The site uses original illustrations. There is no product photography, and the captions say so. |
| Other Product Advertising Content: cacheable up to 24 h, then it must be refreshed and re-displayed (§2(h)) | `program.json → data_shelf_life` records the rule; ASINs are the only product field storable indefinitely. |
| Prices/availability only from an Amazon-served link or API data (Participation Requirements 2(b)); reviews and star ratings only via API (§6(t)) | No price column, no rating column, anywhere. CHK-07 fails on a schema.org price/rating node or a currency figure on a reader-facing page. |
| Pricing display needs an adjacent date/time stamp plus the specified disclaimer; text Program Content needs the "CERTAIN CONTENT…" disclaimer (§2(i), §2(k)) | Both strings live in `program.json → associates.required_disclosures`; the footer prints the content disclaimer; CHK-08 requires it on any page displaying Amazon-sourced wording. |
| No framing, no pop-up/layer ads around Special Links (§6(n), §6(o)) | No embeds, no iframes, no interstitials. The disclosure is static layout furniture, not a modal. |
| No artificial generation of clicks or impressions, by robot or software (§6(s)) | `track.js` fires only on real activation or real visibility; `events.py` rejects non-schema payloads; CI never follows an outbound link. |
| No purchasing through your own Special Links, or asking others to (§6(u)) | The link test verifies the address bar and waits for a real reader. No test orders, ever. |
| No price tracking or price alerting functionality (§6(y)) | Rejected as a feature, not deferred. CHK-09 greps for the copy and for the markup. |
| Time-limited promotional mentions must be removed as soon as the promotion ends (§2(b)) | Seasonal rows carry `review_by` dates; CHK-10 fails when one passes. The site avoids deal copy entirely, because a static host cannot self-expire a sentence. |
| Special Links must use the assigned Associates ID as `tag=XXXXX-##`, be accessed directly from the site, and must not encourage bookmarking (§2(a)–(b)) | Links are generated only as `https://www.amazon.com/dp/<id>?tag=<tracking_id>`; CHK-04 validates the tag and its shape against the implied Associates ID. |
| Purchases via a Redirecting Link, or via an improperly formatted link, are disqualified (Commission Income Statement §2(e),(g)) | Short/intermediate hosts are a build error (CHK-06). Submitted short links stay in the register as inputs, never as hrefs. |
| No inaccurate, overbroad, deceptive or misleading claims about a Product (§2(b)) | Unconfirmed values stay `null` in the data and render as labelled blanks. CHK-03 blocks superlative / score / "we tested" strings lacking provenance. |
| Agent Terms: an Agent touching Program Content must identify itself as `Agent/[name]`, must not mimic human interaction, and must answer human-vs-machine prompts truthfully (IP License §4) | This project runs no Agent against Amazon. A future session that adds one must set that User-Agent and be reviewed. |
| Disclosure "clearly and prominently" (Operating Agreement §5) + the FTC's clear-and-conspicuous standard (16 CFR Part 255; Endorsement Guides FAQ) | Strip under the masthead on every page, repeated in the footer, note above the first affiliate link. CHK-02 requires it per page. |
| Violating §5 or the Program Policies is a material breach, and commissions may be stopped (Operating Agreement §§2, 6) | This is why the gate is in the deploy path rather than in a wiki page. |

## The two rules people most often get wrong here

1. **The shortener question is a presentation-and-tracking question.** §6(w) prohibits using a link
   shortening service "in a manner that makes it unclear that you are linking to an Amazon Site" — it
   does not ban short links as a format. Separately, Commission Income Statement §2(e) disqualifies
   purchases arriving via a Redirecting Link. Whether the supplied `link.amazon` strings are safe
   therefore depends on facts nobody could observe here (destination, tag survival, who owns the hop).
   That is why FLG-003 is *unresolved* rather than *invalid*.
2. **Compliance is a property of the build, not a page on the site.** A `/disclosure` page a visitor has
   to find is the pattern the FTC calls easy to avoid. The strip is layout furniture, so an editor cannot
   lose it and a generator cannot forget it.

## What remains genuinely uncertain (do not mark this "done")

* Whether any of the five identifiers resolve to a live listing at all (FLG-002, FLG-003).
* Whether the account holds API access, and what its grant covers (Q-04).
* Whether an analytical use of API data would ever be approved in writing. It has not been asked.
* Whether disclosure placement meets *your* risk appetite: the build implements the stricter reading (Q-08).
