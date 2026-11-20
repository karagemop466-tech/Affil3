/*
 * Affil3 — privacy-preserving event hook.
 *
 * STATUS: GATED. ENDPOINT is null, so nothing is sent. Setting it requires an
 * endpoint the site owner controls (GitHub Pages cannot store events). See
 * measurement.html and Questions Q06–Q07.
 *
 * Design:
 *  - No cookies and no local storage are written by this script.
 *  - Only the product ID and destination host are sent for outbound clicks.
 *  - Visitors with Global Privacy Control or Do Not Track enabled are not counted.
 *  - Event names are PROPOSED until the owner confirms the five events.
 */
(function () {
  "use strict";
  var ENDPOINT = null; // e.g. "https://events.example.org/collect" — owner to set

  var optedOut = navigator.globalPrivacyControl === true || navigator.doNotTrack === "1";

  function enabled() { return !!ENDPOINT && !optedOut; }

  function send(name, props) {
    if (!enabled()) return;
    var body = JSON.stringify({
      event: name,
      path: location.pathname,
      ts: new Date().toISOString(),
      props: props || {}
    });
    try {
      if (navigator.sendBeacon) {
        navigator.sendBeacon(ENDPOINT, new Blob([body], { type: "application/json" }));
      } else {
        fetch(ENDPOINT, { method: "POST", body: body, keepalive: true,
          headers: { "Content-Type": "application/json" } }).catch(function () {});
      }
    } catch (e) { /* never break the page */ }
  }

  document.addEventListener("click", function (e) {
    var t = e.target;
    if (!t || !t.closest) return;
    var out = t.closest('a[rel~="sponsored"]');
    if (out) {
      var host = "";
      try { host = new URL(out.href).host; } catch (err) { host = ""; }
      send("outbound_click", { product: out.getAttribute("data-product") || "", host: host });
      return;
    }
    var nav = t.closest("[data-event]");
    if (nav) {
      send(nav.getAttribute("data-event"), { target: nav.getAttribute("data-target") || "" });
    }
  }, true);

  window.addEventListener("load", function () { send("page_view", {}); });

  window.AFFIL_ANALYTICS = { enabled: enabled, send: send };
})();
