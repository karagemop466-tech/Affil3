# Aggregate analytics endpoint (not deployed or connected)

GitHub Pages serves static assets and does not execute an API. This small Node.js endpoint is included as a self-hostable, first-party option; it is **not live** on the published static site until you deploy it and define `window.COUNTER_NOTES_ANALYTICS_ENDPOINT` in the site before `assets/app.js` loads, pointing to that fixed HTTPS endpoint. The setting is intentionally absent now.

## Run

```sh
ALLOWED_ORIGIN=https://karagemop466-tech.github.io \
SUMMARY_TOKEN='use-a-long-random-secret-from-your-secret-manager' \
node analytics/server.mjs
```

Set `PORT` and `ANALYTICS_STORE` as needed. Persist the aggregate JSON file on durable storage if counts must survive restarts. Put the service behind HTTPS and a trusted host; never expose `SUMMARY_TOKEN` to browser code. The public summary route requires it in an Authorization header.

The server stores only aggregate counts by UTC day, a fixed event name and an allow-listed page slug, retaining up to 90 days. It does not persist IP addresses, cookies, user agents, referrers, query strings, event-level rows or product IDs. The endpoint accepts only the five event types `page_view`, `guide_open`, `outbound_click`, `suggestion_vote`, and `reader_capture`; requests must match the configured exact Origin. Protect and review the deployment, storage, retention and privacy disclosures before using it for production measurement.

The current front-end endpoint setting is intentionally empty. Its localStorage event log is limited to the current browser and is not site-wide analytics. Do not treat it as a substitute for the self-hosted endpoint, Amazon Associates reports or Search Console.
