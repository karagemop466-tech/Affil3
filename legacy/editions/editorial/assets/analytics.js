/* Privacy-preserving measurement. Five events, no identifiers, no cookies.
 *
 * ENDPOINT is empty in this build. When empty, every send() returns immediately and
 * nothing leaves the browser. The script never blocks a click, never queues a retry
 * against a dead host, and never inspects or records URL parameters.
 *
 * Events: page_view, outbound_product_click, guide_read, suggestion_vote, disclosure_view
 */
(function () {
  "use strict";

  var ENDPOINT = "";

  if (!ENDPOINT) { return; }

  var BOT = /bot|crawler|spider|crawling|headless|preview|monitor/i;
  if (BOT.test(navigator.userAgent || "")) { return; }
  if (navigator.doNotTrack === "1" || window.doNotTrack === "1") { return; }

  function hostOf(url) {
    try { return new URL(url, location.href).hostname; } catch (err) { return null; }
  }

  function send(event, fields) {
    if (!ENDPOINT) { return; }
    var body = JSON.stringify({
      event: event,
      path: location.pathname,
      fields: fields || {}
    });
    try {
      if (navigator.sendBeacon) {
        navigator.sendBeacon(ENDPOINT, new Blob([body], { type: "application/json" }));
      } else {
        fetch(ENDPOINT, {
          method: "POST",
          body: body,
          headers: { "Content-Type": "application/json" },
          keepalive: true,
          mode: "no-cors",
          credentials: "omit"
        }).catch(function () {});
      }
    } catch (err) {
      /* Measurement must never break the page. */
    }
  }

  /* 1. page_view */
  send("page_view", { referrer_host: document.referrer ? hostOf(document.referrer) : null });

  /* 2. outbound_product_click — hostname only, never the full URL with its parameters */
  document.addEventListener("click", function (ev) {
    var a = ev.target && ev.target.closest ? ev.target.closest("a[data-outbound]") : null;
    if (!a) { return; }
    send("outbound_product_click", {
      product_id: a.getAttribute("data-product") || null,
      destination_host: hostOf(a.href)
    });
  }, true);

  /* 3. guide_read — 30 seconds on a guide page */
  if (location.pathname.indexOf("/guides/") === 0 && location.pathname !== "/guides/") {
    var parts = location.pathname.split("/").filter(Boolean);
    var slug = parts.length > 1 ? parts[1] : null;
    var fired = false;
    setTimeout(function () {
      if (fired || document.visibilityState === "hidden") { return; }
      fired = true;
      send("guide_read", { slug: slug });
    }, 30000);
  }

  /* 4. suggestion_vote — only fires if a vote control exists */
  document.addEventListener("click", function (ev) {
    var b = ev.target && ev.target.closest ? ev.target.closest("[data-vote]") : null;
    if (!b) { return; }
    send("suggestion_vote", {
      suggestion_id: b.getAttribute("data-vote"),
      choice: b.getAttribute("data-choice") || null
    });
  }, true);

  /* 5. disclosure_view — the strip is on every page; record it once when seen */
  var strip = document.getElementById("disclosure");
  if (strip && "IntersectionObserver" in window) {
    var seen = false;
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (seen || !entry.isIntersecting) { return; }
        seen = true;
        send("disclosure_view", {});
        io.disconnect();
      });
    }, { threshold: 0.5 });
    io.observe(strip);
  }
})();
