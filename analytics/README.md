# First-party analytics endpoint

This is a small, dependency-free Node.js endpoint. It stores daily aggregates only. It does not write cookies, full URLs, query strings, referrers, IP addresses, user-agent strings, customer identifiers, order identifiers, or email addresses.

## The five event types

| Event | What is counted | Source |
|---|---|---|
| `page_view` | A page load by stable page ID; not a unique visitor or session | Site |
| `guide_engagement` | One count when a guide crosses the 60% scroll threshold; no duration or scroll trace | Site |
| `outbound_click` | A click on a published, approved product link, keyed by a site link ID | Site |
| `reader_capture_intent` | An explicit RSS/newsletter follow action; does not claim that a subscription completed and stores no email | Site |
| `reported_order_import` | A dated aggregate imported from an authorized Amazon Associates Central report | Authorized report import |

The campaign ledger remains separate from client event counts. Add ledger data only from authorized first-party reports, retain the report date and provenance, and leave `eligible_sessions` blank when the source does not provide that value. Do not infer conversion, orders, or revenue from outbound clicks.

## Run locally

Requires Node.js 20 or newer. From the repository root:

```sh
ANALYTICS_ALLOWED_ORIGIN=http://localhost:8787 \
ASSOCIATES_REPORT_TOKEN='use-a-local-test-secret' \
node analytics/server.mjs
```

The API binds to `0.0.0.0:8787` by default. In production, set `NODE_ENV=production`, `ANALYTICS_ALLOWED_ORIGIN` to the exact public origin, a long random `ASSOCIATES_REPORT_TOKEN`, and `ANALYTICS_DATA_PATH` to durable storage outside the Git checkout. The report token is server-side only and must never be placed in `site-config.js`, a page, or a browser request. Keep the endpoint behind TLS, configure upstream rate limits, define a retention period, and restrict report-import access.

`POST /api/events` accepts only the four site event types and an allowlist of stable IDs. `POST /api/reports/associates` requires the bearer token and accepts only aggregate report totals plus a short provenance label. Duplicate report references for the same date and channel are rejected. Raw report files are not accepted or saved.

Run endpoint tests with:

```sh
node analytics/test.mjs
```

## Hosting boundary

GitHub Pages publishes static HTML, CSS, and JavaScript; it does not run this Node endpoint. Accordingly, the checked-in `site-config.js` has an empty endpoint and the live GitHub Pages site does not send analytics events. To turn collection on, host the site and this endpoint together behind a supported server or reverse proxy, then set the endpoint in that deployment. No click or order data is currently being collected by this project. GitHub's own Pages documentation also states that visitor IP addresses are logged and stored for security purposes by the hosting service; this site cannot change that host-level behavior.
