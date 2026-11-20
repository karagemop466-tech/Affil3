# Campaign ledger

An empty, well-defined ledger is the deliverable. Rows arrive only from authorized first-party
reports, each carrying the date and place it was obtained from. No revenue forecast, no
conversion score, and no modelled order count appears anywhere in this directory or on the site.

## `campaign_ledger.csv`

Header, and nothing else.

| Column | Meaning | Where a value may come from |
| --- | --- | --- |
| `date` | UTC date of the reporting period start | Associates Central report period |
| `source` | the exact report the row was taken from, e.g. `Associates Central → Reports → Income Advisory Report` | must be named |
| `channel` | how traffic arrived: `search`, `social`, `newsletter`, `direct`, `other` | our own attribution rule, documented below |
| `eligible_sessions` | sessions counted by the deployed analytics endpoint | `tools/collector.py` output only |
| `clicks` | outbound link clicks | our own `product_link_click` events, cross-checked against the Associates click report |
| `reported_orders` | orders Amazon reports | Associates Central report only, never inferred from clicks |
| `reported_commission` | commission Amazon reports | Associates Central report only |
| `product_category_as_reported` | the category string in the report, verbatim | Associates Central report; this is what settles FLG-005 |
| `retrieved_by` | who pulled it | human or workflow id |
| `provenance_note` | file name, screenshot path, or the export's checksum | required if any numeric cell is filled |

**Channel rule.** A visit is attributed to `search` when the referrer host is a search engine,
`social` for the named social hosts, `newsletter` when the `utm_source=newsletter` parameter is
present, `direct` when there is no referrer, and `other` otherwise. The rule is applied at
ingest time in `tools/ledger.py`, it is deterministic, and it is deliberately coarse: an
affiliate site that reports precise channel revenue without a measured basis is making things up
with extra steps.

**Writing a row.** `python3 tools/ledger.py append --date 2026-12-01 --channel search --clicks 41
--reported-orders 2 --source "Associates Central → Reports → Earnings" --by arena-c7a56e3d`
refuses to write unless `--source` is present, and refuses to write an orders or commission value
without a `--by` that is not `agent-unattended`. That is the whole gate: automation for
arithmetic, a human for anything that came from Amazon.

## `events-YYYY-MM-DD.jsonl`

Written by `tools/collector.py`, one JSON object per line, five event names only
(`data/events.json`). Nothing is in this directory yet because no endpoint is deployed —
FLG-010. An empty file is the accurate state; a file full of plausible numbers would not be.
