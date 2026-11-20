/*
 * The Crisp Index — privacy-preserving event beacon.
 *
 * Design (see SUG-003 / SUG-004, FLG-006):
 *  - No cookies, no localStorage, no fingerprinting, no IP or user-agent logging.
 *  - Sends only: { event, path, ts, ref? } to ONE self-hosted endpoint.
 *  - Ships in dry-run mode: while TCI_CONFIG.analyticsEndpoint is null, nothing
 *    is transmitted. Deploy tools/analytics-endpoint/ and set the endpoint to
 *    release the gate.
 *  - Proposed five-event schema (owner confirmation pending — Q-003):
 *    page_view, outbound_click, guide_read, newsletter_signup, feedback_click.
 */
(function () {
  "use strict";
  var cfg = window.TCI_CONFIG || {};
  var ENDPOINT = cfg.analyticsEndpoint || null;

  function tci(event, extra) {
    if (!ENDPOINT) return; // dry-run: gate closed (FLG-006)
    var payload = { event: event, path: location.pathname, ts: Date.now() };
    if (extra && extra.ref) payload.ref = String(extra.ref).slice(0, 120);
    try {
      fetch(ENDPOINT, {
        method: "POST",
        keepalive: true,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      }).catch(function () {});
    } catch (e) { /* never break the page for analytics */ }
  }
  window.tci = tci;

  // 1. page_view
  tci("page_view");

  // 2. outbound_click — every product/outbound link is marked data-tci="outbound"
  document.addEventListener("click", function (e) {
    var a = e.target && e.target.closest ? e.target.closest("a[data-tci=outbound]") : null;
    if (a) {
      tci("outbound_click", { ref: a.getAttribute("data-product") || a.href });
    }
    var fb = e.target && e.target.closest ? e.target.closest("a[data-tci=feedback]") : null;
    if (fb) {
      // 5. feedback_click — 'suggest a topic / report an issue' links
      tci("feedback_click", { ref: fb.getAttribute("href") });
    }
  });

  // 3. guide_read — fired once when a reader passes 75% of an article
  var article = document.querySelector(".article");
  if (article && "IntersectionObserver" in window) {
    var sent = false;
    var sentinel = document.createElement("div");
    sentinel.style.position = "absolute";
    sentinel.style.top = "75%";
    sentinel.style.height = "1px";
    sentinel.style.width = "1px";
    article.style.position = "relative";
    article.appendChild(sentinel);
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting && !sent) {
          sent = true;
          tci("guide_read", { ref: location.pathname });
          io.disconnect();
        }
      });
    });
    io.observe(sentinel);
  }

  // 4. newsletter_signup — emitted by the capture form when captureEndpoint is live
  document.addEventListener("submit", function (e) {
    if (e.target && e.target.classList && e.target.classList.contains("capture-form")) {
      tci("newsletter_signup");
    }
  });
})();
