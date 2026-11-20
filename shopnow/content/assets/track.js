/* ShopNow 047 - outbound click and conversion measurement.
 *
 * Privacy posture, stated in code so it can be audited rather than promised:
 *   - no document.cookie reads or writes
 *   - no localStorage (identity lives in sessionStorage and dies with the tab)
 *   - no fingerprinting: no canvas, no screen, no fonts, no plugin list, no timezone
 *   - no referrer, no destination URL query string, no page text in the payload
 *   - exactly one endpoint, configured at build time; with none configured nothing
 *     is transmitted and events stay in this tab only
 *
 * See register/measurement.json for the five event definitions this emits.
 */
(function () {
  "use strict";

  var CFG = window.SHOPNOW_MEASURE || {};
  var ENDPOINT = typeof CFG.endpoint === "string" && CFG.endpoint.indexOf("{{") === -1 ? CFG.endpoint : null;
  var MAX_BUFFER = 200;
  var KEY = "sn047.q";
  var SID = null;

  function sessionToken() {
    if (SID) return SID;
    try {
      SID = sessionStorage.getItem("sn047.s");
      if (!SID) {
        SID = (crypto.randomUUID ? crypto.randomUUID() : String(Date.now()) + "-" + Math.random().toString(36).slice(2));
        sessionStorage.setItem("sn047.s", SID);
      }
    } catch (e) {
      SID = "ephemeral";
    }
    return SID;
  }

  function buffer(ev) {
    try {
      var q = JSON.parse(sessionStorage.getItem(KEY) || "[]");
      q.push(ev);
      if (q.length > MAX_BUFFER) q = q.slice(q.length - MAX_BUFFER);
      sessionStorage.setItem(KEY, JSON.stringify(q));
      return q;
    } catch (e) { return [ev]; }
  }

  function send(ev) {
    if (!ENDPOINT) return;
    // sendBeacon keeps the event alive across the navigation we are about to allow.
    if (navigator.sendBeacon) {
      try { navigator.sendBeacon(ENDPOINT, new Blob([JSON.stringify(ev)], { type: "application/json" })); return; } catch (e) {}
    }
    try {
      fetch(ENDPOINT, { method: "POST", body: JSON.stringify(ev), headers: { "Content-Type": "application/json" }, keepalive: true, referrerPolicy: "no-referrer", mode: "cors" }).catch(function () {});
    } catch (e) {}
  }

  var KNOWN = { page_view: 1, guide_view: 1, outbound_click: 1, intent_confirm: 1, register_gap_view: 1 };

  function track(id, fields) {
    if (!KNOWN[id]) return;
    var ev = { e: id, s: sessionToken(), p: location.pathname, t: new Date().toISOString() };
    if (fields) for (var k in fields) if (fields[k] != null) ev[k] = fields[k];
    var q = buffer(ev);
    send(ev);
    // opportunistic drain: if a previous visit buffered locally and an endpoint now
    // exists, flush it once. No retry queue is kept server-side.
    if (ENDPOINT && q.length > 1 && q.length % 25 === 0) {
      q.slice(0, q.length - 1).forEach(send);
    }
  }

  window.__shopnowTrack = track;

  document.addEventListener("DOMContentLoaded", function () {
    var path = location.pathname;
    track("page_view", { slug: (path.match(/\/([^/]+)\/$/) || [null, null])[1] });

    var gm = path.match(/\/guides\/([^/]+)\/$/);
    if (gm) track("guide_view", { guide_slug: gm[1], cluster: document.documentElement.getAttribute("data-cluster") || null });

    var gap = document.querySelector("[data-gap-flag]");
    if (gap) track("register_gap_view", { flag_id: gap.getAttribute("data-gap-flag"), field_names: gap.getAttribute("data-gap-fields") || null });
  });

  // Intercept commerce clicks. We do not preventDefault: the reader's navigation must
  // never depend on our analytics working, and blocking it would be its own UX bug.
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("a[data-aff]");
    if (!a) return;
    track("outbound_click", {
      product_id: a.getAttribute("data-aff"),
      asin_observed: a.getAttribute("data-asin") || null,
      placement: a.getAttribute("data-placement") || "unlabelled",
      link_format: "special_tagged_dp"
    });
  }, { capture: true });
})();
