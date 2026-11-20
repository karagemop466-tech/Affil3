/* The Countertop Edit — privacy-preserving analytics client.
 *
 * Five defined events:
 *   page_view     - a page loaded
 *   product_view  - a product card/row was clicked
 *   guide_view    - a guide page loaded
 *   outbound_click- an outbound (Amazon) link was clicked
 *   conversion    - NOT sent by this client. Recorded only from authorized
 *                   first-party reports (Amazon Associates) in the campaign ledger.
 *
 * Privacy: no cookies, no localStorage, no identifiers. The client sends only
 * the event name, the page path, and (for clicks) the destination host. The
 * server stores no IP addresses.
 *
 * Endpoint: override with window.ANALYTICS_ENDPOINT before this script loads.
 * Default '/api/collect' is served by the self-hosted endpoint
 * (server/analytics_server.py). On static hosts without that endpoint the
 * client silently no-ops.
 */
(function () {
  "use strict";

  var ENDPOINT = window.ANALYTICS_ENDPOINT || "/api/collect";

  function channelFromReferrer() {
    var ref = document.referrer || "";
    if (!ref) return "direct";
    try {
      var host = new URL(ref).hostname;
      if (host.indexOf("google.") === 0 || host.indexOf("bing.") === 0 || host.indexOf("duckduckgo.") === 0) return "organic";
      if (host.indexOf("t.co") === 0 || host.indexOf("facebook.") === 0 || host.indexOf("instagram.") === 0 || host.indexOf("twitter.") === 0 || host.indexOf("x.com") === 0 || host.indexOf("pinterest.") === 0 || host.indexOf("youtube.") === 0) return "social";
      if (host.indexOf("substack") >= 0 || host.indexOf("buttondown") >= 0) return "email";
      return "referral";
    } catch (e) {
      return "referral";
    }
  }

  function send(payload) {
    payload.ts = new Date().toISOString();
    var body = JSON.stringify(payload);
    try {
      if (navigator.sendBeacon) {
        navigator.sendBeacon(ENDPOINT, new Blob([body], { type: "application/json" }));
        return;
      }
      fetch(ENDPOINT, { method: "POST", body: body, headers: { "Content-Type": "application/json" }, keepalive: true }).catch(function () {});
    } catch (e) { /* endpoint absent or blocked: privacy-first no-op */ }
  }

  function track(event, extra) {
    var payload = { event: event, path: location.pathname.split("?")[0], channel: channelFromReferrer() };
    if (extra) { for (var k in extra) { if (Object.prototype.hasOwnProperty.call(extra, k)) payload[k] = extra[k]; } }
    send(payload);
  }

  // page_view (and guide_view on guide pages)
  document.addEventListener("DOMContentLoaded", function () {
    track("page_view");
    var guide = document.body.getAttribute("data-guide-id");
    if (guide) { track("guide_view", { guide: guide }); }
  });

  // product_view + outbound_click via delegation
  document.addEventListener("click", function (ev) {
    var target = ev.target.closest ? ev.target.closest("[data-product-view]") : null;
    if (target) {
      track("product_view", { product: target.getAttribute("data-product-view") });
    }

    var link = ev.target.closest ? ev.target.closest("a[data-outbound]") : null;
    if (link && link.href) {
      var host = "";
      try { host = new URL(link.href).hostname; } catch (e) { host = link.getAttribute("data-outbound-host") || ""; }
      track("outbound_click", { target: host, rel: link.getAttribute("rel") || "" });
    }
  }, true);

  // expose for debugging
  window.affil3Analytics = { track: track, endpoint: ENDPOINT };
})();
