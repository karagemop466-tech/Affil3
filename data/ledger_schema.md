# Campaign ledger — schema and rules

This file is `data/ledger.csv`. It ships with a header row and **no data rows**, on purpose.

## Why it is empty

A ledger is only worth keeping if every number in it can be traced back to a report
that Amazon authorised us to see. Right now there is no such report, so there is no
number to put in it. Writing a plausible number would be worse than an empty file,
because an empty file is obviously empty and a plausible number is not.

The columns are defined now so that the first real row can be added without a
schema change and without anyone having to guess what a column meant.

## Column definitions

| Column | Type | Meaning | Who is allowed to fill it |
| --- | --- | --- | --- |
| `entry_date` | date | The day the row was written into the ledger. | Anyone with write access. |
| `period_start` | date | First day of the reporting period the row covers. | Derived from the source report. |
| `period_end` | date | Last day of the reporting period the row covers. | Derived from the source report. |
| `source` | enum | Which system the numbers came from. `amazon_report` or `first_party_analytics`. | Derived from the source. |
| `channel` | enum | Where the traffic came from. `organic_search`, `direct`, `referral`, `social`, `email`, `paid`, `unknown`. | First-party analytics. |
| `campaign_id` | string | Stable identifier for the campaign or content piece the row is about. | Editorial. |
| `landing_path` | string | The site path the session started on, e.g. `/guides/basket-or-oven-style-air-fryer/`. | First-party analytics. |
| `product_id` | string | The product the row is about, matching `id` in `data/products.json`. | Editorial. |
| `eligible_sessions` | integer | Sessions that Amazon's own definition counts. Amazon measures a session as beginning when a customer clicks through a Special Link and ending at the first of: 24 hours elapse; the customer places an order for a Product other than a digital product; or the customer clicks through a Special Link that is not ours. | `amazon_report` only. Never estimated. |
| `outbound_clicks` | integer | Clicks on our outbound product links. | First-party analytics. May be cross-checked against `amazon_report`. |
| `reported_orders` | integer | Orders as reported by an authorised first-party report. | `amazon_report` only. Never estimated, never inferred from click-through rate. |
| `reported_order_value` | decimal | Order value in the reporting currency, where the report provides it. | `amazon_report` only. |
| `reporting_currency` | string | ISO 4217 currency code for the value above, e.g. `USD`. | Derived from the source report. |
| `report_source` | string | Where the report lives — a report name and period, or the URL or file the numbers were read from. | Whoever read it. |
| `report_retrieved_on` | date | The day the report was read. | Whoever read it. |
| `provenance_note` | string | Anything that would let a reader reconstruct this row later: a screenshot filename, a report identifier, a change of scope. | Whoever wrote it. |

## Rules

1. **One row per (period, channel, campaign, product) combination.** If a number
   cannot be broken down that way, it does not go in this ledger. It goes in a report.
2. **Never mix sources in one row.** A row is either from an Amazon report or from
   our own analytics. If you need to compare them, write two rows and reconcile them
   in `provenance_note`.
3. **Never fill a number you inferred.** If the click-to-order rate is not in an
   authorised report, `reported_orders` stays empty.
4. **Dates are ISO 8601.** `2026-11-01`, not `November 1st`.
5. **A blank is a fact.** A blank cell means the number was not obtained from an
   authorised first-party report. It does not mean zero.
6. **No scores, no forecasts, no projections in this file.** A column for a
   conversion score or a revenue estimate would be a column that eventually gets
   filled with a guess.

## Where the first rows will come from

`amazon_report` rows come from the Associates reporting in Associates Central, once
the tracking ID question on the Flagged for Review page has been closed and the
account is enrolled. `first_party_analytics` rows come from the self-hosted
collector described on the Measurement page, which writes NDJSON to
`data/events.ndjson` on the server that hosts it.

The site's own click counter and Amazon's order report are different measurements of
different things. Keeping them in separate rows with a shared period is the only way
to reconcile them honestly.

## Related files

- `data/products.json` — the product register, with the `product_id` values used here.
- `data/config.json` — the measurement configuration, including the five event ids.
- `data/flags.json` — the open items that gate the first Amazon-sourced row.
