/* Counter Tested — event recorder.
 *
 * Rules this file implements, and why:
 *  1. No cookies, no localStorage, no fingerprinting. `sid` is random per page load and dies with the tab.
 *  2. Nothing is sent unless a collector URL is configured in data/program.json -> measurement.endpoint.
 *     With no endpoint (the GitHub Pages default) this script counts in memory only, for the page's own display.
 *  3. No synthetic events. Every event here is triggered by a real interaction or by the page actually being
 *     visible: Amazon's Participation Requirements 6(s) prohibit artificially generating clicks or impressions,
 *     so this file must never be called from a test harness, a prefetch, or a timer that ignores visibility.
 *  4. No referrer, no user-agent, no IP, and the outbound destination is recorded as a host name only.
 *
 * Event names/fields come from the single source of truth: tools/events.py (schema). Keep them in sync.
 */
(function () {
  "use strict";
  var body = document.body;
  var endpoint = body.getAttribute("data-collector") || "";
  var version = parseInt(body.getAttribute("data-schema-version") || "1", 10);
  var path = location.pathname;
  var isDoc = body.getAttribute("data-page-kind") === "doc";
  var hasAffiliate = !!document.querySelector("[data-affiliate]");
  var sid = (window.crypto && crypto.getRandomValues)
    ? (function (a) { crypto.getRandomValues(a); return Array.prototype.map.call(a, function (x) { return ("0" + x.toString(16)).slice(-2); }).join(""); })(new Uint8Array(6))
    : String(Math.random()).slice(2, 14);

  var local = { page_view: 0, guide_view: 0, outbound_click: 0, disclosure_view: 0, product_intent_confirmation: 0 };
  var sent = false;

  function emit(ev, extra) {
    if (!local.hasOwnProperty(ev)) { return; }   // unknown events are dropped, not accepted
    local[ev] += 1;
    if (window.__ct) { window.__ct[ev] = local[ev]; }
    if (!endpoint || sent) { return; }
    var payload = { ev: ev, path: path, sid: sid, v: version };
    if (extra) { for (var k in extra) { if (Object.prototype.hasOwnProperty.call(extra, k)) { payload[k] = extra[k]; } } }
    try {
      var blob = new Blob([JSON.stringify(payload)], { type: "text/plain" });
      if (navigator.sendBeacon) { navigator.sendBeacon(endpoint, blob); }
      else { fetch(endpoint, { method: "POST", body: JSON.stringify(payload), keepalive: true, mode: "no-cors" }); }
    } catch (e) { /* never break the page for a counter */ }
  }

  // EV-01 page_view — after first paint, once.
  function onPageView() { if (!sent) { emit("page_view", { host_kind: location.hostname === "localhost" || location.protocol === "file:" ? "local" : "pages" }); } }
  if (document.readyState === "complete" || document.readyState === "interactive") { onPageView(); }
  else { document.addEventListener("DOMContentLoaded", onPageView, { once: true }); }

  // EV-02 guide_view — 30s of actually-visible time, or 75% depth, whichever first.
  if (isDoc) {
    var visibleMs = 0, last = Date.now(), done = false;
    function tick() {
      var now = Date.now();
      if (!document.hidden) { visibleMs += now - last; }
      last = now;
      if (!done && visibleMs >= 30000) { done = true; fire(); }
    }
    function depth() {
      if (done) { return; }
      var h = document.documentElement;
      var max = h.scrollHeight - h.clientHeight;
      if (max > 0 && (h.scrollTop / max) >= 0.75) { done = true; fire(); }
    }
    function fire() {
      emit("guide_view", {
        doc: body.getAttribute("data-doc") || path,
        dwell_s: Math.round(visibleMs / 1000),
        depth_pct: Math.min(100, Math.round((document.documentElement.scrollTop / Math.max(1, document.documentElement.scrollHeight - document.documentElement.clientHeight)) * 100))
      });
    }
    document.addEventListener("visibilitychange", tick);
    addEventListener("scroll", depth, { passive: true, capture: true });
    setInterval(tick, 1000);
  }

  // EV-03 outbound_click — real pointer/key activation on a marked affiliate link.
  document.addEventListener("click", function (e) {
    var a = e.target && e.target.closest ? e.target.closest("a[data-affiliate]") : null;
    if (!a) { return; }
    var host = "";
    try { host = new URL(a.href, location.href).host; } catch (err) { host = "unknown"; }
    emit("outbound_click", {
      product_slot: a.getAttribute("data-slot") || "",
      block_id: a.getAttribute("data-block") || "",
      destination_host: host,
      tag_present: (a.getAttribute("href") || "").indexOf("tag=") !== -1
    });
  }, { capture: true });

  // EV-04 disclosure_view — the strip really entered the viewport, on a page that can send you somewhere.
  if (hasAffiliate && "IntersectionObserver" in window) {
    var strip = document.getElementById("disclosure-strip");
    if (strip) {
      var io = new IntersectionObserver(function (entries) {
        for (var i = 0; i < entries.length; i++) {
          if (entries[i].isIntersecting) { emit("disclosure_view", { page_kind: body.getAttribute("data-page-kind") || "page" }); io.disconnect(); break; }
        }
      }, { threshold: 0.6 });
      io.observe(strip);
    }
  }
})();
