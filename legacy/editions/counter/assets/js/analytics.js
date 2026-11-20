/* Crisp & Counter — privacy-preserving event client.
 * No cookies. No third-party beacons. No IP or user-agent capture.
 * Events post ONLY to a first-party endpoint when the site owner configures one
 * (meta[name="ck-endpoint"]); otherwise counts aggregate in this browser only.
 * Event register: see desk/analytics.html (E1–E5).
 */
(function () {
  "use strict";
  var KEY = "ck_events_v1";
  var endpoint = (document.querySelector('meta[name="ck-endpoint"]') || {}).content || "";
  var sessionKey = "ck_session_v1";

  function buf() {
    try { return JSON.parse(localStorage.getItem(KEY)) || { events: {}, sessions: [] }; }
    catch (e) { return { events: {}, sessions: [] }; }
  }
  function save(b) { try { localStorage.setItem(KEY, JSON.stringify(b)); } catch (e) {} }

  function firstPartySession() {
    // A random per-browser id that never leaves the browser unless the owner
    // configures a first-party endpoint. Rotates when storage is cleared.
    var s = null;
    try { s = sessionStorage.getItem(sessionKey); } catch (e) {}
    if (!s) {
      s = "s" + Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
      try { sessionStorage.setItem(sessionKey, s); } catch (e) {}
    }
    return s;
  }

  function track(name, payload) {
    payload = payload || {};
    var b = buf();
    b.events[name] = (b.events[name] || 0) + 1;
    b.last = { name: name, payload: payload, t: new Date().toISOString() };
    save(b);
    if (endpoint && window.fetch && navigator.sendBeacon) {
      var body = JSON.stringify({
        e: name, p: payload, t: new Date().toISOString(),
        path: location.pathname, s: firstPartySession()
      });
      try { navigator.sendBeacon(endpoint, body); } catch (err) {}
    }
    document.dispatchEvent(new CustomEvent("ck:track", { detail: { name: name, payload: payload } }));
  }
  window.ckTrack = track;

  // E1 — page_view
  document.addEventListener("DOMContentLoaded", function () {
    track("page_view", { path: location.pathname });

    // E3 — outbound_click on every sponsored product link
    document.querySelectorAll('a[data-aff]').forEach(function (a) {
      a.addEventListener("click", function () {
        track("outbound_click", {
          product: a.getAttribute("data-aff") || "",
          kind: a.getAttribute("data-aff-kind") || "link",
          path: location.pathname
        });
      });
    });

    // E2 — product_impression (once per card per page load)
    if ("IntersectionObserver" in window) {
      var seen = {};
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (!en.isIntersecting) return;
          var id = en.target.getAttribute("data-product-id");
          if (!id || seen[id]) return;
          seen[id] = true;
          track("product_impression", { product: id });
          io.unobserve(en.target);
        });
      }, { threshold: 0.35 });
      document.querySelectorAll("[data-product-id]").forEach(function (el) { io.observe(el); });
    }

    // E4 — guide_read: 20 seconds or 50% scroll
    if (document.body.hasAttribute("data-guide")) {
      var slug = document.body.getAttribute("data-guide");
      var fired = false;
      function fireRead() {
        if (fired) return; fired = true;
        track("guide_read", { guide: slug });
      }
      setTimeout(fireRead, 20000);
      window.addEventListener("scroll", function () {
        var h = document.documentElement.scrollHeight - window.innerHeight;
        if (h > 0 && window.scrollY / h >= 0.5) fireRead();
      }, { passive: true });
    }

    // E5 — feedback_submit on suggestion/feedback links
    document.querySelectorAll('a[data-feedback]').forEach(function (a) {
      a.addEventListener("click", function () {
        track("feedback_submit", { suggestion: a.getAttribute("data-feedback") || "" });
      });
    });
  });
})();
