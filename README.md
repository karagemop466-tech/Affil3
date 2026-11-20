# Affil3

A static buying-guide site for five submitted Amazon products, built from structured data.
Live site (GitHub Pages): https://karagemop466-tech.github.io/Affil3/

## What is here

| Path | Purpose |
| --- | --- |
| `data/products.json` | The five product rows: submitted link, intended ASIN fields (blank until verified), observed Amazon fields (kept separate), flags, sources |
| `data/sources.json` | Source register (S01–S12): official page, how it was checked, status |
| `data/flags.json` | Flagged for Review items (FLG-001 …) with evidence and the manual step that closes each |
| `data/questions.json` | Known facts, open questions, and ways to discover missing information |
| `data/suggestions.json` | Options to choose between. Nothing is implemented until chosen |
| `data/guides.json` | Question-led guides (content, dates, sources) |
| `data/config.json` | Site name, tracking ID, disclosure text, analytics endpoint (empty by default) |
| `data/events.json` | The five proposed analytics events and privacy rules |
| `data/ledger.json` | Empty campaign ledger (filled only from authorized first-party reports) |
| `tools/build.mjs` | Generates the site at the repository root (no dependencies). Replaces only its own paths |
| `tools/verify.mjs` | Publishing gate: data and HTML checks; exits non-zero on failure |
| `tools/collector.mjs` | Optional self-hosted analytics collector (aggregate counts only) |
| `src/assets/` | Stylesheet and browser measurement script (source; copied to `assets/`) |
| `index.html`, `shop/`, `guides/`, `categories/`, … | Generated site served by GitHub Pages from the repository root |
| `legacy/arena-83a43a96/` | Earlier root-level site from session `arena-83a43a96-affil3` (PR #1), moved here unchanged |
| `EXECUTIVE_SUMMARY-6249757a.md` | Executive summary for this session (the root `EXECUTIVE_SUMMARY.md` belongs to session `arena-83a43a96-affil3` and is unchanged) |
| `COORDINATION.md` | Shared task board (session `arena-83a43a96-affil3` section unchanged, session `6249757a` section appended), verification log, irregularities, PR and deploy record |

## Commands

```sh
npm run build     # regenerate the site at the repository root
npm run verify    # run the publishing gate
npm run check     # build, then verify
npm run collector # optional: start the analytics collector on :8787
```

Node.js 18 or later. No packages are installed.

## Rules the build enforces

- Every product row has a source link to an official page, or the field is blank and flagged.
- Intended ASIN, official listing URL, confirmation date and confirmation source are filled only from an official source. Observed redirect destinations live in separate fields.
- Every link to an Amazon host carries `rel="sponsored noopener"`.
- Product links use the tracking ID from `data/config.json` (`?tag=shopnow047c-20`), and point to an observed `/dp/` product. No redirects or cloaking.
- The disclosure strip sits under the masthead on every page and is repeated in the footer. It contains the Associates statement from Operating Agreement §5.
- No prices, ratings or availability are shown.
- Analytics records only the five listed events, with no cookies. The browser script sends nothing unless an endpoint is set.

## Turning analytics on

GitHub Pages cannot run the collector. To measure clicks:

1. Run `tools/collector.mjs` on a host you control, behind HTTPS, with `SITE_ORIGIN=https://karagemop466-tech.github.io`.
2. Set `analyticsEndpoint` in `data/config.json` to `https://<your-host>/collect`.
3. Run `npm run check` and push.

See suggestion S-03 and flag FLG-009.

## Open items

See `/flagged/` on the live site and `COORDINATION.md`. The main blockers are the 9-character submitted tokens (FLG-001), the observed destinations that differ from the tokens (FLG-002), and Associates validation of the tagged links (gate G-02, FLG-005).
