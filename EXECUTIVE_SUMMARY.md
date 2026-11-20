# Executive summary

**Project:** Counter Tested — an Amazon Associates affiliate site and the publishing machinery behind it.
**State:** v0 published to GitHub Pages, links gated, evidence complete, products unverified.
**Date:** 2026-11-20 · **Session:** `S-A3-01` · **Branch:** `arena/be9ed869-affil3` → `main`
**Full version, on the site:** <https://karagemop466-tech.github.io/Affil3/executive-summary.html>

---

## 1. What was asked, and what was actually built

The brief asked for an AI-powered affiliate platform: automated product research, trend and conversion
detection, pricing/review/competition analysis, generated SEO articles, managed affiliate links, click and
conversion tracking, continuous campaign optimisation — across five supplied product links, with a tracking
ID, compliance with Amazon Associates policy, and a repository that documents every claim with an official
source.

What exists now is the compliant subset of that sentence, plus the parts that were missing entirely:

| Brief item | Delivered | Honest status |
| --- | --- | --- |
| Organised register of requirements, sources and findings | `data/sources.json` (28 rows), `docs/`, COORDINATION board, 4 site registers | Complete. The repo started empty: there was no prior register to read, so each one was reconstructed and labelled as such (FLG-001). |
| A site that reads like a shop, not an audit | Front page, shelf, 5 guides, 2 topic clusters, per-product records | Complete. Reader pages and audit pages are separated, joined by one nav group + footer. |
| Findable: one site to index, a reason to rank | Static site, self-canonicals, sitemap.xml, RSS feed, robots.txt, Article + BreadcrumbList JSON-LD, question-shaped titles | Complete technically. No domain authority yet — nothing can shortcut that. |
| Trustworthy machinery | Deterministic builder, 13-check publish gate in CI, intake/ledger/event tools, drift check | Complete, and demonstrated: sabotage tests make the gate fail correctly. |
| Product-intent confirmation records | Per-link record: intended id, char count, derived candidate URL, confirmation date/method/source, observed redirect in a **separate** field | Complete as a structure; **0 of 5 confirmed**, because the destinations could not be resolved from this environment. |
| Replace ambiguous links with validated Special Links | Links are generated only as `https://www.amazon.com/dp/<id>?tag=shopnow047c-20` with `rel="sponsored"`, and only after per-product confirmation; supplied short links retained as inputs | Policy-complete and gated. The one-link test needs a human in the enrolled account (S02 in the brief). |
| Click and conversion measurement | Cookieless collector, 5 defined events with schema + validator, self-hosted endpoint, empty provenance-checked ledger | Complete code, **zero data**: Pages cannot run a process, and inventing numbers was refused. |
| Disclosure above the fold | Strip under the masthead on every page, footer repeat, plain-language note above the first affiliate link; enforced by CHK-02 | Complete. |
| Sponsored marking of outbound links | Every affiliate anchor: `rel="sponsored nofollow noopener"`; mislabelling a citation as sponsored is also a build failure | Complete. |
| Evidence-based iteration / campaign ledger | Ledger with a fixed schema that refuses rows lacking a named first-party report and date; no conversion score, no forecast | Complete and empty, which is the correct state at zero traffic. |
| Compliance gate in the publishing workflow | CHK-01…CHK-13 in `tools/check_site.py`, wired into the deploy job so a violation stops publication | Complete — this is the load-bearing piece. |
| "Automate product research" | **Deliberately not built**, and documented why | The licence forbids it in the form described. See §3. |

## 2. What the sources actually say (the finding that reshaped the brief)

Read from Amazon's own pages (Operating Agreement updated 2025-10-15; Program Policies updated 2026-04-14):

* Program Content **may not be used to develop or improve machine-learning or multimodal models**, and the
  APIs/Data Feeds **may not be used to aggregate, analyse, extract or repurpose** product content without
  **express prior written approval** (IP License §1, §2(e)).
* **Data mining and robots are outside the licence** entirely (IP License §1), so "scrape Amazon for
  pricing and reviews" is not a risky implementation of the plan — it is a different plan.
* **Images may not be stored or cached at all**; other product data may be cached for **24 hours** and must
  then be refreshed; ASINs may be kept indefinitely (IP License §2(h)).
* **Prices, availability, star ratings and review content** may only appear from an Amazon-served link or
  from an API call under licence, with a date/time stamp and a specific disclaimer (2(b), 6(t), 2(i), 2(k)).
* **Price tracking and price-alert functionality is prohibited** (6(y)); expired promotional mentions must
  be removed (2(b)) — which is why this site carries no deal content at all.
* **You may not purchase through your own links**, and **clicks/impressions may not be artificially
  generated** (6(u), 6(s)) — so the usual "test purchase" verification trick and any synthetic traffic are
  both off the table, and the link test is a destination check plus a next-day report check.
* Links must be **direct, correctly formatted, and tagged `XXXXX-##`**; purchases arriving via an
  intermediate redirect or a malformed link are **disqualified** (2(a)–(b); Commission Income Statement 2(e),(g)).
* A **2026 addition** imposes **Agent Terms** (IP License §4): software acting on someone's behalf must
  name itself `Agent/[name]` in its User-Agent and must not mimic human interaction.
* Violating §5 or the Program Policies is a **material breach**, and Amazon may stop paying commissions.
* Account survival has a clock: **3 qualifying sales within 180 days**, or the application can be withdrawn
  and the account is not reinstatable.

**Conclusion adopted:** automate everything on our side of the line (validation, generation, gating,
scheduling, reporting, integrity) and put a human gate in front of everything across it. The result is less
magical than the brief's phrasing and far more likely to still exist in a year.

## 3. What is unverified — and it is the commercial part

* **The five product links.** All are `https://link.amazon/<9 characters>`. There was no network route to
  that host from the build environment (one attempt at the derived `/dp/` URL also failed), so **no
  destination, title, category, price, availability, rating or commission is known for any of them.** Per
  instruction the links are *not* declared invalid — their compliance status is unresolved (FLG-003), and the
  two clauses that bear on it are quoted rather than interpreted.
* Because of that, the site ships **zero clickable affiliate links**. Cards show the identifier, what is
  missing, and the five-minute path to turning it on. Publishing "Buy now" over an unresolved identifier
  would put a reader one click from a 404 and put the account one step from unattributable traffic.
* **The account is unknown**: whether `shopnow047c-20` exists on it, whether this URL is registered, whether
  the 180-day window has started, and whether API access exists. All are `null` in `data/program.json`,
  because nothing official was available to fill them (FLG-007).
* **There is no demand evidence at all**: no traffic history, no backlinks, no indexed queries. Any revenue
  or ranking promise would be invented, so none is made (FLG-008).

## 4. Six decisions that gate everything else

| # | Decision | Cost of the answer | Blocks |
| --- | --- | --- | --- |
| Q-01 | Application date + qualifying-sale count | 2 minutes in the account | whether there is any runway left; sets the whole sequence |
| Q-02 | Does `shopnow047c-20` exist, and is this URL registered | 3 minutes | whether any click can ever attribute |
| Q-03 | The five-link test (destination, tag survival, listing title) | ~5 min each | the shelf becoming a shop; FLG-002/003/005 |
| Q-04 | Is there API access, and what does the grant cover | 5 minutes to check, longer to apply | whether prices/ratings/specs may ever be displayed |
| Q-09 | Which niche do we actually own | one hour of honest competitive reading | the editorial plan, the cluster set, the competitive frame |
| Q-11 / SG-14 | Stay on Pages, or run one small process elsewhere | a domain, ~1–2 h setup | real click measurement, any form or capture, anything server-side |

`data/suggestions.json` holds 28 numbered suggestions with cost, risk, evidence and an empty decision field;
`data/questions.json` holds the questions with the discovery method for each; `data/flags.json` holds the 10
open items. The site renders all three from the same files, so approving a row is a data edit plus a rebuild.

## 5. Economics, stated without a forecast

Revenue here is commission on qualifying purchases, from a shelf of products whose listings are unconfirmed,
on a domain with no authority, in a category where the incumbents have testing labs. The honest read: **the
probability that this specific configuration earns meaningful commission in its first quarter is low**, and
the two levers that change that answer are not on this site — they are (a) resolving the links and getting
indexed, and (b) owning a narrow, genuinely useful angle (counter footprint and cleanup cost) rather than
competing on "best air fryer". Commissions per sale are small; the volume needed for a meaningful monthly
figure is large; and per policy, price data cannot be cached to sweeten a table.

What is defensible about the current state: the site is *correct*, the machinery is *trustworthy*, the
compliance posture is *documented with citations*, and the path to commerce is *one short protocol* rather
than a redesign.

## 6. Immediate next actions, in order

1. **Q-01 → Q-02 → Q-03.** One browser session inside the enrolled account settles four of the six decisions
   above. Follow `docs/LINK_TEST_PROTOCOL.md`; record each result with `tools/product_intake.py confirm`.
2. **Flip the gate per product** as each link confirms (`link_state`, then `allow_live_links`) and rebuild.
3. **Verify Search Console** (SG-29), submit `sitemap.xml`, then hold the cadence: 2 guides/week for 6 weeks.
4. **Decide Q-11** before writing another measurement feature; deploy `tools/collect_server.py` or accept
   "no click data" explicitly.
5. **Approve or reject the 28 suggestions** — especially SG-01 (licence boundary), SG-04 (niche), SG-10/SG-12
   (measurement), SG-16 (cadence), SG-30 (reader capture: proposed *deferred*).
6. **Ask Amazon in writing** whether an analytical use of API data would be approved, and record the reply in
   the register. Do not implement it first.

## 7. Verification method (what "no hallucinations" was made to mean here)

Facts were taken only from documents fetched in the session and recorded with URL + section + access date in
`data/sources.json`. Where a page could not be fetched, its row says so (`primary-snippet`,
`reference-only`) and no displayed claim rests on it. Product attributes were left `null` rather than
inferred; a `needs review` page publishes every unresolved item with its source links. `tools/check_site.py`
re-verifies the reader-facing consequences of those rules on every build, and CI fails the deploy when they
break. Sabotage tests (removing the disclosure; a mistagged link; a shortener href) were run and each
produced a failing check.
