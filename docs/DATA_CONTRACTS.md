# Data contracts

Every rendered value comes from `data/`. Nothing is hand-written into `site/` — CI rebuilds and fails on
drift. If a value is unknown, the field is `null`, the table renders a labelled blank, and a flag exists.

## `data/program.json` — the relationship and the switches

| Path | Meaning | Written by |
| --- | --- | --- |
| `associates.tracking_id` | the tag printed on every outbound link | operator; never invented |
| `associates.implied_associates_id` | derived prefix CHK-04 uses to sanity-check the tag shape | derived, with its basis recorded |
| `associates.required_disclosures.*` | verbatim disclosure strings the layout prints | copied from the agreement/licence text |
| `associates.join_clock.*` | 180-day / 3-qualifying-sale state | `tools/campaign_ledger.py program` |
| `associates.api_access.*` | whether Creators/PA API use is possible at all | operator; `null` = unknown |
| `commerce_switch.allow_live_links` | site-wide commerce gate; `false` renders no clickable affiliate link | operator, after the link test |
| `measurement.endpoint` | collector URL; `null` means the site records nothing remotely | operator |
| `data_shelf_life.*` | the 24 h cache rule from the licence | fixed by [S08] |

## `data/products.json` — the product-intent register

One record per submitted link. Three field groups, kept deliberately apart:

* **intended** — `intended_asin`, `intended_asin_char_count`, `submitted_url`, `candidate_listing_url`
  (with `candidate_listing_url_basis` stating how it was derived).
* **confirmed** — `official_listing_url`, `confirmation.{date,method,confirmed_by,evidence,status}`.
  Populated only by `tools/product_intake.py confirm`, which requires `--method` and an ISO `--date`.
* **observed** — `observed_redirect_target`, `observed_redirect_note`. Never merged into *intended*.
* **licence-restricted** — `price`, `availability`, `rating`, `review_count`, `commission_rate`. The
  intake tool exposes no flag that sets these; rendering one requires a provenance row, and today there
  is no lawful source to create one.
* **governance** — `link_state` (`pending` | `live`), `flags[]`, `_provenance{}`.

Invariant enforced by `product_intake.py scan`: `link_state=live` requires both a confirmed listing URL
and an observed redirect; a value with no provenance entry is a failure; `confirmation.status=confirmed`
without a date is a failure.

## `data/sources.json` — the only facts the project may assert

`{id, claim, publisher, url, section, accessed, verification, quote?, note?, used_by[]}`.
`verification` is one of:

| value | means |
| --- | --- |
| `primary-full` | the page was fetched and the clause read in context in that session |
| `primary-full-intro` | fetched; introduction read, later sections not captured |
| `primary-landing` | page reached, body text not captured — cite by number, do not quote |
| `primary-snippet` | official page text seen via search results, not re-fetched — verify before relying |
| `reference-only` | background; **no displayed claim may depend on it** |

Downgrade a row honestly when you re-check it. Never upgrade one from memory.

## `data/suggestions.json`, `data/questions.json`, `data/flags.json`

Registers with decision fields. A suggestion's `decision` starts `"pending"`; the site renders whatever is
in the file, so page and register cannot disagree. `status` ∈ `proposed · partially-adopted ·
adopted-in-build · proposed-defer`. Flags never block a merge — only a failed gate does. Numbering:
`SG-01..SG-24` opened by the bootstrap session, `SG-27..SG-30` carried from the brief's parallel pass;
`SG-25/26` were never created and the gap is recorded in `_meta` so nobody hunts for lost rows.

## `data/events.schema.json`

The five permitted events, their extra fields, and the rules the collector enforces. Universal fields:
`ts` (server clock, never the client's) `ev` `path` `sid` `v`. Unknown event or unknown field ⇒ rejected
and logged to `data/ledger/events.rejected.log` as key names only, never as content.

## `data/ledger/campaign.jsonl`

Append-only. `tools/campaign_ledger.py` refuses a row without `--source` and `--report-date`, refuses
unknown fields, and refuses derived metrics (`conversion_rate`, `ctr`, `revenue_forecast`, `score`, …).
The raw event stream (`events.jsonl`) is git-ignored on purpose: it is runtime data, not a source of
truth. `campaign.example.jsonl` documents the row shape and is never read.

## Adding a guide

1. `python3 tools/new_guide.py --title '…' --cluster air-fryers --week N` — creates the file and the
   calendar row in one operation, as `draft`.
2. Fill the claims table in the file. One row per factual sentence, each naming a `sources.json` id.
3. Flip `status: published` in the file **and** in `data/editorial-calendar.json` (same commit).
4. `python3 tools/build_site.py && python3 tools/check_site.py`. CHK-12 fails if steps 3 or 4 drift.
