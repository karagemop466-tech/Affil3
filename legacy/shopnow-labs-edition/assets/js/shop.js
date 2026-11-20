/* ==========================================================================
   ShopNow Labs — first-party, cookieless event emitter.

   Design rules:
   - No third-party requests. The only outbound request this file can make is
     to ANALYTICS_ENDPOINT, and only when that string is non-empty.
   - No cookies, no localStorage, no fingerprinting, no persistent id.
   - Payloads carry page path, product id and coarse categories only.
   - If the endpoint is empty, every event is dropped in the browser and
     nothing leaves the machine. That is the shipped state.
   - Fails silently: analytics must never break the page.
   ========================================================================== */
(function () {
  "use strict";

  var ENDPOINT = (window.ANALYTICS_ENDPOINT || "").trim();
  var MAX_QUEUE = 40;
  var queue = [];
  var start = Date.now();
  var sent = {};

  function viewportBucket() {
    var w = window.innerWidth || 0;
    if (w < 480) return "xs";
    if (w < 768) return "sm";
    if (w < 1024) return "md";
    if (w < 1440) return "lg";
    return "xl";
  }

  // Coarse referrer class. The full referrer string is never sent.
  function referrerClass() {
    var ref = document.referrer || "";
    if (!ref) return "direct";
    try {
      var host = new URL(ref).hostname;
      if (host === location.hostname) return "internal";
      if (/google\.|bing\.|duckduckgo\.|yahoo\.|ecosia\.|brave\./.test(host)) return "search";
      return "referral";
    } catch (e) {
      return "unknown";
    }
  }

  function productIdFrom(el) {
    var node = el.closest("[data-product-link], a[href*='/dp/']");
    if (!node) return "";
    var m = (node.getAttribute("href") || "").match(/\/dp\/([A-Z0-9]{10})/i);
    if (m) return m[1];
    var holder = node.closest("[data-product-id]");
    return holder ? holder.getAttribute("data-product-id") : "";
  }

  function emit(name, extra) {
    var payload = {
      e: name,
      p: location.pathname,
      r: referrerClass(),
      v: viewportBucket(),
      t: Math.round((Date.now() - start) / 1000),
      ts: new Date().toISOString()
    };
    if (extra) {
      for (var k in extra) {
        if (Object.prototype.hasOwnProperty.call(extra, k)) payload[k] = extra[k];
      }
    }

    // Ship-state guard: with no endpoint, nothing is transmitted or stored.
    if (!ENDPOINT) {
      if (window.__affil3Debug) {
        // eslint-disable-next-line no-console
        console.info("[shop] event dropped (no endpoint):", payload);
      }
      return;
    }

    if (queue.length >= MAX_QUEUE) queue.shift();
    queue.push(payload);
    flush();
  }

  var flushTimer = null;
  function flush() {
    if (!ENDPOINT || !queue.length) return;
    var batch = queue.splice(0, queue.length);
    try {
      var body = JSON.stringify({ site: "shopnow-labs", events: batch });
      if (!navigator.sendBeacon) {
        fetch(ENDPOINT, {
          method: "POST",
          body: body,
          headers: { "content-type": "application/json" },
          keepalive: true,
          credentials: "omit",
          mode: "cors"
        }).catch(function () {});
        return;
      }
      // text/plain keeps this a simple request, avoiding a preflight.
      navigator.sendBeacon(ENDPOINT, new Blob([body], { type: "text/plain;charset=UTF-8" }));
    } catch (e) {
      /* never break the page for analytics */
    }
  }
  function scheduleFlush() {
    if (flushTimer) return;
    flushTimer = setTimeout(function () {
      flushTimer = null;
      flush();
    }, 1500);
  }

  function once(key, fn) {
    if (sent[key]) return;
    sent[key] = true;
    fn();
  }

  function init() {
    emit("page_view");

    // product page view
    var m = location.pathname.match(/\/products\/([^/]+)\//);
    if (m) emit("product_view", { slug: m[1] });

    // guide read at 75% depth, once per page
    if (/\/buying-guides\/[^/]+\//.test(location.pathname)) {
      var fired = false;
      var onScroll = function () {
        var doc = document.documentElement;
        var max = doc.scrollHeight - window.innerHeight;
        if (max <= 0) return;
        if ((window.scrollY || doc.scrollTop || 0) / max >= 0.75) {
          if (fired) return;
          fired = true;
          emit("guide_read", { slug: location.pathname.split("/").filter(Boolean).pop() });
          window.removeEventListener("scroll", onScroll, { passive: true });
        }
      };
      window.addEventListener("scroll", onScroll, { passive: true });
      onScroll();
    }

    // outbound clicks on paid product links
    document.addEventListener(
      "click",
      function (ev) {
        var a = ev.target.closest && ev.target.closest("a[data-outbound], a[data-product-link]");
        if (!a) return;
        var href = a.getAttribute("href") || "";
        if (!/amazon\./i.test(href)) return;
        emit("outbound_click", {
          pid: productIdFrom(a),
          pos: a.dataset.position || "inline"
        });
        flush(); // leave immediately after; send before unload
      },
      true
    );

    // newsletter form
    var form = document.querySelector("[data-capture]");
    if (form) {
      form.addEventListener("submit", function (ev) {
        ev.preventDefault();
        var field = form.querySelector('input[type="email"]');
        var ok = !!(field && field.checkValidity && field.checkValidity());
        emit("capture_submit", { valid: ok ? "1" : "0" });
        var note = document.querySelector("[data-capture-note]");
        if (note) {
          note.innerHTML = ok
            ? "Thanks. No list is connected yet, so nothing was sent or stored — this is a placeholder until an endpoint is configured."
            : "That address does not look complete. Nothing was sent.";
        }
      });
    }

    // session-ish visibility, not identity
    document.addEventListener("visibilitychange", function () {
      if (document.visibilityState === "hidden") flush();
    });
    window.addEventListener("pagehide", flush);
    setInterval(flush, 15000);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
