---
title: "Privacy"
slug: privacy
description: "What this site collects, what it does not, and what Amazon and GitHub do on their own pages."
---

## This site

- No accounts, no sign-in, no comment forms.
- The site sets no cookies. It does not write to localStorage or sessionStorage.
- The site includes one script, `measure.js`. When a receiver is configured, it sends five event names (page view, disclosure view, product view, guide view and outbound click), the page path without any query string, and a product code such as P01. It sends no user identifier.
- Do Not Track and Global Privacy Control are honoured. If either is on, nothing is sent.
- While no receiver is configured, the script sends nothing at all. At the time of this build, no receiver is configured. See [FLG-004](@/flagged-for-review/).
- The receiver (`analytics/collect_server.py` in the repository) keeps daily counts only. It does not store IP addresses, user agents or referrers.

## Hosting

The site is hosted by GitHub Pages. GitHub's own privacy statement covers the server logs GitHub keeps.

## Amazon

Links go to Amazon pages. Amazon's Privacy Notice and cookie practices apply there. (Associates policy on privacy disclosure, [SRC-02]({{link:SRC-02}})). This site uses none of its own.

## Changes

This page is updated when the measurement setup changes. The build date is shown in the footer.
