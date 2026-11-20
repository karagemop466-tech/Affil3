---
title: Privacy
slug: privacy
description: No cookies, no trackers, no third-party scripts. Here is the complete list of what could possibly be recorded, and how to turn it off.
---

## Short version

This site sets **no cookies**, uses **no third-party analytics or advertising scripts**, and stores **nothing** about you on our side. There is no account, no newsletter form, no comment system, and no fingerprinting.

## The one measurement, and its current state

We wrote a click counter for the site, because a shop that cannot see which links get clicked cannot decide what to write next. It is switched to **local-only** today, and here is what that means in practice.

**If the collector endpoint is unconfigured** (the current state on this deployment): a page records a bounded list of events in your browser's `sessionStorage`. Nothing is sent anywhere. `sessionStorage` is cleared when you close the tab. There is no server behind this site - it is static files - so "we" cannot read it even if we wanted to.

**If a collector is configured later**, a page sends one small JSON object per event to that one endpoint, over HTTPS, and nothing else.

### What an event contains

| Event | Fields sent | Why |
|---|---|---|
| Page view | page path, a random per-tab token, timestamp | was anyone here |
| Guide view | guide slug, cluster, token, timestamp | which topic earned attention |
| Outbound click | our product id, placement on the page, timestamp | which surface gets the click |
| Link copy | product id, timestamp | deliberate buying intent |
| Gap view | the flag id of a missing field | does a blank field cost us anything |

### What is never included

Your name, email, or any account identifier. Your IP address, as far as our own code is concerned - we do not read or send it. Your device model, browser version, screen size, or fonts. The text you typed into search, the page you came from beyond its origin, or anything about the destination URL. Cross-site or cross-visit identity of any kind.

The random per-tab token exists so that ten clicks from one reading session are not counted as ten readers. It is not stored anywhere durable and it is generated fresh each time you open the site.

## Selling data

There is none. No data broker, no ad network, no analytics vendor, and no affiliate network gets a payload from this page. The register that backs every article lives in a public repository as ordinary text files.

## Amazon's side of the click

When you click a `Sponsored` link, you leave this site. Amazon then handles your session under [Amazon's own Privacy Notice](https://www.amazon.com/gp/help/customer/display.html?nodeId=GX7NJQ4ZB8MHFRNJ), and the attribution that lets us earn a commission works through their cookie and their session, not through anything recorded here. We cannot see who you are, what you bought, or whether you returned it - and we do not need to: the only numbers we are allowed to publish about earnings are the ones read out of Amazon's own reports, dated, with their source attached.

## Turning it off

Three ways, none of which breaks the site:

1. Do nothing - with no collector configured there is no transmission to disable.
2. Clear site data in your browser; `sessionStorage` dies with the tab anyway.
3. Block the domain if you use a network filter. Every page works without JavaScript; the counter simply does not run.

## If this site later serves readers outside the United States

The design was chosen to sit outside consent-banner regimes for a US audience: no cookies, no persistent identifiers, no profiling. "Outside most regimes" is not "outside all of them", and if the audience changes, the lawful-basis note on this page changes with it before the collector is switched on. That dependency is recorded as an open decision rather than a promise.
