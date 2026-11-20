/* ShopNow Kitchen Edit — page behaviors.
   2 — outbound_product_click  (anchors with data-product-intent)
   3 — guide_engaged           (75% scroll on guide pages, once)
   4 — reader_capture_submitted
   5 — dashboard_event_exported (dashboard page wires this) */
(function () {
  "use strict";
  function track(name, payload) {
    if (typeof window.shopnowTrack === "function") window.shopnowTrack(name, payload || {});
  }

  /* 2 — outbound product clicks */
  document.addEventListener("click", function (ev) {
    var a = ev.target && ev.target.closest ? ev.target.closest("a[data-product-intent]") : null;
    if (!a) return;
    track("outbound_product_click", {
      product_id: a.getAttribute("data-product-intent"),
      intended_asin: a.getAttribute("data-intent-asin") || "",
      target_host: (function () { try { return new URL(a.href).host; } catch (e) { return ""; } })(),
      link_status: a.getAttribute("data-link-status") || "unverified",
      sponsored_rel: (a.rel || "").indexOf("sponsored") !== -1
    });
    /* intentional: no preventDefault — the click proceeds to Amazon */
  });

  /* 3 — guide engagement (75% depth, once per load) */
  var fired = false;
  function depth() {
    var doc = document.documentElement;
    var max = (doc.scrollHeight - window.innerHeight);
    return max > 0 ? (window.scrollY / max) : 1;
  }
  window.addEventListener("scroll", function () {
    if (fired || depth() < 0.75) return;
    if (!document.body.hasAttribute("data-is-guide")) return;
    fired = true;
    track("guide_engaged", { path: location.pathname, depth_percent: 75 });
  }, { passive: true });

  /* 4 — reader capture (no address leaves the browser; see Q-08) */
  document.addEventListener("submit", function (ev) {
    var form = ev.target;
    if (!form || !form.hasAttribute("data-capture")) return;
    ev.preventDefault();
    var email = form.querySelector('input[type="email"]');
    var value = email ? email.value : "";
    track("reader_capture_submitted", {
      placement: form.getAttribute("data-capture") || "unknown",
      endpoint_configured: !!(window.SHOPNOW_CONFIG && window.SHOPNOW_CONFIG.analyticsEndpoint)
    });
    form.innerHTML = '<p class="ok-note"><strong>Noted.</strong> Your interest is recorded locally in this browser. ' +
      'No email list exists yet — when the newsletter provider decision lands (SG-11), this is the form that connects to it.</p>';
    if (email) email.value = value ? "" : "";
  });
})();
