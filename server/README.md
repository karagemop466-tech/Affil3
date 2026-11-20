# Self-hosted analytics endpoint

`collect.js` is the first-party event collector for the site's five defined
events (see `desk/analytics/`). It is deliberately small and privacy-preserving:

- accepts `POST /collect` with `{ e, p, t, path, s }`
- allows only the five registered event names
- stores a JSONL line per event — **no IP, no user-agent, no cookies, no query strings**
- answers `GET /health` for monitoring

## Deploy

```sh
PORT=8787 CK_LOG=/var/lib/ck/events.jsonl node server/collect.js
```

Put it behind HTTPS (Caddy/nginx/cloud function), then set the endpoint in the
site: edit the `ck-endpoint` meta value in `scripts/build_site.py`
(`<meta name="ck-endpoint" content="">`) to your `https://…/collect` URL and
run `python3 scripts/build_site.py`. That is the only change needed — the
client (`assets/js/analytics.js`) already prefers `navigator.sendBeacon`.

## Why not on GitHub Pages?

GitHub Pages serves static files only (source S07). Until this collector is
deployed, events aggregate in the visitor's own `localStorage` and the
[campaign ledger](../desk/campaign-ledger/) stays empty by design (FLG-006).

## Reading the data

`events.jsonl` is append-only. Aggregate it with anything (duckdb, jq, a
spreadsheet). Rows enter the campaign ledger only via authorized first-party
reports — this file is a raw event log, not a revenue source.
