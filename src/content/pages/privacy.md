---
title: Privacy
desc: What the site records, what it does not, and who can see either.
date: 2026-11-20
kicker: Privacy
cluster: null
author: Counter Tested
status: published
sources: S19, S12
layout: page
---

Short version: this site sets no cookies, runs no third-party script, and as published today records nothing about you at all.

## What we built

The site ships with its own counter rather than a third-party analytics tool, because the counter is the only way to answer "did this guide earn a click" without sending reader data to somebody else's script.

- **No cookies, no localStorage, no fingerprinting.** A random id is generated per page load, lives in memory, and dies when the tab closes. It cannot follow you between pages.
- **Not logged:** your IP address (the collector discards it and never writes it), your user agent, your referrer, your screen size, the query string of the link you clicked.
- **Logged, if a collector is configured:** an event name, the path you were on, a timestamp to the second, and for a click the destination's host name and whether the affiliate tag was present. Five events exist, defined in public, with one purpose each — see [Measurement](measurement.html).
- **Not logged ever:** anything that would let us tie a visit to a person. Amazon's rules also forbid associating a tracking sub-tag with a specific end user, so the design makes that impossible rather than merely discouraged.

## Why nothing is collected right now

The site is hosted on GitHub Pages, which serves static files and cannot run the collector process. Until the endpoint is deployed somewhere and written into `data/program.json`, the counter script has nowhere to send anything, so it counts in the visitor's own browser and no further. We would rather publish zero data than quietly collect some.

## Third parties

- **Amazon.** When you click a product link, Amazon sets its own cookies on its own site as part of processing that visit and any resulting order. That is their notice, not ours, and we do not control or read what they store. Their programme policies make the operator responsible for disclosing this category of third-party cookie use, which is what this section is.
- **GitHub.** Hosting the pages; they see standard request logs for their own purposes.
- **Nothing else.** No ad networks, no social pixels, no embeds, no fonts loaded from another domain, no external JavaScript or CSS. Every stylesheet and script is in this repository and readable.

## Your side of it

There is no account, no newsletter form and no comment system on this site, so there is nothing to delete or export. If a future version adds one, this page has to be rewritten first — the build gate includes a check that a page cannot advertise a capture mechanism that does not exist.

Found something here that contradicts this page? That is a bug and a compliance problem at once. Open an issue; we would rather be told.
