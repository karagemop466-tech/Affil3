# RUNBOOK — in-account procedures

Everything in this file needs the enrolled Amazon Associates account. None of it can be done from
the repository, by a crawler, or by an agent, which is why the site ships with the corresponding
fields blank and flagged rather than estimated.

Order matters: **R1 → R2 → R3** is the minimum to move from "published site" to "site that can
earn". R4 onward is the loop that keeps it honest.

---

## R1. Confirm the tracking ID exists (1 minute) — closes Q-03, FLG-009

1. Associates Central → **Tools → Tracking IDs**.
2. Look for `shopnow047c-20`.
   - Present → write `tracking_id_state: "exists"` in `data/config.json`.
   - Absent → create it, or change `amazon.tracking_id` to an ID that exists. The build reads
     config, so every link on the site updates on the next build.
3. `python3 counterwise/tools/build.py && python3 counterwise/tools/gate.py`

**Why first:** every link on the site carries this string. If it does not exist, the traffic is
free for Amazon and worthless for us.

## R2. Prove one click reaches the reports (10 minutes) — closes FLG-002

1. Copy a product link from `counterwise/gear/index.html` (it looks like
   `https://www.amazon.com/dp/B0CDY277D3?tag=shopnow047c-20`).
2. Open it in a **clean browser profile** (no Amazon sign-in), browse one product, add to cart,
   remove it or abandon the cart. Do not buy.
3. Wait for the click report: Associates Central → **Reports → Earnings**, switch to the
   hourly view, confirm one click against the tracking ID.
4. When it appears, edit `data/products.json`: set that row's `observation.link_state` to
   `"in-account-confirmed"`. The gear table's "pending-test" label disappears on the next build.

If the click never shows up, stop publishing product links and diagnose the tag before scaling —
the site works fine with no links at all, and an uncredited site is the same thing with traffic.

## R3. Record product intent (5 minutes per row) — closes Q-01, FLG-001

For each of the five supplied links, in `data/products.json` under `intent`:

| Field | What to write |
| --- | --- |
| `intended_asin` | the ASIN you meant to promote, copied from your own link builder |
| `official_listing_url` | the URL as the program's tooling produced it |
| `confirmation_date` | today's date, in the account, not the date a fetch ran |
| `confirmed_via` | where you saw it, e.g. `SiteStripe → Get Link` or the Link Check tool |
| `confirmed_by` | who confirmed it |

Then set `intent.status` to `confirmed` and rebuild. `tools/gate.py` refuses an `intended_asin`
that is not 10 characters or that arrives without the three provenance fields — that is why the
fields stay blank until R3 is actually done.

**Do not** copy the observed `/dp/` identifier into `intended_asin`. The observed identifier is
evidence about where a link went on one date; intent is a statement about what you meant.

## R4. Decide the fate of the supplied `link.amazon` codes (20 minutes) — closes FLG-003

1. In the account, generate a link for one product **through SiteStripe** and compare it,
   parameter by parameter, with `https://link.amazon/<token>`.
2. Read **Help → Operating Agreement → Special Links** and the **Program Policies** page for the
   clauses our register quotes but could not read on the US copy: tag as a URL parameter, no
   link shortening that obscures the destination, additional original content next to product-list
   links, and the rule that Special Links point at Products.
3. Record the version date you saw in `data/sources.json` under SG-02/SG-03 and set
   `verification` to `read`.

Until R4 is done, the site keeps publishing rebuilt `/dp/?tag=` links and treats the supplied codes
as evidence in the tables, not as links to ship. That is a choice we can undo in one build; a
suspended account is not.

## R5. Product data feed (0 or 60 minutes) — unblocks S-04, FLG-007

Associates Central → **Tools → Product Advertising API**.

- If "Join or manage your account" is available, request access, create credentials, and store
  them in the deployment's secret store. Never in this repository, never in `data/`.
- Once `amazon.pa_api_access` is `confirmed`, the gate allows price, availability and rating
  fields to appear, and `data/config.json` may flip `publish_prices`/`publish_ratings` to true.
- If access is unavailable, leave everything as it is. "Amazon shows the live price at click
  time" is the answer we give readers, and it is honest.

## R6. Search Console (15 minutes) — closes Q-08, unblocks the cadence

1. `search.google.com/search-console` → Add property.
   - **URL-prefix** property: verify with the HTML meta tag option; paste the token into
     `data/config.json → search_console.verification_token` and rebuild. (The build only emits the
     tag when the token is non-empty, so an unverified state stays visible in the markup.)
   - **Domain** property: needs DNS control, which means the domain decision (S-15) first.
2. Submit `https://karagemop466-tech.github.io/Affil3/sitemap.xml`.
3. Check **Links → Top linked pages** weekly; that is the list that should replace the guessed
   topic queue after the review point in the cadence note.

## R7. Measurement, if you want it (1 hour) — closes FLG-010

1. Put `tools/collector.py` on any small host that can run one process (bind `0.0.0.0` behind
   your TLS terminator, or run it behind nginx and proxy `/e`).
2. Set `measurement.endpoint` in `data/config.json` to `https://metrics.<your-domain>` and
   `measurement.status` to `deployed`; rebuild. The front end starts sending; the page attribute
   and config must agree or the gate fails the build.
3. Decide reader capture at the same time (`S-10`). Until an endpoint exists the signup form is a
   no-op that says so on the page — never a black hole for an address.
4. Update `counterwise/privacy/` text in the same commit; the gate checks that a live endpoint and a
   collection claim stay consistent.

## R8. The refresh loop (every 90 days, or on a schedule)

```bash
python3 counterwise/tools/resolve_links.py            # re-follow the supplied links; rewrites links.json + observation only
python3 counterwise/tools/build.py && python3 counterwise/tools/gate.py
git add -A && git commit -m "refresh: re-capture listing observations" && git push origin <branch>
```

`tools/resolve_links.py` touches `observation` fields only, and prints what it could not verify.
Anything older than 90 days gets a visible "captured on" date rather than a quiet delete, because
the dangerous state for a page like this is not being wrong on day one — it is being right on day
one and stale on day four hundred.

## R9. Publishing (mechanical, already wired)

```bash
git pull --rebase origin <branch>
python3 counterwise/tools/build.py           # refuses to finish if the gate fails
git add -A && git commit && git push origin <branch>
gh pr create --base main ...  →  gh pr merge <n> --squash
```

The `build` workflow runs on every push to `main` and on pull requests as a second opinion. Pages
serves `main:/docs` with `counterwise/.nojekyll` present, so GitHub does not try to build the output with
Jekyll. **Never hand-edit `counterwise/`** — the manifest hash check (R06) fails any build whose HTML was
not generated from the data on disk.

## R10. Reading the board (weekly, 10 minutes)

`counterwise/suggestions/index.html` is generated from `data/suggestions.json`. To decide a row, fill its
`review_decision` with the choice and the date, then rebuild; the board shows your answer verbatim.
Nine rows are waiting on that. The `summary_counts` field must match the board — the gate checks
the arithmetic, so a stale tally fails the build instead of quietly misleading you.
