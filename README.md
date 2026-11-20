# Countertop Notes — kitchen choices, made clearer

This repo now contains a publication-style Amazon affiliate site plus a source-backed Research desk. The front page leads with practical buyer questions; product identity, link compliance, analytics, and search setup remain visibly gated wherever the available evidence is incomplete.

## Important status

- Five submitted URLs are recorded. Intended ASIN, official intended listing URL, confirmation date, and confirmation source remain blank until confirmed; observed destinations are separate.
- The selected Tracking ID `shopnow047c-20` is owner-provided and has not been verified against Associates Central.
- The exact compliance status of the supplied short links is unresolved in **FLG-003**; this project does not claim they are invalid.
- Price, availability, reviews, competition, commission, trend, conversion, and revenue fields are blank. The campaign ledger is empty.
- A proposed privacy-preserving five-event schema and a self-hosted Node endpoint are included. The request does not define the five-event contract; the built Pages artifact and default preview serve a disabled runtime, and collection must not be enabled until the specification is confirmed.
- Search Console ownership and reader capture are not configured.

See [Executive Summary](EXECUTIVE-SUMMARY.md), [requirements status](docs/REQUIREMENTS.md), [official source register](docs/SOURCES.md), and the public **Flagged for Review** page.

## Build and verify

Requires Node.js 20 or newer. There are no third-party package dependencies.

```sh
npm run check
```

The command builds static HTML into ignored `_site/` and checks local links, disclosures, navigation, product-link `rel="sponsored"`, source links on table rows, blank unverified fields, sitemap/RSS coverage, event schema, and campaign-ledger state.

To build and preview the site:

```sh
npm run build
npm start
```

Both the generated Pages artifact and the default preview serve a disabled analytics runtime. The default preview also rejects event and summary requests. The Node endpoint binds to `0.0.0.0:4173`, but analytics can be enabled only through an explicit environment setting; use that only in an isolated local development environment after review, never in the shared Arena preview or a public production process:

```sh
HOST=127.0.0.1 ANALYTICS_ENABLED=true npm start
```

When explicitly enabled, the endpoint stores daily aggregate event counts under ignored `.local/`, with 90-day retention by default. It checks Fetch Metadata, requires a matching Origin, and enables no CORS access. If a separately hosted reverse proxy rewrites the request host, configure only its exact public origin with `ANALYTICS_ALLOWED_ORIGINS`; never allow arbitrary origins. Hosting-provider and reverse-proxy logs can have their own retention. GitHub Pages never runs this server. A production runtime must be separately hosted, privacy-reviewed, configured, and verified before measurement is described as active.

## Site map

- `site-src/pages/` — page content fragments
- `site-src/data/` — product-intent register, sources, requirements, flags, suggestions, event schema, and empty campaign ledger
- `site-src/assets/` — original illustration, design system, and browser scripts
- `scripts/build-site.mjs` — creates pages, sitemap, RSS, and robots file
- `scripts/verify-site.mjs` — offline consistency and link checks
- `server/index.mjs` — optional static preview and aggregate-only API
- `.github/workflows/pages.yml` — checked GitHub Pages build/deployment workflow

The current configured Pages URL is `https://karagemop466-tech.github.io/Affil3/`. Deployment and GitHub Pages Actions-source settings must be confirmed after the PR is merged.
