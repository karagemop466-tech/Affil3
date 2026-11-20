# Measurement, and its honest ceiling

## The five events

`page_view`, `guide_view`, `outbound_click`, `disclosure_view`, `product_intent_confirmation` — defined in
[`data/events.schema.json`](../data/events.schema.json), each with what it records, what it refuses to
record, and why. They were named in the bootstrap session because the brief's "five defined events" were
not defined anywhere in the repo (FLG-006, SG-12) and are marked as proposed until approved.

## Running the collector locally

```bash
# 1. start the collector
python3 tools/collect_server.py --host 127.0.0.1 --port 8099 --out data/ledger/events.jsonl

# 2. point the site at it (temporarily)
python3 - <<'EOF'
import json, pathlib
p = pathlib.Path("data/program.json")
d = json.loads(p.read_text())
d["measurement"]["endpoint"] = "http://127.0.0.1:8099/e"
p.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
EOF

# 3. rebuild, browse as a reader, then read the stream
python3 tools/build_site.py && python3 -m http.server 8080 --directory site
python3 tools/events.py report

# 4. revert before committing
git checkout data/program.json && python3 tools/build_site.py
```

Browsing your own site locally to exercise the counter is fine. **Do not stage clicks on the published
site to make numbers appear** — the Participation Requirements prohibit artificially generating clicks or
impressions, and it is the same reason `check_site.py` never follows an outbound link.

## Deploying the endpoint for real

Pages cannot run a process, so `measurement.endpoint` stays `null` while the site lives on Pages. Any host
that can run `python3 tools/collect_server.py` behind HTTPS is enough: a container with a read-write path
for `data/ledger/events.jsonl`, `--origin <your-site-host>` so only your site may post, and a body-size cap
at the reverse proxy too. Summaries stay on the host (`tools/events.py report`); there is deliberately no
read API, and no access log that would record a client address.

## What can never be measured here

* **Conversion rate, as an on-site number.** Orders live in Amazon's reports and the attribution window
  stays open long after the visit: the session closes 24 hours after the click; an order added to the cart
  inside it counts up to 89 days later; dispatch and payment may run 180 days. A ratio computed on
  same-week numbers is a guess about an unfinished window, so the ledger stores both columns raw and
  computes neither.
* **Revenue forecasts.** Nothing on the site projects income. There is no traffic history, no confirmed
  product set, and the brief itself said to present no forecast.
* **A person.** No cookies, no persistent id, no IP, no user agent, no referrer. "Sessions" in the report
  are page loads sharing a `path`, and that association is unstable by design.
* **Whether a reader understood the disclosure.** `disclosure_view` measures placement, not
  comprehension, and must never be cited as evidence of legal adequacy.

## Choosing the next topic from data

1. Search Console verified (SG-29) and 10+ pages indexed.
2. A non-brand query shows ≥ 20 impressions and an average position better than ~40.
3. `python3 tools/new_guide.py --from-query "<query>" --title "<question-shaped title>" --cluster <cluster>`.
4. After two weeks: does that page hold `guide_view`, and did it earn `outbound_click`? A page with views
   and no clicks has a shelf problem, not a writing problem. A page with no impressions at all is a topic
   problem, and the honest move is to drop it rather than double down.
