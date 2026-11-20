# Self-hosted analytics endpoint (the gate behind docs/site-config.js)

The brief: *"Add a privacy-preserving outbound-click counter and a self-hosted
analytics endpoint; record the five defined events."* GitHub Pages is a static
host, so the endpoint must live elsewhere. Two reference implementations ship
here; deploying either one and setting `analyticsEndpoint` in
`docs/site-config.js` releases the counter (flag FLG-006).

## Privacy contract (both implementations)

- Accept only: `{event, path, ts, ref?}` — nothing else.
- Do not log IP addresses, user agents, cookies, or any cross-request identifier.
- `ref` is truncated to 120 chars and is only ever a product id or internal path.
- Aggregate counts only; raw rows are optional and event-scoped.

## Event schema (PROPOSED — confirm via SUG-003 / Q-003)

`page_view`, `outbound_click`, `guide_read`, `newsletter_signup`, `feedback_click`

## Option A — Cloudflare Worker (recommended, SUG-004a)

1. `npm install -g wrangler && wrangler login`
2. `wrangler deploy worker.js` (wrangler.toml below), optionally binding a KV
   namespace to persist counters.
3. Put the deployed URL (e.g. `https://tci-count.example.workers.dev/e`) into
   `docs/site-config.js` as `analyticsEndpoint`.

```toml
# wrangler.toml
name = "tci-count"
main = "worker.js"
compatibility_date = "2026-11-20"
```

## Option B — Python stdlib server (SUG-004b)

`python3 server.py` serves `POST /e` and `GET /stats` on port 8787, appending
JSONL to `events.jsonl`. Put it behind TLS (Caddy/nginx) before use.

## Releasing the gate

1. Deploy one of the above.
2. Set `analyticsEndpoint` in `docs/site-config.js`.
3. Confirm a test `outbound_click` appears in the endpoint's stats.
4. Close FLG-006 in `data/flags.json` and log it in `COORDINATION.md`.
