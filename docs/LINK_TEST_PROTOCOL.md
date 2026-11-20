# Link verification protocol — one link first, then scale

**Do not buy anything through your own links to test this.** Purchasing through your own Special Links —
or asking friends, family or contractors to — is prohibited (Participation Requirements §6(u)), and the
purchase is disqualified anyway. The test below verifies the destination and the tag, then waits for a
real reader's click to show up in the reports.

Time: 3–5 minutes for the first link, about a minute for each one after.

## Before you start

1. Sign in to Amazon with the same account that owns Associates.
2. Associates Central → Account Settings → **Manage your tracking IDs**: confirm `shopnow047c-20` is
   listed, and that this site's URL appears in the registered-website list (that is question Q-02).
3. Note the application date and qualifying-sale count from the account home page, then record them:
   `python3 tools/campaign_ledger.py program --application-date YYYY-MM-DD --qualifying-sales N`

## One link, start to finish (do exactly one before the others)

1. Open the submitted short link, for example `https://link.amazon/B04G1MEwY`, in a normal tab.
2. Read the **final address bar**. Two outcomes:
   * it lands on `amazon.com/dp/<id>` and the query still contains `tag=shopnow047c-20` → the shortener
     preserved the tag; record that;
   * it lands on a search-results page, an error page, or without the tag → record exactly that. Do not
     "fix" the register with an assumed value; a blank cell with a flag is worth more than a tidy lie.
3. Generate the same link the sanctioned way, for comparison: **SiteStripe → Get Link: Text** on the
   product page, and **Product Linking → Product Links** in Associates Central. Whatever those tools
   hand back is the link the account recognises; that is the "Special Links" path §2(a)–(b) describe.
4. Confirm the listing identity: copy the exact product title and the department/category as printed on
   the page. Nothing else about the product goes into the register — no price, no rating, no review text.
5. Record it:

   ```bash
   python3 tools/product_intake.py confirm --slot 1 \
     --observed-redirect 'https://www.amazon.com/dp/XXXXXXXXXX?tag=shopnow047c-20' \
     --listing-url       'https://www.amazon.com/dp/XXXXXXXXXX' \
     --title 'Exact listing title' --category 'Kitchen & Dining' \
     --method 'SiteStripe + manual click' --date 2026-11-24 --by <initials>
   ```

   The record becomes `link_state: live` only when *both* the confirmed listing URL and the observed
   redirect exist. `scan` will refuse the rest.
6. Next day: Associates Central → Reports, filtered to the tracking ID. If the test click does not
   appear, the referral is not attributable — stop there, open a flag, and leave the shelf gated.
7. Update `data/flags.json`: set FLG-003 to `resolved` (or `escalated`, with one sentence on why), and
   correct `intended_asin` if the supplied string was truncated in transcription.
8. Set `data/program.json → commerce_switch.allow_live_links: true`, then
   `python3 tools/build_site.py && python3 tools/check_site.py`, commit and push. The gate must pass.

## Then the other four

Same eight steps per slot. Enable the ones that pass; leave the rest pending. A partially live shelf is
the correct output of partially verified input: the gate is per product (`link_state`) as well as
site-wide, so nothing rides along on someone else's confirmation.

## What this protocol deliberately excludes

* No test orders, no favours from relatives, no "click it a few times to see if it works" — §6(s), §6(u).
* No scraping to fill in the rest: robots and data mining against Program Content are outside the
  licence, and API data may not be aggregated or analysed without written approval. If you want that
  capability, ask Amazon in writing first and record the answer in the register.
* No claims about what the product is like. Confirming a destination settles *which page this link
  opens*. It does not settle whether the appliance is any good, and that gap stays open until somebody
  cooks in one.
